<template>
  <div class="full-page-content">
    <div class="content-header">
      <h2>接口自动化测试平台</h2>
    </div>

    <el-row :gutter="20" class="content-row">
      <el-col :span="8">
        <div class="content-block">
          <h3>项目概览</h3>
          <p>测试项目: 5个</p>
          <p>接口用例: 120个</p>
          <p>通过率: 92.3%</p>
        </div>
      </el-col>
      <el-col :span="16">
        <div class="content-block">
          <h3>最近执行记录</h3>
          <el-table :data="recentRuns">
            <!-- 表格列保持不变 -->
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.full-page-content {
  padding: 20px;
  height: 100%;
}

.content-header {
  margin-bottom: 20px;
}

.content-block {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  height: 100%;
}

.content-row {
  margin-bottom: 20px;
}
</style>
