# PPT生成系统设计文档

## 1. 数据结构

### 1.1 PPT项目数据结构
```json
{
  "id": "uuid",
  "conversation_id": "uuid",
  "title": "PPT标题",
  "theme": "modern",  // 主题：modern, business, academic, creative
  "slides": [
    {
      "slide_number": 1,
      "type": "title",  // title, content, image, video, chart
      "layout": "title_slide",
      "title": "幻灯片标题",
      "content": {
        "text": "正文内容",
        "bullet_points": ["要点1", "要点2"],
        "images": [
          {
            "url": "图片URL或路径",
            "position": {"x": 100, "y": 100, "width": 400, "height": 300},
            "caption": "图片说明"
          }
        ],
        "videos": [
          {
            "url": "视频URL",
            "thumbnail": "缩略图URL",
            "position": {"x": 100, "y": 100, "width": 640, "height": 480}
          }
        ]
      },
      "animations": [
        {
          "element": "title",
          "type": "fade_in",  // fade_in, slide_in, zoom_in
          "duration": 0.5,
          "delay": 0
        }
      ],
      "notes": "演讲备注"
    }
  ],
  "metadata": {
    "created_at": "2024-03-09T12:00:00Z",
    "updated_at": "2024-03-09T12:30:00Z",
    "author": "用户名",
    "version": 1
  }
}
```

## 2. 技术栈

### 2.1 后端技术
- **python-pptx**: PPTX文件生成和操作
- **Pillow**: 图片处理（裁剪、压缩、格式转换）
- **requests**: 下载网络资源
- **moviepy**: 视频处理（可选）

### 2.2 前端技术
- **reveal.js**: PPT预览和演示
- **Fabric.js**: Canvas编辑器（拖拽、缩放、旋转）
- **vue-draggable**: 幻灯片排序
- **Element Plus**: UI组件

### 2.3 AI集成
- **GLM-4**: 内容生成
- **Web Search**: 图片搜索
- **DALL-E/SD**: AI图片生成（可选）

## 3. 实现流程

### 3.1 阶段1：内容生成
```
用户确认大纲
    ↓
AI生成每页详细内容
    ↓
AI推荐配图（搜索或生成）
    ↓
保存到数据库
```

### 3.2 阶段2：PPTX生成
```python
# 伪代码
def generate_pptx(ppt_data):
    prs = Presentation()

    # 设置主题
    apply_theme(prs, ppt_data['theme'])

    # 遍历每页
    for slide_data in ppt_data['slides']:
        # 选择布局
        layout = get_layout(slide_data['layout'])
        slide = prs.slides.add_slide(layout)

        # 添加标题
        add_title(slide, slide_data['title'])

        # 添加内容
        add_content(slide, slide_data['content'])

        # 添加图片
        for img in slide_data['content']['images']:
            add_image(slide, img)

        # 添加动画
        for anim in slide_data['animations']:
            add_animation(slide, anim)

    # 保存文件
    prs.save('output.pptx')
```

### 3.3 阶段3：预览生成
```python
# 将PPTX转换为预览格式
def convert_to_preview(pptx_path):
    # 方案1: 转换为图片
    slides_images = convert_pptx_to_images(pptx_path)

    # 方案2: 转换为HTML（reveal.js格式）
    html_content = convert_pptx_to_html(pptx_path)

    # 方案3: 返回JSON数据，前端渲染
    preview_data = {
        'slides': [...],
        'theme': '...',
        'assets': [...]
    }

    return preview_data
```

### 3.4 阶段4：前端编辑
```vue
<template>
  <div class="ppt-editor">
    <!-- 幻灯片列表 -->
    <div class="slides-sidebar">
      <draggable v-model="slides" @end="onSlideReorder">
        <div v-for="(slide, index) in slides" :key="slide.id"
             :class="['slide-thumbnail', { active: currentSlide === index }]"
             @click="selectSlide(index)">
          <img :src="slide.thumbnail" />
          <span>{{ index + 1 }}</span>
        </div>
      </draggable>
    </div>

    <!-- 编辑区域 -->
    <div class="edit-area">
      <canvas ref="fabricCanvas"></canvas>
    </div>

    <!-- 属性面板 -->
    <div class="properties-panel">
      <el-form>
        <el-form-item label="标题">
          <el-input v-model="currentSlideData.title" />
        </el-form-item>
        <el-form-item label="布局">
          <el-select v-model="currentSlideData.layout">
            <el-option label="标题页" value="title_slide" />
            <el-option label="内容页" value="content" />
            <el-option label="图片页" value="image" />
          </el-select>
        </el-form-item>
        <!-- 更多属性 -->
      </el-form>
    </div>
  </div>
</template>
```

## 4. 主题系统

### 4.1 预设主题
```python
THEMES = {
    'modern': {
        'colors': {
            'primary': '#409EFF',
            'secondary': '#67C23A',
            'background': '#FFFFFF',
            'text': '#303133'
        },
        'fonts': {
            'title': ('Microsoft YaHei', 44, True),
            'body': ('Microsoft YaHei', 18, False)
        },
        'layouts': ['title_slide', 'content', 'two_column', 'image_full']
    },
    'business': {
        'colors': {
            'primary': '#1F3A93',
            'secondary': '#2E86AB',
            'background': '#F5F5F5',
            'text': '#2C3E50'
        },
        'fonts': {
            'title': ('Arial', 44, True),
            'body': ('Arial', 18, False)
        }
    },
    'academic': {
        'colors': {
            'primary': '#2C3E50',
            'secondary': '#8E44AD',
            'background': '#FFFFFF',
            'text': '#34495E'
        },
        'fonts': {
            'title': ('Times New Roman', 44, True),
            'body': ('Times New Roman', 18, False)
        }
    }
}
```

## 5. 动画系统

### 5.1 支持的动画类型
- **进入动画**: fade_in, slide_in, zoom_in, bounce_in
- **强调动画**: pulse, shake, spin
- **退出动画**: fade_out, slide_out, zoom_out

### 5.2 动画实现
```python
from pptx.util import Inches
from pptx.enum.shapes import MSO_SHAPE

def add_animation(slide, element, animation_type):
    """
    添加动画效果
    注意：python-pptx对动画支持有限，复杂动画需要直接操作XML
    """
    # 基础动画可以通过python-pptx实现
    # 复杂动画需要操作slide._element的XML
    pass
```

## 6. 图片和视频处理

### 6.1 图片处理流程
```python
def process_image(image_url, target_size=(800, 600)):
    """处理图片：下载、压缩、裁剪"""
    # 下载图片
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))

    # 调整大小
    img.thumbnail(target_size, Image.LANCZOS)

    # 压缩
    output = BytesIO()
    img.save(output, format='JPEG', quality=85, optimize=True)

    return output.getvalue()
```

### 6.2 视频处理
```python
def add_video_to_slide(slide, video_url, position):
    """
    添加视频到幻灯片
    注意：PPTX支持嵌入视频，但需要本地文件
    """
    # 下载视频
    video_path = download_video(video_url)

    # 添加到幻灯片
    left, top, width, height = position
    slide.shapes.add_movie(
        video_path,
        Inches(left), Inches(top),
        Inches(width), Inches(height)
    )
```

## 7. API设计

### 7.1 WebSocket事件
```javascript
// 生成PPT
socket.emit('generate_ppt', {
  conversation_id: 'uuid',
  user_id: 'uuid',
  outline: {...},
  theme: 'modern',
  options: {
    include_images: true,
    include_animations: true
  }
})

// 接收生成进度
socket.on('ppt_generation_progress', (data) => {
  // data: { progress: 50, message: '正在生成第5页...' }
})

// 接收完成通知
socket.on('ppt_generated', (data) => {
  // data: { ppt_id: 'uuid', preview_url: '...', download_url: '...' }
})

// 更新单页
socket.emit('update_slide', {
  ppt_id: 'uuid',
  slide_number: 3,
  updates: {...}
})

// AI修改单页
socket.emit('ai_modify_slide', {
  ppt_id: 'uuid',
  slide_number: 3,
  instruction: '把这页改成更简洁的风格'
})
```

### 7.2 REST API
```
POST /api/ppt/generate          # 生成PPT
GET  /api/ppt/:id               # 获取PPT信息
PUT  /api/ppt/:id               # 更新PPT
GET  /api/ppt/:id/preview       # 获取预览数据
GET  /api/ppt/:id/download      # 下载PPTX文件
POST /api/ppt/:id/slides/:num   # 更新单页
DELETE /api/ppt/:id/slides/:num # 删除单页
POST /api/ppt/:id/slides        # 添加新页
```

## 8. 实现优先级

### Phase 1: 基础生成（MVP）
- [x] 数据库模型设计
- [ ] python-pptx基础集成
- [ ] 简单主题支持（1-2个）
- [ ] 文本内容生成
- [ ] 基础布局（标题页、内容页）
- [ ] 导出PPTX功能

### Phase 2: 预览和编辑
- [ ] 预览数据生成
- [ ] 前端预览组件（reveal.js）
- [ ] 基础编辑功能（修改文本）
- [ ] 幻灯片排序

### Phase 3: 多媒体支持
- [ ] 图片搜索和插入
- [ ] 图片处理和优化
- [ ] 视频支持
- [ ] AI图片生成（可选）

### Phase 4: 高级功能
- [ ] 可视化编辑器（Fabric.js）
- [ ] 动画系统
- [ ] 更多主题和布局
- [ ] 批量AI修改
- [ ] 模板系统

## 9. 技术挑战和解决方案

### 9.1 挑战：python-pptx动画支持有限
**解决方案**：
- 基础动画使用python-pptx
- 复杂动画直接操作XML
- 或使用预设模板

### 9.2 挑战：PPTX预览性能
**解决方案**：
- 生成缩略图缓存
- 使用WebWorker处理大文件
- 懒加载幻灯片

### 9.3 挑战：实时协作编辑
**解决方案**：
- WebSocket实时同步
- 操作队列和冲突解决
- 版本控制

## 10. 示例代码

### 10.1 生成简单PPT
```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

def create_simple_ppt(title, slides_data):
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    # 标题页
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title_shape = slide.shapes.title
    title_shape.text = title

    # 内容页
    for slide_data in slides_data:
        content_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(content_layout)

        # 标题
        title_shape = slide.shapes.title
        title_shape.text = slide_data['title']

        # 内容
        content_shape = slide.placeholders[1]
        tf = content_shape.text_frame

        for point in slide_data['points']:
            p = tf.add_paragraph()
            p.text = point
            p.level = 0

    return prs
```
