<script setup>
/**
 * VenueModel3D - 场馆3D模型组件（占位版）
 * 使用Three.js渲染简单的3D场馆场景
 * 完整的3D模型将在后续单独添加
 */
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { ZONES } from '../utils/constants'

const containerRef = ref(null)
const webglSupported = ref(true)

// Three.js核心对象
let scene = null
let camera = null
let renderer = null
let controls = null
let animationId = null
// 场馆区域网格
const zoneMeshes = []

/**
 * 初始化Three.js场景
 */
function initScene() {
  try {
    const container = containerRef.value
    if (!container) return

    const width = container.clientWidth
    const height = container.clientHeight

    // 创建场景
    scene = new THREE.Scene()
    scene.fog = new THREE.FogExp2(0x0a0e27, 0.02)

    // 创建相机
    camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000)
    camera.position.set(12, 10, 12)
    camera.lookAt(0, 0, 0)

    // 创建渲染器
    renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
    })
    renderer.setSize(width, height)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.setClearColor(0x000000, 0)
    container.appendChild(renderer.domElement)

    // 轨道控制器
    controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.dampingFactor = 0.05
    controls.autoRotate = true
    controls.autoRotateSpeed = 0.5
    controls.maxPolarAngle = Math.PI / 2.2
    controls.minDistance = 5
    controls.maxDistance = 30

    // 添加灯光
    setupLights()

    // 添加场馆模型
    createVenueModel()

    // 添加地面网格
    createGroundGrid()

    // 添加粒子背景
    createParticles()

    // 启动渲染循环
    animate()
  } catch (e) {
    console.warn('WebGL初始化失败:', e)
    webglSupported.value = false
    // 清理可能已创建的部分资源
    if (renderer) {
      renderer.dispose()
      renderer = null
    }
    if (controls) {
      controls.dispose()
      controls = null
    }
    scene = null
    camera = null
  }
}

/**
 * 设置灯光
 */
function setupLights() {
  // 环境光
  const ambientLight = new THREE.AmbientLight(0x1a1a4e, 0.6)
  scene.add(ambientLight)

  // 主方向光
  const directionalLight = new THREE.DirectionalLight(0x00f0ff, 0.8)
  directionalLight.position.set(5, 10, 5)
  scene.add(directionalLight)

  // 补光
  const fillLight = new THREE.DirectionalLight(0x4d7cff, 0.3)
  fillLight.position.set(-5, 5, -5)
  scene.add(fillLight)

  // 点光源 - 场馆中心
  const pointLight = new THREE.PointLight(0x00f0ff, 1, 20)
  pointLight.position.set(0, 3, 0)
  scene.add(pointLight)
}

/**
 * 创建场馆模型（简化版 - 由几何体组成）
 */
function createVenueModel() {
  // 场馆主体 - 圆形底座
  const baseGeometry = new THREE.CylinderGeometry(6, 6.5, 0.3, 64)
  const baseMaterial = new THREE.MeshPhongMaterial({
    color: 0x0d1135,
    transparent: true,
    opacity: 0.8,
    shininess: 30,
  })
  const base = new THREE.Mesh(baseGeometry, baseMaterial)
  base.position.y = -0.15
  scene.add(base)

  // 场馆外壳 - 半球形
  const shellGeometry = new THREE.SphereGeometry(5.5, 64, 32, 0, Math.PI * 2, 0, Math.PI / 2)
  const shellMaterial = new THREE.MeshPhongMaterial({
    color: 0x111640,
    transparent: true,
    opacity: 0.3,
    side: THREE.DoubleSide,
    shininess: 60,
    wireframe: false,
  })
  const shell = new THREE.Mesh(shellGeometry, shellMaterial)
  shell.position.y = 0
  scene.add(shell)

  // 线框版本 - 科技感
  const wireframeGeometry = new THREE.SphereGeometry(5.6, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2)
  const wireframeMaterial = new THREE.MeshBasicMaterial({
    color: 0x00f0ff,
    transparent: true,
    opacity: 0.08,
    wireframe: true,
  })
  const wireframe = new THREE.Mesh(wireframeGeometry, wireframeMaterial)
  wireframe.position.y = 0
  scene.add(wireframe)

  // 各区域标记
  ZONES.forEach((zone) => {
    const { x, z } = zone.position
    const color = new THREE.Color(zone.color)

    // 区域底座
    const zoneGeometry = new THREE.BoxGeometry(1.8, 0.6, 1.8)
    const zoneMaterial = new THREE.MeshPhongMaterial({
      color: color,
      transparent: true,
      opacity: 0.6,
      emissive: color,
      emissiveIntensity: 0.2,
    })
    const zoneMesh = new THREE.Mesh(zoneGeometry, zoneMaterial)
    zoneMesh.position.set(x, 0.3, z)
    scene.add(zoneMesh)
    zoneMeshes.push({ mesh: zoneMesh, zone })

    // 区域边框
    const edgeGeometry = new THREE.EdgesGeometry(zoneGeometry)
    const edgeMaterial = new THREE.LineBasicMaterial({
      color: color,
      transparent: true,
      opacity: 0.8,
    })
    const edges = new THREE.LineSegments(edgeGeometry, edgeMaterial)
    edges.position.copy(zoneMesh.position)
    scene.add(edges)
  })

  // 中心舞台
  const stageGeometry = new THREE.CylinderGeometry(1.5, 1.5, 0.8, 32)
  const stageMaterial = new THREE.MeshPhongMaterial({
    color: 0xffd700,
    transparent: true,
    opacity: 0.5,
    emissive: 0xffd700,
    emissiveIntensity: 0.3,
  })
  const stage = new THREE.Mesh(stageGeometry, stageMaterial)
  stage.position.set(0, 0.4, 0)
  scene.add(stage)
}

/**
 * 创建地面网格
 */
function createGroundGrid() {
  const gridHelper = new THREE.GridHelper(30, 30, 0x00f0ff, 0x0d1135)
  gridHelper.position.y = -0.3
  gridHelper.material.opacity = 0.15
  gridHelper.material.transparent = true
  scene.add(gridHelper)
}

/**
 * 创建粒子背景
 */
function createParticles() {
  const particleCount = 500
  const positions = new Float32Array(particleCount * 3)
  const colors = new Float32Array(particleCount * 3)

  for (let i = 0; i < particleCount; i++) {
    const i3 = i * 3
    positions[i3] = (Math.random() - 0.5) * 30
    positions[i3 + 1] = Math.random() * 15
    positions[i3 + 2] = (Math.random() - 0.5) * 30

    // 随机青色/蓝色
    const colorChoice = Math.random()
    if (colorChoice < 0.5) {
      colors[i3] = 0
      colors[i3 + 1] = 0.94
      colors[i3 + 2] = 1
    } else {
      colors[i3] = 0.3
      colors[i3 + 1] = 0.49
      colors[i3 + 2] = 1
    }
  }

  const particleGeometry = new THREE.BufferGeometry()
  particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  particleGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))

  const particleMaterial = new THREE.PointsMaterial({
    size: 0.05,
    vertexColors: true,
    transparent: true,
    opacity: 0.6,
    blending: THREE.AdditiveBlending,
  })

  const particleSystem = new THREE.Points(particleGeometry, particleMaterial)
  particleSystem.name = 'particles'
  scene.add(particleSystem)
}

/**
 * 渲染循环
 */
function animate() {
  if (!renderer || !scene || !camera) return

  animationId = requestAnimationFrame(animate)

  // 更新控制器
  controls?.update()

  // 区域呼吸动画
  const time = Date.now() * 0.001
  zoneMeshes.forEach(({ mesh }, index) => {
    mesh.position.y = 0.3 + Math.sin(time + index * 0.5) * 0.05
  })

  // 粒子缓慢旋转
  const particles = scene.getObjectByName('particles')
  if (particles) {
    particles.rotation.y += 0.0003
  }

  // 渲染
  renderer.render(scene, camera)
}

/**
 * 窗口大小变化处理
 */
function handleResize() {
  const container = containerRef.value
  if (!container || !camera || !renderer) return

  const width = container.clientWidth
  const height = container.clientHeight

  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

onMounted(() => {
  initScene()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)

  // 停止动画
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }

  // 清理Three.js资源
  if (renderer) {
    renderer.dispose()
    containerRef.value?.removeChild(renderer.domElement)
    renderer = null
  }

  if (controls) {
    controls.dispose()
    controls = null
  }

  // 递归释放场景中的几何体和材质
  if (scene) {
    scene.traverse((object) => {
      if (object.geometry) object.geometry.dispose()
      if (object.material) {
        if (Array.isArray(object.material)) {
          object.material.forEach((m) => m.dispose())
        } else {
          object.material.dispose()
        }
      }
    })
    scene = null
  }

  camera = null
  zoneMeshes.length = 0
})
</script>

<template>
  <div v-if="webglSupported" ref="containerRef" class="venue-model-3d" />
  <div v-else class="venue-model-3d-fallback">
    <div class="fallback-content">
      <span class="fallback-icon">🏟️</span>
      <p class="fallback-title">3D模型需要WebGL支持</p>
      <p class="fallback-subtitle">请在支持WebGL的浏览器中查看</p>
    </div>
  </div>
</template>

<style scoped>
.venue-model-3d {
  width: 100%;
  height: 100%;
  min-height: 300px;
  position: relative;
  overflow: hidden;
}

.venue-model-3d-fallback {
  width: 100%;
  height: 100%;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse at center, #0d1135 0%, #0a0e27 100%);
  border-radius: 8px;
}

.fallback-content {
  text-align: center;
}

.fallback-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 16px;
}

.fallback-title {
  font-size: 16px;
  color: #e0e6ff;
  margin: 0 0 8px 0;
}

.fallback-subtitle {
  font-size: 13px;
  color: #6b7394;
  margin: 0;
}
</style>
