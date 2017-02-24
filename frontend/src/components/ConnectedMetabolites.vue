<template>
  <div class="connected-metabolites">
    <h1>Connected metabolites</h1>
    <div id="cy" ref="cy"></div>
  </div>
</template>

<script>
import jquery from 'expose?$!expose?jQuery!jquery';
import axios from 'axios';
import cytoscape from 'cytoscape';
import { default as regCose } from 'cytoscape-cose-bilkent';
import cyqtip from 'cytoscape-qtip';
import { default as transform } from '../data-mappers/connected-metabolites';
import { default as graph } from '../graph-stylers/connected-metabolites';

export default {
  name: 'connected-metabolites',
  data() {
    return {
      errorMessage: '',
    };
  },
  methods: {
    load() {
      axios.get(`enzymes/${this.$route.params.enzyme_id}/connected_metabolites`)
        .then((response) => {
          this.errorMessage = '';

          const [elms, rels] = transform(response.data);
          const [elements, stylesheet] = graph(elms, rels);

          const cy = cytoscape({
            container: this.$refs.cy,
            elements,
            style: stylesheet,
            layout: {
              name: 'cose-bilkent',
              tilingPaddingVertical: 50,
              tilingPaddingHorizontal: 50,
            },
            ready() {
              cy.$('node').qtip({
                content: 'Remove<br>Re-center view<br>Only 1st level interactions<br>Expand to 1st level interactions',
                position: {
                  my: 'top center',
                  at: 'bottom center',
                },
                style: {
                  classes: 'qtip-bootstrap',
                  tip: {
                    width: 16,
                    height: 8,
                  },
                },
              });
            },
          });
        })
        .catch((error) => {
          this.errorMessage = error.message;
        });
    },
  },
  beforeMount() {
    regCose(cytoscape);
    cyqtip(cytoscape, jquery);
    this.load();
  },
};

</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

h1, h2 {
  font-weight: normal;
}

#cy {
  border: 1px dotted black;
  position: static;
  margin: auto;
  height: 820px;
}

</style>
