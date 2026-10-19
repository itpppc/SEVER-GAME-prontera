# -*- coding: utf-8 -*-
"""
Generate PWA icons for Bangkok Smart Mobility
"""
from PIL import Image, ImageDraw, ImageFont
import math

def create_app_icon(size, filename):
    # Create image with RGBA
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Outer margin
    padding = int(size * 0.05)
    
    # Background rounded rect with gradient
    for y in range(size):
        # Vertical gradient from cyan (#06b6d4) to blue/indigo (#2563eb)
        ratio = y / float(size)
        r = int(6 + ratio * (37 - 6))
        g = int(182 + ratio * (99 - 182))
        b = int(212 + ratio * (235 - 212))
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
        
    # Mask rounded rectangle
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    corner_radius = int(size * 0.22)
    mask_draw.rounded_rectangle([(0, 0), (size, size)], radius=corner_radius, fill=255)
    img.putalpha(mask)
    
    # Re-obtain draw handle
    draw = ImageDraw.Draw(img)
    
    # Draw internal glowing circular or mobility emblem
    cx, cy = size // 2, int(size * 0.44)
    r_outer = int(size * 0.28)
    
    # Glow ring
    draw.ellipse([(cx - r_outer, cy - r_outer), (cx + r_outer, cy + r_outer)], 
                 outline=(255, 255, 255, 80), width=max(2, int(size * 0.015)))
                 
    # Inner circle
    r_inner = int(size * 0.23)
    draw.ellipse([(cx - r_inner, cy - r_inner), (cx + r_inner, cy + r_inner)], 
                 fill=(15, 23, 42, 220), outline=(56, 189, 248, 255), width=max(2, int(size * 0.02)))
                 
    # Mobility / Bus symbol representation inside circle
    # Bus body
    bw = int(size * 0.26)
    bh = int(size * 0.26)
    bx = cx - bw // 2
    by = cy - bh // 2 + int(size * 0.01)
    
    draw.rounded_rectangle([(bx, by), (bx + bw, by + bh)], radius=int(size * 0.04), 
                           fill=(255, 255, 255, 255))
                           
    # Bus windshield
    ww = int(bw * 0.8)
    wh = int(bh * 0.38)
    wx = cx - ww // 2
    wy = by + int(bh * 0.12)
    draw.rounded_rectangle([(wx, wy), (wx + ww, wy + wh)], radius=int(size * 0.02), 
                           fill=(15, 23, 42, 255))
                           
    # Headlights
    hl_r = max(2, int(size * 0.025))
    hl_y = by + int(bh * 0.65)
    draw.ellipse([(bx + int(bw * 0.16) - hl_r, hl_y - hl_r), (bx + int(bw * 0.16) + hl_r, hl_y + hl_r)], fill=(245, 158, 11, 255))
    draw.ellipse([(bx + int(bw * 0.84) - hl_r, hl_y - hl_r), (bx + int(bw * 0.84) + hl_r, hl_y + hl_r)], fill=(245, 158, 11, 255))
    
    # Wheels
    wheel_w = int(bw * 0.18)
    wheel_h = int(bh * 0.15)
    draw.rounded_rectangle([(bx + int(bw * 0.12), by + bh - 2), (bx + int(bw * 0.12) + wheel_w, by + bh + wheel_h)], 
                           radius=int(size * 0.01), fill=(15, 23, 42, 255))
    draw.rounded_rectangle([(bx + int(bw * 0.70), by + bh - 2), (bx + int(bw * 0.70) + wheel_w, by + bh + wheel_h)], 
                           radius=int(size * 0.01), fill=(15, 23, 42, 255))
                           
    # Bottom text "BKK" or "TON-AI"
    text_y = int(size * 0.76)
    # Draw simple clean modern badge block
    badge_w = int(size * 0.65)
    badge_h = int(size * 0.14)
    badge_x = (size - badge_w) // 2
    draw.rounded_rectangle([(badge_x, text_y), (badge_x + badge_w, text_y + badge_h)], 
                           radius=int(badge_h * 0.35), fill=(15, 23, 42, 240), 
                           outline=(56, 189, 248, 180), width=max(1, int(size * 0.01)))
                           
    # Draw "BKK SMART" text if font available or simple lines
    try:
        font = ImageFont.truetype("arial.ttf", int(size * 0.08))
        draw.text((cx, text_y + badge_h // 2), "BKK MOBILITY", fill=(255, 255, 255, 255), font=font, anchor="mm")
    except:
        pass
        
    img.save(filename, "PNG")
    print(f"Generated {filename} ({size}x{size})")

create_app_icon(512, "icon-512.png")
create_app_icon(192, "icon-192.png")
create_app_icon(180, "apple-touch-icon.png")
create_app_icon(64, "favicon.png")
print("All PWA icons generated successfully!")
