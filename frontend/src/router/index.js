import Vue from 'vue';
import VueRouter from 'vue-router';
import Home from '@/views/Home.vue';
import DeviceUpgrade from '@/components/DeviceUpgrade.vue';

Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/device-upgrade',
    name: 'DeviceUpgrade',
    component: DeviceUpgrade,
  },
];

const router = new VueRouter({
    mode: 'history',
    base: process.env.BASE_URL,
    routes,
});

export default router;
