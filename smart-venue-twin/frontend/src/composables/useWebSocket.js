/**
 * WebSocket组合式函数
 * 连接后端实时数据推送，支持自动重连
 */
import { ref, onUnmounted, readonly } from 'vue'
import { WS_MESSAGE_TYPES } from '../utils/constants'

// WebSocket连接URL - 使用相对路径，由Vite代理转发到后端
const WS_URL = `${location.protocol === 'https:' ? 'wss:' : 'ws:'}//${location.host}/ws/realtime`

// 重连配置
const RECONNECT_DELAY = 3000 // 重连延迟3秒
const MAX_RECONNECT_ATTEMPTS = 10 // 最大重连次数

export function useWebSocket() {
  // 响应式数据 - 实时指标
  const visitorCount = ref(0) // 当前在场人数
  const equipmentAlerts = ref([]) // 设备告警列表
  const revenueTick = ref(0) // 实时营收增量
  const trafficDensity = ref({}) // 各区域客流密度
  const connected = ref(false) // 连接状态

  let ws = null // WebSocket实例
  let reconnectAttempts = 0 // 当前重连次数
  let reconnectTimer = null // 重连定时器
  let intentionallyClosed = false // 是否主动关闭

  /**
   * 处理收到的消息
   */
  function handleMessage(event) {
    try {
      const data = JSON.parse(event.data)
      switch (data.type) {
        case WS_MESSAGE_TYPES.VISITOR_COUNT:
          visitorCount.value = data.value
          break
        case WS_MESSAGE_TYPES.EQUIPMENT_ALERT:
          // 新告警添加到列表头部，最多保留20条
          equipmentAlerts.value = [data.value, ...equipmentAlerts.value].slice(0, 20)
          break
        case WS_MESSAGE_TYPES.REVENUE_TICK:
          revenueTick.value = data.value
          break
        case WS_MESSAGE_TYPES.TRAFFIC_DENSITY:
          trafficDensity.value = data.value
          break
        case WS_MESSAGE_TYPES.SYSTEM_STATUS:
          // 系统状态消息，可扩展
          console.log('[WS] 系统状态:', data.value)
          break
        default:
          console.warn('[WS] 未知消息类型:', data.type)
      }
    } catch (err) {
      console.error('[WS] 消息解析失败:', err)
    }
  }

  /**
   * 连接WebSocket
   */
  function connect() {
    if (ws && (ws.readyState === WebSocket.CONNECTING || ws.readyState === WebSocket.OPEN)) {
      return
    }

    intentionallyClosed = false

    try {
      ws = new WebSocket(WS_URL)

      ws.onopen = () => {
        console.log('[WS] 连接成功')
        connected.value = true
        reconnectAttempts = 0 // 重置重连计数
      }

      ws.onmessage = handleMessage

      ws.onerror = (error) => {
        console.error('[WS] 连接错误:', error)
      }

      ws.onclose = (event) => {
        console.log('[WS] 连接关闭:', event.code, event.reason)
        connected.value = false

        // 非主动关闭时自动重连
        if (!intentionallyClosed && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttempts++
          console.log(`[WS] 将在${RECONNECT_DELAY / 1000}秒后重连 (第${reconnectAttempts}次)`)
          reconnectTimer = setTimeout(connect, RECONNECT_DELAY)
        }
      }
    } catch (err) {
      console.error('[WS] 创建连接失败:', err)
      connected.value = false
    }
  }

  /**
   * 主动断开连接
   */
  function disconnect() {
    intentionallyClosed = true
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    if (ws) {
      ws.close()
      ws = null
    }
    connected.value = false
  }

  /**
   * 发送消息
   * @param {object} data - 要发送的数据
   */
  function send(data) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data))
    } else {
      console.warn('[WS] 连接未就绪，无法发送消息')
    }
  }

  // 组件卸载时自动断开
  onUnmounted(() => {
    disconnect()
  })

  return {
    // 响应式数据（只读）
    visitorCount: readonly(visitorCount),
    equipmentAlerts: readonly(equipmentAlerts),
    revenueTick: readonly(revenueTick),
    trafficDensity: readonly(trafficDensity),
    connected: readonly(connected),
    // 方法
    connect,
    disconnect,
    send,
  }
}
