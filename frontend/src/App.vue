<template>
  <div id="app">
    <section class="section">
      <div class="container">
        <router-view></router-view>
      </div>
    </section>
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
}

</style>
