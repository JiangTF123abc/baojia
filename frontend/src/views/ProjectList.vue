<template>
  <div class="project-list-layout">
    <div class="tree-panel">
      <ProjectTree />
    </div>
    <div class="content-panel">
      <router-view />
      <div v-if="$route.name === 'Projects' || !$route.params.id" class="empty-hint">
        <el-empty description="请从左侧选择项目" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ProjectTree from '@/components/ProjectTree/index.vue'
</script>

<style scoped>
.project-list-layout {
  display: flex;
  height: 100%;
  overflow: hidden;
  background: var(--bg-panel);
}
.tree-panel {
  width: 280px;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  overflow-y: auto;
  flex-shrink: 0;
  background: rgba(0, 0, 0, 0.1);
}
.content-panel {
  flex: 1;
  overflow: hidden;
  position: relative;
  background: transparent;
}
.empty-hint {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  flex-direction: column;
}
.empty-hint :deep(.el-empty__description) {
  color: var(--text-muted);
  font-size: 16px;
  letter-spacing: 1px;
}
</style>
