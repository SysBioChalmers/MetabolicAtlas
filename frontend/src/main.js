import Vue from 'vue';
import VueMatomo from 'vue-matomo';
import VueMeta from 'vue-meta';
import axios from 'axios';
import vueDebounce from 'vue-debounce';
import NProgress from 'nprogress';
import App from '@/App';
import router from '@/router';
import { default as EventBus } from '@/event-bus';
import store from './store';
import linkHandlerMixin from './mixins/linkHandler';

axios.defaults.baseURL = '/api/v2';
axios.defaults.onDownloadProgress = function onDownloadProgress(progressEvent) {
  const percentCompleted = Math.floor((progressEvent.loaded * 100.0) / progressEvent.total);
  NProgress.set(percentCompleted / 100.0);
};

Vue.use(vueDebounce);

if (navigator.doNotTrack !== '1') {
  Vue.use(VueMatomo, {
    host: 'https://csbi.chalmers.se/matomo',
    siteId: process.env.VUE_APP_MATOMOID,
    router,
  });
}

Vue.mixin(linkHandlerMixin);

Vue.use(VueMeta);

new Vue({ // eslint-disable-line no-new
  el: '#app',
  router,
  store,
  EventBus,
  render: h => h(App),
});
