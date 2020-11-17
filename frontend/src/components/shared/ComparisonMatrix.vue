<template>
  <table v-if="mergedComparisons" class="table is-bordered">
    <thead>
      <tr>
        <th>compared to ↓</th>
        <th v-for="cn in columnNames" :key="cn" colspan="2">{{ cn.replace('Gem', '') }}</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(rn, i) in rowNames" :key="rn + i">
        <th>{{ rn.replace('Gem', '') }}</th>
        <template v-for="(cn, j) in columnNames">
          <td v-for="(type, k) in types" :key="cn + j + type" :style="{backgroundColor: colors[k]}">
            {{ matrix[i][j][type] }}
          </td>
        </template>
      </tr>
    </tbody>
    <caption>
      Legend:
      <span v-for="(type, k) of types" :key="type" :style="{backgroundColor: colors[k]}">
        {{ type }}
      </span>
    </caption>
  </table>
</template>

<script>

export default {
  name: 'ComparisonMatrix',
  props: {
    comparisons: { type: Object, required: true },
  },
  data() {
    return {
      colors: ['#eef6fc', '#fffbeb'],
    };
  },
  computed: {
    mergedComparisons() {
      // currently has support for two types
      if (this.comparisons && Object.keys(this.comparisons).length !== 2) {
        return null;
      }

      const [t1, t2] = this.types;
      return this.comparisons[t1].map((row, i) => Object.keys(row).reduce((mergedRow, key) => {
        mergedRow[key] = { // eslint-disable-line no-param-reassign
          [t1]: this.comparisons[t1][i][key],
          [t2]: this.comparisons[t2][i][key],
        };
        return mergedRow;
      }, {}));
    },
    types() {
      return Object.keys(this.comparisons);
    },
    singles() {
      return this.mergedComparisons.filter(c => Object.keys(c).length === 1);
    },
    doubles() {
      return this.mergedComparisons.filter(c => Object.keys(c).length === 2);
    },
    triples() {
      return this.mergedComparisons.filter(c => Object.keys(c).length === 3);
    },
    quadruples() {
      return this.mergedComparisons.filter(c => Object.keys(c).length === 4);
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
table {
  caption-side: bottom;

  caption {
    padding: 0.25em;

    span {
      padding: 0.25em;
    }
  }

  th, td {
    cursor: pointer;
  }

  th[colspan="2"] {
    text-align: center;
  }

  td {
    &:hover {
      opacity: 0.5;
    }

    &:nth-child(odd) {
      border-left: none;
    }

    &:nth-child(even) {
      border-right: none;
    }
  }
}

</style>
