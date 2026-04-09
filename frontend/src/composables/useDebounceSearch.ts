import { ref } from 'vue'

export function useDebounceSearch<T>(
  searchFn: (query: string) => Promise<T[]>,
  delay = 300
) {
  const results = ref<T[]>([])
  const loading = ref(false)
  let timer: ReturnType<typeof setTimeout> | null = null

  function search(query: string) {
    if (timer) clearTimeout(timer)
    if (!query.trim()) {
      results.value = []
      return
    }
    loading.value = true
    timer = setTimeout(async () => {
      try {
        results.value = await searchFn(query)
      } finally {
        loading.value = false
      }
    }, delay)
  }

  function clear() {
    results.value = []
    loading.value = false
    if (timer) clearTimeout(timer)
  }

  return { results, loading, search, clear }
}
