<template>
  <div>
    <h1>Run Scripts</h1>
    <select v-model="selectedScript">
      <option value="check_version">Check Version</option>
      <option value="upgrade_device">Upgrade Device</option>
      <option value="extract_device_ip">Extract Device IP</option>
    </select>
    <button @click="runScript">Run</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      selectedScript: 'check_version'
    };
  },
  methods: {
    runScript() {
      this.$emit('run-script', this.selectedScript);
    }
  }
};
</script>
