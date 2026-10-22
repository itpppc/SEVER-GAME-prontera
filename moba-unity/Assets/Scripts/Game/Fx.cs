using System.Collections.Generic;
using UnityEngine;

namespace Ramakien.Moba.Game
{
    /// <summary>Short-lived world effects: glows, rings, beams, telegraphs. Pure visuals.</summary>
    public sealed class Fader : MonoBehaviour
    {
        public Material Mat; public Color Base; public float Life = 0.5f, T;
        public Vector3 S0, S1; public bool PulseAlpha;
        void Update()
        {
            T += Time.deltaTime;
            float k = Mathf.Clamp01(T / Life);
            transform.localScale = Vector3.Lerp(S0, S1, 1f - (1f - k) * (1f - k));
            float a = PulseAlpha ? (0.55f + 0.45f * Mathf.Sin(T * 18f)) * (1f - k * 0.3f) : (1f - k);
            if (Mat != null) { var c = Base; c.a = Base.a * a; Mat.SetColor("_Color", c); }
            if (T >= Life) { if (Mat != null) Destroy(Mat); Destroy(gameObject); }
        }
    }

    public static class Fx
    {
        static Transform _root;
        public static Transform Root { get { if (_root == null) _root = new GameObject("fx").transform; return _root; } }
        public static void Reset() { if (_root != null) Object.Destroy(_root.gameObject); _root = null; }

        static Fader Make(Mesh mesh, Material mat, Vector3 pos, Quaternion rot, Vector3 s0, Vector3 s1, float life, Color c, bool pulse = false)
        {
            var go = new GameObject("fx"); go.transform.SetParent(Root, false);
            go.transform.position = pos; go.transform.rotation = rot;
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var r = go.AddComponent<MeshRenderer>(); r.sharedMaterial = mat;
            r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off; r.receiveShadows = false;
            var f = go.AddComponent<Fader>(); f.Mat = mat; f.Base = c; f.Life = life; f.S0 = s0; f.S1 = s1; f.PulseAlpha = pulse;
            return f;
        }

        static Quaternion Facing()
        {
            var cam = Camera.main;
            return cam != null ? Quaternion.LookRotation(cam.transform.forward, cam.transform.up) * Quaternion.Euler(90, 0, 0) : Quaternion.identity;
        }

        public static void Flash(Vector3 pos, Color c, float size, float life = 0.25f)
        {
            Make(Gfx.Quad, Gfx.Additive(c, Gfx.Glow), pos, Facing(), Vector3.one * size * 0.4f, Vector3.one * size, life, c);
        }

        public static void Ring(Vector3 pos, Color c, float size, float life = 0.45f)
        {
            Make(Gfx.Quad, Gfx.Additive(c, Gfx.Ring), new Vector3(pos.x, 0.12f, pos.z), Quaternion.identity, Vector3.one * size * 0.2f, Vector3.one * size, life, c);
        }

        public static void Sparks(Vector3 pos, Color c, int n, float spread)
        {
            for (int i = 0; i < n; i++)
            {
                Vector3 off = new Vector3(Random.Range(-1f, 1f), Random.Range(0f, 1f), Random.Range(-1f, 1f)) * spread;
                Flash(pos + off, c, Random.Range(0.25f, 0.6f), Random.Range(0.18f, 0.4f));
            }
        }

        /// <summary>Thin glowing bolt from a to b (arrows, turret shots).</summary>
        public static void Bolt(Vector3 a, Vector3 b, Color c, float width, float life)
        {
            Vector3 d = b - a; float len = d.magnitude; if (len < 0.01f) return;
            Make(Gfx.Box, Gfx.Additive(c), (a + b) * 0.5f, Quaternion.LookRotation(d), new Vector3(width, width, len), new Vector3(width * 0.3f, width * 0.3f, len), life, c);
            Flash(b, c, width * 4f, life);
        }

        /// <summary>Ground rectangle shown while a line skill is charging (both teams see it).</summary>
        public static void Telegraph(Vector3 from, Vector3 dir, float length, float width, Color c, float life)
        {
            dir.y = 0; if (dir.sqrMagnitude < 0.0001f) dir = Vector3.right; dir.Normalize();
            Quaternion rot = Quaternion.LookRotation(dir);
            Make(Gfx.Quad, Gfx.Alpha(c, Gfx.White), from + dir * (length * 0.5f) + Vector3.up * 0.1f, rot, new Vector3(width, 1, length), new Vector3(width * 0.8f, 1, length), life, c, true);
            Make(Gfx.Quad, Gfx.Additive(c, Gfx.White), from + dir * (length * 0.5f) + Vector3.up * 0.11f, rot, new Vector3(width * 0.12f, 1, length), new Vector3(width * 0.12f, 1, length), life, new Color(1, 1, 0.8f, 0.8f), true);
        }

        /// <summary>The Brahmastra beam: layered additive boxes, rings along the line, glow at both ends.</summary>
        public static void Brahmastra(Vector3 from, Vector3 dir, float length)
        {
            dir.y = 0; dir.Normalize();
            Vector3 a = from + Vector3.up * 1.6f, b = a + dir * length;
            Quaternion rot = Quaternion.LookRotation(dir);
            Vector3 mid = (a + b) * 0.5f;
            Make(Gfx.Box, Gfx.Additive(new Color(1f, 0.6f, 0.15f, 0.22f)), mid, rot, new Vector3(2.4f, 2.4f, length), new Vector3(0.4f, 0.4f, length), 0.7f, new Color(1f, 0.6f, 0.15f, 0.22f));
            Make(Gfx.Box, Gfx.Additive(new Color(1f, 0.8f, 0.3f, 0.5f)), mid, rot, new Vector3(1.3f, 1.3f, length), new Vector3(0.25f, 0.25f, length), 0.65f, new Color(1f, 0.8f, 0.3f, 0.5f));
            Make(Gfx.Box, Gfx.Additive(new Color(1f, 0.97f, 0.8f, 0.95f)), mid, rot, new Vector3(0.55f, 0.55f, length), new Vector3(0.1f, 0.1f, length), 0.6f, new Color(1f, 0.97f, 0.8f, 0.95f));
            for (int i = 0; i < 24; i++)
            {
                Vector3 p = a + dir * (i * length / 24f + 1f);
                var q = Quaternion.LookRotation(dir) * Quaternion.Euler(90, 0, 0);
                Make(Gfx.Quad, Gfx.Additive(new Color(1f, 0.9f, 0.5f, 0.8f), Gfx.Ring), p, q, Vector3.one * 1.2f, Vector3.one * (2.6f + (i % 3) * 0.6f), 0.55f, new Color(1f, 0.9f, 0.5f, 0.8f));
            }
            Flash(a, new Color(1f, 0.9f, 0.6f, 1f), 7f, 0.5f);
            Flash(b, new Color(1f, 0.8f, 0.4f, 1f), 5f, 0.5f);
            Ring(from, new Color(1f, 0.85f, 0.4f, 1f), 9f, 0.6f);
        }
    }

    /// <summary>Procedural sound effects (no audio files needed).</summary>
    public static class Sfx
    {
        static AudioSource _src; static readonly Dictionary<string, AudioClip> _c = new Dictionary<string, AudioClip>();
        public static bool Mute;

        static AudioClip Make(string key, float dur, System.Func<float, float, float> f)
        {
            AudioClip c;
            if (_c.TryGetValue(key, out c)) return c;
            int rate = 22050, n = (int)(rate * dur);
            var data = new float[n];
            for (int i = 0; i < n; i++) { float t = (float)i / rate; data[i] = Mathf.Clamp(f(t, t / dur), -1f, 1f); }
            c = AudioClip.Create(key, n, 1, rate, false); c.SetData(data, 0);
            _c[key] = c; return c;
        }

        static float Noise(int i) { uint x = (uint)(i * 747796405u + 2891336453u); x = ((x >> (int)((x >> 28) + 4)) ^ x) * 277803737u; return ((x >> 22) ^ x) / (float)uint.MaxValue * 2f - 1f; }

        public static void Play(string name, float vol = 0.6f)
        {
            if (Mute) return;
            if (_src == null)
            {
                var go = new GameObject("sfx"); Object.DontDestroyOnLoad(go); _src = go.AddComponent<AudioSource>(); _src.spatialBlend = 0;
            }
            AudioClip clip = null;
            switch (name)
            {
                case "hit": clip = Make(name, 0.09f, (t, k) => Noise((int)(t * 22050)) * 0.5f * (1 - k) + Mathf.Sin(t * 2 * Mathf.PI * 180f) * 0.5f * (1 - k)); break;
                case "shoot": clip = Make(name, 0.14f, (t, k) => Mathf.Sin(t * 2 * Mathf.PI * (900f - 600f * k)) * 0.4f * (1 - k)); break;
                case "swing": clip = Make(name, 0.2f, (t, k) => Noise((int)(t * 22050)) * 0.35f * Mathf.Sin(k * Mathf.PI)); break;
                case "skill": clip = Make(name, 0.3f, (t, k) => Mathf.Sin(t * 2 * Mathf.PI * (300f + 500f * k)) * 0.35f * (1 - k)); break;
                case "charge": clip = Make(name, 1.25f, (t, k) => Mathf.Sin(t * 2 * Mathf.PI * (200f + 900f * k * k)) * 0.3f * k); break;
                case "boom": clip = Make(name, 0.9f, (t, k) => (Noise((int)(t * 22050)) * 0.6f + Mathf.Sin(t * 2 * Mathf.PI * (90f - 50f * k)) * 0.9f) * (1 - k) * (1 - k)); break;
                case "level": clip = Make(name, 0.5f, (t, k) => (Mathf.Sin(t * 2 * Mathf.PI * (k < 0.5f ? 660f : 880f)) * 0.3f) * (1 - k)); break;
                case "tower": clip = Make(name, 0.5f, (t, k) => (Noise((int)(t * 22050)) * 0.5f + Mathf.Sin(t * 2 * Mathf.PI * 70f)) * (1 - k) * 0.8f); break;
                default: return;
            }
            _src.PlayOneShot(clip, vol);
        }
    }
}
