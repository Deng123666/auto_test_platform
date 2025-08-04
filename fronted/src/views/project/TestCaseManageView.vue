<template>
  <div class="projects-container">
    <div class="page-header">
      <h1 class="page-title">{{ projectName }} 用例管理</h1>
      <el-button
        type="primary"

        @click="handleAddTestCase"
        class="add-btn"
      >添加用例</el-button>
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
        :data="testCases"
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
              @click=""
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
// 保持原有的script逻辑完全不变
import { defineComponent, onMounted, ref, reactive, toRefs } from 'vue';
// import { fetchProjects, createProject, updateProject, deleteProject } from '@/api/projects';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useRouter, useRoute } from 'vue-router';
import { Folder, Warning, FolderDelete } from '@element-plus/icons-vue';
import { createTestCase, deleteTestCase, fetchTestCases, updateTestCase } from '@/api/test_cases';

interface TestCases {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

interface ApiResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: TestCases[];
}

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

    const testCases = ref<TestCases[]>([]);
    const projectId = Number(route.params.projectId);
    const projectName = ref(history.state?.projectName || "")
    console.log(projectId)
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

    const router = useRouter();
    // const goToProjectDetail = (project: Project) => {
    //   router.push({
    //     name: 'Cases',
    //     params: { projectId: project.id },
    //     state: { projectName: project.name }
    //   });
    // };

    const formTestCase = reactive<TestCases>({
      id: 0,
      name: '',
      description: '',
      created_at: '',
      updated_at: '',
    });

    const formRules = {
      name: [
        { required: true, message: '请输入用例名称', trigger: 'blur' },
        { max: 20, message: '用例名称不能超过20个字符', trigger: 'blur' }
      ],
      description: [
        { max: 200, message: '用例描述不能超过200个字符', trigger: 'blur' }
      ]
    };

    const getTestCases = async () => {
      loading.value = true;
      error.value = '';
      try {
        const response: ApiResponse = await fetchTestCases(projectId);
        // projects.value = response.results;
         testCases.value = response.results.sort((a, b) => a.id - b.id);
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
      dialogVisible.value = true;
      if (testCaseFormRef.value) {
        testCaseFormRef.value.resetFields();
      }
    };

    const handleEdit = (testCase: TestCases) => {
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

    const handleDelete = (testCase: TestCases) => {
      deleteProjectId.value = testCase.id;
      deleteProjectName.value = testCase.name;
      deleteDialogVisible.value = true;
    };

    // const submitTestCaseForm = async () => {
    //   if (!testCaseFormRef.value) return;

    //   try {
    //     await testCaseFormRef.value.validate();
    //     submitLoading.value = true;

    //     if (isEditMode.value) {
    //       await updateTestCase(formTestCase.id, {
    //         name: formTestCase.name,
    //         description: formTestCase.description
    //       });
    //       ElMessage.success('用例更新成功');
    //     } else {
    //       await createTestCase({
    //         name: formTestCase.name,
    //         description: formTestCase.description
    //       });
    //       ElMessage.success('用例创建成功');
    //     }

    //     dialogVisible.value = false;
    //     getTestCases();
    //   } catch (err) {
    //     if (err === false) {
    //       return;
    //     }
    //     error.value = isEditMode.value ? '更新用例失败，请稍后重试' : '创建用例失败，请稍后重试';
    //     console.error(err);
    //   } finally {
    //     submitLoading.value = false;
    //   }
    // };
    const submitTestCaseForm = async () => {
    if (!testCaseFormRef.value) return;

    try {
      await testCaseFormRef.value.validate();
      submitLoading.value = true;

      if (isEditMode.value) {
        await updateTestCase(formTestCase.id, {
          name: formTestCase.name,
          description: formTestCase.description,
          project: projectId
        });
        ElMessage.success('用例更新成功');
      } else {
        await createTestCase({
          name: formTestCase.name,
          description: formTestCase.description,
          project: projectId
        });
        ElMessage.success('用例创建成功');
      }

      dialogVisible.value = false;
      getTestCases();
    } catch (err) {
      if (err === false) {
        return;
      }
      const errorMsg = isEditMode.value ? '更新用例失败，请稍后重试' : '创建用例失败，请稍后重试';
      error.value = errorMsg;
      ElMessage.error(errorMsg);
      console.error(err);
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

    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleString();
    };

    onMounted(() => {
      getTestCases();
    });

    return {
      testCases,
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
      projectName,
      handleAddTestCase,
      handleEdit,
      handleDelete,
      submitTestCaseForm,
      confirmDelete,
      formatDate,
      getTestCases,
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
