function bindClickEvent() {
  const el = document.querySelector('.topbar-wrapper');
  if (el) {
    el.onclick = () => {
      location.href = '/';
    };
    let b = document.querySelector('body');
    const f = document.createElement('footer');
    b.appendChild(f);
    f.outerHTML = '<footer id="footer" class="footer has-background-primary-lighter is-size-6 py-4"><div class="columns is-gapless"><div class="column is-7-desktop is-5-tablet has-text-centered-mobile"><p>2020 © <span class="is-hidden-tablet-only"> &nbsp;Department of Biology and Biological Engineering | </span> &nbsp;Chalmers University of Technology</p></div><div class="column"><div class="content has-text-right has-text-centered-mobile is-size-2-mobile"><p><a href="https://www.sysbio.se" title="SysBio"><img src="/img/sysbio-logo.png" class="my-0 mx-2"></a><a href="http://www.chalmers.se" title="Chalmers University of Technology"><img src="/img/chalmers.png" class="my-0 mx-2"></a><a href="https://kaw.wallenberg.org/" title="Knut and Alice Wallenberg Foundation"><img src="/img/wallenberg.gif" class="my-0 mx-2"></a><a href="https://www.kth.se/en/bio/centres/wcpr" title="CBH | KTH Royal Institute of Technology"><img src="/img/wpcr.jpg" class="my-0 mx-2"></a><a href="https://nbis.se/"><img src="/img/nbislogo-green.png" title="National Bioinformatics Infrastructure Sweden" class="my-0 mx-2"></a><a href="https://www.scilifelab.se" title="Science for Life Laboratory (SciLifeLab)"><img src="/img/scilifelab.png" class="my-0 mx-2"></a></p></div></div></div></footer>';
  } else {
    setTimeout(bindClickEvent, 100);
  }
}

bindClickEvent();
