<template>
  <table v-if="comparisons.length > 0" class="table is-striped is-bordered">
    <thead>
      <tr>
        <th></th>
        <th v-for="cn in columnNames" :key="cn">{{ cn }}</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(rn, i) in rowNames" :key="rn + i">
        <th>{{ rn }}</th>
        <td v-for="(cn, j) in columnNames" :key="cn + j">
          {{ matrix[i][j] }}
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>

export default {
  name: 'ComparisonMatrix',
  props: {
    comparisons: { type: Array, required: true },
  },
  computed: {
    singles() {
      return this.comparisons.filter(c => Object.keys(c).length === 1);
    },
    doubles() {
      return this.comparisons.filter(c => Object.keys(c).length === 2);
    },
    triples() {
      return this.comparisons.filter(c => Object.keys(c).length === 3);
    },
    quadruples() {
      return this.comparisons.filter(c => Object.keys(c).length === 4);
    },
    columnNames() {
      return this.singles.map(x => Object.keys(x)[0]);
    },
    rowNames() {
      let names = [...this.columnNames];

      if (this.singles.length === 4) {
        const [n1, n2, n3, n4] = names;

        names = [
          ...names,
          `${n1} + ${n2}`,
          `${n1} + ${n3}`,
          `${n1} + ${n4}`,
          `${n2} + ${n3}`,
          `${n2} + ${n4}`,
          `${n3} + ${n4}`,
        ];
      }

      if (this.singles.length > 2) {
        names.push('all others');
      }

      return names;
    },
    matrix() {
      return this.rowNames.map((rn, i) => this.columnNames.map((cn, j) => {
        let comparison;

        if (rn === cn) {
          comparison = this.singles.find(x => Object.keys(x)[0] === cn);
        } else if (i < this.columnNames.length && j < this.columnNames.length) {
          comparison = this.doubles.find(x => Object.keys(x).includes(rn) && Object.keys(x).includes(cn));
        } else if (i === this.rowNames.length - 1) { // if last row
          comparison = this.columnNames.length === 3 ? this.triples[0] : this.quadruples[0];
        } else {
          const [k1, k2] = rn.split(' + '); // e.g. HumanGem + MouseGem
          comparison = k1 !== cn && k2 !== cn && this.triples.find(x => Object.keys(x).includes(k1)
            && Object.keys(x).includes(k2) && Object.keys(x).includes(cn));
        }

        return comparison ? comparison[cn] : '-';
      }));
    },
  },
};

</script>

<style lang="scss" scoped>

th, td {
  cursor: pointer;
}

</style>
