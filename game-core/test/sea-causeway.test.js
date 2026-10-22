import { test } from 'node:test';
import assert from 'node:assert/strict';
import { SeaCauseway, EventBus } from '../src/index.js';
import { Faction } from './helpers.js';

const A = Faction.AYODHYA;
const L = Faction.LANKA;

test('build and interrupt move progress in 0.1% stones', () => {
  const c = new SeaCauseway();
  assert.deepEqual(c.build('rama', A, 50), { ok: true, applied: 50, capped: false, percent: 5 });
  assert.deepEqual(c.interrupt('fish', L, 20), { ok: true, applied: 20, capped: false, percent: 3 });
});

test('faction, amount and per-action cap are enforced', () => {
  const c = new SeaCauseway();
  assert.deepEqual(c.build('fish', L, 10), { ok: false, why: 'wrongFaction' });
  assert.deepEqual(c.interrupt('rama', A, 10), { ok: false, why: 'wrongFaction' });
  for (const bad of [0, -5, 1.5, NaN, Infinity]) assert.deepEqual(c.build('rama', A, bad), { ok: false, why: 'badAmount' });
  assert.deepEqual(c.build('rama', A, 999), { ok: true, applied: 50, capped: true, percent: 5 });
});

test('progress never drops below 0 or a reached checkpoint', () => {
  const c = new SeaCauseway();
  c.interrupt('fish', L, 50);
  assert.equal(c.stones, 0);
  for (let i = 0; i < 6; i++) c.build('rama', A, 50); // 300 stones = 30%, checkpoint 25% locked
  assert.equal(c.floor, 250);
  for (let i = 0; i < 5; i++) c.interrupt('fish', L, 50);
  assert.equal(c.percent, 25);
});

test('reaching 100% completes and locks the causeway; events fire in order', () => {
  const events = [];
  const bus = new EventBus();
  bus.on((e) => events.push(e.kind));
  const c = new SeaCauseway({ emitter: bus });
  for (let i = 0; i < 25; i++) c.build(`b${i % 3}`, A, 50);
  assert.equal(c.state, 'completed');
  assert.equal(c.percent, 100);
  assert.deepEqual(c.interrupt('fish', L, 50), { ok: false, why: 'completed' });
  assert.deepEqual(c.build('rama', A, 1), { ok: false, why: 'completed' });
  assert.deepEqual(events.filter((k) => k !== 'build'), ['checkpoint', 'checkpoint', 'checkpoint', 'complete']);
  assert.equal([...c.built.values()].reduce((a, b) => a + b, 0), 1000);
});

test('resolveRound applies the net effect and credits shares that sum exactly', () => {
  const c = new SeaCauseway();
  const r = c.resolveRound({
    builders: [{ id: 'a', stones: 30 }, { id: 'b', stones: 30 }, { id: 'c', stones: 30 }],
    creatures: [{ id: 'fish', stones: 50 }],
  });
  assert.equal(r.net, 40);
  assert.equal([...c.built.values()].reduce((x, y) => x + y, 0), 40);
  const r2 = c.resolveRound({ creatures: [{ id: 'fish', stones: 50 }, { id: 'crab', stones: 999 }] });
  assert.equal(r2.net, -40, 'cannot remove more than exists');
  assert.equal(c.stones, 0);
});

test('invalid config is rejected', () => {
  assert.throws(() => new SeaCauseway({ checkpoints: [50, 25] }), RangeError);
  assert.throws(() => new SeaCauseway({ totalStones: 0 }), RangeError);
});
