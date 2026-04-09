import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { componentApi } from '@/api'

export function useQuotationTable(props: any, emit: any) {
  const rows = ref<any[]>(props.initialRows ? [...props.initialRows] : [])
  const selectedRows = ref<any[]>([])
  const editingCell = ref<{ row: number; col: string } | null>(null)
  const showBatchDiscount = ref(false)
  const batchDiscountValue = ref(1)
  const showHidden = ref(false)

  const COLS = ['model_number', 'name', 'specification', 'quantity', 'unit_price', 'discount_rate']

  watch(() => props.initialRows, (newRows) => {
    if (newRows) {
      // 保留编辑状态，只更新数据
      const currentEditingId = editingCell.value ? rows.value[editingCell.value.row]?.id : null
      rows.value = [...newRows]
      
      // 恢复编辑状态
      if (currentEditingId && editingCell.value) {
        const newIndex = rows.value.findIndex(r => r.id === currentEditingId)
        if (newIndex >= 0) {
          editingCell.value.row = newIndex
        } else {
          editingCell.value = null
        }
      }
    }
  }, { flush: 'post' })

  // 过滤可见行（根据 is_hidden 字段）
  const visibleRows = computed(() => {
    if (showHidden.value) {
      return rows.value
    }
    return rows.value.filter(row => !row.is_hidden)
  })

  const totalPrice = computed(() => {
    const sum = visibleRows.value.reduce((acc, row) => acc + calcRowTotalNum(row), 0)
    return sum.toFixed(2)
  })

  // 行样式类名
  function getRowClassName({ row }: { row: any }) {
    if (row.is_hidden) {
      return 'hidden-row'
    }
    return ''
  }

  function calcRowTotalNum(row: any): number {
    return (Number(row.quantity) || 0) * (Number(row.unit_price) || 0) * (Number(row.discount_rate) || 1)
  }

  function calcRowTotal(row: any): string {
    return calcRowTotalNum(row).toFixed(2)
  }

  function startEdit(rowIdx: number, col: string) {
    editingCell.value = { row: rowIdx, col }
  }

  function moveDown(rowIdx: number, col: string) {
    if (rowIdx < rows.value.length - 1) {
      editingCell.value = { row: rowIdx + 1, col }
    }
  }

  function moveRight(rowIdx: number, col: string) {
    const idx = COLS.indexOf(col)
    if (idx < COLS.length - 1) {
      editingCell.value = { row: rowIdx, col: COLS[idx + 1] }
    } else if (rowIdx < rows.value.length - 1) {
      editingCell.value = { row: rowIdx + 1, col: COLS[0] }
    }
  }

  function handleKeyDown(e: KeyboardEvent) {
    if (!editingCell.value) return
    const { row, col } = editingCell.value
    if (e.key === 'Tab' && !e.shiftKey) {
      e.preventDefault()
      moveRight(row, col)
    } else if (e.key === 'Tab' && e.shiftKey) {
      e.preventDefault()
      const idx = COLS.indexOf(col)
      if (idx > 0) editingCell.value = { row, col: COLS[idx - 1] }
      else if (row > 0) editingCell.value = { row: row - 1, col: COLS[COLS.length - 1] }
    }
  }

  async function saveCell(row: any) {
    editingCell.value = null
    if (!row.id) return
    try {
      await componentApi.updateBase(row.id, {
        model_number: row.model_number,
        name: row.name,
        specification: row.specification,
        quantity: row.quantity,
        unit_price: row.unit_price,
        discount_rate: row.discount_rate,
        version: row.version,
      })
      row.version = (row.version || 1) + 1
      // 保存后触发change以更新总价和人工费
      emit('change')
    } catch (err: any) {
      if (err.response?.status === 409) {
        ElMessage.warning('数据已被他人修改，请刷新后重试')
        emit('change')
      }
    }
  }

  function fillFromMaterial(row: any, material: any) {
    row.model_number = material.model_number
    row.name = material.name
    row.specification = material.specification
    row.unit_price = material.unit_price
    row.material_id = material.id
  }

  async function addRow() {
    try {
      const res = await componentApi.createBase({
        structure_component_id: props.structureComponentId,
        model_number: '',
        name: '',
        quantity: 1,
        unit_price: 0,
        discount_rate: 1,
      })
      // 立即添加到本地数组，提供即时反馈
      const newRow = res.data.data
      rows.value.push(newRow)
      // 触发change更新总价
      emit('change')
    } catch {
      ElMessage.error('添加失败')
    }
  }

  async function deleteRow(row: any) {
    await ElMessageBox.confirm('确认删除此元器件？', '警告', { type: 'warning' })
    try {
      if (row.id) await componentApi.deleteBase(row.id)
      rows.value = rows.value.filter((r) => r.id !== row.id)
      // 删除后触发change以更新总价
      emit('change')
    } catch {
      ElMessage.error('删除失败')
    }
  }

  // 性能优化：使用 Promise.all 并发删除
  async function batchDelete() {
    await ElMessageBox.confirm(`确认删除选中的 ${selectedRows.value.length} 条记录？`, '警告', { type: 'warning' })
    try {
      await Promise.all(
        selectedRows.value.map(row => (row.id ? componentApi.deleteBase(row.id) : Promise.resolve()))
      )
      const ids = new Set(selectedRows.value.map((r) => r.id))
      rows.value = rows.value.filter((r) => !ids.has(r.id))
      selectedRows.value = []
      emit('change')
      ElMessage.success('批量删除成功')
    } catch {
      ElMessage.error('批量删除失败，部分记录可能未删除')
    }
  }

  // 性能优化：使用 Promise.all 并发保存
  async function applyBatchDiscount() {
    showBatchDiscount.value = false
    try {
      await Promise.all(
        selectedRows.value.map(async (row) => {
          row.discount_rate = batchDiscountValue.value
          await saveCell(row)
        })
      )
      ElMessage.success('批量修改折扣率成功')
    } catch {
      ElMessage.error('批量修改折扣率失败')
    }
  }

  return {
    rows,
    selectedRows,
    editingCell,
    showBatchDiscount,
    batchDiscountValue,
    showHidden,
    visibleRows,
    totalPrice,
    getRowClassName,
    calcRowTotal,
    startEdit,
    moveDown,
    moveRight,
    handleKeyDown,
    saveCell,
    fillFromMaterial,
    addRow,
    deleteRow,
    batchDelete,
    applyBatchDiscount
  }
}
