// @ts-check
import { Faction } from '../core/types.js';

/** @typedef {import('../core/types.js').FactionId} FactionId */
/** @typedef {import('../core/types.js').GameEvent} GameEvent */
/** @typedef {{ emit: (ev: GameEvent) => void }} Emitter */

export const SEA_CAUSEWAY = Object.freeze({
  /** 100% = this many stones. Integers avoid float drift (1 stone = 0.1%). */
  totalStones: 1000,
  /** Reached checkpoints are locked in: interruption cannot push progress below them. */
  checkpoints: [25, 50, 75],
  /** Anti-exploit cap for a single build or interrupt action. */
  maxStonesPerAction: 50,
});

/** @typedef {{ ok: true, applied: number, capped: boolean, percent: number } | { ok: false, why: string }} CausewayResult */

/**
 * "Sea Causeway Construction" (จองถนนข้ามทะเล): Ayodhya builders add stones,
 * Lanka sea creatures (the fish army) carry them away. Completed = locked at 100%.
 */
export class SeaCauseway {
  stones = 0;
  /** @type {'building' | 'completed'} */
  state = 'building';
  /** @type {Map<string, number>} stones placed per builder */
  built = new Map();
  /** @type {Map<string, number>} stones removed per creature */
  removed = new Map();
  /** Locked progress in stones (highest checkpoint reached). */
  floor = 0;

  /** @param {Partial<typeof SEA_CAUSEWAY> & { emitter?: Emitter }} [opts] */
  constructor(opts = {}) {
    const o = { ...SEA_CAUSEWAY, ...opts };
    if (!Number.isInteger(o.totalStones) || o.totalStones < 1) throw new RangeError('totalStones must be an integer >= 1');
    if (!Number.isInteger(o.maxStonesPerAction) || o.maxStonesPerAction < 1) throw new RangeError('maxStonesPerAction must be an integer >= 1');
    if (o.checkpoints.some((c, i, a) => !(c > 0 && c < 100) || (i > 0 && c <= /** @type {number} */ (a[i - 1]))))
      throw new RangeError('checkpoints must be ascending percentages between 0 and 100');
    this.totalStones = o.totalStones;
    this.maxStonesPerAction = o.maxStonesPerAction;
    this.checkpointStones = o.checkpoints.map((p) => Math.round((p / 100) * o.totalStones));
    this.emitter = opts.emitter ?? null;
  }

  get percent() {
    return Math.round((this.stones / this.totalStones) * 1000) / 10;
  }

  /** @param {string} builderId @param {FactionId} faction @param {number} stones @returns {CausewayResult} */
  build(builderId, faction, stones) {
    const why = this.#validate(faction, Faction.AYODHYA, stones);
    if (why) return { ok: false, why };
    const want = Math.min(stones, this.maxStonesPerAction);
    const applied = Math.min(want, this.totalStones - this.stones);
    this.stones += applied;
    this.built.set(builderId, (this.built.get(builderId) ?? 0) + applied);
    this.#emit({ t: 'causeway', kind: 'build', who: builderId, stones: applied, percent: this.percent });
    this.#lockCheckpoints();
    return { ok: true, applied, capped: want < stones, percent: this.percent };
  }

  /** @param {string} creatureId @param {FactionId} faction @param {number} stones @returns {CausewayResult} */
  interrupt(creatureId, faction, stones) {
    const why = this.#validate(faction, Faction.LANKA, stones);
    if (why) return { ok: false, why };
    const want = Math.min(stones, this.maxStonesPerAction);
    const applied = Math.min(want, this.stones - this.floor);
    this.stones -= applied;
    this.removed.set(creatureId, (this.removed.get(creatureId) ?? 0) + applied);
    this.#emit({ t: 'causeway', kind: 'interrupt', who: creatureId, stones: applied, percent: this.percent });
    return { ok: true, applied, capped: want < stones, percent: this.percent };
  }

  /**
   * Resolve one round of simultaneous actions by NET effect, so action order inside a round never matters.
   * Each actor is still capped per action; per-actor stats record what they actually moved.
   * @param {{ builders?: { id: string, stones: number }[], creatures?: { id: string, stones: number }[] }} round
   */
  resolveRound({ builders = [], creatures = [] }) {
    if (this.state === 'completed') return { net: 0, percent: this.percent };
    const sum = (/** @type {{ id: string, stones: number }[]} */ list) =>
      list.reduce((n, a) => n + (Number.isInteger(a.stones) && a.stones > 0 ? Math.min(a.stones, this.maxStonesPerAction) : 0), 0);
    const buildTotal = sum(builders);
    const removeTotal = sum(creatures);
    const net = buildTotal - removeTotal;
    if (net > 0) {
      // Credit builders proportionally to the net stones that actually landed.
      const landed = Math.min(net, this.totalStones - this.stones);
      this.#creditShares(this.built, builders, buildTotal, landed);
      this.stones += landed;
      this.#emit({ t: 'causeway', kind: 'build', who: null, stones: landed, percent: this.percent });
      this.#lockCheckpoints();
      return { net: landed, percent: this.percent };
    }
    if (net < 0) {
      const taken = Math.min(-net, this.stones - this.floor);
      this.#creditShares(this.removed, creatures, removeTotal, taken);
      this.stones -= taken;
      this.#emit({ t: 'causeway', kind: 'interrupt', who: null, stones: taken, percent: this.percent });
      return { net: -taken, percent: this.percent };
    }
    return { net: 0, percent: this.percent };
  }

  snapshot() {
    return {
      state: this.state,
      percent: this.percent,
      floorPercent: Math.round((this.floor / this.totalStones) * 1000) / 10,
      stones: this.stones,
      totalStones: this.totalStones,
    };
  }

  /** @param {FactionId} faction @param {FactionId} expected @param {number} stones */
  #validate(faction, expected, stones) {
    if (this.state === 'completed') return 'completed';
    if (faction !== expected) return 'wrongFaction';
    if (!Number.isInteger(stones) || stones < 1) return 'badAmount';
    return null;
  }

  #lockCheckpoints() {
    for (const cp of this.checkpointStones) {
      if (this.stones >= cp && this.floor < cp) {
        this.floor = cp;
        this.#emit({ t: 'causeway', kind: 'checkpoint', who: null, stones: cp, percent: (cp / this.totalStones) * 100 });
      }
    }
    if (this.stones >= this.totalStones) {
      this.state = 'completed';
      this.floor = this.totalStones;
      this.#emit({ t: 'causeway', kind: 'complete', who: null, stones: this.totalStones, percent: 100 });
    }
  }

  /**
   * Largest-remainder split so credited shares always sum to exactly `amount`.
   * @param {Map<string, number>} ledger @param {{ id: string, stones: number }[]} actors @param {number} total @param {number} amount
   */
  #creditShares(ledger, actors, total, amount) {
    if (amount <= 0 || total <= 0) return;
    const valid = actors.filter((a) => Number.isInteger(a.stones) && a.stones > 0);
    const parts = valid.map((a) => {
      const exact = (Math.min(a.stones, this.maxStonesPerAction) / total) * amount;
      return { id: a.id, whole: Math.floor(exact), rest: exact - Math.floor(exact) };
    });
    let left = amount - parts.reduce((n, p) => n + p.whole, 0);
    for (const p of [...parts].sort((a, b) => b.rest - a.rest || a.id.localeCompare(b.id))) {
      if (left <= 0) break;
      p.whole += 1;
      left -= 1;
    }
    for (const p of parts) if (p.whole) ledger.set(p.id, (ledger.get(p.id) ?? 0) + p.whole);
  }

  /** @param {GameEvent} ev */
  #emit(ev) {
    this.emitter?.emit(ev);
  }
}
