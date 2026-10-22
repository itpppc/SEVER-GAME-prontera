using System.Collections.Generic;
using UnityEngine;
using Ramakien.Moba.Sim;

namespace Ramakien.Moba.Game
{
    /// <summary>Visual for one simulation unit. Reads sim state each frame; never writes back.</summary>
    public sealed class UnitView : MonoBehaviour
    {
        public Unit Unit;
        public Transform Body, ArmPivot, WeaponPivot, Crown;
        public float Scale = 1f;
        public Vector3 LastPos;
        public float Swing, Bob, DeathT, HitFlash;
        public GameObject FormAura;
        public Transform[] Faces;           // Thotsakan stacked faces (shown by stack count)
        public float BaseHeight = 3f;       // for health bars / names

        public void Sync(float dt)
        {
            var u = Unit;
            Vector3 target = new Vector3(u.Pos.X / 100f, 0, u.Pos.Z / 100f);
            Vector3 delta = target - transform.position;
            bool moving = delta.sqrMagnitude > 0.0004f;
            transform.position = Vector3.Lerp(transform.position, target, Mathf.Clamp01(dt * 18f));
            if (Vector3.Distance(transform.position, target) > 2f) transform.position = target;

            if (u.Facing.SqrLength > 0)
            {
                float yaw = Mathf.Atan2(u.Facing.X, u.Facing.Z) * Mathf.Rad2Deg;
                transform.rotation = Quaternion.Slerp(transform.rotation, Quaternion.Euler(0, yaw, 0), Mathf.Clamp01(dt * 14f));
            }
            Bob += dt * (moving ? 14f : 2.2f);
            float amp = moving ? 0.11f : 0.03f;
            if (Body != null) Body.localPosition = new Vector3(0, Mathf.Abs(Mathf.Sin(Bob)) * amp * Scale, 0);
            if (Body != null) Body.localRotation = Quaternion.Euler(moving ? 6f : 0f, 0, Mathf.Sin(Bob) * (moving ? 3f : 0.6f));

            if (Swing > 0)
            {
                Swing -= dt * 4.5f;
                float k = Mathf.Sin(Mathf.Clamp01(1f - Swing) * Mathf.PI);
                if (ArmPivot != null) ArmPivot.localRotation = Quaternion.Euler(-70f * k, 0, 0);
                if (WeaponPivot != null) WeaponPivot.localRotation = Quaternion.Euler(-30f * k, 0, 0);
            }
            else
            {
                if (ArmPivot != null) ArmPivot.localRotation = Quaternion.Slerp(ArmPivot.localRotation, Quaternion.identity, dt * 10f);
                if (WeaponPivot != null) WeaponPivot.localRotation = Quaternion.Slerp(WeaponPivot.localRotation, Quaternion.identity, dt * 10f);
            }

            if (u.Kind == UnitKind.Hero)
            {
                float giant = u.UltTicks > 0 && u.Hero == HeroId.Thotsakan ? 1.3f : 1f;
                transform.localScale = Vector3.Lerp(transform.localScale, Vector3.one * Scale * giant, dt * 8f);
                if (Faces != null) for (int i = 0; i < Faces.Length; i++) Faces[i].gameObject.SetActive(i < u.Faces);
                if (FormAura != null) FormAura.SetActive(u.UltTicks > 0 || u.ChargeTicks > 0);
            }
            if (u.Kind == UnitKind.HeartBox) transform.position = target + new Vector3(0, 0.7f + Mathf.Sin(Time.time * 2f) * 0.18f, 0);
        }
    }

    public static class Builders
    {
        // palette (taken from the character bible: gold ramp, ink outline, team colours)
        const string GOLD = "#f2c14e", GOLD_D = "#c88a24", GOLD_EM = "#3a2400";

        static Material Gold() { return Gfx.ToonMat(GOLD, GOLD_EM); }
        static Material GoldD() { return Gfx.ToonMat(GOLD_D, "#201000"); }

        // ---------------------------------------------------------------- shared body parts
        static Transform Chada(Transform parent, Vector3 pos, float scale, int tiers)
        {
            var root = new GameObject("chada").transform; root.SetParent(parent, false); root.localPosition = pos; root.localScale = Vector3.one * scale;
            Gfx.Part(root, Gfx.Taper(0.95f, 14), Gold(), new Vector3(0, 0, 0), new Vector3(0.6f, 0.14f, 0.6f));
            for (int i = 0; i < 10; i++)
            {
                float a = i / 10f * Mathf.PI * 2f;
                var k = Gfx.Part(root, Gfx.Cone(4), GoldD(), new Vector3(Mathf.Cos(a) * 0.27f, 0.12f, Mathf.Sin(a) * 0.27f), new Vector3(0.1f, 0.22f, 0.1f));
            }
            float y = 0.12f, r = 0.5f;
            for (int i = 0; i < tiers; i++)
            {
                Gfx.Part(root, Gfx.Taper(0.78f, 12), i % 2 == 0 ? Gold() : GoldD(), new Vector3(0, y, 0), new Vector3(r, 0.16f, r));
                y += 0.16f; r *= 0.8f;
            }
            Gfx.Part(root, Gfx.Cone(12), Gold(), new Vector3(0, y, 0), new Vector3(r, 0.75f, r));
            Gfx.Glow3D(root, new Color(1, 0.95f, 0.7f, 0.9f), 0.7f, new Vector3(0, y + 0.8f, 0));
            return root;
        }

        static Transform Face(Transform parent, string skinHex, bool yaksha, float size)
        {
            var root = new GameObject("face").transform; root.SetParent(parent, false);
            var skin = Gfx.ToonMat(skinHex);
            Gfx.Part(root, Gfx.Sphere, skin, Vector3.zero, new Vector3(0.5f, 0.56f, 0.5f) * size);
            var ink = Gfx.ToonMat("#1a0f20", "#1a0f20");
            for (int s = -1; s <= 1; s += 2)
            {
                if (yaksha)
                {
                    Gfx.Part(root, Gfx.Sphere, Gfx.ToonMat("#ffd43a", "#a07a00"), new Vector3(s * 0.11f, 0.03f, 0.22f) * size, new Vector3(0.16f, 0.14f, 0.1f) * size);
                    Gfx.Part(root, Gfx.Sphere, ink, new Vector3(s * 0.11f, 0.03f, 0.27f) * size, new Vector3(0.06f, 0.07f, 0.04f) * size);
                    var brow = Gfx.Part(root, Gfx.Box, ink, new Vector3(s * 0.11f, 0.13f, 0.23f) * size, new Vector3(0.2f, 0.035f, 0.03f) * size);
                    brow.transform.localRotation = Quaternion.Euler(0, 0, -s * 24f);
                    Gfx.Part(root, Gfx.Cone(5), Gfx.ToonMat("#fffaf0"), new Vector3(s * 0.07f, -0.14f, 0.2f) * size, new Vector3(0.05f, 0.12f, 0.05f) * size).transform.localRotation = Quaternion.Euler(180f, 0, 0);
                }
                else
                {
                    var eye = Gfx.Part(root, Gfx.Box, ink, new Vector3(s * 0.1f, 0.03f, 0.235f) * size, new Vector3(0.12f, 0.03f, 0.02f) * size);
                    eye.transform.localRotation = Quaternion.Euler(0, 0, -s * 6f);
                    var brow = Gfx.Part(root, Gfx.Box, ink, new Vector3(s * 0.1f, 0.1f, 0.23f) * size, new Vector3(0.14f, 0.025f, 0.02f) * size);
                    brow.transform.localRotation = Quaternion.Euler(0, 0, -s * 14f);
                }
            }
            if (yaksha) Gfx.Part(root, Gfx.Box, Gfx.ToonMat("#7a0f1a"), new Vector3(0, -0.13f, 0.22f) * size, new Vector3(0.26f, 0.045f, 0.03f) * size);
            else Gfx.Part(root, Gfx.Box, ink, new Vector3(0, -0.14f, 0.235f) * size, new Vector3(0.1f, 0.02f, 0.02f) * size);
            return root;
        }

        class Rig { public Transform Root, Body, ArmPivot, WeaponPivot, Head; }

        static Rig Warrior(Transform parent, string skin, string cloth, string cloth2, bool yaksha)
        {
            var rig = new Rig();
            rig.Root = parent;
            var body = new GameObject("body").transform; body.SetParent(parent, false); rig.Body = body;
            Material S = Gfx.ToonMat(skin), C = Gfx.ToonMat(cloth), C2 = Gfx.ToonMat(cloth2), G = Gold(), Gd = GoldD();
            // legs + boots
            for (int s = -1; s <= 1; s += 2)
            {
                Gfx.Limb(body, new Vector3(s * 0.17f, 1.25f, 0), new Vector3(s * 0.2f, 0.65f, 0.03f), 0.13f, C2);
                Gfx.Limb(body, new Vector3(s * 0.2f, 0.65f, 0.03f), new Vector3(s * 0.2f, 0.12f, 0), 0.1f, S);
                Gfx.Part(body, Gfx.Box, G, new Vector3(s * 0.2f, 0.07f, 0.07f), new Vector3(0.22f, 0.15f, 0.36f));
                Gfx.Part(body, Gfx.Torus(0.11f, 0.035f, 16, 6), G, new Vector3(s * 0.2f, 0.3f, 0), Vector3.one);
            }
            // waist cloth with front flap
            Gfx.Part(body, Gfx.Taper(0.78f, 14), C, new Vector3(0, 1.02f, 0), new Vector3(0.86f, 0.5f, 0.78f));
            Gfx.Part(body, Gfx.Box, C, new Vector3(0, 1.0f, 0.34f), new Vector3(0.3f, 0.66f, 0.05f));
            Gfx.Part(body, Gfx.Box, G, new Vector3(0, 1.34f, 0.35f), new Vector3(0.34f, 0.07f, 0.06f));
            Gfx.Part(body, Gfx.Torus(0.36f, 0.05f, 20, 6), G, new Vector3(0, 1.45f, 0), Vector3.one);
            // torso, V shaped
            Gfx.Part(body, Gfx.Taper(1.5f, 14), C, new Vector3(0, 1.45f, 0), new Vector3(0.6f, 0.78f, 0.5f));
            var plate = Gfx.Part(body, Gfx.Sphere, G, new Vector3(0, 1.88f, 0.1f), new Vector3(0.62f, 0.5f, 0.32f));
            Gfx.Part(body, Gfx.Sphere, Gfx.ToonMat(yaksha ? "#7a2aff" : "#ff3a4a", yaksha ? "#7a2aff" : "#ff3a4a"), new Vector3(0, 1.92f, 0.27f), new Vector3(0.1f, 0.12f, 0.06f));
            Gfx.Part(body, Gfx.Torus(0.27f, 0.06f, 18, 6), G, new Vector3(0, 2.2f, 0), Vector3.one);
            // shoulders with up-swept wings
            for (int s = -1; s <= 1; s += 2)
            {
                Gfx.Part(body, Gfx.Sphere, G, new Vector3(s * 0.46f, 2.12f, 0), new Vector3(0.3f, 0.22f, 0.3f));
                var w = Gfx.Part(body, Gfx.Cone(5), G, new Vector3(s * 0.5f, 2.18f, -0.02f), new Vector3(0.3f, 0.55f, 0.2f));
                w.transform.localRotation = Quaternion.Euler(0, 0, -s * 55f);
            }
            // cape
            var cape = Gfx.Part(body, Gfx.Box, C2, new Vector3(0, 1.5f, -0.3f), new Vector3(0.7f, 1.4f, 0.04f));
            cape.transform.localRotation = Quaternion.Euler(8f, 0, 0);
            // neck + head
            Gfx.Limb(body, new Vector3(0, 2.2f, 0), new Vector3(0, 2.42f, 0), 0.09f, S);
            var head = new GameObject("head").transform; head.SetParent(body, false); head.localPosition = new Vector3(0, 2.64f, 0); rig.Head = head;
            Face(head, skin, yaksha, 1f);
            // arms: left plain, right on a pivot so it can swing
            Gfx.Limb(body, new Vector3(-0.47f, 2.1f, 0), new Vector3(-0.58f, 1.55f, 0.18f), 0.085f, S);
            Gfx.Limb(body, new Vector3(-0.58f, 1.55f, 0.18f), new Vector3(-0.42f, 1.32f, 0.5f), 0.075f, S);
            var arm = new GameObject("armR").transform; arm.SetParent(body, false); arm.localPosition = new Vector3(0.47f, 2.1f, 0); rig.ArmPivot = arm;
            Gfx.Limb(arm, Vector3.zero, new Vector3(0.1f, -0.5f, 0.2f), 0.085f, S);
            Gfx.Limb(arm, new Vector3(0.1f, -0.5f, 0.2f), new Vector3(0.05f, -0.75f, 0.55f), 0.075f, S);
            Gfx.Part(arm, Gfx.Sphere, S, new Vector3(0.05f, -0.78f, 0.58f), Vector3.one * 0.17f);
            var weapon = new GameObject("weapon").transform; weapon.SetParent(arm, false); weapon.localPosition = new Vector3(0.05f, -0.78f, 0.58f); rig.WeaponPivot = weapon;
            return rig;
        }

        // ---------------------------------------------------------------- heroes
        public static UnitView Hero(Unit u, GameObject root)
        {
            var view = root.AddComponent<UnitView>(); view.Unit = u;
            if (u.Hero == HeroId.Rama)
            {
                var rig = Warrior(root.transform, "#3f9a6a", "#c8343f", "#7a1a24", false);
                Chada(rig.Head, new Vector3(0, 0.26f, 0), 1f, 7);
                // divine bow in the weapon pivot: naga-tipped golden arc held forward
                var bow = new GameObject("bow").transform; bow.SetParent(rig.WeaponPivot, false);
                var arc = Gfx.Part(bow, Gfx.Arc(1.0f, 0.045f, 170f, 28), Gold(), new Vector3(0, 0, 0), Vector3.one);
                arc.transform.localRotation = Quaternion.Euler(0f, 90f, 0f);
                Gfx.Part(bow, Gfx.Box, Gfx.ToonMat("#fff6c8", "#fff6c8"), new Vector3(0, 0, -0.18f), new Vector3(0.012f, 2.0f, 0.012f));
                Gfx.Part(bow, Gfx.Cone(5), Gfx.ToonMat("#fffbe6", "#fffbe6"), new Vector3(0, 0, 0.7f), new Vector3(0.05f, 0.35f, 0.05f)).transform.localRotation = Quaternion.Euler(90, 0, 0);
                view.Body = rig.Body; view.ArmPivot = rig.ArmPivot; view.WeaponPivot = rig.WeaponPivot;
                view.Scale = 0.9f; view.BaseHeight = 3.9f * 0.9f;
                view.FormAura = Aura(root.transform, new Color(1f, 0.8f, 0.3f, 0.6f), 1.8f);
            }
            else
            {
                var rig = Warrior(root.transform, "#2f8f5a", "#5a1630", "#2a0f1e", true);
                // ten faces: head is the main face, the crown tiers hold nine more
                var crown = new GameObject("crown").transform; crown.SetParent(rig.Head, false); crown.localPosition = new Vector3(0, 0.26f, 0);
                Gfx.Part(crown, Gfx.Taper(0.95f, 14), Gold(), Vector3.zero, new Vector3(0.62f, 0.14f, 0.62f));
                var faces = new List<Transform>();
                float[][] rows = { new[] { -1.2f, -0.4f, 0.4f, 1.2f }, new[] { -0.9f, 0f, 0.9f }, new[] { -0.45f, 0.45f } };
                float[] ry = { 0.22f, 0.5f, 0.74f }, rs = { 0.62f, 0.52f, 0.45f }, rr = { 0.3f, 0.23f, 0.17f };
                for (int row = 0; row < rows.Length; row++)
                    for (int i = 0; i < rows[row].Length; i++)
                    {
                        float a = rows[row][i];
                        var f = new GameObject("face" + faces.Count).transform; f.SetParent(crown, false);
                        f.localPosition = new Vector3(Mathf.Sin(a) * rr[row], ry[row], Mathf.Cos(a) * rr[row] * 0.55f);
                        f.localRotation = Quaternion.Euler(0, a * 34f, 0);
                        f.localScale = Vector3.one * rs[row];
                        Face(f, "#2f8f5a", true, 1f);
                        Gfx.Part(f, Gfx.Taper(0.7f, 10), Gold(), new Vector3(0, 0.22f, 0), new Vector3(0.45f, 0.14f, 0.45f));
                        faces.Add(f);
                    }
                Chada(crown, new Vector3(0, 0.86f, 0), 0.75f, 4);
                view.Faces = faces.ToArray();
                // khan sword in the weapon pivot (raised)
                var sw = new GameObject("sword").transform; sw.SetParent(rig.WeaponPivot, false);
                Gfx.Part(sw, Gfx.Box, Gfx.ToonMat("#e3ebf5", "#30101a"), new Vector3(0, 0.95f, 0.1f), new Vector3(0.11f, 1.8f, 0.04f));
                Gfx.Part(sw, Gfx.Cone(4), Gfx.ToonMat("#e3ebf5"), new Vector3(0, 1.85f, 0.1f), new Vector3(0.11f, 0.3f, 0.05f));
                Gfx.Part(sw, Gfx.Box, Gold(), new Vector3(0, 0.05f, 0.1f), new Vector3(0.5f, 0.1f, 0.12f));
                Gfx.Part(sw, Gfx.Box, Gfx.ToonMat("#ff4a6a", "#ff4a6a"), new Vector3(0.065f, 0.95f, 0.1f), new Vector3(0.02f, 1.8f, 0.05f));
                sw.localRotation = Quaternion.Euler(-60f, 0, -10f);
                view.Body = rig.Body; view.ArmPivot = rig.ArmPivot; view.WeaponPivot = rig.WeaponPivot;
                view.Scale = 1.15f; view.BaseHeight = 4.5f * 1.15f;
                view.FormAura = Aura(root.transform, new Color(0.9f, 0.1f, 0.25f, 0.6f), 2.6f);
            }
            Blob(root.transform, view.Scale * 1.6f);
            return view;
        }

        static GameObject Aura(Transform parent, Color c, float size)
        {
            var go = Gfx.Part(parent, Gfx.Quad, Gfx.Additive(c, Gfx.Ring), new Vector3(0, 0.08f, 0), Vector3.one * size * 1.6f, "aura");
            go.AddComponent<Spin>();
            go.SetActive(false);
            return go;
        }

        public static void Blob(Transform parent, float size)
        {
            Gfx.Part(parent, Gfx.Quad, Gfx.Alpha(new Color(0.02f, 0.03f, 0.04f, 0.45f), Gfx.Disc), new Vector3(0, 0.03f, 0), new Vector3(size, 1, size * 0.8f), "shadow");
        }

        // ---------------------------------------------------------------- minions
        public static UnitView Minion(Unit u, GameObject root)
        {
            var view = root.AddComponent<UnitView>(); view.Unit = u;
            bool ay = u.Team == Team.Ayodhya;
            bool siege = u.Kind == UnitKind.Siege;
            var rig = Warrior(root.transform, ay ? "#e8e4da" : "#4f7a62", ay ? "#2f5fa8" : "#6a1a2a", ay ? "#1a3260" : "#2a0f1e", !ay);
            float s = siege ? 0.5f : (u.Kind == UnitKind.Ranged ? 0.36f : 0.4f);
            root.transform.localScale = Vector3.one * s;
            view.Scale = s; view.BaseHeight = 3f * s;
            if (ay)
            {
                Gfx.Part(rig.Head, Gfx.Cone(8), Gfx.ToonMat("#c9ccd6"), new Vector3(0, 0.2f, 0), new Vector3(0.5f, 0.4f, 0.5f));
            }
            else
            {
                for (int sg = -1; sg <= 1; sg += 2) Gfx.Part(rig.Head, Gfx.Cone(6), Gold(), new Vector3(sg * 0.17f, 0.22f, 0), new Vector3(0.12f, 0.32f, 0.12f)).transform.localRotation = Quaternion.Euler(0, 0, -sg * 18f);
            }
            if (u.Kind == UnitKind.Ranged)
            {
                var bow = Gfx.Part(rig.WeaponPivot, Gfx.Arc(0.6f, 0.04f, 160f, 14), Gfx.ToonMat("#6a4a2a"), Vector3.zero, Vector3.one);
                bow.transform.localRotation = Quaternion.Euler(0, 90f, 0);
            }
            else if (siege)
            {
                Gfx.Part(rig.WeaponPivot, Gfx.Taper(0.7f, 8), Gfx.ToonMat("#5a3a22"), new Vector3(0, -0.2f, 0), new Vector3(0.28f, 1.2f, 0.28f));
            }
            else
            {
                Gfx.Part(rig.WeaponPivot, Gfx.Box, Gfx.ToonMat("#6a4a2a"), new Vector3(0, 0.6f, 0.1f), new Vector3(0.05f, 2f, 0.05f));
                Gfx.Part(rig.WeaponPivot, Gfx.Cone(4), Gfx.ToonMat("#d8dde6"), new Vector3(0, 1.6f, 0.1f), new Vector3(0.12f, 0.4f, 0.06f));
            }
            view.Body = rig.Body; view.ArmPivot = rig.ArmPivot; view.WeaponPivot = rig.WeaponPivot;
            Blob(root.transform, 3f);
            return view;
        }

        // ---------------------------------------------------------------- structures
        public static UnitView Turret(Unit u, GameObject root)
        {
            var view = root.AddComponent<UnitView>(); view.Unit = u;
            float sc = 1f + (u.Tier - 1) * 0.12f;
            if (u.Team == Team.Ayodhya)
            {
                var white = Gfx.ToonMat("#f4efe4"); var red = Gfx.ToonMat("#b8323c"); var stone = Gfx.ToonMat("#d9cdb4");
                Gfx.Part(root.transform, Gfx.Box, stone, new Vector3(0, 0.3f, 0), new Vector3(4f, 0.6f, 4f));
                Gfx.Part(root.transform, Gfx.Box, Gold(), new Vector3(0, 0.75f, 0), new Vector3(3.2f, 0.3f, 3.2f));
                Gfx.Part(root.transform, Gfx.Taper(0.8f, 8), white, new Vector3(0, 0.9f, 0), new Vector3(2.8f, 2.6f, 2.8f));
                for (int i = 0; i < 4; i++)
                {
                    float a = i * Mathf.PI / 2f + Mathf.PI / 8f;
                    var n = Gfx.Part(root.transform, Gfx.Box, red, new Vector3(Mathf.Cos(a) * 1.2f, 2.2f, Mathf.Sin(a) * 1.2f), new Vector3(0.7f, 1.2f, 0.18f));
                    n.transform.localRotation = Quaternion.Euler(0, -a * Mathf.Rad2Deg + 90f, 0);
                }
                float y = 3.5f, r = 2.1f;
                for (int i = 0; i < 5; i++) { Gfx.Part(root.transform, Gfx.Taper(0.78f, 8), i % 2 == 0 ? Gold() : white, new Vector3(0, y, 0), new Vector3(r, 0.7f, r)); y += 0.7f; r *= 0.78f; }
                Gfx.Part(root.transform, Gfx.Cone(8), Gold(), new Vector3(0, y, 0), new Vector3(r, 2.2f, r));
                Gfx.Part(root.transform, Gfx.Sphere, Gfx.ToonMat("#8fe0ff", "#8fe0ff"), new Vector3(0, y + 2.7f, 0), Vector3.one * 0.7f);
                Gfx.Glow3D(root.transform, new Color(0.5f, 0.85f, 1f, 0.8f), 4f, new Vector3(0, y + 2.7f, 0));
            }
            else
            {
                var stone = Gfx.ToonMat("#4a3f55"); var dark = Gfx.ToonMat("#2e2638"); var red = Gfx.ToonMat("#8c2030");
                Gfx.Part(root.transform, Gfx.Taper(0.85f, 6), dark, new Vector3(0, 0, 0), new Vector3(4.6f, 1f, 4.6f));
                Gfx.Part(root.transform, Gfx.Taper(0.7f, 6), stone, new Vector3(0, 1f, 0), new Vector3(3.2f, 4.2f, 3.2f));
                Gfx.Part(root.transform, Gfx.Taper(1.3f, 6), red, new Vector3(0, 5.2f, 0), new Vector3(2.6f, 1f, 2.6f));
                var face = Gfx.Part(root.transform, Gfx.Sphere, Gfx.ToonMat("#3d8a5c"), new Vector3(0, 6.9f, 0), new Vector3(2.3f, 2.4f, 2f));
                for (int s = -1; s <= 1; s += 2)
                {
                    Gfx.Part(root.transform, Gfx.Sphere, Gfx.ToonMat("#ffdf4a", "#ffdf4a"), new Vector3(s * 0.7f, 7.1f, 0.85f), Vector3.one * 0.5f);
                    Gfx.Part(root.transform, Gfx.Cone(5), Gfx.ToonMat("#ffffff"), new Vector3(s * 0.5f, 6.5f, 0.9f), new Vector3(0.22f, 0.7f, 0.22f)).transform.localRotation = Quaternion.Euler(180f, 0, 0);
                    Gfx.Part(root.transform, Gfx.Cone(6), Gold(), new Vector3(s * 1.1f, 7.8f, 0), new Vector3(0.5f, 1.4f, 0.5f)).transform.localRotation = Quaternion.Euler(0, 0, -s * 30f);
                }
                Gfx.Part(root.transform, Gfx.Cone(6), Gold(), new Vector3(0, 8.1f, 0), new Vector3(1.1f, 1.8f, 1.1f));
                Gfx.Glow3D(root.transform, new Color(1f, 0.25f, 0.4f, 0.85f), 5f, new Vector3(0, 9.9f, 0));
            }
            root.transform.localScale = Vector3.one * sc;
            view.Scale = sc; view.BaseHeight = 8f * sc;
            Blob(root.transform, 6f);
            return view;
        }

        public static UnitView Core(Unit u, GameObject root)
        {
            var view = root.AddComponent<UnitView>(); view.Unit = u;
            if (u.Team == Team.Ayodhya)
            {
                Gfx.Part(root.transform, Gfx.Taper(0.7f, 12), Gfx.ToonMat("#d9cdb4"), Vector3.zero, new Vector3(9f, 1.2f, 9f));
                Gfx.Part(root.transform, Gfx.Taper(0.6f, 10), Gfx.ToonMat("#f4efe4"), new Vector3(0, 1.2f, 0), new Vector3(6f, 4f, 6f));
                float y = 5.2f, r = 4.4f;
                for (int i = 0; i < 6; i++) { Gfx.Part(root.transform, Gfx.Taper(0.8f, 10), i % 2 == 0 ? Gold() : Gfx.ToonMat("#f4efe4"), new Vector3(0, y, 0), new Vector3(r, 1.0f, r)); y += 1f; r *= 0.78f; }
                Gfx.Part(root.transform, Gfx.Cone(10), Gold(), new Vector3(0, y, 0), new Vector3(r, 3f, r));
                Gfx.Part(root.transform, Gfx.Sphere, Gfx.ToonMat("#8fe0ff", "#8fe0ff"), new Vector3(0, y + 3.6f, 0), Vector3.one * 1.1f);
                Gfx.Glow3D(root.transform, new Color(0.5f, 0.85f, 1f, 0.9f), 7f, new Vector3(0, y + 3.6f, 0));
            }
            else
            {
                Gfx.Part(root.transform, Gfx.Taper(0.7f, 8), Gfx.ToonMat("#2e2638"), Vector3.zero, new Vector3(10f, 1.5f, 10f));
                Gfx.Part(root.transform, Gfx.Taper(0.55f, 8), Gfx.ToonMat("#4a3f55"), new Vector3(0, 1.5f, 0), new Vector3(7f, 5f, 7f));
                Gfx.Part(root.transform, Gfx.Taper(1.3f, 8), Gfx.ToonMat("#8c2030"), new Vector3(0, 6.5f, 0), new Vector3(5f, 1.4f, 5f));
                for (int i = 0; i < 6; i++)
                {
                    float a = i / 6f * Mathf.PI * 2f;
                    Gfx.Part(root.transform, Gfx.Cone(5), Gold(), new Vector3(Mathf.Cos(a) * 2.2f, 7.9f, Mathf.Sin(a) * 2.2f), new Vector3(0.7f, 3f, 0.7f));
                }
                Gfx.Part(root.transform, Gfx.Sphere, Gfx.ToonMat("#ff3a5a", "#ff3a5a"), new Vector3(0, 9.5f, 0), Vector3.one * 1.4f);
                Gfx.Glow3D(root.transform, new Color(1f, 0.2f, 0.4f, 0.9f), 8f, new Vector3(0, 9.5f, 0));
            }
            view.BaseHeight = 12f; Blob(root.transform, 10f);
            return view;
        }

        public static UnitView HeartBox(Unit u, GameObject root)
        {
            var view = root.AddComponent<UnitView>(); view.Unit = u;
            Gfx.Part(root.transform, Gfx.Box, Gfx.ToonMat("#5a1630", "#200610"), Vector3.zero, new Vector3(0.9f, 0.6f, 0.65f));
            Gfx.Part(root.transform, Gfx.Taper(0.8f, 4), Gold(), new Vector3(0, 0.3f, 0), new Vector3(1.0f, 0.3f, 0.75f));
            Gfx.Part(root.transform, Gfx.Sphere, Gfx.ToonMat("#ff4a8a", "#ff4a8a"), new Vector3(0, 0.75f, 0), Vector3.one * 0.35f);
            Gfx.Glow3D(root.transform, new Color(1f, 0.3f, 0.6f, 0.9f), 2.6f, new Vector3(0, 0.7f, 0));
            view.BaseHeight = 1.6f;
            return view;
        }

        // ---------------------------------------------------------------- environment
        public static GameObject Environment(Transform parent)
        {
            var env = new GameObject("environment").transform; env.SetParent(parent, false);
            var rnd = new System.Random(5);
            System.Func<double, double, double> R = (a, b) => a + (b - a) * rnd.NextDouble();

            Gfx.Part(env, Gfx.Quad, Gfx.ToonMat("#4b8338"), new Vector3(0, -0.02f, 0), new Vector3(200, 1, 120), "ground");
            for (int i = 0; i < 40; i++)
                Gfx.Part(env, Gfx.Quad, Gfx.ToonMat(rnd.Next(2) == 0 ? "#5a9a42" : "#3f7233"), new Vector3((float)R(-60, 60), -0.015f, (float)R(-28, 28)), new Vector3((float)R(6, 16), 1, (float)R(4, 10)), "patch");
            // lane
            Gfx.Part(env, Gfx.Quad, Gfx.ToonMat("#cdb98e"), new Vector3(0, 0.0f, 0), new Vector3(140, 1, 7.4f), "lane");
            for (int x = -64; x <= 64; x += 2)
                for (int row = 0; row < 3; row++)
                    if (((x / 2) + row) % 2 == 0)
                        Gfx.Part(env, Gfx.Quad, Gfx.ToonMat("#bba777"), new Vector3(x + row * 0.2f, 0.004f, (row - 1) * 2.2f), new Vector3(1.8f, 1, 1.9f), "tile");
            for (int s = -1; s <= 1; s += 2) Gfx.Part(env, Gfx.Box, Gfx.ToonMat("#e6d3a3"), new Vector3(0, 0.1f, s * 3.8f), new Vector3(140, 0.2f, 0.35f), "kerb");
            // river across the lane at x = 0
            Gfx.Part(env, Gfx.Quad, Gfx.Alpha(new Color(0.25f, 0.65f, 0.85f, 0.92f), Gfx.White), new Vector3(0, 0.05f, 0), new Vector3(9f, 1, 120), "river");
            Gfx.Part(env, Gfx.Quad, Gfx.Alpha(new Color(0.6f, 0.9f, 1f, 0.35f), Gfx.White), new Vector3(0, 0.06f, 0), new Vector3(5f, 1, 120), "river-core");
            for (int i = 0; i < 26; i++)
            {
                var pad = Gfx.Part(env, Gfx.Taper(1f, 14), Gfx.ToonMat("#3f8f4c"), new Vector3((float)R(-3.5, 3.5), 0.06f, (float)R(-30, 30)), new Vector3(1f, 0.06f, 1f), "pad");
                if (Mathf.Abs(pad.transform.position.z) < 4.5f) pad.SetActive(false);
            }
            // trees & rocks
            for (int x = -62; x <= 62; x += 3)
            {
                if (Mathf.Abs(x) < 6) continue;
                for (int side = -1; side <= 1; side += 2)
                    for (int row = 0; row < 2; row++)
                        Tree(env, new Vector3(x + (float)R(-1, 1), 0, side * (9f + row * 7f + (float)R(0, 3))), (float)R(1.0, 1.7), rnd.Next(4));
            }
            for (int i = 0; i < 26; i++)
                Gfx.Part(env, Gfx.Sphere, Gfx.ToonMat("#9a948a"), new Vector3((float)R(-60, 60), 0.2f, (rnd.Next(2) * 2 - 1) * (float)R(5, 8.5)), new Vector3((float)R(0.5, 1.4), (float)R(0.4, 0.9), (float)R(0.5, 1.3)), "rock");
            // lotus flowers on the river
            for (int i = 0; i < 12; i++)
            {
                float z = (float)R(-26, 26); if (Mathf.Abs(z) < 4.5f) continue;
                Gfx.Part(env, Gfx.Cone(6), Gfx.ToonMat("#ff9cc2", "#40101c"), new Vector3((float)R(-3, 3), 0.16f, z), new Vector3(0.45f, 0.5f, 0.45f), "lotus");
            }
            return env.gameObject;
        }

        static void Tree(Transform p, Vector3 pos, float s, int hue)
        {
            var t = new GameObject("tree").transform; t.SetParent(p, false); t.localPosition = pos; t.localScale = Vector3.one * s;
            Gfx.Part(t, Gfx.Taper(0.7f, 7), Gfx.ToonMat("#7a4a2a"), Vector3.zero, new Vector3(0.5f, 1.8f, 0.5f));
            string[] greens = { "#2f7a3a", "#3f9a48", "#58b257", "#2a6a44" };
            for (int i = 0; i < 3; i++)
                Gfx.Part(t, Gfx.Sphere, Gfx.ToonMat(greens[(i + hue) % 4]), new Vector3((i - 1) * 0.35f, 2.2f + i * 0.45f, (i % 2) * 0.3f), new Vector3(2.0f - i * 0.3f, 1.7f, 2.0f - i * 0.3f));
        }

    }

    public sealed class Spin : MonoBehaviour
    {
        void Update() { transform.Rotate(0, 60f * Time.deltaTime, 0, Space.Self); }
    }
}
