"""
OfficeCLI MCP PPT生成服务
通过OfficeCLI的MCP（Model Context Protocol）服务生成PPT

## 架构说明

本服务使用MCP协议与OfficeCLI MCP服务器通信：
- **MCP工具**: OfficeCLI暴露一个统一的 `officecli` 工具
- **命令路由**: 通过 `command` 参数区分操作 (create, view, get, set, add, remove, move, validate, batch)

## MCP工具调用格式

```json
{
    "name": "officecli",
    "arguments": {
        "command": "create",
        "file": "/path/to/file.pptx",
        ...
    }
}
```

## 使用方式

```python
from app.services.officecli_mcp_service import get_officecli_mcp_service

service = get_officecli_mcp_service()
if service.is_available():
    result = service.generate_ppt_from_outline(...)
```
"""
import subprocess
import os
import json
import logging
import tempfile
import shutil
import time
import threading
from datetime import datetime
from typing import List, Dict, Optional, Callable, Any
from queue import Queue, Empty

# 导入SKILL知识加载器
from app.services.officecli_skill_loader import get_skill_knowledge

logger = logging.getLogger(__name__)

# OfficeCLI目录路径 - 使用绝对路径确保路径正确
OFFICECLI_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'OfficeCLI-main'))
OFFICECLI_STYLES_DIR = os.path.abspath(os.path.join(OFFICECLI_DIR, 'styles'))


class MCPClient:
    """MCP协议客户端，用于与OfficeCLI MCP服务器通信"""
    
    def __init__(self, officecli_path: str):
        self.officecli_path = officecli_path
        self.process = None
        self.request_id = 0
        self.response_queue = Queue()
        self.reader_thread = None
        self.running = False
        self._initialized = False
        self._lock = threading.Lock()
        
    def start(self) -> bool:
        """启动MCP服务器"""
        if self.process and self.process.poll() is None:
            return True
            
        try:
            # 启动MCP服务器（stdio模式）- 命令是 "officecli mcp"
            cmd = [self.officecli_path, 'mcp']
            
            # 设置环境变量强制UTF-8编码
            env = os.environ.copy()
            env['DOTNET_CLI_UI_LANGUAGE'] = 'en-US'
            env['DOTNET_NOLOGO'] = '1'
            # 在Windows上强制控制台使用UTF-8代码页
            if os.name == 'nt':
                env['CHCP'] = '65001'
            
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',  # 强制使用UTF-8编码
                errors='replace',  # 遇到无法解码的字符时替换而不是报错
                bufsize=1,  # 行缓冲
                cwd=tempfile.gettempdir(),
                env=env
            )
            self.running = True
            
            # 启动后台线程读取响应
            self.reader_thread = threading.Thread(target=self._read_responses, daemon=True)
            self.reader_thread.start()
            
            # 等待服务器初始化
            time.sleep(0.5)
            
            if self.process.poll() is not None:
                stderr = self.process.stderr.read() if self.process.stderr else ''
                logger.error(f"[MCP] 服务器启动失败: {stderr}")
                return False
            
            # 发送初始化请求
            if not self._do_initialize():
                logger.error("[MCP] 初始化失败")
                return False
                
            logger.info("[MCP] MCP服务器启动并初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"[MCP] 启动MCP服务器失败: {e}")
            return False
    
    def _do_initialize(self) -> bool:
        """执行MCP初始化握手"""
        # 发送initialize请求
        response = self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "guowaibao-ppt-service",
                "version": "1.0.0"
            }
        })
        
        if "error" in response:
            logger.error(f"[MCP] initialize失败: {response['error']}")
            return False
        
        # 发送notifications/initialized
        self._send_notification("notifications/initialized", {})
        self._initialized = True
        
        logger.info("[MCP] 初始化握手完成")
        return True
    
    def stop(self):
        """停止MCP服务器"""
        self.running = False
        self._initialized = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            self.process = None
        logger.info("[MCP] MCP服务器已停止")
    
    def _read_responses(self):
        """后台线程：读取MCP服务器的响应"""
        while self.running and self.process:
            try:
                if self.process.stdout:
                    line = self.process.stdout.readline()
                    if line:
                        line = line.strip()
                        if line:
                            try:
                                response = json.loads(line)
                                self.response_queue.put(response)
                                logger.debug(f"[MCP] 收到响应: {json.dumps(response, ensure_ascii=False)[:200]}")
                            except json.JSONDecodeError as e:
                                logger.warning(f"[MCP] JSON解析失败: {e}, line: {line[:100]}")
            except Exception as e:
                if self.running:
                    logger.error(f"[MCP] 读取响应失败: {e}")
                break
    
    def _send_request(self, method: str, params: Dict = None, timeout: int = 60) -> Dict:
        """发送JSON-RPC请求"""
        with self._lock:
            if not self.process or self.process.poll() is not None:
                return {"error": "MCP服务器未运行"}
            
            self.request_id += 1
            request = {
                "jsonrpc": "2.0",
                "id": self.request_id,
                "method": method,
                "params": params or {}
            }
            
            try:
                request_str = json.dumps(request, ensure_ascii=False) + '\n'
                self.process.stdin.write(request_str)
                self.process.stdin.flush()
                logger.debug(f"[MCP] 发送请求: {method}")
                
                # 等待响应（带超时）
                try:
                    response = self.response_queue.get(timeout=timeout)
                    return response
                except Empty:
                    return {"error": f"请求超时 ({timeout}s)"}
                    
            except Exception as e:
                logger.error(f"[MCP] 发送请求失败: {e}")
                return {"error": str(e)}
    
    def _send_notification(self, method: str, params: Dict = None):
        """发送JSON-RPC通知（无响应）"""
        with self._lock:
            if not self.process or self.process.poll() is not None:
                return
            
            notification = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params or {}
            }
            
            try:
                notification_str = json.dumps(notification, ensure_ascii=False) + '\n'
                self.process.stdin.write(notification_str)
                self.process.stdin.flush()
            except Exception as e:
                logger.error(f"[MCP] 发送通知失败: {e}")
    
    def call_officecli(self, arguments: Dict, timeout: int = 60) -> Dict:
        """
        调用OfficeCLI MCP工具
        
        OfficeCLI MCP只暴露一个工具 "officecli"，通过 command 参数区分操作：
        - create: 创建文档
        - view: 查看文档
        - get: 获取节点
        - set: 设置属性
        - add: 添加元素
        - remove: 删除元素
        - move: 移动元素
        - validate: 验证文档
        - batch: 批量执行
        """
        response = self._send_request("tools/call", {
            "name": "officecli",
            "arguments": arguments
        }, timeout=timeout)
        
        # 检查是否有错误
        if "error" in response:
            return {"success": False, "error": response["error"]}
        
        # 提取结果
        result = response.get("result", {})
        if isinstance(result, dict):
            # 检查是否是MCP内容格式
            if "content" in result:
                content = result["content"]
                if isinstance(content, list) and len(content) > 0:
                    first_content = content[0]
                    if isinstance(first_content, dict) and "text" in first_content:
                        text = first_content["text"]
                        # 检查是否是错误
                        if result.get("isError"):
                            return {"success": False, "error": text}
                        # 尝试解析JSON
                        try:
                            return {"success": True, "data": json.loads(text)}
                        except json.JSONDecodeError:
                            return {"success": True, "data": text}
            return {"success": True, "data": result}
        
        return {"success": True, "data": result}
    
    def list_tools(self) -> Dict:
        """获取可用工具列表"""
        return self._send_request("tools/list")
    
    def is_running(self) -> bool:
        """检查MCP服务器是否运行中"""
        return self.running and self.process is not None and self.process.poll() is None and self._initialized


class OfficeCLIMCPPTService:
    """使用OfficeCLI MCP服务生成PPT
    
    ## 驻留模式优化
    
    当需要执行3+条命令操作同一文件时，使用驻留模式(open/close)：
    - open_document(): 打开文档，建立会话
    - close_document(): 关闭文档，释放资源
    - 避免重复I/O，提升性能
    
    ## 批量模式
    
    每张幻灯片使用batch命令批量执行，减少调用次数
    """
    
    def __init__(self):
        self.officecli_path = self._find_officecli()
        self.mcp_client = None
        self.styles_dir = OFFICECLI_STYLES_DIR
        self.watch_process = None
        self.watch_port = 18080
        # 驻留模式状态
        self._open_documents = {}  # {file_path: {'opened_at': timestamp, 'slide_count': int}}
        logger.info(f"[MCP-PPT] 初始化，OfficeCLI路径: {self.officecli_path or '未找到'}")
    
    def _find_officecli(self) -> str:
        """查找officecli可执行文件"""
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        if os.name == 'nt':
            possible_paths = [
                os.path.join(backend_dir, 'OfficeCLI-main', 'officecli.exe'),
                os.path.join(backend_dir, 'OfficeCLI-main', 'bin', 'officecli.exe'),
                'officecli',
                'officecli.exe',
                os.path.expanduser('~/.officecli/officecli.exe'),
                os.path.join(os.getcwd(), 'officecli.exe'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'OfficeCli', 'officecli.exe'),
            ]
        else:
            possible_paths = [
                os.path.join(backend_dir, 'OfficeCLI-main', 'officecli'),
                os.path.join(backend_dir, 'OfficeCLI-main', 'bin', 'officecli'),
                'officecli',
                os.path.expanduser('~/.local/bin/officecli'),
                os.path.expanduser('~/.officecli/officecli'),
                '/usr/local/bin/officecli',
                '/usr/bin/officecli',
            ]
        
        for path in possible_paths:
            if shutil.which(path):
                return path
            if os.path.isfile(path) and os.access(path, os.X_OK if os.name != 'nt' else True):
                return path
        return None
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.officecli_path is not None
    
    def _ensure_mcp_client(self) -> MCPClient:
        """确保MCP客户端已启动"""
        if self.mcp_client is None:
            if not self.officecli_path:
                raise RuntimeError("OfficeCLI未安装或未找到")
            self.mcp_client = MCPClient(self.officecli_path)
        
        if not self.mcp_client.is_running():
            if not self.mcp_client.start():
                raise RuntimeError("MCP服务器启动失败")
        
        return self.mcp_client
    
    def get_available_styles(self) -> List[Dict]:
        """获取所有可用的内置样式模板"""
        styles = []
        
        if not os.path.isdir(self.styles_dir):
            logger.warning(f"[MCP-PPT] 样式目录不存在: {self.styles_dir}")
            return styles
        
        for style_name in os.listdir(self.styles_dir):
            style_path = os.path.join(self.styles_dir, style_name)
            if not os.path.isdir(style_path):
                continue
            
            style_md_path = os.path.join(style_path, 'style.md')
            description = ""
            colors = {}
            
            if os.path.isfile(style_md_path):
                try:
                    with open(style_md_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for line in content.split('\n')[:10]:
                            if line.startswith('# ') and not description:
                                description = line[2:].strip()
                            if line.startswith('| Primary') or line.startswith('| Background'):
                                parts = [p.strip() for p in line.split('|') if p.strip()]
                                if len(parts) >= 2:
                                    colors[parts[0].lower()] = parts[1]
                except Exception as e:
                    logger.warning(f"[MCP-PPT] 读取样式文件失败: {e}")
            
            styles.append({
                'name': style_name,
                'path': style_path,
                'description': description or style_name,
                'colors': colors
            })
        
        return styles
    
    # ============== 驻留模式方法 (Resident Mode) ==============
    
    def open_document(self, file_path: str) -> Dict:
        """
        打开文档（驻留模式）
        
        当需要执行3+条命令操作同一文件时，使用驻留模式避免重复I/O。
        打开后，后续的命令操作将复用已打开的文档句柄。
        
        Args:
            file_path: PPT文件路径
            
        Returns:
            {'success': bool, 'slide_count': int, 'error': str}
        """
        try:
            client = self._ensure_mcp_client()
            
            # 检查是否已打开
            if file_path in self._open_documents:
                logger.info(f"[MCP-PPT] 文档已打开: {file_path}")
                return {'success': True, 'slide_count': self._open_documents[file_path].get('slide_count', 0)}
            
            # 发送open命令
            result = client.call_officecli({
                "command": "open",
                "file": file_path
            })
            
            if result.get("success"):
                # 获取幻灯片数量
                slide_count = self.get_slide_count(file_path)
                
                # 记录打开状态
                self._open_documents[file_path] = {
                    'opened_at': time.time(),
                    'slide_count': slide_count
                }
                
                logger.info(f"[MCP-PPT] 文档打开成功（驻留模式）: {file_path}, 幻灯片数: {slide_count}")
                return {'success': True, 'slide_count': slide_count}
            else:
                error = result.get('error', '未知错误')
                logger.error(f"[MCP-PPT] 打开文档失败: {error}")
                return {'success': False, 'error': error}
                
        except Exception as e:
            logger.error(f"[MCP-PPT] 打开文档异常: {e}")
            return {'success': False, 'error': str(e)}
    
    def close_document(self, file_path: str) -> Dict:
        """
        关闭文档（驻留模式）
        
        完成所有操作后，关闭文档释放资源。
        
        Args:
            file_path: PPT文件路径
            
        Returns:
            {'success': bool, 'error': str}
        """
        try:
            # 从打开记录中移除
            if file_path in self._open_documents:
                del self._open_documents[file_path]
            
            client = self._ensure_mcp_client()
            result = client.call_officecli({
                "command": "close",
                "file": file_path
            })
            
            if result.get("success"):
                logger.info(f"[MCP-PPT] 文档关闭成功: {file_path}")
                return {'success': True}
            else:
                # 即使close命令失败，也从本地记录中移除
                logger.warning(f"[MCP-PPT] 关闭文档命令失败（已从本地移除）: {result.get('error')}")
                return {'success': True}  # 仍然返回成功，因为本地状态已清理
                
        except Exception as e:
            logger.error(f"[MCP-PPT] 关闭文档异常: {e}")
            # 确保本地状态被清理
            if file_path in self._open_documents:
                del self._open_documents[file_path]
            return {'success': False, 'error': str(e)}
    
    def is_document_open(self, file_path: str) -> bool:
        """检查文档是否在驻留模式中打开"""
        return file_path in self._open_documents
    
    def _should_use_resident_mode(self, estimated_commands: int) -> bool:
        """
        判断是否应该使用驻留模式
        
        规则：3+条命令时使用驻留模式
        """
        return estimated_commands >= 3

    # ============== MCP工具调用方法 ==============
    
    def create_ppt(self, output_path: str) -> bool:
        """通过MCP创建空白PPT文件"""
        try:
            client = self._ensure_mcp_client()
            result = client.call_officecli({
                "command": "create",
                "file": output_path
            })
            
            if result.get("success"):
                logger.info(f"[MCP-PPT] 创建PPT成功: {output_path}")
                return True
            else:
                logger.error(f"[MCP-PPT] 创建PPT失败: {result.get('error')}")
                return False
        except Exception as e:
            logger.error(f"[MCP-PPT] 创建PPT异常: {e}")
            return False
    
    def add_slide(self, ppt_path: str, title: str = "", layout_index: int = None) -> bool:
        """通过MCP添加幻灯片"""
        try:
            client = self._ensure_mcp_client()
            props = []
            if title:
                props.append(f"title={title}")
            if layout_index is not None:
                props.append(f"layout={layout_index}")
            
            result = client.call_officecli({
                "command": "add",
                "file": ppt_path,
                "parent": "/",
                "type": "slide",
                "props": props
            })
            
            if result.get("success"):
                logger.debug(f"[MCP-PPT] 添加幻灯片成功: {title or '无标题'}")
                return True
            else:
                logger.warning(f"[MCP-PPT] 添加幻灯片失败: {result.get('error')}")
                return False
        except Exception as e:
            logger.error(f"[MCP-PPT] 添加幻灯片异常: {e}")
            return False
    
    def add_shape(self, ppt_path: str, slide_index: int, shape_type: str = 'shape', 
                  props: Dict = None) -> bool:
        """通过MCP添加形状"""
        try:
            client = self._ensure_mcp_client()
            prop_list = []
            if props:
                for k, v in props.items():
                    prop_list.append(f"{k}={v}")
            
            result = client.call_officecli({
                "command": "add",
                "file": ppt_path,
                "parent": f"/slide[{slide_index}]",
                "type": shape_type,
                "props": prop_list
            })
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"[MCP-PPT] 添加形状异常: {e}")
            return False
    
    def add_picture(self, ppt_path: str, slide_index: int, image_path: str,
                    x: str = "2cm", y: str = "5cm", width: str = "10cm", height: str = "6cm") -> bool:
        """通过MCP添加图片"""
        try:
            client = self._ensure_mcp_client()
            result = client.call_officecli({
                "command": "add",
                "file": ppt_path,
                "parent": f"/slide[{slide_index}]",
                "type": "picture",
                "props": [
                    f"path={image_path}",
                    f"x={x}",
                    f"y={y}",
                    f"width={width}",
                    f"height={height}"
                ]
            })
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"[MCP-PPT] 添加图片异常: {e}")
            return False
    
    def set_element(self, ppt_path: str, path: str, props: Dict) -> bool:
        """通过MCP设置元素属性"""
        try:
            client = self._ensure_mcp_client()
            prop_list = []
            for k, v in props.items():
                prop_list.append(f"{k}={v}")
            
            result = client.call_officecli({
                "command": "set",
                "file": ppt_path,
                "path": path,
                "props": prop_list
            })
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"[MCP-PPT] 设置元素异常: {e}")
            return False
    
    def get_slide_count(self, ppt_path: str) -> int:
        """通过MCP获取幻灯片数量"""
        try:
            client = self._ensure_mcp_client()
            result = client.call_officecli({
                "command": "view",
                "file": ppt_path,
                "mode": "stats"
            })
            
            if result.get("success"):
                data = result.get("data", "")
                # 解析统计信息，格式可能是 "Slides: 5, Shapes: 10"
                if isinstance(data, str):
                    import re
                    match = re.search(r'Slides:\s*(\d+)', data)
                    if match:
                        return int(match.group(1))
            return 0
        except Exception as e:
            logger.error(f"[MCP-PPT] 获取幻灯片数量异常: {e}")
            return 0
    
    def get_slide_structure(self, ppt_path: str, slide_index: int) -> Dict:
        """通过MCP获取幻灯片结构"""
        try:
            client = self._ensure_mcp_client()
            result = client.call_officecli({
                "command": "get",
                "file": ppt_path,
                "path": f"/slide[{slide_index}]",
                "depth": 2
            })
            
            if result.get("success"):
                data = result.get("data", {})
                return data if isinstance(data, dict) else {}
            return {}
        except Exception as e:
            logger.error(f"[MCP-PPT] 获取幻灯片结构异常: {e}")
            return {}
    
    def get_outline(self, ppt_path: str) -> Dict:
        """通过MCP获取PPT大纲"""
        try:
            client = self._ensure_mcp_client()
            result = client.call_officecli({
                "command": "view",
                "file": ppt_path,
                "mode": "outline"
            })
            
            if result.get("success"):
                data = result.get("data", {})
                return data if isinstance(data, dict) else {"raw": str(data)}
            return {}
        except Exception as e:
            logger.error(f"[MCP-PPT] 获取大纲异常: {e}")
            return {}
    
    def validate_ppt(self, ppt_path: str) -> tuple:
        """通过MCP验证PPT"""
        try:
            client = self._ensure_mcp_client()
            result = client.call_officecli({
                "command": "validate",
                "file": ppt_path
            })
            
            if result.get("success"):
                data = result.get("data", "")
                # 如果验证通过，返回的是成功消息
                if isinstance(data, str) and "no errors" in data.lower():
                    return True, data, ""
                # 如果有错误
                if isinstance(data, str) and "error" in data.lower():
                    return False, "", data
                return True, str(data), ""
            return False, "", result.get("error", "验证失败")
        except Exception as e:
            return False, "", str(e)
    
    def view_issues(self, ppt_path: str, limit: int = 20) -> List:
        """通过MCP查看PPT问题"""
        try:
            client = self._ensure_mcp_client()
            result = client.call_officecli({
                "command": "view",
                "file": ppt_path,
                "mode": "issues"
            })
            
            if result.get("success"):
                data = result.get("data", "")
                # 解析JSON格式的问题列表
                if isinstance(data, str):
                    try:
                        parsed = json.loads(data)
                        if isinstance(parsed, dict):
                            return parsed.get("issues", [])
                        elif isinstance(parsed, list):
                            return parsed
                    except json.JSONDecodeError:
                        pass
                elif isinstance(data, dict):
                    return data.get("issues", [])
                elif isinstance(data, list):
                    return data
            return []
        except Exception as e:
            logger.error(f"[MCP-PPT] 查看问题异常: {e}")
            return []
    
    def batch_execute(self, ppt_path: str, commands: List[Dict]) -> Dict:
        """通过MCP批量执行命令"""
        try:
            client = self._ensure_mcp_client()
            result = client.call_officecli({
                "command": "batch",
                "file": ppt_path,
                "commands": json.dumps(commands, ensure_ascii=False)
            }, timeout=120)
            
            return result
        except Exception as e:
            logger.error(f"[MCP-PPT] 批量执行异常: {e}")
            return {"success": False, "error": str(e)}
    
    def start_watch(self, ppt_path: str, port: int = 18080) -> dict:
        """开启实时预览（使用CLI，因为MCP不支持此功能）"""
        if not self.officecli_path:
            return {'success': False, 'error': 'OfficeCLI未安装'}
        
        try:
            cmd = [self.officecli_path, 'watch', ppt_path, '--port', str(port)]
            self.watch_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.watch_port = port
            watch_url = f"http://localhost:{port}"
            logger.info(f"[MCP-PPT] 已开启实时预览: {ppt_path}")
            return {'success': True, 'url': watch_url, 'port': port}
        except Exception as e:
            logger.error(f"[MCP-PPT] 开启实时预览失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def stop_watch(self):
        """停止实时预览"""
        if self.watch_process:
            try:
                self.watch_process.terminate()
                self.watch_process = None
                logger.info("[MCP-PPT] 已停止实时预览")
            except Exception as e:
                logger.warning(f"[MCP-PPT] 停止实时预览失败: {e}")
    
    # ============== 高级PPT生成方法 ==============
    
    def merge_template(self, template_path: str, output_path: str, data: Dict) -> Dict:
        """
        使用OfficeCLI的merge命令合并模板和数据
        
        OfficeCLI merge命令会替换模板中的 {{key}} 占位符
        
        Args:
            template_path: 模板文件路径
            output_path: 输出文件路径
            data: 要填充的数据字典
            
        Returns:
            {'success': bool, 'error': str}
        """
        try:
            client = self._ensure_mcp_client()
            
            # 将数据转换为JSON字符串
            data_json = json.dumps(data, ensure_ascii=False)
            
            result = client.call_officecli({
                "command": "merge",
                "file": template_path,
                "output": output_path,
                "data": data_json
            }, timeout=60)
            
            if result.get("success"):
                logger.info(f"[MCP-PPT] 模板合并成功: {template_path} -> {output_path}")
                return {'success': True}
            else:
                error = result.get('error', '未知错误')
                logger.error(f"[MCP-PPT] 模板合并失败: {error}")
                return {'success': False, 'error': error}
                
        except Exception as e:
            logger.error(f"[MCP-PPT] 模板合并异常: {e}")
            return {'success': False, 'error': str(e)}
    
    def clone_slide(self, ppt_path: str, source_slide_index: int, target_index: int = None) -> bool:
        """
        克隆幻灯片
        
        Args:
            ppt_path: PPT文件路径
            source_slide_index: 源幻灯片索引（1-based）
            target_index: 目标位置索引（可选，默认添加到末尾）
            
        Returns:
            bool: 是否成功
        """
        try:
            client = self._ensure_mcp_client()
            
            props = []
            if target_index is not None:
                props.append(f"index={target_index}")
            
            result = client.call_officecli({
                "command": "add",
                "file": ppt_path,
                "parent": "/",
                "from": f"/slide[{source_slide_index}]",
                "props": props
            })
            
            return result.get("success", False)
        except Exception as e:
            logger.error(f"[MCP-PPT] 克隆幻灯片异常: {e}")
            return False
    
    def get_template_placeholders(self, template_path: str) -> List[Dict]:
        """
        获取模板中的所有占位符
        
        Args:
            template_path: 模板文件路径
            
        Returns:
            占位符列表，每个元素包含 slide_index 和 placeholders
        """
        try:
            # 使用view命令获取模板结构
            client = self._ensure_mcp_client()
            result = client.call_officecli({
                "command": "view",
                "file": template_path,
                "mode": "annotated"
            })
            
            placeholders_by_slide = []
            
            if result.get("success"):
                data = result.get("data", "")
                # 解析占位符 {{key}}
                import re
                placeholder_pattern = r'\{\{([^}]+)\}\}'
                
                # 获取幻灯片数量
                slide_count = self.get_slide_count(template_path)
                
                for slide_idx in range(1, slide_count + 1):
                    # 获取每页的内容
                    slide_result = client.call_officecli({
                        "command": "get",
                        "file": template_path,
                        "path": f"/slide[{slide_idx}]",
                        "depth": 2
                    })
                    
                    if slide_result.get("success"):
                        slide_data = slide_result.get("data", "")
                        # 查找占位符
                        if isinstance(slide_data, str):
                            placeholders = list(set(re.findall(placeholder_pattern, slide_data)))
                        elif isinstance(slide_data, dict):
                            slide_data_str = json.dumps(slide_data)
                            placeholders = list(set(re.findall(placeholder_pattern, slide_data_str)))
                        else:
                            placeholders = []
                        
                        if placeholders:
                            placeholders_by_slide.append({
                                'slide_index': slide_idx,
                                'placeholders': placeholders
                            })
            
            return placeholders_by_slide
            
        except Exception as e:
            logger.error(f"[MCP-PPT] 获取模板占位符异常: {e}")
            return []
    
    def generate_ppt_from_outline(self,
                                   output_path: str,
                                   title: str,
                                   outline: Dict,
                                   requirements: Dict = None,
                                   image_service = None,
                                   progress_callback: Callable = None,
                                   template_type: str = 'blank',
                                   template_path: str = None,
                                   template_styles: Dict = None,
                                   builtin_template_id: str = None,
                                   compact_dialogue: str = '',
                                   compact_context: str = '') -> Dict:
        """
        根据大纲生成完整的PPT（统一入口）
        
        支持三种模式：
        1. 内置模板（template_type='builtin'）：使用模板化脚本生成
        2. 用户上传模板（template_type='uploaded'）：基于模板文件生成
        3. 空白生成（template_type='blank'）：从零开始创建PPT
        
        Args:
            output_path: 输出文件路径
            title: PPT主题
            outline: 大纲数据
            requirements: 需求配置
            image_service: 图片服务
            progress_callback: 进度回调
            template_type: 模板类型 ('builtin' | 'uploaded' | 'blank')
            template_path: 模板文件路径（用户上传模板）
            template_styles: 模板样式
            builtin_template_id: 内置模板ID（如 'builtin_science--time-travel'）
            compact_dialogue: 压缩的对话历史
            compact_context: 压缩的参考资料
        """
        if not self.is_available():
            raise RuntimeError("OfficeCLI未安装，请先安装officecli")
        
        logger.info(f"[MCP-PPT] ========== generate_ppt_from_outline 开始 ==========")
        logger.info(f"[MCP-PPT] 参数: template_type={template_type}, builtin_template_id={builtin_template_id}")
        print(f"[MCP-PPT] ========== generate_ppt_from_outline 开始 ==========")
        print(f"[MCP-PPT] template_type={template_type}, builtin_template_id={builtin_template_id}")
        
        # 内置模板生成 - 使用新的BuildSh生成器
        if template_type == 'builtin' and builtin_template_id:
            logger.info(f"[MCP-PPT] ✓ 进入内置模板生成分支: {builtin_template_id}")
            print(f"[MCP-PPT] ✓ 内置模板: {builtin_template_id}")
            
            # 使用Build_sh生成器
            from app.services.build_sh_generator import get_build_sh_generator
            generator = get_build_sh_generator()
            
            logger.info(f"[BuildShGenerator] 使用内置模板: {builtin_template_id}")
            
            # 调用生成器
            result = generator.generate_with_llm(
                template_id=builtin_template_id,
                outline=outline,
                output_path=output_path,
                progress_callback=progress_callback
            )
            
            logger.info(f"[BuildShGenerator] 生成完成: success={result.get('success')}")
            
            return result
        
        # 用户上传模板生成
        if template_type == 'uploaded' and template_path and os.path.exists(template_path):
            logger.info(f"[MCP-PPT] ✓ 进入用户模板生成分支")
            print(f"[MCP-PPT] ✓ 用户模板: {template_path}")
            return self._generate_ppt_from_template(
                output_path=output_path,
                template_path=template_path,
                title=title,
                outline=outline,
                requirements=requirements or {},
                progress_callback=progress_callback,
                compact_dialogue=compact_dialogue,
                compact_context=compact_context
            )
        
        # 空白生成（fallback）
        logger.info(f"[MCP-PPT] 空白生成模式")
        print(f"[MCP-PPT] 空白生成模式")
        return self._generate_ppt_with_llm(
            output_path=output_path,
            title=title,
            outline=outline,
            requirements=requirements,
            style_theme=template_styles.get('name') if template_styles else None,
            image_service=image_service,
            progress_callback=progress_callback,
            compact_dialogue=compact_dialogue,
            compact_context=compact_context
        )
    
    def _generate_ppt_from_template(self,
                                     output_path: str,
                                     template_path: str,
                                     title: str,
                                     outline: Dict,
                                     requirements: Dict,
                                     progress_callback: Callable = None,
                                     compact_dialogue: str = '',
                                     compact_context: str = '') -> Dict:
        """
        基于模板生成PPT
        
        流程：
        1. 分析模板结构，提取占位符
        2. 根据大纲生成占位符数据
        3. 使用OfficeCLI merge命令填充数据
        4. 验证并修复问题
        
        Args:
            output_path: 输出文件路径
            template_path: 模板文件路径
            title: PPT主题
            outline: 大纲数据
            requirements: 需求配置
            progress_callback: 进度回调
            compact_dialogue: 压缩的对话历史
            compact_context: 压缩的参考资料
        """
        import shutil
        
        try:
            # 1. 发送进度
            if progress_callback:
                progress_callback({'progress': 5, 'message': '分析模板结构...'})
            
            logger.info(f"[MCP-PPT] ========== 基于模板生成PPT ==========")
            logger.info(f"[MCP-PPT] 模板路径: {template_path}")
            logger.info(f"[MCP-PPT] 输出路径: {output_path}")
            
            # 2. 获取模板占位符
            if progress_callback:
                progress_callback({'progress': 10, 'message': '提取模板占位符...'})
            
            placeholders_info = self.get_template_placeholders(template_path)
            logger.info(f"[MCP-PPT] 模板占位符: {placeholders_info}")
            
            # 3. 获取模板幻灯片数量
            template_slide_count = self.get_slide_count(template_path)
            outline_slides = outline.get('slides', [])
            outline_slide_count = len(outline_slides)
            
            logger.info(f"[MCP-PPT] 模板页数: {template_slide_count}, 大纲页数: {outline_slide_count}")
            
            # 4. 先复制模板到输出路径
            if progress_callback:
                progress_callback({'progress': 15, 'message': '复制模板文件...'})
            
            shutil.copy(template_path, output_path)
            
            # 5. 如果大纲页数 > 模板页数，需要克隆幻灯片
            if outline_slide_count > template_slide_count:
                if progress_callback:
                    progress_callback({'progress': 20, 'message': '扩展模板页数...'})
                
                # 找到最适合克隆的内容页（通常是第2页或倒数第2页）
                clone_source = min(2, template_slide_count) if template_slide_count >= 2 else 1
                
                for i in range(template_slide_count, outline_slide_count):
                    logger.info(f"[MCP-PPT] 克隆第{clone_source}页到位置{i+1}")
                    self.clone_slide(output_path, clone_source)
                
                logger.info(f"[MCP-PPT] 扩展后页数: {self.get_slide_count(output_path)}")
            
            # 6. 生成占位符数据
            if progress_callback:
                progress_callback({'progress': 30, 'message': '生成填充数据...'})
            
            # 调用GLM服务生成适配模板的内容
            from app.services.glm_service import adapt_content_to_template_placeholders
            
            # 构建placeholders_by_slide格式
            placeholders_by_slide = []
            for p in placeholders_info:
                placeholders_by_slide.append({
                    'slide_index': p['slide_index'] - 1,  # 转为0-based
                    'placeholders': ['{{' + ph + '}}' for ph in p['placeholders']]
                })
            
            # 如果模板没有占位符，使用默认占位符
            if not placeholders_by_slide:
                # 为每页生成默认占位符
                for i in range(outline_slide_count):
                    placeholders_by_slide.append({
                        'slide_index': i,
                        'placeholders': ['{{title}}', '{{text}}', '{{description}}']
                    })
            
            template_info = {
                'slide_count': max(template_slide_count, outline_slide_count),
                'placeholders_by_slide': placeholders_by_slide
            }
            
            # 调用GLM生成适配内容
            adapted_content = adapt_content_to_template_placeholders(
                topic=title,
                outline=outline,
                requirements=requirements,
                conversation_history=[],
                placeholders_by_slide=placeholders_by_slide,
                template_info=template_info
            )
            
            # 7. 构建merge数据
            if progress_callback:
                progress_callback({'progress': 50, 'message': '填充模板数据...'})
            
            merge_data = {}
            merge_data['title'] = title
            merge_data['subtitle'] = f"{requirements.get('audience', '')} | {requirements.get('purpose', '')}"
            merge_data['date'] = datetime.now().strftime('%Y-%m-%d')
            merge_data['footer'] = title
            
            # 从适配内容中提取数据
            for slide in adapted_content.get('slides', []):
                slide_idx = slide.get('slide_index', 0)
                values = slide.get('values', {})
                
                for key, value in values.items():
                    # 清理key格式
                    clean_key = key.replace('{{', '').replace('}}', '').strip()
                    merge_data[clean_key] = value
            
            # 添加大纲内容
            for idx, slide in enumerate(outline_slides):
                slide_num = idx + 1
                merge_data[f'slide{slide_num}_title'] = slide.get('title', '')
                content_points = slide.get('content_points', [])
                merge_data[f'slide{slide_num}_text'] = '\n'.join([f'• {p}' for p in content_points])
            
            logger.info(f"[MCP-PPT] Merge数据: {json.dumps(merge_data, ensure_ascii=False)[:500]}")
            
            # 8. 使用OfficeCLI merge命令
            if progress_callback:
                progress_callback({'progress': 60, 'message': '执行模板合并...'})
            
            # 直接使用batch命令逐页设置内容（更灵活）
            # 开启驻留模式
            open_result = self.open_document(output_path)
            use_resident = open_result.get('success', False)
            
            # 逐页填充内容
            for slide_idx, slide in enumerate(outline_slides):
                slide_num = slide_idx + 1
                slide_title = slide.get('title', '')
                content_points = slide.get('content_points', [])
                
                if progress_callback:
                    progress = 60 + int((slide_idx / outline_slide_count) * 25)
                    progress_callback({
                        'progress': progress,
                        'message': f'填充第{slide_num}/{outline_slide_count}页...'
                    })
                
                # 构建该页的设置命令
                commands = []
                
                # 设置标题（假设第一个shape是标题）
                commands.append({
                    "command": "set",
                    "path": f"/slide[{slide_num}]/shape[1]",
                    "props": {"text": slide_title}
                })
                
                # 设置内容（假设第二个shape是内容）
                if content_points:
                    content_text = '\n'.join([f'• {p}' for p in content_points[:5]])  # 最多5个要点
                    commands.append({
                        "command": "set",
                        "path": f"/slide[{slide_num}]/shape[2]",
                        "props": {"text": content_text}
                    })
                
                # 批量执行
                if commands:
                    batch_result = self.batch_execute(output_path, commands)
                    if not batch_result.get('success'):
                        logger.warning(f"[MCP-PPT] 第{slide_num}页填充失败: {batch_result.get('error')}")
            
            # 关闭驻留模式
            if use_resident:
                self.close_document(output_path)
            
            # 9. 验证
            if progress_callback:
                progress_callback({'progress': 90, 'message': '验证PPT...'})
            
            valid, stdout, stderr = self.validate_ppt(output_path)
            slide_count = self.get_slide_count(output_path)
            
            logger.info(f"[MCP-PPT] 验证结果: valid={valid}, slide_count={slide_count}")
            
            # 10. 修复问题
            if not valid:
                if progress_callback:
                    progress_callback({'progress': 92, 'message': '修复问题...'})
                
                issues = self.view_issues(output_path, limit=10)
                for issue in issues[:5]:
                    try:
                        self._fix_single_issue(output_path, issue, title, 1)
                    except Exception as e:
                        logger.warning(f"[MCP-PPT] 修复失败: {e}")
            
            if progress_callback:
                progress_callback({'progress': 100, 'message': 'PPT生成完成！'})
            
            logger.info(f"[MCP-PPT] ========== 模板PPT生成完成 ==========")
            
            return {
                'success': True,
                'file_path': output_path,
                'total_slides': slide_count,
                'validation': {'valid': valid, 'message': stdout if valid else stderr},
                'protocol': 'MCP_TEMPLATE_MERGE',
                'template_path': template_path
            }
            
        except Exception as e:
            logger.error(f"[MCP-PPT] 模板生成失败: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def _generate_ppt_with_llm(self,
                               output_path: str,
                               title: str,
                               outline: Dict,
                               requirements: Dict = None,
                               style_theme: str = None,
                               image_service = None,
                               progress_callback: Callable = None,
                               compact_dialogue: str = '',
                               compact_context: str = '') -> Dict:
        """
        使用LLM生成PPT内容，通过MCP协议执行
        
        优化版本（逐页生成 + 逐页执行 + 逐页QA + 整体验证）：
        1. 使用驻留模式(open/close)避免重复I/O
        2. 逐页生成命令、逐页执行（每页内使用batch批量执行）
        3. 逐页QA验证和修复优化
        4. 最后进行整体验证优化修改
        """
        from app.services.glm_service import (
            generate_single_slide_commands,
            review_and_fix_slide_commands
        )
        
        requirements = requirements or {}
        slides = outline.get('slides', [])
        total_slides = len(slides)
        
        if total_slides == 0:
            return {'success': False, 'error': '大纲为空，无法生成PPT'}
        
        # 估算总命令数，决定是否使用驻留模式
        estimated_commands = total_slides * 15  # 平均每页约15条命令
        use_resident_mode = self._should_use_resident_mode(estimated_commands)
        
        try:
            # 1. 通过MCP创建空白PPT
            if progress_callback:
                progress_callback({'progress': 5, 'message': '通过MCP创建PPT文件...'})
            
            if not self.create_ppt(output_path):
                raise RuntimeError("通过MCP创建PPT文件失败")
            
            # 2. 如果使用驻留模式，打开文档
            if use_resident_mode:
                if progress_callback:
                    progress_callback({'progress': 8, 'message': '开启驻留模式...'})
                
                open_result = self.open_document(output_path)
                if not open_result.get('success'):
                    logger.warning(f"[MCP-PPT] 驻留模式开启失败，继续使用普通模式: {open_result.get('error')}")
                    use_resident_mode = False
                else:
                    logger.info(f"[MCP-PPT] ========== 驻留模式已开启 ==========")
            
            logger.info(f"[MCP-PPT] ========== 开始生成PPT（逐页生成 + 逐页执行 + 逐页QA）==========")
            logger.info(f"[MCP-PPT] 主题: {title}, 总页数: {total_slides}, 驻留模式: {use_resident_mode}")
            
            # 3. 提取AI生成的文字大纲内容
            ai_outline_content = self._extract_ai_outline_content(outline)
            
            # 4. 逐页生成、逐页执行、逐页QA验证
            total_commands = 0
            success_count = 0
            fail_count = 0
            slide_qa_results = []  # 逐页QA结果
            
            for slide_idx, slide_info in enumerate(slides):
                slide_num = slide_idx + 1
                slide_title = slide_info.get('title', f'第{slide_num}页')
                
                # 计算进度（预留10%给最终验证）
                base_progress = 10
                progress_per_slide = 80 / total_slides
                current_progress = int(base_progress + (slide_idx * progress_per_slide))
                
                # 4.1 逐页生成命令
                if progress_callback:
                    progress_callback({
                        'progress': current_progress,
                        'message': f'生成第{slide_num}/{total_slides}页: {slide_title}...'
                    })
                
                logger.info(f"[MCP-PPT] Step 1: 生成第{slide_num}页命令...")
                
                try:
                    slide_result = generate_single_slide_commands(
                        topic=title,
                        slide_index=slide_num,
                        total_slides=total_slides,
                        requirements=requirements,
                        style_theme=style_theme,
                        compact_dialogue=compact_dialogue,
                        compact_context=compact_context,
                        slide_title=slide_title,
                        slide_content=slide_info.get('content_points', []),
                        ai_outline_content=ai_outline_content
                    )
                except Exception as e:
                    logger.error(f"[MCP-PPT] 第{slide_num}页命令生成失败: {e}")
                    continue
                
                commands = slide_result.get('commands', [])
                if not commands:
                    logger.warning(f"[MCP-PPT] 第{slide_num}页没有生成命令，跳过")
                    continue
                
                logger.info(f"[MCP-PPT] 第{slide_num}页生成完成，共{len(commands)}条命令")
                
                # 4.2 逐页执行命令（使用batch模式）
                if progress_callback:
                    progress_callback({
                        'progress': current_progress + 1,
                        'message': f'执行第{slide_num}/{total_slides}页命令...'
                    })
                
                logger.info(f"[MCP-PPT] Step 2: 批量执行第{slide_num}页命令...")
                
                batch_result = self._execute_slide_batch_with_qa(
                    output_path, commands, slide_num, title, 
                    enable_qa=True  # 启用逐页QA
                )
                success_count += batch_result.get('success', 0)
                fail_count += batch_result.get('fail', 0)
                total_commands += len(commands)
                
                # 4.3 逐页QA验证和修复
                qa_result = batch_result.get('qa_result')
                if qa_result:
                    slide_qa_results.append({
                        'slide_num': slide_num,
                        'qa': qa_result
                    })
                    
                    # 如果QA未通过，尝试修复该页
                    if not qa_result.get('passed'):
                        logger.warning(f"[MCP-PPT] 第{slide_num}页QA未通过: {qa_result.get('issues')}")
                        
                        if progress_callback:
                            progress_callback({
                                'progress': current_progress + 2,
                                'message': f'修复优化第{slide_num}页...'
                            })
                        
                        # 尝试修复该页问题
                        fix_result = self._fix_slide_issues(
                            output_path, slide_num, qa_result.get('issues', []), 
                            title, slide_title
                        )
                        logger.info(f"[MCP-PPT] 第{slide_num}页修复结果: {fix_result}")
            
            # 5. 最终整体验证优化
            if progress_callback:
                progress_callback({'progress': 90, 'message': '正在进行最终验证优化...'})
            
            logger.info(f"[MCP-PPT] ========== 最终整体验证优化 ==========")
            valid, stdout, stderr = self.validate_ppt(output_path)
            slide_count = self.get_slide_count(output_path)
            
            # 6. 整体问题修复优化
            if not valid or slide_count != total_slides:
                logger.warning(f"[MCP-PPT] 整体验证发现问题: valid={valid}, 预期{total_slides}页, 实际{slide_count}页")
                
                if progress_callback:
                    progress_callback({'progress': 92, 'message': '正在进行整体修复优化...'})
                
                # 多轮整体修复
                for fix_round in range(3):
                    issues = self.view_issues(output_path, limit=15)
                    if not issues:
                        break
                    logger.info(f"[MCP-PPT] 整体修复轮次{fix_round + 1}，发现{len(issues)}个问题")
                    for issue in issues[:5]:
                        try:
                            self._fix_single_issue(output_path, issue, title, fix_round + 1)
                        except Exception as e:
                            logger.warning(f"[MCP-PPT] 修复失败: {e}")
                
                # 重新验证
                valid, stdout, stderr = self.validate_ppt(output_path)
                slide_count = self.get_slide_count(output_path)
            
            # 7. 整体设计质量检查和优化
            if progress_callback:
                progress_callback({'progress': 95, 'message': '整体设计质量检查...'})
            
            # 构建all_slides用于质量检查
            all_slides = [{'slide_index': i+1, 'commands': []} for i in range(total_slides)]
            quality_result = self._check_design_quality(output_path, title, all_slides)
            
            # 如果有设计问题，尝试优化
            if quality_result.get('issues'):
                logger.info(f"[MCP-PPT] 发现{len(quality_result['issues'])}个设计问题，尝试优化")
                self._fix_design_issues(output_path, quality_result['issues'], title)
            
            # 8. 关闭文档（驻留模式）
            if use_resident_mode:
                self.close_document(output_path)
                logger.info(f"[MCP-PPT] ========== 驻留模式已关闭 ==========")
            
            logger.info(f"[MCP-PPT] ========== PPT生成完成 ==========")
            logger.info(f"[MCP-PPT] 总命令数: {total_commands}, 成功: {success_count}, 失败: {fail_count}")
            logger.info(f"[MCP-PPT] 验证结果: valid={valid}, slide_count={slide_count}")
            logger.info(f"[MCP-PPT] 逐页QA结果: {len(slide_qa_results)}页已验证")
            
            if progress_callback:
                progress_callback({'progress': 100, 'message': 'PPT生成完成！'})
            
            return {
                'success': True,
                'file_path': output_path,
                'total_slides': slide_count,
                'validation': {'valid': valid, 'message': stdout if valid else stderr},
                'commands_used': total_commands,
                'commands_success': success_count,
                'commands_failed': fail_count,
                'protocol': 'MCP_RESIDENT_PAGE_BY_PAGE' if use_resident_mode else 'MCP_PAGE_BY_PAGE',
                'quality_check': quality_result,
                'progressive_qa': {
                    'enabled': True,
                    'mode': 'page_by_page',
                    'slides_verified': len(slide_qa_results),
                    'results': slide_qa_results
                }
            }
            
        except Exception as e:
            logger.error(f"[MCP-PPT] PPT生成失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 确保关闭文档
            if use_resident_mode:
                try:
                    self.close_document(output_path)
                except:
                    pass
            
            return {'success': False, 'error': str(e)}
    
    def _execute_slide_batch_with_qa(self, ppt_path: str, commands: list, 
                                      slide_num: int, topic: str,
                                      enable_qa: bool = True) -> Dict:
        """
        使用batch模式执行单页幻灯片命令，并支持渐进式QA
        
        Args:
            ppt_path: PPT文件路径
            commands: 命令列表
            slide_num: 幻灯片编号
            topic: 主题
            enable_qa: 是否启用渐进式QA
            
        Returns:
            {'success': int, 'fail': int, 'qa_result': dict}
        """
        commands = self._normalize_slide_commands(commands, slide_num)
        logger.info(f"[MCP-PPT] 批量执行第{slide_num}页，{len(commands)}条命令（batch模式）")
        
        # 使用MCP batch命令一次性执行
        batch_result = self.batch_execute(ppt_path, commands)
        
        success_count = 0
        fail_count = 0
        
        if batch_result.get('success'):
            # 解析batch执行结果
            data = batch_result.get('data', {})
            if isinstance(data, dict):
                success_count = data.get('success', len(commands))
                fail_count = data.get('fail', 0)
            elif isinstance(data, str):
                # 尝试解析结果字符串
                if 'success' in data.lower():
                    success_count = len(commands)
                else:
                    success_count = len(commands) // 2
                    fail_count = len(commands) - success_count
            else:
                success_count = len(commands)
        else:
            # batch失败，回退到逐条执行
            logger.warning(f"[MCP-PPT] Batch执行失败，回退到逐条执行: {batch_result.get('error')}")
            for cmd in commands:
                result = self._execute_single_command_via_mcp(ppt_path, cmd)
                if result.get('success'):
                    success_count += 1
                else:
                    fail_count += 1
        
        # 渐进式QA：验证该页是否正确生成
        qa_result = None
        if enable_qa:
            qa_result = self._qa_single_slide(ppt_path, slide_num, commands, topic)
            if not qa_result.get('passed'):
                logger.warning(f"[MCP-PPT] 第{slide_num}页QA未通过: {qa_result.get('issues')}")
        
        return {
            'success': success_count,
            'fail': fail_count,
            'qa_result': qa_result
        }
    
    def _qa_single_slide(self, ppt_path: str, slide_num: int, 
                          commands: list, topic: str) -> Dict:
        """
        渐进式QA：验证单页幻灯片
        
        检查项：
        1. 幻灯片是否存在
        2. 幻灯片结构是否正确
        3. 是否有明显的错误
        
        Args:
            ppt_path: PPT文件路径
            slide_num: 幻灯片编号
            commands: 执行的命令列表
            topic: 主题
            
        Returns:
            {'passed': bool, 'issues': list, 'structure': dict}
        """
        issues = []
        
        try:
            # 1. 获取幻灯片结构
            structure = self.get_slide_structure(ppt_path, slide_num)
            
            if not structure:
                # 结构为空，可能幻灯片不存在
                slide_count = self.get_slide_count(ppt_path)
                if slide_count < slide_num:
                    issues.append(f"幻灯片不存在：预期第{slide_num}页，实际只有{slide_count}页")
                else:
                    issues.append(f"无法获取第{slide_num}页结构")
            
            # 2. 检查是否有足够的元素
            if structure:
                children = structure.get('children', [])
                expected_elements = len(commands) - 1  # 减去创建slide的命令
                actual_elements = len(children)
                
                # 如果元素数量远少于预期，可能有问题
                if actual_elements < expected_elements * 0.5:
                    issues.append(f"元素数量不足：预期约{expected_elements}个，实际{actual_elements}个")
            
            # 3. 检查该幻灯片是否有问题
            all_issues = self.view_issues(ppt_path, limit=20)
            slide_issues = [i for i in all_issues if i.get('slide_index') == slide_num]
            if slide_issues:
                issues.extend([i.get('message', '')[:50] for i in slide_issues[:3]])
            
            passed = len(issues) == 0
            
            if passed:
                logger.debug(f"[MCP-PPT] 第{slide_num}页QA通过")
            else:
                logger.warning(f"[MCP-PPT] 第{slide_num}页QA发现问题: {issues}")
            
            return {
                'passed': passed,
                'issues': issues,
                'structure': structure
            }
            
        except Exception as e:
            logger.error(f"[MCP-PPT] QA检查异常: {e}")
            return {
                'passed': False,
                'issues': [f"QA检查异常: {str(e)}"],
                'structure': {}
            }
    
    def _generate_ppt_page_by_page_with_resident(self,
                                                  output_path: str,
                                                  title: str,
                                                  outline: Dict,
                                                  requirements: Dict = None,
                                                  style_theme: str = None,
                                                  image_service = None,
                                                  progress_callback: Callable = None,
                                                  compact_dialogue: str = '',
                                                  compact_context: str = '',
                                                  use_resident_mode: bool = False) -> Dict:
        """
        逐页生成PPT（支持驻留模式）
        """
        from app.services.glm_service import generate_single_slide_commands
        
        requirements = requirements or {}
        slides = outline.get('slides', [])
        total_slides = len(slides)
        
        logger.info(f"[MCP-PPT] 使用逐页生成模式（驻留={use_resident_mode}），共{total_slides}页")
        
        total_commands = 0
        success_count = 0
        fail_count = 0
        slide_qa_results = []
        
        for slide_idx, slide_data in enumerate(slides):
            slide_num = slide_idx + 1
            slide_title = slide_data.get('title', f'第{slide_num}页')
            
            base_progress = 10
            progress_per_slide = 80 / total_slides
            current_progress = int(base_progress + (slide_idx * progress_per_slide))
            
            if progress_callback:
                progress_callback({
                    'progress': current_progress,
                    'message': f'生成第{slide_num}/{total_slides}页: {slide_title}...'
                })
            
            try:
                slide_result = generate_single_slide_commands(
                    topic=title,
                    slide_index=slide_num,
                    total_slides=total_slides,
                    requirements=requirements,
                    style_theme=style_theme,
                    compact_dialogue=compact_dialogue,
                    compact_context=compact_context
                )
                
                commands = slide_result.get('commands', [])
                if not commands:
                    continue
                
                # 使用batch模式执行
                batch_result = self._execute_slide_batch_with_qa(
                    output_path, commands, slide_num, title,
                    enable_qa=True
                )
                success_count += batch_result.get('success', 0)
                fail_count += batch_result.get('fail', 0)
                total_commands += len(commands)
                
                if batch_result.get('qa_result'):
                    slide_qa_results.append({
                        'slide_num': slide_num,
                        'qa': batch_result['qa_result']
                    })
                
            except Exception as e:
                logger.error(f"[MCP-PPT] 第{slide_num}页生成失败: {e}")
        
        # 关闭文档
        if use_resident_mode:
            self.close_document(output_path)
        
        # 验证
        valid, stdout, stderr = self.validate_ppt(output_path)
        slide_count = self.get_slide_count(output_path)
        
        if progress_callback:
            progress_callback({'progress': 100, 'message': 'PPT生成完成！'})
        
        return {
            'success': True,
            'file_path': output_path,
            'total_slides': slide_count,
            'validation': {'valid': valid, 'message': stdout if valid else stderr},
            'commands_used': total_commands,
            'commands_success': success_count,
            'commands_failed': fail_count,
            'protocol': 'MCP_RESIDENT_FALLBACK' if use_resident_mode else 'MCP_FALLBACK',
            'progressive_qa': {
                'enabled': True,
                'slides_verified': len(slide_qa_results),
                'results': slide_qa_results
            }
        }
    
    def _generate_ppt_page_by_page(self,
                                   output_path: str,
                                   title: str,
                                   outline: Dict,
                                   requirements: Dict = None,
                                   style_theme: str = None,
                                   image_service = None,
                                   progress_callback: Callable = None,
                                   compact_dialogue: str = '',
                                   compact_context: str = '') -> Dict:
        """
        逐页生成PPT（回退方案）
        """
        from app.services.glm_service import generate_single_slide_commands, review_and_fix_slide_commands
        
        requirements = requirements or {}
        slides = outline.get('slides', [])
        total_slides = len(slides)
        
        logger.info(f"[MCP-PPT] 使用逐页生成模式，共{total_slides}页")
        
        total_commands = 0
        success_count = 0
        fail_count = 0
        
        for slide_idx, slide_data in enumerate(slides):
            slide_num = slide_idx + 1
            slide_title = slide_data.get('title', f'第{slide_num}页')
            
            base_progress = 10
            progress_per_slide = 80 / total_slides
            current_progress = int(base_progress + (slide_idx * progress_per_slide))
            
            if progress_callback:
                progress_callback({
                    'progress': current_progress,
                    'message': f'生成第{slide_num}/{total_slides}页: {slide_title}...'
                })
            
            try:
                slide_result = generate_single_slide_commands(
                    topic=title,
                    slide_index=slide_num,
                    total_slides=total_slides,
                    requirements=requirements,
                    style_theme=style_theme,
                    compact_dialogue=compact_dialogue,
                    compact_context=compact_context
                )
                
                commands = slide_result.get('commands', [])
                if not commands:
                    continue
                
                batch_result = self._execute_commands_via_mcp(output_path, commands, slide_num)
                success_count += batch_result.get('success', 0)
                fail_count += batch_result.get('fail', 0)
                total_commands += len(commands)
                
            except Exception as e:
                logger.error(f"[MCP-PPT] 第{slide_num}页生成失败: {e}")
        
        # 验证
        valid, stdout, stderr = self.validate_ppt(output_path)
        slide_count = self.get_slide_count(output_path)
        
        if progress_callback:
            progress_callback({'progress': 100, 'message': 'PPT生成完成！'})
        
        return {
            'success': True,
            'file_path': output_path,
            'total_slides': slide_count,
            'validation': {'valid': valid, 'message': stdout if valid else stderr},
            'commands_used': total_commands,
            'commands_success': success_count,
            'commands_failed': fail_count,
            'protocol': 'MCP_FALLBACK'
        }
    
    def _extract_ai_outline_content(self, outline: Dict) -> str:
        """
        从大纲中提取AI生成的文字内容（完整内容，不截断）
        """
        content_parts = []
        
        slides = outline.get('slides', [])
        for slide in slides:
            slide_num = slide.get('slide_number', 0)
            title = slide.get('title', '')
            content_points = slide.get('content_points', [])
            
            content_parts.append(f"第{slide_num}页：{title}")
            for point in content_points:
                content_parts.append(f"  - {point}")
            content_parts.append("")  # 空行分隔
        
        return "\n".join(content_parts)
    
    def _validate_content_allocation(self, all_slides: list, outline: Dict, topic: str) -> Dict:
        """
        验证内容分配是否正确
        
        检查项：
        1. 页数是否完整
        2. 每页标题是否与大纲对应
        3. 每页命令数量是否足够
        4. 内容是否正确分配（而非所有页面使用相同内容）
        """
        issues = []
        outline_slides = outline.get('slides', [])
        
        # 1. 检查页数
        expected_count = len(outline_slides)
        actual_count = len(all_slides)
        
        if actual_count < expected_count:
            issues.append(f"页数不足：预期{expected_count}页，实际{actual_count}页")
        
        # 2. 检查每页内容
        texts_by_slide = {}  # 每页的文本内容
        
        for slide in all_slides:
            slide_index = slide.get('slide_index', 0)
            commands = slide.get('commands', [])
            
            # 提取该页所有文本
            texts = []
            for cmd in commands:
                props = cmd.get('props', {})
                text = props.get('text', '')
                if text and len(text) > 1:
                    texts.append(text[:50])  # 只取前50字符
            
            texts_by_slide[slide_index] = texts
            
            # 检查命令数量
            if slide_index == 1:  # 封面
                if len(commands) < 8:
                    issues.append(f"第{slide_index}页(封面)命令数量不足: {len(commands)}条")
            elif slide_index == actual_count:  # 结尾
                if len(commands) < 6:
                    issues.append(f"第{slide_index}页(结尾)命令数量不足: {len(commands)}条")
            else:  # 内容页
                if len(commands) < 10:
                    issues.append(f"第{slide_index}页命令数量不足: {len(commands)}条")
        
        # 3. 检查内容是否重复（所有页面使用相同内容）
        if len(texts_by_slide) > 2:
            # 比较第2页和第3页的内容
            texts_2 = set(texts_by_slide.get(2, []))
            texts_3 = set(texts_by_slide.get(3, []))
            
            if texts_2 and texts_3:
                overlap = texts_2 & texts_3
                if len(overlap) > len(texts_2) * 0.7:  # 70%以上重复
                    issues.append(f"内容分配问题：第2页和第3页内容高度重复({len(overlap)}条相同)")
        
        # 4. 检查是否与大纲标题对应
        for slide in all_slides:
            slide_index = slide.get('slide_index', 0)
            commands = slide.get('commands', [])
            
            if slide_index <= len(outline_slides):
                expected_title = outline_slides[slide_index - 1].get('title', '')
                
                # 在命令中查找标题
                found_title = False
                for cmd in commands:
                    props = cmd.get('props', {})
                    text = props.get('text', '')
                    if expected_title and expected_title[:10] in text:
                        found_title = True
                        break
                
                if expected_title and not found_title and slide_index > 1:
                    issues.append(f"第{slide_index}页未找到大纲标题: {expected_title[:20]}")
        
        # 判断是否需要重新生成
        need_regenerate = False
        if len(issues) >= 3:  # 3个以上问题
            need_regenerate = True
        if any('内容高度重复' in issue for issue in issues):  # 内容重复
            need_regenerate = True
        if actual_count < expected_count * 0.8:  # 页数不足80%
            need_regenerate = True
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'need_regenerate': need_regenerate,
            'expected_slides': expected_count,
            'actual_slides': actual_count
        }
    
    def _fix_slide_issues(self, ppt_path: str, slide_num: int, issues: list, 
                          topic: str, slide_title: str) -> Dict:
        """
        修复单页幻灯片的问题（逐页QA修复）
        
        Args:
            ppt_path: PPT文件路径
            slide_num: 幻灯片编号
            issues: 问题列表
            topic: 主题
            slide_title: 幻灯片标题
            
        Returns:
            {'success': bool, 'fixed_count': int, 'failed_count': int}
        """
        from app.services.glm_service import generate_single_slide_commands
        
        logger.info(f"[MCP-PPT] 开始修复第{slide_num}页，共{len(issues)}个问题")
        
        fixed_count = 0
        failed_count = 0
        
        for issue in issues:
            try:
                # 尝试直接修复简单问题
                if isinstance(issue, str):
                    issue_msg = issue
                else:
                    issue_msg = issue.get('message', str(issue))
                
                # 1. 幻灯片不存在 - 需要重新生成
                if '幻灯片不存在' in issue_msg or '不存在' in issue_msg:
                    logger.info(f"[MCP-PPT] 第{slide_num}页不存在，尝试重新生成")
                    # 这里无法单独修复，需要在整体验证时处理
                    failed_count += 1
                    continue
                
                # 2. 元素数量不足 - 尝试添加更多元素
                if '元素数量不足' in issue_msg:
                    logger.info(f"[MCP-PPT] 第{slide_num}页元素不足，尝试补充")
                    # 获取当前结构
                    structure = self.get_slide_structure(ppt_path, slide_num)
                    if structure:
                        # 添加一个补充文本框
                        self.add_shape(ppt_path, slide_num, 'shape', {
                            'type': 'text',
                            'text': f'• 补充内容',
                            'x': '2cm',
                            'y': '10cm',
                            'width': '15cm',
                            'height': '1cm',
                            'color': '#666666'
                        })
                        fixed_count += 1
                        continue
                
                # 3. 渐变背景问题
                if 'gradient' in issue_msg.lower() or '渐变' in issue_msg:
                    self.set_element(ppt_path, f"/slide[{slide_num}]", {"background": "#FFFFFF"})
                    fixed_count += 1
                    continue
                
                # 4. 坐标问题
                if 'coordinate' in issue_msg.lower() or '坐标' in issue_msg or 'negative' in issue_msg.lower():
                    # 简化处理：设置一个安全的背景
                    self.set_element(ppt_path, f"/slide[{slide_num}]", {"background": "#FFFFFF"})
                    fixed_count += 1
                    continue
                
                # 5. 其他问题 - 尝试通用修复
                logger.warning(f"[MCP-PPT] 第{slide_num}页未知问题类型: {issue_msg[:50]}")
                failed_count += 1
                
            except Exception as e:
                logger.error(f"[MCP-PPT] 修复第{slide_num}页问题时出错: {e}")
                failed_count += 1
        
        logger.info(f"[MCP-PPT] 第{slide_num}页修复完成: 修复{fixed_count}个, 失败{failed_count}个")
        
        return {
            'success': fixed_count > 0 or len(issues) == 0,
            'fixed_count': fixed_count,
            'failed_count': failed_count
        }
    
    def _fix_single_issue(self, ppt_path: str, issue: Dict, topic: str, round_num: int) -> bool:
        """
        修复单个问题（整体验证时使用）
        """
        issue_type = issue.get('type', '')
        issue_msg = issue.get('message', '')
        slide_index = issue.get('slide_index', 0)
        
        logger.info(f"[MCP-PPT] 修复问题: type={issue_type}, slide={slide_index}, msg={issue_msg[:50]}")
        
        # 根据问题类型执行修复
        if 'background' in issue_msg.lower() and 'gradient' in issue_msg.lower():
            # 渐变背景问题，替换为纯色
            return self.set_element(ppt_path, f"/slide[{slide_index}]", {"background": "#FFFFFF"})
        
        if 'coordinate' in issue_msg.lower() or 'negative' in issue_msg.lower():
            # 坐标问题，需要更详细的修复
            # 这里简化处理，实际应该调用LLM修复
            pass
        
        return False
    
    def _check_design_quality(self, ppt_path: str, title: str, all_slides: list) -> Dict:
        """
        检查PPT设计质量
        
        检查项：
        1. 页面命令数量（是否足够丰富）
        2. 配色一致性
        3. 布局合理性
        """
        issues = []
        
        # 检查每页命令数量
        for slide in all_slides:
            slide_index = slide.get('slide_index', 0)
            commands = slide.get('commands', [])
            
            if slide_index == 1:  # 封面
                if len(commands) < 10:
                    issues.append({
                        'type': 'design',
                        'slide_index': slide_index,
                        'message': f'封面页命令数量不足({len(commands)}条)，建议至少15条'
                    })
            elif slide_index == len(all_slides):  # 结尾页
                if len(commands) < 8:
                    issues.append({
                        'type': 'design',
                        'slide_index': slide_index,
                        'message': f'结尾页命令数量不足({len(commands)}条)，建议至少12条'
                    })
            else:  # 内容页
                if len(commands) < 12:
                    issues.append({
                        'type': 'design',
                        'slide_index': slide_index,
                        'message': f'内容页命令数量不足({len(commands)}条)，建议至少20条'
                    })
        
        # 检查配色一致性
        colors_used = set()
        for slide in all_slides:
            for cmd in slide.get('commands', []):
                props = cmd.get('props', {})
                for key in ['color', 'background', 'line_color']:
                    if key in props:
                        colors_used.add(props[key])
        
        # 如果使用了太多不同的颜色，可能不一致
        if len(colors_used) > 15:
            issues.append({
                'type': 'design',
                'slide_index': 0,
                'message': f'使用了{len(colors_used)}种不同颜色，建议控制在8种以内以保持风格统一'
            })
        
        return {
            'issues': issues,
            'colors_used': list(colors_used),
            'total_slides': len(all_slides)
        }
    
    def _fix_design_issues(self, ppt_path: str, issues: list, topic: str):
        """
        修复设计问题
        """
        from app.services.glm_service import generate_single_slide_commands
        
        for issue in issues:
            slide_index = issue.get('slide_index', 0)
            if slide_index == 0:
                continue  # 全局问题，跳过
            
            logger.info(f"[MCP-PPT] 尝试修复设计问题: slide={slide_index}")
            
            try:
                # 重新生成该页
                slide_result = generate_single_slide_commands(
                    topic=topic,
                    slide_index=slide_index,
                    total_slides=slide_index,  # 这里需要实际总数
                    requirements={'enhanced': True, 'min_commands': 20}
                )
                
                commands = slide_result.get('commands', [])
                if commands:
                    self._execute_commands_via_mcp(ppt_path, commands, slide_index)
                    
            except Exception as e:
                logger.warning(f"[MCP-PPT] 修复设计问题失败: {e}")
    
    def _execute_commands_via_mcp(self, ppt_path: str, commands: list, slide_num: int) -> Dict:
        """通过MCP协议执行JSON命令列表"""
        success_count = 0
        fail_count = 0
        
        commands = self._normalize_slide_commands(commands, slide_num)
        logger.info(f"[MCP-PPT] 通过MCP执行 {len(commands)} 条规范化命令")
        
        for cmd_idx, cmd in enumerate(commands):
            if not isinstance(cmd, dict):
                continue
            
            try:
                result = self._execute_single_command_via_mcp(ppt_path, cmd)
                
                if result.get("success"):
                    success_count += 1
                    logger.debug(f"[MCP-PPT] MCP命令成功 [{slide_num}-{cmd_idx}]")
                else:
                    fail_count += 1
                    logger.warning(f"[MCP-PPT] MCP命令失败 [{slide_num}-{cmd_idx}]: {result.get('error', '')[:100]}")
                    
            except Exception as e:
                fail_count += 1
                logger.warning(f"[MCP-PPT] MCP命令异常 [{slide_num}-{cmd_idx}]: {e}")
        
        logger.info(f"[MCP-PPT] 第{slide_num}页MCP执行完成: 成功 {success_count}, 失败 {fail_count}")
        return {'success': success_count, 'fail': fail_count}
    
    def _execute_single_command_via_mcp(self, ppt_path: str, cmd: dict) -> Dict:
        """通过MCP执行单条命令"""
        if not isinstance(cmd, dict):
            return {"success": False, "error": "无效命令格式"}
        
        client = self._ensure_mcp_client()
        
        command = cmd.get('command', 'add')
        path = cmd.get('path', '/')
        element_type = cmd.get('type', '')
        props = cmd.get('props', {})
        
        # 构建属性列表
        prop_list = []
        for k, v in props.items():
            prop_list.append(f"{k}={v}")
        
        # 根据命令类型构建MCP调用参数
        if command == 'add':
            return client.call_officecli({
                "command": "add",
                "file": ppt_path,
                "parent": path if path != '/' or element_type == 'slide' else path,
                "type": element_type,
                "props": prop_list
            })
        elif command == 'set':
            return client.call_officecli({
                "command": "set",
                "file": ppt_path,
                "path": path,
                "props": prop_list
            })
        elif command == 'remove':
            return client.call_officecli({
                "command": "remove",
                "file": ppt_path,
                "path": path
            })
        elif command == 'move':
            return client.call_officecli({
                "command": "move",
                "file": ppt_path,
                "path": path,
                "to": cmd.get('to', '')
            })
        else:
            return {"success": False, "error": f"未知命令: {command}"}
    
    def _normalize_slide_commands(self, commands: list, slide_num: int) -> list:
        """规范化单页命令"""
        normalized = []
        
        for cmd in (commands or []):
            if not isinstance(cmd, dict):
                continue
            c = dict(cmd)
            props = dict(c.get('props') or {})
            
            # 强制路径到当前页
            path = c.get('path', '/')
            if isinstance(path, str) and path.startswith('/slide['):
                c['path'] = f'/slide[{slide_num}]'
            
            # 禁止gradient背景
            bg = props.get('background')
            if isinstance(bg, str) and 'gradient' in bg.lower():
                props['background'] = '#1F2937'
            
            # 处理无效值
            if props.get('line_color') == 'none':
                props['line_color'] = 'transparent'
            if 'color' in props and isinstance(props['color'], str) and 'gradient' in props['color'].lower():
                props['color'] = '#111111'
            
            c['props'] = props
            normalized.append(c)
        
        # 确保第一条是创建slide
        has_create_slide = any(
            isinstance(c, dict) and c.get('command') == 'add' and c.get('path') == '/' and c.get('type') == 'slide'
            for c in normalized
        )
        if not has_create_slide:
            normalized.insert(0, {
                'command': 'add',
                'path': '/',
                'type': 'slide',
                'props': {'background': '#FFFFFF'}
            })
        
        return normalized
    
    def _parse_json_commands(self, json_text: str, ppt_path: str) -> list:
        """解析JSON命令文本为命令列表"""
        result = []
        
        # 尝试解析为JSON数组
        try:
            commands = json.loads(json_text)
            if isinstance(commands, list):
                return commands
            elif isinstance(commands, dict):
                return [commands]
        except json.JSONDecodeError:
            pass
        
        # 回退到解析bash命令格式
        for line in (json_text or '').split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # 替换deck.pptx为实际路径
            line = line.replace('deck.pptx', ppt_path)
            
            # 移除officecli前缀
            if line.startswith('officecli '):
                line = line[10:]
            
            # 解析命令行
            parts = self._parse_command_line(line)
            if parts:
                cmd = self._convert_args_to_json_cmd(parts)
                if cmd:
                    result.append(cmd)
        
        return result
    
    def _parse_command_line(self, line: str) -> list:
        """解析命令行为参数列表"""
        parts = []
        current = ''
        in_quote = False
        quote_char = None
        
        for char in line:
            if char in ('"', "'") and not in_quote:
                in_quote = True
                quote_char = char
            elif char == quote_char and in_quote:
                in_quote = False
                quote_char = None
            elif char == ' ' and not in_quote:
                if current:
                    parts.append(current)
                    current = ''
            else:
                current += char
        
        if current:
            parts.append(current)
        
        return parts
    
    def _convert_args_to_json_cmd(self, args: list) -> dict:
        """将命令行参数转换为JSON命令"""
        if not args:
            return None
        
        cmd = {
            'command': args[0],
            'path': args[2] if len(args) > 2 else '/',
            'props': {}
        }
        
        # 解析--type参数
        for i, arg in enumerate(args):
            if arg == '--type' and i + 1 < len(args):
                cmd['type'] = args[i + 1]
        
        # 解析--prop参数
        for i, arg in enumerate(args):
            if arg == '--prop' and i + 1 < len(args):
                prop_str = args[i + 1]
                if '=' in prop_str:
                    key, value = prop_str.split('=', 1)
                    cmd['props'][key] = value
        
        return cmd
    
    def cleanup(self):
        """清理资源"""
        self.stop_watch()
        if self.mcp_client:
            self.mcp_client.stop()
            self.mcp_client = None


# 全局实例
_officecli_mcp_service = None


def get_officecli_mcp_service() -> OfficeCLIMCPPTService:
    """获取OfficeCLI MCP服务实例"""
    global _officecli_mcp_service
    if _officecli_mcp_service is None:
        _officecli_mcp_service = OfficeCLIMCPPTService()
    return _officecli_mcp_service