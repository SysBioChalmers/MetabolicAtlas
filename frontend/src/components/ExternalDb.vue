<template>
  <div class="section extended-section">
    <template v-if="externalDb">
      <h3 class="title is-3">
        References to external id {{ externalDb.externalId }}
      </h3>
      <h6 v-if="externalDb.url" class="subtitle is-6">
        Link: <a :href="externalDb.url" target="_blank"> {{ externalDb.url }} </a>
      </h6>
      <ul id="example-1">
        <li v-for="c in components" :key="c.id">
          <router-link :to="{ name: c.componentType.toLowerCase(), params: { model:
            c.model, id: c.id } }">
            {{ c.componentType }} {{ c.id }} from {{ c.model }} {{ c.version }}
          </router-link>
        </li>
      </ul>
    </template>
  </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
  name: 'ExternalDb',
  computed: {
    ...mapState({
      components: state => state.externalDb.components,
      externalDb: state => state.externalDb.externalDb,
    }),
  },
  async beforeMount() {
    await this.$store.dispatch('externalDb/getComponentsForExternalDb', {
      dbName: this.$route.params.dbName,
      externalId: this.$route.params.externalId,
    });
  },
};
</script>

<style lang="scss" scoped>
ul {
  list-style: disc outside none;
}
</style>
