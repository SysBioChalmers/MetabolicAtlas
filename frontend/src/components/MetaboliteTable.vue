<template>
  <div class="metabolite-table">
    <table v-if="info && Object.keys(info).length != 0" class="table">
      <tr>
        <td>Metabolic Atlas ID</td>
        <td>{{ metaboliteId }}</td>
      <tr>
      <tr>
        <td>Name</td>
        <td>{{ info.name }}</td>
      <tr>
      <tr v-for="el, k in info.details">
        <td> {{ k }} </td>
        <td> {{ el }} </td>
      </tr>
      <tr>
        <td>Human Protein atlas</td>
        <td><a :href="info.hpaLink">{{ info.name }}</a></td>
      <tr>
    </table>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'metabolite-table',
  props: ['metaboliteInfo', 'metaboliteId'],
  data() {
    return {
      mId: '',
      info: {},
    };
  },
  watch: {
    metaboliteInfo() {
      this.info = this.metaboliteInfo;
      this.mId = this.metaboliteId;
    },
  },
  methods: {
    load() {
      axios.get(`metabolite/${this.mId}/`)
      .then((response) => {
        console.log(response);
      })
      .catch((error) => {
        console.log('error:');
        console.log(error);
      });
    },
  },
  // beforeMount() {
    // this.load();
  // },
};
</script>

<style lang="scss">

.metabolite-table tr > td:first-child {
  background: lightgray;
  width: 150px;
}

</style>