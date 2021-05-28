<template>
  <section class="section extended-section">
    <div v-if="externalDb" class="container is-fullhd">
      <h3 class="title is-3 mb-2">
        {{ externalDb.dbName }} {{ components[0].componentType }} {{ externalDb.externalId }}
      </h3>
      <p class="my-3">
        This database identifier is associated with the following Metabolic Atlas
        {{ components.length === 1 ? 'component' : 'components' }}:
      </p>
      <div class="tags are-medium is-flex-direction-column is-align-items-flex-start">
        <span v-for="c in components" :key="c.id + c.model + c.version">
          {{ c.componentType }}
          <router-link :to="{ name: c.componentType.toLowerCase(), params: { model:
            c.model, id: c.id } }">
            <span class="tag is-light">{{ c.id }}</span>
          </router-link>
          from {{ c.model }} {{ c.version }}
        </span>
      </div>
      <p v-if="externalDb.url">
        For more details, visit <a :href="externalDb.url" target="_blank"> {{ externalDb.url }} </a>.
      </p>
    </div>
  </section>
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
