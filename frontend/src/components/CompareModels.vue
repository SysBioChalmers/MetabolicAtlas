<template>
  <div>
    <div class="container">
      <p>
        <h2>Comparing two models</h2>
        <table border=1>
          <tr><td width=25>A</td><td>INITModel: Automatically generated model for RNA - HEK 293</td><td>5274 reactions</td></tr>
          <tr><td>B</td><td>Hepatocytes2322: Genome-scale metabolic model for hepatocytes, iHepatocytes2322</td><td>7930 reactions</td></tr>
        </table>
      </p>
      </br>
      <p>
        <h2>Differences found:</h2>
        4619 complete shared reactions [86% shared of As reaction set] [59% shared of Bs reaction set]</br>
        44 reactions only in A and 2700 reactions only in B</br>
        In addition another 611 reactions are the same, but different modifiers are 'indicated' in the two models.</br>
      </p>
      </br>
      <p>
        <table><tr><td>
        <h2>The most affected subsystems - As based on missing reactions</h2>
        <ul>
          <li><a href=''>Transport, extracellular</a> (616 reactions: 608 from A and 8 from B)</li>
          <li><a href=''>Transport, mitochondrial</a> (127 reactions: 127 from A)</li>
          <li><a href=''>Bile acid biosynthesis </a>(102 reactions: 102 from A)</li>
          <li><a href=''>Phenylalanine, tyrosine and tryptophan biosynthesis</a> (92 reactions: 92 from A)</li>
          <li><a href=''>Carnitine shuttle (endoplasmic reticular)</a> (56 reactions: 56 from A)</li>
          <li><a href="">...see more</a></li>
        </ul>
        </td><td>
        <h2>The most affected subsystems - As based on gene expression</h2>
        <ul>
          <li><a href=''>Transport, extracellular</a> (887 reactions)</li>
          <li><a href=''>Transport, mitochondrial</a> (146 reactions)</li>
          <li><a href=''>Leukotriene metabolism</a> (136 reactions)</li>
          <li><a href=''>Carnitine shuttle (mitochondrial)</a> (107 reactions)</li>
          <li><a href=''>Glycerolipid metabolism</a> (74 reactions)</li>          
          <li><a href="">...see more</a></li>
        </ul>
        </td></tr></table>
        <font color='orange'>Each of the names should be a link -> show on the SVG</font>
      </p>
      <p>
        <h2>The most affected compartments - As based on missing reactions</h2>
        <ul>
          <li>Cytosol (1692 reactions: 1676 from A and 16 from B)</li>
          <li>Extracellular (372 reactions: 359 from A and 13 from B)</li>
          <li><a href="">...see more</a></li>
        </ul>
      </p>
      </br>
      <font color='orange'>The below table should show all (?) affected reactions,
      so it has to be possible to filter the table!</font>
      <p>
        <h2>The 3355 affected Reactions:</h2>
        <table>
          <tr><th>ReactionID</th><th>Subsystem</th><th>Compartment</th><th>A</th><th>B</th><th>Show on map</td></tr>
          <tr><td>R_HMR_3905</td><td>Glycolysis / Gluconeogenesis</td><td>Cytosol</td>
            <td><a href="">E_1357</a>, <a href="">E_1981</a>, <a href="">E_2141</a></td>
            <td><a href="">E_1340</a>, <a href="">E_1871</a>, <a href="">E_1978</a>,
              <a href="">E_2090</a>, <a href="">E_2109</a>, <a href="">E_2119</a>,
              <a href="">E_2151</a>, <a href="">E_2158</a>, <a href="">E_2309</a></td>
            <td><input type="radio"></tr>
          <tr><td>R_HMR_8585</td><td>Starch and sucrose metabolism</td><td>Cytosol</td><td>Yes</td><td>No</td></tr>
          <tr><td>R_HMR_8570</td><td>Starch and sucrose metabolism</td><td>Cytosol</td><td>No</td><td>Yes</td></tr>
        </table>
        <font color='orange'>Clicking on the radio button should instantly load the corresponding....</font>
      </p>
      </br>
      <font color='orange'>Do we want to do some sort of GO overrepresentation analysis of the
        enzymes that are found in A but not B (and vice verse)?</font>
    </div>
  </div>
</template>

<script>

export default {
  name: 'about',
};
</script>

<style lang="scss">

.text {
  padding-left: 0.75em;
}

</style>
