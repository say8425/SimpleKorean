// 테마 버튼과 설치 명령 복사 버튼. 스크립트가 없어도 페이지는 시스템 테마로 읽힌다.
(function () {
  var root = document.documentElement;
  var button = document.getElementById('theme');
  var label = document.getElementById('theme-label');
  var names = { light: '라이트', dark: '다크', system: '시스템' };
  var next = { system: 'light', light: 'dark', dark: 'system' };

  function current() {
    var t = root.dataset.theme;
    return t === 'light' || t === 'dark' ? t : 'system';
  }
  function show(pref) {
    label.textContent = names[pref];
    button.setAttribute('aria-label', '화면 테마 바꾸기. 지금은 ' + names[pref]);
  }
  button.addEventListener('click', function () {
    var pref = next[current()];
    if (pref === 'system') delete root.dataset.theme;
    else root.dataset.theme = pref;
    try {
      if (pref === 'system') localStorage.removeItem('theme');
      else localStorage.setItem('theme', pref);
    } catch (e) {}
    show(pref);
  });
  show(current());

  var COPY = '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
  var DONE = '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>';
  var status = document.getElementById('copy-status');

  function fallback(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) {}
    ta.remove();
    return ok;
  }

  Array.prototype.forEach.call(document.querySelectorAll('.copy'), function (btn) {
    var text = btn.parentNode.querySelector('code').textContent;
    var timer;
    btn.innerHTML = COPY;
    btn.title = btn.getAttribute('aria-label');
    function done() {
      btn.innerHTML = DONE;
      btn.classList.add('done');
      status.textContent = '복사했습니다';
      clearTimeout(timer);
      timer = setTimeout(function () {
        btn.innerHTML = COPY;
        btn.classList.remove('done');
        status.textContent = '';
      }, 1600);
    }
    btn.addEventListener('click', function () {
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(done, function () { if (fallback(text)) done(); });
      } else if (fallback(text)) {
        done();
      }
    });
  });
})();
