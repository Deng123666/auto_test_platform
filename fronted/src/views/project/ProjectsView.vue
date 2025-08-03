<template>
  <div class="projects-container">
    <div class="page-header">
      <h1>项目管理</h1>
      <!-- 添加项目按钮 -->
      <el-button type="primary" icon="Plus" @click="handleAddProject">添加项目</el-button>
    </div>

    <!-- 添加/编辑项目对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditMode ? '编辑项目' : '添加新项目'"
      :width="'500px'"
      :close-on-click-modal="false"
    >
      <el-form
        ref="projectFormRef"
        :model="formProject"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="formProject.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="formProject.description"
            placeholder="请输入项目描述"
            type="textarea"
            :rows="4"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitProjectForm" :loading="submitLoading">
          {{ isEditMode ? '确认更新' : '确认添加' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除"
      :width="'30%'"
      :close-on-click-modal="false"
    >
      <span>您确定要删除项目 <strong>{{ deleteProjectName }}</strong> 吗？此操作不可撤销。</span>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmDelete" :loading="deleteLoading">确认删除</el-button>
      </template>
    </el-dialog>

    <!-- 表格区域 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="projects"
        stripe
        style="width: 100%"
        empty-text="暂无项目数据"
      >
        <el-table-column prop="id" label="ID" width="80" style="text-align: center"></el-table-column>
        <el-table-column prop="name" label="项目名称" width="400">

        </el-table-column>
        <el-table-column prop="description" label="项目描述">
          <template #default="scope">
            <el-tooltip :content="scope.row.description || '无描述'" placement="top">
              <div class="description-cell">{{ scope.row.description || '无描述' }}</div>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" style="text-align: center">
          <template #default="scope">{{ formatDate(scope.row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180" style="text-align: center">
          <template #default="scope">{{ formatDate(scope.row.updated_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" style="text-align: center">
          <template #default="scope">
            <el-button
              type="primary"
              size="small"
              icon="Edit"
              @click="handleEdit(scope.row)"
              style="margin-right: 8px; margin-bottom: 2px"
            >编辑</el-button>
            <el-button
              type="danger"
              size="small"
              icon="Delete"
              @click="handleDelete(scope.row)"
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
import { defineComponent, onMounted, ref, reactive, toRefs } from 'vue';
import { fetchProjects, createProject, updateProject, deleteProject } from '@/api/projects';
import { ElMessage, ElMessageBox } from 'element-plus';

interface Project {
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
  results: Project[];
}

export default defineComponent({
  name: 'ProjectsView',
  setup() {
    const projects = ref<Project[]>([]);
    const loading = ref(false);
    const error = ref('');
    const dialogVisible = ref(false);
    const deleteDialogVisible = ref(false);
    const projectFormRef = ref();
    const submitLoading = ref(false);
    const deleteLoading = ref(false);
    const isEditMode = ref(false);
    const currentEditId = ref(0);
    const deleteProjectName = ref('');
    const deleteProjectId = ref(0);

    const formProject = reactive<Project>({
      id: 0,
      name: '',
      description: '',
      created_at: '',
      updated_at: ''
    });

    // 表单验证规则
    const formRules = {
      name: [
        { required: true, message: '请输入项目名称', trigger: 'blur' },
        { max: 20, message: '项目名称不能超过20个字符', trigger: 'blur' }
      ],
      description: [
        { max: 200, message: '项目描述不能超过200个字符', trigger: 'blur' }
      ]
    };

    // 获取项目数据
    const getProjects = async () => {
      loading.value = true;
      error.value = '';
      try {
        const response: ApiResponse = await fetchProjects();
        projects.value = response.results;
      } catch (err) {
        error.value = '获取项目列表失败，请稍后重试';
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    const handleAddProject = () => {
      isEditMode.value = false;
      // 重置表单数据
      formProject.id = 0;
      formProject.name = '';
      formProject.description = '';
      dialogVisible.value = true;
      // 重置表单验证
      if (projectFormRef.value) {
        projectFormRef.value.resetFields();
      }
    };

    const handleEdit = (project: Project) => {
      isEditMode.value = true;
      currentEditId.value = project.id;
      // 填充表单数据
      formProject.id = project.id;
      formProject.name = project.name;
      formProject.description = project.description || '';
      formProject.created_at = project.created_at;
      formProject.updated_at = project.updated_at;
      dialogVisible.value = true;
      // 重置表单验证
      if (projectFormRef.value) {
        projectFormRef.value.clearValidate();
      }
    };

    const handleDelete = (project: Project) => {
      deleteProjectId.value = project.id;
      deleteProjectName.value = project.name;
      deleteDialogVisible.value = true;
    };

    // 提交项目表单（添加/编辑）
    const submitProjectForm = async () => {
      if (!projectFormRef.value) return;

      try {
        // 表单验证
        await projectFormRef.value.validate();
        submitLoading.value = true;

        if (isEditMode.value) {
          // 编辑项目
          await updateProject(formProject.id, {
            name: formProject.name,
            description: formProject.description
          });
          ElMessage.success('项目更新成功');
        } else {
          // 添加项目
          await createProject({
            name: formProject.name,
            description: formProject.description
          });
          ElMessage.success('项目创建成功');
        }

        // 关闭对话框
        dialogVisible.value = false;
        // 重新获取项目列表
        getProjects();
      } catch (err) {
        if (err === false) {
          // 表单验证失败
          return;
        }
        error.value = isEditMode.value ? '更新项目失败，请稍后重试' : '创建项目失败，请稍后重试';
        console.error(err);
      } finally {
        submitLoading.value = false;
      }
    };

    // 确认删除
    const confirmDelete = async () => {
      deleteLoading.value = true;
      try {
        await deleteProject(deleteProjectId.value);
        // 关闭删除对话框
        deleteDialogVisible.value = false;
        // 重新获取项目列表
        getProjects();
        ElMessage.success('项目删除成功');
      } catch (err) {
        error.value = '删除项目失败，请稍后重试';
        console.error(err);
      } finally {
        deleteLoading.value = false;
      }
    };

    // 格式化日期
    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleString();
    };

    // 组件挂载时获取数据
    onMounted(() => {
      getProjects();
    });

    return {
      projects,
      loading,
      error,
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
      getProjects
    };
  }
});
</script>

<style scoped>
.projects-container {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.table-card {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  overflow: hidden;
}

.description-cell {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 400px;
}

.error-alert {
  margin-top: 16px;
}
</style>
