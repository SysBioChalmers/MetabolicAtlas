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
        >{{ $t('export') }}</a>
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
      <tbody id="machingTableBody" ref="machingTableBody">
        <tr
          v-for="elm in matchingElms"
          :class="[{ 'highlight': isSelected(elm.id) }, '']"
          @click="highlight(elm.id)"
        >
          <td v-for="s in structure" v-if="s.modifier" v-html="applyModifier(s, elm)"></td>
          <td v-else>{{ elm[s.field] }}</td>
        </tr>
      </tbody>
      <tbody id="unmachingTableBody" ref="unmachingTableBody">
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
  props: ['structure', 'elms', 'selectedElmId', 'filename', 'sheetname'],
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
      this.sortedElms = this.filteredElms;
      this.matchingElms = this.sortedElms;
    },
  },
  computed: {
    filteredElms: function f() {
      return this.elms.filter(
        el => el.type !== 'reactant_box' && el.type !== 'product_box');
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
      this.sortedElms = this.filteredElms;
      this.tableSearchTerm = '';
      this.updateTable();
    },
    searchTable(term) {
      this.tableSearchTerm = term;
      this.updateTable();
    },
    sortBy(field) {
      const elms = Array.prototype.slice.call(this.filteredElms); // Do not mutate original elms;
      this.sortedElms = elms.sort(compare(field, this.sortAsc ? 'asc' : 'desc'));
      this.sortAsc = !this.sortAsc;
      this.updateTable();
    },
    updateTable() {
      if (this.tableSearchTerm === '') {
        this.matchingElms = this.sortedElms;
        this.unMatchingElms = [];
        this.$refs.machingTableBody.style.display = '';
      } else {
        this.matchingElms = [];
        this.unMatchingElms = [];
        const t = this.tableSearchTerm.toLowerCase();

        for (const elm of this.sortedElms) {
          let matches = false;
          for (const s of this.structure) {
            const val = elm[s.field];
            if (typeof val === 'boolean') {
              break;
            }
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
        // fix disappearing row/cell borders
        if (this.matchingElms.length === 0) {
          this.$refs.machingTableBody.style.display = 'none';
        } else {
          this.$refs.machingTableBody.style.display = '';
        }
      }
    },
    exportToExcel() {
      try {
        downloadFile(this.$refs.table, `${this.filename}.xlsx`, this.sheetname);
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

#unmachingTableBody {
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
