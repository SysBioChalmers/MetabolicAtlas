import Vue from 'vue';
import VueRouter from 'vue-router';
import NetworkGraph from 'components/NetworkGraph';
import Resources from 'components/Resources';
import About from 'components/About';
import Contact from 'components/Contact';
import Help from 'components/Help';
import SearchTable from 'components/SearchTable';

Vue.use(VueRouter);

const routes = [
  { path: '/', name: 'network graph', component: NetworkGraph },
  { path: '/about', name: 'about', component: About },
  { path: '/search', name: 'search', component: SearchTable },
  { path: '/resources', name: 'resources', component: Resources },
  { path: '/help', name: 'help', component: Help },
  { path: '/contact', name: 'contact', component: Contact },
];

const router = new VueRouter({
  mode: 'history',
  routes,
});

export default router;
