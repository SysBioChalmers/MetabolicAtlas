<template>
  <div>
    <p class="menu-label">Subsystem:</p>
    <ul class="menu-list">
      <li class="m-li" v-for="system in systemOrder">
        <span v-if="selectedSystem == system"
        class="li-selected"
        @click="selectSubsystem(system)">
         &#9662;&nbsp;{{ system }}
        </span>
        <span v-else @click="selectSubsystem(system)">
          &#9656;&nbsp;{{ system }}
        </span>
        <ul class="subs-ul" v-show="selectedSystem === system">
          <li v-for="subsystem in subsystems[system]"
          v-if="system !== 'Collection of reactions'"
          @click="showSubsystem(system, subsystem.id)">
              <span v-if="selectedSubSystem==subsystem.name"
              class="li-selected"@click="selectedSubSystem=subsystem.name">
               &#9642;&nbsp;{{ subsystem.name }}
               </span>
              <span v-else @click="selectedSubSystem=subsystem.name">
                &#9642;&nbsp;{{ subsystem.name }}
              </span>
          </li>
          <li v-else class="disable">
              <span>&#9642;&nbsp;{{ subsystem.name }}</span>
          </li>
        </ul>
      </li>
    </ul>
  </div>
</template>

<script>

import axios from 'axios';
import EventBus from '../../event-bus';

export default {
  name: 'subsystem',
  props: ['model'],
  data() {
    return {
      subsystems: {},
      subsystemsSystem: {}, // to get the system from the subsystem
      selectedSystem: '',
      selectedSubSystem: '',
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
  created() {
    /* eslint-disable no-param-reassign */
    EventBus.$on('showSubsystem', (id) => {
      if (!id) {
        this.selectedSystem = 'Other metabolism';
        this.selectedSubSystem = 'Tricarboxylic acid cycle and glyoxylate/dicarboxylate metabolism';
        id = 38;
        this.loadSubsystemCoordinates(id);
      } else {
        this.loadSubsystemCoordinates(id);
      }
    });
    EventBus.$on('resetView', () => {
      this.selectedSystem = '';
      this.selectedSubSystem = '';
    });
  },
  beforeMount() {
    this.loadSubsystem();
  },
  mounted() {
    // EventBus.$emit('showSubsystem', null);
  },
  methods: {
    loadSubsystem() {
      axios.get(`${this.model}/subsystems`)
        .then((response) => {
          const systems = response.data.reduce((subarray, el) => {
            const arr = subarray;
            if (!arr[el.system]) { arr[el.system] = []; }
            arr[el.system].push(el);
            return arr;
          }, {});
          this.subsystems = systems;
          this.subsystemsSystem = {};
          this.subsystemCount = 0;
          console.log(this.subsystems);
          for (const k of Object.keys(systems)) {
            this.subsystems[k] = this.subsystems[k].sort(
              (a, b) => {
                if (a.name > b.name) {
                  return 1;
                }
                return a.name < b.name ? -1 : 0;
              }
            );
            this.subsystemCount += systems[k].length;
            for (const s of systems[k]) {
              this.subsystemsSystem[k] = s;
            }
          }
          console.log(this.subsystems);
          // update the parent component
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
    loadSubsystemCoordinates(id) {
      axios.get(`${this.model}/subsystem/${id}`)
        .then((response) => {
          const subCoors = response.data;
          console.log(subCoors);
          const coors = {
            minX: subCoors.x_top_left,
            maxX: subCoors.x_bottom_right,
            minY: subCoors.y_top_left,
            maxY: subCoors.y_bottom_right,
          };
          EventBus.$emit('showSVGmap', 'subsystem', subCoors.compartmentsvg_id, coors);
        })
        .catch((error) => {
          console.log(error);
        }
      );
    },
    selectSubsystem(system) {
      if (this.selectedSystem === system) {
        this.selectedSystem = '';
      } else {
        this.selectedSystem = system;
      }
    },
    showSubsystem(system, id) {
      // forbid the display of this system
      if (system !== 'Collection of reactions') {
        if (!id) {
          this.loadSubsystemCoordinates(38);
        } else {
          this.loadSubsystemCoordinates(id);
        }
      }
    },
  },
};
</script>

<style lang="scss" scoped>

li.m-li {
  cursor: pointer;
  .disable {
    color: gray;
  }
}

ul.subs-ul {
  overflow-x: hidden;
  overflow-y: auto;
  max-height: 20rem;
}

.menu-list li ul {
  margin: 0.75em 0;
}

.li-selected {
  color: #64CC9A;
}
</style>
