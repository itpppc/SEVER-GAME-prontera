// @ts-check
import { EventBus } from '../core/event-bus.js';
import { makeRng } from '../core/rng.js';

/** @typedef {import('./combatant.js').Combatant} Combatant */
/** @typedef {import('../core/types.js').GameEvent} GameEvent */
/** @typedef {import('../core/types.js').FactionId} FactionId */
/** @typedef {import('../core/types.js').Point} Point */

/**
 * Turn flow (mirrors website/rpg/engine.js):
 *   const order = battle.turnOrder();          // fastest first
 *   for (const u of order) {
 *     const { skip } = battle.beginTurn(u);    // ticks cooldowns, consumes the turn if bound
 *     if (!skip) { skill.use(u, battle, target); battle.endTurn(u); }
 *   }
 *   battle.nextRound();
 */
export class Battle {
  /** @type {Map<string, Combatant>} */
  #units = new Map();
  /** @type {GameEvent[]} */
  log = [];
  round = 1;

  /** @param {{ seed?: number, wind?: number, bus?: EventBus }} [opts] */
  constructor(opts = {}) {
    this.rng = makeRng(opts.seed);
    this.bus = opts.bus ?? new EventBus();
    /** Wind strength 0-100. Drives Wind Revival; raised by skills or the arena. */
    this.wind = 0;
    if (opts.wind != null) this.setWind(opts.wind);
  }

  /** @param {...Combatant} units */
  add(...units) {
    for (const u of units) {
      if (this.#units.has(u.id)) throw new Error(`duplicate combatant id: ${u.id}`);
      this.#units.set(u.id, u);
    }
    return this;
  }

  /** @param {string} id */
  get(id) {
    return this.#units.get(id) ?? null;
  }

  /** @param {{ team?: FactionId, includeDown?: boolean }} [filter] */
  units(filter = {}) {
    return [...this.#units.values()].filter(
      (u) => (filter.team == null || u.team === filter.team) && (filter.includeDown || u.alive),
    );
  }

  /** @param {Combatant} u */
  foesOf(u) {
    return this.units().filter((x) => x.team !== u.team);
  }

  /** @param {Combatant} u */
  friendsOf(u) {
    return this.units({ team: u.team });
  }

  /** Living units within `radius` tiles (Euclidean) of `center`. @param {Point} center @param {number} radius */
  inRadius(center, radius) {
    const r2 = radius * radius;
    return this.units().filter((u) => (u.position.x - center.x) ** 2 + (u.position.y - center.y) ** 2 <= r2);
  }

  /** @param {number} value */
  setWind(value) {
    if (!Number.isFinite(value)) throw new RangeError('wind must be finite');
    this.wind = Math.min(100, Math.max(0, Math.round(value)));
    this.emit({ t: 'wind', value: this.wind });
  }

  /** @param {GameEvent} ev */
  emit(ev) {
    this.log.push(ev);
    this.bus.emit(ev);
  }

  /** Fastest first; objects (e.g. the Heart Box) never take turns. Ties: Ayodhya first, then id for determinism. */
  turnOrder() {
    return this.units()
      .filter((u) => !u.tags.has('object'))
      .sort((a, b) => b.spd - a.spd || (a.team === b.team ? 0 : a.team === 'ayodhya' ? -1 : 1) || a.id.localeCompare(b.id));
  }

  /**
   * Start of a unit's own turn. A bound unit loses the turn, and its statuses still tick.
   * @param {Combatant} u
   * @returns {{ skip: boolean, why?: string }}
   */
  beginTurn(u) {
    if (!u.alive) return { skip: true, why: 'ko' };
    for (const k of Object.keys(u.cds)) if ((u.cds[k] ?? 0) > 0) u.cds[k] = (u.cds[k] ?? 0) - 1;
    if (!u.canAct) {
      const blocker = [...u.statuses.values()].find((s) => s.preventsActions);
      const why = blocker?.id ?? 'cannotAct';
      this.emit({ t: 'skip', who: u.id, why });
      this.endTurn(u);
      return { skip: true, why };
    }
    return { skip: false };
  }

  /** @param {Combatant} u */
  endTurn(u) {
    if (u.alive) u.tickStatuses(this);
  }

  nextRound() {
    this.round += 1;
  }

  /** The faction left standing, or null while both still have fighters (objects do not count). */
  winner() {
    const standing = new Set(this.units().filter((u) => !u.tags.has('object')).map((u) => u.team));
    return standing.size === 1 ? /** @type {FactionId} */ ([...standing][0]) : null;
  }

  /**
   * Run `fn` and return the events it produced, like the per-action `ev` arrays in website/rpg.
   * @template T
   * @param {() => T} fn
   * @returns {{ result: T, events: GameEvent[] }}
   */
  capture(fn) {
    const start = this.log.length;
    const result = fn();
    return { result, events: this.log.slice(start) };
  }
}
