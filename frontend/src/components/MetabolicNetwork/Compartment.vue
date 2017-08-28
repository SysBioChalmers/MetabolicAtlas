<template>
  <div>
    <p class="menu-label">Compartment:</p>
    <ul class="menu-list">
      <li class="m-li" v-for="comp in compartment">
        {{ comp.name }}
      </li>
    </ul>
  </div>
</template>

<script>

import { getCompartments } from '../../helpers/compartment';

export default {
  name: 'compartment',
  data() {
    return {
      compartmentCount: 0,
      compartments: {},
    };
  },
  mounted() {
    this.loadCompartment();
  },
  methods: {
    loadCompartment() {
      this.compartments = this.getCompartments();
    },
    getCompartments,
  },
};
</script>

<style lang="scss" scoped>

li.m-li {
  cursor: pointer;
}

.li-selected {
  color: #64CC9A;
}
</style>
