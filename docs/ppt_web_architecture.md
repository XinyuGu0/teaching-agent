# PPT系统技术方案（修订版）

## 核心架构

### 数据流
```
AI生成内容(JSON) → 前端渲染(HTML/CSS/JS) → 用户编辑 → 后端导出(PPTX)
```

## 技术栈选择

### 方案对比

#### 方案1: reveal.js（推荐用于预览）
**优点：**
- 成熟的HTML演示框架
- 支持Markdown
- 内置主题和动画
- 支持PDF导出

**缺点：**
- 编辑功能需要自己实现
- 不是为编辑设计的

#### 方案2: Slidev（推荐用于快速原型）
**优点：**
- 基于Vue 3
- Markdown驱动
- 开发者友好
- 支持组件

**缺点：**
- 主要面向开发者
- 不适合非技术用户编辑

#### 方案3: 完全自定义（最终推荐）
**优点：**
- 完全控制
- 可以实现任意功能
- 最适合AI生成场景

**缺点：**
- 开发工作量大

## 最终推荐方案：混合架构

### 1. 前端渲染层

#### 1.1 PPT渲染组件
```vue
<!-- SlideRenderer.vue -->
<template>
  <div class="slide-container" :style="slideStyle">
    <!-- 背景 -->
    <div class="slide-background" :style="backgroundStyle"></div>

    <!-- 内容层 -->
    <div class="slide-content">
      <!-- 标题 -->
      <h1 v-if="slide.title"
          class="slide-title"
          :style="titleStyle">
        {{ slide.title }}
      </h1>

      <!-- 文本内容 -->
      <div v-if="slide.content.text"
           class="slide-text"
           v-html="formatText(slide.content.text)">
      </div>

      <!-- 列表 -->
      <ul v-if="slide.content.bullets" class="slide-bullets">
        <li v-for="(item, index) in slide.content.bullets"
            :key="index"
            :class="['bullet-item', `animate-${slide.animations[index]?.type}`]">
          {{ item }}
        </li>
      </ul>

      <!-- 图片 -->
      <img v-for="(img, index) in slide.content.images"
           :key="index"
           :src="img.url"
           :style="getImageStyle(img)"
           class="slide-image" />

      <!-- 视频 -->
      <video v-for="(video, index) in slide.content.videos"
             :key="index"
             :src="video.url"
             :style="getVideoStyle(video)"
             controls
             class="slide-video">
      </video>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  slide: Object,
  theme: Object
})

const slideStyle = computed(() => ({
  width: '960px',
  height: '720px',
  backgroundColor: props.theme.colors.background,
  color: props.theme.colors.text,
  fontFamily: props.theme.fonts.body
}))

// ... 其他样式计算
</script>

<style scoped>
.slide-container {
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

/* 动画 */
.animate-fade-in {
  animation: fadeIn 0.5s ease-in;
}

.animate-slide-in {
  animation: slideIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}
</style>
```

#### 1.2 编辑器组件
```vue
<!-- SlideEditor.vue -->
<template>
  <div class="slide-editor">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-button-group>
        <el-button :icon="Edit" @click="editMode = 'text'">文本</el-button>
        <el-button :icon="Picture" @click="addImage">图片</el-button>
        <el-button :icon="VideoPlay" @click="addVideo">视频</el-button>
        <el-button :icon="MagicStick" @click="aiModify">AI修改</el-button>
      </el-button-group>
    </div>

    <!-- 编辑区域 -->
    <div class="edit-area" ref="editArea">
      <SlideRenderer :slide="currentSlide" :theme="theme" />

      <!-- 编辑覆盖层 -->
      <div class="edit-overlay" v-if="editMode">
        <!-- 文本编辑 -->
        <div v-if="editMode === 'text'" class="text-editor">
          <el-input v-model="currentSlide.title" placeholder="标题" />
          <el-input type="textarea" v-model="currentSlide.content.text" />
        </div>

        <!-- 元素选择和拖拽 -->
        <div v-for="(element, index) in editableElements"
             :key="index"
             class="editable-element"
             :style="element.style"
             @mousedown="startDrag(element)">
          <!-- 调整大小的控制点 -->
          <div class="resize-handle" @mousedown.stop="startResize(element)"></div>
        </div>
      </div>
    </div>

    <!-- 属性面板 -->
    <div class="properties-panel">
      <el-form label-position="top">
        <el-form-item label="布局">
          <el-select v-model="currentSlide.layout">
            <el-option label="标题页" value="title" />
            <el-option label="内容页" value="content" />
            <el-option label="两栏" value="two-column" />
            <el-option label="图片" value="image" />
          </el-select>
        </el-form-item>

        <el-form-item label="背景">
          <el-color-picker v-model="currentSlide.background" />
        </el-form-item>

        <el-form-item label="动画">
          <el-select v-model="currentSlide.animation">
            <el-option label="无" value="none" />
            <el-option label="淡入" value="fade-in" />
            <el-option label="滑入" value="slide-in" />
          </el-select>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>
```

### 2. 后端导出层

#### 2.1 JSON到PPTX转换器
```python
# backend/app/services/ppt_exporter.py

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import requests
from io import BytesIO
from PIL import Image

class PPTExporter:
    """将JSON格式的PPT数据转换为PPTX文件"""

    def __init__(self):
        self.prs = None
        self.theme = None

    def export(self, ppt_data):
        """
        导出PPT

        Args:
            ppt_data: JSON格式的PPT数据

        Returns:
            BytesIO: PPTX文件的字节流
        """
        self.prs = Presentation()
        self.theme = ppt_data.get('theme', {})

        # 设置幻灯片尺寸
        self.prs.slide_width = Inches(10)
        self.prs.slide_height = Inches(7.5)

        # 遍历每页
        for slide_data in ppt_data['slides']:
            self._create_slide(slide_data)

        # 保存到内存
        output = BytesIO()
        self.prs.save(output)
        output.seek(0)

        return output

    def _create_slide(self, slide_data):
        """创建单页幻灯片"""
        layout_type = slide_data.get('layout', 'content')
        layout = self._get_layout(layout_type)

        slide = self.prs.slides.add_slide(layout)

        # 设置背景
        self._set_background(slide, slide_data.get('background'))

        # 添加标题
        if slide_data.get('title'):
            self._add_title(slide, slide_data['title'])

        # 添加内容
        content = slide_data.get('content', {})

        if content.get('text'):
            self._add_text(slide, content['text'])

        if content.get('bullets'):
            self._add_bullets(slide, content['bullets'])

        if content.get('images'):
            for img_data in content['images']:
                self._add_image(slide, img_data)

        if content.get('videos'):
            for video_data in content['videos']:
                self._add_video(slide, video_data)

        # 添加动画（有限支持）
        if slide_data.get('animations'):
            self._add_animations(slide, slide_data['animations'])

    def _get_layout(self, layout_type):
        """获取布局"""
        layout_map = {
            'title': 0,
            'content': 1,
            'two-column': 3,
            'blank': 6
        }
        layout_index = layout_map.get(layout_type, 1)
        return self.prs.slide_layouts[layout_index]

    def _set_background(self, slide, background):
        """设置背景"""
        if not background:
            return

        # 纯色背景
        if isinstance(background, str) and background.startswith('#'):
            fill = slide.background.fill
            fill.solid()
            rgb = self._hex_to_rgb(background)
            fill.fore_color.rgb = RGBColor(*rgb)

        # 图片背景
        elif isinstance(background, dict) and background.get('image'):
            # 下载图片
            img_data = self._download_image(background['image'])
            # 添加为背景（需要特殊处理）
            pass

    def _add_title(self, slide, title_text):
        """添加标题"""
        if slide.shapes.title:
            title = slide.shapes.title
            title.text = title_text

            # 应用主题样式
            if self.theme.get('fonts', {}).get('title'):
                font = title.text_frame.paragraphs[0].font
                font_config = self.theme['fonts']['title']
                font.name = font_config.get('family', 'Arial')
                font.size = Pt(font_config.get('size', 44))
                font.bold = font_config.get('bold', True)

    def _add_text(self, slide, text):
        """添加文本框"""
        left = Inches(1)
        top = Inches(2)
        width = Inches(8)
        height = Inches(4)

        textbox = slide.shapes.add_textbox(left, top, width, height)
        text_frame = textbox.text_frame
        text_frame.text = text

        # 应用样式
        p = text_frame.paragraphs[0]
        p.font.size = Pt(18)

    def _add_bullets(self, slide, bullets):
        """添加项目符号列表"""
        # 使用内容占位符
        if len(slide.placeholders) > 1:
            content = slide.placeholders[1]
            text_frame = content.text_frame
            text_frame.clear()

            for bullet in bullets:
                p = text_frame.add_paragraph()
                p.text = bullet
                p.level = 0

    def _add_image(self, slide, img_data):
        """添加图片"""
        # 下载图片
        img_bytes = self._download_image(img_data['url'])

        # 处理图片
        img = Image.open(BytesIO(img_bytes))

        # 压缩和优化
        if img.width > 1920 or img.height > 1080:
            img.thumbnail((1920, 1080), Image.LANCZOS)

        # 保存到内存
        output = BytesIO()
        img.save(output, format='PNG', optimize=True)
        output.seek(0)

        # 添加到幻灯片
        position = img_data.get('position', {})
        left = Inches(position.get('x', 1))
        top = Inches(position.get('y', 2))
        width = Inches(position.get('width', 4))

        slide.shapes.add_picture(output, left, top, width=width)

    def _add_video(self, slide, video_data):
        """添加视频"""
        # 注意：PPTX只支持嵌入本地视频文件
        # 网络视频需要先下载
        video_path = self._download_video(video_data['url'])

        position = video_data.get('position', {})
        left = Inches(position.get('x', 1))
        top = Inches(position.get('y', 2))
        width = Inches(position.get('width', 6))
        height = Inches(position.get('height', 4))

        slide.shapes.add_movie(
            video_path,
            left, top, width, height,
            poster_frame_image=video_data.get('thumbnail')
        )

    def _add_animations(self, slide, animations):
        """添加动画（有限支持）"""
        # python-pptx对动画支持有限
        # 基础动画可以通过操作XML实现
        pass

    def _download_image(self, url):
        """下载图片"""
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content

    def _download_video(self, url):
        """下载视频"""
        # 实现视频下载逻辑
        pass

    def _hex_to_rgb(self, hex_color):
        """十六进制颜色转RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
```

### 3. API设计

#### 3.1 WebSocket事件
```javascript
// 生成PPT内容（JSON格式）
socket.emit('generate_ppt_content', {
  conversation_id: 'uuid',
  outline: {...},
  theme: 'modern'
})

// 接收生成的内容
socket.on('ppt_content_generated', (data) => {
  // data: { ppt_id: 'uuid', slides: [...], theme: {...} }
  // 前端直接渲染
})

// 更新单页
socket.emit('update_slide', {
  ppt_id: 'uuid',
  slide_number: 3,
  updates: {...}
})

// AI修改
socket.emit('ai_modify_slide', {
  ppt_id: 'uuid',
  slide_number: 3,
  instruction: '把这页改简洁点'
})

// 导出PPTX
socket.emit('export_pptx', {
  ppt_id: 'uuid'
})

// 接收导出结果
socket.on('pptx_exported', (data) => {
  // data: { download_url: '/api/ppt/uuid/download' }
})
```

### 4. 数据库模型

```python
# backend/app/models/ppt.py

from app.extensions import db
from datetime import datetime
import uuid

class PPT(db.Model):
    """PPT项目"""
    __tablename__ = 'ppts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = db.Column(db.String(36), db.ForeignKey('conversations.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    theme = db.Column(db.String(50), default='modern')

    # JSON格式存储幻灯片数据
    slides_data = db.Column(db.JSON, nullable=False)

    # 导出的PPTX文件路径
    pptx_file_path = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    conversation = db.relationship('Conversation', backref='ppts')
    user = db.relationship('User', backref='ppts')

    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'title': self.title,
            'theme': self.theme,
            'slides': self.slides_data,
            'pptx_url': f'/api/ppt/{self.id}/download' if self.pptx_file_path else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
```

## 实现优先级

### Phase 1: 基础渲染和导出
1. ✅ 数据库模型
2. [ ] 前端渲染组件（SlideRenderer）
3. [ ] AI生成JSON格式内容
4. [ ] 后端导出器（PPTExporter）
5. [ ] 基础主题（1-2个）

### Phase 2: 编辑功能
1. [ ] 文本编辑
2. [ ] 图片上传和插入
3. [ ] 布局切换
4. [ ] 幻灯片排序

### Phase 3: 高级功能
1. [ ] 可视化编辑器
2. [ ] 动画效果
3. [ ] AI辅助修改
4. [ ] 更多主题

## 关键优势

1. **Web原生**：完全在浏览器中渲染和编辑
2. **实时预览**：所见即所得
3. **灵活编辑**：支持任意修改
4. **AI集成**：对话式修改
5. **标准导出**：最终导出为标准PPTX格式

## 技术挑战

1. **动画同步**：Web动画和PPTX动画的映射
2. **字体兼容**：Web字体和Office字体的差异
3. **视频处理**：网络视频到本地文件的转换
4. **性能优化**：大量幻灯片的渲染性能
