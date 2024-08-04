import Vue from 'vue';
import App from './App.vue';
import router from './router';
import Vuetify from 'vuetify';
import VueSocketIOExt from 'vue-socket.io-extended';
import SocketIO from 'socket.io-client';
import vuetify from './plugins/vuetify'


Vue.config.productionTip = false;

Vue.use(Vuetify);

Vue.use(VueSocketIOExt, SocketIO('/'))

new Vue({
  router,
  vuetify,
  render: h => h(App)
}).$mount('#app');
