# 修复 WebGL 不可用导致页面白屏 Spec

## Why
页面在无 WebGL 支持的环境（如沙箱、部分虚拟机、旧设备）中完全白屏，因为 Three.js WebGLRenderer 构造函数抛出未捕获异常，导致 Vue 组件挂载失败，整个应用崩溃。

## What Changes
- VenueModel3D.vue: 在 WebGLRenderer 创建处添加 try-catch，WebGL 不可用时显示降级 UI（静态场馆示意图）
- FlyLineChart.vue: 在 echarts-gl 初始化处添加 try-catch，WebGL 不可用时降级为 2D 地图飞线
- CursorTrail.vue: Canvas 2D 不依赖 WebGL，但需确保初始化异常不崩溃应用

## Impact
- Affected code: `VenueModel3D.vue`, `FlyLineChart.vue`
- Affected specs: 页面可访问性、3D模型渲染、飞线图渲染

## ADDED Requirements

### Requirement: WebGL 降级容错
系统 SHALL 在 WebGL 不可用时优雅降级而非白屏崩溃。

#### Scenario: WebGL 不可用
- **WHEN** 浏览器不支持 WebGL 或 WebGL 上下文创建失败
- **THEN** 页面正常显示，3D 模型区域显示降级 UI（带提示文字的静态面板），其他非 WebGL 图表正常渲染

#### Scenario: WebGL 可用
- **WHEN** 浏览器支持 WebGL
- **THEN** 3D 模型和飞线图正常渲染，行为与之前一致
