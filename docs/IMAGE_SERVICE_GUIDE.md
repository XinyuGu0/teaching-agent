# 图片服务配置指南

## 概述

系统支持多种图片来源，优先级如下：
1. Unsplash API（免费，高质量）
2. Pexels API（免费，商用）
3. LLM联网搜索（回退方案）
4. 占位图（最后方案）

## Unsplash API配置

### 1. 注册Unsplash开发者账号

访问：https://unsplash.com/developers

### 2. 创建应用

- 登录后点击"New Application"
- 填写应用信息
- 同意条款
- 获取Access Key

### 3. 配置环境变量

在`.env`文件中添加：

```bash
UNSPLASH_ACCESS_KEY=your_access_key_here
```

### 4. 使用限制

- 免费版：50次请求/小时
- 演示版：50次请求/小时
- 生产版：5000次请求/小时（需申请）

## Pexels API配置

### 1. 注册Pexels账号

访问：https://www.pexels.com/api/

### 2. 获取API Key

- 登录后访问API页面
- 点击"Get Started"
- 获取API Key

### 3. 配置环境变量

在`.env`文件中添加：

```bash
PEXELS_API_KEY=your_api_key_here
```

### 4. 使用限制

- 免费版：200次请求/小时
- 无需申请，注册即可使用

## 推荐配置

### 开发环境

使用Pexels API（更容易获取，限制更宽松）

```bash
PEXELS_API_KEY=your_api_key_here
```

### 生产环境

同时配置两个API，提高可用性

```bash
UNSPLASH_ACCESS_KEY=your_access_key_here
PEXELS_API_KEY=your_api_key_here
```

## 回退方案

如果没有配置任何图片API，系统会：
1. 使用GLM联网搜索图片（可能不稳定）
2. 如果搜索失败，使用占位图

## 测试图片服务

```python
from app.services.image_service import get_image_service

# 获取图片服务
image_service = get_image_service()

# 搜索图片
urls = image_service.search_images("人工智能", num_images=3)
print(urls)

# 验证URL
for url in urls:
    is_valid = image_service.validate_image_url(url)
    print(f"{url}: {'有效' if is_valid else '无效'}")
```

## 常见问题

### Q: 为什么图片搜索失败？

A: 可能的原因：
1. 没有配置API密钥
2. API密钥无效或过期
3. 超过请求限制
4. 网络连接问题

### Q: 如何提高图片质量？

A:
1. 优先使用Unsplash（图片质量更高）
2. 优化搜索关键词（更具体、更准确）
3. 配置多个API作为备份

### Q: 占位图是什么？

A: 当所有图片搜索方案都失败时，系统会使用placeholder.com生成一个带文字的占位图，确保PPT生成不会失败。

## 性能优化

### 缓存图片URL

可以在数据库中缓存已搜索的图片URL，避免重复搜索：

```python
# 伪代码
def search_with_cache(query):
    # 先查缓存
    cached_url = db.get_cached_image(query)
    if cached_url:
        return cached_url

    # 搜索新图片
    url = image_service.search_images(query)[0]

    # 保存到缓存
    db.cache_image(query, url)

    return url
```

### 批量预加载

在生成PPT前，可以批量预加载所有需要的图片：

```python
# 伪代码
def preload_images(slides):
    queries = [slide['title'] for slide in slides]

    # 批量搜索
    for query in queries:
        image_service.search_images(query)
```

## 未来改进

1. **AI图片生成**：集成DALL-E或Stable Diffusion
2. **本地图片库**：建立本地图片数据库
3. **智能推荐**：根据内容类型推荐最合适的图片
4. **图片编辑**：自动裁剪、调整大小、添加滤镜
