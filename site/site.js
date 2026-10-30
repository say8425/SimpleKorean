// 테마 메뉴와 설치 명령 복사 버튼. 스크립트가 없으면 페이지는 시스템 테마로 보이고 테마 메뉴와 복사 버튼은 숨는다.
// 화면에 보이는 문구는 페이지의 HTML에 있다. 그래서 이 파일은 모든 언어 페이지가 함께 쓴다.
(function () {
  var KEY = 'simple-korean-theme';
  var BAR = { light: '#FBFAF6', dark: '#161513' };
  var root = document.documentElement;
  var button = document.getElementById('theme');
  var menu = document.getElementById('theme-menu');
  var label = document.getElementById('theme-label');
  var items = Array.prototype.slice.call(menu.querySelectorAll('[role="menuitemradio"]'));
  // 이 스크립트가 실행되어야 테마 메뉴를 보인다. 스크립트를 받지 못하면 누를 수 없는 버튼이 남지 않는다.
  root.classList.add('theme-ready');

  function current() {
    var t = root.dataset.theme;
    return t === 'light' || t === 'dark' ? t : 'system';
  }
  function itemFor(pref) {
    return items.filter(function (it) { return it.dataset.themeValue === pref; })[0];
  }
  function show(pref) {
    var name = itemFor(pref).querySelector('.name').textContent;
    label.textContent = name;
    button.setAttribute('aria-label', button.dataset.label + ' ' + name);
    items.forEach(function (it) { it.setAttribute('aria-checked', String(it.dataset.themeValue === pref)); });
  }
  // 브라우저 상단 막대 색도 고른 테마를 따른다. 시스템이면 메타 태그마다 원래 색으로 돌린다.
  function applyTheme(pref) {
    if (pref === 'system') delete root.dataset.theme;
    else root.dataset.theme = pref;
    Array.prototype.forEach.call(document.querySelectorAll('meta[name="theme-color"]'), function (m) {
      m.content = pref === 'system' ? m.getAttribute('data-system') : BAR[pref];
    });
    try {
      if (pref === 'system') localStorage.removeItem(KEY);
      else localStorage.setItem(KEY, pref);
    } catch (e) {}
    show(pref);
  }

  function isOpen() { return !menu.hidden; }
  function open(focusLast) {
    menu.hidden = false;
    button.setAttribute('aria-expanded', 'true');
    var target = focusLast ? items[items.length - 1] : itemFor(current());
    target.focus();
  }
  function close(returnFocus) {
    if (!isOpen()) return;
    menu.hidden = true;
    button.setAttribute('aria-expanded', 'false');
    if (returnFocus) button.focus();
  }

  button.addEventListener('click', function () {
    if (isOpen()) close(true);
    else open(false);
  });
  button.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      open(e.key === 'ArrowUp');
    }
  });
  items.forEach(function (it) {
    it.addEventListener('click', function () {
      applyTheme(it.dataset.themeValue);
      close(true);
    });
  });
  menu.addEventListener('keydown', function (e) {
    var i = items.indexOf(document.activeElement);
    var next = null;
    if (e.key === 'ArrowDown') next = items[(i + 1) % items.length];
    else if (e.key === 'ArrowUp') next = items[(i - 1 + items.length) % items.length];
    else if (e.key === 'Home') next = items[0];
    else if (e.key === 'End') next = items[items.length - 1];
    else if (e.key === 'Escape') { e.preventDefault(); close(true); return; }
    else if (e.key === 'Tab') { close(false); return; }
    if (next) { e.preventDefault(); next.focus(); }
  });
  // 화면 낭독기 커서처럼 Tab 말고 다른 방법으로 초점이 메뉴 밖으로 나가도 닫는다.
  menu.addEventListener('focusout', function (e) {
    var to = e.relatedTarget;
    if (to && !menu.contains(to) && to !== button) close(false);
  });
  document.addEventListener('click', function (e) {
    if (isOpen() && !menu.contains(e.target) && !button.contains(e.target)) close(false);
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
      announce(status.dataset.done);
      clearTimeout(timer);
      timer = setTimeout(function () { btn.classList.remove('done'); }, 1600);
    }
    function failed() {
      announce(status.dataset.fail);
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
