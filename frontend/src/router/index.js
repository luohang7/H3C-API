import Vue from 'vue';
import VueRouter from 'vue-router';
import DeviceManagement from '@/views/DeviceManagement.vue';

Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    name: 'DeviceManagement',
    component: DeviceManagement
  },
];

const router = new VueRouter({
    mode: 'history',
    base: process.env.BASE_URL,
    routes,
});

export default router;
