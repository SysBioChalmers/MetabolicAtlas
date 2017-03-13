import Vue from 'vue';
import VueRouter from 'vue-router';
import Hello from 'components/Hello';
import ClosestInteractionPartners from 'components/ClosestInteractionPartners';
import ConnectedMetabolites from 'components/ConnectedMetabolites';

Vue.use(VueRouter);

const routes = [
  { path: '/', component: Hello },
  { path: '/closest-interaction-partners/:reaction_component_id', name: 'closest-interaction-partners', component: ClosestInteractionPartners },
  { path: '/connected-metabolites/:enzyme_id', name: 'connected-metabolites', component: ConnectedMetabolites },
];

const router = new VueRouter({
  mode: 'history',
  routes,
});

export default router;
