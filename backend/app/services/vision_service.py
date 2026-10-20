"""
视觉模型服务
使用视觉模型处理图片、PPT页面等视觉内容
"""
import requests
import base64
from typing import List, Dict, Optional
import os


class VisionService:
    """视觉模型服务"""
    
    def __init__(self):
        # 从环境变量读取配置
        self.base_url = os.getenv('VISION_API_URL', 'https://api.bltcy.cn/v1/chat/completions')
        self.model = os.getenv('VISION_MODEL', 'qwen3-vl-235b-a22b')
        self.api_key = os.getenv('VISION_API_KEY', '')
        
        import logging
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"[VISION] 视觉服务初始化完成， 模型: {self.model}")
    
    def _encode_image(self, image_path: str) -> str:
        """
        将图片编码为base64
        
        Args:
            image_path: 图片路径
            
        Returns:
            base64编码的图片字符串
        """
        try:
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"[VISION] 图片编码失败: {e}")
            return None
    
    def _convert_ppt_page_to_image(self, ppt_path: str, page_index: int = 0) -> Optional[str]:
        """
        将PPT的某一页转换为图片
        
        Args:
            ppt_path: PPT文件路径
            page_index: 页码（从0开始）
            
        Returns:
            临时图片文件路径，如果失败返回None
        """
        try:
            from pptx import Presentation
            from PIL import Image
            import io
            
            # 打开PPT
            prs = Presentation(ppt_path)
            
            # 检查页码是否有效
            if page_index >= len(prs.slides):
                return None
            
            slide = prs.slides[page_index]
            
            # 获取页面尺寸（限制最大尺寸避免内存错误）
            width = min(int(prs.slide_width), 2000)  # 限制最大宽度2000
            height = min(int(prs.slide_height), 2000)  # 限制最大高度2000
            
            # 创建空白图片（白色背景）
            img = Image.new('RGB', (width, height), color='white')
            
            # 保存临时图片
            temp_path = f"temp_slide_{page_index}.png"
            img.save(temp_path)
            
            return temp_path
            
        except Exception as e:
            print(f"[VISION] PPT转图片失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def analyze_ppt_layout(self, ppt_path: str, max_pages: int = 3) -> Dict:
        """
        分析PPT的布局和样式（使用传统方法，避免视觉模型调用失败）

        Args:
            ppt_path: PPT文件路径
            max_pages: 分析的最大页数

        Returns:
            包含布局信息的字典
        """
        try:
            from pptx import Presentation
            
            prs = Presentation(ppt_path)
            total_pages = len(prs.slides)
            
            print(f"[VISION] 开始分析PPT布局")
            print(f"[VISION] 总页数: {total_pages}")
            print(f"[VISION] 将分析前 {min(max_pages, total_pages)} 页")
            
            # 直接使用传统方法分析每一页（避免视觉模型转换图片的内存问题）
            pages_info = []
            for i in range(min(max_pages, total_pages)):
                page_info = self._analyze_page_traditional(ppt_path, i)
                if page_info:
                    pages_info.append(page_info)
                    print(f"[VISION] ✓ 第{i+1}页分析完成: {page_info.get('layout_type')}")
            
            # 提取整体样式
            styles = self._extract_overall_styles(pages_info)
            
            result = {
                'total_pages': total_pages,
                'analyzed_pages': len(pages_info),
                'pages': pages_info,
                'styles': styles,
                'success': True
            }
            
            print(f"[VISION] ✓ PPT分析完成")
            print(f"[VISION]   - 颜色: {styles.get('colors', {})}")
            print(f"[VISION]   - 字体: {styles.get('fonts', {})}")
            
            return result
            
        except Exception as e:
            print(f"[VISION] PPT分析失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'pages': [],
                'styles': {}
            }
    
    def _analyze_single_page(self, ppt_path: str, page_index: int) -> Dict:
        """
        分析单页PPT
        
        Args:
            ppt_path: PPT文件路径
            page_index: 页码
            
        Returns:
            单页分析结果
        """
        try:
            # 将PPT页面转换为图片
            image_path = self._convert_ppt_page_to_image(ppt_path, page_index)
            
            if not image_path:
                # 如果转换失败，使用传统方法
                return self._analyze_page_traditional(ppt_path, page_index)
            
            # 使用视觉模型分析
            return self._analyze_with_vision_model(image_path, page_index)
            
        except Exception as e:
            print(f"[VISION] 单页分析失败，使用传统方法: {e}")
            # 回退到传统方法
            return self._analyze_page_traditional(ppt_path, page_index)
    
    def _analyze_with_vision_model(self, image_path: str, page_index: int) -> Dict:
        """
        使用视觉模型分析图片
        
        Args:
            image_path: 图片路径
            page_index: 页码
            
        Returns:
            分析结果
        """
        try:
            # 编码图片
            base64_image = self._encode_image(image_path)
            
            if not base64_image:
                return self._analyze_page_traditional(image_path, page_index)
            
            # 构建提示词
            prompt = f"""请分析这张PPT页面（第{page_index + 1}页）的布局和样式，以JSON格式返回：

{{
  "layout_type": "布局类型（title/content_with_image/two_column/single_column）",
  "background_color": "背景颜色（十六进制，如FF0000）",
  "text_boxes": [
    {{
      "type": "文本框类型（title/body）",
      "position": "位置（top/left/right/center/bottom）",
      "font_name": "字体名称",
      "font_size": 字体大小,
      "font_bold": 是否粗体
    }}
  ],
  "elements": {{
    "text_count": 文本框数量,
    "image_count": 图片数量,
    "shape_count": 形状数量
  }},
  "color_scheme": {{
    "primary": "主色调",
    "secondary": "辅助色",
    "accent": "强调色"
  }}
}}

要求：
1. 准确识别布局类型
2. 提取真实的颜色值（十六进制）
3. 识别所有文本框及其字体信息
4. 只返回JSON，不要其他内容
"""
            
            # 构建请求
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.3
            }
            
            # 发送请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            print(f"[VISION] 正在请求视觉模型分析第{page_index + 1}页...")
            
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # 解析JSON响应
                try:
                    import json
                    import re
                    
                    # 提取JSON
                    json_match = re.search(r'\{[\s\S]*\}', content)
                    if json_match:
                        analysis = json.loads(json_match.group())
                        
                        # 添加页码
                        analysis['page_number'] = page_index + 1
                        
                        return analysis
                except Exception as e:
                    print(f"[VISION] JSON解析失败: {e}")
            
            print(f"[VISION] 视觉模型返回: {response.status_code}")
            
            # 如果视觉模型失败，回退到传统方法
            return self._analyze_page_traditional(image_path, page_index)
            
        except Exception as e:
            print(f"[VISION] 视觉模型分析失败: {e}")
            import traceback
            traceback.print_exc()
            # 回退到传统方法
            return self._analyze_page_traditional(image_path, page_index)

    def analyze_page_issues(self, image_path: str, page_index: int) -> Dict:
        """分析页面问题并给出缩放建议"""
        try:
            base64_image = self._encode_image(image_path)
            if not base64_image:
                return {}

            prompt = f"""请审查这张PPT页面（第{page_index + 1}页）的版式是否存在拥挤、溢出、重叠等问题，并输出修正建议，以JSON返回：

{{
  "has_issues": true/false,
  "issues": ["overcrowded", "overflow", "overlap", "too_small"],
  "text_scale": 0.85,
  "line_spacing": 1.1
}}

要求：
1. 如果页面拥挤或溢出，请给出建议缩放系数（0.7~1.0）
2. 如果没有问题，has_issues=false，text_scale=1.0
3. 只输出JSON，不要其他内容
"""

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                            },
                            {"type": "text", "text": prompt}
                        ]
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.2
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(self.base_url, json=payload, headers=headers, timeout=60)
            if response.status_code != 200:
                return {}

            content = response.json()['choices'][0]['message']['content']
            import json
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                result = json.loads(json_match.group())
                result['page_number'] = page_index + 1
                return result

            return {}
        except Exception as e:
            print(f"[VISION] 审查分析失败: {e}")
            return {}
    
    def _analyze_page_traditional(self, ppt_path: str, page_index: int) -> Dict:
        """
        使用传统方法分析PPT页面（不使用视觉模型）
        
        Args:
            ppt_path: PPT文件路径
            page_index: 页码
            
        Returns:
            分析结果
        """
        try:
            from pptx import Presentation
            
            prs = Presentation(ppt_path)
            
            if page_index >= len(prs.slides):
                return {}
            
            slide = prs.slides[page_index]
            
            # 统计元素
            text_count = 0
            image_count = 0
            shape_count = 0
            text_boxes = []
            
            # 分析文本框
            for shape in slide.shapes:
                if shape.has_text_frame and shape.text:
                    text_count += 1
                    
                    # 提取字体信息
                    font_name = "Arial"
                    font_size = 18
                    font_bold = False
                    text_type = "body"
                    
                    try:
                        if shape.text_frame.paragraphs:
                            para = shape.text_frame.paragraphs[0]
                            if para.runs:
                                run = para.runs[0]
                                if run.font:
                                    font_name = run.font.name or "Arial"
                                    font_size = int(run.font.size.pt) if run.font.size else 18
                                    font_bold = run.font.bold or False
                                    
                                    if font_size > 24 or font_bold:
                                        text_type = "title"
                    except:
                        pass
                    
                    text_boxes.append({
                        'type': text_type,
                        'position': 'center',  # 简化处理
                        'font_name': font_name,
                        'font_size': font_size,
                        'font_bold': font_bold
                    })
                
                elif shape.shape_type == 13:  # Picture
                    image_count += 1
                else:
                    shape_count += 1
            
            # 提取背景色
            background_color = "FFFFFF"
            try:
                if slide.background and hasattr(slide.background, 'fill') and slide.background.fill:
                    if hasattr(slide.background.fill, 'fore_color') and slide.background.fill.fore_color:
                        if hasattr(slide.background.fill.fore_color, 'rgb') and slide.background.fill.fore_color.rgb:
                            r = slide.background.fill.fore_color.rgb.red
                            g = slide.background.fill.fore_color.rgb.green
                            b = slide.background.fill.fore_color.rgb.blue
                            background_color = f"{r:02X}{g:02X}{b:02X}"
            except:
                pass
            
            # 判断布局类型
            layout_type = "single_column"
            if page_index == 0:
                layout_type = "title"
            elif text_count > 0 and image_count > 0:
                layout_type = "content_with_image"
            elif text_count > 2:
                layout_type = "two_column"
            
            result = {
                'page_number': page_index + 1,
                'layout_type': layout_type,
                'background_color': background_color,
                'text_boxes': text_boxes[:3],  # 限制数量
                'elements': {
                    'text_count': text_count,
                    'image_count': image_count,
                    'shape_count': shape_count
                },
                'color_scheme': {
                    'primary': background_color,
                    'secondary': '333333',
                    'accent': '666666'
                }
            }
            
            print(f"[VISION] ✓ 传统方法分析完成: {layout_type}")
            return result
            
        except Exception as e:
            print(f"[VISION] 传统方法分析失败: {e}")
            return {}
    
    def _extract_overall_styles(self, pages_info: List[Dict]) -> Dict:
        """
        从多页信息中提取整体样式
        
        Args:
            pages_info: 各页分析结果列表
            
        Returns:
            整体样式信息
        """
        if not pages_info:
            return {
                'colors': {
                    'title_slide': {'primary': '1E3A8A', 'secondary': '3B82F6'},
                    'content_slide': {'primary': 'F8FAFC', 'secondary': '1E3A8A'}
                },
                'fonts': {
                    'title': {'name': 'Arial', 'size': 36, 'bold': True},
                    'body': {'name': 'Arial', 'size': 18}
                }
            }
        
        # 提取标题页样式（第一页）
        title_page = pages_info[0] if pages_info else {}
        title_bg = title_page.get('background_color', '1E3A8A')
        
        # 提取内容页样式（第二页或第一页）
        content_page = pages_info[1] if len(pages_info) > 1 else (pages_info[0] if pages_info else {})
        content_bg = content_page.get('background_color', 'F8FAFC')
        
        # 提取字体
        title_font = {'name': 'Arial', 'size': 36, 'bold': True}
        body_font = {'name': 'Arial', 'size': 18}
        
        for page in pages_info:
            for box in page.get('text_boxes', []):
                if box.get('type') == 'title':
                    title_font['name'] = box.get('font_name', 'Arial')
                    title_font['size'] = box.get('font_size', 36)
                    title_font['bold'] = box.get('font_bold', True)
                elif box.get('type') == 'body':
                    if body_font['name'] == 'Arial':  # 只更新第一次
                        body_font['name'] = box.get('font_name', 'Arial')
                        body_font['size'] = box.get('font_size', 18)
        
        # 提取颜色方案
        color_scheme = content_page.get('color_scheme', {})
        primary = color_scheme.get('primary', content_bg)
        secondary = color_scheme.get('secondary', '1E3A8A')
        
        return {
            'colors': {
                'title_slide': {
                    'primary': title_bg,
                    'secondary': secondary
                },
                'content_slide': {
                    'primary': content_bg,
                    'secondary': primary
                }
            },
            'fonts': {
                'title': title_font,
                'body': body_font
            }
        }


# 全局实例
vision_service = VisionService()