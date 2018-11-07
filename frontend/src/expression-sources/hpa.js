/* eslint-disable */

import axios from 'axios';
import { parseXML, unzipXML } from '../helpers/xml-tools';

const notDetectedColor = 'whitesmoke';
const overExpressedColor = '#ffe945';
const rnaExpressionLvl = [
  [1, 'lightgray'],
  [4, 'yellow'],
  [5.5, 'orange'],
  [6.6, 'red'],
];

export function getExpressionColor(value) {
  const v = parseInt(value * 28, 10);
  if (v >= cmap.length) {
    return overExpressedColor;
  }
  return cmap[v];
}
// getExpressionColor(0);

export function getExpLvlLegend() {
  let l = '<div id="HPARNAexpLegend" class="box"><div><h5 class="title is-6 has-text-centered">HPA RNA expression level - log2(tpm) </h5></div>';
  // const w = 150.0/(rnaExpressionLvl.length + (overExpressedColor ? 1 : 0));
  l += '<div class="has-text-centered">';
  if (notDetectedColor) {
    l += `<ul><li><span class="boxc" style="background: ${notDetectedColor};"></span><span>NA</span></li></ul>`;
    // l += `<li><span class="boxc" style="background: ${overExpressedColor};"></span><span>Over Expressed</span></li></ul>`;
  }
  l += '</div><div class="has-text-centered"><ul class="exp-lvl-legend">'
  let i = 0;
  l += '<li>0&nbsp;</li>';
  for (const el of cmap) {
    l += `<li><span style="background: ${el};`;
    if (i % 28 == 0 && i !== 0) {
      l += 'border-bottom: 5px solid black;"></span></li>';
    } else {
      l += '"></span></li>';
    }
    i += 1;
  }
  l += '<li>&nbsp;7+</li></ul></div></div>';
  return l;
}

const cmap = [
  '#00204c', '#00204e', '#002150',
  '#002353', '#002355', '#002456',
  '#00265a', '#00265b', '#00275d',
  '#002861', '#002963', '#002a64',
  '#002b68', '#002c6a', '#002d6c',
  '#002e6e', '#002e6f', '#002f6f',
  '#00306f', '#00316f', '#00316f',
  '#00336e', '#00346e', '#00346e',
  '#06366e', '#0a376d', '#0e376d',
  '#15396d', '#17396d', '#1a3a6c',
  '#1e3c6c', '#203c6c', '#223d6c',
  '#263e6c', '#273f6c', '#29406b',
  '#2c416b', '#2e426b', '#2f436b',
  '#32446b', '#33456b', '#35466b',
  '#37476b', '#38486b', '#3a496b',
  '#3c4a6b', '#3d4b6b', '#3e4b6b',
  '#414d6b', '#424e6b', '#434e6b',
  '#45506b', '#46506b', '#47516b',
  '#49536b', '#4a536b', '#4b546b',
  '#4d556b', '#4e566b', '#4f576c',
  '#51586c', '#52596c', '#535a6c',
  '#555b6c', '#565c6c', '#575d6d',
  '#595e6d', '#5a5f6d', '#5b5f6d',
  '#5d616e', '#5e626e', '#5f626e',
  '#60646e', '#61656f', '#62656f',
  '#64676f', '#65676f', '#666870',
  '#686a70', '#686a70', '#696b71',
  '#6b6d71', '#6c6d72', '#6d6e72',
  '#6f6f72', '#6f7073', '#707173',
  '#727274', '#737374', '#747475',
  '#757575', '#767676', '#777776',
  '#797877', '#7a7977', '#7b7a77',
  '#7c7b78', '#7d7c78', '#7e7d78',
  '#807e78', '#817f78', '#828078',
  '#848178', '#858278', '#868378',
  '#888578', '#898578', '#8a8678',
  '#8c8878', '#8d8878', '#8e8978',
  '#908b78', '#918c78', '#928c78',
  '#948e78', '#958f78', '#968f77',
  '#989177', '#999277', '#9a9377',
  '#9c9477', '#9d9577', '#9e9676',
  '#a09876', '#a19876', '#a29976',
  '#a49b75', '#a59c75', '#a69c75',
  '#a89e74', '#a99f74', '#aaa074',
  '#aca173', '#ada273', '#aea373',
  '#b0a572', '#b1a672', '#b2a672',
  '#b5a871', '#b6a971', '#b7aa70',
  '#b9ab70', '#baac6f', '#bbad6f',
  '#bdaf6e', '#beb06e', '#bfb16d',
  '#c1b26c', '#c2b36c', '#c3b46c',
  '#c6b66b', '#c7b76a', '#c8b86a',
  '#cab969', '#cbba68', '#ccbb68',
  '#cebd67', '#d0be66', '#d1bf66',
  '#d3c065', '#d4c164', '#d5c263',
  '#d7c462', '#d8c561', '#d9c661',
  '#dcc860', '#ddc95f', '#deca5e',
  '#e0cb5d', '#e1cc5c', '#e3cd5b',
  '#e5cf5a', '#e6d059', '#e7d158',
  '#e9d356', '#ebd456', '#ecd555',
  '#eed753', '#efd852', '#f0d951',
  '#f3db4f', '#f4dc4e', '#f5dd4d',
  '#f7df4b', '#f9e049', '#fae048',
  '#fce246', '#fde345', '#ffe443',
  '#ffe642', '#ffe743', '#ffe844',
  '#ffe945',
];
