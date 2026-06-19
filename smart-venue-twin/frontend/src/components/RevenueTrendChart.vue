<script setup>
/**
 * RevenueTrendChart - 营收趋势图
 * 使用ECharts绘制面积折线图，展示营收随时间变化趋势
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { CHART_COLORS } from '../utils/constants'

const props = defineProps({
  // 时序数据: { dates: string[], series: [{ name: string, data: number[] }] }
  data: {
    type: Object,
    default: () => ({}),
  },
})

const chartRef = ref(null)
let chartInstance = null

/**
 * 获取ECharts配置
 */
function getOption() {
  // 默认示例数据
  const defaultData = {
    dates: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
    series: [
      { name: '门票收入', data: [320, 280, 350, 410, 380, 520, 680, 750, 620, 580, 450, 490] },
      { name: '餐饮收入', data: [150, 130, 180, 200, 190, 260, 340, 380, 310, 280, 220, 240] },
      { name: '周边消费', data: [80, 70, 95, 110, 100, 140, 180, 200, 165, 150, 120, 130] },
    ],
  }

  const chartData = props.data.dates ? props.data : defaultData

  // 构建series
  const seriesList = chartData.series.map((s, index) => {
    const color = CHART_COLORS.primary[index % CHART_COLORS.primary.length]
    return {
      name: s.name,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: {
        width: 2,
        color,
        shadowBlur: 8,
        shadowColor: color + '44',
      },
      itemStyle: {
        color,
        borderColor: '#0a0e27',
        borderWidth: 2,
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: color + '40' },
          { offset: 0.5, color: color + '15' },
          { offset: 1, color: color + '00' },
        ]),
      },
      emphasis: {
        focus: 'series',
        itemStyle: {
          shadowBlur: 10,
          shadowColor: color + '66',
        },
      },
      data: s.data,
    }
  })

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(10, 14, 39, 0.85)',
      borderColor: 'rgba(0, 240, 255, 0.3)',
      textStyle: { color: '#e8eaf6', fontSize: 12 },
      axisPointer: {
        type: 'cross',
        lineStyle: { color: 'rgba(0, 240, 255, 0.2)' },
        crossStyle: { color: 'rgba(0, 240, 255, 0.2)' },
      },
    },
    legend: {
      show: true,
      top: 0,
      right: 0,
      textStyle: { color: '#9fa8da', fontSize: 11 },
      itemWidth: 16,
      itemHeight: 8,
      itemGap: 12,
    },
    grid: {
      left: '8%',
      right: '4%',
      top: '14%',
      bottom: '8%',
    },
    xAxis: {
      type: 'category',
      data: chartData.dates,
      boundaryGap: false,
      axisLine: { lineStyle: { color: 'rgba(0, 240, 255, 0.15)' } },
      axisLabel: { color: '#5c6bc0', fontSize: 10 },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisLabel: {
        color: '#5c6bc0',
        fontSize: 10,
        formatter: (val) => val >= 1000 ? `${(val / 1000).toFixed(0)}K` : val,
      },
      splitLine: { lineStyle: { color: 'rgba(0, 240, 255, 0.06)' } },
    },
    series: seriesList,
    animationDuration: 1500,
    animationEasing: 'cubicInOut',
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
  <div ref="chartRef" class="revenue-trend-chart" />
</template>

<style scoped>
.revenue-trend-chart {
  width: 100%;
  height: 100%;
  min-height: 200px;
}
</style>
