<template>
  <div class="container cytoscape-table">
    <div class="columns">
      <div class="column" style="padding-bottom: 0">
        <cytoscape-table-search
          :reset="resetTable"
          @search="searchTable($event)"
          class="is-10"
        ></cytoscape-table-search>
      </div>
      <div class="column is-2" style="padding-bottom: 0">
        <div class="columns">
          <div class="column">
            <a
              @click="exportToExcel"
              class="button is-primary is-pulled-right"
            >{{ $t('exportButton') }}</a>
          </div>
        </div>
      </div>
    </div>
    <div class="columns">
      <div class="column">
        <div class="field">
          <span class="tag">
            # Metabolite(s): {{ metaboliteCount }}
          </span>
          <span class="tag" v-show="enzymeCount">
             # Enzyme(s): {{ enzymeCount }}
          </span>
          <span class="tag" v-show="reactionCount">
             # Reaction(s): {{ reactionCount }}
          </span>
        </div>
        <table class="table is-bordered is-striped is-narrow is-fullwidth" ref="table">
          <thead>
            <tr style="background: #F8F4F4">
              <th class="is-unselectable"
                v-for="s in structure"
                @click="sortBy(s.field)"
              >{{ s.colName }}</th>
            </tr>
          </thead>
          <tbody id="machingTableBody" ref="machingTableBody">
            <tr
              v-for="elm in matchingElms"
              :class="[{ 'highlight': isSelected(elm.id) }, '']"
              @click="highlight(elm.id)">
              <td v-for="s in structure" v-if="'modifier' in s" v-html="applyModifier(s, elm)"></td>
              <td v-else-if="s.field === 'name'">
                <a @click="viewReactionComponent(elm['type'], elm.id)">{{ elm[s.field] }}</a>
              </td>
              <td v-else-if="s.field === 'compartment' && (typeof elm[s.field] !== 'string' && !(elm[s.field] instanceof String))">
                {{ Object.keys(elm[s.field]).map(k => elm[s.field][k] === 1 ? k : `${k}*`).join(', ') }}
              </td>
              <td v-else>
                {{ elm[s.field] }}
              </td>
            </tr>
          </tbody>
          <tbody id="unmachingTableBody" ref="unmachingTableBody">
            <tr
              v-for="elm in unMatchingElms"
              :class="[{ 'highlight': isSelected(elm.id) }, '']"
              @click="highlight(elm.id)">
              <td v-for="s in structure" v-if="'modifier' in s" v-html="applyModifier(s, elm)"></td>
              <td v-else-if="s.field === 'name'">
                <a @click="viewReactionComponent(elm['type'], elm.id)">{{ elm[s.field] }}</a>
              </td>
              <td v-else-if="s.field === 'compartment' && (typeof elm[s.field] !== 'string' && !(elm[s.field] instanceof String))">
                {{ Object.keys(elm[s.field]).map(k => elm[s.field][k] === 1 ? k : `${k}*`).join(', ') }}
              </td>
              <td v-else>{{ elm[s.field] }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>

import CytoscapeTableSearch from 'components/explorer/gemBrowser/CytoscapeTableSearch';
import { default as compare } from '../../../helpers/compare';
import { default as downloadFile } from '../../../helpers/excel-export';
import { default as EventBus } from '../../../event-bus';

export default {
  name: 'cytoscape-table',
  components: {
    CytoscapeTableSearch,
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
    enzymeCount() { return this.elms.filter(el => el.type === 'enzyme').length; },
    metaboliteCount() { return this.elms.filter(el => el.type !== 'enzyme').length; },
    reactionCount() {
      const countReation = {};
      for (const el of this.filteredElms) {
        if (el.reactionid) {
          countReation[el.reactionid] = 1;
        }
      }
      return Object.keys(countReation).length;
    },
  },
  methods: {
    applyModifier(s, elm) { return s.modifier(elm[s.field], elm.link); },
    viewReactionComponent(type, id) { EventBus.$emit('updateSelTab', type, id); },
    isSelected(elmId) { return this.selectedElmId === elmId; },
    highlight(elmId) { this.$emit('highlight', elmId); },
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
      this.sortedElms = elms.sort(compare(field, null, this.sortAsc ? 'asc' : 'desc'));
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
            if (typeof val === 'boolean' || typeof val === 'object') {
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

.cytoscape-table {
  th {
    cursor: pointer;
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
}

</style>
