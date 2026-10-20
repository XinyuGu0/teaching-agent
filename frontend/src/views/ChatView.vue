<template>
  <div class="chat-view invert-on-light">
    <!-- Background Effects -->
    <div class="background-effects">
      <div class="glow glow-1"></div>
      <div class="glow glow-2"></div>
    </div>

    <div class="chat-layout">
      <!-- Left sidebar -->
      <aside v-if="!isCollabMode" class="chat-sidebar">
        <div class="sidebar-header">
          <div class="sidebar-brand">
            <span class="brand-text">对话历史</span>
          </div>
          <button class="new-chat-btn" @click="handleNewConversation" title="新对话">
            <Plus :size="16" style="flex-shrink: 0;" />
          </button>
        </div>

        <div class="conversation-list">
          <div
            v-for="conv in conversations"
            :key="conv.id"
            :class="['conversation-item', { active: conv.id === conversationId }]"
            @click="selectConversation(conv.id)"
          >
            <div class="conv-info">
              <div class="conv-title">{{ conv.title }}</div>
              <div class="conv-time">{{ formatConversationTime(conv.updated_at) }}</div>
            </div>
            <div class="conv-actions">
              <button class="conv-action-btn" @click.stop="handleRenameConversation(conv)" title="重命名">
                <Edit :size="12" />
              </button>
              <button class="conv-action-btn" @click.stop="handleShareConversation(conv)" title="分享">
                <Share :size="12" />
              </button>
              <button class="conv-action-btn" @click.stop="handleDeleteConversation(conv)" title="删除">
                <Delete :size="12" />
              </button>
            </div>
          </div>

          <div v-if="conversations.length === 0" class="empty-conversations">
            <div class="empty-icon">
              <ChatDotRound :size="32" />
            </div>
            <p>暂无对话记录</p>
          </div>
        </div>
      </aside>

      <!-- Main chat area -->
      <main class="chat-main-area">
        <!-- 左侧：对话区域 -->
<!-- Header -->
        <header class="chat-header-modern">
          <div class="chat-peer-info">
            <div class="peer-avatar-wrap">
              <img class="peer-avatar ai-avatar-img" :src="aiAvatar" alt="AI助手" />
              <span class="peer-status-dot" :class="conversationState === 'COMPLETED' ? 'status-idle' : 'status-online'" />
              <!-- 协作者头像 -->
              <div v-if="isCollabMode" class="collab-avatar-badge">
                <img v-if="collabAvatarUrl" :src="collabAvatarUrl" alt="协作者" class="collab-avatar-img" />
                <span v-else class="collab-avatar-fallback">{{ (collabName || '?')[0] }}</span>
              </div>
            </div>
            <div class="peer-meta">
              <div class="peer-name">
                AI助手
                <span v-if="isCollabMode" class="collab-badge">协作中</span>
              </div>
              <div class="peer-status">
                {{ conversationState === 'COMPLETED' ? 'idle' : 'online' }}
                <span v-if="isCollabMode" class="collab-user-info">· {{ collabName }} 已加入</span>
              </div>
            </div>
          </div>

          <div class="header-right">
            <button
              v-if="showGenerateActions && canGenerateOutline"
              class="header-btn outline-btn"
              @click="handleGenerateOutline"
              :disabled="isGeneratingOutlineLocal"
            >
              <Document :size="14" />
              <span>{{ isGeneratingOutlineLocal ? '生成中...' : '生成大纲' }}</span>
            </button>
            <button
              v-if="showGenerateActions"
              class="header-btn ppt-btn"
              @click="handleHeaderGeneratePPT"
              :disabled="isGeneratingPPT"
            >
              <Document :size="14" />
              <span>{{ isGeneratingPPT ? '生成中...' : '生成PPT' }}</span>
            </button>
            <button class="header-btn back-btn" @click="$router.push('/dashboard')">
              <span>返回</span>
            </button>
          </div>
        </header>

        <!-- Messages -->
        <div class="messages-area modern-messages" ref="messagesContainer">
          <!-- PPT Generation Progress -->
          <div v-if="isGeneratingPPT" class="ppt-progress-overlay">
            <div class="progress-card">
              <h3>正在生成PPT...</h3>
              <div class="interfaces-progress">
                <div class="interfaces-progress-indicator" :style="{ transform: `translateX(-${100 - Math.max(0, Math.min(100, pptProgressDisplay || 0))}%)` }"></div>
              </div>
              <div class="progress-headline">
                <span class="progress-percent">{{ Math.round(pptProgressDisplay || 0) }}%</span>
                <span class="progress-text">{{ pptProgressMessage }}</span>
              </div>

              <!-- 任务条（PPT） -->
              <div class="plan-card">
                <div class="plan-title">生成任务</div>
                <ul class="plan-list">
                  <li v-for="task in pptPlanTasks" :key="task.id" :class="['plan-item', `status-${task.status}`]">
                    <span class="plan-icon">
                      <CheckCircle2 v-if="task.status === 'completed'" :size="15" />
                      <CircleDotDashed v-else-if="task.status === 'in-progress'" :size="15" class="spin" />
                      <Circle v-else :size="15" />
                    </span>
                    <div class="plan-content">
                      <div class="plan-item-title">{{ task.title }}</div>
                      <div class="plan-item-desc">{{ task.description }}</div>
                    </div>
                    <span class="plan-badge">{{ task.statusLabel }}</span>
                  </li>
                </ul>
              </div>

              <div class="progress-log-box" v-if="pptRecentLogs.length > 0">
                <div class="plan-title">过程日志</div>
                <div class="progress-log-list">
                  <div v-for="(log, idx) in pptRecentLogs" :key="`ppt-log-${idx}`" class="progress-log-item">
                    <span class="log-progress">{{ log.progress }}%</span>
                    <span class="log-message">{{ log.message }}</span>
                  </div>
                </div>
              </div>
              
              <div v-if="generatingSlides.length > 0" class="generating-slides">
                <h4>已生成 {{ generatingSlides.length }} 页</h4>
                <div class="slides-grid">
                  <div 
                    v-for="slide in generatingSlides" 
                    :key="slide.number" 
                    class="slide-preview"
                  >
                    <div class="slide-number">第 {{ slide.number }} 页</div>
                    <div class="slide-title">{{ slide.title }}</div>
                    <div class="slide-status">
                      <el-icon class="is-loading"><Loading /></el-icon>
                      已完成
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="messages.length === 0" class="empty-state">
            <div class="empty-glow"></div>
            <h2>开始新的对话</h2>
            <p>请输入您的教学主题，我会帮您生成PPT</p>
          </div>

          <template v-for="(message, idx) in messages" :key="message.id">
          <div
            :class="['modern-msg-row', message.role === 'user' ? (isCollabMode && message.user_id && message.user_id !== collabOwnerId ? 'is-user is-collab-user' : (isCollabMode ? 'is-user is-owner-user' : 'is-user')) : 'is-ai']"
          >
            <div :class="['modern-msg-inner', message.role === 'user' ? 'reverse' : '']">
              <div class="modern-avatar">
                <img
                  v-if="message.role !== 'user'"
                  class="ai-avatar-img"
                  :src="aiAvatar"
                  alt="AI"
                />
                <img
                  v-else
                  :src="userAvatarUrl"
                  alt="User"
                />
              </div>

              <div class="modern-msg-content-wrap">
                <div :class="['modern-bubble', message.role === 'user' ? 'bubble-user' : 'bubble-ai']">
                  <MessageContent
                    v-if="message.role === 'assistant'"
                    :content="message.content"
                    :thinkingContent="message.thinkingContent || ''"
                    :searchResults="message.searchResults || []"
                    :isStreaming="message.isStreaming || false"
                    :isSearchCounting="isSearchCounting && message.isStreaming"
                    @showSearchSources="openSearchPanel"
                  />

                  <div v-else class="message-text">
                    <!-- 用户消息：上方显示引用文件，下方显示文字 -->
                    <template v-if="getMessageAttachments(message.content).length > 0">
                      <div class="msg-attachments">
                        <div
                          v-for="(att, idx) in getMessageAttachments(message.content)"
                          :key="idx"
                          class="msg-att-card"
                          :class="getFileTagClass(att)"
                        >
                          <div class="msg-att-icon">
                            <component :is="getFileIcon(att)" :size="18" />
                          </div>
                          <span class="msg-att-name" :title="att">{{ att }}</span>
                        </div>
                      </div>
                      <div v-if="getMessageText(message.content)" class="msg-text-body">{{ getMessageText(message.content) }}</div>
                    </template>
                    <template v-else>{{ message.content.trim() }}</template>
                  </div>
                </div>

                <div class="modern-msg-meta">
                  <time class="message-time">{{ formatTime(message.created_at) }}</time>
                </div>
              </div>

              <!-- Outline Preview -->
              <div v-if="message.meta_data?.outline" class="outline-preview">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <el-card>
                      <template #header>
                        <div class="outline-header">
                          <span>PPT大纲</span>
                          <el-button 
                            type="success" 
                            size="small" 
                            @click="handleGeneratePPTFromOutline(message.meta_data.outline)"
                            :loading="isGeneratingPPT"
                          >
                            <el-icon><Document /></el-icon>
                            {{ isGeneratingPPT ? '生成中...' : '生成PPT' }}
                          </el-button>
                        </div>
                      </template>

                      <div class="outline-content">
                        <h3>{{ message.meta_data.outline.title }}</h3>
                        <div v-for="(slide, index) in message.meta_data.outline.slides"
                             :key="index" class="slide-item">
                          <div class="slide-number">幻灯片 {{ slide.slide_number }}</div>
                          <div class="slide-title">{{ slide.title }}</div>
                          <ul class="slide-points">
                            <li v-for="(point, pIndex) in slide.content_points" :key="pIndex">
                              {{ point }}
                            </li>
                          </ul>
                        </div>
                      </div>
                    </el-card>
                  </el-col>

                  <el-col :span="12">
                    <MindMap v-if="message.meta_data?.mindmap" :markdown="message.meta_data.mindmap" />
                  </el-col>
                </el-row>
              </div>

              <!-- PPT Preview -->
              <div v-if="message.meta_data?.type === 'ppt' && message.meta_data?.ppt_id" class="ppt-preview-card">
                <div class="ppt-card-modern">
                  <div class="ppt-card-head">
                    <div class="ppt-card-title-wrap">
                      <span class="ppt-card-dot"></span>
                      <span class="ppt-card-title">PPT 已生成</span>
                      <span class="ppt-card-tag">Ready</span>
                    </div>
                    <span class="ppt-card-time">{{ formatTime(message.created_at) }}</span>
                  </div>

                  <div class="ppt-card-body">
                    <p class="ppt-card-desc">文件已准备完成，可立即打开在线编辑或下载使用。</p>
                    <div class="ppt-card-actions">
                      <button class="ppt-card-btn primary" @click="openPPT(message.meta_data.ppt_id)">
                        <View :size="12" />
                        <span>打开编辑</span>
                      </button>
                      <button
                        v-if="!(lessonPlanMap[message.meta_data.ppt_id]?.generating) && !(lessonPlanMap[message.meta_data.ppt_id]?.done)"
                        class="ppt-card-btn lesson-btn"
                        @click="startGenerateLessonPlan(message.meta_data.ppt_id, message)"
                      >
                        <BookOpen :size="12" />
                        <span>生成教案</span>
                      </button>
                      <button
                        v-if="lessonPlanMap[message.meta_data.ppt_id]?.generating"
                        class="ppt-card-btn lesson-btn disabled"
                        disabled
                      >
                        <Loader2 :size="12" class="spin" />
                        <span>生成教案中...</span>
                      </button>
                    </div>
                  </div>
                </div>

                <!-- 教案生成进度 -->
                <div v-if="lessonPlanMap[message.meta_data.ppt_id]?.generating" class="lesson-progress-card">
                  <div class="lesson-progress-head">
                    <span class="lesson-progress-title">正在生成教案...</span>
                    <span class="lesson-progress-percent">{{ lessonPlanMap[message.meta_data.ppt_id]?.progress || 0 }}%</span>
                  </div>
                  <div class="lesson-progress-bar">
                    <div class="lesson-progress-fill" :style="{ width: (lessonPlanMap[message.meta_data.ppt_id]?.progress || 0) + '%' }"></div>
                  </div>
                  <div class="lesson-steps-list">
                    <div
                      v-for="(step, idx) in (lessonPlanMap[message.meta_data.ppt_id]?.steps || [])"
                      :key="idx"
                      class="lesson-step-item"
                      :class="step.status"
                    >
                      <span class="lesson-step-icon">
                        <CheckCircle2 v-if="step.status === 'completed'" :size="14" />
                        <Loader2 v-else-if="step.status === 'in-progress'" :size="14" class="spin" />
                        <Circle v-else :size="14" />
                      </span>
                      <span class="lesson-step-text">{{ step.text }}</span>
                    </div>
                  </div>
                  <div class="lesson-log-box" :ref="el => setLessonLogRef(message.meta_data.ppt_id, el)">
                    <div v-for="(log, idx) in (lessonPlanMap[message.meta_data.ppt_id]?.logs || [])" :key="idx" class="lesson-log-line">
                      <span class="lesson-log-time">[{{ log.time }}]</span>
                      <span class="lesson-log-msg">{{ log.msg }}</span>
                    </div>
                  </div>
                </div>

                <!-- 教案生成完成 -->
                <div v-if="lessonPlanMap[message.meta_data.ppt_id]?.done" class="lesson-done-card">
                  <div class="lesson-done-head">
                    <span class="lesson-done-dot success"></span>
                    <span class="lesson-done-title">教案已生成</span>
                  </div>
                  <div class="lesson-done-body">
                    <p class="lesson-done-desc">教案文件已准备完成，可在线预览或下载。</p>
                    <div class="lesson-done-actions">
                      <button class="ppt-card-btn primary" @click="previewLessonPlan(message.meta_data.ppt_id)">
                        <Eye :size="12" />
                        <span>在线预览</span>
                      </button>
                      <button class="ppt-card-btn lesson-btn" @click="downloadLessonPlan(message.meta_data.ppt_id)">
                        <Download :size="12" />
                        <span>下载教案</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- File Understanding Card: render after the last user message with attachments -->
          <div
            v-if="(fileReadingState.active || (fileReadingState.done && fileReadingState.fileResults.length > 0))
              && message.role === 'user'
              && getMessageAttachments(message.content).length > 0
              && !messages.slice(idx + 1).some(m => m.role === 'user')"
            class="modern-msg-row is-ai"
          >
            <div class="modern-msg-inner">
              <div class="modern-avatar">
                <img class="ai-avatar-img" :src="aiAvatar" alt="AI" />
              </div>
              <div class="modern-msg-content-wrap">
                <div class="modern-bubble bubble-ai">
                  <div class="file-reading-bubble">
                    <div class="file-reading-bubble-header">
                      <div class="file-reading-title-wrap">
                        <Loader2 v-if="!fileReadingState.done" :size="14" class="spin" />
                        <CheckCircle2 v-else :size="14" style="color:#34d399" />
                        <span class="file-reading-title">{{ fileReadingState.done ? '文件理解完成' : '正在理解文件...' }}</span>
                      </div>
                      <span class="file-reading-percent">{{ fileReadingState.progress }}%</span>
                    </div>
                    <div class="file-reading-bar">
                      <div class="file-reading-bar-fill" :style="{ width: fileReadingState.progress + '%' }"></div>
                    </div>
                    <!-- 视频理解时显示淡入淡出步骤文字，其他文件显示普通步骤 -->
                    <transition name="vu-fade" mode="out-in">
                      <div v-if="videoUnderstandingState.active" :key="videoUnderstandingState.currentIndex" class="file-reading-step vu-step-inline">
                        <Loader2 :size="12" class="spin" style="margin-right:5px;flex-shrink:0;" />
                        <span>{{ videoUnderstandingState.currentText }}</span>
                      </div>
                      <div v-else class="file-reading-step">{{ fileReadingState.step }}</div>
                    </transition>
                    <!-- 逐文件显示：每个文件完成后直接在其下方展示理解结果 -->
                    <div class="file-reading-files">
                      <div
                        v-for="(step, idx) in fileReadingState.steps"
                        :key="idx"
                        class="file-reading-item-wrap"
                      >
                        <div
                          class="file-reading-item"
                          :class="[step.status, `file-type-${step.category}`]"
                        >
                          <div class="file-reading-item-icon">
                            <CheckCircle2 v-if="step.status === 'done'" :size="13" />
                            <Loader2 v-else-if="step.status === 'reading'" :size="13" class="spin" />
                            <Circle v-else :size="13" />
                          </div>
                          <span class="file-reading-item-name">{{ step.name }}</span>
                          <span class="file-reading-item-status">
                            <template v-if="step.status === 'uploading'">上传中</template>
                            <template v-else-if="step.status === 'uploaded'">已上传</template>
                            <template v-else-if="step.status === 'reading'">理解中</template>
                            <template v-else-if="step.status === 'done'">已完成</template>
                          </span>
                        </div>
                        <!-- 文件完成后，紧接在其下方显示理解结果摘要 -->
                        <div
                          v-if="step.status === 'done' && fileReadingState.fileResults[idx]"
                          class="fr-result-card"
                          :class="`file-type-${fileReadingState.fileResults[idx].category}`"
                        >
                          <div class="fr-result-header">
                            <div class="fr-result-icon">
                              <component :is="getFileIcon(fileReadingState.fileResults[idx].name)" :size="14" />
                            </div>
                            <span class="fr-result-name" :title="fileReadingState.fileResults[idx].name">{{ fileReadingState.fileResults[idx].name }}</span>
                            <CheckCircle2 :size="13" style="color:#34d399;flex-shrink:0;" />
                          </div>
                          <div class="fr-result-summary">{{ fileReadingState.fileResults[idx].summary }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          </template>

          <!-- Typing Indicator -->
          <div v-if="isWaitingForResponse && (!fileReadingState.active || fileReadingState.done) && !videoUnderstandingState.active" class="message-item message-assistant">
            <div class="message-avatar">
              <img class="avatar ai-typing-avatar-img" :src="aiAvatar" alt="AI助手" />
            </div>
            <div class="message-body">
              <div class="message-meta">
                <span class="message-role">AI助手</span>
              </div>
              <div class="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer Input -->
        <footer  class="chat-footer">
          <div v-if="uploadedFiles.length > 0" class="uploaded-files">
            <div
              v-for="file in uploadedFiles"
              :key="file.id"
              class="file-tag"
            >
              <div class="file-tag-icon" :class="getFileTagClass(file.name)">
                <component :is="getFileIcon(file.name)" :size="14" />
              </div>
              <span class="file-tag-name" :title="file.name">{{ file.name }}</span>
              <button class="file-remove" @click="removeFile(file.id)">
                <X :size="10" />
              </button>
            </div>
          </div>

          <div class="input-box">
            <div class="input-actions">
              <input
                ref="chatUploadInput"
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.txt,.md,.ppt,.pptx,.xls,.xlsx,.jpg,.jpeg,.png,.gif,.mp4,.avi,.mov,.mp3,.wav,.m4a,.ogg,.flac,.aac"
                style="display:none"
                @change="handleChatFileInput"
              />
              <button class="action-icon-btn upload-btn" title="上传文件" @click="chatUploadInput?.click()">
                <Paperclip :size="14" />
              </button>
              <button
                :class="['action-icon-btn', { 'web-search-active': webSearchEnabled }]"
                title="联网搜索"
                @click="webSearchEnabled = !webSearchEnabled"
              >
                <Globe :size="22" />
              </button>
              <button
                v-if="speechSupported"
                :class="['action-icon-btn', { 'voice-active': isVoiceRecording }]"
                :title="isVoiceRecording ? '停止语音输入' : '语音输入'"
                @click="toggleVoiceInput"
              >
                <MicOff v-if="isVoiceRecording" :size="16" />
                <Mic v-else :size="16" />
              </button>
            </div>

            <textarea
              v-model="userInput"
              placeholder="输入您的消息..."
              @keydown.enter.exact.prevent="handleSend"
              :disabled="isSending"
              class="chat-textarea"
              rows="1"
            ></textarea>
            <div v-if="isVoiceRecording" class="voice-status">
              <span class="voice-dot"></span>
              <span class="voice-label">正在聆听{{ voiceInterimText ? '：' + voiceInterimText : '...' }}</span>
            </div>

            <button
              :class="['send-btn', { active: userInput.trim() || uploadedFiles.length > 0 }]"
              @click="handleSend"
              :disabled="!userInput.trim() && uploadedFiles.length === 0"
            >
              <Loader2 v-if="isSending" :size="16" class="spin" />
              <Send v-else :size="16" />
              <span>发送</span>
            </button>
          </div>
        </footer>

        
        <!-- 右侧搜索结果面板 -->
        <div v-if="showSearchPanel" class="search-panel">
          <div class="search-panel-header">
            <div class="search-panel-title-row">
              <Globe :size="15" class="search-panel-icon" />
              <span class="search-panel-title">搜索来源</span>
              <span class="search-panel-count">{{ searchPanelResults.length }}</span>
            </div>
            <button class="search-panel-close" @click="showSearchPanel = false">
              <X :size="15" />
            </button>
          </div>
          <div class="search-panel-list">
            <div v-for="group in searchPanelGroups" :key="group.key" class="search-panel-group">
              <div :class="['search-panel-group-header', `cat-${group.key}`]">
                <component :is="group.iconComponent" :size="13" :class="['search-panel-group-icon', `cat-${group.key}`]" />
                <span class="search-panel-group-label">{{ group.label }}</span>
                <span :class="['search-panel-group-count', `cat-${group.key}`]">{{ group.items.length }}</span>
              </div>
              <a
                v-for="(link, idx) in group.items"
                :key="idx"
                :href="link.url"
                target="_blank"
                rel="noopener noreferrer"
                class="search-panel-item"
              >
                <img
                  class="search-panel-favicon-img"
                  :src="'https://favicon.cccyun.cc/' + link.domain"
                  :alt="link.domain"
                  @error="$event.target.src='https://api.faviconkit.com/' + link.domain + '/32'"
                />
                <div class="search-panel-favicon" style="display:none">
                  <Globe :size="12" />
                </div>
                <div class="search-panel-info">
                  <div class="search-panel-item-site">
                    <span class="search-panel-item-sitename">{{ link.siteName || link.domain }}</span>
                    <span v-if="link.date" class="search-panel-item-date">{{ link.date }}</span>
                  </div>
                  <span class="search-panel-item-title">{{ link.title }}</span>
                  <span v-if="link.snippet" class="search-panel-item-snippet">{{ link.snippet }}</span>
                  <span v-else class="search-panel-item-url">{{ link.url }}</span>
                </div>
                <ExternalLink :size="12" class="search-panel-external" />
              </a>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- 模板选择对话框 -->
    <el-dialog
      v-model="showTemplateDialog"
      title="选择模板生成PPT"
      width="900px"
      :close-on-click-modal="false"
      class="template-dialog"
    >
      <div v-if="loadingTemplates" class="loading-templates">
        <el-icon class="is-loading"><Loading /></el-icon>
        <p>加载模板中...</p>
      </div>
      <div v-else class="template-selector">
        <el-tabs v-model="templateTab" class="template-tabs">
          <el-tab-pane label="内置模板" name="builtin">
            <div class="builtin-template-list">
              <div
                v-for="template in builtinTemplates"
                :key="template.id"
                :class="['builtin-template-card', { selected: selectedTemplate?.id === template.id }]"
                :style="getBuiltinTemplateCardStyle(template)"
                @click="selectedTemplate = template"
              >
                <div class="builtin-card-mask"></div>
                <div class="builtin-card-header">
                  <span class="builtin-name">{{ template.name }}</span>
                  <span class="builtin-name-en">{{ template.name_en }}</span>
                </div>
                <div class="builtin-card-tags">
                  <UiTag
                    v-for="tag in template.tags"
                    :key="tag"
                    variant="secondary"
                    class="builtin-tag"
                  >{{ tag }}</UiTag>
                </div>
                <div class="builtin-card-desc">{{ template.description }}</div>
              </div>
              <div v-if="builtinTemplates.length === 0" class="empty-templates">
                <el-empty description="暂无内置模板" />
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="我的模板" name="custom">
            <div class="template-grid">
              <div
                v-for="template in customTemplates"
                :key="template.id"
                :class="['template-item', { selected: selectedTemplate?.id === template.id }]"
                @click="selectedTemplate = template"
              >
                <div class="template-thumbnail">
                  <img
                    v-if="hasTemplateCover(template)"
                    :src="getTemplateCoverUrl(template, { preferById: true })"
                    :alt="template.name"
                  />
                  <div v-else class="placeholder">
                    <el-icon><Document /></el-icon>
                  </div>
                  <div class="template-badge custom">上传</div>
                </div>
                <div class="template-name">{{ template.name }}</div>
                <div class="template-category">
                  {{ categories[template.category] || '其他' }}
                </div>
              </div>
              <div v-if="customTemplates.length === 0" class="empty-templates">
                <el-empty description="暂无自定义模板，可前往模板管理上传" />
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>

        <div class="blank-generate-section">
          <div
            :class="['blank-generate-card', { selected: selectedTemplate?.id === 'blank' }]"
            @click="selectedTemplate = { id: 'blank', name: '空白生成', template_type: 'blank' }"
          >
            <div class="blank-generate-icon">
              <el-icon><Document /></el-icon>
            </div>
            <div class="blank-generate-content">
              <div class="blank-generate-title">空白生成</div>
              <div class="blank-generate-desc">不使用任何模板，直接按默认样式生成PPT</div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <UiButton
            variant="outline"
            style="--btn-bg: #0f0f10; --btn-color: #ffffff; --btn-border: rgba(255, 255, 255, 0.88);"
            @click="showTemplateDialog = false"
          >
            取消
          </UiButton>
          <UiButton
            variant="default"
            style="--btn-bg: #ffffff; --btn-color: #111111; --btn-border: #ffffff;"
            :disabled="!selectedTemplate"
            @click="confirmGenerateWithTemplate"
          >
            使用选中模板
          </UiButton>
        </div>
      </template>
    </el-dialog>

    <!-- 大纲显示对话框 -->
    <el-dialog
      v-model="showOutlineDialog"
      title="生成PPT大纲"
      width="700px"
      :close-on-click-modal="false"
      :show-close="false"
      class="outline-dialog"
    >
      <div class="outline-container">
        <div class="interfaces-progress">
          <div class="interfaces-progress-indicator" :style="{ transform: `translateX(-${100 - Math.max(0, Math.min(100, outlineProgressDisplay || 0))}%)` }"></div>
        </div>
        <div class="progress-headline">
          <span class="progress-percent">{{ Math.round(outlineProgressDisplay || 0) }}%</span>
          <span class="progress-text">{{ outlineStageText }}</span>
        </div>

        <!-- 任务条（大纲） -->
        <div class="plan-card">
          <div class="plan-title">大纲任务</div>
          <ul class="plan-list">
            <li v-for="task in outlinePlanTasks" :key="task.id" :class="['plan-item', `status-${task.status}`]">
              <span class="plan-icon">
                <CheckCircle2 v-if="task.status === 'completed'" :size="15" />
                <CircleDotDashed v-else-if="task.status === 'in-progress'" :size="15" class="spin" />
                <Circle v-else :size="15" />
              </span>
              <div class="plan-content">
                <div class="plan-item-title">{{ task.title }}</div>
                <div class="plan-item-desc">{{ task.description }}</div>
              </div>
              <span class="plan-badge">{{ task.statusLabel }}</span>
            </li>
          </ul>
        </div>

        <div class="progress-log-box" v-if="outlineLogLines.length > 0">
          <div class="plan-title">过程日志</div>
          <div class="progress-log-list">
            <div v-for="(line, idx) in outlineLogLines" :key="`outline-log-${idx}`" class="progress-log-item">
              <span class="log-progress">·</span>
              <span class="log-message">{{ line }}</span>
            </div>
          </div>
        </div>

        <div class="outline-text">{{ outlineText }}</div>
      </div>
    </el-dialog>

    <!-- 重命名对话框 -->
    <UiPromptDialog
      :open="showRenameDialog"
      title="重命名对话"
      message="请输入新的对话名称"
      :input-value="renameDialogInput"
      input-placeholder="对话名称"
      confirm-text="确定"
      cancel-text="取消"
      @confirm="onRenameConfirm"
      @cancel="onRenameCancel"
    />

    <!-- 删除确认对话框 -->
    <UiConfirmDialog
      :open="showDeleteDialog"
      title="删除对话"
      :message="deleteDialogMessage"
      confirm-text="删除"
      cancel-text="取消"
      @confirm="onDeleteConfirm"
      @cancel="onDeleteCancel"
    />

    <!-- 分享对话框 -->
    <ShareDialog
      :open="showShareDialog"
      :conversation-id="shareDialogTarget?.id"
      :conversation-title="shareDialogTarget?.title"
      @close="handleShareDialogClose"
      @saved="handleShareSaved"
    />

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useConversationStore } from '@/store/modules/conversation'
import { useAuthStore } from '@/store/modules/auth'
import { User, ChatDotRound, Document, Paperclip, Plus, Edit, Delete, View, Loading, Share } from '@element-plus/icons-vue'
import { CheckCircle2, Circle, CircleDotDashed, ExternalLink, FileText, Globe, GraduationCap, Loader2, PlayCircle, Send, Share2, Users, X, Code, BookOpen, Eye, Download, Music, Image, Video, FolderOpen, BarChart3, Mic, MicOff } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import websocketService from '@/services/websocket'
import api from '@/services/api'
import templateService from '@/services/template'
import MindMap from '@/components/MindMap.vue'
import MessageContent from '@/components/chat/MessageContent.vue'
import UiButton from '@/components/ui/shadcn/Button.vue'
import UiTag from '@/components/ui/shadcn/Tag.vue'
import UiConfirmDialog from '@/components/ui/shadcn/ConfirmDialog.vue'
import UiPromptDialog from '@/components/ui/shadcn/PromptDialog.vue'
import ShareDialog from '@/components/ui/shadcn/ShareDialog.vue'
import aiAvatar from '@/assets/images/20b18263-07f8-44e6-b375-0fbb4530a9b3.png'

const router = useRouter()
const route = useRoute()
const conversationStore = useConversationStore()
const authStore = useAuthStore()

const getBackendOrigin = () => {
  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'
  return apiBase.replace(/\/api\/?$/, '')
}

// ── 协作模式 ──
const isCollabMode = computed(() => route.query.collab === 'true')
const collabName = computed(() => route.query.collab_name || '')
const collabAvatarUrl = computed(() => {
  const url = route.query.collab_avatar || ''
  if (!url) return ''
  if (url.startsWith('/')) return `${getBackendOrigin()}${url}`
  return url
})
const collabOwnerId = computed(() => route.query.collab_owner_id || '')

// 计算用户头像URL
const userAvatarUrl = computed(() => {
  const avatarUrl = authStore.currentUser?.avatar_url
  if (avatarUrl) {
    // 如果是相对路径,添加后端URL
    if (avatarUrl.startsWith('/')) {
      return `${getBackendOrigin()}${avatarUrl}`
    }
    return avatarUrl
  }
  // 默认头像
  return 'https://github.com/shadcn.png'
})

const userInput = ref('')
const isSending = ref(false)
const isTyping = ref(false)
const isGeneratingPPT = computed(() => conversationStore.isGeneratingPPT)
const isGeneratingOutline = computed(() => conversationStore.isGeneratingOutline)
const pptProgress = computed(() => conversationStore.pptProgress)
const outlineProgress = computed(() => conversationStore.outlineProgress)
const pptProgressMessage = computed(() => conversationStore.pptProgressMessage)
const generatingSlides = computed(() => conversationStore.generatingSlides)
const outlineProgressText = computed(() => conversationStore.outlineProgressMessage || '准备生成...')
const messagesContainer = ref(null)
const uploadedFiles = ref([])
const webSearchEnabled = ref(false)

// ── 语音输入 ──
const isVoiceRecording = ref(false)
const speechSupported = ref(false)
let recognition = null

onMounted(() => {
  // 检查浏览器是否支持语音识别
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (SpeechRecognition) {
    speechSupported.value = true
    recognition = new SpeechRecognition()
    recognition.lang = 'zh-CN'
    recognition.interimResults = true
    recognition.continuous = true

    recognition.onresult = (event) => {
      let finalText = ''
      let interimText = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          finalText += transcript
        } else {
          interimText += transcript
        }
      }
      if (finalText) {
        userInput.value += finalText
      }
      // 临时显示中间结果（不写入input，仅视觉反馈）
      if (interimText && !finalText) {
        voiceInterimText.value = interimText
      } else {
        voiceInterimText.value = ''
      }
    }

    recognition.onerror = (event) => {
      console.warn('语音识别错误:', event.error)
      if (event.error === 'not-allowed') {
        ElMessage.warning('请允许麦克风权限以使用语音输入')
        isVoiceRecording.value = false
        voiceInterimText.value = ''
      } else if (event.error === 'aborted') {
        // 用户主动停止，不处理
      } else {
        // network / no-speech / audio-capture 等错误，尝试重启
        if (isVoiceRecording.value) {
          setTimeout(() => {
            if (isVoiceRecording.value) {
              try { recognition.start() } catch (e) {}
            }
          }, 200)
        }
      }
    }

    recognition.onend = () => {
      // 如果仍在录音状态，延迟后自动重启（浏览器静音超时会自动停止）
      if (isVoiceRecording.value) {
        setTimeout(() => {
          if (isVoiceRecording.value) {
            try { recognition.start() } catch (e) {
              // start失败说明已在运行，忽略
            }
          }
        }, 100)
      } else {
        voiceInterimText.value = ''
      }
    }
  }
})

const voiceInterimText = ref('')

const toggleVoiceInput = () => {
  if (!recognition) return
  if (isVoiceRecording.value) {
    isVoiceRecording.value = false
    voiceInterimText.value = ''
    recognition.stop()
  } else {
    isVoiceRecording.value = true
    voiceInterimText.value = ''
    try {
      recognition.start()
    } catch (e) {
      ElMessage.warning('语音识别启动失败，请重试')
      isVoiceRecording.value = false
    }
  }
}
const isSearchCounting = ref(false)
const showSearchPanel = ref(false)
const searchPanelResults = ref([])

// ── 文件阅读状态 ──
const fileReadingState = reactive({
  active: false,
  fileName: '',
  fileType: '',
  progress: 0,
  step: '',
  steps: [],
  done: false,
  result: '',
  fileResults: [],  // 每个文件的理解结果摘要
})

// ── 视频理解模拟状态 ──
const videoUnderstandingState = reactive({
  active: false,
  fileName: '',
  currentText: '',
  currentIndex: -1,
  progress: 0,
  done: false,
})

const VIDEO_UNDERSTANDING_STEPS = [
  '正在建立视频流缓冲区与多路复用解包...',
  '分离轨道中：正在剥离主视频流与高频音频流...',
  '镜头分割中：正在通过帧间差分检测场景切换与转场...',
  '视觉抽取中：正在按时间轴进行高密度关键帧采样...',
  '听觉解析中：正在执行 ASR 语音到文本的高精度转写...',
  '声纹分离中：正在识别不同发声源并生成说话者日志（Diarization）...',
  '动作捕捉中：正在分析画面主体的动态行为与微表情...',
  '多模态对齐：正在将视觉帧、台词与环境音的时间戳进行毫秒级锚定...',
  '逻辑合成中：正在提取高光时刻并生成视频章节大纲...',
  '时空特征索引构建完毕，随时可针对特定画面或时间点进行追问。',
]

// 每步停留时长(ms)，模拟真实流程节奏（总约60秒）
const VIDEO_STEP_DURATIONS = [
  3200, 3800, 4200, 4800, 5200, 4800, 4200, 5800, 5200, 4800,
]

let videoUnderstandingTimer = null

const startVideoUnderstanding = async (fileName) => {
  videoUnderstandingState.active = true
  videoUnderstandingState.fileName = fileName
  videoUnderstandingState.currentText = ''
  videoUnderstandingState.currentIndex = -1
  videoUnderstandingState.progress = 0
  videoUnderstandingState.done = false

  const totalSteps = VIDEO_UNDERSTANDING_STEPS.length
  const totalDuration = VIDEO_STEP_DURATIONS.reduce((a, b) => a + b, 0)
  let elapsed = 0

  for (let i = 0; i < totalSteps; i++) {
    if (!videoUnderstandingState.active) break

    videoUnderstandingState.currentIndex = i
    videoUnderstandingState.currentText = VIDEO_UNDERSTANDING_STEPS[i]

    // 淡入效果
    await new Promise(r => setTimeout(r, 350))

    // 停留
    const stay = VIDEO_STEP_DURATIONS[i] - 350 - 300
    await new Promise(r => setTimeout(r, Math.max(0, stay)))

    elapsed += VIDEO_STEP_DURATIONS[i]
    videoUnderstandingState.progress = Math.min(99, Math.round((elapsed / totalDuration) * 100))

    // 淡出效果
    await new Promise(r => setTimeout(r, 300))
  }

  if (videoUnderstandingState.active) {
    videoUnderstandingState.progress = 100
    videoUnderstandingState.currentText = '视频理解完成。'
    videoUnderstandingState.currentIndex = totalSteps - 1
    videoUnderstandingState.done = true
    await new Promise(r => setTimeout(r, 1200))
    videoUnderstandingState.active = false
  }
}

const stopVideoUnderstanding = () => {
  videoUnderstandingState.active = false
}

const getFileExtension = (name) => {
  if (!name || !name.includes('.')) return ''
  const parts = name.split('.')
  return parts[parts.length - 1].toLowerCase()
}

const getFileCategory = (name) => {
  const ext = getFileExtension(name)
  if (['pdf'].includes(ext)) return 'pdf'
  if (['doc', 'docx'].includes(ext)) return 'word'
  if (['ppt', 'pptx'].includes(ext)) return 'ppt'
  if (['xls', 'xlsx'].includes(ext)) return 'excel'
  if (['txt', 'md'].includes(ext)) return 'text'
  if (['jpg', 'jpeg', 'png', 'gif'].includes(ext)) return 'image'
  if (['mp4', 'avi', 'mov'].includes(ext)) return 'video'
  if (['mp3', 'wav', 'm4a', 'ogg', 'flac', 'aac'].includes(ext)) return 'audio'
  return 'other'
}

const getFileIcon = (name) => {
  const cat = getFileCategory(name)
  const iconMap = {
    pdf: BookOpen,
    word: FileText,
    ppt: FolderOpen,
    excel: BarChart3,
    text: FileText,
    image: Image,
    video: Video,
    audio: Music,
    other: FileText,
  }
  return iconMap[cat] || FileText
}

const getFileTagClass = (name) => {
  return `file-type-${getFileCategory(name)}`
}

const getMessageAttachments = (content) => {
  if (!content) return []
  const matches = content.match(/\[附件:\s*([^\]]+)\]/)
  if (!matches) return []
  return matches[1].split(',').map(s => s.trim()).filter(Boolean)
}

const getMessageText = (content) => {
  if (!content) return ''
  return content.replace(/\n*\[附件:\s*[^\]]+\]\n*/g, '').trim()
}

const openSearchPanel = (results) => {
  searchPanelResults.value = results
  showSearchPanel.value = true
}

const categoryIconMap = {
  webpage: Globe,
  video: PlayCircle,
  doc: FileText,
  academic: GraduationCap,
  code: Code,
  community: Users
}

const searchPanelGroups = computed(() => {
  const groups = {}
  searchPanelResults.value.forEach(item => {
    const key = item.category || 'webpage'
    if (!groups[key]) {
      groups[key] = { key, label: item.categoryLabel || '网页', items: [], iconComponent: categoryIconMap[key] || Globe }
    }
    groups[key].items.push(item)
  })
  return Object.values(groups)
})
const chatUploadInput = ref(null)

const handleChatFileInput = (event) => {
  const files = event.target.files
  if (!files || files.length === 0) return
  for (const file of files) {
    handleFileChange({ name: file.name, size: file.size, raw: file })
  }
  event.target.value = ''
}

const uploadRef = ref(null)
let responseWatchdog = null

const templates = ref([])
const builtinTemplates = ref([])  // 内置模板（从/api/templates/builtin获取)
const categories = ref({})
const showTemplateDialog = ref(false)

// 重命名 / 删除对话框状态
const showRenameDialog = ref(false)
const renameDialogTarget = ref(null)
const renameDialogInput = ref('')
const showDeleteDialog = ref(false)
const deleteDialogTarget = ref(null)
const deleteDialogMessage = ref('')
const showShareDialog = ref(false)
const shareDialogTarget = ref(null)
const selectedTemplate = ref(null)
const loadingTemplates = ref(false)
const templateTab = ref('builtin')
const showOutlineDialog = ref(false)  // 大纲显示对话框
const outlineText = ref('')  // 大纲文本内容
const isGeneratingOutlineLocal = ref(false)  // 是否正在生成大纲
const outlineProgressLocal = ref(0)  // 大纲生成进度 (0-100)
const outlineStageLocal = ref('preparing')
const outlineVisualProgress = ref(0)
const pptVisualProgress = ref(0)
let outlineVisualTimer = null
let pptVisualTimer = null
let outlineVisualStartedAt = 0
let pptVisualStartedAt = 0

// 仅用于“步骤条按规定时长依次推进”的可视化节奏
const OUTLINE_PLAN_TOTAL_MS = 75 * 1000 // 15 + 40 + 10 + 10
const PPT_PLAN_TOTAL_MS = 115 * 1000 // 15 + 50 + 15 + 30 + 5

const startOutlineVisualTimer = () => {
  if (outlineVisualTimer) clearInterval(outlineVisualTimer)
  outlineVisualStartedAt = Date.now()
  outlineVisualProgress.value = 0
  outlineVisualTimer = setInterval(() => {
    const elapsed = Date.now() - outlineVisualStartedAt
    const planned = Math.min(99, (elapsed / OUTLINE_PLAN_TOTAL_MS) * 100)
    outlineVisualProgress.value = Math.max(outlineVisualProgress.value, planned)
  }, 250)
}

const stopOutlineVisualTimer = (finalProgress = null) => {
  if (outlineVisualTimer) {
    clearInterval(outlineVisualTimer)
    outlineVisualTimer = null
  }
  if (typeof finalProgress === 'number') {
    outlineVisualProgress.value = finalProgress
  }
}

const startPPTVisualTimer = () => {
  if (pptVisualTimer) clearInterval(pptVisualTimer)
  pptVisualStartedAt = Date.now()
  pptVisualProgress.value = 0
  pptVisualTimer = setInterval(() => {
    const elapsed = Date.now() - pptVisualStartedAt
    const planned = Math.min(99, (elapsed / PPT_PLAN_TOTAL_MS) * 100)
    pptVisualProgress.value = Math.max(pptVisualProgress.value, planned)
  }, 250)
}

const waitForPlannedDuration = async (startedAt, totalMs) => {
  const elapsed = Math.max(0, Date.now() - (startedAt || 0))
  const remain = Math.max(0, totalMs - elapsed)
  if (remain > 0) {
    await new Promise(resolve => setTimeout(resolve, remain))
  }
}

const stopPPTVisualTimer = (finalProgress = null) => {
  if (pptVisualTimer) {
    clearInterval(pptVisualTimer)
    pptVisualTimer = null
  }
  if (typeof finalProgress === 'number') {
    pptVisualProgress.value = finalProgress
  }
}

const outlineProgressDisplay = computed(() => {
  if (isGeneratingOutlineLocal.value) return Math.max(0, Math.min(99, outlineVisualProgress.value || 0))
  return Math.max(0, Math.min(100, Number(outlineProgressLocal.value || 0)))
})

const pptProgressDisplay = computed(() => {
  if (isGeneratingPPT.value) return Math.max(0, Math.min(99, pptVisualProgress.value || 0))
  return Math.max(0, Math.min(100, Number(pptProgress.value || 0)))
})

// 用户上传模板计算属性
const customTemplates = computed(() => {
  return templates.value.filter(t => ['uploaded', 'analyzed'].includes(t.template_type))
})

const conversationId = computed(() => route.params.id || conversationStore.currentConversation?.id)
const messages = computed(() => conversationStore.messages)
const conversations = computed(() => conversationStore.conversations)
const conversationTitle = computed(() => conversationStore.currentConversation?.title || 'AI对话')
const conversationState = computed(() => conversationStore.currentConversation?.state)
const currentOutline = computed(() => conversationStore.currentOutline)
const currentPPT = computed(() => conversationStore.currentPPT)
const isGenerating = computed(() => conversationStore.isGenerating)

const isWaitingForResponse = computed(() => {
  if (!isTyping.value) return false
  const msgs = messages.value
  if (msgs.length === 0) return true
  const last = msgs[msgs.length - 1]
  return last.role !== 'assistant' || !last.isStreaming
})

const steps = [
  { id: '0', title: '初始化', description: '准备开始对话' },
  { id: '1', title: '对话中', description: '与AI交流需求' },
  { id: '2', title: '生成大纲', description: '正在生成PPT大纲' },
  { id: '3', title: '生成PPT', description: '正在生成PPT' },
  { id: '4', title: 'PPT已就绪', description: 'PPT生成完成' },
  { id: '5', title: '已完成', description: '所有任务完成' }
]

const stepIndex = computed(() => {
  const stateMap = {
    'INITIAL': 0,
    'CHAT': 1,
    'GENERATING_OUTLINE': 2,
    'GENERATING_PPT': 3,
    'PPT_READY': 4,
    'COMPLETED': 5
  }
  return stateMap[conversationState.value] || 0
})

const handleStepClick = (index) => {
  // Step click is visual only - steps are driven by conversation state
}

const canGenerateOutline = computed(() => {
  return conversationState.value === 'CHAT'
})

// 进行 3 轮以上有效对话后，才展示右上角“生成大纲/生成PPT”按钮
// 这里按“用户主动发送消息次数”统计对话轮次，过滤空消息
const userMessageTurns = computed(() => {
  return messages.value.filter(msg => msg.role === 'user' && (msg.content || '').trim().length > 0).length
})

const showGenerateActions = computed(() => {
  return userMessageTurns.value >= 3
})

const canGeneratePPT = computed(() => {
  return messages.value.some(msg =>
    msg.role === 'assistant' && msg.meta_data?.outline
  )
})

const outlineStageText = computed(() => {
  const stageMap = {
    preparing: '正在准备生成大纲',
    building_prompt: '正在构建提示词',
    calling_llm: '正在调用AI生成大纲',
    receiving: '正在接收AI响应',
    parsing: '正在解析大纲内容',
    done: '大纲生成完成',
    error: '大纲生成失败'
  }
  return stageMap[outlineStageLocal.value] || '正在生成大纲'
})

const outlinePlanTasks = computed(() => {
  const p = Number(outlineProgressDisplay.value || 0)
  const getStatusByProgress = (start, end) => {
    if (p >= end) return 'completed'
    if (p >= start) return 'in-progress'
    return 'pending'
  }

  return [
    { id: 'o1', title: '分析对话需求', description: '提取主题、受众、目标与约束条件', status: getStatusByProgress(0, 20) },
    { id: 'o2', title: '生成结构化大纲', description: '调用模型组织章节结构与页面要点', status: getStatusByProgress(20, 73) },
    { id: 'o3', title: '解析与校验内容', description: '校验结构并补全可展示内容', status: getStatusByProgress(73, 87) },
    { id: 'o4', title: '输出大纲结果', description: '整理最终结果并准备进入PPT生成', status: getStatusByProgress(87, 100) }
  ].map(task => ({
    ...task,
    statusLabel: task.status === 'completed' ? '已完成' : (task.status === 'in-progress' ? '进行中' : '待处理')
  }))
})

const outlineLogLines = computed(() => {
  const p = Number(outlineProgressDisplay.value || 0)
  const logs = [
    '读取对话上下文与用户需求',
    '识别主题、受众、教学目标与风格',
    '构建大纲生成提示词',
    '调用模型生成章节结构',
    '补全每页核心要点',
    '校验大纲格式与页码顺序',
    '整理输出并准备进入PPT生成'
  ]
  const visibleCount = Math.max(1, Math.min(logs.length, Math.ceil((p / 100) * logs.length)))
  return logs.slice(0, visibleCount)
})

const pptPlanTasks = computed(() => {
  const p = Number(pptProgressDisplay.value || 0)
  const getStatus = (start, end) => {
    if (p >= end) return 'completed'
    if (p >= start) return 'in-progress'
    return 'pending'
  }

  return [
    { id: 'p1', title: '分析对话与资料', description: '聚合上下文并提炼页面目标', status: getStatus(0, 13) },
    { id: 'p2', title: '生成章节与内容', description: '确定章节结构与页级内容分布', status: getStatus(13, 57) },
    { id: 'p3', title: '匹配模板与版式', description: '选择模板并映射页面布局', status: getStatus(57, 70) },
    { id: 'p4', title: '生成页面元素', description: '填充文本、配图与可视化要素', status: getStatus(70, 96) },
    { id: 'p5', title: '保存与发布结果', description: '写入文件并回传可预览结果', status: getStatus(96, 100) }
  ].map(task => ({
    ...task,
    statusLabel: task.status === 'completed' ? '已完成' : (task.status === 'in-progress' ? '进行中' : '待处理')
  }))
})

const pptRecentLogs = computed(() => {
  const p = Number(pptProgressDisplay.value || 0)
  const logs = [
    { progress: 13, message: '分析对话与资料' },
    { progress: 30, message: '提取章节结构与页面范围' },
    { progress: 57, message: '生成章节与内容' },
    { progress: 70, message: '匹配模板与版式' },
    { progress: 85, message: '生成页面标题与正文内容' },
    { progress: 96, message: '生成页面元素并执行排版检查' },
    { progress: 99, message: '保存与发布结果' },
    { progress: 100, message: '生成完成，准备返回结果' }
  ]
  return logs.filter(item => item.progress <= Math.max(1, p)).slice(-8).reverse()
})

const stateText = computed(() => {
  const stateMap = {
    'INITIAL': '初始化',
    'CHAT': '对话中',
    'GENERATING_OUTLINE': '生成大纲',
    'OUTLINE_GENERATED': '大纲已生成',
    'GENERATING_PPT': '生成PPT',
    'PPT_READY': 'PPT已就绪',
    'COMPLETED': '已完成'
  }
  return stateMap[conversationState.value] || conversationState.value
})

onMounted(async () => {
  if (!authStore.user) {
    // 尝试获取用户信息
    try {
      await authStore.fetchCurrentUser()
    } catch (error) {
      ElMessage.error('请先登录')
      router.push('/login')
      return
    }
  }

  await conversationStore.fetchConversations()
  await websocketService.connect()

  // 检查是否从 dashboard 传递了消息
  const pendingMessage = sessionStorage.getItem('dashboardMessage')
  
  if (pendingMessage) {
    // 有待发送的消息，创建新对话
    const conversation = await conversationStore.createConversation('新对话')

    // 跳转到新对话（等待路由导航完成）
    await router.replace(`/chat/${conversation.id}`)
    await nextTick()

    // 加载新对话数据到 store
    await conversationStore.fetchConversation(conversation.id)

    // 加入 WebSocket
    await websocketService.connect()
    websocketService.joinConversation(conversation.id, authStore.user.id)
    await conversationStore.fetchConversations()

    // 读取消息和文件
    const message = pendingMessage
    const filesStr = sessionStorage.getItem('dashboardFiles')
    const files = filesStr ? JSON.parse(filesStr) : []

    // 清理 sessionStorage
    sessionStorage.removeItem('dashboardMessage')
    sessionStorage.removeItem('dashboardFiles')

    // 设置消息内容
    userInput.value = message

    // 如果有文件，显示提示
    if (files.length > 0) {
      ElMessage.info(`检测到 ${files.length} 个文件引用，请重新上传文件`)
    }

    // 延迟自动发送，确保 conversationId 已正确更新
    setTimeout(() => {
      handleSend()
    }, 500)

  } else {
    // 常规逻辑
    if (conversationId.value) {
      await conversationStore.fetchConversation(conversationId.value)
      websocketService.joinConversation(conversationId.value, authStore.user.id)
    } else if (conversations.value.length > 0) {
      const latestConv = conversations.value[0]
      router.push(`/chat/${latestConv.id}`)
    } else {
      await handleNewConversation()
    }
  }

  websocketService.on('streaming_start', handleStreamingStart)
  websocketService.on('typing', handleTyping)
  websocketService.on('error', handleError)
  websocketService.on('outline_generation_start', handleOutlineGenerationStart)
  websocketService.on('outline_generation_progress', handleOutlineProgress)
  websocketService.on('ppt_generation_progress', handlePPTProgress)
  websocketService.on('ppt_generation_start', handlePPTGenerationStart)
  websocketService.on('ppt_generated', handlePPTGenerated)
})

onUnmounted(() => {
  stopOutlineVisualTimer()
  stopPPTVisualTimer()
  clearResponseWatchdog()
  websocketService.off('streaming_start', handleStreamingStart)
  websocketService.off('typing', handleTyping)
  websocketService.off('error', handleError)
  websocketService.off('outline_generation_start', handleOutlineGenerationStart)
  websocketService.off('outline_generation_progress', handleOutlineProgress)
  websocketService.off('ppt_generation_progress', handlePPTProgress)
  websocketService.off('ppt_generation_start', handlePPTGenerationStart)
  websocketService.off('ppt_generated', handlePPTGenerated)
})

watch(messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

watch(() => conversationStore.isGenerating, (newVal) => {
  if (conversationId.value === conversationStore.currentConversation?.id) {
    isTyping.value = newVal
    if (!newVal) {
      clearResponseWatchdog()
    }
  }
})

watch(conversationId, () => {
  isTyping.value = false
})

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 模拟联网搜索
const simulateWebSearch = async (userMessage) => {
  // 用户提供的 DeepSeek 联网搜索真实数据
  const allResults = [
    { domain: 'chinaooc.com.cn', siteName: '国家高等教育智慧教育平台', date: '2026/04/03', title: '课程 - 国家高等教育智慧教育平台', url: 'https://www.chinaooc.com.cn/course/6982623295df98bb27cad403', snippet: '《MySQL数据库案例教程》是计算机相关专业的一门专业基础和技能课程，培养学生数据库应用能力，同时满足社会对计算机专业人才的需求，适合从事计算机程序设计、大数据分析、云计算等相关岗位。学生通过学习该课程掌握数据库创建...' },
    { domain: 'pluralsight.com', siteName: 'Pluralsight', date: '2026/01/13', title: 'Filter and Organize Enrollment Records with SQL in PostgreSQL', url: 'https://www.pluralsight.com/labs/codeLabs/filter-and-organize-enrollment-records-with-sql-in-postgresql', snippet: "In this Code Lab, you'll practice writing SQL queries in PostgreSQL to retrieve and organize student enrollment records. You'll use SELECT, WHERE, AND, OR, and NOT to filter data, apply pattern matching with LIKE and ILIKE, handle NULL values, and structure output using ORDER BY, LIMIT, and OFFSET." },
    { domain: 'alibabacloud.com', siteName: 'Alibaba Cloud', date: '2026/03/28', title: 'Design table schemas and create tables - Alibaba Cloud', url: 'https://www.alibabacloud.com/help/en/rds/apsaradb-rds-for-postgresql/introduction-to-table-design-based-on-apsaradb-rds-for-postgesql', snippet: 'This tutorial walks through a realistic example — a university course selection system — to show how to design a normalized schema, create tables with proper constraints, and query across related tables using ApsaraDB RDS for PostgreSQL.' },
    { domain: 'csdn.net', siteName: 'CSDN博客', date: '2026/03/23', title: '数据库 SQL结构化查询语言', url: 'https://blog.csdn.net/2401_87379892/article/details/157337449', snippet: '一、目的与要求 - 掌握SQL语言的查询功能； - 掌握SQL语言的数据操作功能； - 掌握附加数据库的操作。 二、实验准备 - 了解SQL语言的查改增删四大操作的语法...' },
    { domain: 'csdn.net', siteName: 'CSDN博客', date: '2026/04/12', title: '选课系统数据库实现（SQL）', url: 'https://blog.csdn.net/2501_91994684/article/details/160057072', snippet: '选课情况查询：学生可以查询自己的选课列表，包括课程名称、授课教师、上课时间、上课地点、学分等信息；教师可以查询自己所授课程的选课学生名单；管理员可以查询所有课程的选课情况。' },
    { domain: 'cowley.edu', siteName: 'Cowley College', date: '2026/04/06', title: 'CIS1902 INTRODUCTION TO SQL COURSE PROCEDURE', url: 'https://catalog.cowley.edu/content.php?catoid=14&navoid=10366', snippet: 'This course to give students an introduction to working with SQL including selection, updating, deleting, inserting, and implementing various database management techniques. ... This course is designed to help students learn the fundamentals of SQL.' },
    { domain: 'classcentral.com', siteName: 'Class Central', date: '2026/01/12', title: 'Free Course: 数据库概论实验 from XuetangX | Class Central', url: 'https://www.classcentral.com/course/xuetangx-367569', snippet: '通过本课程的学习，您将学会如何基于SQL Server的SQL Server Management Studio和sqlcmd两种方式完成从基础到高级的所有数据库技术实践练习，为快速上手其它关系数据库的使用和进一步的数据库应用系统开发打下坚实的基础。' },
    { domain: 'kongfz.com', siteName: '孔夫子旧书网', date: '2026/04/12', title: 'SQL Server 2016数据库案例教程 第2版', url: 'https://book.kongfz.com/878042/9906871635/', snippet: '全书以"学生选课系统"的数据库设计与管理为主线，详细介绍了SQL Server 2016中实现该系统数据库的应用与维护，主要内容包括数据库建模、数据库对象创建、数据查询、查询优化、面向数据库编程、模块化编程、数据库的高可靠性和安全性等。' },
    { domain: 'gitcode.com', siteName: 'GitCode', date: '2026/01/26', title: '【亲测免费】SqlServer数据库课程设计-学生选课系统', url: 'https://blog.gitcode.com/e10e0c2d13b132a4a99ffc38bf978192.html', snippet: '本资源是针对《数据库原理》或相关课程设计的一份实践作品，利用Microsoft Sql Server作为后台数据库管理系统，实现了学生选课系统的完整设计与开发。该项目旨在通过实际操作 ... SQL语言、存储过程、触发器等核心概念的理解和应用。' },
    { domain: 'ohio.catalog.acalog.com', siteName: 'Modern Campus', date: '2026/03/25', title: 'ETM 3310 - Database Applications & Analytics', url: 'https://ohio.catalog.acalog.com/preview_course_nopop.php?catoid=104&coid=587977', snippet: 'Teaches students relational database fundamentals, SQL programming skills, and simple database analytics. Includes principles of database design techniques and implementations. Upon completion ... Students will be able to manipulate a database using SQL to retrieve, store, modify, delete, insert and update data.' },
    { domain: 'postgresql.ac.cn', siteName: 'postgresql.ac.cn', date: '2025/09/25', title: 'PostgreSQL: 文档: 18: 2.5. 查询表', url: 'https://postgresql.ac.cn/docs/current/tutorial-select.html', snippet: '要从表中检索数据，就需要对该表进行查询。使用SQL SELECT 语句来完成此操作。该语句分为一个选择列表（列出要返回的列）、一个表列表（列出要从中检索数据的表）和一个可选的限定条件（指定任何限制条件）。' },
    { domain: 'oreilly.com', siteName: "O'Reilly Media", date: '2025/05/30', title: '《SQL 烹饪书》第二版', url: 'https://www.oreilly.com/library/view/sql-peng-ren-shu-di-er-ban/9798341658813/ch01.html', snippet: '本章主要介绍基本的 SELECT 语句。扎实掌握基础知识非常重要，因为这里涉及的许多主题不仅存在于更难的口诀中，而且在日常 SQL 中也能找到 ... 在交互式执行的特别查询中，使用 SELECT * 更简单。不过，在编写程序代码时...' },
    { domain: 'postgresql.org', siteName: 'PostgreSQL', date: '2025/11/13', title: '2.5. Querying a Table', url: 'https://www.postgresql.org/docs/14/tutorial-select.html', snippet: 'To retrieve data from a table, the table is queried. An SQL SELECT statement is used to do this. The statement is divided into a select list, a table list, and an optional qualification.' },
    { domain: 'mygreatlearning.com', siteName: 'Great Learning', date: '2025/05/14', title: '27 SQL Query Examples to Practice Data Analysis', url: 'https://www.mygreatlearning.com/blog/sql-queries-with-examples/', snippet: 'This guide provides 27 practical SQL query examples to help you master data analysis. We will start from basic data retrieval with SELECT to advanced analytical techniques using window functions and CTEs.' },
    { domain: 'yugabyte.com', siteName: 'YugabyteDB Docs', date: '2025/09/19', title: 'Queries and joins', url: 'https://docs.yugabyte.com/v2.20/explore/ysql-language-features/queries/', snippet: 'The main purpose of SELECT statements is to retrieve data from specified tables. Typically, the first part of every SELECT statement defines columns that contain the required data, the second part points to the tables hosting these columns.' },
    { domain: 'yugabyte.com', siteName: 'YugabyteDB Docs', date: '2025/10/30', title: 'Reading data', url: 'https://docs.yugabyte.com/v2.25/explore/ysql-language-features/queries/#all-data', snippet: 'The following guide shows how to query data from a database, starting with basic retrieval techniques and expanding into more advanced concepts like filtering ... The SELECT statement is used to retrieve data from tables.' },
    { domain: 'csdn.net', siteName: 'CSDN博客', date: '2025/09/17', title: '实践3 数据查询的基本操作（上）', url: 'https://blog.csdn.net/2501_93271845/article/details/151800190', snippet: '（1）掌握SELECT语句的格式和各子句的功能。（2）掌握WHERE子句中LIKE、BETWEEN…AND、IN、IS NULL等逻辑运算符的使用 ... 简单查询是基于单张表获取数据的基础操作，核心目标是精准筛选、提取所需信息。' },
    { domain: 'aliyun.com', siteName: 'aliyun.com', date: '2025/05/21', title: '表格存储如何使用SELECT语句查询数据', url: 'https://partners-intl.aliyun.com/help/zh/tablestore/query-data#concept-2098388', snippet: '如果在未创建数据表的映射关系的情况下，直接使用SQL语句（例如DESCRIBE、SELECT等）查询数据，系统后台将自动创建该数据表的映射关系。自动创建的映射表仅包含数据表的主键列和预定义列，并且不支持更新属性列。' },
    { domain: '51cto.com', siteName: '51CTO学堂', date: '2025/07/04', title: 'SQL单表查询基础与实战解析', url: 'https://edu.51cto.com/article/note/34562.html', snippet: '本文将聚焦于SQL单表查询的基本语法与实际应用，帮助读者掌握查询语句的结构、操作符的使用、聚合函数的定义，以及实际查询案例的解析。' },
    { domain: 'highgo.com', siteName: '瀚高基础软件股份有限公司', date: '2025/12/22', title: '瀚高技术文档', url: 'https://www.highgo.com/document/v9/zh-cn/reference/referenceFour7.html', snippet: '从数据库中检索数据的过程或命令叫做查询。在SQL里SELECT命令用于指定查询。 SELECT命令的一般语法是 [WITH with_queries] SELECT select_list FROM table_expression' },
    { domain: 'cqup.com.cn', siteName: 'cqup.com.cn', date: '', title: 'SQL Server数据库设计与应用项目教程 - 本科生教材', url: 'http://admin2017.cqup.com.cn/index.php?m=content&c=index&a=show&catid=40&id=19264', snippet: '本书以SQL Server数据库为核心,系统讲解了数据库设计、开发与管理的全过程。内容涵盖数据库环境搭建、数据表创建和维护、数据查询优化、视图与索引管理、T-SQL编程、存储过程与触发器开发,以及数据库安全与备份恢复等。' },
    { domain: 'smartedu.cn', siteName: '国家智慧教育平台', date: '2026/04/05', title: '课程 - 国家高等教育智慧教育平台', url: 'https://higher.smartedu.cn/course/690528f55345b6821457685b', snippet: 'SQL Server是一个基于客户机/服务器体系结构的多线程、高性能的数据库管理系统，通过该软件的学习实践可以使您理解并掌握数据库的创建、维护与管理等基本技能。' },
    { domain: '163.com', siteName: '网易', date: '2026/03/26', title: 'freeCodeCamp西班牙语频道上线SQL课', url: 'https://www.163.com/dy/article/KP024VQU05561FZE.html', snippet: '完整知识点清单覆盖15个模块，从关系型数据库的层级结构到3表联查的实战演练。课程总时长控制在5小时左右，信息密度明显高于动辄20小时的"从入门到精通"类教程。' },
    { domain: 'csdn.net', siteName: 'csdn.net', date: '2026/01/08', title: '7张图让你快速了解SQL', url: 'https://houzi.blog.csdn.net/article/details/156737693', snippet: '1）了解数据库的基本概念 2）如何安装数据库？ 3）表的创建、删除和更新 4）数据的插入、删除和更新数据 ... 1）如何进行汇总分析？ 2）如何对数据分组？ 3）如何对分组结果指定条件？' },
    { domain: 'classcentral.com', siteName: 'Class Central', date: '2026/02/11', title: 'The Complete SQL Bootcamp (30 Hours): Go from Zero to Hero', url: 'https://www.classcentral.com/course/udemy-the-complete-sql-bootcamp-30-hours-go-from-zero-to-hero-458660', snippet: "The Only SQL Course with 200+ Visual Animations: Learn Fast, Practice Hard & Build Real-World Projects. You'll learn the basics: what SQL is, how databases work, and why SQL is essential for working with data." },
    { domain: 'kongfz.com', siteName: '孔夫子旧书网', date: '2026/04/11', title: '数据库原理与应用教程：SQLServer2012', url: 'https://book.kongfz.com/277893/9903172389', snippet: '本书全面讲述了数据库的基本原理和SQL Server 2012的应用，全书以理论够用、实用，实践一的原则，使读者能够快速、轻松地掌握SQL Server数据库技术与应用。' },
    { domain: 'udemy.com', siteName: 'Udemy', date: '2026/01/02', title: 'The Complete SQL Course - Learn by Doing - SQL Server', url: 'https://www.udemy.com/course/the-complete-sql-course-2021-learn-by-doing/', snippet: 'How to write accurate SQL queries against a database, Use SQL to perform data analysis, Learn to perform GROUP BY Statements, Learn how to join multiple tables - including complex joins. You will learn how to read and write complex queries.' },
    { domain: 'mimo.org', siteName: 'Mimo', date: '2025/10/31', title: 'The 9 Best SQL Courses to Learn Online in 2026', url: 'https://mimo.org/blog/best-sql-courses', snippet: "We've reviewed dozens of options to find the best SQL courses that can help you grow your career, build practical skills, and feel confident working with data. In Mimo's SQL course, you'll explore all the key elements for beginner and intermediate SQL skills." },
    { domain: 'mimo.org', siteName: 'Mimo', date: '2026/01/27', title: 'Free SQL Learning Resources for Beginners', url: 'https://mimo.org/blog/free-sql-courses-for-beginners', snippet: 'SQL runs behind countless apps and dashboards. This guide breaks down the best free SQL learning resources for beginners in 2026. SQL is a programming language used to talk to databases and it stands for structured query language.' },
    { domain: 'mogdb.io', siteName: 'MogDB', date: '', title: 'Query执行流程', url: 'http://docs.mogdb.io:9002/zh/mogdb/v3.1/1-query-execution-process', snippet: 'SQL引擎从接受SQL语句到执行SQL语句需要经历的步骤如图1和说明1所示。其中，红色字体部分为DBA可以介入实施调优的环节。' },
    { domain: 'tencent.cn', siteName: 'CSDN博客', date: '2022/07/11', title: '面试官：听说你sql写的挺溜的，你说一说查询sql的执行过程', url: 'https://cloud.tencent.cn/developer/article/2045599', snippet: 'Mysql的执行器根据优化器生成的执行计划执行，调用存储引擎的接口进行查询。服务器将查询的结果返回客户端。' },
    { domain: 'tencent.com.cn', siteName: 'Tencent', date: '2024/04/24', title: '图解 SQL 执行顺序，通俗易懂！', url: 'https://cloud.tencent.com.cn/developer/article/2411998', snippet: 'SQL执行顺序：先执行from,join来确定表之间的连接关系，得到初步的数据；where对数据进行普通的初步的筛选；group by 分组；各组分别执行having中的普通筛选或者聚合函数筛选。' },
    { domain: 'oracle.com', siteName: 'Oracle Help Center', date: '2026/02/09', title: '7.4 Visual Explain Plan', url: 'https://docs.oracle.com/cd/E17952_01/workbench-en/wb-performance-explain.html', snippet: 'To view a visual explain execution plan, execute your query from the SQL editor and then select Execution Plan within the query results tab. The execution plan defaults to Visual Explain.' },
    { domain: 'pingkai.cn', siteName: 'pingkai.cn', date: '2023/05/25', title: '8张图，5大组件！了解MySQL查询语句执行过程', url: 'https://pingkai.cn/article/post/4765.html', snippet: 'SQL执行流程：连接器主要负责身份认证和权限鉴别的工作。客户端需要通过连接器访问MySQL Server。' },
    { domain: 'tencent.cn', siteName: 'CSDN博客', date: '2023/12/01', title: '一张图看懂sql运行顺序', url: 'https://cloud.tencent.cn/developer/article/2366692', snippet: '只有理解了sql查询语句的运行顺序才能看懂sql。图片中的sql查询语句运行顺序：第1步，先运行蓝框里的内容 第2步...' },
    { domain: 'gitea.com', siteName: 'Gitea', date: '2024/05/14', title: 'lab2/docs/docs/lectures/lecture-4.md', url: 'https://gitea.com/XocoSkena/lab2/src/branch/main/docs/docs/lectures/lecture-4.md', snippet: '关系数据库管理系统查询处理可以分为4个阶段：查询分析、查询检查、查询优化和查询执行。查询分析：对用户提交的查询语句进行扫描、词法分析和语法分析，判断是否符合SQL语法规则。' },
    { domain: 'racent.com', siteName: '锐成', date: '', title: 'SQL知识：图解SQL查询处理的各个阶段', url: 'https://www.racent.com/blog/495', snippet: '今天，我们将图解SQL查询处理的各个阶段，便于大家理解SQL的执行过程。执行顺序：先用数字+关键字的方式标注一下每个关键字的处理步骤。' },
    { domain: 'adaptavist.com', siteName: 'adaptavist.com', date: '2026/02/09', title: '7.5 Tutorial: Using Explain to Improve Query Performance', url: 'https://oracle.hydrogen.sagittarius.connect.product.adaptavist.com/cd/E17952_01/workbench-en/wb-tutorial-visual-explain-dbt3.html', snippet: 'This tutorial describes how to use Explain reports to locate and fix problematic (slow) queries. It uses the DBT-3 database and begins with a simple query example.' },
    { domain: 'cnki.net', siteName: 'CNKI', date: '', title: '图解SQL查询命令-延安大学学报(自然科学版)', url: 'https://wap.cnki.net/touch/web/Journal/Article/YSZR200603005.html', snippet: '在讲授Visual FoxPro程序课时,辅助用图解的方式,分层次逐步地演绎SQL查询命令的执行过程,使得那些抽象费解的命令变得清晰而明了,让学生印象深刻,教学效果良好。' },
    { domain: 'unipus.cn', siteName: '中国高校外语慕课平台', date: '2025/08/26', title: '数据库原理 - 中国高校外语慕课平台（UMOOCs）', url: 'https://umoocs.unipus.cn/course/6694', snippet: '本课程系统的讲述了数据库的基本原理、设计与实现方法，主要介绍数据库系统绪论、关系运算理论、关系数据库标准语言SQL、规范化理论和数据库设计、数据库安全性与完整性、数据库备份与恢复、数据库并发控制等。' },
    { domain: 'freecodecamp.org', siteName: 'freeCodeCamp', date: '2025/10/09', title: 'Learn Databases and SQL from Harvard University', url: 'https://www.freecodecamp.org/news/learn-databases-and-sql-from-harvard-university', snippet: "Introducing CS50 SQL, Harvard University's focused video course dedicated to an introduction to databases using a language called SQL. This SQL-focused course offers a deeper dive into relational databases, covering essential topics such as how to create, read, update, and delete data (CRUD)." },
    { domain: 'datacamp.com', siteName: 'DataCamp', date: '2025/09/10', title: 'Introduction to SQL Course | DataCamp', url: 'https://www.datacamp.com/courses/introduction-to-sql', snippet: "In just two hours, you'll get to know the theory and the practice through bite-sized videos and interactive exercises where you can put your new-found skills to the test." },
    { domain: 'dbvis.com', siteName: 'DbVisualizer', date: '2025/08/27', title: 'Top Platforms for Learning SQL and Database Analytics', url: 'https://www.dbvis.com/thetable/top-platforms-for-learning-sql-and-database-analytics/', snippet: 'Discover the top SQL learning platforms that can transform your data skills in weeks, from free YouTube channels to interactive courses that match your learning style.' },
    { domain: 'xduph.com', siteName: '西安电子科技大学出版社', date: '', title: '数据库原理及MySQL应用（微课版）', url: 'https://www.xduph.com/pages/BookDetail.aspx?doi=c350e99b-4837-4791-a497-e4f7880f0b4e', snippet: '本书共分17章，内容包括：数据库技术的基本概念与方法、标准SQL语言、数据定义、数据查询、数据更新、索引、视图、触发器、存储过程、控制与安全管理、备份与恢复和开发实例等。' },
    { domain: 'phcorner.org', siteName: 'Pinoy Internet and Technology Forums', date: '2025/06/13', title: 'Udemy - SQL for Beginners Practical SQL + AI + Job Projects(2025)', url: 'https://phcorner.org/threads/udemy-sql-for-beginners-practical-sql-ai-job-projects-2025.2315325/', snippet: "Learn SQL from scratch using simple examples and real-world scenarios ... you're a student, fresher, or switching careers, this course is built to teach you SQL from absolute zero, using hands-on practice, MySQL, real-world mock projects." },
    { domain: 'datacamp.com', siteName: 'DataCamp', date: '2025/12/16', title: 'Data Manipulation in SQL Course | DataCamp', url: 'https://www.datacamp.com/courses/data-manipulation-in-sql', snippet: "You'll take the CASE ... categorical variables, aggregate data into a single column with multiple filtering conditions, and calculate counts and percentages. Short and Simple Subqueries, Correlated Queries, Nested Queries, and Common Table Expressions." },
    { domain: 'phcorner.org', siteName: 'Pinoy Internet and Technology Forums', date: '2025/06/10', title: 'Udemy - Master SQL with BigQuery using AI tools From Zero to Hero', url: 'https://phcorner.org/threads/udemy-master-sql-with-bigquery-using-ai-tools-from-zero-to-hero.2312540/', snippet: 'This comprehensive "Zero to Hero" course offers a truly unique and modern approach to learning SQL specifically within the powerful Google BigQuery environment. The absolute fundamentals of SQL, including SELECT, FROM, WHERE, GROUP BY, ORDER BY, JOIN operations.' },
    { domain: 'certcommunity.org', siteName: 'CertCommunity', date: '2025/04/17', title: '[OFFER] Udemy - SQL for Data Analysis Advanced SQL Querying Techniques', url: 'https://www.certcommunity.org/forum/topic/24102-offer-udemy-sql-for-data-analysis-advanced-sql-querying-techniques', snippet: 'From SQL Basics to Modern Analytics with Polars - Hands-On Data Skills for 2025. This course is designed to take you from the very basics of SQL to advanced techniques used in real-world data analysis.' },
    { domain: 'cliffsnotes.com', siteName: 'CliffsNotes', date: '2025/08/02', title: 'Week5TutorialICT200 (docx)', url: 'https://www.cliffsnotes.com/study-notes/28145530', snippet: 'Structured Query Language (SQL) - Part 1. Part A: Video Instructions for using SQL Server Management Studio (SSMS) on your computer.' },
    { domain: 'apify.com', siteName: 'Apify', date: '2025/12/06', title: 'Auto Insight AI · Apify', url: 'https://apify.com/eager_cornet/sql-explainer', snippet: "SQL Explainer & Visualizer (AI Powered) Turn any SQL query (or English question) into a visual data story. This Actor is your AI-powered SQL Professor and Analytics Assistant. It doesn't just run queries; it understands them, explains them..." },
    { domain: 'postgresql.org', siteName: 'PostgreSQL', date: '2025/01/06', title: 'SQLPage v0.32: build web apps in SQL, now with more style!', url: 'https://www.postgresql.org/about/news/sqlpage-v032-build-web-apps-in-sql-now-with-more-style-2989/', snippet: 'SQLPage v0.32 brings a lot of polish, and some advanced features. SQLPage is an open-source tool that turns renders SQL query results as interactive web pages. It\'s used to build advanced internal tools, dashboards, and public websites, entirely in SQL.' },
    { domain: '51cto.com', siteName: '51CTO学堂', date: '2025/07/04', title: '开源数据可视化工具达芬奇（DaVinci）入门指南', url: 'https://edu.51cto.com/article/note/4035.html', snippet: '达芬奇（DaVinci）是一款由国内宜线团队开发的开源数据可视化工具，支持多种图形展示方式，操作简单，适合中小型公司使用。其核心功能包括：拖拽式操作：用户可以通过简单的拖拽操作完成数据可视化。' },
    { domain: 'apple.com', siteName: 'Apple', date: '2025/11/18', title: 'Zing DataGPT: Data Viz & AI App', url: 'https://apps.apple.com/us/app/zing-datagpt-data-viz-ai/id1563294091', snippet: 'All the powerful SQL functionality is included: counts, sums, filtering, and group bys! A powerful SQL client lets you create tables and export CSV files to Google Sheets and Microsoft Excel.' },
    { domain: 'csdn.net', siteName: 'CSDN', date: '2025/09/19', title: 'Blazer：一个免费开源、基于SQL的数据分析与可视化工具', url: 'https://tonydong.blog.csdn.net/article/details/151706066', snippet: 'Blazer 是一个免费开源、基于浏览器的数据分析与可视化工具，通过编写 SQL 查询数据、生成图表和仪表盘。Blazer 项目使用 Ruby 和 HTML 开发，遵循 MIT 开源协议。' },
    { domain: 'ld246.com', siteName: '链滴', date: '2025/09/29', title: 'STtools 插件：聚合可视化操作面板（数据库图表生成器）', url: 'https://ld246.com/article/1759067943123/comment/1759112102453#comments', snippet: 'SQL 查询统计图表 用于统计每个 SQL 代码查询到的数量 应用场景示例：统计某个文档中使用特定关键词的次数，用饼图展示，直观展示相关内容的占比。' },
    { domain: 'csdn.net', siteName: 'CSDN博客', date: '2025/12/24', title: '推荐开源项目：Bdash - 简单易用的SQL客户端', url: 'https://blog.csdn.net/gitblog_00017/article/details/138789201', snippet: 'Bdash 是一款轻量级的数据分析SQL客户端，旨在简化数据查询和可视化的过程。它以其简洁的界面、强大的功能和多数据源支持赢得了开发者们的喜爱。' },
    { domain: 'gitcode.com', siteName: 'GitCode', date: '2026/01/18', title: '探索数据的新境界：qStudio，免费的SQL分析利器', url: 'https://blog.gitcode.com/388eaaec760d118ff8176899bf4787d2.html', snippet: 'qStudio 正是为这一需求量身定制的免费SQL图形界面工具。它不仅支持运行SQL脚本、轻松浏览表格、图表展示，还能方便地导出查询结果。' },
    { domain: 'dbvis.com', siteName: 'DbVisualizer', date: '2025/12/19', title: 'Creating Queries Graphically', url: 'https://www.dbvis.com/docs/12.1/working-with-sql/creating-queries-graphically/', snippet: 'The Query Builder provides a point and click interface and does not require in-depth knowledge about the SQL syntax. To create a query, open the query builder using the SQL Commander->Show Query Builder menu choice.' },
  ]

  // 为每条结果分配分类
  const categoryMap = {
    'webpage': '网页', 'video': '视频', 'doc': '文档',
    'academic': '学术', 'code': '代码', 'community': '社区',
  }
  const domainCategoryMap = {
    'chinaooc.com.cn': 'academic', 'smartedu.cn': 'academic', 'classcentral.com': 'academic',
    'unipus.cn': 'academic', 'cnki.net': 'academic', 'udemy.com': 'academic',
    'freecodecamp.org': 'academic', 'datacamp.com': 'academic', 'pluralsight.com': 'academic',
    'mimo.org': 'academic', 'highgo.com': 'academic', 'xduph.com': 'academic',
    'csdn.net': 'webpage', 'juejin.cn': 'webpage', 'zhihu.com': 'webpage',
    '51cto.com': 'webpage', '163.com': 'webpage', 'tencent.cn': 'webpage',
    'pingkai.cn': 'webpage', 'racent.com': 'webpage', 'ld246.com': 'webpage',
    'stackoverflow.com': 'code', 'github.com': 'code', 'gitcode.com': 'code',
    'gitea.com': 'code', 'apify.com': 'code',
    'oreilly.com': 'doc', 'postgresql.org': 'doc', 'postgresql.ac.cn': 'doc',
    'docs.oracle.com': 'doc', 'alibabacloud.com': 'doc', 'cloud.tencent.com': 'doc',
    'aliyun.com': 'doc', 'dbvis.com': 'doc', 'yugabyte.com': 'doc',
    'mogdb.io': 'doc', 'developer.mozilla.org': 'doc', 'runoob.com': 'doc',
    'bilibili.com': 'video', 'youtube.com': 'video',
  }

  allResults.forEach(r => {
    r.category = domainCategoryMap[r.domain] || 'webpage'
    r.categoryLabel = categoryMap[r.category] || '网页'
  })

  // 模拟搜索过程：15秒内逐步增加结果
  const totalTarget = allResults.length
  const totalDuration = 15000
  const startTime = Date.now()
  let addedCount = 0

  while (addedCount < totalTarget) {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / totalDuration, 1)
    const expectedCount = Math.floor(Math.pow(progress, 0.7) * totalTarget)
    const batchAdd = Math.max(1, Math.min(
      expectedCount - addedCount,
      1 + Math.floor(Math.random() * 4)
    ))
    const toAdd = Math.min(batchAdd, totalTarget - addedCount)
    addedCount += toAdd
    conversationStore.setSearchResults([...allResults.slice(0, addedCount)])
    const delay = 100 + Math.floor(Math.random() * 500)
    await new Promise(resolve => setTimeout(resolve, delay))
  }

  conversationStore.setSearchResults([...allResults])
  await new Promise(resolve => setTimeout(resolve, 300))
}

const handleSend = async () => {
  if ((!userInput.value.trim() && uploadedFiles.value.length === 0) || isSending.value) return

  const message = userInput.value.trim()
  const files = [...uploadedFiles.value]
  userInput.value = ''
  uploadedFiles.value = []
  isSending.value = true

  try {
    let finalMessage = message
    let fileSummary = ''

    if (files.length > 0) {
      // 先添加用户消息到聊天（带附件信息）
      const fileNames = files.map(f => f.name).join(', ')
      const previewMessage = message ? `${message}\n\n[附件: ${fileNames}]` : `[附件: ${fileNames}]`

      conversationStore.addUserMessage({
        id: 'optimistic-' + Date.now(),
        role: 'user',
        content: previewMessage,
        created_at: new Date().toISOString()
      })

      // 启动文件阅读状态（在聊天中显示为AI消息气泡）
      startFileReading(files)

      // 上传文件
      const formData = new FormData()
      files.forEach(file => {
        formData.append('files', file.raw)
      })
      formData.append('conversation_id', conversationId.value)

      const uploadResponse = await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      const uploadedDocs = uploadResponse.data.documents || []

      // 模拟文件解析过程，传入后端提取的真实文档内容
      const realTexts = uploadedDocs.map(doc => ({
        name: doc.original_filename,
        text: doc.extracted_text || ''
      }))
      await simulateFileReading(files, uploadedDocs, realTexts)

      // 解析完成后，发送消息给AI（文件内容已由后端提取，不再重复拼接摘要文本）
      finalMessage = message ? `${message}\n\n[附件: ${fileNames}]` : `[附件: ${fileNames}]`

      // 启用联网搜索时模拟搜索效果
      if (webSearchEnabled.value) {
        isSearchCounting.value = true
        await simulateWebSearch(finalMessage)
        isSearchCounting.value = false
      }

      // 发送消息给AI（包含文件内容摘要，AI会据此回复）
      conversationStore.sendMessage(finalMessage, authStore.user.id)
    } else {
      // 没有文件，直接发送
      conversationStore.addUserMessage({
        id: 'optimistic-' + Date.now(),
        role: 'user',
        content: finalMessage,
        created_at: new Date().toISOString()
      })

      // 启用联网搜索时模拟搜索效果
      if (webSearchEnabled.value) {
        isSearchCounting.value = true
        await simulateWebSearch(finalMessage)
        isSearchCounting.value = false
      }

      conversationStore.sendMessage(finalMessage, authStore.user.id)
    }
  } catch (error) {
    ElMessage.error('发送消息失败: ' + error.message)
    fileReadingState.done = true
  } finally {
    isSending.value = false
  }
}

const handleFileChange = (file) => {
  const cat = getFileCategory(file.name)
  const maxSize = (cat === 'video' || cat === 'audio') ? 200 * 1024 * 1024 : 50 * 1024 * 1024
  const maxLabel = (cat === 'video' || cat === 'audio') ? '200MB' : '50MB'
  if (file.size > maxSize) {
    ElMessage.error(`${cat === 'video' ? '视频' : cat === 'audio' ? '音频' : '文件'}大小不能超过${maxLabel}`)
    return
  }

  uploadedFiles.value.push({
    id: Date.now() + Math.random(),
    name: file.name,
    raw: file.raw
  })
}

const removeFile = (fileId) => {
  uploadedFiles.value = uploadedFiles.value.filter(f => f.id !== fileId)
}

// ── 文件阅读模拟 ──
const startFileReading = (files) => {
  const names = files.map(f => f.name).join('、')
  fileReadingState.active = true
  fileReadingState.fileName = names
  fileReadingState.fileType = getFileCategory(files[0]?.name)
  fileReadingState.progress = 0
  fileReadingState.step = '正在理解文件...'
  fileReadingState.steps = files.map(f => ({ name: f.name, status: 'uploading', category: getFileCategory(f.name) }))
  fileReadingState.done = false
  fileReadingState.result = ''
  fileReadingState.fileResults = []
}

const simulateFileReading = async (files, docs, realTexts = []) => {
  const delay = (ms) => new Promise(r => setTimeout(r, ms))

  try {
    // Phase 1: 上传完成
    fileReadingState.step = '文件理解完成，开始解析...'
    fileReadingState.progress = 10
    fileReadingState.steps.forEach(s => s.status = 'uploaded')
    await delay(500)

    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      const cat = getFileCategory(file.name)
      const stepItem = fileReadingState.steps[i]
      const realText = realTexts[i]?.text || ''

      stepItem.status = 'reading'
      fileReadingState.step = `正在理解: ${file.name}`

      if (cat === 'video') {
        // 视频使用独立的视频理解卡片（淡入淡出动画）
        fileReadingState.step = `${file.name}: 启动视频理解...`
        fileReadingState.progress = 5
        await delay(300)

        // 启动视频理解卡片动画（约60秒）
        await startVideoUnderstanding(file.name)

        stepItem.status = 'done'
        fileReadingState.progress = 100
        fileReadingState.step = `${file.name}: 视频理解完成`
        fileReadingState.fileResults.push({
          name: file.name,
          category: 'video',
          summary: `视频时长约${2 + Math.floor(Math.random() * 8)}分钟，包含${3 + Math.floor(Math.random() * 5)}个场景切换。已识别${2 + Math.floor(Math.random() * 3)}位说话人，提取${80 + Math.floor(Math.random() * 120)}条语音片段，画面中检测到文字、人物和物品等多类元素。`
        })
        // 视频理解完成后不再追加解析结果文本（已由视频理解卡片展示）

      } else if (cat === 'audio') {
        const audioSteps = [
          { text: '正在解码音频编码格式与采样率参数...', progress: 12 },
          { text: '正在执行频谱分析与降噪预处理...', progress: 25 },
          { text: '正在启动 ASR 引擎进行语音到文本的高精度转写...', progress: 45 },
          { text: '正在识别不同发声源并生成说话者日志（Diarization）...', progress: 65 },
          { text: '正在提取语调、停顿与情感特征向量...', progress: 80 },
          { text: '正在合成语音时间轴与语义段落索引...', progress: 92 },
          { text: '音频深层语义解析完毕，支持按时间戳精准定位追问。', progress: 100 },
        ]
        for (const as of audioSteps) {
          fileReadingState.step = `${file.name}: ${as.text}`
          fileReadingState.progress = as.progress
          await delay(350 + Math.random() * 500)
        }
        stepItem.status = 'done'
        const contentPreview = realText ? `\n内容预览:\n${realText.substring(0, 500)}` : ''
        fileReadingState.result += `🎵 ${file.name}: 音频时长约${1 + Math.floor(Math.random() * 5)}分钟，已提取语音文字内容。${contentPreview}\n`
        fileReadingState.fileResults.push({
          name: file.name,
          category: 'audio',
          summary: `音频时长约${1 + Math.floor(Math.random() * 5)}分钟，已识别${60 + Math.floor(Math.random() * 100)}条语音片段，区分${1 + Math.floor(Math.random() * 3)}位说话人，提取背景音乐与音效信息。`
        })

      } else if (cat === 'image') {
        const imgSteps = [
          { text: '正在加载图像矩阵与色彩空间解码...', progress: 12 },
          { text: '正在提取底层视觉特征（边缘、纹理、对比度）...', progress: 28 },
          { text: '正在扫描全图并生成目标边界框（Bounding Box）...', progress: 42 },
          { text: '正在进行实体识别，锁定画面核心人、物、景...', progress: 56 },
          { text: '正在扫描画面中的微小细节与文本区域（场景 OCR）...', progress: 70 },
          { text: '正在分析画面主体的空间拓扑关系（相对位置与遮挡）...', progress: 82 },
          { text: '正在推断图像的整体情境色彩与可能的环境音效...', progress: 92 },
          { text: '正在生成多维度图像描述与视觉特征向量...', progress: 100 },
        ]
        for (const is of imgSteps) {
          fileReadingState.step = `${file.name}: ${is.text}`
          fileReadingState.progress = is.progress
          await delay(300 + Math.random() * 500)
        }
        stepItem.status = 'done'
        const contentPreview = realText ? `\n识别结果:\n${realText.substring(0, 500)}` : ''
        fileReadingState.result += `🖼️ ${file.name}: 图片已识别。${contentPreview}\n`
        fileReadingState.fileResults.push({
          name: file.name,
          category: 'image',
          summary: `图片分辨率${800 + Math.floor(Math.random() * 4000)}×${600 + Math.floor(Math.random() * 3000)}，识别到${1 + Math.floor(Math.random() * 5)}个主要物体，${Math.random() > 0.5 ? '检测到画面中的文字内容（OCR）。' : '未检测到文字内容。'}画面主体为${['风景','人物','产品','图表','文档截图'][Math.floor(Math.random() * 5)]}类。`
        })

      } else if (cat === 'pdf') {
        const pdfSteps = [
          { text: '正在初始化文档解析引擎...', progress: 10 },
          { text: '正在解析 DOM 树与底层排版数据...', progress: 22 },
          { text: '正在清洗冗余格式，提取纯文本字符流...', progress: 36 },
          { text: '正在识别文档层级，重构标题与段落从属关系...', progress: 50 },
          { text: '正在提取文档中的嵌套元素（表格、列表、脚注）...', progress: 64 },
          { text: '正在调用 OCR 引擎扫描文档内的内嵌图片...', progress: 76 },
          { text: '正在进行长文本分块（Chunking）与语义向量映射...', progress: 88 },
          { text: '正在建立段落间的逻辑引用与上下文记忆库...', progress: 95 },
          { text: '正在生成全局摘要与高频实体词云...', progress: 100 },
        ]
        for (const ps of pdfSteps) {
          fileReadingState.step = `${file.name}: ${ps.text}`
          fileReadingState.progress = ps.progress
          await delay(300 + Math.random() * 400)
        }
        stepItem.status = 'done'
        const contentPreview = realText ? `\n文档内容:\n${realText.substring(0, 800)}` : ''
        fileReadingState.result += `📄 ${file.name}: PDF文档，已提取全部文本内容。${contentPreview}\n`
        fileReadingState.fileResults.push({
          name: file.name,
          category: 'pdf',
          summary: `PDF文档共${5 + Math.floor(Math.random() * 15)}页，提取约${500 + Math.floor(Math.random() * 2000)}字文本内容，识别到${Math.floor(Math.random() * 3)}个表格和${Math.floor(Math.random() * 5)}张图片。`
        })

      } else if (cat === 'word' || cat === 'text') {
        const docSteps = [
          { text: '正在初始化文档解析引擎...', progress: 10 },
          { text: '正在解析 DOM 树与底层排版数据...', progress: 22 },
          { text: '正在清洗冗余格式，提取纯文本字符流...', progress: 36 },
          { text: '正在识别文档层级，重构标题与段落从属关系...', progress: 50 },
          { text: '正在提取文档中的嵌套元素（表格、列表、脚注）...', progress: 64 },
          { text: '正在调用 OCR 引擎扫描文档内的内嵌图片...', progress: 76 },
          { text: '正在进行长文本分块（Chunking）与语义向量映射...', progress: 88 },
          { text: '正在建立段落间的逻辑引用与上下文记忆库...', progress: 95 },
          { text: '语义索引构建完毕，已开启智能问答模式。', progress: 100 },
        ]
        for (const ds of docSteps) {
          fileReadingState.step = `${file.name}: ${ds.text}`
          fileReadingState.progress = ds.progress
          await delay(250 + Math.random() * 350)
        }
        stepItem.status = 'done'
        const contentPreview = realText ? `\n文档内容:\n${realText.substring(0, 800)}` : ''
        fileReadingState.result += `📝 ${file.name}: 文档已解析。${contentPreview}\n`
        fileReadingState.fileResults.push({
          name: file.name,
          category: 'word',
          summary: `文档共${3 + Math.floor(Math.random() * 10)}个段落，提取约${300 + Math.floor(Math.random() * 1500)}字文本内容，识别到${Math.floor(Math.random() * 3)}级标题结构。`
        })

      } else if (cat === 'ppt') {
        const pptSteps = [
          { text: '正在解包演示文稿对象集...', progress: 10 },
          { text: '正在按页码拆分幻灯片画布与演讲者备注...', progress: 22 },
          { text: '正在读取单页布局坐标，区分标题层与内容层...', progress: 36 },
          { text: '正在提取数据驱动组件（图表、SmartArt、数据透视表）...', progress: 50 },
          { text: '正在对幻灯片配图执行视觉描述（Image Captioning）...', progress: 64 },
          { text: '正在提取页内及跨页的关键连接词与过渡逻辑...', progress: 76 },
          { text: '正在合成图文联合特征，建立跨模态索引...', progress: 88 },
          { text: '正在提取核心论点，重构全局演讲大纲...', progress: 95 },
          { text: '演示文稿全息解析完成，支持跨页逻辑推演。', progress: 100 },
        ]
        for (const ps of pptSteps) {
          fileReadingState.step = `${file.name}: ${ps.text}`
          fileReadingState.progress = ps.progress
          await delay(300 + Math.random() * 400)
        }
        stepItem.status = 'done'
        const contentPreview = realText ? `\n演示文稿内容:\n${realText.substring(0, 800)}` : ''
        fileReadingState.result += `📊 ${file.name}: 演示文稿，已提取全部内容。${contentPreview}\n`
        fileReadingState.fileResults.push({
          name: file.name,
          category: 'ppt',
          summary: `演示文稿共${8 + Math.floor(Math.random() * 10)}张幻灯片，提取约${400 + Math.floor(Math.random() * 1200)}字文本内容，识别到${Math.floor(Math.random() * 4)}个图表和${Math.floor(Math.random() * 3)}条备注。`
        })

      } else if (cat === 'excel') {
        const xlsSteps = [
          { text: '正在解析电子表格文件结构与编码格式...', progress: 12 },
          { text: '正在扫描工作表目录，识别数据区域与合并单元格...', progress: 28 },
          { text: '正在逐行解析单元格数据类型与格式规则...', progress: 44 },
          { text: '正在提取公式依赖链与跨表引用关系...', progress: 58 },
          { text: '正在识别图表、数据透视表与条件格式...', progress: 72 },
          { text: '正在对数值列执行统计摘要与异常值检测...', progress: 86 },
          { text: '正在建立行列索引与数据语义映射...', progress: 95 },
          { text: '表格数据解析完毕，支持按单元格精准查询与计算。', progress: 100 },
        ]
        for (const xs of xlsSteps) {
          fileReadingState.step = `${file.name}: ${xs.text}`
          fileReadingState.progress = xs.progress
          await delay(300 + Math.random() * 400)
        }
        stepItem.status = 'done'
        const contentPreview = realText ? `\n表格数据:\n${realText.substring(0, 800)}` : ''
        fileReadingState.result += `📈 ${file.name}: 表格文件，已提取数据。${contentPreview}\n`
        fileReadingState.fileResults.push({
          name: file.name,
          category: 'excel',
          summary: `表格包含${2 + Math.floor(Math.random() * 5)}个工作表，共${50 + Math.floor(Math.random() * 500)}行×${5 + Math.floor(Math.random() * 15)}列数据，识别到${Math.floor(Math.random() * 3)}个公式和${Math.floor(Math.random() * 2)}个图表。`
        })

      } else {
        await delay(500)
        stepItem.status = 'done'
        const contentPreview = realText ? `\n内容:\n${realText.substring(0, 500)}` : ''
        fileReadingState.result += `📎 ${file.name}: 文件已读取。${contentPreview}\n`
        fileReadingState.fileResults.push({
          name: file.name,
          category: 'other',
          summary: `文件已读取，提取约${100 + Math.floor(Math.random() * 500)}字内容。`
        })
      }
    }

    fileReadingState.progress = 100
    fileReadingState.step = '全部文件理解完成'
    fileReadingState.done = true
    // 不再隐藏卡片，保留展示每个文件的理解结果

  } catch (e) {
    fileReadingState.done = true
  }
}

const handleNewConversation = async () => {
  try {
    const conversation = await conversationStore.createConversation('新对话')
    router.push(`/chat/${conversation.id}`)

    await websocketService.connect()
    websocketService.joinConversation(conversation.id, authStore.user.id)

    await conversationStore.fetchConversations()
  } catch (error) {
    ElMessage.error('创建对话失败: ' + error.message)
  }
}

const selectConversation = async (convId) => {
  if (convId === conversationId.value) return

  try {
    router.push(`/chat/${convId}`)
    await conversationStore.fetchConversation(convId)
    websocketService.joinConversation(convId, authStore.user.id)
  } catch (error) {
    ElMessage.error('加载对话失败: ' + error.message)
  }
}

const handleRenameConversation = (conv) => {
  renameDialogTarget.value = conv
  renameDialogInput.value = conv.title
  showRenameDialog.value = true
}

const onRenameConfirm = async (newTitle) => {
  const conv = renameDialogTarget.value
  showRenameDialog.value = false
  if (!conv || !newTitle || newTitle === conv.title) return

  try {
    await api.put(`/conversations/${conv.id}`, { title: newTitle })
    await conversationStore.fetchConversations()

    if (conv.id === conversationId.value) {
      conversationStore.currentConversation.title = newTitle
    }

    ElMessage.success('重命名成功')
  } catch (error) {
    ElMessage.error('重命名失败: ' + error.message)
  }
}

const onRenameCancel = () => {
  showRenameDialog.value = false
  renameDialogTarget.value = null
}

const handleDeleteConversation = (conv) => {
  deleteDialogTarget.value = conv
  deleteDialogMessage.value = `确定要删除对话"${conv.title}"吗？此操作不可恢复。`
  showDeleteDialog.value = true
}

const onDeleteConfirm = async () => {
  const conv = deleteDialogTarget.value
  showDeleteDialog.value = false
  if (!conv) return

  try {
    await api.delete(`/conversations/${conv.id}`)
    await conversationStore.fetchConversations()

    if (conv.id === conversationId.value) {
      if (conversations.value.length > 0) {
        router.push(`/chat/${conversations.value[0].id}`)
      } else {
        await handleNewConversation()
      }
    }

    ElMessage.success('删除成功')
  } catch (error) {
    ElMessage.error('删除失败: ' + error.message)
  }
}

const onDeleteCancel = () => {
  showDeleteDialog.value = false
  deleteDialogTarget.value = null
}

const handleShareConversation = (conv) => {
  shareDialogTarget.value = conv
  showShareDialog.value = true
}

const handleShareDialogClose = () => {
  showShareDialog.value = false
  shareDialogTarget.value = null
}

const handleShareSaved = () => {
  // Share settings saved, dialog stays open to show link
}

const handleHeaderGeneratePPT = () => {
  const conv = conversationStore.currentConversation
  if (!conv) {
    ElMessage.error('请先选择一个对话')
    return
  }

  // 查找现有大纲，如果没有则使用空大纲
  const outlineMessage = messages.value.slice().reverse().find(msg =>
    msg.role === 'assistant' &&
    msg.meta_data?.outline
  )

  if (outlineMessage) {
    handleGeneratePPTFromOutline(outlineMessage.meta_data.outline)
  } else {
    // 没有大纲时，使用对话需求直接生成
    const requirements = conv.requirements || {}
    const topic = requirements.topic || conv.title || '未命名主题'
    const defaultOutline = {
      title: topic,
      slides: [
        { slide_number: 1, title: topic, content_points: ['内容待生成'], position: 'cover' },
        { slide_number: 2, title: '主要内容', content_points: ['要点1', '要点2', '要点3'], position: 'content' },
        { slide_number: 3, title: '总结', content_points: ['感谢观看'], position: 'ending' }
      ]
    }
    handleGeneratePPTFromOutline(defaultOutline)
  }
}

const handleGenerateOutline = () => {
  const conv = conversationStore.currentConversation
  if (!conv) return
  const requirements = conv.requirements || {}
  const topic = requirements.topic || '未知主题'
  conversationStore.updateConversationState('GENERATING_OUTLINE')
  conversationStore.generateOutline(topic, requirements, authStore.user.id)
}

const handleGeneratePPTFromOutline = async (outline) => {
  try {
    // 蚂蚁: 直接打开模板选择对话框，不再先生成大纲
    // 保存对话记录到 window，供后续使用
    const messages = conversationStore.messages || []
    console.log('[PPT] 对话记录数量:', messages.length)
    
    if (!messages || messages.length === 0) {
      ElMessage.error('对话记录为空，无法生成PPT')
      return
    }
    
    // 构建对话内容字符串并保存
    const dialogueText = messages.map(m => {
      const role = m.role === 'user' ? '用户' : 'AI'
      const content = m.content || ''
      return `${role}: ${content}`
    }).join('\n\n')
    
    window.currentDialogue = dialogueText
    console.log('[PPT] 对话内容长度:', dialogueText.length)
    
    // 直接打开模板选择对话框
    showTemplateDialog.value = true
    selectedTemplate.value = null
  } catch (error) {
    console.error('[PPT] 打开模板选择失败:', error)
    ElMessage.error('操作失败: ' + error.message)
  }
}

const generatePPTWithTemplate = async (outline, templateId) => {
  try {
    conversationStore.startPPTGeneration()

    const requirements = conversationStore.currentConversation?.requirements || {}

    console.log('[PPT] 使用指定大纲生成PPT:', outline)
    console.log('[PPT] 使用模板ID:', templateId)

    // 蚂蚁: 显示打字机效果的大纲内容
    const outlineText = `正在生成PPT大纲...\n\n主题: ${outline.title}\n\n`
    let currentText = ''
    
    // 蚂蚁: 打字机效果显示大纲
    for (let i = 0; i < outlineText.length; i++) {
      currentText += outlineText[i]
      // 这里可以更新UI显示currentText
      await new Promise(resolve => setTimeout(resolve, 30))
    }
    
    // 蚂蚁: 显示每页大纲
    if (outline.slides && outline.slides.length > 0) {
      for (let i = 0; i < outline.slides.length; i++) {
        const slide = outline.slides[i]
        const slideText = `\n第${slide.slide_number}页: ${slide.title}\n`
        
        for (let j = 0; j < slideText.length; j++) {
          currentText += slideText[j]
          // 这里可以更新UI显示currentText
          await new Promise(resolve => setTimeout(resolve, 20))
        }
        
        // 蚂蚁: 显示要点
        if (slide.content_points && slide.content_points.length > 0) {
          for (const point of slide.content_points) {
            const pointText = `  - ${point}\n`
            for (let k = 0; k < pointText.length; k++) {
              currentText += pointText[k]
              // 这里可以更新UI显示currentText
              await new Promise(resolve => setTimeout(resolve, 15))
            }
          }
        }
      }
    }

    // 蚂蚁: 调用WebSocket生成PPT
    websocketService.generatePPT(
      conversationId.value,
      authStore.user.id,
      outline,
      requirements,
      'modern',
      templateId
    )
  } catch (error) {
    ElMessage.error('生成PPT失败: ' + error.message)
    conversationStore.failPPTGeneration(error?.message || 'PPT生成失败')
  }
}

const confirmGenerateWithTemplate = async () => {
  showTemplateDialog.value = false
  const templateId = selectedTemplate.value?.id

  if (!templateId) {
    ElMessage.warning('请选择一个模板')
    return
  }

  try {
    // 蚂蚁: 获取对话记录
    const messages = conversationStore.messages || []
    console.log('[PPT] 对话记录数量:', messages.length)
    
    if (!messages || messages.length === 0) {
      ElMessage.error('对话记录为空，无法生成PPT')
      return
    }
    
    // 构建对话内容字符串
    const dialogueText = messages.map(m => {
      const role = m.role === 'user' ? '用户' : 'AI'
      const content = m.content || ''
      return `${role}: ${content}`
    }).join('\n\n')
    
    console.log('[PPT] 对话内容长度:', dialogueText.length)
    
    // 显示大纲生成对话框
    showOutlineDialog.value = true
    outlineText.value = ''
    isGeneratingOutlineLocal.value = true
    outlineProgressLocal.value = 0
    outlineStageLocal.value = 'preparing'
    startOutlineVisualTimer()
    outlineText.value = '正在准备生成大纲...\n'
    
    // 使用SSE流式接收大纲生成进度
    const sseResponse = await fetch(`/api/conversations/${conversationId.value}/generate-outline`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.accessToken}`
      },
      body: JSON.stringify({
        dialogue: dialogueText,
        template_id: templateId
      })
    })
    
    if (!sseResponse.ok) {
      throw new Error('生成大纲请求失败')
    }
    
    const reader = sseResponse.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let outline = null
    
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''  // 保留未完成的行
      
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        
        try {
          const data = JSON.parse(line.slice(6))
          
          // 更新真实进度
          outlineProgressLocal.value = data.progress
          if (data.stage) {
            outlineStageLocal.value = data.stage
          }
          
          if (data.stage === 'preparing') {
            outlineText.value = '正在准备生成大纲...\n'
          } else if (data.stage === 'building_prompt') {
            outlineText.value = '正在构建提示词...\n'
          } else if (data.stage === 'calling_llm') {
            outlineText.value = '正在调用AI生成大纲...\n'
          } else if (data.stage === 'receiving') {
            outlineText.value = `正在接收AI响应... (${data.progress}%)\n`
          } else if (data.stage === 'parsing') {
            outlineText.value = '正在解析大纲内容...\n'
          } else if (data.stage === 'done') {
            await waitForPlannedDuration(outlineVisualStartedAt, OUTLINE_PLAN_TOTAL_MS)
            outline = data.outline
            outlineProgressLocal.value = 100
            outlineStageLocal.value = 'done'
            stopOutlineVisualTimer(100)
            
            // 显示大纲内容
            outlineText.value = '大纲生成完成！\n\n'
            const slides = outline.slides || []
            for (let i = 0; i < slides.length; i++) {
              const slide = slides[i]
              outlineText.value += `第${i + 1}页: ${slide.title}\n`
              if (slide.content_points && slide.content_points.length > 0) {
                for (let j = 0; j < slide.content_points.length; j++) {
                  outlineText.value += `  ${j + 1}. ${slide.content_points[j]}\n`
                }
              }
              outlineText.value += '\n'
            }
          } else if (data.stage === 'error') {
            outlineStageLocal.value = 'error'
            stopOutlineVisualTimer()
            throw new Error(data.message || '生成大纲失败')
          }
        } catch (parseErr) {
          if (parseErr.message && !parseErr.message.includes('JSON')) {
            throw parseErr
          }
        }
      }
    }
    
    isGeneratingOutlineLocal.value = false
    
    if (!outline) {
      ElMessage.error('生成大纲失败：未获取到大纲内容')
      showOutlineDialog.value = false
      return
    }
    
    console.log('[PPT] 生成的大纲:', outline)
    
    // 等待1秒让用户看到完成状态
    await new Promise(resolve => setTimeout(resolve, 1000))
    showOutlineDialog.value = false
    
    conversationStore.updatePPTProgress(0, '准备生成PPT...')
    startPPTVisualTimer()
    
    // 调用WebSocket生成PPT
    window.currentOutline = outline
    await generatePPTWithTemplate(outline, templateId)
  } catch (error) {
    console.error('[PPT] 生成失败:', error)
    stopOutlineVisualTimer()
    stopPPTVisualTimer()
    showOutlineDialog.value = false
    if (error !== 'cancel') {
      ElMessage.error('生成PPT失败: ' + error.message)
    }
  }
}

watch(currentPPT, (ppt) => {
  if (ppt) {
    ElMessage.success('PPT生成成功！')
  }
})

const openPPT = (pptId) => {
  router.push(`/ppt/${pptId}`)
}

// ── 教案生成 ──
const lessonPlanMap = reactive({})
const lessonLogRefs = {}

const getLessonState = (pptId) => {
  if (!lessonPlanMap[pptId]) {
    lessonPlanMap[pptId] = {
      generating: false,
      done: false,
      progress: 0,
      steps: [],
      logs: [],
      taskId: null,
      result: null,
    }
  }
  return lessonPlanMap[pptId]
}

const setLessonLogRef = (pptId, el) => {
  if (el) lessonLogRefs[pptId] = el
}

const startGenerateLessonPlan = async (pptId, message) => {
  const state = getLessonState(pptId)
  state.generating = true
  state.done = false
  state.progress = 0
  state.steps = []
  state.logs = []
  state.result = null

  try {
    const pptName = message?.content?.substring(0, 50) || '演示文稿'
    const res = await api.post('/lesson-plans/generate/', {
      ppt_name: pptName,
      ppt_id: pptId,
    })
    state.taskId = res.data.task_id
    pollLessonPlanTask(pptId)
  } catch (e) {
    ElMessage.error('启动教案生成失败')
    state.generating = false
  }
}

const pollLessonPlanTask = (pptId) => {
  const state = getLessonState(pptId)
  if (!state.taskId) return
  const timer = setInterval(async () => {
    try {
      const res = await api.get(`/lesson-plans/task/${state.taskId}/`)
      const data = res.data
      state.progress = data.progress
      state.steps = data.steps
      state.logs = data.logs

      nextTick(() => {
        const logEl = lessonLogRefs[pptId]
        if (logEl) logEl.scrollTop = logEl.scrollHeight
      })

      if (data.status === 'completed') {
        clearInterval(timer)
        state.generating = false
        state.done = true
        state.result = data.result
        ElMessage.success('教案生成完成！')
      } else if (data.status === 'failed') {
        clearInterval(timer)
        state.generating = false
        state.done = false
        ElMessage.error('教案生成失败: ' + (data.error || '未知错误'))
      }
    } catch (e) {
      clearInterval(timer)
      state.generating = false
    }
  }, 1000)
}

const downloadLessonPlan = async (pptId) => {
  const state = getLessonState(pptId)
  if (!state.taskId) return
  try {
    const res = await api.get(`/lesson-plans/file/${state.taskId}/`, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = state.result?.doc_name || '教案.docx'
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (e) {
    ElMessage.error('下载失败')
  }
}

const previewLessonPlan = async (pptId) => {
  const state = getLessonState(pptId)
  if (!state.taskId) return
  try {
    const res = await api.get(`/lesson-plans/preview/${state.taskId}/`)
    const cfg = res.data
    const onlyofficeUrl = cfg.onlyoffice_url || 'http://localhost:80'

    const html = `<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>${cfg.file_name || '教案预览'}</title></head>
<body style="margin:0;padding:0;height:100vh;">
<div id="editor" style="height:100vh;"></div>
<script src="${onlyofficeUrl}/web-apps/apps/api/documents/api.js"><\/script>
<script>
  const config = {
    type: 'desktop',
    documentType: 'word',
    document: ${JSON.stringify(cfg.document)},
    editorConfig: ${JSON.stringify(cfg.editor_config)},
    width: '100%',
    height: '100%',
    token: ${JSON.stringify(cfg.token || '')}
  };
  new window.DocsAPI.DocEditor('editor', config);
<\/script>
</body></html>`

    const blob = new Blob([html], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank')
  } catch (e) {
    ElMessage.error('打开预览失败')
  }
}

const clearResponseWatchdog = () => {
  if (responseWatchdog) {
    clearTimeout(responseWatchdog)
    responseWatchdog = null
  }
}

const startResponseWatchdog = () => {
  clearResponseWatchdog()
  responseWatchdog = setTimeout(() => {
    if (isTyping.value) {
      ElMessage.warning('响应耗时较长，可能网络或模型繁忙，请稍后重试')
    }
  }, 65000)
}

const handleStreamingStart = () => {
  isTyping.value = true
  startResponseWatchdog()
}

const handleTyping = () => {
  isTyping.value = true
  startResponseWatchdog()
}

const handleError = (data) => {
  clearResponseWatchdog()
  isTyping.value = false
  if (typeof data?.message === 'string' && data.message.includes('大纲生成失败')) {
    conversationStore.failOutlineGeneration(data.message)
  }
  ElMessage.error(data.message || '发生错误')
}

const handleOutlineGenerationStart = () => {
  conversationStore.startOutlineGeneration()
}

const handleOutlineProgress = (data) => {
  conversationStore.updateOutlineProgress(data.progress, data.message)
  if ((data.progress || 0) >= 100) {
    conversationStore.finishOutlineGeneration()
  }
}

const handlePPTGenerationStart = () => {
  conversationStore.startPPTGeneration()
  if (!pptVisualTimer) startPPTVisualTimer()
}

const handlePPTProgress = (data) => {
  conversationStore.updatePPTProgress(data.progress, data.message, data.slide_number, data.slide_data)
}

const handlePPTGenerated = (data) => {
  // 后端已明确返回完成事件时，立刻结束前端“计划进度”占位，避免长时间停在 99%
  stopPPTVisualTimer(100)
  if (data?.ppt) {
    conversationStore.setPPT(data.ppt)
  }
  conversationStore.finishPPTGeneration()
  ElMessage.success('PPT生成成功！')
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''

  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date

  if (diff < 0) return '刚刚'
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`

  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatConversationTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date

  if (diff < 86400000) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
}

const loadTemplates = async () => {
  try {
    loadingTemplates.value = true
    // 并行加载内置模板和用户上传模板
    const [builtinRes, customRes] = await Promise.all([
      templateService.getBuiltinTemplates(),
      templateService.getTemplates()
    ])
    builtinTemplates.value = builtinRes.data.templates || []
    templates.value = customRes.data.templates || []
    categories.value = customRes.data.categories || {}
  } catch (error) {
    console.error('加载模板失败', error)
  } finally {
    loadingTemplates.value = false
  }
}

onMounted(() => {
  loadTemplates()
})

const getTemplateThumbnailUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path
  }
  // 绝对本地路径(如 C:\...) 无法直接作为HTTP路径拼接使用
  if (/^[a-zA-Z]:\\/.test(path)) {
    return ''
  }
  return path.startsWith('/') ? `http://localhost:5000${path}` : `http://localhost:5000/${path}`
}

const hasTemplateCover = (template) => {
  if (!template) return false
  return !!(
    template.thumbnail_url ||
    template.cover_url ||
    template.thumbnail_path ||
    (template.id && ['uploaded', 'analyzed'].includes(template.template_type))
  )
}

const getTemplateCoverUrl = (template, { preferById = false } = {}) => {
  if (!template) return ''

  const directPath = template.thumbnail_url || template.cover_url || template.thumbnail_path || ''

  if (directPath && (directPath.startsWith('http://') || directPath.startsWith('https://'))) {
    return directPath
  }

  // 用户模板优先走后端thumbnail接口，兼容数据库里保存绝对路径/未返回URL字段的情况
  if (preferById && template.id && ['uploaded', 'analyzed'].includes(template.template_type)) {
    return templateService.getTemplateThumbnailUrl(template.id)
  }

  return getTemplateThumbnailUrl(directPath)
}

const getBuiltinTemplateCardStyle = (template) => {
  const coverUrl = getTemplateCoverUrl(template)
  if (!coverUrl) return {}

  return {
    backgroundImage: `url(${coverUrl})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundRepeat: 'no-repeat'
  }
}
</script>

<style scoped>
/* ============================================
   ChatView - Dark Theme (matches Dashboard)
   ============================================ */

.chat-view {
  --cv-bg: #0a0a0b;
  --cv-text: #ffffff;
  --cv-panel: rgba(255, 255, 255, 0.02);
  --cv-panel-strong: rgba(255, 255, 255, 0.05);
  --cv-border: rgba(255, 255, 255, 0.08);
  --cv-border-soft: rgba(255, 255, 255, 0.06);
  --cv-text-main: rgba(255, 255, 255, 0.9);
  --cv-text-secondary: rgba(255, 255, 255, 0.7);
  --cv-text-muted: rgba(255, 255, 255, 0.45);
  --cv-text-dim: rgba(255, 255, 255, 0.3);

  height: 100vh;
  background: var(--cv-bg);
  color: var(--cv-text);
  position: relative;
  overflow: hidden;
}

:global(:root[data-theme='light']) .chat-view {
  --cv-bg: #f6f8fc;
  --cv-text: #111827;
  --cv-panel: rgba(255, 255, 255, 0.78);
  --cv-panel-strong: rgba(255, 255, 255, 0.95);
  --cv-border: rgba(15, 23, 42, 0.14);
  --cv-border-soft: rgba(15, 23, 42, 0.1);
  --cv-text-main: #111827;
  --cv-text-secondary: #374151;
  --cv-text-muted: #6b7280;
  --cv-text-dim: #9ca3af;
}

/* Background Effects */
.background-effects {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.glow {
  position: absolute;
  border-radius: 50%;
  mix-blend-mode: normal;
  filter: blur(128px);
  animation: glowPulse 6s ease-in-out infinite;
}

.glow-1 {
  top: -10%;
  left: 10%;
  width: 24rem;
  height: 24rem;
  background: rgba(139, 92, 246, 0.08);
}

.glow-2 {
  bottom: -10%;
  right: 10%;
  width: 20rem;
  height: 20rem;
  background: rgba(99, 102, 241, 0.08);
  animation-delay: 2s;
}

@keyframes glowPulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* Layout */
.chat-layout {
  display: flex;
  height: 100%;
  position: relative;
  z-index: 1;
}

/* ============================================
   Sidebar
   ============================================ */
.chat-sidebar {
  width: 280px;
  background: var(--cv-panel);
  border-right: 1px solid var(--cv-border-soft);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  backdrop-filter: blur(20px);
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid var(--cv-border-soft);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-icon {
  width: 32px;
  height: 28px;
  border-radius: 8px;
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  color: white;
}

.brand-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--cv-text-main);
}

.new-chat-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  background: var(--cv-panel-strong);
  border: 1px solid var(--cv-border);
  border-radius: 8px;
  color: var(--cv-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.new-chat-btn:hover {
  background: color-mix(in srgb, var(--cv-panel-strong) 75%, #8b5cf6 25%);
  color: var(--cv-text-main);
  border-color: color-mix(in srgb, var(--cv-border) 70%, #8b5cf6 30%);
}

/* Conversation List */
.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.conversation-list::-webkit-scrollbar {
  width: 4px;
}

.conversation-list::-webkit-scrollbar-thumb {
  background: var(--cv-border);
  border-radius: 2px;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  margin-bottom: 2px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
  position: relative;
}

.conversation-item:hover {
  background: var(--cv-panel-strong);
}

.conversation-item.active {
  background: rgba(139, 92, 246, 0.15);
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.conv-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: var(--cv-panel-strong);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--cv-text-muted);
  flex-shrink: 0;
}

.conversation-item.active .conv-icon {
  background: rgba(139, 92, 246, 0.3);
  color: #a78bfa;
}

.conv-info {
  flex: 1;
  min-width: 0;
}

.conv-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--cv-text-main);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conv-time {
  font-size: 11px;
  color: var(--cv-text-dim);
  margin-top: 2px;
}

.conv-actions {
  display: none;
  gap: 2px;
  flex-shrink: 0;
}

.conversation-item:hover .conv-actions {
  display: flex;
}

.conv-action-btn {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: none;
  background: transparent;
  color: var(--cv-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.conv-action-btn:hover {
  background: var(--cv-panel-strong);
  color: var(--cv-text-main);
}

.empty-conversations {
  padding: 40px 20px;
  text-align: center;
}

.empty-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: var(--cv-panel);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  color: var(--cv-text-dim);
}

.empty-conversations p {
  font-size: 13px;
  color: var(--cv-text-dim);
}

/* ============================================
   Main Chat Area
   ============================================ */
.chat-main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  position: relative;
}

/* ============================================
   Right Search Panel
   ============================================ */
.search-panel {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 380px;
  z-index: 10;
  background: #111113;
  border-left: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  animation: slideInRight 0.25s ease;
}

@keyframes slideInRight {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

.search-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}

.search-panel-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-panel-icon {
  color: rgba(255, 255, 255, 0.5);
}

.search-panel-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
}

.search-panel-count {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.06);
  padding: 1px 7px;
  border-radius: 999px;
}

.search-panel-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.35);
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  transition: all 0.15s;
}

.search-panel-close:hover {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.8);
}

.search-panel-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.search-panel-group {
  margin-bottom: 4px;
}

.search-panel-group-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px 4px;
  position: relative;
}

.search-panel-group-header::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 14px;
  border-radius: 999px;
}

.search-panel-group-header.cat-webpage::before { background: #60a5fa; }
.search-panel-group-header.cat-video::before { background: #f472b6; }
.search-panel-group-header.cat-doc::before { background: #fbbf24; }
.search-panel-group-header.cat-academic::before { background: #a78bfa; }
.search-panel-group-header.cat-code::before { background: #34d399; }
.search-panel-group-header.cat-community::before { background: #fb923c; }

.search-panel-group-icon {
  flex-shrink: 0;
}

.search-panel-group-icon.cat-webpage { color: #60a5fa; }
.search-panel-group-icon.cat-video { color: #f472b6; }
.search-panel-group-icon.cat-doc { color: #fbbf24; }
.search-panel-group-icon.cat-academic { color: #a78bfa; }
.search-panel-group-icon.cat-code { color: #34d399; }
.search-panel-group-icon.cat-community { color: #fb923c; }

.search-panel-group-label {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.55);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.search-panel-group-count {
  font-size: 11px;
  padding: 0 6px;
  border-radius: 999px;
  line-height: 18px;
}

.search-panel-group-count.cat-webpage { color: #60a5fa; background: rgba(96, 165, 250, 0.1); }
.search-panel-group-count.cat-video { color: #f472b6; background: rgba(244, 114, 182, 0.1); }
.search-panel-group-count.cat-doc { color: #fbbf24; background: rgba(251, 191, 36, 0.1); }
.search-panel-group-count.cat-academic { color: #a78bfa; background: rgba(167, 139, 250, 0.1); }
.search-panel-group-count.cat-code { color: #34d399; background: rgba(52, 211, 153, 0.1); }
.search-panel-group-count.cat-community { color: #fb923c; background: rgba(251, 146, 60, 0.1); }

.search-panel-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  text-decoration: none;
  transition: background 0.15s;
  cursor: pointer;
}

.search-panel-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.search-panel-favicon {
  width: 22px;
  height: 22px;
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.06);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: rgba(255, 255, 255, 0.3);
}

.search-panel-favicon-img {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  flex-shrink: 0;
  object-fit: contain;
  background: rgba(255, 255, 255, 0.9);
  padding: 2px;
}

.search-panel-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
  flex: 1;
}

.search-panel-item-site {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-panel-item-sitename {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  white-space: nowrap;
}

.search-panel-item-date {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.25);
  white-space: nowrap;
}

.search-panel-item-title {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.72);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}

.search-panel-item-snippet {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
}

.search-panel-item-url {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.28);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.search-panel-external {
  flex-shrink: 0;
  color: rgba(255, 255, 255, 0.18);
}

/* Header */
.chat-header-modern {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid var(--cv-border-soft);
  background: color-mix(in srgb, var(--cv-bg) 85%, transparent 15%);
  backdrop-filter: blur(16px);
  flex-shrink: 0;
}

.chat-peer-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.peer-avatar-wrap {
  position: relative;
  width: 36px;
  height: 36px;
}

.peer-avatar {
  width: 36px;
  height: 36px;
  border-radius: 9999px;
  background: #ffffff;
  border: 1px solid var(--cv-border);
  object-fit: cover;
}

.ai-avatar-img {
  background: #ffffff;
  object-fit: contain;
  padding: 2px;
}

.peer-status-dot {
  position: absolute;
  right: -1px;
  bottom: -1px;
  width: 10px;
  height: 10px;
  border-radius: 9999px;
  border: 2px solid var(--cv-bg);
}

.status-online {
  background: #22c55e;
}

.status-idle {
  background: #9ca3af;
}

.peer-meta {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.peer-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--cv-text-main);
}

.peer-status {
  margin-top: 2px;
  font-size: 12px;
  color: var(--cv-text-muted);
  text-transform: lowercase;
}

/* 协作者头像徽章 */
.collab-avatar-badge {
  position: absolute;
  left: -6px;
  bottom: -4px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid var(--cv-bg);
  overflow: hidden;
  background: #a78bfa;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.collab-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.collab-avatar-fallback {
  font-size: 9px;
  color: #fff;
  font-weight: 700;
}

.collab-badge {
  display: inline-block;
  margin-left: 6px;
  padding: 1px 6px;
  font-size: 10px;
  font-weight: 600;
  color: #a78bfa;
  background: rgba(167, 139, 250, 0.12);
  border: 1px solid rgba(167, 139, 250, 0.25);
  border-radius: 999px;
  vertical-align: middle;
}

.collab-user-info {
  color: #a78bfa;
  font-size: 11px;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  border-bottom: 1px solid var(--cv-border-soft);
  background: var(--cv-panel);
  backdrop-filter: blur(20px);
  flex-shrink: 0;
}

.header-left {
  flex: 1;
  display: flex;
  align-items: center;
  margin-right: 20px;
  overflow: hidden;
}

/* Plan Steps */
.plan-steps {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 0;
}

.plan-step {
  display: flex;
  align-items: center;
  position: relative;
  flex: 1;
  min-width: 0;
}

.step-icon-wrapper {
  flex-shrink: 0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.step-icon-wrapper:hover {
  transform: scale(1.1);
}

.step-icon-wrapper:active {
  transform: scale(0.9);
}

.step-completed .step-icon-wrapper {
  background: rgba(34, 197, 94, 0.1);
}

.step-active .step-icon-wrapper {
  background: rgba(59, 130, 246, 0.1);
  animation: pulse-ring 2s ease-in-out infinite;
}

@keyframes pulse-ring {
  0%, 100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.2); }
  50% { box-shadow: 0 0 0 4px rgba(59, 130, 246, 0); }
}

.icon-completed {
  color: #22c55e;
}

.icon-active {
  color: #3b82f6;
}

.icon-pending {
  color: var(--cv-text-dim);
}

.step-content {
  flex: 1;
  min-width: 0;
  margin-left: 6px;
  overflow: hidden;
}

.step-title {
  font-size: 12px;
  font-weight: 500;
  color: var(--cv-text-dim);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.2s ease;
}

.title-completed {
  color: rgba(34, 197, 94, 0.8);
}

.title-active {
  color: var(--cv-text-main);
  font-weight: 600;
}

.step-connector {
  flex: 1;
  height: 2px;
  background: var(--cv-border);
  margin: 0 8px;
  border-radius: 1px;
  transition: background 0.3s ease;
  min-width: 12px;
}

.connector-completed {
  background: rgba(34, 197, 94, 0.4);
}

.header-right {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.menu-btn {
  width: 34px;
  justify-content: center;
  padding: 0;
}

.header-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: 8px;
  border: 1px solid var(--cv-border);
  background: var(--cv-panel);
  color: var(--cv-text-secondary);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.header-btn:hover:not(:disabled) {
  background: var(--cv-panel-strong);
  color: var(--cv-text-main);
  border-color: color-mix(in srgb, var(--cv-border) 70%, #8b5cf6 30%);
}

.header-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.outline-btn:hover:not(:disabled) {
  border-color: rgba(52, 211, 153, 0.3);
  color: #34d399;
}

.ppt-btn:hover:not(:disabled) {
  border-color: rgba(139, 92, 246, 0.3);
  color: #a78bfa;
}

.back-btn:hover {
  border-color: color-mix(in srgb, var(--cv-border) 70%, #8b5cf6 30%);
}

/* ============================================
   Messages Area
   ============================================ */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.modern-messages {
  padding: 18px 22px;
}

.modern-msg-row {
  display: flex;
  margin: 14px 0;
  animation: messageIn 0.3s ease-out;
}

.modern-msg-row.is-user {
  justify-content: flex-end;
}

.modern-msg-row.is-ai {
  justify-content: flex-start;
}

.modern-msg-inner {
  display: flex;
  gap: 10px;
  max-width: 82%;
  align-items: flex-start;
}

.modern-msg-row.is-ai .modern-msg-inner {
  flex-wrap: wrap;
}

.modern-msg-inner.reverse {
  flex-direction: row-reverse;
}

.modern-avatar {
  width: 32px;
  height: 32px;
  flex: 0 0 32px;
}

.modern-avatar img {
  width: 100%;
  height: 100%;
  display: block;
  flex-shrink: 0;
  border-radius: 9999px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: #111;
  object-fit: cover;
}

.modern-avatar img.ai-avatar-img {
  background: #ffffff;
  object-fit: contain;
  padding: 2px;
  border-color: rgba(255, 255, 255, 0.32);
}

.modern-msg-content-wrap {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 0;
  flex: 1;
}

.modern-msg-inner.reverse .modern-msg-content-wrap {
  align-items: flex-end;
}

.modern-bubble {
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 14px;
  line-height: 1.5;
  border: 1px solid transparent;
}

.bubble-ai {
  background: #262626;
  border-color: #3a3a3a;
  color: rgba(255, 255, 255, 0.94);
}

.bubble-user {
  background: #ffffff;
  border-color: #e5e7eb;
  color: #111827;
}

.modern-bubble .message-text {
  background: transparent;
  border: none;
  padding: 0;
  color: inherit;
}

.modern-msg-meta {
  margin-top: 5px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modern-msg-row.is-user .modern-msg-meta {
  justify-content: flex-end;
}

.msg-action-trigger {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
  color: rgba(255, 255, 255, 0.6);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s ease;
}

.modern-msg-row:hover .msg-action-trigger {
  opacity: 1;
}

.messages-area::-webkit-scrollbar {
  width: 6px;
}

.messages-area::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
}

.messages-area::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.15);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  position: relative;
}

.empty-glow {
  position: absolute;
  width: 20rem;
  height: 20rem;
  border-radius: 50%;
  background: rgba(139, 92, 246, 0.06);
  filter: blur(96px);
  pointer-events: none;
}

.empty-state h2 {
  font-size: 1.25rem;
  font-weight: 500;
  background: linear-gradient(to right, rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.4));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
  position: relative;
}

.empty-state p {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.3);
  position: relative;
}

/* Message Items */
.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  animation: messageIn 0.3s ease-out;
}

@keyframes messageIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-user {
  flex-direction: row-reverse;
}

/* Avatars */
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-avatar {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.7);
}

.ai-avatar {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(99, 102, 241, 0.3));
  color: #a78bfa;
}

.ai-typing-avatar-img {
  border-radius: 9999px;
  background: #fff;
  object-fit: contain;
  padding: 2px;
  border: 1px solid rgba(255, 255, 255, 0.32);
}

/* Message Body */
.message-body {
  max-width: 70%;
  min-width: 200px;
}

.message-user .message-body {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
}

.message-user .message-meta {
  flex-direction: row-reverse;
}

.message-role {
  font-weight: 500;
  color: rgba(255, 255, 255, 0.5);
}

.message-text {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
}

.message-user .message-text {
  background: rgba(139, 92, 246, 0.15);
  border-color: rgba(139, 92, 246, 0.2);
  color: rgba(255, 255, 255, 0.9);
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background: rgba(139, 92, 246, 0.6);
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-8px);
    opacity: 1;
  }
}

/* ============================================
   Footer / Input
   ============================================ */
.chat-footer {
  padding: 14px 24px 28px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
 background: rgba(10, 10, 10, 0.85);
 backdrop-filter: blur(20px);
  flex-shrink: 0;
}

.uploaded-files {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.file-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
}

.file-remove {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.file-remove:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

/* Input Box */
.input-box {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #141416;
  border: 1px solid #2a2a2e;
  border-radius: 14px;
  transition: all 0.2s ease;
}

.input-box:focus-within {
  border-color: rgba(255, 255, 255, 0.18);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.04);
}

.input-actions {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.action-icon-btn {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.35);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.action-icon-btn.upload-btn {
  width: 28px;
  height: 28px;
}

.action-icon-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.8);
}

.action-icon-btn.web-search-active {
  color: #60a5fa;
  background: rgba(96, 165, 250, 0.12);
  box-shadow: 0 0 12px rgba(96, 165, 250, 0.25);
}

.action-icon-btn.voice-active {
  color: #f43f5e;
  background: rgba(244, 63, 94, 0.12);
  animation: voice-pulse 1.5s ease-in-out infinite;
}

@keyframes voice-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(244, 63, 94, 0.3); }
  50% { box-shadow: 0 0 0 6px rgba(244, 63, 94, 0); }
}

.voice-status {
  position: absolute;
  bottom: -22px;
  left: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: rgba(244, 63, 94, 0.8);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: calc(100% - 28px);
}

.voice-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #f43f5e;
  animation: voice-dot-blink 1s ease-in-out infinite;
  flex-shrink: 0;
}

@keyframes voice-dot-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.voice-label {
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-textarea {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: rgba(255, 255, 255, 0.92);
  font-size: 14px;
  line-height: 1.55;
  resize: none;
  min-height: 22px;
  max-height: 120px;
  padding: 5px 0;
  font-family: inherit;
}

.chat-textarea::placeholder {
  color: rgba(255, 255, 255, 0.25);
}

.send-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.3);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
  white-space: nowrap;
}

.send-btn.active {
  background: #ffffff;
  color: #0a0a0a;
  border-color: #ffffff;
  box-shadow: 0 2px 8px rgba(255, 255, 255, 0.08);
}

.send-btn.active:hover {
  background: #f3f4f6;
  border-color: #f3f4f6;
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.spin {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ============================================
   File Reading Overlay
   ============================================ */
/* File Reading Bubble (inside AI message) */
.file-reading-bubble {
  min-width: 280px;
  max-width: 400px;
}

.file-reading-bubble-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.file-reading-title-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-reading-title {
  font-size: 13px;
  font-weight: 600;
  color: rgba(255,255,255,0.9);
}

.file-reading-percent {
  font-size: 12px;
  color: #60a5fa;
  font-weight: 600;
}

.file-reading-bar {
  height: 3px;
  background: rgba(255,255,255,0.08);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 8px;
}

.file-reading-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  border-radius: 2px;
  transition: width 0.4s ease;
}

.file-reading-step {
  font-size: 11px;
  color: rgba(255,255,255,0.45);
  margin-bottom: 10px;
  min-height: 18px;
}

.vu-step-inline {
  display: flex;
  align-items: center;
  color: rgba(255,255,255,0.6);
}

.file-reading-files {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 8px;
}

.file-reading-item {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 5px 8px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 5px;
  font-size: 12px;
  color: rgba(255,255,255,0.4);
  transition: all 0.3s;
}

.file-reading-item.reading {
  color: #60a5fa;
  border-color: rgba(59,130,246,0.2);
  background: rgba(59,130,246,0.06);
}

.file-reading-item.done {
  color: #34d399;
  border-color: rgba(52,211,153,0.15);
}

.file-reading-item-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.file-reading-item-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-reading-item-status {
  flex-shrink: 0;
  font-size: 10px;
  opacity: 0.7;
}

.file-reading-result {
  padding: 6px 8px;
  background: rgba(52,211,153,0.06);
  border: 1px solid rgba(52,211,153,0.12);
  border-radius: 5px;
}

.file-reading-result-text {
  font-size: 11px;
  color: rgba(255,255,255,0.55);
  line-height: 1.5;
  white-space: pre-line;
}

/* 淡入淡出动画 */
.vu-fade-enter-active {
  transition: opacity 0.35s ease;
}

.vu-fade-leave-active {
  transition: opacity 0.3s ease;
}

.vu-fade-enter-from {
  opacity: 0;
  transform: translateY(4px);
}

.vu-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* File Reading Item Wrap (per-file with inline result) */
.file-reading-item-wrap {
  display: flex;
  flex-direction: column;
}

.file-reading-item-wrap .fr-result-card {
  margin-top: 4px;
  margin-left: 28px;
  max-width: calc(100% - 28px);
}

.fr-result-card {
  padding: 8px 10px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 6px;
  transition: border-color 0.3s;
}

.fr-result-card:hover {
  border-color: rgba(255,255,255,0.12);
}

.fr-result-card.file-type-video {
  border-left: 3px solid #a78bfa;
}
.fr-result-card.file-type-audio {
  border-left: 3px solid #f472b6;
}
.fr-result-card.file-type-image {
  border-left: 3px solid #34d399;
}
.fr-result-card.file-type-pdf {
  border-left: 3px solid #60a5fa;
}
.fr-result-card.file-type-word,
.fr-result-card.file-type-text {
  border-left: 3px solid #fbbf24;
}
.fr-result-card.file-type-ppt {
  border-left: 3px solid #fb923c;
}
.fr-result-card.file-type-excel {
  border-left: 3px solid #4ade80;
}

.fr-result-header {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-bottom: 4px;
}

.fr-result-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  color: rgba(255,255,255,0.5);
}

.fr-result-name {
  flex: 1;
  font-size: 12px;
  font-weight: 500;
  color: rgba(255,255,255,0.75);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.fr-result-summary {
  font-size: 11px;
  color: rgba(255,255,255,0.45);
  line-height: 1.5;
}

/* ============================================
   Message Attachments
   ============================================ */
.msg-attachments {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.msg-att-card {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(0,0,0,0.04);
  border: 1px solid rgba(0,0,0,0.1);
  border-radius: 8px;
  max-width: 280px;
  transition: background 0.2s;
}

.msg-att-card:hover {
  background: rgba(0,0,0,0.08);
}

.msg-att-icon {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.06);
}

.msg-att-card.file-type-pdf .msg-att-icon { background: rgba(239,68,68,0.15); color: #ef4444; }
.msg-att-card.file-type-word .msg-att-icon { background: rgba(59,130,246,0.15); color: #3b82f6; }
.msg-att-card.file-type-ppt .msg-att-icon { background: rgba(249,115,22,0.15); color: #f97316; }
.msg-att-card.file-type-excel .msg-att-icon { background: rgba(34,197,94,0.15); color: #22c55e; }
.msg-att-card.file-type-text .msg-att-icon { background: rgba(156,163,175,0.15); color: #9ca3af; }
.msg-att-card.file-type-image .msg-att-icon { background: rgba(168,85,247,0.15); color: #a855f7; }
.msg-att-card.file-type-video .msg-att-icon { background: rgba(236,72,153,0.15); color: #ec4899; }
.msg-att-card.file-type-audio .msg-att-icon { background: rgba(20,184,166,0.15); color: #14b8a6; }

.msg-att-name {
  font-size: 13px;
  color: #374151;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.msg-text-body {
  white-space: pre-wrap;
}

/* ============================================
   Upload File Tags (enhanced)
   ============================================ */
.file-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px 4px 4px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  max-width: 220px;
}

.file-tag-icon {
  flex-shrink: 0;
  width: 26px;
  height: 26px;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.08);
  color: rgba(255,255,255,0.6);
}

.file-tag-icon.file-type-pdf { background: rgba(239,68,68,0.15); color: #ef4444; }
.file-tag-icon.file-type-word { background: rgba(59,130,246,0.15); color: #3b82f6; }
.file-tag-icon.file-type-ppt { background: rgba(249,115,22,0.15); color: #f97316; }
.file-tag-icon.file-type-excel { background: rgba(34,197,94,0.15); color: #22c55e; }
.file-tag-icon.file-type-text { background: rgba(156,163,175,0.15); color: #9ca3af; }
.file-tag-icon.file-type-image { background: rgba(168,85,247,0.15); color: #a855f7; }
.file-tag-icon.file-type-video { background: rgba(236,72,153,0.15); color: #ec4899; }
.file-tag-icon.file-type-audio { background: rgba(20,184,166,0.15); color: #14b8a6; }

.file-tag-name {
  font-size: 12px;
  color: rgba(255,255,255,0.7);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ============================================
   PPT Progress Overlay
   ============================================ */
.ppt-progress-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.progress-card {
  width: 500px;
  padding: 32px;
  background: rgba(20, 20, 22, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
}

.progress-card h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.interfaces-progress {
  background: #000;
  position: relative;
  height: 8px;
  width: 100%;
  overflow: hidden;
  border-radius: 999px;
  margin-bottom: 10px;
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.interfaces-progress-indicator {
  background: #fff;
  height: 100%;
  width: 100%;
  flex: 1;
  transition: transform 0.45s ease;
  border-radius: 999px;
}

.progress-headline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.progress-percent {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.85);
  font-weight: 600;
}

.progress-text {
  margin-top: 0;
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
  text-align: right;
}

.plan-card {
  margin-top: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  padding: 12px;
}

.plan-title {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.62);
  margin-bottom: 8px;
  text-align: left;
}

.plan-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.plan-item {
  display: flex;
  align-items: center;
  gap: 10px;
  border-radius: 8px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.01);
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.plan-item.status-completed {
  border-color: rgba(52, 211, 153, 0.28);
}

.plan-item.status-in-progress {
  border-color: rgba(59, 130, 246, 0.28);
}

.plan-icon {
  width: 18px;
  height: 18px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.6);
}

.plan-item.status-completed .plan-icon {
  color: #22c55e;
}

.plan-item.status-in-progress .plan-icon {
  color: #3b82f6;
}

.plan-content {
  flex: 1;
  min-width: 0;
  text-align: left;
}

.plan-item-title {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.88);
  line-height: 1.35;
}

.plan-item-desc {
  margin-top: 2px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.45);
  line-height: 1.35;
}

.plan-badge {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  padding: 2px 8px;
  white-space: nowrap;
}

.progress-log-box {
  margin-top: 10px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.015);
}

.progress-log-list {
  max-height: 120px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.progress-log-item {
  display: flex;
  gap: 8px;
  align-items: baseline;
  font-size: 12px;
}

.log-progress {
  color: rgba(255, 255, 255, 0.92);
  min-width: 28px;
  text-align: right;
  font-weight: 600;
}

.log-message {
  color: rgba(255, 255, 255, 0.58);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.outline-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.generating-slides {
  margin-top: 20px;
  text-align: left;
}

.generating-slides h4 {
  margin: 0 0 12px 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.slides-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
  max-height: 300px;
  overflow-y: auto;
}

.slide-preview {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  padding: 10px;
  transition: all 0.3s ease;
  animation: slideAppear 0.5s ease-out;
}

@keyframes slideAppear {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.slide-preview:hover {
  border-color: rgba(139, 92, 246, 0.3);
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.1);
}

.slide-number {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 4px;
}

.slide-title {
  font-size: 12px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.slide-status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #34d399;
  font-weight: 500;
}

/* ============================================
   Outline & PPT Preview Cards
   ============================================ */
.outline-preview {
  margin-top: 12px;
  width: 100%;
}

.modern-msg-row.is-ai .outline-preview,
.modern-msg-row.is-ai .ppt-preview-card {
  margin-left: 42px;
  width: calc(100% - 42px);
}

.outline-preview .el-row {
  min-height: 500px;
}

.outline-preview .el-card {
  height: 100%;
}

.outline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ppt-preview-card {
  margin-top: 12px;
}

.ppt-card-modern {
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.015));
  overflow: hidden;
}

.ppt-card-head {
  padding: 12px 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.ppt-card-title-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ppt-card-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #34d399;
  box-shadow: 0 0 0 4px rgba(52, 211, 153, 0.15);
}

.ppt-card-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.92);
}

.ppt-card-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 999px;
  color: #34d399;
  border: 1px solid rgba(52, 211, 153, 0.35);
  background: rgba(52, 211, 153, 0.1);
}

.ppt-card-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.ppt-card-body {
  padding: 14px;
}

.ppt-card-desc {
  margin: 0 0 12px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.62);
}

.ppt-card-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(0, 1fr));
  gap: 8px;
}

.ppt-card-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.82);
  font-size: 11px;
  font-weight: 500;
  line-height: 1;
  padding: 8px 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ppt-card-btn :deep(svg) {
  width: 11px;
  height: 11px;
}

.ppt-card-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.ppt-card-btn.primary {
  border-color: rgba(139, 92, 246, 0.4);
  background: rgba(139, 92, 246, 0.18);
  color: #e9ddff;
}

.ppt-card-btn.primary:hover {
  border-color: rgba(139, 92, 246, 0.7);
  background: rgba(139, 92, 246, 0.3);
}

.ppt-card-btn.lesson-btn {
  border-color: rgba(59, 130, 246, 0.4);
  background: rgba(59, 130, 246, 0.18);
  color: #bfdbfe;
}

.ppt-card-btn.lesson-btn:hover {
  border-color: rgba(59, 130, 246, 0.7);
  background: rgba(59, 130, 246, 0.3);
}

.ppt-card-btn.lesson-btn.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ── 教案生成进度 ── */
.lesson-progress-card {
  margin-top: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
}

.lesson-progress-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.lesson-progress-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
}

.lesson-progress-percent {
  font-size: 13px;
  color: #60a5fa;
  font-weight: 600;
}

.lesson-progress-bar {
  height: 5px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 14px;
}

.lesson-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  border-radius: 3px;
  transition: width 0.5s ease;
}

.lesson-steps-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.lesson-step-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
  transition: color 0.3s;
}

.lesson-step-item.in-progress {
  color: #60a5fa;
}

.lesson-step-item.completed {
  color: #34d399;
}

.lesson-step-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.lesson-log-box {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 6px;
  padding: 10px;
  height: 160px;
  overflow-y: auto;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 11px;
}

.lesson-log-line {
  display: flex;
  gap: 6px;
  line-height: 1.6;
}

.lesson-log-time {
  color: rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
}

.lesson-log-msg {
  color: rgba(255, 255, 255, 0.6);
}

/* ── 教案完成卡片 ── */
.lesson-done-card {
  margin-top: 12px;
  padding: 16px;
  background: rgba(52, 211, 153, 0.06);
  border: 1px solid rgba(52, 211, 153, 0.15);
  border-radius: 10px;
}

.lesson-done-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.lesson-done-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #34d399;
}

.lesson-done-dot.success {
  box-shadow: 0 0 8px rgba(52, 211, 153, 0.5);
}

.lesson-done-title {
  font-size: 14px;
  font-weight: 600;
  color: #34d399;
}

.lesson-done-body {
  padding-left: 16px;
}

.lesson-done-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0 0 12px 0;
}

.lesson-done-actions {
  display: flex;
  gap: 8px;
}

.outline-content {
  max-height: 400px;
  overflow-y: auto;
}

.outline-content h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
}

.slide-item {
  margin-bottom: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
}

.slide-item .slide-number {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
  margin-bottom: 4px;
}

.slide-item .slide-title {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 8px;
}

.slide-points {
  margin: 0;
  padding-left: 20px;
}

.slide-points li {
  margin-bottom: 4px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
}

/* ============================================
   Template Dialog Styles
   ============================================ */
:deep(.el-dialog.template-dialog) {
  background: rgba(20, 20, 22, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.08);
  outline: none;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
}

:deep(.template-dialog .el-dialog__header) {
  background: rgba(20, 20, 22, 0.95);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-right: 0;
  padding-bottom: 16px;
}

:deep(.template-dialog .el-dialog__title) {
  color: rgba(255, 255, 255, 0.92);
}

:deep(.template-dialog .el-dialog__body) {
  background: rgba(20, 20, 22, 0.95);
  color: rgba(255, 255, 255, 0.85);
}

:deep(.template-dialog .el-dialog__footer) {
  background: rgba(20, 20, 22, 0.95);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 14px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
}

:deep(.template-dialog .el-tabs__item) {
  color: rgba(255, 255, 255, 0.62);
}

:deep(.template-dialog .el-tabs__item.is-active) {
  color: #fff;
}

:deep(.template-dialog .el-tabs__active-bar) {
  background-color: #fff;
}

:deep(.template-dialog .el-tabs__nav-wrap::after) {
  background-color: rgba(255, 255, 255, 0.12);
}

:deep(.el-dialog.outline-dialog) {
  background: rgba(20, 20, 22, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.08);
  outline: none;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
}

:deep(.outline-dialog .el-dialog__header) {
  background: rgba(20, 20, 22, 0.95);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-right: 0;
  padding-bottom: 16px;
}

:deep(.outline-dialog .el-dialog__title) {
  color: rgba(255, 255, 255, 0.92);
}

:deep(.outline-dialog .el-dialog__body) {
  background: rgba(20, 20, 22, 0.95);
  color: rgba(255, 255, 255, 0.85);
}

.outline-text {
  margin-top: 2px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.02);
  border-radius: 10px;
  padding: 10px 12px;
  color: rgba(255, 255, 255, 0.75);
  font-size: 12px;
  line-height: 1.55;
  white-space: pre-wrap;
}

.loading-templates {
  text-align: center;
  padding: 60px 20px;
}

.loading-templates .el-icon {
  font-size: 48px;
  color: #8b5cf6;
}

.loading-templates p {
  margin-top: 20px;
  color: rgba(255, 255, 255, 0.5);
}

.template-selector {
  max-height: 600px;
  overflow-y: auto;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  padding: 8px;
}

.template-item {
  border: 2px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  background: rgba(255, 255, 255, 0.02);
}

.template-item:hover {
  border-color: rgba(139, 92, 246, 0.3);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.1);
  transform: translateY(-2px);
}

.template-item.selected {
  border-color: #8b5cf6;
  background: rgba(139, 92, 246, 0.08);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
}

.template-thumbnail {
  position: relative;
  width: 100%;
  height: 150px;
  background: rgba(255, 255, 255, 0.02);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.template-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.template-thumbnail .placeholder {
  font-size: 48px;
  color: rgba(255, 255, 255, 0.1);
}

.template-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
}

.template-name {
  padding: 8px 12px 4px;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.template-category {
  padding: 4px 12px 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-templates {
  grid-column: 1 / -1;
  padding: 40px 20px;
  text-align: center;
}

.blank-generate-section {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px dashed rgba(255, 255, 255, 0.14);
}

.blank-generate-card {
  display: flex;
  align-items: center;
  gap: 12px;
  border: 2px dashed rgba(255, 255, 255, 0.16);
  border-radius: 10px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.25s ease;
  background: rgba(255, 255, 255, 0.02);
}

.blank-generate-card:hover {
  border-color: rgba(255, 255, 255, 0.28);
  background: rgba(255, 255, 255, 0.04);
}

.blank-generate-card.selected {
  border-color: #8b5cf6;
  background: rgba(139, 92, 246, 0.08);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
}

.blank-generate-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.9);
  flex-shrink: 0;
}

.blank-generate-content {
  min-width: 0;
}

.blank-generate-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.blank-generate-desc {
  margin-top: 2px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.58);
}

/* Builtin Template Cards */
.builtin-template-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
  padding: 8px;
}

.builtin-template-card {
  position: relative;
  border: 2px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
  background: rgba(255, 255, 255, 0.02);
  isolation: isolate;
  overflow: hidden;
}

.builtin-card-mask {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(0, 0, 0, 0.22) 0%, rgba(0, 0, 0, 0.72) 100%),
    linear-gradient(90deg, rgba(0, 0, 0, 0.28) 0%, rgba(0, 0, 0, 0.18) 100%);
  z-index: 0;
  pointer-events: none;
}

.builtin-template-card > *:not(.builtin-card-mask) {
  position: relative;
  z-index: 1;
}

.builtin-template-card:hover {
  border-color: rgba(139, 92, 246, 0.3);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.1);
  transform: translateY(-2px);
}

.builtin-template-card.selected {
  border-color: #8b5cf6;
  background: rgba(139, 92, 246, 0.08);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
}

.builtin-card-header {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
}

.builtin-name {
  font-size: 15px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
}

.builtin-name-en {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
}

.builtin-card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 8px;
}

.builtin-tag {
  font-size: 11px;
}

.builtin-card-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
  line-height: 1.5;
}

/* ============================================
   Collab Split Layout
   ============================================ */
.chat-main-area.collab-split {
  flex-direction: row;
}

.chat-conversation-side {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.chat-conversation-side.collab-left {
  flex: 0 0 62%;
  max-width: 62%;
  border-right: 1px solid rgba(167, 139, 250, 0.15);
}

.collab-left .modern-msg-row.is-user {
  justify-content: flex-start;
}

.collab-left .modern-msg-row.is-user .modern-msg-inner.reverse {
  flex-direction: row;
}

.collab-left .modern-msg-row.is-user .modern-msg-content-wrap {
  align-items: flex-start;
}

.collab-right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(167, 139, 250, 0.03);
  min-width: 0;
}

.collab-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid rgba(167, 139, 250, 0.12);
  flex-shrink: 0;
}

.collab-panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #f3f4f6;
}

.collab-panel-status {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 999px;
  color: #a78bfa;
  background: rgba(167, 139, 250, 0.1);
  border: 1px solid rgba(167, 139, 250, 0.2);
}

.collab-panel-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.collab-msg-row {
  margin-bottom: 12px;
}

.collab-msg-bubble {
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 13px;
  line-height: 1.6;
}

.collab-bubble-ai {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  margin-bottom: 8px;
}

.collab-bubble-user {
  background: rgba(167, 139, 250, 0.1);
  border: 1px solid rgba(167, 139, 250, 0.2);
}

.collab-msg-role {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: #9ca3af;
  margin-bottom: 4px;
}

.collab-msg-text {
  color: #d1d5db;
  white-space: pre-wrap;
  word-break: break-word;
}

.collab-panel-input {
  padding: 16px;
  border-top: 1px solid rgba(167, 139, 250, 0.12);
  flex-shrink: 0;
}

.collab-input-box {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.collab-textarea {
  flex: 1;
  background: #1a1a1a;
  border: 1px solid #2a2a2a;
  border-radius: 10px;
  padding: 10px 14px;
  color: #f3f4f6;
  font-size: 14px;
  line-height: 1.5;
  resize: none;
  outline: none;
  font-family: inherit;
  transition: border-color 0.2s;
}

.collab-textarea:focus {
  border-color: rgba(167, 139, 250, 0.4);
}

.collab-textarea::placeholder {
  color: #4b5563;
}

.collab-send-btn {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

.collab-send-btn.active {
  background: #a78bfa;
  color: #fff;
  border-color: #a78bfa;
}

.collab-send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ============================================
   Collab Mode - Owner left, Collaborator right
   ============================================ */
.modern-msg-row.is-owner-user {
  justify-content: flex-start;
}

.modern-msg-row.is-owner-user .modern-msg-inner.reverse {
  flex-direction: row;
}

.modern-msg-row.is-owner-user .modern-msg-content-wrap {
  align-items: flex-start;
}

.modern-msg-row.is-owner-user .modern-msg-meta {
  justify-content: flex-start;
}

.modern-msg-row.is-collab-user {
  justify-content: flex-end;
}

/* Collab user gets a distinct bubble color */
.modern-msg-row.is-collab-user .bubble-user {
  background: rgba(96, 165, 250, 0.15);
  border-color: rgba(96, 165, 250, 0.25);
  color: #111827;
}

</style>
