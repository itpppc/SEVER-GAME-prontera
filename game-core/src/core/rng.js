// @ts-check

/** @typedef {() => number} Rng Returns a float in [0, 1). */

/**
 * Seeded mulberry32 (same algorithm as website/rpg/engine.js) so replays and tests are deterministic.
 * Omit the seed to fall back to Math.random.
 * @param {number} [seed]
 * @returns {Rng}
 */
export function makeRng(seed) {
  if (seed == null) return Math.random;
  let s = seed >>> 0;
  return () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
