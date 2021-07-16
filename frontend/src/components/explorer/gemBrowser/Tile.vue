<template>
  <router-link class="tile is-parent" :class="size"
               :to="{ name: type, params: { model: model.short_name, id: data.id } }">
    <div class="tile is-child is-clickable box hoverable"
         :title="`Click to view ${data.name || data.id}`">
      <p class="is-capitalized subtitle is-size-4-desktop is-size-5-tablet
         has-text-weight-light has-text-grey-light">{{ label || type }}</p>
      <template v-if="type === 'metabolite'">
        <span class="is-capitalized"><b>{{ data.name }}</b></span>
        with {{ model.short_name }} ID <b>{{ data.id }}</b> is in
        the <b>{{ data.compartment }}</b> compartment.
        <p v-if="data.formula">Its formula is <b>{{ data.formula }}</b>.</p>
        <p v-if="data.reactionCount">This compound is involved in
          <b>{{ data.reactionCount }}</b> reaction(s) across the model.
        </p>
      </template>
      <template v-else-if="type === 'reaction'">
        <b>{{ data.id }}</b> is <b>{{ data.isReversible ? 'reversible' : 'irreversible' }}</b>
        and has the following equation:
        <br>
        <b v-html="getSimpleEquation(data)"></b>
        <br><br>
        This reaction is part of <b>{{ data.subsystemCount }}</b> subsystem(s)
        and <b>{{ data.compartmentCount }}</b> compartment(s) and is associated
        with <b>{{ data.geneCount }}</b> gene(s).
      </template>
      <template v-else-if="type === 'compartment'">
        <span class="is-capitalized"><b>{{ data.name }}</b></span> has
        <b>{{ data.reactionCount }}</b> reactions,
        <b>{{ data.metaboliteCount }}</b> metabolite(s) and
        <b>{{ data.geneCount }}</b> gene(s).
        <br><br>
        <b>Major subsystems</b>:
        <br>
        <p><ul><li v-for="sub in data.majorSubsystems" :key="sub">{{ sub }}</li></ul></p>
      </template>
      <template v-else-if="type === 'subsystem'">
        <b>{{ data.name }}</b> has <b>{{ data.reactionCount }}</b> reaction(s),
        <b>{{ data.metaboliteCount }}</b> metabolite(s) and
        <b>{{ data.geneCount }}</b> gene(s).
        This subsystem spans across <b>{{ data.compartmentCount }}</b> compartment(s).
      </template>
      <template v-else>
        <template v-if="data.name">
          <b>{{ data.name }}</b> with {{ model.short_name }} ID <b>{{ data.id }}</b>
          is associated with <b>{{ data.reactionCount }}</b> reaction(s) across
          <b>{{ data.subsystemCount }}</b> subsystem(s) and
          <b>{{ data.compartmentCount }}</b> compartment(s).
        </template>
        <template v-else>
          <b>{{ data.id }}</b> is associated with
          <b>{{ data.reactionCount }}</b> reaction(s) across
          <b>{{ data.subsystemCount }}</b> subsystem(s) and
          <b>{{ data.compartmentCount }}</b> compartment(s).
        </template>
      </template>
      <slot></slot>
    </div>
  </router-link>
</template>

<script>
import { getSimpleEquation } from '@/helpers/utils';
import { mapState } from 'vuex';

export default {
  name: 'Tile',
  props: {
    type: String,
    data: Object,
    size: String,
    label: String,
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
    }),
  },
  methods: {
    getSimpleEquation,
  },
};
</script>

<style lang="scss"></style>
