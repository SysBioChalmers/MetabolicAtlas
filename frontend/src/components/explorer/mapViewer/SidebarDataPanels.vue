<template>
  <div id="sidebar_mapviewer">
    <div v-if="currentMap" class="card my-3">
      <header class="card-header" @click.prevent="showMapCardContent = !showMapCardContent">
        <p class="card-header-title is-capitalized is-inline">
          {{ currentMap.type }}:
          <i>{{ currentMap.name }}</i>
        </p>
      </header>
      <div v-if="dim==='2d' && currentMap.reactionList && missingReactionList.length > 0"
           class="card-content p-4">
        <div v-if="currentMap.mapReactionIdSet.length == 1" class="content mb-0">
          Please note that {{ missingReactionList.length }}
          of the reactions in the {{ currentMap.type }} are not shown on the map.
          <a @click="$emit('update:showModal', true)"> See comparison </a>
        </div>
        <div v-else class="content mb-0">
          Please note that {{ missingReactionList.length }} of the reactions in the
          {{ currentMap.type }} are not shown on any of the {{ currentMap.name }} maps.
          <a @click="$emit('update:showModal', true)"> See comparison </a>
        </div>
      </div>
      <footer v-if="currentMap.type !== 'custom'" class="card-footer sidebarCardHover">
        <router-link class="p-0 is-info is-outlined card-footer-item has-text-centered"
                     :to="{ name: currentMap.type, params: { model: model.short_name, id: currentMap.id } }">  <!-- eslint-disable-line max-len -->
          <span class="icon is-large"><i class="fa fa-table fa-lg"></i></span>
          <span>{{ messages.gemBrowserName }}</span>
        </router-link>
      </footer>
    </div>
    <template v-if="loading">
      <div class="card loading">
        <a class="button is-large is-loading"></a>
      </div>
    </template>
    <template v-else-if="!selectionData.error">
      <div v-if="selectionData.data && currentMap.type !== 'subsystem' && selectionData.type === 'subsystem'"
           class="card my-3">
        <header class="card-header">
          <p class="card-header-title is-capitalized is-inline is-unselectable">
            {{ selectionData.type }}: <i>{{ selectionData.data.id }}</i>
          </p>
        </header>
        <footer class="card-footer">
          <router-link class="p-0 is-info is-outlined card-footer-item has-text-centered"
                       :to="{ name: selectionData.type, params: { model: model.short_name, id: idfy(selectionData.data.id) } }">  <!-- eslint-disable-line max-len -->
            <span class="icon is-large"><i class="fa fa-table fa-lg"></i></span>
            <span>{{ messages.gemBrowserName }}</span>
          </router-link>
          <router-link
            class="p-0 is-primary is-outlined card-footer-item has-text-centered"
            :to="{ name: 'viewer', params: { model: model.short_name, type: selectionData.type, map_id: idfy(selectionData.data.id) }, query: { dim: dim } }">  <!-- eslint-disable-line max-len -->
            <span class="icon is-large"><i class="fa fa-map-o fa-lg"></i></span>
            <span>Load map</span>
          </router-link>
        </footer>
      </div>
      <div v-else-if="selectionData.data && ['metabolite', 'gene', 'reaction'].includes(selectionData.type)"
           class="card my-3">
        <header class="card-header is-clickable"
                @click.prevent="toggleSelectionCardContent">
          <p class="card-header-title is-inline is-capitalized is-unselectable">
            {{ selectionData.type }}: <i>{{ selectionData.data.name || selectionData.data.id }}</i>
          </p>
          <a href="#" class="card-header-icon" aria-label="more options">
            <span class="icon">
              <i aria-hidden="true" :class="[showSelectionCardContent ? 'fa-caret-down' : 'fa-caret-right', 'fa']"></i>
            </span>
          </a>
        </header>
        <div v-show="showSelectionCardContent" class="card-content px-4">
          <div class="content">
            <template v-for="item in selectedElementDataKeys[selectionData.type]
              .filter(i => selectionData.data[i.name])">
              <template v-if="item.name === 'synonyms'">
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <span class="has-text-weight-bold">{{ capitalize(item.display || item.name) }}:</span><p>
                  <template v-for="s in selectionData.data[item.name].split('; ')">
                    <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                    &ndash;&nbsp;{{ s }}<br :key="s">
                  </template></p>
              </template>
              <template v-else-if="item.name === 'subsystems'">
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <span class="has-text-weight-bold">{{ capitalize(item.display || item.name) }}:</span><p>
                  <template v-for="s in selectionData.data[item.name]">
                    &ndash;&nbsp;{{ s.name }}<br :key="s.id">
                  </template></p>
              </template>
              <template v-else-if="item.name === 'compartment'">
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <span class="has-text-weight-bold">{{ capitalize(item.display || item.name) }}:</span>
                {{ selectionData.data[item.name].name }}
              </template>
              <template v-else-if="item.name === 'equation'">
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <p><span class="has-text-weight-bold" v-html="capitalize(item.display || item.name) + ':'"></span><br>
                  <span v-html="reformatChemicalReactionHTML(selectionData.data, false, model.short_name)"></span>
                </p>
              </template>
              <template v-else-if="item.name === 'formula'">
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <p><span class="has-text-weight-bold" v-html="capitalize(item.display || item.name) + ': '"></span>
                  <span v-html="chemicalFormula(selectionData.data[item.name], selectionData.data.charge)"></span></p>
              </template>
              <template v-else-if="selectionData.data[item.name]">
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                <p><span class="has-text-weight-bold" v-html="capitalize(item.display || item.name) + ':'"></span>
                  {{ selectionData.data[item.name] }}</p>
              </template>
            </template>
            <template v-if="selectionHasNoData()">
              {{ messages.noInfoAvailable }}
            </template>
          </div>
        </div>
        <footer class="card-footer">
          <router-link class="p-0 is-info is-outlined card-footer-item has-text-centered"
                       :to="{ name: selectionData.type,
                              params: { model: model.short_name, id: selectionData.data.id } }">
            <span class="icon is-large"><i class="fa fa-table fa-lg"></i></span>
            <span>{{ messages.gemBrowserName }}</span>
          </router-link>
        </footer>
      </div>
    </template>
    <template v-else>
      <div class="card my-3">
        <header class="card-header is-clickable">
          <p class="card-header-title is-inline is-unselectable has-text-weight-normal">
            This {{ selectionData.type }} does not exist in {{ model.short_name }}.
            Email us at contact@metabolicatlas.org
          </p>
        </header>
      </div>
    </template>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { capitalize, reformatStringToLink, reformatChemicalReactionHTML } from '@/helpers/utils';
import { chemicalFormula } from '@/helpers/chemical-formatters';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'SidebarDataPanels',
  props: {
    dim: String,
    currentMap: Object,
    mapsData: Object,
    selectionData: Object,
    showModal: Boolean,
    missingReactionList: Array,
  },
  data() {
    return {
      errorMessage: '',
      selectedElementDataKeys: {
        metabolite: [
          { name: 'id' },
          { name: 'formula' },
          { name: 'compartment' },
        ],
        gene: [
          { name: 'id' },
          { name: 'alternateName', display: 'Alt&nbsp;name' },
          { name: 'synonyms', display: 'Synonym(s)' },
        ],
        reaction: [
          { name: 'equation' },
          { name: 'subsystems', display: 'Subsystem(s)' },
        ],
      },
      showMapCardContent: true,
      showSelectionCardContent: true,
      messages,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      loading: state => state.maps.loadingElement,
    }),
  },
  watch: {
    selectionData() {
      this.openSelectionCardContent();
    },
  },
  methods: {
    selectionHasNoData() {
      if (!(this.selectionData.type
          in this.selectedElementDataKeys)) {
        return true;
      }
      for (let i = 0;
        i < this.selectedElementDataKeys[this.selectionData.type].length;
        i += 1) {
        const k = this.selectedElementDataKeys[this.selectionData.type][i];
        if (k.name in this.selectionData.data
          && this.selectionData.data[k.name]) {
          return false;
        }
      }
      return true;
    },
    capitalize,
    reformatStringToLink,
    chemicalFormula,
    reformatChemicalReactionHTML,
    toggleSelectionCardContent() {
      if (this.showSelectionCardContent) {
        this.hideSelectionCardContent();
      } else {
        this.openSelectionCardContent();
      }
    },
    openSelectionCardContent() {
      this.showSelectionCardContent = true;
      this.$emit('openSelectionCardContent');
    },
    hideSelectionCardContent() {
      this.showSelectionCardContent = false;
    },
  },
};
</script>

<style lang="scss" scoped>
  #sidebar_mapviewer {
    .content p:not(:last-child) {
      margin-bottom: 0.3em;
    }

    .loading .button {
      width: 100%;
    }
  }
</style>
