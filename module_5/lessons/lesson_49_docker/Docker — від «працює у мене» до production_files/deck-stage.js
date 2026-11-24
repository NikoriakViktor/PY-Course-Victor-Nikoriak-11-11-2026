/*
 * deck-stage.js — невеликий рушій презентації для <deck-stage>.
 *
 * Розмітка:
 *   <deck-stage>
 *     <section class="slide"> … </section>      ← один слайд 1920×1080
 *   </deck-stage>
 *
 * Покрокова поява всередині слайда:
 *   data-step="2"   елемент з'являється на кроці 2 і лишається
 *   data-at="2"     елемент отримує клас .at лише НА кроці 2 (підсвітка)
 *   data-steps="5"  (на <section>) явна кількість кроків, якщо керує JS
 *
 * Події (спливають від <section>):
 *   deck-step  { index, step, max }  — щоразу, коли змінився слайд або крок
 *
 * Клавіші: → / пробіл — далі · ← — назад · ↓ ↑ — цілий слайд
 *          Home / End · O — огляд · F — на весь екран
 * Адреса:  #7 — слайд 7 · #7.3 — слайд 7, крок 3
 */
(function () {
  'use strict';

  var W = 1920, H = 1080;

  var CSS = [
    'html,body{height:100%;margin:0;overflow:hidden}',
    'deck-stage{position:fixed;inset:0;display:block;overflow:hidden;background:#000}',
    'deck-stage>section{position:absolute!important;left:50%;top:50%;margin:0;transform-origin:center;',
    '  transform:translate(-50%,-50%) scale(var(--deck-scale,1));',
    '  opacity:0;visibility:hidden;pointer-events:none;transition:opacity .3s ease,visibility 0s .3s}',
    'deck-stage>section.deck-active{opacity:1;visibility:visible;pointer-events:auto;transition:opacity .3s ease}',
    'deck-stage [data-step]{opacity:0;transform:translateY(16px);pointer-events:none;',
    '  transition:opacity .45s ease,transform .45s ease}',
    'deck-stage [data-step].on{opacity:1;transform:none;pointer-events:auto}',

    /* огляд усіх слайдів */
    'deck-stage.deck-overview{overflow:auto;background:#0b0d10}',
    'deck-stage.deck-overview>section{opacity:1;visibility:visible;pointer-events:auto;cursor:pointer;',
    '  transform-origin:0 0;transition:none;outline:0 solid transparent}',
    'deck-stage.deck-overview>section *{pointer-events:none!important}',
    'deck-stage.deck-overview>section.deck-active{outline:10px solid #6cc4e8}',
    'deck-stage.deck-overview [data-step]{opacity:1;transform:none}',

    /* службові елементи */
    '.deck-bar{position:fixed;left:0;bottom:0;height:3px;background:#6cc4e8;z-index:20;transition:width .3s ease}',
    '.deck-ui{position:fixed;right:12px;bottom:12px;z-index:21;display:flex;gap:6px;align-items:center;',
    '  font:13px/1 ui-monospace,Menlo,Consolas,monospace;color:#cfd6dd;opacity:0;transition:opacity .25s}',
    '.deck-ui.show{opacity:1}',
    '.deck-ui button{font:inherit;color:inherit;background:rgba(20,24,30,.9);border:1px solid #3a424c;',
    '  border-radius:8px;padding:8px 11px;cursor:pointer}',
    '.deck-ui button:hover{background:#2a323c}',
    '.deck-ui span{background:rgba(20,24,30,.9);border:1px solid #3a424c;border-radius:8px;padding:8px 11px}',

    '@media print{',
    '  @page{size:1920px 1080px;margin:0}',
    '  html,body{height:auto;overflow:visible}',
    '  deck-stage{position:static;overflow:visible}',
    '  deck-stage>section{position:relative!important;left:0;top:0;transform:none!important;opacity:1!important;',
    '    visibility:visible!important;break-after:page;page-break-after:always}',
    '  deck-stage [data-step]{opacity:1!important;transform:none!important}',
    '  .deck-bar,.deck-ui{display:none!important}',
    '}'
  ].join('\n');

  function pad(n) { return n < 10 ? '0' + n : '' + n; }

  class DeckStage extends HTMLElement {
    connectedCallback() {
      if (this._started) return;
      this._started = true;
      var self = this;
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () { self._setup(); });
      } else {
        this._setup();
      }
    }

    _setup() {
      var self = this;
      var style = document.createElement('style');
      style.textContent = CSS;
      document.head.appendChild(style);

      this.slides = Array.prototype.filter.call(this.children, function (el) {
        return el.tagName === 'SECTION';
      });
      this.index = -1;
      this.step = 0;
      this.overview = false;

      this.slides.forEach(function (s, i) {
        var max = Number(s.dataset.steps) || 0;
        s.querySelectorAll('[data-step],[data-at]').forEach(function (el) {
          max = Math.max(max, Number(el.dataset.step || el.dataset.at) || 0);
        });
        s._max = max;
        s.querySelectorAll('[data-slide-num]').forEach(function (el) {
          el.textContent = pad(i + 1) + ' / ' + pad(self.slides.length);
        });
        s.addEventListener('click', function () {
          if (self.overview) { self.toggleOverview(false); self.go(i, 0); }
        });
      });

      this._buildUi();
      window.addEventListener('resize', function () { self._fit(); });
      window.addEventListener('hashchange', function () { self._fromHash(); });
      document.addEventListener('keydown', function (e) { self._key(e); });
      this._touch();
      this._fit();
      if (!this._fromHash()) this.go(0, 0);
    }

    _buildUi() {
      var self = this;
      this.bar = document.createElement('div');
      this.bar.className = 'deck-bar';
      document.body.appendChild(this.bar);

      var ui = document.createElement('div');
      ui.className = 'deck-ui';
      function btn(label, title, fn) {
        var b = document.createElement('button');
        b.type = 'button'; b.textContent = label; b.title = title;
        b.addEventListener('click', function () { fn(); b.blur(); });
        ui.appendChild(b);
      }
      btn('‹', 'Назад (←)', function () { self.prev(); });
      this.counter = document.createElement('span');
      ui.appendChild(this.counter);
      btn('›', 'Далі (→ або пробіл)', function () { self.next(); });
      btn('▦', 'Огляд слайдів (O)', function () { self.toggleOverview(); });
      btn('⛶', 'На весь екран (F)', function () { self.fullscreen(); });
      document.body.appendChild(ui);
      this.ui = ui;

      var timer;
      document.addEventListener('mousemove', function () {
        ui.classList.add('show');
        clearTimeout(timer);
        timer = setTimeout(function () { ui.classList.remove('show'); }, 2500);
      });
    }

    _fit() {
      if (this.overview) { this._layoutOverview(); return; }
      var k = Math.min(window.innerWidth / W, window.innerHeight / H);
      this.style.setProperty('--deck-scale', k);
    }

    _layoutOverview() {
      var cols = Math.max(2, Math.min(5, Math.floor(window.innerWidth / 380)));
      var gap = 18;
      var k = (this.clientWidth - gap * (cols + 1)) / cols / W;
      this.slides.forEach(function (s, i) {
        s.style.left = gap + (i % cols) * (W * k + gap) + 'px';
        s.style.top = gap + Math.floor(i / cols) * (H * k + gap) + 'px';
        s.style.transform = 'scale(' + k + ')';
      });
    }

    toggleOverview(force) {
      this.overview = force === undefined ? !this.overview : force;
      this.classList.toggle('deck-overview', this.overview);
      if (this.overview) {
        this._layoutOverview();
        var cur = this.slides[this.index];
        if (cur) this.scrollTop = Math.max(0, cur.offsetTop - 60);
      } else {
        this.slides.forEach(function (s) { s.style.left = s.style.top = s.style.transform = ''; });
        this.scrollTop = 0;
        this._fit();
      }
    }

    fullscreen() {
      if (document.fullscreenElement) document.exitFullscreen();
      else if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen();
    }

    _fromHash() {
      var m = /^#(\d+)(?:\.(\d+))?$/.exec(location.hash);
      if (!m) return false;
      this.go(Number(m[1]) - 1, m[2] ? Number(m[2]) : 0);
      return true;
    }

    _key(e) {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      var t = e.target;
      var typing = t && /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName);
      var onButton = t && t.tagName === 'BUTTON';
      if (typing) return;
      var k = e.key;
      if (this.overview) {
        if (k === 'Escape' || k === 'o' || k === 'O' || k === 'щ' || k === 'Щ') this.toggleOverview(false);
        else if (k === 'ArrowRight') this._show(this.index + 1, 0);
        else if (k === 'ArrowLeft') this._show(this.index - 1, 0);
        else if (k === 'Enter') this.toggleOverview(false);
        else return;
        e.preventDefault();
        return;
      }
      if ((k === ' ' || k === 'Enter') && onButton) return;   // кнопка демо має спрацювати сама
      if (k === 'ArrowRight' || k === ' ' || k === 'PageDown' || k === 'Enter') this.next();
      else if (k === 'ArrowLeft' || k === 'PageUp' || k === 'Backspace') this.prev();
      else if (k === 'ArrowDown') this.go(this.index + 1, 0);
      else if (k === 'ArrowUp') this.go(this.index - 1, 0);
      else if (k === 'Home') this.go(0, 0);
      else if (k === 'End') this.go(this.slides.length - 1, 0);
      else if (k === 'f' || k === 'F' || k === 'а' || k === 'А') this.fullscreen();
      else if (k === 'o' || k === 'O' || k === 'щ' || k === 'Щ') this.toggleOverview();
      else return;
      e.preventDefault();
    }

    _touch() {
      var self = this, x0 = null, y0 = null;
      this.addEventListener('touchstart', function (e) {
        x0 = e.touches[0].clientX; y0 = e.touches[0].clientY;
      }, { passive: true });
      this.addEventListener('touchend', function (e) {
        if (x0 === null || self.overview) return;
        var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
        x0 = null;
        if (Math.abs(dx) < 60 || Math.abs(dx) < Math.abs(dy)) return;
        if (dx < 0) self.next(); else self.prev();
      }, { passive: true });
    }

    next() {
      var s = this.slides[this.index];
      if (s && this.step < s._max) this._show(this.index, this.step + 1);
      else if (this.index < this.slides.length - 1) this._show(this.index + 1, 0);
    }

    prev() {
      if (this.step > 0) this._show(this.index, this.step - 1);
      else if (this.index > 0) this._show(this.index - 1, this.slides[this.index - 1]._max);
    }

    go(i, step) { this._show(i, step || 0); }

    _show(i, step) {
      if (!this.slides.length) return;
      i = Math.max(0, Math.min(this.slides.length - 1, i));
      var s = this.slides[i];
      step = Math.max(0, Math.min(s._max, step));
      this.slides.forEach(function (el, n) { el.classList.toggle('deck-active', n === i); });
      this.index = i;
      this.step = step;

      s.querySelectorAll('[data-step]').forEach(function (el) {
        el.classList.toggle('on', Number(el.dataset.step) <= step);
      });
      s.querySelectorAll('[data-at]').forEach(function (el) {
        el.classList.toggle('at', Number(el.dataset.at) === step);
      });

      var total = this.slides.length;
      var done = (i + (s._max ? step / (s._max + 1) : 0)) / Math.max(1, total - 1);
      this.bar.style.width = Math.min(100, done * 100) + '%';
      this.counter.textContent = (i + 1) + ' / ' + total;

      var hash = '#' + (i + 1) + (step ? '.' + step : '');
      if (location.hash !== hash) {
        try { history.replaceState(null, '', hash); } catch (err) { /* file:// у деяких браузерах */ }
      }
      if (this.overview) {
        var top = s.offsetTop;
        if (top < this.scrollTop || top > this.scrollTop + this.clientHeight - 200) this.scrollTop = Math.max(0, top - 60);
      }
      s.dispatchEvent(new CustomEvent('deck-step', {
        bubbles: true,
        detail: { index: i, step: step, max: s._max }
      }));
    }
  }

  if (!customElements.get('deck-stage')) customElements.define('deck-stage', DeckStage);
})();
