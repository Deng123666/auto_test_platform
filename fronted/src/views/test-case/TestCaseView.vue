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
              @click="openConfigCard(scope.row)"
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

    <!-- 接口配置弹窗 -->
    <el-dialog
      v-model="configCardVisible"
      title="接口配置"
      :width="'800px'"
      :close-on-click-modal="false"
      class="modern-dialog"
    >
      <el-form
        ref="apiConfigFormRef"
        :model="apiConfigForm"
        label-width="100px"
        label-position="top"
      >
        <el-row :gutter="20">
          <el-col :span="16">
            <el-form-item label="请求URL" prop="url">
              <el-input
                v-model="apiConfigForm.url"
                placeholder="请输入接口URL"
                clearable
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="请求方法" prop="method">
              <el-select
                v-model="apiConfigForm.method"
                placeholder="请选择请求方法"
                style="width: 100%"
              >
                <el-option label="GET" value="GET" />
                <el-option label="POST" value="POST" />
                <el-option label="PUT" value="PUT" />
                <el-option label="DELETE" value="DELETE" />
                <el-option label="PATCH" value="PATCH" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 多页参数输入区域 -->
        <el-tabs v-model="activeTab" type="card" class="params-tabs">
          <el-tab-pane label="Query参数" name="query">
            <el-table
              :data="apiConfigForm.queryParams"
              border
              style="width: 100%"
              size="small"
            >
              <el-table-column prop="key" label="参数名">
                <template #default="scope">
                  <el-input v-model="scope.row.key" size="small" />
                </template>
              </el-table-column>
              <el-table-column prop="value" label="参数值">
                <template #default="scope">
                  <el-input v-model="scope.row.value" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button
                    type="text"
                    size="small"
                    @click="removeParam('query', scope.$index)"
                    icon="Delete"
                    class="text-danger"
                  />
                </template>
              </el-table-column>
            </el-table>
            <el-button
              type="dashed"
              size="small"
              @click="addParam('query')"
              style="width: 100%; margin-top: 10px"
            >
              <el-icon><Plus /></el-icon> 添加参数
            </el-button>
          </el-tab-pane>

          <el-tab-pane label="请求头" name="headers">
            <el-table
              :data="apiConfigForm.headerParams"
              border
              style="width: 100%"
              size="small"
            >
              <el-table-column prop="key" label="参数名">
                <template #default="scope">
                  <el-input v-model="scope.row.key" size="small" />
                </template>
              </el-table-column>
              <el-table-column prop="value" label="参数值">
                <template #default="scope">
                  <el-input v-model="scope.row.value" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button
                    type="text"
                    size="small"
                    @click="removeParam('headers', scope.$index)"
                    icon="Delete"
                    class="text-danger"
                  />
                </template>
              </el-table-column>
            </el-table>
            <el-button
              type="dashed"
              size="small"
              @click="addParam('headers')"
              style="width: 100%; margin-top: 10px"
            >
              <el-icon><Plus /></el-icon> 添加参数
            </el-button>
          </el-tab-pane>

          <el-tab-pane label="请求体" name="body">
            <el-radio-group v-model="apiConfigForm.bodyType" style="margin-bottom: 15px">
              <el-radio label="form-data" /> form-data
              <el-radio label="x-www-form-urlencoded" /> x-www-form-urlencoded
              <el-radio label="raw" /> raw
              <el-radio label="binary" /> binary
            </el-radio-group>

            <template v-if="['form-data', 'x-www-form-urlencoded'].includes(apiConfigForm.bodyType)">
              <el-table
                :data="apiConfigForm.bodyParams"
                border
                style="width: 100%"
                size="small"
              >
                <el-table-column prop="key" label="参数名">
                  <template #default="scope">
                    <el-input v-model="scope.row.key" size="small" />
                  </template>
                </el-table-column>
                <el-table-column prop="value" label="参数值">
                  <template #default="scope">
                    <el-input v-model="scope.row.value" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="操作">
                  <template #default="scope">
                    <el-button
                      type="text"
                      size="small"
                      @click="removeParam('body', scope.$index)"
                      icon="Delete"
                      class="text-danger"
                    />
                  </template>
                </el-table-column>
              </el-table>
              <el-button
                type="dashed"
                size="small"
                @click="addParam('body')"
                style="width: 100%; margin-top: 10px"
              >
                <el-icon><Plus /></el-icon> 添加参数
              </el-button>
            </template>

            <template v-else-if="apiConfigForm.bodyType === 'raw'">
              <el-select v-model="apiConfigForm.rawType" style="width: 100%; margin-bottom: 10px">
                <el-option label="Text" value="text" />
                <el-option label="JavaScript" value="javascript" />
                <el-option label="JSON" value="json" />
                <el-option label="HTML" value="html" />
                <el-option label="XML" value="xml" />
              </el-select>
              <el-input
                v-model="apiConfigForm.rawBody"
                type="textarea"
                rows="6"
                placeholder="请输入请求体内容"
              />
            </template>

            <template v-else-if="apiConfigForm.bodyType === 'binary'">
              <el-upload class="upload-demo" action="#" :auto-upload="false">
                <el-button type="primary">点击上传文件</el-button>
              </el-upload>
            </template>
          </el-tab-pane>
        </el-tabs>
      </el-form>

      <template #footer>
        <el-button @click="configCardVisible = false">取消</el-button>
        <el-button type="primary" @click="saveApiConfig">保存配置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref, reactive, computed, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter, useRoute } from 'vue-router';
import { Folder, Warning, FolderDelete, Plus } from '@element-plus/icons-vue';
import { createTestCase, createTestCaseApiConfig, deleteTestCase, fetchTestCases, updateTestCase } from '@/api/test_cases';
import { fetchProjects } from '@/api/projects';
import type { TestCase, Project, ApiResponse } from '@/types';
import { getTestCaseApiConfig, saveTestCaseApiConfig } from '@/api/test_cases';


export default defineComponent({
  name: 'ProjectsView',
  components: {
    Folder,
    Warning,
    FolderDelete,
    Plus,
  },
  setup() {
    const route = useRoute();
    const router = useRouter();

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
    const searchQuery = ref('');


    const defaultProject = computed({
      get() {
        return formTestCase.project || null;
      },
      set(val) {
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
      isConfigured: false
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

    const currentRouteProjectId = computed(() => {
      return route.params.projectId?.toString();
    });

    const getTestCases = async () => {
      loading.value = true;
      error.value = '';
      try {
        const projectsResponse = await fetchProjects();
        projects.value = projectsResponse.results;

        const projectMap = new Map(projects.value.map(p => [p.id, p.name]));

        const routeProjectId = route.params.projectId;
        const routeProjectName = route.query.projectName?.toString();

        let finalProjectId = routeProjectId ? Number(routeProjectId) : null;
        if (routeProjectName) {
          const matchedProject = projects.value.find(p => p.name === routeProjectName);
          if (matchedProject) {
            finalProjectId = matchedProject.id;
            if (!isEditMode.value) {
              formTestCase.project = finalProjectId;
            }
          } else {
            error.value = '未找到名称为 "' + routeProjectName + '" 的项目';
          }
        }

        const response: ApiResponse<TestCase> = await fetchTestCases();
        testCases.value = response.results
          .map(caseItem => ({
            ...caseItem,
            projectName: projectMap.get(caseItem.project) || '未知项目'
          }))
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

        const requestData = {
          name: formTestCase.name,
          description: formTestCase.description,
          project: Number(formTestCase.project)
        };

        if (isEditMode.value) {
          await updateTestCase(formTestCase.id, requestData);
          ElMessage.success('用例更新成功');
        } else {
          await createTestCase(requestData);
          ElMessage.success('用例创建成功');
        }

        dialogVisible.value = false;
        await getTestCases();
      } catch (err) {
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

    const filteredTestCases = computed(() => {
      const query = searchQuery.value.toLowerCase().trim();
      if (!query) return testCases.value;
      return testCases.value.filter(testCase =>
        testCase.name.toLowerCase().includes(query) ||
        (testCase.description && testCase.description.toLowerCase().includes(query)) ||
        testCase.projectName.toLowerCase().includes(query)
      );
    });

    // 接口配置相关变量
    const configCardVisible = ref(false);
    const activeTab = ref('query');
    const currentConfigTestCase = ref<TestCase | null>(null);
    const apiConfigLoading = ref(false); // 新增：加载配置的loading状态

    const apiConfigForm = reactive({
      url: '',
      method: 'GET',
      queryParams: [] as Array<{key: string; value: string}>,
      headerParams: [] as Array<{key: string; value: string}>,
      bodyType: 'form-data',
      rawType: 'json',
      rawBody: '',
      bodyParams: [] as Array<{key: string; value: string}>
    });

    // 接口配置相关方法
    const openConfigCard = async (testCase: TestCase) => {
      currentConfigTestCase.value = testCase;
      configCardVisible.value = true;
      apiConfigLoading.value = true;

      try {
        // 重置表单
        apiConfigForm.url = '';
        apiConfigForm.method = 'GET';
        apiConfigForm.queryParams = [];
        apiConfigForm.headerParams = [];
        apiConfigForm.bodyParams = [];
        apiConfigForm.rawBody = '';
        apiConfigForm.bodyType = 'form-data';
        apiConfigForm.rawType = 'json';

        const savedConfig = await getTestCaseApiConfig(testCase.id);
        apiConfigForm.url = savedConfig.url;
        apiConfigForm.method = savedConfig.method;
        apiConfigForm.queryParams = savedConfig.query_params || [];
        apiConfigForm.headerParams = savedConfig.header_params || [];
        apiConfigForm.bodyType = savedConfig.body_type;
        apiConfigForm.rawType = savedConfig.raw_type || 'json';
        apiConfigForm.rawBody = savedConfig.raw_body || '';
        apiConfigForm.bodyParams = savedConfig.body_params || [];
      } catch (err) {
        console.error('加载接口配置222失败:', err);
        const requestData = {
          test_case: testCase.id,
          url: apiConfigForm.url = "https://www.baidu.com",
          method: apiConfigForm.method = 'GET',
          queryParams: [],
          headerParams: [],
          bodyType: '',
          rawType: 'json',
          rawBody: '',
          bodyParams: [],
        }
        await createTestCaseApiConfig(requestData);

      } finally {
        apiConfigLoading.value = false;
      }
    };

    const addParam = (type: 'query' | 'headers' | 'body') => {
      if (type === 'query') {
        apiConfigForm.queryParams.push({ key: '', value: '' });
      } else if (type === 'headers') {
        apiConfigForm.headerParams.push({ key: '', value: '' });
      } else if (type === 'body') {
        apiConfigForm.bodyParams.push({ key: '', value: '' });
      }
    };

    const removeParam = (type: 'query' | 'headers' | 'body', index: number) => {
      if (type === 'query') {
        apiConfigForm.queryParams.splice(index, 1);
      } else if (type === 'headers') {
        apiConfigForm.headerParams.splice(index, 1);
      } else if (type === 'body') {
        apiConfigForm.bodyParams.splice(index, 1);
      }
    };

    const saveApiConfig = async () => {
      if (!currentConfigTestCase.value) return;

      apiConfigLoading.value = true;
      try {
        const requestData = {
          test_case: currentConfigTestCase.value.id,
          url: apiConfigForm.url,
          method: apiConfigForm.method,
          query_params: apiConfigForm.queryParams.filter(param => param.key.trim()),
          header_params: apiConfigForm.headerParams.filter(param => param.key.trim()),
          body_type: apiConfigForm.bodyType,
          raw_type: apiConfigForm.rawType,
          raw_body: apiConfigForm.rawBody,
          body_params: apiConfigForm.bodyParams.filter(param => param.key.trim())
        };
        await saveTestCaseApiConfig(requestData, currentConfigTestCase.value.id);
        ElMessage.success('接口配置保存成功');
        configCardVisible.value = false;
      } catch (err) {
        console.error('保存接口配置失败:', err);
        ElMessage.error('保存接口配置失败，请稍后重试');
      } finally {
        apiConfigLoading.value = false;
      }
    };

    // const createApiConfig = async () => {
    //   if (!currentConfigTestCase.value) return;
    // }

    const goToTestCaseDetail = (testCase: TestCase) => {
      router.push({
        name: 'CaseDetail',
        params: { testCaseId: testCase.id },
        query: { projectName: testCase.projectName, testCaseName: testCase.name }
      });
    };

    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleString();
    };

    onMounted(() => {
      getTestCases();
    });

    watch(
      () => [route.query.projectName, route.params.projectId],
      () => {
        getTestCases();
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
      defaultProject,
      isProjectFixed,
      currentRouteProjectId,
      handleAddTestCase,
      handleEdit,
      handleDelete,
      submitTestCaseForm,
      confirmDelete,
      formatDate,
      goToTestCaseDetail,

      // 接口配置相关
      configCardVisible,
      activeTab,
      apiConfigForm,
      apiConfigLoading,
      openConfigCard,
      addParam,
      removeParam,
      saveApiConfig
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

a.primary-btn {
  background: linear-gradient(135deg, #4361ee, #3a0ca3);
  border: none;
  box-shadow: 0 4px 6px rgba(67, 97, 238, 0.2);
}

a.danger-btn {
  background: linear-gradient(135deg, #f43f5e, #e11d48);
  border: none;
  box-shadow: 0 4px 6px rgba(244, 63, 94, 0.2);
}

dialog-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(67, 97, 238, 0.25);
}

danger-btn:hover {
  box-shadow: 0 6px 12px rgba(244, 63, 94, 0.25);
}

/* 接口配置弹窗样式 */
.params-tabs {
  margin-top: 20px;
}

.el-tabs__content {
  padding-top: 15px;
}
</style>
