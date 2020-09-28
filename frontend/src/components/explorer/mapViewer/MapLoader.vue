<template>
  <div v-show="loading" class="map-loader loading">
    <a class="button is-loading"></a>
  </div>
</template>

<script>

export default {
  name: 'MapLoader',
  props: {
    loading: {
      type: Boolean,
      required: true,
    },
  },
};

</script>

<style lang="scss">

.map-loader {
  z-index: 10;
  position: absolute;
  background: black;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0.8;
  display: table;
  a {
    color: white;
    font-size: 5em;
    font-weight: 1000;
    display: table-cell;
    vertical-align: middle;
    background: black;
    border: 0;
  }
}
</style>
