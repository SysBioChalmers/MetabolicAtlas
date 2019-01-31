// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import axios from 'axios';
import Vue from 'vue';
import lodash from 'lodash';
import VueLodash from 'vue-lodash/dist/vue-lodash.min';
import App from './App';
import router from './router';
import { EventBus } from './event-bus';

axios.defaults.baseURL = '/api';

Vue.use(VueLodash, lodash);

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  EventBus,
  template: '<App/>',
  components: { App },
});
