<template>
  <div id="app" class="container">
    <router-view></router-view>
  </div>
</template>

<script>

export default {
  name: 'app',
};
</script>

<style lang='scss'>

@import '~bulma';

sup {
  vertical-align: bottom;
  font-size: 0.7em;
}

</style>
