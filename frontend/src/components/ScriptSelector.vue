<template>
  <v-app>
    <v-container>
      <h1>运行脚本</h1>
      <v-select
        v-model="selectedScript"
        :items="scripts"
        label="选择脚本"
        outlined
      ></v-select>

      <div v-if="selectedScript === 'file_transfer'">
        <v-text-field
          v-model="tftpServer"
          label="TFTP服务器地址"
          outlined
        ></v-text-field>
        <v-textarea
          v-model="fileList"
          label="文件列表 (每行一个文件名)"
          outlined
        ></v-textarea>
      </div>

      <div v-if="selectedScript === 'check_version'">
        <v-text-field
            v-model="targetVersion"
            label="目标版本(例如:S5130S_EI-CMW710-R6357)"
            outlined
        ></v-text-field>
      </div>

      <v-btn @click="runScript" color="primary" class="mx-2">运行</v-btn>
      <v-btn @click="stopScript" color="error" class="mx-2">停止</v-btn>

      <div v-if="scriptOutput" id="output">
        <h2>脚本输出</h2>
        <pre>{{ scriptOutput }}</pre>
      </div>
    </v-container>
  </v-app>
</template>

<script>
export default {
  data() {
    return {
      selectedScript: 'netconf_set',
      scripts: [
        { text: '配置netconf', value: 'netconf_set' },
        { text: '检查版本', value: 'check_version' },
        { text: '生成升级表格', value: 'extract_device_ip' },
        { text: '获取升级包', value: 'file_transfer' },
        { text: '升级设备', value: 'upgrade_device' },
      ],
      tftpServer: '',
      fileList: '',
      scriptOutput: '',
      targetVersion: '',
    };
  },
  mounted() {
    this.$socket.client.on('connect', () => {
      console.log('成功连接到 WebSocket');
    });
    this.$socket.client.on('disconnect', () => {
      console.log('WebSocket 连接已断开');
    });
    this.$socket.client.on('脚本输出', (data) => {
      console.log('输出:', data);
      this.scriptOutput += data.output + '\n';
       this.$nextTick(() => {
        const outputDiv = this.$el.querySelector('#output');
         if (outputDiv) {
           outputDiv.scrollTop = outputDiv.scrollHeight;
         }
      });
    });
  },
  methods: {
    clearOutput(){
      this.scriptOutput = '';
    },
    async runScript() {
      this.clearOutput();
      try {
        const requestBody = {
          script: this.selectedScript
        };

        if (this.selectedScript === 'file_transfer') {
          requestBody.tftpServer = this.tftpServer;
          requestBody.fileList = this.fileList.split('\n').map(file => file.trim()).join(','); // 将换行符转换为逗号，并去除每行两端的空格
        }

        if (this.selectedScript === 'check_version') {
          requestBody.targetVersion = this.targetVersion;
        }

        const response = await fetch('/run_script', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
          throw new Error('响应异常');
        }

        const data = await response.json();
        console.log('脚本已成功运行', data);
      } catch (error) {
        console.error('运行脚本时出错:', error);
      }
    },
    async stopScript() {
      try {
        const response = await fetch('/stop_script', {
          method: 'POST'
        });

        if (!response.ok) {
          throw new Error('响应异常');
        }

        const data = await response.json();
        console.log('脚本已成功停止', data);
      } catch (error) {
        console.error('停止脚本时出错:', error);
      }
    }
  }
};
</script>

<style>
@import "~vuetify/dist/vuetify.min.css";

h1 {
  margin-bottom: 20px;
}
#output {
  height: 400px;
  overflow-y: auto;
  background-color: #f5f5f5;
  padding: 10px;
  border: 1px solid #ccc;
  margin-top: 20px;
  white-space: pre-wrap; /* 保持换行 */
}
</style>
