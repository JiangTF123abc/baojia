import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export interface CabinetTypeConfig {
  id: number
  control_category: string
  cabinet_type: string
  control_structure: string
  description?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface AutoMatchRule {
  id: number
  cabinet_type_config_id: number
  material_id: number
  component_category: string
  default_quantity: number
  is_required: boolean
  match_priority: number
  material?: {
    id: number
    model_number: string
    name: string
    specification?: string
    unit_price: number
    component_type?: string
  }
}

export const useCabinetConfigStore = defineStore('cabinetConfig', () => {
  // 状态
  const configs = ref<CabinetTypeConfig[]>([])
  const configsMap = ref<Map<number, CabinetTypeConfig>>(new Map())
  const rulesCache = ref<Map<number, AutoMatchRule[]>>(new Map())
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const activeConfigs = computed(() => {
    return configs.value.filter(config => config.is_active)
  })

  // 根据分类获取配置
  const getConfigsByCategory = computed(() => {
    return (category: string) => {
      return activeConfigs.value.filter(
        config => config.control_category === category
      )
    }
  })

  // 根据柜体类型获取配置
  const getConfigsByCabinetType = computed(() => {
    return (cabinetType: string) => {
      return activeConfigs.value.filter(
        config => config.cabinet_type === cabinetType
      )
    }
  })

  // 方法：加载所有配置
  const fetchConfigs = async (force = false) => {
    if (configs.value.length > 0 && !force) {
      return configs.value
    }

    loading.value = true
    error.value = null

    try {
      const response = await api.get('/cabinet-type-configs')
      if (response.data.code === 0) {
        configs.value = response.data.data
        
        // 更新 map
        configsMap.value.clear()
        configs.value.forEach(config => {
          configsMap.value.set(config.id, config)
        })
        
        return configs.value
      } else {
        throw new Error(response.data.message || '加载配置失败')
      }
    } catch (err: any) {
      error.value = err.message || '加载配置失败'
      console.error('加载柜体配置失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 方法：根据分类查找配置
  const findConfig = async (
    controlCategory: string,
    cabinetType: string,
    controlStructure: string
  ): Promise<CabinetTypeConfig | null> => {
    // 确保配置已加载
    if (configs.value.length === 0) {
      await fetchConfigs()
    }

    return (
      configs.value.find(
        config =>
          config.control_category === controlCategory &&
          config.cabinet_type === cabinetType &&
          config.control_structure === controlStructure &&
          config.is_active
      ) || null
    )
  }

  // 方法：获取自动匹配规则
  const fetchAutoMatchRules = async (
    configId: number,
    force = false
  ): Promise<AutoMatchRule[]> => {
    // 检查缓存
    if (rulesCache.value.has(configId) && !force) {
      return rulesCache.value.get(configId)!
    }

    loading.value = true
    error.value = null

    try {
      const response = await api.get(
        `/cabinet-type-configs/${configId}/auto-match-rules`
      )
      if (response.data.code === 0) {
        const rules = response.data.data
        rulesCache.value.set(configId, rules)
        return rules
      } else {
        throw new Error(response.data.message || '加载匹配规则失败')
      }
    } catch (err: any) {
      error.value = err.message || '加载匹配规则失败'
      console.error('加载自动匹配规则失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 方法：搜索配置
  const searchConfigs = async (params: {
    control_category?: string
    cabinet_type?: string
    control_structure?: string
  }) => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get('/cabinet-type-configs/search', { params })
      if (response.data.code === 0) {
        return response.data.data
      } else {
        throw new Error(response.data.message || '搜索配置失败')
      }
    } catch (err: any) {
      error.value = err.message || '搜索配置失败'
      console.error('搜索柜体配置失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 方法：创建配置（管理员）
  const createConfig = async (data: Partial<CabinetTypeConfig>) => {
    loading.value = true
    error.value = null

    try {
      const response = await api.post('/cabinet-type-configs', data)
      if (response.data.code === 0) {
        const newConfig = response.data.data
        configs.value.push(newConfig)
        configsMap.value.set(newConfig.id, newConfig)
        return newConfig
      } else {
        throw new Error(response.data.message || '创建配置失败')
      }
    } catch (err: any) {
      error.value = err.message || '创建配置失败'
      console.error('创建柜体配置失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 方法：更新配置（管理员）
  const updateConfig = async (id: number, data: Partial<CabinetTypeConfig>) => {
    loading.value = true
    error.value = null

    try {
      const response = await api.put(`/cabinet-type-configs/${id}`, data)
      if (response.data.code === 0) {
        const updatedConfig = response.data.data
        const index = configs.value.findIndex(c => c.id === id)
        if (index !== -1) {
          configs.value[index] = updatedConfig
        }
        configsMap.value.set(id, updatedConfig)
        
        // 清除相关规则缓存
        rulesCache.value.delete(id)
        
        return updatedConfig
      } else {
        throw new Error(response.data.message || '更新配置失败')
      }
    } catch (err: any) {
      error.value = err.message || '更新配置失败'
      console.error('更新柜体配置失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 方法：删除配置（管理员）
  const deleteConfig = async (id: number) => {
    loading.value = true
    error.value = null

    try {
      const response = await api.delete(`/cabinet-type-configs/${id}`)
      if (response.data.code === 0) {
        configs.value = configs.value.filter(c => c.id !== id)
        configsMap.value.delete(id)
        rulesCache.value.delete(id)
        return true
      } else {
        throw new Error(response.data.message || '删除配置失败')
      }
    } catch (err: any) {
      error.value = err.message || '删除配置失败'
      console.error('删除柜体配置失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 方法：清除缓存
  const clearCache = () => {
    configs.value = []
    configsMap.value.clear()
    rulesCache.value.clear()
    error.value = null
  }

  return {
    // 状态
    configs,
    configsMap,
    rulesCache,
    loading,
    error,
    
    // 计算属性
    activeConfigs,
    getConfigsByCategory,
    getConfigsByCabinetType,
    
    // 方法
    fetchConfigs,
    findConfig,
    fetchAutoMatchRules,
    searchConfigs,
    createConfig,
    updateConfig,
    deleteConfig,
    clearCache
  }
})
