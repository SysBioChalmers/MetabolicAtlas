import Vue from 'vue';
import VueCookie from 'vue-cookie';

Vue.use(VueCookie);

export function isCookiePolicyAccepted() {
  return Vue.cookie.get('acceptCookiePolicy');
}

export function acceptCookiePolicy() {
  Vue.cookie.set('acceptCookiePolicy', true);
}
