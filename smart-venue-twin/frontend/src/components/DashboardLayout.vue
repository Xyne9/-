<script setup>
/**
 * DashboardLayout - 主大屏布局 v2.0
 * 霓虹科技风，扫描线、粒子背景、数据面板、雷达扫描
 */
import { ref, onMounted, onUnmounted } from 'vue'
import GlassPanel from './GlassPanel.vue'
import KpiCard from './KpiCard.vue'
import VenueModel3D from './VenueModel3D.vue'
import FlyLineChart from './FlyLineChart.vue'
import PolarRoseChart from './PolarRoseChart.vue'
import ParticleScatterChart from './ParticleScatterChart.vue'
import RevenueTrendChart from './RevenueTrendChart.vue'
import EquipmentStatusPanel from './EquipmentStatusPanel.vue'
import TrafficHeatmap from './TrafficHeatmap.vue'
import { useWebSocket } from '../composables/useWebSocket'
import { useNumberRoll } from '../composables/useNumberRoll'
import { formatDate } from '../utils/format'
import { isWebGLAvailable } from '../utils/webgl'

const { visitorCount, equipmentAlerts, revenueTick, trafficDensity, connected, connect } = useWebSocket()
const webglSupported = ref(false)

const currentTime = ref('')
const currentDate = ref('')
let clockTimer = null

const totalRevenue = useNumberRoll(0, { prefix: '¥', decimals: 2 })
const todayVisitors = useNumberRoll(0, { suffix: '人' })
const occupancyRate = useNumberRoll(0, { suffix: '%', decimals: 1 })
const alertCount = useNumberRoll(0, { suffix: '条' })

const eventData = ref([
  { time: '14:30', name: '开幕式彩排', venue: '主舞台', status: '进行中' },
  { time: '15:00', name: '嘉宾签到', venue: 'VIP大厅', status: '即将开始' },
  { time: '16:00', name: '主题演讲', venue: '会议中心', status: '待开始' },
  { time: '18:00', name: '晚宴', venue: '宴会厅', status: '待开始' },
])

const weatherData = ref({ temp: 26, humidity: 58, wind: '东南风 3级', status: '晴' })
const systemMetrics = ref([
  { label: '网络带宽', value: 68, unit: '%', color: 'var(--accent-cyan)' },
  { label: '存储容量', value: 42, unit: '%', color: 'var(--accent-blue)' },
  { label: 'CPU负载', value: 35, unit: '%', color: 'var(--accent-teal)' },
  { label: '内存使用', value: 57, unit: '%', color: 'var(--accent-purple)' },
])

const scrollMessages = ref([
  '🟢 系统运行正常 | 所有核心服务在线 | 数据刷新间隔: 3s',
  '📊 今日营收较昨日增长12.5% | 预测本月营收将突破历史新高',
  '⚠️ 电梯系统-1号梯检测到异常，已派工单 #WO-20240619-001',
  '🏟️ VIP区域上座率已达95%，建议启动分流预案 | 预计峰值客流14:30',
  '🌡️ 空调系统运行稳定，场馆温度23.5°C | 湿度52% | PM2.5: 18μg/m³',
  '📡 网络设备状态良好，带宽利用率68% | 在线设备: 1,247台',
  '🔒 安防系统-东区检测到预警信号 | 已自动调取CCTV-07画面',
  '💡 照明系统已切换至赛事模式 | 节能率: 32%',
  '🚗 停车场占用率: 78% | 剩余车位: 286个',
  '📱 APP在线用户: 12,847 | 今日新增: 326',
])

const scale = ref(1)
function updateScale() {
  scale.value = Math.min(window.innerWidth / 1920, window.innerHeight / 1080)
}

function updateClock() {
  const now = new Date()
  currentTime.value = formatDate(now, 'time')
  currentDate.value = formatDate(now, 'date')
}

onMounted(() => {
  webglSupported.value = isWebGLAvailable()
  connect()
  updateClock()
  clockTimer = setInterval(updateClock, 1000)
  updateScale()
  window.addEventListener('resize', updateScale)

  setTimeout(() => {
    totalRevenue.setValue(1285600.50)
    todayVisitors.setValue(18652)
    occupancyRate.setValue(87.3)
    alertCount.setValue(3)
  }, 500)

  requestAnimationFrame(() => {
    document.body.style.transform = 'translateZ(0)'
    requestAnimationFrame(() => { document.body.style.transform = '' })
  })
})

onUnmounted(() => {
  if (clockTimer) { clearInterval(clockTimer); clockTimer = null }
  window.removeEventListener('resize', updateScale)
})
</script>

<template>
  <div class="dashboard-wrapper">
    <!-- 背景层 -->
    <div class="bg-layer">
      <div class="bg-grid" />
      <div class="bg-glow bg-glow--left" />
      <div class="bg-glow bg-glow--right" />
    </div>

    <!-- 扫描线 -->
    <div class="scan-line" />

    <div class="screen-wrapper">
      <!-- ==================== 顶部标题栏 ==================== -->
      <header class="dashboard-header">
        <div class="header-left">
          <div class="header-logo">
            <span class="header-logo__icon">◆</span>
            <span class="header-logo__text">SMART TWIN</span>
          </div>
          <div class="header-divider" />
          <span class="header-subtitle">智慧场馆数字孪生平台</span>
        </div>

        <div class="header-center">
          <h1 class="header-title">
            <span class="header-title__glow" />
            智慧场馆与赛事运行数字孪生
          </h1>
          <div class="header-line" />
        </div>

        <div class="header-right">
          <div class="header-info">
            <span class="header-info__label">天气</span>
            <span class="header-info__value">{{ weatherData.status }} {{ weatherData.temp }}°C</span>
          </div>
          <div class="header-info">
            <span class="header-info__label">日期</span>
            <span class="header-info__value">{{ currentDate }}</span>
          </div>
          <div class="header-time">{{ currentTime }}</div>
          <div class="header-status" :class="connected ? 'online' : 'offline'">
            <span class="header-status__dot" />
            {{ connected ? '在线' : '离线' }}
          </div>
        </div>
      </header>

      <!-- ==================== 主内容区 ==================== -->
      <main class="dashboard-main">
        <!-- ===== 左侧面板 ===== -->
        <div class="left-panel">
          <GlassPanel title="核心指标" accent-color="var(--accent-cyan)" size="small">
            <div class="kpi-grid">
              <KpiCard label="今日营收" :value="totalRevenue.displayValue.value" prefix="¥" :decimals="2"
                color="var(--accent-cyan)" font-size="20px" :change="12.5" :max-value="2000000" />
              <KpiCard label="在场人数" :value="todayVisitors.displayValue.value" suffix="人"
                color="var(--accent-teal)" font-size="20px" :change="8.3" :max-value="30000" />
              <KpiCard label="上座率" :value="occupancyRate.displayValue.value" suffix="%" :decimals="1"
                color="var(--accent-blue)" font-size="20px" :change="-2.1" :max-value="100" />
              <KpiCard label="告警数" :value="alertCount.displayValue.value" suffix="条"
                color="var(--accent-orange)" font-size="20px" :change="-33" :max-value="20" />
            </div>
          </GlassPanel>

          <GlassPanel title="营收趋势" accent-color="var(--accent-teal)" class="flex-1">
            <RevenueTrendChart />
          </GlassPanel>

          <GlassPanel title="客流热力图" accent-color="var(--accent-blue)" class="flex-1">
            <TrafficHeatmap />
          </GlassPanel>
        </div>

        <!-- ===== 中央面板 ===== -->
        <div class="center-panel">
          <GlassPanel title="场馆数字孪生" accent-color="var(--accent-cyan)" :bordered="true" :glow="true" class="flex-2">
            <VenueModel3D v-if="webglSupported" />
            <div v-else class="webgl-fallback">
              <span class="webgl-fallback__icon">🏟️</span>
              <p class="webgl-fallback__text">3D模型需要WebGL支持</p>
            </div>
          </GlassPanel>

          <GlassPanel title="客流流向" accent-color="var(--accent-purple)" class="flex-1">
            <FlyLineChart v-if="webglSupported" />
            <div v-else class="webgl-fallback">
              <span class="webgl-fallback__icon">📊</span>
              <p class="webgl-fallback__text">飞线图需要WebGL支持</p>
            </div>
          </GlassPanel>
        </div>

        <!-- ===== 右侧面板 ===== -->
        <div class="right-panel">
          <GlassPanel title="多维分析" accent-color="var(--accent-purple)" class="flex-1">
            <PolarRoseChart />
          </GlassPanel>

          <GlassPanel title="经济关联" accent-color="var(--accent-pink)" class="flex-1">
            <ParticleScatterChart x-axis-label="关联度" y-axis-label="增长率" />
          </GlassPanel>

          <GlassPanel title="设备健康" accent-color="var(--accent-orange)" class="flex-1">
            <EquipmentStatusPanel />
          </GlassPanel>
        </div>
      </main>

      <!-- ==================== 底部状态栏 ==================== -->
      <footer class="dashboard-footer">
        <div class="footer-left">
          <span class="footer-metric" v-for="m in systemMetrics" :key="m.label">
            <span class="footer-metric__label">{{ m.label }}</span>
            <span class="footer-metric__bar">
              <span class="footer-metric__fill" :style="{ width: m.value + '%', background: m.color }" />
            </span>
            <span class="footer-metric__value" :style="{ color: m.color }">{{ m.value }}{{ m.unit }}</span>
          </span>
        </div>
        <div class="footer-center">
          <div class="scroll-bar">
            <div class="scroll-content">
              <span v-for="(msg, i) in scrollMessages" :key="i" class="scroll-message">{{ msg }}</span>
            </div>
          </div>
        </div>
        <div class="footer-right">
          <span class="footer-status">
            <span class="status-dot status-dot--green" /> 系统正常
          </span>
          <span class="footer-status">
            <span class="status-dot status-dot--cyan" /> 数据刷新: 3s
          </span>
        </div>
      </footer>
    </div>
  </div>
</template>

<style scoped>
/* ==================== 大屏容器 ==================== */
.dashboard-wrapper {
  width: 100vw; height: 100vh;
  position: relative;
  background: var(--bg-primary);
  overflow: hidden;
}

/* ==================== 背景层 ==================== */
.bg-layer {
  position: absolute; inset: 0;
  pointer-events: none; z-index: 0;
}

.bg-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px);
  background-size: 40px 40px;
}

.bg-glow {
  position: absolute;
  width: 600px; height: 600px;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.08;
}
.bg-glow--left { top: -200px; left: -200px; background: var(--accent-cyan); }
.bg-glow--right { bottom: -200px; right: -200px; background: var(--accent-purple); }

/* ==================== 扫描线 ==================== */
.scan-line {
  position: absolute; top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(0, 240, 255, 0.4), transparent);
  z-index: 0; pointer-events: none;
  animation: scanLine 4s linear infinite;
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.3), 0 0 40px rgba(0, 240, 255, 0.1);
}

/* ==================== 主布局 ==================== */
.screen-wrapper {
  width: 100vw; height: 100vh;
  position: relative; z-index: 1;
  display: flex; flex-direction: column;
}

/* ==================== 顶部标题栏 ==================== */
.dashboard-header {
  height: 68px;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px;
  position: relative; flex-shrink: 0;
  background: linear-gradient(180deg, rgba(0, 240, 255, 0.04) 0%, transparent 100%);
  border-bottom: 1px solid rgba(0, 240, 255, 0.08);
}

.header-left {
  display: flex; align-items: center; gap: 16px;
  min-width: 300px;
}

.header-logo {
  display: flex; align-items: center; gap: 8px;
}

.header-logo__icon {
  font-size: 18px; color: var(--accent-cyan);
  text-shadow: 0 0 12px var(--accent-cyan);
  animation: spin 6s linear infinite;
}

.header-logo__text {
  font-size: 12px; font-weight: 700;
  color: var(--accent-cyan); letter-spacing: 3px;
  font-family: var(--font-mono);
}

.header-divider {
  width: 1px; height: 20px;
  background: linear-gradient(180deg, transparent, rgba(0, 240, 255, 0.3), transparent);
}

.header-subtitle {
  font-size: 11px; color: var(--text-muted);
  letter-spacing: 2px;
}

.header-center {
  display: flex; flex-direction: column; align-items: center;
  flex: 1;
}

.header-title {
  font-size: 22px; font-weight: 700;
  color: var(--text-primary); letter-spacing: 8px;
  position: relative;
  text-shadow: 0 0 20px rgba(0, 240, 255, 0.2), 0 0 40px rgba(0, 240, 255, 0.1);
}

.header-title__glow {
  position: absolute; top: 0; left: -100%;
  width: 50%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.05), transparent);
  animation: titleSweep 4s ease-in-out infinite;
}

.header-line {
  width: 260px; height: 2px; margin-top: 6px;
  background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
  border-radius: 1px;
  box-shadow: 0 0 8px rgba(0, 240, 255, 0.3);
}

.header-right {
  display: flex; align-items: center; gap: 20px;
  min-width: 360px; justify-content: flex-end;
}

.header-info {
  display: flex; flex-direction: column; align-items: flex-end;
  gap: 2px;
}

.header-info__label {
  font-size: 10px; color: var(--text-muted); letter-spacing: 1px;
}

.header-info__value {
  font-size: 12px; color: var(--text-secondary);
  font-family: var(--font-mono);
}

.header-time {
  font-size: 18px; color: var(--accent-cyan);
  font-family: var(--font-mono); font-weight: 600;
  text-shadow: 0 0 10px rgba(0, 240, 255, 0.4);
}

.header-status {
  display: flex; align-items: center; gap: 6px;
  font-size: 11px; font-family: var(--font-mono);
  padding: 4px 10px; border-radius: 12px;
  border: 1px solid rgba(0, 240, 255, 0.15);
}
.header-status.online { color: var(--accent-teal); border-color: rgba(0, 229, 160, 0.3); }
.header-status.offline { color: var(--accent-red); border-color: rgba(255, 59, 92, 0.3); }

.header-status__dot {
  width: 6px; height: 6px; border-radius: 50%;
}
.online .header-status__dot { background: var(--accent-teal); box-shadow: 0 0 6px var(--accent-teal); }
.offline .header-status__dot { background: var(--accent-red); box-shadow: 0 0 6px var(--accent-red); }

/* ==================== 主内容区 ==================== */
.dashboard-main {
  flex: 1; display: flex; gap: 10px;
  padding: 10px; overflow: hidden;
}

.left-panel { width: 30%; display: flex; flex-direction: column; gap: 10px; }
.center-panel { width: 40%; display: flex; flex-direction: column; gap: 10px; }
.right-panel { width: 30%; display: flex; flex-direction: column; gap: 10px; }

.flex-1 { flex: 1; min-height: 0; }
.flex-2 { flex: 2; min-height: 0; }

.kpi-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2px;
}

/* ==================== WebGL降级 ==================== */
.webgl-fallback {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  height: 100%; min-height: 200px;
  color: #4a5580; gap: 8px;
}
.webgl-fallback__icon { font-size: 36px; opacity: 0.5; }
.webgl-fallback__text { font-size: 13px; margin: 0; }

/* ==================== 底部状态栏 ==================== */
.dashboard-footer {
  height: 40px;
  display: flex; align-items: center;
  padding: 0 16px; gap: 16px;
  flex-shrink: 0;
  border-top: 1px solid rgba(0, 240, 255, 0.08);
  background: linear-gradient(0deg, rgba(0, 240, 255, 0.03) 0%, transparent 100%);
}

.footer-left {
  display: flex; align-items: center; gap: 16px;
  flex-shrink: 0;
}

.footer-metric {
  display: flex; align-items: center; gap: 4px;
  font-size: 10px;
}

.footer-metric__label {
  color: var(--text-muted); white-space: nowrap;
}

.footer-metric__bar {
  width: 40px; height: 3px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 2px; overflow: hidden;
}

.footer-metric__fill {
  height: 100%; border-radius: 2px;
  transition: width 0.6s ease;
  box-shadow: 0 0 4px currentColor;
}

.footer-metric__value {
  font-family: var(--font-mono); font-size: 10px;
}

.footer-center {
  flex: 1; overflow: hidden;
}

.scroll-bar {
  width: 100%; overflow: hidden; position: relative;
}

.scroll-content {
  display: flex; gap: 60px; white-space: nowrap;
  animation: scrollLeft 50s linear infinite;
}

.scroll-message {
  font-size: 11px; color: var(--text-secondary);
  letter-spacing: 0.5px; flex-shrink: 0;
}

.footer-right {
  display: flex; align-items: center; gap: 12px;
  flex-shrink: 0;
}

.footer-status {
  display: flex; align-items: center; gap: 4px;
  font-size: 10px; color: var(--text-muted);
  font-family: var(--font-mono);
}

.status-dot {
  width: 5px; height: 5px; border-radius: 50%;
}
.status-dot--green { background: var(--accent-teal); box-shadow: 0 0 4px var(--accent-teal); }
.status-dot--cyan { background: var(--accent-cyan); box-shadow: 0 0 4px var(--accent-cyan); }

/* ==================== 动画 ==================== */
@keyframes scrollLeft {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
</style>