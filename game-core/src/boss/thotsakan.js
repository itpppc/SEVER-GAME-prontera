// @ts-check
import { Combatant } from '../combat/combatant.js';

/** @typedef {import('../combat/combatant.js').CombatantInit} CombatantInit */
/** @typedef {import('../combat/combatant.js').Hit} Hit */
/** @typedef {import('../combat/battle.js').Battle} Battle */
/** @typedef {import('../core/types.js').Point} Point */

/** Raid phases. Ids are shared with the HUD spec ("หัวใจทศกัณฐ์"). */
export const BossPhase = Object.freeze({
  /** Phase 1: heart hidden in its box, boss takes no damage of any kind. */
  HEART_SEALED: 'heartSealed',
  /** Phase 2: box destroyed, boss is vulnerable and enraged. */
  HEART_EXPOSED: 'heartExposed',
});

/** @typedef {typeof BossPhase[keyof typeof BossPhase]} BossPhaseId */

/**
 * The box that holds Thotsakan's heart (กล่องดวงใจ). A static object on the field:
 * it never acts, ignores crowd control, and only the opposing faction can damage it.
 */
export class HeartBox extends Combatant {
  /**
   * @param {{ id: string, owner: ThotsakanBoss, maxHp: number, def?: number, mdef?: number, position?: Point }} init
   */
  constructor(init) {
    super({ id: init.id, name: 'กล่องดวงใจ', team: init.owner.team, maxHp: init.maxHp, def: init.def ?? 60, mdef: init.mdef ?? 60, position: init.position, tags: ['heartBox', 'object', 'ccImmune'] });
    this.owner = init.owner;
  }

  /** @override @param {Hit} hit */
  guardDamage(hit) {
    if (!hit.source) return 'noSource';
    if (hit.source.team === this.team) return 'friendlyFire';
    return null;
  }

  /** @override @param {Hit} hit @param {Battle} battle */
  onDefeated(hit, battle) {
    this.owner.exposeHeart(battle, hit.source?.id ?? null);
  }
}

/** Thotsakan (ทศกัณฐ์), Lord of Lanka: two-phase raid boss driven by the Heart Removal system. */
export class ThotsakanBoss extends Combatant {
  /** @type {BossPhaseId} */
  phase = BossPhase.HEART_SEALED;

  /**
   * @param {Omit<CombatantInit, 'maxHp'> & {
   *   maxHp?: number,
   *   heartBox: { id?: string, maxHp: number, def?: number, mdef?: number, position?: Point },
   *   enrageAtkMultiplier?: number,
   * }} init
   */
  constructor(init) {
    super({ maxHp: 20000, atk: 220, def: 80, matk: 160, mdef: 70, spd: 10, ...init, tags: ['boss', 'ccImmune', ...(init.tags ?? [])] });
    this.enrageAtkMultiplier = init.enrageAtkMultiplier ?? 1.25;
    this.heartBox = new HeartBox({ id: init.heartBox.id ?? `${this.id}:heartBox`, owner: this, ...init.heartBox });
  }

  get invulnerable() {
    return this.phase === BossPhase.HEART_SEALED;
  }

  /** @override */
  guardDamage() {
    return this.invulnerable ? 'heartSealed' : null;
  }

  /**
   * Phase 1 -> 2. Idempotent; called by the HeartBox when it is destroyed.
   * @param {Battle} battle
   * @param {string | null} byId who broke the box (for rewards and the log)
   * @returns {boolean} true if the phase changed
   */
  exposeHeart(battle, byId) {
    if (this.phase === BossPhase.HEART_EXPOSED) return false;
    const from = this.phase;
    this.phase = BossPhase.HEART_EXPOSED;
    this.atk = Math.round(this.atk * this.enrageAtkMultiplier);
    this.matk = Math.round(this.matk * this.enrageAtkMultiplier);
    this.heartBrokenBy = byId;
    battle.emit({ t: 'phase', who: this.id, from, to: this.phase });
    return true;
  }
}
