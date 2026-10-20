"""
OfficeCLI SKILL.md 加载器
读取并解析OfficeCLI的SKILL.md文件，提取有用的知识和最佳实践
"""
import os
import re
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# SKILL.md文件路径
SKILL_MD_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'OfficeCLI-main', 'SKILL.md'
)


class SkillKnowledge:
    """从SKILL.md提取的知识"""
    
    def __init__(self):
        self.raw_content = ""
        self.pitfalls: List[Dict] = []
        self.value_formats: Dict[str, List[str]] = {}
        self.element_types: Dict[str, List[str]] = {}
        self.commands: Dict[str, str] = {}
        self.view_modes: List[str] = []
        self.loaded = False
        
    def load(self, skill_path: str = None) -> bool:
        """加载并解析SKILL.md"""
        path = skill_path or SKILL_MD_PATH
        
        if not os.path.isfile(path):
            logger.warning(f"[SkillLoader] SKILL.md文件不存在: {path}")
            return False
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.raw_content = f.read()
            
            self._parse_pitfalls()
            self._parse_value_formats()
            self._parse_element_types()
            self._parse_commands()
            self._parse_view_modes()
            
            self.loaded = True
            logger.info(f"[SkillLoader] SKILL.md加载成功，提取 {len(self.pitfalls)} 个陷阱提示")
            return True
            
        except Exception as e:
            logger.error(f"[SkillLoader] 加载SKILL.md失败: {e}")
            return False
    
    def _parse_pitfalls(self):
        """解析常见陷阱"""
        # 匹配表格中的陷阱
        pattern = r'\|\s*`?([^`|\n]+)`?\s*\|\s*([^|\n]+)\s*\|'
        in_pitfall_section = False
        
        for line in self.raw_content.split('\n'):
            if '## Common Pitfalls' in line or '## 常见陷阱' in line:
                in_pitfall_section = True
                continue
            if in_pitfall_section and line.startswith('##'):
                break
            if in_pitfall_section and '|' in line and 'Pitfall' not in line:
                match = re.search(pattern, line)
                if match:
                    pitfall = match.group(1).strip()
                    solution = match.group(2).strip()
                    if pitfall and solution and not pitfall.startswith('-'):
                        self.pitfalls.append({
                            'pitfall': pitfall,
                            'solution': solution
                        })
    
    def _parse_value_formats(self):
        """解析值格式"""
        # 颜色格式
        self.value_formats['colors'] = [
            'FF0000', 'red', 'rgb(255,0,0)', 'accent1..accent6'
        ]
        # 尺寸格式
        self.value_formats['dimensions'] = [
            '914400', '2.54cm', '1in', '72pt', '96px'
        ]
        # 间距格式
        self.value_formats['spacing'] = [
            '12pt', '0.5cm', '1.5x', '150%'
        ]
    
    def _parse_element_types(self):
        """解析元素类型"""
        self.element_types = {
            'pptx': [
                'slide', 'shape', 'textbox', 'picture', 'image', 'img',
                'chart', 'table', 'row', 'tr', 'connector', 'connection',
                'line', 'group', 'video', 'audio', 'media', 'equation',
                'formula', 'math', 'notes', 'paragraph', 'para', 'run',
                'zoom', 'slidezoom'
            ],
            'docx': [
                'paragraph', 'para', 'run', 'table', 'row', 'tr', 'cell',
                'td', 'image', 'picture', 'img', 'header', 'footer',
                'section', 'bookmark', 'comment', 'footnote', 'endnote',
                'formfield', 'sdt', 'contentcontrol', 'chart', 'equation',
                'formula', 'math', 'field', 'hyperlink', 'style', 'toc',
                'watermark', 'break', 'pagebreak', 'columnbreak'
            ],
            'xlsx': [
                'sheet', 'row', 'cell', 'chart', 'image', 'picture',
                'comment', 'table', 'listobject', 'namedrange',
                'definedname', 'pivottable', 'pivot', 'sparkline',
                'validation', 'datavalidation', 'autofilter', 'shape',
                'textbox', 'databar', 'colorscale', 'iconset',
                'formulacf', 'csv', 'tsv'
            ]
        }
    
    def _parse_commands(self):
        """解析命令"""
        self.commands = {
            'create': '创建空白 .docx/.xlsx/.pptx（根据扩展名判断类型）',
            'view': '查看内容（模式：outline, stats, issues, text, annotated）',
            'get': '获取元素及子元素（--depth N, --json）',
            'query': 'CSS风格查询（[attr=value], :contains(), :has() 等）',
            'set': '修改元素属性',
            'add': '添加元素（或通过 --from <path> 克隆）',
            'remove': '删除元素',
            'move': '移动元素（--to <parent> --index N）',
            'swap': '交换两个元素',
            'validate': 'OpenXML模式校验',
            'batch': '单次打开/保存周期内执行多条操作',
            'merge': '模板合并 — 用JSON数据替换 {{key}} 占位符',
            'watch': '在浏览器中实时HTML预览，自动刷新',
            'mcp': '启动MCP服务器，用于AI工具集成',
            'raw': '查看文档部件的原始XML',
            'raw-set': '通过XPath修改原始XML',
        }
    
    def _parse_view_modes(self):
        """解析view模式"""
        self.view_modes = [
            'outline',   # 文档结构
            'stats',     # 统计信息
            'issues',    # 格式/内容/结构问题
            'text',      # 纯文本提取
            'annotated'  # 带格式注释的文本
        ]
    
    def get_pitfall_hint(self, command: str) -> Optional[str]:
        """获取与命令相关的陷阱提示"""
        command = command.lower()
        for pitfall in self.pitfalls:
            if command in pitfall['pitfall'].lower():
                return f"提示: {pitfall['solution']}"
        return None
    
    def validate_color(self, color: str) -> tuple:
        """验证颜色格式"""
        if not color:
            return False, "颜色不能为空"
        
        # 十六进制
        if re.match(r'^#?[0-9A-Fa-f]{6}$', color):
            return True, None
        # 主题色
        if color.lower().startswith('accent'):
            return True, None
        # RGB
        if color.lower().startswith('rgb('):
            return True, None
        # 命名色
        named_colors = ['red', 'blue', 'green', 'black', 'white', 'yellow', 
                       'orange', 'purple', 'pink', 'gray', 'grey', 'cyan', 'magenta']
        if color.lower() in named_colors:
            return True, None
        
        return False, f"无效的颜色格式: {color}。支持: 十六进制(FF0000)、命名色(red)、RGB(rgb(255,0,0))、主题色(accent1)"
    
    def validate_dimension(self, value: str) -> tuple:
        """验证尺寸格式"""
        if not value:
            return False, "尺寸不能为空"
        
        # 纯数字（EMU）
        if value.isdigit():
            return True, None
        
        # 带单位
        units = ['cm', 'in', 'pt', 'px']
        for unit in units:
            if value.endswith(unit):
                try:
                    float(value[:-len(unit)])
                    return True, None
                except ValueError:
                    break
        
        return False, f"无效的尺寸格式: {value}。支持: EMU(914400)、cm(2.54cm)、in(1in)、pt(72pt)、px(96px)"
    
    def get_element_types_for_format(self, format_type: str) -> List[str]:
        """获取指定格式的元素类型"""
        return self.element_types.get(format_type.lower(), [])
    
    def is_valid_element_type(self, format_type: str, element_type: str) -> bool:
        """检查元素类型是否有效"""
        types = self.get_element_types_for_format(format_type)
        return element_type.lower() in [t.lower() for t in types]
    
    def get_command_help(self, command: str) -> Optional[str]:
        """获取命令帮助"""
        return self.commands.get(command.lower())
    
    def generate_cli_hint(self, operation: str, format_type: str = 'pptx') -> str:
        """生成CLI使用提示"""
        hints = []
        
        # 添加相关陷阱提示
        pitfall_hint = self.get_pitfall_hint(operation)
        if pitfall_hint:
            hints.append(pitfall_hint)
        
        # 添加命令帮助
        cmd_help = self.get_command_help(operation)
        if cmd_help:
            hints.append(f"用法: {cmd_help}")
        
        return '\n'.join(hints) if hints else ""


# 全局实例
_skill_knowledge = None


def get_skill_knowledge() -> SkillKnowledge:
    """获取SKILL知识实例"""
    global _skill_knowledge
    if _skill_knowledge is None:
        _skill_knowledge = SkillKnowledge()
        _skill_knowledge.load()
    return _skill_knowledge


def reload_skill_knowledge(skill_path: str = None) -> bool:
    """重新加载SKILL知识"""
    global _skill_knowledge
    _skill_knowledge = SkillKnowledge()
    return _skill_knowledge.load(skill_path)