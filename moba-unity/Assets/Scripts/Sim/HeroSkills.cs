using System;
using System.Collections.Generic;

namespace Ramakien.Moba.Sim
{
    /// <summary>Skill rules for the two launch heroes. Numbers follow FOUNDATION-th.md section 1.1 and HERO-KITS-th.md section 2.3.
    /// Mana is left out of this slice (cooldowns only) to keep the first playable simple.</summary>
    public static class HeroSkills
    {
        public static int Rank(Unit h) { return SimMath.Clamp((h.Level - 1) / 3, 0, 5); }
        static int Pick(int rank, params int[] v) { return v[Math.Min(rank, v.Length - 1)]; }
                static int Cd(double seconds) { return (int)(seconds * SimMath.TickHz); }

        /// <summary>CD in ticks for UI.</summary>
        public static int BaseCooldown(HeroId id, int slot, int rank)
        {
            if (id == HeroId.Rama)
            {
                if (slot == 0) return Cd(8); if (slot == 1) return Cd(12); return Cd(70);
            }
            int[] q = { 90, 85, 80, 75, 70, 65 }, e = { 140, 132, 124, 116, 108, 100 }, r = { 80, 70, 60, 60, 60, 60 };   // q,e in 1/10 s
            if (slot == 0) return q[Math.Min(rank, 5)] * SimMath.TickHz / 10;
            if (slot == 1) return e[Math.Min(rank, 5)] * SimMath.TickHz / 10;
            return r[Math.Min(rank, 5)] * SimMath.TickHz;
        }

        public static bool Cast(World w, Unit h, int slot, Vec2 aim)
        {
            if (h.SkillCd[slot] > 0 || h.ChargeTicks > 0) return false;
            Vec2 dir = aim - h.Pos;
            if (dir.SqrLength < 25) dir = h.Facing.SqrLength > 0 ? h.Facing : new Vec2(-World.Sign(h.Team), 0);
            h.Facing = dir;
            bool ok = h.Hero == HeroId.Rama ? CastRama(w, h, slot, dir) : CastThotsakan(w, h, slot, dir);
            if (ok)
            {
                if (!(h.Hero == HeroId.Thotsakan && slot == 0 && h.ComboStep > 0))
                    h.SkillCd[slot] = BaseCooldown(h.Hero, slot, Rank(h));
                w.Events.Add(new SimEvent { Type = SimEvent.T.Skill, A = h.Id, B = slot, P = h.Pos, Q = h.Pos + dir.WithLength(500) });
            }
            return ok;
        }

        // ---------------------------------------------------------------- Phra Ram (Marksman)
        static bool CastRama(World w, Unit h, int slot, Vec2 dir)
        {
            int rank = Rank(h);
            switch (slot)
            {
                case 0: // Q ศรกระจาย: fan of 5 arrows, 30 degrees, 180 (+0.8 AD) each, repeated hits on one target count 50%
                {
                    int baseD = Pick(rank, 110, 140, 160, 180, 200, 220);
                    var hit = new Dictionary<int, int>();
                    for (int i = -2; i <= 2; i++)
                    {
                        Vec2 d = Rotate(dir, i * 7500);       // 7.5 degrees apart = 30 total
                        Vec2 end = h.Pos + d.WithLength(900);
                        for (int k = 0; k < w.Units.Count; k++)
                        {
                            var u = w.Units[k];
                            if (!u.Alive || u.Team == h.Team || u.Kind == UnitKind.HeartBox) continue;
                            long r = u.Radius + 40;
                            if (SimMath.SqrDistToSegment(u.Pos, h.Pos, end) > r * r) continue;
                            int n; hit.TryGetValue(u.Id, out n);
                            hit[u.Id] = n + 1;
                            int raw = baseD + h.EffectiveAd * 8 / 10;
                            if (n > 0) raw /= 2;
                            w.Hit(h, u, raw, DamageType.Physical);
                        }
                    }
                    return true;
                }
                case 1: // E ก้าวเทพ: 4 m dash, next basic attack +40% range and +50% damage
                {
                    h.Pos = h.Pos + dir.WithLength(400);
                    h.Pos = new Vec2(SimMath.Clamp(h.Pos.X, -World.LaneHalf, World.LaneHalf), SimMath.Clamp(h.Pos.Z, -2800, 2800));
                    h.EmpoweredTicks = 4 * SimMath.TickHz;
                    return true;
                }
                default: // R ศรพรหมาสตร์: 1.25 s charge (aim shown to both teams), then 60 m piercing beam
                    h.ChargeTicks = Cd(1.25); h.ChargeDir = dir;
                    w.Events.Add(new SimEvent { Type = SimEvent.T.Beam, A = h.Id, B = 0, P = h.Pos, Q = h.Pos + dir.WithLength(6000) });
                    return true;
            }
        }

        public static void FireCharged(World w, Unit h)
        {
            Vec2 dir = h.ChargeDir;
            Vec2 end = h.Pos + dir.WithLength(6000);
            int rank = Rank(h);
            int baseD = Pick(rank, 300, 340, 380, 400, 440, 480);
            bool killedHero = false;
            for (int k = 0; k < w.Units.Count; k++)
            {
                var u = w.Units[k];
                if (!u.Alive || u.Team == h.Team || u.Kind == UnitKind.HeartBox) continue;
                long r = u.Radius + 80;
                if (SimMath.SqrDistToSegment(u.Pos, h.Pos, end) > r * r) continue;
                bool wasHero = u.Kind == UnitKind.Hero;
                int missing = u.MaxHp - u.Hp;
                w.Hit(h, u, baseD + h.EffectiveAd * 12 / 10, DamageType.Physical);
                if (u.Alive && missing > 0) w.Hit(h, u, (u.MaxHp - u.Hp) * 15 / 100, DamageType.True);
                if (wasHero && !u.Alive) killedHero = true;
            }
            w.Events.Add(new SimEvent { Type = SimEvent.T.Beam, A = h.Id, B = 1, P = h.Pos, Q = end });
            h.SkillCd[2] = BaseCooldown(HeroId.Rama, 2, rank);
            if (killedHero) h.SkillCd[2] = h.SkillCd[2] * 60 / 100;      // refund 40%
        }

        // ---------------------------------------------------------------- Thotsakan (Warrior)
        static bool CastThotsakan(World w, Unit h, int slot, Vec2 dir)
        {
            int rank = Rank(h);
            switch (slot)
            {
                case 0: // Q พระขรรค์สิบหน้า: 120 degree cone, 3 strokes inside 4 s; stroke 3 is 150% and slows
                {
                    int step = h.ComboStep;               // 0,1,2
                    int baseD = Pick(rank, 80, 110, 140, 170, 200, 230);
                    int raw = baseD + h.EffectiveAd * 5 / 10;
                    if (step == 2) raw = raw * 150 / 100;
                    if (step == 2) h.Pos = h.Pos + dir.WithLength(200);
                    int faces = 0;
                    for (int k = 0; k < w.Units.Count; k++)
                    {
                        var u = w.Units[k];
                        if (!u.Alive || u.Team == h.Team || u.Kind == UnitKind.HeartBox) continue;
                        if (!SimMath.InCone(h.Pos, dir, u.Pos, 400, 500, u.Radius)) continue;
                        w.Hit(h, u, raw, DamageType.Physical);
                        if (step == 2 && u.Alive) u.Status.ApplySlow(300, Cd(1.5));
                        if (u.Kind == UnitKind.Hero) faces = 1;
                    }
                    AddFaces(h, faces);
                    h.ComboStep = (step + 1) % 3;
                    h.ComboWindow = h.ComboStep == 0 ? 0 : 4 * SimMath.TickHz;
                    if (h.ComboStep != 0) h.SkillCd[0] = Cd(0.5);   // short gap between strokes
                    else h.SkillCd[0] = BaseCooldown(HeroId.Thotsakan, 0, rank);
                    return true;
                }
                case 1: // W สิบเศียรคำราม: 3.5 m roar, magic damage, -20% enemy attack for 3 s
                {
                    int raw = Pick(rank, 100, 140, 180, 220, 260, 300) + h.Stats.Hp * 4 / 100;
                    int hits = 0;
                    for (int k = 0; k < w.Units.Count; k++)
                    {
                        var u = w.Units[k];
                        if (!u.Alive || u.Team == h.Team || u.Kind == UnitKind.HeartBox) continue;
                        if (!Vec2.Within(h.Pos, u.Pos, 350 + u.Radius)) continue;
                        w.Hit(h, u, raw, DamageType.Magic);
                        u.Status.AdDownPermille = 200; u.Status.AdDownTicks = Cd(3);
                        if (u.Kind == UnitKind.Hero) hits = 1;
                    }
                    AddFaces(h, hits);
                    return true;
                }
                default: // R ทศพักตร์ยี่สิบกร: 8 s giant form, +AD, 20% lifesteal, all ten faces
                {
                    h.UltTicks = Cd(8);
                    h.BonusAd = Pick(rank, 40, 70, 100, 100, 100, 100);
                    h.LifestealPermille = 200;
                    h.Faces = 10; h.FacesTicks = 8;
                    int raw = Pick(rank, 200, 300, 400, 400, 400, 400) + h.EffectiveAd * 6 / 10;
                    for (int k = 0; k < w.Units.Count; k++)
                    {
                        var u = w.Units[k];
                        if (!u.Alive || u.Team == h.Team || u.Kind == UnitKind.HeartBox) continue;
                        if (Vec2.Within(h.Pos, u.Pos, 300 + u.Radius)) w.Hit(h, u, raw, DamageType.Physical);
                    }
                    return true;
                }
            }
        }

        static void AddFaces(Unit h, int n)
        {
            if (n <= 0 || h.UltTicks > 0) return;
            h.Faces = Math.Min(10, h.Faces + n); h.FacesTicks = 8;
        }

        public static void EndUlt(World w, Unit h)
        {
            h.BonusAd = 0; h.LifestealPermille = 0; h.Faces = 0; h.FacesTicks = 0;
        }

        // ---------------------------------------------------------------- basic attacks
        public static void BasicAttack(World w, Unit h, Unit t)
        {
            h.AttackCooldown = h.AttackIntervalTicks;
            if (h.Hero == HeroId.Rama)
            {
                int raw = h.EffectiveAd;
                if (h.EmpoweredTicks > 0) { raw = raw * 150 / 100; h.EmpoweredTicks = 0; }
                h.BasicCount++;
                w.Events.Add(new SimEvent { Type = SimEvent.T.Skill, A = h.Id, B = -1, P = h.Pos, Q = t.Pos });
                w.Hit(h, t, raw, DamageType.Physical);
                if (h.BasicCount % 4 == 0)       // passive ศรทิพย์: every 4th shot pierces a second target for 120%
                {
                    Vec2 d = t.Pos - h.Pos;
                    Vec2 end = t.Pos + d.WithLength(500);
                    for (int k = 0; k < w.Units.Count; k++)
                    {
                        var u = w.Units[k];
                        if (!u.Alive || u.Team == h.Team || u.Id == t.Id || u.Kind == UnitKind.HeartBox) continue;
                        long r = u.Radius + 40;
                        if (SimMath.SqrDistToSegment(u.Pos, h.Pos, end) <= r * r) { w.Hit(h, u, h.EffectiveAd * 120 / 100, DamageType.Physical); break; }
                    }
                }
                return;
            }
            // Thotsakan: melee, whole circle while in giant form (70% on secondary targets)
            w.Events.Add(new SimEvent { Type = SimEvent.T.Skill, A = h.Id, B = -1, P = h.Pos, Q = t.Pos });
            if (h.UltTicks > 0)
            {
                for (int k = 0; k < w.Units.Count; k++)
                {
                    var u = w.Units[k];
                    if (!u.Alive || u.Team == h.Team || u.Kind == UnitKind.HeartBox) continue;
                    if (!Vec2.Within(h.Pos, u.Pos, 300 + u.Radius)) continue;
                    w.Hit(h, u, u.Id == t.Id ? h.EffectiveAd : h.EffectiveAd * 70 / 100, DamageType.Physical);
                }
            }
            else w.Hit(h, t, h.EffectiveAd, DamageType.Physical);
        }

        /// <summary>Rotate a vector by an angle in 1/1000 degrees (fixed-point, deterministic lookup).</summary>
        public static Vec2 Rotate(Vec2 v, int milliDeg)
        {
            double a = milliDeg / 1000.0 * Math.PI / 180.0;
            int c = (int)Math.Round(Math.Cos(a) * 1000), s = (int)Math.Round(Math.Sin(a) * 1000);
            return new Vec2((int)(((long)v.X * c - (long)v.Z * s) / 1000), (int)(((long)v.X * s + (long)v.Z * c) / 1000));
        }
    }
}
