<template>
  <el-container class="h-screen">
    <!-- 侧边栏区域 -->
    <el-aside width="auto">
      <Sidebar />
    </el-aside>

    <!-- 主内容区域 -->
    <el-main>
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import Sidebar from './Sidebar.vue'
</script>

<style scoped>
.el-aside {
  transition: width 0.3s ease;
}

.el-main {
  padding: 20px;
  background-color: #f0f2f5;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
