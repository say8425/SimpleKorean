// 테마 버튼과 설치 명령 복사 버튼. 스크립트가 없으면 페이지는 시스템 테마로 보이고 복사 버튼은 숨는다.
(function () {
  var KEY = 'simple-korean-theme';
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
      if (pref === 'system') localStorage.removeItem(KEY);
      else localStorage.setItem(KEY, pref);
    } catch (e) {}
    show(pref);
  });
  show(current());

  var status = document.getElementById('copy-status');
  function announce(text) {
    // 같은 글을 다시 넣으면 화면 낭독기가 읽지 않는다. 그래서 비운 뒤에 넣는다.
    status.textContent = '';
    setTimeout(function () { status.textContent = text; }, 50);
  }
  function legacyCopy(text) {
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
    btn.hidden = false;
    btn.title = btn.getAttribute('aria-label');
    function done() {
      btn.classList.add('done');
      announce('복사했습니다');
      clearTimeout(timer);
      timer = setTimeout(function () { btn.classList.remove('done'); }, 1600);
    }
    function failed() {
      announce('복사하지 못했습니다. 명령을 직접 선택해 복사하세요');
    }
    btn.addEventListener('click', function () {
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(done, failed);
      } else if (legacyCopy(text)) {
        done();
      } else {
        failed();
      }
    });
  });
})();
