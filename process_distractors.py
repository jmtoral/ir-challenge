import os
import cv2
import numpy as np
from PIL import Image

BRAIN_DIR = r'C:\Users\User\.gemini\antigravity-ide\brain\41cc5522-44e5-4cef-be68-d5b77ff8a94f'
OUT_DIR = r'd:\PROYECTOS_PERSONALES\ir_challenge\assets_transparent'
os.makedirs(OUT_DIR, exist_ok=True)

ITEMS = [
    ('test_pecsi_1788628405611.jpg', 'pecsi-lata-355ml.png'),
    ('test_pecsi_botella_1788628667779.jpg', 'pecsi-botella-600ml.png'),
    ('test_devils_cola_1788628456190.jpg', 'devils-cola-botella-600ml.png'),
    ('test_queso_oaxaca_1788628514602.jpg', 'queso-oaxaca-bolsa.png'),
    ('test_pollo_rostizado_1788628528075.jpg', 'pollo-rostizado-bolsa.png'),
    ('test_tupper_comida_1788628651271.jpg', 'tupper-comida.png')
]

def process_item(src_name, out_name):
    src_path = os.path.join(BRAIN_DIR, src_name)
    out_path = os.path.join(OUT_DIR, out_name)
    
    img = cv2.imread(src_path)
    if img is None:
        print(f"Error loading {src_path}")
        return
        
    h, w = img.shape[:2]
    # Check background corners
    corners = [img[0, 0], img[0, w-1], img[h-1, 0], img[h-1, w-1]]
    bg_color = np.mean(corners, axis=0)
    
    # Calculate difference from white/background
    diff = np.max(np.abs(img.astype(float) - [255, 255, 255]), axis=2)
    
    # Floodfill from edges to find outside background only
    # Add a 1px border for floodfill
    padded = cv2.copyMakeBorder(img, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[255, 255, 255])
    mask = np.zeros((h + 4, w + 4), np.uint8)
    
    # Floodfill from (0,0) on padded
    # Tolerance of 25 for near-white
    cv2.floodFill(padded, mask, (0, 0), [0, 0, 0], loDiff=(18, 18, 18), upDiff=(18, 18, 18), flags=cv2.FLOODFILL_MASK_ONLY | (255 << 8))
    bg_mask = mask[2:-2, 2:-2] == 255
    
    # Alpha channel: 0 where background, 255 where foreground
    alpha = np.where(bg_mask, 0, 255).astype(np.uint8)
    
    # For bottles (pecsi bottle, devils cola), make sure the cap area is not pierced
    if 'botella' in out_name:
        cap_x1, cap_x2 = int(w * 0.35), int(w * 0.65)
        cap_y1, cap_y2 = int(h * 0.02), int(h * 0.18)
        alpha[cap_y1:cap_y2, cap_x1:cap_x2] = np.maximum(alpha[cap_y1:cap_y2, cap_x1:cap_x2], 255)
    
    # Smooth edges with slight blur on alpha
    alpha_blurred = cv2.GaussianBlur(alpha, (3, 3), 0)
    
    # Crop to bounding box of object with 4px margin
    coords = cv2.findNonZero(alpha)
    if coords is not None:
        bx, by, bw, bh = cv2.boundingRect(coords)
        bx = max(0, bx - 4)
        by = max(0, by - 4)
        bw = min(w - bx, bw + 8)
        bh = min(h - by, bh + 8)
        
        cropped_bgr = img[by:by+bh, bx:bx+bw]
        cropped_alpha = alpha_blurred[by:by+bh, bx:bx+bw]
    else:
        cropped_bgr = img
        cropped_alpha = alpha_blurred
        
    b, g, r = cv2.split(cropped_bgr)
    rgba = cv2.merge([r, g, b, cropped_alpha])
    
    pil_img = Image.fromarray(rgba)
    pil_img.save(out_path, 'PNG')
    print(f"Saved {out_name} (size: {pil_img.size})")

def main():
    for src, out in ITEMS:
        process_item(src, out)
    print("All distractors processed!")

if __name__ == '__main__':
    main()
