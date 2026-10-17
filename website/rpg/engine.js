/* ศึกลงกา (turn-based prototype): battle rules with no DOM access, so the same file runs in the browser and in Node tests. */
(function (root) {
  'use strict';

  // Status effects: multipliers are read in calcDamage; turns tick down at the end of the bearer's own turn.
  const STATUS = Object.freeze({
    stun:    { label: 'มึน', icon: '💫', bad: true },
    shield:  { label: 'โล่', icon: '🛡️', bad: false },
    atkUp:   { label: 'พลังขึ้น', icon: '⚔️', bad: false },
    atkDown: { label: 'พลังลด', icon: '🌀', bad: true },
    defDown: { label: 'เกราะแตก', icon: '💔', bad: true },
    rage:    { label: 'คลั่ง', icon: '🔥', bad: false },
  });

  // target: enemy | ally | allEnemies | allAllies | self. Effect "to" overrides who receives that effect.
  const HEROES = Object.freeze({
    rama: {
      name: 'พระราม', img: 'rama', hp: 900, atk: 120, def: 40, spd: 14,
      skills: [
        { id: 'shot', name: 'ยิงศร', desc: 'ยิงศัตรู 1 ตัว', target: 'enemy', cd: 0, fx: [{ k: 'dmg', p: 1.0 }] },
        { id: 'rain', name: 'ฝนศร', desc: 'ยิงศัตรูทุกตัว', target: 'allEnemies', cd: 2, fx: [{ k: 'dmg', p: 0.75 }] },
        { id: 'brahma', name: 'ศรพรหมาสตร์', desc: 'ศรศักดิ์สิทธิ์ แรงมาก 1 ตัว', target: 'enemy', cd: 3, fx: [{ k: 'dmg', p: 2.4 }] },
      ],
    },
    hanuman: {
      name: 'หนุมาน', img: 'hanuman', hp: 1200, atk: 95, def: 60, spd: 16,
      skills: [
        { id: 'trident', name: 'ฟาดตรีเพชร', desc: 'ตีศัตรู 1 ตัว', target: 'enemy', cd: 0, fx: [{ k: 'dmg', p: 1.0 }] },
        { id: 'yawn', name: 'หาวเป็นดาว', desc: 'ตีเบา ๆ แล้วทำให้มึน ข้าม 1 ตา', target: 'enemy', cd: 3, fx: [{ k: 'dmg', p: 0.6 }, { k: 'status', s: 'stun', t: 1 }] },
        { id: 'pavilion', name: 'อมพลับพลา', desc: 'กางโล่ให้ทุกคน รับดาเมจลดลง 40% 2 ตา', target: 'allAllies', cd: 4, fx: [{ k: 'status', s: 'shield', t: 2 }] },
      ],
    },
    phiphek: {
      name: 'พิเภก', img: 'phiphek', hp: 800, atk: 70, def: 35, spd: 12,
      skills: [
        { id: 'lotus', name: 'ปัดดอกบัว', desc: 'ตีศัตรู 1 ตัว', target: 'enemy', cd: 0, fx: [{ k: 'dmg', p: 0.9 }] },
        { id: 'mantra', name: 'มนต์บัวทอง', desc: 'ฟื้นพลังชีวิตทุกคน', target: 'allAllies', cd: 2, fx: [{ k: 'heal', p: 1.4, pct: 0.1 }] },
        { id: 'omen', name: 'ทำนายจุดอ่อน', desc: 'เกราะศัตรูแตก และพวกเราแรงขึ้น 2 ตา', target: 'allEnemies', cd: 3, fx: [{ k: 'status', s: 'defDown', t: 2 }, { k: 'status', s: 'atkUp', t: 2, to: 'allAllies' }] },
      ],
    },
  });

  // Enemy moves; "tell" is the warning shown one turn ahead so the player can react (shield, stun).
  const MOVES = Object.freeze({
    smash:   { name: 'ทุบ', target: 'randomHero', fx: [{ k: 'dmg', p: 1.0 }] },
    diamond: { name: 'นิ้วเพชร', tell: true, target: 'randomHero', fx: [{ k: 'dmg', p: 2.0 }] },
    claw:    { name: 'ข่วน', target: 'randomHero', fx: [{ k: 'dmg', p: 1.0 }] },
    illusion:{ name: 'ลวงตา', tell: true, target: 'strongestHero', fx: [{ k: 'dmg', p: 0.6 }, { k: 'status', s: 'atkDown', t: 2 }] },
    spearJab:{ name: 'แทงหอก', target: 'randomHero', fx: [{ k: 'dmg', p: 1.0 }] },
    mokkha:  { name: 'หอกโมกขศักดิ์', tell: true, target: 'healthiestHero', fx: [{ k: 'dmg', p: 2.2 }] },
    quake:   { name: 'กระทืบแผ่นดิน', tell: true, target: 'allHeroes', fx: [{ k: 'dmg', p: 0.8 }] },
  });

  const ENEMIES = Object.freeze({
    nonthok:  { name: 'นนทก', img: 'nonthok', hp: 520, atk: 95, def: 35, spd: 13, pattern: ['smash', 'smash', 'diamond'] },
    benjakai: { name: 'นางเบญกาย', img: 'benjakai', hp: 440, atk: 80, def: 30, spd: 15, pattern: ['claw', 'illusion', 'claw'] },
    kumpakan: { name: 'กุมภกรรณ', img: 'kumpakan', hp: 2500, atk: 172, def: 50, spd: 9, boss: true, doze: 0.25,
      pattern: ['spearJab', 'spearJab', 'mokkha'], ragePattern: ['spearJab', 'quake', 'mokkha'] },
  });

  const STAGE_1 = Object.freeze({
    id: 'lanka-gate',
    title: 'ด่าน 1 ประตูเมืองลงกา',
    party: ['hanuman', 'rama', 'phiphek'],
    threeStarRounds: 16,
    waves: [
      {
        enemies: ['nonthok', 'benjakai'],
        intro: [
          { who: 'phiphek', text: 'ข้างหน้าคือประตูเมืองลงกา มีนนทกกับเบญกายเฝ้าอยู่' },
          { who: 'benjakai', text: 'พ่อ! มาทำอะไรตรงนี้ จะไม่ให้ผ่านง่าย ๆ หรอกนะ' },
          { who: 'hanuman', text: 'ปล่อยข้าลุยเลย! ใครโดนกระบวนท่าลิงก็ขอให้ทำใจ' },
        ],
      },
      {
        enemies: ['kumpakan'],
        intro: [
          { who: 'kumpakan', text: 'หาววว... ใครมาเสียงดังหน้าประตู ข้ากำลังหลับสบาย' },
          { who: 'rama', text: 'ระวังหอกโมกขศักดิ์ เห็นเตือนเมื่อไร ให้หนุมานกางโล่' },
        ],
      },
    ],
    outro: [
      { who: 'rama', text: 'ผ่านประตูลงกาแล้ว ไปช่วยนางสีดากันต่อ!' },
      { who: 'hanuman', text: 'ด่านต่อไปเจออินทรชิต รอเลยนะ' },
    ],
  });

  function makeRng(seed) {
    if (seed == null) return Math.random;
    let s = seed >>> 0;
    return function () { // mulberry32
      s = (s + 0x6D2B79F5) >>> 0;
      let t = s;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  let uid = 0;
  function makeUnit(def, key, side) {
    return {
      uid: 'u' + (++uid), key, side, name: def.name, img: def.img, boss: !!def.boss,
      maxHp: def.hp, hp: def.hp, atk: def.atk, def: def.def, spd: def.spd,
      skills: def.skills || null, pattern: def.pattern || null, ragePattern: def.ragePattern || null,
      doze: def.doze || 0, step: 0, cds: {}, status: {}, fresh: [], dozedLast: false, next: null,
    };
  }

  class Battle {
    constructor(stage, opts) {
      opts = opts || {};
      this.stage = stage;
      this.rng = makeRng(opts.seed);
      this.heroes = stage.party.map((k) => makeUnit(HEROES[k], k, 'hero'));
      this.enemies = [];
      this.wave = -1;
      this.round = 0;
      this.queue = [];
      this.over = null; // 'win' | 'lose'
    }

    alive(list) { return list.filter((u) => u.hp > 0); }
    foesOf(u) { return u.side === 'hero' ? this.enemies : this.heroes; }
    friendsOf(u) { return u.side === 'hero' ? this.heroes : this.enemies; }
    find(uid) { return this.heroes.concat(this.enemies).find((u) => u.uid === uid) || null; }

    nextWave() {
      this.wave += 1;
      const w = this.stage.waves[this.wave];
      this.enemies = w.enemies.map((k) => makeUnit(ENEMIES[k], k, 'enemy'));
      this.enemies.forEach((e) => { e.next = this.planMove(e); });
      // Fresh wave: clear hero cooldowns and statuses so the boss fight starts fair, keep HP.
      this.heroes.forEach((h) => { h.cds = {}; h.status = {}; });
      this.queue = [];
      return w;
    }

    hasMoreWaves() { return this.wave < this.stage.waves.length - 1; }

    // Turn order: everyone alive, fastest first. Rebuilt at the start of each round.
    nextActor() {
      while (true) {
        if (!this.queue.length) {
          this.round += 1;
          this.queue = this.alive(this.heroes.concat(this.enemies))
            .sort((a, b) => b.spd - a.spd || (a.side === 'hero' ? -1 : 1))
            .map((u) => u.uid);
        }
        const u = this.find(this.queue.shift());
        if (u && u.hp > 0) return u;
      }
    }

    upcoming(n) {
      const order = this.queue.map((id) => this.find(id)).filter((u) => u && u.hp > 0);
      if (order.length < n) {
        const next = this.alive(this.heroes.concat(this.enemies)).sort((a, b) => b.spd - a.spd || (a.side === 'hero' ? -1 : 1));
        while (order.length < n && next.length) order.push(...next.slice(0, n - order.length));
      }
      return order.slice(0, n);
    }

    // Start of a unit's turn: tick cooldowns, then check stun/sleep. Returns events; skip=true means the turn is lost.
    beginTurn(u) {
      const ev = [];
      Object.keys(u.cds).forEach((k) => { if (u.cds[k] > 0) u.cds[k] -= 1; });
      if (u.status.stun) {
        delete u.status.stun;
        ev.push({ t: 'skip', who: u.uid, why: 'stun' });
        this.endTurn(u, ev);
        return { skip: true, ev };
      }
      if (u.doze && !u.status.rage && !u.dozedLast && this.rng() < u.doze) {
        u.dozedLast = true;
        ev.push({ t: 'skip', who: u.uid, why: 'sleep' });
        this.endTurn(u, ev);
        return { skip: true, ev };
      }
      u.dozedLast = false;
      return { skip: false, ev };
    }

    endTurn(u, ev) {
      const fresh = u.fresh;
      u.fresh = [];
      Object.keys(u.status).forEach((s) => {
        if (s === 'rage' || fresh.includes(s)) return;
        u.status[s] -= 1;
        if (u.status[s] <= 0) { delete u.status[s]; ev.push({ t: 'expire', who: u.uid, s }); }
      });
      this.checkOver();
    }

    skillReady(u, skill) { return !(u.cds[skill.id] > 0); }

    validTargets(u, skill) {
      if (skill.target === 'enemy') return this.alive(this.foesOf(u));
      if (skill.target === 'ally') return this.alive(this.friendsOf(u));
      return [];
    }

    // Hero action. targetUid is required only for single-target skills.
    useSkill(u, skillId, targetUid) {
      const skill = u.skills.find((s) => s.id === skillId);
      if (!skill || !this.skillReady(u, skill)) throw new Error('skill not ready: ' + skillId);
      let targets;
      if (skill.target === 'enemy' || skill.target === 'ally') {
        const t = this.find(targetUid);
        if (!t || t.hp <= 0 || !this.validTargets(u, skill).includes(t)) throw new Error('bad target');
        targets = [t];
      } else targets = this.groupTargets(u, skill.target);
      if (skill.cd) u.cds[skill.id] = skill.cd + 1; // +1 because beginTurn ticks once before the next choice
      const ev = [{ t: 'act', who: u.uid, name: skill.name, targets: targets.map((x) => x.uid) }];
      this.applyFx(u, skill.fx, targets, ev);
      this.endTurn(u, ev);
      return ev;
    }

    groupTargets(u, kind) {
      if (kind === 'allEnemies') return this.alive(this.foesOf(u));
      if (kind === 'allAllies') return this.alive(this.friendsOf(u));
      if (kind === 'self') return [u];
      return [];
    }

    applyFx(src, fx, targets, ev) {
      fx.forEach((f) => {
        const recv = f.to ? this.groupTargets(src, f.to) : targets;
        recv.forEach((t) => {
          if (t.hp <= 0) return;
          if (f.k === 'dmg') {
            const r = this.calcDamage(src, t, f.p);
            t.hp = Math.max(0, t.hp - r.amount);
            ev.push({ t: 'dmg', who: t.uid, amount: r.amount, crit: r.crit, hp: t.hp });
            if (t.hp === 0) ev.push({ t: 'ko', who: t.uid });
            else if (t.ragePattern && !t.status.rage && t.hp <= t.maxHp / 2) {
              t.status.rage = 1;
              t.step = 0;
              t.next = this.planMove(t);
              ev.push({ t: 'rage', who: t.uid });
            }
          } else if (f.k === 'heal') {
            const amount = Math.round(src.atk * f.p + t.maxHp * (f.pct || 0));
            const before = t.hp;
            t.hp = Math.min(t.maxHp, t.hp + amount);
            ev.push({ t: 'heal', who: t.uid, amount: t.hp - before, hp: t.hp });
          } else if (f.k === 'status') {
            t.status[f.s] = Math.max(t.status[f.s] || 0, f.t);
            if (t === src) src.fresh.push(f.s); // don't tick a self-buff away in the same turn it was cast
            ev.push({ t: 'status', who: t.uid, s: f.s });
          }
        });
      });
    }

    calcDamage(src, t, power) {
      let atk = src.atk;
      if (src.status.atkUp) atk *= 1.3;
      if (src.status.atkDown) atk *= 0.7;
      if (src.status.rage) atk *= 1.25;
      const def = t.def * (t.status.defDown ? 0.5 : 1);
      let dmg = atk * power * (100 / (100 + def)) * (0.92 + this.rng() * 0.16);
      const crit = this.rng() < 0.12;
      if (crit) dmg *= 1.5;
      if (t.status.shield) dmg *= 0.6;
      return { amount: Math.max(1, Math.round(dmg)), crit };
    }

    planMove(e) {
      const pat = e.status.rage && e.ragePattern ? e.ragePattern : e.pattern;
      return pat[e.step % pat.length];
    }

    // Enemy turn: perform the telegraphed move, then plan the next one.
    enemyAct(e) {
      const move = MOVES[e.next];
      const heroes = this.alive(this.heroes);
      let targets;
      if (move.target === 'allHeroes') targets = heroes;
      else if (move.target === 'strongestHero') targets = [heroes.slice().sort((a, b) => b.atk - a.atk)[0]];
      else if (move.target === 'healthiestHero') targets = [heroes.slice().sort((a, b) => b.hp - a.hp)[0]];
      else targets = [heroes[Math.floor(this.rng() * heroes.length)]];
      const ev = [{ t: 'act', who: e.uid, name: move.name, targets: targets.map((x) => x.uid), big: !!move.tell }];
      this.applyFx(e, move.fx, targets, ev);
      e.step += 1;
      e.next = this.planMove(e);
      this.endTurn(e, ev);
      return ev;
    }

    // Simple helper AI for heroes: used by the Auto button and by the balance test.
    autoChoice(u) {
      const ready = (id) => { const s = u.skills.find((x) => x.id === id); return s && this.skillReady(u, s); };
      const foes = this.alive(this.enemies);
      const team = this.alive(this.heroes);
      const threat = foes.find((e) => MOVES[e.next] && MOVES[e.next].tell && !e.status.stun);
      const weakest = foes.slice().sort((a, b) => a.hp - b.hp)[0];
      const toughest = foes.slice().sort((a, b) => b.hp - a.hp)[0];
      if (u.key === 'phiphek') {
        const hurt = team.filter((h) => h.hp < h.maxHp * 0.6).length;
        if (ready('mantra') && hurt >= 1) return { skill: 'mantra' };
        if (ready('omen')) return { skill: 'omen' };
        return { skill: 'lotus', target: weakest.uid };
      }
      if (u.key === 'hanuman') {
        const shielded = team.every((h) => h.status.shield);
        if (threat && ready('yawn')) return { skill: 'yawn', target: threat.uid };
        if (threat && ready('pavilion') && !shielded) return { skill: 'pavilion' };
        return { skill: 'trident', target: weakest.uid };
      }
      if (ready('brahma')) return { skill: 'brahma', target: toughest.uid };
      if (foes.length > 1 && ready('rain')) return { skill: 'rain' };
      return { skill: 'shot', target: weakest.uid };
    }

    checkOver() {
      if (!this.alive(this.heroes).length) this.over = 'lose';
      else if (!this.alive(this.enemies).length && !this.hasMoreWaves()) this.over = 'win';
      return this.over;
    }

    waveCleared() { return !this.alive(this.enemies).length; }

    stars() {
      if (this.over !== 'win') return 0;
      const allAlive = this.alive(this.heroes).length === this.heroes.length;
      if (allAlive && this.round <= this.stage.threeStarRounds) return 3;
      return allAlive ? 2 : 1;
    }
  }

  root.LankaRPG = Object.freeze({ Battle, HEROES, ENEMIES, MOVES, STATUS, STAGE_1 });
})(typeof window !== 'undefined' ? window : globalThis);
