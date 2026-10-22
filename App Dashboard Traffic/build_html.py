# -*- coding: utf-8 -*-
import json, os

with open('dashboard_data.json', 'r', encoding='utf-8') as f:
    raw_json_str = f.read()

parts = []
