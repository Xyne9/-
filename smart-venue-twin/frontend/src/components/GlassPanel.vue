<script setup>
/**
 * GlassPanel - 玻璃态面板组件
 * 提供毛玻璃效果、渐变边框、内发光等视觉效果
 * 支持slot内容注入
 */
import { computed } from 'vue'

const props = defineProps({
  // 面板标题
  title: {
    type: String,
    default: '',
  },
  // 是否显示渐变边框
  bordered: {
    type: Boolean,
    default: true,
  },
  // 是否显示内发光
  glow: {
    type: Boolean,
    default: true,
  },
  // 是否启用悬停增强效果
  hoverable: {
    type: Boolean,
    default: false,
  },
  // 面板尺寸
  size: {
    type: String,
    default: 'default', // 'small' | 'default' | 'large'
    validator: (v) => ['small', 'default', 'large'].includes(v),
  },
  // 自定义样式
  customStyle: {
    type: Object,
    default: () => ({}),
  },
})

// 计算class列表
const panelClass = computed(() => [
  'glass-panel',
  props.bordered && 'glass-panel--bordered',
  props.glow && 'glass-panel--glow',
  props.hoverable && 'glass-panel--hover',
  `glass-panel--${props.size}`,
])
</script>

<template>
  <div :class="panelClass" :style="customStyle">
    <!-- 标题栏 -->
    <div v-if="title" class="glass-panel__header">
      <span class="glass-panel__title">{{ title }}</span>
      <!-- 标题栏右侧插槽 -->
      <slot name="header-extra" />
    </div>
    <!-- 内容区 -->
    <div class="glass-panel__body">
      <slot />
    </div>
    <!-- 底部插槽 -->
    <slot name="footer" />
  </div>
</template>

<style scoped>
.glass-panel {
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  box-shadow:
    0 8px 32px var(--glass-shadow),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  overflow: hidden;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

/* 尺寸变体 */
.glass-panel--small .glass-panel__body {
  padding: 8px 12px;
}

.glass-panel--default .glass-panel__body {
  padding: 12px 16px;
}

.glass-panel--large .glass-panel__body {
  padding: 16px 20px;
}

/* 渐变边框 */
.glass-panel--bordered::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: var(--radius-lg);
  padding: 1px;
  background: linear-gradient(
    135deg,
    rgba(0, 240, 255, 0.3),
    rgba(0, 212, 170, 0.1),
    rgba(77, 124, 255, 0.2),
    rgba(0, 240, 255, 0.05)
  );
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
  z-index: 1;
}

/* 内发光 - 顶部高光线 */
.glass-panel--glow::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(0, 240, 255, 0.4),
    transparent
  );
  pointer-events: none;
  z-index: 2;
}

/* 悬停增强 */
.glass-panel--hover:hover {
  border-color: rgba(0, 240, 255, 0.25);
  box-shadow:
    0 8px 32px var(--glass-shadow),
    0 0 20px rgba(0, 240, 255, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

/* 标题栏 */
.glass-panel__header {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  border-bottom: 1px solid rgba(0, 240, 255, 0.08);
  position: relative;
  flex-shrink: 0;
}

/* 标题栏底部装饰线 */
.glass-panel__header::before {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 16px;
  width: 40px;
  height: 2px;
  background: var(--gradient-cyan);
  border-radius: 1px;
}

/* 标题文字 */
.glass-panel__title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 1px;
  padding-left: 10px;
  position: relative;
}

/* 标题前装饰条 */
.glass-panel__title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 12px;
  background: var(--gradient-cyan);
  border-radius: 2px;
}

/* 内容区 */
.glass-panel__body {
  flex: 1;
  overflow: hidden;
}
</style>
