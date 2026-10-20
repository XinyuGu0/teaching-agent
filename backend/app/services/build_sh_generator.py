"""
基于build.sh的PPT生成器
直接使用OfficeCLI的build.sh脚本，通过LLM转换命令并替换text属性
支持灵活的页数结构：1页封面 + N页内页 + 1页结尾
"""
import os
import json
import logging
import re
from typing import Dict, List, Any, Callable

logger = logging.getLogger(__name__)


class BuildShPPTGenerator:
    """基于build.sh的灵活页数PPT生成器"""
    
    def __init__(self):
        self.styles_dir = os.path.join(
            os.path.dirname(__file__), '..', '..',
            'OfficeCLI-main', 'examples', 'ppt', 'templates', 'styles'
        )
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """获取所有包含build.sh的可用模板（从硬编码配置中获取）"""
        from app.services.build_sh_templates import get_all_template_ids, get_template_metadata
        
        templates = []
        template_ids = get_all_template_ids()
        
        for dir_name in template_ids:
            try:
                metadata = get_template_metadata(dir_name)
                
                template_info = {
                    'id': f'builtin_{dir_name}',
                    'dir_name': dir_name,
                    'name': metadata.get('name', self._generate_display_name(dir_name)),
                    'template_type': 'builtin',
                    'background_color': metadata.get('background_color', 'FFFFFF'),
                    'font': metadata.get('font', '思源黑体'),
                    'category': metadata.get('category', 'general'),
                    'tags': metadata.get('tags', []),
                    'description': metadata.get('description', '')
                }
                
                templates.append(template_info)
                logger.info(f"[BuildShGenerator] Found template: {dir_name}")
            except Exception as e:
                logger.warning(f"[BuildShGenerator] Failed to load template {dir_name}: {e}")
        
        return templates
    
    def _parse_build_sh_metadata(self, build_sh_path: str, dir_name: str) -> Dict[str, Any]:
        """解析build.sh提取模板元数据"""
        with open(build_sh_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取文件名
        file_match = re.search(r'file_name\s*=\s*["\'](.+?)["\']', content)
        if not file_match:
            file_match = re.search(r'FILE\s*=\s*["\'](.+?)["\']', content)
        
        # 提取背景色
        bg_match = re.search(r'background[=:\s]+["\']?([A-Fa-f0-9]{6})', content)
        
        # 提取字体
        font_match = re.search(r'font["\']?\s*[:=]\s*["\']([^"\']+)["\']', content)
        
        # 生成显示名称
        name = self._generate_display_name(dir_name)
        
        return {
            'id': f'builtin_{dir_name}',
            'dir_name': dir_name,
            'name': name,
            'file_name': file_match.group(1) if file_match else f'{dir_name}.pptx',
            'build_sh_path': build_sh_path,
            'background_color': bg_match.group(1) if bg_match else 'FFFFFF',
            'font': font_match.group(1) if font_match else '思源黑体',
            'template_type': 'builtin'
        }
    
    def _generate_display_name(self, dir_name: str) -> str:
        """根据目录名生成显示名称"""
        # 分类映射
        category_map = {
            'science': '科学',
            'brand': '品牌',
            'product': '产品',
            'lifestyle': '生活',
            'productivity': '效率',
            'tech': '科技',
            'future': '未来'
        }
        
        # 分割目录名
        parts = dir_name.split('--')
        if len(parts) == 2:
            category, style = parts
            category_name = category_map.get(category, category)
            
            # 风格名称映射
            style_names = {
                'time-travel': '时间旅行',
                'alien-guide': '外星指南',
                'space-exploration': '太空探索',
                'aura-coffee': '咖啡美学',
                'aura-coffee-dark': '咖啡美学（深色）',
                'cat-philosophy': '猫咪哲学',
                'cat-secret-life': '猫咪秘密',
                'geminicli-timetravel': '时光穿梭',
                'attention-budget': '注意力预算',
                'wildlife-company': '野生动物',
                '2050-vision': '2050愿景'
            }
            
            style_name = style_names.get(style, style.replace('-', ' ').title())
            return f"{category_name} - {style_name}"
        
        return dir_name.replace('-', ' ').title()

    def read_build_sh(self, template_id: str) -> str:
        """读取指定内置模板的 build.sh 内容"""
        from app.services.build_sh_templates import get_build_sh_content

        normalized_id = template_id
        if normalized_id.startswith('builtin_builtin_'):
            normalized_id = normalized_id.replace('builtin_builtin_', 'builtin_', 1)
        if not normalized_id.startswith('builtin_'):
            normalized_id = f'builtin_{normalized_id}'

        build_sh = get_build_sh_content(normalized_id)
        if build_sh:
            return build_sh

        raise FileNotFoundError(f"无法读取模板build.sh: {template_id}")

    def get_available_templates(self) -> List[Dict[str, Any]]:
        """获取所有包含build.sh的可用模板（从硬编码配置中获取）"""
        from app.services.build_sh_templates import get_all_template_ids, get_template_metadata
        
        templates = []
        template_ids = get_all_template_ids()
        
        for dir_name in template_ids:
            try:
                metadata = get_template_metadata(dir_name)
                
                template_info = {
                    'id': f'builtin_{dir_name}',
                    'dir_name': dir_name,
                    'name': metadata.get('name', self._generate_display_name(dir_name)),
                    'template_type': 'builtin',
                    'background_color': metadata.get('background_color', 'FFFFFF'),
                    'font': metadata.get('font', '思源黑体'),
                    'category': metadata.get('category', 'general'),
                    'tags': metadata.get('tags', []),
                    'description': metadata.get('description', '')
                }
                
                templates.append(template_info)
                logger.info(f"[BuildShGenerator] Found template: {dir_name}")
            except Exception as e:
                logger.warning(f"[BuildShGenerator] Failed to load template {dir_name}: {e}")
        
        return templates
    
    def generate_with_llm(
        self, 
        template_id: str, 
        outline: Dict[str, Any], 
        output_path: str,
        progress_callback: Callable = None
    ) -> Dict[str, Any]:
        """使用LLM生成灵活页数的PPT"""
        
        try:
            # 1. 读取build.sh
            if progress_callback:
                progress_callback({'progress': 10, 'message': '读取模板文件...'})
            
            build_sh_content = self.read_build_sh(template_id)
            
            # 2. 分析大纲，确定页数
            slides = outline.get('slides', [])
            total_pages = 2 + len(slides)  # 封面 + N个内页 + 结尾
            
            logger.info(f"[BuildShGenerator] 总页数: {total_pages} (封面1 + 内页{len(slides)} + 结尾1)")
            logger.info(f"[BuildShGenerator] 大纲标题: {outline.get('title', '')}")
            
            # 3. 构建LLM提示词
            if progress_callback:
                progress_callback({'progress': 20, 'message': '分析内容结构...'})
            
            prompt = self._build_prompt(build_sh_content, outline, output_path, total_pages)
            
            # 4. 调用LLM
            if progress_callback:
                progress_callback({'progress': 30, 'message': '生成PPT命令...'})
            
            llm_response = self._call_llm(prompt)
            
            if not llm_response:
                raise RuntimeError("LLM返回空响应")
            
            logger.info(f"[BuildShGenerator] LLM响应长度: {len(llm_response)} 字符")
            
            # 5. 提取Python代码
            python_code = self._extract_python_code(llm_response)
            
            if not python_code:
                raise RuntimeError("无法从LLM响应中提取Python代码")
            
            logger.info(f"[BuildShGenerator] 提取的Python代码长度: {len(python_code)} 字符")
            
            # 6. 执行生成的代码
            if progress_callback:
                progress_callback({'progress': 60, 'message': f'正在生成PPT（共{total_pages}页）...'})
            
            page_status = self._execute_python_code(python_code, output_path, total_pages)
            
            # 7. 验证文件是否生成
            if not os.path.exists(output_path):
                raise RuntimeError(f"PPT文件未生成: {output_path}")
            
            if progress_callback:
                progress_callback({'progress': 100, 'message': f'PPT生成完成（共{total_pages}页）'})
            
            return {
                'success': True, 
                'file_path': output_path,
                'total_pages': total_pages,
                'page_status': page_status,  # 添加页面状态信息
                'python_code': python_code  # 返回代码用于调试
            }
            
        except FileNotFoundError as e:
            logger.error(f"[BuildShGenerator] 文件未找到: {e}")
            return {'success': False, 'error': f'模板文件缺失: {str(e)}'}
        except Exception as e:
            logger.error(f"[BuildShGenerator] 生成失败: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    def _build_prompt(
        self, 
        build_sh: str, 
        outline: Dict[str, Any], 
        output_path: str,
        total_pages: int
    ) -> str:
        """构建LLM提示词"""
        
        # 构建内页信息
        slides_info = ""
        for i, slide in enumerate(outline.get('slides', []), start=2):
            layout = slide.get('layout', 'auto')
            points = slide.get('content_points', [])
            slides_info += f"""
  第{i}页（内页）:
    - 标题: {slide.get('title', '')}
    - 要点: {', '.join(points) if points else '无'}
    - 布局建议: {layout}
"""
        
        prompt = f"""
你是一个PPT生成命令转换专家。请根据以下要求转换build.sh脚本：

【原始build.sh脚本】
```bash
{build_sh}
```

【用户大纲内容】
主题: {outline.get('title', '演示文稿')}

页面结构（共{total_pages}页）:
  第1页（封面）: {outline.get('title', '演示文稿')}
{slides_info}
  第{total_pages}页（结尾）: 行动号召
  ppt页面根据ppt内容的定位在模板中可以重复选择多次模板页

【转换要求】

1. **页面结构**：
   - 第1页：封面（hero）- 使用主题标题
   - 第2到{total_pages-1}页：内页（content）- 根据大纲slides生成
   - 第{total_pages}页：结尾（cta）- 行动号召

2. **内页生成策略**：
   - 遍历大纲的slides数组，每个slide生成一个内页
   - 使用克隆命令：`subprocess.run(["officecli", "add", file_name, "/", "--from", "/slide[1]"], check=True)`
   - 用batch set命令修改文本内容和位置
   - 根据layout字段选择模板元素：
     * statement: 使用statement-text展示title，statement-sub展示content_points组合
     * pillars: 使用pillar-1/2/3-title展示content_points[0/1/2]
     * evidence: 使用evi-data展示content_points[0]（数据），evi-desc展示其他
     * auto: 自动判断（3个要点→pillars，有数字→evidence，其他→statement）

3. **命令转换**：
   - Linux bash命令 → Python subprocess格式
   - 只替换JSON中"text"属性的值，其他属性保持不变
   - 保持所有风格属性（font, size, color, x, y, width, height, preset, fill等）
   - 使用临时JSON文件 + `--input`参数执行batch命令
   - 所有subprocess.run都要加 check=True
   - **重要**：JSON对象只能使用以下有效字段：command, parent, path, type, from, index, to, props, selector, text, mode, depth, part, xpath, action, xml。绝对不要使用"target"等无效字段

4. **字数对应**：
   - hero-title: 8-15字（主题标题）
   - hero-sub: 15-30字（要点组合，用"|"分隔）
   - statement-text: 10-20字
   - statement-sub: 30-50字
   - pillar-title: 4-8字
   - pillar-desc: 20-40字
   - evi-data: 1-10字（数字或百分比）
   - evi-desc: 30-60字
   - cta-title: 8-15字
   - cta-sub: 15-30字

5. **输出文件名**: {os.path.basename(output_path)}

6. **重要提示**：
   - 保持所有装饰元素（name包含bg-、glow、star、ring、line、dot、circle等）不变
   - 只修改有明确语义的文本元素（hero-title, statement-text, pillar-title等）
   - 确保每个内页都克隆自第1页，然后修改文本
   - 使用transition:"morph"实现平滑过渡

【输出格式】
返回完整的Python脚本，严格按以下结构：

```python
import subprocess
import json
import os

file_name = "{output_path}"

# 1. 创建PPT
subprocess.run(["officecli", "create", file_name], check=True)

# 2. 添加封面slide（slide 1）
subprocess.run([
    "officecli", "add", file_name, "/",
    "--type", "slide",
    "--prop", "layout=blank",
    "--prop", "background=XXXXXX"
], check=True)

# 封面元素（从build.sh提取，只替换text）
hero_commands = [
    # ... 保持所有装饰元素不变
    {{"command":"add","parent":"/slide[1]","type":"shape","props":{{"name":"!!hero-title","text":"{outline.get('title', '演示文稿')}","font":"...","size":"..."}}}},
    # ... 其他元素
]

with open("slide1.json", "w", encoding="utf-8") as f:
    json.dump(hero_commands, f, ensure_ascii=False)
subprocess.run(["officecli", "batch", file_name, "--input", "slide1.json"], check=True)

# 3. 循环添加内页（slide 2 到 slide {total_pages-1}）
# ... 根据大纲slides生成

# 4. 添加结尾slide（slide {total_pages}）
# ... 克隆并修改为cta

# 5. 验证
subprocess.run(["officecli", "validate", file_name], check=True)

# 6. 清理临时文件
for i in range(1, {total_pages + 1}):
    try:
        os.remove(f"slide{{i}}.json")
    except:
        pass

print(f"PPT生成完成（共{total_pages}页）: {{file_name}}")
```

请直接返回Python代码，不要包含```python标记，不要有任何解释说明。
"""
        
        logger.info(f"[BuildShGenerator] 提示词长度: {len(prompt)} 字符")
        return prompt
    
    def _call_llm(self, prompt: str, enable_thinking: bool = True) -> str:
        """调用GLM服务"""
        try:
            from app.services.glm_service import chat as llm_chat
            
            response = llm_chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,  # 降低温度以获得更稳定的代码输出
                max_tokens=8000,  # 增加token限制以容纳完整代码
                enable_thinking=enable_thinking  # 启用思考模式，提高质量
            )
            
            content = response.get('content', '')
            finish_reason = response.get('finish_reason', '')
            
            if finish_reason == 'length':
                logger.warning(f"[BuildShGenerator] LLM响应被截断，长度: {len(content)}")
                raise RuntimeError("LLM响应因长度限制被截断，请重试或调整提示词")
            
            logger.info(f"[BuildShGenerator] LLM调用成功，响应长度: {len(content)}")
            return content
            
        except Exception as e:
            logger.error(f"[BuildShGenerator] LLM调用失败: {e}")
            raise
    
    def _extract_python_code(self, llm_response: str) -> str:
        """从LLM响应中提取Python代码"""
        code = llm_response.strip()

        # 优先提取markdown代码块（支持前后包含解释文本）
        fenced_match = re.search(r'```(?:python|Python)?\s*(.*?)```', llm_response, re.DOTALL)
        if fenced_match:
            code = fenced_match.group(1).strip()
        else:
            # 兼容仅包含代码或带少量标记的情况
            markers = ['```python', '```Python', '```']
            for marker in markers:
                if code.startswith(marker):
                    code = code[len(marker):]
                if code.endswith(marker):
                    code = code[:-len(marker)]
            code = code.strip()

        # 如果仍包含前置说明，尽量从import subprocess开始截取
        import_pos = code.find('import subprocess')
        if import_pos > 0:
            code = code[import_pos:].strip()
        
        # 验证是否是有效的Python代码
        if 'import subprocess' not in code:
            logger.warning("[BuildShGenerator] 提取的代码可能不完整：缺少import语句")
        
        if 'officecli' not in code:
            logger.warning("[BuildShGenerator] 提取的代码可能不完整：缺少officecli命令")
        
        return code
    
    def _execute_python_code(self, python_code: str, output_path: str, total_pages: int):
        """执行生成的Python代码，支持页面级别错误处理"""
        import threading
        import time
        
        # 页面状态跟踪
        page_status = {
            'total_pages': total_pages,
            'successful_pages': [],
            'failed_pages': [],
            'skipped_pages': [],
            'errors': []
        }
        
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # 修改文件名变量
            # 使用正则表达式确保正确替换
            python_code = re.sub(
                r'file_name\s*=\s*["\'].+?["\']',
                f'file_name = {repr(output_path)}',
                python_code
            )
            
            # 如果代码中没有file_name变量，添加一个
            if 'file_name =' not in python_code:
                python_code = f'file_name = {repr(output_path)}\n' + python_code
            
            # 验证生成的代码是否有问题
            self._validate_generated_json_files(python_code)
            
            # 过滤无效的OfficeCLI字段
            logger.debug(f"[BuildShGenerator] 过滤前代码长度: {len(python_code)}")
            python_code = self._filter_officecli_commands(python_code)
            logger.debug(f"[BuildShGenerator] 过滤后代码长度: {len(python_code)}")
            
            logger.info(f"[BuildShGenerator] 准备执行Python代码，输出路径: {output_path}")
            logger.debug(f"[BuildShGenerator] Python代码预览:\n{python_code[:500]}...")
            
            # 语法检查
            try:
                compile(python_code, '<string>', 'exec')
            except SyntaxError as e:
                line_no = e.lineno or 0
                code_lines = python_code.splitlines()
                start = max(1, line_no - 3)
                end = min(len(code_lines), line_no + 3)
                context = "\n".join(
                    f"{i:04d}: {code_lines[i - 1]}" for i in range(start, end + 1)
                )
                logger.error(f"[BuildShGenerator] Python语法错误: {e}")
                logger.error(f"[BuildShGenerator] 语法错误上下文(第{line_no}行附近):\n{context}")
                raise RuntimeError(f"生成的Python代码有语法错误: {e}")
            
            # 执行代码（添加超时保护和页面级别错误处理）
            execution_result = {'success': False, 'error': None, 'page_status': page_status}
            
            def execute_with_timeout():
                try:
                    exec_globals = {
                        '__builtins__': __builtins__,
                        '__file__': output_path,
                        'page_status': page_status
                    }
                    
                    # 在执行前验证生成的JSON文件
                    self._validate_generated_json_files(python_code)
                    
                    # 修改代码，添加页面级别错误处理
                    code_to_execute = self._add_page_error_handling(python_code, page_status)
                    
                    exec(code_to_execute, exec_globals)
                    execution_result['success'] = True
                    execution_result['page_status'] = page_status
                    
                except Exception as e:
                    execution_result['error'] = e
                    execution_result['page_status'] = page_status
                    logger.error(f"[BuildShGenerator] 代码执行异常: {e}", exc_info=True)
            
            # 启动执行线程
            exec_thread = threading.Thread(target=execute_with_timeout)
            exec_thread.daemon = True
            exec_thread.start()
            
            # 等待执行完成，最多等待300秒
            exec_thread.join(timeout=300)
            
            if exec_thread.is_alive():
                logger.error(f"[BuildShGenerator] 代码执行超时（300秒）")
                page_status['errors'].append("代码执行超时")
                return page_status
            
            if not execution_result['success'] and execution_result['error']:
                logger.error(f"[BuildShGenerator] 执行失败: {execution_result['error']}")
                page_status['errors'].append(str(execution_result['error']))
            
            return page_status
            
        except SyntaxError as e:
            logger.error(f"[BuildShGenerator] Python语法错误: {e}")
            logger.error(f"[BuildShGenerator] 错误代码位置:\n{python_code[max(0, e.offset-100):e.offset+100]}")
            page_status['errors'].append(f"语法错误: {e}")
            return page_status
        except Exception as e:
            logger.error(f"[BuildShGenerator] Python代码执行失败: {e}", exc_info=True)
            page_status['errors'].append(str(e))
            return page_status
    
    def _validate_generated_json_files(self, python_code: str):
        """验证生成的JSON文件是否包含有效的OfficeCLI命令"""
        import json
        import re
        import os
        
        # 查找所有写入JSON文件的操作 - 更宽泛的匹配
        json_write_pattern = r'with open\(["\']([^"\']+\.json)["\'].*?\) as f:\s*\n\s*json\.dump\(([^,]+),'
        matches = re.findall(json_write_pattern, python_code, re.MULTILINE | re.DOTALL)
        
        for json_file, var_name in matches:
            try:
                # 尝试多种方式解析变量内容
                var_name = var_name.strip()
                
                # 方法1: 查找直接的列表赋值
                var_pattern = rf'{re.escape(var_name)}\s*=\s*(\[.*?\])'
                var_match = re.search(var_pattern, python_code, re.DOTALL)
                
                if var_match:
                    json_content = var_match.group(1)
                    try:
                        commands = json.loads(json_content)
                        self._validate_commands_list(commands, json_file)
                    except json.JSONDecodeError:
                        logger.warning(f"[BuildShGenerator] 无法直接解析 {json_file} 的JSON内容，跳过静态验证")
                        continue
                
                logger.debug(f"[BuildShGenerator] {json_file} 验证完成")
                    
            except Exception as e:
                logger.error(f"[BuildShGenerator] 验证JSON文件失败 {json_file}: {e}")
                # 不抛出异常，继续执行，让运行时错误暴露问题
                continue
    
    def _add_runtime_validation(self, python_code: str) -> str:
        """在代码中添加运行时验证"""
        import re
        
        # 在每个officecli batch命令前添加验证
        batch_pattern = r'(subprocess\.run\(\["officecli",\s*"batch",\s*[^,]+,\s*"--input",\s*("[^"]+\.json"|[^,]+)\])'
        
        def add_validation(match):
            batch_call = match.group(0)
            json_file = match.group(1)
            
            validation_code = f'''
# 运行时验证JSON文件
try:
    import json
    import os
    json_path = {json_file}
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            commands = json.load(f)
        
        # 过滤无效命令
        filtered_commands = []
        for cmd in commands:
            if isinstance(cmd, dict):
                command = cmd.get('command')
                if command == 'set' and 'path' not in cmd:
                    print(f"过滤无效set命令: {{cmd}}")
                    continue
                filtered_commands.append(cmd)
        
        # 重新写入过滤后的命令
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_commands, f, ensure_ascii=False, indent=2)
        
        print(f"JSON文件 {{json_path}} 验证完成，剩余 {{len(filtered_commands)}} 个命令")
except Exception as e:
    print(f"JSON文件验证失败: {{e}}")

'''
            return validation_code + batch_call
        
        modified_code = re.sub(batch_pattern, add_validation, python_code)
        return modified_code
    
    def _add_page_error_handling(self, python_code: str, page_status: dict) -> str:
        """在代码中添加页面级别错误处理"""
        import re
        
        # 在每个batch命令周围添加try-except
        batch_pattern = r'(subprocess\.run\(\["officecli",\s*"batch"[^)]+\)\s*)'
        
        def add_page_error_handling(match):
            batch_call = match.group(0)
            json_file_match = re.search(r'"([^"]+\.json)"', batch_call)
            json_file = json_file_match.group(1) if json_file_match else ""
            
            # 从JSON文件名推断页码 (slide2.json -> page 2)
            page_match = re.search(r'slide(\d+)\.json', json_file)
            page_num = int(page_match.group(1)) if page_match else 0
            
            error_handling_code = f'''
# 页面 {page_num} 错误处理
try:
    result = {batch_call}
    if result.returncode == 0:
        page_status['successful_pages'].append({page_num})
        print(f"页面 {page_num} 生成成功")
    else:
        raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
except subprocess.CalledProcessError as e:
    print(f"页面 {page_num} 生成失败: {{e}}")
    page_status['failed_pages'].append({page_num})
    # 尝试修复并重试
    try:
        fixed_commands = self._retry_fix_page_commands({json_file!r}, {page_num})
        if fixed_commands:
            # 重新写入修复后的命令
            import json
            with open({json_file!r}, 'w', encoding='utf-8') as f:
                json.dump(fixed_commands, f, ensure_ascii=False, indent=2)
            
            # 重试执行
            result = {batch_call}
            if result.returncode == 0:
                page_status['successful_pages'].append({page_num})
                print(f"页面 {page_num} 修复后生成成功")
            else:
                page_status['failed_pages'].append({page_num})
                print(f"页面 {page_num} 修复后仍失败")
        else:
            page_status['failed_pages'].append({page_num})
            print(f"页面 {page_num} 无法修复，跳过")
    except Exception as retry_e:
        page_status['failed_pages'].append({page_num})
        print(f"页面 {page_num} 重试失败: {{retry_e}}")
except Exception as e:
    print(f"页面 {page_num} 未知错误: {{e}}")
    page_status['failed_pages'].append({page_num})
'''
            return error_handling_code
        
        modified_code = re.sub(batch_pattern, add_page_error_handling, python_code)
        return modified_code
    
    def _retry_fix_page_commands(self, json_file: str, page_num: int) -> list:
        """使用LLM修复失败的页面命令"""
        try:
            # 读取原始命令
            with open(json_file, 'r', encoding='utf-8') as f:
                original_commands = json.load(f)
            
            # 构建修复提示
            fix_prompt = f"""
请修复以下OfficeCLI命令，这些命令在页面{page_num}生成时失败。
原始命令：
{json.dumps(original_commands, ensure_ascii=False, indent=2)}

请分析可能的错误原因：
1. 缺少必需的字段（如'set'命令缺少'path'字段）
2. 无效的命令格式
3. 错误的参数值

请提供修复后的命令列表，确保所有命令都是有效的OfficeCLI命令。
只返回JSON格式的命令列表，不要包含其他解释。
"""
            
            # 调用LLM进行修复
            response = self._call_llm(fix_prompt, enable_thinking=True)
            
            # 解析修复后的命令
            try:
                fixed_commands = json.loads(response)
                if isinstance(fixed_commands, list):
                    # 验证修复后的命令
                    validated_commands = self._filter_officecli_commands(fixed_commands)
                    return validated_commands
            except json.JSONDecodeError:
                print(f"LLM返回的修复命令格式错误: {response}")
                return None
                
        except Exception as e:
            print(f"修复页面{page_num}命令时出错: {e}")
            return None
    
    def _validate_commands_list(self, commands, json_file):
        """验证命令列表"""
        if not isinstance(commands, list):
            return
            
        for i, cmd in enumerate(commands):
            if isinstance(cmd, dict):
                command = cmd.get('command')
                if command == 'set' and 'path' not in cmd:
                    logger.error(f"[BuildShGenerator] 发现无效set命令在{json_file}[{i}]: 缺少path字段 - {cmd}")
                    # 移除无效命令
                    commands[i] = None
                    continue
                
                # 检查是否有其他必需字段
                if command and not all(k in cmd for k in ['command']):
                    logger.error(f"[BuildShGenerator] 发现无效命令在{json_file}[{i}]: 缺少command字段 - {cmd}")
                    commands[i] = None
                    continue
        
        # 过滤掉None值
        original_count = len(commands)
        commands[:] = [cmd for cmd in commands if cmd is not None]
        filtered_count = original_count - len(commands)
        
        if filtered_count > 0:
            logger.warning(f"[BuildShGenerator] 从{json_file}中移除了 {filtered_count} 个无效命令")
        
        logger.debug(f"[BuildShGenerator] {json_file} 验证通过，包含 {len(commands)} 个有效命令")
    
    def _filter_officecli_commands(self, python_code_or_commands):
        """过滤OfficeCLI命令中的无效字段。

        支持直接过滤Python代码中的JSON数组，也支持过滤命令列表对象。
        """
        import ast
        import json
        import re

        valid_fields = {
            'command', 'parent', 'path', 'type', 'from', 'index', 'to',
            'props', 'selector', 'text', 'mode', 'depth', 'part', 'xpath',
            'action', 'xml'
        }

        def filter_dict(obj):
            """递归过滤字典中的无效字段，并验证命令完整性"""
            if isinstance(obj, dict):
                command = obj.get('command')
                if command == 'set' and 'path' not in obj:
                    logger.warning(f"[BuildShGenerator] 跳过无效的set命令：缺少path字段 - {obj}")
                    return None

                filtered = {k: filter_dict(v) for k, v in obj.items() if k in valid_fields}
                if any(v is None for v in filtered.values()):
                    logger.warning(f"[BuildShGenerator] 命令包含无效值，跳过: {filtered}")
                    return None
                return filtered
            elif isinstance(obj, list):
                filtered_list = []
                filtered_count = 0
                for item in obj:
                    filtered_item = filter_dict(item)
                    if filtered_item is not None:
                        filtered_list.append(filtered_item)
                    else:
                        filtered_count += 1
                if filtered_count > 0:
                    logger.debug(f"[BuildShGenerator] 从列表中过滤掉 {filtered_count} 个无效命令")
                return filtered_list
            else:
                return obj

        def filter_commands_list(commands):
            if not isinstance(commands, list):
                return commands
            return filter_dict(commands)

        def find_command_blocks(code):
            assign_pattern = re.compile(r'(\w+_commands\s*=\s*)\[')
            for match in assign_pattern.finditer(code):
                start = match.end() - 1
                depth = 0
                in_string = False
                escape = False
                for idx in range(start, len(code)):
                    ch = code[idx]
                    if in_string:
                        if escape:
                            escape = False
                        elif ch == '\\':
                            escape = True
                        elif ch == '"':
                            in_string = False
                    else:
                        if ch == '"':
                            in_string = True
                        elif ch == '[':
                            depth += 1
                        elif ch == ']':
                            depth -= 1
                            if depth == 0:
                                yield match.group(1), code[start:idx + 1], start, idx + 1
                                break

        if isinstance(python_code_or_commands, list):
            return filter_commands_list(python_code_or_commands)

        if not isinstance(python_code_or_commands, str):
            raise TypeError("_filter_officecli_commands 接受字符串或命令列表")

        python_code = python_code_or_commands
        modified_code = python_code

        # 关键：必须逆序替换，避免前面替换改变后续索引导致代码被破坏
        command_blocks = list(find_command_blocks(python_code))
        for var_name, block, start_idx, end_idx in reversed(command_blocks):
            try:
                commands = ast.literal_eval(block)
                if not isinstance(commands, list):
                    raise ValueError("命令块不是列表")

                logger.debug(f"[BuildShGenerator] 解析到 {len(commands)} 个OfficeCLI命令")
                filtered_commands = filter_commands_list(commands)
                logger.debug(f"[BuildShGenerator] 过滤后剩余 {len(filtered_commands)} 个有效命令")

                if not filtered_commands:
                    logger.warning(f"[BuildShGenerator] 所有命令都被过滤，跳过此命令块")
                    continue

                filtered_json = json.dumps(filtered_commands, ensure_ascii=False, indent=2)
                new_block = filtered_json
                modified_code = modified_code[:start_idx] + new_block + modified_code[end_idx:]
            except Exception as e:
                logger.warning(f"[BuildShGenerator] 命令块解析失败，跳过过滤: {e}")
                continue

        return modified_code


# 单例模式
_build_sh_generator_instance = None

def get_build_sh_generator() -> BuildShPPTGenerator:
    """获取BuildShPPTGenerator单例"""
    global _build_sh_generator_instance
    if _build_sh_generator_instance is None:
        _build_sh_generator_instance = BuildShPPTGenerator()
    return _build_sh_generator_instance
