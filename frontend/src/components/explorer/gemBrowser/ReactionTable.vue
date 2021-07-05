<template>
  <div class="columns">
    <div v-if="showReactionLoader">
      <loader />
    </div>
    <div v-else class="column table-template">
      <h4 class="subtitle is-4">Reactions</h4>
      <div v-if="errorMessage" class="notification is-danger">
        {{ errorMessage }}
      </div>
      <p v-if="relatedMetCount" class="control field">
        <button class="button" @click="toggleExpandAllCompartment">
          {{ !expandAllCompartment ? "See reactions from all compartments" : "Restrict to current compartment" }}
        </button>
      </p>
      <div class="field columns">
        <div class="column"
             :title="(reactions.length || -1) === limitReaction ?
               `The number of reactions displayed is limited to ${limitReaction}` : ''"
        >
          Showing {{ reactions.length }} reaction(s)
          <template v-if="(reactions.length || -1) === limitReaction" class="icon">
            <i class="fa fa-exclamation-triangle has-text-warning"></i> limited to {{ limitReaction }}
          </template>
        </div>
        <div class="column is-narrow">
          <ExportTSV :filename="`Reactions for ${type} ${sourceName}.tsv`" :format-function="formatToTSV">
          </ExportTSV>
        </div>
      </div>
      <div class="table-container">
        <table ref="table" class="table is-bordered is-striped is-narrow is-fullwidth">
          <thead>
            <tr class="has-background-white-ter">
              <th v-for="f in fields" v-show="showCol(f.name)"
                  :key="f.name" class="is-unselectable is-clickable"
                  :title="`Sort by ${f.display}`"
                  @click="sortTable(f.name, null, null)">
                {{ f.display.replace(' ', '&nbsp;') }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in sortedReactions" :key="r.id">
              <td>
                <a :href="`/explore/${model.short_name}/gem-browser/reaction/${r.id}`" @click="handleRouterClick">
                  {{ r.id }}
                </a>
              </td>
              <td v-html="reformatChemicalReactionHTML(r, false, model.short_name, selectedElmId)"></td>
              <td>
                <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key max-len -->
                <template v-for="(m, index) in r.genes">{{ index == 0 ? '' : ', ' }}<a :class="{'cms' : sourceName === m.name }" :href="`/explore/${model.short_name}/gem-browser/gene/${m.id}`" @click="handleRouterClick">{{ m.name || m.id }}</a>
                </template>
              </td>
              <td v-show="showCP">{{ r.cp }}</td>
              <td v-show="showSubsystem">
                <template v-if="r.subsystem_str">
                  <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key max-len -->
                  <template v-for="(s, index) in r.subsystem_str.split('; ')">{{ index == 0 ? '' : '; ' }}<a :href="`/explore/${model.short_name}/gem-browser/subsystem/${idfy(s)}`" @click="handleRouterClick">{{ s }}</a>
                  </template>
                </template>
              </td>
              <td>
                <template v-for="(RP, i) in r.compartment_str.split(' => ')">
                  <template v-if="i !== 0">{{ r.reversible ? ' &#8660; ' : ' &#8658; ' }}</template>
                  <template v-for="(compo, j) in RP.split(' + ')">
                    <template v-if="j != 0"> + </template>
                    <!-- eslint-disable-next-line vue/valid-v-for vue/require-v-for-key max-len -->
                    <a :href="`/explore/${model.short_name}/gem-browser/compartment/${idfy(compo)}`" @click="handleRouterClick">{{ compo }}</a>
                  </template>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import Loader from '@/components/Loader';
import { default as compare } from '@/helpers/compare';
import ExportTSV from '@/components/shared/ExportTSV';
import { idfy, reformatChemicalReactionHTML, getChemicalReaction } from '@/helpers/utils';

export default {
  name: 'ReactionTable',
  components: {
    ExportTSV,
    Loader,
  },
  props: {
    sourceName: { type: String, required: true },
    type: { type: String, required: true },
    selectedElmId: { type: String, required: false, default: null },
    relatedMetCount: { type: Number, required: false, default: 0 },
  },
  data() {
    return {
      fields: [
        { display: 'Reaction ID', name: 'id' },
        { display: 'Equation', name: 'equation' },
        { display: 'Genes', name: 'genes' },
        { display: 'C/P', name: 'cp' },
        { display: 'Subsystem', name: 'subsystem_str' },
        { display: 'Compartment', name: 'compartment_str' },
      ],
      sortOrder: 'asc',
      sortBy: 'id',
      sortPattern: '',
      expandAllCompartment: false,
      showReactionLoader: true,
      errorMessage: '',
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
      reactions: state => state.reactions.relatedReactions,
      limitReaction: state => state.reactions.relatedReactionsLimit,
    }),
    showCP() {
      return this.selectedElmId; // true or false
    },
    showSubsystem() {
      return this.type !== 'subsystem';
    },
    sortedReactions() {
      let reactionsCopy = [...this.reactions];
      if (reactionsCopy.length === 0) {
        return [];
      }
      // create consume/produce column
      if (this.selectedElmId) {
        reactionsCopy = reactionsCopy.map((r) => {
          const rCopy = { ...r };
          if (rCopy.reversible) {
            rCopy.cp = 'consume/produce';
          } else {
            const boolC = rCopy.reactants.filter(
              e => e.id === this.selectedElmId);
            if (boolC.length !== 0) {
              rCopy.cp = 'consume';
            } else {
              const boolP = rCopy.products.filter(
                e => e.id === this.selectedElmId);
              if (boolP.length !== 0) {
                rCopy.cp = 'produce';
              }
            }
          }

          return rCopy;
        });
      }
      return reactionsCopy.concat().sort(
        compare(this.sortBy, this.sortPattern, this.sortOrder));
    },
  },
  watch: {
    sourceName() {
      this.setup();
    },
  },
  async beforeMount() {
    this.setup();
  },
  methods: {
    async setup() {
      this.showReactionLoader = true;
      this.$store.dispatch('reactions/clearRelatedReactions');
      this.errorMessage = '';
      try {
        const payload = {
          model: this.model,
          id: this.sourceName,
          allCompartments: this.expandAllCompartment,
        };
        await this.$store.dispatch(`reactions/getRelatedReactionsFor${this.type[0].toUpperCase()}${this.type.slice(1)}`, payload);
        this.showReactionLoader = false;
      } catch {
        this.errorMessage = `Could not load reactions for ${this.type} ${this.sourceName}.`;
        this.showReactionLoader = false;
      }
    },
    async toggleExpandAllCompartment() {
      this.expandAllCompartment = !this.expandAllCompartment;
      await this.setup();
    },
    sortTable(field, pattern, order) {
      if (order) {
        this.sortOrder = order;
      } else if (field !== this.sortBy) {
        this.sortOrder = 'asc';
      } else {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      }
      this.sortBy = field;
      this.sortPattern = pattern;
    },
    showCol(name) {
      if ((name === 'cp' && !this.showCP) || (name === 'subsystem_str' && !this.showSubsystem)) {
        return false;
      }
      return true;
    },
    formatToTSV() {
      let tsvContent = `${this.fields.filter((e) => {
        if ((e.name === 'cp' && !this.showCP)
          || (e.name === 'subsystem_str' && !this.showSubsystem)) {
          return false;
        }
        return true;
      }).map(e => e.display).join('\t')}\n`;
      tsvContent += this.sortedReactions.map((r) => {
        const arr = [];
        arr.push(r.id);
        arr.push(getChemicalReaction(r));
        arr.push(r.genes.map(g => g.name || g.id).join('; '));
        if (this.showCP) {
          arr.push(r.cp);
        }
        if (this.showSubsystem) {
          arr.push(r.subsystem_str);
        }
        arr.push(r.compartment_str);
        return arr.join('\t');
      }).join('\n');
      return tsvContent;
    },
    idfy,
    reformatChemicalReactionHTML,
  },
};

</script>

<style lang="scss">
a.cms {
  color: rgb(54, 54, 54);
  cursor: default;
  font-weight: 600;
}
</style>
