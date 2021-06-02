import Vue from 'vue';
import Vuex from 'vuex';
import models from './modules/models';
import browserTiles from './modules/browserTiles';
import gems from './modules/gems';
import genes from './modules/genes';
import reactions from './modules/reactions';
import subsystems from './modules/subsystems';
import metabolites from './modules/metabolites';
import compartments from './modules/compartments';
import maps from './modules/maps';
import interactionPartners from './modules/interactionPartners';
import search from './modules/search';
import humanProteinAtlas from './modules/humanProteinAtlas';
import europepmc from './modules/europepmc';
import compare from './modules/compare';
import externalDb from './modules/externalDb';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    models,
    browserTiles,
    gems,
    genes,
    reactions,
    subsystems,
    metabolites,
    compartments,
    maps,
    interactionPartners,
    search,
    humanProteinAtlas,
    europepmc,
    compare,
    externalDb,
  },
});
