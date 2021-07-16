<template>
  <div>
    <h4 class="subtitle is-size-4">References</h4>
    <p>Reference details are fetched dynamically from
      <a href="https://europepmc.org" target="_blank">Europe PMC</a>
      based on their PMID.
    </p>
    <template v-if="referenceList.length === 0">
      <p>There are no associated references.</p>
    </template>
    <template v-else>
      <br>
      <table class="main-table table is-fullwidth">
        <tr v-for="pmid in referenceList" :key="pmid">
          <td class="td-key has-background-primary has-text-white-bis">{{ pmid }}</td>
          <td v-if="formattedRefs[pmid]">
            <template v-if="formattedRefs[pmid].link">
              <a target="_blank" :href="formattedRefs[pmid].link">
                <span v-html="formattedRefs[pmid].formattedString"></span>
              </a>
            </template>
            <template v-else>
              <span v-html="formattedRefs[pmid].formattedString"></span>
            </template>
          </td>
          <td v-else>
            Not found in <a :href="`https://europepmc.org/search?query=${pmid}`" target="_blank">Europe PMC</a>
          </td>
        </tr>
      </table>
    </template>
  </div>
</template>

<script>

import { mapState } from 'vuex';

export default {
  name: 'References',
  props: {
    referenceList: {
      type: Array,
      required: true,
    },
  },
  computed: {
    ...mapState({
      formattedRefs: state => state.europepmc.formattedRefs,
    }),
  },
  async beforeMount() {
    if (this.referenceList.length > 0) {
      const queryIds = `(EXT_ID:"${this.referenceList.join('"+OR+EXT_ID:"')}")`;
      await this.$store.dispatch('europepmc/searchReferences', queryIds);
    }
  },
};
</script>

<style lang="scss"></style>
