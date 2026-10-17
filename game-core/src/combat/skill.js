// @ts-check

/** @typedef {import('./combatant.js').Combatant} Combatant */
/** @typedef {import('./battle.js').Battle} Battle */
/** @typedef {import('../core/types.js').DamageType} DamageType */
/** @typedef {import('../core/types.js').GameEvent} GameEvent */

/** @typedef {{ ok: true, events: GameEvent[] } | { ok: false, why: string }} SkillResult */

/**
 * Template method: `use` runs the shared checks (alive, can act, MP, cooldown, target),
 * pays the cost, then calls `execute`. Subclasses implement `execute` and optionally `validateTarget`.
 * @template T target type (a Combatant, a Point, or null for self-casts)
 */
export class Skill {
  /** @param {{ id: string, name: string, mpCost?: number, cd?: number }} spec */
  constructor(spec) {
    if (!spec.id) throw new TypeError('skill id is required');
    this.id = spec.id;
    this.name = spec.name;
    this.mpCost = spec.mpCost ?? 0;
    this.cd = spec.cd ?? 0;
    if (!Number.isInteger(this.mpCost) || this.mpCost < 0) throw new RangeError(`${spec.id}: mpCost must be an integer >= 0`);
    if (!Number.isInteger(this.cd) || this.cd < 0) throw new RangeError(`${spec.id}: cd must be an integer >= 0`);
  }

  /** @param {Combatant} caster @param {Battle} battle @param {T} target @returns {string | null} */
  check(caster, battle, target) {
    if (!caster.alive) return 'casterDown';
    if (!caster.canAct) return 'cannotAct';
    if ((caster.cds[this.id] ?? 0) > 0) return 'onCooldown';
    if (caster.mp < this.mpCost) return 'notEnoughMp';
    return this.validateTarget(caster, battle, target);
  }

  /** @param {Combatant} _caster @param {Battle} _battle @param {T} _target @returns {string | null} */
  validateTarget(_caster, _battle, _target) {
    return null;
  }

  /** @param {Combatant} caster @param {Battle} battle @param {T} target @returns {SkillResult} */
  use(caster, battle, target) {
    const why = this.check(caster, battle, target);
    if (why) return { ok: false, why };
    caster.mp -= this.mpCost;
    // +1 because beginTurn ticks once before the next choice (website/rpg convention).
    if (this.cd) caster.cds[this.id] = this.cd + 1;
    const { events } = battle.capture(() => this.execute(caster, battle, target));
    return { ok: true, events };
  }

  /**
   * @abstract
   * @param {Combatant} _caster @param {Battle} _battle @param {T} _target
   * @returns {void}
   */
  execute(_caster, _battle, _target) {
    throw new Error(`${this.id}: execute() not implemented`);
  }
}

/**
 * Single-target hit scaled from atk (physical) or matk (magic).
 * @extends {Skill<Combatant>}
 */
export class Strike extends Skill {
  /** @param {{ id: string, name: string, kind: DamageType, power: number, range?: number, mpCost?: number, cd?: number }} spec */
  constructor(spec) {
    super(spec);
    this.kind = spec.kind;
    this.power = spec.power;
    this.range = spec.range ?? Infinity;
  }

  /** @override @param {Combatant} caster @param {Battle} _battle @param {Combatant} target */
  validateTarget(caster, _battle, target) {
    if (!target?.alive) return 'badTarget';
    if (target.team === caster.team) return 'friendlyTarget';
    const d = Math.hypot(target.position.x - caster.position.x, target.position.y - caster.position.y);
    return d > this.range ? 'outOfRange' : null;
  }

  /** @override @param {Combatant} caster @param {Battle} battle @param {Combatant} target */
  execute(caster, battle, target) {
    battle.emit({ t: 'act', who: caster.id, name: this.name, targets: [target.id] });
    const base = this.kind === 'magic' ? caster.matk : caster.atk;
    target.receiveDamage({ power: base * this.power, kind: this.kind, source: caster }, battle);
  }
}
