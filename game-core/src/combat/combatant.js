// @ts-check
import { Faction } from '../core/types.js';
import { StatusId } from './status-effects.js';

/** @typedef {import('../core/types.js').FactionId} FactionId */
/** @typedef {import('../core/types.js').Point} Point */
/** @typedef {import('../core/types.js').DamageType} DamageType */
/** @typedef {import('./status-effects.js').StatusEffect} StatusEffect */
/** @typedef {import('./battle.js').Battle} Battle */

/**
 * @typedef {object} Hit
 * @property {number} power         raw damage before mitigation
 * @property {DamageType} kind
 * @property {Combatant | null} source
 * @property {string[]} [tags]      e.g. 'sealsRevival' stops on-defeat passives
 */

/**
 * @typedef {(
 *   | { landed: true, amount: number, ko: boolean, revived: boolean }
 *   | { landed: false, why: string }
 * )} DamageResult
 */

/**
 * Returns true when it saved the owner (owner must already have hp > 0 again).
 * @typedef {(owner: Combatant, hit: Hit, battle: Battle) => boolean} DefeatInterceptor
 */

/**
 * @typedef {object} CombatantInit
 * @property {string} id
 * @property {string} name
 * @property {FactionId} team
 * @property {number} maxHp
 * @property {number} [maxMp]
 * @property {number} [atk]
 * @property {number} [def]
 * @property {number} [matk]
 * @property {number} [mdef]
 * @property {number} [spd]
 * @property {Point} [position]
 * @property {string[]} [tags]   'ccImmune', 'boss', 'object' (cannot act, not counted for victory)
 */

const FACTIONS = new Set(Object.values(Faction));

/** @param {number} n @param {string} field */
function assertStat(n, field) {
  if (!Number.isFinite(n) || n < 0) throw new RangeError(`${field} must be a finite number >= 0`);
}

export class Combatant {
  /** @type {Map<string, StatusEffect>} */
  statuses = new Map();
  /** Skill cooldowns in own turns, same convention as website/rpg (`cds`). @type {Record<string, number>} */
  cds = {};
  /** Statuses applied this turn that must not tick until the next turn. @type {Set<string>} */
  fresh = new Set();
  /** @type {DefeatInterceptor[]} */
  #defeatInterceptors = [];

  /** @param {CombatantInit} init */
  constructor(init) {
    if (!init.id) throw new TypeError('combatant id is required');
    if (!FACTIONS.has(init.team)) throw new TypeError(`unknown team: ${init.team}`);
    if (!Number.isInteger(init.maxHp) || init.maxHp < 1) throw new RangeError('maxHp must be an integer >= 1');
    this.id = init.id;
    this.name = init.name;
    this.team = init.team;
    this.maxHp = init.maxHp;
    this.hp = init.maxHp;
    this.maxMp = init.maxMp ?? 0;
    this.mp = this.maxMp;
    this.atk = init.atk ?? 0;
    this.def = init.def ?? 0;
    this.matk = init.matk ?? 0;
    this.mdef = init.mdef ?? 0;
    this.spd = init.spd ?? 0;
    for (const f of /** @type {const} */ (['maxMp', 'atk', 'def', 'matk', 'mdef', 'spd'])) assertStat(this[f], f);
    this.position = { ...(init.position ?? { x: 0, y: 0 }) };
    this.tags = new Set(init.tags ?? []);
  }

  get alive() {
    return this.hp > 0;
  }

  get canAct() {
    if (!this.alive || this.tags.has('object')) return false;
    for (const s of this.statuses.values()) if (s.preventsActions) return false;
    return true;
  }

  get canMove() {
    if (!this.alive || this.tags.has('object')) return false;
    for (const s of this.statuses.values()) if (s.preventsMovement) return false;
    return true;
  }

  /** @param {string} id */
  hasStatus(id) {
    return this.statuses.has(id);
  }

  /** @param {DefeatInterceptor} fn */
  addDefeatInterceptor(fn) {
    this.#defeatInterceptors.push(fn);
  }

  /**
   * Same id refreshes to the longer duration instead of stacking.
   * @param {StatusEffect} effect
   * @param {Battle} battle
   * @param {Combatant | null} [appliedBy]
   * @returns {boolean} applied
   */
  applyStatus(effect, battle, appliedBy = null) {
    if (!this.alive) return false;
    if (effect.crowdControl) {
      const why = this.tags.has('ccImmune') ? 'ccImmune' : this.hasStatus(StatusId.BIND_RESIST) ? 'diminishingReturns' : null;
      if (why) {
        battle.emit({ t: 'resist', who: this.id, s: effect.id, why });
        return false;
      }
    }
    const current = this.statuses.get(effect.id);
    if (current && current.turns >= effect.turns) return true;
    this.statuses.set(effect.id, effect);
    if (appliedBy === this) this.fresh.add(effect.id);
    battle.emit({ t: 'status', who: this.id, s: effect.id, turns: effect.turns });
    return true;
  }

  /** @param {string} id @param {Battle} battle */
  removeStatus(id, battle) {
    const s = this.statuses.get(id);
    if (!s) return;
    this.statuses.delete(id);
    battle.emit({ t: 'expire', who: this.id, s: id });
  }

  /** Called at the end of the bearer's own turn. @param {Battle} battle */
  tickStatuses(battle) {
    const fresh = this.fresh;
    this.fresh = new Set();
    // Snapshot: statuses added by onExpire (e.g. bindResist) must survive this pass.
    for (const s of [...this.statuses.values()]) {
      if (fresh.has(s.id)) continue;
      s.turns -= 1;
      if (s.turns <= 0) {
        this.removeStatus(s.id, battle);
        s.onExpire?.(this, battle);
      }
    }
  }

  /**
   * Subclass hook: return a reason to cancel the hit entirely (invulnerability, friendly-fire rules).
   * @param {Hit} _hit
   * @param {Battle} _battle
   * @returns {string | null}
   */
  guardDamage(_hit, _battle) {
    return null;
  }

  /** @param {Hit} hit */
  mitigate(hit) {
    if (hit.power === 0) return 0;
    const armor = hit.kind === 'physical' ? this.def : hit.kind === 'magic' ? this.mdef : 0;
    let dmg = hit.power * (100 / (100 + armor));
    for (const s of this.statuses.values()) dmg *= s.damageTakenMultiplier;
    return Math.max(1, Math.round(dmg));
  }

  /**
   * @param {Hit} hit
   * @param {Battle} battle
   * @returns {DamageResult}
   */
  receiveDamage(hit, battle) {
    if (!Number.isFinite(hit.power) || hit.power < 0) throw new RangeError('hit.power must be a finite number >= 0');
    const by = hit.source?.id ?? null;
    if (!this.alive) return { landed: false, why: 'alreadyDown' };
    const why = this.guardDamage(hit, battle);
    if (why) {
      battle.emit({ t: 'blocked', who: this.id, by, why });
      return { landed: false, why };
    }
    const amount = Math.min(this.hp, this.mitigate(hit));
    this.hp -= amount;
    battle.emit({ t: 'dmg', who: this.id, by, amount, kind: hit.kind, hp: this.hp });
    if (this.hp > 0) return { landed: true, amount, ko: false, revived: false };

    for (const intercept of this.#defeatInterceptors) {
      if (intercept(this, hit, battle) && this.hp > 0) return { landed: true, amount, ko: false, revived: true };
    }
    this.statuses.clear();
    this.fresh.clear();
    battle.emit({ t: 'ko', who: this.id, by });
    this.onDefeated(hit, battle);
    return { landed: true, amount, ko: true, revived: false };
  }

  /** Subclass hook, runs once after a real defeat. @param {Hit} _hit @param {Battle} _battle */
  onDefeated(_hit, _battle) {}

  /**
   * Bring a downed unit back. Used by passives such as Wind Revival.
   * @param {number} hpRatio 0 < ratio <= 1
   * @param {string} why
   * @param {Battle} battle
   */
  restoreLife(hpRatio, why, battle) {
    if (!(hpRatio > 0 && hpRatio <= 1)) throw new RangeError('hpRatio must be in (0, 1]');
    this.hp = Math.max(1, Math.round(this.maxHp * hpRatio));
    battle.emit({ t: 'revive', who: this.id, hp: this.hp, why });
  }

  /** @param {number} amount @param {Battle} battle @returns {number} healed */
  heal(amount, battle) {
    if (!this.alive || amount <= 0) return 0;
    const before = this.hp;
    this.hp = Math.min(this.maxHp, this.hp + Math.round(amount));
    battle.emit({ t: 'heal', who: this.id, amount: this.hp - before, hp: this.hp });
    return this.hp - before;
  }

  /** @param {Point} to @returns {boolean} moved */
  moveTo(to) {
    if (!this.canMove) return false;
    this.position = { x: to.x, y: to.y };
    return true;
  }
}
