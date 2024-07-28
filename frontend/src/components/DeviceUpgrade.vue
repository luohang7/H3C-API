<template>
  <v-container>
    <h1>设备升级</h1>
    <!-- 脚本选择器组件 -->
    <script-selector />
    <!-- 文件上传组件 -->
    <file-upload />
  </v-container>
</template>

<script>
import ScriptSelector from './ScriptSelector.vue';
import FileUpload from './FileUpload.vue';

export default {
  name: 'DeviceUpgrade',
  components: {
    ScriptSelector,
    FileUpload,
  },
};
</script>

<style>
@import "~vuetify/dist/vuetify.min.css";
</style>