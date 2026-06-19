/**
 * 常量定义 - 智慧场馆数字孪生
 * 包含区域定义、颜色方案、事件类型等
 */

// ========================================
// 场馆区域定义（用于3D模型定位和着色）
// ========================================
export const ZONES = [
  { id: 'A', name: 'A区', label: 'A区·普通席', color: '#00f0ff', position: { x: -3, y: 0, z: 2 } },
  { id: 'B', name: 'B区', label: 'B区·普通席', color: '#00d4aa', position: { x: -1, y: 0, z: 2 } },
  { id: 'C', name: 'C区', label: 'C区·普通席', color: '#4d7cff', position: { x: 1, y: 0, z: 2 } },
  { id: 'D', name: 'D区', label: 'D区·普通席', color: '#a855f7', position: { x: 3, y: 0, z: 2 } },
  { id: 'VIP', name: 'VIP区', label: 'VIP区·贵宾席', color: '#ffd700', position: { x: 0, y: 0, z: -1 } },
]

// ========================================
// 图表配色方案
// ========================================
export const CHART_COLORS = {
  // 主色调
  primary: ['#00f0ff', '#00d4aa', '#4d7cff', '#a855f7', '#ff8c00', '#ff6b9d', '#ffd700', '#ff4757'],
  // 渐变色对
  gradients: [
    ['#00f0ff', '#00d4aa'],
    ['#4d7cff', '#00f0ff'],
    ['#a855f7', '#4d7cff'],
    ['#ff8c00', '#ffd700'],
    ['#ff6b9d', '#a855f7'],
    ['#00d4aa', '#4d7cff'],
  ],
  // 热力图色阶
  heatmap: ['#0a0e27', '#0d2847', '#0e4d64', '#1a7a5a', '#2ecc71', '#ffd700', '#ff8c00', '#ff4757'],
  // 半透明版本（用于面积图等）
  alpha: [
    'rgba(0, 240, 255, 0.3)',
    'rgba(0, 212, 170, 0.3)',
    'rgba(77, 124, 255, 0.3)',
    'rgba(168, 85, 247, 0.3)',
    'rgba(255, 140, 0, 0.3)',
    'rgba(255, 107, 157, 0.3)',
  ],
}

// ========================================
// 事件类型定义
// ========================================
export const EVENT_TYPES = [
  { type: 'concert', label: '演唱会', color: '#ff6b9d', icon: '🎵' },
  { type: 'sports', label: '体育赛事', color: '#00f0ff', icon: '⚽' },
  { type: 'exhibition', label: '展览', color: '#a855f7', icon: '🎨' },
  { type: 'conference', label: '会议', color: '#4d7cff', icon: '🎤' },
  { type: 'performance', label: '演出', color: '#ffd700', icon: '🎭' },
  { type: 'other', label: '其他', color: '#00d4aa', icon: '📋' },
]

// ========================================
// 设备状态定义
// ========================================
export const EQUIPMENT_STATUS = {
  normal: { label: '正常', color: '#00d4aa', level: 'success' },
  warning: { label: '预警', color: '#ffd700', level: 'warning' },
  error: { label: '故障', color: '#ff4757', level: 'danger' },
  offline: { label: '离线', color: '#5c6bc0', level: 'info' },
  maintenance: { label: '维护中', color: '#4d7cff', level: 'primary' },
}

// ========================================
// 设备类型定义
// ========================================
export const EQUIPMENT_TYPES = [
  { type: 'hvac', label: '空调系统', icon: '❄️' },
  { type: 'lighting', label: '照明系统', icon: '💡' },
  { type: 'security', label: '安防系统', icon: '🔒' },
  { type: 'fire', label: '消防系统', icon: '🧯' },
  { type: 'elevator', label: '电梯系统', icon: '🛗' },
  { type: 'network', label: '网络设备', icon: '📡' },
  { type: 'power', label: '供电系统', icon: '⚡' },
  { type: 'water', label: '给排水系统', icon: '💧' },
]

// ========================================
// 客流密度等级
// ========================================
export const TRAFFIC_LEVELS = {
  low: { label: '稀疏', color: '#00d4aa', range: [0, 30] },
  medium: { label: '适中', color: '#ffd700', range: [30, 60] },
  high: { label: '拥挤', color: '#ff8c00', range: [60, 80] },
  critical: { label: '饱和', color: '#ff4757', range: [80, 100] },
}

// ========================================
// 大屏布局尺寸（1920x1080）
// ========================================
export const LAYOUT = {
  width: 1920,
  height: 1080,
  header: { height: 64 },
  footer: { height: 36 },
  left: { width: '30%' },
  center: { width: '40%' },
  right: { width: '30%' },
  gap: 12,
  padding: 12,
}

// ========================================
// WebSocket消息类型
// ========================================
export const WS_MESSAGE_TYPES = {
  VISITOR_COUNT: 'visitor_count',
  EQUIPMENT_ALERT: 'equipment_alert',
  REVENUE_TICK: 'revenue_tick',
  TRAFFIC_DENSITY: 'traffic_density',
  SYSTEM_STATUS: 'system_status',
}

// ========================================
// API路径
// ========================================
export const API_PATHS = {
  OVERVIEW: '/overview',
  REVENUE_TREND: '/revenue/trend',
  REVENUE_BY_TYPE: '/revenue/by-type',
  TRAFFIC_HEATMAP: '/traffic/heatmap',
  TRAFFIC_FLOW_LINES: '/traffic/flow-lines',
  EQUIPMENT_STATUS: '/equipment/status',
  EQUIPMENT_3D_MODEL: '/equipment/3d-model',
  ECONOMIC_CORRELATION: '/economic/correlation',
  HOTEL_PRICE: '/economic/hotel-price',
}
