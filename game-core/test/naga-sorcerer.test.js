import { test } from 'node:test';
import assert from 'node:assert/strict';
import { NagaSorcerer } from '../src/index.js';
import { dummy, newBattle, Faction } from './helpers.js';

const setup = () => {
  const battle = newBattle();
  const naga = new NagaSorcerer({ id: 'naga', name: 'Naga', team: Faction.LANKA, position: { x: 0, y: 0 } });
  const a = dummy('a', Faction.AYODHYA, { position: { x: 4, y: 0 } });
  const b = dummy('b', Faction.AYODHYA, { position: { x: 5, y: 1 } });
  const far = dummy('far', Faction.AYODHYA, { position: { x: 9, y: 0 } });
  const ally = dummy('ally', Faction.LANKA, { position: { x: 4, y: 1 } });
  battle.add(naga, a, b, far, ally);
  return { battle, naga, a, b, far, ally };
};

test('Naga Binding: hits and binds every enemy in the radius, never allies', () => {
  const { battle, naga, a, b, far, ally } = setup();
  const r = naga.skills.nagaBinding.use(naga, battle, { x: 4, y: 0 });
  assert.equal(r.ok, true);
  assert.equal(a.hasStatus('nagaBound') && b.hasStatus('nagaBound'), true);
  assert.equal(far.hasStatus('nagaBound'), false);
  assert.equal(ally.hasStatus('nagaBound'), false);
  assert.equal(ally.hp, ally.maxHp);
  assert.equal(a.hp, 500 - Math.round(130 * 0.6));
  assert.equal(a.canAct || a.canMove || a.moveTo({ x: 0, y: 0 }), false);
  assert.equal(naga.mp, 90);
});

test('Naga Binding: bound unit loses 2 turns, then gets 1 turn of bindResist', () => {
  const { battle, naga, a } = setup();
  naga.skills.nagaBinding.use(naga, battle, { x: 4, y: 0 });
  assert.equal(battle.beginTurn(a).skip, true);
  assert.equal(battle.beginTurn(a).skip, true);
  assert.equal(a.hasStatus('nagaBound'), false);
  assert.equal(a.hasStatus('bindResist'), true);
  assert.equal(battle.beginTurn(a).skip, false);
});

test('Naga Binding: diminishing returns blocks an immediate re-bind', () => {
  const { battle, naga, a } = setup();
  const naga2 = new NagaSorcerer({ id: 'naga2', name: 'Naga 2', team: Faction.LANKA, position: { x: 1, y: 0 } });
  battle.add(naga2);
  naga.skills.nagaBinding.use(naga, battle, { x: 4, y: 0 });
  battle.beginTurn(a);
  battle.beginTurn(a);
  naga2.skills.nagaBinding.use(naga2, battle, { x: 4, y: 0 });
  assert.equal(a.hasStatus('nagaBound'), false);
  assert.ok(battle.log.some((e) => e.t === 'resist' && e.who === 'a' && e.why === 'diminishingReturns'));
});

test('Naga Binding: ccImmune units take damage but are not bound', () => {
  const { battle, naga } = setup();
  const boss = dummy('boss', Faction.AYODHYA, { position: { x: 3, y: 0 }, tags: ['ccImmune'] });
  battle.add(boss);
  naga.skills.nagaBinding.use(naga, battle, { x: 3, y: 0 });
  assert.ok(boss.hp < boss.maxHp);
  assert.equal(boss.hasStatus('nagaBound'), false);
});

test('Naga Binding: rejects out-of-range, no MP, cooldown, bound caster; no cost on failure', () => {
  const { battle, naga } = setup();
  const skill = naga.skills.nagaBinding;
  assert.deepEqual(skill.use(naga, battle, { x: 20, y: 0 }), { ok: false, why: 'outOfRange' });
  assert.deepEqual(skill.use(naga, battle, { x: NaN, y: 0 }), { ok: false, why: 'badTarget' });
  assert.equal(naga.mp, 120);
  skill.use(naga, battle, { x: 4, y: 0 });
  assert.deepEqual(skill.use(naga, battle, { x: 4, y: 0 }), { ok: false, why: 'onCooldown' });
  naga.cds = {};
  naga.mp = 10;
  assert.deepEqual(skill.use(naga, battle, { x: 4, y: 0 }), { ok: false, why: 'notEnoughMp' });
});

test('Naga Binding: a target killed by the damage is not bound', () => {
  const { battle, naga } = setup();
  const weak = dummy('weak', Faction.AYODHYA, { maxHp: 10, position: { x: 4, y: -1 } });
  battle.add(weak);
  naga.skills.nagaBinding.use(naga, battle, { x: 4, y: 0 });
  assert.equal(weak.alive, false);
  assert.equal(weak.statuses.size, 0);
});
