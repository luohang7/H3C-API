<template>
  <v-app>
    <div>
      <v-file-input
        label="Select CSV file"
        @change="handleFileUpload"
      ></v-file-input>
      <v-btn @click="uploadFile">Upload</v-btn>

      <v-dialog v-model="showSuccessMessage" max-width="290">
        <v-card>
          <v-card-title class="headline">Upload Success</v-card-title>
          <v-card-text>Your file has been uploaded successfully!</v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="green darken-1" text @click="closeModal">Close</v-btn>
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
    handleFileUpload(event) {
      this.selectedFile = event.target.files[0];
    },
    async uploadFile() {
      const formData = new FormData();
      formData.append('file', this.selectedFile);

      try {
        const response = await fetch('/upload_csv', {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log('File uploaded successfully', data);
        this.showSuccessMessage = true;  // 显示成功消息
      } catch (error) {
        console.error('Error uploading file:', error);
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
