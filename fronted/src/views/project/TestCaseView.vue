<template>
  <div class="test-case-container">
    <div class="page-header">
      <h1>测试用例管理</h1>
      <!-- 搜索区域 -->
      <div class="search-container">
        <el-select
          v-model="selectedProjectId"
          filterable
          remote
          reserve-keyword
          placeholder="请选择项目"
          :remote-method="remoteSearchProjects"
          :loading="projectLoading"
          style="width: 240px; margin-right: 10px"
          @change="handleProjectChange"
        >
          <el-option
            v-for="project in projectOptions"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          ></el-option>
        </el-select>
        <el-button type="primary" icon="Search" @click="getTestCases">搜索</el-button>
      </div>
    </div>

    <!-- 测试用例表格 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="testCases"
        stripe
        style="width: 100%"
        empty-text="暂无测试用例数据"
      >
        <el-table-column prop="id" label="ID" width="80" style="text-align: center"></el-table-column>
        <el-table-column prop="name" label="用例名称" width="400" ></el-table-column>
        <el-table-column prop="project_name" label="所属项目" width="500"></el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="400" style="text-align: center">
          <template #default="scope">{{ formatDate(scope.row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="400" style="text-align: center">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              icon="Edit"
              @click="handleEdit(scope.row)"
              style="margin-right: 8px"
            >编辑</el-button>
            <el-button
              type="danger"
              size="small"
              icon="Edit"
              @click=""
              style="margin-right: 8px"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 错误提示 -->
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      :closable="true"
      class="error-alert"
    ></el-alert>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref, reactive, toRefs, watch } from 'vue';
import { useRoute } from 'vue-router';
import { fetchTestCases, createTestCase, updateTestCase, deleteTestCase } from '@/api/test_cases'; // 假设已有的API方法
import { fetchProjects } from '@/api/projects';
import { ElMessage } from 'element-plus';

interface Project {
  id: number;
  name: string;
}

interface TestCase {
  id: number;
  name: string;
  project_id: number;
  project_name: string;
  description: string;
  environment: string;
  created_at: string;
  // 其他测试用例相关字段
}

interface ApiResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: TestCase[];
}

export default defineComponent({
  name: 'TestCaseView',
  setup() {
    const route = useRoute();
    const testCases = ref<TestCase[]>([]);
    const loading = ref(false);
    const error = ref('');
    const projectOptions = ref<Project[]>([]);
    const projectLoading = ref(false);
    const selectedProjectId = ref<number | undefined>(undefined);

    // 从路由参数获取项目ID（如果有）
    const projectIdFromRoute = ref<number | undefined>(route.params.projectId ? Number(route.params.projectId) : undefined);

    // 初始化时如果有路由参数则设置选中项目
    onMounted(() => {
      if (projectIdFromRoute.value) {
        selectedProjectId.value = projectIdFromRoute.value;
        getTestCases();
      }
      // 获取项目列表用于下拉选择
      getProjects();
    });

    // 监听路由参数变化
    watch(
      () => route.params.projectId,
      (newVal) => {
        if (newVal) {
          selectedProjectId.value = Number(newVal);
          getTestCases();
        }
      }
    );

    // 获取项目列表（用于下拉选择）
    const getProjects = async () => {
      projectLoading.value = true;
      try {
        const response = await fetchProjects({ search: '' }); // 假设已有获取项目列表的API
        projectOptions.value = response.results;
        // 如果路由中有项目ID但下拉列表中还没有选项，等待选项加载后自动选择
        if (projectIdFromRoute.value && !selectedProjectId.value) {
          selectedProjectId.value = projectIdFromRoute.value;
          getTestCases();
        }
      } catch (err) {
        error.value = '获取项目列表失败，请稍后重试';
        console.error(err);
      } finally {
        projectLoading.value = false;
      }
    };

    // 远程搜索项目
    const remoteSearchProjects = async (query: string) => {
      if (query.length < 2) return;
      projectLoading.value = true;
      try {
        const response = await fetchProjects({ search: query }); // 假设支持搜索参数
        projectOptions.value = response.results;
      } catch (err) {
        ElMessage.error('搜索项目失败');
        console.error(err);
      } finally {
        projectLoading.value = false;
      }
    };

    // 获取测试用例数据
    const getTestCases = async () => {
      if (!selectedProjectId.value) {
        ElMessage.warning('请先选择项目');
        return;
      }

      loading.value = true;
      error.value = '';
      try {
        const response: ApiResponse = await fetchTestCases(
          selectedProjectId.value
        );
        testCases.value = response.results;
      } catch (err) {
        error.value = '获取测试用例失败，请稍后重试';
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    // 处理项目选择变化
    const handleProjectChange = () => {
      getTestCases();
    };

    // 查看测试步骤
    const handleViewSteps = (testCaseId: number) => {
      // 跳转到测试步骤页面或打开步骤详情对话框
      // 这里可以使用路由跳转，例如：
      // router.push({ name: 'TestSteps', params: { testCaseId } });
      ElMessage.success(`查看测试用例 ${testCaseId} 的步骤`);
    };

    // 编辑测试用例
    const handleEdit = (testCase: TestCase) => {
      // 实现编辑逻辑
      ElMessage.success(`编辑测试用例: ${testCase.name}`);
    };

    // 格式化日期
    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleString();
    };

    // 获取优先级标签类型
    // const getPriorityType = (priority: string) => {
    //   switch (priority.toLowerCase()) {
    //     case 'high':
    //       return 'danger';
    //     case 'medium':
    //       return 'warning';
    //     case 'low':
    //       return 'success';
    //     default:
    //       return 'info';
    //   }
    // };

    return {
      testCases,
      loading,
      error,
      projectOptions,
      projectLoading,
      selectedProjectId,
      getTestCases,
      handleProjectChange,
      handleViewSteps,
      handleEdit,
      formatDate,
      // getPriorityType,
      remoteSearchProjects
    };
  }
});
</script>

<style scoped>
.test-case-container {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-container {
  display: flex;
  align-items: center;
}

.table-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  overflow: hidden;
}

.error-alert {
  margin-top: 16px;
}
</style>
