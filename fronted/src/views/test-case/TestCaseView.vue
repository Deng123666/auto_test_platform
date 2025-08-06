<template>
  <div class="projects-container">
    <div class="page-header">
      <h1 class="page-title">{{ $route.query.projectName }} 用例管理 </h1>
      <div class="search-container">
        <el-input
          v-model="searchQuery"
          placeholder="请输入关键词搜索用例..."
          clearable
          style="width: 300px; margin-right: 16px;"
        />
        <el-button
          type="primary"
          @click="handleAddTestCase"
          class="add-btn"
        >添加用例</el-button>
      </div>
    </div>
    <el-alert v-if="error" :message="error" type="error" show-icon style="margin-bottom: 16px;"> 添加失败，请重试 </el-alert>
    <el-card class="modern-card">
      <div v-if="testCases.length === 0 && !loading" class="empty-state" style="height: 720px;">
        <el-icon :size="64" color="#C0C4CC"><FolderDelete /></el-icon>
        <p class="empty-text">空空如也~</p>
        <el-button type="primary" @click="handleAddTestCase">创建第一个用例</el-button>
      </div>

      <el-table
        v-else
        v-loading="loading"
        :data="filteredTestCases"
        stripe
        style="width: 100%"
        class="modern-table"
        :height="730"
      >
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
        <el-table-column prop="name" label="用例名称" width="280">
          <template #default="scope">
            <el-link
              type="primary"
              @click="goToTestCaseDetail(scope.row)"
              class="project-link"
            >
              <el-icon class="link-icon"><Folder /></el-icon>
              {{ scope.row.name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="用例描述" align="left">
          <template #default="scope">
            <div class="description-cell">
              <el-tooltip
                :content="scope.row.description || '无描述'"
                placement="top"
              >
                <span>{{ scope.row.description || '—' }}</span>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="projectName" label="项目" align="left">
          <template #default="scope">
            <div class="description-cell">
              <el-tooltip
                :content="scope.row.projectName || '无项目'"
                placement="top"
              >
                <span>{{ scope.row.projectName || '—' }}</span>
              </el-tooltip>
            </div>
           </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" align="left">
          <template #default="scope">
            <div class="timestamp">
              {{ formatDate(scope.row.created_at) }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180" align="left">
          <template #default="scope">
            <div class="timestamp">
              {{ formatDate(scope.row.updated_at) }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="scope">
            <el-button
              type="primary"


              @click="handleEdit(scope.row)"
              class="action-btn edit-btn"
            >编辑</el-button>
            <el-button
              type="danger"


              @click="handleDelete(scope.row)"
              class="action-btn"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEditMode ? '编辑用例' : '添加新用例'"
      :width="'500px'"
      :close-on-click-modal="false"
      class="modern-dialog"
    >
      <el-form
        ref="testCaseFormRef"
        :model="formTestCase"
        :rules="formRules"
        label-width="100px"
        label-position="top"
      >
        <el-form-item label="用例名称" prop="name">
          <el-input
            v-model="formTestCase.name"
            placeholder="请输入用例名称"
            clearable
          />
        </el-form-item>
        <!-- 添加项目选择下拉框 -->
        <el-form-item label="所属项目" prop="project">
          <el-select
            v-model="defaultProject"
            placeholder="请选择项目"
            filterable
            clearable
            :disabled="isProjectFixed"
            style="width: 100%"
          >
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="用例描述" prop="description">
          <el-input
            v-model="formTestCase.description"
            placeholder="请输入用例描述"
            type="textarea"
            :rows="4"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false" class="dialog-btn">取消</el-button>
        <el-button
          type="primary"
          @click="submitTestCaseForm"
          :loading="submitLoading"
          class="dialog-btn primary-btn"
        >
          {{ isEditMode ? '更新用例' : '创建用例' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除"
      :width="'480px'"
      :close-on-click-modal="false"
      class="delete-dialog"
    >
      <div class="delete-content">
        <el-icon color="#F56C6C" :size="48"><Warning /></el-icon>
        <div class="delete-text">
          <h3>确认删除用例吗？</h3>
          <p>您即将删除用例 <strong>{{ deleteProjectName }}</strong>，此操作不可撤销。</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="deleteDialogVisible = false" class="dialog-btn">取消</el-button>
        <el-button
          type="danger"
          @click="confirmDelete"
          :loading="deleteLoading"
          class="dialog-btn danger-btn"
        >确认删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref, reactive, toRefs, computed, watch } from 'vue';
// import { fetchProjects, createProject, updateProject, deleteProject } from '@/api/projects';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useRouter, useRoute } from 'vue-router';
import { Folder, Warning, FolderDelete } from '@element-plus/icons-vue';
import { createTestCase, deleteTestCase, fetchTestCases, updateTestCase } from '@/api/test_cases';
import { fetchProjects } from '@/api/projects';
import type { TestCase, Project, ApiResponse } from '@/types';

// interface TestCases {
//   id: number;
//   name: string;
//   description: string | null;
//   created_at: string;
//   updated_at: string;
//   project: number,
//   projectName: string,
// }

// interface Project {
//   id: number,
//   name: string
// }

// interface ApiResponse {
//   count: number;
//   next: string | null;
//   previous: string | null;
//   results: TestCases[];
// }

export default defineComponent({
  name: 'ProjectsView',
  components: {
    Folder,
    Warning,
    FolderDelete
  },
  setup() {
    // 原有的setup逻辑保持完全不变
    // const router = useRouter();
    const route = useRoute();

    const testCases = ref<TestCase[]>([]);
    const currentProjectName = route.query?.projectName;
    const currentProjectId = route.params.projectId;
    const projectName = ref('');
    const projects = ref<Project[]>([]);
    const loading = ref(false);
    const error = ref('');
    const dialogVisible = ref(false);
    const deleteDialogVisible = ref(false);
    const testCaseFormRef = ref();
    const submitLoading = ref(false);
    const deleteLoading = ref(false);
    const isEditMode = ref(false);
    const currentEditId = ref(0);
    const deleteProjectName = ref('');
    const deleteProjectId = ref(0);
    const searchQuery = ref(''); // 搜索关键词

    const router = useRouter();

    const defaultProject = computed({
      get() {
        // 当原数据为0时返回null，使选择框显示占位符
        return formTestCase.project || null;
      },
      set(val) {
        // 选择值时同步更新原数据
        formTestCase.project = val || 0;
      }
    });

    const formTestCase = reactive<TestCase>({
      id: 0,
      name: '',
      description: '',
      created_at: '',
      updated_at: '',
      project: 0,
      projectName: '',
    });

    const formRules = {
      name: [
        { required: true, message: '请输入用例名称', trigger: 'blur' },
        { max: 20, message: '用例名称不能超过20个字符', trigger: 'blur' }
      ],
      description: [
        { max: 200, message: '用例描述不能超过200个字符', trigger: 'blur' }
      ],
      project: [
        { required: true, message: '请选择项目', trigger: 'change' }
      ]
    };

    const isProjectFixed = computed(() => {
      return !!route.query.projectName;
    });

    // 获取路由中的 projectId（转为字符串类型）
    const currentRouteProjectId = computed(() => {
      return route.params.projectId?.toString();
    });

    const getTestCases = async () => {
      loading.value = true;
      error.value = '';
      try {
        // 先获取所有项目
        const projectsResponse = await fetchProjects();
        projects.value = projectsResponse.results;

        // 创建项目ID到名称的映射
        const projectMap = new Map(projects.value.map(p => [p.id, p.name]));

        // 获取路由中的 projectId 和 projectName
        const routeProjectId = route.params.projectId;
        const routeProjectName = route.query.projectName?.toString();

        // 若路由中存在 projectName，查找对应的项目 ID
        let finalProjectId = routeProjectId ? Number(routeProjectId) : null; // 修改：默认null而非0
        if (routeProjectName) {
          const matchedProject = projects.value.find(p => p.name === routeProjectName);
          if (matchedProject) {
            finalProjectId = matchedProject.id;
            // 如果是添加用例（非编辑模式），自动填充项目 ID 到表单
            if (!isEditMode.value) {
              formTestCase.project = finalProjectId;
            }
          } else {
            error.value = '未找到名称为 "' + routeProjectName + '" 的项目';
          }
        }

        // 获取测试用例数据并过滤（根据最终确定的项目 ID）
        const response: ApiResponse<TestCase> = await fetchTestCases();
        testCases.value = response.results
          .map(caseItem => ({
            ...caseItem,
            projectName: projectMap.get(caseItem.project) || '未知项目'
          }))
          // 修改：修复过滤逻辑，当finalProjectId为null时不过滤
          .filter(caseItem => finalProjectId === null || caseItem.project === finalProjectId)
          .sort((a, b) => a.id - b.id);
      } catch (err) {
        error.value = '获取用例列表失败，请稍后重试';
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    const handleAddTestCase = () => {
      isEditMode.value = false;
      formTestCase.id = 0;
      formTestCase.name = '';
      formTestCase.description = '';
      // 初始化项目字段为当前项目的 ID（转换为数字）
      if (route.params.projectId) {
        formTestCase.project = Number(route.params.projectId);
      }
      dialogVisible.value = true;
      if (testCaseFormRef.value) {
        testCaseFormRef.value.resetFields();
      }
    };

    const handleEdit = (testCase: TestCase) => {
      isEditMode.value = true;
      currentEditId.value = testCase.id;
      formTestCase.id = testCase.id;
      formTestCase.name = testCase.name;
      formTestCase.description = testCase.description || '';
      formTestCase.created_at = testCase.created_at;
      formTestCase.updated_at = testCase.updated_at;
      dialogVisible.value = true;
      if (testCaseFormRef.value) {
        testCaseFormRef.value.clearValidate();
      }
    };

    const handleDelete = (testCase: TestCase) => {
      deleteProjectId.value = testCase.id;
      deleteProjectName.value = testCase.name;
      deleteDialogVisible.value = true;
    };

    const submitTestCaseForm = async () => {
      if (!testCaseFormRef.value) return;

      try {
        await testCaseFormRef.value.validate();
        submitLoading.value = true;

        // 修复：确保project参数为数字类型且正确传递
        const requestData = {
          name: formTestCase.name,
          description: formTestCase.description,
          project: Number(formTestCase.project) // 强制转换为数字类型
        };

        console.log('提交参数:', requestData); // 添加调试日志

        if (isEditMode.value) {
          await updateTestCase(formTestCase.id, requestData);
          ElMessage.success('用例更新成功');
        } else {
          // 修复：仅使用表单中的project值，删除路由参数混合逻辑
          await createTestCase(requestData);
          ElMessage.success('用例创建成功');
        }

        dialogVisible.value = false;
        // 修复：确保数据刷新完成
        await getTestCases();
      } catch (err) {
        // 增强错误处理
        console.error('提交错误详情:', err);
        if (err instanceof Error) {
          ElMessage.error(`错误: ${err.message}`);
        } else if (typeof err === 'object' && err) {
          ElMessage.error(`请求失败: ${JSON.stringify(err)}`);
        } else {
          const errorMsg = isEditMode.value ? '更新用例失败，请稍后重试' : '创建用例失败，请稍后重试';
          error.value = errorMsg;
          ElMessage.error(errorMsg);
        }
      } finally {
        submitLoading.value = false;
      }
    };

    const confirmDelete = async () => {
      deleteLoading.value = true;
      try {
        await deleteTestCase(deleteProjectId.value);
        deleteDialogVisible.value = false;
        getTestCases();
        ElMessage.success('用例删除成功');
      } catch (err) {
        error.value = '删除用例失败，请稍后重试';
        console.error(err);
      } finally {
        deleteLoading.value = false;
      }
    };

    // 添加搜索过滤计算属性
    const filteredTestCases = computed(() => {
      const query = searchQuery.value.toLowerCase().trim();
      if (!query) return testCases.value;
      return testCases.value.filter(testCase =>
        testCase.name.toLowerCase().includes(query) ||
        (testCase.description && testCase.description.toLowerCase().includes(query)) ||
        testCase.projectName.toLowerCase().includes(query)
      );
    });

    const goToTestCaseDetail = (testCase: TestCase) => {
      router.push({
        name: 'CaseDetail',
        params: { testCaseId: testCase.id },
        state: { testCaseName: testCase.name }
      });
    };

    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleString();
    };

    onMounted(() => {
      getTestCases();
    });

    // 添加路由参数监听，参数变化时重新获取用例数据
    watch(
      // 监听影响用例过滤的路由参数
      () => [route.query.projectName, route.params.projectId],
      // 参数变化时执行的回调
      () => {
        getTestCases(); // 重新获取并过滤用例数据
      }
    );

    return {
      testCases,
      filteredTestCases,
      searchQuery,
      loading,
      error,
      dialogVisible,
      deleteDialogVisible,
      testCaseFormRef,
      submitLoading,
      deleteLoading,
      isEditMode,
      deleteProjectName,
      formTestCase,
      formRules,
      projects,
      currentProjectName,
      currentProjectId,
      isProjectFixed,
      defaultProject,
      handleAddTestCase,
      handleEdit,
      handleDelete,
      submitTestCaseForm,
      confirmDelete,
      formatDate,
      getTestCases,
      goToTestCaseDetail,
    };
  }
});
</script>

<style scoped>
.projects-container {
  padding: 24px;
  max-width: 1600px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: #1f2d3d;
  margin: 0;
}

.add-btn {
  background: linear-gradient(135deg, #4361ee, #3a0ca3);
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  box-shadow: 0 4px 6px rgba(67, 97, 238, 0.2);
  transition: all 0.3s ease;
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(67, 97, 238, 0.3);
}

.modern-card {
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  border: none;
  overflow: hidden;
}

.empty-state {
  padding: 60px 0;
  text-align: center;
  color: #909399;
}

.empty-text {
  margin: 16px 0 24px;
  font-size: 1.1rem;
}

.modern-table {
  --el-table-border-color: transparent;
  --el-table-header-bg-color: #f8fafc;
  --el-table-row-hover-bg-color: #f3f6ff;
}

.modern-table :deep(.el-table__header) th {
  background-color: #f8fafc;
  font-weight: 600;
  color: #2d3748;
}

.modern-table :deep(.el-table__row) {
  transition: background-color 0.2s ease;
}

.description-cell {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  color: #4a5568;
  line-height: 1.5;
}

.project-link {
  display: inline-flex;
  align-items: center;
  font-weight: 500;
  font-size: 1.05rem;
}

.link-icon {
  margin-right: 8px;
  color: #4361ee;
}

.timestamp {
  color: #718096;
  font-size: 0.9rem;
}

.action-btn {
  border-radius: 6px;
  padding: 7px 10px;
  margin-left: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.edit-btn {
  background-color: #e6f7ff;
  color: #1890ff;
  border-color: #91d5ff;
}

.action-btn:hover {
  transform: translateY(-1px);
}

.modern-dialog {
  border-radius: 14px;
}

.modern-dialog :deep(.el-dialog__header) {
  padding: 20px;
  border-bottom: 1px solid #eee;
  margin-right: 0;
}

.modern-dialog :deep(.el-dialog__body) {
  padding: 25px 20px;
}

.delete-dialog :deep(.el-dialog__header) {
  padding: 20px 20px 10px;
  border-bottom: none;
}

.delete-content {
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.delete-text {
  margin-left: 20px;
}

.delete-text h3 {
  margin: 0 0 8px;
  color: #1f2d3d;
}

.delete-text p {
  margin: 0;
  color: #5e6c82;
}

.dialog-btn {
  padding: 10px 20px;
  border-radius: 8px;
  min-width: 100px;
  transition: all 0.3s ease;
}a

.primary-btn {
  background: linear-gradient(135deg, #4361ee, #3a0ca3);
  border: none;
  box-shadow: 0 4px 6px rgba(67, 97, 238, 0.2);
}

.danger-btn {
  background: linear-gradient(135deg, #f43f5e, #e11d48);
  border: none;
  box-shadow: 0 4px 6px rgba(244, 63, 94, 0.2);
}

.dialog-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(67, 97, 238, 0.25);
}

.danger-btn:hover {
  box-shadow: 0 6px 12px rgba(244, 63, 94, 0.25);
}
</style>
