<template>
  <div v-if="showModal" class="modal is-active">
    <div class="modal-background" @click="closeModal"></div>
    <div class="modal-content p-5 column is-6-fullhd is-8-desktop is-10-tablet is-full-mobile
    has-background-white">
      <h4 class="title is-size-4 m-0 mb-2"> List of missing and total reactions on the map </h4>
      <p v-if="currentMap.mapReactionIdSet.length == 1" class="pb-4">
        There are {{ missingReactionList.length }} reactions not shown on the map. Some reactions
        are missing as the {{ currentMap.type }} is being updated much more often than the maps.
        Also, as the maps are manually curated, occasionally some reactions cannot be added.
        The number of reactions shown are {{ mapReactionList.length }}.
        The number of reactions shown is {{ mapReactionList.length }}.
      </p>
      <p v-else class="pb-4">
        There are {{ missingReactionList.length }} reactions not shown on any of the {{ currentMap.name }} maps.
        The 2D map of {{ currentMap.name }} is split into multiple maps due to its size. The number of missing
        reactions displayed is the missing reactions when the reactions in all {{ currentMap.name }} maps are
        combined.
        Some reactions are missing as the {{ currentMap.type }} is being updated much more often than the maps.
        Also, as the maps are manually curated, occasionally some reactions cannot be added.
        The number of reactions shown is {{ mapReactionList.length }}.
      </p>
      <table class="table main-table is-fullwidth m-0">
        <tbody>
          <tr>
            <td class="td-key has-background-primary has-text-white-bis">
              {{ currentMap.mapReactionIdSet.length == 1 ? "Missing reactions on the map" : `Missing reactions
                    on the combined ${currentMap.name} maps` }}
            </td>
            <td>
              <div v-html="missingReactionIdListHtml"></div>
              <div v-if="!showFullReactionListMissing && missingReactionList.length > displayedReaction">
                <br>
                <button class="is-small button" @click="showFullReactionListMissing=true">
                  ... and {{ missingReactionList.length - displayedReaction }} more
                </button>
              </div>
            </td>
          </tr>
          <tr>
            <td class="td-key has-background-primary has-text-white-bis">
              {{ currentMap.mapReactionIdSet.length == 1 ? "Reactions shown on the map" : `Reactions shown
                    on the combined ${currentMap.name} maps` }}
            </td>
            <td>
              <div v-html="mapReactionIdListHtml"></div>
              <div v-if="!showFullReactionListMap && mapReactionList.length > displayedReaction">
                <br>
                <button class="is-small button" @click="showFullReactionListMap=true">
                  ... and {{ mapReactionList.length - displayedReaction }} more
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <button class="modal-close is-large" @click="closeModal"></button>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import { buildCustomLink } from '@/helpers/utils';

export default {
  name: 'MissingReactionsModal',
  props: {
    currentMap: Object,
    missingReactionList: Array,
    mapReactionList: Array,
    showModal: Boolean,
  },
  data() {
    return {
      showFullReactionListMissing: false,
      showFullReactionListMap: false,
      displayedReaction: 40,
    };
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
    }),
    mapReactionIdListHtml() {
      const l = ['<span class="tags">'];
      for (let i = 0; i < this.mapReactionList.length; i += 1) {
        const r = this.mapReactionList[i];
        if (!this.showFullReactionListMap && i === this.displayedReaction) {
          break;
        }
        const customLink = buildCustomLink({ model: this.model.short_name, type: 'reaction', id: r, title: r, cssClass: 'target="_blank"' });
        l.push(
          `<span id="${r}" class="tag">${customLink}</span>`
        );
      }
      l.push('</span>');
      return l.join('');
    },
    missingReactionIdListHtml() {
      const l = ['<span class="tags">'];
      for (let i = 0; i < this.missingReactionList.length; i += 1) {
        const r = this.missingReactionList[i];
        if (!this.showFullReactionListMissing && i === this.displayedReaction) {
          break;
        }
        const customLink = buildCustomLink({ model: this.model.short_name, type: 'reaction', id: r, title: r, cssClass: 'target="_blank"' });
        l.push(
          `<span id="${r}" class="tag">${customLink}</span>`
        );
      }
      l.push('</span>');
      return l.join('');
    },
  },
  methods: {
    closeModal() {
      this.$emit('update:showModal', false);
      this.showFullReactionListMissing = false;
      this.showFullReactionListMap = false;
    },
  },
};
</script>

<style lang="scss" scoped>

</style>
