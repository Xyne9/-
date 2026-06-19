<script setup>
/**
 * DashboardLayout - 主大屏布局组件
 * 1920x1080优化的大屏仪表盘布局
 * 左面板(30%) | 中央3D模型(40%) | 右面板(30%)
 * 顶部标题栏 + 底部滚动状态栏
 */
import { ref, onMounted, onUnmounted } from 'vue'
import GlassPanel from './GlassPanel.vue'
import KpiCard from './KpiCard.vue'
import NumberRoll from './NumberRoll.vue'
import VenueModel3D from './VenueModel3D.vue'
import FlyLineChart from './FlyLineChart.vue'
import PolarRoseChart from './PolarRoseChart.vue'
import ParticleScatterChart from './ParticleScatterChart.vue'
import RevenueTrendChart from './RevenueTrendChart.vue'
import EquipmentStatusPanel from './EquipmentStatusPanel.vue'
import TrafficHeatmap from './TrafficHeatmap.vue'
import { useWebSocket } from '../composables/useWebSocket'
import { useGSAP } from '../composables/useGSAP'
import { useNumberRoll } from '../composables/useNumberRoll'
import { formatDate } from '../utils/format'
import { isWebGLAvailable } from '../utils/webgl'

// WebSocket实时数据
const { visitorCount, equipmentAlerts, revenueTick, trafficDensity, connected, connect } = useWebSocket()

// GSAP动画
const { staggerEntrance, chartEntrance, countUp } = useGSAP()

// WebGL支持检测
const webglSupported = ref(false)

// 实时时钟
const currentTime = ref('')
const currentDate = ref('')
let clockTimer = null

// KPI数据（使用数字滚动）
const totalRevenue = useNumberRoll(0, { prefix: '¥', decimals: 2 })
const todayVisitors = useNumberRoll(0, { suffix: '人' })
const occupancyRate = useNumberRoll(0, { suffix: '%', decimals: 1 })
const alertCount = useNumberRoll(0, { suffix: '条' })

// 底部滚动消息
const scrollMessages = ref([
  '🟢 系统运行正常 | 所有核心服务在线',
  '📊 今日营收较昨日增长12.5%',
  '⚠️ 电梯系统-1号梯检测到异常，已派工单',
  '🏟️ VIP区域上座率已达95%，建议启动分流预案',
  '🌡️ 空调系统运行稳定，场馆温度23.5°C',
  '📡 网络设备状态良好，带宽利用率68%',
  '🔒 安防系统-东区检测到预警信号',
  '💡 照明系统已切换至赛事模式',
])

// 模拟初始数据加载
onMounted(() => {
  // 检测WebGL支持（必须在任何WebGL组件渲染前执行）
  webglSupported.value = isWebGLAvailable()

  // 连接WebSocket
  connect()

  // 启动时钟
  updateClock()
  clockTimer = setInterval(updateClock, 1000)

  // 大屏自适应缩放
  updateScale()
  window.addEventListener('resize', updateScale)

  // 模拟KPI数据加载（后续由API替换）
  setTimeout(() => {
    totalRevenue.setValue(1285600.50)
    todayVisitors.setValue(18652)
    occupancyRate.setValue(87.3)
    alertCount.setValue(3)
  }, 500)

  // 入场动画（WebGL可用时启用以验证）
  if (webglSupported.value) {
    setTimeout(() => {
      staggerEntrance('.left-panel .glass-panel', { stagger: 0.2, delay: 0.3 })
      staggerEntrance('.right-panel .glass-panel', { stagger: 0.2, delay: 0.6 })
      chartEntrance('.center-panel', { delay: 0.4 })
    }, 100)
  }

  // 强制触发重绘，修复沙箱环境渲染异常
  requestAnimationFrame(() => {
    document.body.style.transform = 'translateZ(0)'
    requestAnimationFrame(() => {
      document.body.style.transform = ''
    })
  })
})

onUnmounted(() => {
  if (clockTimer) {
    clearInterval(clockTimer)
    clockTimer = null
  }
  window.removeEventListener('resize', updateScale)
})

/**
 * 更新时钟
 */
function updateClock() {
  const now = new Date()
  currentTime.value = formatDate(now, 'time')
  currentDate.value = formatDate(now, 'date')
}

/**
 * 大屏自适应缩放
 */
const scale = ref(1)
function updateScale() {
  const scaleX = window.innerWidth / 1920
  const scaleY = window.innerHeight / 1080
  scale.value = Math.min(scaleX, scaleY)
}
</script>

<template>
  <div class="dashboard-wrapper">
    <div class="screen-wrapper">
      <!-- ==================== 顶部标题栏 ==================== -->
      <header class="dashboard-header">
        <div class="header-left">
          <span class="header-decoration" />
          <span class="header-subtitle">SMART VENUE DIGITAL TWIN</span>
        </div>
        <div class="header-center">
          <h1 class="header-title">智慧场馆与赛事运行数字孪生</h1>
          <div class="header-line" />
        </div>
        <div class="header-right">
          <span class="header-date">{{ currentDate }}</span>
          <span class="header-time">{{ currentTime }}</span>
          <span class="header-status" :class="{ 'status-online': connected, 'status-offline': !connected }">
            {{ connected ? '● 在线' : '○ 离线' }}
          </span>
        </div>
      </header>

      <!-- ==================== 主内容区 ==================== -->
      <main class="dashboard-main">
        <!-- ===== 左侧面板 ===== -->
        <div class="left-panel">
          <!-- KPI指标卡片区 -->
          <GlassPanel title="核心指标" class="kpi-panel">
            <div class="kpi-grid">
              <KpiCard
                label="今日营收"
                :value="totalRevenue.displayValue.value"
                prefix="¥"
                :decimals="2"
                color="var(--accent-cyan)"
                font-size="22px"
                :change="12.5"
              />
              <KpiCard
                label="在场人数"
                :value="todayVisitors.displayValue.value"
                suffix="人"
                color="var(--accent-teal)"
                font-size="22px"
                :change="8.3"
              />
              <KpiCard
                label="上座率"
                :value="occupancyRate.displayValue.value"
                suffix="%"
                :decimals="1"
                color="var(--accent-blue)"
                font-size="22px"
                :change="-2.1"
              />
              <KpiCard
                label="告警数"
                :value="alertCount.displayValue.value"
                suffix="条"
                color="var(--accent-orange)"
                font-size="22px"
                :change="-33"
              />
            </div>
          </GlassPanel>

          <!-- 营收趋势图 -->
          <GlassPanel title="营收趋势" class="revenue-panel">
            <RevenueTrendChart />
          </GlassPanel>

          <!-- 客流热力图 -->
          <GlassPanel title="客流热力图" class="heatmap-panel">
            <TrafficHeatmap />
          </GlassPanel>
        </div>

        <!-- ===== 中央3D模型区 ===== -->
        <div class="center-panel">
          <GlassPanel title="场馆数字孪生" class="model-panel" :bordered="true" :glow="true">
            <VenueModel3D v-if="webglSupported" />
            <div v-else class="webgl-fallback">
              <span class="webgl-fallback__icon">🏟️</span>
              <p class="webgl-fallback__text">3D模型需要WebGL支持</p>
            </div>
          </GlassPanel>

          <!-- 中央底部飞线图 -->
          <GlassPanel title="客流流向" class="flyline-panel">
            <FlyLineChart v-if="webglSupported" />
            <div v-else class="webgl-fallback">
              <span class="webgl-fallback__icon">📊</span>
              <p class="webgl-fallback__text">飞线图需要WebGL支持</p>
            </div>
          </GlassPanel>
        </div>

        <!-- ===== 右侧面板 ===== -->
        <div class="right-panel">
          <!-- 极坐标玫瑰图 -->
          <GlassPanel title="多维分析" class="polar-panel">
            <PolarRoseChart />
          </GlassPanel>

          <!-- 经济关联散点图 -->
          <GlassPanel title="经济关联分析" class="scatter-panel">
            <ParticleScatterChart
              x-axis-label="关联度"
              y-axis-label="增长率"
            />
          </GlassPanel>

          <!-- 设备健康状态 -->
          <GlassPanel title="设备健康状态" class="equipment-panel">
            <EquipmentStatusPanel />
          </GlassPanel>
        </div>
      </main>

      <!-- ==================== 底部滚动状态栏 ==================== -->
      <footer class="dashboard-footer">
        <div class="scroll-bar">
          <div class="scroll-content">
            <span v-for="(msg, i) in scrollMessages" :key="i" class="scroll-message">
              {{ msg }}
            </span>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<style scoped>
/* 大屏容器 - 自适应缩放 */
.dashboard-wrapper {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0a0e27;
  overflow: hidden;
}

.screen-wrapper {
  width: 100vw;
  height: 100vh;
  transform-origin: left top;
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

/* ==================== 顶部标题栏 ==================== */
.dashboard-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: relative;
  flex-shrink: 0;
  background: linear-gradient(180deg, rgba(0, 240, 255, 0.05) 0%, transparent 100%);
}

/* 标题栏底部装饰线 */
.dashboard-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(0, 240, 255, 0.3),
    rgba(0, 240, 255, 0.5),
    rgba(0, 240, 255, 0.3),
    transparent
  );
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 280px;
}

.header-decoration {
  width: 8px;
  height: 8px;
  background: var(--accent-cyan);
  border-radius: 50%;
  box-shadow: 0 0 10px var(--accent-cyan);
  /* 呼吸动画在部分环境导致渲染异常，暂时禁用 */
  /* animation: breathe 2s ease-in-out infinite; */
}

.header-subtitle {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 3px;
  font-family: var(--font-mono);
}

.header-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.header-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 6px;
  text-shadow: 0 0 20px rgba(0, 240, 255, 0.3);
  position: relative;
}

.header-line {
  width: 200px;
  height: 2px;
  margin-top: 6px;
  background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
  border-radius: 1px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 280px;
  justify-content: flex-end;
}

.header-date {
  font-size: 12px;
  color: var(--text-secondary);
}

.header-time {
  font-size: 16px;
  color: var(--accent-cyan);
  font-family: var(--font-mono);
  font-weight: 600;
}

.header-status {
  font-size: 11px;
  font-family: var(--font-mono);
}

.status-online {
  color: var(--accent-teal);
}

.status-offline {
  color: var(--accent-red);
}

/* ==================== 主内容区 ==================== */
.dashboard-main {
  flex: 1;
  display: flex;
  gap: 12px;
  padding: 12px;
  overflow: hidden;
}

/* 左侧面板 */
.left-panel {
  width: 30%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 中央区域 */
.center-panel {
  width: 40%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 右侧面板 */
.right-panel {
  width: 30%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* KPI面板 */
.kpi-panel {
  flex-shrink: 0;
}

.kpi-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px;
}

/* 营收趋势面板 */
.revenue-panel {
  flex: 1;
  min-height: 0;
}

/* 热力图面板 */
.heatmap-panel {
  flex: 1;
  min-height: 0;
}

/* 3D模型面板 */
.model-panel {
  flex: 2;
  min-height: 0;
}

/* 飞线图面板 */
.flyline-panel {
  flex: 1;
  min-height: 0;
}

/* 极坐标面板 */
.polar-panel {
  flex: 1;
  min-height: 0;
}

/* 散点图面板 */
.scatter-panel {
  flex: 1;
  min-height: 0;
}

/* 设备状态面板 */
.equipment-panel {
  flex: 1;
  min-height: 0;
}

/* ==================== 底部滚动状态栏 ==================== */
.dashboard-footer {
  height: 36px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  position: relative;
  flex-shrink: 0;
  background: linear-gradient(0deg, rgba(0, 240, 255, 0.03) 0%, transparent 100%);
}

/* 顶部装饰线 */
.dashboard-footer::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(0, 240, 255, 0.2),
    rgba(0, 240, 255, 0.3),
    rgba(0, 240, 255, 0.2),
    transparent
  );
}

.scroll-bar {
  width: 100%;
  overflow: hidden;
  position: relative;
}

.scroll-content {
  display: flex;
  gap: 60px;
  white-space: nowrap;
  /* 滚动动画在部分环境导致渲染异常，暂时禁用 */
  /* animation: scrollLeft 60s linear infinite; */
}

.scroll-message {
  font-size: 12px;
  color: var(--text-secondary);
  letter-spacing: 0.5px;
  flex-shrink: 0;
}

/* 滚动动画 */
@keyframes scrollLeft {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}

/* WebGL不可用时的降级占位 */
.webgl-fallback {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 200px;
  color: #6b7394;
  gap: 8px;
}

.webgl-fallback__icon {
  font-size: 36px;
  opacity: 0.6;
}

.webgl-fallback__text {
  font-size: 13px;
  margin: 0;
}
</style>
