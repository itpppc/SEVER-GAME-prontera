import { test } from 'node:test';
import assert from 'node:assert/strict';
import { ThotsakanBoss, BossPhase, WanonWarrior } from '../src/index.js';
import { dummy, newBattle, Faction } from './helpers.js';

const setup = () => {
  const battle = newBattle();
  const boss = new ThotsakanBoss({ id: 'thotsakan', name: 'Thotsakan', team: Faction.LANKA, heartBox: { maxHp: 300, def: 0 } });
  const hero = new WanonWarrior({ id: 'hero', name: 'Hero', team: Faction.AYODHYA, atk: 200 });
  const demon = dummy('demon', Faction.LANKA, { atk: 500 });
  battle.add(boss, boss.heartBox, hero, demon);
  return { battle, boss, box: boss.heartBox, hero, demon };
};

test('Phase 1: boss blocks physical, magic and true damage', () => {
  const { battle, boss, hero } = setup();
  for (const kind of ['physical', 'magic', 'true']) {
    assert.deepEqual(boss.receiveDamage({ power: 1e6, kind, source: hero }, battle), { landed: false, why: 'heartSealed' });
  }
  assert.equal(boss.hp, boss.maxHp);
  assert.equal(boss.phase, BossPhase.HEART_SEALED);
});

test('Heart Box: friendly fire and sourceless damage are ignored', () => {
  const { battle, box, demon } = setup();
  assert.deepEqual(box.receiveDamage({ power: 1e6, kind: 'true', source: demon }, battle), { landed: false, why: 'friendlyFire' });
  assert.deepEqual(box.receiveDamage({ power: 1e6, kind: 'true', source: null }, battle), { landed: false, why: 'noSource' });
  assert.equal(box.hp, box.maxHp);
});

test('Heart Box destroyed -> Phase 2: boss vulnerable and enraged, event emitted once', () => {
  const { battle, boss, box, hero } = setup();
  hero.position = { ...box.position };
  while (box.alive) assert.equal(hero.skills.strike.use(hero, battle, box).ok, true);
  assert.equal(boss.phase, BossPhase.HEART_EXPOSED);
  assert.equal(boss.heartBrokenBy, 'hero');
  assert.equal(boss.atk, Math.round(220 * 1.25));
  assert.equal(battle.log.filter((e) => e.t === 'phase').length, 1);
  const r = boss.receiveDamage({ power: 1000, kind: 'true', source: hero }, battle);
  assert.equal(r.landed, true);
  assert.equal(boss.hp, boss.maxHp - 1000);
  assert.equal(boss.exposeHeart(battle, 'x'), false, 'idempotent');
});

test('Heart Box never takes a turn and does not count for victory', () => {
  const { battle, boss, demon } = setup();
  assert.ok(!battle.turnOrder().includes(boss.heartBox));
  boss.phase = BossPhase.HEART_EXPOSED;
  boss.hp = 0;
  demon.hp = 0;
  assert.equal(battle.winner(), Faction.AYODHYA);
});
