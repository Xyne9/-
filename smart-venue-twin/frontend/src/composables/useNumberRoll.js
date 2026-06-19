/**
 * 数字滚动动画组合式函数
 * 使用GSAP实现数字从旧值到新值的平滑过渡
 */
import { ref, watch, onUnmounted } from 'vue'
import gsap from 'gsap'

/**
 * 创建带动画的响应式数字
 * @param {number} initialValue - 初始值
 * @param {object} options - 配置项
 * @returns {object} { displayValue, setValue, animate }
 */
export function useNumberRoll(initialValue = 0, options = {}) {
  const {
    duration = 1, // 动画时长（秒）
    decimals = 0, // 小数位数
    ease = 'power2.out', // 缓动函数
    delay = 0, // 延迟
    prefix = '', // 前缀
    suffix = '', // 后缀
  } = options

  // 显示值（响应式）
  const displayValue = ref(initialValue)
  // 内部补间对象
  const tweenObj = { value: initialValue }
  // 当前动画实例
  let tween = null

  /**
   * 设置新值并触发动画
   * @param {number} newValue - 目标值
   * @param {object} overrideOptions - 覆盖配置项
   */
  function setValue(newValue, overrideOptions = {}) {
    const finalDuration = overrideOptions.duration ?? duration
    const finalEase = overrideOptions.ease ?? ease
    const finalDelay = overrideOptions.delay ?? delay

    // 停止当前动画
    if (tween) {
      tween.kill()
    }

    // 创建新的GSAP补间动画
    tween = gsap.to(tweenObj, {
      value: newValue,
      duration: finalDuration,
      ease: finalEase,
      delay: finalDelay,
      onUpdate: () => {
        // 根据小数位数更新显示值
        displayValue.value = decimals > 0
          ? Number(tweenObj.value.toFixed(decimals))
          : Math.round(tweenObj.value)
      },
    })
  }

  /**
   * 立即设置值（无动画）
   * @param {number} value - 目标值
   */
  function setValueImmediate(value) {
    if (tween) {
      tween.kill()
      tween = null
    }
    tweenObj.value = value
    displayValue.value = decimals > 0
      ? Number(value.toFixed(decimals))
      : Math.round(value)
  }

  /**
   * 获取格式化后的显示文本
   * @returns {string} 带前缀后缀的格式化数字
   */
  function getFormatted() {
    const val = decimals > 0
      ? displayValue.value.toFixed(decimals)
      : String(displayValue.value)
    return `${prefix}${val}${suffix}`
  }

  // 组件卸载时清理动画
  onUnmounted(() => {
    if (tween) {
      tween.kill()
      tween = null
    }
  })

  return {
    displayValue,
    setValue,
    setValueImmediate,
    getFormatted,
  }
}

/**
 * 创建多个数字滚动的批量管理器
 * @param {Array<{key: string, initial: number, options?: object}>} items - 数字配置列表
 * @returns {object} { values, setValue, setValues }
 */
export function useNumberRollBatch(items) {
  const rollers = {}
  const values = {}

  items.forEach(({ key, initial = 0, options = {} }) => {
    rollers[key] = useNumberRoll(initial, options)
    values[key] = rollers[key].displayValue
  })

  /**
   * 设置单个值
   */
  function setValue(key, newValue) {
    rollers[key]?.setValue(newValue)
  }

  /**
   * 批量设置值
   * @param {object} data - { key: value } 映射
   */
  function setValues(data) {
    Object.entries(data).forEach(([key, value]) => {
      rollers[key]?.setValue(value)
    })
  }

  return {
    values,
    setValue,
    setValues,
  }
}
