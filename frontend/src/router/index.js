import Vue from 'vue';
import VueRouter from 'vue-router';
import Home from 'components/Home';
import Explorer from 'components/Explorer';
import Resources from 'components/Resources';
import About from 'components/About';
import Help from 'components/Help';
import Models from 'components/Models';
import ModelsFTP from 'components/ModelsFTP';
import CompareModels from 'components/CompareModels';
import NotFound from 'components/NotFound';

Vue.use(VueRouter);

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/explore', name: 'explorerRoot', component: Explorer, props: true },
  { path: '/explore/search', name: 'search', component: Explorer },
  { path: '/explore/gem-browser/:model', name: 'browserRoot', component: Explorer, props: true },
  { path: '/explore/gem-browser/:model/:type/:id', name: 'browser', component: Explorer, props: true },
  { path: '/explore/map-viewer/:model', name: 'viewer', component: Explorer, props: true },
  { path: '/explore/map-viewer/:model/compartment/:id/:dim', name: 'viewerCompartment', component: Explorer, props: true },
  { path: '/explore/map-viewer/:model/subsystem/:id/:dim', name: 'viewerSubsystem', component: Explorer, props: true },
  { path: '/about', name: 'about', component: About },
  { path: '/gems', name: 'gems', component: Models },
  { path: '/gems/download', name: 'gemsDL', component: ModelsFTP },
  { path: '/gems/compare', name: 'comparemodels', component: CompareModels },
  { path: '/resources', name: 'resources', component: Resources },
  { path: '/documentation', name: 'documentation', component: Help },
  { path: '/*', name: 'notFound', component: NotFound },
];

const router = new VueRouter({
  mode: 'history',
  routes,
});

export default router;
