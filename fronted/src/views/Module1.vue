<template>
  <el-card class="module-card">
    <template #header>
      <div class="card-header">
        <h2>接口测试管理</h2>
      </div>
    </template>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="接口列表" name="list">
        <p>接口测试管理内容区域</p>
      </el-tab-pane>
      <el-tab-pane label="测试集合" name="collections">
        <p>测试集合管理</p>
      </el-tab-pane>
      <el-tab-pane label="执行历史" name="history">
        <p>历史执行记录</p>
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeTab = ref<string>('list')
</script>

<style scoped>
.module-card {
  min-height: calc(100vh - 100px);
}
</style>
