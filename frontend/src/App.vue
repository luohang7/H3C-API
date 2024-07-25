<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
import Vue from 'vue';
import SocketIO from 'socket.io-client';
import VueSocketIO from 'vue-socket-io';

// 连接到Socket.io服务器
const socket = SocketIO('http://localhost:5000');

// 将socket连接添加到Vue原型，以便在任何组件中都可以通过this.$socket访问
Vue.use(new VueSocketIO({
  connection: socket,
}));
export default {
  name: 'App'


};
</script>

<style>
@import '~vuetify/dist/vuetify.min.css';
</style>
