<script setup>
/**
 * FlyLineChart - 3D飞线图组件
 * 使用ECharts + echarts-gl绘制3D飞线效果
 * 展示场馆客流/物流的流动路径
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import 'echarts-gl'
import { CHART_COLORS } from '../utils/constants'

const props = defineProps({
  // 飞线数据: [{ from: [lng, lat], to: [lng, lat], value: number, name: string }]
  data: {
    type: Array,
    default: () => [],
  },
  // 散点数据: [{ name, value: [lng, lat, value] }]
  points: {
    type: Array,
    default: () => [],
  },
})

const chartRef = ref(null)
const webglSupported = ref(true)
const chartReady = ref(false)
let chartInstance = null

/**
 * 构建飞线数据 - 在两点间插值生成弧线
 */
function buildLineData(from, to) {
  const points = []
  const segments = 30
  for (let i = 0; i <= segments; i++) {
    const t = i / segments
    const x = from[0] + (to[0] - from[0]) * t
    const y = from[1] + (to[1] - from[1]) * t
    // 弧线高度 = 抛物线
    const z = Math.sin(t * Math.PI) * 2
    points.push([x, y, z])
  }
  return points
}

/**
 * 获取ECharts配置
 */
function getOption() {
  // 默认示例数据（当未传入数据时使用）
  const defaultLines = [
    { from: [0, -3], to: [0, 3], value: 80, name: 'A→VIP' },
    { from: [-3, 0], to: [3, 0], value: 60, name: 'B→C' },
    { from: [2, -2], to: [-2, 2], value: 45, name: 'D→A' },
    { from: [-1, -2], to: [1, 2], value: 70, name: 'B→VIP' },
    { from: [3, 1], to: [-3, -1], value: 55, name: 'C→A' },
  ]

  const defaultPoints = [
    { name: 'A区', value: [0, -3, 50] },
    { name: 'B区', value: [-3, 0, 40] },
    { name: 'C区', value: [3, 0, 60] },
    { name: 'D区', value: [2, -2, 35] },
    { name: 'VIP区', value: [0, 3, 80] },
  ]

  const lines = props.data.length > 0 ? props.data : defaultLines
  const pts = props.points.length > 0 ? props.points : defaultPoints

  // 构建飞线轨迹数据
  const lineData = lines.map((line) => ({
    coords: buildLineData(line.from, line.to),
  }))

  // 构建飞线效果数据（带动画）
  const effectData = lines.map((line) => ({
    coords: buildLineData(line.from, line.to),
    value: line.value,
  }))

  return {
    backgroundColor: 'transparent',
    tooltip: {
      show: true,
      backgroundColor: 'rgba(10, 14, 39, 0.85)',
      borderColor: 'rgba(0, 240, 255, 0.3)',
      textStyle: { color: '#e8eaf6', fontSize: 12 },
    },
    // 使用 grid3D 坐标系，不依赖 geo3D 地图数据
    grid3D: {
      show: false,
      boxWidth: 10,
      boxHeight: 6,
      boxDepth: 10,
      viewControl: {
        autoRotate: true,
        autoRotateSpeed: 3,
        distance: 18,
        alpha: 25,
        beta: 40,
        rotateSensitivity: 2,
        zoomSensitivity: 1,
      },
      light: {
        main: { intensity: 0.6, shadow: false },
        ambient: { intensity: 0.4 },
      },
      environment: 'transparent',
    },
    xAxis3D: { type: 'value', min: -5, max: 5, show: false },
    yAxis3D: { type: 'value', min: -5, max: 5, show: false },
    zAxis3D: { type: 'value', min: 0, max: 3, show: false },
    series: [
      // 飞线轨迹
      {
        type: 'line3D',
        coordinateSystem: 'cartesian3D',
        effect: {
          show: true,
          period: 4,
          trailWidth: 4,
          trailLength: 0.3,
          trailOpacity: 0.8,
          trailColor: CHART_COLORS.primary[0],
        },
        lineStyle: {
          width: 1,
          color: 'rgba(0, 240, 255, 0.2)',
          opacity: 0.3,
        },
        data: lineData.flatMap((d) => d.coords.map((c) => [c[0], c[1], c[2]])),
      },
      // 散点 - 区域标记
      {
        type: 'scatter3D',
        coordinateSystem: 'cartesian3D',
        symbolSize: 14,
        itemStyle: {
          color: CHART_COLORS.primary[0],
          opacity: 0.9,
          borderWidth: 1,
          borderColor: 'rgba(0, 240, 255, 0.6)',
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{b}',
          textStyle: {
            color: '#e8eaf6',
            fontSize: 11,
            backgroundColor: 'transparent',
          },
        },
        data: pts.map((p) => ({
          name: p.name,
          value: [p.value[0], p.value[1], p.value[2] ? p.value[2] / 20 : 1],
        })),
      },
    ],
  }
}

/**
 * 获取2D回退ECharts配置（WebGL不可用时使用）
 */
function get2DFallbackOption() {
  // 2D回退：使用直角坐标系散点+连线，不依赖GeoJSON地图数据
  const defaultCities = [
    { name: '北京', value: [116.46, 39.92, 80] },
    { name: '上海', value: [121.48, 31.22, 90] },
    { name: '广州', value: [113.23, 23.16, 60] },
    { name: '深圳', value: [114.07, 22.62, 55] },
    { name: '成都', value: [104.06, 30.67, 45] },
    { name: '武汉', value: [114.31, 30.52, 70] },
    { name: '杭州', value: [120.15, 30.28, 50] },
    { name: '南京', value: [118.80, 32.06, 40] },
    { name: '西安', value: [108.94, 34.26, 35] },
    { name: '重庆', value: [106.55, 29.56, 48] },
  ]
  const dest = { name: '国家体育场', value: [116.40, 39.99, 100] }

  const pts = props.points.length > 0 ? props.points : defaultCities
  const allPoints = [...pts, dest]

  // 飞线数据：所有城市到目的地
  const lineData = pts.map((p) => ({
    coords: [[p.value[0], p.value[1]], [dest.value[0], dest.value[1]]],
  }))

  return {
    backgroundColor: 'transparent',
    tooltip: {
      show: true,
      backgroundColor: 'rgba(10, 14, 39, 0.85)',
      borderColor: 'rgba(0, 240, 255, 0.3)',
      textStyle: { color: '#e8eaf6', fontSize: 12 },
    },
    xAxis: {
      type: 'value',
      min: 73, max: 136,
      show: false,
    },
    yAxis: {
      type: 'value',
      min: 18, max: 54,
      show: false,
    },
    series: [
      {
        type: 'lines',
        coordinateSystem: 'cartesian2d',
        zlevel: 2,
        effect: {
          show: true,
          period: 4,
          trailLength: 0.4,
          symbolSize: 4,
          trailColor: CHART_COLORS.primary[0],
          color: CHART_COLORS.primary[0],
        },
        lineStyle: {
          width: 1.5,
          color: 'rgba(0, 240, 255, 0.3)',
          curveness: 0.3,
        },
        data: lineData,
      },
      {
        type: 'effectScatter',
        coordinateSystem: 'cartesian2d',
        zlevel: 3,
        rippleEffect: { brushType: 'stroke', scale: 4, period: 4 },
        symbolSize: (val) => Math.max((val[2] || 50) / 8, 6),
        itemStyle: { color: CHART_COLORS.primary[0] },
        label: {
          show: true,
          position: 'top',
          formatter: '{b}',
          color: '#c0d8f0',
          fontSize: 10,
        },
        data: allPoints.map((p) => ({
          name: p.name,
          value: [p.value[0], p.value[1], p.value[2] || 50],
        })),
      },
    ],
  }
}

/**
 * 初始化图表
 */
function initChart() {
  if (!chartRef.value) return
  try {
    chartInstance = echarts.init(chartRef.value, null, {
      renderer: 'canvas',
    })
    chartInstance.setOption(getOption())
    chartReady.value = true
  } catch (e) {
    console.warn('WebGL不可用，尝试2D回退:', e)
    webglSupported.value = false
    if (chartInstance) {
      chartInstance.dispose()
      chartInstance = null
    }
    try {
      chartInstance = echarts.init(chartRef.value, null, {
        renderer: 'canvas',
      })
      chartInstance.setOption(get2DFallbackOption())
      chartReady.value = true
    } catch (e2) {
      console.warn('2D回退也失败:', e2)
      if (chartInstance) {
        chartInstance.dispose()
        chartInstance = null
      }
    }
  }
}

/**
 * 窗口大小变化时自适应
 */
function handleResize() {
  chartInstance?.resize()
}

// 监听数据变化
watch(
  () => [props.data, props.points],
  () => {
    if (chartInstance) {
      chartInstance.setOption(webglSupported.value ? getOption() : get2DFallbackOption())
    }
  },
  { deep: true }
)

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<template>
  <div v-if="chartReady || webglSupported" ref="chartRef" class="fly-line-chart" />
  <div v-else class="fly-line-chart fly-line-chart--fallback">
    飞线图需要浏览器图形支持
  </div>
</template>

<style scoped>
.fly-line-chart {
  width: 100%;
  height: 100%;
  min-height: 200px;
}
.fly-line-chart--fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(232, 234, 246, 0.5);
  font-size: 14px;
}
</style>
