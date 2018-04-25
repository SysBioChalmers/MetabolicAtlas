import Vue from 'vue';
import VueRouter from 'vue-router';
import GemsExplorer from 'components/GemsExplorer';
import Resources from 'components/Resources';
import About from 'components/About';
import Contact from 'components/Contact';
import Help from 'components/Help';
import SearchTable from 'components/SearchTable';
import Models from 'components/Models';
import CompareModels from 'components/CompareModels';
import Atlas from 'components/Atlas';
import Hreed from 'components/Hreed';

Vue.use(VueRouter);

const routes = [
  { path: '/', name: 'GemsExplorerRoot', component: GemsExplorer },
  { path: '/GemsExplorer/:model/', name: 'GemsExplorerModel', component: GemsExplorer },
  { path: '/GemsExplorer/:model/:type/:id', name: 'GemsExplorer', component: GemsExplorer },
  { path: '/about', name: 'about', component: About },
  { path: '/comparemodels', name: 'comparemodels', component: CompareModels },
  { path: '/search', name: 'search', component: SearchTable },
  { path: '/gems', name: 'gems', component: Models },
  { path: '/gems/:id', name: 'gemsID', component: Models },
  { path: '/resources', name: 'resources', component: Resources },
  { path: '/documentation', name: 'documentation', component: Help },
  { path: '/contact', name: 'contact', component: Contact },
  { path: '/Atlas', name: 'atlas', component: Atlas },
  { path: '/hreed', name: 'hreed', component: Hreed },
  { path: '/*', name: 'GemsExplorerDefault', component: GemsExplorer },
];

const router = new VueRouter({
  mode: 'history',
  routes,
});

export default router;
