<script setup>
/**
 * KpiCard - KPI指标卡片 v2.0
 * 环形进度、脉冲光效、趋势指示
 */
import { computed } from 'vue'
import NumberRoll from './NumberRoll.vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: Number, required: true },
  prefix: { type: String, default: '' },
  suffix: { type: String, default: '' },
  decimals: { type: Number, default: 0 },
  icon: { type: String, default: '' },
  change: { type: Number, default: 0 },
  changeUnit: { type: String, default: '%' },
  color: { type: String, default: 'var(--accent-cyan)' },
  fontSize: { type: String, default: '24px' },
  maxValue: { type: Number, default: 0 },
})

const trend = computed(() => props.change > 0 ? 'up' : props.change < 0 ? 'down' : 'flat')
const changeColor = computed(() => props.change > 0 ? 'var(--accent-teal)' : props.change < 0 ? 'var(--accent-red)' : 'var(--text-muted)')
const changeText = computed(() => {
  const sign = props.change > 0 ? '+' : ''
  return `${sign}${props.change}${props.changeUnit}`
})

const circumference = 2 * Math.PI * 28
const progressOffset = computed(() => {
  if (!props.maxValue) return 0
  const pct = Math.min(props.value / props.maxValue, 1)
  return circumference * (1 - pct)
})
</script>

<template>
  <div class="kpi-card" :style="{ '--kpi-color': color }">
    <!-- 环形进度背景 -->
    <svg v-if="maxValue" class="kpi-card__ring" viewBox="0 0 64 64">
      <circle cx="32" cy="32" r="28" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="3" />
      <circle cx="32" cy="32" r="28" fill="none" :stroke="color" stroke-width="3"
        stroke-linecap="round" :stroke-dasharray="circumference"
        :stroke-dashoffset="progressOffset" class="kpi-card__ring-progress"
        style="transform: rotate(-90deg); transform-origin: center;" />
    </svg>

    <!-- 图标 -->
    <div v-if="icon" class="kpi-card__icon">{{ icon }}</div>

    <!-- 数值 -->
    <div class="kpi-card__value">
      <NumberRoll :value="value" :prefix="prefix" :suffix="suffix" :decimals="decimals"
        :font-size="fontSize" :color="color" />
    </div>

    <!-- 标签 -->
    <div class="kpi-card__label">{{ label }}</div>

    <!-- 变化趋势 -->
    <div v-if="change !== 0" class="kpi-card__change" :style="{ color: changeColor }">
      <span class="kpi-card__arrow">{{ trend === 'up' ? '▲' : '▼' }}</span>
      {{ changeText }}
    </div>

    <!-- 脉冲点 -->
    <span class="kpi-card__pulse" />
  </div>
</template>

<style scoped>
.kpi-card {
  --kpi-color: var(--accent-cyan);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 14px 10px;
  text-align: center;
  position: relative;
  min-height: 110px;
}

.kpi-card__ring {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 64px; height: 64px;
  opacity: 0.4;
  pointer-events: none;
}

.kpi-card__ring-progress {
  transition: stroke-dashoffset 0.8s ease;
  filter: drop-shadow(0 0 4px var(--kpi-color));
}

.kpi-card__icon {
  font-size: 18px;
  margin-bottom: 2px;
}

.kpi-card__value {
  line-height: 1.2;
  margin-bottom: 2px;
}

.kpi-card__label {
  font-size: 11px;
  color: var(--text-secondary);
  letter-spacing: 1px;
  white-space: nowrap;
}

.kpi-card__change {
  font-size: 11px;
  font-family: var(--font-mono);
  margin-top: 3px;
  display: flex;
  align-items: center;
  gap: 2px;
}

.kpi-card__arrow {
  font-size: 10px;
}

/* 脉冲光点 */
.kpi-card__pulse {
  position: absolute;
  top: 8px; right: 8px;
  width: 6px; height: 6px;
  background: var(--kpi-color);
  border-radius: 50%;
  box-shadow: 0 0 6px var(--kpi-color);
  animation: breathe 2s ease-in-out infinite;
}
</style>