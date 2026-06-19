<script setup>
/**
 * ParticleScatterChart - 粒子散点图
 * 使用ECharts绘制散点图，展示多维度数据分布
 * 如：经济关联分析、设备故障分布等
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { CHART_COLORS } from '../utils/constants'

const props = defineProps({
  // 数据: [{ name, value: [x, y, size], category }]
  data: {
    type: Array,
    default: () => [],
  },
  // X轴标签
  xAxisLabel: {
    type: String,
    default: '',
  },
  // Y轴标签
  yAxisLabel: {
    type: String,
    default: '',
  },
})

const chartRef = ref(null)
let chartInstance = null

/**
 * 获取ECharts配置
 */
function getOption() {
  // 默认示例数据 - 经济关联分析
  const defaultData = [
    { name: '酒店业', value: [65, 80, 45], category: '住宿' },
    { name: '餐饮业', value: [70, 75, 55], category: '餐饮' },
    { name: '零售业', value: [55, 60, 35], category: '零售' },
    { name: '交通业', value: [80, 85, 50], category: '交通' },
    { name: '娱乐业', value: [45, 50, 30], category: '娱乐' },
    { name: '广告业', value: [90, 70, 40], category: '媒体' },
    { name: '物流业', value: [75, 65, 25], category: '物流' },
    { name: '旅游业', value: [85, 90, 60], category: '旅游' },
  ]

  const data = props.data.length > 0 ? props.data : defaultData

  // 按类别分组
  const categories = [...new Set(data.map((d) => d.category))]
  const seriesList = categories.map((cat, index) => {
    const catData = data.filter((d) => d.category === cat)
    return {
      name: cat,
      type: 'scatter',
      data: catData.map((d) => ({
        name: d.name,
        value: d.value,
      })),
      symbolSize: (val) => Math.max(val[2] * 0.8, 8),
      itemStyle: {
        color: new echarts.graphic.RadialGradient(0.5, 0.5, 0.8, [
          { offset: 0, color: CHART_COLORS.primary[index % CHART_COLORS.primary.length] },
          { offset: 1, color: CHART_COLORS.primary[index % CHART_COLORS.primary.length] + '44' },
        ]),
        shadowBlur: 10,
        shadowColor: CHART_COLORS.primary[index % CHART_COLORS.primary.length] + '66',
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 20,
          borderColor: '#fff',
          borderWidth: 1,
        },
        label: { show: true },
      },
      label: {
        show: false,
        position: 'top',
        formatter: '{b}',
        color: '#e8eaf6',
        fontSize: 11,
      },
    }
  })

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(10, 14, 39, 0.85)',
      borderColor: 'rgba(0, 240, 255, 0.3)',
      textStyle: { color: '#e8eaf6', fontSize: 12 },
      formatter: (params) => {
        return `<b>${params.name}</b><br/>
                ${props.xAxisLabel || 'X'}: ${params.value[0]}<br/>
                ${props.yAxisLabel || 'Y'}: ${params.value[1]}<br/>
                影响度: ${params.value[2]}`
      },
    },
    legend: {
      show: true,
      bottom: 0,
      textStyle: { color: '#9fa8da', fontSize: 11 },
      itemWidth: 10,
      itemHeight: 10,
    },
    grid: {
      left: '12%',
      right: '8%',
      top: '8%',
      bottom: '15%',
    },
    xAxis: {
      name: props.xAxisLabel,
      nameTextStyle: { color: '#9fa8da', fontSize: 11 },
      axisLine: { lineStyle: { color: 'rgba(0, 240, 255, 0.15)' } },
      axisLabel: { color: '#5c6bc0', fontSize: 10 },
      splitLine: { lineStyle: { color: 'rgba(0, 240, 255, 0.06)' } },
    },
    yAxis: {
      name: props.yAxisLabel,
      nameTextStyle: { color: '#9fa8da', fontSize: 11 },
      axisLine: { lineStyle: { color: 'rgba(0, 240, 255, 0.15)' } },
      axisLabel: { color: '#5c6bc0', fontSize: 10 },
      splitLine: { lineStyle: { color: 'rgba(0, 240, 255, 0.06)' } },
    },
    series: seriesList,
    animationDuration: 1500,
    animationEasing: 'elasticOut',
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
  <div ref="chartRef" class="particle-scatter-chart" />
</template>

<style scoped>
.particle-scatter-chart {
  width: 100%;
  height: 100%;
  min-height: 200px;
}
</style>
