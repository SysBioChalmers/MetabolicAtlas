// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import axios from 'axios';
import Vue from 'vue';
import VueHead from 'vue-head';
import VueI18n from 'vue-i18n';
import lodash from 'lodash';
import VueLodash from 'vue-lodash/dist/vue-lodash.min';
import App from './App';
import router from './router';
import { EventBus } from './event-bus';
import { default as messages } from './localization';

axios.defaults.baseURL = '/api';

Vue.use(VueI18n);
Vue.use(VueHead);
Vue.use(VueLodash, lodash);
const i18n = new VueI18n({
  locale: 'en',
  messages,
});

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  EventBus,
  i18n,
  template: '<App/>',
  components: { App },
  head: {
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
    ],
  },
});

