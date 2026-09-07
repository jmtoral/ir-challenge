import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from packing_core import create_cooler_base, apply_glass_and_reflections, pack_shelf, WIDTH, HEIGHT, ASSETS_DIR, OUT_DIR, FRIDGES_DIR

def generate_all():
    rounds_data = {}

    # =========================================================================
    # ROUND 1: Fridge 1 — Tiendita de Barrio: Invasión de Abarrotes
    # Misión: "Encuentra todas las Coca-Cola Original" (Botellas vidrio / PET)
    # Totalmente lleno: Tupper en repisa 1, Queso Oaxaca en repisa 2, 0 espacios vacíos
    # =========================================================================
    shelves_1 = [480, 980, 1480]
    base_1 = create_cooler_base(shelves_1)
    hotspots_1 = []

    # Shelf 1 (y=480): Tupper + 7 botellas (8 front items + 2 fondo)
    s1_front = [
        {'filename': 'sprite-limon-lima-600ml-pet.png', 'target_h': 350, 'brand': 'Sprite', 'variant': 'Limon-Lima', 'package': 'Bottle', 'target': False},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'fanta-sabor-naranja-1-5-l-pet.png', 'target_h': 350, 'brand': 'Fanta', 'variant': 'Naranja', 'package': 'Bottle', 'target': False},
        {'filename': 'tupper-comida.png', 'target_h': 210, 'brand': 'Abarrotes', 'variant': 'Tupper', 'package': 'Tupper', 'target': False, 'distractor_label': '¡Eso es un Tupper!'},
        {'filename': 'coca-cola-original-235ml-vidrio.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'sidral-mundet-manzana-600ml-pet.png', 'target_h': 350, 'brand': 'Sidral Mundet', 'variant': 'Manzana', 'package': 'Bottle', 'target': False},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'sprite-limon-lima-600ml-pet.png', 'target_h': 350, 'brand': 'Sprite', 'variant': 'Limon-Lima', 'package': 'Bottle', 'target': False}
    ]
    s1_bg = [
        {'filename': 'sidral-mundet-manzana-600ml-pet.png', 'center_x': 490, 'target_h': 330},
        {'filename': 'ameyal-sabor-limon-600ml-pet.png', 'center_x': 630, 'target_h': 330}
    ]
    hotspots_1.extend(pack_shelf(base_1, 480, s1_front, s1_bg))

    # Shelf 2 (y=980): Queso Oaxaca + 9 botellas (10 front items + 1 fondo)
    s2_front = [
        {'filename': 'coca-cola-original-235ml-vidrio.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'ameyal-sabor-limon-600ml-pet.png', 'target_h': 350, 'brand': 'Ameyal', 'variant': 'Limon', 'package': 'Bottle', 'target': False},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'queso-oaxaca-bolsa.png', 'target_h': 250, 'brand': 'Abarrotes', 'variant': 'Queso Oaxaca', 'package': 'Bolsa', 'target': False, 'distractor_label': '¡Eso es Queso Oaxaca!'},
        {'filename': 'coca-cola-original-235ml-vidrio.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'fanta-sabor-fresa-1-5-l-pet.png', 'target_h': 350, 'brand': 'Fanta', 'variant': 'Fresa', 'package': 'Bottle', 'target': False},
        {'filename': 'sprite-limon-lima-2l-pet.png', 'target_h': 360, 'brand': 'Sprite', 'variant': 'Limon-Lima', 'package': 'Bottle', 'target': False},
        {'filename': 'coca-cola-sin-azucar-235-ml.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Bottle', 'target': False},
        {'filename': 'sidral-mundet-manzana-600ml-pet.png', 'target_h': 350, 'brand': 'Sidral Mundet', 'variant': 'Manzana', 'package': 'Bottle', 'target': False},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True}
    ]
    s2_bg = [
        {'filename': 'fanta-sabor-fresa-1-5-l-pet.png', 'center_x': 450, 'target_h': 330}
    ]
    hotspots_1.extend(pack_shelf(base_1, 980, s2_front, s2_bg))

    # Shelf 3 (y=1480): 11 botellas apretadas hombro con hombro
    s3_front = [
        {'filename': 'sidral-mundet-manzana-verde-600ml-pet.png', 'target_h': 350, 'brand': 'Sidral Mundet', 'variant': 'Manzana Verde', 'package': 'Bottle', 'target': False},
        {'filename': 'coca-cola-original-235ml-vidrio.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'coca-cola-sin-azucar-235-ml.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Bottle', 'target': False},
        {'filename': 'ameyal-sabor-sandia-2l-pet.png', 'target_h': 360, 'brand': 'Ameyal', 'variant': 'Sandia', 'package': 'Bottle', 'target': False},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'sidral-mundet-manzana-600ml-pet.png', 'target_h': 350, 'brand': 'Sidral Mundet', 'variant': 'Manzana', 'package': 'Bottle', 'target': False},
        {'filename': 'coca-cola-original-235ml-vidrio.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'fanta-sabor-naranja-1-5-l-pet.png', 'target_h': 350, 'brand': 'Fanta', 'variant': 'Naranja', 'package': 'Bottle', 'target': False},
        {'filename': 'ameyal-sabor-uva-2l-pet.png', 'target_h': 360, 'brand': 'Ameyal', 'variant': 'Uva', 'package': 'Bottle', 'target': False},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'sprite-limon-lima-600ml-pet.png', 'target_h': 350, 'brand': 'Sprite', 'variant': 'Limon-Lima', 'package': 'Bottle', 'target': False}
    ]
    hotspots_1.extend(pack_shelf(base_1, 1480, s3_front))

    fridge_1 = apply_glass_and_reflections(base_1)
    fridge_1.convert('RGB').save(os.path.join(OUT_DIR, 'fridge-01.png'), 'PNG')
    fridge_1.convert('RGB').save(os.path.join(FRIDGES_DIR, 'fridge-01.png'), 'PNG')
    print('fridge-01.png created (White Coca-Cola interior, 100% abarrotado)')

    rounds_data['round1'] = {
        'id': 1,
        'title': 'Ronda 1 — Tiendita de Barrio',
        'mission': 'Encuentra todas las Coca-Cola Original',
        'subtext': 'Anaqueles 100% llenos de tiendita. ¡Cuidado con el Tupper y el Queso Oaxaca!',
        'time': 10.0,
        'image': 'assets/fridge-01.png',
        'hotspots': hotspots_1,
        'target_count': sum(1 for h in hotspots_1 if h['target'])
    }

    # =========================================================================
    # ROUND 2: Fridge 2 — Guerra de Colas: Cuidado con las Copias
    # Misión: "Encuentra todas las Coca-Cola" (Original y Sin Azúcar)
    # Totalmente lleno: Devil's Cola y Pecsi invadiendo el anaquel
    # =========================================================================
    shelves_2 = [480, 980, 1480]
    base_2 = create_cooler_base(shelves_2)
    hotspots_2 = []

    # Shelf 1 (y=480): 11 items (Devil's Cola + Pecsi lata/botella + Coca-Cola + Fanta/Sprite)
    s2_1_front = [
        {'filename': 'coca-cola-sin-azucar-235-ml.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Bottle', 'target': True},
        {'filename': 'devils-cola-botella-600ml.png', 'target_h': 350, 'brand': "Devil's Cola", 'variant': 'Cola', 'package': 'Bottle', 'target': False, 'distractor_label': "¡Es Devil's Cola, no Coca-Cola!"},
        {'filename': 'sprite-limon-lima-600ml-pet.png', 'target_h': 350, 'brand': 'Sprite', 'variant': 'Limon-Lima', 'package': 'Bottle', 'target': False},
        {'filename': 'coca-cola-original-235ml-vidrio.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'pecsi-lata-355ml.png', 'target_h': 230, 'brand': 'Pecsi', 'variant': 'Cola', 'package': 'Can', 'target': False, 'distractor_label': '¡Es Pecsi, no Coca-Cola!'},
        {'filename': 'coccolsinazu-sinazuc-nor-alu-235ml-8pz_3.png', 'target_h': 230, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Can', 'target': True},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'devils-cola-botella-600ml.png', 'target_h': 350, 'brand': "Devil's Cola", 'variant': 'Cola', 'package': 'Bottle', 'target': False, 'distractor_label': "¡Es Devil's Cola, no Coca-Cola!"},
        {'filename': 'coca-cola-sin-azucar-235-ml.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Bottle', 'target': True},
        {'filename': 'fanta-sabor-naranja-1-5-l-pet.png', 'target_h': 350, 'brand': 'Fanta', 'variant': 'Naranja', 'package': 'Bottle', 'target': False},
        {'filename': 'pecsi-botella-600ml.png', 'target_h': 350, 'brand': 'Pecsi', 'variant': 'Cola', 'package': 'Bottle', 'target': False, 'distractor_label': '¡Es Pecsi, no Coca-Cola!'}
    ]
    s2_1_bg = [
        {'filename': 'sidral-mundet-manzana-600ml-pet.png', 'center_x': 500, 'target_h': 330},
        {'filename': 'fanta-sabor-fresa-1-5-l-pet.png', 'center_x': 620, 'target_h': 330}
    ]
    hotspots_2.extend(pack_shelf(base_2, 480, s2_1_front, s2_1_bg))

    # Shelf 2 (y=980): 11 items
    s2_2_front = [
        {'filename': 'sidral-mundet-manzana-600ml-pet.png', 'target_h': 350, 'brand': 'Sidral Mundet', 'variant': 'Manzana', 'package': 'Bottle', 'target': False},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'pecsi-botella-600ml.png', 'target_h': 350, 'brand': 'Pecsi', 'variant': 'Cola', 'package': 'Bottle', 'target': False, 'distractor_label': '¡Es Pecsi, no Coca-Cola!'},
        {'filename': 'coca-cola-sin-azucar-235-ml.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Bottle', 'target': True},
        {'filename': 'ameyal-sabor-fresa-kiwi-2-l.png', 'target_h': 360, 'brand': 'Ameyal', 'variant': 'Fresa-Kiwi', 'package': 'Bottle', 'target': False},
        {'filename': 'devils-cola-botella-600ml.png', 'target_h': 350, 'brand': "Devil's Cola", 'variant': 'Cola', 'package': 'Bottle', 'target': False, 'distractor_label': "¡Es Devil's Cola, no Coca-Cola!"},
        {'filename': 'coca-cola-original-235ml-vidrio.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'sprite-limon-lima-2l-pet.png', 'target_h': 360, 'brand': 'Sprite', 'variant': 'Limon-Lima', 'package': 'Bottle', 'target': False},
        {'filename': 'pecsi-botella-600ml.png', 'target_h': 350, 'brand': 'Pecsi', 'variant': 'Cola', 'package': 'Bottle', 'target': False, 'distractor_label': '¡Es Pecsi, no Coca-Cola!'},
        {'filename': 'coca-cola-sin-azucar-235-ml.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Bottle', 'target': True},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True}
    ]
    hotspots_2.extend(pack_shelf(base_2, 980, s2_2_front))

    # Shelf 3 (y=1480): Tupper + 8 items (total 9 items)
    s2_3_front = [
        {'filename': 'tupper-comida.png', 'target_h': 210, 'brand': 'Abarrotes', 'variant': 'Tupper', 'package': 'Tupper', 'target': False, 'distractor_label': '¡Eso es un Tupper!'},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'pecsi-lata-355ml.png', 'target_h': 230, 'brand': 'Pecsi', 'variant': 'Cola', 'package': 'Can', 'target': False, 'distractor_label': '¡Es Pecsi, no Coca-Cola!'},
        {'filename': 'coca-cola-sin-azucar-235-ml.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Bottle', 'target': True},
        {'filename': 'devils-cola-botella-600ml.png', 'target_h': 350, 'brand': "Devil's Cola", 'variant': 'Cola', 'package': 'Bottle', 'target': False, 'distractor_label': "¡Es Devil's Cola, no Coca-Cola!"},
        {'filename': 'coca-cola-original-235ml-vidrio.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'ameyal-sabor-uva-2l-pet.png', 'target_h': 360, 'brand': 'Ameyal', 'variant': 'Uva', 'package': 'Bottle', 'target': False},
        {'filename': 'sidral-mundet-manzana-355ml-lata.png', 'target_h': 230, 'brand': 'Sidral Mundet', 'variant': 'Manzana', 'package': 'Can', 'target': False},
        {'filename': 'coca-cola-sin-azucar-235-ml.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Bottle', 'target': True}
    ]
    s2_3_bg = [
        {'filename': 'fanta-sabor-naranja-1-5-l-pet.png', 'center_x': 180, 'target_h': 330},
        {'filename': 'ameyal-sabor-limon-600ml-pet.png', 'center_x': 290, 'target_h': 330}
    ]
    hotspots_2.extend(pack_shelf(base_2, 1480, s2_3_front, s2_3_bg))

    fridge_2 = apply_glass_and_reflections(base_2)
    fridge_2.convert('RGB').save(os.path.join(OUT_DIR, 'fridge-02.png'), 'PNG')
    fridge_2.convert('RGB').save(os.path.join(FRIDGES_DIR, 'fridge-02.png'), 'PNG')
    print('fridge-02.png created (Guerra de Colas abarrotado)')

    rounds_data['round2'] = {
        'id': 2,
        'title': 'Ronda 2 — Guerra de Colas',
        'mission': 'Encuentra todas las Coca-Cola',
        'subtext': '¡No te confundas con Devil\'s Cola ni Pecsi! Solo productos Coca-Cola (Original y Sin Azúcar).',
        'time': 9.0,
        'image': 'assets/fridge-02.png',
        'hotspots': hotspots_2,
        'target_count': sum(1 for h in hotspots_2 if h['target'])
    }

    # =========================================================================
    # ROUND 3: Fridge 3 — Desmadre en Anaquel
    # Misión: "Encuentra todas las botellas Coca-Cola"
    # Totalmente lleno: Pollo Rostizado en repisa 2, latas vs botellas, 0 espacios vacíos
    # =========================================================================
    shelves_3 = [480, 980, 1480]
    base_3 = create_cooler_base(shelves_3)
    hotspots_3 = []

    # Shelf 1 (y=480): 11 items
    s3_1_front = [
        {'filename': 'coca-cola-original-235ml-vidrio.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'coccolsinazu-sinazuc-nor-alu-235ml-8pz_3.png', 'target_h': 230, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Can', 'target': False, 'distractor_label': '¡Es una lata, no una botella!'},
        {'filename': 'pecsi-botella-600ml.png', 'target_h': 350, 'brand': 'Pecsi', 'variant': 'Cola', 'package': 'Bottle', 'target': False, 'distractor_label': '¡Es Pecsi!'},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'sprite_355ml_12_lata-100-parent_1.png', 'target_h': 230, 'brand': 'Sprite', 'variant': 'Limon-Lima', 'package': 'Can', 'target': False},
        {'filename': 'coca-cola-sin-azucar-235-ml.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Bottle', 'target': True},
        {'filename': 'sidral-mundet-manzana-355ml-lata.png', 'target_h': 230, 'brand': 'Sidral Mundet', 'variant': 'Manzana', 'package': 'Can', 'target': False},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'pecsi-lata-355ml.png', 'target_h': 230, 'brand': 'Pecsi', 'variant': 'Cola', 'package': 'Can', 'target': False, 'distractor_label': '¡Es Pecsi!'},
        {'filename': 'fanta-sabor-naranja-1-5-l-pet.png', 'target_h': 350, 'brand': 'Fanta', 'variant': 'Naranja', 'package': 'Bottle', 'target': False},
        {'filename': 'coca-cola-sin-azucar-235-ml.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Bottle', 'target': True}
    ]
    s3_1_bg = [
        {'filename': 'sprite-limon-lima-600ml-pet.png', 'center_x': 210, 'target_h': 330},
        {'filename': 'ameyal-sabor-limon-600ml-pet.png', 'center_x': 510, 'target_h': 330},
        {'filename': 'fanta-sabor-fresa-1-5-l-pet.png', 'center_x': 710, 'target_h': 330}
    ]
    hotspots_3.extend(pack_shelf(base_3, 480, s3_1_front, s3_1_bg))

    # Shelf 2 (y=980): Pollo Rostizado (h=310) + 8 botellas (9 front items + 2 fondo)
    s3_2_front = [
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'devils-cola-botella-600ml.png', 'target_h': 350, 'brand': "Devil's Cola", 'variant': 'Cola', 'package': 'Bottle', 'target': False, 'distractor_label': "¡Es Devil's Cola!"},
        {'filename': 'pollo-rostizado-bolsa.png', 'target_h': 310, 'brand': 'Abarrotes', 'variant': 'Pollo Rostizado', 'package': 'Bolsa', 'target': False, 'distractor_label': '¡Eso es un Pollo Rostizado!'},
        {'filename': 'coccolsinazu-sinazuc-nor-alu-235ml-8pz_3.png', 'target_h': 230, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Can', 'target': False, 'distractor_label': '¡Es una lata, no una botella!'},
        {'filename': 'coca-cola-sin-azucar-235-ml.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Bottle', 'target': True},
        {'filename': 'devils-cola-botella-600ml.png', 'target_h': 350, 'brand': "Devil's Cola", 'variant': 'Cola', 'package': 'Bottle', 'target': False, 'distractor_label': "¡Es Devil's Cola!"},
        {'filename': 'coca-cola-original-235ml-vidrio.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'sprite-limon-lima-600ml-pet.png', 'target_h': 350, 'brand': 'Sprite', 'variant': 'Limon-Lima', 'package': 'Bottle', 'target': False},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True}
    ]
    s3_2_bg = [
        {'filename': 'sidral-mundet-manzana-600ml-pet.png', 'center_x': 360, 'target_h': 330},
        {'filename': 'ameyal-sabor-uva-2l-pet.png', 'center_x': 540, 'target_h': 330}
    ]
    hotspots_3.extend(pack_shelf(base_3, 980, s3_2_front, s3_2_bg))

    # Shelf 3 (y=1480): Queso Oaxaca + 9 botellas y latas (10 front items)
    s3_3_front = [
        {'filename': 'sidral-mundet-manzana-600ml-pet.png', 'target_h': 350, 'brand': 'Sidral Mundet', 'variant': 'Manzana', 'package': 'Bottle', 'target': False},
        {'filename': 'pecsi-lata-355ml.png', 'target_h': 230, 'brand': 'Pecsi', 'variant': 'Cola', 'package': 'Can', 'target': False, 'distractor_label': '¡Es Pecsi!'},
        {'filename': 'coca-cola-original-235ml-vidrio.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'queso-oaxaca-bolsa.png', 'target_h': 250, 'brand': 'Abarrotes', 'variant': 'Queso Oaxaca', 'package': 'Bolsa', 'target': False, 'distractor_label': '¡Eso es Queso Oaxaca!'},
        {'filename': 'coca-cola-sin-azucar-235-ml.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Bottle', 'target': True},
        {'filename': 'ameyal-sabor-limon-600ml-pet.png', 'target_h': 350, 'brand': 'Ameyal', 'variant': 'Limon', 'package': 'Bottle', 'target': False},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'coccolsinazu-sinazuc-nor-alu-235ml-8pz_3.png', 'target_h': 230, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Can', 'target': False, 'distractor_label': '¡Es una lata, no una botella!'},
        {'filename': 'coca-cola-original-235ml-vidrio.png', 'target_h': 340, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'fanta-sabor-fresa-1-5-l-pet.png', 'target_h': 350, 'brand': 'Fanta', 'variant': 'Fresa', 'package': 'Bottle', 'target': False}
    ]
    s3_3_bg = [
        {'filename': 'sprite-limon-lima-2l-pet.png', 'center_x': 450, 'target_h': 330}
    ]
    hotspots_3.extend(pack_shelf(base_3, 1480, s3_3_front, s3_3_bg))

    fridge_3 = apply_glass_and_reflections(base_3)
    fridge_3.convert('RGB').save(os.path.join(OUT_DIR, 'fridge-03.png'), 'PNG')
    fridge_3.convert('RGB').save(os.path.join(FRIDGES_DIR, 'fridge-03.png'), 'PNG')
    print('fridge-03.png created (Desmadre en anaquel abarrotado)')

    rounds_data['round3'] = {
        'id': 3,
        'title': 'Ronda 3 — Desmadre en Anaquel',
        'mission': 'Encuentra todas las botellas Coca-Cola',
        'subtext': 'Solo BOTELLAS Coca-Cola. Ignora las latas, el pollo rostizado y la competencia.',
        'time': 8.5,
        'image': 'assets/fridge-03.png',
        'hotspots': hotspots_3,
        'target_count': sum(1 for h in hotspots_3 if h['target'])
    }

    # =========================================================================
    # ROUND 4: Fridge 4 — HUMAN BENCHMARK: Tiendita Extrema
    # Misión: "Encuentra todas las Coca-Cola Original"
    # 4 anaqueles ultra apretados (42 productos totales), condensación, 0 espacios vacíos
    # =========================================================================
    shelves_4 = [380, 780, 1180, 1530]
    base_4 = create_cooler_base(shelves_4, is_intense=True)
    hotspots_4 = []

    # Shelf 1 (y=380, h=260): Tupper + 9 items (total 10 items)
    s4_1_front = [
        {'filename': 'sprite-limon-lima-600ml-pet.png', 'target_h': 260, 'brand': 'Sprite', 'variant': 'Limon-Lima', 'package': 'Bottle', 'target': False},
        {'filename': 'devils-cola-botella-600ml.png', 'target_h': 260, 'brand': "Devil's Cola", 'variant': 'Cola', 'package': 'Bottle', 'target': False, 'distractor_label': "¡Es Devil's Cola!"},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 260, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'tupper-comida.png', 'target_h': 180, 'brand': 'Abarrotes', 'variant': 'Tupper', 'package': 'Tupper', 'target': False, 'distractor_label': '¡Eso es un Tupper!'},
        {'filename': 'coca-cola-sin-azucar-235-ml.png', 'target_h': 250, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Bottle', 'target': False},
        {'filename': 'pecsi-lata-355ml.png', 'target_h': 190, 'brand': 'Pecsi', 'variant': 'Cola', 'package': 'Can', 'target': False, 'distractor_label': '¡Es Pecsi!'},
        {'filename': 'coca-cola-original-235ml-vidrio.png', 'target_h': 250, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'sidral-mundet-manzana-600ml-pet.png', 'target_h': 260, 'brand': 'Sidral Mundet', 'variant': 'Manzana', 'package': 'Bottle', 'target': False},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 260, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'fanta-sabor-naranja-1-5-l-pet.png', 'target_h': 260, 'brand': 'Fanta', 'variant': 'Naranja', 'package': 'Bottle', 'target': False}
    ]
    s4_1_bg = [
        {'filename': 'ameyal-sabor-limon-600ml-pet.png', 'center_x': 450, 'target_h': 250}
    ]
    hotspots_4.extend(pack_shelf(base_4, 380, s4_1_front, s4_1_bg))

    # Shelf 2 (y=780, h=260): Queso Oaxaca + 9 items (total 10 items)
    s4_2_front = [
        {'filename': 'coca-cola-sin-azucar-235-ml.png', 'target_h': 250, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Bottle', 'target': False},
        {'filename': 'queso-oaxaca-bolsa.png', 'target_h': 210, 'brand': 'Abarrotes', 'variant': 'Queso Oaxaca', 'package': 'Bolsa', 'target': False, 'distractor_label': '¡Eso es Queso Oaxaca!'},
        {'filename': 'coca-cola-original-235ml-vidrio.png', 'target_h': 250, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'pecsi-botella-600ml.png', 'target_h': 260, 'brand': 'Pecsi', 'variant': 'Cola', 'package': 'Bottle', 'target': False, 'distractor_label': '¡Es Pecsi!'},
        {'filename': 'sprite_355ml_12_lata-100-parent_1.png', 'target_h': 190, 'brand': 'Sprite', 'variant': 'Limon-Lima', 'package': 'Can', 'target': False},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 260, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'devils-cola-botella-600ml.png', 'target_h': 260, 'brand': "Devil's Cola", 'variant': 'Cola', 'package': 'Bottle', 'target': False, 'distractor_label': "¡Es Devil's Cola!"},
        {'filename': 'sidral-mundet-manzana-600ml-pet.png', 'target_h': 260, 'brand': 'Sidral Mundet', 'variant': 'Manzana', 'package': 'Bottle', 'target': False},
        {'filename': 'coca-cola-original-235ml-vidrio.png', 'target_h': 250, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'ameyal-sabor-uva-2l-pet.png', 'target_h': 260, 'brand': 'Ameyal', 'variant': 'Uva', 'package': 'Bottle', 'target': False}
    ]
    s4_2_bg = [
        {'filename': 'fanta-sabor-fresa-1-5-l-pet.png', 'center_x': 270, 'target_h': 250}
    ]
    hotspots_4.extend(pack_shelf(base_4, 780, s4_2_front, s4_2_bg))

    # Shelf 3 (y=1180, h=260): Pollo Rostizado + 8 items (total 9 items)
    s4_3_front = [
        {'filename': 'pollo-rostizado-bolsa.png', 'target_h': 250, 'brand': 'Abarrotes', 'variant': 'Pollo Rostizado', 'package': 'Bolsa', 'target': False, 'distractor_label': '¡Eso es un Pollo Rostizado!'},
        {'filename': 'coca-cola-sin-azucar-235-ml.png', 'target_h': 250, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Bottle', 'target': False},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 260, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'sidral-mundet-manzana-355ml-lata.png', 'target_h': 190, 'brand': 'Sidral Mundet', 'variant': 'Manzana', 'package': 'Can', 'target': False},
        {'filename': 'coca-cola-original-235ml-vidrio.png', 'target_h': 250, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'pecsi-botella-600ml.png', 'target_h': 260, 'brand': 'Pecsi', 'variant': 'Cola', 'package': 'Bottle', 'target': False, 'distractor_label': '¡Es Pecsi!'},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 260, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'ameyal-sabor-limon-600ml-pet.png', 'target_h': 260, 'brand': 'Ameyal', 'variant': 'Limon', 'package': 'Bottle', 'target': False},
        {'filename': 'sprite-limon-lima-2l-pet.png', 'target_h': 260, 'brand': 'Sprite', 'variant': 'Limon-Lima', 'package': 'Bottle', 'target': False}
    ]
    s4_3_bg = [
        {'filename': 'fanta-sabor-naranja-1-5-l-pet.png', 'center_x': 200, 'target_h': 250}
    ]
    hotspots_4.extend(pack_shelf(base_4, 1180, s4_3_front, s4_3_bg))

    # Shelf 4 (y=1530, h=260): Tupper + 9 items (total 10 items)
    s4_4_front = [
        {'filename': 'sidral-mundet-manzana-verde-600ml-pet.png', 'target_h': 260, 'brand': 'Sidral Mundet', 'variant': 'Manzana Verde', 'package': 'Bottle', 'target': False},
        {'filename': 'coccolsinazu-sinazuc-nor-alu-235ml-8pz_3.png', 'target_h': 190, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Can', 'target': False},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 260, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'pecsi-botella-600ml.png', 'target_h': 260, 'brand': 'Pecsi', 'variant': 'Cola', 'package': 'Bottle', 'target': False, 'distractor_label': '¡Es Pecsi!'},
        {'filename': 'tupper-comida.png', 'target_h': 180, 'brand': 'Abarrotes', 'variant': 'Tupper', 'package': 'Tupper', 'target': False, 'distractor_label': '¡Eso es un Tupper!'},
        {'filename': 'coca-cola-original-235ml-vidrio.png', 'target_h': 250, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'devils-cola-botella-600ml.png', 'target_h': 260, 'brand': "Devil's Cola", 'variant': 'Cola', 'package': 'Bottle', 'target': False, 'distractor_label': "¡Es Devil's Cola!"},
        {'filename': 'coca-cola-sin-azucar-235-ml.png', 'target_h': 250, 'brand': 'Coca-Cola', 'variant': 'Sin Azucar', 'package': 'Bottle', 'target': False},
        {'filename': 'coca-cola-original-250-ml-pet.png', 'target_h': 260, 'brand': 'Coca-Cola', 'variant': 'Original', 'package': 'Bottle', 'target': True},
        {'filename': 'fanta-sabor-fresa-1-5-l-pet.png', 'target_h': 260, 'brand': 'Fanta', 'variant': 'Fresa', 'package': 'Bottle', 'target': False}
    ]
    s4_4_bg = [
        {'filename': 'ameyal-sabor-sandia-2l-pet.png', 'center_x': 570, 'target_h': 250}
    ]
    hotspots_4.extend(pack_shelf(base_4, 1530, s4_4_front, s4_4_bg))

    fridge_4 = apply_glass_and_reflections(base_4, is_intense=True)
    fridge_4.convert('RGB').save(os.path.join(OUT_DIR, 'fridge-04.png'), 'PNG')
    fridge_4.convert('RGB').save(os.path.join(FRIDGES_DIR, 'fridge-04.png'), 'PNG')
    print('fridge-04.png created (Tiendita Extrema 100% abarrotado)')

    rounds_data['round4'] = {
        'id': 4,
        'title': 'Ronda 4 — HUMAN BENCHMARK: Tiendita Extrema',
        'mission': 'Encuentra todas las Coca-Cola Original',
        'subtext': 'Máximo caos de tiendita: 4 anaqueles repletos de borde a borde, abarrotes y marcas pirata.',
        'time': 7.0,
        'image': 'assets/fridge-04.png',
        'hotspots': hotspots_4,
        'target_count': sum(1 for h in hotspots_4 if h['target'])
    }

    # Export hotspots metadata
    with open(r'd:\PROYECTOS_PERSONALES\ir_challenge\hotspots.json', 'w', encoding='utf-8') as f:
        json.dump(rounds_data, f, indent=2, ensure_ascii=False)
    print('hotspots.json created successfully with zero empty spaces!')

if __name__ == '__main__':
    generate_all()
