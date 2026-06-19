import { createApp } from 'vue'
import App from './App.vue'

// 导入全局样式
import './styles/global.css'
import './styles/glassmorphism.css'
import './styles/animations.css'

// 创建Vue应用实例
const app = createApp(App)

// 全局错误捕获 - 诊断"一闪而过"问题
app.config.errorHandler = (err, instance, info) => {
  console.error('[Vue Error]', err)
  console.error('[Vue Error Info]', info)
  // 在页面上显示错误信息
  const el = document.getElementById('app')
  if (el && el.innerHTML.trim() === '') {
    el.innerHTML = `<div style="color:#ff4757;background:#0a0e27;padding:40px;font-family:monospace;white-space:pre-wrap;">
      <h2>应用崩溃</h2>
      <pre>${err}\n\n组件: ${info}</pre>
    </div>`
  }
}

// 全局未捕获错误
window.addEventListener('error', (e) => {
  console.error('[Global Error]', e.error || e.message)
  const el = document.getElementById('app')
  if (el && el.firstChild === null) {
    el.innerHTML = `<div style="color:#ff4757;background:#0a0e27;padding:40px;font-family:monospace;">
      <h2>全局错误</h2>
      <pre>${e.error || e.message}</pre>
    </div>`
  }
})

app.mount('#app')
