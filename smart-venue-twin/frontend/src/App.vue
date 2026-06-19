<script setup>
import DashboardLayout from './components/DashboardLayout.vue'
import CursorTrail from './components/CursorTrail.vue'
</script>

<template>
  <div class="app-root">
    <!-- 鼠标光标拖尾特效 -->
    <CursorTrail />
    <!-- 主大屏布局 -->
    <DashboardLayout />
  </div>
</template>

<style scoped>
.app-root {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  position: relative;
  background: var(--bg-primary);
}
</style>
