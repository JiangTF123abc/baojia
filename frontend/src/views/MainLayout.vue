<template>
  <el-container style="height: 100vh">
    <el-aside width="240px" style="border-right: 1px solid #e4e7ed; overflow-y: auto">
      <div class="sidebar-header">
        <span>电气报价系统</span>
        <el-button link @click="auth.logout(); router.push('/login')">退出</el-button>
      </div>
      <el-menu :router="true" :default-active="route.path">
        <el-menu-item index="/projects">
          <el-icon><Folder /></el-icon>项目列表
        </el-menu-item>
        <el-menu-item index="/templates">
          <el-icon><Collection /></el-icon>模板库
        </el-menu-item>
        <el-menu-item v-if="auth.user?.role === 'admin'" index="/admin">
          <el-icon><Setting /></el-icon>管理面板
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-main style="padding: 0; overflow: hidden">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
</script>

<style scoped>
.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  font-weight: bold;
  border-bottom: 1px solid #e4e7ed;
}
</style>
