// @ts-check

/** @typedef {import('./types.js').GameEvent} GameEvent */
/** @typedef {(ev: GameEvent) => void} Listener */

/**
 * Minimal pub/sub. A throwing listener (e.g. a UI bug) is reported but never corrupts combat state.
 */
export class EventBus {
  /** @type {Set<Listener>} */
  #listeners = new Set();
  /** @type {(err: unknown) => void} */
  #onError;

  /** @param {{ onError?: (err: unknown) => void }} [opts] */
  constructor(opts = {}) {
    this.#onError = opts.onError ?? ((err) => console.error('[game-core] listener failed', err));
  }

  /** @param {Listener} fn @returns {() => void} unsubscribe */
  on(fn) {
    this.#listeners.add(fn);
    return () => this.#listeners.delete(fn);
  }

  /** @param {GameEvent} ev */
  emit(ev) {
    for (const fn of [...this.#listeners]) {
      try {
        fn(ev);
      } catch (err) {
        this.#onError(err);
      }
    }
  }
}
