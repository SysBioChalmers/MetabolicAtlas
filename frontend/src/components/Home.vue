<template>
  <section class="section extended-section">
    <div class="container" id="home">
      <div class="columns">
        <div class="column">
          <div class="card">
            <header class="card-header">
              <p class="card-header-title title">BIG BANNER HERE?</p>
            </header>
          </div>
        </div>
      </div>
      <div class="columns">
        <div class="column">
          <div class="card">
            <div class="columns is-mobile is-multiline is-gapless" id="panelslide">
              <div class="column is-full-mobile is-narrow has-background-primary has-text-weight-bold">
                <aside class="menu">
                  <ul class="menu-list is-size-5">
                    <li v-for="menuItem in menu">
                      <a @click="selectMenu(menuItem)" :class="[ {'is-active' : menuItem.title === currentMenu.title}, menuItem.type]">{{ menuItem.title}}</a>
                    </li>
                  </ul>
                </aside>
              </div>
              <div class="column is-full-mobile">
                <p class="is-size-5">{{ currentMenu.text }}</p>
              </div>
              <div class="column is-full-mobile">
                <div class="box">
                  <img :src="currentMenu.img" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="columns">
        <div class="column is-half" v-for="card in cards">
          <div class="card is-size-5">
            <header class="card-header has-background-primary has-text-white">
              <p class="card-content has-text-weight-bold">{{ card.title }}</p>
            </header>
            <div class="card-content">
              <p v-for="paragraph in card.text">{{ paragraph }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
/* eslint-disable global-require*/
export default {
  name: 'home',
  data() {
    return {
      menu: [
        { type: '',
          title: 'Welcome',
          text: 'Sint possimus est aut.',
          img: '' },
        { type: '',
          title: 'Explore integrated models',
          text: 'Et aliquid temporibus eveniet excepturi.',
          img: '' },
        { type: 'homepage-submenu',
          title: 'GEM Browser',
          text: 'Ducimus natus et facere ipsum voluptatem hic.',
          img: require('../assets/gemBrowser2.png') },
        { type: 'homepage-submenu',
          title: 'Map Viewer',
          text: 'Eaque quisquam fuga nihil velit alias similique quisquam eum.',
          img: require('../assets/mapViewer2.png') },
        { type: 'homepage-submenu',
          title: 'Search',
          text: 'Eius ab in ex perspiciatis quidem voluptas.',
          img: '' },
        { type: 'homepage-submenu',
          title: 'Export',
          text: '',
          img: '' },
        { type: '',
          title: 'Community GEMs',
          text: '',
          img: '' },
        { type: 'homepage-submenu',
          title: 'Compare',
          text: '',
          img: '' },
        { type: 'homepage-submenu',
          title: 'Analyze',
          text: '',
          img: '' },
        { type: 'homepage-submenu',
          title: 'Download',
          text: '',
          img: '' },
        { type: '',
          title: 'Resources',
          text: '',
          img: '',
        },
      ],
      currentMenu: {},
      cards: [
        { title: 'Latest news',
          text: [
            'Sint possimus est aut. Et aliquid temporibus eveniet excepturi. Ducimus natus et facere ipsum voluptatem hic. Eaque quisquam fuga nihil velit alias similique quisquam eum. Eius ab in ex perspiciatis quidem voluptas.',
            'Sint possimus est aut. Et aliquid temporibus eveniet excepturi. Ducimus natus et facere ipsum voluptatem hic. Eaque quisquam fuga nihil velit alias similique quisquam eum. Eius ab in ex perspiciatis quidem voluptas.'] },
        { title: 'Community',
          text: [
            'Sint possimus est aut. Et aliquid temporibus eveniet excepturi. Ducimus natus et facere ipsum voluptatem hic. Eaque quisquam fuga nihil velit alias similique quisquam eum. Eius ab in ex perspiciatis quidem voluptas.',
            'Sint possimus est aut. Et aliquid temporibus eveniet excepturi. Ducimus natus et facere ipsum voluptatem hic. Eaque quisquam fuga nihil velit alias similique quisquam eum. Eius ab in ex perspiciatis quidem voluptas.'] },
      ],
    };
  },
  beforeMount() {
    this.currentMenu = this.menu[0];
  },
  methods: {
    selectMenu(newMenu) {
      this.currentMenu = newMenu;
    },
  },
};

</script>
