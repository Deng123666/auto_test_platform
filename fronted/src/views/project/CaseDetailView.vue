<template>
  <div class="project-detail-container">
    <div class="page-header">
      <el-button @click="goBack" icon="ArrowLeftBold" type="text" style="margin-right: 10px;">返回</el-button>
      <el-input
        v-model="project.name"
        placeholder="项目名称"
        style="width: 200px;"
        @blur="saveProjectName"
      ></el-input>
    </div>

    <!-- URL 和请求方式区域 -->
    <div class="request-section">
      <el-select v-model="request.method" placeholder="选择方法" style="width: 100px; margin-right: 10px;">
        <el-option label="GET" value="GET"></el-option>
        <el-option label="POST" value="POST"></el-option>
        <el-option label="PUT" value="PUT"></el-option>
        <el-option label="DELETE" value="DELETE"></el-option>
        <el-option label="PATCH" value="PATCH"></el-option>
      </el-select>
      <el-input v-model="request.url" placeholder="输入请求URL"></el-input>
    </div>

    <!-- 参数区域 -->
    <div class="params-section">
      <h3>请求参数</h3>
      <div class="param-row" v-for="(param, index) in request.params" :key="index">
        <el-input v-model="param.key" placeholder="参数名" style="width: 150px; margin-right: 10px;"></el-input>
        <el-input v-model="param.value" placeholder="参数值" style="flex: 1; margin-right: 10px;"></el-input>
        <el-select v-model="param.type" style="width: 120px; margin-right: 10px;">
          <el-option label="String" value="string"></el-option>
          <el-option label="Number" value="number"></el-option>
          <el-option label="Boolean" value="boolean"></el-option>
          <el-option label="JSON" value="json"></el-option>
        </el-select>
        <el-button @click="removeParam(index)" type="danger" icon="Delete" circle></el-button>
      </div>
      <el-button @click="addParam" type="primary" icon="Plus" style="margin-top: 10px;">添加参数</el-button>
    </div>

    <!-- 设置预期结果区域 -->
    <div class="expected-result-section">
      <h3>预期结果</h3>
      <el-input
        v-model="expectedResult"
        type="textarea"
        :rows="5"
        placeholder="输入预期返回结果（JSON格式）"
      ></el-input>
    </div>

    <!-- 提交测试按钮 -->
    <div class="action-section">
      <el-button type="primary" @click="runTest">运行测试</el-button>
      <el-button @click="saveTestConfig">保存配置</el-button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { fetchProjectDetail, updateProject } from '@/api/projects';
import { ElMessage } from 'element-plus';

interface Project {
  id: number;
  name: string;
  description: string | null;
}

interface RequestParam {
  key: string;
  value: string;
  type: string;
}

export default defineComponent({
  name: 'ProjectDetailView',
  setup() {
    const route = useRoute();
    const router = useRouter();

    const project = reactive<Project>({
      id: 0,
      name: '',
      description: ''
    });

    const request = reactive({
      method: 'GET',
      url: '',
      params: [] as RequestParam[]
    });

    const expectedResult = ref('');
    const loading = ref(false);

    // 获取项目详情
    const fetchProjectData = async () => {
      loading.value = true;
      try {
        const projectId = Number(route.params.projectId);
        if (projectId) {
          const response = await fetchProjectDetail(projectId);
          Object.assign(project, response);

          // 从路由状态中获取传递的项目名称
          if (route.state?.projectName) {
            project.name = route.state.projectName;
          }
        }
      } catch (error) {
        ElMessage.error('获取项目详情失败');
        console.error(error);
      } finally {
        loading.value = false;
      }
    };

    onMounted(() => {
      fetchProjectData();
    });

    // 返回项目列表
    const goBack = () => {
      router.push({ name: 'projects' });
    };

    // 保存项目名称
    const saveProjectName = async () => {
      try {
        await updateProject(project.id, {
          name: project.name,
          description: project.description || ''
        });
        ElMessage.success('项目名称更新成功');
      } catch (error) {
        ElMessage.error('更新项目名称失败');
        console.error(error);
      }
    };

    // 添加参数
    const addParam = () => {
      request.params.push({ key: '', value: '', type: 'string' });
    };

    // 移除参数
    const removeParam = (index: number) => {
      request.params.splice(index, 1);
    };

    // 运行测试
    const runTest = () => {
      ElMessage.info('测试运行功能待实现');
      // 这里可以添加发送API请求并验证结果的实际逻辑
    };

    // 保存测试配置
    const saveTestConfig = () => {
      ElMessage.success('测试配置已保存');
      // 这里可以添加保存配置到数据库的逻辑
    };

    return {
      project,
      request,
      expectedResult,
      loading,
      goBack,
      saveProjectName,
      addParam,
      removeParam,
      runTest,
      saveTestConfig
    };
  }
});
</script>

<style scoped>
.project-detail-container {
  padding: 24px;
}

.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}

.request-section {
  display: flex;
  margin-bottom: 24px;
}

.params-section, .expected-result-section {
  margin-bottom: 24px;
}

.param-row {
  display: flex;
  margin-bottom: 10px;
  align-items: center;
}

.action-section {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
