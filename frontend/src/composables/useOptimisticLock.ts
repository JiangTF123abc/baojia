import { ElMessageBox } from 'element-plus'

export function useOptimisticLock() {
  async function updateWithLock<T>(
    updateFn: () => Promise<T>,
    onConflict?: (latestData: any) => void
  ): Promise<T | null> {
    try {
      return await updateFn()
    } catch (err: any) {
      if (err.response?.status === 409) {
        const latest = err.response.data?.data
        if (onConflict) {
          onConflict(latest)
        } else {
          await ElMessageBox.alert(
            '数据已被他人修改，请刷新后重试。',
            '并发冲突',
            { type: 'warning' }
          )
        }
        return null
      }
      throw err
    }
  }

  return { updateWithLock }
}
