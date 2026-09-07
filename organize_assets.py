import os
import shutil

BASE_DIR = r'd:\PROYECTOS_PERSONALES\ir_challenge'
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

RAW_SRC = os.path.join(BASE_DIR, 'asset_ir_challenge')
TRANS_SRC = os.path.join(BASE_DIR, 'assets_transparent')

# Target dirs
DIR_FRIDGES = os.path.join(ASSETS_DIR, 'fridges')
DIR_RAW = os.path.join(ASSETS_DIR, 'raw')
DIR_CUTOUTS = os.path.join(ASSETS_DIR, 'cutouts')
DIR_BEV = os.path.join(DIR_CUTOUTS, 'beverages')
DIR_PARODY = os.path.join(DIR_CUTOUTS, 'parody')
DIR_GROC = os.path.join(DIR_CUTOUTS, 'groceries')

for d in [DIR_FRIDGES, DIR_RAW, DIR_CUTOUTS, DIR_BEV, DIR_PARODY, DIR_GROC]:
    os.makedirs(d, exist_ok=True)

# 1. Copy/move raw assets from asset_ir_challenge to assets/raw
if os.path.exists(RAW_SRC):
    for f in os.listdir(RAW_SRC):
        sp = os.path.join(RAW_SRC, f)
        dp = os.path.join(DIR_RAW, f)
        if os.path.isfile(sp):
            shutil.copy2(sp, dp)
    print(f"Copied raw assets to {DIR_RAW}")

# 2. Categorize transparent cutouts into assets/cutouts/
GROCERY_FILES = {'queso-oaxaca-bolsa.png', 'pollo-rostizado-bolsa.png', 'tupper-comida.png'}
PARODY_FILES = {'pecsi-lata-355ml.png', 'pecsi-botella-600ml.png', 'devils-cola-botella-600ml.png'}

if os.path.exists(TRANS_SRC):
    for f in os.listdir(TRANS_SRC):
        sp = os.path.join(TRANS_SRC, f)
        if not os.path.isfile(sp) or not f.endswith('.png'):
            continue
        if f in GROCERY_FILES:
            target_dir = DIR_GROC
        elif f in PARODY_FILES:
            target_dir = DIR_PARODY
        else:
            target_dir = DIR_BEV
        shutil.copy2(sp, os.path.join(target_dir, f))
    print("Categorized cutouts into cutouts/beverages, cutouts/parody, cutouts/groceries")

# 3. Clean up root debug images
DEBUG_FILES = [
    'debug_crop1.png',
    'f2_shelf1_caps.png', 'f2_shelf2_caps.png', 'f2_shelf3_caps.png',
    'f4_shelf1_caps.png', 'f4_shelf2_caps.png', 'f4_shelf3_caps.png', 'f4_shelf4_caps.png',
    'shelf1_caps.png', 'shelf2_caps.png', 'shelf3_caps.png',
    'test_clean.png', 'test_fridge.jpg', 'test_white_cooler.png'
]
for df in DEBUG_FILES:
    dp = os.path.join(BASE_DIR, df)
    if os.path.exists(dp):
        try:
            os.remove(dp)
        except Exception:
            pass

print("Root directory cleaned up successfully!")
