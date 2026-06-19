<script setup>
/**
 * NumberRoll - 数字滚动动画组件
 * 数字变化时，每个数位从旧值滚动到新值
 * 使用GSAP实现平滑动画
 */
import { ref, watch, computed, onUnmounted } from 'vue'
import gsap from 'gsap'

const props = defineProps({
  // 目标数字
  value: {
    type: Number,
    required: true,
  },
  // 小数位数
  decimals: {
    type: Number,
    default: 0,
  },
  // 前缀（如 ¥、$）
  prefix: {
    type: String,
    default: '',
  },
  // 后缀（如 %、万）
  suffix: {
    type: String,
    default: '',
  },
  // 动画时长（秒）
  duration: {
    type: Number,
    default: 0.8,
  },
  // 缓动函数
  ease: {
    type: String,
    default: 'power2.out',
  },
  // 千分位分隔
  useGrouping: {
    type: Boolean,
    default: true,
  },
  // 字体大小
  fontSize: {
    type: String,
    default: '24px',
  },
  // 文字颜色
  color: {
    type: String,
    default: 'var(--accent-cyan)',
  },
})

// 内部补间值
const tweenValue = ref(props.value)
// GSAP动画实例
let tween = null

/**
 * 格式化数字为字符串数组（每个字符一个元素）
 */
const formattedDigits = computed(() => {
  const val = props.decimals > 0
    ? tweenValue.value.toFixed(props.decimals)
    : Math.round(tweenValue.value).toString()

  // 是否需要千分位
  if (props.useGrouping) {
    const parts = val.split('.')
    parts[0] = Number(parts[0]).toLocaleString('zh-CN')
    return (props.prefix + parts.join('.') + props.suffix).split('')
  }
  return (props.prefix + val + props.suffix).split('')
})

/**
 * 判断字符是否为数字
 */
function isDigit(char) {
  return /\d/.test(char)
}

// 监听value变化，触发动画
watch(
  () => props.value,
  (newVal) => {
    if (tween) {
      tween.kill()
    }
    tween = gsap.to(tweenValue, {
      value: newVal,
      duration: props.duration,
      ease: props.ease,
    })
  }
)

onUnmounted(() => {
  if (tween) {
    tween.kill()
    tween = null
  }
})
</script>

<template>
  <span class="number-roll" :style="{ fontSize, color }">
    <span
      v-for="(char, index) in formattedDigits"
      :key="index"
      :class="['number-roll__char', { 'number-roll__digit': isDigit(char) }]"
    >{{ char }}</span>
  </span>
</template>

<style scoped>
.number-roll {
  display: inline-flex;
  align-items: baseline;
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.number-roll__char {
  display: inline-block;
  transition: transform 0.3s ease;
}

.number-roll__digit {
  /* 数字字符的额外样式 */
  min-width: 0.6em;
  text-align: center;
}
</style>
