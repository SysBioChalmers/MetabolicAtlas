/* eslint-disable */

import pako from 'pako';

export function unzipXML(filestream) {
  const blocks = inflateConcatenatedGzip(filestream);
  const xmlContent = mergeBlocks(blocks);
  return xmlContent;
}

export function fetchXML(url) {
  const filestream = loadBinaryResource(url);
  const xmlContent = unzipXML(filestream);
  return xmlContent;
}

export function parseXML(s) {
  if (typeof window.DOMParser !== 'undefined') {
    const parser = new window.DOMParser();
    return parser.parseFromString(s, 'text/xml');
  } else if (typeof window.ActiveXObject !== 'undefined' && new window.ActiveXObject('Microsoft.XMLDOM')) {
    const xmlDoc = new window.ActiveXObject('Microsoft.XMLDOM');
    xmlDoc.async = 'false';
    xmlDoc.loadXML(s);
    return xmlDoc;
  }
  throw new Error('No XML parser found');
}

//
// private functions
//
function loadBinaryResource(url) {
  const req = new XMLHttpRequest();
  req.open('GET', url, false);
  req.overrideMimeType('text/plain; charset=x-user-defined');
  req.send(null);
  if (req.status !== 200) {
    return '';
  }
  return req.responseText;
}

function inflateConcatenatedGzip(buffer) {
  var position = 0;
  var blocks = [];
  do {
    var inflator = new pako.Inflate();
    inflator.push(buffer.slice(position));
    if (inflator.err) { throw inflator.msg; }
    blocks.push(inflator.result);
    position += inflator.strm.total_in;
  } while (inflator.strm.avail_in > 0);
  return blocks;
}

function arrayBufferToString(buffer){
  var bufView = new Uint16Array(buffer);
  var length = bufView.length;
  var result = '';
  var addition = Math.pow(2,16)-1;

  for(var i = 0;i<length;i+=addition){
    if(i + addition > length){
        addition = length - i;
    }
    result += String.fromCharCode.apply(null, bufView.subarray(i,i+addition));
  }
  return result;
}

function mergeBlocks(blocks) {
  const stringBlocks = blocks.map(b => arrayBufferToString(b));
  return stringBlocks.join('');
}

