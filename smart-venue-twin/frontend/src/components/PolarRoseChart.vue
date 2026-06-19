<script setup>
/**
 * PolarRoseChart - 多维极坐标玫瑰图
 * 使用ECharts绘制极坐标玫瑰图，展示多维度数据对比
 * 如：各区域客流、各类型营收等多维分析
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { CHART_COLORS } from '../utils/constants'

const props = defineProps({
  // 数据: [{ name: string, value: number, category: string }]
  data: {
    type: Array,
    default: () => [],
  },
  // 维度名称列表
  categories: {
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
  // 默认示例数据
  const defaultData = [
    { name: 'A区', value: 85, category: '上座率' },
    { name: 'B区', value: 72, category: '上座率' },
    { name: 'C区', value: 68, category: '上座率' },
    { name: 'D区', value: 90, category: '上座率' },
    { name: 'VIP区', value: 95, category: '上座率' },
    { name: 'A区', value: 45, category: '满意度' },
    { name: 'B区', value: 60, category: '满意度' },
    { name: 'C区', value: 55, category: '满意度' },
    { name: 'D区', value: 70, category: '满意度' },
    { name: 'VIP区', value: 88, category: '满意度' },
    { name: 'A区', value: 30, category: '消费指数' },
    { name: 'B区', value: 40, category: '消费指数' },
    { name: 'C区', value: 35, category: '消费指数' },
    { name: 'D区', value: 50, category: '消费指数' },
    { name: 'VIP区', value: 92, category: '消费指数' },
  ]

  const cats = props.categories.length > 0
    ? props.categories
    : ['上座率', '满意度', '消费指数']
  const data = props.data.length > 0 ? props.data : defaultData

  // 按类别分组
  const seriesData = cats.map((cat, index) => {
    const catData = data.filter((d) => d.category === cat)
    return {
      type: 'bar',
      name: cat,
      coordinateSystem: 'polar',
      stack: 'total',
      data: catData.map((d) => d.value),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: CHART_COLORS.primary[index] },
          { offset: 1, color: CHART_COLORS.primary[index] + '66' },
        ]),
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 240, 255, 0.3)',
        },
      },
    }
  })

  // 区域名称
  const areaNames = [...new Set(data.map((d) => d.name))]

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(10, 14, 39, 0.85)',
      borderColor: 'rgba(0, 240, 255, 0.3)',
      textStyle: { color: '#e8eaf6', fontSize: 12 },
    },
    legend: {
      show: true,
      bottom: 0,
      textStyle: {
        color: '#9fa8da',
        fontSize: 11,
      },
      itemWidth: 12,
      itemHeight: 8,
      data: cats,
    },
    polar: {
      radius: ['10%', '75%'],
      center: ['50%', '48%'],
    },
    angleAxis: {
      type: 'category',
      data: areaNames,
      boundaryGap: false,
      axisLine: {
        lineStyle: { color: 'rgba(0, 240, 255, 0.15)' },
      },
      axisLabel: {
        color: '#9fa8da',
        fontSize: 10,
      },
      splitLine: {
        lineStyle: { color: 'rgba(0, 240, 255, 0.06)' },
      },
    },
    radiusAxis: {
      axisLine: {
        lineStyle: { color: 'rgba(0, 240, 255, 0.15)' },
      },
      axisLabel: {
        color: '#5c6bc0',
        fontSize: 10,
      },
      splitLine: {
        lineStyle: { color: 'rgba(0, 240, 255, 0.06)' },
      },
    },
    series: seriesData,
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
  () => [props.data, props.categories],
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
  <div ref="chartRef" class="polar-rose-chart" />
</template>

<style scoped>
.polar-rose-chart {
  width: 100%;
  height: 100%;
  min-height: 200px;
}
</style>
