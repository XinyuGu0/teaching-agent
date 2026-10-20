"""
PPT模板管理服务
仅支持用户上传的模板管理
"""
import os
import json
import shutil
import logging
import subprocess
from typing import List, Dict, Optional
from datetime import datetime
from flask import current_app

from app.extensions import db
from app.models.template import Template

logger = logging.getLogger(__name__)


class TemplateService:
    """PPT模板管理服务"""
    
    def __init__(self):
        self.officecli_path = self._find_officecli()
    
    def _find_officecli(self) -> str:
        """查找officecli可执行文件"""
        if os.name == 'nt':
            possible_paths = [
                'officecli',
                'officecli.exe',
                os.path.expanduser('~/.officecli/officecli.exe'),
            ]
        else:
            possible_paths = [
                'officecli',
                os.path.expanduser('~/.local/bin/officecli'),
                os.path.expanduser('~/.officecli/officecli'),
                '/usr/local/bin/officecli',
            ]
        
        for path in possible_paths:
            if shutil.which(path):
                return path
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
        return None
    
    def _run_officecli(self, args: List[str], timeout: int = 60) -> tuple:
        """执行officecli命令"""
        if not self.officecli_path:
            raise RuntimeError("OfficeCLI未安装或未找到")
        
        cmd = [self.officecli_path] + args
        logger.debug(f"[TemplateService] 执行命令: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"OfficeCLI命令超时")
        except Exception as e:
            raise RuntimeError(f"OfficeCLI命令执行失败: {e}")
    
    def get_templates_by_type(self, template_type: str = None, user_id: str = None) -> List[Template]:
        """获取模板列表"""
        query = Template.query
        
        if template_type:
            query = query.filter_by(template_type=template_type)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        return query.order_by(Template.usage_count.desc()).all()
    
    def get_all_templates(self, user_id: str = None) -> Dict[str, List[Template]]:
        """获取所有模板，按类型分组"""
        result = {'uploaded': []}
        
        if user_id:
            result['uploaded'] = Template.query.filter_by(
                template_type='uploaded',
                user_id=user_id
            ).order_by(Template.created_at.desc()).all()
        
        return result
    
    def save_uploaded_template(self, file, user_id: str, name: str = None, 
                               category: str = None, thumbnail_path: str = None) -> Template:
        """保存用户上传的PPT模板"""
        upload_dir = current_app.config.get('TEMPLATE_UPLOAD_DIR', 
                                            os.path.join(current_app.instance_path, 'templates'))
        os.makedirs(upload_dir, exist_ok=True)
        
        import uuid
        file_ext = os.path.splitext(file.filename)[1] or '.pptx'
        safe_name = f"{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(upload_dir, safe_name)
        
        file.save(file_path)
        
        if not name:
            name = os.path.splitext(file.filename)[0]
        if not category:
            category = 'other'
        
        template = Template(
            user_id=user_id,
            name=name,
            category=category,
            template_type='uploaded',
            file_path=file_path,
            thumbnail_path=thumbnail_path,
            source_format=file_ext.lstrip('.'),
            description=f"用户上传 - {name}",
            is_public=False
        )
        
        db.session.add(template)
        db.session.commit()
        
        logger.info(f"[TemplateService] 用户 {user_id} 上传模板: {name}, 分类: {category}")
        return template
    
    def get_categories(self) -> List[Dict]:
        """获取模板分类列表"""
        return [
            {'id': 'business', 'name': '商务', 'description': '商务汇报、工作总结'},
            {'id': 'education', 'name': '教育', 'description': '教学课件、学术报告'},
            {'id': 'creative', 'name': '创意', 'description': '创意设计、艺术展示'},
            {'id': 'technology', 'name': '科技', 'description': '科技、技术主题'},
            {'id': 'minimal', 'name': '极简', 'description': '简约风格'},
            {'id': 'other', 'name': '其他', 'description': '其他类型'}
        ]
    
    def parse_template_styles(self, ppt_path: str) -> Dict:
        """使用officecli解析PPT模板的样式信息"""
        if not self.officecli_path:
            return {}
        try:
            returncode, stdout, stderr = self._run_officecli(['get', ppt_path, '/theme', '--json'])
            if returncode == 0 and stdout.strip():
                theme_data = json.loads(stdout)
                return {
                    'theme': theme_data,
                    'background_color': self._extract_background_color(theme_data),
                    'font_scheme': self._extract_font_scheme(theme_data),
                    'color_scheme': self._extract_color_scheme(theme_data)
                }
        except Exception as e:
            logger.warning(f"[TemplateService] 解析模板样式失败: {e}")
        return {}
    
    def get_template_info(self, ppt_path: str) -> Dict:
        """使用officecli获取PPT模板的基本信息"""
        if not self.officecli_path:
            return {}
        try:
            returncode, stdout, stderr = self._run_officecli(['view', ppt_path, 'stats', '--json'])
            stats = json.loads(stdout) if returncode == 0 and stdout.strip() else {}
            
            returncode, stdout, stderr = self._run_officecli(['view', ppt_path, 'outline', '--json'])
            outline = json.loads(stdout) if returncode == 0 and stdout.strip() else {}
            
            returncode, stdout, stderr = self._run_officecli(['get', ppt_path, '/slide[1]', '--depth', '1', '--json'])
            slide_structure = json.loads(stdout) if returncode == 0 and stdout.strip() else {}
            
            return {
                'stats': stats, 'outline': outline,
                'slide_structure': slide_structure,
                'slide_count': stats.get('slides', 0)
            }
        except Exception as e:
            logger.warning(f"[TemplateService] 获取模板信息失败: {e}")
            return {}
    
    def _extract_background_color(self, theme_data: Dict) -> Optional[str]:
        try:
            return theme_data.get('background') or theme_data.get('fill')
        except:
            return None
    
    def _extract_font_scheme(self, theme_data: Dict) -> Dict:
        try:
            fs = theme_data.get('fontScheme', {})
            return {
                'major': fs.get('majorFont', {}).get('latin', 'Arial'),
                'minor': fs.get('minorFont', {}).get('latin', 'Arial')
            }
        except:
            return {}
    
    def _extract_color_scheme(self, theme_data: Dict) -> Dict:
        try:
            cs = theme_data.get('colorScheme', {})
            return {k: cs[k] for k in ['accent1','accent2','accent3','accent4','accent5','accent6','dk1','dk2','lt1','lt2'] if k in cs}
        except:
            return {}
    
    def parse_uploaded_template(self, template_id: str) -> Dict:
        """解析用户上传的模板"""
        template = Template.query.get(template_id)
        if not template:
            raise ValueError("模板不存在")
        if template.template_type != 'uploaded':
            raise ValueError("只能解析用户上传的模板")
        
        styles = self.parse_template_styles(template.file_path)
        template_info = self.get_template_info(template.file_path)
        template.styles = styles
        template.template_info = template_info
        db.session.commit()
        return {'styles': styles, 'template_info': template_info}
    
    def get_template_placeholders(self, template_id: str) -> List[Dict]:
        """获取模板中的占位符信息"""
        template = Template.query.get(template_id)
        if not template or not template.file_path or not self.officecli_path:
            return []
        
        placeholders = []
        try:
            template_info = template.template_info or {}
            slide_count = template_info.get('slide_count', 0)
            for i in range(1, slide_count + 1):
                returncode, stdout, stderr = self._run_officecli([
                    'get', template.file_path, f'/slide[{i}]', '--depth', '2', '--json'
                ])
                if returncode == 0 and stdout.strip():
                    slide_data = json.loads(stdout)
                    for shape in slide_data.get('shapes', []):
                        if shape.get('placeholder'):
                            placeholders.append({
                                'slide_index': i,
                                'shape_index': shape.get('index'),
                                'type': shape.get('placeholder_type', 'unknown'),
                                'name': shape.get('name', ''),
                                'text': shape.get('text', '')
                            })
        except Exception as e:
            logger.warning(f"[TemplateService] 获取占位符失败: {e}")
        return placeholders


# 全局实例
_template_service = None


def get_template_service() -> TemplateService:
    """获取模板服务实例"""
    global _template_service
    if _template_service is None:
        _template_service = TemplateService()
    return _template_service