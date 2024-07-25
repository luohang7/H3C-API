<template>
  <div>
    <ScriptSelector />
    <FileUpload />
  </div>
</template>

<script>
import FileUpload from '@/components/FileUpload.vue';
import ScriptSelector from '@/components/ScriptSelector.vue';

export default {
  components: {
    FileUpload,
    ScriptSelector,
  },
};
</script>

<style>
@import '~vuetify/dist/vuetify.min.css';
</style>

