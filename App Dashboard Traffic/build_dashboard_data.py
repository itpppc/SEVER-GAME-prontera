import os
import json
import pandas as pd
import numpy as np

print('Starting data processing for Bangkok Transportation Dashboard...')

# 1. CCTV
print('Processing CCTV Data...')
df_cctv = pd.read_csv('CCTV_BKK_otp_66_05.csv', encoding='utf-8-sig')

for col in ['volume', 'capacity']:
    if df_cctv[col].dtype == object:
        df_cctv[col] = df_cctv[col].astype(str).str.replace(',', '', regex=False)
    df_cctv[col] = pd.to_numeric(df_cctv[col], errors='coerce').fillna(0)

df_cctv['speed'] = pd.to_numeric(df_cctv['speed'], errors='coerce').fillna(0)
df_cctv['density'] = pd.to_numeric(df_cctv['density'], errors='coerce').fillna(0)
df_cctv['v/c'] = pd.to_numeric(df_cctv['v/c'], errors='coerce').fillna(0)

camera_groups = df_cctv.groupby(['id', 'name', 'organization', 'latitude', 'longitude'])
camera_list = []
for (cid, cname, org, lat, lon), grp in camera_groups:
    avg_speed = round(float(grp['speed'].mean()), 1)
    avg_vc = round(float(grp['v/c'].mean()), 2)
    avg_vol = round(float(grp['volume'].mean()), 0)
    avg_cap = round(float(grp['capacity'].mean()), 0)
    avg_den = round(float(grp['density'].mean()), 1)
    max_vc = round(float(grp['v/c'].max()), 2)
    
    if avg_vc < 0.7:
        status = 'คล่องตัว'
        color = '#10b981'
    elif avg_vc < 1.0:
        status = 'เริ่มชะลอตัว'
        color = '#f59e0b'
    else:
        status = 'หนาแน่น / ติดขัด'
        color = '#ef4444'

    camera_list.append({
        'id': int(cid),
        'name': str(cname),
        'organization': str(org).upper(),
        'lat': float(lat),
        'lng': float(lon),
        'avg_speed': avg_speed,
        'avg_vc': avg_vc,
        'avg_volume': int(avg_vol),
        'avg_capacity': int(avg_cap),
        'avg_density': avg_den,
        'max_vc': max_vc,
        'status': status,
        'color': color
    })

org_stats = {}
for org, grp in df_cctv.groupby('organization'):
    org_stats[str(org).upper()] = {
        'count': int(grp['name'].nunique()),
        'avg_speed': round(float(grp['speed'].mean()), 1),
        'avg_vc': round(float(grp['v/c'].mean()), 2),
        'avg_volume': int(grp['volume'].mean())
    }

def extract_hour(t_str):
    try:
        return int(str(t_str).split(':')[0])
    except:
        return 0

df_cctv['hour'] = df_cctv['time_start'].apply(extract_hour)
all_hours = sorted(df_cctv['hour'].unique())
hourly_labels = [f'{h:02d}:00' for h in all_hours]

hw = df_cctv[df_cctv['date_type'] == 'working'].groupby('hour').agg({'speed':'mean','volume':'mean','v/c':'mean'}).to_dict()
hh = df_cctv[df_cctv['date_type'] == 'holiday'].groupby('hour').agg({'speed':'mean','volume':'mean','v/c':'mean'}).to_dict()

hourly_data = {
    'labels': hourly_labels,
    'working': {
        'speed': [round(float(hw['speed'].get(h, 0)), 1) for h in all_hours],
        'volume': [int(hw['volume'].get(h, 0)) for h in all_hours],
        'vc': [round(float(hw['v/c'].get(h, 0)), 2) for h in all_hours]
    },
    'holiday': {
        'speed': [round(float(hh['speed'].get(h, 0)), 1) for h in all_hours],
        'volume': [int(hh['volume'].get(h, 0)) for h in all_hours],
        'vc': [round(float(hh['v/c'].get(h, 0)), 2) for h in all_hours]
    }
}

speed_bins = [0, 30, 50, 70, 90, 300]
speed_labels = ['< 30 กม./ชม.', '30 - 50 กม./ชม.', '50 - 70 กม./ชม.', '70 - 90 กม./ชม.', '> 90 กม./ชม.']
df_cctv['speed_bin'] = pd.cut(df_cctv['speed'], bins=speed_bins, labels=speed_labels, right=False)
speed_dist = {k: int(v) for k, v in df_cctv['speed_bin'].value_counts()[speed_labels].to_dict().items()}

top_congested = sorted(camera_list, key=lambda x: x['avg_vc'], reverse=True)[:10]
top_fastest = sorted(camera_list, key=lambda x: x['avg_speed'], reverse=True)[:10]
print('CCTV processing complete.')

# 2. Bus stops
print('Processing Bus Stops Data...')
df_bus = pd.read_excel('ผลการวิเคราะห์พื้นที่ที่มีการจอดรับและจ.xlsx', sheet_name='otp_69_05')
df_bus['Month'] = df_bus['Month'].astype(str).str.strip()

years_list = sorted([int(x) for x in df_bus['Year'].unique()])
month_order = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
               'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']

districts_data = []
dist_grouped = df_bus.groupby('district')
for dist_name, grp in dist_grouped:
    total_wd = int(grp['total_stops_wd'].sum())
    total_we = int(grp['total_stops_we'].sum())
    pickup_wd = int(grp['pickup_wd'].sum())
    dropoff_wd = int(grp['dropoff_wd'].sum())
    pickup_we = int(grp['pickup_we'].sum())
    dropoff_we = int(grp['dropoff_we'].sum())
    stop_count = int(grp['bus_stop'].nunique())
    
    top_in_dist = grp.groupby('bus_stop')['total_stops_wd'].sum().sort_values(ascending=False).head(3)
    top_stops = [{'name': str(s), 'stops_wd': int(v)} for s, v in top_in_dist.items()]
    
    districts_data.append({
        'name': str(dist_name),
        'total_wd': total_wd,
        'total_we': total_we,
        'pickup_wd': pickup_wd,
        'dropoff_wd': dropoff_wd,
        'pickup_we': pickup_we,
        'dropoff_we': dropoff_we,
        'stop_count': stop_count,
        'top_stops': top_stops
    })

districts_data = sorted(districts_data, key=lambda x: x['total_wd'], reverse=True)

top_stops_overall = df_bus.groupby(['bus_stop', 'district']).agg({
    'total_stops_wd': 'sum',
    'pickup_wd': 'sum',
    'dropoff_wd': 'sum',
    'total_stops_we': 'sum',
    'pickup_we': 'sum',
    'dropoff_we': 'sum'
}).reset_index()

top_stops_overall['grand_total'] = top_stops_overall['total_stops_wd'] + top_stops_overall['total_stops_we']
top_stops_overall = top_stops_overall.sort_values(by='grand_total', ascending=False)

top_25_stops = []
for idx, r in top_stops_overall.head(25).iterrows():
    top_25_stops.append({
        'rank': len(top_25_stops) + 1,
        'bus_stop': str(r['bus_stop']),
        'district': str(r['district']),
        'pickup_wd': int(r['pickup_wd']),
        'dropoff_wd': int(r['dropoff_wd']),
        'total_wd': int(r['total_stops_wd']),
        'total_we': int(r['total_stops_we']),
        'grand_total': int(r['grand_total'])
    })

monthly_trend = {}
for m in month_order:
    m_grp = df_bus[df_bus['Month'] == m]
    if len(m_grp) > 0:
        monthly_trend[m] = {
            'total_wd': int(m_grp['total_stops_wd'].sum()),
            'total_we': int(m_grp['total_stops_we'].sum())
        }

yearly_trend = {}
for y in years_list:
    y_grp = df_bus[df_bus['Year'] == y]
    yearly_trend[str(y)] = {
        'total_wd': int(y_grp['total_stops_wd'].sum()),
        'total_we': int(y_grp['total_stops_we'].sum()),
        'pickup_wd': int(y_grp['pickup_wd'].sum()),
        'dropoff_wd': int(y_grp['dropoff_wd'].sum())
    }

searchable_stops = []
for idx, r in top_stops_overall.head(300).iterrows():
    searchable_stops.append({
        'name': str(r['bus_stop']),
        'district': str(r['district']),
        'total_wd': int(r['total_stops_wd']),
        'pickup_wd': int(r['pickup_wd']),
        'dropoff_wd': int(r['dropoff_wd']),
        'total_we': int(r['total_stops_we']),
        'grand_total': int(r['grand_total'])
    })

print('Bus stops processing complete.')

# 3. Travel
travel_modes = [
    {
        'id': 'bus',
        'name': 'รถโดยสารประจำทาง (Bus)',
        'color': '#3b82f6',
        'time_total': '50 - 55',
        'time_total_num': 52.5,
        'time_in_transit': '35 - 40',
        'time_in_transit_num': 37.5,
        'time_feeder_num': 15.0,
        'cost_total': '18 - 30',
        'cost_total_num': 24.0,
        'cost_in_transit': '14 - 24',
        'cost_in_transit_num': 19.0,
        'cost_feeder_num': 5.0,
        'speed_rank': 'ปานกลาง',
        'cost_rank': 'ประหยัดสุด',
        'feeder': {'การเดิน': 70, 'จักรยานยนต์รับจ้าง': 10, 'รถโดยสารประจำทาง': 0, 'อื่นๆ': 20}
    },
    {
        'id': 'boat',
        'name': 'เรือโดยสาร (Boat)',
        'color': '#06b6d4',
        'time_total': '45 - 55',
        'time_total_num': 50.0,
        'time_in_transit': '25 - 30',
        'time_in_transit_num': 27.5,
        'time_feeder_num': 22.5,
        'cost_total': '25 - 30',
        'cost_total_num': 27.5,
        'cost_in_transit': '18 - 21',
        'cost_in_transit_num': 19.5,
        'cost_feeder_num': 8.0,
        'speed_rank': 'ปานกลาง-เร็ว',
        'cost_rank': 'ปานกลาง',
        'feeder': {'การเดิน': 70, 'จักรยานยนต์รับจ้าง': 10, 'รถโดยสารประจำทาง': 0, 'อื่นๆ': 20}
    },
    {
        'id': 'train',
        'name': 'รถไฟฟ้า (BTS/MRT Rail)',
        'color': '#8b5cf6',
        'time_total': '30 - 50',
        'time_total_num': 40.0,
        'time_in_transit': '15 - 25',
        'time_in_transit_num': 20.0,
        'time_feeder_num': 20.0,
        'cost_total': '45 - 50',
        'cost_total_num': 47.5,
        'cost_in_transit': '28 - 35',
        'cost_in_transit_num': 31.5,
        'cost_feeder_num': 16.0,
        'speed_rank': 'เร็วที่สุด',
        'cost_rank': 'สูงกว่าระบบอื่น',
        'feeder': {'การเดิน': 50, 'จักรยานยนต์รับจ้าง': 20, 'รถโดยสารประจำทาง': 10, 'อื่นๆ': 20}
    }
]

dashboard_data = {
    'overview': {
        'cctv_cameras_count': len(camera_list),
        'cctv_records_count': len(df_cctv),
        'avg_traffic_speed': round(float(df_cctv['speed'].mean()), 1),
        'avg_traffic_vc': round(float(df_cctv['v/c'].mean()), 2),
        'bus_districts_count': len(districts_data),
        'bus_unique_stops': int(df_bus['bus_stop'].nunique()),
        'bus_records_count': len(df_bus),
        'total_bus_wd': int(df_bus['total_stops_wd'].sum()),
        'total_bus_we': int(df_bus['total_stops_we'].sum()),
        'travel_modes_count': len(travel_modes)
    },
    'cctv': {
        'cameras': camera_list,
        'org_stats': org_stats,
        'hourly': hourly_data,
        'speed_dist': speed_dist,
        'top_congested': top_congested,
        'top_fastest': top_fastest
    },
    'bus': {
        'years': years_list,
        'months': [m for m in month_order if m in monthly_trend],
        'districts': districts_data,
        'top_25_stops': top_25_stops,
        'monthly_trend': monthly_trend,
        'yearly_trend': yearly_trend,
        'searchable_stops': searchable_stops
    },
    'travel': {
        'modes': travel_modes
    }
}

with open('dashboard_data.json', 'w', encoding='utf-8') as f:
    json.dump(dashboard_data, f, ensure_ascii=False, indent=2)

print('Done writing dashboard_data.json')
