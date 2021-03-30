<template>
  <div class="container is-fullhd cytoscape-table">
    <div class="columns">
      <div class="column is-half is-8-tablet">
        <input v-model="tableSearch" class="input" type="text" placeholder="Search in table"
               data-hj-whitelist @keyup.prevent="updateTable">
      </div>
      <div class="column"></div>
      <div class="column is-narrow">
        <ExportTSV :filename="`${filename}.tsv`" :format-function="formatToTSV" />
      </div>
    </div>
    <div class="columns">
      <div class="column">
        <div class="field">
          <span class="tag">
            # Reaction(s): {{ reactions.length }}
          </span>
          &nbsp;
          <span class="tag">
            # Unique Metabolite(s): {{ metaboliteCount }}
          </span>
          &nbsp;
          <span v-show="geneCount" class="tag">
            # Unique Gene(s): {{ geneCount }}
          </span>
          <span v-show="isGraphVisible">
            &nbsp; Click on a <span class="tag is-rounded"><span class="is-size-6">label</span></span>
            to highlight the corresponding element on the graph
          </span>
        </div>
        <div class="table-container">
          <table id="cytoTable" ref="table" class="table is-bordered is-narrow is-fullwidth">
            <thead>
              <tr style="background: #F8F4F4">
                <th v-for="s in columns" :key="s.field" class="is-unselectable is-clickable" @click="sortBy(s.field)">
                  {{ s.display }}
                </th>
              </tr>
            </thead>
            <tbody id="machingTableBody" ref="machingTableBody">
              <tr v-for="r in matchingReactions" :key="r.id">
                <td v-for="s in columns" :key="s.field">
                  <template v-if="s.field === 'id'">
                    <span class="tag is-rounded is-clickable" :class="[{ 'hl': isSelected(r.id) }, '']"
                          @click="HLreaction(r.id)">
                      <span class="is-size-6">{{ r.id }}</span>
                    </span>
                  </template>
                  <template v-else-if="['reactants', 'products', 'genes'].includes(s.field)">
                    <template v-for="el in r[s.field]">
                      <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                      <span class="tag is-rounded is-clickable is-medium"
                            :title="s.field !== 'genes' ? `${el.id} - ${el.compartment_str}` : el.id"
                            :class="[{ 'hl': isSelected(el.id) }, '']" @click="highlight(el.id)">
                        <span class="">{{ el.name || el.id }}</span>
                      </span>
                    </template>
                  </template>
                  <template v-else>
                    {{ r[s.field] }}
                  </template>
                </td>
              </tr>
            </tbody>
            <tbody id="unmachingTableBody" ref="unmachingTableBody">
              <tr v-for="r in unMatchingReactions" :key="r.id">
                <td v-for="s in columns" :key="s.field">
                  <template v-if="s.field === 'id'">
                    <span class="tag is-rounded is-clickable" :class="[{ 'hl': isSelected(r.id) }, '']"
                          @click="HLreaction(r.id)">
                      <span class="is-size-6">{{ r.id }}</span>
                    </span>
                  </template>
                  <template v-else-if="['reactants', 'products', 'genes'].includes(s.field)">
                    <template v-for="el in r[s.field]">
                      <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key -->
                      <span class="tag is-rounded is-clickable is-medium"
                            :title="s.field !== 'genes' ? `${el.id} - ${el.compartment_str}` : el.id"
                            :class="[{ 'hl': isSelected(el.id) }, '']" @click="highlight(el.id)">
                        <span class="">{{ el.name || el.id }}</span>
                      </span>
                    </template>
                  </template>
                  <template v-else>
                    {{ r[s.field] }}
                  </template>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

import ExportTSV from '@/components/shared/ExportTSV';
import { default as compare } from '@/helpers/compare';

export default {
  name: 'CytoscapeTable',
  components: {
    ExportTSV,
  },
  props: {
    reactions: Array,
    selectedElmId: String,
    selectedReactionId: String,
    isGraphVisible: Boolean,
    filename: String,
  },
  data() {
    return {
      columns: [
        { field: 'id', display: 'Reaction ID' },
        { field: 'reactants', display: 'Reactants' },
        { field: 'products', display: 'Products' },
        { field: 'genes', display: 'Genes' },
        { field: 'compartment', display: 'Compartment' },
      ],
      matchingReactions: [],
      unMatchingReactions: [],
      sortAsc: true,
      sortField: null,
      tableSearch: '',
      errorMessage: '',
      hlID: null,
    };
  },
  computed: {
    sortedReactions() {
      const reactions = Array.prototype.slice.call(this.reactions); // Do not mutate original elms;
      return reactions.sort(compare(this.sortField, null, this.sortAsc ? 'asc' : 'desc'));
    },
    geneCount() {
      const genes = new Set();
      this.reactions.forEach((r) => {
        r.genes.forEach((e) => { genes.add(e.id); });
      });
      return genes.size;
    },
    metaboliteCount() {
      const metabolites = new Set();
      this.reactions.forEach((r) => {
        r.reactants.forEach((e) => { metabolites.add(e.id); });
        r.products.forEach((e) => { metabolites.add(e.id); });
      });
      return metabolites.size;
    },
  },
  watch: {
    reactions() {
      this.sortAsc = true;
      this.sortField = null;
      this.hlID = null;
      this.updateTable();
    },
    selectedElmId() {
      this.hlID = this.selectedElmId.slice();
    },
  },
  mounted() {
    this.hlID = null;
    this.updateTable();
  },
  methods: {
    isSelected(elmId) {
      return this.hlID === elmId || this.selectedReactionId === elmId;
    },
    highlight(elmId) {
      const sameID = this.hlID === elmId;
      this.hlID = sameID ? '' : elmId;
      this.$emit('highlight', this.hlID);
    },
    HLreaction(rID) {
      this.$emit('HLreaction', this.selectedReactionId === rID ? null : rID);
    },
    sortBy(field) {
      this.sortField = field;
      this.sortAsc = !this.sortAsc;
      this.updateTable();
    },
    updateTable() {
      if (this.tableSearch === '') {
        this.matchingReactions = Array.prototype.slice.call(this.sortedReactions);
        this.unMatchingReactions = [];
        this.$refs.machingTableBody.style.display = '';
      } else {
        this.matchingReactions = [];
        this.unMatchingReactions = [];
        const t = this.tableSearch.toLowerCase();
        this.sortedReactions.forEach((elm) => {
          let matches = false;
          this.columns.every((s) => {
            const val = elm[s.field];
            if (typeof val === 'object' && ['reactants', 'products', 'genes'].includes(s.field)) {
              let match = false;
              val.every((el) => {
                Object.keys(el).every((k) => {
                  if (k === 'id') {
                    match = el[k].toLowerCase() === t;
                  } else {
                    match = el[k].toLowerCase().includes(t);
                  }
                  if (match) {
                    matches = match;
                  }
                  return !matches;
                });
                return !matches;
              });
            } else if (!matches && val && val.toLowerCase().includes(t)) {
              matches = true;
            }
            return !matches;
          });
          if (matches) {
            this.matchingReactions.push(elm);
          } else {
            this.unMatchingReactions.push(elm);
          }
        });

        // fix disappearing row/cell borders
        if (this.matchingReactions.length === 0) {
          this.$refs.machingTableBody.style.display = 'none';
        } else {
          this.$refs.machingTableBody.style.display = '';
        }
      }
    },
    formatToTSV() {
      let tsvContent = `${this.columns.map(e => e.display).join('\t')}\n`;
      tsvContent += this.sortedReactions.map(d => [
        d.id,
        d.reactants.map(e => e.name || e.id).join('; '),
        d.products.map(e => e.name || e.id).join('; '),
        d.genes.map(e => e.name || e.id).join('; '),
        d.compartment,
      ].join('\t')
      ).join('\n');
      return tsvContent;
    },
  },
};

</script>

<style lang="scss">
.cytoscape-table {
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
