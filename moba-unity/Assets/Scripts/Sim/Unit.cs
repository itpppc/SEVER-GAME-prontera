using System;
using System.Collections.Generic;

namespace Ramakien.Moba.Sim
{
    public enum Team { Ayodhya = 0, Lanka = 1 }
    public enum UnitKind { Hero, Melee, Ranged, Siege, Turret, Core, HeartBox }
    public enum DamageType { Physical, Magic, True }
    public enum HeroId { Rama, Thotsakan }

    /// <summary>Per-level stat line: value = Base + Growth * (level - 1). Growth for AS is per-mille of base.</summary>
    public sealed class HeroStats
    {
        public int Hp, HpGrowth;
        public int Ad, AdGrowth;
        public int Armor, ArmorGrowthX10;   // x10 so 2.5 / 3.6 stay integers
        public int Mr, MrGrowthX10;
        public int AsX1000, AsGrowthPermille; // 0.70 attacks/s = 700
        public int MoveSpeed;               // u per second
        public int Range;                   // u
    }

    public sealed class Status
    {
        public int SlowPermille, SlowTicks;
        public int StunTicks;
        public int AdDownPermille, AdDownTicks;
        public int ExposedTicks;            // heartExposed: +15% damage taken, 20% slow
        public int UntargetableHealTicks;   // heartSealed window

        public void Tick()
        {
            if (SlowTicks > 0 && --SlowTicks == 0) SlowPermille = 0;
            if (StunTicks > 0) StunTicks--;
            if (AdDownTicks > 0 && --AdDownTicks == 0) AdDownPermille = 0;
            if (ExposedTicks > 0) ExposedTicks--;
            if (UntargetableHealTicks > 0) UntargetableHealTicks--;
        }

        public void ApplySlow(int permille, int ticks)
        {
            // Slows do not stack: the strongest wins, the longest of equal strength wins (FOUNDATION 2.5)
            if (permille > SlowPermille || (permille == SlowPermille && ticks > SlowTicks)) { SlowPermille = permille; SlowTicks = ticks; }
        }
    }

    public sealed class Unit
    {
        public int Id;
        public Team Team;
        public UnitKind Kind;
        public HeroId Hero;                 // valid when Kind == Hero
        public int Tier;                    // turrets: 1..4 (4 = base turret)
        public Vec2 Pos;
        public Vec2 Facing = new Vec2(1, 0);
        public int Radius = 50;

        public int Hp, MaxHp;
        public int Ad, Armor, Mr;
        public int AttackIntervalTicks;
        public int AttackRange;
        public int MoveSpeed;
        public int ArmorPenPermille;

        public bool Alive = true;
        public bool Invulnerable;           // turret ordering, heart window
        public int AttackCooldown;
        public int TargetId = -1;
        public int LastHitById = -1;
        public int LastDamagedTick = -99999;

        // hero-only
        public int Level = 1, Xp, Gold;
        public int RespawnTicks;
        public int Kills, Deaths, Assists;
        public readonly int[] SkillCd = new int[3];
        public int LifestealPermille;
        public int BonusAd;
        public int UltTicks;                // active transformation / buff
        public int ComboStep, ComboWindow;  // Thotsakan Q
        public int Faces, FacesTicks;       // Thotsakan passive stacks
        public int BasicCount;              // Rama passive: every 4th basic pierces
        public int EmpoweredTicks;          // Rama E: next basic +40% range, +50% dmg
        public int ChargeTicks; public Vec2 ChargeDir; // Rama R wind-up
        public int HeroDamageTick = -99999; // last tick this unit damaged an enemy hero (turret aggro)
        public int HeartHealPerTick;
        public Vec2? PendingHeartRevive;
        public int ShieldDrPermille;        // Thotsakan heart: damage reduction while box alive

        // turret focus: consecutive shots at the same hero
        public int FocusStacks, FocusTargetId = -1, FocusLastTick = -99999;

        // minions
        public int LaneDir;                 // +1 walks toward +X, -1 toward -X

        public readonly Status Status = new Status();
        public HeroStats Stats;

        public bool IsStructure { get { return Kind == UnitKind.Turret || Kind == UnitKind.Core; } }
        public bool IsMinion { get { return Kind == UnitKind.Melee || Kind == UnitKind.Ranged || Kind == UnitKind.Siege; } }
        public bool CanAct { get { return Alive && Status.StunTicks == 0; } }

        public int CurrentMoveSpeed
        {
            get
            {
                int slow = Status.SlowPermille;
                if (Status.ExposedTicks > 0) slow = Math.Max(slow, 200);
                int ms = MoveSpeed * (1000 - slow) / 1000;
                return SimMath.Clamp(ms, 150, 550);
            }
        }

        public int EffectiveAd
        {
            get { return (Ad + BonusAd) * (1000 - Status.AdDownPermille) / 1000; }
        }

        public int HpPermille { get { return MaxHp == 0 ? 0 : (int)((long)Hp * 1000 / MaxHp); } }
    }

    public static class Damage
    {
        /// <summary>FOUNDATION 2.3: pen% before flat pen, then 100/(100+armor); negative armor amplifies up to x2.</summary>
        public static int MitigationPermille(int resist, int penPermille, int penFlat)
        {
            if (resist < 0) return 2000 - 100000 / (100 - resist);
            long eff = (long)resist * (1000 - penPermille) / 1000 - penFlat;
            if (eff < 0) eff = 0;
            return (int)(100000 / (100 + eff));
        }

        public static int Resolve(int raw, DamageType type, Unit src, Unit dst)
        {
            long dmg = raw;
            int pen = src != null ? src.ArmorPenPermille : 0;
            if (type == DamageType.Physical) dmg = dmg * MitigationPermille(dst.Armor + FaceArmor(dst), pen, 0) / 1000;
            else if (type == DamageType.Magic) dmg = dmg * MitigationPermille(dst.Mr + FaceArmor(dst), 0, 0) / 1000;
            if (dst.Status.ExposedTicks > 0) dmg = dmg * 1150 / 1000;                    // heartExposed
            if (type != DamageType.True && dst.ShieldDrPermille > 0) dmg = dmg * (1000 - dst.ShieldDrPermille) / 1000;
            return (int)Math.Max(0, dmg);
        }

        static int FaceArmor(Unit u) { return u.Kind == UnitKind.Hero && u.Hero == HeroId.Thotsakan ? u.Faces * 3 : 0; }
    }
}
