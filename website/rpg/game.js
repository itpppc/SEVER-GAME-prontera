/* ศึกลงกา (turn-based prototype): screen, input and animation. Rules live in engine.js. */
(function () {
  'use strict';
  const { Battle, HEROES, ENEMIES, STATUS, STAGE_1 } = window.LankaRPG;
  const $ = (id) => document.getElementById(id);
  const IMG = (slug) => '/assets/img/chars/' + slug + '.svg';
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const store = {
    get(k, d) { try { const v = localStorage.getItem('lanka-rpg:' + k); return v == null ? d : JSON.parse(v); } catch (_) { return d; } },
    set(k, v) { try { localStorage.setItem('lanka-rpg:' + k, JSON.stringify(v)); } catch (_) { /* private mode: settings just won't persist */ } },
  };

  const ui = {
    battle: null,
    speed: store.get('speed', 1) === 2 ? 2 : 1,
    auto: store.get('auto', false) === true,
    pick: null, // { unit, resolve } while waiting for the player's choice
    cards: new Map(),
  };

  const wait = (ms) => new Promise((r) => setTimeout(r, reduced ? Math.min(ms, 220) / ui.speed : ms / ui.speed));
  const nameOf = (key) => (HEROES[key] || ENEMIES[key]).name;

  /* ---------- rendering ---------- */

  function buildSide(el, units) {
    el.textContent = '';
    units.forEach((u) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'unit' + (u.boss ? ' boss' : '') + ' ' + u.side;
      b.disabled = true;
      b.dataset.uid = u.uid;
      b.innerHTML =
        (u.side === 'enemy' ? '<span class="intent" hidden></span>' : '') +
        '<span class="pic"><img src="' + IMG(u.img) + '" alt="" width="92" height="148" decoding="async"></span>' +
        '<span class="nm">' + u.name + '</span>' +
        '<span class="hp"><span class="hp-fill"></span></span>' +
        '<span class="hp-num"></span>' +
        '<span class="st"></span>';
      b.addEventListener('click', () => onTarget(u.uid));
      el.appendChild(b);
      ui.cards.set(u.uid, b);
    });
  }

  function renderAll() {
    const bt = ui.battle;
    bt.heroes.concat(bt.enemies).forEach((u) => {
      const c = ui.cards.get(u.uid);
      if (!c) return;
      const pct = Math.max(0, u.hp / u.maxHp * 100);
      const fill = c.querySelector('.hp-fill');
      fill.style.width = pct + '%';
      fill.classList.toggle('low', pct <= 30);
      c.querySelector('.hp-num').textContent = u.hp + ' / ' + u.maxHp;
      c.classList.toggle('ko', u.hp <= 0);
      c.querySelector('.st').innerHTML = Object.keys(u.status)
        .map((s) => '<span title="' + STATUS[s].label + '" class="' + (STATUS[s].bad ? 'bad' : 'good') + '">' + STATUS[s].icon + '<small>' + STATUS[s].label + '</small></span>').join('');
      const intent = c.querySelector('.intent');
      if (intent) {
        const mv = window.LankaRPG.MOVES[u.next];
        const show = u.hp > 0 && mv && mv.tell;
        intent.hidden = !show;
        if (show) intent.textContent = '⚠ เตรียม' + mv.name;
      }
      c.setAttribute('aria-label', u.name + ' พลังชีวิต ' + u.hp + ' จาก ' + u.maxHp +
        (u.hp <= 0 ? ' หมดแรงแล้ว' : '') + (intent && !intent.hidden ? ' ' + intent.textContent : ''));
    });
    $('round').textContent = 'ตา ' + Math.max(1, bt.round);
    const order = bt.upcoming(6);
    $('order').innerHTML = '<span class="order-lbl">คิวต่อไป</span>' + order.map((u) =>
      '<img class="' + u.side + '" src="' + IMG(u.img) + '" alt="' + u.name + '" width="28" height="44">').join('');
  }

  function setActive(u) {
    ui.cards.forEach((c) => c.classList.remove('active'));
    if (u) ui.cards.get(u.uid).classList.add('active');
  }

  function pulseField() {
    const f = $('field');
    f.classList.add('flash');
    setTimeout(() => f.classList.remove('flash'), 400);
  }

  function say(text) { $('log').textContent = text; }

  function float(uid, text, kind) {
    const c = ui.cards.get(uid);
    if (!c) return;
    const f = document.createElement('span');
    f.className = 'float ' + (kind || '');
    f.textContent = text;
    c.appendChild(f);
    const done = () => f.remove();
    f.addEventListener('animationend', done);
    setTimeout(done, 1600);
  }

  function pulse(uid, cls) {
    const c = ui.cards.get(uid);
    if (!c) return;
    c.classList.remove(cls);
    void c.offsetWidth; // restart the CSS animation
    c.classList.add(cls);
    setTimeout(() => c.classList.remove(cls), 600);
  }

  /* ---------- event playback ---------- */

  async function play(events) {
    const bt = ui.battle;
    for (const e of events) {
      const u = bt.find(e.who);
      if (e.t === 'act') {
        pulse(e.who, 'acting');
        say(u.name + ' ใช้ ' + e.name);
        if (e.big) pulseField();
        await wait(380);
      } else if (e.t === 'dmg') {
        pulse(e.who, 'hit');
        float(e.who, (e.crit ? 'คริ! ' : '-') + e.amount, e.crit ? 'crit' : 'dmg');
        renderAll();
        await wait(170);
      } else if (e.t === 'heal') {
        float(e.who, '+' + e.amount, 'heal');
        renderAll();
        await wait(120);
      } else if (e.t === 'status') {
        float(e.who, STATUS[e.s].icon + ' ' + STATUS[e.s].label, STATUS[e.s].bad ? 'bad' : 'good');
        renderAll();
        await wait(120);
      } else if (e.t === 'ko') {
        say(u.name + ' หมดแรง!');
        renderAll();
        await wait(380);
      } else if (e.t === 'rage') {
        float(e.who, '🔥 ตื่นเต็มตา!', 'crit');
        say(u.name + ' ตื่นเต็มตาแล้ว! โกรธจัด ตีแรงขึ้น');
        renderAll();
        await wait(600);
      } else if (e.t === 'skip') {
        pulse(e.who, 'hit');
        float(e.who, e.why === 'sleep' ? '💤 Zzz' : '💫 มึน', 'bad');
        say(e.why === 'sleep' ? u.name + ' เผลอหลับ! ข้ามตานี้' : u.name + ' ยังมึนอยู่ ข้ามตานี้');
        await wait(600);
      }
    }
    renderAll();
    await wait(200);
  }

  /* ---------- player input ---------- */

  function renderSkills(u) {
    const box = $('skills');
    box.textContent = '';
    u.skills.forEach((s, i) => {
      const ready = ui.battle.skillReady(u, s);
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'skill' + (i === 0 ? ' basic' : '');
      b.disabled = !ready || ui.auto;
      const left = u.cds[s.id] || 0; // own turns until the skill is back
      b.innerHTML = '<strong>' + s.name + '</strong><span>' + s.desc + '</span>' +
        (ready ? (s.cd ? '<em>พัก ' + s.cd + ' ตา</em>' : '<em>ใช้ได้ทุกตา</em>') : '<em class="cd">อีก ' + left + ' ตา</em>');
      b.addEventListener('click', () => onSkill(s));
      box.appendChild(b);
    });
  }

  function clearSkills() {
    $('skills').textContent = '';
  }

  function choose(u) {
    return new Promise((resolve) => {
      ui.pick = { unit: u, resolve, skill: null };
      $('prompt').textContent = 'ตาของ ' + u.name + ' เลือกท่า';
      renderSkills(u);
      const first = $('skills').querySelector('button:not(:disabled)');
      if (first) first.focus({ preventScroll: true });
    });
  }

  function finishPick(choice) {
    const p = ui.pick;
    if (!p) return;
    ui.pick = null;
    setTargeting(null);
    clearSkills();
    p.resolve(choice);
  }

  function onSkill(s) {
    const p = ui.pick;
    if (!p) return;
    if (s.target !== 'enemy' && s.target !== 'ally') return finishPick({ skill: s.id });
    const targets = ui.battle.validTargets(p.unit, s);
    if (targets.length === 1) return finishPick({ skill: s.id, target: targets[0].uid });
    p.skill = s;
    setTargeting(targets);
    $('prompt').textContent = s.name + ': แตะเลือกเป้าหมาย';
    $('skills').innerHTML = '<button type="button" class="skill cancel" id="btn-cancel"><strong>ยกเลิก</strong><span>เลือกท่าใหม่</span></button>';
    $('btn-cancel').addEventListener('click', cancelTarget);
    const t = ui.cards.get(targets[0].uid);
    if (t) t.focus({ preventScroll: true });
  }

  function cancelTarget() {
    const p = ui.pick;
    if (!p || !p.skill) return;
    p.skill = null;
    setTargeting(null);
    $('prompt').textContent = 'ตาของ ' + p.unit.name + ' เลือกท่า';
    renderSkills(p.unit);
  }

  function setTargeting(list) {
    const ids = new Set((list || []).map((u) => u.uid));
    ui.cards.forEach((c, uid) => {
      c.disabled = !ids.has(uid);
      c.classList.toggle('targetable', ids.has(uid));
    });
    $('field').classList.toggle('targeting', ids.size > 0);
  }

  function onTarget(uid) {
    const p = ui.pick;
    if (p && p.skill) finishPick({ skill: p.skill.id, target: uid });
  }

  /* ---------- dialogue ---------- */

  function talk(lines) {
    return new Promise((resolve) => {
      if (!lines || !lines.length) return resolve();
      const ov = $('talk');
      let i = 0;
      const show = () => {
        const l = lines[i];
        $('talk-face').src = IMG((HEROES[l.who] || ENEMIES[l.who]).img);
        $('talk-name').textContent = nameOf(l.who);
        $('talk-text').textContent = l.text;
        $('talk-next').textContent = i === lines.length - 1 ? 'สู้เลย! ⚔' : 'ต่อไป ▸';
      };
      const close = () => {
        ov.hidden = true;
        $('talk-next').removeEventListener('click', next);
        $('talk-skip').removeEventListener('click', close);
        document.removeEventListener('keydown', key);
        resolve();
      };
      const next = () => { i += 1; if (i >= lines.length) close(); else show(); };
      const key = (ev) => { if (ev.key === 'Escape') close(); };
      $('talk-next').addEventListener('click', next);
      $('talk-skip').addEventListener('click', close);
      document.addEventListener('keydown', key);
      show();
      ov.hidden = false;
      $('talk-next').focus();
    });
  }

  /* ---------- flow ---------- */

  async function banner(text) {
    const w = $('wave');
    w.textContent = text;
    w.classList.remove('show');
    void w.offsetWidth;
    w.classList.add('show');
    await wait(900);
  }

  async function fight() {
    const bt = ui.battle;
    while (!bt.over && !bt.waveCleared()) {
      const u = bt.nextActor();
      setActive(u);
      renderAll();
      const begin = bt.beginTurn(u);
      if (begin.skip) { await play(begin.ev); continue; }
      let ev;
      if (u.side === 'enemy') {
        $('prompt').textContent = 'ตาของ ' + u.name;
        clearSkills();
        await wait(450);
        ev = bt.enemyAct(u);
      } else {
        let c;
        if (ui.auto) {
          $('prompt').textContent = 'ออโต้: ' + u.name;
          clearSkills();
          await wait(350);
          c = bt.autoChoice(u);
        } else c = await choose(u);
        ev = bt.useSkill(u, c.skill, c.target);
      }
      await play(ev);
    }
    setActive(null);
  }

  async function run() {
    $('result').hidden = true;
    ui.battle = new Battle(STAGE_1);
    ui.cards.clear();
    const bt = ui.battle;
    buildSide($('heroes'), bt.heroes);
    say('');
    while (true) {
      const w = bt.nextWave();
      buildSide($('enemies'), bt.enemies);
      ui.cards.forEach((c, uid) => { if (!bt.find(uid)) ui.cards.delete(uid); });
      renderAll();
      clearSkills();
      $('prompt').textContent = bt.enemies.some((e) => e.boss) ? 'บอสปรากฏตัว!' : 'ศึกเริ่มแล้ว';
      await banner(bt.enemies.some((e) => e.boss) ? 'บอส: ' + bt.enemies[0].name : 'คลื่นที่ ' + (bt.wave + 1) + ' / ' + STAGE_1.waves.length);
      await talk(w.intro);
      await fight();
      if (bt.over) break;
      say('ชนะคลื่นนี้แล้ว!');
      await wait(700);
    }
    if (bt.over === 'win') await talk(STAGE_1.outro);
    showResult();
  }

  function showResult() {
    const bt = ui.battle;
    const win = bt.over === 'win';
    const stars = bt.stars();
    const best = Math.max(stars, store.get('best:' + STAGE_1.id, 0));
    if (win) store.set('best:' + STAGE_1.id, best);
    $('result-title').textContent = win ? 'ชนะแล้ว! 🎉' : 'แพ้แล้ว ลองใหม่นะ';
    $('result-stars').innerHTML = win
      ? '<span class="on">' + '★'.repeat(stars) + '</span><span class="off">' + '★'.repeat(3 - stars) + '</span><span class="sr-only">ได้ ' + stars + ' ดาว จาก 3</span>'
      : '';
    $('result-text').textContent = win
      ? 'ใช้ไป ' + bt.round + ' ตา' + (stars < 3 ? ' (3 ดาว: ทุกคนรอด และจบใน ' + STAGE_1.threeStarRounds + ' ตา)' : '') + ' สถิติดีที่สุด ' + best + ' ดาว'
      : 'เคล็ดลับ: เห็นป้าย ⚠ บนหัวศัตรู ให้หนุมานใช้ "หาวเป็นดาว" ทำให้มึน หรือ "อมพลับพลา" กางโล่ และให้พิเภกฟื้นพลังบ่อย ๆ';
    $('result').hidden = false;
    $('btn-retry').focus();
  }

  /* ---------- toolbar ---------- */

  function syncTools() {
    $('btn-speed').textContent = 'x' + ui.speed;
    $('btn-speed').setAttribute('aria-pressed', String(ui.speed === 2));
    $('btn-speed').setAttribute('aria-label', 'ความเร็ว x' + ui.speed);
    $('btn-auto').setAttribute('aria-pressed', String(ui.auto));
    $('btn-auto').textContent = ui.auto ? 'ออโต้: เปิด' : 'ออโต้';
  }

  $('btn-speed').addEventListener('click', () => { ui.speed = ui.speed === 1 ? 2 : 1; store.set('speed', ui.speed); syncTools(); });
  $('btn-auto').addEventListener('click', () => {
    ui.auto = !ui.auto;
    store.set('auto', ui.auto);
    syncTools();
    if (ui.auto && ui.pick) finishPick(ui.battle.autoChoice(ui.pick.unit));
  });
  $('btn-retry').addEventListener('click', run);
  document.addEventListener('keydown', (ev) => { if (ev.key === 'Escape') cancelTarget(); });

  syncTools();
  run();
})();
