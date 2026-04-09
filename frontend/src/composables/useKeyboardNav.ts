import { ref } from 'vue'

export function useKeyboardNav(cols: string[]) {
  const editingCell = ref<{ row: number; col: string } | null>(null)

  function startEdit(row: number, col: string) {
    editingCell.value = { row, col }
  }

  function stopEdit() {
    editingCell.value = null
  }

  function moveDown(rowCount: number) {
    if (!editingCell.value) return
    const { row, col } = editingCell.value
    if (row < rowCount - 1) editingCell.value = { row: row + 1, col }
  }

  function moveRight(rowCount: number) {
    if (!editingCell.value) return
    const { row, col } = editingCell.value
    const idx = cols.indexOf(col)
    if (idx < cols.length - 1) {
      editingCell.value = { row, col: cols[idx + 1] }
    } else if (row < rowCount - 1) {
      editingCell.value = { row: row + 1, col: cols[0] }
    }
  }

  function moveLeft() {
    if (!editingCell.value) return
    const { row, col } = editingCell.value
    const idx = cols.indexOf(col)
    if (idx > 0) {
      editingCell.value = { row, col: cols[idx - 1] }
    } else if (row > 0) {
      editingCell.value = { row: row - 1, col: cols[cols.length - 1] }
    }
  }

  function handleKeyDown(e: KeyboardEvent, rowCount: number) {
    if (!editingCell.value) return
    if (e.key === 'Enter') { e.preventDefault(); moveDown(rowCount) }
    else if (e.key === 'Tab' && !e.shiftKey) { e.preventDefault(); moveRight(rowCount) }
    else if (e.key === 'Tab' && e.shiftKey) { e.preventDefault(); moveLeft() }
  }

  return { editingCell, startEdit, stopEdit, moveDown, moveRight, moveLeft, handleKeyDown }
}
