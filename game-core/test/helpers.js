import { Battle, Combatant, Faction } from '../src/index.js';

/** A plain training dummy. */
export const dummy = (id, team, extra = {}) =>
  new Combatant({ id, name: id, team, maxHp: 500, atk: 50, def: 0, mdef: 0, spd: 5, ...extra });

export const newBattle = (opts = {}) => new Battle({ seed: 7, ...opts });
export { Faction };
