<template>
  <div v-if="selectedElm && ['gene', 'metabolite', 'reaction'].includes(selectedElm.type)" class="card">
    <header class="card-header">
      <p class="card-header-title">
        <span class="is-capitalized">
          {{ selectedElm.type }}: {{ selectedElm.name || selectedElm.id }}
          <span v-if="selectedElm.type === 'metabolite'" class="has-text-weight-light has-text-grey-light">
            {{ selectedElm.compartment }}
          </span>
        </span>
      </p>
    </header>
    <footer class="card-footer has-text-centered">
      <router-link
        v-if="showIpButton && selectedElm.type !== 'reaction'"
        class="card-footer-item p-0"
        :to="{ name: 'interaction', params: { model: model.short_name, id: selectedElm.real_id || selectedElm.id } }">  <!-- eslint-disable-line max-len -->
        <span class="icon is-large"><i class="fa fa-share-alt fa-lg"></i></span>
        <span>{{ messages.interPartName }}</span>
      </router-link>
      <router-link
        class="card-footer-item p-0"
        :to="{ name: selectedElm.type, params: { model: model.short_name, id: selectedElm.real_id || selectedElm.id } }">  <!-- eslint-disable-line max-len -->
        <span class="icon is-large"><i class="fa fa-table fa-lg"></i></span>
        <span>{{ messages.gemBrowserName }}</span>
      </router-link>
    </footer>
  </div>
</template>

<script>

import { mapState } from 'vuex';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'Sidebar',
  props: {
    selectedElm: Object,
    showIpButton: Boolean,
  },
  data() {
    return {
      messages,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
    }),
  },
};
</script>

<style lang="scss"></style>
