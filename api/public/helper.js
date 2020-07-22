let eventBound = false;

function sleep (ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function bindClickEvent() {
  const el = document.querySelector('.topbar img');

  if (el) {
    el.onclick = () => {
      location.href = '/';
    };
    eventBound = true;
  } else {
    sleep(50).then(bindClickEvent);
  }
}


bindClickEvent();
