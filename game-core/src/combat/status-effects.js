// @ts-check

/** @typedef {import('./combatant.js').Combatant} Combatant */
/** @typedef {import('./battle.js').Battle} Battle */

/**
 * @typedef {object} StatusSpec
 * @property {string} id                     camelCase id, same style as website/rpg STATUS keys
 * @property {string} label                  Thai label for the HUD
 * @property {number} turns                  ticks down at the end of the bearer's own turn
 * @property {string | null} [sourceId]
 * @property {boolean} [crowdControl]        blocked by the `ccImmune` tag and by `bindResist`
 * @property {boolean} [preventsActions]     bearer skips its turn
 * @property {boolean} [preventsMovement]
 * @property {number} [damageTakenMultiplier]
 * @property {(bearer: Combatant, battle: Battle) => void} [onExpire]
 */

export class StatusEffect {
  /** @param {StatusSpec} spec */
  constructor(spec) {
    if (!spec.id) throw new TypeError('status id is required');
    if (!Number.isInteger(spec.turns) || spec.turns < 1) throw new RangeError(`status ${spec.id}: turns must be an integer >= 1`);
    this.id = spec.id;
    this.label = spec.label;
    this.turns = spec.turns;
    this.sourceId = spec.sourceId ?? null;
    this.crowdControl = spec.crowdControl ?? false;
    this.preventsActions = spec.preventsActions ?? false;
    this.preventsMovement = spec.preventsMovement ?? false;
    this.damageTakenMultiplier = spec.damageTakenMultiplier ?? 1;
    this.onExpire = spec.onExpire;
  }
}

export const StatusId = Object.freeze({
  NAGA_BOUND: 'nagaBound',
  BIND_RESIST: 'bindResist',
});

/**
 * Short immunity after a bind ends (diminishing returns), so two Naga Sorcerers cannot chain-lock a target forever.
 * @param {number} turns
 */
export const bindResist = (turns) => new StatusEffect({ id: StatusId.BIND_RESIST, label: 'ต้านบ่วง', turns });

/**
 * Naga coils: no movement, no action. Grants `bindResist` when it wears off.
 * @param {{ turns: number, resistTurns: number, sourceId: string }} opts
 */
export const nagaBound = ({ turns, resistTurns, sourceId }) =>
  new StatusEffect({
    id: StatusId.NAGA_BOUND,
    label: 'บ่วงนาค',
    turns,
    sourceId,
    crowdControl: true,
    preventsActions: true,
    preventsMovement: true,
    onExpire: (bearer, battle) => {
      if (resistTurns > 0) bearer.applyStatus(bindResist(resistTurns), battle);
    },
  });
