<template>
   <div v-if="errorMessage">
    {{ errorMessage }}
   </div>
  <div v-else>
    <span class="title">Models</span>
    <br>
    <span id="show-m-but" class="button is-primary" :class="{'is-active': showMaintained }"
    @click="showMaintained = !showMaintained">
      Maintained only
    </span>
    <div class="container">
      <table v-show="filteredOldGEMS.length != 0" 
      class="table is-bordered is-striped is-narrow">
        <thead>
          <tr>
            <th v-for="f in fields"
              @click="sortBy(f.name)">{{ f.display }}
              </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="gem in filteredOldGEMS">
            <td v-for="i in fields.length">
              {{ gem[fields[i-1].name] }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>


<script>
import axios from 'axios';
import $ from 'jquery';
import { default as compare } from '../helpers/compare';

export default {
  name: 'resources',
  data() {
    return {
      fields: [
        { name: 'organism', display: 'Organism' },
        { name: 'set_name', display: 'Set' },
        { name: 'label', display: 'Label' },
        { name: 'organ_system', display: 'System' },
        { name: 'tissue', display: 'Tissue' },
        { name: 'cell_type', display: 'Cell type' },
        { name: 'reaction_count', display: '# reactions' },
        { name: 'metabolite_count', display: '# metabolites' },
        { name: 'enzyme_count', display: '# enzymes' },
        { name: 'maintained', display: 'Maintained' },
        { name: 'year', display: 'Year' },
      ],
      sortAsc: true,
      errorMessage: '',
      oldGEMs: [],
      sortedOldGEMS: [],
      GEMS: [],
      showMaintained: false,
    };
  },
  computed: {
    filteredOldGEMS: function f() {
      return this.showMaintained ?
       this.sortedOldGEMS.filter(el => el.maintained) : this.sortedOldGEMS;
    },
  },
  methods: {
    getGEMs() {
      axios.get('gems/')
      .then((response) => {
        console.log(response);
        this.GEMs = response.data;
      })
      .catch(() => {
        this.errorMessage = this.$t('notFoundError');
      });
    },
    getOldGEMs() {
      axios.get('old_gems/')
      .then((response) => {
        this.oldMGEMs = [];
        console.log(response.data);
        for (let i = 0; i < response.data.length; i += 1) {
          const gem = response.data[i];
          const sample = gem.sample;
          delete gem.sample;
          this.oldGEMs.push($.extend(gem, sample));
        }
        this.sortedOldGEMS = this.oldGEMs;
        this.errorMessage = '';
      })
      .catch((error) => {
        console.log(error);
        this.errorMessage = this.$t('notFoundError');
      });
    },
    sortBy(field) {
      const gemsList = Array.prototype.slice.call(
      this.sortedOldGEMS); // Do not mutate original elms;
      this.sortedOldGEMS = gemsList.sort(
        compare(field, this.sortAsc ? 'asc' : 'desc'));
      this.sortAsc = !this.sortAsc;
    },
  },
  beforeMount() {
    // this.getGEMs();
    this.getOldGEMs();
  },
};

</script>

<style lang="scss">

.title {
  display: block;
  margin-bottom: 1rem;
}

#show-m-but {
  margin-bottom: 1rem;
}

.dsc, .name {
  height: 75px;
  line-height: 75px;

  span {
    display: inline-block;
    vertical-align: middle;
    line-height: normal;
  }
}

.name {
  font-size: 1.5rem;
}

</style>
