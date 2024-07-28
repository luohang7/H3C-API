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
      <v-btn @click="runScript" color="primary" class="mx-2">运行</v-btn>
      <v-btn @click="stopScript" color="error" class="mx-2">停止</v-btn>
      <div v-if="scriptOutput">
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
      selectedScript: 'check_version',
      scripts: [
        {text: '检查版本', value: 'check_version'},
        {text: '升级设备', value: 'upgrade_device'}
      ],
      scriptOutput: ''
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
    });
  },
  methods: {
    clearOutput(){
      this.scriptOutput = '';
    },
    async runScript() {
      this.clearOutput();
      try {
        const response = await fetch('/run_script', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({script: this.selectedScript})
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
</style>
