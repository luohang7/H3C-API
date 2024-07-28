<template>
  <v-app-bar app color="primary" dark>
    <v-toolbar-title>设备管理系统</v-toolbar-title>
    <v-spacer></v-spacer>
    <v-btn text @click="navigateToUpgrade">设备升级</v-btn>
  </v-app-bar>
</template>

<script>
export default {
  name: 'Navbar',
  methods: {
    navigateToUpgrade() {
      if (this.$route.path !== '/') {
        this.$router.push('/');
      }
    }
  }
}
</script>
