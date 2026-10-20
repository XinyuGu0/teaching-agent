import { io } from 'socket.io-client'
import { useConversationStore } from '@/store/modules/conversation'
import { useAuthStore } from '@/store/modules/auth'

class WebSocketService {
  constructor() {
    this.socket = null
    this.connected = false
    this.handlersSetup = false  // 标记是否已设置处理器
  }

  connect() {
    return new Promise((resolve, reject) => {
      if (this.socket && this.connected) {
        resolve()
        return
      }

      const wsUrl = import.meta.env.VITE_WS_URL || 'http://localhost:5000'
      const authStore = useAuthStore()
      const token = authStore.accessToken

      this.socket = io(wsUrl, {
        auth: { token },
        transports: ['websocket', 'polling']
      })

      this.socket.on('connect', () => {
        console.log('WebSocket connected')
        this.connected = true
        resolve()
      })

      this.socket.on('disconnect', () => {
        console.log('WebSocket disconnected')
        this.connected = false
      })

      this.socket.on('connected', (data) => {
        console.log('Server confirmed connection:', data)
      })

      this.socket.on('error', (data) => {
        console.error('WebSocket error:', data.message)
        reject(new Error(data.message))
      })

      // 只设置一次消息处理器
      if (!this.handlersSetup) {
        this.setupMessageHandlers()
        this.handlersSetup = true
      }
    })
  }

  setupMessageHandlers() {
    const conversationStore = useConversationStore()

    this.socket.on('conversation_history', (data) => {
      conversationStore.setMessages(data.messages)
    })

    this.socket.on('message_received', (message) => {
      if (message.role === 'assistant') {
        conversationStore.addMessage(message)
        conversationStore.finishStreaming()
      } else if (message.role === 'user') {
        conversationStore.addUserMessage(message)
      }
    })

    this.socket.on('streaming_start', () => {
      conversationStore.startStreaming()
    })

    this.socket.on('message_chunk', (data) => {
      conversationStore.appendToStreamingMessage(data.content)
    })

    this.socket.on('thinking_chunk', (data) => {
      conversationStore.appendToStreamingThinking(data.content)
    })

    this.socket.on('outline_generated', (data) => {
      conversationStore.setOutline(data.outline)
      conversationStore.addMessage(data.message)
      conversationStore.finishOutlineGeneration()
    })

    // When server streams outline markdown via message_chunk, attach meta_data at the end.
    this.socket.on('outline_stream_complete', (data) => {
      conversationStore.finalizeStreamingMessage(data?.meta_data || {})
    })

    this.socket.on('outline_generation_start', () => {
      conversationStore.startOutlineGeneration()
    })

    this.socket.on('outline_generation_progress', (data) => {
      conversationStore.updateOutlineProgress(data.progress, data.message)
      if ((data.progress || 0) >= 100) {
        conversationStore.finishOutlineGeneration()
      }
    })

    this.socket.on('state_changed', (data) => {
      conversationStore.updateConversationState(data.new_state, data.requirements)
    })

    this.socket.on('ppt_generation_start', (data) => {
      // PPT generation started
      conversationStore.startPPTGeneration()
    })

    this.socket.on('ppt_generation_progress', (data) => {
      // PPT generation progress update with slide data
      conversationStore.updatePPTProgress(data.progress, data.message, data.slide_number, data.slide_data)
    })

    this.socket.on('ppt_generated', (data) => {
      conversationStore.setPPT(data.ppt)
      conversationStore.finishPPTGeneration()
    })

    this.socket.on('ppt_generation_failed', (data) => {
      conversationStore.failPPTGeneration(data?.message || 'PPT生成失败')
    })

    this.socket.on('slide_updated', (data) => {
      conversationStore.updateSlide(data)
    })
  }

  on(event, callback) {
    if (this.socket) {
      this.socket.on(event, callback)
    }
  }

  off(event, callback) {
    if (this.socket) {
      this.socket.off(event, callback)
    }
  }

  joinConversation(conversationId, userId) {
    if (!this.socket || !this.connected) {
      console.error('Socket not connected')
      return
    }

    this.socket.emit('join_conversation', {
      conversation_id: conversationId,
      user_id: userId
    })
  }

  sendMessage(conversationId, userId, content) {
    if (!this.socket || !this.connected) {
      console.error('Socket not connected')
      return
    }

    this.socket.emit('send_message', {
      conversation_id: conversationId,
      user_id: userId,
      content
    })
  }

  generateOutline(conversationId, userId, topic, requirements) {
    if (!this.socket || !this.connected) {
      console.error('Socket not connected')
      return
    }

    this.socket.emit('generate_outline', {
      conversation_id: conversationId,
      user_id: userId,
      topic,
      requirements
    })
  }

  generatePPT(conversationId, userId, outline, requirements, theme = 'modern', templateId = null) {
    if (!this.socket || !this.connected) {
      console.error('Socket not connected')
      return
    }

    this.socket.emit('generate_ppt', {
      conversation_id: conversationId,
      user_id: userId,
      outline,
      requirements,
      theme,
      template_id: templateId
    })
  }

  // Docmee API生成（方案二：实时流式生成PPT）
  generateApiPPT(conversationId, userId, outlineMarkdown, requirements = {}) {
    if (!this.socket || !this.connected) {
      console.error('Socket not connected')
      return
    }

    this.socket.emit('generate_api_ppt', {
      conversation_id: conversationId,
      user_id: userId,
      outline_markdown: outlineMarkdown,
      requirements
    })
  }

  updateSlide(pptId, slideNumber, updates) {
    if (!this.socket || !this.connected) {
      console.error('Socket not connected')
      return
    }

    this.socket.emit('update_slide', {
      ppt_id: pptId,
      slide_number: slideNumber,
      updates
    })
  }

  aiModifySlide(pptId, slideNumber, instruction) {
    if (!this.socket || !this.connected) {
      console.error('Socket not connected')
      return
    }

    this.socket.emit('ai_modify_slide', {
      ppt_id: pptId,
      slide_number: slideNumber,
      instruction
    })
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
      this.connected = false
    }
  }
}

export default new WebSocketService()
