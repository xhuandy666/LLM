
  <!-- <div id="app">
    <el-container>
  <el-header>基于大模型的表格数据生成</el-header>
  <el-main>
    <el-input
    style="width: auto;margin-right: 50px;"
  type="textarea"
  autosize
  placeholder="请输入内容"
  v-model="textarea1">
</el-input>

<el-input
style="width: 700px;"
  type="textarea"
  :autosize="{ minRows: 1, maxRows: 20}"
  placeholder=" "
  v-model="textarea2">
</el-input>
<div style="margin: 10px 0;"></div>
  </el-main>
  </el-container>

    <router-view/>
  </div> -->
  
  <template>
  <!-- 最外层页面于窗口同宽，使聊天面板居中 -->
  <div class="home-view">
  
    <!-- 整个聊天面板 -->
    <div class="chat-panel">
      <!-- 左侧的会话列表 -->
      <!-- <div class="session-panel">
        <div class="title">ChatGPT助手</div>
        <div class="description">构建你的AI助手</div>
      </div> -->
      <!-- 右侧的消息记录 -->
      <div class="message-panel">
        <div>
    <div class="chat-container" ref="chatContainer">
      <div class="chat-message" v-for="(message, index) in messages" :key="index">
        {{ message }}
      </div>
    </div>

    <!-- <div class="input-container">
      <input style="margin-top:10px;height:60px;width:680px" type="text" v-model="newMessage" placeholder="输入你的消息...">
      <button @click="sendMessage">发送</button>
    </div> -->
    <!-- 输入框 -->
    <el-input
    v-model="newMessage"
    style="margin-top: 10px;"
  type="textarea"
  :rows="2"
  placeholder="请输入内容"
  >
</el-input>
<el-button  type="primary" plain @click="sendMessage()">发送</el-button>

  </div>
  </div>
    </div>
  </div>
</template>
<style lang="scss" scoped>
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
      // /* 左侧聊天会话面板*/
      // .session-panel {
      //   background-color: rgb(231, 248, 255);
      //   width: 300px;
      //   border-top-left-radius: 20px;
      //   border-bottom-left-radius: 20px;
      //   padding: 20px;
      //   position: relative;
      //   border-right: 1px solid rgba(black, 0.07);
      //   /* 标题*/
      //   .title {
      //     margin-top: 20px;
      //     font-size: 20px;
      //   }

      //   /* 描述*/
      //   .description {
      //     color: rgba(black, 0.7);
      //     font-size: 10px;
      //     margin-top: 10px;
      //   }
      // }

      /* 右侧消息记录面板*/
      .message-panel {
        width: 700px;
        height: 800px;
      }
    }
  }
</style>

<script>

import axios from 'axios';
export default {
  data() {
    return {
      textarea: '',
      messages: [],
      newMessage: ''
    };
  },
  methods: {
    sendMessage() {
      // Make a request to the backend using Axios or Fetch
      // Replace 'backend-url' with the actual URL of your Flask backend
      axios.post('http://127.0.0.1:5000/api/data', { message: this.newMessage })
        .then(response => {
          // Handle the response from the backend
          // For example, you can update the messages array with the response data
          console.log(response.data);
          this.messages.push(response.data);
          // Clear the input field
          this.newMessage = '';
        })
        .catch(error => {
          // Handle any errors that occur during the request
          console.error(error);
        });
    }
  }
};
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