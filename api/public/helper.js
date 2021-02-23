function bindClickEvent() {
  const el = document.querySelector('.topbar-wrapper');
  if (el) {
    el.onclick = () => {
      location.href = '/';
    };
    let b = document.querySelector('body');
  } else {
    setTimeout(bindClickEvent, 100);
  }
}

bindClickEvent();
