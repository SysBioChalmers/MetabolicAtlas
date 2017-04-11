import Vue from 'vue';
import VueRouter from 'vue-router';
import NetworkGraph from 'components/NetworkGraph';
import About from 'components/About';
import ClosestInteractionPartners from 'components/ClosestInteractionPartners';
import ConnectedMetabolites from 'components/ConnectedMetabolites';

Vue.use(VueRouter);

const routes = [
  { path: '/', name: 'network graph', component: NetworkGraph },
  { path: '/about', name: 'about', component: About },
  { path: '/closest-interaction-partners/:reaction_component_id', name: 'closest-interaction-partners', component: ClosestInteractionPartners },
  { path: '/connected-metabolites/:enzyme_id', name: 'connected-metabolites', component: ConnectedMetabolites },
];

const router = new VueRouter({
  mode: 'history',
  routes,
});

export default router;
