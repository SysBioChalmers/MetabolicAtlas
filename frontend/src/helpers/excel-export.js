import { default as XLSX } from 'xlsx';
import { default as FileSaver } from 'file-saver';

const s2ab = (s) => {
  /* eslint no-plusplus: ["error", { "allowForLoopAfterthoughts": true }] */
  /* eslint no-bitwise: ["error", { "allow": ["&"] }] */
  if (typeof ArrayBuffer !== 'undefined') {
    const buf = new ArrayBuffer(s.length);
    const view = new Uint8Array(buf);
    for (let i = 0; i !== s.length; ++i) {
      view[i] = s.charCodeAt(i) & 0xFF;
    }
    return buf;
  }

  const buf = new Array(s.length);
  for (let i = 0; i !== s.length; ++i) {
    buf[i] = s.charCodeAt(i) & 0xFF;
  }
  return buf;
};

export default (table, filename) => {
  const workbook = XLSX.utils.table_to_book(table, {
    sheet: 'haha',
  });

  const workbookOut = XLSX.write(workbook, {
    bookType: 'xlsx',
    bookSST: true,
    type: 'binary',
  });

  const blob = new Blob([s2ab(workbookOut)], {
    type: 'application/octet-stream',
  });

  FileSaver.saveAs(blob, filename);
};
