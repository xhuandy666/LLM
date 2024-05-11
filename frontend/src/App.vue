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
      <el-menu-item index="1"> <el-button type="text" @click="open">帮助</el-button></el-menu-item>
      <el-menu-item index="2"> <el-button type="text" @click="dialog = true" style="margin-left:1700px" >设置</el-button></el-menu-item>
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
          <el-option label="ERNIE-Speed-128K" value="ernie-speed-128k"></el-option>
          <el-option label="ERNIE-4.0-8K-0329" value="ernie-4.0-8k-0329"></el-option>
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
      <div v-for="message in messages":class="['message-row', message.role === 'user' ? 'right' : 'left']">
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
      <el-button  type="primary" icon="el-icon-star-on" plain @click="AutoOptimize()":loading="loading">{{ loading ? '优化中 ...' : '指令优化' }}</el-button>
      <el-button  type="primary" icon="el-icon-upload" plain @click="exportCsv()">导出csv</el-button>
    </div>
  </el-card>
<!-- v-clipboard:copy="this.messages.content"
      v-clipboard:success="onCopy"
      v-clipboard:error="onError" -->
  </el-main>
</el-container>
</template>
<style lang="scss" scoped>

.message-row {
    display: flex;

    &.right {
      // 消息显示在右侧
      justify-content: flex-end;

      .row {
        // 头像也要靠右侧
        .avatar-wrapper {
          display: flex;
          justify-content: flex-end;
          .avatar {
            box-shadow: 20px 20px 20px 3px rgba(0, 0, 0, 0.03);
            margin-bottom: 10px;
          }
        }

        // 用户回复的消息和ChatGPT回复的消息背景颜色做区分
        .message {
          background-color: rgb(231, 248, 255);
          
        }
      }
    }

    // 默认靠左边显示
    .row {
      .avatar-wrapper {
        .avatar {
          box-shadow: 20px 20px 20px 3px rgba(0, 0, 0, 0.03);
          margin-bottom: 10px;
          
        }
      }

      .message {
        font-size: 15px;
        padding: 1.5px;
        // 限制消息展示的最大宽度
        max-width: 600px;
        // 圆润一点
        border-radius: 7px;
        // 给消息框加一些描边，看起来更加实一些，要不然太扁了轻飘飘的。
        border: 1px solid rgba(black, 0.1);
        // 增加一些阴影看起来更加立体
        box-shadow: 20px 20px 20px 1px rgba(0, 0, 0, 0.01);
      }
    }
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
.box-card {
  margin: 2% auto;
  width: 50%;
  min-width: 1100px;
  text-align: left;

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
    /* 与窗口同宽 */
    width: 100vw;
    /* 水平方向上剧中 */
    justify-content: center;

    .chat-panel {
      /* 聊天面板flex布局，让会话列表和聊天记录左右展示 */
      display: flex;
      /* 让聊天面板圆润一些 */
      border-radius: 20px;
      background-color: white;
      /* 给一些阴影 */
      box-shadow: 0 0 20px 20px rgba(black, 0.05);
      /* 与上方增加一些间距 */
      margin-top: 70px;
     
      /* 右侧消息记录面板*/
      .message-panel {
        width: 700px;
        height: 800px;
      }
    }
  }
  .message-input {
    padding: 20px;
    border-top: 1px solid rgba(black, 0.07);
    border-left: 1px solid rgba(black, 0.07);
    border-right: 1px solid rgba(black, 0.07);
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
      user_question: '',
      copyNewMessage: '',
      user_name: 'user',
      user_Logo: "https://img0.baidu.com/it/u=2864837501,1810663520&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=500",
      assistant_Logo: "https://img2.baidu.com/it/u=2784541464,2988923813&fm=253&fmt=auto&app=138&f=PNG?w=240&h=240",
      dialog: false,
      loading: false,
      selectModels: 'ernie-speed-128k',
      ModelsIntro: 'ERNIE Speed是百度2024年最新发布的自研高性能大语言模型，通用能力优异，适合作为基座模型进行精调，更好地处理特定场景问题，同时具备极佳的推理性能。',
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
    parseMarkdownTable() {  
      // 解析Markdown文本，并提取出HTML表格  
      const html = this.md.render(this.messages[this.messages.length - 1].content);  
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
      if (!htmlTable) return;  
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
      this.loading = true;
      axios.post('http://127.0.0.1:5000/api/optimize', { message: this.newMessage})
        .then(response => {
          this.newMessage = response.data;
          this.loading = false;
        })
        .catch(error => {
          console.error('Error optimize prompt:', error);
        });
    },
    updataInput(){
      if(this.selectModels === 'ernie-speed-128k'){
        this.ModelsIntro = 'ERNIE Speed是百度2024年最新发布的自研高性能大语言模型，通用能力优异，适合作为基座模型进行精调，更好地处理特定场景问题，同时具备极佳的推理性能。';
      }else if(this.selectModels === 'ernie-4.0-8k-0329'){
        this.ModelsIntro = 'ERNIE 4.0是百度自研的旗舰级超大规模⼤语⾔模型，相较ERNIE 3.5实现了模型能力全面升级，广泛适用于各领域复杂任务场景；支持自动对接百度搜索插件，保障问答信息时效。';
      }
    },
    
    clearHistory(){
      axios.get('http://127.0.0.1:5000/api/clear')
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
      this.loadingInstance  = this.starLoading();
      this.copyNewMessage = this.newMessage;
      this.newMessage = '';
      this.user_question=this.copyNewMessage
      this.messages.push(this.copyNewMessage);
      axios.post('http://127.0.0.1:5000/api/data', { message: this.copyNewMessage, model: this.selectModels})
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
        });
       
    },
    copy() {
      // this.copiedList=this.messages
      // this.copiedList.reverse()
    
      // navigator.clipboard.writeText 该方法需要在安全域下才能够使用，比如：https 协议的地址、127.0.0.1、localhost
      navigator.clipboard
        .writeText(this.messages[this.messages.length - 1].content)
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
      location.reload();
      this.messages = [];
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