/**
 * WebGL支持检测工具
 * 在沙箱/无GPU环境中安全检测WebGL可用性
 */

/**
 * 检测WebGL是否可用
 * 使用离屏canvas进行安全检测，不会触发渲染器初始化
 * @returns {boolean}
 */
export function isWebGLAvailable() {
  try {
    const canvas = document.createElement('canvas')
    // 尝试获取WebGL上下文，不创建渲染器
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl')
    if (!gl) return false
    // 获取扩展信息确认WebGL真正可用
    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info')
    if (debugInfo) {
      const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL)
      // 某些环境下会返回SwiftShader（软件渲染），也视为不可用
      // 避免GPU进程崩溃
      if (renderer && renderer.includes('SwiftShader')) return false
    }
    return true
  } catch (e) {
    return false
  }
}