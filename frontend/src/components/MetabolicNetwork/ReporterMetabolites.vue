<template>
  <div>
    <div class="field">
      <div class="">
        <label class="label">IDs: </label>
      </div>
      <p class="control">
        <textarea id="idarea" class="textarea" ref="textarea" placeholder="udp, h2o2, sam, m_m01784n">udp, h2o2, sam, m_m01784n</textarea>
      </p>
    </div>
    <div>
      <button class="button is-primary" @click="searchElements">Search</button>
    </div>
    <div id="table-res" v-show="showResults">
      <span class="help is-small">Click on a row to highlight the corresponding components</span>
      <table class="table">
        <thead>
          <tr>
            <th>Compartment</th>
             <th>Elements<br>found</th>
          </tr>
        </thead>
        <tbody>
          <tr class="m-tr" v-for="v, k in results"
            @click="hlElements($event, k, v)">
            <td>{{ getCompartmentFromCID(k).name }}</td>
            <td>{{ v.length  }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
/* eslint-disable global-require, no-dynamic-require */
export default {
  name: 'reporter-metabolites',
  data() {
    return {
      errorMessage: '',
      showResults: false,
      showMissingSVGString: true,
      showLoader: true,
      svgContent: null,
      svgName: '',
      compartmentID: 0,
      results: {},
      HLelms: [],
      switched: true,
      panZoom: null,
      snap: null,
      zoomBox: {
        minX: 99999,
        maxX: 0,
        minY: 99999,
        maxY: 0,
      },
    };
  },
  methods: {
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
