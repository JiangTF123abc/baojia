<template>
  <el-container class="dashboard-layout">
    <!-- Sidebar -->
    <el-aside width="260px" class="glass-sidebar">
      <div class="sidebar-header">
        <div class="brand-logo">
          <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" class="logo-svg">
            <path d="M32 8L8 20V44L32 56L56 44V20L32 8Z" stroke="currentColor" stroke-width="2.5" fill="none"/>
            <path d="M32 8V56M8 20L56 44M56 20L8 44" stroke="currentColor" stroke-width="2" opacity="0.5"/>
            <circle cx="32" cy="32" r="8" fill="currentColor" opacity="0.3"/>
          </svg>
        </div>
        <span class="brand-text">EEQS<span class="highlight">.</span>PRO</span>
      </div>

      <div class="menu-container">
        <el-menu :router="true" :default-active="route.path" class="custom-menu">
          <div class="menu-label">主要功能</div>
          <el-menu-item index="/projects">
            <el-icon><Folder /></el-icon>项目列表
          </el-menu-item>
          <el-menu-item index="/templates">
            <el-icon><Collection /></el-icon>模板库
          </el-menu-item>
          
          <div v-if="auth.user?.role === 'admin'" class="menu-label mt-6">系统管理</div>
          <el-menu-item v-if="auth.user?.role === 'admin'" index="/admin">
            <el-icon><Setting /></el-icon>管理面板
          </el-menu-item>
        </el-menu>
      </div>

      <div class="sidebar-footer">
        <div class="user-profile">
          <div class="avatar">{{ auth.user?.username?.charAt(0).toUpperCase() || 'U' }}</div>
          <div class="user-info">
            <span class="username">{{ auth.user?.username || 'User' }}</span>
            <span class="role">{{ auth.user?.role === 'admin' ? 'Administrator' : 'User' }}</span>
          </div>
        </div>
        <el-button class="logout-btn" @click="handleLogout" title="退出登录">
          <el-icon><SwitchButton /></el-icon>
        </el-button>
      </div>
    </el-aside>

    <!-- Main Content -->
    <el-container class="main-container">
      <el-header class="top-header" height="64px">
        <div class="header-left">
          <h2 class="page-title">{{ currentRouteName }}</h2>
        </div>
        <div class="header-right">
          <div class="system-status">
            <span class="status-dot"></span>
            <span class="status-text">System Online</span>
          </div>
        </div>
      </el-header>

      <el-main class="main-content">
        <div class="content-wrapper">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Folder, Collection, Setting, SwitchButton } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const handleLogout = () => {
  auth.logout()
  router.push('/login')
}

const currentRouteName = computed(() => {
  const path = route.path
  if (path.startsWith('/projects')) return '项目列表 (Projects)'
  if (path.startsWith('/templates')) return '模板库 (Templates)'
  if (path.startsWith('/admin')) return '管理面板 (Admin Panel)'
  return '仪表盘 (Dashboard)'
})
</script>

<style scoped>
.dashboard-layout {
  height: 100vh;
  background-color: var(--bg-dark);
  background-image: radial-gradient(circle at 50% 0%, rgba(14, 165, 233, 0.05), transparent 50%);
}

.glass-sidebar {
  display: flex;
  flex-direction: column;
  background: rgba(24, 24, 27, 0.6);
  backdrop-filter: blur(16px);
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.2);
  z-index: 10;
}

.sidebar-header {
  height: 80px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.brand-logo {
  width: 32px;
  height: 32px;
  color: var(--primary-color);
  margin-right: 12px;
  filter: drop-shadow(0 0 8px rgba(14, 165, 233, 0.4));
}

.brand-text {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 1px;
}

.brand-text .highlight {
  color: var(--primary-color);
}

.menu-container {
  flex: 1;
  padding: 24px 12px;
  overflow-y: auto;
}

.menu-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: var(--text-muted);
  margin: 0 12px 12px;
  font-weight: 600;
}

.mt-6 {
  margin-top: 32px;
}

.custom-menu {
  border-right: none;
  background: transparent;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(0, 0, 0, 0.2);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--primary-color), #3b82f6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.3);
}

.user-info {
  display: flex;
  flex-direction: column;
}

.username {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.role {
  font-size: 12px;
  color: var(--text-muted);
}

.logout-btn {
  background: transparent !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: var(--text-muted) !important;
  width: 36px;
  height: 36px;
  padding: 0;
  border-radius: 10px;
  transition: all 0.3s;
  box-shadow: none !important;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.1) !important;
  color: #ef4444 !important;
  border-color: rgba(239, 68, 68, 0.3) !important;
}

.main-container {
  display: flex;
  flex-direction: column;
  background: transparent;
}

.top-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  background: rgba(24, 24, 27, 0.4);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.page-title {
  margin: 0;
  font-size: 20px;
  color: var(--text-primary);
}

.system-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 20px;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #10b981;
  box-shadow: 0 0 8px #10b981;
  animation: pulse 2s infinite;
}

.status-text {
  font-size: 12px;
  font-weight: 600;
  color: #10b981;
  letter-spacing: 0.5px;
}

@keyframes pulse {
  0% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
  100% { opacity: 1; transform: scale(1); }
}

.main-content {
  padding: 24px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  flex: 1;
  background: var(--bg-panel);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  position: relative;
}

/* Page Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
