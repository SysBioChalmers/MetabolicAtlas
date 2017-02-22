// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import axios from 'axios';
import Vue from 'vue';
import VueRouter from 'vue-router';
import App from './App';
import Hello from './components/Hello';
import ConnectedMetabolites from './components/ConnectedMetabolites';

Vue.use(VueRouter);

axios.defaults.baseURL = 'http://localhost:8000/api';

const routes = [
  { path: '/', component: Hello },
  { path: '/connected-metabolites/:enzyme_id', component: ConnectedMetabolites },
];

const router = new VueRouter({
  mode: 'history',
  routes,
});

/* eslint-disable no-new */
new Vue({
  router,
  el: '#app',
  template: '<App/>',
  components: { App },
});

