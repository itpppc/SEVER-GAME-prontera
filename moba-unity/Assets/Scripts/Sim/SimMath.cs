// Pure C# simulation core. No UnityEngine here: same code runs in the Editor, on a server and in SimTests.
// Units: distance in "u" (1 m = 100 u), time in ticks (30 Hz), percentages in per-mille (1000 = 100%).
using System;

namespace Ramakien.Moba.Sim
{
    public struct Vec2
    {
        public int X, Z;
        public Vec2(int x, int z) { X = x; Z = z; }

        public static Vec2 operator +(Vec2 a, Vec2 b) { return new Vec2(a.X + b.X, a.Z + b.Z); }
        public static Vec2 operator -(Vec2 a, Vec2 b) { return new Vec2(a.X - b.X, a.Z - b.Z); }
        public static readonly Vec2 Zero = new Vec2(0, 0);

        public long SqrLength { get { return (long)X * X + (long)Z * Z; } }
        public int Length { get { return SimMath.Sqrt(SqrLength); } }

        /// <summary>Vector of the given length in this direction; zero stays zero.</summary>
        public Vec2 WithLength(int len)
        {
            int l = Length;
            if (l == 0) return Zero;
            return new Vec2((int)((long)X * len / l), (int)((long)Z * len / l));
        }

        public static long Dot(Vec2 a, Vec2 b) { return (long)a.X * b.X + (long)a.Z * b.Z; }
        public static long Cross(Vec2 a, Vec2 b) { return (long)a.X * b.Z - (long)a.Z * b.X; }
        public static int Distance(Vec2 a, Vec2 b) { return (a - b).Length; }
        public static bool Within(Vec2 a, Vec2 b, int r) { return (a - b).SqrLength <= (long)r * r; }
        public override string ToString() { return "(" + X + "," + Z + ")"; }
    }

    public static class SimMath
    {
        public const int TickHz = 30;
        public const int TickMs = 1000 / TickHz;          // 33 ms
        public const int Permille = 1000;

        public static int Ticks(int ms) { return (ms + TickMs - 1) / TickMs; }
        public static int Seconds(int ticks) { return ticks / TickHz; }

        public static int Sqrt(long v)
        {
            if (v <= 0) return 0;
            long r = (long)Math.Sqrt(v);                   // exact for the ranges we use; corrected below
            while (r * r > v) r--;
            while ((r + 1) * (r + 1) <= v) r++;
            return (int)r;
        }

        public static int Clamp(int v, int lo, int hi) { return v < lo ? lo : (v > hi ? hi : v); }

        /// <summary>Point-to-segment squared distance (for line skillshots).</summary>
        public static long SqrDistToSegment(Vec2 p, Vec2 a, Vec2 b)
        {
            Vec2 ab = b - a, ap = p - a;
            long len2 = ab.SqrLength;
            if (len2 == 0) return ap.SqrLength;
            long t = Vec2.Dot(ap, ab);
            if (t <= 0) return ap.SqrLength;
            if (t >= len2) return (p - b).SqrLength;
            // distance^2 = |ap x ab|^2 / |ab|^2
            double c = Vec2.Cross(ap, ab);
            return (long)(c * c / len2);
        }

        /// <summary>True when p lies inside the cone at origin facing dir with half-angle given by cos (per-mille).</summary>
        public static bool InCone(Vec2 origin, Vec2 dir, Vec2 p, int radius, int cosHalfPermille, int targetRadius)
        {
            Vec2 d = p - origin;
            long r = radius + targetRadius;
            if (d.SqrLength > r * r) return false;
            if (d.SqrLength <= (long)targetRadius * targetRadius) return true;
            int dl = d.Length, fl = dir.Length;
            if (dl == 0 || fl == 0) return true;
            return Vec2.Dot(d, dir) * Permille >= (long)cosHalfPermille * dl * fl;
        }
    }

    /// <summary>mulberry32, same generator as website/rpg and game-core makeRng.</summary>
    public sealed class Rng
    {
        uint _s;
        public Rng(uint seed) { _s = seed; }
        public uint NextU()
        {
            unchecked
            {
                _s += 0x6D2B79F5;
                uint t = _s;
                t = (t ^ (t >> 15)) * (t | 1);
                t ^= t + (t ^ (t >> 7)) * (t | 61);
                return t ^ (t >> 14);
            }
        }
        public int Range(int lo, int hiExclusive) { return lo + (int)(NextU() % (uint)Math.Max(1, hiExclusive - lo)); }
        public bool ChancePermille(int p) { return Range(0, 1000) < p; }
    }
}
