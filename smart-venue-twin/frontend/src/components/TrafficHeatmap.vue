<script setup>
/**
 * TrafficHeatmap - 客流热力图
 * 使用ECharts绘制热力图，展示场馆各区域客流密度
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { CHART_COLORS, ZONES } from '../utils/constants'

const props = defineProps({
  // 热力数据: [{ zone: string, hour: number, value: number }]
  data: {
    type: Array,
    default: () => [],
  },
  // 时间段标签
  hours: {
    type: Array,
    default: () => [],
  },
})

const chartRef = ref(null)
let chartInstance = null

/**
 * 获取ECharts配置
 */
function getOption() {
  // 默认示例数据 - 各区域24小时客流
  const defaultHours = Array.from({ length: 24 }, (_, i) => `${String(i).padStart(2, '0')}:00`)
  const zoneNames = ZONES.map((z) => z.name)

  // 生成模拟热力数据
  const defaultData = []
  zoneNames.forEach((zone, zoneIdx) => {
    for (let hour = 0; hour < 24; hour++) {
      // 模拟客流分布：上午渐增，下午高峰，晚间下降
      let base = 0
      if (hour >= 9 && hour <= 12) base = 30 + hour * 3
      else if (hour >= 13 && hour <= 18) base = 60 + Math.sin((hour - 13) / 5 * Math.PI) * 30
      else if (hour >= 19 && hour <= 22) base = 50 - (hour - 19) * 10
      else base = 5 + Math.random() * 10

      // VIP区客流更高
      if (zone === 'VIP区') base *= 1.2

      defaultData.push([hour, zoneIdx, Math.round(Math.max(0, Math.min(100, base + (Math.random() - 0.5) * 15)))])
    }
  })

  const hours = props.hours.length > 0 ? props.hours : defaultHours
  const data = props.data.length > 0 ? props.data : defaultData

  return {
    backgroundColor: 'transparent',
    tooltip: {
      position: 'top',
      backgroundColor: 'rgba(10, 14, 39, 0.85)',
      borderColor: 'rgba(0, 240, 255, 0.3)',
      textStyle: { color: '#e8eaf6', fontSize: 12 },
      formatter: (params) => {
        return `${zoneNames[params.value[1]]} ${hours[params.value[0]]}<br/>客流密度: <b style="color:#00f0ff">${params.value[2]}</b>%`
      },
    },
    grid: {
      left: '12%',
      right: '6%',
      top: '4%',
      bottom: '12%',
    },
    xAxis: {
      type: 'category',
      data: hours,
      splitArea: { show: false },
      axisLine: { lineStyle: { color: 'rgba(0, 240, 255, 0.15)' } },
      axisLabel: {
        color: '#5c6bc0',
        fontSize: 9,
        interval: 2,
      },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'category',
      data: zoneNames,
      axisLine: { lineStyle: { color: 'rgba(0, 240, 255, 0.15)' } },
      axisLabel: { color: '#9fa8da', fontSize: 10 },
      axisTick: { show: false },
    },
    visualMap: {
      min: 0,
      max: 100,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: 0,
      inRange: {
        color: CHART_COLORS.heatmap,
      },
      textStyle: {
        color: '#5c6bc0',
        fontSize: 10,
      },
      itemWidth: 12,
      itemHeight: 80,
    },
    series: [
      {
        type: 'heatmap',
        data: data,
        label: {
          show: false,
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 240, 255, 0.5)',
          },
        },
        itemStyle: {
          borderColor: 'rgba(10, 14, 39, 0.8)',
          borderWidth: 2,
          borderRadius: 2,
        },
      },
    ],
    animationDuration: 1000,
    animationEasing: 'cubicOut',
  }
}

function initChart() {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption(getOption())
}

function handleResize() {
  chartInstance?.resize()
}

watch(
  () => props.data,
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
  <div ref="chartRef" class="traffic-heatmap" />
</template>

<style scoped>
.traffic-heatmap {
  width: 100%;
  height: 100%;
  min-height: 200px;
}
</style>
