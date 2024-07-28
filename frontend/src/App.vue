<template>
  <v-app>
    <v-app-bar app>
      <v-toolbar-title>设备管理系统</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn text :to="{ name: 'Home' }">首页</v-btn>
      <v-btn text :to="{ name: 'DeviceUpgrade' }">设备升级</v-btn>
    </v-app-bar>
    <v-main>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: 'App'
};
</script>

<style>
@import '~vuetify/dist/vuetify.min.css';
</style>
