<template>
  <div>
    <div class="field">
      <p class="control">
        <textarea id="idarea" class="textarea" ref="textarea" placeholder="M_m01965g, E_3071, E_3122, M_m02597g, M_m01969g, E_463, M_m02682g, R_HMR_4410">M_m01965g, E_3071, E_3122, M_m02597g, M_m01969g, E_463, M_m02682g, R_HMR_4410</textarea>
      </p>
    </div>
    <div>
      <button class="button is-info" @click="searchElements(false)">Search</button>
      <button class="button is-info" @click="searchElements(true)">Highlight</button>
    </div>
    <div id="table-res" v-show="showResults">
      <span class="help is-small">Click on a row to highlight the corresponding components</span>
      <table class="table">
        <thead>
          <tr>
            <th>Compartment</th>
             <th>IDs found</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="v, k in results">
            <tr class="m-tr" @click="selectedRow=k">
              <td>{{ k }}</td>
              <td>{{ v.length }}
                <span class="tag" @click="zoomOnElements(k, v)">View</span>
              </td>
            </tr>
            <tr class="hm-tr"v-show="selectedRow===k">
              <td colspan="2">
                <div class="tags">
                  <span v-for="id in v" class="tag" @click="zoomOnElements(k, [id])">{{ id }}</span>
                </div>
              </td>
            </tr>
          </template>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>

import axios from 'axios';
import { getCompartmentFromName } from '../../../helpers/compartment';
import { default as EventBus } from '../../../event-bus';

export default {
  name: 'finder',
  props: ['model'],
  data() {
    return {
      errorMessage: '',
      showResults: false,
      selectedRow: '',
      compartmentName: '',
      results: {},
      enzymeIDs: [],
      HLIDs: [],
    };
  },
  created() {
    EventBus.$on('resetView', () => {
      this.compartmentName = 0;
    });
  },
  methods: {
    searchElements(HLonly) {
      const termsString = this.$refs.textarea.value;
      const arrayTerms = termsString.trim().split(/[,;|-]/);
      const filterArray = [];
      for (let i = 0; i < arrayTerms.length; i += 1) {
        const trimTerm = arrayTerms[i].trim();
        if (trimTerm.length !== 0) {
          filterArray.push(trimTerm);
        }
      }
      this.getReactionComponentIDs(filterArray, HLonly);
    },
    getReactionComponentIDs(array, HLonly) {
      // get the correct IDs from the backend
      axios.post(`${this.model}/convert_to_reaction_component_ids/${this.compartmentName}`, { data: array })
      .then((response) => {
        const res = response.data;
        const d = {};
        // const enzymeIDs = [];
        for (let i = 0; i < res.length; i += 1) {
          const compartmentName = res[i][0];
          const id = res[i][1];
          if (!d[compartmentName]) {
            d[compartmentName] = [];
          }
          d[compartmentName].push(id);
        }
        if (!HLonly) {
          this.results = d;
          this.showResults = Object.keys(this.results).length !== 0;
        } else {
          let idlist = [];
          for (const key of Object.keys(d)) {
            idlist = idlist.concat(d[key]);
          }
          this.HLIDs = idlist;
          EventBus.$emit('showSVGmap', 'highlight', null, this.HLIDs);
        }
      })
      .catch(() => {});
    },
    hlCompartmentElements(compartmentName, ids) {
      EventBus.$emit('showSVGmap', 'compartment', compartmentName, ids);
    },
    zoomOnElements(compartmentName, ids) {
      EventBus.$emit('showSVGmap', 'find', compartmentName, ids);
    },
    getCompartmentFromName,
  },
};
</script>

<style lang="scss" scoped>



  #idarea {
    height: 100px;
  }

  #table-res {
    margin-top: 1rem;
  }

  tr.m-tr {
    cursor: pointer;
    td {
        padding: 0.3em 0.5em;
    }
  }

  tr.hm-tr {
    .tag {
      cursor: pointer;
    }
    &.hover {
      background-color: #fff;
    }
    div {
      overflow-x: hidden;
      overflow-y: auto;
      max-height: 10rem;
    }
  }

  tr.sel-tr {
    background: #eee;
  }
</style>
