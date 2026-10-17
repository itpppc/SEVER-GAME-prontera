import { test } from 'node:test';
import assert from 'node:assert/strict';
import { Battle, Combatant, EventBus, makeRng } from '../src/index.js';
import { dummy, newBattle, Faction } from './helpers.js';

test('turn order: fastest first, ties broken deterministically', () => {
  const b = newBattle();
  b.add(dummy('slow', Faction.AYODHYA, { spd: 1 }), dummy('fast', Faction.LANKA, { spd: 9 }), dummy('tie', Faction.AYODHYA, { spd: 9 }));
  assert.deepEqual(b.turnOrder().map((u) => u.id), ['tie', 'fast', 'slow']);
});

test('duplicate ids and bad stats are rejected', () => {
  const b = newBattle();
  b.add(dummy('x', Faction.AYODHYA));
  assert.throws(() => b.add(dummy('x', Faction.LANKA)));
  assert.throws(() => new Combatant({ id: 'y', name: 'y', team: 'mars', maxHp: 10 }), TypeError);
  assert.throws(() => new Combatant({ id: 'y', name: 'y', team: Faction.LANKA, maxHp: 0 }), RangeError);
  assert.throws(() => dummy('z', Faction.LANKA).receiveDamage({ power: NaN, kind: 'true', source: null }, b), RangeError);
});

test('mitigation: def reduces physical, mdef reduces magic, true ignores both, min 1', () => {
  const b = newBattle();
  const t = dummy('t', Faction.LANKA, { def: 100, mdef: 300 });
  b.add(t);
  assert.equal(t.mitigate({ power: 200, kind: 'physical', source: null }), 100);
  assert.equal(t.mitigate({ power: 200, kind: 'magic', source: null }), 50);
  assert.equal(t.mitigate({ power: 200, kind: 'true', source: null }), 200);
  assert.equal(t.mitigate({ power: 0.1, kind: 'physical', source: null }), 1);
});

test('a throwing listener does not break the battle', () => {
  const errors = [];
  const bus = new EventBus({ onError: (e) => errors.push(e) });
  bus.on(() => { throw new Error('ui bug'); });
  const b = new Battle({ bus });
  const t = dummy('t', Faction.LANKA);
  b.add(t);
  t.receiveDamage({ power: 10, kind: 'true', source: null }, b);
  assert.equal(t.hp, 490);
  assert.equal(errors.length, 1);
});

test('seeded rng is deterministic', () => {
  const a = makeRng(42), c = makeRng(42);
  assert.deepEqual([a(), a(), a()], [c(), c(), c()]);
});
