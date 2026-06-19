# Tasks

- [x] Task 1: 修复 VenueModel3D.vue WebGL 异常崩溃
  - [x] 1.1: 在 initScene() 中包裹 WebGLRenderer 创建的 try-catch
  - [x] 1.2: 添加 webglSupported 响应式标志
  - [x] 1.3: WebGL 不可用时显示降级 UI（提示文字 + 场馆示意图标）
  - [x] 1.4: 确保 onUnmounted 中安全清理（renderer 可能为 null）

- [x] Task 2: 修复 FlyLineChart.vue echarts-gl 异常
  - [x] 2.1: 在 echarts.init/setOption 处添加 try-catch
  - [x] 2.2: echarts-gl 初始化失败时降级为 2D 直角坐标系飞线图
  - [x] 2.3: 3D模式改用 grid3D 坐标系，不依赖 geo3D 地图数据

- [x] Task 3: 验证修复效果
  - [x] 3.1: 确认页面在无 WebGL 环境下不再白屏
  - [x] 3.2: 确认所有非 WebGL 组件正常渲染

# Task Dependencies
- Task 2 依赖 Task 1（先修复最关键的 3D 模型崩溃）
- Task 3 依赖 Task 1 和 Task 2
