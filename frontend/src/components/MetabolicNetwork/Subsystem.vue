<template>
  <div>
    <p class="menu-label">Subsystem:</p>
    <ul class="menu-list">
      <li class="m-li" v-for="system in systemOrder">
        <span v-if="showSubsystem[system]" 
        class="li-selected"@click="toggleShowSubSystem(system)">
         &#9662; {{ system }}</span>
        <span v-else @click="toggleShowSubSystem(system)"
        > &#9656; {{ system }}</span>
        <ul v-show="showSubsystem[system]">
          <li  v-for="subsystem in subsystems[system]">
            &#9642; {{ subsystem.name }}
          </li>
        </ul>
      </li>
    </ul>
  </div>
</template>

<script>

import axios from 'axios';

export default {
  name: 'subsystem',
  data() {
    return {
      subsystems: {},
      showSubsystem: {},
      subsystemCount: 0,
      systemOrder: [
        'Amino Acid metabolism',
        'Fatty acid',
        'Carnitine shuttle',
        'Glycosphingolipid biosynthesis/metabolism',
        'Cholesterol biosynthesis',
        'Vitamin metabolism',
        'Other metabolism',
        'Other',
        'Collection of reactions',
      ],
    };
  },
  beforeMount() {
    this.loadSubsystem();
  },
  methods: {
    loadSubsystem() {
      axios.get('subsystems')
        .then((response) => {
          console.log(response);
          const systems = response.data.reduce((subarray, el) => {
            const arr = subarray;
            if (!arr[el.system]) { arr[el.system] = []; }
            arr[el.system].push(el);
            return arr;
          }, {});
          console.log(systems);
          this.subsystems = systems;
          this.subsystemCount = 0;
          for (const k of Object.keys(systems)) {
            this.showSubsystem[k] = false;
            this.subsystemCount += systems[k].length;
          }
          this.$emit('sendSubSysCount', this.subsystemCount);
        })
        .catch((error) => {
          console.log(error);
          this.loading = false;
          switch (error.response.status) {
            default:
              this.errorMessage = this.$t('unknownError');
          }
        });
    },
    toggleShowSubSystem(system) {
      const newShowSubsystem = {};
      for (const k of Object.keys(this.subsystems)) {
        newShowSubsystem[k] = false;
      }

      if (!this.showSubsystem[system]) {
        newShowSubsystem[system] = true;
      }
      this.showSubsystem = newShowSubsystem;
    },
  },
};
</script>

<style lang="scss" scoped>

li.m-li {
  cursor: pointer;
}

.li-selected {
  color: #64CC9A;
}
</style>
