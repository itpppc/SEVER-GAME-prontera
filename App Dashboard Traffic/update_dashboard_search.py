# -*- coding: utf-8 -*-
"""
Script to add the prominent Global Search Bar and Autocomplete to the Dashboard.
"""
import json
import os
import shutil

print("Reading build_complete_dashboard.py...")
with open("build_complete_dashboard.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Search CSS to add
search_css = """
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
"""

# 2. Search HTML
search_html = """
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
"""

# 3. Search JavaScript
search_js = """
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
    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&')})`, 'gi');
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
"""

# Insert CSS before `</style>`
content = content.replace("</style>", search_css + "\n  </style>")

# Insert HTML inside `<header class="dashboard-header">` between brand-section and header-actions
target_header = """    </div>

    <div class="header-actions">"""

replacement_header = f"""    </div>

{search_html}

    <div class="header-actions">"""

content = content.replace(target_header, replacement_header)

# Insert JavaScript before `// Global App State`
content = content.replace("// Global App State", search_js + "\n  // Global App State")

# Write updated build_complete_dashboard.py
with open("build_complete_dashboard.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated build_complete_dashboard.py with Global Search successfully.")
