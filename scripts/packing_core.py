import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
OUT_DIR = ASSETS_DIR
FRIDGES_DIR = os.path.join(ASSETS_DIR, 'fridges')
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(FRIDGES_DIR, exist_ok=True)

CUTOUT_DIRS = [
    os.path.join(ASSETS_DIR, 'cutouts', 'beverages'),
    os.path.join(ASSETS_DIR, 'cutouts', 'parody'),
    os.path.join(ASSETS_DIR, 'cutouts', 'groceries'),
    os.path.join(ASSETS_DIR, 'archive', 'assets_transparent')
]

WIDTH = 1200
HEIGHT = 1600

def find_asset(filename):
    for d in CUTOUT_DIRS:
        p = os.path.join(d, filename)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"Cannot find asset {filename} in cutouts directories.")

from PIL import ImageFont

def create_cooler_base(shelves_y, is_intense=False):
    """
    Creates a commercial Coca-Cola display refrigerator interior (inspired by coca3.JPG):
    - Clean white/cool-gray back wall
    - Brushed aluminum vertical adjustment pilasters with slot perforations
    - White metallic wire rack shelves with depth wire ribs & double-wire front lips
    - Cool commercial daylight LED refrigeration wash
    """
    base = Image.new('RGBA', (WIDTH, HEIGHT), (245, 249, 254, 255))
    draw = ImageDraw.Draw(base)

    # 1. Back wall clean white/cool-gray gradient
    for y in range(HEIGHT):
        t = y / float(HEIGHT)
        r = int(248 - t * 24)
        g = int(251 - t * 20)
        b = int(255 - t * 14)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

    # 2. Side walls (depth perspective)
    wall_w = 40
    for x in range(wall_w):
        prog = x / float(wall_w)
        shade = int(205 + prog * 35)
        draw.line([(x, 0), (x, HEIGHT)], fill=(shade - 4, shade, shade + 6, 255))
        draw.line([(WIDTH - 1 - x, 0), (WIDTH - 1 - x, HEIGHT)], fill=(shade - 4, shade, shade + 6, 255))

    # Corner seam shadows
    draw.line([(wall_w, 0), (wall_w, HEIGHT)], fill=(170, 182, 198, 255), width=2)
    draw.line([(WIDTH - wall_w - 1, 0), (WIDTH - wall_w - 1, HEIGHT)], fill=(170, 182, 198, 255), width=2)

    # 3. Vertical Pilaster adjustment tracks (brushed aluminum with slots)
    pilasters = [260, 600, 940]
    for px in pilasters:
        draw.rectangle([px - 9, 0, px + 9, HEIGHT], fill=(235, 240, 246, 255), outline=(188, 198, 210, 255))
        for sy_slot in range(25, HEIGHT - 25, 20):
            draw.rectangle([px - 6, sy_slot, px - 2, sy_slot + 7], fill=(155, 168, 182, 255))
            draw.rectangle([px + 2, sy_slot, px + 6, sy_slot + 7], fill=(155, 168, 182, 255))

    # 4. White metallic wire rack shelves (as in coca3.JPG)
    for sy in shelves_y:
        # Realistic drop shadow onto back wall
        shadow = Image.new('RGBA', (WIDTH, 34), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        for shy in range(34):
            s_a = int(85 * (1 - shy / 34.0))
            s_draw.line([(wall_w, shy), (WIDTH - wall_w, shy)], fill=(40, 55, 75, s_a))
        base.paste(shadow, (0, sy + 14), shadow)

        # Wire shelf surface: fine longitudinal wires & cross ribs (depth grid)
        rack_depth = 26
        for dy in range(sy - rack_depth, sy, 5):
            draw.line([(wall_w + 2, dy), (WIDTH - wall_w - 2, dy)], fill=(225, 232, 240, 255), width=1)
        for rx in range(wall_w + 6, WIDTH - wall_w - 4, 13):
            draw.line([(rx, sy - rack_depth), (rx, sy)], fill=(210, 220, 230, 255), width=1)

        # Shelf side mounting brackets
        for bx in [wall_w, WIDTH - wall_w - 18]:
            draw.polygon([(bx, sy - 8), (bx + 18, sy - 8), (bx + 18, sy + 12), (bx, sy + 4)], fill=(220, 226, 235, 255), outline=(180, 190, 204, 255))

        # Shelf front double wire lip (white coated wire guard rail)
        draw.rectangle([wall_w - 2, sy - 2, WIDTH - wall_w + 2, sy + 2], fill=(255, 255, 255, 255), outline=(198, 208, 220, 255))
        draw.rectangle([wall_w - 2, sy + 6, WIDTH - wall_w + 2, sy + 10], fill=(245, 248, 252, 255), outline=(190, 200, 212, 255))
        # Welded vertical connector wire pins every 36 px
        for wx in range(wall_w + 14, WIDTH - wall_w - 10, 36):
            draw.line([(wx, sy - 1), (wx, sy + 9)], fill=(215, 224, 235, 255), width=2)

        # Slim commercial white/clear ticket moulding with subtle price tags
        rail_h = 16
        draw.rectangle([wall_w, sy + 10, WIDTH - wall_w, sy + 10 + rail_h], fill=(252, 254, 255, 230), outline=(205, 215, 226, 255))
        for tx in range(wall_w + 20, WIDTH - wall_w - 50, 92):
            draw.rectangle([tx, sy + 12, tx + 48, sy + 8 + rail_h], fill=(255, 255, 255, 255), outline=(220, 226, 234, 255))
            draw.line([(tx + 4, sy + 16), (tx + 24, sy + 16)], fill=(50, 50, 50, 255), width=2)
            draw.line([(tx + 4, sy + 21), (tx + 42, sy + 21)], fill=(220, 30, 45, 255), width=2)

    # 5. Cold Commercial LED Lighting
    led_glow = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    lg_draw = ImageDraw.Draw(led_glow)
    
    # Top ceiling LED wash
    top_glow_h = 220
    for ly in range(top_glow_h):
        glow_a = int(85 * (1 - ly / float(top_glow_h)))
        lg_draw.line([(0, ly), (WIDTH, ly)], fill=(185, 230, 255, glow_a))

    # Side vertical LED tubes
    side_glow_w = 60
    for sx in range(side_glow_w):
        side_a = int(75 * (1 - sx / float(side_glow_w)))
        lg_draw.line([(sx, 0), (sx, HEIGHT)], fill=(185, 230, 255, side_a))
        lg_draw.line([(WIDTH - 1 - sx, 0), (WIDTH - 1 - sx, HEIGHT)], fill=(185, 230, 255, side_a))

    # Under-shelf wash
    for sy in shelves_y:
        under_h = 40
        for uy in range(under_h):
            u_a = int(50 * (1 - uy / float(under_h)))
            lg_draw.line([(wall_w, sy + 26 + uy), (WIDTH - wall_w, sy + 26 + uy)], fill=(195, 235, 255, u_a))

    base = Image.alpha_composite(base, led_glow)
    return base

def apply_glass_and_reflections(img, is_intense=False):
    """
    Applies authentic double-door commercial display case details (coca3.JPG):
    - Top curved illuminated Coca-Cola marquee ("Coca-Cola enjoy ice cold")
    - Bottom black compressor kickplate with cooling louvers and Carel digital thermostat (3.2°C)
    - Double sliding glass doors with black perimeter frame and subtle center overlap seam
    - Specular reflections and condensation for intense difficulty
    """
    overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # 1. Subtle diagonal glass reflection
    for i in range(-HEIGHT, WIDTH + HEIGHT, 6):
        prog = (i + HEIGHT) / (WIDTH + 2 * HEIGHT)
        alpha = int(14 * np.sin(prog * np.pi))
        if is_intense:
            alpha = int(alpha * 1.8)
        d.line([(i, 0), (i - 380, HEIGHT)], fill=(235, 248, 255, alpha), width=5)

    # 2. Top Coca-Cola Marquee / Canopy (Inspired by coca3.JPG)
    marquee_h = 86
    for my in range(marquee_h):
        norm = my / float(marquee_h)
        curve = np.sin(norm * np.pi)
        r = int(212 + curve * 38)
        g = int(20 + curve * 22)
        b = int(28 + curve * 26)
        d.line([(0, my), (WIDTH, my)], fill=(r, g, b, 255))
    
    # Marquee top & bottom black frame trim
    d.rectangle([0, 0, WIDTH, 5], fill=(16, 18, 20, 255))
    d.rectangle([0, marquee_h - 6, WIDTH, marquee_h], fill=(18, 20, 22, 255))
    d.line([(0, marquee_h - 6), (WIDTH, marquee_h - 6)], fill=(55, 60, 68, 255), width=1)

    # Typography & bottle silhouette on marquee
    try:
        font_coke = ImageFont.truetype("arial.ttf", 36)
        font_sub = ImageFont.truetype("arial.ttf", 20)
        font_bold = ImageFont.truetype("arialbd.ttf", 22)
    except:
        font_coke = font_sub = font_bold = ImageFont.load_default()

    d.text((65, 24), "Coca-Cola", fill=(255, 255, 255, 255), font=font_coke)
    d.text((680, 32), "enjoy", fill=(255, 255, 255, 240), font=font_sub)
    bx = 745
    by = 22
    d.polygon([(bx+7, by+4), (bx+11, by+4), (bx+10, by+12), (bx+14, by+20), (bx+14, by+36), (bx+12, by+44), (bx+6, by+44), (bx+4, by+36), (bx+4, by+20), (bx+8, by+12)], fill=(255, 255, 255, 250))
    d.text((770, 30), "ice cold", fill=(255, 255, 255, 245), font=font_bold)

    # 3. Bottom Compressor Kickplate / Grill & Digital Thermostat (coca3.JPG)
    kickplate_h = 55
    top_k = HEIGHT - kickplate_h
    d.rectangle([0, top_k, WIDTH, HEIGHT], fill=(20, 22, 25, 255))
    d.line([(0, top_k), (WIDTH, top_k)], fill=(50, 55, 62, 255), width=2)

    # Horizontal ventilation louvers
    for ly in range(top_k + 12, HEIGHT - 10, 8):
        d.line([(55, ly), (WIDTH - 55, ly)], fill=(8, 9, 11, 255), width=4)
        d.line([(55, ly + 2), (WIDTH - 55, ly + 2)], fill=(42, 46, 52, 255), width=1)

    # Carel/Eliwell Digital Thermostat Box
    tx, ty, tw, th = 110, top_k + 10, 96, 34
    d.rectangle([tx, ty, tx + tw, ty + th], fill=(12, 14, 16, 255), outline=(55, 62, 70, 255))
    d.rectangle([tx + 4, ty + 4, tx + tw - 4, ty + th - 4], fill=(6, 12, 8, 255))
    try:
        font_led = ImageFont.truetype("cour.ttf", 20)
    except:
        font_led = ImageFont.load_default()
    d.text((tx + 12, ty + 7), "3.2°C", fill=(50, 255, 120, 255), font=font_led)
    d.ellipse([tx + tw - 16, ty + 10, tx + tw - 10, ty + 16], fill=(40, 230, 255, 255))

    # 4. Outer Black Frame & Dual Sliding Door Structure
    frame_w = 30
    d.rectangle([0, marquee_h, frame_w, top_k], fill=(22, 24, 28, 255))
    d.rectangle([WIDTH - frame_w, marquee_h, WIDTH, top_k], fill=(22, 24, 28, 255))
    d.rectangle([frame_w, marquee_h, WIDTH - frame_w, top_k], outline=(65, 75, 88, 180), width=2)

    # Center Sliding Door Overlap Seam (coca3.JPG 2-door model)
    center_x = 600
    overlap_w = 14
    overlap_layer = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    ol_draw = ImageDraw.Draw(overlap_layer)
    ol_draw.rectangle([center_x - overlap_w//2, marquee_h + 2, center_x + overlap_w//2, top_k - 2], fill=(20, 24, 30, 75))
    ol_draw.line([(center_x - overlap_w//2, marquee_h + 2), (center_x - overlap_w//2, top_k - 2)], fill=(120, 140, 165, 110), width=1)
    ol_draw.line([(center_x + overlap_w//2, marquee_h + 2), (center_x + overlap_w//2, top_k - 2)], fill=(40, 48, 58, 130), width=1)
    
    # Handles on sliding doors
    for hx in [center_x - 18, center_x + 18]:
        ol_draw.rectangle([hx - 3, (marquee_h + top_k)//2 - 60, hx + 3, (marquee_h + top_k)//2 + 60], fill=(26, 28, 32, 175), outline=(80, 90, 105, 160))
    
    overlay = Image.alpha_composite(overlay, overlap_layer)

    # 5. Condensation droplets for intense round 4
    if is_intense:
        np.random.seed(42)
        drop_img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
        drop_draw = ImageDraw.Draw(drop_img)
        for _ in range(550):
            dx = int(np.random.uniform(frame_w + 10, WIDTH - frame_w - 10))
            dy = int(np.random.uniform(marquee_h + 10, top_k - 10))
            dr = int(np.random.uniform(2, 6))
            drop_draw.ellipse([dx - dr, dy - dr, dx + dr, dy + dr], fill=(255, 255, 255, int(np.random.uniform(45, 120))))
            drop_draw.ellipse([dx - dr + 1, dy - dr + 1, dx, dy], fill=(255, 255, 255, 160))
        overlay = Image.alpha_composite(overlay, drop_img)

    result = Image.alpha_composite(img, overlay)
    return result

def pack_shelf(base_img, shelf_y, items_spec, bg_items=None, x_start=55, x_end=1145):
    """
    Packs items continuously from x_start to x_end with ZERO gaps.
    items_spec: list of dicts:
      {
        'filename': '...',
        'target_h': 340,
        'brand': '...',
        'variant': '...',
        'package': '...',
        'distractor_label': '...',
        'target': bool
      }
    """
    # 1. Place background items if any (peeking behind tuppers, cans or quesos)
    if bg_items:
        from PIL import ImageEnhance
        for bg in bg_items:
            p = find_asset(bg['filename'])
            prod = Image.open(p).convert('RGBA')
            w, h = prod.size
            th = bg.get('target_h', 330)
            ratio = th / float(h)
            nw = max(10, int(w * ratio))
            nh = int(th)
            prod_scaled = prod.resize((nw, nh), Image.Resampling.LANCZOS)
            
            # Subtly shade background items for realistic depth without affecting alpha
            enhancer = ImageEnhance.Brightness(prod_scaled)
            prod_dimmed = enhancer.enhance(0.85)
            
            bx = int(bg['center_x'] - nw / 2)
            by = shelf_y - nh - 10
            base_img.paste(prod_dimmed, (bx, by), prod_dimmed)

    # 2. Measure all front items
    loaded = []
    total_w = 0
    for item in items_spec:
        p = find_asset(item['filename'])
        prod = Image.open(p).convert('RGBA')
        w, h = prod.size
        th = item['target_h']
        ratio = th / float(h)
        nw = max(10, int(w * ratio))
        nh = int(th)
        prod_scaled = prod.resize((nw, nh), Image.Resampling.LANCZOS)
        loaded.append((item, prod_scaled, nw, nh))
        total_w += nw

    n = len(loaded)
    avail_w = x_end - x_start
    overlap = (total_w - avail_w) / float(n - 1) if n > 1 else 0

    hotspots = []
    cur_x = float(x_start)

    for i, (item, prod_scaled, nw, nh) in enumerate(loaded):
        left_x = int(round(cur_x))
        top_y = shelf_y - nh + 8
        center_x = left_x + nw // 2

        # Soft realistic contact shadow on the white shelf rack
        shadow_w = int(nw * 0.92)
        shadow_h = int(nw * 0.22)
        shadow = Image.new('RGBA', (shadow_w, shadow_h), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.ellipse([0, 0, shadow_w, shadow_h], fill=(30, 48, 70, 130))
        shadow = shadow.filter(ImageFilter.GaussianBlur(3))
        base_img.paste(shadow, (int(center_x - shadow_w / 2), shelf_y - int(shadow_h / 2)), shadow)

        # Paste product
        base_img.paste(prod_scaled, (left_x, top_y), prod_scaled)

        # Bounding box percentages
        pct_x = round((left_x / WIDTH) * 100.0, 2)
        pct_y = round((top_y / HEIGHT) * 100.0, 2)
        pct_w = round((nw / WIDTH) * 100.0, 2)
        pct_h = round((nh / HEIGHT) * 100.0, 2)

        h_dict = {
            'x': pct_x,
            'y': pct_y,
            'width': pct_w,
            'height': pct_h,
            'brand': item['brand'],
            'variant': item['variant'],
            'package': item['package'],
            'name': f"{item['brand']} {item['variant']} ({item['package']})".strip(),
            'target': item.get('target', False)
        }
        if item.get('distractor_label'):
            h_dict['distractor_label'] = item['distractor_label']
        hotspots.append(h_dict)

        cur_x += (nw - overlap)

    return hotspots
