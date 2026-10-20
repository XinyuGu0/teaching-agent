import { defineStore } from 'pinia'
import api from '@/services/api'
import websocket from '@/services/websocket'

export const useConversationStore = defineStore('conversation', {
  state: () => ({
    conversations: [],
    currentConversation: null,
    messages: [],
    conversationState: 'INITIAL',
    currentOutline: null,
    currentPPT: null,  // 当前PPT数据
    pageStatus: null,  // PPT页面生成状态信息
    isGenerating: false,
    streamingMessage: null,  // For streaming AI responses
    isGeneratingOutline: false, // 是否正在生成大纲
    outlineProgress: 0, // 大纲生成进度 (0-100)
    outlineProgressMessage: '', // 大纲生成进度消息
    isGeneratingPPT: false,  // 是否正在生成PPT
    pptProgress: 0,  // PPT生成进度 (0-100)
    pptProgressMessage: '',  // PPT生成进度消息
    pptProgressLogs: [], // 进度日志（用于前端展示与排查）
    generatingSlides: []  // 正在生成的幻灯片列表
  }),

  actions: {
    async fetchConversations() {
      try {
        const response = await api.get('/conversations')
        this.conversations = response.data.conversations
      } catch (error) {
        console.error('Error fetching conversations:', error)
        throw error
      }
    },

    async createConversation(title = 'New Conversation') {
      try {
        const response = await api.post('/conversations', { title })
        this.currentConversation = response.data.conversation
        this.messages = []
        // 将新对话添加到列表顶部
        if (response.data.conversation) {
          const exists = this.conversations.some(c => c.id === response.data.conversation.id)
          if (!exists) {
            this.conversations.unshift(response.data.conversation)
          }
        }
        return this.currentConversation
      } catch (error) {
        console.error('Error creating conversation:', error)
        throw error
      }
    },

    async fetchConversation(conversationId) {
      try {
        const response = await api.get(`/conversations/${conversationId}`)
        this.currentConversation = response.data.conversation
        this.messages = response.data.conversation.messages || []
        // 同步对话状态
        if (response.data.conversation.state) {
          this.conversationState = response.data.conversation.state
        }
        return this.currentConversation
      } catch (error) {
        console.error('Error fetching conversation:', error)
        throw error
      }
    },

    async loadConversation(conversationId, userId) {
      try {
        const response = await api.get(`/conversations/${conversationId}`)
        this.currentConversation = response.data.conversation
        this.messages = response.data.conversation.messages || []

        // Join WebSocket room
        websocket.joinConversation(conversationId, userId)
      } catch (error) {
        console.error('Error loading conversation:', error)
        throw error
      }
    },

    sendMessage(content, userId) {
      if (!this.currentConversation) {
        console.error('No active conversation')
        return
      }

      this.isGenerating = true
      websocket.sendMessage(this.currentConversation.id, userId, content)
    },

    generateOutline(topic, requirements, userId) {
      if (!this.currentConversation) {
        console.error('No active conversation')
        return
      }

      this.isGenerating = true
      this.startOutlineGeneration()
      websocket.generateOutline(
        this.currentConversation.id,
        userId,
        topic,
        requirements
      )
    },

    setMessages(messages) {
      this.messages = messages
    },

    addMessage(message) {
      // If there's a streaming message, replace it with the final message
      if (this.streamingMessage) {
        const index = this.messages.findIndex(m => m.id === this.streamingMessage.id)
        if (index !== -1) {
          this.messages[index] = message
        } else {
          this.messages.push(message)
        }
        this.streamingMessage = null
      } else {
        this.messages.push(message)
      }
      this.isGenerating = false
    },

    addUserMessage(message) {
      // 去重：相同 id 直接跳过
      if (this.messages.some(m => m.id === message.id)) return
      // 去重：如果已有乐观消息（内容相同的 user 消息），用真实消息替换它
      const optimisticIdx = this.messages.findIndex(
        m => m.role === 'user' && m.id.startsWith('optimistic-') && m.content === message.content
      )
      if (optimisticIdx !== -1) {
        this.messages[optimisticIdx] = message
        return
      }
      this.messages.push(message)
    },

    startStreaming() {
      this.isGenerating = true
      this.streamingMessage = null
    },

    finishStreaming() {
      this.isGenerating = false
      this.streamingMessage = null
    },

    // Used when server streams an assistant message (via message_chunk) but sends meta_data only at the end.
    finalizeStreamingMessage(meta_data = {}) {
      if (!this.streamingMessage) return

      this.streamingMessage.meta_data = meta_data || {}
      this.streamingMessage.isStreaming = false

      this.isGenerating = false
      this.streamingMessage = null
    },

    appendToStreamingMessage(content) {
      if (!this.streamingMessage) {
        this.streamingMessage = {
          id: 'streaming-' + Date.now(),
          role: 'assistant',
          content: content,
          thinkingContent: '',
          searchResults: [],
          created_at: new Date().toISOString(),
          isStreaming: true
        }
        this.messages.push(this.streamingMessage)
      } else {
        const idx = this.messages.findIndex(m => m.id === this.streamingMessage.id)
        if (idx !== -1) {
          this.messages[idx] = { ...this.messages[idx], content: this.messages[idx].content + content }
          this.streamingMessage = this.messages[idx]
        }
      }
    },

    appendToStreamingThinking(content) {
      if (!this.streamingMessage) {
        // 思考内容先到，正文还没有
        this.streamingMessage = {
          id: 'streaming-' + Date.now(),
          role: 'assistant',
          content: '',
          thinkingContent: content,
          searchResults: [],
          created_at: new Date().toISOString(),
          isStreaming: true
        }
        this.messages.push(this.streamingMessage)
      } else {
        const idx = this.messages.findIndex(m => m.id === this.streamingMessage.id)
        if (idx !== -1) {
          this.messages[idx] = { ...this.messages[idx], thinkingContent: (this.messages[idx].thinkingContent || '') + content }
          this.streamingMessage = this.messages[idx]
        }
      }
    },

    setSearchResults(results) {
      if (!this.streamingMessage) {
        this.streamingMessage = {
          id: 'streaming-' + Date.now(),
          role: 'assistant',
          content: '',
          thinkingContent: '',
          searchResults: results,
          created_at: new Date().toISOString(),
          isStreaming: true
        }
        this.messages.push(this.streamingMessage)
      } else {
        const idx = this.messages.findIndex(m => m.id === this.streamingMessage.id)
        if (idx !== -1) {
          this.messages[idx] = { ...this.messages[idx], searchResults: results }
          this.streamingMessage = this.messages[idx]
        }
      }
    },

    setOutline(outline) {
      this.currentOutline = outline
      this.conversationState = 'outline_generated'
      this.isGenerating = false
      this.finishOutlineGeneration()
    },

    updateConversationState(newState, requirements) {
      this.conversationState = newState
      if (this.currentConversation) {
        this.currentConversation.state = newState
        if (requirements) {
          this.currentConversation.requirements = requirements
        }
      }
    },

    setPPT(ppt) {
      this.currentPPT = ppt
      // 如果PPT数据中包含页面状态信息，单独存储
      if (ppt && ppt.page_status) {
        this.pageStatus = ppt.page_status
      }
    },

    startOutlineGeneration() {
      this.isGeneratingOutline = true
      this.outlineProgress = 0
      this.outlineProgressMessage = '开始生成大纲...'
    },

    updateOutlineProgress(progress, message) {
      this.isGeneratingOutline = true
      this.outlineProgress = Math.max(0, Math.min(100, Math.round(progress || 0)))
      this.outlineProgressMessage = message || '正在生成大纲...'
    },

    finishOutlineGeneration() {
      this.isGeneratingOutline = false
      this.outlineProgress = 100
      this.outlineProgressMessage = '大纲生成完成！'
    },

    failOutlineGeneration(message = '大纲生成失败') {
      this.isGeneratingOutline = false
      this.outlineProgress = 0
      this.outlineProgressMessage = message
      this.isGenerating = false
    },

    startPPTGeneration() {
      this.isGeneratingPPT = true
      this.pptProgress = 0
      this.pptProgressMessage = '开始生成PPT...'
      this.pptProgressLogs = [{ time: new Date().toISOString(), progress: 0, message: '开始生成PPT...' }]
      this.generatingSlides = []
    },

    updatePPTProgress(progress, message, slideNumber, slideData) {
      this.pptProgress = Math.round(progress)
      this.pptProgressMessage = message

      if (message) {
        this.pptProgressLogs.push({
          time: new Date().toISOString(),
          progress: Math.round(progress),
          message
        })
        if (this.pptProgressLogs.length > 50) {
          this.pptProgressLogs = this.pptProgressLogs.slice(-50)
        }
      }

      if (slideNumber && slideData) {
        // 更新或添加幻灯片
        const existingIndex = this.generatingSlides.findIndex(s => s.number === slideNumber)
        if (existingIndex !== -1) {
          this.generatingSlides[existingIndex] = {
            number: slideNumber,
            data: slideData,
            title: slideData.objects?.[0]?.text || `第${slideNumber}页`
          }
        } else {
          this.generatingSlides.push({
            number: slideNumber,
            data: slideData,
            title: slideData.objects?.[0]?.text || `第${slideNumber}页`
          })
        }
      }
    },

    finishPPTGeneration() {
      this.isGeneratingPPT = false
      this.pptProgress = 100
      this.pptProgressMessage = 'PPT生成完成！'
      this.pptProgressLogs.push({ time: new Date().toISOString(), progress: 100, message: 'PPT生成完成！' })
    },

    failPPTGeneration(message = 'PPT生成失败') {
      this.isGeneratingPPT = false
      this.pptProgress = 0
      this.pptProgressMessage = message
      this.pptProgressLogs.push({
        time: new Date().toISOString(),
        progress: 0,
        message
      })
    },

    updateSlide(data) {
      if (this.currentPPT && this.currentPPT.id === data.ppt_id) {
        const slides = [...this.currentPPT.slides]
        slides[data.slide_number] = data.slide
        this.currentPPT = {
          ...this.currentPPT,
          slides
        }
      }
    },

    clearCurrentConversation() {
      this.currentConversation = null
      this.messages = []
      this.currentOutline = null
      this.currentPPT = null
      this.conversationState = 'INITIAL'
      this.isGeneratingOutline = false
      this.outlineProgress = 0
      this.outlineProgressMessage = ''
    }
  }
})
