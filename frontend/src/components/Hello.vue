<template>
  <div class="hello">
    <h1>{{ msg }}</h1>
    <button v-on:click="load">Load something</button>
    <div id="poll" v-if="loaded">
      <div v-for="poll in polls">
        <h2>{{ poll.question }}</h2>
        <ol>
          <li v-for="choice in poll.choices">
            {{ choice.choice }} ({{ choice.votes }})
          </li>
        </ol>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'hello',
  data() {
    return {
      loaded: false,
      polls: [],
      errorMessage: '',
      msg: 'Welcome to Your Vue.js App',
    };
  },
  methods: {
    load() {
      const endpoint = 'https://private-51ed0a-e0.apiary-mock.com/questions';

      axios.get(endpoint)
        .then((response) => {
          this.loaded = true;
          this.errorMessage = '';
          this.polls = response.data;
        })
        .catch((error) => {
          this.loaded = true;
          this.errorMessage = error.message;
          this.polls = [];
        });
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#poll {
  text-align: left;
  margin: 0 auto;
  width: 420px;
}

h1, h2 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: block;
  margin: 0 10px;
}

a {
  color: #42b983;
}
</style>
