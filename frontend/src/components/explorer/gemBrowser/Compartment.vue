<template>
  <component-layout
    component-type="compartment" :component-name="compartment.name"
    query-component-action="compartments/getCompartmentSummary"
    :include-reaction-table="false"
  >
    <template v-slot:table>
      <table v-if="compartment && Object.keys(compartment).length != 0"
             class="table main-table is-fullwidth">
        <tr>
          <td class="td-key has-background-primary has-text-white-bis">Name</td>
          <td> {{ compartment.name }}</td>
        </tr>
        <tr>
          <td class="td-key has-background-primary has-text-white-bis">Subsystems</td>
          <td>
            <div v-html="subsystemListHtml"></div>
            <div v-if="!showFullSubsystem && subsystems.length > limitSubsystem">
              <br>
              <button class="is-small button" @click="showFullSubsystem=true">
                ... and {{ subsystems.length - limitSubsystem }} more
              </button>
            </div>
          </td>
        </tr>
        <tr>
          <td class="td-key has-background-primary has-text-white-bis">Reactions</td>
          <td> {{ compartment.reactionsCount }}</td>
        </tr>
        <tr>
          <td class="td-key has-background-primary has-text-white-bis">Metabolites</td>
          <td> {{ compartment.metabolitesCount }}</td>
        </tr>
        <tr>
          <td class="td-key has-background-primary has-text-white-bis">Genes</td>
          <td> {{ compartment.genesCount }}</td>
        </tr>
      </table>
    </template>
  </component-layout>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import ComponentLayout from '@/layouts/explorer/gemBrowser/ComponentLayout';
import { buildCustomLink, generateSocialMetaTags } from '@/helpers/utils';

export default {
  name: 'Compartment',
  components: {
    ComponentLayout,
  },
  data() {
    return {
      showFullSubsystem: false,
      limitSubsystem: 30,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
    }),
    ...mapGetters({
      compartment: 'compartments/info',
      subsystems: 'compartments/subsystems',
    }),
    subsystemListHtml() {
      const l = ['<span class="tags">'];
      const sortedSubsystemList = this.subsystems.concat().sort((a, b) => (a.name < b.name ? -1 : 1));
      for (let i = 0; i < sortedSubsystemList.length; i += 1) {
        const s = sortedSubsystemList[i];
        if (!this.showFullSubsystem && i === this.limitSubsystem) {
          break;
        }
        const customLink = buildCustomLink({ model: this.model.short_name, type: 'subsystem', id: s.id, title: s.name });
        l.push(`<span id="${s.id}" class="tag sub">${customLink}</span>`);
      }
      l.push('</span>');
      return l.join('');
    },
  },
  metaInfo() {
    if (!this.model || !this.compartment.name) {
      return {};
    }

    const title = `${this.compartment.name}, Compartment in ${this.model.short_name}`;
    const description = `The compartment ${this.compartment.name} in ${this.model.short_name} (version ${this.model.version}) consists of ${this.compartment.subsystemCount} subsystems, ${this.compartment.reactionsCount} reactions, ${this.compartment.metabolitesCount} metabolites, and ${this.compartment.genesCount} genes.`;

    return {
      title,
      meta: generateSocialMetaTags({ title, description }),
    };
  },
};
</script>

<style lang="scss">
</style>
