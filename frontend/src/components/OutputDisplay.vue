<template>
  <div>
    <h2>Output</h2>
    <pre>{{ output }}</pre>
    <h2>Error</h2>
    <pre>{{ error }}</pre>
  </div>
</template>

<script>
export default {
  props: ['output', 'error']
};
</script>
