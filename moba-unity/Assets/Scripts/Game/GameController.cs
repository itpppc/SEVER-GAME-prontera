using System.Collections.Generic;
using UnityEngine;
using Ramakien.Moba.Sim;

namespace Ramakien.Moba.Game
{
    /// <summary>Boots itself (no scene setup needed): menu, match loop at 30 Hz, input, camera, effects and HUD.</summary>
    public sealed class GameController : MonoBehaviour
    {
        enum Mode { Menu, Playing, Over }
        static bool _booted;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Boot()
        {
            if (_booted) return;
            _booted = true;
            new GameObject("RamakienMoba").AddComponent<GameController>();
        }

        // ---------------------------------------------------------------- state
        Mode _mode = Mode.Menu;
        World _w; Bot _bot;
        int _me, _foe;                         // hero slots
        HeroId _pick = HeroId.Rama; int _difficulty = 1;
        float _acc; float _timeScale = 1f;
        readonly Dictionary<int, UnitView> _views = new Dictionary<int, UnitView>();
        Transform _worldRoot; Camera _cam; Vector3 _camPos; float _shake;
        Font _font;

        // input
        int _joyFinger = int.MinValue; Vector2 _joyOrigin, _joyVec; bool _attackHeld;
        readonly bool[] _skillPressed = new bool[3];
        float _scale = 1f, _vw = 1920f;

        // hud
        struct Float { public Vector3 Pos; public string Text; public float T; public Color C; public int Size; }
        readonly List<Float> _floats = new List<Float>();
        string _banner = ""; float _bannerT; Color _bannerC = Color.white;
        readonly List<string> _feed = new List<string>(); readonly List<float> _feedT = new List<float>();
        bool _blueWon;

        GUIStyle _st;

        // ---------------------------------------------------------------- lifecycle
        void Awake()
        {
            Application.targetFrameRate = 60;
            QualitySettings.vSyncCount = 0;
            Screen.orientation = ScreenOrientation.LandscapeLeft;
            _font = Font.CreateDynamicFontFromOSFont(new[] { "Leelawadee UI", "Tahoma", "Noto Sans Thai", "Noto Sans", "Droid Sans", "Arial" }, 44);
            SetupCamera();
            Prepare(false);
        }

        void SetupCamera()
        {
            _cam = Camera.main;
            if (_cam == null) { var go = new GameObject("Main Camera"); go.tag = "MainCamera"; _cam = go.AddComponent<Camera>(); go.AddComponent<AudioListener>(); }
            _cam.clearFlags = CameraClearFlags.SolidColor;
            _cam.backgroundColor = Gfx.Hex("#1c2622");
            _cam.fieldOfView = 36f; _cam.nearClipPlane = 0.5f; _cam.farClipPlane = 220f;
            RenderSettings.fog = true; RenderSettings.fogMode = FogMode.Linear;
            RenderSettings.fogColor = Gfx.Hex("#1c2622"); RenderSettings.fogStartDistance = 55f; RenderSettings.fogEndDistance = 130f;
        }

        void StartMatch()
        {
            Cleanup();
            Prepare(true);
            Banner(_pick == HeroId.Rama ? "ศึกลงกา เริ่มแล้ว!" : "ลงกา บุกอโยธยา!", new Color(1f, 0.85f, 0.4f), 2.5f);
            Sfx.Play("level");
        }

        /// <summary>Builds the world and its views. play=false builds a still preview for the menu background.</summary>
        void Prepare(bool play)
        {
            _me = _pick == HeroId.Rama ? 0 : 1; _foe = 1 - _me;
            _w = new World((uint)(System.DateTime.Now.Ticks & 0x7fffffff), HeroId.Rama, HeroId.Thotsakan);
            _bot = new Bot(_foe, _difficulty);
            _worldRoot = new GameObject("world").transform;
            Builders.Environment(_worldRoot);
            _views.Clear(); _floats.Clear(); _feed.Clear(); _feedT.Clear();
            if (!play)
            {
                _w.Heroes[0].Pos = new Vec2(-900, 150); _w.Heroes[0].Facing = new Vec2(1000, 0);
                _w.Heroes[1].Pos = new Vec2(900, -100); _w.Heroes[1].Facing = new Vec2(-1000, 0);
                _w.Units.RemoveAll(u => u.IsMinion);
            }
            for (int i = 0; i < _w.Units.Count; i++) AddView(_w.Units[i]);
            foreach (var kv in _views) kv.Value.transform.position = new Vector3(kv.Value.Unit.Pos.X / 100f, 0, kv.Value.Unit.Pos.Z / 100f);
            _acc = 0; _timeScale = 1f; _mode = play ? Mode.Playing : Mode.Menu;
            var h = _w.Heroes[_me];
            _camPos = new Vector3(h.Pos.X / 100f, 0, h.Pos.Z / 100f);
            _joyFinger = int.MinValue; _joyVec = Vector2.zero; _attackHeld = false; _atkFinger = int.MinValue;
        }

        void Cleanup()
        {
            foreach (var kv in _views) if (kv.Value != null) Destroy(kv.Value.gameObject);
            _views.Clear();
            if (_worldRoot != null) Destroy(_worldRoot.gameObject);
            Fx.Reset();
        }

        UnitView AddView(Unit u)
        {
            var go = new GameObject(u.Kind + "_" + u.Id);
            go.transform.SetParent(_worldRoot, false);
            go.transform.position = new Vector3(u.Pos.X / 100f, 0, u.Pos.Z / 100f);
            UnitView v;
            switch (u.Kind)
            {
                case UnitKind.Hero: v = Builders.Hero(u, go); break;
                case UnitKind.Turret: v = Builders.Turret(u, go); break;
                case UnitKind.Core: v = Builders.Core(u, go); break;
                case UnitKind.HeartBox: v = Builders.HeartBox(u, go); break;
                default: v = Builders.Minion(u, go); break;
            }
            v.LastPos = go.transform.position;
            _views[u.Id] = v;
            return v;
        }

        // ---------------------------------------------------------------- update
        void Update()
        {
            _scale = Screen.height / 1080f; _vw = Screen.width / _scale;
            if (_mode == Mode.Playing) PlayUpdate();
            else if (_mode == Mode.Over) { SyncViews(Time.deltaTime); UpdateCamera(Time.deltaTime); ReadMenuInput(); }
            else { ReadMenuInput(); SyncViews(Time.deltaTime); IdleCamera(); }
            for (int i = _floats.Count - 1; i >= 0; i--) { var f = _floats[i]; f.T += Time.deltaTime; if (f.T > 1.1f) _floats.RemoveAt(i); else _floats[i] = f; }
            if (_bannerT > 0) _bannerT -= Time.deltaTime;
            for (int i = _feed.Count - 1; i >= 0; i--) { _feedT[i] -= Time.deltaTime; if (_feedT[i] <= 0) { _feed.RemoveAt(i); _feedT.RemoveAt(i); } }
        }

        void IdleCamera()
        {
            _cam.transform.position = new Vector3(Mathf.Sin(Time.time * 0.2f) * 5f, 6.5f, 14f);
            _cam.transform.rotation = Quaternion.LookRotation(new Vector3(0, 3.2f, 0) - _cam.transform.position);
        }

        void PlayUpdate()
        {
            ReadGameInput();
            _acc += Time.deltaTime * _timeScale;
            int guard = 0;
            while (_acc >= 1f / SimMath.TickHz && guard++ < 6)
            {
                _acc -= 1f / SimMath.TickHz;
                _w.Cmd[_me] = BuildPlayerCommand();
                _w.Cmd[_foe] = _bot.Think(_w);
                _w.Step();
                for (int i = 0; i < _skillPressed.Length; i++) _skillPressed[i] = false;
                HandleEvents();
                if (_w.Winner.HasValue) { _blueWon = (int)_w.Winner.Value == _me; _mode = Mode.Over; Banner(_blueWon ? "ชัยชนะ!" : "พ่ายแพ้", _blueWon ? new Color(1f, 0.85f, 0.3f) : new Color(1f, 0.35f, 0.35f), 6f); break; }
            }
            SyncViews(Time.deltaTime);
            UpdateCamera(Time.deltaTime);
        }

        void SyncViews(float dt)
        {
            // create views for new units, retire views for dead ones
            for (int i = 0; i < _w.Units.Count; i++) { var u = _w.Units[i]; if (u.Alive && !_views.ContainsKey(u.Id)) AddView(u); }
            var remove = new List<int>();
            foreach (var kv in _views)
            {
                var v = kv.Value; var u = v.Unit;
                if (!u.Alive && u.Kind != UnitKind.Hero)
                {
                    v.DeathT += dt;
                    v.transform.localScale = Vector3.Lerp(v.transform.localScale, Vector3.zero, dt * 9f);
                    if (v.DeathT > 0.35f) { Destroy(v.gameObject); remove.Add(kv.Key); }
                    continue;
                }
                bool vis = u.Alive;
                if (v.gameObject.activeSelf != vis) v.gameObject.SetActive(vis);
                if (vis) v.Sync(dt);
            }
            foreach (var k in remove) _views.Remove(k);
        }

        void UpdateCamera(float dt)
        {
            var h = _w.Heroes[_me];
            Vector3 want = new Vector3(Mathf.Clamp(h.Pos.X / 100f, -48f, 48f), 0, h.Pos.Z / 100f * 0.5f);
            _camPos = Vector3.Lerp(_camPos, want, Mathf.Clamp01(dt * 5f));
            _shake = Mathf.Max(0, _shake - dt * 3f);
            Vector3 jitter = new Vector3(Random.Range(-1f, 1f), Random.Range(-1f, 1f), 0) * _shake * 0.35f;
            _cam.transform.position = _camPos + new Vector3(0f, 17f, 15.5f) + jitter;
            _cam.transform.rotation = Quaternion.LookRotation(_camPos + new Vector3(0, 1.2f, -0.5f) - _cam.transform.position);
        }

        // ---------------------------------------------------------------- events -> effects
        Vector3 P(Vec2 v) { return new Vector3(v.X / 100f, 0, v.Z / 100f); }

        void HandleEvents()
        {
            for (int i = 0; i < _w.Events.Count; i++)
            {
                var e = _w.Events[i];
                switch (e.Type)
                {
                    case SimEvent.T.Damage:
                    {
                        if (e.Amount <= 0) break;
                        UnitView sv, dv; _views.TryGetValue(e.A, out sv); _views.TryGetValue(e.B, out dv);
                        bool big = e.Amount >= 300;
                        bool toMe = e.B == _w.Heroes[_me].Id;
                        bool fromMe = e.A == _w.Heroes[_me].Id;
                        if (dv != null && (fromMe || toMe || big || dv.Unit.Kind == UnitKind.Hero))
                            _floats.Add(new Float { Pos = P(e.P) + Vector3.up * (dv.BaseHeight * 0.8f), Text = "-" + e.Amount, T = 0, C = toMe ? new Color(1f, 0.35f, 0.3f) : (big ? new Color(1f, 0.85f, 0.3f) : new Color(1f, 0.97f, 0.9f)), Size = big ? 56 : 34 });
                        if (dv != null) Fx.Flash(P(e.P) + Vector3.up * 1.4f, new Color(1f, 0.8f, 0.4f, 0.9f), big ? 2.6f : 1.2f, 0.18f);
                        if (fromMe || toMe) Sfx.Play("hit", 0.35f);
                        if (toMe) _shake = Mathf.Max(_shake, 0.25f);
                        break;
                    }
                    case SimEvent.T.Skill:
                    {
                        UnitView v; if (!_views.TryGetValue(e.A, out v)) break;
                        v.Swing = 1f;
                        if (e.B == -1 && v.Unit.Hero == HeroId.Rama && v.Unit.Kind == UnitKind.Hero)
                        {
                            Fx.Bolt(P(e.P) + Vector3.up * 2.2f, P(e.Q) + Vector3.up * 1.3f, new Color(1f, 0.9f, 0.5f, 0.9f), 0.12f, 0.12f);
                            if (e.A == _w.Heroes[_me].Id) Sfx.Play("shoot", 0.3f);
                        }
                        else if (e.B >= 0)
                        {
                            Color c = v.Unit.Hero == HeroId.Rama ? new Color(1f, 0.85f, 0.4f, 0.9f) : new Color(1f, 0.3f, 0.4f, 0.9f);
                            Fx.Ring(P(e.P), c, e.B == 1 && v.Unit.Hero == HeroId.Thotsakan ? 8f : 5f, 0.4f);
                            if (v.Unit.Hero == HeroId.Rama && e.B == 0)
                                for (int k = -2; k <= 2; k++) Fx.Bolt(P(e.P) + Vector3.up * 2f, P(e.P) + Vector3.up * 1.4f + Quaternion.Euler(0, k * 7.5f, 0) * (new Vector3(e.Q.X - e.P.X, 0, e.Q.Z - e.P.Z).normalized * 9f), c, 0.14f, 0.2f);
                            Sfx.Play(e.B == 2 ? "boom" : "skill", 0.5f);
                            if (e.B == 2 && v.Unit.Hero == HeroId.Thotsakan) { Banner("ทศพักตร์ยี่สิบกร!", new Color(1f, 0.35f, 0.45f), 1.6f); _shake = 0.8f; }
                        }
                        break;
                    }
                    case SimEvent.T.Beam:
                    {
                        Vector3 dir = P(e.Q) - P(e.P);
                        if (e.B == 0)
                        {
                            Fx.Telegraph(P(e.P), dir, 60f, 1.7f, new Color(1f, 0.75f, 0.2f, 0.4f), 1.25f);
                            Sfx.Play("charge", 0.5f);
                            if (e.A != _w.Heroes[_me].Id) Banner("ระวัง! ศรพรหมาสตร์", new Color(1f, 0.6f, 0.2f), 1.5f);
                        }
                        else
                        {
                            Fx.Brahmastra(P(e.P), dir, 60f); _shake = 1f; Sfx.Play("boom", 0.8f);
                            Banner("ศรพรหมาสตร์!", new Color(1f, 0.85f, 0.35f), 1.6f);
                        }
                        break;
                    }
                    case SimEvent.T.TurretShot:
                        Fx.Bolt(P(e.P) + Vector3.up * 9f, P(e.Q) + Vector3.up * 1.5f, new Color(0.7f, 0.9f, 1f, 0.9f), 0.2f, 0.18f);
                        break;
                    case SimEvent.T.Death:
                    {
                        UnitView v; _views.TryGetValue(e.B, out v);
                        float size = v != null && v.Unit.IsStructure ? 10f : (v != null && v.Unit.Kind == UnitKind.Hero ? 5f : 2.2f);
                        Fx.Sparks(P(e.P) + Vector3.up, new Color(1f, 0.7f, 0.3f, 1f), v != null && v.Unit.IsMinion ? 3 : 10, size * 0.4f);
                        Fx.Ring(P(e.P), new Color(1f, 0.8f, 0.4f, 1f), size, 0.5f);
                        if (v != null && v.Unit.IsStructure) { Sfx.Play("tower", 0.9f); _shake = 1.2f; Banner(v.Unit.Kind == UnitKind.Core ? "แกนกลางแตก!" : "ป้อมแตก!", new Color(1f, 0.8f, 0.3f), 1.8f); }
                        if (v != null && v.Unit.Kind == UnitKind.Hero)
                        {
                            Feed((v.Unit.Team == Team.Ayodhya ? "พระราม" : "ทศกัณฐ์") + " พ่ายแพ้");
                            if (v.Unit.Id == _w.Heroes[_foe].Id) Banner("กำจัดศัตรู!", new Color(1f, 0.85f, 0.3f), 1.5f);
                        }
                        break;
                    }
                    case SimEvent.T.Level:
                        Fx.Ring(P(e.P), new Color(0.6f, 1f, 0.7f, 1f), 6f, 0.7f);
                        if (e.A == _w.Heroes[_me].Id) { Sfx.Play("level", 0.6f); Feed("เลเวล " + e.Amount); }
                        break;
                    case SimEvent.T.HeartBreak:
                        Fx.Sparks(P(e.P) + Vector3.up, new Color(1f, 0.3f, 0.6f, 1f), 14, 1.6f);
                        Banner("กล่องดวงใจแตก!", new Color(1f, 0.4f, 0.7f), 1.8f); _shake = 0.7f; Sfx.Play("boom", 0.6f);
                        break;
                    case SimEvent.T.Revive:
                        Fx.Ring(P(e.P), new Color(1f, 0.9f, 0.5f, 1f), 7f, 0.7f); break;
                }
            }
        }

        void Banner(string t, Color c, float secs) { _banner = t; _bannerC = c; _bannerT = secs; }
        void Feed(string s) { _feed.Add(s); _feedT.Add(4f); if (_feed.Count > 4) { _feed.RemoveAt(0); _feedT.RemoveAt(0); } }

        // ---------------------------------------------------------------- input
        Rect JoyArea() { return new Rect(0, 340, _vw * 0.42f, 740); }
        Vector2 AtkC() { return new Vector2(_vw - 170, 910); }
        Vector2[] SkillC() { return new[] { new Vector2(_vw - 380, 950), new Vector2(_vw - 320, 790), new Vector2(_vw - 140, 735) }; }
        float[] SkillR() { return new[] { 62f, 62f, 74f }; }

        Vector2 ToGui(Vector2 screen) { return new Vector2(screen.x / _scale, (Screen.height - screen.y) / _scale); }

        struct Pt { public int Id; public Vector2 P; public int Phase; }  // phase 0 began, 1 held, 2 ended

        List<Pt> Pointers()
        {
            var l = new List<Pt>();
            for (int i = 0; i < Input.touchCount; i++)
            {
                var t = Input.GetTouch(i);
                l.Add(new Pt { Id = t.fingerId, P = ToGui(t.position), Phase = t.phase == TouchPhase.Began ? 0 : (t.phase == TouchPhase.Ended || t.phase == TouchPhase.Canceled ? 2 : 1) });
            }
            if (Input.touchCount == 0)
            {
                if (Input.GetMouseButtonDown(0)) l.Add(new Pt { Id = -1, P = ToGui(Input.mousePosition), Phase = 0 });
                else if (Input.GetMouseButtonUp(0)) l.Add(new Pt { Id = -1, P = ToGui(Input.mousePosition), Phase = 2 });
                else if (Input.GetMouseButton(0)) l.Add(new Pt { Id = -1, P = ToGui(Input.mousePosition), Phase = 1 });
            }
            return l;
        }

        static bool InCircle(Vector2 p, Vector2 c, float r) { return (p - c).sqrMagnitude <= r * r; }

        int _atkFinger = int.MinValue;

        void ReadGameInput()
        {
            var ptrs = Pointers();
            var sc = SkillC(); var sr = SkillR();
            for (int i = 0; i < ptrs.Count; i++)
            {
                var p = ptrs[i];
                if (p.Phase == 0)
                {
                    bool used = false;
                    for (int s = 0; s < 3; s++) if (InCircle(p.P, sc[s], sr[s] + 14)) { _skillPressed[s] = true; used = true; }
                    if (!used && InCircle(p.P, AtkC(), 112)) { _attackHeld = true; _atkFinger = p.Id; used = true; }
                    if (!used && _joyFinger == int.MinValue && JoyArea().Contains(p.P)) { _joyFinger = p.Id; _joyOrigin = p.P; _joyVec = Vector2.zero; }
                }
                else if (p.Phase == 1 && p.Id == _joyFinger)
                {
                    Vector2 d = p.P - _joyOrigin; float m = d.magnitude;
                    if (m > 130f) { _joyOrigin += d.normalized * (m - 130f); d = p.P - _joyOrigin; }
                    _joyVec = d.magnitude < 14f ? Vector2.zero : d / 130f;
                }
                if (p.Phase == 2)
                {
                    if (p.Id == _joyFinger) { _joyFinger = int.MinValue; _joyVec = Vector2.zero; }
                    if (p.Id == _atkFinger) { _atkFinger = int.MinValue; _attackHeld = false; }
                }
            }
            // keyboard (Editor / PC): WASD or arrows move, Space attacks, Q E R skills
            Vector2 kv = new Vector2(Input.GetAxisRaw("Horizontal"), -Input.GetAxisRaw("Vertical"));
            if (_joyFinger == int.MinValue) _joyVec = kv.sqrMagnitude > 0 ? kv.normalized : Vector2.zero;
            _attackHeld = Input.GetKey(KeyCode.Space) || _atkFinger != int.MinValue;
            if (Input.GetKeyDown(KeyCode.Q)) _skillPressed[0] = true;
            if (Input.GetKeyDown(KeyCode.E)) _skillPressed[1] = true;
            if (Input.GetKeyDown(KeyCode.R)) _skillPressed[2] = true;
            if (Input.GetKeyDown(KeyCode.Escape)) { Cleanup(); Prepare(false); }
        }

        Command BuildPlayerCommand()
        {
            var me = _w.Heroes[_me]; var foe = _w.Heroes[_foe];
            if (!me.Alive) return default(Command);
            Vec2 dirMove = _joyVec.sqrMagnitude > 0.01f ? new Vec2((int)(_joyVec.x * 1000), (int)(_joyVec.y * 1000)) : Vec2.Zero;

            for (int s = 2; s >= 0; s--)
            {
                if (!_skillPressed[s] || me.SkillCd[s] > 0) continue;
                Unit near = NearestEnemy(me, 1700, true);
                Vec2 aim = near != null ? near.Pos : me.Pos + new Vec2(-World.Sign(me.Team) * 800, 0);
                if (s == 1 && me.Hero == HeroId.Rama && dirMove.SqrLength > 0) aim = me.Pos + dirMove.WithLength(500);
                _skillPressed[s] = false;
                return new Command { Kind = CmdKind.Skill, Slot = s, Point = aim };
            }
            if (dirMove.SqrLength > 0) return new Command { Kind = CmdKind.Move, Point = me.Pos + dirMove.WithLength(1200) };
            // standing still: attack the best target in range automatically, or the pressed button's target
            Unit t = NearestEnemy(me, me.AttackRange + (_attackHeld ? 350 : 60), true);
            if (t != null) return new Command { Kind = CmdKind.Attack, TargetId = t.Id };
            return default(Command);
        }

        Unit NearestEnemy(Unit me, int range, bool heroFirst)
        {
            Unit best = null; long bd = long.MaxValue;
            for (int i = 0; i < _w.Units.Count; i++)
            {
                var u = _w.Units[i];
                if (!u.Alive || u.Team == me.Team) continue;
                if (u.IsStructure && u.Invulnerable) continue;
                long d = (u.Pos - me.Pos).SqrLength; long r = range + u.Radius;
                if (d > r * r) continue;
                long score = d;
                if (heroFirst && u.Kind == UnitKind.Hero) score -= 90000000L;
                if (u.Kind == UnitKind.HeartBox) score -= 60000000L;
                if (score < bd) { bd = score; best = u; }
            }
            return best;
        }

        void ReadMenuInput()
        {
            var ptrs = Pointers();
            for (int i = 0; i < ptrs.Count; i++)
            {
                if (ptrs[i].Phase != 0) continue;
                var p = ptrs[i].P;
                if (_mode == Mode.Menu)
                {
                    float cx = _vw / 2f;
                    if (new Rect(cx - 400, 380, 380, 250).Contains(p)) _pick = HeroId.Rama;
                    if (new Rect(cx + 20, 380, 380, 250).Contains(p)) _pick = HeroId.Thotsakan;
                    for (int d = 0; d < 3; d++) if (new Rect(cx - 330 + d * 230, 665, 210, 76).Contains(p)) _difficulty = d;
                    if (new Rect(cx - 220, 780, 440, 110).Contains(p)) StartMatch();
                }
                else if (_mode == Mode.Over)
                {
                    if (new Rect(_vw / 2f - 240, 640, 220, 90).Contains(p)) StartMatch();
                    if (new Rect(_vw / 2f + 20, 640, 220, 90).Contains(p)) { Cleanup(); Prepare(false); }
                }
            }
            if (_mode == Mode.Menu && Input.GetKeyDown(KeyCode.Return)) StartMatch();
        }

        // ---------------------------------------------------------------- GUI
        void OnGUI()
        {
            if (Event.current.type != EventType.Repaint) return;
            GUI.matrix = Matrix4x4.Scale(new Vector3(_scale, _scale, 1f));
            if (_st == null) { _st = new GUIStyle(GUI.skin.label) { font = _font, alignment = TextAnchor.MiddleCenter, wordWrap = false, clipping = TextClipping.Overflow }; }
            if (_mode == Mode.Menu) { DrawMenu(); return; }
            if (_w == null) return;
            DrawBars();
            DrawFloats();
            DrawHud();
            if (_mode == Mode.Over) DrawOver();
        }

        void Fill(Rect r, Color c) { var old = GUI.color; GUI.color = c; GUI.DrawTexture(r, Texture2D.whiteTexture); GUI.color = old; }
        void Disc(Vector2 c, float r, Color col) { var old = GUI.color; GUI.color = col; GUI.DrawTexture(new Rect(c.x - r, c.y - r, r * 2, r * 2), Gfx.Disc); GUI.color = old; }
        void RingGui(Vector2 c, float r, Color col) { var old = GUI.color; GUI.color = col; GUI.DrawTexture(new Rect(c.x - r, c.y - r, r * 2, r * 2), Gfx.Ring); GUI.color = old; }

        void Text(Rect r, string s, int size, Color c, TextAnchor a = TextAnchor.MiddleCenter, bool outline = true)
        {
            _st.fontSize = size; _st.alignment = a;
            if (outline)
            {
                _st.normal.textColor = new Color(0.1f, 0.05f, 0.15f, 0.95f);
                float o = Mathf.Max(1.5f, size * 0.06f);
                GUI.Label(new Rect(r.x - o, r.y, r.width, r.height), s, _st); GUI.Label(new Rect(r.x + o, r.y, r.width, r.height), s, _st);
                GUI.Label(new Rect(r.x, r.y - o, r.width, r.height), s, _st); GUI.Label(new Rect(r.x, r.y + o, r.width, r.height), s, _st);
            }
            _st.normal.textColor = c; GUI.Label(r, s, _st);
        }

        Vector2 ScreenToGui(Vector3 world)
        {
            Vector3 sp = _cam.WorldToScreenPoint(world);
            if (sp.z < 0) return new Vector2(-9999, -9999);
            return new Vector2(sp.x / _scale, (Screen.height - sp.y) / _scale);
        }

        void DrawBars()
        {
            foreach (var kv in _views)
            {
                var v = kv.Value; var u = v.Unit;
                if (!u.Alive || u.Kind == UnitKind.HeartBox) continue;
                Vector2 p = ScreenToGui(v.transform.position + Vector3.up * v.BaseHeight);
                if (p.x < -100 || p.x > _vw + 100 || p.y < -100 || p.y > 1180) continue;
                bool mine = u.Team == _w.Heroes[_me].Team;
                Color hp = mine ? new Color(0.3f, 0.7f, 1f) : new Color(1f, 0.32f, 0.3f);
                if (u.Id == _w.Heroes[_me].Id) hp = new Color(0.45f, 1f, 0.4f);
                float w = u.Kind == UnitKind.Hero ? 150 : (u.IsStructure ? 190 : 62), h = u.Kind == UnitKind.Hero ? 16 : (u.IsStructure ? 16 : 8);
                Rect r = new Rect(p.x - w / 2, p.y - h, w, h);
                Fill(new Rect(r.x - 2, r.y - 2, r.width + 4, r.height + 4), new Color(0.1f, 0.05f, 0.15f, 0.95f));
                Fill(new Rect(r.x, r.y, r.width * Mathf.Clamp01(u.Hp / (float)u.MaxHp), r.height), hp);
                if (u.Kind == UnitKind.Hero)
                {
                    for (int t = 1; t < 10; t++) Fill(new Rect(r.x + r.width * t / 10f - 0.5f, r.y, 1f, r.height), new Color(0.1f, 0.05f, 0.15f, 0.8f));
                    Text(new Rect(p.x - 100, p.y - 48, 200, 30), "Lv" + u.Level + "  " + (u.Hero == HeroId.Rama ? "พระราม" : "ทศกัณฐ์"), 24, Color.white);
                }
                if (u.Invulnerable && u.IsStructure) Text(new Rect(p.x - 80, p.y - 40, 160, 24), "ป้องกัน", 18, new Color(0.8f, 0.8f, 0.9f, 0.8f));
            }
            var me = _w.Heroes[_me];
            if (!me.Alive) Text(new Rect(_vw / 2 - 300, 420, 600, 90), "ฟื้นใน " + Mathf.CeilToInt(me.RespawnTicks / (float)SimMath.TickHz) + " วินาที", 52, new Color(1f, 0.9f, 0.6f));
        }

        void DrawFloats()
        {
            for (int i = 0; i < _floats.Count; i++)
            {
                var f = _floats[i]; float k = f.T / 1.1f;
                Vector2 p = ScreenToGui(f.Pos + Vector3.up * (k * 2.4f));
                var c = f.C; c.a = 1f - k * k;
                Text(new Rect(p.x - 100, p.y - 30, 200, 60), f.Text, (int)(f.Size * (1.3f - 0.3f * Mathf.Min(1f, k * 6f))), c);
            }
        }

        void DrawHud()
        {
            var me = _w.Heroes[_me]; var foe = _w.Heroes[_foe];
            var panel = new Color(0.1f, 0.06f, 0.16f, 0.78f); var gold = new Color(0.95f, 0.75f, 0.3f);
            // top score
            float cx = _vw / 2f;
            Fill(new Rect(cx - 262, 14, 524, 62), gold); Fill(new Rect(cx - 259, 17, 518, 56), panel);
            Fill(new Rect(cx - 259, 17, 220, 56), new Color(0.15f, 0.4f, 0.75f, 0.9f)); Fill(new Rect(cx + 39, 17, 220, 56), new Color(0.65f, 0.12f, 0.2f, 0.9f));
            Text(new Rect(cx - 259, 17, 220, 56), "อโยธยา  " + _w.Heroes[0].Kills, 30, Color.white);
            Text(new Rect(cx + 39, 17, 220, 56), _w.Heroes[1].Kills + "  ลงกา", 30, Color.white);
            int sec = _w.Tick / SimMath.TickHz;
            Text(new Rect(cx - 40, 17, 80, 56), (sec / 60).ToString("00") + ":" + (sec % 60).ToString("00"), 28, new Color(1f, 0.92f, 0.65f));
            // my stats
            Fill(new Rect(_vw - 400, 14, 386, 56), gold); Fill(new Rect(_vw - 397, 17, 380, 50), panel);
            Disc(new Vector2(_vw - 370, 42), 14, gold);
            Text(new Rect(_vw - 350, 17, 150, 50), me.Gold.ToString("N0"), 28, new Color(1f, 0.85f, 0.4f), TextAnchor.MiddleLeft);
            Text(new Rect(_vw - 200, 17, 180, 50), me.Kills + " / " + me.Deaths + " / " + me.Assists, 28, Color.white);
            // xp / level
            float need = World.XpToNext(me.Level);
            Fill(new Rect(_vw - 400, 74, 386, 12), new Color(0.1f, 0.06f, 0.16f, 0.85f));
            Fill(new Rect(_vw - 400, 74, 386 * (me.Level >= World.MaxLevel ? 1f : Mathf.Clamp01(me.Xp / need)), 12), new Color(0.65f, 0.4f, 1f));
            Text(new Rect(_vw - 400, 88, 386, 34), "เลเวล " + me.Level, 24, Color.white, TextAnchor.MiddleRight);
            // minimap
            DrawMinimap();
            // feed
            for (int i = 0; i < _feed.Count; i++)
                Text(new Rect(_vw - 460, 130 + i * 38, 440, 36), _feed[i], 24, new Color(1f, 0.92f, 0.7f, Mathf.Clamp01(_feedT[i])), TextAnchor.MiddleRight);
            // banner
            if (_bannerT > 0)
            {
                float a = Mathf.Clamp01(_bannerT * 2f); float pop = 1f + Mathf.Clamp01(_bannerT - 1.2f) * 0.5f;
                var c = _bannerC; c.a = a;
                Text(new Rect(cx - 560, 150, 1120, 140), _banner, (int)(78 * pop), c);
            }
            DrawControls(me);
        }

        void DrawMinimap()
        {
            Rect r = new Rect(22, 22, 330, 130);
            Fill(new Rect(r.x - 3, r.y - 3, r.width + 6, r.height + 6), new Color(0.95f, 0.75f, 0.3f)); Fill(r, new Color(0.17f, 0.35f, 0.2f, 0.92f));
            Fill(new Rect(r.x, r.center.y - 14, r.width, 28), new Color(0.78f, 0.7f, 0.5f, 0.95f));
            Fill(new Rect(r.center.x - 8, r.y, 16, r.height), new Color(0.3f, 0.6f, 0.85f, 0.85f));
            System.Func<Vec2, Vector2> m = p => new Vector2(r.x + (p.X + World.LaneHalf) / (2f * World.LaneHalf) * r.width, r.center.y + p.Z / 2800f * 30f);
            for (int i = 0; i < _w.Units.Count; i++)
            {
                var u = _w.Units[i]; if (!u.Alive || u.Kind == UnitKind.HeartBox) continue;
                Color c = u.Team == Team.Ayodhya ? new Color(0.4f, 0.75f, 1f) : new Color(1f, 0.35f, 0.35f);
                Vector2 p = m(u.Pos);
                if (u.IsStructure) Fill(new Rect(p.x - 7, p.y - 7, 14, 14), c);
                else if (u.Kind == UnitKind.Hero) { Disc(p, 11, Color.white); Disc(p, 9, c); }
                else Disc(p, 3.2f, c);
            }
            // camera view box
            Vector2 cc = m(new Vec2((int)(_camPos.x * 100), 0));
            Fill(new Rect(cc.x - 28, r.y + 2, 56, 1.5f), new Color(1, 1, 1, 0.8f)); Fill(new Rect(cc.x - 28, r.yMax - 3.5f, 56, 1.5f), new Color(1, 1, 1, 0.8f));
        }

        void DrawControls(Unit me)
        {
            // joystick
            Vector2 baseC = _joyFinger == int.MinValue ? new Vector2(250, 900) : _joyOrigin;
            Disc(baseC, 130, new Color(1f, 1f, 1f, 0.09f)); RingGui(baseC, 130, new Color(1f, 0.9f, 0.6f, 0.45f));
            Disc(baseC + _joyVec * 90f, 52, new Color(0.95f, 0.75f, 0.3f, 0.95f)); Disc(baseC + _joyVec * 90f, 40, new Color(1f, 0.9f, 0.55f, 1f));
            // attack
            Vector2 a = AtkC();
            Disc(a, 100, new Color(0.1f, 0.06f, 0.16f, 0.9f)); Disc(a, 94, _attackHeld ? new Color(1f, 0.85f, 0.4f) : new Color(0.85f, 0.55f, 0.15f));
            Text(new Rect(a.x - 90, a.y - 30, 180, 60), "โจมตี", 38, Color.white);
            // skills
            var sc = SkillC(); var sr = SkillR();
            string[] keys = { "Q", "E", "R" };
            string[][] names = { new[] { "ศรกระจาย", "พระขรรค์" }, new[] { "ก้าวเทพ", "คำราม" }, new[] { "พรหมาสตร์", "ยี่สิบกร" } };
            for (int s = 0; s < 3; s++)
            {
                int cd = me.SkillCd[s]; int baseCd = Mathf.Max(1, HeroSkills.BaseCooldown(me.Hero, s, HeroSkills.Rank(me)));
                bool ready = cd == 0 && me.Alive;
                Color col = s == 2 ? new Color(1f, 0.82f, 0.28f) : (s == 0 ? new Color(0.3f, 0.65f, 0.95f) : new Color(0.3f, 0.78f, 0.5f));
                Disc(sc[s], sr[s] + 7, new Color(0.95f, 0.75f, 0.3f)); Disc(sc[s], sr[s] + 3, new Color(0.1f, 0.06f, 0.16f)); Disc(sc[s], sr[s], ready ? col : col * 0.45f);
                if (ready && s == 2) RingGui(sc[s], sr[s] + 16 + Mathf.Sin(Time.time * 6f) * 4f, new Color(1f, 0.85f, 0.4f, 0.8f));
                if (cd > 0)
                {
                    float frac = Mathf.Clamp01(cd / (float)baseCd);
                    GUI.BeginGroup(new Rect(sc[s].x - sr[s], sc[s].y - sr[s] + sr[s] * 2f * (1f - frac), sr[s] * 2f, sr[s] * 2f * frac));
                    Disc(new Vector2(sr[s], sr[s] - sr[s] * 2f * (1f - frac)), sr[s], new Color(0, 0, 0, 0.62f));
                    GUI.EndGroup();
                    Text(new Rect(sc[s].x - 50, sc[s].y - 24, 100, 48), Mathf.CeilToInt(cd / (float)SimMath.TickHz).ToString(), 38, Color.white);
                }
                else Text(new Rect(sc[s].x - 50, sc[s].y - 28, 100, 48), keys[s], 40, Color.white);
                Text(new Rect(sc[s].x - 90, sc[s].y + sr[s] + 2, 180, 28), names[s][me.Hero == HeroId.Rama ? 0 : 1], 20, new Color(1f, 0.95f, 0.8f));
            }
        }

        void DrawMenu()
        {
            float cx = _vw / 2f;
            Fill(new Rect(0, 0, _vw, 1080), new Color(0.05f, 0.03f, 0.1f, 0.55f));
            Text(new Rect(cx - 600, 60, 1200, 130), "ศึกลงกา", 120, new Color(1f, 0.85f, 0.35f));
            Text(new Rect(cx - 600, 190, 1200, 60), "Prontera รามเกียรติ์ · MOBA", 38, new Color(1f, 0.95f, 0.8f));
            Text(new Rect(cx - 600, 262, 1200, 50), "อโยธยา  ปะทะ  ลงกา", 34, new Color(0.9f, 0.9f, 1f));
            Text(new Rect(cx - 600, 320, 1200, 44), "เลือกฮีโร่ของคุณ", 28, new Color(1f, 0.92f, 0.7f));
            DrawCard(new Rect(cx - 400, 380, 380, 250), "พระราม", "นักแม่นธนู · ฝ่ายอโยธยา", "ศรพรหมาสตร์ ยิงทะลุทั้งเลน", _pick == HeroId.Rama, new Color(0.2f, 0.5f, 0.85f));
            DrawCard(new Rect(cx + 20, 380, 380, 250), "ทศกัณฐ์", "นักรบ · ฝ่ายลงกา", "กล่องดวงใจ ตายแล้วฟื้นได้", _pick == HeroId.Thotsakan, new Color(0.75f, 0.15f, 0.25f));
            string[] dn = { "ง่าย", "ปกติ", "ยาก" };
            for (int d = 0; d < 3; d++)
            {
                Rect r = new Rect(cx - 330 + d * 230, 665, 210, 76);
                Fill(new Rect(r.x - 3, r.y - 3, r.width + 6, r.height + 6), _difficulty == d ? new Color(1f, 0.85f, 0.4f) : new Color(0.4f, 0.35f, 0.5f));
                Fill(r, _difficulty == d ? new Color(0.5f, 0.35f, 0.08f) : new Color(0.14f, 0.09f, 0.22f));
                Text(r, "บอท" + dn[d], 32, Color.white);
            }
            Rect play = new Rect(cx - 220, 780, 440, 110);
            Fill(new Rect(play.x - 4, play.y - 4, play.width + 8, play.height + 8), new Color(0.2f, 0.1f, 0.02f));
            Fill(play, new Color(0.9f, 0.6f, 0.12f));
            Text(play, "เริ่มเล่น", 54, Color.white);
            Text(new Rect(cx - 600, 920, 1200, 40), "เล่นฟรี ไม่มีเก็บเงิน · ต้นแบบทดสอบ (Q E R สกิล · Space โจมตี · WASD เดิน)", 22, new Color(1f, 0.95f, 0.8f, 0.8f));
        }

        void DrawCard(Rect r, string name, string role, string desc, bool sel, Color col)
        {
            Fill(new Rect(r.x - 4, r.y - 4, r.width + 8, r.height + 8), sel ? new Color(1f, 0.85f, 0.4f) : new Color(0.4f, 0.35f, 0.5f));
            Fill(r, new Color(0.1f, 0.06f, 0.16f, 0.95f)); Fill(new Rect(r.x, r.y, r.width, 80), col);
            Text(new Rect(r.x, r.y, r.width, 80), name, 52, Color.white);
            Text(new Rect(r.x, r.y + 100, r.width, 40), role, 26, new Color(1f, 0.92f, 0.7f));
            Text(new Rect(r.x, r.y + 150, r.width, 40), desc, 24, Color.white);
            if (sel) Text(new Rect(r.x, r.y + 200, r.width, 36), "เลือกแล้ว", 24, new Color(0.5f, 1f, 0.5f));
        }

        void DrawOver()
        {
            float cx = _vw / 2f;
            Fill(new Rect(0, 0, _vw, 1080), new Color(0, 0, 0, 0.5f));
            Text(new Rect(cx - 500, 300, 1000, 180), _blueWon ? "ชัยชนะ!" : "พ่ายแพ้", 150, _blueWon ? new Color(1f, 0.85f, 0.3f) : new Color(1f, 0.4f, 0.4f));
            var me = _w.Heroes[_me];
            Text(new Rect(cx - 500, 490, 1000, 60), "เวลา " + (_w.Tick / SimMath.TickHz / 60) + " นาที · สังหาร " + me.Kills + " · เลเวล " + me.Level, 34, Color.white);
            Fill(new Rect(cx - 240, 640, 220, 90), new Color(0.9f, 0.6f, 0.12f)); Text(new Rect(cx - 240, 640, 220, 90), "เล่นอีกครั้ง", 34, Color.white);
            Fill(new Rect(cx + 20, 640, 220, 90), new Color(0.35f, 0.3f, 0.5f)); Text(new Rect(cx + 20, 640, 220, 90), "เมนู", 34, Color.white);
        }

    }
}
