import { ref, computed, watch, reactive, nextTick } from 'vue'
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
 * 项目和报表相关的逻辑
 */
export function useProjectDetail() {
  const route = useRoute()
  const projectStore = useProjectStore()

  const project = computed(() =>
    projectStore.projects.find((p) => p.id === Number(route.params.id))
  )
  const cabinets = computed(() => project.value?.cabinets || [])

  const excelLoading = ref(false)
  const pdfLoading = ref(false)
  const showBomImport = ref(false)

  async function reloadProject() {
    const projectId = Number(route.params.id)
    if (projectId) {
      await projectStore.reloadProject(projectId)
    }
  }

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
    reloadProject,
    generateExcel,
    generatePdf,
    onBomImported
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
 * 配电柜管理逻辑
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
      const newCabinet = res.data.data
      
      // 乐观更新：立即添加到本地数据
      if (project.value && project.value.cabinets) {
        project.value.cabinets.push(newCabinet)
      }
      
      showAddCabinet.value = false
      newCabinetForm.name = ''
      newCabinetForm.cabinetType = { control_category: '', cabinet_type: '', control_structure: '' }
      newCabinetForm.quotationMode = 'detailed'
      
      selectedCabinetId.value = newCabinet.id
      
      // 后台reload以确保数据一致性
      await reloadProject()
      
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
 * 结构组件管理逻辑
 */
export function useStructureManager(selectedCabinet: any, selectedCabinetId: any, reloadProject: () => Promise<void>) {
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
      
      console.log('创建结构组件，payload:', payload)
      const res = await componentApi.createStructure(payload)
      const newSc = res.data.data
      console.log('结构组件创建成功:', newSc)
      
      showAddStructure.value = false
      
      // 立即reload以显示新组件
      console.log('开始reload项目...')
      await reloadProject()
      console.log('reload完成')
      
      // 等待DOM更新后再设置选中状态
      await nextTick()
      selectedScId.value = newSc.id
      console.log('已选中新组件:', newSc.id)
      
      ElMessage.success('结构组件已创建')
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
      renamingScId.value = null
      await reloadProject()
    } catch {
      ElMessage.error('重命名失败')
      renamingScId.value = null
    }
  }

  async function deleteSc(sc: any) {
    await ElMessageBox.confirm(`确认删除组件「${sc.name}」？`, '警告', { type: 'warning' })
    try {
      await componentApi.deleteStructure(sc.id)
      if (selectedScId.value === sc.id) {
        const scs = selectedCabinet.value?.structure_components || []
        const remaining = scs.filter((s: any) => s.id !== sc.id)
        selectedScId.value = remaining.length > 0 ? remaining[0].id : null
      }
      await reloadProject()
      ElMessage.success('已删除')
    } catch {
      ElMessage.error('删除失败')
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
