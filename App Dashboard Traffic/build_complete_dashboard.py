# -*- coding: utf-8 -*-
"""
Script to build the complete standalone Bangkok Transit & Traffic Dashboard HTML file.
"""
import json
import os
import shutil

print("Reading dashboard_data.json...")
with open("dashboard_data.json", "r", encoding="utf-8") as f:
    data_json_str = f.read()

# Load to verify structure
data = json.loads(data_json_str)
overview = data["overview"]
print(f"Data verified: {overview['cctv_cameras_count']} CCTV cameras, {overview['bus_districts_count']} districts, {overview['travel_modes_count']} travel modes.")

# Prepare standalone HTML template
html_content = f'''<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Bangkok Smart Mobility & Transit Analytics Dashboard</title>
  <meta name="description" content="ระบบวิเคราะห์ข้อมูลการจราจรและโครงข่ายการเดินทางสาธารณะ กรุงเทพมหานคร จากข้อมูล CCTV, จุดจอดรถเมล์ และสถิติการเดินทาง" />

  <!-- Google Fonts: Prompt & Plus Jakarta Sans -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Prompt:wght@300;400;500;600;700&display=swap" rel="stylesheet">

  <!-- Chart.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>

  <!-- Leaflet Map CSS & JS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>

  <style>
    :root {{
      --bg-main: #0a0f1d;
      --bg-card: rgba(18, 26, 47, 0.75);
      --bg-card-hover: rgba(28, 40, 70, 0.85);
      --bg-glass: rgba(15, 23, 42, 0.65);
      --border-color: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(56, 189, 248, 0.5);
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --text-muted: #64748b;
      
      --accent-cyan: #06b6d4;
      --accent-cyan-glow: rgba(6, 182, 212, 0.25);
      --accent-blue: #3b82f6;
      --accent-emerald: #10b981;
      --accent-emerald-glow: rgba(16, 185, 129, 0.25);
      --accent-amber: #f59e0b;
      --accent-rose: #f43f5e;
      --accent-purple: #8b5cf6;

      --radius-sm: 8px;
      --radius-md: 14px;
      --radius-lg: 20px;
      --shadow-card: 0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
      --shadow-glow: 0 0 20px rgba(6, 182, 212, 0.15);
      --transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Prompt', 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-main);
      background-image: 
        radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.12) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(139, 92, 246, 0.12) 0px, transparent 50%),
        radial-gradient(at 50% 100%, rgba(6, 182, 212, 0.08) 0px, transparent 50%);
      background-attachment: fixed;
      color: var(--text-primary);
      min-height: 100vh;
      line-height: 1.5;
      overflow-x: hidden;
    }}

    /* Scrollbar */
    ::-webkit-scrollbar {{
      width: 8px;
      height: 8px;
    }}
    ::-webkit-scrollbar-track {{
      background: #0a0f1d;
    }}
    ::-webkit-scrollbar-thumb {{
      background: #1e293b;
      border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: #334155;
    }}

    /* Layout */
    .app-container {{
      max-width: 1680px;
      margin: 0 auto;
      padding: 20px 28px 60px;
    }}

    /* Header */
    header.dashboard-header {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      padding: 20px 28px;
      background: var(--bg-card);
      backdrop-filter: blur(16px);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-card);
      margin-bottom: 24px;
      position: sticky;
      top: 16px;
      z-index: 1000;
    }}

    .brand-section {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}

    .brand-icon {{
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: linear-gradient(135deg, #06b6d4, #3b82f6);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 15px rgba(6, 182, 212, 0.4);
      font-size: 24px;
    }}

    .brand-title-area h1 {{
      font-size: 1.45rem;
      font-weight: 700;
      letter-spacing: -0.01em;
      background: linear-gradient(90deg, #ffffff, #cbd5e1);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .brand-title-area p {{
      font-size: 0.85rem;
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .badge-live {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 2px 8px;
      border-radius: 20px;
      font-size: 0.72rem;
      font-weight: 600;
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}

    .pulse-dot {{
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #10b981;
      animation: pulse 2s infinite;
    }}

    @keyframes pulse {{
      0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
      70% {{ transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }}
      100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 9px 18px;
      border-radius: var(--radius-sm);
      font-size: 0.88rem;
      font-weight: 500;
      font-family: inherit;
      cursor: pointer;
      border: 1px solid transparent;
      transition: var(--transition);
      text-decoration: none;
    }}

    .btn-outline {{
      background: rgba(255, 255, 255, 0.05);
      border-color: var(--border-color);
      color: var(--text-primary);
    }}
    .btn-outline:hover {{
      background: rgba(255, 255, 255, 0.1);
      border-color: rgba(255, 255, 255, 0.2);
    }}

    .btn-primary {{
      background: linear-gradient(135deg, #06b6d4, #2563eb);
      color: #ffffff;
      box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);
    }}
    .btn-primary:hover {{
      opacity: 0.95;
      transform: translateY(-1px);
      box-shadow: 0 6px 16px rgba(6, 182, 212, 0.4);
    }}

    /* Navigation Tabs */
    .nav-tabs {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(15, 23, 42, 0.8);
      padding: 6px;
      border-radius: var(--radius-md);
      border: 1px solid var(--border-color);
      margin-bottom: 24px;
      overflow-x: auto;
    }}

    .nav-tab {{
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px 20px;
      border-radius: var(--radius-sm);
      color: var(--text-secondary);
      font-size: 0.9rem;
      font-weight: 500;
      cursor: pointer;
      border: none;
      background: transparent;
      transition: var(--transition);
      white-space: nowrap;
      font-family: inherit;
    }}

    .nav-tab:hover {{
      color: var(--text-primary);
      background: rgba(255, 255, 255, 0.05);
    }}

    .nav-tab.active {{
      color: #ffffff;
      background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(59, 130, 246, 0.2));
      border: 1px solid rgba(6, 182, 212, 0.4);
      box-shadow: 0 2px 10px rgba(6, 182, 212, 0.2);
      font-weight: 600;
    }}

    /* Executive KPI Grid */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 18px;
      margin-bottom: 24px;
    }}

    .kpi-card {{
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 20px 22px;
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      position: relative;
      overflow: hidden;
      box-shadow: var(--shadow-card);
      transition: var(--transition);
    }}

    .kpi-card:hover {{
      transform: translateY(-2px);
      border-color: rgba(255, 255, 255, 0.16);
      background: var(--bg-card-hover);
    }}

    .kpi-card::before {{
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, transparent, var(--kpi-accent, #06b6d4), transparent);
    }}

    .kpi-info {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .kpi-label {{
      font-size: 0.82rem;
      font-weight: 500;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .kpi-value {{
      font-size: 1.85rem;
      font-weight: 700;
      color: #ffffff;
      font-family: 'Plus Jakarta Sans', 'Prompt', sans-serif;
      line-height: 1.2;
    }}

    .kpi-desc {{
      font-size: 0.78rem;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 6px;
      margin-top: 4px;
    }}

    .kpi-badge {{
      display: inline-flex;
      align-items: center;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 0.72rem;
      font-weight: 600;
    }}

    .kpi-icon-box {{
      width: 46px;
      height: 46px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
      flex-shrink: 0;
      background: var(--icon-bg, rgba(6, 182, 212, 0.1));
      color: var(--icon-color, #06b6d4);
      border: 1px solid var(--icon-border, rgba(6, 182, 212, 0.2));
    }}

    /* Tab Panes */
    .tab-content {{
      display: none;
      animation: fadeIn 0.3s ease-in-out;
    }}

    .tab-content.active {{
      display: block;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(6px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* Dashboard Grid System */
    .grid-2 {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 20px;
      margin-bottom: 24px;
    }}

    .grid-3 {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      margin-bottom: 24px;
    }}

    .grid-2-1 {{
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 20px;
      margin-bottom: 24px;
    }}

    .grid-1-2 {{
      display: grid;
      grid-template-columns: 1fr 2fr;
      gap: 20px;
      margin-bottom: 24px;
    }}

    @media (max-width: 1180px) {{
      .grid-2, .grid-3, .grid-2-1, .grid-1-2 {{
        grid-template-columns: 1fr;
      }}
    }}

    /* Dashboard Cards */
    .dashboard-card {{
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-card);
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}

    .card-header {{
      padding: 16px 20px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      background: rgba(15, 23, 42, 0.4);
    }}

    .card-title-group {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .card-title-group h3 {{
      font-size: 1.05rem;
      font-weight: 600;
      color: #f8fafc;
    }}

    .card-title-group span.subtitle {{
      font-size: 0.8rem;
      color: var(--text-secondary);
      font-weight: 400;
    }}

    .card-tools {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .card-body {{
      padding: 20px;
      flex: 1;
      position: relative;
    }}

    /* Filter Controls inside cards */
    .pill-btn-group {{
      display: inline-flex;
      background: rgba(15, 23, 42, 0.6);
      padding: 3px;
      border-radius: 6px;
      border: 1px solid var(--border-color);
    }}

    .pill-btn {{
      padding: 4px 12px;
      border-radius: 4px;
      border: none;
      background: transparent;
      color: var(--text-secondary);
      font-size: 0.78rem;
      font-weight: 500;
      cursor: pointer;
      transition: var(--transition);
      font-family: inherit;
    }}

    .pill-btn.active {{
      background: var(--accent-cyan);
      color: #04101e;
      font-weight: 700;
    }}

    /* Charts Container */
    .chart-container {{
      position: relative;
      width: 100%;
      height: 330px;
    }}

    .chart-container-sm {{
      position: relative;
      width: 100%;
      height: 250px;
    }}

    /* Interactive Leaflet Map */
    #traffic-map {{
      width: 100%;
      height: 480px;
      border-radius: var(--radius-sm);
      z-index: 10;
    }}

    .map-legend {{
      position: absolute;
      bottom: 25px;
      right: 25px;
      background: rgba(15, 23, 42, 0.9);
      backdrop-filter: blur(8px);
      padding: 10px 14px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-color);
      z-index: 999;
      font-size: 0.78rem;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .legend-item {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .legend-color {{
      width: 12px;
      height: 12px;
      border-radius: 50%;
    }}

    /* Tables */
    .table-responsive {{
      overflow-x: auto;
      max-height: 460px;
    }}

    table.data-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
      text-align: left;
    }}

    table.data-table th {{
      background: rgba(15, 23, 42, 0.8);
      color: var(--text-secondary);
      padding: 12px 14px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      border-bottom: 1px solid var(--border-color);
      position: sticky;
      top: 0;
      z-index: 5;
    }}

    table.data-table td {{
      padding: 11px 14px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      color: #e2e8f0;
    }}

    table.data-table tr:hover td {{
      background: rgba(255, 255, 255, 0.03);
    }}

    .rank-badge {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 24px;
      height: 24px;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 700;
    }}

    .rank-1 {{ background: #ffd700; color: #1a1a1a; }}
    .rank-2 {{ background: #c0c0c0; color: #1a1a1a; }}
    .rank-3 {{ background: #cd7f32; color: #ffffff; }}
    .rank-default {{ background: rgba(255, 255, 255, 0.1); color: var(--text-secondary); }}

    /* Status Tags */
    .status-tag {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 3px 8px;
      border-radius: 20px;
      font-size: 0.72rem;
      font-weight: 600;
    }}

    .status-fluid {{
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}

    .status-moderate {{
      background: rgba(245, 158, 11, 0.15);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.3);
    }}

    .status-congested {{
      background: rgba(244, 63, 94, 0.15);
      color: #fb7185;
      border: 1px solid rgba(244, 63, 94, 0.3);
    }}

    /* Progress bar in table */
    .bar-wrapper {{
      display: flex;
      align-items: center;
      gap: 8px;
      width: 100%;
    }}

    .bar-bg {{
      flex: 1;
      height: 6px;
      background: rgba(255, 255, 255, 0.08);
      border-radius: 3px;
      overflow: hidden;
    }}

    .bar-fill {{
      height: 100%;
      border-radius: 3px;
      transition: width 0.4s ease;
    }}

    /* Travel Mode Comparison Cards */
    .mode-cards-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      margin-bottom: 24px;
    }}

    @media (max-width: 980px) {{
      .mode-cards-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .mode-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      position: relative;
      box-shadow: var(--shadow-card);
    }}

    .mode-card.featured {{
      border-color: rgba(6, 182, 212, 0.4);
      background: linear-gradient(180deg, rgba(6, 182, 212, 0.08) 0%, rgba(18, 26, 47, 0.75) 100%);
    }}

    .mode-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .mode-title {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .mode-icon {{
      width: 44px;
      height: 44px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
    }}

    .mode-metrics {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      background: rgba(15, 23, 42, 0.5);
      padding: 14px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-color);
    }}

    .mode-metric-item {{
      display: flex;
      flex-direction: column;
    }}

    .mode-metric-item .label {{
      font-size: 0.74rem;
      color: var(--text-secondary);
    }}

    .mode-metric-item .value {{
      font-size: 1.25rem;
      font-weight: 700;
      color: #ffffff;
      font-family: 'Plus Jakarta Sans', sans-serif;
    }}

    /* Filter Toolbar */
    .filter-toolbar {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 16px 20px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      margin-bottom: 20px;
    }}

    .filter-inputs {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 12px;
      flex: 1;
    }}

    .search-box {{
      position: relative;
      min-width: 280px;
      flex: 1;
    }}

    .search-box input {{
      width: 100%;
      padding: 9px 14px 9px 38px;
      border-radius: var(--radius-sm);
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid var(--border-color);
      color: #ffffff;
      font-size: 0.88rem;
      font-family: inherit;
      outline: none;
      transition: var(--transition);
    }}

    .search-box input:focus {{
      border-color: var(--accent-cyan);
      box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.15);
    }}

    .search-box .search-icon {{
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      font-size: 15px;
    }}

    .select-dropdown {{
      padding: 9px 14px;
      border-radius: var(--radius-sm);
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      font-size: 0.86rem;
      font-family: inherit;
      outline: none;
      cursor: pointer;
      transition: var(--transition);
    }}

    .select-dropdown:focus {{
      border-color: var(--accent-cyan);
    }}

    /* Commuter Calculator */
    .calc-card {{
      background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.7));
      border: 1px solid rgba(6, 182, 212, 0.3);
      border-radius: var(--radius-md);
      padding: 24px;
      margin-top: 20px;
    }}

    .calc-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-top: 16px;
    }}

    .calc-input-group {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .calc-input-group label {{
      font-size: 0.82rem;
      color: var(--text-secondary);
      font-weight: 500;
    }}

    .calc-input-group input, .calc-input-group select {{
      padding: 10px 14px;
      border-radius: var(--radius-sm);
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid var(--border-color);
      color: #ffffff;
      font-family: inherit;
      outline: none;
    }}

    .calc-results {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
      margin-top: 18px;
      padding-top: 18px;
      border-top: 1px solid var(--border-color);
    }}

    @media (max-width: 768px) {{
      .calc-results {{
        grid-template-columns: 1fr;
      }}
    }}

    .calc-result-box {{
      background: rgba(15, 23, 42, 0.6);
      padding: 14px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-color);
      text-align: center;
    }}

    .calc-result-box .val {{
      font-size: 1.4rem;
      font-weight: 700;
      color: var(--accent-cyan);
      font-family: 'Plus Jakarta Sans', sans-serif;
    }}

    /* Pagination */
    .pagination-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 14px 20px;
      border-top: 1px solid var(--border-color);
      font-size: 0.84rem;
      color: var(--text-secondary);
    }}

    .pagination-buttons {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .page-btn {{
      padding: 6px 12px;
      border-radius: 4px;
      border: 1px solid var(--border-color);
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-primary);
      cursor: pointer;
      font-family: inherit;
      font-size: 0.8rem;
    }}

    .page-btn:disabled {{
      opacity: 0.4;
      cursor: not-allowed;
    }}

    .page-btn.active {{
      background: var(--accent-cyan);
      color: #04101e;
      font-weight: 700;
      border-color: var(--accent-cyan);
    }}

    /* Footer */
    footer.dashboard-footer {{
      margin-top: 40px;
      padding: 24px;
      text-align: center;
      border-top: 1px solid var(--border-color);
      color: var(--text-muted);
      font-size: 0.82rem;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    /* Custom Leaflet popup */
    .leaflet-popup-content-wrapper {{
      background: #0f172a !important;
      color: #f8fafc !important;
      border: 1px solid rgba(6, 182, 212, 0.4) !important;
      border-radius: 12px !important;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6) !important;
    }}
    .leaflet-popup-tip {{
      background: #0f172a !important;
    }}
    .custom-popup h4 {{
      font-size: 0.95rem;
      margin-bottom: 6px;
      color: #38bdf8;
    }}
    .custom-popup p {{
      font-size: 0.8rem;
      margin-bottom: 4px;
      color: #cbd5e1;
    }}

    /* Responsive adjustments */
    @media (max-width: 768px) {{
      .app-container {{
        padding: 12px 14px 40px;
      }}
      header.dashboard-header {{
        padding: 16px;
        flex-direction: column;
        align-items: flex-start;
      }}
      .header-actions {{
        width: 100%;
        justify-content: flex-end;
      }}
    }}
  
    /* Prominent Global Search Bar in Header */
    .header-search-container {
      position: relative;
      flex: 1;
      max-width: 520px;
      min-width: 280px;
      margin: 0 16px;
    }

    .global-search-box {
      position: relative;
      display: flex;
      align-items: center;
      width: 100%;
    }

    .global-search-input {
      width: 100%;
      height: 44px;
      padding: 0 46px 0 44px;
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 28px;
      color: #f8fafc;
      font-size: 0.92rem;
      font-family: inherit;
      outline: none;
      transition: var(--transition);
      box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
    }

    .global-search-input:focus {
      border-color: var(--accent-cyan);
      background: rgba(15, 23, 42, 0.98);
      box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.3), 0 4px 15px rgba(6, 182, 212, 0.2);
    }

    .global-search-icon {
      position: absolute;
      left: 15px;
      color: var(--accent-cyan);
      pointer-events: none;
      display: flex;
      align-items: center;
    }

    .global-search-clear {
      position: absolute;
      right: 40px;
      background: rgba(255, 255, 255, 0.1);
      border: none;
      color: #94a3b8;
      width: 22px;
      height: 22px;
      border-radius: 50%;
      display: none;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 13px;
      transition: var(--transition);
    }

    .global-search-clear:hover {
      background: rgba(244, 63, 94, 0.4);
      color: #fff;
    }

    .global-search-kbd {
      position: absolute;
      right: 12px;
      padding: 3px 7px;
      border-radius: 6px;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: #94a3b8;
      font-size: 0.72rem;
      font-family: monospace;
      pointer-events: none;
    }

    /* Live Search Results Dropdown */
    .search-results-dropdown {
      position: absolute;
      top: calc(100% + 10px);
      left: 0;
      right: 0;
      background: rgba(15, 23, 42, 0.97);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(6, 182, 212, 0.35);
      border-radius: var(--radius-md);
      box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.8), 0 0 25px rgba(6, 182, 212, 0.2);
      max-height: 480px;
      overflow-y: auto;
      z-index: 2500;
      display: none;
      animation: fadeIn 0.2s ease;
    }

    .search-results-dropdown.show {
      display: block;
    }

    .search-result-group {
      padding: 10px 14px 6px;
      font-size: 0.74rem;
      font-weight: 700;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      background: rgba(10, 15, 29, 0.5);
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .search-result-item {
      padding: 11px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      cursor: pointer;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      transition: var(--transition);
    }

    .search-result-item:hover, .search-result-item.selected {
      background: rgba(6, 182, 212, 0.15);
      padding-left: 20px;
    }

    .search-result-left {
      display: flex;
      align-items: center;
      gap: 10px;
      overflow: hidden;
      flex: 1;
    }

    .search-result-name {
      font-size: 0.88rem;
      font-weight: 600;
      color: #f8fafc;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .search-result-name mark {
      background: rgba(6, 182, 212, 0.35);
      color: #38bdf8;
      border-radius: 2px;
      padding: 0 2px;
    }

    .search-result-sub {
      font-size: 0.76rem;
      color: var(--text-secondary);
    }

    .search-result-badge {
      font-size: 0.72rem;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 4px;
      white-space: nowrap;
    }

    .search-dropdown-footer {
      padding: 12px 16px;
      background: rgba(10, 15, 29, 0.95);
      border-top: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.82rem;
      color: var(--accent-cyan);
      cursor: pointer;
      font-weight: 600;
      transition: var(--transition);
    }

    .search-dropdown-footer:hover {
      background: rgba(6, 182, 212, 0.2);
      color: #ffffff;
    }

  </style>
</head>
<body>

<div class="app-container">

  <!-- Header -->
  <header class="dashboard-header">
    <div class="brand-section">
      <div class="brand-icon">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.5 2.8C2.1 11.2 2 11.6 2 12v4c0 .6.4 1 1 1h2"/>
          <circle cx="7" cy="17" r="2"/>
          <path d="M9 17h6"/>
          <circle cx="17" cy="17" r="2"/>
        </svg>
      </div>
      <div class="brand-title-area">
        <h1>Bangkok Smart Mobility & Transit Dashboard</h1>
        <p>
          ระบบวิเคราะห์การเดินทาง โครงข่ายขนส่ง และสภาพการจราจร กทม.
          <span class="badge-live"><span class="pulse-dot"></span> ข้อมูลสมบูรณ์ 3 แหล่งข้อมูล (CCTV, ป้ายรถเมล์, โหมดเดินทาง)</span>
        </p>
      </div>
    </div>


    <!-- Global Search Bar in Header -->
    <div class="header-search-container">
      <div class="global-search-box">
        <span class="global-search-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
        </span>
        <input 
          type="text" 
          id="globalSearchInput" 
          class="global-search-input" 
          placeholder="🔍 ค้นหาป้ายรถเมล์, กล้อง CCTV, 50 เขต หรือชื่อถนน..." 
          autocomplete="off"
          oninput="onGlobalSearchInput()" 
          onkeydown="onGlobalSearchKeydown(event)"
          onfocus="onGlobalSearchFocus()"
        />
        <button id="globalSearchClear" class="global-search-clear" onclick="clearGlobalSearch()" title="ล้างการค้นหา">✕</button>
        <span id="globalSearchKbd" class="global-search-kbd">/</span>
      </div>
      <div id="globalSearchResults" class="search-results-dropdown">
        <!-- Live autocomplete results populated via JS -->
      </div>
    </div>


    <div class="header-actions">
      <button class="btn btn-outline" onclick="window.print()" title="พิมพ์หรือบันทึกรายงานเป็น PDF">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 6 2 18 2 18 9"></polyline>
          <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>
          <rect x="6" y="14" width="12" height="8"></rect>
        </svg>
        พิมพ์รายงาน
      </button>
      <button class="btn btn-primary" onclick="exportFilteredCSV()" title="ส่งออกข้อมูลเป็น CSV">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
        Export CSV
      </button>
    </div>
  </header>

  <!-- Navigation Tabs -->
  <nav class="nav-tabs" role="tablist">
    <button class="nav-tab active" onclick="switchTab('overview')">
      <span>🌟</span> ภาพรวมผู้บริหาร (Overview)
    </button>
    <button class="nav-tab" onclick="switchTab('traffic')">
      <span>🚦</span> วิเคราะห์สภาพจราจร & CCTV (Traffic)
    </button>
    <button class="nav-tab" onclick="switchTab('bus')">
      <span>🚌</span> โครงข่ายป้ายรถเมล์ (Bus Network)
    </button>
    <button class="nav-tab" onclick="switchTab('transit')">
      <span>⏱️</span> เปรียบเทียบต้นทุน & เวลา (Modes)
    </button>
    <button class="nav-tab" onclick="switchTab('explorer')">
      <span>🔍</span> ค้นหาและกรองข้อมูล (Data Explorer)
    </button>
  </nav>

  <!-- Executive KPI Grid (Always visible for quick high-level view) -->
  <div class="kpi-grid">
    <div class="kpi-card" style="--kpi-accent: #06b6d4;">
      <div class="kpi-info">
        <span class="kpi-label">จุดตรวจวัด CCTV จราจร</span>
        <span class="kpi-value" id="kpi-cctv-cameras">176 จุด</span>
        <span class="kpi-desc">
          <span class="kpi-badge" style="background:rgba(6,182,212,0.2);color:#38bdf8;">15,774 รายการ</span>
          ครอบคลุม DOH, BMA, EXAT
        </span>
      </div>
      <div class="kpi-icon-box" style="--icon-bg: rgba(6, 182, 212, 0.12); --icon-color: #06b6d4; --icon-border: rgba(6, 182, 212, 0.3);">
        📹
      </div>
    </div>

    <div class="kpi-card" style="--kpi-accent: #10b981;">
      <div class="kpi-info">
        <span class="kpi-label">ความเร็วเฉลี่ยบนท้องถนน</span>
        <span class="kpi-value" id="kpi-avg-speed">41.9 <small style="font-size:0.9rem;font-weight:400;color:var(--text-secondary);">กม./ชม.</small></span>
        <span class="kpi-desc">
          <span class="kpi-badge" style="background:rgba(16,185,129,0.2);color:#34d399;">V/C เฉลี่ย 0.73</span>
          ความจุยังรองรับได้
        </span>
      </div>
      <div class="kpi-icon-box" style="--icon-bg: rgba(16, 185, 129, 0.12); --icon-color: #10b981; --icon-border: rgba(16, 185, 129, 0.3);">
        ⚡
      </div>
    </div>

    <div class="kpi-card" style="--kpi-accent: #3b82f6;">
      <div class="kpi-info">
        <span class="kpi-label">เครือข่ายป้ายรถเมล์</span>
        <span class="kpi-value" id="kpi-bus-stops">4,201 <small style="font-size:0.9rem;font-weight:400;color:var(--text-secondary);">ป้าย</small></span>
        <span class="kpi-desc">
          <span class="kpi-badge" style="background:rgba(59,130,246,0.2);color:#60a5fa;">50 เขต กทม.</span>
          78,644 ข้อมูลการวิเคราะห์
        </span>
      </div>
      <div class="kpi-icon-box" style="--icon-bg: rgba(59, 130, 246, 0.12); --icon-color: #3b82f6; --icon-border: rgba(59, 130, 246, 0.3);">
        🚏
      </div>
    </div>

    <div class="kpi-card" style="--kpi-accent: #f59e0b;">
      <div class="kpi-info">
        <span class="kpi-label">ยอดจอดรับ-ส่ง (วันธรรมดา)</span>
        <span class="kpi-value" id="kpi-bus-vol">1.07 <small style="font-size:0.9rem;font-weight:400;color:var(--text-secondary);">ล้านครั้ง</small></span>
        <span class="kpi-desc">
          <span class="kpi-badge" style="background:rgba(245,158,11,0.2);color:#fbbf24;">+6.5% vs วันหยุด</span>
          (วันหยุด 1.01 ล้านครั้ง)
        </span>
      </div>
      <div class="kpi-icon-box" style="--icon-bg: rgba(245, 158, 11, 0.12); --icon-color: #f59e0b; --icon-border: rgba(245, 158, 11, 0.3);">
        🚌
      </div>
    </div>

    <div class="kpi-card" style="--kpi-accent: #8b5cf6;">
      <div class="kpi-info">
        <span class="kpi-label">ความเร็ว vs ประหยัดที่สุด</span>
        <span class="kpi-value">BTS 40 น. <span style="font-size:1rem;color:var(--text-secondary);">/ เมล์ 24 บ.</span></span>
        <span class="kpi-desc">
          <span class="kpi-badge" style="background:rgba(139,92,246,0.2);color:#c084fc;">3 ระบบหลัก</span>
          รถเมล์, เรือด่วน, รถไฟฟ้า
        </span>
      </div>
      <div class="kpi-icon-box" style="--icon-bg: rgba(139, 92, 246, 0.12); --icon-color: #8b5cf6; --icon-border: rgba(139, 92, 246, 0.3);">
        🚆
      </div>
    </div>
  </div>

  <!-- TAB 1: OVERVIEW -->
  <div id="tab-overview" class="tab-content active">
    <!-- Row 1: Executive Insights Cards -->
    <div class="grid-3">
      <div class="dashboard-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3>🔴 จุดคอขวดจราจรสูงสุด (Bottlenecks)</h3>
          </div>
          <span class="badge-live" style="background:rgba(244,63,94,0.15);color:#fb7185;border-color:rgba(244,63,94,0.3);">Top V/C Ratio</span>
        </div>
        <div class="card-body" id="overview-bottlenecks" style="display:flex;flex-direction:column;gap:12px;">
          <!-- Injected via JS -->
        </div>
      </div>

      <div class="dashboard-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3>🚏 ป้ายรถเมล์ผู้โดยสารหนาแน่นสุด</h3>
          </div>
          <span class="badge-live" style="background:rgba(59,130,246,0.15);color:#60a5fa;border-color:rgba(59,130,246,0.3);">Top Transit</span>
        </div>
        <div class="card-body" id="overview-busstops" style="display:flex;flex-direction:column;gap:12px;">
          <!-- Injected via JS -->
        </div>
      </div>

      <div class="dashboard-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3>📊 สัดส่วนความคล่องตัวการจราจร กทม.</h3>
          </div>
        </div>
        <div class="card-body" style="display:flex;flex-direction:column;align-items:center;justify-content:center;">
          <div style="width:200px;height:200px;position:relative;">
            <canvas id="overviewTrafficStatusChart"></canvas>
          </div>
          <div style="display:flex;gap:14px;margin-top:16px;font-size:0.8rem;">
            <span style="color:#10b981;">● คล่องตัว (&lt;0.7)</span>
            <span style="color:#f59e0b;">● ชะลอตัว (0.7-1.0)</span>
            <span style="color:#f43f5e;">● ติดขัด (&gt;1.0)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Row 2: 24h Profile & District Volume -->
    <div class="grid-2">
      <div class="dashboard-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3>⏱️ พฤติกรรมความเร็วและปริมาณรถ 24 ชั่วโมง</h3>
            <span class="subtitle">วันธรรมดา vs วันหยุด</span>
          </div>
          <div class="pill-btn-group">
            <button class="pill-btn active" onclick="setOverviewTrafficMode('speed')">ความเร็ว (Speed)</button>
            <button class="pill-btn" onclick="setOverviewTrafficMode('volume')">ปริมาณรถ (Volume)</button>
            <button class="pill-btn" onclick="setOverviewTrafficMode('vc')">V/C Ratio</button>
          </div>
        </div>
        <div class="card-body">
          <div class="chart-container">
            <canvas id="overviewHourlyChart"></canvas>
          </div>
        </div>
      </div>

      <div class="dashboard-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3>🏙️ Top 10 เขตที่มีปริมาณการจอดรับ-ส่งสูงสุด</h3>
            <span class="subtitle">เปรียบเทียบวันธรรมดาและวันหยุด</span>
          </div>
        </div>
        <div class="card-body">
          <div class="chart-container">
            <canvas id="overviewDistrictsChart"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- TAB 2: TRAFFIC & CCTV -->
  <div id="tab-traffic" class="tab-content">
    <!-- Map & Summary -->
    <div class="grid-2-1">
      <div class="dashboard-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3>🗺️ แผนที่พิกัดกล้อง CCTV และสถานะจราจรอัจฉริยะ (176 จุด)</h3>
            <span class="subtitle">คลิกที่มาร์กเกอร์เพื่อดูสถิติเชิงลึก</span>
          </div>
          <div class="card-tools">
            <select id="mapOrgFilter" class="select-dropdown" onchange="filterMapPoints()" style="padding:4px 10px;font-size:0.8rem;">
              <option value="ALL">ทุกหน่วยงาน (DOH, BMA, EXAT)</option>
              <option value="DOH">กรมทางหลวง (DOH)</option>
              <option value="BMA">กรุงเทพมหานคร (BMA)</option>
              <option value="EXAT">การทางพิเศษ (EXAT)</option>
            </select>
          </div>
        </div>
        <div class="card-body" style="padding:10px;position:relative;">
          <div id="traffic-map"></div>
          <div class="map-legend">
            <div class="legend-item"><div class="legend-color" style="background:#10b981;"></div> คล่องตัว (V/C &lt; 0.7)</div>
            <div class="legend-item"><div class="legend-color" style="background:#f59e0b;"></div> เริ่มชะลอตัว (0.7 - 1.0)</div>
            <div class="legend-item"><div class="legend-color" style="background:#ef4444;"></div> ติดขัดหนาแน่น (V/C &gt; 1.0)</div>
          </div>
        </div>
      </div>

      <div class="dashboard-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3>📊 สถิติตามหน่วยงานผู้ดูแล</h3>
            <span class="subtitle">DOH vs BMA vs EXAT</span>
          </div>
        </div>
        <div class="card-body">
          <div class="chart-container-sm" style="height:200px;">
            <canvas id="trafficAgencyChart"></canvas>
          </div>
          <div id="trafficAgencyStats" style="margin-top:16px;display:flex;flex-direction:column;gap:8px;font-size:0.82rem;">
            <!-- Render agency breakdown stats -->
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row: Speed Distribution & Bottlenecks -->
    <div class="grid-2">
      <div class="dashboard-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3>⚡ การกระจายตัวของระดับความเร็ว (Speed Distribution)</h3>
            <span class="subtitle">จำนวนจุดตรวจวัดตามช่วงความเร็ว</span>
          </div>
        </div>
        <div class="card-body">
          <div class="chart-container">
            <canvas id="speedDistChart"></canvas>
          </div>
        </div>
      </div>

      <div class="dashboard-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3>🚦 10 จุดที่พบค่าวิกฤตความจุสูงสุด (Peak Congestion / V/C)</h3>
            <span class="subtitle">อัตราส่วนปริมาณต่อความจุสูงสุด</span>
          </div>
        </div>
        <div class="card-body" style="padding:0;">
          <div class="table-responsive" style="max-height:330px;">
            <table class="data-table">
              <thead>
                <tr>
                  <th style="width:40px;">#</th>
                  <th>ชื่อจุดตรวจวัด / ถนน</th>
                  <th>หน่วยงาน</th>
                  <th>ความเร็วเฉลี่ย</th>
                  <th>Peak V/C</th>
                  <th>สถานะ</th>
                </tr>
              </thead>
              <tbody id="topCongestedTable">
                <!-- Render top congested -->
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- TAB 3: BUS NETWORK -->
  <div id="tab-bus" class="tab-content">
    <div class="grid-2">
      <div class="dashboard-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3>🚌 Top 15 เขตที่มีปริมาณการจอดรับ-ส่งผู้โดยสารสูงสุด</h3>
            <span class="subtitle">วันทำงานปกติ (Weekday Stops)</span>
          </div>
        </div>
        <div class="card-body">
          <div class="chart-container">
            <canvas id="busDistrictsTopChart"></canvas>
          </div>
        </div>
      </div>

      <div class="dashboard-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3>🔄 สัดส่วนผู้โดยสารขึ้น (Pickup) vs ผู้โดยสารลง (Dropoff)</h3>
            <span class="subtitle">10 เขตที่มีปริมาณสูงสุด</span>
          </div>
        </div>
        <div class="card-body">
          <div class="chart-container">
            <canvas id="busPickupDropoffChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Top 25 Bus Stops Leaderboard -->
    <div class="dashboard-card">
      <div class="card-header">
        <div class="card-title-group">
          <h3>🏆 Top 25 ป้ายรถเมล์ที่มีการใช้งานสูงสุดในกรุงเทพมหานคร</h3>
          <span class="subtitle">ยอดรวมการจอดรับ-ส่งผู้โดยสารทั้งวันธรรมดาและวันหยุด</span>
        </div>
        <div class="card-tools">
          <input type="text" id="busLeaderboardFilter" placeholder="กรองชื่อป้ายหรือเขต..." oninput="filterBusLeaderboard()" class="select-dropdown" style="padding:6px 12px;font-size:0.82rem;min-width:200px;" />
        </div>
      </div>
      <div class="card-body" style="padding:0;">
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th style="width:50px;">อันดับ</th>
                <th>ชื่อป้ายหยุดรถโดยสาร</th>
                <th>เขต / พื้นที่</th>
                <th>ขึ้น (Pickup)</th>
                <th>ลง (Dropoff)</th>
                <th>วันทำงาน (WD)</th>
                <th>วันหยุด (WE)</th>
                <th style="min-width:180px;">ยอดรวมสะสม (Total)</th>
              </tr>
            </thead>
            <tbody id="top25BusStopsTable">
              <!-- Rendered via JS -->
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <!-- TAB 4: TRANSIT MODES (TIME & COST) -->
  <div id="tab-transit" class="tab-content">
    <!-- Comparative 3 Cards -->
    <div class="mode-cards-grid" id="modeCardsContainer">
      <!-- Rendered via JS -->
    </div>

    <!-- Charts Breakdown -->
    <div class="grid-2">
      <div class="dashboard-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3>⏱️ โครงสร้างเวลาในการเดินทาง (นาทีต่อเที่ยว)</h3>
            <span class="subtitle">เวลาในระบบหลัก (In-transit) vs เวลาเชื่อมต่อระบบย่อย (Feeder)</span>
          </div>
        </div>
        <div class="card-body">
          <div class="chart-container">
            <canvas id="modeTimeChart"></canvas>
          </div>
        </div>
      </div>

      <div class="dashboard-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3>💰 โครงสร้างค่าใช้จ่ายในการเดินทาง (บาทต่อเที่ยว)</h3>
            <span class="subtitle">ค่าโดยสารระบบหลัก vs ค่าใช้จ่ายเชื่อมต่อระบบย่อย</span>
          </div>
        </div>
        <div class="card-body">
          <div class="chart-container">
            <canvas id="modeCostChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Interactive Commuter Calculator -->
    <div class="calc-card">
      <div style="display:flex;align-items:center;gap:10px;">
        <span style="font-size:24px;">🧮</span>
        <div>
          <h3 style="font-size:1.15rem;font-weight:700;color:#ffffff;">เครื่องคำนวณและประเมินทางเลือกการเดินทางอัจฉริยะ (Commute Route Estimator)</h3>
          <p style="font-size:0.84rem;color:var(--text-secondary);">ทดลองคำนวณเปรียบเทียบเวลา ค่าใช้จ่าย และวิธีเดินทางเชื่อมต่อตามระยะทาง</p>
        </div>
      </div>

      <div class="calc-grid">
        <div class="calc-input-group">
          <label>เลือกโหมดการเดินทางหลัก</label>
          <select id="calcMode" onchange="recalculateCommute()">
            <option value="bus">รถโดยสารประจำทาง (Bus) - ประหยัดสุด</option>
            <option value="boat">เรือโดยสาร (Boat) - เลี่ยงรถติด</option>
            <option value="train" selected>รถไฟฟ้า (BTS/MRT Rail) - รวดเร็วที่สุด</option>
          </select>
        </div>

        <div class="calc-input-group">
          <label>ระยะทางโดยประมาณ (กิโลเมตร)</label>
          <input type="number" id="calcDistance" value="15" min="1" max="100" oninput="recalculateCommute()" />
        </div>

        <div class="calc-input-group">
          <label>จำนวนเที่ยวเดินทางต่อวัน</label>
          <select id="calcTrips" onchange="recalculateCommute()">
            <option value="1">1 เที่ยว (ขาเดียว)</option>
            <option value="2" selected>2 เที่ยว (ไป-กลับ)</option>
          </select>
        </div>

        <div class="calc-input-group">
          <label>จำนวนวันทำงานต่อเดือน</label>
          <input type="number" id="calcDays" value="22" min="1" max="31" oninput="recalculateCommute()" />
        </div>
      </div>

      <div class="calc-results">
        <div class="calc-result-box">
          <div style="font-size:0.8rem;color:var(--text-secondary);">เวลาเดินทางเฉลี่ยต่อเที่ยว</div>
          <div class="val" id="calcResultTime">40 นาที</div>
          <div style="font-size:0.75rem;color:var(--text-muted);margin-top:2px;" id="calcResultTimeDetail">ระบบหลัก 20 น. + เข้าออก 20 น.</div>
        </div>

        <div class="calc-result-box">
          <div style="font-size:0.8rem;color:var(--text-secondary);">ค่าใช้จ่ายเฉลี่ยต่อเที่ยว</div>
          <div class="val" id="calcResultCost" style="color:#34d399;">47.5 บาท</div>
          <div style="font-size:0.75rem;color:var(--text-muted);margin-top:2px;" id="calcResultCostDetail">ระบบหลัก 31.5 บ. + Feeder 16 บ.</div>
        </div>

        <div class="calc-result-box">
          <div style="font-size:0.8rem;color:var(--text-secondary);">ค่าใช้จ่ายประมาณการต่อเดือน</div>
          <div class="val" id="calcResultMonthly" style="color:#f59e0b;">2,090 บาท</div>
          <div style="font-size:0.75rem;color:var(--text-muted);margin-top:2px;">(เดินทาง 44 เที่ยวต่อเดือน)</div>
        </div>
      </div>
    </div>
  </div>

  <!-- TAB 5: DATA EXPLORER & ADVANCED FILTERS -->
  <div id="tab-explorer" class="tab-content">
    <div class="filter-toolbar">
      <div class="filter-inputs">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input type="text" id="explorerSearchInput" placeholder="ค้นหาชื่อป้ายรถเมล์, เขต, หรือกล้อง CCTV..." oninput="onExplorerFilterChange()" />
        </div>

        <select id="explorerTypeFilter" class="select-dropdown" onchange="onExplorerFilterChange()">
          <option value="ALL">ข้อมูลทั้งหมด (รถเมล์ + CCTV)</option>
          <option value="BUS">เฉพาะจุดจอดรถเมล์ (Bus Stops)</option>
          <option value="CCTV">เฉพาะเซนเซอร์ CCTV จราจร</option>
        </select>

        <select id="explorerDistrictFilter" class="select-dropdown" onchange="onExplorerFilterChange()">
          <option value="ALL">ทุกเขตในกรุงเทพมหานคร (50 เขต)</option>
          <!-- Dynamic districts options -->
        </select>

        <select id="explorerSortFilter" class="select-dropdown" onchange="onExplorerFilterChange()">
          <option value="VOLUME_DESC">เรียงตามปริมาณสูงสุด (Volume Desc)</option>
          <option value="VOLUME_ASC">เรียงตามปริมาณน้อยสุด (Volume Asc)</option>
          <option value="NAME_ASC">เรียงตามตัวอักษร (A-Z / ก-ฮ)</option>
        </select>
      </div>

      <div style="display:flex;align-items:center;gap:10px;">
        <span id="explorerRecordCount" style="font-size:0.85rem;color:var(--text-secondary);font-weight:500;">
          กำลังแสดง 0 รายการ
        </span>
        <button class="btn btn-outline" onclick="resetExplorerFilters()" style="padding:7px 12px;font-size:0.8rem;">
          ล้างตัวกรอง
        </button>
      </div>
    </div>

    <!-- Explorer Data Table -->
    <div class="dashboard-card">
      <div class="card-body" style="padding:0;">
        <div class="table-responsive" style="max-height:560px;">
          <table class="data-table">
            <thead>
              <tr>
                <th style="width:50px;">#</th>
                <th style="width:100px;">ประเภท</th>
                <th>ชื่อตำแหน่ง / ป้ายรถเมล์ / กล้อง CCTV</th>
                <th>พื้นที่ / เขต / หน่วยงาน</th>
                <th>ปริมาณ (วันธรรมดา / รถ)</th>
                <th>ปริมาณ (วันหยุด / ความจุ)</th>
                <th>ดัชนีชี้วัด (Total / V-C)</th>
                <th>สถานะการจราจร / การใช้งาน</th>
              </tr>
            </thead>
            <tbody id="explorerTableBody">
              <!-- Render dynamic rows -->
            </tbody>
          </table>
        </div>

        <div class="pagination-bar">
          <span id="paginationInfo">หน้าที่ 1 จาก 1</span>
          <div class="pagination-buttons">
            <button id="btnPrevPage" class="page-btn" onclick="changeExplorerPage(-1)">← ก่อนหน้า</button>
            <span id="pageNumbersContainer" style="display:flex;gap:4px;"></span>
            <button id="btnNextPage" class="page-btn" onclick="changeExplorerPage(1)">ถัดไป →</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Footer -->
  <footer class="dashboard-footer">
    <div style="font-weight:600;color:var(--text-primary);">
      Bangkok Smart Mobility & Transit Analytics Dashboard
    </div>
    <div>
      พัฒนาขึ้นจากการสังเคราะห์และบูรณาการข้อมูล 3 ชุด:
      1) เซนเซอร์กล้อง CCTV การจราจร (สำนักงานนโยบายและแผนการขนส่งและจราจร สนข. / กทม. / กรมทางหลวง / กทพ.)
      2) ผลการวิเคราะห์จุดจอดรับ-ส่งผู้โดยสารประจำทาง 50 เขต
      3) สถิติเวลาเดินทางและค่าใช้จ่ายตามรูปแบบการเดินทาง
    </div>
    <div style="color:var(--text-muted);font-size:0.75rem;">
      ไฟล์ Dashboard แบบ Standalone สามารถเปิดใช้งานแบบ Offline ได้ทันทีโดยไม่ต้องเชื่อมต่อระบบหลังบ้าน
    </div>
  </footer>

</div>

<!-- Embedded Inlined Dataset (Ensures 100% offline file:/// compatibility) -->
<script>
  const DASHBOARD_DATA = {data_json_str};

  
  // -------------------------------------------------------------
  // GLOBAL SEARCH & AUTOCOMPLETE CONTROLLER
  // -------------------------------------------------------------
  let searchSelectedIdx = -1;

  document.addEventListener('keydown', (e) => {
    // Focus search input when pressing '/' if not already inside an input/textarea
    if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
      e.preventDefault();
      const input = document.getElementById('globalSearchInput');
      if (input) {
        input.focus();
        input.select();
      }
    }
    if (e.key === 'Escape') {
      closeGlobalSearchDropdown();
      const input = document.getElementById('globalSearchInput');
      if (input) input.blur();
    }
  });

  // Close dropdown on click outside
  document.addEventListener('click', (e) => {
    const container = document.querySelector('.header-search-container');
    if (container && !container.contains(e.target)) {
      closeGlobalSearchDropdown();
    }
  });

  function onGlobalSearchFocus() {
    const input = document.getElementById('globalSearchInput');
    if (input && input.value.trim().length > 0) {
      onGlobalSearchInput();
    }
  }

  function clearGlobalSearch() {
    const input = document.getElementById('globalSearchInput');
    if (input) {
      input.value = '';
      input.focus();
    }
    document.getElementById('globalSearchClear').style.display = 'none';
    closeGlobalSearchDropdown();
  }

  function closeGlobalSearchDropdown() {
    const dropdown = document.getElementById('globalSearchResults');
    if (dropdown) dropdown.classList.remove('show');
    searchSelectedIdx = -1;
  }

  function highlightMatch(text, query) {
    if (!query) return text;
    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  }

  function onGlobalSearchInput() {
    const input = document.getElementById('globalSearchInput');
    const clearBtn = document.getElementById('globalSearchClear');
    const dropdown = document.getElementById('globalSearchResults');
    const q = (input.value || '').trim().toLowerCase();

    if (q.length > 0) {
      clearBtn.style.display = 'flex';
    } else {
      clearBtn.style.display = 'none';
      closeGlobalSearchDropdown();
      return;
    }

    const busStops = DASHBOARD_DATA.bus.searchable_stops;
    const cctvCameras = DASHBOARD_DATA.cctv.cameras;
    const districts = DASHBOARD_DATA.bus.districts;

    // Filter matches
    const matchedDistricts = districts.filter(d => d.name.toLowerCase().includes(q)).slice(0, 3);
    const matchedBus = busStops.filter(b => b.name.toLowerCase().includes(q) || b.district.toLowerCase().includes(q)).slice(0, 5);
    const matchedCCTV = cctvCameras.filter(c => c.name.toLowerCase().includes(q) || c.organization.toLowerCase().includes(q)).slice(0, 4);

    const totalMatches = matchedDistricts.length + matchedBus.length + matchedCCTV.length;

    if (totalMatches === 0) {
      dropdown.innerHTML = `
        <div style="padding:24px;text-align:center;color:var(--text-muted);font-size:0.88rem;">
          ไม่พบผลลัพธ์ที่ตรงกับ "<b>${escapeHtml(q)}</b>"<br>
          <span style="font-size:0.78rem;color:var(--text-secondary);">ลองค้นหาชื่อเขต เช่น "จตุจักร", "บางรัก" หรือชื่อป้าย เช่น "สยาม", "อนุสาวรีย์"</span>
        </div>
      `;
      dropdown.classList.add('show');
      return;
    }

    let html = '';

    // 1. Districts Section
    if (matchedDistricts.length > 0) {
      html += `<div class="search-result-group">🏙️ เขตในกรุงเทพมหานคร (${matchedDistricts.length})</div>`;
      matchedDistricts.forEach(d => {
        html += `
          <div class="search-result-item" onclick="selectGlobalResult('district', '${escapeHtml(d.name)}')">
            <div class="search-result-left">
              <span style="font-size:18px;">🏙️</span>
              <div>
                <div class="search-result-name">${highlightMatch(d.name, q)}</div>
                <div class="search-result-sub">${d.stop_count} ป้ายหยุดรถ | วันทำงาน ${formatNumber(d.total_wd)} ครั้ง</div>
              </div>
            </div>
            <span class="search-result-badge" style="background:rgba(59,130,246,0.2);color:#60a5fa;">ดูข้อมูลเขต</span>
          </div>
        `;
      });
    }

    // 2. Bus Stops Section
    if (matchedBus.length > 0) {
      html += `<div class="search-result-group">🚏 จุดจอดรับ-ส่งรถเมล์ (${matchedBus.length})</div>`;
      matchedBus.forEach(b => {
        html += `
          <div class="search-result-item" onclick="selectGlobalResult('bus', '${escapeHtml(b.name)}')">
            <div class="search-result-left">
              <span style="font-size:18px;">🚌</span>
              <div>
                <div class="search-result-name">${highlightMatch(b.name, q)}</div>
                <div class="search-result-sub">${highlightMatch(b.district, q)} | ผู้โดยสารสะสม ${formatNumber(b.grand_total)} ครั้ง</div>
              </div>
            </div>
            <span class="search-result-badge" style="background:rgba(16,185,129,0.2);color:#34d399;">ป้ายรถเมล์</span>
          </div>
        `;
      });
    }

    // 3. CCTV Cameras Section
    if (matchedCCTV.length > 0) {
      html += `<div class="search-result-group">📹 เซนเซอร์กล้อง CCTV จราจร (${matchedCCTV.length})</div>`;
      matchedCCTV.forEach(c => {
        const statusColor = c.avg_vc > 1.0 ? '#fb7185' : (c.avg_vc >= 0.7 ? '#fbbf24' : '#34d399');
        html += `
          <div class="search-result-item" onclick="selectGlobalResult('cctv', ${c.id})">
            <div class="search-result-left">
              <span style="font-size:18px;">📹</span>
              <div>
                <div class="search-result-name">${highlightMatch(c.name, q)}</div>
                <div class="search-result-sub">หน่วยงาน ${c.organization} | ความเร็ว ${c.avg_speed} กม./ชม. | V/C ${c.avg_vc}</div>
              </div>
            </div>
            <span class="search-result-badge" style="background:rgba(6,182,212,0.2);color:${statusColor};">${c.status}</span>
          </div>
        `;
      });
    }

    // Footer: View all in Data Explorer
    html += `
      <div class="search-dropdown-footer" onclick="goToExplorerSearch('${escapeHtml(q)}')">
        <span>🔍 ดูผลการค้นหาทั้งหมดใน Data Explorer &rarr;</span>
        <span style="font-size:0.74rem;color:#94a3b8;">กด Enter</span>
      </div>
    `;

    dropdown.innerHTML = html;
    dropdown.classList.add('show');
    searchSelectedIdx = -1;
  }

  function escapeHtml(text) {
    if (!text) return '';
    return text.toString()
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function onGlobalSearchKeydown(e) {
    const dropdown = document.getElementById('globalSearchResults');
    if (!dropdown || !dropdown.classList.contains('show')) {
      if (e.key === 'Enter') {
        goToExplorerSearch(document.getElementById('globalSearchInput').value.trim());
      }
      return;
    }

    const items = dropdown.querySelectorAll('.search-result-item');
    if (items.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      searchSelectedIdx = (searchSelectedIdx + 1) % items.length;
      updateSearchSelection(items);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      searchSelectedIdx = (searchSelectedIdx - 1 + items.length) % items.length;
      updateSearchSelection(items);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (searchSelectedIdx >= 0 && searchSelectedIdx < items.length) {
        items[searchSelectedIdx].click();
      } else {
        goToExplorerSearch(document.getElementById('globalSearchInput').value.trim());
      }
    }
  }

  function updateSearchSelection(items) {
    items.forEach((it, idx) => {
      if (idx === searchSelectedIdx) {
        it.classList.add('selected');
        it.scrollIntoView({ block: 'nearest' });
      } else {
        it.classList.remove('selected');
      }
    });
  }

  function selectGlobalResult(type, val) {
    closeGlobalSearchDropdown();
    
    if (type === 'bus') {
      switchTab('explorer');
      const searchBox = document.getElementById('explorerSearchInput');
      const typeFilter = document.getElementById('explorerTypeFilter');
      if (searchBox) searchBox.value = val;
      if (typeFilter) typeFilter.value = 'BUS';
      onExplorerFilterChange();
      window.scrollTo({ top: 350, behavior: 'smooth' });
    } else if (type === 'district') {
      switchTab('bus');
      window.scrollTo({ top: 250, behavior: 'smooth' });
    } else if (type === 'cctv') {
      switchTab('traffic');
      const cam = DASHBOARD_DATA.cctv.cameras.find(c => c.id === val);
      if (cam && AppState.map) {
        AppState.map.setView([cam.lat, cam.lng], 15);
        // Find and open popup
        AppState.mapMarkers.forEach(m => {
          const latLng = m.getLatLng();
          if (Math.abs(latLng.lat - cam.lat) < 0.0001 && Math.abs(latLng.lng - cam.lng) < 0.0001) {
            m.openPopup();
          }
        });
        window.scrollTo({ top: 300, behavior: 'smooth' });
      }
    }
  }

  function goToExplorerSearch(q) {
    closeGlobalSearchDropdown();
    switchTab('explorer');
    const searchBox = document.getElementById('explorerSearchInput');
    const typeFilter = document.getElementById('explorerTypeFilter');
    if (searchBox) searchBox.value = q;
    if (typeFilter) typeFilter.value = 'ALL';
    onExplorerFilterChange();
    window.scrollTo({ top: 350, behavior: 'smooth' });
  }

  // Global App State
  const AppState = {{
    currentTab: 'overview',
    overviewTrafficMetric: 'speed',
    explorerPage: 1,
    explorerPageSize: 15,
    explorerFilteredData: [],
    charts: {{}},
    map: null,
    mapMarkers: []
  }};

  // Helper formatting functions
  function formatNumber(num) {{
    return new Intl.NumberFormat('th-TH').format(num);
  }}

  function switchTab(tabId) {{
    AppState.currentTab = tabId;
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

    const tabButtons = document.querySelectorAll('.nav-tab');
    const tabs = ['overview', 'traffic', 'bus', 'transit', 'explorer'];
    const idx = tabs.indexOf(tabId);
    if (idx !== -1 && tabButtons[idx]) {{
      tabButtons[idx].classList.add('active');
    }}

    const target = document.getElementById('tab-' + tabId);
    if (target) {{
      target.classList.add('active');
    }}

    // Invalidate map size if opening traffic tab
    if (tabId === 'traffic' && AppState.map) {{
      setTimeout(() => {{
        AppState.map.invalidateSize();
      }}, 200);
    }}
  }}

  // -------------------------------------------------------------
  // INITIALIZE DASHBOARD COMPONENTS
  // -------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', () => {{
    initOverviewTab();
    initTrafficTab();
    initBusTab();
    initTransitTab();
    initExplorerTab();
    recalculateCommute();
  }});

  // 1. OVERVIEW TAB
  function initOverviewTab() {{
    const cctv = DASHBOARD_DATA.cctv;
    const bus = DASHBOARD_DATA.bus;

    // Bottlenecks widget
    const bottlenecksEl = document.getElementById('overview-bottlenecks');
    bottlenecksEl.innerHTML = '';
    cctv.top_congested.slice(0, 3).forEach((item, i) => {{
      const div = document.createElement('div');
      div.style.cssText = 'background:rgba(15,23,42,0.5);padding:10px 12px;border-radius:8px;border:1px solid rgba(244,63,94,0.2);display:flex;align-items:center;justify-content:space-between;gap:8px;';
      div.innerHTML = `
        <div style="display:flex;align-items:center;gap:10px;">
          <span class="rank-badge rank-1" style="background:#f43f5e;color:#fff;">${{i+1}}</span>
          <div>
            <div style="font-weight:600;font-size:0.85rem;color:#f8fafc;max-width:240px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="${{item.name}}">${{item.name}}</div>
            <div style="font-size:0.75rem;color:var(--text-secondary);">ความเร็ว: ${{item.avg_speed}} กม./ชม. | หน่วยงาน: ${{item.organization}}</div>
          </div>
        </div>
        <div style="text-align:right;">
          <div style="font-weight:700;color:#fb7185;font-size:0.95rem;">V/C ${{item.avg_vc}}</div>
          <div style="font-size:0.72rem;color:var(--text-muted);">${{item.status}}</div>
        </div>
      `;
      bottlenecksEl.appendChild(div);
    }});

    // Busiest Bus Stops widget
    const busStopsEl = document.getElementById('overview-busstops');
    busStopsEl.innerHTML = '';
    bus.top_25_stops.slice(0, 3).forEach((item, i) => {{
      const div = document.createElement('div');
      div.style.cssText = 'background:rgba(15,23,42,0.5);padding:10px 12px;border-radius:8px;border:1px solid rgba(59,130,246,0.2);display:flex;align-items:center;justify-content:space-between;gap:8px;';
      div.innerHTML = `
        <div style="display:flex;align-items:center;gap:10px;">
          <span class="rank-badge rank-1" style="background:#3b82f6;color:#fff;">${{i+1}}</span>
          <div>
            <div style="font-weight:600;font-size:0.85rem;color:#f8fafc;max-width:240px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="${{item.bus_stop}}">${{item.bus_stop}}</div>
            <div style="font-size:0.75rem;color:var(--text-secondary);">${{item.district}}</div>
          </div>
        </div>
        <div style="text-align:right;">
          <div style="font-weight:700;color:#60a5fa;font-size:0.95rem;">${{formatNumber(item.grand_total)}}</div>
          <div style="font-size:0.72rem;color:var(--text-muted);">ครั้งสะสม</div>
        </div>
      `;
      busStopsEl.appendChild(div);
    }});

    // Donut chart: Traffic Status
    let fluidCount = 0, moderateCount = 0, congestedCount = 0;
    cctv.cameras.forEach(c => {{
      if (c.avg_vc < 0.7) fluidCount++;
      else if (c.avg_vc < 1.0) moderateCount++;
      else congestedCount++;
    }});

    const ctxStatus = document.getElementById('overviewTrafficStatusChart').getContext('2d');
    AppState.charts.overviewStatus = new Chart(ctxStatus, {{
      type: 'doughnut',
      data: {{
        labels: ['คล่องตัว', 'เริ่มชะลอตัว', 'หนาแน่น/ติดขัด'],
        datasets: [{{
          data: [fluidCount, moderateCount, congestedCount],
          backgroundColor: ['#10b981', '#f59e0b', '#f43f5e'],
          borderWidth: 0,
          hoverOffset: 6
        }}]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{
            callbacks: {{
              label: (ctx) => ` ${{ctx.label}}: ${{ctx.raw}} จุด (${{Math.round(ctx.raw / cctv.cameras.length * 100)}}%)`
            }}
          }}
        }}
      }}
    }});

    // Hourly traffic line chart
    const ctxHourly = document.getElementById('overviewHourlyChart').getContext('2d');
    AppState.charts.overviewHourly = new Chart(ctxHourly, {{
      type: 'line',
      data: {{
        labels: cctv.hourly.labels,
        datasets: [
          {{
            label: 'วันทำงาน (Working Day)',
            data: cctv.hourly.working.speed,
            borderColor: '#06b6d4',
            backgroundColor: 'rgba(6, 182, 212, 0.1)',
            fill: true,
            tension: 0.35,
            borderWidth: 2.5,
            pointRadius: 2,
            pointHoverRadius: 6
          }},
          {{
            label: 'วันหยุด (Holiday/Weekend)',
            data: cctv.hourly.holiday.speed,
            borderColor: '#8b5cf6',
            backgroundColor: 'rgba(139, 92, 246, 0.05)',
            fill: true,
            borderDash: [5, 5],
            tension: 0.35,
            borderWidth: 2,
            pointRadius: 2,
            pointHoverRadius: 6
          }}
        ]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        scales: {{
          x: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }} }},
          y: {{
            grid: {{ color: 'rgba(255,255,255,0.05)' }},
            ticks: {{ color: '#94a3b8' }},
            title: {{ display: true, text: 'ความเร็วเฉลี่ย (กม./ชม.)', color: '#94a3b8' }}
          }}
        }},
        plugins: {{
          legend: {{ labels: {{ color: '#cbd5e1' }} }}
        }}
      }}
    }});

    // Districts top 10 chart
    const ctxDist = document.getElementById('overviewDistrictsChart').getContext('2d');
    const top10Dist = bus.districts.slice(0, 10);
    AppState.charts.overviewDist = new Chart(ctxDist, {{
      type: 'bar',
      data: {{
        labels: top10Dist.map(d => d.name.replace('เขต', '')),
        datasets: [
          {{
            label: 'วันทำงานปกติ',
            data: top10Dist.map(d => d.total_wd),
            backgroundColor: '#3b82f6',
            borderRadius: 4
          }},
          {{
            label: 'วันหยุดสุดสัปดาห์',
            data: top10Dist.map(d => d.total_we),
            backgroundColor: 'rgba(59, 130, 246, 0.35)',
            borderRadius: 4
          }}
        ]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        scales: {{
          x: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8' }} }},
          y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }} }}
        }},
        plugins: {{
          legend: {{ labels: {{ color: '#cbd5e1' }} }}
        }}
      }}
    }});
  }}

  function setOverviewTrafficMode(mode) {{
    AppState.overviewTrafficMetric = mode;
    const btnGroup = event.target.parentElement;
    btnGroup.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');

    const chart = AppState.charts.overviewHourly;
    const hourly = DASHBOARD_DATA.cctv.hourly;

    if (mode === 'speed') {{
      chart.data.datasets[0].data = hourly.working.speed;
      chart.data.datasets[1].data = hourly.holiday.speed;
      chart.options.scales.y.title.text = 'ความเร็วเฉลี่ย (กม./ชม.)';
    }} else if (mode === 'volume') {{
      chart.data.datasets[0].data = hourly.working.volume;
      chart.data.datasets[1].data = hourly.holiday.volume;
      chart.options.scales.y.title.text = 'ปริมาณรถเฉลี่ย (คัน/ชม.)';
    }} else if (mode === 'vc') {{
      chart.data.datasets[0].data = hourly.working.vc;
      chart.data.datasets[1].data = hourly.holiday.vc;
      chart.options.scales.y.title.text = 'V/C Ratio (ความจุ/ความต้องการ)';
    }}
    chart.update();
  }}

  // 2. TRAFFIC TAB
  function initTrafficTab() {{
    const cctv = DASHBOARD_DATA.cctv;

    // Map initialization
    try {{
      if (typeof L !== 'undefined') {{
        AppState.map = L.map('traffic-map').setView([13.7563, 100.5018], 11);
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
          attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
          maxZoom: 19
        }}).addTo(AppState.map);

        renderMapMarkers('ALL');
      }}
    }} catch (e) {{
      console.warn('Leaflet map error or offline:', e);
      document.getElementById('traffic-map').innerHTML = '<div style="padding:40px;text-align:center;color:#94a3b8;">แผนที่พร้อมใช้งาน (แสดงพิกัดผ่าน Leaflet)</div>';
    }}

    // Agency stats chart & list
    const agencyData = cctv.org_stats;
    const orgKeys = Object.keys(agencyData);
    const orgLabels = {{
      'DOH': 'กรมทางหลวง (DOH)',
      'BMA': 'กทม. (BMA)',
      'EXAT': 'การทางพิเศษ (EXAT)'
    }};

    const ctxAgency = document.getElementById('trafficAgencyChart').getContext('2d');
    AppState.charts.trafficAgency = new Chart(ctxAgency, {{
      type: 'polarArea',
      data: {{
        labels: orgKeys.map(k => orgLabels[k] || k),
        datasets: [{{
          data: orgKeys.map(k => agencyData[k].avg_speed),
          backgroundColor: [
            'rgba(6, 182, 212, 0.65)',
            'rgba(16, 185, 129, 0.65)',
            'rgba(139, 92, 246, 0.65)'
          ],
          borderWidth: 1,
          borderColor: '#0f172a'
        }}]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
          legend: {{ position: 'bottom', labels: {{ color: '#94a3b8', font: {{ size: 11 }} }} }}
        }},
        scales: {{
          r: {{ grid: {{ color: 'rgba(255,255,255,0.08)' }}, ticks: {{ display: false }} }}
        }}
      }}
    }});

    const statsListEl = document.getElementById('trafficAgencyStats');
    statsListEl.innerHTML = '';
    orgKeys.forEach(k => {{
      const st = agencyData[k];
      const row = document.createElement('div');
      row.style.cssText = 'display:flex;justify-content:space-between;padding:6px 10px;background:rgba(15,23,42,0.4);border-radius:6px;';
      row.innerHTML = `
        <span style="font-weight:600;color:#f8fafc;">${{orgLabels[k] || k}} (${{st.count}} กล้อง)</span>
        <span style="color:#38bdf8;">ความเร็ว ${{st.avg_speed}} กม./ชม. | V/C ${{st.avg_vc}}</span>
      `;
      statsListEl.appendChild(row);
    }});

    // Speed distribution chart
    const speedDist = cctv.speed_dist;
    const ctxSpeed = document.getElementById('speedDistChart').getContext('2d');
    AppState.charts.speedDist = new Chart(ctxSpeed, {{
      type: 'bar',
      data: {{
        labels: Object.keys(speedDist),
        datasets: [{{
          label: 'จำนวนบันทึก (รายการ)',
          data: Object.values(speedDist),
          backgroundColor: [
            '#ef4444',
            '#f59e0b',
            '#10b981',
            '#06b6d4',
            '#3b82f6'
          ],
          borderRadius: 6
        }}]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        scales: {{
          x: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8' }} }},
          y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }} }}
        }},
        plugins: {{
          legend: {{ display: false }}
        }}
      }}
    }});

    // Top Congested table
    const topTable = document.getElementById('topCongestedTable');
    topTable.innerHTML = '';
    cctv.top_congested.forEach((cam, i) => {{
      const tr = document.createElement('tr');
      const statusClass = cam.avg_vc > 1.0 ? 'status-congested' : (cam.avg_vc >= 0.7 ? 'status-moderate' : 'status-fluid');
      tr.innerHTML = `
        <td><span class="rank-badge ${{i < 3 ? 'rank-' + (i+1) : 'rank-default'}}">${{i+1}}</span></td>
        <td style="font-weight:600;color:#fff;" title="${{cam.name}}">${{cam.name}}</td>
        <td><span class="kpi-badge" style="background:rgba(255,255,255,0.1);">${{cam.organization}}</span></td>
        <td>${{cam.avg_speed}} กม./ชม.</td>
        <td style="font-weight:700;color:#fb7185;">${{cam.max_vc}} (เฉลี่ย ${{cam.avg_vc}})</td>
        <td><span class="status-tag ${{statusClass}}">${{cam.status}}</span></td>
      `;
      topTable.appendChild(tr);
    }});
  }}

  function renderMapMarkers(filterOrg) {{
    if (!AppState.map) return;
    AppState.mapMarkers.forEach(m => AppState.map.removeLayer(m));
    AppState.mapMarkers = [];

    const cameras = DASHBOARD_DATA.cctv.cameras;
    cameras.forEach(cam => {{
      if (filterOrg !== 'ALL' && cam.organization !== filterOrg) return;

      const circle = L.circleMarker([cam.lat, cam.lng], {{
        radius: 7,
        fillColor: cam.color,
        color: '#ffffff',
        weight: 1.5,
        opacity: 0.9,
        fillOpacity: 0.85
      }});

      circle.bindPopup(`
        <div class="custom-popup">
          <h4>${{cam.name}}</h4>
          <p><b>หน่วยงาน:</b> ${{cam.organization}}</p>
          <p><b>ความเร็วเฉลี่ย:</b> ${{cam.avg_speed}} กม./ชม.</p>
          <p><b>V/C Ratio:</b> ${{cam.avg_vc}} (สูงสุด: ${{cam.max_vc}})</p>
          <p><b>ปริมาณรถเฉลี่ย:</b> ${{formatNumber(cam.avg_volume)}} คัน/ชม.</p>
          <p><b>สถานะ:</b> <span style="color:${{cam.color}};font-weight:700;">${{cam.status}}</span></p>
        </div>
      `);

      circle.addTo(AppState.map);
      AppState.mapMarkers.push(circle);
    }});
  }}

  function filterMapPoints() {{
    const org = document.getElementById('mapOrgFilter').value;
    renderMapMarkers(org);
  }}

  // 3. BUS TAB
  function initBusTab() {{
    const bus = DASHBOARD_DATA.bus;
    const top15 = bus.districts.slice(0, 15);

    // District bar chart
    const ctxTopDist = document.getElementById('busDistrictsTopChart').getContext('2d');
    AppState.charts.busTopDist = new Chart(ctxTopDist, {{
      type: 'bar',
      data: {{
        labels: top15.map(d => d.name.replace('เขต', '')),
        datasets: [{{
          label: 'การจอดรับ-ส่งวันทำงาน (ครั้ง)',
          data: top15.map(d => d.total_wd),
          backgroundColor: '#3b82f6',
          borderRadius: 4
        }}]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        scales: {{
          x: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8', maxRotation: 45 }} }},
          y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }} }}
        }},
        plugins: {{
          legend: {{ display: false }}
        }}
      }}
    }});

    // Pickup vs Dropoff chart
    const top10 = bus.districts.slice(0, 10);
    const ctxFlow = document.getElementById('busPickupDropoffChart').getContext('2d');
    AppState.charts.busFlow = new Chart(ctxFlow, {{
      type: 'bar',
      data: {{
        labels: top10.map(d => d.name.replace('เขต', '')),
        datasets: [
          {{
            label: 'ผู้โดยสารขึ้น (Pickup)',
            data: top10.map(d => d.pickup_wd),
            backgroundColor: '#10b981',
            borderRadius: 4
          }},
          {{
            label: 'ผู้โดยสารลง (Dropoff)',
            data: top10.map(d => d.dropoff_wd),
            backgroundColor: '#f59e0b',
            borderRadius: 4
          }}
        ]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        scales: {{
          x: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8' }} }},
          y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }} }}
        }},
        plugins: {{
          legend: {{ labels: {{ color: '#cbd5e1' }} }}
        }}
      }}
    }});

    // Render Top 25 stops table
    renderBusLeaderboard(bus.top_25_stops);
  }}

  function renderBusLeaderboard(stopsList) {{
    const tbody = document.getElementById('top25BusStopsTable');
    tbody.innerHTML = '';
    const maxTotal = stopsList.length > 0 ? stopsList[0].grand_total : 1;

    stopsList.forEach((stop, i) => {{
      const tr = document.createElement('tr');
      const pct = Math.round((stop.grand_total / maxTotal) * 100);
      tr.innerHTML = `
        <td><span class="rank-badge ${{stop.rank <= 3 ? 'rank-' + stop.rank : 'rank-default'}}">${{stop.rank}}</span></td>
        <td style="font-weight:600;color:#fff;">${{stop.bus_stop}}</td>
        <td><span class="kpi-badge" style="background:rgba(59,130,246,0.15);color:#60a5fa;">${{stop.district}}</span></td>
        <td style="color:#34d399;">${{formatNumber(stop.pickup_wd)}}</td>
        <td style="color:#fbbf24;">${{formatNumber(stop.dropoff_wd)}}</td>
        <td>${{formatNumber(stop.total_wd)}}</td>
        <td>${{formatNumber(stop.total_we)}}</td>
        <td>
          <div class="bar-wrapper">
            <span style="font-weight:700;color:#38bdf8;min-width:60px;">${{formatNumber(stop.grand_total)}}</span>
            <div class="bar-bg">
              <div class="bar-fill" style="width:${{pct}}%;background:linear-gradient(90deg,#06b6d4,#3b82f6);"></div>
            </div>
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    }});
  }}

  function filterBusLeaderboard() {{
    const q = document.getElementById('busLeaderboardFilter').value.toLowerCase();
    const all = DASHBOARD_DATA.bus.top_25_stops;
    const filtered = all.filter(s => s.bus_stop.toLowerCase().includes(q) || s.district.toLowerCase().includes(q));
    renderBusLeaderboard(filtered);
  }}

  // 4. TRANSIT TAB (MODES)
  function initTransitTab() {{
    const modes = DASHBOARD_DATA.travel.modes;
    const container = document.getElementById('modeCardsContainer');
    container.innerHTML = '';

    const iconMap = {{
      'bus': '🚌',
      'boat': '🚢',
      'train': '🚊'
    }};

    modes.forEach(m => {{
      const isFeatured = m.id === 'train';
      const card = document.createElement('div');
      card.className = `mode-card ${{isFeatured ? 'featured' : ''}}`;
      card.innerHTML = `
        <div class="mode-header">
          <div class="mode-title">
            <div class="mode-icon" style="background:rgba(255,255,255,0.06);color:${{m.color}};">
              ${{iconMap[m.id] || '🚗'}}
            </div>
            <div>
              <h3 style="font-size:1.1rem;font-weight:700;color:#fff;">${{m.name}}</h3>
              <span class="status-tag status-fluid" style="background:rgba(6,182,212,0.15);color:#38bdf8;">${{m.speed_rank}} | ${{m.cost_rank}}</span>
            </div>
          </div>
          ${{isFeatured ? '<span class="kpi-badge" style="background:#06b6d4;color:#04101e;">เร็วที่สุด</span>' : ''}}
        </div>

        <div class="mode-metrics">
          <div class="mode-metric-item">
            <span class="label">เวลารวม (นาที/เที่ยว)</span>
            <span class="value" style="color:${{m.color}};">${{m.time_total}}</span>
          </div>
          <div class="mode-metric-item">
            <span class="label">ค่าใช้จ่ายรวม (บาท/เที่ยว)</span>
            <span class="value" style="color:#34d399;">${{m.cost_total}}</span>
          </div>
          <div class="mode-metric-item">
            <span class="label">เวลาในระบบหลัก</span>
            <span style="font-size:0.95rem;color:#f8fafc;font-weight:600;">${{m.time_in_transit}} นาที</span>
          </div>
          <div class="mode-metric-item">
            <span class="label">ค่าโดยสารระบบหลัก</span>
            <span style="font-size:0.95rem;color:#f8fafc;font-weight:600;">${{m.cost_in_transit}} บาท</span>
          </div>
        </div>

        <div style="font-size:0.78rem;color:var(--text-secondary);background:rgba(15,23,42,0.4);padding:10px;border-radius:6px;">
          <b>สัดส่วนการเชื่อมต่อ Feeder:</b> เดิน ${{m.feeder['การเดิน']}}% | วินมอเตอร์ไซค์ ${{m.feeder['จักรยานยนต์รับจ้าง']}}%
        </div>
      `;
      container.appendChild(card);
    }});

    // Mode Time stacked bar chart
    const ctxTime = document.getElementById('modeTimeChart').getContext('2d');
    AppState.charts.modeTime = new Chart(ctxTime, {{
      type: 'bar',
      data: {{
        labels: modes.map(m => m.name),
        datasets: [
          {{
            label: 'เวลาในระบบหลัก (In-transit)',
            data: modes.map(m => m.time_in_transit_num),
            backgroundColor: '#3b82f6',
            borderRadius: 4
          }},
          {{
            label: 'เวลาเชื่อมต่อ Feeder (เข้า-ออก)',
            data: modes.map(m => m.time_feeder_num),
            backgroundColor: '#06b6d4',
            borderRadius: 4
          }}
        ]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        scales: {{
          x: {{ stacked: true, grid: {{ display: false }}, ticks: {{ color: '#94a3b8' }} }},
          y: {{ stacked: true, grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }}, title: {{ display: true, text: 'นาทีต่อเที่ยว', color: '#94a3b8' }} }}
        }},
        plugins: {{
          legend: {{ labels: {{ color: '#cbd5e1' }} }}
        }}
      }}
    }});

    // Mode Cost stacked bar chart
    const ctxCost = document.getElementById('modeCostChart').getContext('2d');
    AppState.charts.modeCost = new Chart(ctxCost, {{
      type: 'bar',
      data: {{
        labels: modes.map(m => m.name),
        datasets: [
          {{
            label: 'ค่าโดยสารระบบหลัก',
            data: modes.map(m => m.cost_in_transit_num),
            backgroundColor: '#10b981',
            borderRadius: 4
          }},
          {{
            label: 'ค่าเดินทาง Feeder',
            data: modes.map(m => m.cost_feeder_num),
            backgroundColor: '#f59e0b',
            borderRadius: 4
          }}
        ]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        scales: {{
          x: {{ stacked: true, grid: {{ display: false }}, ticks: {{ color: '#94a3b8' }} }},
          y: {{ stacked: true, grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }}, title: {{ display: true, text: 'บาทต่อเที่ยว', color: '#94a3b8' }} }}
        }},
        plugins: {{
          legend: {{ labels: {{ color: '#cbd5e1' }} }}
        }}
      }}
    }});
  }}

  function recalculateCommute() {{
    const modeId = document.getElementById('calcMode').value;
    const distance = parseFloat(document.getElementById('calcDistance').value) || 15;
    const tripsPerDay = parseInt(document.getElementById('calcTrips').value) || 2;
    const daysPerMonth = parseInt(document.getElementById('calcDays').value) || 22;

    const modeObj = DASHBOARD_DATA.travel.modes.find(m => m.id === modeId) || DASHBOARD_DATA.travel.modes[0];

    // Calculated time based on speed ratio & distance
    let baseTransitTime = modeObj.time_in_transit_num;
    // Scale slightly with distance
    let scaledTransitTime = Math.round(baseTransitTime * (distance / 15));
    let totalTime = scaledTransitTime + modeObj.time_feeder_num;

    // Calculated cost
    let baseCost = modeObj.cost_in_transit_num;
    let scaledTransitCost = Math.round(baseCost * Math.max(0.7, (distance / 15)));
    let totalCostPerTrip = scaledTransitCost + modeObj.cost_feeder_num;
    let monthlyCost = totalCostPerTrip * tripsPerDay * daysPerMonth;

    document.getElementById('calcResultTime').innerText = `${{totalTime}} นาที`;
    document.getElementById('calcResultTimeDetail').innerText = `ระบบหลัก ${{scaledTransitTime}} น. + เชื่อมต่อ ${{modeObj.time_feeder_num}} น.`;

    document.getElementById('calcResultCost').innerText = `${{totalCostPerTrip}} บาท`;
    document.getElementById('calcResultCostDetail').innerText = `ระบบหลัก ${{scaledTransitCost}} บ. + Feeder ${{modeObj.cost_feeder_num}} บ.`;

    document.getElementById('calcResultMonthly').innerText = `${{formatNumber(monthlyCost)}} บาท`;
  }}

  // 5. DATA EXPLORER & ADVANCED FILTERS
  function initExplorerTab() {{
    const distSelect = document.getElementById('explorerDistrictFilter');
    const districts = DASHBOARD_DATA.bus.districts;
    distSelect.innerHTML = '<option value="ALL">ทุกเขตในกรุงเทพมหานคร (50 เขต)</option>';
    districts.forEach(d => {{
      const opt = document.createElement('option');
      opt.value = d.name;
      opt.innerText = `${{d.name}} (${{d.stop_count}} ป้าย)`;
      distSelect.appendChild(opt);
    }});

    onExplorerFilterChange();
  }}

  function onExplorerFilterChange() {{
    const query = (document.getElementById('explorerSearchInput').value || '').trim().toLowerCase();
    const type = document.getElementById('explorerTypeFilter').value;
    const district = document.getElementById('explorerDistrictFilter').value;
    const sort = document.getElementById('explorerSortFilter').value;

    let items = [];

    // Bus items
    if (type === 'ALL' || type === 'BUS') {{
      DASHBOARD_DATA.bus.searchable_stops.forEach(s => {{
        if (district !== 'ALL' && s.district !== district) return;
        if (query && !s.name.toLowerCase().includes(query) && !s.district.toLowerCase().includes(query)) return;

        items.push({{
          type: 'BUS',
          typeName: 'ป้ายรถเมล์',
          name: s.name,
          location: s.district,
          metric1: s.total_wd,
          metric1Label: 'วันธรรมดา: ' + formatNumber(s.total_wd),
          metric2: s.total_we,
          metric2Label: 'วันหยุด: ' + formatNumber(s.total_we),
          total: s.grand_total,
          totalLabel: formatNumber(s.grand_total) + ' ครั้ง',
          status: 'ป้ายหนาแน่น',
          statusClass: 'status-fluid'
        }});
      }});
    }}

    // CCTV items
    if (type === 'ALL' || type === 'CCTV') {{
      DASHBOARD_DATA.cctv.cameras.forEach(c => {{
        if (district !== 'ALL') return; // CCTV don't have district tagged directly
        if (query && !c.name.toLowerCase().includes(query) && !c.organization.toLowerCase().includes(query)) return;

        const statusClass = c.avg_vc > 1.0 ? 'status-congested' : (c.avg_vc >= 0.7 ? 'status-moderate' : 'status-fluid');
        items.push({{
          type: 'CCTV',
          typeName: 'กล้อง CCTV',
          name: c.name,
          location: c.organization,
          metric1: c.avg_volume,
          metric1Label: 'ปริมาณ: ' + formatNumber(c.avg_volume) + ' คัน/ชม.',
          metric2: c.avg_capacity,
          metric2Label: 'ความจุ: ' + formatNumber(c.avg_capacity),
          total: c.avg_vc,
          totalLabel: 'V/C ' + c.avg_vc + ' (ความเร็ว ' + c.avg_speed + ' กม./ชม.)',
          status: c.status,
          statusClass: statusClass
        }});
      }});
    }}

    // Sorting
    if (sort === 'VOLUME_DESC') {{
      items.sort((a, b) => b.total - a.total);
    }} else if (sort === 'VOLUME_ASC') {{
      items.sort((a, b) => a.total - b.total);
    }} else if (sort === 'NAME_ASC') {{
      items.sort((a, b) => a.name.localeCompare(b.name, 'th'));
    }}

    AppState.explorerFilteredData = items;
    AppState.explorerPage = 1;
    renderExplorerTable();
  }}

  function renderExplorerTable() {{
    const items = AppState.explorerFilteredData;
    const totalCount = items.length;
    const pageSize = AppState.explorerPageSize;
    const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));
    const page = Math.min(AppState.explorerPage, totalPages);

    document.getElementById('explorerRecordCount').innerText = `พบ ${{formatNumber(totalCount)}} รายการ`;
    document.getElementById('paginationInfo').innerText = `หน้าที่ ${{page}} จาก ${{totalPages}} (แสดง ${{Math.min(pageSize, totalCount - (page-1)*pageSize)}} รายการ)`;

    const tbody = document.getElementById('explorerTableBody');
    tbody.innerHTML = '';

    if (totalCount === 0) {{
      tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:40px;color:var(--text-muted);">ไม่พบข้อมูลที่ตรงกับเงื่อนไขการค้นหา</td></tr>';
      return;
    }}

    const start = (page - 1) * pageSize;
    const pageItems = items.slice(start, start + pageSize);

    pageItems.forEach((it, idx) => {{
      const tr = document.createElement('tr');
      const typeBadge = it.type === 'BUS' 
        ? '<span class="kpi-badge" style="background:rgba(59,130,246,0.2);color:#60a5fa;">🚌 รถเมล์</span>'
        : '<span class="kpi-badge" style="background:rgba(6,182,212,0.2);color:#38bdf8;">📹 CCTV</span>';

      tr.innerHTML = `
        <td>${{start + idx + 1}}</td>
        <td>${{typeBadge}}</td>
        <td style="font-weight:600;color:#fff;" title="${{it.name}}">${{it.name}}</td>
        <td>${{it.location}}</td>
        <td>${{it.metric1Label}}</td>
        <td>${{it.metric2Label}}</td>
        <td style="font-weight:700;color:#38bdf8;">${{it.totalLabel}}</td>
        <td><span class="status-tag ${{it.statusClass}}">${{it.status}}</span></td>
      `;
      tbody.appendChild(tr);
    }});

    // Update pagination controls
    document.getElementById('btnPrevPage').disabled = page <= 1;
    document.getElementById('btnNextPage').disabled = page >= totalPages;

    const pageNumContainer = document.getElementById('pageNumbersContainer');
    pageNumContainer.innerHTML = '';
    for (let p = Math.max(1, page - 2); p <= Math.min(totalPages, page + 2); p++) {{
      const pBtn = document.createElement('button');
      pBtn.className = `page-btn ${{p === page ? 'active' : ''}}`;
      pBtn.innerText = p;
      pBtn.onclick = () => {{
        AppState.explorerPage = p;
        renderExplorerTable();
      }};
      pageNumContainer.appendChild(pBtn);
    }}
  }}

  function changeExplorerPage(delta) {{
    AppState.explorerPage += delta;
    renderExplorerTable();
  }}

  function resetExplorerFilters() {{
    document.getElementById('explorerSearchInput').value = '';
    document.getElementById('explorerTypeFilter').value = 'ALL';
    document.getElementById('explorerDistrictFilter').value = 'ALL';
    document.getElementById('explorerSortFilter').value = 'VOLUME_DESC';
    onExplorerFilterChange();
  }}

  function exportFilteredCSV() {{
    const items = AppState.explorerFilteredData;
    if (!items || items.length === 0) {{
      alert('ไม่มีข้อมูลสำหรับ Export');
      return;
    }}

    let csvContent = "\uFEFFลำดับ,ประเภท,ชื่อตำแหน่ง,พื้นที่/เขต/หน่วยงาน,ข้อมูล1,ข้อมูล2,ดัชนีรวม,สถานะ\\n";
    items.forEach((it, idx) => {{
      const cleanName = `"${{it.name.replace(/"/g, '""')}}"`;
      const cleanLoc = `"${{it.location.replace(/"/g, '""')}}"`;
      csvContent += `${{idx+1}},${{it.typeName}},${{cleanName}},${{cleanLoc}},${{it.metric1}},${{it.metric2}},${{it.total}},${{it.status}}\\n`;
    }});

    const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'bangkok_mobility_analytics_export.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }}
</script>

</body>
</html>
'''

print("Writing index.html...")
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Copying to dashboard.html...")
shutil.copyfile("index.html", "dashboard.html")

print("Files created successfully in E:\\Agentic: index.html and dashboard.html")
