<template>
  <v-app>
    <div>
      <v-file-input
        label="请按此文件名devices.csv上传文件"
        @change="handleFileUpload"
      ></v-file-input>
      <v-btn @click="uploadFile">上传</v-btn>

      <v-dialog v-model="showSuccessMessage" max-width="290">
        <v-card>
          <v-card-title class="headline">上传成功</v-card-title>
          <v-card-text>您的文件已成功上传！</v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="green darken-1" text @click="closeModal">关闭</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </v-app>
</template>

<script>
export default {
  data() {
    return {
      selectedFile: null,
      showSuccessMessage: false
    };
  },
  methods: {
    handleFileUpload(file) {
      this.selectedFile = file;
    },
    async uploadFile() {
      if (!this.selectedFile) {
        console.error('没有选择文件');
        return;
      }
      const formData = new FormData();
      formData.append('file', this.selectedFile);

      try {
        const response = await fetch('/upload_csv', {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          throw new Error('网络响应不正常');
        }

        const data = await response.json();
        console.log('文件上传成功', data);
        this.showSuccessMessage = true;
      } catch (error) {
        console.error('文件上传出错:', error);
      }
    },
    closeModal() {
      this.showSuccessMessage = false;
    }
  }
};
</script>

<style>
@import "~vuetify/dist/vuetify.min.css";
</style>
