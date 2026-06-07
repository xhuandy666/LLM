<template>
  <el-container>
    <el-header>
      <el-menu
      :default-active="activeIndex"
      class="el-menu-demo"
      mode="horizontal"
      @select="handleSelect"
      background-color="#545c64"
      text-color="#fff"
      active-text-color="#ffd04b">
      <!-- <el-menu-item index="1"> <el-button type="text" @click="open">帮助</el-button></el-menu-item> -->
      <el-menu-item index="1"> <el-button type="text" @click="dialog = true" style="margin-left:1770px" >设置</el-button></el-menu-item>
      <el-drawer
  title="模型切换"
  :before-close="handleClose"
  :visible.sync="dialog"
  direction="rtl"
  custom-class="demo-drawer"
  ref="drawer"
  >
  <div class="demo-drawer__content">
    <el-form :model="form">
    
      <el-form-item label="模型名称" :label-width="formLabelWidth">
        <el-select v-model="selectModels" @change="updataInput" placeholder="请选择模型">
          <el-option label="Qwen Plus 2025-09-11" value="qwen-plus-2025-09-11"></el-option>
          <el-option label="Qwen Plus" value="qwen-plus"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="模型介绍" :label-width="formLabelWidth">
        <el-input type="textarea" autosize v-model="ModelsIntro" :disabled="true"></el-input>
      </el-form-item>
    </el-form>
    <div class="demo-drawer__footer">
      <el-button @click="cancelForm">取 消</el-button>
      <el-button type="primary" @click="$refs.drawer.closeDrawer()" :loading="loading">{{ loading ? '切换中 ...' : '确 定' }}</el-button>
    </div>
  </div>
</el-drawer>

      <span
      style=" background-color:#545c64 ;position: absolute;color:#fff ;padding-top: 0px;right: 43%;font-size: 17px;font-weight: bold"> 基于大模型的表格数据生成</span>

      </el-menu>
    </el-header>
    <el-main>
      <el-card class="box-card">
    <div slot="header" class="head">  
      <span style="font-weight: bold;font-size: 15px;margin-top:-55px;">TablesGenerator</span>
    </div>
    <div id="dialog_container" style="display: flex;flex-direction: column;">
      <div v-for="(message, index) in messages" :key="index" :class="['message-row', message.role === 'user' ? 'right' : 'left']">
    <!-- 消息展示，分为上下，上面是头像，下面是消息 -->
        <div class="row">
      <!-- 头像， -->
          <div class="avatar-wrapper" >
          <el-avatar
            v-if="message.role === 'user'"
            :src="user_Logo"
            class="avatar"
            shape="square"
          />
          <el-avatar v-else :src="assistant_Logo" class="avatar" shape="square" style="margin-bottom: -60px;"/>
          </div>
      <!-- 发送的消息或者回复的消息 -->
      <div class="message"  >
        <!-- 预览模式，用来展示markdown格式的消息 -->
        <TextLoading v-if="message.content.length<=0"></TextLoading>
        <v-md-editor :value="message.content" mode="preview" 
        :style="{backgroundColor:message.role === 'user' ? 'rgb(231, 248, 255)' : '#f4f4f5', width: '600px'}"
       
        ></v-md-editor>
        
        
           
       

            <!-- <div v-for="message in messages" :class="['message', message.role === 'user' ? 'user' : 'assistant']">
              <v-md-editor :value="message.content" mode="preview"></v-md-editor>
              
            </div>
      -->
      </div>
    </div>
    </div>
    </div>
    
    <div class="agent-panel">
      <div class="agent-controls">
        <el-select
          v-model="selectedTemplate"
          clearable
          size="small"
          placeholder="选择业务模板"
          class="template-select"
        >
          <el-option
            v-for="template in templates"
            :key="template.id"
            :label="template.name"
            :value="template.id"
          ></el-option>
        </el-select>
        <el-button
          type="primary"
          icon="el-icon-s-operation"
          plain
          size="small"
          :loading="schemaLoading"
          @click="planSchema()"
        >规划 Schema</el-button>
        <el-button
          type="success"
          icon="el-icon-circle-check"
          plain
          size="small"
          :loading="validationLoading"
          @click="validateGeneratedTable()"
        >质量检查</el-button>
      </div>
      <div v-if="schemaPlan" class="schema-panel">
        <div class="schema-summary">
          <span class="schema-title">{{ schemaPlan.scenario_label }}</span>
          <span>目标行数：{{ schemaPlan.row_count }}</span>
          <span>来源：{{ formatPlanSource(schemaPlan.source) }}</span>
        </div>
        <el-table :data="schemaPlan.schema" size="mini" max-height="220">
          <el-table-column prop="label" label="字段" width="110"></el-table-column>
          <el-table-column prop="name" label="字段名" width="140"></el-table-column>
          <el-table-column prop="type" label="类型" width="90"></el-table-column>
          <el-table-column label="约束">
            <template slot-scope="scope">
              {{ formatConstraints(scope.row.constraints) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div v-if="validationResult" class="validation-panel">
        <div class="validation-summary">
          <el-tag :type="validationResult.passed ? 'success' : 'danger'">
            {{ validationResult.passed ? '校验通过' : '校验未通过' }}
          </el-tag>
          <span>实际行数：{{ validationResult.summary.row_count.actual }}</span>
          <span>问题数量：{{ validationResult.summary.issue_count }}</span>
        </div>
        <div v-if="validationResult.issues.length > 0" class="issue-list">
          <div
            v-for="(issue, issueIndex) in validationResult.issues"
            :key="issueIndex"
            class="issue-item"
          >
            <el-tag size="mini" type="warning">{{ issue.type }}</el-tag>
            <span>{{ issue.message }}</span>
          </div>
        </div>
        <pre class="validation-report">{{ validationResult.report }}</pre>
      </div>
    </div>

    <el-divider ></el-divider>
    <el-input
        type="textarea"
        :autosize="{ minRows: 2, maxRows: 4}"
        @keydown.enter.native="fetchTable()"
        v-model="newMessage"
    >
    <!-- <template slot="append"> //插槽插入文字按钮
      <el-button 
      type="text"
      :disabled="coolDown"
      @click="AutoOptimize()">指令优化</el-button>
      </template> -->
    </el-input>
      <div class="buttons" >
      <el-button  type="success"  icon="el-icon-thumb" plain @click="fetchTable() ">生成表格</el-button>
      <el-button  type="warning" icon="el-icon-paperclip" plain @click="copy()">复制表格</el-button>
      <el-button  type="danger" icon="el-icon-delete" plain @click="clearAll()">清除记录</el-button>
      <el-button  type="primary" icon="el-icon-star-on" plain @click="AutoOptimize()" :loading="loading">{{ loading ? '优化中 ...' : '指令优化' }}</el-button>
      <el-button  type="primary" icon="el-icon-upload" plain @click="exportCsv()">导出csv</el-button>
    </div>
  </el-card>
<!-- v-clipboard:copy="this.messages.content"
      v-clipboard:success="onCopy"
      v-clipboard:error="onError" -->
  </el-main>
</el-container>
</template>
<style scoped>

.message-row {
  display: flex;
}

.message-row.right {
  justify-content: flex-end;
}

.message-row.right .avatar-wrapper {
  display: flex;
  justify-content: flex-end;
}

.message-row .avatar {
  box-shadow: 20px 20px 20px 3px rgba(0, 0, 0, 0.03);
  margin-bottom: 10px;
}

.message-row.right .message {
  background-color: rgb(231, 248, 255);
}

.message-row .message {
  font-size: 15px;
  padding: 1.5px;
  max-width: 600px;
  border-radius: 7px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 20px 20px 20px 1px rgba(0, 0, 0, 0.01);
}

.question_card{
  justify-content: flex-end;
}

.head{
  display: flex;
  justify-content: center;
  margin-top: 10px;
  height: 40px;

}

.buttons {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.agent-panel {
  line-height: 1.5;
  margin-top: 14px;
}

.agent-controls {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 10px;
}

.template-select {
  width: 260px;
}

.schema-panel {
  margin-top: 10px;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background: #fafafa;
}

.validation-panel {
  margin-top: 10px;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  background: #fff;
}

.schema-summary {
  display: flex;
  gap: 18px;
  align-items: center;
  margin-bottom: 8px;
  color: #606266;
  font-size: 13px;
}

.schema-title {
  color: #303133;
  font-weight: 600;
}

.validation-summary {
  display: flex;
  gap: 18px;
  align-items: center;
  margin-bottom: 8px;
  color: #606266;
  font-size: 13px;
}

.issue-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 8px;
}

.issue-item {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  color: #606266;
  font-size: 13px;
}

.validation-report {
  margin: 0;
  padding: 8px;
  white-space: pre-wrap;
  color: #303133;
  background: #f7f7f7;
  border-radius: 4px;
  line-height: 1.5;
}

.box-card {
  margin: 2% auto;
  width: 50%;
  min-width: 1100px;
  text-align: left;
  line-height: 1.5;

}

#dialog_container {
  overflow: auto;
  scroll-margin-right: 1px;
  /*根据屏幕占比设置高度*/
  min-height: calc(100vh - 360px);
  max-height: calc(100vh - 360px);
}

.home-view {
  display: flex;
  width: 100vw;
  justify-content: center;
}

.home-view .chat-panel {
  display: flex;
  border-radius: 20px;
  background-color: white;
  box-shadow: 0 0 20px 20px rgba(0, 0, 0, 0.05);
  margin-top: 70px;
}

.home-view .message-panel {
  width: 700px;
  height: 800px;
}

  .message-input {
    padding: 20px;
    border-top: 1px solid rgba(0, 0, 0, 0.07);
    border-left: 1px solid rgba(0, 0, 0, 0.07);
    border-right: 1px solid rgba(0, 0, 0, 0.07);
    border-top-right-radius: 5px;
    border-top-left-radius: 5px;
  }

  .button-wrapper {
    display: flex;
    justify-content: flex-end;
    margin-top: 0px;
  }


  .el-header {
    background-color: #303b49;
    color: #c0b5b5;
    text-align: center;
    line-height: 60px;
  }
  .el-main {
    background-color: #E9EEF3;
    color: #333;
    text-align: center;
    line-height: 160px;
  }
</style>

<script>

import axios from 'axios';
import TextLoading from './components/TextLoading.vue';
import MarkdownIt from 'markdown-it';  
import Papa from 'papaparse';  

export default {
  data() {
    return {
      md: new MarkdownIt(),
      textarea: '',
      messages: [],
      newMessage:'',
      copiedList: [],
      activeIndex: '1',
      user_question: '',
      copyNewMessage: '',
      user_name: 'user',
      user_Logo: "https://img0.baidu.com/it/u=2864837501,1810663520&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=500",
      assistant_Logo: "https://img2.baidu.com/it/u=2784541464,2988923813&fm=253&fmt=auto&app=138&f=PNG?w=240&h=240",
      dialog: false,
      loading: false,
      apiBaseUrl: 'http://127.0.0.1:5000',
      sessionId: `session-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      selectModels: 'qwen-plus-2025-09-11',
      ModelsIntro: 'Qwen Plus 通过 DashScope OpenAI-compatible API 调用，与 Career Copilot 当前使用的 Qwen 配置保持一致。',
      templates: [],
      selectedTemplate: '',
      schemaPlan: null,
      schemaLoading: false,
      validationResult: null,
      validationLoading: false,
      tempModel: '',
      form: {
        name: '',
        region: '',
        date1: '',
        date2: '',
        delivery: false,
        type: [],
        resource: '',
        desc: ''
      },
      formLabelWidth: '80px',
      timer: null,
    };
  },
  methods: {
    loadTemplates() {
      axios.get(`${this.apiBaseUrl}/api/templates`)
        .then(response => {
          this.templates = response.data.templates || [];
        })
        .catch(error => {
          console.error('Error loading templates:', error);
          this.$message.warning('业务模板加载失败');
        });
    },
    planSchema(showMessage = true) {
      return this.requestSchemaPlan(this.newMessage, showMessage);
    },
    requestSchemaPlan(message, showMessage = true) {
      if (!message.trim() && !this.selectedTemplate) {
        this.$message.warning('请先输入需求或选择业务模板');
        return Promise.resolve(null);
      }
      this.schemaLoading = true;
      return axios.post(`${this.apiBaseUrl}/api/schema/plan`, {
        message: message,
        template_id: this.selectedTemplate || null
      })
        .then(response => {
          this.schemaPlan = response.data;
          if (showMessage) {
            this.$message.success('Schema 规划完成');
          }
          return response.data;
        })
        .catch(error => {
          console.error('Error planning schema:', error);
          this.$message.error(error.response?.data?.error || 'Schema 规划失败');
          return null;
        })
        .finally(() => {
          this.schemaLoading = false;
        });
    },
    validateGeneratedTable(showMessage = true) {
      const lastAssistantMessage = this.getLastAssistantMessage();
      if (!lastAssistantMessage) {
        this.$message.warning('暂无可校验的表格');
        return Promise.resolve(null);
      }
      if (!this.schemaPlan) {
        this.$message.warning('请先规划 Schema');
        return Promise.resolve(null);
      }
      this.validationLoading = true;
      return axios.post(`${this.apiBaseUrl}/api/validate`, {
        markdown: lastAssistantMessage.content,
        schema_plan: this.schemaPlan
      })
        .then(response => {
          this.validationResult = response.data;
          if (showMessage) {
            const message = response.data.passed ? '质量检查通过' : '质量检查发现问题';
            this.$message({
              type: response.data.passed ? 'success' : 'warning',
              message: message
            });
          }
          return response.data;
        })
        .catch(error => {
          console.error('Error validating table:', error);
          this.$message.error(error.response?.data?.error || '质量检查失败');
          return null;
        })
        .finally(() => {
          this.validationLoading = false;
        });
    },
    formatPlanSource(source) {
      const sourceMap = {
        template: '业务模板',
        inferred_template: '意图识别',
        custom: '自定义'
      };
      return sourceMap[source] || source;
    },
    formatConstraints(constraints) {
      if (!constraints || Object.keys(constraints).length === 0) {
        return '-';
      }
      const parts = [];
      if (constraints.enum && constraints.enum.length > 0) {
        parts.push(`枚举: ${constraints.enum.join('/')}`);
      }
      if (constraints.min !== undefined || constraints.max !== undefined) {
        const minValue = constraints.min !== undefined ? constraints.min : '-';
        const maxValue = constraints.max !== undefined ? constraints.max : '-';
        parts.push(`范围: ${minValue} ~ ${maxValue}`);
      }
      if (constraints.unit) {
        parts.push(`单位: ${constraints.unit}`);
      }
      if (constraints.pattern) {
        parts.push(`格式: ${constraints.pattern}`);
      }
      if (constraints.format) {
        parts.push(`格式: ${constraints.format}`);
      }
      if (constraints.examples) {
        parts.push(`示例: ${constraints.examples.join('/')}`);
      }
      return parts.length > 0 ? parts.join('；') : JSON.stringify(constraints);
    },
    parseMarkdownTable() {
      const lastAssistantMessage = this.getLastAssistantMessage();
      if (!lastAssistantMessage) return null;
      // 解析Markdown文本，并提取出HTML表格
      const html = this.md.render(lastAssistantMessage.content);
      // 这里假设Markdown文本中只有一个表格，你可能需要调整这部分以适应更复杂的情况
      const tableHtml = html.match(/<table>[\s\S]*?<\/table>/);
      if (!tableHtml) return null;
      return tableHtml[0];
    },  
    htmlToTableData(html) {  
      // 使用DOM解析来提取表格数据  
      const tempElement = document.createElement('div');  
      tempElement.innerHTML = html;  
      const table = tempElement.querySelector('table');  
      const rows = Array.from(table.querySelectorAll('tr'));  
      return rows.map(row => Array.from(row.querySelectorAll('td, th')).map(cell => cell.innerText.trim()));  
    },  
    exportCsv(){
      const htmlTable = this.parseMarkdownTable();  
      if (!htmlTable) {
        this.$message.warning('暂无可导出的表格');
        return;
      }
      const tableData = this.htmlToTableData(htmlTable);  
      const csv = Papa.unparse(tableData);  
      // 创建一个blob对象，并创建一个下载链接来下载CSV文件  
      const blob = new Blob(["\uFEFF" + csv], { type: 'text/csv;charset=utf-8;' });  
      const link = document.createElement('a');  
      link.href = URL.createObjectURL(blob);  
      link.download = 'table.csv';  
      link.click();  
      URL.revokeObjectURL(link.href); // 释放URL对象以节省内存
    },

    AutoOptimize(){
      if (!this.newMessage.trim()) {
        this.$message.warning('请先输入需要优化的指令');
        return;
      }
      this.loading = true;
      axios.post(`${this.apiBaseUrl}/api/optimize`, { message: this.newMessage, model: this.selectModels})
        .then(response => {
          this.newMessage = response.data;
          this.loading = false;
        })
        .catch(error => {
          console.error('Error optimize prompt:', error);
          this.loading = false;
          this.$message.error(error.response?.data?.error || '指令优化失败');
        });
    },
    updataInput(){
      if(this.selectModels === 'qwen-plus-2025-09-11'){
        this.ModelsIntro = 'Qwen Plus 2025-09-11 是当前默认模型，与 Career Copilot 的实测配置保持一致。';
      }else if(this.selectModels === 'qwen-plus'){
        this.ModelsIntro = 'Qwen Plus 是通用文本生成模型，可作为默认模型不可用时的保守备选。';
      }
    },
    
    clearHistory(){
      return axios.get(`${this.apiBaseUrl}/api/clear`, { params: { session_id: this.sessionId }})
    },
    starLoading() {
    // 创建一个 loading 实例并赋值给 loading 变量
    let loading = this.$loading({
        text: "加载中", // 设置 loading 文本为 "加载中"
        spinner: "el-icon-loading", // 使用 Element UI 提供的加载图标
        background: "rgba(0, 0, 0, 0.7)", // 设置 loading 遮罩层背景色为半透明黑色
        target: document.querySelector("body"), // 将 loading 遮罩层挂载到页面 body 元素上
    });
    
    return {
        // 方法用于关闭 loading 遮罩层
        closeLoading: () => {
            loading.close(); // 调用 loading 实例的 close 方法关闭遮罩层
        }
    };
    },
    fetchTable() {
      if (!this.newMessage.trim()) {
        this.$message.warning('请先输入表格生成需求');
        return;
      }
      this.loadingInstance  = this.starLoading();
      this.copyNewMessage = this.newMessage;
      const requestMessage = this.copyNewMessage;
      this.newMessage = '';
      this.user_question=this.copyNewMessage
      this.messages.push({ role: 'user', content: this.copyNewMessage });
      this.messages.push({ role: 'assistant', content: '' });
      this.validationResult = null;
      this.requestSchemaPlan(requestMessage, false).then(() => axios.post(`${this.apiBaseUrl}/api/data`, {
        message: this.copyNewMessage,
        model: this.selectModels,
        session_id: this.sessionId,
        template_id: this.selectedTemplate || null
      }))
        .then(response => {
          this.messages = response.data;
          // this.tableResult = response.data;
          this.$nextTick(() => {
			// 在 nextTick 之后关闭 loading
				this.loadingInstance.closeLoading();
			});

        })
        .catch(error => {
          console.error('Error fetching table:', error);
          this.messages.pop();
          this.$message.error(error.response?.data?.error || '生成表格失败');
          this.$nextTick(() => {
            this.loadingInstance.closeLoading();
          });
        });
       
    },
    copy() {
      // this.copiedList=this.messages
      // this.copiedList.reverse()
    
      // navigator.clipboard.writeText 该方法需要在安全域下才能够使用，比如：https 协议的地址、127.0.0.1、localhost
      const lastAssistantMessage = this.getLastAssistantMessage();
      if (!lastAssistantMessage) {
        this.$message.warning('暂无可复制表格');
        return;
      }
      navigator.clipboard
        .writeText(lastAssistantMessage.content)
        .then(() => {
          this.$message.success("复制成功");
        })
        .catch((err) => {
          // 复制失败
          console.error("复制失败");
        });
    },

    // onError() {
    //   console.error("复制失败");
    // },
    // // 复制
    // onCopy() {
    //   this.$message.success("复制成功");
    // },


    sendMessage() {
      this.copyNewMessage = this.newMessage;
      this.newMessage = '';
      this.user_question=this.copyNewMessage
      // this.messages.push(this.copyNewMessage);
     
    },

    clearAll() {
      this.messages = [];
      this.validationResult = null;
      this.clearHistory();
    },
    getLastAssistantMessage() {
      return [...this.messages].reverse().find(message => message.role === 'assistant' && message.content);
    },
    handleSelect(index) {
      this.activeIndex = index;
    },
    handleClose(done) {
      if (this.loading) {
        return;
      }
      this.$confirm('确定要切换模型吗？')
        .then(_ => {
          this.loading = true;
          this.tempModel = this.selectModels;
          console.log(this.tempModel);
          this.timer = setTimeout(() => {
            done();
            // 动画关闭需要一定的时间
            setTimeout(() => {
              this.loading = false;
              
              this.selectModels = this.tempModel;
            }, 400);
          }, 2000);
        }
        
      )
        .catch(_ => {});
        
    },
    cancelForm() {
      this.loading = false;
      this.dialog = false;
      clearTimeout(this.timer);
    }
  
  },
  mounted() {
    this.clearHistory();
    this.loadTemplates();
  }
}
</script>

<style scoped>
.chat-container {
  width: auto;
  height: 700px;
  border: 1px solid #ccc;
  overflow-y: scroll;
}

.chat-message {
  padding: 10px;
  margin-bottom: 10px;
  border-bottom: 1px solid #ccc;
}

.input-container {
  height: 30px; /* Increase the height to make the input box bigger */
  margin-bottom: 2px;
}
 
</style>
