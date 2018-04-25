<template>
  <div>
    <div>
      <ul class="menu-list">
        <li class="m-li" v-for="system in systemOrder">
          <span v-if="selectedSystem == system"
          class="li-selected"
          @click="selectSystem(system)">
           &#9662;&nbsp;{{ system }}
          </span>
          <span v-else @click="selectSystem(system)">
            &#9656;&nbsp;{{ system }}
          </span>
          <ul class="subs-ul" v-show="selectedSystem === system">
            <li v-for="subsystem in subsystems[system]"
              v-if="system !== 'Collection of reactions'">
              <span v-if="selectedSubsystem === subsystem"
              class="li-selected"@click="selectedSubsystem=subsystem">
               &#9642;&nbsp;{{ subsystem.name }}
               </span>
              <span v-else @click="selectedSubsystem=subsystem">
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
    <div v-if="selectedSubsystem">
      <hr>
      <table class="table">
      <tr>
        <td>
          <a @click="exploreSubsystem()">{{ selectedSubsystem.name }}</a>
        </td>
        <td>
          <span class="tag" @click="showSubsystem()">View</span>
        </td>
      </tr>
      </table>
      <ul class="menu-list">
        <li class="menu-label">
          # reactions: {{ selectedSubsystem['nr_reactions'] }}
        </li>
        <li class="menu-label">
          # metabolites: {{ selectedSubsystem['nr_metabolites'] }}
        </li>
        <li class="menu-label">
          # enzymes: {{ selectedSubsystem['nr_enzymes'] }}
        </li>
        <li class="menu-label">
          # compartments: {{ selectedSubsystem['nr_compartments'] }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script>

import axios from 'axios';
import EventBus from '../../event-bus';

export default {
  name: 'subsystem',
  props: ['model', 'subsystemName'],
  data() {
    return {
      subsystems: {},
      subsystemsDict: {},
      subsystemsSystem: {}, // to get the system from the subsystem
      selectedSystem: '',
      selectedSubsystem: '',
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
  watch: {
    subsystemName(newVal, oldVal) { // eslint-disable-line no-unused-vars
      console.log(this.subsystemName);
      console.log(this.subsystemsSystem);
      if (this.subsystemName in this.subsystemsSystem) {
        this.selectedSystem = this.subsystemsSystem[this.subsystemName];
        this.selectedSubsystem = this.subsystemsDict[this.subsystemName];
        const s = `${this.selectedSystem} - ${this.selectedSubsystem.nr_metabolites} Metabolites; ${this.selectedSubsystem.nr_enzymes} Enzymes; ${this.selectedSubsystem.nr_reactions} Reactions; ${this.selectedSubsystem.nr_compartments} Compartments`;
        this.$emit('showMapInfo', s);
      } else {
        this.selectedSystem = '';
      }
    },
  },
  created() {
    /* eslint-disable no-param-reassign */
    EventBus.$on('showSubsystem', (name) => {
      if (!name) {
        const subname = 'Tricarboxylic acid cycle and glyoxylate/dicarboxylate metabolism';
        this.selectedSystem = 'Other metabolism';
        this.selectedSubsystem = this.subsystems[subname];
        this.loadSubsystemCoordinates(subname, null);
      } else {
        this.loadSubsystemCoordinates(name, null);
      }
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
              this.subsystemsDict[s.name] = s;
              this.subsystemsSystem[s.name] = k;
            }
          }
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
    loadSubsystemCoordinates(subsystemName, compName) {
      let url = `${this.model}/subsystem_coord/${subsystemName}`;
      if (compName) {
        url = `${this.model}/subsystem_coord/${subsystemName}/${compName}`;
      }
      console.log(url);
      axios.get(url)
        .then((response) => {
          const subCoors = response.data;
          const coors = {
            minX: subCoors.x_top_left,
            maxX: subCoors.x_bottom_right,
            minY: subCoors.y_top_left,
            maxY: subCoors.y_bottom_right,
          };
          EventBus.$emit('requestViewer', 'subsystem', subCoors.compartment_name, subsystemName, coors);
        })
        .catch((error) => {
          console.log(error);
        }
      );
    },
    selectSystem(system) {
      if (this.selectedSystem === system) {
        this.selectedSystem = '';
      } else {
        this.selectedSystem = system;
      }
    },
    exploreSubsystem() {
      EventBus.$emit('updateSelTab', 'subsystem', this.selectedSubsystem.id);
    },
    showSubsystem() {
      if (this.selectedSystem !== 'Collection of reactions') {
        EventBus.$emit('showSubsystem', this.selectedSubsystem.name);
      }
    },
  },
};
</script>

<style lang="scss" scoped>

li {
  font-size: 13;
}

li.m-li {
  cursor: pointer;
  .disable {
    color: gray;
  }
}

span.tag {
  cursor: pointer;
}

ul.subs-ul {
  overflow-x: hidden;
  overflow-y: auto;
  max-height: 15rem;
}

.menu-list li ul {
  margin: 0.75em 0;
}

.li-selected {
  color: #64CC9A;
}
</style>
