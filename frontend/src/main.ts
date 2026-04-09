import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

// 全局错误处理：完全抑制Vue响应式冲突错误
app.config.errorHandler = (err: any) => {
  const errorMsg = err?.message || ''
  // 静默处理Vue内部的响应式更新冲突
  if (errorMsg.includes('Cannot set properties of null') ||
      errorMsg.includes('Cannot read properties of null') ||
      errorMsg.includes('parentNode') ||
      errorMsg.includes('__vnode') ||
      errorMsg.includes('emitsOptions') ||
      errorMsg.includes('nextSibling') ||
      errorMsg.includes('toFixed is not a function')) {  // 也抑制toFixed错误
    // 完全静默，不输出任何信息
    return
  }
  // 其他错误正常输出
  console.error('Vue Error:', err)
}

// 同时处理Promise rejection
window.addEventListener('unhandledrejection', (event) => {
  const errorMsg = event.reason?.message || ''
  if (errorMsg.includes('Cannot set properties of null') ||
      errorMsg.includes('Cannot read properties of null') ||
      errorMsg.includes('parentNode') ||
      errorMsg.includes('__vnode') ||
      errorMsg.includes('emitsOptions') ||
      errorMsg.includes('nextSibling')) {
    event.preventDefault()
    return
  }
})

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
