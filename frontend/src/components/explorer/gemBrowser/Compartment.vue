<template>
  <div class="section extended-section">
    <div class="container is-fullhd">
      <div v-if="modelNotFound || componentNotFound" class="columns is-centered">
        <NotFound
          :type="modelNotFound ? 'model' : type"
          :component-id="modelNotFound ? $route.params.model : cName" />
      </div>
      <div v-else>
        <div class="columns">
          <div class="column">
            <h3 class="title is-3"><span class="is-capitalized">{{ type }}</span> {{ compartment.name }}</h3>
          </div>
        </div>
        <loader v-if="showLoaderMessage" :message="showLoaderMessage" class="columns" />
        <div v-else class="columns is-multiline is-variable is-8">
          <div class="subsystem-table column is-10-widescreen is-9-desktop is-full-tablet">
            <div class="table-container">
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
            </div>
            <p v-if="model">The
              <a :href="`/api/v2/${model.apiVersion}/compartments/${cName}?full=true`"
                 target="_blank">complete list in JSON format</a>
              of reactions / metabolites / genes is available using our
              <a href="/api/v2" target="_blank">API</a></p>
          </div>
          <div class="column is-2-widescreen is-3-desktop is-half-tablet has-text-centered">
            <maps-available :id="cName" :type="type" :element-i-d="''" />
            <gem-contact :id="cName" :type="type" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import Loader from '@/components/Loader';
import NotFound from '@/components/NotFound';
import MapsAvailable from '@/components/explorer/gemBrowser/MapsAvailable';
import GemContact from '@/components/shared/GemContact';
import { buildCustomLink } from '@/helpers/utils';

export default {
  name: 'Compartment',
  components: {
    NotFound,
    Loader,
    MapsAvailable,
    GemContact,
  },
  data() {
    return {
      cName: '',
      type: 'compartment',
      modelNotFound: false,
      showFullSubsystem: false,
      limitSubsystem: 30,
      componentNotFound: false,
      showLoaderMessage: '',
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
  watch: {
    '$route.params': 'setup',
  },
  async created() {
    if (!this.model || this.model.short_name !== this.$route.params.model) {
      const modelSelectionSuccessful = await this.$store.dispatch('models/selectModel', this.$route.params.model);
      if (!modelSelectionSuccessful) {
        this.modelNotFound = true;
      }
    }
    this.setup();
  },
  methods: {
    async setup() {
      this.showLoaderMessage = 'Loading compartment data';
      this.cName = this.$route.params.id;
      try {
        const payload = { model: this.model, id: this.cName };
        await this.$store.dispatch('compartments/getCompartmentSummary', payload);
        this.componentNotFound = false;
        this.showLoaderMessage = '';
      } catch {
        this.componentNotFound = true;
      }
    },
  },
};
</script>

<style lang="scss">
</style>
