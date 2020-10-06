<template>
  <div class="canvasOption overlay">
    <span class="button" title="Zoom in" @click="zoomIn()"><i class="fa fa-search-plus"></i></span>
    <span class="button" title="Zoom out" @click="zoomOut()"><i class="fa fa-search-minus"></i></span>
    <span class="button" title="Show/Hide genes"
          style="padding: 4.25px;"
          @click="toggleGenes()">
      <i class="fa fa-eye-slash">&thinsp;G</i>
    </span>
    <span v-if="toggleSubsystems"
          class="button" style="padding: 4.25px;"
          title="Show/Hide subsystem"
          @click="toggleSubsystems()">
      <i class="fa fa-eye-slash">&thinsp;S</i>
    </span>
    <span class="button" title="Toggle fullscreen"
          :disabled="isFullscreenDisabled"
          @click="handleToggleFullScreen()">
      <i class="fa" :class="{ 'fa-compress': isFullscreen, 'fa-arrows-alt': !isFullscreen}"></i>
    </span>
    <span v-if="downloadCanvas" class="button" title="Download as SVG" @click="downloadCanvas()">
      <i class="fa fa-download"></i>
    </span>
  </div>
</template>

<script>

export default {
  name: 'MapControls',
  props: {
    isFullscreen: {
      type: Boolean,
      required: true,
    },
    zoomIn: {
      type: Function,
      required: true,
    },
    zoomOut: {
      type: Function,
      required: true,
    },
    toggleFullScreen: {
      type: Function,
      required: true,
    },
    toggleGenes: {
      type: Function,
      required: true,
    },
    toggleSubsystems: {
      type: Function,
    },
    downloadCanvas: {
      type: Function,
    },
  },
  computed: {
    isFullscreenDisabled() {
      if ((document.fullScreenElement !== undefined && document.fullScreenElement === null)
        || (document.msFullscreenElement !== undefined && document.msFullscreenElement === null)
        || (document.mozFullScreen !== undefined && !document.mozFullScreen)
        || (document.webkitIsFullScreen !== undefined && !document.webkitIsFullScreen)) {
        return false;
      }
      return true;
    },
  },
  methods: {
    handleToggleFullScreen() {
      if (!this.isFullscreenDisabled) {
        this.toggleFullScreen();
      }
    },
  },
};

</script>

<style lang="scss">

</style>
