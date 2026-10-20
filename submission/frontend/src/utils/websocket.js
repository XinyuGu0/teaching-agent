/**
 * WebSocket 通信封装
 * 提供自动重连、事件订阅、心跳保活机制
 */
const BASE_WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:5000'

export class ChatWebSocket {
  /**
   * @param {string} conversationId - 对话 ID
   * @param {string} userId - 用户 ID
   */
  constructor(conversationId, userId) {
    this.conversationId = conversationId
    this.userId = userId
    this.ws = null
    this.listeners = new Map()
    this.reconnectAttempts = 0
    this.maxReconnect = 5
    this.reconnectDelay = 2000
  }

  /** 建立 WebSocket 连接 */
  connect() {
    const url = `${BASE_WS_URL}/ws/chat/${this.conversationId}`
    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      console.log(`[WS] 已连接: ${this.conversationId}`)
      this.reconnectAttempts = 0
    }

    this.ws.onmessage = (event) => {
      try {
        const { event: evt, data } = JSON.parse(event.data)
        this._emit(evt, data)
      } catch (e) {
        console.error('[WS] 消息解析失败:', e)
      }
    }

    this.ws.onclose = () => {
      console.log('[WS] 连接关闭')
      this._tryReconnect()
    }

    this.ws.onerror = (err) => {
      console.error('[WS] 连接错误:', err)
    }
  }

  /**
   * 发送用户消息
   * @param {string} content - 消息内容
   */
  sendMessage(content) {
    this._send('send_message', { content, user_id: this.userId })
  }

  /** 触发大纲生成 */
  generateOutline() {
    this._send('generate_outline', { user_id: this.userId })
  }

  /** 触发 PPT 生成 */
  generatePpt(templateId) {
    this._send('generate_ppt', { user_id: this.userId, template_id: templateId })
  }

  /**
   * 注册事件监听
   * @param {string} event - 事件名称
   * @param {Function} callback - 回调函数
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  /** 断开连接 */
  disconnect() {
    this.reconnectAttempts = this.maxReconnect // 阻止自动重连
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.listeners.clear()
  }

  // ---- 私有方法 ----

  _send(event, data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ event, data }))
    }
  }

  _emit(event, data) {
    const handlers = this.listeners.get(event) || []
    handlers.forEach((fn) => fn(data))
  }

  _tryReconnect() {
    if (this.reconnectAttempts >= this.maxReconnect) return
    this.reconnectAttempts++
    const delay = this.reconnectDelay * this.reconnectAttempts
    console.log(`[WS] ${delay}ms 后尝试第${this.reconnectAttempts}次重连...`)
    setTimeout(() => this.connect(), delay)
  }
}