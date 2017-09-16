<template>
  <div>
    <div class="field">
      <div class="">
        <label class="label">IDs: </label>
      </div>
      <br>
      <p class="control">
        <textarea id="idarea" class="textarea" ref="textarea" placeholder="M_m01965g, E_3071, E_3122, M_m02597g, M_m01969g, E_463, M_m02682g">M_m01965g, E_3071, E_3122, M_m02597g, M_m01969g, E_463, M_m02682g</textarea>
      </p>
    </div>
    <div>
      <button class="button is-primary" @click="searchElements">Search</button>
      <button class="button is-primary" @click="" disabled>Highlight</button>
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
            @click="hlElements(k, v)">
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
    };
  },
  created() {
    EventBus.$on('resetView', () => {
      this.compartmentID = 0;
    });
  },
  methods: {
    searchElements() {
      const termsString = this.$refs.textarea.value;
      const arrayTerms = termsString.trim().split(',');
      const filterArray = [];
      for (let i = 0; i < arrayTerms.length; i += 1) {
        const trimTerm = arrayTerms[i].trim();
        if (trimTerm.length !== 0) {
          filterArray.push(trimTerm);
        }
      }
      this.getReactionComponentIDs(filterArray);
    },
    getReactionComponentIDs(array) {
      // get the correct IDs from the backend
      axios.post(`convert_to_reaction_component_ids/${this.compartmentID}`, { data: array })
      .then((response) => {
        const res = response.data;
        const d = {};
        this.enzymeIDs = [];
        for (let i = 0; i < res.length; i += 1) {
          const compartmentID = res[i][0];
          const id = res[i][1];
          if (id[0] === 'M') {
            if (!d[compartmentID.toString()]) {
              d[compartmentID.toString()] = [];
            }
            d[compartmentID.toString()].push(id);
          } else {
            this.enzymeIDs.push(id);
          }
        }
        this.results = d;
        this.showResults = this.results.length !== 0;
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
    hlElements(compartmentID, ids) {
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
