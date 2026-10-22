using System.Collections.Generic;
using UnityEngine;

namespace Ramakien.Moba.Game
{
    /// <summary>Procedural meshes and materials. Everything is generated in code, so the project needs no imported art to run.</summary>
    public static class Gfx
    {
        static Shader _toon, _fx;
        static readonly Dictionary<string, Material> _toonCache = new Dictionary<string, Material>();
        static readonly Dictionary<string, Mesh> _meshCache = new Dictionary<string, Mesh>();
        static Texture2D _glow, _ring, _disc, _white;

        public static Shader Toon { get { if (_toon == null) _toon = Resources.Load<Shader>("RamakienToon") ?? Shader.Find("Ramakien/Toon") ?? Shader.Find("Standard"); return _toon; } }
        public static Shader Fx { get { if (_fx == null) _fx = Resources.Load<Shader>("RamakienFX") ?? Shader.Find("Ramakien/FX") ?? Shader.Find("Sprites/Default"); return _fx; } }

        public static Color Hex(string h)
        {
            Color c; ColorUtility.TryParseHtmlString(h, out c); return c;
        }

        public static Material ToonMat(string hex, string emissiveHex = null)
        {
            string key = hex + "|" + emissiveHex;
            Material m;
            if (_toonCache.TryGetValue(key, out m)) return m;
            m = new Material(Toon);
            m.SetColor("_Color", Hex(hex));
            if (emissiveHex != null) m.SetColor("_Emission", Hex(emissiveHex));
            _toonCache[key] = m;
            return m;
        }

        public static Material Additive(Color c, Texture tex = null)
        {
            var m = new Material(Fx);
            m.SetColor("_Color", c);
            m.SetFloat("_Src", 5); m.SetFloat("_Dst", 1);          // SrcAlpha, One
            m.mainTexture = tex != null ? tex : White;
            return m;
        }

        public static Material Alpha(Color c, Texture tex = null)
        {
            var m = new Material(Fx);
            m.SetColor("_Color", c);
            m.SetFloat("_Src", 5); m.SetFloat("_Dst", 10);         // SrcAlpha, OneMinusSrcAlpha
            m.mainTexture = tex != null ? tex : White;
            return m;
        }

        // ---------------------------------------------------------------- textures
        public static Texture2D White
        {
            get
            {
                if (_white == null) { _white = new Texture2D(2, 2); _white.SetPixels(new[] { Color.white, Color.white, Color.white, Color.white }); _white.Apply(); }
                return _white;
            }
        }

        public static Texture2D Glow { get { if (_glow == null) _glow = Radial(64, 0f, 1f, 2.2f); return _glow; } }
        public static Texture2D Disc { get { if (_disc == null) _disc = Radial(64, 0f, 0.96f, 12f); return _disc; } }
        public static Texture2D Ring
        {
            get
            {
                if (_ring == null)
                {
                    int n = 128; var t = new Texture2D(n, n, TextureFormat.RGBA32, true); t.wrapMode = TextureWrapMode.Clamp;
                    for (int y = 0; y < n; y++) for (int x = 0; x < n; x++)
                    {
                        float dx = (x + 0.5f) / n * 2 - 1, dy = (y + 0.5f) / n * 2 - 1;
                        float r = Mathf.Sqrt(dx * dx + dy * dy);
                        float a = Mathf.Clamp01(1f - Mathf.Abs(r - 0.93f) / 0.05f) + Mathf.Clamp01(1f - Mathf.Abs(r - 0.78f) / 0.02f) * 0.6f;
                        t.SetPixel(x, y, new Color(1, 1, 1, Mathf.Clamp01(a)));
                    }
                    t.Apply(); _ring = t;
                }
                return _ring;
            }
        }

        static Texture2D Radial(int n, float inner, float outer, float falloff)
        {
            var t = new Texture2D(n, n, TextureFormat.RGBA32, true); t.wrapMode = TextureWrapMode.Clamp;
            for (int y = 0; y < n; y++) for (int x = 0; x < n; x++)
            {
                float dx = (x + 0.5f) / n * 2 - 1, dy = (y + 0.5f) / n * 2 - 1;
                float r = Mathf.Sqrt(dx * dx + dy * dy);
                float a = r >= outer ? 0f : Mathf.Pow(Mathf.Clamp01(1f - r / outer), falloff > 8f ? 0.15f : falloff);
                if (falloff > 8f) a = r <= outer ? 1f : 0f;
                t.SetPixel(x, y, new Color(1, 1, 1, a));
            }
            t.Apply(); return t;
        }

        // ---------------------------------------------------------------- meshes
        static Mesh Cached(string key, System.Func<Mesh> make)
        {
            Mesh m;
            if (!_meshCache.TryGetValue(key, out m)) { m = make(); m.name = key; _meshCache[key] = m; }
            return m;
        }

        public static Mesh Sphere { get { return Cached("sphere", () => Lathe(new[] { new Vector2(0, -0.5f), new Vector2(0.2f, -0.46f), new Vector2(0.36f, -0.35f), new Vector2(0.45f, -0.2f), new Vector2(0.5f, 0), new Vector2(0.45f, 0.2f), new Vector2(0.36f, 0.35f), new Vector2(0.2f, 0.46f), new Vector2(0, 0.5f) }, 20)); } }
        public static Mesh Cone(int sides = 10) { return Cached("cone" + sides, () => Lathe(new[] { new Vector2(0, 0), new Vector2(0.5f, 0), new Vector2(0, 1f) }, sides)); }
        /// <summary>Tapered cylinder of height 1 standing on y = 0. radiusTop is a fraction of the bottom radius 0.5.</summary>
        public static Mesh Taper(float topRatio, int sides = 12) { return Cached("taper" + topRatio + "_" + sides, () => Lathe(new[] { new Vector2(0, 0), new Vector2(0.5f, 0), new Vector2(0.5f * topRatio, 1f), new Vector2(0, 1f) }, sides)); }
        public static Mesh Capsule { get { return Cached("capsule", () => Lathe(new[] { new Vector2(0, 0), new Vector2(0.28f, 0.03f), new Vector2(0.45f, 0.14f), new Vector2(0.5f, 0.3f), new Vector2(0.5f, 0.7f), new Vector2(0.45f, 0.86f), new Vector2(0.28f, 0.97f), new Vector2(0, 1f) }, 12)); } }
        public static Mesh Torus(float majorR, float minorR, int seg = 24, int sides = 8) { return Cached("torus" + majorR + "_" + minorR + "_" + seg, () => MakeTorus(majorR, minorR, seg, sides, 360f)); }
        public static Mesh Arc(float majorR, float minorR, float degrees, int seg = 24) { return Cached("arc" + majorR + "_" + minorR + "_" + degrees, () => MakeTorus(majorR, minorR, seg, 6, degrees)); }

        public static Mesh Box { get { return Cached("box", () => MakeBox()); } }
        public static Mesh Quad { get { return Cached("quad", () => MakeQuad()); } }

        /// <summary>Surface of revolution from a profile of (radius, y) points. Smooth normals.</summary>
        public static Mesh Lathe(Vector2[] profile, int sides)
        {
            var verts = new List<Vector3>(); var norms = new List<Vector3>(); var uvs = new List<Vector2>(); var cols = new List<Color>(); var tris = new List<int>();
            int rings = profile.Length;
            for (int r = 0; r < rings; r++)
            {
                Vector2 p = profile[r];
                Vector2 prev = profile[Mathf.Max(0, r - 1)], next = profile[Mathf.Min(rings - 1, r + 1)];
                Vector2 tan = next - prev; Vector2 n2 = new Vector2(tan.y, -tan.x).normalized;   // outward in (radius,y)
                if (tan.sqrMagnitude < 1e-8f) n2 = Vector2.up;
                for (int s = 0; s <= sides; s++)
                {
                    float a = (float)s / sides * Mathf.PI * 2f;
                    float ca = Mathf.Cos(a), sa = Mathf.Sin(a);
                    verts.Add(new Vector3(p.x * ca, p.y, p.x * sa));
                    norms.Add(new Vector3(n2.x * ca, n2.y, n2.x * sa).normalized);
                    uvs.Add(new Vector2((float)s / sides, (float)r / (rings - 1)));
                    cols.Add(Color.white);
                }
            }
            int stride = sides + 1;
            for (int r = 0; r < rings - 1; r++)
                for (int s = 0; s < sides; s++)
                {
                    int a = r * stride + s, b = a + 1, c = a + stride, d = c + 1;
                    tris.Add(a); tris.Add(c); tris.Add(b);
                    tris.Add(b); tris.Add(c); tris.Add(d);
                }
            var m = new Mesh(); m.SetVertices(verts); m.SetNormals(norms); m.SetUVs(0, uvs); m.SetColors(cols); m.SetTriangles(tris, 0);
            m.RecalculateBounds(); return m;
        }

        static Mesh MakeTorus(float R, float r, int seg, int sides, float degrees)
        {
            var verts = new List<Vector3>(); var norms = new List<Vector3>(); var cols = new List<Color>(); var uvs = new List<Vector2>(); var tris = new List<int>();
            for (int i = 0; i <= seg; i++)
            {
                float a = (float)i / seg * degrees * Mathf.Deg2Rad;
                Vector3 c = new Vector3(Mathf.Cos(a) * R, 0, Mathf.Sin(a) * R);
                Vector3 outDir = new Vector3(Mathf.Cos(a), 0, Mathf.Sin(a));
                for (int j = 0; j <= sides; j++)
                {
                    float b = (float)j / sides * Mathf.PI * 2f;
                    Vector3 n = outDir * Mathf.Cos(b) + Vector3.up * Mathf.Sin(b);
                    verts.Add(c + n * r); norms.Add(n); cols.Add(Color.white); uvs.Add(new Vector2((float)i / seg, (float)j / sides));
                }
            }
            int st = sides + 1;
            for (int i = 0; i < seg; i++) for (int j = 0; j < sides; j++)
            {
                int a = i * st + j, b = a + 1, c2 = a + st, d = c2 + 1;
                tris.Add(a); tris.Add(b); tris.Add(c2); tris.Add(b); tris.Add(d); tris.Add(c2);
            }
            var m = new Mesh(); m.SetVertices(verts); m.SetNormals(norms); m.SetUVs(0, uvs); m.SetColors(cols); m.SetTriangles(tris, 0);
            m.RecalculateBounds(); return m;
        }

        static Mesh MakeBox()
        {
            var v = new List<Vector3>(); var n = new List<Vector3>(); var t = new List<int>(); var c = new List<Color>(); var uv = new List<Vector2>();
            Vector3[] nrm = { Vector3.up, Vector3.down, Vector3.left, Vector3.right, Vector3.forward, Vector3.back };
            for (int f = 0; f < 6; f++)
            {
                Vector3 N = nrm[f];
                Vector3 U = f < 2 ? Vector3.right : (f < 4 ? Vector3.forward : Vector3.right);
                Vector3 V = Vector3.Cross(N, U);
                int b = v.Count;
                v.Add((N - U - V) * 0.5f); v.Add((N + U - V) * 0.5f); v.Add((N + U + V) * 0.5f); v.Add((N - U + V) * 0.5f);
                for (int i = 0; i < 4; i++) { n.Add(N); c.Add(Color.white); }
                uv.Add(new Vector2(0, 0)); uv.Add(new Vector2(1, 0)); uv.Add(new Vector2(1, 1)); uv.Add(new Vector2(0, 1));
                bool flip = Vector3.Dot(Vector3.Cross(v[b + 1] - v[b], v[b + 2] - v[b]), N) < 0;
                if (flip) { t.Add(b); t.Add(b + 2); t.Add(b + 1); t.Add(b); t.Add(b + 3); t.Add(b + 2); }
                else { t.Add(b); t.Add(b + 1); t.Add(b + 2); t.Add(b); t.Add(b + 2); t.Add(b + 3); }
            }
            var m = new Mesh(); m.SetVertices(v); m.SetNormals(n); m.SetUVs(0, uv); m.SetColors(c); m.SetTriangles(t, 0); m.RecalculateBounds(); return m;
        }

        static Mesh MakeQuad()
        {
            var m = new Mesh();
            m.SetVertices(new List<Vector3> { new Vector3(-0.5f, 0, -0.5f), new Vector3(0.5f, 0, -0.5f), new Vector3(0.5f, 0, 0.5f), new Vector3(-0.5f, 0, 0.5f) });
            m.SetNormals(new List<Vector3> { Vector3.up, Vector3.up, Vector3.up, Vector3.up });
            m.SetUVs(0, new List<Vector2> { new Vector2(0, 0), new Vector2(1, 0), new Vector2(1, 1), new Vector2(0, 1) });
            m.SetColors(new List<Color> { Color.white, Color.white, Color.white, Color.white });
            m.SetTriangles(new List<int> { 0, 2, 1, 0, 3, 2, 0, 1, 2, 0, 2, 3 }, 0);       // double sided
            m.RecalculateBounds(); return m;
        }

        // ---------------------------------------------------------------- builders
        public static GameObject Part(Transform parent, Mesh mesh, Material mat, Vector3 pos, Vector3 scale, string name = "part")
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.transform.localPosition = pos; go.transform.localScale = scale;
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var r = go.AddComponent<MeshRenderer>(); r.sharedMaterial = mat;
            r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off; r.receiveShadows = false;
            return go;
        }

        /// <summary>Capsule limb between two local points (capsule mesh stands on its local origin, so the pivot is point a).</summary>
        public static GameObject Limb(Transform parent, Vector3 a, Vector3 b, float radius, Material mat)
        {
            Vector3 d = b - a;
            var go = Part(parent, Capsule, mat, a, new Vector3(radius * 2f, d.magnitude, radius * 2f), "limb");
            go.transform.localRotation = Quaternion.FromToRotation(Vector3.up, d.normalized);
            return go;
        }

        public static GameObject Glow3D(Transform parent, Color c, float size, Vector3 pos)
        {
            var go = Part(parent, Quad, Additive(c, Glow), pos, Vector3.one * size, "glow");
            go.AddComponent<Billboard>();
            return go;
        }
    }

    /// <summary>Faces the camera (used for glow sprites).</summary>
    public sealed class Billboard : MonoBehaviour
    {
        void LateUpdate()
        {
            var cam = Camera.main; if (cam == null) return;
            // Quad lies in XZ; rotate so its up-normal points at the camera
            transform.rotation = Quaternion.LookRotation(cam.transform.forward, cam.transform.up) * Quaternion.Euler(90, 0, 0);
        }
    }
}
