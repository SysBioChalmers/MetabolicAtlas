<template>
  <div id="sidebar_mapviewer">
    <div v-if="currentMap" class="card my-3">
      <header class="card-header" @click.prevent="showMapCardContent = !showMapCardContent">
        <p class="card-header-title is-capitalized is-inline">
          {{ currentMap.type }}:
          <i>{{ currentMap.name }}</i>
        </p>
      </header>
      <div v-if="currentMap.reactionList && missingReactionList.length > 0"
      class="card-content p-4 sidebarCardHover">
        <div class="content mb-0" @click="showModal = true">
          Please note that {{ missingReactionList.length }}
          of the reactions in the model are not shown on the map
          <span class="icon"><i class="fa fa-info-circle"></i></span>
      </div>
      <div>
        <div v-if="showModal" class="modal is-active">
          <div class="modal-background"></div>
          <div class="modal-content p-5 column is-6-fullhd is-8-desktop is-10-tablet is-full-mobile
            has-background-white">
            <h4 class="title is-size-4 m-0 mb-2"> List of missing and total reactions on the map </h4>
            <p class="pb-4"> There are {{ missingReactionList.length }}
                reactions not shown on the map as compared to the model since
                the map is manually curated and some reactions are not possible
                to add to the map. The number of reaction shown on the map is
                {{ mapReactionList.length }}.
            </p>
            <table class="table main-table is-fullwidth m-0">
              <tbody>
                <tr>
                  <td class="td-key has-background-primary has-text-white-bis" >Missing reactions on the map</td>
                  <td>
                    <div v-html="missingReactionIdListHtml"></div>
                    <div v-if="!showFullReactionListMissing &&  missingReactionList.length > displayedReaction">
                      <br>
                      <button class="is-small button" @click="showFullReactionListMissing=true">
                        ... and {{ missingReactionList.length - displayedReaction }} more
                      </button>
                      <span v-show="missingReactionList.length >= limitReaction"
                            class="tag is-medium is-warning is-pulled-right">
                        The number of reactions displayed is limited to {{ limitReaction }}
                      </span>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td class="td-key has-background-primary has-text-white-bis">Reactions shown on the map</td>
                  <td>
                    <div v-html="mapReactionIdListHtml"></div>
                    <div v-if="!showFullReactionListMap &&  mapReactionList.length > displayedReaction">
                      <br>
                      <button class="is-small button" @click="showFullReactionListMap=true">
                        ... and {{ mapReactionList.length - displayedReaction }} more
                      </button>
                      <span v-show="mapReactionList.length >= limitReaction"
                            class="tag is-medium is-warning is-pulled-right">
                        The number of reactions displayed is limited to {{ limitReaction }}
                      </span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <button class="modal-close" @click="closeModal"></button>
        </div>
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
                @click.prevent="showSelectionCardContent = !showSelectionCardContent">
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
import { capitalize, reformatStringToLink, reformatChemicalReactionHTML, buildCustomLink } from '@/helpers/utils';
import { chemicalFormula } from '@/helpers/chemical-formatters';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'SidebarDataPanels',
  props: {
    dim: String,
    currentMap: Object,
    mapsData: Object,
    selectionData: Object,
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
      showModal: false,
      showFullReactionListMissing: false,
      showFullReactionListTotal: false,
      displayedReaction: 40,
      limitReaction: 999999999,
      missingNumberOfReactions: null,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      loading: state => state.maps.loadingElement,
      mapReactionList: state => state.maps.svgReactionsIdList,
    }),
    modelNumberOfReactions() {
      return this.currentMap.reactionList ? this.currentMap.reactionList.length : null;
    },
    mapReactionIdListHtml() {
      const l = ['<span class="tags">'];
      for (let i = 0; i < this.mapReactionList.length; i += 1) {
        const r = this.mapReactionList[i];
        if ((!this.showFullReactionListMap && i === this.displayedReaction)
          || i === this.limitReaction) {
          break;
        }
        const customLink = buildCustomLink({ model: this.model.short_name, type: 'reaction', id: r, title: r, cssClass: 'target="_blank"' });
        l.push(
          `<span id="${r}" class="tag">${customLink}</span>`
        );
      }
      l.push('</span>');
      return l.join('');
    },
    missingReactionList() {
      const modelReactionIdSet = new Set(this.currentMap.reactionList);
      const mapReactionIdSet = new Set(this.mapReactionList);
      const missingReactionIdSet = new Set([...modelReactionIdSet].filter(x => !mapReactionIdSet.has(x)));
      const missingReactionList = Array.from(missingReactionIdSet);
      return missingReactionList;
    },
    missingReactionIdListHtml() {
      const l = ['<span class="tags">'];
      for (let i = 0; i < this.missingReactionList.length; i += 1) {
        const r = this.missingReactionList[i];
        if ((!this.showFullReactionListMissing && i === this.displayedReaction)
          || i === this.limitReaction) {
          break;
        }
        const customLink = buildCustomLink({ model: this.model.short_name, type: 'reaction', id: r, title: r, cssClass: 'target="_blank"' });
        l.push(
          `<span id="${r}" class="tag">${customLink}</span>`
        );
      }
      l.push('</span>');
      return l.join('');
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
    closeModal() {
      this.showModal = false;
      this.showFullReactionListMissing = false;
      this.showFullReactionListMap = false;
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

  .sidebarCardHover:hover {
    background: rgba(51,68,109,.03);
    cursor: pointer;
  }
</style>
