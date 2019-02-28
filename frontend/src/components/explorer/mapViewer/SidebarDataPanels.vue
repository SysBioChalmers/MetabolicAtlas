<template>
  <div>
    <div class="column" v-if="tissue && dim === '2d'">
      <div class="card">
        <header class="card-header" @click.prevent="showLvlCardContent = !showLvlCardContent">
          <p class="card-header-title">
            Selected tissue: {{ tissue }}
          </p>
          <a href="#" class="card-header-icon" aria-label="more options">
            <span class="icon">
              <i class="fa fa-caret-down" aria-hidden="true" v-if="!showLvlCardContent"></i>
              <i class="fa fa-caret-up" aria-hidden="true" v-else="showLvlCardContent"></i>
            </span>
          </a>
        </header>
        <div v-html="getExpLvlLegend()" v-show="showLvlCardContent"></div>
      </div>
    </div>
    <div class="column" v-if="mapName">
      <div class="card">
        <header class="card-header" @click.prevent="showMapCardContent = !showMapCardContent">
          <p class="card-header-title">
            <template v-if="mapType === 'compartment'">
              <template v-if="dim === '3d'">
                {{ capitalize(mapType) }}: {{ mapsData.compartments[mapName].name }}
              </template>
              <template v-else>
                {{ capitalize(mapType) }}: {{ mapsData.compartmentsSVG[mapName].name }}
              </template>
            </template>
            <template v-else-if="mapType === 'subsystem'">
              <template v-if="dim === '3d'">
                {{ capitalize(mapType) }}: {{ mapsData.subsystemsStats[mapName].name }}
              </template>
              <template v-else>
                {{ capitalize(mapType) }}: {{ mapsData.subsystemsSVG[mapName].name }}
              </template>
            </template>
          </p>
          <a href="#" class="card-header-icon" aria-label="more options">
            <span class="icon">
              <i class="fa fa-caret-down" aria-hidden="true" v-if="!showMapCardContent"></i>
              <i class="fa fa-caret-up" aria-hidden="true" v-else="showMapCardContent"></i>
            </span>
          </a>
        </header>
        <div class="card-content" v-show="showMapCardContent">
          <div class="content">
            <template>
              <template v-if="mapType === 'compartment'">
                <template v-if="dim === '3d'">
                  <span class="has-text-weight-bold">Reactions:</span> {{ mapsData.compartments[mapName]['reaction_count'] }}<br>
                  <span class="has-text-weight-bold">Metabolites:</span> {{ mapsData.compartments[mapName]['metabolite_count'] }}<br>
                  <span class="has-text-weight-bold">Enzymes:</span> {{ mapsData.compartments[mapName]['enzyme_count'] }}<br>
                  <span class="has-text-weight-bold">Subsystems:</span> {{ mapsData.compartments[mapName]['subsystem_count'] }}<br>
                </template>
                <template v-else>
                  <!-- show the stats of the model not the maps -->
                  <span class="has-text-weight-bold">Reactions:</span> {{ mapsData.compartments[mapsData.compartmentsSVG[mapName].compartment]['reaction_count'] }}<br>
                  <span class="has-text-weight-bold">Metabolites:</span> {{ mapsData.compartments[mapsData.compartmentsSVG[mapName].compartment]['metabolite_count'] }}<br>
                  <span class="has-text-weight-bold">Enzymes:</span> {{ mapsData.compartments[mapsData.compartmentsSVG[mapName].compartment]['enzyme_count'] }}<br>
                  <span class="has-text-weight-bold">Subsystems:</span> {{ mapsData.compartments[mapsData.compartmentsSVG[mapName].compartment]['subsystem_count'] }}<br>
                </template>
              </template>
              <template v-else-if="mapType === 'subsystem'">
                <template v-if="dim === '3d'">
                  <span class="has-text-weight-bold">Reactions:</span> {{ mapsData.subsystemsStats[mapName]['reaction_count'] }}<br>
                  <span class="has-text-weight-bold">Metabolites:</span> {{ mapsData.subsystemsStats[mapName]['metabolite_count'] }}<br>
                  <span class="has-text-weight-bold">Enzymes:</span> {{ mapsData.subsystemsStats[mapName]['enzyme_count'] }}<br>
                  <span class="has-text-weight-bold">Compartments:</span> {{ mapsData.subsystemsStats[mapName]['compartment_count'] }}<br>
                </template>
                <template v-else>
                  <!-- show the stats of the model not the maps -->
                  <span class="has-text-weight-bold">Reactions:</span> {{ mapsData.subsystemsStats[mapsData.subsystemsSVG[mapName].subsystem]['reaction_count'] }}<br>
                  <span class="has-text-weight-bold">Metabolites:</span> {{ mapsData.subsystemsStats[mapsData.subsystemsSVG[mapName].subsystem]['metabolite_count'] }}<br>
                  <span class="has-text-weight-bold">Enzymes:</span> {{ mapsData.subsystemsStats[mapsData.subsystemsSVG[mapName].subsystem]['enzyme_count'] }}<br>
                  <span class="has-text-weight-bold">Compartments:</span> {{ mapsData.subsystemsStats[mapsData.subsystemsSVG[mapName].subsystem]['compartment_count'] }}<br>
                </template>
              </template>
            </template>
          </div>
        </div>
        <footer class="card-footer">
          <a class="card-footer-item has has-text-centered" @click="viewOnGemBrowser()">View more on the Browser</a>
        </footer>
      </div>
    </div>
    <template v-if="loading">
      <div class="loading">
        <a class="button is-loading"></a>
      </div>
    </template>
    <template v-else>
      <div class="column" v-if="selectionData.data">
        <div class="card">
          <header class="card-header" v-if="!selectionData.error" @click.prevent="showSelectionCardContent = !showSelectionCardContent">
            <p class="card-header-title">
              {{ capitalize(selectionData.type) }}: {{ selectionData.data.id }}
            </p>
            <a href="#" class="card-header-icon" aria-label="more options">
              <span class="icon">
                <i class="fa fa-caret-down" aria-hidden="true" v-if="!showSelectionCardContent"></i>
                <i class="fa fa-caret-up" aria-hidden="true" v-else="showSelectionCardContent"></i>
              </span>
            </a>
          </header>
          <div class="card-content" v-show="showSelectionCardContent">
            <div class="content">
              <template v-if="!selectionData.error">
                <template v-if="['metabolite', 'enzyme', 'reaction'].includes(selectionData.type)">
                  <p v-if="selectionData.data['rnaLvl'] != null">
                    <span class="has-text-weight-bold">RNA&nbsp;level:</span><span>{{ selectionData.data['rnaLvl'] }}</span>
                  </p>
                  <template v-for="item in selectedElementDataKeys[model.database_name][selectionData.type]"
                    v-if="selectionData.data[item.name] != null || item.name === 'external_ids'" >
                    <template v-if="item.name === 'external_ids'">
                      <span class="has-text-weight-bold" v-html="capitalize(item.display || item.name) + ':'"
                      v-if="hasExternalIDs(item.value)"></span>
                      <p v-if="hasExternalIDs(item.value)">
                        <template v-for="eid in item.value" v-if="selectionData.data[eid[1]] && selectionData.data[eid[2]]">
                          <span class="has-text-weight-bold">{{ capitalize(eid[0]) }}:</span>
                          <span v-html="reformatStringToLink(selectionData.data[eid[1]], selectionData.data[eid[2]])"></span><br>
                        </template>
                      </p v-if="hasExternalIDs(item.value)">
                    </template>
                    <template v-else-if="['aliases', 'subsystem'].includes(item.name)">
                      <span class="has-text-weight-bold">{{ capitalize(item.display || item.name) }}:</span><p>
                      <template v-for="s in selectionData.data[item.name].split('; ')">
                        &ndash;&nbsp;{{ s }}<br>
                      </template></p>
                    </template>
                    <template v-else-if="['reactants', 'products'].includes(item.name)">
                      <span class="has-text-weight-bold">{{ capitalize(item.display || item.name) }}:</span><p>
                      <template v-for="s in selectionData.data[item.name]">
                        &ndash;&nbsp;{{ s.name }}<br>
                      </template></p>
                    </template>
                    <template v-else-if="item.name === 'equation'">
                      <p><span class="has-text-weight-bold" v-html="capitalize(item.display || item.name) + ':'"></span><br>
                      <span v-html="chemicalReaction(selectionData.data[item.name], selectionData.data['is_reversible'])"></span></p>
                    </template>
                    <template v-else>
                      <p><span class="has-text-weight-bold" v-html="capitalize(item.display || item.name) + ':'"></span>
                      {{ selectionData.data[item.name] }}</p>
                    </template>
                  </template>
                  <template v-if="selectionHasNoData()">
                    {{ messages.noInfoAvailable }}
                  </template>
                </template>
                <template v-else>
                  <template v-if="dim === '3d'">
                    <span class="has-text-weight-bold">Reactions:</span> {{ mapsData.subsystemsStats[idfy(selectionData.data.id)]['reaction_count'] }}<br>
                    <span class="has-text-weight-bold">Metabolites:</span> {{ mapsData.subsystemsStats[idfy(selectionData.data.id)]['metabolite_count'] }}<br>
                    <span class="has-text-weight-bold">Enzymes:</span> {{ mapsData.subsystemsStats[idfy(selectionData.data.id)]['enzyme_count'] }}<br>
                    <span class="has-text-weight-bold">Compartments:</span> {{ mapsData.subsystemsStats[idfy(selectionData.data.id)]['compartment_count'] }}<br>
                  </template>
                  <template v-else>
                    <!-- show the stats of the model not the maps -->
                    <span class="has-text-weight-bold">Total model stats:</span><br>
                    <span class="has-text-weight-bold">Reactions:</span> {{ mapsData.subsystemsStats[mapsData.subsystemsSVG[idfy(selectionData.data.id)].subsystem]['reaction_count'] }}<br>
                    <span class="has-text-weight-bold">Metabolites:</span> {{ mapsData.subsystemsStats[mapsData.subsystemsSVG[idfy(selectionData.data.id)].subsystem]['metabolite_count'] }}<br>
                    <span class="has-text-weight-bold">Enzymes:</span> {{ mapsData.subsystemsStats[mapsData.subsystemsSVG[idfy(selectionData.data.id)].subsystem]['enzyme_count'] }}<br>
                    <span class="has-text-weight-bold">Compartments:</span> {{ mapsData.subsystemsStats[mapsData.subsystemsSVG[idfy(selectionData.data.id)].subsystem]['compartment_count'] }}<br>
                  </template>
                </template>
              </template>
              <template v-else-if="selectionData.error">
                <div class="has-text-danger">
                  {{ messages.unknownError }}
                </div>
              </template>
            </div>
          </div>
          <footer class="card-footer" v-if="!selectionData.error">
            <a class="card-footer-item has has-text-centered" @click="viewOnGemBrowser()">View more on the Browser</a>
          </footer>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { capitalize, reformatStringToLink, idfy } from '../../../helpers/utils';
import { chemicalReaction } from '../../../helpers/chemical-formatters';
import { getExpLvlLegend } from '../../../expression-sources/hpa';
import { default as EventBus } from '../../../event-bus';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'sidebar-data-panels',
  props: ['model', 'dim', 'tissue', 'mapType', 'mapName', 'mapsData', 'selectionData', 'loading'],
  data() {
    return {
      errorMessage: '',
      selectedElementDataKeys: {
        hmr2: {
          metabolite: [
            { name: 'name' },
            { name: 'model_name', display: 'Model&nbsp;name' },
            { name: 'formula' },
            { name: 'compartment' },
            { name: 'aliases', display: 'Synonyms' },
            {
              name: 'external_ids',
              display: 'External&nbsp;IDs',
              value: [
                ['HMDB', 'hmdb_id', 'hmdb_link'],
                ['chebi', 'chebi_id', 'chebi_link'],
                ['mnxref', 'mnxref_id', 'mnxref_link'],
              ],
            },
          ],
          enzyme: [
            { name: 'gene_name', display: 'Gene&nbsp;name' },
            { name: 'gene_synonyms', display: 'Synonyms' },
            {
              name: 'external_ids',
              display: 'External&nbsp;IDs',
              value: [
                ['Uniprot', 'uniprot_id', 'uniprot_link'],
                ['NCBI', 'ncbi_id', 'ncbi_link'],
                ['Ensembl', 'id', 'name_link'],
              ],
            },
          ],
          reaction: [
            { name: 'equation' },
            // { name: 'gene_rule', display: 'GPR' },
            { name: 'subsystem', display: 'Subsystems' },
            { name: 'reactants' },
            { name: 'products' },
          ],
        },
        yeast: {
          metabolite: [],
          enzyme: [],
          reaction: [],
        },
      },
      showLvlCardContent: true,
      showMapCardContent: true,
      showSelectionCardContent: true,
      messages,
    };
  },
  created() {
  },
  methods: {
    viewOnGemBrowser() {
      if (this.selectionData.data && this.selectionData.data.id) {
        EventBus.$emit('navigateTo', 'GEMBrowser', this.model.database_name, this.selectionData.type, this.selectionData.data.id);
      } else if (this.mapType) {
        let nameID = null;
        if (this.mapType === 'compartment') {
          nameID = this.mapsData.compartmentsSVG[this.mapName].compartment;
        } else {
          nameID = this.mapsData.subsystemsSVG[this.mapName].subsystem;
        }
        EventBus.$emit('navigateTo', 'GEMBrowser', this.model.database_name, this.mapType, nameID);
      }
    },
    hasExternalIDs(keys) {
      for (const eid of keys) {
        if (this.selectionData.data[eid[1]] && this.selectionData.data[eid[2]]) {
          return true;
        }
      }
      return false;
    },
    selectionHasNoData() {
      if (!(this.selectionData.type in
          this.selectedElementDataKeys[this.model.database_name])) {
        return true;
      }
      for (const k of this.selectedElementDataKeys[this.model.database_name][this.selectionData.type]) {  // eslint-disable-line max-len
        if (k.name in this.selectionData.data &&
          this.selectionData.data[k.name]) {
          return false;
        }
      }
      return true;
    },
    getExpLvlLegend,
    capitalize,
    reformatStringToLink,
    chemicalReaction,
    idfy,
  },
};
</script>

<style lang="scss" scoped>
  .card-header {
    cursor: pointer
  }
</style>
