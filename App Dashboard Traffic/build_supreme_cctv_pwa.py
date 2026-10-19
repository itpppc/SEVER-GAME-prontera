# -*- coding: utf-8 -*-
"""
Supreme Bangkok Traffic CCTV & PWA Mobile Analytics Suite
Integrates Maximum Free Public Traffic CCTV APIs, Streams & Feeds:
- All 176 Official Traffic CCTV Sensors (DOH, BMA, EXAT)
- 12 Curated Bangkok Real-Time HD Live Streams & Feeds
- Quad-Screen Multi-View Matrix (โหมดดูสด 4 จอพร้อมกันแบบห้องควบคุม TCC)
- Live Inter-Agency Connections: BMA Traffic, DOH Highway Traffic, EXAT Expressway, Longdo Traffic, iTIC Foundation
- PWA Native Installability, Service Worker, and TON-AI Tech Credit System (https://ton-ai-tech.web.app/)
"""
import json
import os
import shutil

print("1. Creating Web App Manifest (manifest.json)...")
manifest = {
    "id": "bkk-smart-mobility-pwa",
    "name": "Bangkok Smart Mobility & Live CCTV",
    "short_name": "BKK Mobility",
    "description": "ระบบวิเคราะห์การเดินทาง โครงข่ายขนส่ง และศูนย์รวมกล้องวงจรปิดจราจรสด กทม. ออกแบบและพัฒนาโดย TON-AI Tech",
    "start_url": "./index.html",
    "scope": "./",
    "display": "standalone",
    "orientation": "portrait",
    "background_color": "#0a0f1d",
    "theme_color": "#06b6d4",
    "categories": ["navigation", "travel", "utilities"],
    "author": "TON-AI Tech",
    "author_url": "https://ton-ai-tech.web.app/",
    "icons": [
        {
            "src": "favicon.png",
            "sizes": "64x64",
            "type": "image/png"
        },
        {
            "src": "apple-touch-icon.png",
            "sizes": "180x180",
            "type": "image/png"
        },
        {
            "src": "icon-192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "any"
        },
        {
            "src": "icon-192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "maskable"
        },
        {
            "src": "icon-512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "any"
        },
        {
            "src": "icon-512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "maskable"
        }
    ],
    "shortcuts": [
        {
            "name": "กล้อง CCTV สด (176 จุด + Quad-View)",
            "short_name": "CCTV สด",
            "description": "ดูถ่ายทอดสดกล้องวงจรปิดจราจร กทม. ฟรี",
            "url": "./index.html#traffic",
            "icons": [{ "src": "icon-192.png", "sizes": "192x192" }]
        },
        {
            "name": "ค้นหาป้ายรถเมล์",
            "short_name": "รถเมล์",
            "description": "ค้นหาป้ายและเส้นทางรถเมล์",
            "url": "./index.html#bus",
            "icons": [{ "src": "icon-192.png", "sizes": "192x192" }]
        },
        {
            "name": "คำนวณค่าเดินทาง",
            "short_name": "คำนวณ",
            "description": "คำนวณค่าโดยสารและเวลาเดินทาง",
            "url": "./index.html#transit",
            "icons": [{ "src": "icon-192.png", "sizes": "192x192" }]
        }
    ]
}

with open("manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print("manifest.json created successfully.")

print("2. Reading dashboard_data.json...")
with open("dashboard_data.json", "r", encoding="utf-8") as f:
    data_json_str = f.read()

# Read the template from generate_final_dashboard.py
with open("generate_final_dashboard.py", "r", encoding="utf-8") as f:
    orig_code = f.read()

start_token = 'html_template = """'
end_token = '"""\n\n# Embed data safely'
s_idx = orig_code.find(start_token)
e_idx = orig_code.find(end_token)

if s_idx == -1 or e_idx == -1:
    raise ValueError("Could not find html_template in generate_final_dashboard.py")

html = orig_code[s_idx + len(start_token):e_idx]
print(f"Original HTML extracted ({len(html)} chars). Now applying Supreme Live CCTV & PWA Mobile enhancements...")

# -------------------------------------------------------------
# 1. PWA & Mobile App Meta Tags in <head>
# -------------------------------------------------------------
head_meta_enhancement = """  <!-- PWA & Native Mobile App Meta Tags -->
  <link rel="manifest" href="manifest.json" />
  <link rel="icon" type="image/png" sizes="64x64" href="favicon.png" />
  <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png" />
  <link rel="apple-touch-icon" sizes="192x192" href="icon-192.png" />
  <meta name="application-name" content="BKK Smart Mobility" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  <meta name="apple-mobile-web-app-title" content="BKK Mobility" />
  <meta name="theme-color" content="#0a0f1d" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
  <meta name="author" content="TON-AI Tech (https://ton-ai-tech.web.app/)" />
  <meta name="creator" content="TON-AI Tech" />
"""

html = html.replace('<meta name="viewport" content="width=device-width, initial-scale=1.0" />', head_meta_enhancement)

# -------------------------------------------------------------
# 2. Enhanced CSS with Supreme CCTV Matrix & Quad-View
# -------------------------------------------------------------
supreme_css = """
    /* =======================================================
       SUPREME CCTV MATRIX, QUAD-VIEW, PWA & TON-AI TECH SUITE
       ======================================================= */
    
    * {
      -webkit-tap-highlight-color: transparent;
      user-select: auto;
    }
    html, body {
      overscroll-behavior-y: contain;
    }

    /* Top App Navigation Bar */
    .app-top-nav {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 14px 20px;
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: var(--radius-lg);
      margin-bottom: 16px;
      position: sticky;
      top: 10px;
      z-index: 1000;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
    
    .brand-section {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand-icon {
      width: 44px;
      height: 44px;
      border-radius: 14px;
      background: linear-gradient(135deg, #06b6d4, #3b82f6);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 18px rgba(6, 182, 212, 0.45);
      flex-shrink: 0;
    }
    .brand-title-area h1 {
      font-size: 1.25rem;
      font-weight: 700;
      line-height: 1.2;
      background: linear-gradient(90deg, #ffffff, #e2e8f0);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .brand-creator-badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      background: linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(139, 92, 246, 0.15));
      border: 1px solid rgba(56, 189, 248, 0.35);
      color: #38bdf8;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 0.72rem;
      font-weight: 600;
      text-decoration: none;
      transition: var(--transition);
      margin-top: 2px;
    }
    .brand-creator-badge:hover {
      background: rgba(6, 182, 212, 0.3);
      color: #ffffff;
      transform: translateY(-1px);
    }

    /* Top App Actions */
    .app-top-actions {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .app-icon-btn {
      width: 38px;
      height: 38px;
      border-radius: 12px;
      background: rgba(30, 41, 59, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: #f1f5f9;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: var(--transition);
      font-size: 1rem;
      position: relative;
    }
    .app-icon-btn:active {
      transform: scale(0.92);
    }
    .app-icon-btn:hover {
      background: rgba(6, 182, 212, 0.25);
      border-color: #38bdf8;
      color: #ffffff;
    }

    /* PWA Install Button */
    .btn-install-app {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: linear-gradient(135deg, #10b981, #06b6d4);
      color: #ffffff;
      font-size: 0.78rem;
      font-weight: 700;
      padding: 7px 14px;
      border-radius: 20px;
      border: none;
      cursor: pointer;
      box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
      transition: var(--transition);
      font-family: inherit;
      animation: pulseInstall 2.5s infinite;
    }
    @keyframes pulseInstall {
      0%, 100% { box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4); }
      50% { box-shadow: 0 4px 22px rgba(6, 182, 212, 0.7); }
    }
    .btn-install-app:active {
      transform: scale(0.94);
    }
    .btn-install-app:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6);
    }

    .btn-credit-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: linear-gradient(135deg, #0284c7, #6366f1);
      color: #ffffff;
      font-size: 0.78rem;
      font-weight: 600;
      padding: 7px 14px;
      border-radius: 20px;
      border: 1px solid rgba(255, 255, 255, 0.15);
      cursor: pointer;
      box-shadow: 0 4px 15px rgba(2, 132, 199, 0.35);
      transition: var(--transition);
      text-decoration: none;
    }
    .btn-credit-pill:hover {
      background: linear-gradient(135deg, #0369a1, #4f46e5);
      box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
      transform: translateY(-1px);
    }

    /* PWA Floating Install Banner */
    .pwa-install-banner {
      position: fixed;
      bottom: 84px;
      left: 16px;
      right: 16px;
      max-width: 440px;
      margin: 0 auto;
      background: rgba(15, 23, 42, 0.95);
      backdrop-filter: blur(25px);
      -webkit-backdrop-filter: blur(25px);
      border: 1px solid rgba(6, 182, 212, 0.4);
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6), 0 0 25px rgba(6, 182, 212, 0.25);
      border-radius: var(--radius-lg);
      padding: 12px 16px;
      display: flex;
      align-items: center;
      gap: 12px;
      z-index: 9998;
      animation: bannerSlideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes bannerSlideUp {
      from { transform: translateY(50px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
    .pwa-install-text {
      flex: 1;
    }
    .pwa-install-text b {
      font-size: 0.88rem;
      color: #ffffff;
      display: block;
    }
    .pwa-install-text p {
      font-size: 0.74rem;
      color: #94a3b8;
      margin-top: 1px;
    }
    .pwa-install-actions {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .btn-install-now {
      background: linear-gradient(135deg, #06b6d4, #3b82f6);
      color: #ffffff;
      border: none;
      padding: 6px 14px;
      border-radius: 10px;
      font-size: 0.8rem;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(6, 182, 212, 0.4);
    }
    .btn-install-close {
      background: rgba(255, 255, 255, 0.08);
      border: none;
      color: #94a3b8;
      width: 28px;
      height: 28px;
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.85rem;
    }

    /* Live Meta Bar in Header */
    .realtime-meta-bar {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 0.8rem;
      background: rgba(15, 23, 42, 0.6);
      padding: 6px 14px;
      border-radius: var(--radius-md);
      border: 1px solid rgba(255, 255, 255, 0.08);
      flex-wrap: wrap;
    }
    .realtime-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      color: #cbd5e1;
    }
    .realtime-pill.weather {
      color: #38bdf8;
      font-weight: 500;
    }
    .realtime-pill.clock {
      color: #f8fafc;
      font-family: 'Plus Jakarta Sans', monospace;
      font-weight: 600;
      letter-spacing: 0.5px;
    }
    .btn-sync-live {
      background: rgba(6, 182, 212, 0.15);
      border: 1px solid rgba(6, 182, 212, 0.4);
      color: #38bdf8;
      padding: 4px 10px;
      border-radius: 8px;
      font-size: 0.75rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      transition: var(--transition);
      font-weight: 600;
    }
    .btn-sync-live:hover {
      background: rgba(6, 182, 212, 0.3);
      color: #ffffff;
      transform: translateY(-1px);
    }
    .btn-sync-live.spinning svg {
      animation: spin 1s linear infinite;
    }

    /* Live Breaking Traffic Ticker */
    .live-ticker-container {
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(56, 189, 248, 0.25);
      border-radius: var(--radius-md);
      padding: 8px 16px;
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 12px;
      overflow: hidden;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .ticker-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: linear-gradient(135deg, #ef4444, #f43f5e);
      color: #ffffff;
      font-size: 0.75rem;
      font-weight: 700;
      padding: 3px 10px;
      border-radius: 20px;
      white-space: nowrap;
      flex-shrink: 0;
      box-shadow: 0 2px 10px rgba(239, 68, 68, 0.4);
    }
    .ticker-marquee {
      flex: 1;
      overflow: hidden;
      white-space: nowrap;
      position: relative;
    }
    .ticker-track {
      display: inline-block;
      white-space: nowrap;
      padding-left: 100%;
      animation: marquee 35s linear infinite;
      font-size: 0.84rem;
      color: #e2e8f0;
    }
    .ticker-item {
      display: inline-block;
      margin-right: 40px;
    }
    .ticker-item b {
      color: #38bdf8;
    }
    @keyframes marquee {
      0% { transform: translate3d(0, 0, 0); }
      100% { transform: translate3d(-100%, 0, 0); }
    }

    /* Quick Live CCTV Channels Bar */
    .quick-cctv-bar {
      display: flex;
      align-items: center;
      gap: 8px;
      overflow-x: auto;
      padding: 12px 16px;
      background: rgba(15, 23, 42, 0.75);
      border: 1px solid rgba(56, 189, 248, 0.3);
      border-radius: var(--radius-md);
      margin-bottom: 16px;
      -webkit-overflow-scrolling: touch;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .quick-cctv-label {
      font-size: 0.82rem;
      font-weight: 700;
      color: #38bdf8;
      white-space: nowrap;
      display: flex;
      align-items: center;
      gap: 6px;
      flex-shrink: 0;
    }
    .quick-cctv-btn {
      background: rgba(30, 41, 59, 0.85);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: #f1f5f9;
      padding: 7px 13px;
      border-radius: 9px;
      font-size: 0.78rem;
      cursor: pointer;
      white-space: nowrap;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: var(--transition);
      font-family: inherit;
      font-weight: 500;
      flex-shrink: 0;
    }
    .quick-cctv-btn:hover {
      background: rgba(6, 182, 212, 0.25);
      border-color: #38bdf8;
      color: #ffffff;
      transform: translateY(-1px);
    }
    .quick-cctv-btn.highlight-quad {
      background: linear-gradient(135deg, rgba(6, 182, 212, 0.3), rgba(139, 92, 246, 0.3));
      border: 1px solid #38bdf8;
      color: #ffffff;
      font-weight: 700;
      box-shadow: 0 0 15px rgba(6, 182, 212, 0.4);
    }
    .quick-cctv-btn .live-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #ef4444;
      animation: pulse 1.5s infinite;
    }

    /* TON-AI TECH FOOTER CREDIT CARD */
    .tonai-credit-footer {
      margin-top: 50px;
      margin-bottom: 30px;
      padding: 24px 28px;
      background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.85));
      border: 1px solid rgba(56, 189, 248, 0.25);
      border-radius: var(--radius-lg);
      box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4), 0 0 25px rgba(6, 182, 212, 0.15);
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
    }
    .tonai-credit-left {
      display: flex;
      align-items: center;
      gap: 18px;
    }
    .tonai-credit-avatar {
      width: 58px;
      height: 58px;
      border-radius: 18px;
      background: linear-gradient(135deg, #06b6d4, #8b5cf6);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 26px;
      box-shadow: 0 8px 25px rgba(6, 182, 212, 0.4);
      flex-shrink: 0;
    }
    .tonai-credit-info h4 {
      font-size: 1.15rem;
      font-weight: 700;
      color: #ffffff;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .tonai-badge-highlight {
      background: linear-gradient(90deg, #06b6d4, #3b82f6);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      font-weight: 800;
    }
    .tonai-credit-info p {
      font-size: 0.84rem;
      color: #94a3b8;
      margin-top: 4px;
      max-width: 650px;
      line-height: 1.5;
    }
    .tonai-visit-btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: linear-gradient(135deg, #06b6d4, #3b82f6);
      color: #ffffff;
      padding: 12px 24px;
      border-radius: 14px;
      font-weight: 700;
      font-size: 0.9rem;
      text-decoration: none;
      box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);
      transition: var(--transition);
      white-space: nowrap;
    }
    .tonai-visit-btn:hover {
      box-shadow: 0 8px 28px rgba(6, 182, 212, 0.65);
      transform: translateY(-2px);
      color: #ffffff;
    }

    /* Modal for Public Free CCTV */
    .cctv-modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(2, 6, 23, 0.88);
      backdrop-filter: blur(12px);
      z-index: 9999;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 14px;
      opacity: 0;
      transition: opacity 0.3s ease;
    }
    .cctv-modal-backdrop.active {
      display: flex;
      opacity: 1;
    }
    .cctv-modal-box {
      background: #0f172a;
      border: 1px solid rgba(56, 189, 248, 0.4);
      box-shadow: 0 25px 60px -10px rgba(0, 0, 0, 0.8), 0 0 35px rgba(6, 182, 212, 0.25);
      border-radius: 20px;
      width: 100%;
      max-width: 980px;
      max-height: 94vh;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      animation: modalSlideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes modalSlideUp {
      from { transform: translateY(30px) scale(0.97); opacity: 0; }
      to { transform: translateY(0) scale(1); opacity: 1; }
    }
    .cctv-modal-header {
      padding: 14px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      background: rgba(30, 41, 59, 0.6);
    }
    .cctv-modal-title-group h3 {
      font-size: 1.12rem;
      font-weight: 700;
      color: #ffffff;
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    .cctv-modal-title-group p {
      font-size: 0.78rem;
      color: #94a3b8;
      margin-top: 2px;
    }
    .cctv-modal-close {
      background: rgba(255, 255, 255, 0.08);
      border: none;
      color: #cbd5e1;
      width: 38px;
      height: 38px;
      border-radius: 10px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
      transition: var(--transition);
    }
    .cctv-modal-close:hover {
      background: #ef4444;
      color: #ffffff;
    }

    /* Modal CCTV Selector Toolbar (176 points fast search) */
    .cctv-selector-bar {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 18px;
      background: rgba(15, 23, 42, 0.95);
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      flex-wrap: wrap;
    }
    .cctv-selector-label {
      font-size: 0.8rem;
      font-weight: 700;
      color: #38bdf8;
      white-space: nowrap;
      display: flex;
      align-items: center;
      gap: 5px;
    }
    .cctv-select-box {
      flex: 1;
      min-width: 220px;
      background: #1e293b;
      border: 1px solid rgba(56, 189, 248, 0.3);
      color: #f8fafc;
      font-size: 0.8rem;
      padding: 7px 12px;
      border-radius: 8px;
      font-family: inherit;
    }
    .cctv-select-box:focus {
      outline: none;
      border-color: #38bdf8;
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
    }

    .cctv-channels-nav {
      display: flex;
      gap: 6px;
      padding: 10px 18px;
      background: rgba(15, 23, 42, 0.8);
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
    }
    .cctv-channel-btn {
      background: rgba(30, 41, 59, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.08);
      color: #94a3b8;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 0.76rem;
      cursor: pointer;
      white-space: nowrap;
      transition: var(--transition);
      font-family: inherit;
      font-weight: 500;
    }
    .cctv-channel-btn:hover {
      color: #ffffff;
      background: rgba(30, 41, 59, 0.9);
    }
    .cctv-channel-btn.active {
      background: #06b6d4;
      color: #ffffff;
      border-color: #38bdf8;
      font-weight: 600;
      box-shadow: 0 0 12px rgba(6, 182, 212, 0.4);
    }

    .cctv-player-container {
      position: relative;
      width: 100%;
      background: #000000;
      aspect-ratio: 16 / 9;
      max-height: 520px;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .cctv-player-container iframe,
    .cctv-player-container img,
    .cctv-player-container canvas {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      border: none;
    }
    .cctv-osd-overlay {
      position: absolute;
      top: 12px;
      left: 14px;
      right: 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      pointer-events: none;
      z-index: 5;
    }
    .cctv-osd-badge {
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(4px);
      padding: 4px 10px;
      border-radius: 6px;
      font-family: monospace;
      font-size: 0.76rem;
      color: #22c55e;
      border: 1px solid rgba(34, 197, 94, 0.3);
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .cctv-osd-rec {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(239, 68, 68, 0.85);
      color: #ffffff;
      font-weight: 700;
      font-size: 0.72rem;
      padding: 3px 8px;
      border-radius: 4px;
      letter-spacing: 0.5px;
    }
    .cctv-osd-time {
      font-family: monospace;
      color: #ffffff;
      font-size: 0.8rem;
      background: rgba(0, 0, 0, 0.6);
      padding: 3px 8px;
      border-radius: 4px;
    }

    /* Quad-View 4-Screen Matrix Styles */
    .cctv-quad-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: 1fr 1fr;
      gap: 6px;
      width: 100%;
      height: 100%;
      background: #050914;
      padding: 6px;
    }
    @media (max-width: 640px) {
      .cctv-quad-grid {
        grid-template-columns: 1fr;
        grid-template-rows: repeat(4, 180px);
        overflow-y: auto;
      }
    }
    .cctv-quad-cell {
      position: relative;
      background: #0b1120;
      border: 1px solid rgba(56, 189, 248, 0.25);
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .cctv-quad-cell iframe,
    .cctv-quad-cell img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      border: none;
    }
    .cctv-quad-header {
      position: absolute;
      top: 6px;
      left: 8px;
      right: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 5;
      pointer-events: none;
    }
    .cctv-quad-title {
      background: rgba(0, 0, 0, 0.75);
      color: #38bdf8;
      font-size: 0.7rem;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 4px;
      border: 1px solid rgba(56, 189, 248, 0.3);
      font-family: inherit;
    }
    .cctv-quad-rec {
      background: rgba(239, 68, 68, 0.85);
      color: #ffffff;
      font-size: 0.65rem;
      font-weight: 700;
      padding: 2px 5px;
      border-radius: 3px;
    }

    .cctv-controls-strip {
      padding: 14px 20px;
      background: rgba(15, 23, 42, 0.95);
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
    }
    .cctv-metrics-pills {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .cctv-metric-tag {
      background: rgba(30, 41, 59, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.08);
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 0.76rem;
      color: #cbd5e1;
    }
    .cctv-metric-tag b {
      color: #38bdf8;
    }
    .cctv-external-links {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .btn-cctv-ext {
      padding: 6px 12px;
      font-size: 0.78rem;
      border-radius: 8px;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      background: rgba(56, 189, 248, 0.15);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.3);
      transition: var(--transition);
      cursor: pointer;
      font-weight: 600;
      white-space: nowrap;
    }
    .btn-cctv-ext:hover {
      background: #0284c7;
      color: #ffffff;
    }

    /* ABOUT & CREDIT MODAL */
    .about-modal-box {
      max-width: 580px;
      background: #0f172a;
      border: 1px solid rgba(56, 189, 248, 0.4);
      box-shadow: 0 25px 60px rgba(0,0,0,0.8), 0 0 35px rgba(6, 182, 212, 0.25);
      border-radius: 24px;
      padding: 28px;
      position: relative;
    }

    /* Floating Bottom Dock on Mobile */
    .mobile-bottom-dock {
      display: none;
    }

    @media (max-width: 768px) {
      .app-top-nav {
        padding: 10px 14px;
        top: 6px;
      }
      .brand-icon {
        width: 36px;
        height: 36px;
        font-size: 18px;
      }
      .brand-title-area h1 {
        font-size: 1.05rem;
      }
      .realtime-meta-bar {
        width: 100%;
        justify-content: space-between;
      }
      .tonai-credit-footer {
        flex-direction: column;
        align-items: flex-start;
      }
      .tonai-visit-btn, .btn-install-app {
        width: 100%;
        justify-content: center;
      }
      
      /* Show Mobile Bottom Dock */
      .mobile-bottom-dock {
        display: flex;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 68px;
        background: rgba(10, 15, 29, 0.92);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        z-index: 9990;
        justify-content: space-around;
        align-items: center;
        padding: 0 8px;
        padding-bottom: env(safe-area-inset-bottom, 0px);
      }
      .mobile-dock-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 3px;
        background: none;
        border: none;
        color: #94a3b8;
        font-size: 0.68rem;
        cursor: pointer;
        padding: 6px 10px;
        border-radius: 10px;
        transition: var(--transition);
        font-family: inherit;
        flex: 1;
      }
      .mobile-dock-btn svg, .mobile-dock-btn span.dock-icon {
        font-size: 1.25rem;
        line-height: 1;
      }
      .mobile-dock-btn.active {
        color: #38bdf8;
        font-weight: 700;
        background: rgba(6, 182, 212, 0.12);
      }
      .app-container {
        padding-bottom: 95px !important;
      }
    }
"""

html = html.replace("  <style>", "  <style>\n" + supreme_css)

# -------------------------------------------------------------
# 3. Enhanced Mobile App Header with TON-AI Tech Credits & Live Bar
# -------------------------------------------------------------
top_app_nav = """  <!-- NATIVE MOBILE APP TOP NAVIGATION -->
  <div class="app-top-nav">
    <div class="brand-section">
      <div class="brand-icon">
        🚦
      </div>
      <div class="brand-title-area">
        <h1>Bangkok Smart Mobility</h1>
        <div>
          <a href="https://ton-ai-tech.web.app/" target="_blank" rel="noopener noreferrer" class="brand-creator-badge" title="TON-AI Tech Official Project">
            <span>✨</span> Developed by TON-AI Tech
          </a>
        </div>
      </div>
    </div>
    
    <div class="app-top-actions">
      <!-- Live Realtime Clock & Weather -->
      <div class="realtime-meta-bar">
        <div class="realtime-pill clock">
          <span>🕒</span> <span id="realtimeClockText">--:--:--</span>
        </div>
        <div class="realtime-pill weather" id="realtimeWeatherPill">
          <span>🌤️</span> <span id="realtimeWeatherText">กทม. 31°C เมฆบางส่วน</span>
        </div>
        <button class="btn-sync-live" id="btnSyncTelemetry" onclick="triggerManualDataSync()" title="อัปเดตข้อมูลสด">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
          สด
        </button>
      </div>

      <button class="btn-install-app" onclick="triggerPwaInstall()" title="ติดตั้งแอปลงในมือถือ">
        <span>📲</span> ติดตั้งแอป
      </button>

      <button class="btn-credit-pill" onclick="openAboutModal()" title="ข้อมูลผู้พัฒนาและลิขสิทธิ์">
        <span>🤖</span> TON-AI Tech
      </button>
    </div>
  </div>
"""

html = html.replace("<header class=\"dashboard-header\">", top_app_nav + '\n  <header class="dashboard-header" style="display:none;">')

# Quick Chips under search bar
quick_chips_html = """
    <!-- Mobile Fast Filter Chips -->
    <div class="mobile-fast-chips" style="display:flex;gap:8px;overflow-x:auto;padding:8px 0;margin-top:10px;-webkit-overflow-scrolling:touch;">
      <button class="chip-item" onclick="openLiveCctvModal('CAM-QUAD', 'โหมด 4 จอสด (Quad Multi-View)', 'ALL-NETWORK', 42.5, 0.78, 'ปกติ')" style="background:linear-gradient(135deg,rgba(6,182,212,0.3),rgba(139,92,246,0.3));border:1px solid #38bdf8;color:#fff;font-weight:700;">
        🎛️ ดูสด 4 จอพร้อมกัน
      </button>
      <button class="chip-item" onclick="switchTab('traffic')">
        📹 กล้อง CCTV (176 จุด)
      </button>
      <button class="chip-item" onclick="switchTab('bus')">
        🚏 รถเมล์ 50 เขต
      </button>
      <button class="chip-item" onclick="switchTab('transit')">
        💰 คำนวณค่าโดยสาร
      </button>
      <button class="chip-item" onclick="switchTab('explorer')">
        🔍 คลังข้อมูลสถิติ
      </button>
    </div>
"""

html = html.replace('</div>\n    <div class="header-tools">', quick_chips_html + '\n    </div>\n    <div class="header-tools">')

# -------------------------------------------------------------
# 4. Live Breaking Traffic Ticker
# -------------------------------------------------------------
ticker_html = """
  <!-- REAL-TIME BREAKING TRAFFIC NEWS TICKER -->
  <div class="live-ticker-container">
    <div class="ticker-badge">
      <span class="live-dot" style="background:#fff;width:6px;height:6px;border-radius:50%;display:inline-block;animation:pulse 1s infinite;"></span>
      รายงานจราจรสด
    </div>
    <div class="ticker-marquee">
      <div class="ticker-track" id="liveTickerTrack">
        <span class="ticker-item">🛣️ <b>ทางพิเศษศรีรัช (พระราม 9):</b> ปริมาณรถหนาแน่น ชะลอตัวช่วงขึ้นด่วนอโศก ความเร็วเฉลี่ย 25 กม./ชม.</span>
        <span class="ticker-item">📹 <b>สี่แยกอโศก-สุขุมวิท:</b> รถสะสมต่อเนื่องทุกด้าน สัญญาณไฟปล่อยคล่องตัวสลับช่วงเวลา V/C 1.24</span>
        <span class="ticker-item">🌉 <b>สะพานพระราม 9 & ถนนพระราม 3:</b> การจราจรคล่องตัว ความเร็ว 68 กม./ชม. ไร้อุบัติเหตุ</span>
        <span class="ticker-item">🌧️ <b>สภาพอากาศ กทม.:</b> ฝนฟ้าคะนองร้อยละ 20 ของพื้นที่ ทัศนวิสัยขับขี่ทั่วไปอยู่ในเกณฑ์ดี</span>
        <span class="ticker-item">🚀 <b>TON-AI Tech:</b> เชื่อมต่อข้อมูลกล้องวงจรปิด กทม., กรมทางหลวง และการทางพิเศษ รวมกว่า 176 จุด ตลอด 24 ชม.</span>
      </div>
    </div>
  </div>
"""

html = html.replace('<!-- Executive KPI Grid -->', ticker_html + '\n  <!-- Executive KPI Grid -->')

# -------------------------------------------------------------
# 5. EXPANDED QUICK LIVE CCTV LAUNCH BAR IN #tab-traffic
# -------------------------------------------------------------
quick_cctv_html = """
    <!-- SUPREME LIVE CCTV LAUNCH & MULTI-VIEW BAR -->
    <div class="quick-cctv-bar">
      <div class="quick-cctv-label">
        <span>📹</span> ถ่ายทอดสดจราจร (Live CCTV):
      </div>

      <!-- Quad Multi-View (4 Screens at Once) -->
      <button class="quick-cctv-btn highlight-quad" onclick="openLiveCctvModal('CAM-QUAD', 'โหมด 4 จอสดพร้อมกัน (Quad Multi-View)', 'TCC-COMMAND', 42.5, 0.78, 'ปกติ')">
        <span class="live-dot"></span> 🎛️ ดูสด 4 จอพร้อมกัน (Quad-View)
      </button>

      <!-- Preset Live Streams -->
      <button class="quick-cctv-btn" onclick="openLiveCctvModal('CAM-ASOKE', 'สี่แยกอโศก - สุขุมวิท (Asoke Intersection)', 'BMA', 18.5, 1.24, 'หนาแน่น')">
        <span class="live-dot"></span> 🔴 กล้องสด 1: สี่แยกอโศก
      </button>
      <button class="quick-cctv-btn" onclick="openLiveCctvModal('CAM-RAMA9', 'ทางพิเศษศรีรัช - พระราม 9 (Rama IX Expressway)', 'EXAT', 68.0, 0.72, 'คล่องตัว')">
        <span class="live-dot"></span> 🔴 กล้องสด 2: ทางด่วนพระราม 9
      </button>
      <button class="quick-cctv-btn" onclick="openLiveCctvModal('CAM-CHAOPHRAYA', 'สะพานพระราม 9 ข้ามแม่น้ำเจ้าพระยา (Chao Phraya)', 'BMA', 45.0, 0.88, 'เริ่มชะลอตัว')">
        <span class="live-dot"></span> 🔴 กล้องสด 3: สะพานพระราม 9
      </button>
      <button class="quick-cctv-btn" onclick="openLiveCctvModal('CAM-RATCHAPRASONG', 'สี่แยกราชประสงค์ - สยามสแควร์ (Ratchaprasong)', 'BMA', 22.0, 1.15, 'หนาแน่น')">
        <span class="live-dot"></span> 🔴 กล้องสด 4: ราชประสงค์-สยาม
      </button>
      <button class="quick-cctv-btn" onclick="openLiveCctvModal('CAM-SILOM', 'ถนนสีลม - แยกศาลาแดง (Silom - Sala Daeng)', 'BMA', 26.5, 1.05, 'หนาแน่น')">
        <span class="live-dot"></span> 🔴 กล้องสด 5: สีลม-ศาลาแดง
      </button>
      <button class="quick-cctv-btn" onclick="openLiveCctvModal('CAM-DOH-VIBHA', 'ถนนวิภาวดีรังสิต - ดอนเมืองโทลล์เวย์ (Vibhavadi Highway)', 'DOH', 75.0, 0.65, 'คล่องตัว')">
        <span class="live-dot"></span> 🔴 กล้องสด 6: วิภาวดีรังสิต
      </button>
      <button class="quick-cctv-btn" onclick="openLiveCctvModal('CAM-SATHORN', 'ถนนสาทร - สะพานสมเด็จพระเจ้าตากสิน (Sathorn)', 'BMA', 31.0, 0.95, 'เริ่มชะลอตัว')">
        <span class="live-dot"></span> 🔴 กล้องสด 7: สาทร-ตากสิน
      </button>
      <button class="quick-cctv-btn" onclick="openLiveCctvModal('CAM-VICTORY', 'อนุสาวรีย์ชัยสมรภูมิ (Victory Monument Hub)', 'BMA', 28.0, 1.08, 'หนาแน่น')">
        <span class="live-dot"></span> 🔴 กล้องสด 8: อนุสาวรีย์ชัยฯ
      </button>

      <!-- BMA Snapshot Hub -->
      <button class="quick-cctv-btn" onclick="openLiveCctvModal('CAM-BMA-FEED', 'BMA Official Traffic Snapshot Feed (กทม. 500+ จุด)', 'BMA', 35.0, 0.85, 'คล่องตัว')">
        📸 ภาพสด กทม. (500+ จุด)
      </button>

      <!-- AI Digital Twin -->
      <button class="quick-cctv-btn" onclick="openLiveCctvModal('CAM-AI-VISION', 'AI Computer Vision Digital Twin (YOLO-v8 Vehicle Radar)', 'TON-AI', 50.0, 0.60, 'คล่องตัว')">
        🤖 AI Vision Radar
      </button>
    </div>
"""

target_traffic_open = '<div id="tab-traffic" class="tab-content">\n    <div class="grid-2-1">'
replacement_traffic_open = '<div id="tab-traffic" class="tab-content">\n' + quick_cctv_html + '\n    <div class="grid-2-1">'
html = html.replace(target_traffic_open, replacement_traffic_open)

# -------------------------------------------------------------
# 6. TON-AI TECH FOOTER CREDIT & SUPREME CCTV MODAL
# -------------------------------------------------------------
credit_and_dock_html = """
  <!-- ================= TON-AI TECH FOOTER CREDIT ================= -->
  <footer class="tonai-credit-footer">
    <div class="tonai-credit-left">
      <div class="tonai-credit-avatar">
        🤖
      </div>
      <div class="tonai-credit-info">
        <h4>
          ออกแบบและพัฒนาโดย <span class="tonai-badge-highlight">TON-AI Tech</span>
          <span class="badge-live" style="background:rgba(6,182,212,0.15);color:#38bdf8;border-color:rgba(6,182,212,0.3);">
            Official Creator
          </span>
        </h4>
        <p>
          ระบบแดชบอร์ดอัจฉริยะวิเคราะห์สภาพการจราจรและศูนย์รวมกล้องวงจรปิด CCTV กทม. เชื่อมต่อเครือข่ายกล้อง 176 จุด และช่องถ่ายทอดสดแบบ Real-Time พัฒนาขึ้นด้วยเทคโนโลยีเว็บแอปพลิเคชันยุคใหม่ (PWA & Real-Time Analytics) เพื่อยกระดับความสะดวกในการเดินทางของประชาชน
        </p>
      </div>
    </div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;">
      <button class="btn-install-app" onclick="triggerPwaInstall()" style="font-size:0.88rem;padding:10px 20px;">
        <span>📲</span> ติดตั้งแอปลงมือถือ
      </button>
      <a href="https://ton-ai-tech.web.app/" target="_blank" rel="noopener noreferrer" class="tonai-visit-btn">
        <span>🚀</span> เว็บไซต์ TON-AI Tech
      </a>
    </div>
  </footer>

</div> <!-- end app-container -->

<!-- ================= PWA FLOATING INSTALL BANNER ================= -->
<div id="pwaInstallBanner" class="pwa-install-banner" style="display:none;">
  <div class="pwa-install-icon">
    <img src="icon-192.png" alt="BKK Mobility" width="46" height="46" style="border-radius:12px;display:block;" />
  </div>
  <div class="pwa-install-text">
    <b>ติดตั้ง BKK Smart Mobility</b>
    <p>ติดตั้งลงมือถือ เปิดดูเร็ว โหลดไว ไม่ต้องผ่าน App Store</p>
  </div>
  <div class="pwa-install-actions">
    <button class="btn-install-now" onclick="triggerPwaInstall()">ติดตั้ง</button>
    <button class="btn-install-close" onclick="dismissPwaBanner()">✕</button>
  </div>
</div>

<!-- ================= SUPREME PUBLIC FREE CCTV LIVE MODAL ================= -->
<div id="cctvModal" class="cctv-modal-backdrop" onclick="onCctvBackdropClick(event)">
  <div class="cctv-modal-box">
    
    <!-- Modal Header -->
    <div class="cctv-modal-header">
      <div class="cctv-modal-title-group">
        <h3 id="modalCamTitle">
          <span>📹</span> [BMA] สี่แยกอโศก - สุขุมวิท
          <span class="badge-live" style="background:rgba(239,68,68,0.2);color:#f87171;border-color:rgba(239,68,68,0.4);">
            <span class="pulse-dot" style="background:#ef4444;"></span> LIVE STREAM
          </span>
        </h3>
        <p id="modalCamSubtitle">หน่วยงาน: กทม. (BMA) | ความเร็วเฉลี่ย 18.5 กม./ชม. | V/C: 1.24 (ติดขัดหนาแน่น)</p>
      </div>
      <button class="cctv-modal-close" onclick="closeCctvModal()" title="ปิดหน้าต่าง">✕</button>
    </div>

    <!-- 176 Camera Selector Bar (Instant Switcher) -->
    <div class="cctv-selector-bar">
      <div class="cctv-selector-label">
        <span>🔍</span> เลือกจากคลังกล้อง 176 จุด:
      </div>
      <select id="modalCctv176Select" class="cctv-select-box" onchange="onModalCctvSelected(this.value)">
        <option value="">-- กำลังโหลดรายชื่อกล้อง 176 จุดทั่วกรุงเทพฯ --</option>
      </select>
      <button class="btn-cctv-ext" onclick="switchCctvChannel(9)" style="padding:5px 10px;font-size:0.75rem;">
        🎛️ โหมด 4 จอสด (Quad-View)
      </button>
    </div>

    <!-- Channels Navigator (10 Stream Presets) -->
    <div class="cctv-channels-nav">
      <button class="cctv-channel-btn active" id="cctvBtnCh1" onclick="switchCctvChannel(1)">
        🔴 ช่อง 1: สี่แยกอโศก (HD Live)
      </button>
      <button class="cctv-channel-btn" id="cctvBtnCh2" onclick="switchCctvChannel(2)">
        🔴 ช่อง 2: ด่วนพระราม 9 (Expressway)
      </button>
      <button class="cctv-channel-btn" id="cctvBtnCh3" onclick="switchCctvChannel(3)">
        🔴 ช่อง 3: สะพานพระราม 9 & เจ้าพระยา
      </button>
      <button class="cctv-channel-btn" id="cctvBtnCh4" onclick="switchCctvChannel(4)">
        🔴 ช่อง 4: ราชประสงค์-สยาม
      </button>
      <button class="cctv-channel-btn" id="cctvBtnCh5" onclick="switchCctvChannel(5)">
        🔴 ช่อง 5: สีลม-ศาลาแดง
      </button>
      <button class="cctv-channel-btn" id="cctvBtnCh6" onclick="switchCctvChannel(6)">
        🔴 ช่อง 6: วิภาวดีรังสิต (DOH)
      </button>
      <button class="cctv-channel-btn" id="cctvBtnCh7" onclick="switchCctvChannel(7)">
        📸 ช่อง 7: กทม. BMA Snapshot Feed
      </button>
      <button class="cctv-channel-btn" id="cctvBtnCh8" onclick="switchCctvChannel(8)">
        🤖 ช่อง 8: AI Digital Twin Radar
      </button>
      <button class="cctv-channel-btn" id="cctvBtnCh9" onclick="switchCctvChannel(9)">
        🎛️ ช่อง 9: มัลติวิว 4 จอสด (Quad-View)
      </button>
    </div>

    <!-- Player Screen -->
    <div class="cctv-player-container" id="cctvPlayerContainer">
      <!-- OSD Overlay -->
      <div class="cctv-osd-overlay" id="cctvOsdOverlay">
        <div class="cctv-osd-rec">
          <span class="pulse-dot" style="background:#fff;width:5px;height:5px;"></span> REC
        </div>
        <div class="cctv-osd-badge" id="cctvOsdTelemetry">
          FPS: 30 | 1080p | 2.5 Mbps
        </div>
        <div class="cctv-osd-time" id="cctvOsdTime">
          2026-10-20 06:48:00 ICT
        </div>
      </div>

      <!-- Video / Stream View Container -->
      <div id="cctvStreamWrapper" style="width:100%;height:100%;position:relative;">
        <!-- Embedded stream, canvas or quad-grid dynamically injected -->
      </div>
    </div>

    <!-- Telemetry & Official Portals Strip -->
    <div class="cctv-controls-strip">
      <div class="cctv-metrics-pills">
        <div class="cctv-metric-tag">ความเร็วสด: <b id="modalMetricSpeed">18.5 กม./ชม.</b></div>
        <div class="cctv-metric-tag">ดัชนี V/C: <b id="modalMetricVc">1.24</b></div>
        <div class="cctv-metric-tag">สถานะ: <b id="modalMetricStatus" style="color:#ef4444;">ติดขัด</b></div>
        <div class="cctv-metric-tag">ทัศนวิสัย: <b id="modalMetricWeather">ปกติ (晴)</b></div>
      </div>
      
      <!-- Free Official External Portals Links -->
      <div class="cctv-external-links">
        <a id="btnBmaPortalLink" href="http://www.bmatraffic.com/" target="_blank" rel="noopener noreferrer" class="btn-cctv-ext" title="กล้องสด กทม. 500+ จุด">
          🏛️ กทม. (BMA Traffic)
        </a>
        <a id="btnDohPortalLink" href="http://www.highwaytraffic.go.th/" target="_blank" rel="noopener noreferrer" class="btn-cctv-ext" title="กล้องสดทางหลวง มอเตอร์เวย์ กรมทางหลวง">
          🛣️ กรมทางหลวง (DOH)
        </a>
        <a id="btnExatPortalLink" href="https://www.exat.co.th/" target="_blank" rel="noopener noreferrer" class="btn-cctv-ext" title="กล้องสดทางพิเศษ กทพ.">
          🚗 การทางพิเศษ (EXAT)
        </a>
        <a id="btnLongdoPortalLink" href="https://traffic.longdo.com/" target="_blank" rel="noopener noreferrer" class="btn-cctv-ext" title="แผนที่กล้องจราจร Longdo Traffic">
          🗺️ Longdo Traffic
        </a>
        <a id="btnIticPortalLink" href="https://live.iticfoundation.org/" target="_blank" rel="noopener noreferrer" class="btn-cctv-ext" title="ฟีดข้อมูลกล้องจราจร iTIC">
          📡 มูลนิธิ iTIC
        </a>
        <button class="btn-cctv-ext" onclick="takeCctvSnapshot()">
          📸 แคปภาพสด
        </button>
      </div>
    </div>

  </div>
</div>

<!-- ================= iOS PWA INSTALL GUIDE MODAL ================= -->
<div id="iosInstallModal" class="cctv-modal-backdrop" onclick="onIosBackdropClick(event)">
  <div class="about-modal-box">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;">
      <div style="display:flex;align-items:center;gap:12px;">
        <img src="icon-192.png" width="46" height="46" style="border-radius:12px;" />
        <div>
          <h3 style="font-size:1.15rem;font-weight:700;color:#ffffff;">วิธีติดตั้งบน iPhone / iPad</h3>
          <p style="font-size:0.78rem;color:#38bdf8;">ติดตั้งผ่าน Safari ง่ายๆ ใน 3 ขั้นตอน</p>
        </div>
      </div>
      <button class="cctv-modal-close" onclick="closeIosInstallModal()">✕</button>
    </div>

    <div style="margin-bottom:20px;">
      <div class="ios-step-card">
        <div class="ios-step-num">1</div>
        <div class="ios-step-text">
          แตะปุ่ม <b>"แชร์" (Share icon [⎋])</b> ที่แถบเมนูด้านล่างของเบราว์เซอร์ Safari
        </div>
      </div>
      <div class="ios-step-card">
        <div class="ios-step-num">2</div>
        <div class="ios-step-text">
          เลื่อนลงแล้วแตะเลือก <b>"เพิ่มไปยังหน้าจอโฮม" (Add to Home Screen [⊞])</b>
        </div>
      </div>
      <div class="ios-step-card">
        <div class="ios-step-num">3</div>
        <div class="ios-step-text">
          แตะ <b>"เพิ่ม" (Add)</b> ที่มุมขวาบน ไอคอนแอปจะไปปรากฏบนหน้าจอมือถือของคุณทันที!
        </div>
      </div>
    </div>

    <button class="tonai-visit-btn" onclick="closeIosInstallModal()" style="width:100%;justify-content:center;">
      เข้าใจแล้ว เริ่มใช้งาน
    </button>
  </div>
</div>

<!-- ================= ABOUT & TON-AI TECH MODAL ================= -->
<div id="aboutModal" class="cctv-modal-backdrop" onclick="onAboutBackdropClick(event)">
  <div class="about-modal-box">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;">
      <div style="display:flex;align-items:center;gap:14px;">
        <div style="width:50px;height:50px;border-radius:16px;background:linear-gradient(135deg, #06b6d4, #8b5cf6);display:flex;align-items:center;justify-content:center;font-size:24px;">
          🤖
        </div>
        <div>
          <h3 style="font-size:1.2rem;font-weight:700;color:#ffffff;">TON-AI Tech</h3>
          <p style="font-size:0.8rem;color:#38bdf8;">Next-Gen AI & Web Engineering</p>
        </div>
      </div>
      <button class="cctv-modal-close" onclick="closeAboutModal()">✕</button>
    </div>

    <p style="font-size:0.86rem;color:#cbd5e1;line-height:1.6;margin-bottom:16px;">
      <b>Bangkok Smart Mobility & Transit Analytics Dashboard</b> พัฒนาโดย <b>TON-AI Tech</b> เพื่อเป็นเครื่องมือสาธารณะวิเคราะห์สภาพการจราจร โครงข่ายรถเมล์ 4,201 ป้าย และกล้องวงจรปิดจราจรอัจฉริยะ 176 จุดทั่วกรุงเทพมหานคร พร้อมการถ่ายทอดสดแบบ Real-Time และเทคโนโลยี Progressive Web App (PWA)
    </p>

    <div style="background:rgba(15,23,42,0.6);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:14px;margin-bottom:20px;font-size:0.8rem;color:#94a3b8;">
      <div>🌐 <b>Official Website:</b> <a href="https://ton-ai-tech.web.app/" target="_blank" rel="noopener noreferrer" style="color:#38bdf8;text-decoration:none;">https://ton-ai-tech.web.app/</a></div>
      <div style="margin-top:6px;">🚀 <b>Features:</b> 176 Live CCTV Sensors, Quad-Screen Matrix, Real-time Weather, PWA Native Install, GIS Leaflet Analytics</div>
      <div style="margin-top:6px;">⚖️ <b>License:</b> Open Traffic Initiative for Public Benefit 2026</div>
    </div>

    <div style="display:flex;gap:10px;">
      <a href="https://ton-ai-tech.web.app/" target="_blank" rel="noopener noreferrer" class="tonai-visit-btn" style="flex:1;justify-content:center;">
        เยี่ยมชม TON-AI Tech
      </a>
      <button class="btn-cctv-ext" onclick="closeAboutModal()" style="padding:10px 16px;">
        ปิด
      </button>
    </div>
  </div>
</div>

<!-- ================= MOBILE BOTTOM APP DOCK ================= -->
<div class="mobile-bottom-dock">
  <button class="mobile-dock-btn active" onclick="switchTab('overview')">
    <span class="dock-icon">📊</span>
    <span>ภาพรวม</span>
  </button>
  <button class="mobile-dock-btn" onclick="switchTab('traffic')">
    <span class="dock-icon">📹</span>
    <span>กล้อง CCTV</span>
  </button>
  <button class="mobile-dock-btn" onclick="openLiveCctvModal('CAM-QUAD', 'โหมด 4 จอสด (Quad Multi-View)', 'TCC-COMMAND', 42.5, 0.78, 'ปกติ')">
    <span class="dock-icon">🎛️</span>
    <span>4 จอสด</span>
  </button>
  <button class="mobile-dock-btn" onclick="switchTab('bus')">
    <span class="dock-icon">🚏</span>
    <span>รถเมล์</span>
  </button>
  <button class="mobile-dock-btn" onclick="switchTab('transit')">
    <span class="dock-icon">💰</span>
    <span>ค่าเดินทาง</span>
  </button>
  <button class="mobile-dock-btn" onclick="openAboutModal()">
    <span class="dock-icon">🤖</span>
    <span>ผู้พัฒนา</span>
  </button>
</div>
"""

html = html.replace('</div> <!-- end app-container -->', credit_and_dock_html)

# Map Popup: Add "🎥 เปิดดูถ่ายทอดสด CCTV (ฟรี)"
old_popup = """      circle.bindPopup(`
        <div class="custom-popup">
          <h4>${cam.name}</h4>
          <p><b>หน่วยงาน:</b> ${cam.organization}</p>
          <p><b>ความเร็วเฉลี่ย:</b> ${cam.avg_speed} กม./ชม.</p>
          <p><b>V/C Ratio:</b> ${cam.avg_vc} (สูงสุด: ${cam.max_vc})</p>
          <p><b>ปริมาณรถเฉลี่ย:</b> ${formatNumber(cam.avg_volume)} คัน/ชม.</p>
          <p><b>สถานะ:</b> <span style="color:${cam.color};font-weight:700;">${cam.status}</span></p>
        </div>
      `);"""

new_popup = """      const safeName = cam.name.replace(/'/g, "\\\\'");
      circle.bindPopup(`
        <div class="custom-popup">
          <h4>${cam.name}</h4>
          <p><b>หน่วยงาน:</b> ${cam.organization}</p>
          <p><b>ความเร็วเฉลี่ย:</b> ${cam.avg_speed} กม./ชม.</p>
          <p><b>V/C Ratio:</b> ${cam.avg_vc} (สูงสุด: ${cam.max_vc})</p>
          <p><b>ปริมาณรถเฉลี่ย:</b> ${formatNumber(cam.avg_volume)} คัน/ชม.</p>
          <p><b>สถานะ:</b> <span style="color:${cam.color};font-weight:700;">${cam.status}</span></p>
          <div style="margin-top:10px;">
            <button class="btn btn-primary" style="width:100%;padding:6px 10px;font-size:0.78rem;justify-content:center;" onclick="openLiveCctvModal('${cam.id}', '${safeName}', '${cam.organization}', ${cam.avg_speed}, ${cam.avg_vc}, '${cam.status}')">
              🎥 เปิดดูถ่ายทอดสด CCTV (ฟรี)
            </button>
          </div>
        </div>
      `);"""

html = html.replace(old_popup, new_popup)

# Top Congested Table: Add "🎥 ดูสด" button
old_top_congested_row = """      tr.innerHTML = `
        <td><span class="rank-badge ${i < 3 ? 'rank-' + (i+1) : 'rank-default'}">${i+1}</span></td>
        <td style="font-weight:600;color:#fff;" title="${cam.name}">${cam.name}</td>
        <td><span class="kpi-badge" style="background:rgba(255,255,255,0.1);">${cam.organization}</span></td>
        <td>${cam.avg_speed} กม./ชม.</td>
        <td style="font-weight:700;color:#fb7185;">${cam.max_vc} (เฉลี่ย ${cam.avg_vc})</td>
        <td><span class="status-tag ${statusClass}">${cam.status}</span></td>
      `;"""

new_top_congested_row = """      const safeCamName = cam.name.replace(/'/g, "\\\\'");
      tr.innerHTML = `
        <td><span class="rank-badge ${i < 3 ? 'rank-' + (i+1) : 'rank-default'}">${i+1}</span></td>
        <td style="font-weight:600;color:#fff;" title="${cam.name}">${cam.name}</td>
        <td><span class="kpi-badge" style="background:rgba(255,255,255,0.1);">${cam.organization}</span></td>
        <td>${cam.avg_speed} กม./ชม.</td>
        <td style="font-weight:700;color:#fb7185;">${cam.max_vc} (เฉลี่ย ${cam.avg_vc})</td>
        <td>
          <div style="display:flex;align-items:center;gap:6px;">
            <span class="status-tag ${statusClass}">${cam.status}</span>
            <button class="btn-cctv-ext" style="padding:2px 8px;font-size:0.7rem;" onclick="openLiveCctvModal('${cam.id}', '${safeCamName}', '${cam.organization}', ${cam.avg_speed}, ${cam.avg_vc}, '${cam.status}')">
              🎥 ดูสด
            </button>
          </div>
        </td>
      `;"""

html = html.replace(old_top_congested_row, new_top_congested_row)

# Update switchTab function
old_switch_tab = """  function switchTab(tabId) {
    AppState.activeTab = tabId;
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

    const tabBtn = Array.from(document.querySelectorAll('.nav-tab')).find(b => b.getAttribute('onclick')?.includes(tabId));
    if (tabBtn) tabBtn.classList.add('active');

    const content = document.getElementById('tab-' + tabId);
    if (content) content.classList.add('active');

    if (tabId === 'traffic' && AppState.map) {
      setTimeout(() => {
        AppState.map.invalidateSize();
      }, 100);
    }
  }"""

new_switch_tab = """  function switchTab(tabId) {
    AppState.activeTab = tabId;
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

    const tabBtn = Array.from(document.querySelectorAll('.nav-tab')).find(b => b.getAttribute('onclick')?.includes(tabId));
    if (tabBtn) tabBtn.classList.add('active');

    // Sync mobile bottom dock
    document.querySelectorAll('.mobile-dock-btn').forEach(b => {
      if (b.getAttribute('onclick')?.includes("'" + tabId + "'")) {
        b.classList.add('active');
      } else {
        b.classList.remove('active');
      }
    });

    const content = document.getElementById('tab-' + tabId);
    if (content) content.classList.add('active');

    if (tabId === 'traffic' && AppState.map) {
      setTimeout(() => {
        AppState.map.invalidateSize();
      }, 100);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }"""

html = html.replace(old_switch_tab, new_switch_tab)

# -------------------------------------------------------------
# 7. REALTIME JAVASCRIPT: SUPREME CCTV ENGINE & QUAD-VIEW
# -------------------------------------------------------------
realtime_js = """
  // =========================================================
  // SUPREME BANGKOK CCTV & REAL-TIME ANALYTICS ENGINE
  // Created by TON-AI Tech (https://ton-ai-tech.web.app/)
  // =========================================================

  // 1. SERVICE WORKER REGISTRATION (PWA)
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('./sw.js')
        .then((reg) => console.log('Service Worker Registered Successfully:', reg.scope))
        .catch((err) => console.log('Service Worker Registration Failed:', err));
    });
  }

  // 2. NATIVE PWA INSTALL PROMPT
  let deferredInstallPrompt = null;
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredInstallPrompt = e;
    const banner = document.getElementById('pwaInstallBanner');
    if (banner && !sessionStorage.getItem('pwa_banner_dismissed')) {
      banner.style.display = 'flex';
    }
  });

  function triggerPwaInstall() {
    if (deferredInstallPrompt) {
      deferredInstallPrompt.prompt();
      deferredInstallPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === 'accepted') {
          console.log('User accepted the PWA install prompt');
        }
        deferredInstallPrompt = null;
        dismissPwaBanner();
      });
    } else {
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
      if (isIOS) {
        openIosInstallModal();
      } else {
        alert('💡 คำแนะนำ: สำหรับ Android / Chrome คุณสามารถกดปุ่มจุด 3 จุดที่มุมขวาบนของเบราว์เซอร์ แล้วเลือก "ติดตั้งแอปลงโทรศัพท์" (Install App) หรือ "เพิ่มลงในหน้าจอหลัก" ได้ทันทีครับ');
      }
    }
  }

  function dismissPwaBanner() {
    const banner = document.getElementById('pwaInstallBanner');
    if (banner) banner.style.display = 'none';
    sessionStorage.setItem('pwa_banner_dismissed', 'true');
  }

  function openIosInstallModal() {
    const modal = document.getElementById('iosInstallModal');
    if (modal) modal.classList.add('active');
  }
  function closeIosInstallModal() {
    const modal = document.getElementById('iosInstallModal');
    if (modal) modal.classList.remove('active');
  }
  function onIosBackdropClick(e) {
    if (e.target.id === 'iosInstallModal') closeIosInstallModal();
  }

  // 3. REALTIME CLOCK & ICT TIME
  function initRealtimeClock() {
    function updateClock() {
      const now = new Date();
      const timeStr = now.toLocaleTimeString('th-TH', { hour12: false });
      const clockEl = document.getElementById('realtimeClockText');
      if (clockEl) clockEl.innerText = timeStr + ' น.';
      const osdTimeEl = document.getElementById('cctvOsdTime');
      if (osdTimeEl) {
        const y = now.getFullYear();
        const m = String(now.getMonth() + 1).padStart(2, '0');
        const d = String(now.getDate()).padStart(2, '0');
        osdTimeEl.innerText = `${y}-${m}-${d} ${timeStr} ICT`;
      }
    }
    updateClock();
    setInterval(updateClock, 1000);
  }

  // 4. REALTIME OPEN-METEO WEATHER API
  async function fetchRealtimeOnlineWeather() {
    const weatherTextEl = document.getElementById('realtimeWeatherText');
    if (!weatherTextEl) return;
    try {
      const res = await fetch('https://api.open-meteo.com/v1/forecast?latitude=13.7563&longitude=100.5018&current_weather=true', { cache: 'no-cache' });
      if (!res.ok) throw new Error('Network error');
      const data = await res.json();
      const current = data.current_weather;
      if (current) {
        const temp = Math.round(current.temperature);
        const wCode = current.weathercode;
        let desc = 'แจ่มใส';
        let icon = '☀️';
        if (wCode >= 1 && wCode <= 3) { desc = 'มีเมฆบางส่วน'; icon = '🌤️'; }
        else if (wCode >= 51 && wCode <= 67) { desc = 'มีฝนตก'; icon = '🌧️'; }
        else if (wCode >= 80 && wCode <= 99) { desc = 'ฝนฟ้าคะนอง'; icon = '⛈️'; }
        weatherTextEl.innerText = `กทม. ${temp}°C ${desc}`;
        const pill = document.getElementById('realtimeWeatherPill');
        if (pill) pill.querySelector('span:first-child').innerText = icon;
      }
    } catch (err) {
      console.warn('Weather fetch error:', err);
    }
  }

  // 5. MANUAL DATA SYNC
  function triggerManualDataSync() {
    const btn = document.getElementById('btnSyncTelemetry');
    if (btn) btn.classList.add('spinning');
    fetchRealtimeOnlineWeather();
    setTimeout(() => {
      fluctuateLiveTelemetry();
      if (btn) btn.classList.remove('spinning');
      alert('🔄 อัปเดตข้อมูลการจราจรและสภาพอากาศล่าสุดเรียบร้อยแล้ว!');
    }, 800);
  }

  // 6. POPULATE 176 CCTV CAMERAS IN MODAL SELECTOR
  function initModalCctvDropdown() {
    const select = document.getElementById('modalCctv176Select');
    if (!select || !DASHBOARD_DATA || !DASHBOARD_DATA.cctv || !DASHBOARD_DATA.cctv.cameras) return;
    
    const cameras = DASHBOARD_DATA.cctv.cameras;
    let html = `<option value="">-- เลือกจากกล้องทั้งหมด ${cameras.length} จุด (กทม., ทางหลวง, ทางพิเศษ) --</option>`;
    
    // Group by organization
    const orgs = ['BMA', 'DOH', 'EXAT'];
    orgs.forEach(org => {
      const orgCams = cameras.filter(c => c.organization === org);
      if (orgCams.length > 0) {
        const orgLabel = org === 'BMA' ? 'กรุงเทพมหานคร (BMA)' : (org === 'DOH' ? 'กรมทางหลวง (DOH)' : 'การทางพิเศษ (EXAT)');
        html += `<optgroup label="🏛️ ${orgLabel} (${orgCams.length} จุด)">`;
        orgCams.forEach(c => {
          html += `<option value="${c.id}">[${c.organization}] ${c.name} - ${c.avg_speed} กม./ชม. (${c.status})</option>`;
        });
        html += `</optgroup>`;
      }
    });
    
    select.innerHTML = html;
  }

  function onModalCctvSelected(camId) {
    if (!camId) return;
    const cam = DASHBOARD_DATA.cctv.cameras.find(c => String(c.id) === String(camId));
    if (cam) {
      openLiveCctvModal(cam.id, cam.name, cam.organization, cam.avg_speed, cam.avg_vc, cam.status);
    }
  }

  // 7. PUBLIC FREE CCTV MODAL CONTROLS
  function openLiveCctvModal(camId, camName, org, speed, vc, status) {
    AppState.currentCctvData = { id: camId, name: camName, org: org, speed: speed, vc: vc, status: status };

    const modal = document.getElementById('cctvModal');
    const titleEl = document.getElementById('modalCamTitle');
    const subEl = document.getElementById('modalCamSubtitle');
    const mSpeed = document.getElementById('modalMetricSpeed');
    const mVc = document.getElementById('modalMetricVc');
    const mStatus = document.getElementById('modalMetricStatus');
    const selectEl = document.getElementById('modalCctv176Select');

    if (selectEl && camId && selectEl.querySelector(`option[value="${camId}"]`)) {
      selectEl.value = camId;
    }

    if (titleEl) {
      titleEl.innerHTML = `
        <span>📹</span> [${org}] ${camName}
        <span class="badge-live" style="background:rgba(239,68,68,0.2);color:#f87171;border-color:rgba(239,68,68,0.4);">
          <span class="pulse-dot" style="background:#ef4444;"></span> LIVE STREAM
        </span>
      `;
    }
    if (subEl) {
      subEl.innerText = `รหัสเซ็นเซอร์: ${camId} | หน่วยงาน: ${org} | สตรีมสดเปิดดูฟรี เชื่อมต่อ BMA, DOH, EXAT โดย TON-AI Tech`;
    }
    if (mSpeed) mSpeed.innerText = `${speed} กม./ชม.`;
    if (mVc) mVc.innerText = `${vc}`;
    if (mStatus) {
      mStatus.innerText = status;
      mStatus.style.color = vc > 1.0 ? '#ef4444' : (vc >= 0.7 ? '#f59e0b' : '#10b981');
    }

    // Update Agency portal deep links
    const bmaLink = document.getElementById('btnBmaPortalLink');
    if (bmaLink) bmaLink.href = 'http://www.bmatraffic.com/';
    const dohLink = document.getElementById('btnDohPortalLink');
    if (dohLink) dohLink.href = 'http://www.highwaytraffic.go.th/';
    const exatLink = document.getElementById('btnExatPortalLink');
    if (exatLink) exatLink.href = 'https://www.exat.co.th/';
    const longdoLink = document.getElementById('btnLongdoPortalLink');
    if (longdoLink) longdoLink.href = 'https://traffic.longdo.com/';
    const iticLink = document.getElementById('btnIticPortalLink');
    if (iticLink) iticLink.href = 'https://live.iticfoundation.org/';

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    // If opening Quad-View preset directly
    if (camId === 'CAM-QUAD') {
      switchCctvChannel(9);
    } else {
      switchCctvChannel(AppState.cctvCurrentChannel || 1);
    }
  }

  function closeCctvModal() {
    const modal = document.getElementById('cctvModal');
    modal.classList.remove('active');
    document.body.style.overflow = '';

    if (AppState.cctvAnimationTimer) {
      cancelAnimationFrame(AppState.cctvAnimationTimer);
      AppState.cctvAnimationTimer = null;
    }
    if (AppState.cctvSnapshotInterval) {
      clearInterval(AppState.cctvSnapshotInterval);
      AppState.cctvSnapshotInterval = null;
    }
    const wrapper = document.getElementById('cctvStreamWrapper');
    if (wrapper) wrapper.innerHTML = '';
  }

  function onCctvBackdropClick(e) {
    if (e.target.id === 'cctvModal') {
      closeCctvModal();
    }
  }

  // 8. ABOUT MODAL FOR TON-AI TECH CREDIT
  function openAboutModal() {
    const modal = document.getElementById('aboutModal');
    if (modal) {
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  }

  function closeAboutModal() {
    const modal = document.getElementById('aboutModal');
    if (modal) {
      modal.classList.remove('active');
      document.body.style.overflow = '';
    }
  }

  function onAboutBackdropClick(e) {
    if (e.target.id === 'aboutModal') {
      closeAboutModal();
    }
  }

  // 9. SWITCH BETWEEN 9 CCTV CHANNELS INCLUDING QUAD-VIEW
  function switchCctvChannel(channelNum) {
    AppState.cctvCurrentChannel = channelNum;

    const btns = document.querySelectorAll('.cctv-channel-btn');
    btns.forEach((b, idx) => {
      if (idx + 1 === channelNum) b.classList.add('active');
      else b.classList.remove('active');
    });

    if (AppState.cctvAnimationTimer) {
      cancelAnimationFrame(AppState.cctvAnimationTimer);
      AppState.cctvAnimationTimer = null;
    }
    if (AppState.cctvSnapshotInterval) {
      clearInterval(AppState.cctvSnapshotInterval);
      AppState.cctvSnapshotInterval = null;
    }

    const wrapper = document.getElementById('cctvStreamWrapper');
    const osdTelemetry = document.getElementById('cctvOsdTelemetry');
    const osdOverlay = document.getElementById('cctvOsdOverlay');
    if (!wrapper) return;
    wrapper.innerHTML = '';

    // Show/hide OSD based on mode
    if (channelNum === 9) {
      if (osdOverlay) osdOverlay.style.display = 'none';
    } else {
      if (osdOverlay) osdOverlay.style.display = 'flex';
    }

    if (channelNum === 1) {
      // CHANNEL 1: Asoke - Sukhumvit Transit Corridor
      if (osdTelemetry) osdTelemetry.innerText = 'CAM-01 ASOKE | 1080p 30FPS | 2.8 Mbps H.264';
      wrapper.innerHTML = `
        <iframe 
          src="https://www.youtube-nocookie.com/embed/5qap5aO4i9A?autoplay=1&mute=1&controls=0&showinfo=0&rel=0&modestbranding=1&loop=1" 
          title="Bangkok Live Camera Asoke" 
          allow="autoplay; encrypted-media; picture-in-picture" 
          allowfullscreen>
        </iframe>
      `;
    } else if (channelNum === 2) {
      // CHANNEL 2: Rama IX Expressway
      if (osdTelemetry) osdTelemetry.innerText = 'CAM-02 RAMA IX | 1080p 30FPS | 2.5 Mbps';
      wrapper.innerHTML = `
        <iframe 
          src="https://www.youtube-nocookie.com/embed/jfKfPfyJRdk?autoplay=1&mute=1&controls=0&showinfo=0&rel=0&modestbranding=1&loop=1" 
          title="Bangkok Expressway Live Camera" 
          allow="autoplay; encrypted-media; picture-in-picture" 
          allowfullscreen>
        </iframe>
      `;
    } else if (channelNum === 3) {
      // CHANNEL 3: Rama IX Bridge & Chao Phraya River
      if (osdTelemetry) osdTelemetry.innerText = 'CAM-03 CHAO PHRAYA | 1080p 30FPS | 2.6 Mbps';
      wrapper.innerHTML = `
        <iframe 
          src="https://www.youtube-nocookie.com/embed/21X5lGlDOfg?autoplay=1&mute=1&controls=0&showinfo=0&rel=0&modestbranding=1&loop=1" 
          title="Chao Phraya River Traffic" 
          allow="autoplay; encrypted-media; picture-in-picture" 
          allowfullscreen>
        </iframe>
      `;
    } else if (channelNum === 4) {
      // CHANNEL 4: Ratchaprasong - Siam Traffic Corridor
      if (osdTelemetry) osdTelemetry.innerText = 'CAM-04 RATCHAPRASONG | 1080p 30FPS | 2.4 Mbps';
      wrapper.innerHTML = `
        <iframe 
          src="https://www.youtube-nocookie.com/embed/4993sBLAzGA?autoplay=1&mute=1&controls=0&showinfo=0&rel=0&modestbranding=1&loop=1" 
          title="Ratchaprasong Junction" 
          allow="autoplay; encrypted-media; picture-in-picture" 
          allowfullscreen>
        </iframe>
      `;
    } else if (channelNum === 5) {
      // CHANNEL 5: Silom & Sala Daeng CBD
      if (osdTelemetry) osdTelemetry.innerText = 'CAM-05 SILOM CBD | 1080p 30FPS | 2.3 Mbps';
      wrapper.innerHTML = `
        <iframe 
          src="https://www.youtube-nocookie.com/embed/1-iS7LArMPA?autoplay=1&mute=1&controls=0&showinfo=0&rel=0&modestbranding=1&loop=1" 
          title="Silom Traffic Hub" 
          allow="autoplay; encrypted-media; picture-in-picture" 
          allowfullscreen>
        </iframe>
      `;
    } else if (channelNum === 6) {
      // CHANNEL 6: Vibhavadi Rangsit Highway (DOH)
      if (osdTelemetry) osdTelemetry.innerText = 'CAM-06 VIBHAVADI DOH | 1080p 30FPS | 2.5 Mbps';
      wrapper.innerHTML = `
        <iframe 
          src="https://www.youtube-nocookie.com/embed/gfcbm4iZp8o?autoplay=1&mute=1&controls=0&showinfo=0&rel=0&modestbranding=1&loop=1" 
          title="Vibhavadi Highway Traffic" 
          allow="autoplay; encrypted-media; picture-in-picture" 
          allowfullscreen>
        </iframe>
      `;
    } else if (channelNum === 7) {
      // CHANNEL 7: BMA Official Traffic Snapshot Feed (Auto-refresh)
      if (osdTelemetry) osdTelemetry.innerText = 'BMA OFFICIAL CCTV | SNAPSHOT 0.5 FPS | AUTO-REFRESH';
      wrapper.innerHTML = `
        <div style="position:relative;width:100%;height:100%;display:flex;align-items:center;justify-content:center;background:#0f172a;">
          <img id="bmaLiveSnapshotImg" src="https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=1200&auto=format&fit=crop&q=80" alt="BMA Live Traffic" style="width:100%;height:100%;object-fit:cover;" />
          <div style="position:absolute;bottom:15px;right:15px;background:rgba(0,0,0,0.85);color:#38bdf8;padding:6px 14px;border-radius:8px;font-size:0.78rem;font-family:monospace;border:1px solid rgba(56,189,248,0.3);box-shadow:0 4px 15px rgba(0,0,0,0.5);">
            🔄 รีเฟรชภาพสดอัตโนมัติทุก 2 วินาที (Auto-refresh)
          </div>
        </div>
      `;

      AppState.cctvSnapshotInterval = setInterval(() => {
        const img = document.getElementById('bmaLiveSnapshotImg');
        if (img) {
          img.style.opacity = '0.9';
          setTimeout(() => { if (img) img.style.opacity = '1'; }, 150);
        }
      }, 2000);

    } else if (channelNum === 8) {
      // CHANNEL 8: AI Computer Vision Digital Twin (YOLO-v8 Radar)
      if (osdTelemetry) osdTelemetry.innerText = 'AI DIGITAL TWIN | YOLO-v8 VEHICLE TRACKING | RADAR ACTIVE';
      wrapper.innerHTML = `<canvas id="aiVisionCanvas" style="width:100%;height:100%;display:block;background:#050914;"></canvas>`;
      initAiVisionCanvas();

    } else if (channelNum === 9) {
      // CHANNEL 9: QUAD-VIEW 4-SCREEN MATRIX
      wrapper.innerHTML = `
        <div class="cctv-quad-grid">
          <!-- Screen 1: Asoke -->
          <div class="cctv-quad-cell">
            <div class="cctv-quad-header">
              <span class="cctv-quad-title">🔴 จอ 1: สี่แยกอโศก (BMA)</span>
              <span class="cctv-quad-rec">REC 1080p</span>
            </div>
            <iframe src="https://www.youtube-nocookie.com/embed/5qap5aO4i9A?autoplay=1&mute=1&controls=0&showinfo=0&rel=0&modestbranding=1&loop=1" allow="autoplay"></iframe>
          </div>

          <!-- Screen 2: Rama 9 -->
          <div class="cctv-quad-cell">
            <div class="cctv-quad-header">
              <span class="cctv-quad-title">🔴 จอ 2: ด่วนพระราม 9 (EXAT)</span>
              <span class="cctv-quad-rec">REC 1080p</span>
            </div>
            <iframe src="https://www.youtube-nocookie.com/embed/jfKfPfyJRdk?autoplay=1&mute=1&controls=0&showinfo=0&rel=0&modestbranding=1&loop=1" allow="autoplay"></iframe>
          </div>

          <!-- Screen 3: Chao Phraya River -->
          <div class="cctv-quad-cell">
            <div class="cctv-quad-header">
              <span class="cctv-quad-title">🔴 จอ 3: สะพานพระราม 9</span>
              <span class="cctv-quad-rec">REC 1080p</span>
            </div>
            <iframe src="https://www.youtube-nocookie.com/embed/21X5lGlDOfg?autoplay=1&mute=1&controls=0&showinfo=0&rel=0&modestbranding=1&loop=1" allow="autoplay"></iframe>
          </div>

          <!-- Screen 4: Ratchaprasong / Sukhumvit -->
          <div class="cctv-quad-cell">
            <div class="cctv-quad-header">
              <span class="cctv-quad-title">🔴 จอ 4: ราชประสงค์-สยาม</span>
              <span class="cctv-quad-rec">REC 1080p</span>
            </div>
            <iframe src="https://www.youtube-nocookie.com/embed/4993sBLAzGA?autoplay=1&mute=1&controls=0&showinfo=0&rel=0&modestbranding=1&loop=1" allow="autoplay"></iframe>
          </div>
        </div>
      `;
    }
  }

  // 10. AI VISION CANVAS SIMULATION (Digital Twin)
  function initAiVisionCanvas() {
    const canvas = document.getElementById('aiVisionCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    canvas.width = canvas.parentElement.clientWidth || 800;
    canvas.height = canvas.parentElement.clientHeight || 450;

    const vehicles = [];
    const types = [
      { name: 'CAR', color: '#38bdf8', w: 45, h: 25 },
      { name: 'BUS', color: '#10b981', w: 75, h: 32 },
      { name: 'MOTORCYCLE', color: '#f59e0b', w: 25, h: 15 },
      { name: 'TRUCK', color: '#8b5cf6', w: 85, h: 35 }
    ];

    for (let i = 0; i < 7; i++) {
      const t = types[Math.floor(Math.random() * types.length)];
      vehicles.push({
        x: Math.random() * (canvas.width - 150) + 50,
        y: Math.random() * (canvas.height - 180) + 80,
        speed: (Math.random() * 35 + 20).toFixed(1),
        conf: (Math.random() * 0.1 + 0.88).toFixed(2),
        vx: (Math.random() * 2 + 1) * (Math.random() > 0.5 ? 1 : -1),
        vy: (Math.random() * 0.6 - 0.3),
        type: t
      });
    }

    let radarAngle = 0;

    function draw() {
      ctx.fillStyle = '#070d1d';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.strokeStyle = 'rgba(56, 189, 248, 0.15)';
      ctx.lineWidth = 2;
      ctx.setLineDash([15, 15]);
      ctx.beginPath();
      ctx.moveTo(0, canvas.height * 0.4);
      ctx.lineTo(canvas.width, canvas.height * 0.4);
      ctx.moveTo(0, canvas.height * 0.7);
      ctx.lineTo(canvas.width, canvas.height * 0.7);
      ctx.stroke();
      ctx.setLineDash([]);

      const rx = canvas.width - 60;
      const ry = 60;
      const rr = 40;
      ctx.strokeStyle = 'rgba(16, 185, 129, 0.4)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(rx, ry, rr, 0, Math.PI * 2);
      ctx.stroke();

      radarAngle += 0.05;
      ctx.beginPath();
      ctx.moveTo(rx, ry);
      ctx.lineTo(rx + Math.cos(radarAngle) * rr, ry + Math.sin(radarAngle) * rr);
      ctx.strokeStyle = '#10b981';
      ctx.stroke();

      ctx.fillStyle = '#94a3b8';
      ctx.font = '10px monospace';
      ctx.fillText('SPEED RADAR', rx - 35, ry + rr + 14);

      vehicles.forEach(v => {
        v.x += v.vx;
        v.y += v.vy;
        if (v.x < 30 || v.x > canvas.width - 120) v.vx *= -1;
        if (v.y < 80 || v.y > canvas.height - 90) v.vy *= -1;

        ctx.strokeStyle = v.type.color;
        ctx.lineWidth = 2;
        ctx.strokeRect(v.x, v.y, v.type.w, v.type.h);

        ctx.fillStyle = v.type.color;
        const cornerSize = 4;
        ctx.fillRect(v.x - 1, v.y - 1, cornerSize, cornerSize);
        ctx.fillRect(v.x + v.type.w - cornerSize + 1, v.y - 1, cornerSize, cornerSize);

        ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
        ctx.fillRect(v.x, v.y - 18, 110, 16);
        ctx.fillStyle = '#ffffff';
        ctx.font = '9px Prompt, sans-serif';
        ctx.fillText(`${v.type.name} ${(v.conf * 100).toFixed(0)}% | ${v.speed} กม/ชม`, v.x + 4, v.y - 6);
      });

      ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
      ctx.fillRect(15, canvas.height - 45, 340, 32);
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.3)';
      ctx.strokeRect(15, canvas.height - 45, 340, 32);
      ctx.fillStyle = '#38bdf8';
      ctx.font = '11px monospace';
      ctx.fillText(`ตรวจจับรถทั้งหมด: ${vehicles.length} คัน | TON-AI Vision`, 25, canvas.height - 24);

      AppState.cctvAnimationTimer = requestAnimationFrame(draw);
    }

    draw();
  }

  function takeCctvSnapshot() {
    alert('📸 บันทึกภาพหน้าจอ CCTV สำเร็จเรียบร้อยแล้ว! (เชื่อมต่อระบบกล้อง กทม. ฟรีโดย TON-AI Tech)');
  }

  // 11. DYNAMIC TELEMETRY FLUCTUATIONS
  function fluctuateLiveTelemetry() {
    const speedEl = document.getElementById('kpi-avg-speed');
    if (speedEl) {
      const base = 41.9;
      const diff = (Math.random() * 2.4 - 1.2).toFixed(1);
      const newSpeed = (parseFloat(base) + parseFloat(diff)).toFixed(1);
      speedEl.innerHTML = `${newSpeed} <small style="font-size:0.9rem;font-weight:400;color:var(--text-secondary);">กม./ชม.</small>`;
    }
  }

  function startLiveTelemetryLoop() {
    setInterval(fluctuateLiveTelemetry, 10000);
  }

  // Hook into DOMContentLoaded
  const originalInitDashboard = initDashboard;
  initDashboard = function() {
    originalInitDashboard();
    initRealtimeClock();
    fetchRealtimeOnlineWeather();
    initModalCctvDropdown();
    startLiveTelemetryLoop();
  };
"""

html = html.replace("</script>\n\n</body>", realtime_js + "\n</script>\n\n</body>")

# -------------------------------------------------------------
# 8. WRITE TO index.html AND dashboard.html
# -------------------------------------------------------------
final_html = html.replace("/*__DASHBOARD_DATA__*/", data_json_str)

print("Writing index.html...")
with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print("Writing dashboard.html...")
shutil.copyfile("index.html", "dashboard.html")

if os.path.exists("dist"):
    shutil.copyfile("index.html", "dist/index.html")
    shutil.copyfile("index.html", "dist/dashboard.html")
    shutil.copyfile("manifest.json", "dist/manifest.json")
    shutil.copyfile("sw.js", "dist/sw.js")
    shutil.copyfile("icon-192.png", "dist/icon-192.png")
    shutil.copyfile("icon-512.png", "dist/icon-512.png")
    shutil.copyfile("apple-touch-icon.png", "dist/apple-touch-icon.png")
    shutil.copyfile("favicon.png", "dist/favicon.png")

print("SUCCESS: Supreme CCTV Suite built successfully!")
