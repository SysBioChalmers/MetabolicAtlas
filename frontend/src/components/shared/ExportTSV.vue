<template>
  <span>
    <a class="button is-primary is-outlined" @click="exportToTSV">
      <span class="icon is-large"><i class="fa fa-download"></i></span>
      <span>Export to TSV</span>
    </a>
    <ErrorPanel :message="errorMessage" @hideErrorPanel="errorMessage=''" />
  </span>
</template>

<script>

import { default as FileSaver } from 'file-saver';
import ErrorPanel from '@/components/shared/ErrorPanel';
import { default as messages } from '@/helpers/messages';

export default {
  name: 'ExportTSV',
  components: {
    ErrorPanel,
  },
  props: {
    arg: [Number, String, Object, Array],
    filename: String,
    formatFunction: Function,
  },
  data() {
    return {
      messages,
      errorMessage: '',
    };
  },
  methods: {
    exportToTSV() {
      try {
        let tsvContent = null;
        // one argument can be passed to the format function
        if (this.arg !== undefined) {
          tsvContent = this.formatFunction(this.arg);
        } else {
          tsvContent = this.formatFunction();
        }
        const blob = new Blob([tsvContent], {
          type: 'text/tsv;charset=utf-8',
        });
        FileSaver.saveAs(blob, this.filename);
      } catch (error) {
        this.errorMessage = messages.fileSaveError;
      }
    },
  },
};
</script>

<style lang="scss"></style>
