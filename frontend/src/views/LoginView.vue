<template>
  <div class="login-wrapper">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
      <div class="grid-pattern"></div>
    </div>

    <div class="login-container">
      <!-- 左侧品牌区域 -->
      <div class="brand-section">
        <div class="brand-content">
          <div class="brand-icon">
            <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M32 8L8 20V44L32 56L56 44V20L32 8Z" stroke="currentColor" stroke-width="2.5" fill="none"/>
              <path d="M32 8V56M8 20L56 44M56 20L8 44" stroke="currentColor" stroke-width="2" opacity="0.5"/>
              <circle cx="32" cy="32" r="8" fill="currentColor" opacity="0.3"/>
            </svg>
          </div>
          <h1 class="brand-title">电气设备报价系统</h1>
          <p class="brand-subtitle">高效 · 精准 · 专业</p>
          <div class="brand-features">
            <div class="feature-item">
              <span class="feature-icon">⚡</span>
              <span>智能报价</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">📊</span>
              <span>数据分析</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">🔒</span>
              <span>安全可靠</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录表单区域 -->
      <div class="form-section">
        <div class="login-card">
          <div class="card-header">
            <h2>欢迎回来</h2>
            <p>请登录您的账户</p>
          </div>

          <el-form :model="form" @submit.prevent="handleLogin" label-position="top" class="login-form">
            <el-form-item label="用户名" prop="username">
              <el-input
                v-model="form.username"
                placeholder="请输入用户名"
                size="large"
                :prefix-icon="User"
              />
            </el-form-item>

            <el-form-item label="密码" prop="password">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                show-password
                :prefix-icon="Lock"
              />
            </el-form-item>

            <div class="form-options">
              <el-checkbox v-model="rememberMe">记住我</el-checkbox>
              <a href="#" class="forgot-link">忘记密码？</a>
            </div>

            <el-button
              type="primary"
              native-type="submit"
              :loading="loading"
              size="large"
              class="login-btn"
            >
              <span v-if="!loading">登 录</span>
            </el-button>
          </el-form>

          <div class="card-footer">
            <span>还没有账户？</span>
            <router-link to="/register" class="register-link">立即注册</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const rememberMe = ref(false)
const form = reactive({ username: '', password: '' })

async function handleLogin() {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    router.push('/')
  } catch {
    ElMessage.error('用户名或密码错误')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrapper {
  position: relative;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
  overflow: hidden;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(59, 130, 246, 0.05));
  animation: float 20s infinite ease-in-out;
}

.circle-1 {
  width: 600px;
  height: 600px;
  top: -200px;
  right: -100px;
  animation-delay: 0s;
}

.circle-2 {
  width: 400px;
  height: 400px;
  bottom: -150px;
  left: -100px;
  animation-delay: -5s;
}

.circle-3 {
  width: 300px;
  height: 300px;
  top: 50%;
  left: 30%;
  animation-delay: -10s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.05); }
  66% { transform: translate(-20px, 20px) scale(0.95); }
}

.grid-pattern {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px);
  background-size: 60px 60px;
}

/* 主容器 */
.login-container {
  position: relative;
  display: flex;
  min-height: 100vh;
  z-index: 1;
}

/* 左侧品牌区域 */
.brand-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.brand-content {
  text-align: center;
  color: #fff;
  max-width: 400px;
}

.brand-icon {
  width: 100px;
  height: 100px;
  margin: 0 auto 32px;
  color: var(--primary-color);
  animation: pulse-glow 3s infinite ease-in-out;
}

.brand-icon svg {
  width: 100%;
  height: 100%;
}

@keyframes pulse-glow {
  0%, 100% { filter: drop-shadow(0 0 20px rgba(14, 165, 233, 0.3)); }
  50% { filter: drop-shadow(0 0 40px rgba(14, 165, 233, 0.6)); }
}

.brand-title {
  font-family: var(--font-display);
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 16px;
  background: linear-gradient(90deg, #fff, var(--primary-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 2px;
}

.brand-subtitle {
  font-family: var(--font-body);
  font-size: 16px;
  color: var(--text-muted);
  margin-bottom: 48px;
  letter-spacing: 8px;
  text-transform: uppercase;
}

.brand-features {
  display: flex;
  justify-content: center;
  gap: 24px;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  min-width: 100px;
}

.feature-item:hover {
  background: rgba(14, 165, 233, 0.1);
  border-color: rgba(14, 165, 233, 0.3);
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.feature-icon {
  font-size: 28px;
}

.feature-item span:last-child {
  font-size: 13px;
  color: var(--text-regular);
  font-weight: 600;
}

/* 右侧表单区域 */
.form-section {
  width: 520px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.login-card {
  width: 100%;
  background: rgba(24, 24, 27, 0.7);
  border-radius: 24px;
  padding: 48px 40px;
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.card-header {
  text-align: center;
  margin-bottom: 40px;
}

.card-header h2 {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.card-header p {
  color: var(--text-muted);
  font-size: 15px;
}

/* 表单样式 */
.login-form {
  margin-bottom: 24px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 28px;
}

.login-form :deep(.el-form-item__label) {
  color: var(--text-regular);
  font-weight: 600;
  padding-bottom: 8px !important;
  font-size: 14px;
}

.login-form :deep(.el-input) {
  --el-input-border-radius: 12px;
}

.login-form :deep(.el-input__wrapper) {
  padding: 14px 16px;
  background-color: rgba(0, 0, 0, 0.2);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  transition: all 0.3s ease;
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.2) inset;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--primary-color) inset !important;
  background-color: rgba(14, 165, 233, 0.05);
}

.login-form :deep(.el-input__inner) {
  font-size: 16px;
  height: 24px;
  color: var(--text-primary);
}

.login-form :deep(.el-input__prefix .el-icon) {
  color: var(--text-muted);
  font-size: 18px;
}

/* 选项行 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.form-options :deep(.el-checkbox__label) {
  color: var(--text-muted);
  font-size: 14px;
}

.forgot-link {
  color: var(--primary-color);
  font-size: 14px;
  text-decoration: none;
  transition: color 0.2s;
}

.forgot-link:hover {
  color: var(--primary-hover);
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  height: 56px;
  font-size: 16px;
  font-weight: 700;
  font-family: var(--font-display);
  border-radius: 12px;
  background: linear-gradient(135deg, var(--primary-color) 0%, #0284c7 100%);
  border: none;
  box-shadow: 0 8px 20px rgba(14, 165, 233, 0.3);
  transition: all 0.3s ease;
  letter-spacing: 4px;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(14, 165, 233, 0.4);
}

.login-btn:active:not(:disabled) {
  transform: translateY(0);
}

/* 底部链接 */
.card-footer {
  text-align: center;
  color: var(--text-muted);
  font-size: 14px;
}

.register-link {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 600;
  margin-left: 4px;
  transition: color 0.2s;
}

.register-link:hover {
  color: var(--primary-hover);
}

/* 响应式 */
@media (max-width: 1024px) {
  .login-container {
    flex-direction: column;
  }

  .brand-section {
    padding: 60px 40px 40px;
  }

  .brand-title {
    font-size: 28px;
  }

  .brand-features {
    gap: 16px;
  }

  .feature-item {
    padding: 12px;
  }

  .feature-icon {
    font-size: 24px;
  }

  .form-section {
    width: 100%;
    padding: 0 40px 60px;
  }

  .login-card {
    max-width: 420px;
    margin: 0 auto;
  }
}

@media (max-width: 640px) {
  .brand-section {
    padding: 40px 24px 24px;
  }

  .brand-subtitle {
    font-size: 14px;
    letter-spacing: 4px;
  }

  .brand-features {
    flex-wrap: wrap;
    gap: 12px;
  }

  .form-section {
    padding: 0 20px 40px;
  }

  .login-card {
    padding: 32px 24px;
    border-radius: 20px;
  }

  .card-header h2 {
    font-size: 24px;
  }
}
</style>
