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
    geo3D: {
      map: '',
      boxDepth: 8,
      boxWidth: 8,
      environment: 'transparent',
      groundPlane: {
        show: false,
      },
      viewControl: {
        autoRotate: true,
        autoRotateSpeed: 3,
        distance: 12,
        alpha: 25,
        beta: 40,
        rotateSensitivity: 2,
        zoomSensitivity: 1,
      },
      light: {
        main: {
          intensity: 0.6,
          shadow: false,
        },
        ambient: {
          intensity: 0.4,
        },
      },
    },
    series: [
      // 飞线轨迹
      {
        type: 'lines3D',
        coordinateSystem: 'geo3D',
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
        data: lineData,
      },
      // 散点 - 区域标记
      {
        type: 'scatter3D',
        coordinateSystem: 'geo3D',
        symbolSize: 12,
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
        data: pts,
      },
    ],
  }
}

/**
 * 初始化图表
 */
function initChart() {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value, null, {
    renderer: 'canvas',
  })
  chartInstance.setOption(getOption())
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
      chartInstance.setOption(getOption())
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
  <div ref="chartRef" class="fly-line-chart" />
</template>

<style scoped>
.fly-line-chart {
  width: 100%;
  height: 100%;
  min-height: 200px;
}
</style>
