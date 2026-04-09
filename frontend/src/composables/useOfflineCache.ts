import { ref, onMounted, onUnmounted } from 'vue'
import { ElNotification } from 'element-plus'

const CACHE_KEY = 'offline_pending_changes'

export function useOfflineCache() {
  const isOnline = ref(navigator.onLine)
  const pendingCount = ref(0)

  function loadPending(): any[] {
    try {
      return JSON.parse(localStorage.getItem(CACHE_KEY) || '[]')
    } catch {
      return []
    }
  }

  function savePending(items: any[]) {
    localStorage.setItem(CACHE_KEY, JSON.stringify(items))
    pendingCount.value = items.length
  }

  function cacheChange(change: { type: string; id: number; data: any }) {
    const pending = loadPending()
    // 合并同一实体的修改
    const idx = pending.findIndex((p) => p.type === change.type && p.id === change.id)
    if (idx >= 0) {
      pending[idx].data = { ...pending[idx].data, ...change.data }
    } else {
      pending.push(change)
    }
    savePending(pending)
  }

  function clearCache() {
    localStorage.removeItem(CACHE_KEY)
    pendingCount.value = 0
  }

  function handleOnline() {
    isOnline.value = true
    const pending = loadPending()
    if (pending.length > 0) {
      ElNotification({
        title: '网络已恢复',
        message: `检测到 ${pending.length} 条未同步修改，请手动刷新页面以同步数据。`,
        type: 'warning',
        duration: 0,
      })
    }
  }

  function handleOffline() {
    isOnline.value = false
    ElNotification({
      title: '网络已断开',
      message: '当前处于离线状态，修改将暂存本地。',
      type: 'warning',
    })
  }

  onMounted(() => {
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    pendingCount.value = loadPending().length
  })

  onUnmounted(() => {
    window.removeEventListener('online', handleOnline)
    window.removeEventListener('offline', handleOffline)
  })

  return { isOnline, pendingCount, cacheChange, clearCache, loadPending }
}
