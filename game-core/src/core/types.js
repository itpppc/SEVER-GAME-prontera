// @ts-check

/** The two sides of the war. Combatants and objectives use the same ids. */
export const Faction = Object.freeze({ AYODHYA: 'ayodhya', LANKA: 'lanka' });

/** @typedef {typeof Faction[keyof typeof Faction]} FactionId */
/** @typedef {{ x: number, y: number }} Point */
/** @typedef {'physical' | 'magic' | 'true'} DamageType */

/**
 * One battle event. The `t`/`who` shape matches the event log of website/rpg/engine.js,
 * so the same renderer can play both.
 * @typedef {(
 *   | { t: 'act', who: string, name: string, targets: string[] }
 *   | { t: 'dmg', who: string, by: string | null, amount: number, kind: DamageType, hp: number }
 *   | { t: 'blocked', who: string, by: string | null, why: string }
 *   | { t: 'ko', who: string, by: string | null }
 *   | { t: 'revive', who: string, hp: number, why: string }
 *   | { t: 'status', who: string, s: string, turns: number }
 *   | { t: 'resist', who: string, s: string, why: string }
 *   | { t: 'expire', who: string, s: string }
 *   | { t: 'skip', who: string, why: string }
 *   | { t: 'heal', who: string, amount: number, hp: number }
 *   | { t: 'phase', who: string, from: string, to: string }
 *   | { t: 'wind', value: number }
 *   | { t: 'causeway', kind: 'build' | 'interrupt' | 'checkpoint' | 'complete', who: string | null, stones: number, percent: number }
 * )} GameEvent
 */

export {};
