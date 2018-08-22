import Vue from 'vue';
import VueRouter from 'vue-router';
import GemsExplorer from 'components/GemsExplorer';
import Resources from 'components/Resources';
import About from 'components/About';
import Help from 'components/Help';
import SearchTable from 'components/SearchTable';
import Models from 'components/Models';
import CompareModels from 'components/CompareModels';
import MetabolicViewer from 'components/MetabolicViewer';

Vue.use(VueRouter);

const routes = [
  { path: '/', name: 'GemsExplorerRoot', component: GemsExplorer },
  { path: '/gemsExplorer/:model/', name: 'GemsExplorerModel', component: GemsExplorer, props: true },
  { path: '/gemsExplorer/:model/:type/:id', name: 'GemsExplorer', component: GemsExplorer, props: true },
  { path: '/metabolicViewer/:model/', name: 'MetabolicViewer', component: MetabolicViewer, props: true },
  { path: '/about', name: 'about', component: About },
  { path: '/search', name: 'search', component: SearchTable },
  { path: '/gems', name: 'gems', component: Models },
  { path: '/gems/compare/', name: 'comparemodels', component: CompareModels },
  { path: '/gems/:id', name: 'gemsID', component: Models },
  { path: '/resources', name: 'resources', component: Resources },
  { path: '/documentation', name: 'documentation', component: Help },
  { path: '/contact', name: 'contact', component: Contact },
  { path: '/*', name: 'GemsExplorerDefault', component: GemsExplorer },
];

const router = new VueRouter({
  mode: 'history',
  routes,
});

export default router;
