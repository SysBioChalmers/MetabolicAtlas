import Vue from 'vue';
import VueRouter from 'vue-router';
import NProgress from 'nprogress';
import Home from '@/components/Home';
import Explorer from '@/components/Explorer';
import GemBrowser from '@/components/explorer/GemBrowser';
import Compartment from '@/components/explorer/gemBrowser/Compartment';
import Gene from '@/components/explorer/gemBrowser/Gene';
import Metabolite from '@/components/explorer/gemBrowser/Metabolite';
import Reaction from '@/components/explorer/gemBrowser/Reaction';
import Subsystem from '@/components/explorer/gemBrowser/Subsystem';
import MapViewer from '@/components/explorer/MapViewer';
import InteractionPartners from '@/components/explorer/InteractionPartners';
import SearchTable from '@/components/SearchTable';
import About from '@/components/About';
import Documentation from '@/components/Documentation';
import Repository from '@/components/Repository';
import CompareModels from '@/components/CompareModels';
import FourOFour from '@/components/FourOFour';
import Resources from '@/components/Resources';
import ExternalDb from '@/components/ExternalDb';

Vue.use(VueRouter);

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/search', name: 'search', component: SearchTable },
  { path: '/explore/:model?', name: 'explorer', component: Explorer },
  { path: '/explore/:model/gem-browser', name: 'browser', component: GemBrowser },
  { path: '/explore/:model/gem-browser/compartment/:id', name: 'compartment', component: Compartment },
  { path: '/explore/:model/gem-browser/gene/:id', name: 'gene', component: Gene },
  { path: '/explore/:model/gem-browser/metabolite/:id', name: 'metabolite', component: Metabolite },
  { path: '/explore/:model/gem-browser/reaction/:id', name: 'reaction', component: Reaction },
  { path: '/explore/:model/gem-browser/subsystem/:id', name: 'subsystem', component: Subsystem },
  { path: '/explore/:model/map-viewer/:map_id?', name: 'viewer', component: MapViewer },
  { path: '/explore/:model/interaction-partners/:id?', name: 'interaction', component: InteractionPartners },
  { path: '/about', name: 'about', component: About },
  { path: '/gems/repository/:model_id?', name: 'gems', component: Repository },
  { path: '/gems/comparison', name: 'comparemodels', component: CompareModels },
  { path: '/resources', name: 'resources', component: Resources },
  { path: '/documentation', name: 'documentation', component: Documentation },
  { path: '/identifier/:dbName/:identifierId', name: 'identifier', component: ExternalDb },
  { path: '/*', name: 'fourOfour', component: FourOFour },
];

const router = new VueRouter({
  mode: 'history',
  routes,
  scrollBehavior(to) {
    return to.hash ? { selector: to.hash } : {};
  },
});

NProgress.configure({
  speed: 600,
  showSpinner: false,
});

router.beforeResolve((to, from, next) => { // eslint-disable-line no-unused-vars
  NProgress.start();
  next();
});

router.afterEach((to, from) => { // eslint-disable-line no-unused-vars
  NProgress.done();
});

export default router;
