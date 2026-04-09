<template>
  <div class="bom-import">
    <!-- 拖拽上传区域 -->
    <el-upload
      v-if="!previewData"
      drag
      :auto-upload="false"
      accept=".xlsx,.xls"
      :on-change="handleFileChange"
      :show-file-list="false"
    >
      <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
      <div class="el-upload__text">拖拽 Excel BOM 文件到此处，或 <em>点击上传</em></div>
      <template #tip>
        <div class="el-upload__tip">支持 .xlsx / .xls 格式，列需包含：型号、名称、数量、规格</div>
      </template>
    </el-upload>

    <!-- 解析预览 -->
    <div v-if="previewData" class="preview">
      <div class="preview-header">
        <span>解析结果：共 {{ previewData.length }} 行</span>
        <div>
          <el-button size="small" @click="previewData = null">重新上传</el-button>
          <el-button size="small" type="primary" :loading="importing" @click="confirmImport">
            确认导入
          </el-button>
        </div>
      </div>
      <el-table :data="previewData" border size="small" max-height="400">
        <el-table-column label="型号" prop="model_number" min-width="120" />
        <el-table-column label="名称" prop="name" min-width="120" />
        <el-table-column label="规格" prop="specification" min-width="120" />
        <el-table-column label="数量" prop="quantity" width="80" />
        <el-table-column label="单价" prop="unit_price" width="90" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.matched ? 'success' : 'warning'" size="small">
              {{ row.matched ? '已匹配' : '待确认' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 错误信息 -->
    <el-alert v-if="errorMsg" :title="errorMsg" type="error" show-icon style="margin-top: 8px" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { bomApi } from '@/api'

const props = defineProps<{ projectId: number }>()
const emit = defineEmits<{ (e: 'imported'): void }>()

const previewData = ref<any[] | null>(null)
const errorMsg = ref('')
const importing = ref(false)
let uploadedData: any = null

async function handleFileChange(file: any) {
  errorMsg.value = ''
  try {
    const res = await bomApi.upload(file.raw)
    if (res.data.code !== 0) {
      errorMsg.value = res.data.message || '解析失败'
      return
    }
    previewData.value = res.data.data.rows || []
    uploadedData = res.data.data
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || '文件格式无效，请检查列名是否正确'
  }
}

async function confirmImport() {
  if (!uploadedData) return
  importing.value = true
  try {
    await bomApi.confirm({ project_id: props.projectId, rows: previewData.value })
    ElMessage.success('BOM 导入成功')
    previewData.value = null
    emit('imported')
  } catch (err: any) {
    errorMsg.value = err.response?.data?.message || '导入失败'
  } finally {
    importing.value = false
  }
}
</script>

<style scoped>
.bom-import { padding: 16px; }
.preview-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 8px; font-size: 13px; color: #606266;
}
</style>
