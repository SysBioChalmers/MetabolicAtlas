import Vue from 'vue';
import VueRouter from 'vue-router';
import NetworkGraph from 'components/NetworkGraph';
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
  { path: '/', name: 'network graph', component: NetworkGraph },
  { path: '/about', name: 'about', component: About },
  { path: '/comparemodels', name: 'compare models', component: CompareModels },
  { path: '/search', name: 'search', component: SearchTable },
  { path: '/models', name: 'models', component: Models },
  { path: '/resources', name: 'resources', component: Resources },
  { path: '/help', name: 'help', component: Help },
  { path: '/contact', name: 'contact', component: Contact },
  { path: '/Atlas', name: 'atlas', component: Atlas },
  { path: '/hreed', name: 'contact', component: Hreed },
];

const router = new VueRouter({
  mode: 'history',
  routes,
});

export default router;
