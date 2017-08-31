<template>
  <div class="column content">
    <div v-if="selectedElm && ['enzyme', 'metabolite', 'reaction'].includes(selectedElm.type)" class="card">
      <header class="card-header">
        <p class="card-header-title">
          <span v-if="selectedElm.type === 'reaction'">
            Reaction ID: {{ selectedElm.id }}
          </span>
          <span v-else>
            {{ selectedElm.type === 'enzyme' ? 'Enzyme' : 'Metabolite' }}: {{ selectedElm.name }}
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
            {{ selectedElm.details.catalytic_activity }}
          </div>
          <div v-if="!selectedElm.details.function &&
                     !selectedElm.details.catalytic_activity">
            {{ $t('noInfoAvailable') }}
          </div>
        </div>
        <div v-else-if="selectedElm.type === 'metabolite'" class="card-content">
          <div v-if="selectedElm.details.hmdb_description">
            <p class="label">Description</p>
            <p>{{ selectedElm.details.hmdb_description }}</p>
            <br>
          </div>
          <div v-if="selectedElm.details.mass">
            <p class="label il">Molecular mass: </p>
            {{ selectedElm.details.mass }} g/mol
            <br>
          </div>
          <div v-if="selectedElm.details.kegg">
            <p class="label il">Kegg: </p>
            <a :href="keggLink" target="_blank">{{ selectedElm.details.kegg }}</a>
            <br>
          </div>
          <div v-if="!selectedElm.details.hmdb_description &&
                     !selectedElm.details.mass &&
                     !selectedElm.details.kegg">
            {{ $t('noInfoAvailable') }}
          </div>
          <div v-else>
            <button class="button" v-on:click="viewMetaboliteInfo()">More</button>
          </div>
        </div>
      </div>
      <div v-else-if="selectedElm.type === 'reaction'" class="card-content">
        <div v-if="selectedElm.pathway">
          <p class="label">Pathway</p>
          <p>{{ selectedElm.pathway }}</p>
          <br>
        </div>
        <div v-else>
          {{ $t('noInfoAvailable') }}
        </div>
        <div v-else>
          <button class="button" v-on:click="viewMetaboliteInfo()">More</button>
        </div>
      </div>
      <div v-else>
        <div class="card-content">
          {{ $t('noInfoAvailable') }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>

import { default as EventBus } from '../event-bus';

export default {
  name: 'sidebar',
  props: ['selectedElm'],
  data() {
    return {
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
    viewMetaboliteInfo: function viewMetaboliteInfo() {
      EventBus.$emit('updateSelTab', 3,
       this.selectedElm.real_id ? this.selectedElm.real_id : this.selectedElm.id);
    },
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