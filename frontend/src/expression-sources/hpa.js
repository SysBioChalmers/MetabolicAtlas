/* eslint-disable */

import axios from 'axios';
import { parseXML, unzipXML } from '../helpers/xml-tools';

const notDetectedColor = 'whitesmoke';
const overExpressedColor = 'darkred';
const rnaExpressionLvl = [
  [1, 'lightgray'],
  [4, 'yellow'],
  [5.5, 'orange'],
  [6.6, 'red'],
];

export function getExpressionColor(value) {
  for (const el of rnaExpressionLvl) {
    if (value <= el[0]) {
      return el[1];
    }
  }
  return overExpressedColor;
}
// getExpressionColor(0);

export function getExpLvlLegend() {
  let l = '<div id="HPARNAexpLegend" class="box"><div><h5 class="title is-6 has-text-centered">HPA RNA expression level - log2(tpm) </h5></div>';
  const w = 150.0/(rnaExpressionLvl.length + (overExpressedColor ? 1 : 0));
  l += '<div class="has-text-centered">';
  l += '<ul class="exp-lvl-legend">'
  if (notDetectedColor) {
    l += `<li><span style="background: ${notDetectedColor}"></span> NA</li>`;
  }
  let lv;
  for (const el of rnaExpressionLvl) {
    lv = el[0];
    l += `<li><span style="background: ${el[1]}"></span> <=${el[0]}</li>`;
  }
  if (overExpressedColor) {
    l += `<li><span style="background: ${overExpressedColor}"></span> >${lv}</li>`;
  }
  l += '</ul></div></div>';
  return l;
}
