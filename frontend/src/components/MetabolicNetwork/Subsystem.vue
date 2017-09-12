<template>
  <div>
    <p class="menu-label">Subsystem:</p>
    <ul class="menu-list">
      <li class="m-li" v-for="system in systemOrder">
        <span v-if="selectedSystem==system" 
        class="li-selected"@click="selectedSystem=system">
         &#9662; {{ system }}</span>
        <span v-else @click="selectedSystem=system"
        > &#9656; {{ system }}</span>
        <ul v-show="selectedSystem==system">
          <li v-for="subsystem in subsystems[system]"
          @click="showSubsystem(subsystem.id)">
              <span v-if="selectedSubSystem==subsystem.name" 
              class="li-selected"@click="selectedSubSystem=subsystem.name">
               &#9642; {{ subsystem.name }}</span>
              <span v-else @click="selectedSubSystem=subsystem.name">
                &#9642; {{ subsystem.name }}
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
  beforeMount() {
    EventBus.$on('showSubsystem', (id) => {
      if (!id) {
        console.log('test');
        // this.selectedSystem = 'Other metabolism';
        // this.selectedSubSystem = 'Tricarboxylic acid cycle and
        //  glyoxylate/dicarboxylate metabolism';
        // subID = 38;
      } else {
        this.loadSubsystemCoordinates(id);
      }
    });
    EventBus.$on('resetView', () => {
      this.selectedSystem = '';
      this.selectedSubSystem = '';
    });
    this.loadSubsystem();
    // EventBus.$emit('showSubsystem', 0);
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
          this.subsystems = systems;
          this.subsystemsSystem = {};
          this.subsystemCount = 0;
          for (const k of Object.keys(systems)) {
            this.subsystemCount += systems[k].length;
            for (const s of systems[k]) {
              this.subsystemsSystem[k] = s;
            }
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
    loadSubsystemCoordinates(id) {
      axios.get(`subsystem/${id}`)
        .then((response) => {
          console.log(response);
          const subCoors = response.data;
          const coors = {
            minX: subCoors.x_top_left,
            maxX: subCoors.x_bottom_right,
            minY: subCoors.y_top_left,
            maxY: subCoors.y_bottom_right,
          };
          EventBus.$emit('showSVGmap', 'tiles', subCoors.compartment_name, coors);
        })
        .catch((error) => {
          console.log(error);
        }
      );
    },
    showSubsystem(id) {
      if (!id) {
        this.loadSubsystemCoordinates(38);
      } else {
        this.loadSubsystemCoordinates(id);
      }
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
