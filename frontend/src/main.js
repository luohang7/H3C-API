import Vue from 'vue';
import App from './App.vue';
import router from './router';
import Vuetify from 'vuetify';
import 'vuetify/dist/vuetify.min.css';
import VueSocketIOExt from 'vue-socket.io-extended';
import SocketIO from 'socket.io-client';


Vue.config.productionTip = false;

Vue.use(Vuetify);

Vue.use(VueSocketIOExt, SocketIO('http://localhost:5000'))

new Vue({
  router,
  vuetify: new Vuetify(),
  render: h => h(App)
}).$mount('#app');
