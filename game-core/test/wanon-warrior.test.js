import { test } from 'node:test';
import assert from 'node:assert/strict';
import { WanonWarrior, nagaBound } from '../src/index.js';
import { dummy, newBattle, Faction } from './helpers.js';

const setup = (wind, revival) => {
  const battle = newBattle({ wind });
  const wanon = new WanonWarrior({ id: 'wanon', name: 'Wanon', team: Faction.AYODHYA, maxHp: 1000, def: 0, windRevival: revival });
  const foe = dummy('yaksha', Faction.LANKA);
  battle.add(wanon, foe);
  return { battle, wanon, foe };
};
const lethal = (source, tags) => ({ power: 99999, kind: 'true', source, tags });

test('Wind Revival: revives at 30% HP when wind >= threshold', () => {
  const { battle, wanon, foe } = setup(60);
  const r = wanon.receiveDamage(lethal(foe), battle);
  assert.deepEqual(r, { landed: true, amount: 1000, ko: false, revived: true });
  assert.equal(wanon.hp, 300);
  assert.equal(wanon.windRevival.charges, 0);
  assert.ok(battle.log.some((e) => e.t === 'revive' && e.why === 'windRevival'));
  assert.ok(!battle.log.some((e) => e.t === 'ko'));
});

test('Wind Revival: no revive when the wind is calm', () => {
  const { battle, wanon, foe } = setup(39);
  const r = wanon.receiveDamage(lethal(foe), battle);
  assert.equal(r.landed && r.ko, true);
  assert.equal(wanon.alive, false);
  assert.equal(wanon.windRevival.charges, 1, 'charge is not spent on a failed trigger');
});

test('Wind Revival: exactly at threshold counts', () => {
  const { battle, wanon, foe } = setup(40);
  assert.equal(wanon.receiveDamage(lethal(foe), battle).landed, true);
  assert.equal(wanon.alive, true);
});

test('Wind Revival: only once per battle by default', () => {
  const { battle, wanon, foe } = setup(100);
  wanon.receiveDamage(lethal(foe), battle);
  const second = wanon.receiveDamage(lethal(foe), battle);
  assert.equal(second.landed && second.ko, true);
});

test('Wind Revival: a sealsRevival hit cannot be cheated', () => {
  const { battle, wanon, foe } = setup(100);
  wanon.receiveDamage(lethal(foe, ['sealsRevival']), battle);
  assert.equal(wanon.alive, false);
  assert.equal(wanon.windRevival.charges, 1);
});

test('Wind Revival: revival clears crowd control', () => {
  const { battle, wanon, foe } = setup(100);
  wanon.applyStatus(nagaBound({ turns: 2, resistTurns: 1, sourceId: foe.id }), battle, foe);
  wanon.receiveDamage(lethal(foe), battle);
  assert.equal(wanon.hasStatus('nagaBound'), false);
  assert.equal(wanon.canAct, true);
});

test('Call the Wind raises wind (capped at 100) and goes on cooldown', () => {
  const { battle, wanon } = setup(0);
  const skill = wanon.skills.callTheWind;
  assert.equal(skill.use(wanon, battle, null).ok, true);
  assert.equal(battle.wind, 30);
  assert.equal(wanon.mp, 40);
  assert.deepEqual(skill.use(wanon, battle, null), { ok: false, why: 'onCooldown' });
  for (let i = 0; i < 4; i++) battle.beginTurn(wanon), battle.endTurn(wanon);
  assert.equal(skill.use(wanon, battle, null).ok, true);
  battle.setWind(250);
  assert.equal(battle.wind, 100);
});
