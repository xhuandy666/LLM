<template>
  <el-container>
    <el-header>
      <el-menu
      :default-active="activeIndex2"
      class="el-menu-demo"
      mode="horizontal"
      @select="handleSelect"
      background-color="#545c64"
      text-color="#fff"
      active-text-color="#ffd04b">
      <el-menu-item index="1"> <el-button type="text" @click="open">帮助</el-button></el-menu-item>
      <span
      style=" background-color:#545c64 ;position: absolute;color:#fff ;padding-top: 0px;right: 43%;font-size: 20px;font-weight: bold"> 基于大模型的表格数据生成</span>

      </el-menu>
    </el-header>
    <el-main>
      <el-card class="box-card">
    <div slot="header" class="head">  
      <span style="font-weight: bold;font-size: 15px;margin-top:-55px;">TablesGenerator</span>
    </div>
    <div id="dialog_container" style="display: flex;flex-direction: column;">
            <div v-for="message in messages" :class="['message', message.role === 'user' ? 'user' : 'assistant']">
                {{ message.content }}
            </div>
        <!-- <el-divider content-position="right">{{ user_name }} </el-divider>
        <span id="question_card" style="font-size: 15px;">{{ user_question }}</span>
        <el-divider content-position="left">回答</el-divider>
        <span id="answer_card">
          <v-md-editor :value="tableResult" mode="preview"></v-md-editor>
        </span> -->
      </div>
    
    <el-divider ></el-divider>
    <el-input
        type="textarea"
        :autosize="{ minRows: 2, maxRows: 4}"
        @keydown.enter.native="sendMessage"
        v-model="newMessage"
    >
    </el-input>
      <div class="buttons" >
      <el-button  type="danger" plain @click="fetchTable()">生成表格</el-button>
      <el-button  type="primary" @click="copy">复制表格</el-button>
    </div>
  </el-card>

  </el-main>
</el-container>
</template>
<style lang="scss" scoped>

.message {
    max-width: 50%;
    word-wrap: break-word;
}

.user{
  margin-left: auto;
  align-self: flex-end;
}

.assistant{
  margin-right: auto;
  align-self: flex-start;
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
  min-width: 900px;
  text-align: left;

}

#dialog_container {
  overflow: auto;
  scroll-margin-right: 1px;
  /*根据屏幕占比设置高度*/
  min-height: calc(100vh - 360px);
  max-height: calc(100vh - 360px);
}

  // .home-view {
  //   display: flex;
  //   /* 与窗口同宽 */
  //   width: 100vw;
  //   /* 水平方向上剧中 */
  //   justify-content: center;

  //   .chat-panel {
  //     /* 聊天面板flex布局，让会话列表和聊天记录左右展示 */
  //     display: flex;
  //     /* 让聊天面板圆润一些 */
  //     border-radius: 20px;
  //     background-color: white;
  //     /* 给一些阴影 */
  //     box-shadow: 0 0 20px 20px rgba(black, 0.05);
  //     /* 与上方增加一些间距 */
  //     margin-top: 70px;
     
  //     /* 右侧消息记录面板*/
  //     .message-panel {
  //       width: 700px;
  //       height: 800px;
  //     }
  //   }
  // }
  // .message-input {
  //   padding: 20px;
  //   border-top: 1px solid rgba(black, 0.07);
  //   border-left: 1px solid rgba(black, 0.07);
  //   border-right: 1px solid rgba(black, 0.07);
  //   border-top-right-radius: 5px;
  //   border-top-left-radius: 5px;
  // }

  // .button-wrapper {
  //   display: flex;
  //   justify-content: flex-end;
  //   margin-top: 0px;
  // }


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
export default {
  data() {
    return {
      textarea: '',
      messages: [],
      newMessage: '',
      user_question: '',
      copyNewMessage: '',
      tableResult: '',
      user_name: 'user',
      messages: []
    };
  },
  methods: {
    clearHistory(){
      axios.get('http://127.0.0.1:5000/api/clear')
    },

    fetchTable() {
      this.copyNewMessage = this.newMessage;
      this.newMessage = '';
      this.user_question=this.copyNewMessage
      this.messages.push(this.copyNewMessage);
      axios.post('http://127.0.0.1:5000/api/data', { message: this.copyNewMessage })
        .then(response => {
          this.messages = response.data;
          // this.tableResult = response.data;
        })
        .catch(error => {
          console.error('Error fetching table:', error);
        });
    },
    copy() {
      // navigator.clipboard.writeText 该方法需要在安全域下才能够使用，比如：https 协议的地址、127.0.0.1、localhost
      navigator.clipboard
        .writeText(this.tableResult)
        .then(() => {
          this.$tableResult.success("复制成功");
        })
        .catch((err) => {
          // 复制失败
          console.error("复制失败");
        });
    },




    sendMessage() {
      this.copyNewMessage = this.newMessage;
      this.newMessage = '';
      this.user_question=this.copyNewMessage
      // this.messages.push(this.copyNewMessage);
     
    },

    clearAll() {
      this.messages = [];
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