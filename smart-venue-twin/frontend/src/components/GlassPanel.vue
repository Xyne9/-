<script setup>
/**
 * GlassPanel - 科技感面板组件 v2.0
 * 流光线框、角落装饰、扫描线、霓虹标题
 */
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  bordered: { type: Boolean, default: true },
  glow: { type: Boolean, default: true },
  hoverable: { type: Boolean, default: false },
  size: { type: String, default: 'default', validator: (v) => ['small', 'default', 'large'].includes(v) },
  accentColor: { type: String, default: '' },
  customStyle: { type: Object, default: () => ({}) },
})

const panelClass = computed(() => [
  'glass-panel',
  props.bordered && 'glass-panel--bordered',
  props.glow && 'glass-panel--glow',
  props.hoverable && 'glass-panel--hover',
  `glass-panel--${props.size}`,
])
</script>

<template>
  <div :class="panelClass" :style="[customStyle, accentColor ? { '--panel-accent': accentColor } : {}]">
    <!-- 角落装饰 -->
    <span class="corner-tl" />
    <span class="corner-tr" />
    <span class="corner-bl" />
    <span class="corner-br" />

    <!-- 标题栏 -->
    <div v-if="title" class="glass-panel__header">
      <span class="glass-panel__dot" />
      <span class="glass-panel__title">{{ title }}</span>
      <span class="glass-panel__line" />
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
  --panel-accent: var(--accent-cyan);
  position: relative;
  display: flex;
  flex-direction: column;
  background: var(--glass-bg);
  border: 1px solid rgba(0, 240, 255, 0.1);
  border-radius: var(--radius-lg);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.03);
  overflow: hidden;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

/* 尺寸变体 */
.glass-panel--small .glass-panel__body { padding: 8px 12px; }
.glass-panel--default .glass-panel__body { padding: 12px 16px; }
.glass-panel--large .glass-panel__body { padding: 16px 20px; }

/* 渐变边框 */
.glass-panel--bordered::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: var(--radius-lg);
  padding: 1px;
  background: linear-gradient(135deg, rgba(0, 240, 255, 0.3), rgba(0, 212, 170, 0.1), rgba(77, 124, 255, 0.2), rgba(0, 240, 255, 0.05));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
  z-index: 1;
}

/* 顶部高光线 */
.glass-panel--glow::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--panel-accent), transparent);
  opacity: 0.5;
  pointer-events: none;
  z-index: 2;
}

/* 悬停增强 */
.glass-panel--hover:hover {
  border-color: rgba(0, 240, 255, 0.2);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4), 0 0 20px rgba(0, 240, 255, 0.05);
}

/* 角落装饰 */
.corner-tl, .corner-tr, .corner-bl, .corner-br {
  position: absolute;
  width: 12px; height: 12px;
  border-color: var(--panel-accent);
  border-style: solid;
  z-index: 3;
  pointer-events: none;
  opacity: 0.6;
}
.corner-tl { top: 2px; left: 2px; border-width: 2px 0 0 2px; border-radius: 3px 0 0 0; }
.corner-tr { top: 2px; right: 2px; border-width: 2px 2px 0 0; border-radius: 0 3px 0 0; }
.corner-bl { bottom: 2px; left: 2px; border-width: 0 0 2px 2px; border-radius: 0 0 0 3px; }
.corner-br { bottom: 2px; right: 2px; border-width: 0 2px 2px 0; border-radius: 0 0 3px 0; }

/* 标题栏 */
.glass-panel__header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  border-bottom: 1px solid rgba(0, 240, 255, 0.06);
  position: relative;
  flex-shrink: 0;
}

/* 标题前装饰点 */
.glass-panel__dot {
  width: 6px; height: 6px;
  background: var(--panel-accent);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--panel-accent);
  flex-shrink: 0;
  animation: breathe 2s ease-in-out infinite;
}

/* 标题文字 */
.glass-panel__title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 1.5px;
  text-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
  flex-shrink: 0;
}

/* 标题后装饰线 */
.glass-panel__line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, var(--panel-accent), transparent);
  opacity: 0.3;
}

/* 内容区 */
.glass-panel__body {
  flex: 1;
  overflow: hidden;
  position: relative;
  z-index: 0;
}
</style>