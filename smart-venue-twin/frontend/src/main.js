import { createApp } from 'vue'
import App from './App.vue'

// 导入全局样式
import './styles/global.css'
import './styles/glassmorphism.css'
import './styles/animations.css'

// 创建Vue应用实例
const app = createApp(App)

app.mount('#app')
