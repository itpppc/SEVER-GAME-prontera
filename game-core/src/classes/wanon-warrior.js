// @ts-check
import { Combatant } from '../combat/combatant.js';
import { Skill, Strike } from '../combat/skill.js';

/** @typedef {import('../combat/combatant.js').CombatantInit} CombatantInit */
/** @typedef {import('../combat/combatant.js').Hit} Hit */
/** @typedef {import('../combat/battle.js').Battle} Battle */

export const WIND_REVIVAL = Object.freeze({
  /** Minimum battle wind (0-100) for the wind god to answer. */
  windThreshold: 40,
  /** HP restored, as a share of maxHp. */
  hpRatio: 0.3,
  /** Revivals per battle. */
  charges: 1,
});

/**
 * Passive "Wind Revival" (คืนชีพด้วยลม): the monkey warrior is a child of the wind;
 * when struck down while the wind is strong enough, the wind breathes life back into it.
 * Fails when out of charges, the wind is too calm, or the killing hit carries `sealsRevival`.
 */
export class WindRevival {
  /** @param {Partial<typeof WIND_REVIVAL>} [opts] */
  constructor(opts = {}) {
    const o = { ...WIND_REVIVAL, ...opts };
    if (!(o.hpRatio > 0 && o.hpRatio <= 1)) throw new RangeError('hpRatio must be in (0, 1]');
    if (!Number.isInteger(o.charges) || o.charges < 0) throw new RangeError('charges must be an integer >= 0');
    this.windThreshold = o.windThreshold;
    this.hpRatio = o.hpRatio;
    this.charges = o.charges;
  }

  /** @param {Hit} hit @param {Battle} battle @returns {string | null} why it cannot trigger */
  blockReason(hit, battle) {
    if (this.charges <= 0) return 'noCharges';
    if (hit.tags?.includes('sealsRevival')) return 'revivalSealed';
    if (battle.wind < this.windThreshold) return 'calmWind';
    return null;
  }

  /** @param {Combatant} owner */
  attach(owner) {
    owner.addDefeatInterceptor((self, hit, battle) => {
      if (this.blockReason(hit, battle)) return false;
      this.charges -= 1;
      // A fresh breath of wind also shakes off crowd control.
      for (const s of [...self.statuses.values()]) if (s.crowdControl) self.removeStatus(s.id, battle);
      self.restoreLife(this.hpRatio, 'windRevival', battle);
      return true;
    });
    return this;
  }
}

/**
 * Active "Call the Wind" (เรียกลมพระพาย): raises battle wind so Wind Revival can trigger.
 * @extends {Skill<null>}
 */
export class CallTheWind extends Skill {
  /** @param {{ amount?: number, mpCost?: number, cd?: number }} [opts] */
  constructor(opts = {}) {
    super({ id: 'callTheWind', name: 'เรียกลมพระพาย', mpCost: opts.mpCost ?? 20, cd: opts.cd ?? 3 });
    this.amount = opts.amount ?? 30;
  }

  /** @override @param {Combatant} caster @param {Battle} battle */
  execute(caster, battle) {
    battle.emit({ t: 'act', who: caster.id, name: this.name, targets: [] });
    battle.setWind(battle.wind + this.amount);
  }
}

/** Wanon Warrior (นักรบวานร): fast melee assassin of the Ayodhya side. */
export class WanonWarrior extends Combatant {
  /** @param {Omit<CombatantInit, 'maxHp'> & { maxHp?: number, windRevival?: Partial<typeof WIND_REVIVAL> }} init */
  constructor(init) {
    super({ maxHp: 1100, maxMp: 60, atk: 110, def: 45, matk: 20, mdef: 30, spd: 17, ...init, tags: ['wanon', ...(init.tags ?? [])] });
    this.windRevival = new WindRevival(init.windRevival).attach(this);
    this.skills = {
      strike: new Strike({ id: 'tailStrike', name: 'ฟาดหางวานร', kind: 'physical', power: 1, range: 1.5 }),
      callTheWind: new CallTheWind(),
    };
  }
}
