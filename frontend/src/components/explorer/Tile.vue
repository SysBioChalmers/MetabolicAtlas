<template>
  <div class="tile is-parent" :class="size" @click="navigate()">
    <div class="tile is-child box">
      <p class="is-capitalized title has-text-primary">{{ type }}</p>
      <template v-if="data.formula">
        <span class="is-capitalized">{{ data.name }}</span> with {{ model }} id {{ data.id}} is in the <i>{{ data.compartment }}</i> compartment.
        <p>It has the {{ data.formula }}.</p>
        <p v-if="data.reaction_count">This metabolite is involved in <i>{{ data.reaction_count }}</i> reaction(s) across the model.</p>
      </template>
      <template v-else-if="data.equation">
        {{ data.name }} is reversible and has the following equation: {{ data.equation }}.<br><br>
        This reaction is part of <i>{{ data.sub_count }}</i> subsystem(s) and  <i>{{ data.comp_count}}</i> compartment(s) and is catalyzed by <i>{{ data.e_count }}</i> enzyme(s).
      </template>
      <template v-else-if="data.subsystems">
        <span class="is-capitalized">{{ data.name }}</span> has <i>{{ data.reactions }}</i> reactions.<br><br>
        Subsystems:<br>
        <p v-for="sub in data.subsystems">{{ sub }}<br></p>
      </template>
      <template v-else-if="data.metabolites">
        <i>{{ data.name}}</i> has <i>{{ data.reactions }}</i> reaction(s), <i>{{ data.enzymes }}</i> enzyme(s) and <i>{{ data.metabolites }}</i> metabolite(s). This subsystem spans across <i>{{ data.comp_count }}</i> compartment(s).
      </template>
      <template v-else>
        <i>{{ data.name}}</i> with {{ model }} id {{ data.id}} catalyzes <i>{{ data.reactions }}</i> reaction(s) across {{ data.sub_count}} subsystem(s) and <i>{{ data.comp_count }}</i> compartment(s).
      </template>
      <slot></slot>
    </div>
  </div>
</template>

<script>

export default {
  name: 'tile',
  props: ['type', 'data', 'size', 'model'],
  data() {
    return {
      // name,
    };
  },
  methods: {
    navigate() {
      this.$router.push(`/explore/gem-browser/${this.model}/${this.type}/${this.data.id}`);
    },
  },
};

</script>

<style lang="scss" scoped>

.tile.is-parent {
  :hover {
    cursor: pointer;
  }
}
.box {
  box-shadow: 0 2px 3px lightgray, 0 0 0 1px lightgray;
}
</style>
