<template>
  <div>
    <ScriptSelector @run-script="runScript" />
    <OutputDisplay :output="output" :error="error" />
    <FileUpload />
  </div>
</template>

<script>
import FileUpload from '@/components/FileUpload.vue';
import ScriptSelector from '@/components/ScriptSelector.vue';
import OutputDisplay from '@/components/OutputDisplay.vue';

export default {
  components: {
    FileUpload,
    ScriptSelector,
    OutputDisplay
  },
  data() {
    return {
      output: '',
      error: ''
    };
  },
  methods: {
    runScript(script) {
      console.log(`Running script: ${script}`);
      fetch('/run_script', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ script: script })
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
          console.log('Received response:', data);
          this.output = data.output;
          this.error = data.error;
        })
        .catch(error => {
          console.error('Error during fetch:', error);
          this.output = '';
          this.error = error.message;
        });
    }
  }
};
</script>
