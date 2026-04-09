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
}
.tree-panel {
  width: 260px;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
  flex-shrink: 0;
}
.content-panel {
  flex: 1;
  overflow: hidden;
  position: relative;
}
.empty-hint {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
</style>
