using System;
using System.Collections.Generic;

namespace Ramakien.Moba.Sim
{
    public enum CmdKind { None, Move, Attack, Skill }

    /// <summary>One player/bot command for one tick. Skills: slot 0 = Q, 1 = E, 2 = R (ultimate).</summary>
    public struct Command
    {
        public CmdKind Kind;
        public Vec2 Point;          // move target or aim point
        public int TargetId;
        public int Slot;
    }

    public struct SimEvent
    {
        public enum T { Damage, Death, Spawn, Skill, Beam, Heal, Level, TurretShot, GameOver, HeartBreak, Revive }
        public T Type; public int A, B, Amount; public Vec2 P, Q; public bool Crit;
    }

    /// <summary>Single-lane 1v1 slice of the Himmapan battlefield (lane along X, Ayodhya on the left).</summary>
    public sealed class World
    {
        public const int LaneHalf = 6600;          // u from centre to core
        public static readonly int[] TurretX = { 2400, 4200, 5400 }; // T1, T2, base turret (absolute X)
        public const int CoreX = 6400;
        public const int MaxLevel = 15;

        public int Tick;
        public readonly List<Unit> Units = new List<Unit>();
        public readonly List<SimEvent> Events = new List<SimEvent>();
        public readonly Rng Rng;
        public Team? Winner;
        public Unit[] Heroes = new Unit[2];
        public Command[] Cmd = new Command[2];

        int _nextId = 1;
        int _nextWave;
        public int HeartBoxId = -1;
        public Vec2 HeartSpot;
        int _heartRespawnTick = -1;
        public bool HeartBoxActive { get { return Find(HeartBoxId) != null; } }

        // economy values from ECONOMY-MAP-th.md section 2
        const int WaveInterval = 30 * SimMath.TickHz;
        const int FirstWave = 30 * SimMath.TickHz;

        public World(uint seed, HeroId ayodhya, HeroId lanka)
        {
            Rng = new Rng(seed);
            SpawnStructures();
            Heroes[0] = SpawnHero(Team.Ayodhya, ayodhya);
            Heroes[1] = SpawnHero(Team.Lanka, lanka);
            _nextWave = FirstWave;
            if (lanka == HeroId.Thotsakan || ayodhya == HeroId.Thotsakan) PlaceHeartBox(Heroes[lanka == HeroId.Thotsakan ? 1 : 0]);
        }

        public int Minute { get { return Tick / (60 * SimMath.TickHz); } }
        public Unit Find(int id) { for (int i = 0; i < Units.Count; i++) if (Units[i].Id == id && Units[i].Alive) return Units[i]; return null; }
        public static int Sign(Team t) { return t == Team.Ayodhya ? -1 : 1; }
        public static Team Other(Team t) { return t == Team.Ayodhya ? Team.Lanka : Team.Ayodhya; }
        public Vec2 BasePos(Team t) { return new Vec2(Sign(t) * (LaneHalf - 400), 0); }

        // ------------------------------------------------------------ setup
        void SpawnStructures()
        {
            for (int ti = 0; ti < 2; ti++)
            {
                Team team = (Team)ti;
                int sg = Sign(team);
                for (int i = 0; i < TurretX.Length; i++)
                {
                    var u = NewUnit(team, UnitKind.Turret, new Vec2(sg * TurretX[i], 0));
                    u.Tier = i + 1; u.Radius = 160;
                    int[] hp = { 4500, 4800, 5000 }, ar = { 70, 90, 120 };
                    u.MaxHp = u.Hp = hp[i]; u.Armor = ar[i]; u.Mr = ar[i];
                    u.AttackRange = i == 2 ? 850 : 800;
                    u.Invulnerable = i != 0;                    // must fall T1 -> T2 -> base turret -> core
                }
                var core = NewUnit(team, UnitKind.Core, new Vec2(sg * CoreX, 0));
                core.MaxHp = core.Hp = 7000; core.Armor = 120; core.Mr = 120; core.Radius = 260; core.Invulnerable = true;
            }
        }

        Unit NewUnit(Team team, UnitKind kind, Vec2 pos)
        {
            var u = new Unit { Id = _nextId++, Team = team, Kind = kind, Pos = pos };
            Units.Add(u);
            return u;
        }

        static HeroStats StatsFor(HeroId id)
        {
            switch (id)
            {
                case HeroId.Rama:       // Marksman scale, FOUNDATION 2.2
                    return new HeroStats { Hp = 2550, HpGrowth = 165, Ad = 160, AdGrowth = 12, Armor = 15, ArmorGrowthX10 = 25, Mr = 15, MrGrowthX10 = 10, AsX1000 = 700, AsGrowthPermille = 30, MoveSpeed = 350, Range = 650 };
                default:                // Thotsakan, HERO-KITS 2.2
                    return new HeroStats { Hp = 3200, HpGrowth = 240, Ad = 165, AdGrowth = 11, Armor = 27, ArmorGrowthX10 = 36, Mr = 20, MrGrowthX10 = 15, AsX1000 = 700, AsGrowthPermille = 20, MoveSpeed = 370, Range = 180 };
            }
        }

        Unit SpawnHero(Team team, HeroId id)
        {
            var u = NewUnit(team, UnitKind.Hero, BasePos(team));
            u.Hero = id; u.Stats = StatsFor(id); u.Radius = 60;
            u.Facing = new Vec2(-Sign(team), 0);
            u.Gold = 500;
            Recalc(u, true);
            return u;
        }

        public void Recalc(Unit u, bool fill)
        {
            var s = u.Stats; int l = u.Level - 1;
            int oldMax = u.MaxHp;
            u.MaxHp = s.Hp + s.HpGrowth * l;
            u.Ad = s.Ad + s.AdGrowth * l;
            u.Armor = s.Armor + s.ArmorGrowthX10 * l / 10;
            u.Mr = s.Mr + s.MrGrowthX10 * l / 10;
            int asx = s.AsX1000 * (1000 + s.AsGrowthPermille * l) / 1000;
            u.AttackIntervalTicks = Math.Max(5, SimMath.TickHz * 1000 / Math.Max(1, Math.Min(2500, asx)));
            u.MoveSpeed = s.MoveSpeed; u.AttackRange = s.Range;
            if (fill) u.Hp = u.MaxHp; else u.Hp += u.MaxHp - oldMax;
        }

        void PlaceHeartBox(Unit owner)
        {
            // one of three jungle spots behind the Lanka lane; the bot picks the near one
            HeartSpot = new Vec2(Sign(owner.Team) * 3600, 2300);
            var hb = NewUnit(owner.Team, UnitKind.HeartBox, HeartSpot);
            hb.MaxHp = hb.Hp = 1; hb.Radius = 80;
            HeartBoxId = hb.Id;
            owner.ShieldDrPermille = 100;
        }

        // ------------------------------------------------------------ main loop
        public void Step()
        {
            if (Winner.HasValue) return;
            Events.Clear();
            Tick++;

            SpawnWaves();
            for (int i = 0; i < Units.Count; i++) Units[i].Status.Tick();
            for (int h = 0; h < 2; h++) StepHero(Heroes[h], Cmd[h]);
            for (int i = 0; i < Units.Count; i++)
            {
                var u = Units[i];
                if (!u.Alive) continue;
                if (u.IsMinion) StepMinion(u);
                else if (u.Kind == UnitKind.Turret) StepTurret(u);
            }
            StepHeartBox();
            StepRegen();
            Units.RemoveAll(u => !u.Alive && u.Kind != UnitKind.Hero);
        }

        void StepRegen()
        {
            if (Tick % SimMath.TickHz != 0) return;
            for (int h = 0; h < 2; h++)
            {
                var u = Heroes[h];
                if (u.Alive && u.Hp < u.MaxHp) u.Hp = Math.Min(u.MaxHp, u.Hp + 8 + u.Level);
                if (u.Alive && u.FacesTicks > 0 && --u.FacesTicks == 0) u.Faces = 0;
            }
            for (int i = 0; i < Units.Count; i++)
            {
                var c = Units[i];
                if (c.Kind == UnitKind.Core && c.Alive && Tick - c.LastDamagedTick > 8 * SimMath.TickHz) c.Hp = Math.Min(c.MaxHp, c.Hp + 20);
            }
            // gold trickle (ECONOMY: passive income)
            for (int h = 0; h < 2; h++) if (Heroes[h].Alive) Heroes[h].Gold += 2;
        }

        // ------------------------------------------------------------ waves (ECONOMY-MAP 2.1 / 2.2)
        void SpawnWaves()
        {
            if (Tick != _nextWave) return;
            _nextWave += WaveInterval;
            int waveNo = (Tick - FirstWave) / WaveInterval;      // 0-based
            int m = Math.Min(Tick / (60 * SimMath.TickHz), 14);
            int melee = Minute >= 10 ? 4 : 3;
            int siegeEvery = Minute >= 14 ? 1 : (Minute >= 8 ? 2 : 3);
            bool siege = (waveNo + 1) % siegeEvery == 0;
            for (int t = 0; t < 2; t++)
            {
                Team team = (Team)t; int sg = Sign(team);
                int k = 0;
                Action<UnitKind> add = kind =>
                {
                    var u = NewUnit(team, kind, new Vec2(sg * (LaneHalf - 800) + sg * 60 * k, (k % 3 - 1) * 70));
                    u.LaneDir = -sg; u.Radius = 45; k++;
                    switch (kind)
                    {
                        case UnitKind.Melee: u.MaxHp = 480 + 20 * m; u.Ad = 14 + m; u.AttackRange = 120; u.AttackIntervalTicks = 40; u.MoveSpeed = 325; break;
                        case UnitKind.Ranged: u.MaxHp = 300 + 12 * m; u.Ad = 24 + (3 * m) / 2; u.AttackRange = 500; u.AttackIntervalTicks = 45; u.MoveSpeed = 325; break;
                        default: u.MaxHp = 950 + 45 * m; u.Ad = 40 + (5 * m) / 2; u.Armor = 40; u.AttackRange = 450; u.AttackIntervalTicks = 60; u.MoveSpeed = 300; u.Radius = 70; break;
                    }
                    u.Hp = u.MaxHp;
                };
                for (int i = 0; i < melee; i++) add(UnitKind.Melee);
                for (int i = 0; i < 3; i++) add(UnitKind.Ranged);
                if (siege) add(UnitKind.Siege);
            }
        }

        public static int MinionGold(Unit u, int m)
        {
            switch (u.Kind) { case UnitKind.Melee: return 20 + m / 2; case UnitKind.Ranged: return 15 + (35 * m) / 100; default: return 50 + 2 * m; }
        }
        public static int MinionXp(Unit u, int m)
        {
            switch (u.Kind) { case UnitKind.Melee: return 40 + (16 * m) / 10; case UnitKind.Ranged: return 32 + (13 * m) / 10; default: return 95 + (34 * m) / 10; }
        }
        public static int XpToNext(int level) { return 200 + 110 * (level - 1); }

        // ------------------------------------------------------------ minions
        void StepMinion(Unit u)
        {
            if (u.Status.StunTicks > 0) return;
            if (u.AttackCooldown > 0) u.AttackCooldown--;
            Unit target = NearestEnemy(u, u.AttackRange + 150, false);
            if (target != null)
            {
                u.Facing = target.Pos - u.Pos;
                if (SimMath.Sqrt((target.Pos - u.Pos).SqrLength) <= u.AttackRange + target.Radius)
                {
                    if (u.AttackCooldown == 0)
                    {
                        u.AttackCooldown = u.AttackIntervalTicks;
                        int raw = u.Ad;
                        if (u.Kind == UnitKind.Siege && target.IsStructure) raw *= 2;
                        Hit(u, target, raw, DamageType.Physical);
                    }
                    return;
                }
                MoveToward(u, target.Pos, u.MoveSpeed);
                return;
            }
            // march along the lane toward the enemy base; stop at a friendly blocker structure
            Vec2 goal = new Vec2(-Sign(u.Team) * CoreX, 0);
            MoveToward(u, goal, u.MoveSpeed);
        }

        public void MoveToward(Unit u, Vec2 dest, int speed)
        {
            Vec2 d = dest - u.Pos;
            int step = speed * 1000 / SimMath.TickHz / 1000;
            if (step < 1) step = 1;
            int len = d.Length;
            if (len == 0) return;
            if (len <= step) u.Pos = dest; else u.Pos = u.Pos + d.WithLength(step);
            u.Facing = d;
            u.Pos = new Vec2(SimMath.Clamp(u.Pos.X, -LaneHalf, LaneHalf), SimMath.Clamp(u.Pos.Z, -2800, 2800));
        }

        // ------------------------------------------------------------ turrets (ECONOMY-MAP section 6)
        void StepTurret(Unit t)
        {
            if (t.AttackCooldown > 0) { t.AttackCooldown--; return; }
            int range = t.AttackRange;
            Unit target = null;
            // aggro: an enemy hero that hit our hero inside range pulls the turret for at least 2 s
            var focus = Find(t.FocusTargetId);
            if (focus != null && Tick - t.FocusLastTick < 2 * SimMath.TickHz && Vec2.Within(t.Pos, focus.Pos, range + focus.Radius)) target = focus;
            if (target == null)
            {
                Unit enemyHero = Heroes[(int)Other(t.Team)];
                Unit ownHero = Heroes[(int)t.Team];
                if (enemyHero.Alive && Vec2.Within(t.Pos, enemyHero.Pos, range + enemyHero.Radius) && ownHero.Alive
                    && Tick - enemyHero.HeroDamageTick < 3 * SimMath.TickHz && Vec2.Within(t.Pos, ownHero.Pos, range + 300))
                    target = enemyHero;
            }
            if (target == null) target = NearestEnemy(t, range, true, minionsFirst: true);
            if (target == null) { t.FocusStacks = 0; return; }

            t.AttackCooldown = SimMath.TickHz;     // 1 shot / s
            int minute = Math.Min(Minute, 14);
            int baseDmg;
            switch (t.Tier) { case 1: baseDmg = 150 + 10 * minute; break; case 2: baseDmg = 180 + 11 * minute; break; default: baseDmg = (t.Tier == 3 ? 230 : 200) + 12 * minute; break; }
            int raw;
            if (target.Kind == UnitKind.Hero)
            {
                if (t.FocusTargetId != target.Id || Tick - t.FocusLastTick > 75) t.FocusStacks = 0;
                t.FocusTargetId = target.Id; t.FocusLastTick = Tick;
                int[] pct = { 1000, 1350, 1700, 2050, 2400 };
                raw = baseDmg * pct[Math.Min(t.FocusStacks, 4)] / 1000;
                t.FocusStacks++;
            }
            else
            {
                int pctMax = target.Kind == UnitKind.Melee ? 450 : (target.Kind == UnitKind.Ranged ? 700 : (t.Tier == 1 ? 140 : (t.Tier == 2 ? 120 : 100)));
                raw = target.MaxHp * pctMax / 1000;
            }
            var saved = t.ArmorPenPermille; t.ArmorPenPermille = 250;
            Events.Add(new SimEvent { Type = SimEvent.T.TurretShot, A = t.Id, B = target.Id, P = t.Pos, Q = target.Pos });
            Hit(t, target, raw, DamageType.Physical);
            t.ArmorPenPermille = saved;
        }

        // ------------------------------------------------------------ targeting helpers
        public Unit NearestEnemy(Unit from, int range, bool includeHeroes, bool minionsFirst = false)
        {
            Unit best = null; long bestD = long.MaxValue;
            Team enemy = Other(from.Team);
            for (int i = 0; i < Units.Count; i++)
            {
                var o = Units[i];
                if (!o.Alive || o.Team != enemy || o.Kind == UnitKind.HeartBox) continue;
                if (o.Kind == UnitKind.Hero && !includeHeroes && !(from.IsMinion && o.Kind == UnitKind.Hero)) continue;
                if (o.IsStructure && !from.IsMinion) continue;
                long d = (o.Pos - from.Pos).SqrLength;
                long r = range + o.Radius;
                if (d > r * r) continue;
                long score = d;
                if (minionsFirst && o.Kind == UnitKind.Hero) score += 100000000L;      // minions soak turret shots first
                if (from.IsMinion && o.Kind == UnitKind.Hero) score += 40000000L;      // minions prefer minions
                if (o.IsStructure && !o.Invulnerable) score += 0;
                if (score < bestD) { bestD = score; best = o; }
            }
            return best;
        }

        // ------------------------------------------------------------ damage
        public int Hit(Unit src, Unit dst, int raw, DamageType type)
        {
            if (!dst.Alive) return 0;
            if (dst.Invulnerable) { Events.Add(new SimEvent { Type = SimEvent.T.Damage, A = src != null ? src.Id : 0, B = dst.Id, Amount = 0, P = dst.Pos }); return 0; }
            if (dst.Status.UntargetableHealTicks > 0) return 0;                           // heartSealed blocks all damage incl. true
            if (dst.Kind == UnitKind.HeartBox)
            {
                if (src == null || src.Kind != UnitKind.Hero || src.Team == dst.Team) return 0;
                dst.Hp -= 1; BreakHeart(src); return 1;
            }
            int dmg = type == DamageType.True ? raw : Damage.Resolve(raw, type, src, dst);
            if (src != null && src.Kind == UnitKind.Hero && dst.Kind == UnitKind.Hero) src.HeroDamageTick = Tick;
            dst.Hp -= dmg;
            dst.LastDamagedTick = Tick;
            if (src != null) dst.LastHitById = src.Id;
            Events.Add(new SimEvent { Type = SimEvent.T.Damage, A = src != null ? src.Id : 0, B = dst.Id, Amount = dmg, P = dst.Pos, Crit = false });
            if (src != null && src.LifestealPermille > 0 && src.Alive) Heal(src, dmg * src.LifestealPermille / 1000);
            if (dst.Hp <= 0) Die(dst, src);
            return dmg;
        }

        public void Heal(Unit u, int amt)
        {
            if (amt <= 0 || !u.Alive) return;
            u.Hp = Math.Min(u.MaxHp, u.Hp + amt);
            Events.Add(new SimEvent { Type = SimEvent.T.Heal, A = u.Id, Amount = amt, P = u.Pos });
        }

        void Die(Unit dst, Unit src)
        {
            if (dst.Kind == UnitKind.Hero && dst.Hero == HeroId.Thotsakan && HeartBoxActive && dst.Team == Find(HeartBoxId).Team)
            {
                // passive: heartSealed (near the box) or revive at the box
                var hb = Find(HeartBoxId);
                if (Vec2.Within(dst.Pos, hb.Pos, 1800))
                {
                    dst.Hp = 1; dst.Status.UntargetableHealTicks = 2 * SimMath.TickHz;
                    dst.HeartHealPerTick = dst.MaxHp * 30 / 100 / (2 * SimMath.TickHz) + 1;
                    ConsumeHeart(dst, false);
                    return;
                }
                ConsumeHeart(dst, true);
            }
            dst.Alive = false; dst.Hp = 0;
            Events.Add(new SimEvent { Type = SimEvent.T.Death, A = src != null ? src.Id : 0, B = dst.Id, P = dst.Pos });
            Unit killerHero = (src != null && src.Kind == UnitKind.Hero) ? src : null;
            if (dst.Kind == UnitKind.Hero)
            {
                dst.Deaths++;
                dst.RespawnTicks = (6 + 5 * dst.Level / 2 + Math.Max(0, Minute - 12)) * SimMath.TickHz;
                dst.ChargeTicks = 0; dst.UltTicks = 0;
                if (killerHero != null) { killerHero.Kills++; killerHero.Gold += 300; GrantXp(killerHero, 120 + 40 * dst.Level); }
                return;
            }
            if (dst.IsMinion)
            {
                int m = Math.Min(Minute, 14);
                Unit h = Heroes[(int)Other(dst.Team)];
                bool lastHit = src != null && src.Id == h.Id;
                bool near = h.Alive && Vec2.Within(h.Pos, dst.Pos, 1200);
                if (lastHit) h.Gold += MinionGold(dst, m);
                if (near) GrantXp(h, MinionXp(dst, m) * (lastHit ? 1000 : 800) / 1000);
                return;
            }
            if (dst.Kind == UnitKind.Turret)
            {
                Unit h = Heroes[(int)Other(dst.Team)];
                h.Gold += dst.Tier == 1 ? 250 : 200;
                for (int i = 0; i < Units.Count; i++)
                    if (Units[i].Kind == UnitKind.Turret && Units[i].Team == dst.Team && Units[i].Tier == dst.Tier + 1) Units[i].Invulnerable = false;
                if (dst.Tier == 3)
                    for (int i = 0; i < Units.Count; i++) if (Units[i].Kind == UnitKind.Core && Units[i].Team == dst.Team) Units[i].Invulnerable = false;
                return;
            }
            if (dst.Kind == UnitKind.Core)
            {
                Winner = Other(dst.Team);
                Events.Add(new SimEvent { Type = SimEvent.T.GameOver, A = (int)Winner.Value });
            }
        }

        public void GrantXp(Unit h, int xp)
        {
            if (h.Level >= MaxLevel) return;
            h.Xp += xp;
            while (h.Level < MaxLevel && h.Xp >= XpToNext(h.Level))
            {
                h.Xp -= XpToNext(h.Level); h.Level++;
                Recalc(h, false);
                Events.Add(new SimEvent { Type = SimEvent.T.Level, A = h.Id, Amount = h.Level, P = h.Pos });
            }
        }

        // ------------------------------------------------------------ Thotsakan heart box
        void BreakHeart(Unit breaker)
        {
            var hb = Find(HeartBoxId);
            if (hb == null) return;
            hb.Alive = false; HeartBoxId = -1;
            Events.Add(new SimEvent { Type = SimEvent.T.HeartBreak, A = breaker.Id, P = hb.Pos });
            var owner = Heroes[(int)hb.Team];
            owner.ShieldDrPermille = 0;
            owner.Status.ExposedTicks = 6 * SimMath.TickHz;     // heartExposed
            breaker.Gold += 50;
            _heartRespawnTick = Tick + 180 * SimMath.TickHz;
        }

        void ConsumeHeart(Unit owner, bool reviveAtBox)
        {
            var hb = Find(HeartBoxId);
            Vec2 at = hb != null ? hb.Pos : owner.Pos;
            if (hb != null) { hb.Alive = false; HeartBoxId = -1; }
            owner.ShieldDrPermille = 0;
            _heartRespawnTick = Tick + 180 * SimMath.TickHz;
            if (reviveAtBox) { owner.PendingHeartRevive = at; }
        }

        void StepHeartBox()
        {
            var owner = Heroes[0].Hero == HeroId.Thotsakan ? Heroes[0] : (Heroes[1].Hero == HeroId.Thotsakan ? Heroes[1] : null);
            if (owner == null) return;
            if (owner.Status.UntargetableHealTicks > 0 && owner.Alive) owner.Hp = Math.Min(owner.MaxHp, owner.Hp + owner.HeartHealPerTick);
            if (_heartRespawnTick > 0 && Tick >= _heartRespawnTick && owner.Alive && !HeartBoxActive) { _heartRespawnTick = -1; PlaceHeartBox(owner); }
        }

        // ------------------------------------------------------------ hero stepping & respawn
        void StepHero(Unit h, Command cmd)
        {
            if (!h.Alive)
            {
                if (h.RespawnTicks > 0 && --h.RespawnTicks == 0)
                {
                    h.Alive = true; h.Hp = h.MaxHp;
                    h.Pos = h.PendingHeartRevive.HasValue ? h.PendingHeartRevive.Value : BasePos(h.Team);
                    if (h.PendingHeartRevive.HasValue) { h.Hp = h.MaxHp * 30 / 100; h.PendingHeartRevive = null; }
                    Events.Add(new SimEvent { Type = SimEvent.T.Revive, A = h.Id, P = h.Pos });
                }
                else if (h.PendingHeartRevive.HasValue && h.RespawnTicks > 2 * SimMath.TickHz) h.RespawnTicks = 2 * SimMath.TickHz;
                return;
            }
            for (int i = 0; i < 3; i++) if (h.SkillCd[i] > 0) h.SkillCd[i]--;
            if (h.AttackCooldown > 0) h.AttackCooldown--;
            if (h.ComboWindow > 0 && --h.ComboWindow == 0) h.ComboStep = 0;
            if (h.EmpoweredTicks > 0) h.EmpoweredTicks--;
            if (h.UltTicks > 0 && --h.UltTicks == 0) HeroSkills.EndUlt(this, h);
            if (h.Status.StunTicks > 0) return;

            if (h.ChargeTicks > 0)
            {
                if (--h.ChargeTicks == 0) HeroSkills.FireCharged(this, h);
                return;                                                // rooted while drawing the bow
            }

            switch (cmd.Kind)
            {
                case CmdKind.Skill:
                    HeroSkills.Cast(this, h, cmd.Slot, cmd.Point);
                    break;
                case CmdKind.Attack:
                    var t = Find(cmd.TargetId);
                    if (t == null || t.Team == h.Team) { h.TargetId = -1; break; }
                    h.TargetId = t.Id;
                    ApproachAndAttack(h, t);
                    break;
                case CmdKind.Move:
                    h.TargetId = -1;
                    MoveToward(h, cmd.Point, h.CurrentMoveSpeed);
                    break;
                default:
                    if (h.TargetId >= 0)
                    {
                        var tt = Find(h.TargetId);
                        if (tt != null && tt.Team != h.Team) ApproachAndAttack(h, tt); else h.TargetId = -1;
                    }
                    break;
            }
            h.Pos = new Vec2(SimMath.Clamp(h.Pos.X, -LaneHalf, LaneHalf), SimMath.Clamp(h.Pos.Z, -2800, 2800));
        }

        void ApproachAndAttack(Unit h, Unit t)
        {
            int range = h.AttackRange + (h.EmpoweredTicks > 0 ? h.AttackRange * 40 / 100 : 0);
            if (h.Hero == HeroId.Thotsakan && h.UltTicks > 0) range = 300;
            if (Vec2.Within(h.Pos, t.Pos, range + t.Radius))
            {
                h.Facing = t.Pos - h.Pos;
                if (h.AttackCooldown == 0) HeroSkills.BasicAttack(this, h, t);
            }
            else MoveToward(h, t.Pos, h.CurrentMoveSpeed);
        }
    }
}
