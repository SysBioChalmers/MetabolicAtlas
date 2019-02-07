<template>
  <section class="section extended-section">
    <div class="container">
      <span class="title">Genome-Scale Metabolic Models - FTP access</span>
      <br><br>
      <div>
        <h4 class="is-4 title">Downloading from a web browser</h4>
        Model files can be downloaded from <a href="http://ftp.icsb.chalmers.se">ftp.icsb.chalmers.se</a>
        <br><br>
        <h4 class="is-4 title">Downloading from a FTP client</h4>
        Connect to the FTP using your favorite FTP client (e.g. <a href="https://filezilla-project.org/">FileZilla</a>)
        <br><br>
        <span class="has-text-weight-bold lab">Host:</span> ftp.icsb.chalmers.se<br>
        <span class="has-text-weight-bold lab">Login:</span> (leave it empty)<br>
        <span class="has-text-weight-bold lab">Password:</span> (leave it empty)<br>
        <span class="has-text-weight-bold lab">Port:</span> 21
      </div>
    </div>
  </section>
</template>


<script>
export default {
  name: 'gemsDL',
  data() {
    return {
    };
  },
  methods: {
  },
};

</script>

<style lang="scss">
span.lab {
  width: 80px;
  display: inline-block;
}
</style>
