<template>
  <div class="svgbox p-0 m-0">
    <div v-if="errorMessage" class="columns is-centered">
      <div class="column is-half has-text-centered">
        <p class="notification has-background-danger-light" style="margin-top: 30%;" v-html="errorMessage"></p>
      </div>
    </div>
    <MapLoader />
    <div id="svg-wrapper" v-html="svgContent">
    </div>
    <MapControls wrapper-elem-selector=".svgbox" :is-fullscreen="isFullscreen"
                 :zoom-in="zoomIn" :zoom-out="zoomOut"
                 :toggle-full-screen="toggleFullscreen" :toggle-genes="toggleGenes"
                 :toggle-subsystems="toggleSubsystems" :download-canvas="downloadCanvas" />
    <MapSearch ref="mapsearch" :matches="searchedNodesOnMap"
               :fullscreen="isFullscreen"
               @searchOnMap="searchIDsOnMap" @centerViewOn="centerElementOnSVG"
               @unHighlightAll="unHighlight" />
    <div id="tooltip" ref="tooltip"></div>
  </div>
</template>

<script>

import { mapGetters, mapState } from 'vuex';
import $ from 'jquery';
import Panzoom from '@panzoom/panzoom';
import { default as FileSaver } from 'file-saver';
import { debounce } from 'vue-debounce';
import MapControls from '@/components/explorer/mapViewer/MapControls';
import MapLoader from '@/components/explorer/mapViewer/MapLoader';
import MapSearch from '@/components/explorer/mapViewer/MapSearch';
import { default as EventBus } from '@/event-bus';
import { default as messages } from '@/helpers/messages';
import { reformatChemicalReactionHTML } from '@/helpers/utils';

export default {
  name: 'Svgmap',
  components: {
    MapControls,
    MapLoader,
    MapSearch,
  },
  props: {
    mapData: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      errorMessage: '',

      isFullscreen: false,
      panzoom: null,
      panzoomOptions: {
        maxScale: 1,
        minScale: 0.01,
        step: 0.1,
        canvas: true,
      },
      currentZoomScale: 1,
      lastWheelZoomTime: Date.now(),

      selectedNodesOnMap: [],
      selectedElemsHL: [],

      searchedNodesOnMap: [],
      searchedElemsHL: [],

      currentCoords: { x: null, y: null, zoom: null },

      selectedItemHistory: {},

      HPARNAlevels: {}, // enz id as key, [current tissue level, color] as value
      defaultGeneColor: '#feb',
      messages,

      initialLoadWithParams: true,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      svgContent: state => state.maps.svgMap,
      idsFound: state => state.maps.idsFound,
      selectedElement: state => state.maps.selectedElement,
      coords: state => state.maps.coords,
      selectedElementId: state => state.maps.selectedElementId,
      searchTerm: state => state.maps.searchTerm,
    }),
    ...mapGetters({
      selectIds: 'maps/selectIds',
    }),
  },
  watch: {
    async mapData() {
      await this.init();
    },
    svgContent: 'loadSvgPanzoom',
  },
  created() {
    EventBus.$off('apply2DHPARNAlevels');
    EventBus.$on('apply2DHPARNAlevels', (levels) => {
      this.applyHPARNAlevelsOnMap(levels);
    });
    this.updateURLCoord = debounce(this.updateURLCoord, 150);
  },
  async mounted() {
    const self = this;
    ['.met', '.enz', '.rea', '.subsystem'].forEach((aClass) => {
      $('#svg-wrapper').on('click', aClass, async function f() {
        await self.selectElement($(this));
      });
    });
    $('#svg-wrapper').on('mouseover', '.enz', function f(e) {
      const id = $(this).attr('class').split(' ')[1].trim();
      if (id in self.HPARNAlevels) {
        if (self.HPARNAlevels[id].length === 2) {
          self.$refs.tooltip.innerHTML = `RNA log<sub>2</sub>(TPM+1): ${self.HPARNAlevels[id][1]}`;
        } else {
          self.$refs.tooltip.innerHTML = `RNA log<sub>2</sub>(TPM<sub>T1</sub>+1): ${self.HPARNAlevels[id][2]}<br>`;
          self.$refs.tooltip.innerHTML += `RNA log<sub>2</sub>(TPM<sub>T2</sub>+1): ${self.HPARNAlevels[id][3]}<br>`;
          self.$refs.tooltip.innerHTML += `RNA log<sub>2</sub>(TPM ratio): ${self.HPARNAlevels[id][1]}<br>`;
        }
      } else if (Object.keys(self.HPARNAlevels).length !== 0) {
        self.$refs.tooltip.innerHTML = `RNA log<sub>2</sub>(TPM+1): ${self.HPARNAlevels['n/a'][1]}`;
      } else {
        return;
      }
      self.$refs.tooltip.style.top = `${(e.pageY - $('.svgbox').first().offset().top) + 15}px`;
      self.$refs.tooltip.style.left = `${(e.pageX - $('.svgbox').first().offset().left) + 15}px`;
      self.$refs.tooltip.style.display = 'block';
    });
    $('#svg-wrapper').on('mouseout', '.enz', () => {
      self.$refs.tooltip.innerHTML = '';
      self.$refs.tooltip.style.display = 'none';
    });
    $('.svgbox').on('webkitfullscreenchange mozfullscreenchange fullscreenchange mozFullScreen MSFullscreenChange', (e) => {
      $('.svgbox').first().toggleClass('fullscreen');
      self.isFullscreen = $('.svgbox').first().hasClass('fullscreen');
      e.stopPropagation();
    });
    await this.init();
  },
  methods: {
    async init() {
      this.$refs.mapsearch.reset();
      if (this.mapData.svgs.length === 0) {
        this.errorMessage = messages.mapNotFound;
        return;
      }
      this.$store.dispatch('maps/setLoading', true);
      const payload = { model: this.model.short_name, svgName: this.mapData.svgs[0].filename };
      await this.$store.dispatch('maps/getSvgMap', payload);
      this.bindKeyboardShortcuts();
    },
    bindKeyboardShortcuts() {
      document.addEventListener('keydown', (event) => {
        const key = event.key || event.keyCode;
        const panDistance = 10;
        switch (key) {
          case 'ArrowLeft':
          case 37:
            this.relativePan(-panDistance, 0);
            break;
          case 'ArrowUp':
          case 38:
            this.relativePan(0, -panDistance);
            break;
          case 'ArrowRight':
          case 39:
            this.relativePan(panDistance, 0);
            break;
          case 'ArrowDown':
          case 40:
            this.relativePan(0, panDistance);
            break;
          default:
            return;
        }
        event.preventDefault();
      });
    },
    relativePan(x, y) {
      this.panzoom.pan(x, y, { relative: true });
    },
    toggleGenes() {
      if ($('.enz, .ee').first().attr('visibility') === 'hidden') {
        $('.enz, .ee').attr('visibility', 'visible');
      } else {
        $('.enz, .ee').attr('visibility', 'hidden');
      }
    },
    toggleSubsystems() {
      if ($('.subsystem').first().attr('visibility') === 'hidden') {
        $('.subsystem').attr('visibility', 'visible');
      } else {
        $('.subsystem').attr('visibility', 'hidden');
      }
    },
    toggleFullscreen() {
      this.isFullscreen = !this.isFullscreen;
    },
    zoomToValue(v) {
      if (v >= this.panzoomOptions.minScale
        && v <= this.panzoomOptions.maxScale
      ) {
        this.panzoom.zoomToPoint(v, {
          clientX: this.clientFocusX(),
          clientY: this.clientFocusY(),
        });
      }
    },
    zoomIn() {
      this.zoomToValue(this.currentZoomScale + this.panzoomOptions.step);
    },
    zoomOut() {
      this.zoomToValue(this.currentZoomScale - this.panzoomOptions.step);
    },
    restoreMapPosition(x, y, zoom) {
      this.zoomToValue(1.0);
      this.panToCoords({ panX: x, panY: y, zoom });
      this.zoomToValue(zoom);

      const payload = { ...this.coords, x, y, z: zoom };
      this.$store.dispatch('maps/setCoords', payload);
    },
    updateURLCoord(e) {
      const z = e.detail.scale || this.currentZoomScale;
      const x = e.detail.x || 0;
      const y = e.detail.y || 0;

      const payload = { ...this.coords, x, y, z };
      this.$store.dispatch('maps/setCoords', payload);
    },
    processSelSearchParam() {
      // unselect
      this.unHighlight(this.searchedElemsHL, 'schhl');
      this.unHighlight(this.selectedElemsHL, 'selhl');
      if (this.searchTerm) {
        this.$refs.mapsearch.search(this.searchTerm);
      } else if (this.coords && this.initialLoadWithParams) {
        const coords = Object.values(this.coords);
        this.restoreMapPosition(coords[0], coords[1], coords[2]);
      }
      // selection (sidebar), get the first node with this id
      const elms = this.findElementsOnSVG(this.selectIds);
      this.selectElement(elms[0] || null, true);
    },
    loadSvgPanzoom() {
      if (!this.svgContent) {
        return;
      }

      if (window.scrollY > 0) {
        // for optimal SVG positioning, the calculation expects window.scrollY to be 0
        window.scrollTo(0, 0);
      }

      this.initialLoadWithParams = !!this.$route.query.coords;

      // load the lib svgPanzoom on the SVG loaded
      const panzoomElem = document.getElementById('svg-wrapper');
      this.panzoom = Panzoom(panzoomElem, this.panzoomOptions);

      setTimeout(() => {
        // reset
        this.panzoom.reset();
        panzoomElem.parentElement.removeEventListener('wheel', this.handleWheelEvent);

        // bind event listeners
        panzoomElem.addEventListener('panzoomchange', this.updateURLCoord);
        panzoomElem.addEventListener('panzoomzoom', (e) => {
          this.currentZoomScale = e.detail.scale;
        });

        panzoomElem.parentElement.addEventListener('wheel', this.handleWheelEvent);

        const svg = document.querySelector('#svg-wrapper svg').getBBox();
        const svgBox = document.querySelector('.svgbox');

        // set default pan
        const focusX = svg.width / 2 - svgBox.offsetWidth / 2;
        const focusY = svg.height / 2 - svgBox.offsetHeight / 3;
        this.panzoom.pan(-focusX, -focusY);

        // set default zoom
        const minZoomScale = Math.min(
          svgBox.offsetWidth / svg.width,
          svgBox.offsetHeight / svg.height
        );

        this.panzoom.zoomToPoint(minZoomScale, {
          clientX: this.clientFocusX(),
          clientY: this.clientFocusY(),
        });

        this.processSelSearchParam();
        this.$store.dispatch('maps/setLoading', false);
      }, 0);
    },
    handleWheelEvent(event) {
      event.preventDefault();

      // In certain browsers such as Safari and Firefox,
      // the wheel event triggers too many zooms to be handled
      // properly so that the focal point becomes wrong.
      // This acts as a little bumper to prevent as many zoom events.
      // It is added for all browsers as it is less computationally
      // expensive and helps out performance for bigger maps.
      setTimeout(() => {
        const timeDelta = Date.now() - this.lastWheelZoomTime;

        if (timeDelta > 50) {
          this.lastWheelZoomTime = Date.now();
          this.panzoom.zoomWithWheel(event, { step: 0.3 });
        }
      });
    },
    downloadCanvas() {
      const blob = new Blob([document.getElementById('svg-wrapper').innerHTML], {
        type: 'data:text/tsv;charset=utf-8',
      });
      FileSaver.saveAs(blob, `${this.mapData.id}.svg`);
    },
    applyHPARNAlevelsOnMap(RNAlevels) {
      this.HPARNAlevels = RNAlevels;
      if (Object.keys(this.HPARNAlevels).length === 0) {
        $('#svg-wrapper .enz .shape').attr('fill', this.defaultGeneColor);
        return;
      }

      const allGenes = $('#svg-wrapper .enz');
      Object.values(allGenes).forEach((oneEnz) => {
        try {
          const ID = oneEnz.classList[1];
          if (this.HPARNAlevels[ID] !== undefined) {
            oneEnz.children[0].setAttribute('fill', this.HPARNAlevels[ID][0]); // 0 is the float value, 1 the color hex
          } else {
            oneEnz.children[0].setAttribute('fill', this.HPARNAlevels['n/a'][0]);
          }
        } catch {
          // .values() returns the prop 'length', we don't want that
        }
        return true;
      });

      // update cached selected elements
      Object.keys(this.selectedItemHistory).filter(id => this.HPARNAlevels[id] !== undefined)
        .forEach((ID) => {
          this.selectedItemHistory[ID].rnaLvl = this.HPARNAlevels[ID];
        });
      EventBus.$emit('loadRNAComplete', true, '');
    },
    searchIDsOnMap(ids) {
      this.unHighlight(this.searchedElemsHL, 'schhl');
      this.searchedNodesOnMap = [];
      if (ids) {
        this.searchIDs = ids;
      }
      if (this.searchIDs.length !== 0) {
        this.searchedNodesOnMap = this.findElementsOnSVG(this.searchIDs);
        if (this.searchedNodesOnMap.length !== 0) {
          this.searchedElemsHL = this.highlight(this.searchedNodesOnMap, 'schhl');
          this.centerElementOnSVG(this.searchedNodesOnMap[0]);
        }
      }
    },
    findElementsOnSVG(IDs) {
      const elmsOnMap = [];
      for (let i = 0; i < IDs.length; i += 1) {
        const id = IDs[i].trim();
        const reaSelector = `#svg-wrapper .rea[id="${id}"]`;
        if ($(reaSelector).length) {
          elmsOnMap.push($(reaSelector).first());
        }
        const metEnzSelector = `#svg-wrapper .met[class*=" ${id} "], #svg-wrapper .enz[class*=" ${id} "]`;
        if ($(metEnzSelector).length) {
          $(metEnzSelector).each((k, v) => { // eslint-disable-line no-unused-vars
            elmsOnMap.push($(v));
          });
        }
        const subSelector = `#svg-wrapper .subsystem[id="${id}"]`;
        if ($(subSelector).length) {
          const firstText = $(subSelector).first().find('text')[0];
          elmsOnMap.push($(firstText));
        }
      }
      return elmsOnMap;
    },
    centerElementOnSVG(element) {
      if (!element) {
        return;
      }

      // eslint-disable-next-line max-len
      const coords = this.getSvgElemCoordinates(element) || this.getSvgElemCoordinates($(element).find('.shape')[0]);
      if (!coords) {
        return;
      }
      // const zoom = element.is('text') ? 0.8 : 1; zoom out a bit when centering a subsystem label
      this.panToCoords({ panX: -coords[4], panY: -coords[5], zoom: 1, center: true });
    },
    getSvgElemCoordinates(el) {
      // read and parse the transform attribut
      const node = $(el);
      let transform = node.attr('transform');
      if (transform) {
        transform = transform.substring(0, transform.length - 1);
        transform = transform.substring(7, transform.length);
        return transform.split(',').map(parseFloat);
      }
      return null;
    },
    highlight(nodes, className) {
      const elmsSelected = [];
      for (const el of nodes) { // eslint-disable-line no-restricted-syntax
        if (!el.is('text')) { // do not HL subsystem texts
          $(el).addClass(className);
          elmsSelected.push(el);
          if (el.hasClass('rea') && className === 'selhl') {
            const selectors = `#svg-wrapper .met.${el.attr('id')}`;
            const elms = $(selectors);
            for (const con of elms) { // eslint-disable-line no-restricted-syntax
              $(con).addClass(className);
              elmsSelected.push(con);
            }
          }
        }
      }
      return elmsSelected;
    },
    unHighlight(elements, className) { // un-highlight elements
      if (elements.length !== 0) {
        for (let i = 0; i < elements.length; i += 1) {
          $(elements[i]).removeClass(className);
        }
      }
    },
    getElementIdAndType(element) {
      if (element.hasClass('rea')) {
        return [element.attr('id'), 'reaction'];
      } if (element.hasClass('enz')) {
        return [element.attr('class').split(' ')[1], 'gene'];
      } if (element.hasClass('met')) {
        return [element.attr('class').split(' ')[1], 'metabolite'];
      }
      return [element.attr('id'), 'subsystem'];
    },
    async selectElement(element, routeSelect = false) {
      if (!element) {
        return;
      }
      const [id, type] = this.getElementIdAndType(element);

      if (this.selectedElementId === id && !routeSelect) {
        this.unSelectElement();
        return;
      }

      const selectionData = { type, data: null, error: false };

      this.unHighlight(this.selectedElemsHL, 'selhl');
      if (!element.hasClass('subsystem')) {
        // HL all nodes type but subsystems
        this.selectedElemsHL = this.highlight(this.findElementsOnSVG([id]), 'selhl');
      }

      if (this.selectedItemHistory[id]) {
        selectionData.data = this.selectedItemHistory[id];
        this.$store.dispatch('maps/setSelectedElementId', id);
        this.$emit('updatePanelSelectionData', selectionData);
        return;
      }

      if (type === 'subsystem') {
        // the sidePanel shows only the id for subsystems
        selectionData.data = { id };
        this.$emit('updatePanelSelectionData', selectionData);
        return;
      }

      this.$emit('startSelection');
      try {
        this.$store.dispatch('maps/setLoadingElement', true);
        const payload = {
          model: this.model.apiName,
          version: this.model.apiVersion,
          type,
          id,
        };
        await this.$store.dispatch('maps/getSelectedElement', payload);
        // TODO: consider refactoring more of this block into Vuex
        selectionData.data = this.selectedElement;
        this.selectedItemHistory[id] = selectionData.data;
        this.$emit('updatePanelSelectionData', selectionData);
        this.$emit('endSelection', true);
        this.$store.dispatch('maps/setLoadingElement', false);
      } catch {
        this.$emit('updatePanelSelectionData', selectionData);
        this.$set(selectionData, 'error', true);
        this.$emit('endSelection', false);
        this.$store.dispatch('maps/setLoadingElement', false);
      }
    },
    unSelectElement() {
      this.unHighlight(this.selectedElemsHL, 'selhl');
      this.$store.dispatch('maps/setSelectedElementId', null);
      this.selectedElemsHL = [];
      this.$emit('unSelect');
    },
    clientFocusX() {
      const svgBox = document.querySelector('.svgbox');

      // This is the same as the $tablet (scss variable) width
      if (window.innerWidth < 660) {
        return svgBox.offsetWidth / 2;
      }

      const sidebar = document.querySelector('#mapSidebar');
      return (svgBox.offsetWidth / 2) + sidebar.offsetWidth;
    },
    clientFocusY() {
      const svgBox = document.querySelector('.svgbox');
      const navbar = document.querySelector('#navbar');
      return (svgBox.offsetHeight / 2) + navbar.offsetHeight;
    },
    panToCoords({ panX, panY, zoom, center }) {
      this.panzoom.zoom(zoom);
      if (center) {
        this.panzoom.pan(panX + ($('.svgbox').width() / 2), panY + ($('.svgbox').height() / 2));
      } else {
        this.panzoom.pan(panX, panY);
      }
    },
    reformatChemicalReactionHTML,
  },
};
</script>

<style lang="scss">

.met, .rea, .enz {
  .shape, .lbl {
    cursor: pointer;
  }
  &:hover {
    .shape {
      fill: salmon;
    }
    .lbl {
      font-weight: 900;
      text-shadow: 0 0 2px white;
    }
  }
}

.svgbox {
  position: relative;
  width: 100%;
  height:100%;
  &.fullscreen {
    background: white;
  }

  #svg-wrapper {
    position: relative;

    svg {
      position: relative;
      display: block;
    }
  }
}

svg .selhl {
  display: inline;
  .shape {
    fill: red;
    display: inline;
  }
}

svg .schhl {
  display: inline;
  .shape {
    stroke: orange;
    stroke-width: 5px;
    display: inline;
  }
}

#tooltip {
  background: whitesmoke;
  color: black;
  border-radius: 3px;
  border: 1px solid gray;
  padding: 8px;
  position: absolute;
  display: none;
}
</style>
