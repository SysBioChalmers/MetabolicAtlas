<template>
  <div class="column has-text-centered is-three-fifths-desktop is-three-quarters-tablet is-fullwidth-mobile">
    <div class="box has-background-light content">
      <template v-if="type">
        <p class="title is-size-5">
          <span class="is-capitalized">{{ type }}</span><code>{{ componentId }}</code>not found
        </p>
        <template v-if="type === 'model'">
          <p>Visit the Explore page to select one of the integrated models</p>
        </template>
        <template v-else>
          <p>
            Probably there is a typo in the {{ type }} identifier in the URL
            <br>
            Use the
            <span v-if="type === 'map'">list of {{ type }}s</span>
            <span v-else>search bar above </span>
            to find other {{ type }}s
          </p>
        </template>
      </template>
      <template v-else>
        <h1 class="is-size-1 has-text-weight-bold">¯\_(ツ)_/¯<br>404</h1><br>
        <p class="is-size-5">
          The page requested does not exist on this
          <router-link :to="{ name: 'about', hash: '#7-February-2020' }">
            <b>new version of Metabolic Atlas</b>
          </router-link><br>
          If you are looking to download a GEM, look in the menu for
          <router-link :to="{ name: 'gems' }"><b>GEM > Repository</b></router-link>
        </p>
        <br>
      </template>
    </div>
  </div>
</template>
<script>

export default {
  name: 'NotFound',
  props: {
    type: String,
    componentId: String,
  },
};

</script>

<style lang="scss" scoped>
code {
  font-size: 1em;
}
</style>
