// @ts-check
import { Combatant } from '../combat/combatant.js';
import { Skill, Strike } from '../combat/skill.js';
import { nagaBound } from '../combat/status-effects.js';

/** @typedef {import('../combat/combatant.js').CombatantInit} CombatantInit */
/** @typedef {import('../combat/battle.js').Battle} Battle */
/** @typedef {import('../core/types.js').Point} Point */

export const NAGA_BINDING = Object.freeze({
  mpCost: 30,
  cd: 4,
  /** Max distance from caster to the target point. */
  castRange: 6,
  /** AOE radius around the target point. */
  radius: 2,
  /** Magic damage, as a share of matk. */
  power: 0.6,
  /** Bound turns (no move, no action). */
  turns: 2,
  /** Immunity turns after the bind ends (diminishing returns). */
  resistTurns: 1,
});

/**
 * "Naga Binding" (บ่วงนาคบาศ): ground-targeted AOE. Enemies in the circle take magic damage,
 * then survivors are bound. Allies are never hit. `ccImmune` units and units with `bindResist` resist.
 * @extends {Skill<Point>}
 */
export class NagaBinding extends Skill {
  /** @param {Partial<typeof NAGA_BINDING>} [opts] */
  constructor(opts = {}) {
    const o = { ...NAGA_BINDING, ...opts };
    super({ id: 'nagaBinding', name: 'บ่วงนาคบาศ', mpCost: o.mpCost, cd: o.cd });
    this.castRange = o.castRange;
    this.radius = o.radius;
    this.power = o.power;
    this.turns = o.turns;
    this.resistTurns = o.resistTurns;
  }

  /** @override @param {Combatant} caster @param {Battle} _battle @param {Point} point */
  validateTarget(caster, _battle, point) {
    if (!point || !Number.isFinite(point.x) || !Number.isFinite(point.y)) return 'badTarget';
    return Math.hypot(point.x - caster.position.x, point.y - caster.position.y) > this.castRange ? 'outOfRange' : null;
  }

  /** @override @param {Combatant} caster @param {Battle} battle @param {Point} point */
  execute(caster, battle, point) {
    const targets = battle.inRadius(point, this.radius).filter((u) => u.team !== caster.team);
    battle.emit({ t: 'act', who: caster.id, name: this.name, targets: targets.map((u) => u.id) });
    for (const t of targets) {
      t.receiveDamage({ power: caster.matk * this.power, kind: 'magic', source: caster }, battle);
      if (t.alive) t.applyStatus(nagaBound({ turns: this.turns, resistTurns: this.resistTurns, sourceId: caster.id }), battle, caster);
    }
  }
}

/** Naga Sorcerer (หมอผีนาคา): Lanka-side spellcaster built around crowd control. */
export class NagaSorcerer extends Combatant {
  /** @param {Omit<CombatantInit, 'maxHp'> & { maxHp?: number, nagaBinding?: Partial<typeof NAGA_BINDING> }} init */
  constructor(init) {
    super({ maxHp: 800, maxMp: 120, atk: 40, def: 30, matk: 130, mdef: 60, spd: 12, ...init, tags: ['naga', ...(init.tags ?? [])] });
    this.skills = {
      venomBolt: new Strike({ id: 'venomBolt', name: 'ศรพิษนาคา', kind: 'magic', power: 1, range: 6 }),
      nagaBinding: new NagaBinding(init.nagaBinding),
    };
  }
}
