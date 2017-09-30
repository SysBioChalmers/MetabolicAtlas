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

function getExpressionColor(value) {
  for (const el of rnaExpressionLvl) {
    if (value <= el[0]) {
      return el[1];
    }
  }
  return overExpressedColor;
}
getExpressionColor(0);

export function getExpLvlLegend() {
  let l = '<div class="box"><div><h5 class="title is-6 has-text-centered">HPA RNA expression level - log2(tpm) </h5></div>';
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

export default function(rawElms, xmlContent, unzip) {
  if (unzip) {
    // TODO fix the unzip in the front end, now its done in the backend
    // commit 0514b007c945534db6168a4dc731e282ce97f545 contains a working code
    // but without backend request
    xmlContent = unzipXML(xmlContent)
  }

  if (xmlContent === '') {
    return [];
  }

  const xmlDoc = parseXML(xmlContent);
  console.log(xmlDoc);
  const genes = xmlDoc.getElementsByTagName('entry');
  const hpaGeneEx = {};
  let hpaRnaTissues = {};
  let hpaRnaCellLines = {};
  for (const gene of genes) {
    const genename = gene.getElementsByTagName('name')[0].textContent;
    hpaGeneEx[genename] = [];
    const samples = gene.getElementsByTagName('rnaExpression')[0].getElementsByTagName('data');
    // Loop through rnaExpression children 'samples'
    for (let i = 0; i < samples.length; i += 1) {
      let sampleType;
      let sampleName;
      let replicates = [];
      // Collect log2(tpm) expression values and sample name of one sample
      for (const sampleEl of samples[i].children) {
        if (sampleEl.tagName === 'level') {
          if (sampleEl.textContent !== 'Not detected') {
            if (sampleType === 'cellLine') {
              hpaRnaCellLines[sampleName] = null;
            } else if (sampleType === 'tissue') {
              hpaRnaTissues[sampleName] = null;
            }
            replicates.push(Math.log2(sampleEl.getAttribute('tpm') + 1));
          }
        } else {
          sampleName = sampleEl.textContent;
          // sampleType is cell line or tissue AFAIK
          sampleType = sampleEl.tagName;
        }
      }
      // Now take median in case of replicates
      replicates = replicates.sort((a, b) => a - b);
      const middle = Math.floor(replicates.length / 2);
      const geneExpression = { name: sampleName, type: sampleType };
      if (!replicates.length) {
        geneExpression.value = null;
        geneExpression.color = notDetectedColor;
      } else if (replicates.length % 2 === 0) {
        geneExpression.value = (replicates[middle] + replicates[middle - 1]) / 2;
      } else {
        geneExpression.value = replicates[middle];
      }
      if (geneExpression.value) {
        geneExpression.color = getExpressionColor(geneExpression.value);
      }
      hpaGeneEx[genename].push(geneExpression);
    }
  }

  hpaRnaTissues = Object.keys(hpaRnaTissues).sort();
  hpaRnaCellLines = Object.keys(hpaRnaCellLines).sort();

  const rawElms2 = rawElms;

  for (const elid of Object.keys(rawElms2)) {
    // expressionElms[elid] = rawElms[elid];
    if (!rawElms2[elid].expressionLvl) {
      rawElms2[elid].expressionLvl = {};
    }
    if (!rawElms2[elid].expressionLvl.HPA) {
      rawElms2[elid].expressionLvl.HPA = {};
    }
    rawElms2[elid].expressionLvl.HPA.RNA = {};
    const HPARNAexp = rawElms2[elid].expressionLvl.HPA.RNA;
    if (hpaGeneEx[rawElms[elid].short]) {
      for (const tissue of hpaGeneEx[rawElms[elid].short]) {
        HPARNAexp[tissue.name] = tissue.color;
      }
    }
  }
  return {
    graphElements: rawElms2,
    tissues: hpaRnaTissues,
    cellLines: hpaRnaCellLines,
  };
}
