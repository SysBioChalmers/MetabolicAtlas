export default function (link, inNewTab) {
  const a = document.createElement('a');
  a.href = link;
  if (inNewTab) {
    a.target = '_blank';
  }
  a.style.display = 'none';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
