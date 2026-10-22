using System;

namespace Ramakien.Moba.Sim
{
    /// <summary>Utility-style lane bot. Level 0 = easy, 1 = normal, 2 = hard. Deterministic (uses the world RNG).</summary>
    public sealed class Bot
    {
        readonly int _slot; readonly int _level;
        public Bot(int heroSlot, int level) { _slot = heroSlot; _level = level; }

        public Command Think(World w)
        {
            var me = w.Heroes[_slot];
            var foe = w.Heroes[1 - _slot];
            if (!me.Alive || me.Status.StunTicks > 0) return default(Command);
            int sg = World.Sign(me.Team);
            Vec2 home = w.BasePos(me.Team);

            // 1. recover when low
            bool low = me.HpPermille < 280;
            if (low || (me.HpPermille < 450 && foe.Alive && Vec2.Within(me.Pos, foe.Pos, 900) && foe.HpPermille > me.HpPermille + 100))
            {
                // run home, but use the escape skill on the way
                if (me.Hero == HeroId.Rama && me.SkillCd[1] == 0 && Vec2.Within(me.Pos, foe.Pos, 700))
                    return new Command { Kind = CmdKind.Skill, Slot = 1, Point = home };
                return new Command { Kind = CmdKind.Move, Point = home };
            }
            if (me.HpPermille < 600 && Tick(w) % 90 < 60 && !Vec2.Within(me.Pos, foe.Pos, 1100) && me.Pos.X * sg > 2000)
                return new Command { Kind = CmdKind.Move, Point = home };   // top up at the fountain side

            // 2. fight the enemy hero when it is worth it
            if (foe.Alive && Vec2.Within(me.Pos, foe.Pos, 1400) && !UnderEnemyTurret(w, me, foe))
            {
                int react = _level == 0 ? 25 : (_level == 1 ? 8 : 2);
                if (Tick(w) % react == 0)
                {
                    var c = TrySkill(w, me, foe);
                    if (c.Kind == CmdKind.Skill) return c;
                }
                if (me.HpPermille + 80 >= foe.HpPermille || _level == 0)
                    return new Command { Kind = CmdKind.Attack, TargetId = foe.Id };
            }

            // 3. farm / push
            Unit target = w.NearestEnemy(me, me.AttackRange + 120, false);
            if (target != null && target.Kind == UnitKind.Hero) target = null;
            if (target != null)
            {
                if (target.IsStructure && !FriendlyMinionsNear(w, me, target.Pos, 700) && target.Kind != UnitKind.Core) { /* wait for minions */ }
                else
                {
                    // use Q on minion clumps when ready (hard bots only)
                    if (_level >= 1 && me.Hero == HeroId.Rama && me.SkillCd[0] == 0 && CountEnemyMinions(w, me, 900) >= 3)
                        return new Command { Kind = CmdKind.Skill, Slot = 0, Point = target.Pos };
                    return new Command { Kind = CmdKind.Attack, TargetId = target.Id };
                }
            }
            // 4. walk with the wave: stand just behind our front-most minion
            int front = FrontLine(w, me);
            int stopX = front - sg * 250;
            Vec2 dest = new Vec2(stopX, 0);
            if (Math.Abs(me.Pos.X - dest.X) < 120) return default(Command);
            return new Command { Kind = CmdKind.Move, Point = dest };
        }

        static int Tick(World w) { return w.Tick; }

        Command TrySkill(World w, Unit me, Unit foe)
        {
            int dist = Vec2.Distance(me.Pos, foe.Pos);
            if (me.Hero == HeroId.Rama)
            {
                if (me.SkillCd[2] == 0 && dist < 2600 && (foe.HpPermille < 560 || _level >= 2 && dist > 900))
                    return new Command { Kind = CmdKind.Skill, Slot = 2, Point = Lead(foe) };
                if (me.SkillCd[0] == 0 && dist < 800) return new Command { Kind = CmdKind.Skill, Slot = 0, Point = foe.Pos };
                if (me.SkillCd[1] == 0 && dist > 800 && dist < 1200 && _level >= 1)
                    return new Command { Kind = CmdKind.Skill, Slot = 1, Point = foe.Pos };
            }
            else
            {
                if (me.SkillCd[2] == 0 && dist < 350 && foe.HpPermille < 800) return new Command { Kind = CmdKind.Skill, Slot = 2 };
                if (me.SkillCd[1] == 0 && dist < 330) return new Command { Kind = CmdKind.Skill, Slot = 1 };
                if (me.SkillCd[0] == 0 && dist < 380) return new Command { Kind = CmdKind.Skill, Slot = 0, Point = foe.Pos };
            }
            return default(Command);
        }

        static Vec2 Lead(Unit foe) { return foe.Pos + foe.Facing.WithLength(0); }

        static bool UnderEnemyTurret(World w, Unit me, Unit foe)
        {
            for (int i = 0; i < w.Units.Count; i++)
            {
                var t = w.Units[i];
                if (t.Kind != UnitKind.Turret || !t.Alive || t.Team == me.Team) continue;
                if (Vec2.Within(t.Pos, foe.Pos, t.AttackRange + 150) && !FriendlyMinionsNear(w, me, t.Pos, 600)) return true;
            }
            return false;
        }

        static bool FriendlyMinionsNear(World w, Unit me, Vec2 p, int r)
        {
            for (int i = 0; i < w.Units.Count; i++)
            {
                var u = w.Units[i];
                if (u.Alive && u.Team == me.Team && u.IsMinion && Vec2.Within(u.Pos, p, r)) return true;
            }
            return false;
        }

        static int CountEnemyMinions(World w, Unit me, int r)
        {
            int n = 0;
            for (int i = 0; i < w.Units.Count; i++)
            {
                var u = w.Units[i];
                if (u.Alive && u.Team != me.Team && u.IsMinion && Vec2.Within(u.Pos, me.Pos, r)) n++;
            }
            return n;
        }

        static int FrontLine(World w, Unit me)
        {
            int sg = World.Sign(me.Team);
            int best = sg * 1500;                  // default: hold near our first turret
            bool any = false;
            for (int i = 0; i < w.Units.Count; i++)
            {
                var u = w.Units[i];
                if (!u.Alive || u.Team != me.Team || !u.IsMinion) continue;
                if (!any || (sg < 0 ? u.Pos.X > best : u.Pos.X < best)) { best = u.Pos.X; any = true; }
            }
            return best;
        }
    }
}
