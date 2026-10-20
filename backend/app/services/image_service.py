"""
图片服务
优先使用AI生图，失败时回退到全网搜索与占位图。
"""
from typing import List
import requests
import os
import time
import logging

# 配置日志
logger = logging.getLogger(__name__)


class ImageService:
    """图片服务类"""

    def __init__(self):
        # AI生图配置（使用bltcy API）
        self.image_gen_api_url = os.getenv('IMAGE_GEN_API_URL', 'https://api.bltcy.cn/v1/images/generations')
        self.image_gen_api_key = os.getenv('IMAGE_GEN_API_KEY', '')
        self.image_gen_model = os.getenv('IMAGE_GEN_MODEL', 'qwen-image')
        self.image_gen_timeout = int(os.getenv('IMAGE_GEN_TIMEOUT', '60'))

        # 视觉模型配置
        self.vision_api_url = os.getenv('VISION_API_URL', 'https://api.bltcy.cn/v1/chat/completions')
        self.vision_api_key = os.getenv('VISION_API_KEY', '')
        self.vision_model = os.getenv('VISION_MODEL', 'qwen3-vl-235b-a22b')

        # 传统图库API
        self.unsplash_access_key = os.getenv('UNSPLASH_ACCESS_KEY', '')
        self.pexels_api_key = os.getenv('PEXELS_API_KEY', '')

        logger.info("[IMAGE] 图片服务初始化完成")
        logger.info(f"[IMAGE] 生图模型: {self.image_gen_model}")
        logger.info(f"[IMAGE] 视觉模型: {self.vision_model}")

    def search_images(self, query: str, num_images: int = 1) -> List[str]:
        """
        搜索/生成图片

        优先级：
        1. AI生图（qwen-image）
        2. Unsplash API（如果配置）
        3. Pexels API（如果配置）
        4. 全网搜索（LLM联网）

        Args:
            query: 搜索关键词
            num_images: 需要的图片数量

        Returns:
            图片URL列表
        """
        logger.info(f"[IMAGE] 开始搜索图片: {query}, 数量: {num_images}")

        # 1. 优先使用AI生图
        generated_urls = self._generate_with_ai(query, num_images)
        if generated_urls:
            logger.info(f"[IMAGE] AI生图成功: {len(generated_urls)}张")
            return generated_urls

        # 2. 尝试Unsplash
        if self.unsplash_access_key:
            urls = self._search_unsplash(query, num_images)
            if urls:
                logger.info(f"[IMAGE] Unsplash搜索成功: {len(urls)}张")
                return urls

        # 3. 尝试Pexels
        if self.pexels_api_key:
            urls = self._search_pexels(query, num_images)
            if urls:
                logger.info(f"[IMAGE] Pexels搜索成功: {len(urls)}张")
                return urls

        # 4. 回退到全网搜索
        urls = self._search_with_web(query, num_images)
        if urls:
            logger.info(f"[IMAGE] 全网搜索成功: {len(urls)}张")
            return urls

        logger.warning(f"[IMAGE] 所有图片搜索方式均失败")
        return []

    def _generate_with_ai(self, query: str, num_images: int) -> List[str]:
        """使用AI生成图片"""
        if not self.image_gen_api_key:
            logger.debug("[IMAGE] 未配置AI生图API密钥")
            return []

        try:
            logger.info(f"[IMAGE] 开始AI生图: {query}")
            
            headers = {
                "Authorization": f"Bearer {self.image_gen_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.image_gen_model,
                "prompt": f"{query}，高清、专业、适合教学PPT、16:9构图",
                "size": "1792x1024",
                "n": num_images
            }

            response = requests.post(
                self.image_gen_api_url,
                headers=headers,
                json=payload,
                timeout=self.image_gen_timeout
            )
            response.raise_for_status()
            data = response.json()

            # 提取图片URL
            urls = []
            if 'data' in data:
                for item in data['data']:
                    if isinstance(item, dict):
                        url = item.get('url') or item.get('image_url')
                        if url and url.startswith('http'):
                            urls.append(url)

            if urls:
                logger.info(f"[IMAGE] AI生图成功，获取{len(urls)}张图片")
            return urls[:num_images]

        except Exception as e:
            logger.error(f"[IMAGE] AI生图失败: {e}")
            return []

    def _search_with_web(self, query: str, num_images: int) -> List[str]:
        """使用LLM联网搜索图片"""
        try:
            from app.services import glm_service

            messages = [
                {
                    "role": "system",
                    "content": "你是图片搜索专家。使用联网搜索找到真实可访问的图片URL。"
                },
                {
                    "role": "user",
                    "content": f"""请使用联网搜索，找到"{query}"相关的{num_images}张高质量图片。

要求：
1. 使用Bing/Google/百度等搜索引擎联网搜索
2. 高清、专业、美观
3. 横向图片（适合PPT）
4. 只返回URL，每行一个
5. 确保URL真实可访问"""
                }
            ]

            response = glm_service.chat(messages, temperature=0.3, enable_web_search=True)
            content = response.get('content', '')

            # 提取URL
            urls = []
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('http') and 'example.com' not in line:
                    urls.append(line)
                    if len(urls) >= num_images:
                        break

            return urls

        except Exception as e:
            logger.error(f"[IMAGE] 全网搜索失败: {e}")
            return []

    def _search_unsplash(self, query: str, num_images: int) -> List[str]:
        """使用Unsplash API搜索图片"""
        try:
            url = "https://api.unsplash.com/search/photos"
            headers = {"Authorization": f"Client-ID {self.unsplash_access_key}"}
            params = {
                "query": query,
                "per_page": num_images,
                "orientation": "landscape"
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = data.get('results', [])

            urls = []
            for result in results[:num_images]:
                image_url = result.get('urls', {}).get('regular')
                if image_url:
                    urls.append(image_url)

            return urls

        except Exception as e:
            logger.error(f"[IMAGE] Unsplash搜索失败: {e}")
            return []

    def _search_pexels(self, query: str, num_images: int) -> List[str]:
        """使用Pexels API搜索图片"""
        try:
            url = "https://api.pexels.com/v1/search"
            headers = {"Authorization": self.pexels_api_key}
            params = {
                "query": query,
                "per_page": num_images,
                "orientation": "landscape"
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            photos = data.get('photos', [])

            urls = []
            for photo in photos[:num_images]:
                image_url = photo.get('src', {}).get('large')
                if image_url:
                    urls.append(image_url)

            return urls

        except Exception as e:
            logger.error(f"[IMAGE] Pexels搜索失败: {e}")
            return []

    def get_placeholder_image(self, width: int = 1920, height: int = 1080,
                             text: str = "Image") -> str:
        """获取占位图片URL"""
        try:
            from urllib.parse import quote
            encoded_text = quote(text)
            
            url = f"https://placehold.co/{width}x{height}/3B82F6/FFFFFF?text={encoded_text}"
            
            if self.validate_image_url(url):
                return url
            
            url2 = f"https://dummyimage.com/{width}x{height}/3B82F6/FFFFFF&text={encoded_text}"
            if self.validate_image_url(url2):
                return url2
            
            logger.warning("[IMAGE] 占位图服务不可用")
            return None
            
        except Exception as e:
            logger.error(f"[IMAGE] 获取占位图失败: {e}")
            return None

    def validate_image_url(self, url: str) -> bool:
        """验证图片URL是否可访问"""
        try:
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except:
            return False


# 全局图片服务实例
_image_service = None


def get_image_service() -> ImageService:
    """获取图片服务实例"""
    global _image_service
    if _image_service is None:
        _image_service = ImageService()
    return _image_service