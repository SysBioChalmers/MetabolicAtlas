<template>
  <div id="dataOverlayBox"
       class="column is-one-fifth-widescreen is-one-quarter-desktop
         is-one-quarter-tablet has-background-lightgray">
    <div class="title is-size-4 has-text-centered">Gene expression data</div>
    <div class="has-text-centered"
         title="Load a TSV file with gene IDs and TPM values.
         More information can be found in the documentation.">
      Load custom gene expression
      <span style="white-space: nowrap;">
        data
        <router-link :to="{ name: 'documentation', hash: '#Data-overlay'}">
          <span class="icon"><i class="fa fa-info-circle"></i></span>
        </router-link>
      </span>
    </div>
    <div class="file is-centered mb-2">
      <label class="file-label">
        <input class="file-input"
               type="file"
               name="resume"
               @change="getFileName">
        <span class="file-cta">
          <span class="file-icon">
            <i class="fa fa-upload"></i>
          </span>
          <span class="file-label">
            Choose a file
          </span>
        </span>
      </label>
    </div>
    <div v-if="customFileName" id="fileNameBox" class="mb-4">
      <div v-show="!showFileLoader" class="tags has-addons is-centered"
           :title="errorCustomFile ? errorCustomFileMsg : customFileInfo">
        <span class="tag" :class="errorCustomFile ? 'is-danger' : 'is-success'">
          <div class="is-size-6">{{ customFileName }}</div>
        </span>
        <a class="tag is-delete" title="Unload file" @click="unloadUploadedFile()"></a>
      </div>
      <div v-show="showFileLoader" class="has-text-centered">
        <a class="button is-small is-loading"></a>
      </div>
    </div>
    <div class="card my-3">
      <div class="card-content py-2 p-3">
        <div class="has-text-centered title is-size-6">Data 1</div>
        <div v-if="dataSourcesAvailable" class="control">
          <p>RNA levels from <a href="https://www.proteinatlas.org" target="_blank">proteinAtlas.org</a></p>
          <div class="select is-fullwidth">
            <select :disabled="disabledRNAlvl" @change="(e) => setFirstTissue('HPA', e.target.value)">
              <option>None</option>
              <option v-for="tissue in HPATissues" :key="tissue"
                      :selected="tissue === tissue1"
                      class="is-clickable is-capitalized">{{ tissue }}</option>
            </select>
          </div>
        </div>
        <p>{{ dataSourcesAvailable ? 'Or uploaded data' : 'RNA levels from uploaded data' }}</p>
        <div class="control">
          <div class="select is-fullwidth">
            <select
              v-model="customTissue1"
              :disabled="disabledCustomSelectData"
              @change="(e) => setFirstTissue('custom', e.target.value)">
              <option v-if="!disabledCustomSelectData">None</option>
              <option v-for="tissue in customTissues" :key="tissue"
                      class="is-clickable is-capitalized">{{ tissue }}</option>
            </select>
          </div>
        </div>
      </div>
    </div>
    <div class="card my-3">
      <div class="card-content py-2 p-3">
        <div class="has-text-centered title is-size-6">Data 2 (for comparison)</div>
        <div v-if="dataSourcesAvailable" class="control">
          <p>RNA levels from <a href="https://www.proteinatlas.org" target="_blank">proteinAtlas.org</a></p>
          <div class="select is-fullwidth">
            <select :disabled="disabledRNAlvl" @change="(e) => setSecondTissue('HPA', e.target.value)">
              <option>None</option>
              <option v-for="tissue in HPATissues" :key="tissue"
                      :selected="tissue === tissue2"
                      class="is-clickable is-capitalized">{{ tissue }}</option>
            </select>
          </div>
        </div>
        <div>{{ dataSourcesAvailable ? 'Or uploaded data' : 'RNA levels from uploaded data' }}</div>
        <div class="control">
          <div class="select is-fullwidth">
            <select
              v-model="customTissue2"
              :disabled="disabledCustomSelectData"
              @change="(e) => setSecondTissue('custom', e.target.value)">
              <option v-if="!disabledCustomSelectData">None</option>
              <option v-for="tissue in customTissues"
                      :key="tissue"
                      class="is-clickable is-capitalized">{{ tissue }}</option>
            </select>
          </div>
        </div>
      </div>
    </div>
    <RNAexpression class="my-3"
                   :map-type="mapType"
                   :map-name="mapName"
                   @loadedCustomLevels="setCustomTissues($event)"
                   @errorCustomFile="handleErrorCustomFile($event)" />
  </div>
</template>

<script>

import { mapGetters, mapState } from 'vuex';
import $ from 'jquery';
import RNAexpression from '@/components/explorer/mapViewer/RNAexpression.vue';
import { default as EventBus } from '@/event-bus';

const NOFILELOADED = 'No file loaded';

export default {
  name: 'DataOverlay',
  components: {
    RNAexpression,
  },
  props: {
    mapType: String,
    mapName: String,
    dim: String,
  },
  data() {
    return {
      errorMessage: '',

      showLvlCardContent: true,
      customTissues: [NOFILELOADED],

      customTissue1: NOFILELOADED,
      customTissue2: NOFILELOADED,

      tissue1Source: '',
      tissue2Source: '',

      customFileName: '',
      showFileLoader: true,
      errorCustomFile: false,
      errorCustomFileMsg: '',
      customFileInfo: '',
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      showing2D: state => state.maps.showing2D,
      dataOverlayPanelVisible: state => state.maps.dataOverlayPanelVisible,
      tissue1: state => state.maps.tissue1,
      tissue2: state => state.maps.tissue2,
      mapLoaded: state => !state.maps.loading,
    }),
    ...mapGetters({
      HPATissues: 'humanProteinAtlas/HPATissues',
    }),
    disabledRNAlvl() {
      return !this.mapName || this.HPATissues.length === 0;
    },
    disabledCustomSelectData() {
      return this.customTissues.length === 1 && this.customTissues[0] === NOFILELOADED;
    },
    isSelectedHPAtissue1() {
      return this.HPATissues.length !== 0 && this.tissue1 !== 'None';
    },
    isSelectedHPAtissue2() {
      return this.HPATissues.length !== 0 && this.tissue2 !== 'None';
    },
    isSelectedCustomtissue1() {
      return !this.disabledCustomSelectData && !(NOFILELOADED, 'None').includes(this.customTissue1);
    },
    isSelectedCustomtissue2() {
      return !this.disabledCustomSelectData && !(NOFILELOADED, 'None').includes(this.customTissue2);
    },
    isSelectedTissue1() {
      return this.isSelectedHPAtissue1 || this.isSelectedCustomtissue1;
    },
    isSelectedTissue2() {
      return this.isSelectedHPAtissue2 || this.isSelectedCustomtissue2;
    },
    selectedTissue1() {
      if (this.isSelectedTissue1) {
        return this.isSelectedHPAtissue1 ? this.tissue1 : this.customTissue1;
      }
      return '';
    },
    selectedTissue2() {
      if (this.isSelectedTissue2) {
        return this.isSelectedHPAtissue2 ? this.tissue2 : this.customTissue2;
      }
      return '';
    },
    dataSourcesAvailable() {
      return this.model.short_name === 'Human-GEM';
    },
  },
  watch: {
    mapLoaded: 'reloadGeneExpressionData',
    HPATissues: 'reloadGeneExpressionData',
  },
  created() {
    EventBus.$on('loadedCustomExpressionData', (info) => {
      this.customTissue1 = 'None';
      this.customTissue2 = 'None';
      this.customFileInfo = info;
    });

    EventBus.$off('loadingCustomFile');
    EventBus.$on('loadingCustomFile', () => {
      this.showFileLoader = true;
    });
  },
  methods: {
    reloadGeneExpressionData() {
      if (this.mapLoaded && this.HPATissues.length > 0) {
        // check if tissues are provided in the URL
        if (!this.$route.query) {
          return;
        }

        const { g1, g2 } = this.$route.query;

        if (g1 !== 'None' && !this.HPATissues.includes(g1)) {
          this.$store.dispatch('maps/setTissue1', 'None');
        } else {
          this.setFirstTissue('HPA', g1);
        }

        if (g2 !== 'None' && !this.HPATissues.includes(g2)) {
          this.$store.dispatch('maps/setTissue2', 'None');
        } else {
          this.setSecondTissue('HPA', g2);
        }

        if (this.isSelectedTissue1 || this.isSelectedTissue2) {
          EventBus.$emit('selectTissues', this.selectedTissue1, this.tissue1Source, this.selectedTissue2, this.tissue2Source, this.dim);
        }
      }
    },
    getFileName(e) {
      if (e.target.files.length !== 0) {
        this.customFileName = e.target.files[0].name;
        this.errorCustomFile = false;
        this.errorCustomFileMsg = '';
        this.customFileInfo = '';
        EventBus.$emit('loadCustomGeneExpData', e.target.files[0]);
        $('.file-input')[0].value = '';
      } else {
        this.customFileName = '';
      }
    },
    setCustomTissues(info) {
      this.customTissues = info.tissues;
      this.customTissue1 = 'None';
      this.customTissue2 = 'None';
      this.customFileInfo = `Entries found: ${info.entries} - Series loaded: ${info.series}`;
      this.showFileLoader = false;
    },
    setFirstTissue(source, tissue) {
      if (source === 'HPA' && this.isSelectedCustomtissue1) {
        this.clearCustomTissue1Selection();
      } else if (source === 'custom' && this.isSelectedHPAtissue1) {
        this.$store.dispatch('maps/setTissue1', 'None');
      }
      this.$store.dispatch('maps/setTissue1', tissue);
      this.loadRNAlevelsTissue1(this.selectedTissue1, source);
      this.tissue1Source = source;
    },
    setSecondTissue(source, tissue) {
      if (source === 'HPA' && this.isSelectedCustomtissue2) {
        this.clearCustomTissue2Selection();
      } else if (source === 'custom' && this.isSelectedHPAtissue2) {
        this.$store.dispatch('maps/setTissue2', 'None');
      }
      this.$store.dispatch('maps/setTissue2', tissue);
      this.loadRNAlevelsTissue2(this.selectedTissue2, source);
      this.tissue2Source = source;
    },
    clearCustomTissue1Selection() {
      if (this.disabledCustomSelectData) {
        this.customTissue1 = NOFILELOADED;
      } else {
        this.customTissue1 = 'None';
      }
    },
    clearCustomTissue2Selection() {
      if (this.disabledCustomSelectData) {
        this.customTissue2 = NOFILELOADED;
      } else {
        this.customTissue2 = 'None';
      }
    },
    loadRNAlevelsTissue1(tissue, source) {
      if (!tissue) {
        EventBus.$emit('unselectFirstTissue');
        this.$store.dispatch('maps/setTissue1', 'None');
      } else {
        EventBus.$emit('selectFirstTissue', tissue, source, this.dim);
      }
    },
    loadRNAlevelsTissue2(tissue, source) {
      if (!tissue) {
        EventBus.$emit('unselectSecondTissue');
        this.$store.dispatch('maps/setTissue2', 'None');
      } else {
        EventBus.$emit('selectSecondTissue', tissue, source, this.dim);
      }
    },
    unloadUploadedFile() {
      this.customFileName = '';
      this.customTissues = [NOFILELOADED];
      this.customTissue1 = NOFILELOADED;
      this.customTissue2 = NOFILELOADED;
      if (this.isSelectedTissue1 || this.isSelectedTissue2) {
        EventBus.$emit('selectTissues', this.selectedTissue1, this.tissue1Source, this.selectedTissue2, this.tissue2Source, this.dim);
      }
    },
    handleErrorCustomFile(errorMsg) {
      this.errorCustomFile = true;
      this.errorCustomFileMsg = errorMsg;
      this.showFileLoader = false;
    },
  },
};
</script>

<style lang="scss">
@media screen and (min-width: $tablet) {
  #dataOverlayBox {
    margin-right: -1rem;
  }
}

#fileNameBox {
  span.tag {
    width: 90%;
    cursor: help;
      > div {
      white-space: nowrap;
      overflow: hidden;
      max-width: 250px;
      text-overflow: ellipsis;
      cursor: help;
    }
  }
}
</style>
