<template>
  <div class="tile is-parent" :class="size" @click="navigate()">
    <div class="tile is-child box">
      <p class="is-capitalized title has-text-primary">{{ type }}</p>
      <template v-if="type == 'metabolite'">
        <span class="is-capitalized"><b>{{ data.name }}</b></span> with {{ model.short_name }} ID <b>{{ data.id}}</b> is in the <b>{{ data.compartment }}</b> compartment.
        <p>Its formula is <b>{{ data.formula }}</b>.</p>
        <p v-if="data.reaction_count">This compound is involved in <b>{{ data.reaction_count }}</b> reaction(s) across the model.</p>
      </template>
      <template v-else-if="type == 'reaction'">
        <b>{{ data.id }}</b> is <b>{{ data.is_reversible ? 'reversible' : 'irreversible' }}</b> and has the following equation:<br><b>{{ data.equation_wname.replace('=>', data.is_reversible ? '&#8660;' : '&#8658;') }}</b>.<br><br>
        This reaction is part of <b>{{ data.subsystem_count }}</b> subsystem(s) and <b>{{ data.compartment_count}}</b> compartment(s) and is catalyzed by <b>{{ data.enzyme_count }}</b> enzyme(s).
      </template>
      <template v-else-if="type == 'compartment'">
        <span class="is-capitalized"><b>{{ data.name }}</b></span> has <b>{{ data.reaction_count }}</b> reactions, <b>{{ data.metabolite_count }}</b> metabolite(s) and <b>{{ data.enzyme_count }}</b> enzyme(s).<br><br>
        <b>Major subsystems</b>:<br>
        <p><ul>
          <li v-for="sub in data.subsystems">{{ sub }}</li>
        </ul></p>
      </template>
      <template v-else-if="type == 'subsystem'">
        <b>{{ data.name}}</b> has <b>{{ data.reaction_count }}</b> reaction(s), <b>{{ data.metabolite_count }}</b> metabolite(s) and <b>{{ data.enzyme_count }}</b> enzyme(s). This subsystem spans across <b>{{ data.compartment_count }}</b> compartment(s).
      </template>
      <template v-else>
        <b>{{ data.name}}</b> with {{ model.short_name }} ID <b>{{ data.id}}</b> catalyzes <b>{{ data.reaction_count }}</b> reaction(s) across <b>{{ data.subsystem_count }}</b> subsystem(s) and <b>{{ data.compartment_count }}</b> compartment(s).
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
      this.$router.push(`/explore/gem-browser/${this.model.database_name}/${this.type}/${this.data.id}`);
    },
  },
};

</script>

<style lang="scss" scoped>

.tile.is-child {
  &:hover {
    cursor: pointer;
    box-shadow: 0 2px 3px gray, 0 0 0 1px gray;
  }
  ul {
    list-style-type: disc;
    margin-left: 2rem;
  }
}
.box {
  box-shadow: 0 2px 3px lightgray, 0 0 0 1px lightgray;
}
</style>
