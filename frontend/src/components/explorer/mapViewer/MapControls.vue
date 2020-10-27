<template>
  <div class="canvasOption overlay p-2">
    <span class="button" title="Zoom in" @click="zoomIn()"><i class="fa fa-search-plus"></i></span>
    <span class="button" title="Zoom out" @click="zoomOut()"><i class="fa fa-search-minus"></i></span>
    <span class="button" title="Show/Hide genes"
          style="padding: 4.25px;"
          @click="toggleGenes()">
      <i class="fa fa-eye-slash">&thinsp;G</i>
    </span>
    <span v-if="toggleLabels" class="button" title="Show/Hide labels"
          style="padding: 4.25px;"
          @click="toggleLabels()">
      <i class="fa fa-eye-slash">&thinsp;L</i>
    </span>
    <span v-if="toggleSubsystems"
          class="button" style="padding: 4.25px;"
          title="Show/Hide subsystem"
          @click="toggleSubsystems()">
      <i class="fa fa-eye-slash">&thinsp;S</i>
    </span>
    <span v-if="toggleBackgroundColor" class="button" title="Toggle background color"
          @click="toggleBackgroundColor()">
      <i class="fa fa-adjust"></i>
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
    wrapperElemSelector: {
      type: String,
      required: true,
    },
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
    toggleLabels: {
      type: Function,
    },
    toggleSubsystems: {
      type: Function,
    },
    toggleBackgroundColor: {
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
      if (this.isFullscreenDisabled) {
        return;
      }

      const elem = document.querySelector(this.wrapperElemSelector);
      if ((document.fullScreenElement !== undefined && document.fullScreenElement === null)
        || (document.msFullscreenElement !== undefined && document.msFullscreenElement === null)
        || (document.mozFullScreen !== undefined && !document.mozFullScreen)
        || (document.webkitIsFullScreen !== undefined && !document.webkitIsFullScreen)) {
        if (elem.requestFullScreen) {
          elem.requestFullScreen();
        } else if (elem.mozRequestFullScreen) {
          elem.mozRequestFullScreen();
        } else if (elem.webkitRequestFullScreen) {
          elem.webkitRequestFullScreen(Element.ALLOW_KEYBOARD_INPUT);
        } else if (elem.msRequestFullscreen) {
          elem.msRequestFullscreen();
        }
      } else if (document.cancelFullScreen) {
        document.cancelFullScreen();
      } else if (document.mozCancelFullScreen) {
        document.mozCancelFullScreen();
      } else if (document.webkitCancelFullScreen) {
        document.webkitCancelFullScreen();
      } else if (document.msExitFullscreen) {
        document.msExitFullscreen();
      }
      this.toggleFullScreen();
    },
  },
};

</script>

<style lang="scss">

</style>
