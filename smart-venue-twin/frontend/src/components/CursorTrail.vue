<script setup>
/**
 * CursorTrail - 鼠标光标拖尾特效组件
 * Canvas绘制，粒子跟随鼠标移动并逐渐消失
 * 使用requestAnimationFrame保证性能
 */
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref(null)

// 粒子配置
const CONFIG = {
  maxParticles: 50, // 最大粒子数
  particleSize: 3, // 粒子基础大小
  particleLife: 800, // 粒子生命周期（毫秒）
  fadeRate: 0.02, // 每帧衰减率
  glowSize: 15, // 发光半径
  glowColor: '0, 240, 255', // 发光颜色 RGB
  trailColor: '0, 212, 170', // 拖尾颜色 RGB
  motionBlur: 0.15, // 运动模糊系数
}

// 粒子数组
let particles = []
// 动画帧ID
let animationId = null
// 上一帧鼠标位置
let lastMouse = { x: 0, y: 0 }
// 当前鼠标位置
let currentMouse = { x: 0, y: 0 }
// Canvas上下文
let ctx = null
// 画布尺寸
let width = 0
let height = 0

/**
 * 粒子类
 */
class Particle {
  constructor(x, y) {
    this.x = x
    this.y = y
    this.size = CONFIG.particleSize + Math.random() * 2
    this.life = 1.0 // 1.0 -> 0.0
    this.decay = CONFIG.fadeRate + Math.random() * 0.01
    this.vx = (Math.random() - 0.5) * 1.5 // X方向速度
    this.vy = (Math.random() - 0.5) * 1.5 // Y方向速度
    this.alpha = 1.0
  }

  update() {
    this.x += this.vx
    this.y += this.vy
    this.life -= this.decay
    this.alpha = this.life
    this.size *= 0.98
    return this.life > 0
  }

  draw(context) {
    if (this.alpha <= 0) return

    // 发光效果
    const gradient = context.createRadialGradient(
      this.x, this.y, 0,
      this.x, this.y, this.size * 3
    )
    gradient.addColorStop(0, `rgba(${CONFIG.glowColor}, ${this.alpha * 0.6})`)
    gradient.addColorStop(0.5, `rgba(${CONFIG.trailColor}, ${this.alpha * 0.2})`)
    gradient.addColorStop(1, `rgba(${CONFIG.glowColor}, 0)`)

    context.beginPath()
    context.arc(this.x, this.y, this.size * 3, 0, Math.PI * 2)
    context.fillStyle = gradient
    context.fill()

    // 核心亮点
    context.beginPath()
    context.arc(this.x, this.y, this.size * 0.5, 0, Math.PI * 2)
    context.fillStyle = `rgba(255, 255, 255, ${this.alpha * 0.8})`
    context.fill()
  }
}

/**
 * 鼠标移动事件处理
 */
function onMouseMove(event) {
  currentMouse.x = event.clientX
  currentMouse.y = event.clientY

  // 计算鼠标移动速度
  const dx = currentMouse.x - lastMouse.x
  const dy = currentMouse.y - lastMouse.y
  const speed = Math.sqrt(dx * dx + dy * dy)

  // 根据速度生成粒子，速度越快粒子越多
  const count = Math.min(Math.floor(speed / 5) + 1, 5)
  for (let i = 0; i < count; i++) {
    if (particles.length < CONFIG.maxParticles) {
      // 在上一位置和当前位置之间插值
      const t = i / count
      const x = lastMouse.x + dx * t
      const y = lastMouse.y + dy * t
      particles.push(new Particle(x, y))
    }
  }

  lastMouse.x = currentMouse.x
  lastMouse.y = currentMouse.y
}

/**
 * 动画循环
 */
function animate() {
  if (!ctx) return

  // 运动模糊效果 - 半透明覆盖
  ctx.fillStyle = `rgba(10, 14, 39, ${CONFIG.motionBlur})`
  ctx.fillRect(0, 0, width, height)

  // 更新和绘制粒子
  particles = particles.filter((p) => {
    const alive = p.update()
    if (alive) p.draw(ctx)
    return alive
  })

  // 绘制鼠标位置的发光点
  const glowGradient = ctx.createRadialGradient(
    currentMouse.x, currentMouse.y, 0,
    currentMouse.x, currentMouse.y, CONFIG.glowSize
  )
  glowGradient.addColorStop(0, `rgba(${CONFIG.glowColor}, 0.3)`)
  glowGradient.addColorStop(1, `rgba(${CONFIG.glowColor}, 0)`)
  ctx.beginPath()
  ctx.arc(currentMouse.x, currentMouse.y, CONFIG.glowSize, 0, Math.PI * 2)
  ctx.fillStyle = glowGradient
  ctx.fill()

  animationId = requestAnimationFrame(animate)
}

/**
 * 调整Canvas尺寸
 */
function resize() {
  const canvas = canvasRef.value
  if (!canvas) return
  width = window.innerWidth
  height = window.innerHeight
  canvas.width = width
  canvas.height = height
}

onMounted(() => {
  const canvas = canvasRef.value
  if (!canvas) return

  ctx = canvas.getContext('2d')
  resize()

  // 监听窗口大小变化
  window.addEventListener('resize', resize)
  // 监听鼠标移动
  window.addEventListener('mousemove', onMouseMove)

  // 启动动画循环
  animate()
})

onUnmounted(() => {
  // 清理事件监听
  window.removeEventListener('resize', resize)
  window.removeEventListener('mousemove', onMouseMove)
  // 停止动画
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }
  // 清理资源
  particles = []
  ctx = null
})
</script>

<template>
  <canvas
    ref="canvasRef"
    class="cursor-trail"
  />
</template>

<style scoped>
.cursor-trail {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 9999;
}
</style>
