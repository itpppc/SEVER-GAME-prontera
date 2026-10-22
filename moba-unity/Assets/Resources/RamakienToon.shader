// Built-in render pipeline. Flat 3-band toon shading with a fixed key light, rim light and an inverted-hull ink outline.
// No scene lights are needed, so it renders the same in the Editor, in builds and on phones.
Shader "Ramakien/Toon"
{
    Properties
    {
        _Color ("Color", Color) = (1,1,1,1)
        _Emission ("Emission", Color) = (0,0,0,0)
        _Ink ("Outline Color", Color) = (0.10,0.06,0.13,1)
        _OutlineWidth ("Outline Width", Float) = 0.035
        _Tint ("Light Tint", Color) = (1,0.93,0.82,1)
        _Shadow ("Shadow Color", Color) = (0.36,0.40,0.62,1)
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" "Queue"="Geometry" }

        Pass
        {
            Name "OUTLINE"
            Cull Front
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            fixed4 _Ink; float _OutlineWidth;
            struct appdata { float4 vertex : POSITION; float3 normal : NORMAL; };
            struct v2f { float4 pos : SV_POSITION; };
            v2f vert (appdata v)
            {
                v2f o;
                float3 n = normalize(v.normal);
                // width is in object space; objects are scaled uniformly so it stays proportional
                o.pos = UnityObjectToClipPos(float4(v.vertex.xyz + n * _OutlineWidth, 1.0));
                return o;
            }
            fixed4 frag (v2f i) : SV_Target { return _Ink; }
            ENDCG
        }

        Pass
        {
            Name "BASE"
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            fixed4 _Color; fixed4 _Emission; fixed4 _Tint; fixed4 _Shadow;
            struct appdata { float4 vertex : POSITION; float3 normal : NORMAL; };
            struct v2f { float4 pos : SV_POSITION; float3 nrm : TEXCOORD0; float3 wpos : TEXCOORD1; };
            v2f vert (appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.nrm = UnityObjectToWorldNormal(v.normal);
                o.wpos = mul(unity_ObjectToWorld, v.vertex).xyz;
                return o;
            }
            fixed4 frag (v2f i) : SV_Target
            {
                float3 n = normalize(i.nrm);
                float3 L = normalize(float3(-0.45, 0.80, 0.40));
                float d = dot(n, L) * 0.5 + 0.5;
                float band = d > 0.62 ? 1.0 : (d > 0.36 ? 0.72 : 0.46);
                fixed3 lit = lerp(_Shadow.rgb, _Tint.rgb, saturate((band - 0.46) / 0.54));
                float3 V = normalize(_WorldSpaceCameraPos - i.wpos);
                float rim = pow(1.0 - saturate(dot(n, V)), 3.0);
                fixed3 col = _Color.rgb * lit + rim * 0.22 * _Tint.rgb + _Emission.rgb;
                return fixed4(col, 1.0);
            }
            ENDCG
        }
    }
    Fallback "Diffuse"
}
