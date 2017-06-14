<template>
  <div class="container reaction-table">
    <table class="table is-bordered is-striped is-narrow" ref="table">
      <thead>
        <tr>
          <th>Reaction Id</th>
          <th>Equation</th>
          <th v-if="false">Reactants</th>
          <th v-if="false">Products</th>
          <th>Modifiers</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in reactions">
          <td>{{ r.id }}</td>
          <td>{{ r.equation }}</td>
          <td v-if="false">{{ r.reactants.length }}</td>
          <td v-if="false">{{ r.products.length }}</td>
          <td>{{ r.modifiers.join(', ') }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>

export default {
  name: 'reaction-table',
  props: ['reactions'],
};

</script>

<style lang="scss">
</style>
