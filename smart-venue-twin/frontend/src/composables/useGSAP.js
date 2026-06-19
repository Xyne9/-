/**
 * GSAP动画组合式函数
 * 提供大屏常用的入场动画、数字动画等
 */
import { onMounted, onUnmounted } from 'vue'
import gsap from 'gsap'

/**
 * 使用GSAP动画
 * @returns {object} 动画辅助方法
 */
export function useGSAP() {
  // 存储所有动画实例，便于统一清理
  const animations = []

  /**
   * 交错入场动画 - 从下方淡入
   * @param {string|Element} selector - CSS选择器或DOM元素
   * @param {object} options - 配置项
   */
  function staggerEntrance(selector, options = {}) {
    const {
      stagger = 0.15, // 交错延迟
      duration = 0.6, // 单个动画时长
      delay = 0, // 整体延迟
      y = 30, // Y轴偏移
      ease = 'power2.out', // 缓动函数
    } = options

    const anim = gsap.from(selector, {
      opacity: 0,
      y,
      duration,
      stagger,
      delay,
      ease,
    })
    animations.push(anim)
    return anim
  }

  /**
   * 图表容器入场动画 - 淡入+缩放
   * @param {string|Element} selector - CSS选择器或DOM元素
   * @param {object} options - 配置项
   */
  function chartEntrance(selector, options = {}) {
    const {
      duration = 0.8,
      delay = 0,
      scale = 0.9,
      ease = 'back.out(1.2)',
    } = options

    const anim = gsap.from(selector, {
      opacity: 0,
      scale,
      duration,
      delay,
      ease,
    })
    animations.push(anim)
    return anim
  }

  /**
   * 数字计数动画 - 从0到目标值
   * @param {object} target - 响应式ref对象
   * @param {number} endValue - 目标值
   * @param {object} options - 配置项
   */
  function countUp(target, endValue, options = {}) {
    const {
      duration = 1.5,
      delay = 0,
      ease = 'power2.out',
      decimals = 0, // 小数位数
      onUpdate, // 每帧更新回调
    } = options

    const obj = { value: 0 }
    const anim = gsap.to(obj, {
      value: endValue,
      duration,
      delay,
      ease,
      onUpdate: () => {
        const val = decimals > 0
          ? Number(obj.value.toFixed(decimals))
          : Math.round(obj.value)
        target.value = val
        onUpdate?.(val)
      },
    })
    animations.push(anim)
    return anim
  }

  /**
   * 从左侧滑入
   * @param {string|Element} selector - CSS选择器或DOM元素
   * @param {object} options - 配置项
   */
  function slideInLeft(selector, options = {}) {
    const {
      duration = 0.6,
      delay = 0,
      x = -50,
      ease = 'power2.out',
    } = options

    const anim = gsap.from(selector, {
      opacity: 0,
      x,
      duration,
      delay,
      ease,
    })
    animations.push(anim)
    return anim
  }

  /**
   * 从右侧滑入
   * @param {string|Element} selector - CSS选择器或DOM元素
   * @param {object} options - 配置项
   */
  function slideInRight(selector, options = {}) {
    const {
      duration = 0.6,
      delay = 0,
      x = 50,
      ease = 'power2.out',
    } = options

    const anim = gsap.from(selector, {
      opacity: 0,
      x,
      duration,
      delay,
      ease,
    })
    animations.push(anim)
    return anim
  }

  /**
   * 脉冲动画 - 缩放脉冲
   * @param {string|Element} selector - CSS选择器或DOM元素
   * @param {object} options - 配置项
   */
  function pulse(selector, options = {}) {
    const {
      duration = 0.6,
      scale = 1.05,
      repeat = -1, // 无限重复
      yoyo = true,
      ease = 'power1.inOut',
    } = options

    const anim = gsap.to(selector, {
      scale,
      duration,
      repeat,
      yoyo,
      ease,
    })
    animations.push(anim)
    return anim
  }

  /**
   * 创建自定义GSAP动画
   * @param {string|Element} selector - CSS选择器或DOM元素
   * @param {object} toProps - gsap.to属性
   * @param {object} fromProps - 可选gsap.from属性
   */
  function animate(selector, toProps, fromProps = null) {
    let anim
    if (fromProps) {
      anim = gsap.fromTo(selector, fromProps, toProps)
    } else {
      anim = gsap.to(selector, toProps)
    }
    animations.push(anim)
    return anim
  }

  /**
   * 清理所有动画
   */
  function cleanup() {
    animations.forEach((anim) => {
      anim.kill()
    })
    animations.length = 0
  }

  // 组件卸载时清理
  onUnmounted(() => {
    cleanup()
  })

  return {
    staggerEntrance,
    chartEntrance,
    countUp,
    slideInLeft,
    slideInRight,
    pulse,
    animate,
    cleanup,
    // 暴露gsap以便高级使用
    gsap,
  }
}
