<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1>设备管理</h1>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="6">
        <script-selector />
      </v-col>
      <v-col cols="6">
        <file-upload />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import ScriptSelector from '@/components/ScriptSelector.vue';
import FileUpload from '@/components/FileUpload.vue';

export default {
  name: 'DeviceManagement',
  components: {
    ScriptSelector,
    FileUpload
  }
}
</script>
