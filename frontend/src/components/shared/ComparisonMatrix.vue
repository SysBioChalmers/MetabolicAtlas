<template>
  <div v-if="mergedComparisons" class="table-container">
    <table class="table">
      <thead>
        <tr>
          <th></th>
          <th v-for="cn in columnNames" :key="cn">{{ cn }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(rn, i) in rowNames" :key="rn + i">
          <th>{{ rn }}</th>
          <td v-for="(cn, j) in columnNames" :key="cn + j" :class="{selected: isSelectedCell(i, j)}">
            <div>
              <span v-for="(type, k) in types" :key="cn + j + type"
                    :style="{backgroundColor: colors[k]}"
                    @click="handleSelectCell(i, j)">
                {{ matrix[i][j][type] }}
              </span>
            </div>
          </td>
        </tr>
      </tbody>
      <caption>
        click a cell to see the comparison details
        <br />
        legend:
        <span v-for="(type, k) of types" :key="type" :style="{backgroundColor: colors[k]}">
          {{ type }}
        </span>
      </caption>
    </table>
  </div>
</template>

<script>

import { mapState } from 'vuex';

export default {
  name: 'ComparisonMatrix',
  data() {
    return {
      colors: ['#eef6fc', '#fffbeb'],
    };
  },
  computed: {
    ...mapState({
      comparisons: state => state.compare.comparisons,
      modelList: state => state.models.modelList,
      selectedCell: state => state.compare.selectedCell,
    }),
    mergedComparisons() {
      // currently has support for two types
      if (this.comparisons && Object.keys(this.comparisons).length !== 2) {
        return null;
      }

      const [t1, t2] = this.types;
      return this.comparisons[t1].map((row, i) => Object.keys(row).reduce((mergedRow, key) => {
        const model = this.modelList.find(m => m.apiName === key);
        mergedRow[model.short_name] = { // eslint-disable-line no-param-reassign
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
        names.push('others');
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
  mounted() {
    this.handleSelectCell(1, 0); // default
  },
  methods: {
    isSelectedCell(r, c) {
      const { row, col } = this.selectedCell.position;
      return row === r && col === c;
    },
    handleSelectCell(row, col) {
      const selectedModels = [this.$route.query.models].flat().map((m) => {
        const [model, version] = m.split('-');
        return this.modelList.find(mo => mo.apiName === model && mo.version === version);
      });

      const model = selectedModels.find(m => m.short_name === this.columnNames[col]);
      let models;
      if (this.rowNames[row] === 'others') {
        models = selectedModels.filter(m => m.short_name !== this.columnNames[col]);
      } else {
        models = selectedModels.filter(m => m.short_name === this.rowNames[row]);
      }

      this.$store.dispatch('compare/setSelectedCell', {
        model: { model: model.apiName, version: model.apiVersion },
        models: models.map(m => ({ model: m.apiName, version: m.apiVersion })),
        position: { row, col },
      });
    },
  },
};

</script>

<style lang="scss" scoped>
table {
  caption-side: bottom;

  caption {
    font-size: 0.9em;
    font-style: italic;
    padding: 0.25em;

    span {
      padding: 0.25em;
    }
  }

  th {
    padding: 0.5em 0.75em;
    white-space: nowrap;
  }

  td {
    cursor: pointer;
    padding: 0;

    &.selected, &:hover {
      outline: 2px solid $black;
      outline-offset: -2px;
    }

    div {
      display: flex;

      span {
        padding: 0.5em 0.75em;
        width: 50%;
      }
    }
  }
}
</style>
