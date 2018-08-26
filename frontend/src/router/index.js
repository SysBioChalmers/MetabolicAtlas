import Vue from 'vue';
import VueRouter from 'vue-router';
import Home from 'components/Home';
import Explorer from 'components/Explorer';
import Resources from 'components/Resources';
import About from 'components/About';
import Help from 'components/Help';
import Models from 'components/Models';
import CompareModels from 'components/CompareModels';
import Atlas from 'components/Atlas';
import Hreed from 'components/Hreed';


Vue.use(VueRouter);

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/explore', name: 'explorerRoot', component: Explorer, props: true },
  { path: '/explore/search', name: 'search', component: Explorer },
  { path: '/explore/browser/:model', name: 'browserRoot', component: Explorer, props: true },
  { path: '/explore/browser/:model/:type/:id', name: 'browser', component: Explorer, props: true },
  { path: '/explore/viewer/:model', name: 'viewer', component: Explorer, props: true },
  { path: '/about', name: 'about', component: About },
  { path: '/gems', name: 'gems', component: Models },
  { path: '/gems/compare', name: 'comparemodels', component: CompareModels },
  { path: '/gems/:id', name: 'gemsID', component: Models },
  { path: '/resources', name: 'resources', component: Resources },
  { path: '/documentation', name: 'documentation', component: Help },
  { path: '/Atlas', name: 'atlas', component: Atlas },
  { path: '/hreed', name: 'hreed', component: Hreed },
  { path: '/*', name: 'Home', component: Home },
];

const router = new VueRouter({
  mode: 'history',
  routes,
});

export default router;
