import os
import cv2
import numpy as np
from PIL import Image

BRAIN_DIR = r'C:\Users\User\.gemini\antigravity-ide\brain\41cc5522-44e5-4cef-be68-d5b77ff8a94f'
OUT_DIR = r'd:\PROYECTOS_PERSONALES\ir_challenge\assets_transparent'
os.makedirs(OUT_DIR, exist_ok=True)

ITEMS = [
    ('test_pecsi_1788628405611.jpg', 'pecsi-lata-355ml.png', 15),
    ('test_pecsi_botella_1788628667779.jpg', 'pecsi-botella-600ml.png', 15),
    ('test_devils_cola_1788628456190.jpg', 'devils-cola-botella-600ml.png', 15),
    ('test_queso_oaxaca_1788628514602.jpg', 'queso-oaxaca-bolsa.png', 15),
    ('test_pollo_rostizado_1788628528075.jpg', 'pollo-rostizado-bolsa.png', 15),
    ('test_tupper_comida_1788628651271.jpg', 'tupper-comida.png', 15)
]

def extract_grabcut(src_name, out_name, margin=15):
    src_path = os.path.join(BRAIN_DIR, src_name)
    out_path = os.path.join(OUT_DIR, out_name)
    
    img = cv2.imread(src_path)
    if img is None:
        print(f"ERROR: cannot read {src_path}")
        return
        
    h, w = img.shape[:2]
    
    mask = np.zeros(img.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    
    rect = (margin, margin, w - 2 * margin, h - 2 * margin)
    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 4, cv2.GC_INIT_WITH_RECT)
    
    # Foreground mask: where mask is FG (1) or Probable FG (3)
    fg_mask = np.where((mask == 1) | (mask == 3), 255, 0).astype('uint8')
    
    # Clean up small holes inside the object (closing)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    fg_closed = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
    
    # Find largest contour to remove stray background specks
    contours, _ = cv2.findContours(fg_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    final_mask = np.zeros_like(fg_closed)
    if contours:
        # Keep any contour with area > 2% of image
        for cnt in contours:
            if cv2.contourArea(cnt) > (w * h * 0.02):
                cv2.drawContours(final_mask, [cnt], -1, 255, -1)
    else:
        final_mask = fg_closed
        
    # Feather edge with 3x3 gaussian blur for crisp antialiasing
    alpha = cv2.GaussianBlur(final_mask, (3, 3), 0)
    
    # Crop to bounding box with 6px padding
    coords = cv2.findNonZero(final_mask)
    if coords is not None:
        bx, by, bw, bh = cv2.boundingRect(coords)
        bx = max(0, bx - 6)
        by = max(0, by - 6)
        bw = min(w - bx, bw + 12)
        bh = min(h - by, bh + 12)
        
        cropped_bgr = img[by:by+bh, bx:bx+bw]
        cropped_alpha = alpha[by:by+bh, bx:bx+bw]
    else:
        cropped_bgr = img
        cropped_alpha = alpha
        
    b, g, r = cv2.split(cropped_bgr)
    rgba = cv2.merge([r, g, b, cropped_alpha])
    
    pil_img = Image.fromarray(rgba)
    pil_img.save(out_path, 'PNG')
    nonzeros = (cropped_alpha > 50).sum()
    print(f"SUCCESS: {out_name} saved! Size={pil_img.size}, Solid pixels={nonzeros}")

def main():
    for src, out, m in ITEMS:
        extract_grabcut(src, out, m)
    print("All 6 distractors extracted with GrabCut!")

if __name__ == '__main__':
    main()
