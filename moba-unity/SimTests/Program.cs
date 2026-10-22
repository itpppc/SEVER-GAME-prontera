using System;
using System.Linq;
using Ramakien.Moba.Sim;

static class Program
{
    static int fails;
    static void Check(bool ok, string name) { Console.WriteLine((ok ? "PASS " : "FAIL ") + name); if (!ok) fails++; }

    static int Main(string[] args)
    {
        // --- formulas (FOUNDATION 2.3)
        Check(Damage.MitigationPermille(100, 0, 0) == 500, "armor 100 -> 50% mitigation");
        Check(Damage.MitigationPermille(100, 250, 0) == 571, "armor 100 with 25% pen -> eff 75 -> 57%");
        Check(Damage.MitigationPermille(-100, 0, 0) == 1500, "negative armor amplifies");
        Check(SimMath.Sqrt(1000000) == 1000 && SimMath.Sqrt(999999) == 999, "integer sqrt");
        Check(World.XpToNext(1) == 200 && World.XpToNext(14) == 1630, "xp curve");
        long total = 0; for (int l = 1; l < 15; l++) total += World.XpToNext(l);
        Check(total == 12810, "total xp 1->15 = 12810");

        // --- determinism: same seed + same bots -> identical state
        string a = Run(7, 1, 1, 60 * 6), b = Run(7, 1, 1, 60 * 6);
        Check(a == b, "deterministic replay: " + a);

        // --- full matches
        for (int lvl = 0; lvl <= 2; lvl++)
        {
            string r = Run(11, lvl, lvl, 60 * 25);
            Console.WriteLine("  match(lvl " + lvl + "): " + r);
        }

        // --- Brahmastra pierces and refunds on kill
        var w = new World(1, HeroId.Rama, HeroId.Thotsakan);
        var rama = w.Heroes[0]; var tos = w.Heroes[1];
        rama.Pos = new Vec2(-2000, 0); tos.Pos = new Vec2(2000, 0); tos.Hp = 200;
        w.Heroes[0].Level = 15; w.Recalc(rama, true);
        w.Cmd[0] = new Command { Kind = CmdKind.Skill, Slot = 2, Point = tos.Pos };
        for (int i = 0; i < 50; i++) { w.Step(); w.Cmd[0] = default(Command); }
        Check(rama.SkillCd[2] > 0, "Brahmastra fired and is on cooldown");
        Check(tos.Alive == false || tos.Hp < 200 || tos.Status.UntargetableHealTicks > 0, "Brahmastra reached 40 m target");

        // --- heart box: sealed blocks damage, breaking it exposes
        var w2 = new World(2, HeroId.Rama, HeroId.Thotsakan);
        var t2 = w2.Heroes[1];
        Check(w2.HeartBoxActive, "heart box placed at start");
        Check(t2.ShieldDrPermille == 100, "10% damage reduction while box lives");
        var r2 = w2.Heroes[0]; r2.Pos = w2.HeartSpot + new Vec2(-200, 0);
        for (int i = 0; i < 5; i++) { var hb = w2.Find(w2.HeartBoxId); if (hb != null) w2.Hit(r2, hb, 100, DamageType.Physical); }
        Check(!w2.HeartBoxActive && t2.Status.ExposedTicks > 0 && t2.ShieldDrPermille == 0, "box broken -> heartExposed");

        Console.WriteLine(fails == 0 ? "ALL OK" : fails + " FAILED");
        return fails;
    }

    static string Run(uint seed, int lvA, int lvB, int seconds)
    {
        var w = new World(seed, HeroId.Rama, HeroId.Thotsakan);
        var ba = new Bot(0, lvA); var bb = new Bot(1, lvB);
        for (int t = 0; t < seconds * 30 && !w.Winner.HasValue; t++)
        {
            w.Cmd[0] = ba.Think(w); w.Cmd[1] = bb.Think(w); w.Step();
        }
        int turrets0 = w.Units.Count(u => u.Kind == UnitKind.Turret && u.Team == Team.Ayodhya);
        int turrets1 = w.Units.Count(u => u.Kind == UnitKind.Turret && u.Team == Team.Lanka);
        return "t=" + (w.Tick / 30) + "s winner=" + (w.Winner.HasValue ? w.Winner.ToString() : "none") +
               " lv=" + w.Heroes[0].Level + "/" + w.Heroes[1].Level +
               " kda=" + w.Heroes[0].Kills + "/" + w.Heroes[0].Deaths + " vs " + w.Heroes[1].Kills + "/" + w.Heroes[1].Deaths +
               " turrets=" + turrets0 + "/" + turrets1 + " gold=" + w.Heroes[0].Gold + "/" + w.Heroes[1].Gold;
    }
}
