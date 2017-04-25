<template>
  <div class="container cytoscape-table">
    <div class="columns">
      <table-search
        :reset="resetTable"
        @search="searchTable($event)"
        class="column is-11"
      ></table-search>
      <div class="column is-1">
        <a
          @click="exportToExcel"
          class="button is-primary"
        >Export</a>
      </div>
    </div>
    <table class="table is-bordered is-striped is-narrow" ref="table">
      <thead>
        <tr>
          <th
            v-for="s in structure"
            @click="sortBy(s.field)"
          >{{ s.colName }}</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="elm in matchingElms"
          :class="[{ 'highlight': isSelected(elm.id) }, '']"
          @click="highlight(elm.id)"
        >
          <td v-for="s in structure" v-if="s.modifier" v-html="applyModifier(s, elm)"></td>
          <td v-else>{{ elm[s.field] }}</td>
        </tr>
      </tbody>
      <tbody class="unMatchingTable">
        <tr
          v-for="elm in unMatchingElms"
          :class="[{ 'highlight': isSelected(elm.id) }, '']"
          @click="highlight(elm.id)"
        >
          <td v-for="s in structure" v-if="s.modifier" v-html="applyModifier(s, elm)"></td>
          <td v-else>{{ elm[s.field] }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>

import TableSearch from 'components/TableSearch';
import { default as compare } from '../helpers/compare';
import { default as downloadFile } from '../helpers/excel-export';

export default {
  name: 'cytoscape-table',
  components: {
    TableSearch,
  },
  props: ['structure', 'elms', 'selectedElmId'],
  data() {
    return {
      sortedElms: [],
      matchingElms: [],
      unMatchingElms: [],
      sortAsc: true,
      tableSearchTerm: '',
      errorMessage: '',
    };
  },
  watch: {
    elms() {
      this.sortedElms = this.elms;
      this.matchingElms = this.elms;
    },
  },
  methods: {
    applyModifier(s, elm) {
      return s.modifier(elm[s.field], elm.link);
    },
    isSelected(elmId) {
      return this.selectedElmId === elmId;
    },
    highlight(elmId) {
      this.$emit('highlight', elmId);
    },
    resetTable() {
      this.sortedElms = this.elms;
      this.tableSearchTerm = '';
      this.updateTable();
    },
    searchTable(term) {
      this.tableSearchTerm = term;
      this.updateTable();
    },
    sortBy(field) {
      const elms = Array.prototype.slice.call(this.elms); // Do not mutate original elms;
      this.sortedElms = elms.sort(compare(field, this.sortAsc ? 'asc' : 'desc'));
      this.sortAsc = !this.sortAsc;
      this.updateTable();
    },
    updateTable() {
      if (this.tableSearchTerm === '') {
        this.matchingElms = this.sortedElms;
        this.unMatchingElms = [];
      } else {
        this.matchingElms = [];
        this.unMatchingElms = [];
        const t = this.tableSearchTerm.toLowerCase();

        for (const elm of this.sortedElms) {
          let matches = false;
          for (const s of this.structure) {
            const val = elm[s.field];
            if (val && val.toLowerCase().includes(t)) {
              matches = true;
              break;
            }
          }

          if (matches) {
            this.matchingElms.push(elm);
          } else {
            this.unMatchingElms.push(elm);
          }
        }
      }
    },
    exportToExcel() {
      try {
        downloadFile(this.$refs.table, 'metabolic_atlas_export.xlsx');
      } catch (e) {
        this.errorMessage = e;
      }
    },
  },
};

</script>

<style lang="scss">

th {
  cursor: pointer;
  user-select: none;
}

tr.highlight {
  background-color: #C5F4DD !important;
}

.unMatchingTable {
  opacity: 0.3;
}

sup {
  vertical-align: bottom;
  font-size: 0.7em;

  &.top {
    vertical-align: top;
  }
}

</style>
