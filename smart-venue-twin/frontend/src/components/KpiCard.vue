<script setup>
/**
 * KpiCard - KPI指标卡片组件
 * 展示关键指标数值，支持数字滚动动画
 */
import { computed } from 'vue'
import NumberRoll from './NumberRoll.vue'

const props = defineProps({
  // 指标标题
  label: {
    type: String,
    required: true,
  },
  // 指标数值
  value: {
    type: Number,
    required: true,
  },
  // 前缀
  prefix: {
    type: String,
    default: '',
  },
  // 后缀
  suffix: {
    type: String,
    default: '',
  },
  // 小数位数
  decimals: {
    type: Number,
    default: 0,
  },
  // 图标（emoji或文字）
  icon: {
    type: String,
    default: '',
  },
  // 变化值（正数上升，负数下降）
  change: {
    type: Number,
    default: 0,
  },
  // 变化值单位
  changeUnit: {
    type: String,
    default: '%',
  },
  // 主题色
  color: {
    type: String,
    default: 'var(--accent-cyan)',
  },
  // 字体大小
  fontSize: {
    type: String,
    default: '28px',
  },
})

// 变化趋势
const trend = computed(() => {
  if (props.change > 0) return 'up'
  if (props.change < 0) return 'down'
  return 'flat'
})

// 变化值颜色
const changeColor = computed(() => {
  if (props.change > 0) return 'var(--accent-teal)'
  if (props.change < 0) return 'var(--accent-red)'
  return 'var(--text-muted)'
})

// 变化值文本
const changeText = computed(() => {
  const sign = props.change > 0 ? '+' : ''
  return `${sign}${props.change}${props.changeUnit}`
})
</script>

<template>
  <div class="kpi-card">
    <!-- 图标 -->
    <div v-if="icon" class="kpi-card__icon" :style="{ color }">
      {{ icon }}
    </div>
    <!-- 数值区 -->
    <div class="kpi-card__value">
      <NumberRoll
        :value="value"
        :prefix="prefix"
        :suffix="suffix"
        :decimals="decimals"
        :font-size="fontSize"
        :color="color"
      />
    </div>
    <!-- 标签 -->
    <div class="kpi-card__label">{{ label }}</div>
    <!-- 变化趋势 -->
    <div v-if="change !== 0" class="kpi-card__change" :style="{ color: changeColor }">
      <span class="kpi-card__arrow">
        {{ trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→' }}
      </span>
      {{ changeText }}
    </div>
  </div>
</template>

<style scoped>
.kpi-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 8px;
  text-align: center;
  position: relative;
}

.kpi-card__icon {
  font-size: 20px;
  margin-bottom: 4px;
}

.kpi-card__value {
  line-height: 1.2;
  margin-bottom: 4px;
}

.kpi-card__label {
  font-size: 12px;
  color: var(--text-secondary);
  letter-spacing: 1px;
  white-space: nowrap;
}

.kpi-card__change {
  font-size: 11px;
  font-family: var(--font-mono);
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 2px;
}

.kpi-card__arrow {
  font-size: 12px;
}
</style>
