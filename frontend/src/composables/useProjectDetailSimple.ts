import { ref, computed, reactive, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useProjectStore } from '@/stores/project'
import { reportApi, cabinetApi, componentApi, priceApi } from '@/api'

/**
 * 获取配电柜基础成本（材料总价）
 */
export function getCabinetTotalNum(cabinet: any): number {
  return (cabinet.structure_components || []).reduce((sum: number, sc: any) => {
    return sum + (sc.base_components || []).reduce((s: number, bc: any) => {
      return s + (Number(bc.quantity) || 0) * (Number(bc.unit_price) || 0) * (Number(bc.discount_rate) || 1)
    }, 0)
  }, 0)
}

/**
 * 简化版：每次操作后完整reload，避免响应式问题
 */
export function useProjectDetail() {
  const route = useRoute()
  const projectStore = useProjectStore()

  // 使用ref而不是computed，以便在reload期间完全控制数据
  const project = ref<any>(null)
  const cabinets = ref<any[]>([])
  
  // 更新本地数据的函数
  function updateLocalData() {
    const projectId = Number(route.params.id)
    const found = projectStore.projects.find((p) => p.id === projectId)
    project.value = found || null
    cabinets.value = found?.cabinets || []
  }

  const excelLoading = ref(false)
  const pdfLoading = ref(false)
  const showBomImport = ref(false)
  const isReloading = ref(false)
  let reloadTimer: ReturnType<typeof setTimeout> | null = null

  // 普通reload：使用suspense模式平滑更新
  async function reloadProject() {
    if (isReloading.value) {
      console.log('reloadProject: 已有reload在进行中，跳过')
      return
    }
    
    isReloading.value = true
    
    try {
      // 加载新数据
      await projectStore.loadProjects()
      
      // 使用requestAnimationFrame确保在下一帧更新
      await new Promise(resolve => requestAnimationFrame(resolve))
      
      // 批量更新数据
      updateLocalData()
      
      // 再等一帧确保DOM更新完成
      await new Promise(resolve => requestAnimationFrame(resolve))
    } catch (error) {
      console.error('reloadProject失败:', error)
    } finally {
      isReloading.value = false
    }
  }
  
  // Debounced版本，用于频繁触发的场景（如表格编辑）
  function reloadProjectDebounced() {
    if (reloadTimer) {
      clearTimeout(reloadTimer)
    }
    reloadTimer = setTimeout(() => {
      reloadProject()
    }, 500)
  }
  
  // 初始化数据
  updateLocalData()
  
  // 监听路由变化更新数据
  watch(() => route.params.id, () => {
    if (!isReloading.value) {
      updateLocalData()
    }
  })

  async function generateExcel() {
    if (!project.value) return
    excelLoading.value = true
    try {
      const res = await reportApi.generateInternalPricing(project.value.id)
      const token = res.data.data.token
      window.open(reportApi.download(token))
    } catch {
      ElMessage.error('生成核价单失败')
    } finally {
      excelLoading.value = false
    }
  }

  async function generatePdf() {
    if (!project.value) return
    pdfLoading.value = true
    try {
      const res = await reportApi.generateCustomerQuotation(project.value.id)
      const token = res.data.data.token
      window.open(reportApi.download(token))
    } catch {
      ElMessage.error('生成报价单失败')
    } finally {
      pdfLoading.value = false
    }
  }

  async function onBomImported() {
    showBomImport.value = false
    await reloadProject()
    ElMessage.success('BOM导入成功')
  }

    return {
    project,
    cabinets,
    excelLoading,
    pdfLoading,
    showBomImport,
    isReloading,
    reloadProject,
    reloadProjectDebounced,
    generateExcel,
    generatePdf,
    onBomImported,
    projectStore,
    updateLocalData
  }
}

/**
 * 人工费用逻辑
 */
export function useLaborCost(cabinets: any) {
  const laborCostDetail = ref<any>(null)
  const loadingLaborCost = ref(false)

  async function loadLaborCost(cabinetId: number) {
    const cabinet = cabinets.value.find((c: any) => c.id === cabinetId)
    if (!cabinet) return

    const baseCost = getCabinetTotalNum(cabinet)

    // 检查是否有完整的配置
    if (!cabinet.control_category || !cabinet.cabinet_type || !cabinet.control_structure) {
      laborCostDetail.value = null
      return
    }

    loadingLaborCost.value = true
    try {
      const res = await priceApi.calculateLabor(cabinetId, baseCost)
      if (res.data.code === 0) {
        laborCostDetail.value = res.data.data.labor_cost_detail
      }
    } catch (err) {
      console.error('加载人工费用失败:', err)
      laborCostDetail.value = null
    } finally {
      loadingLaborCost.value = false
    }
  }

  return {
    laborCostDetail,
    loadingLaborCost,
    loadLaborCost
  }
}

/**
 * 配电柜管理逻辑 - 简化版
 */
export function useCabinetManager(project: any, cabinets: any, reloadProject: () => Promise<void>) {
  const selectedCabinetId = ref<number | null>(null)
  const showAddCabinet = ref(false)
  const showRenameCabinet = ref(false)
  const addingCabinet = ref(false)
  
  const newCabinetForm = reactive({
    name: '',
    cabinetType: { control_category: '', cabinet_type: '', control_structure: '' },
    quotationMode: 'detailed' as 'detailed' | 'quick'
  })
  const renameCabinetName = ref('')
  const renamingCabinetTarget = ref<any>(null)

  const cabinetMenu = reactive({
    visible: false,
    x: 0,
    y: 0,
    cabinet: null as any,
  })

  const selectedCabinet = computed(() =>
    cabinets.value.find((c: any) => c.id === selectedCabinetId.value) || null
  )

  function showCabinetMenu(event: MouseEvent, cabinet: any) {
    cabinetMenu.visible = true
    cabinetMenu.x = event.clientX
    cabinetMenu.y = event.clientY
    cabinetMenu.cabinet = cabinet
  }

  async function addCabinet() {
    if (!newCabinetForm.name.trim()) {
      ElMessage.warning('请输入配电柜名称')
      return
    }
    
    if (newCabinetForm.quotationMode === 'quick') {
      if (!newCabinetForm.cabinetType.control_category ||
          !newCabinetForm.cabinetType.cabinet_type ||
          !newCabinetForm.cabinetType.control_structure) {
        ElMessage.warning('快速报价模式需要选择完整的柜体类型')
        return
      }
    }
    
    addingCabinet.value = true
    try {
      const payload: any = {
        project_id: project.value!.id,
        name: newCabinetForm.name,
        quotation_mode: newCabinetForm.quotationMode
      }
      if (newCabinetForm.cabinetType.control_category) {
        Object.assign(payload, newCabinetForm.cabinetType)
      }
      
      const res = await cabinetApi.create(payload)
      const newCabinetId = res.data.data.id
      
      showAddCabinet.value = false
      newCabinetForm.name = ''
      newCabinetForm.cabinetType = { control_category: '', cabinet_type: '', control_structure: '' }
      newCabinetForm.quotationMode = 'detailed'
      
      // 先清空选中状态
      selectedCabinetId.value = null
      
      // 等待DOM更新
      await nextTick()
      
      // reload数据
      await reloadProject()
      
      // 等待数据更新后再选中
      await nextTick()
      selectedCabinetId.value = newCabinetId
      
      ElMessage.success(payload.quotation_mode === 'quick' ? '配电柜已创建，元器件已自动匹配' : '配电柜已创建')
    } catch (err: any) {
      ElMessage.error(err.response?.data?.message || '创建失败')
    } finally {
      addingCabinet.value = false
    }
  }

  function renameCabinet(cabinet: any) {
    cabinetMenu.visible = false
    renamingCabinetTarget.value = cabinet
    renameCabinetName.value = cabinet.name
    showRenameCabinet.value = true
  }

  async function confirmRenameCabinet() {
    if (!renameCabinetName.value.trim()) return
    try {
      await cabinetApi.update(renamingCabinetTarget.value.id, {
        name: renameCabinetName.value,
        version: renamingCabinetTarget.value.version,
      })
      showRenameCabinet.value = false
      await reloadProject()
      ElMessage.success('已重命名')
    } catch {
      ElMessage.error('重命名失败')
    }
  }

  async function copyCabinet(cabinet: any) {
    cabinetMenu.visible = false
    try {
      await cabinetApi.copy(cabinet.id)
      await reloadProject()
      ElMessage.success('配电柜已复制')
    } catch {
      ElMessage.error('复制失败')
    }
  }

  async function deleteCabinet(cabinet: any) {
    cabinetMenu.visible = false
    await ElMessageBox.confirm(`确认删除配电柜「${cabinet.name}」？此操作不可撤销。`, '警告', { type: 'warning' })
    try {
      await cabinetApi.delete(cabinet.id)
      if (selectedCabinetId.value === cabinet.id) {
        selectedCabinetId.value = null
      }
      await reloadProject()
      ElMessage.success('已删除')
    } catch {
      ElMessage.error('删除失败')
    }
  }

  return {
    selectedCabinetId,
    selectedCabinet,
    showAddCabinet,
    showRenameCabinet,
    addingCabinet,
    newCabinetForm,
    renameCabinetName,
    cabinetMenu,
    showCabinetMenu,
    addCabinet,
    renameCabinet,
    confirmRenameCabinet,
    copyCabinet,
    deleteCabinet
  }
}

/**
 * 结构组件管理逻辑 - 简化版
 */
export function useStructureManager(selectedCabinet: any, selectedCabinetId: any, reloadProject: () => Promise<void>, projectStore: any, updateLocalData: () => void) {
  const selectedScId = ref<number | null>(null)
  const showAddStructure = ref(false)
  const renamingScId = ref<number | null>(null)
  const renamingScName = ref('')
  const renameInputRef = ref()
  const newStructureForm = reactive({ name: '', circuit_type: '' })

  const selectedSc = computed(() =>
    (selectedCabinet.value?.structure_components || []).find((sc: any) => sc.id === selectedScId.value) || null
  )

  async function addStructureComponent() {
    if (!selectedCabinetId.value) return
    const cabinet = selectedCabinet.value
    if (cabinet && cabinet.control_structure === '非标控制') {
      newStructureForm.name = `组件${(cabinet.structure_components?.length || 0) + 1}`
      newStructureForm.circuit_type = ''
      showAddStructure.value = true
    } else {
      await createStructureComponent()
    }
  }

  async function createStructureComponent() {
    if (!selectedCabinetId.value) return
    const cabinet = selectedCabinet.value
    const isNonStandard = cabinet && cabinet.control_structure === '非标控制'
    
    if (isNonStandard && showAddStructure.value && !newStructureForm.circuit_type) {
      ElMessage.warning('请选择回路类型')
      return
    }
    
    try {
      const payload: any = {
        cabinet_id: selectedCabinetId.value,
        name: showAddStructure.value ? newStructureForm.name : `组件${(cabinet?.structure_components?.length || 0) + 1}`,
      }
      if (isNonStandard && newStructureForm.circuit_type) {
        payload.circuit_type = newStructureForm.circuit_type
      }
      
      // 先调用API创建
      const res = await componentApi.createStructure(payload)
      const newSc = res.data.data
      
      showAddStructure.value = false
      ElMessage.success('结构组件已创建')
      
      // 乐观更新：直接添加到本地数据
      if (cabinet && cabinet.structure_components) {
        cabinet.structure_components.push(newSc)
      }
      
      // 后台同步完整数据（忽略可能的错误）
      setTimeout(async () => {
        try {
          await projectStore.loadProjects()
          updateLocalData()
        } catch (e) {
          // 忽略错误
        }
      }, 100)
    } catch (error) {
      console.error('创建结构组件失败:', error)
      ElMessage.error('创建失败')
    }
  }

  function startRenameTab(sc: any) {
    renamingScId.value = sc.id
    renamingScName.value = sc.name
    nextTick(() => { renameInputRef.value?.focus?.() })
  }

  async function confirmRenameTab(sc: any) {
    if (!renamingScName.value.trim()) {
      renamingScId.value = null
      return
    }
    try {
      await componentApi.updateStructure(sc.id, { name: renamingScName.value, version: sc.version })
      
      // 乐观更新：直接修改本地数据
      sc.name = renamingScName.value
      renamingScId.value = null
      
      // 后台同步
      setTimeout(async () => {
        try {
          await projectStore.loadProjects()
          updateLocalData()
        } catch (e) {
          // 忽略错误
        }
      }, 100)
    } catch {
      ElMessage.error('重命名失败')
      renamingScId.value = null
    }
  }

  async function deleteSc(sc: any) {
    await ElMessageBox.confirm(`确认删除组件「${sc.name}」？`, '警告', { type: 'warning' })
    
    try {
      await componentApi.deleteStructure(sc.id)
      ElMessage.success('已删除')
      
      // 乐观更新：直接从本地数据中移除
      const cabinet = selectedCabinet.value
      if (cabinet && cabinet.structure_components) {
        const index = cabinet.structure_components.findIndex((s: any) => s.id === sc.id)
        if (index >= 0) {
          cabinet.structure_components.splice(index, 1)
        }
      }
      
      // 后台同步
      setTimeout(async () => {
        try {
          await projectStore.loadProjects()
          updateLocalData()
        } catch (e) {
          // 忽略错误
        }
      }, 100)
    } catch (error: any) {
      if (error.response?.status === 404) {
        ElMessage.success('已删除')
        // 同样做乐观更新
        const cabinet = selectedCabinet.value
        if (cabinet && cabinet.structure_components) {
          const index = cabinet.structure_components.findIndex((s: any) => s.id === sc.id)
          if (index >= 0) {
            cabinet.structure_components.splice(index, 1)
          }
        }
      } else {
        ElMessage.error('删除失败')
      }
    }
  }

  return {
    selectedScId,
    selectedSc,
    showAddStructure,
    newStructureForm,
    renamingScId,
    renamingScName,
    renameInputRef,
    addStructureComponent,
    createStructureComponent,
    startRenameTab,
    confirmRenameTab,
    deleteSc
  }
}
