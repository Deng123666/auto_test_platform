<template>
  <div class="projects-container">
    <div class="page-header">
      <h1 class="page-title">项目管理</h1>
      <el-button
        type="primary"
        @click="handleAddProject"
        class="add-btn"
      >添加项目</el-button>
    </div>

    <el-card class="modern-card">
      <div v-if="projects.length === 0 && !loading" class="empty-state" style="height: 720px;">
        <el-icon :size="100" color="#C0C4CC"><FolderDelete /></el-icon>
        <p class="empty-text">空空如也~</p>
        <el-button type="primary" @click="handleAddProject">创建第一个项目</el-button>
      </div>

      <el-table
        v-else
        v-loading="loading"
        :data="projects"
        stripe
        style="width: 100%"
        class="modern-table"
        :height="750"
      >
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
        <el-table-column prop="name" label="项目名称" width="280">
          <template #default="scope">
            <el-link
              type="primary"
              @click="goToProjectDetail(scope.row)"
              class="project-link"
            >
              <el-icon class="link-icon"><Folder /></el-icon>
              {{ scope.row.name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="项目描述" align="left">
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
      :title="isEditMode ? '编辑项目' : '添加新项目'"
      :width="'500px'"
      :close-on-click-modal="false"
      class="modern-dialog"
    >
      <el-form
        ref="projectFormRef"
        :model="formProject"
        :rules="formRules"
        label-width="100px"
        label-position="top"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input
            v-model="formProject.name"
            placeholder="请输入项目名称"
            clearable
          />
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="formProject.description"
            placeholder="请输入项目描述"
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
          @click="submitProjectForm"
          :loading="submitLoading"
          class="dialog-btn primary-btn"
        >
          {{ isEditMode ? '更新项目' : '创建项目' }}
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
          <h3>确认删除项目吗？</h3>
          <p>您即将删除项目 <strong>{{ deleteProjectName }}</strong>，此操作不可撤销。</p>
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
import { defineComponent, onMounted, ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import { Folder, Warning, FolderDelete } from '@element-plus/icons-vue';
import { useProjectStore } from '@/stores/project';
import type { Project } from '@/types';

export default defineComponent({
  name: 'ProjectsView',
  components: {
    Folder,
    Warning,
    FolderDelete
  },
  setup() {
    const projectStore = useProjectStore();
    const router = useRouter();

    const dialogVisible = ref(false);
    const deleteDialogVisible = ref(false);
    const projectFormRef = ref();
    const submitLoading = ref(false);
    const deleteLoading = ref(false);
    const isEditMode = ref(false);
    const currentEditId = ref(0);
    const deleteProjectName = ref('');
    const deleteProjectId = ref(0);
    const isInitialized = ref(false);

    const goToProjectDetail = (project: Project) => {
      router.push({
        name: 'ProjectDetailCases',
        params: { projectId: project.id },
        query: { projectName: project.name }
      });
    };

    const formProject = reactive<Project>({
      id: 0,
      name: '',
      description: '',
      created_at: '',
      updated_at: ''
    });

    const formRules = {
      name: [
        { required: true, message: '请输入项目名称', trigger: 'blur' },
        { max: 20, message: '项目名称不能超过20个字符', trigger: 'blur' }
      ],
      description: [
        { max: 200, message: '项目描述不能超过200个字符', trigger: 'blur' }
      ]
    };

    const handleAddProject = () => {
      isEditMode.value = false;
      formProject.id = 0;
      formProject.name = '';
      formProject.description = '';
      dialogVisible.value = true;
      if (projectFormRef.value) {
        projectFormRef.value.resetFields();
      }
    };

    const handleEdit = (project: Project) => {
      isEditMode.value = true;
      currentEditId.value = project.id;
      formProject.id = project.id;
      formProject.name = project.name;
      formProject.description = project.description || '';
      formProject.created_at = project.created_at;
      formProject.updated_at = project.updated_at;
      dialogVisible.value = true;
      if (projectFormRef.value) {
        projectFormRef.value.clearValidate();
      }
    };

    const handleDelete = (project: Project) => {
      deleteProjectId.value = project.id;
      deleteProjectName.value = project.name;
      deleteDialogVisible.value = true;
    };

    const submitProjectForm = async () => {
      if (!projectFormRef.value) return;

      try {
        await projectFormRef.value.validate();
        submitLoading.value = true;

        if (isEditMode.value) {
          await projectStore.updateProject(formProject.id, {
            name: formProject.name,
            description: formProject.description
          });
          ElMessage.success('项目更新成功');
        } else {
          await projectStore.createProject({
            name: formProject.name,
            description: formProject.description
          });
          ElMessage.success('项目创建成功');
        }

        dialogVisible.value = false;
      } catch (err) {
        if (err === false) {
          return;
        }
        console.error(err);
      } finally {
        submitLoading.value = false;
      }
    };

    const confirmDelete = async () => {
      deleteLoading.value = true;
      try {
        await projectStore.deleteProject(deleteProjectId.value);
        deleteDialogVisible.value = false;
        ElMessage.success('项目删除成功');
      } catch (err) {
        console.error(err);
      } finally {
        deleteLoading.value = false;
      }
    };

    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleString();
    };

    onMounted(async () => {
    // 如果已有持久化数据且未初始化，直接使用
    if (projectStore.projects.length > 0 && !isInitialized.value) {
      isInitialized.value = true;
      return;
    }

    // 否则重新加载数据
    await projectStore.getProjects();
    isInitialized.value = true;
  });

    return {
      projects: projectStore.projects,
      loading: projectStore.loading,
      error: projectStore.error,
      dialogVisible,
      deleteDialogVisible,
      projectFormRef,
      submitLoading,
      deleteLoading,
      isEditMode,
      deleteProjectName,
      formProject,
      formRules,
      handleAddProject,
      handleEdit,
      handleDelete,
      submitProjectForm,
      confirmDelete,
      formatDate,
      goToProjectDetail,
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
}

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
