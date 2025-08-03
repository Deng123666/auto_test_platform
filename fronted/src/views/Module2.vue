<template>
  <el-card class="module-card">
    <template #header>
      <div class="card-header">
        <h2>用例管理</h2>
        <el-button type="primary" size="small">添加用例</el-button>
      </div>
    </template>

    <el-table :data="testCases" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="用例名称" />
      <el-table-column prop="module" label="所属模块" />
      <el-table-column prop="status" label="状态">
        <template #default="scope">
          <el-tag :type="scope.row.status === '启用' ? 'success' : 'info'">
            {{ scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default>
          <el-button size="small">编辑</el-button>
          <el-button size="small" type="danger">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
interface TestCase {
  id: number;
  name: string;
  module: string;
  status: '启用' | '禁用';
}

const testCases = ref<TestCase[]>([
  { id: 1, name: '用户登录验证', module: '认证模块', status: '启用' },
  { id: 2, name: '创建新订单', module: '订单模块', status: '启用' },
  { id: 3, name: '支付流程验证', module: '支付模块', status: '禁用' },
])
</script>

<style scoped>
.module-card {
  min-height: calc(100vh - 100px);
}
</style>
