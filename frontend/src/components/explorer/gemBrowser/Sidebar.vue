<template>
  <div v-if="selectedElm && ['enzyme', 'metabolite', 'reaction'].includes(selectedElm.type)" class="card">
    <header class="card-header">
      <p class="card-header-title">
        <span v-if="selectedElm.type === 'reaction'">
          Reaction ID: {{ selectedElm.id }}
        </span>
        <span v-else class="is-capitalized">
          {{ selectedElm.type }}
          <router-link :to="{ path: `/explore/gem-browser/${this.model}/${selectedElm.type}/${this.selectedElm.real_id || this.selectedElm.id}` }">
            {{ selectedElm.name }}
          </router-link>
        </span>
      </p>
    </header>
    <div v-if="selectedElm.details" class="card">
      <div v-if="selectedElm.type === 'enzyme'" class="card-content">
        <div v-if="selectedElm.details.function">
          <p class="label">Function</p>
          <p>{{ selectedElm.details.function }}</p>
          <br>
        </div>
        <div v-if="selectedElm.details.catalytic_activity">
          <p class="label">Catalytic Activity</p>
          <p>{{ selectedElm.details.catalytic_activity }}</p>
          <br>
        </div>
        <div v-if="!selectedElm.details.function &&
                   !selectedElm.details.catalytic_activity">
          {{ messages.noInfoAvailable }}
        </div>
      </div>
      <div v-else-if="selectedElm.type === 'metabolite'" class="card-content">
        <div v-if="selectedElm.details.hmdb_description">
          <p class="label">Description</p>
          <p>{{ selectedElm.details.hmdb_description }}</p>
          <br>
        </div>
        <div v-if="selectedElm.formula">
          <p class="label il">Formula:</p>
          <span v-html="chemicalFormula(selectedElm.formula)"></span>
          <br>
        </div>
        <div v-if="selectedElm.details.mass">
          <p class="label il">Molecular mass: </p>
          <span>{{ selectedElm.details.mass  }} g/mol</span>
          <br>
        </div>
        <div v-if="selectedElm.details.kegg">
          <p class="label il">Kegg: </p>
          <a :href="keggLink" target="_blank">{{ selectedElm.details.kegg }}</a>
          <br>
        </div>
        <div v-if="!selectedElm.details.hmdb_description &&
                   !selectedElm.formula &&
                   !selectedElm.details.mass &&
                   !selectedElm.details.kegg">
          {{ messages.noInfoAvailable }}
        </div>
      </div>
    </div>
    <div v-else-if="selectedElm.type === 'reaction'" class="card-content">
      <div v-if="selectedElm.subsystem">
        <p class="label">Subsystem</p>
        <p>{{ selectedElm.subsystem.join(', ') }}</p>
      </div>
      <div v-if="!selectedElm.subsystem">
        {{ messages.noInfoAvailable }}
      </div>
    </div>
    <div v-else>
      <div class="card-content">
        {{ messages.noInfoAvailable }}
      </div>
    </div>
  </div>
</template>

<script>

import { chemicalFormula } from '../../../helpers/chemical-formatters';
import { default as messages } from '../../../helpers/messages';

export default {
  name: 'sidebar',
  props: ['model', 'selectedElm', 'view'],
  data() {
    return {
      messages,
    };
  },
  computed: {
    keggLink() {
      if (this.selectedElm
        && this.selectedElm.type === 'metabolite'
        && this.selectedElm.details
        && this.selectedElm.details.kegg
      ) {
        return `http://www.genome.jp/dbget-bin/www_bget?cpd:${this.selectedElm.details.kegg}`;
      }
      return '';
    },
  },
  methods: {
    chemicalFormula,
  },
};
</script>

<style lang="scss">

#sidebar {

  .label.il {
    display: inline-block;
  }

  .label:last-child {
    margin-bottom: 0.5em;
  }
}

</style>
