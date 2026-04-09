import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

export interface AutoMatchResult {
  cabinet_id: number
  matched_count: number
  message: string
}

export interface AutoMatchPreview {
  config_found: boolean
  config?: {
    id: number
    control_category: string
    cabinet_type: string
    control_structure: string
  }
  rules_count: number
  preview_items: Array<{
    material_id: number
    model_number: string
    name: string
    specification?: string
    component_category: string
    default_quantity: number
    is_required: boolean
    unit_price: number
  }>
  estimated_cost: number
}

export function useAutoMatch() {
  const loading = ref(false)
  const error = ref<string | null>(null)

  /**
   * 触发自动匹配
   */
  const triggerAutoMatch = async (cabinetId: number): Promise<AutoMatchResult | null> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.post(`/cabinets/${cabinetId}/auto-match`)
      
      if (response.data.code === 0) {
        const result = response.data.data
        ElMessage.success(result.message || '自动匹配成功')
        return result
      } else {
        throw new Error(response.data.message || '自动匹配失败')
      }
    } catch (err: any) {
      error.value = err.message || '自动匹配失败'
      ElMessage.error(error.value || '自动匹配失败')
      console.error('自动匹配失败:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 应用自动隐藏规则
   */
  const applyHideRules = async (cabinetId: number): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.post(`/cabinets/${cabinetId}/apply-hide-rules`)
      
      if (response.data.code === 0) {
        const result = response.data.data
        ElMessage.success(result.message || '应用隐藏规则成功')
        return true
      } else {
        throw new Error(response.data.message || '应用隐藏规则失败')
      }
    } catch (err: any) {
      error.value = err.message || '应用隐藏规则失败'
      ElMessage.error(error.value || '应用隐藏规则失败')
      console.error('应用隐藏规则失败:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取自动匹配预览
   */
  const getAutoMatchPreview = async (cabinetId: number): Promise<AutoMatchPreview | null> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/cabinets/${cabinetId}/auto-match-preview`)
      
      if (response.data.code === 0) {
        return response.data.data
      } else {
        throw new Error(response.data.message || '获取预览失败')
      }
    } catch (err: any) {
      error.value = err.message || '获取预览失败'
      console.error('获取自动匹配预览失败:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 显示自动匹配预览对话框
   */
  const showAutoMatchPreview = async (cabinetId: number): Promise<boolean> => {
    const preview = await getAutoMatchPreview(cabinetId)
    
    if (!preview) {
      return false
    }

    if (!preview.config_found) {
      ElMessage.warning('未找到匹配的柜体配置，无法自动匹配')
      return false
    }

    if (preview.rules_count === 0) {
      ElMessage.warning('该柜体类型暂无自动匹配规则')
      return false
    }

    // 构建预览内容
    const previewHtml = `
      <div style="text-align: left;">
        <p><strong>柜体配置：</strong>${preview.config?.control_category} > ${preview.config?.cabinet_type} > ${preview.config?.control_structure}</p>
        <p><strong>匹配规则数：</strong>${preview.rules_count} 条</p>
        <p><strong>预计成本：</strong>¥${preview.estimated_cost.toFixed(2)}</p>
        <div style="margin-top: 10px;">
          <strong>将添加以下元器件：</strong>
          <ul style="max-height: 300px; overflow-y: auto; margin-top: 5px;">
            ${preview.preview_items.map(item => `
              <li>
                ${item.model_number} - ${item.name}
                (数量: ${item.default_quantity}, 单价: ¥${item.unit_price})
                ${item.is_required ? '<span style="color: red;">[必需]</span>' : ''}
              </li>
            `).join('')}
          </ul>
        </div>
      </div>
    `

    try {
      await ElMessageBox.confirm(previewHtml, '自动匹配预览', {
        confirmButtonText: '确认匹配',
        cancelButtonText: '取消',
        dangerouslyUseHTMLString: true,
        type: 'info'
      })
      
      // 用户确认后执行匹配
      const result = await triggerAutoMatch(cabinetId)
      return result !== null
    } catch {
      // 用户取消
      return false
    }
  }

  /**
   * 自动匹配并应用隐藏规则（组合操作）
   */
  const autoMatchWithHide = async (cabinetId: number): Promise<boolean> => {
    const matchResult = await triggerAutoMatch(cabinetId)
    if (!matchResult) {
      return false
    }

    // 应用隐藏规则
    await applyHideRules(cabinetId)
    
    return true
  }

  return {
    loading,
    error,
    triggerAutoMatch,
    applyHideRules,
    getAutoMatchPreview,
    showAutoMatchPreview,
    autoMatchWithHide
  }
}
