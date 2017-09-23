<template>
  <div>
    <div class="field">
      <div class="">
        <label class="label">IDs: </label>
      </div>
      <br>
      <p class="control">
        <textarea id="idarea" class="textarea" ref="textarea" placeholder="M_m01965g, E_3071, E_3122, M_m02597g, M_m01969g, E_463, M_m02682g, R_HMR_4410">M_m01965g, E_3071, E_3122, M_m02597g, M_m01969g, E_463, M_m02682g, R_HMR_4410</textarea>
      </p>
    </div>
    <div>
      <button class="button is-primary" @click="searchElements(false)">Search</button>
      <button class="button is-primary" @click="searchElements(true)">Highlight</button>
    </div>
    <div id="table-res" v-show="showResults">
      <span class="help is-small">Click on a row to highlight the corresponding components</span>
      <table class="table">
        <thead>
          <tr>
            <th>Compartment</th>
             <th>Metabolites<br>found</th>
          </tr>
        </thead>
        <tbody>
          <tr class="m-tr" v-for="v, k in results"
            @click="hlCompartmentElements(k, v)">
            <td>{{ getCompartmentFromCID(k).name }}</td>
            <td>{{ v.length  }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>

import axios from 'axios';
import { getCompartmentFromCID } from '../../helpers/compartment';
import { default as EventBus } from '../../event-bus';

export default {
  name: 'region',
  data() {
    return {
      errorMessage: '',
      showResults: false,
      compartmentID: 0,
      results: {},
      enzymeIDs: [],
      HLIDs: [],
    };
  },
  created() {
    EventBus.$on('resetView', () => {
      this.compartmentID = 0;
    });
  },
  methods: {
    searchElements(HLonly) {
      const termsString = this.$refs.textarea.value;
      const arrayTerms = termsString.trim().split(',');
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
      axios.post(`convert_to_reaction_component_ids/${this.compartmentID}`, { data: array })
      .then((response) => {
        const res = response.data;
        const d = {};
        const enzymeIDs = [];
        for (let i = 0; i < res.length; i += 1) {
          const compartmentID = res[i][0];
          const id = res[i][1];
          if (id[0] === 'M' || id[0] === 'R') {
            if (!d[compartmentID.toString()]) {
              d[compartmentID.toString()] = [];
            }
            d[compartmentID.toString()].push(id);
          } else {
            enzymeIDs.push(id);
          }
        }
        // NOTE d is empty when only enzymes are found..

        if (!HLonly) {
          this.results = d;
          this.enzymeIDs = enzymeIDs;
          this.showResults = Object.keys(this.results).length !== 0;
        } else {
          let idlist = [];
          for (const key of Object.keys(d)) {
            idlist = idlist.concat(d[key]);
          }
          this.HLIDs = idlist.concat(enzymeIDs);
          EventBus.$emit('showSVGmap', 'highlight', null, this.HLIDs);
        }
      })
      .catch(() => {});
    },
    hlRow(tr) {
      const currentRow = tr;
      for (const row of tr.parentElement.getElementsByTagName('tr')) {
        row.classList.remove('sel-tr');
      }
      currentRow.classList.add('sel-tr');
    },
    hlCompartmentElements(compartmentID, ids) {
      EventBus.$emit('showSVGmap', 'compartment', compartmentID, ids.concat(this.enzymeIDs));
    },
    getCompartmentFromCID,
  },
};
</script>

<style lang="scss" scoped>
  #idarea {
    width: 100px;
    height: 200px;
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

  tr.sel-tr {
    background: #eee;
  }

  svg .hl {
    fill: #22FFFF;
  }
</style>
