# CLAUDE.md — Instrucciones operativas para IMAGE RECOGNITION: THE GAME

- **Juego en Vivo (GitHub Pages):** [https://jmtoral.github.io/ir-challenge/](https://jmtoral.github.io/ir-challenge/)
- **Repositorio GitHub:** [https://github.com/jmtoral/ir-challenge](https://github.com/jmtoral/ir-challenge)

## Qué es este proyecto

**IMAGE RECOGNITION: THE GAME** es una aplicación web interactiva tipo corporate arcade diseñada para entrenar y evaluar habilidades operativas de reconocimiento visual en anaquel y refrigeradores de bebidas comerciales (auditoría de anaquel / Image Recognition).

El jugador se enfrenta a escenarios fotográficos completos de enfriadores comerciales con productos visibles del portafolio, interactuando directamente sobre la imagen para identificar variantes, empaques y marcas bajo presión de tiempo con métricas reales de Computer Vision (**Precision**, **Recall**, **Accuracy**).

---

## Arquitectura del Juego

### 1. Escenarios Fotográficos y Rondas de Tiendita
- **Ronda 1 — Tiendita de Barrio (9.0s)**:
  - Imagen: `assets/fridge-01.png`
  - Misión: *"Encuentra todas las Coca-Cola Original"*
  - Desafío: Botellas apretadas en anaquel real. Primeros distractores de abarrotes (**Queso Oaxaca** en bolsa y **Tupper** con comida).
- **Ronda 2 — Guerra de Colas (8.5s)**:
  - Imagen: `assets/fridge-02.png`
  - Misión: *"Encuentra todas las Coca-Cola"* (Original y Sin Azúcar).
  - Desafío: Invasión de marcas parodia que engañan la vista: **Devil's Cola** (etiqueta roja muy similar) y **Pecsi** (botella y lata).
- **Ronda 3 — Desmadre en Anaquel (7.5s)**:
  - Imagen: `assets/fridge-03.png`
  - Misión: *"Encuentra todas las botellas Coca-Cola"*
  - Desafío: **Pollo Rostizado** en bolsa térmica ocupando anaquel; latas de Coca-Cola y Pecsi que deben discriminarse del formato botella.
- **Ronda 4 — Human Benchmark: Tiendita Extrema (6.0s)**:
  - Imagen: `assets/fridge-04.png`
  - Misión: *"Encuentra todas las Coca-Cola Original"*
  - Desafío: Máxima densidad (28+ items apiñados pegados hombro con hombro), pollo, queso, tupper, colas pirata y condensación densa sobre el cristal.

### 2. Hotspots y Coordenadas Relativas
- Mapeados en `hotspots.json` con porcentajes relativos (`x`, `y`, `width`, `height` de 0 a 100%) sobre la imagen base (1200×1600, proporción 3:4).
- Totalmente invisibles antes del primer clic.
- **Acierto (Target)**: Halo verde luminoso SVG/CSS + badge flotante animado `+100 Correcto` (~700ms) + audio armónico ascendente.
- **Falso Positivo (Distractor)**: Halo rojo con sacudida (*shake*) + badge flotante contextual (`−50 ¡Eso es Queso Oaxaca!`, `−50 ¡Es Devil's Cola!`, etc.) + zumbido grave.
- **Bonus de tiempo**: Si se encuentran todos los objetivos antes del límite, la ronda finaliza automáticamente sumando bonus proporcional a los segundos restantes.

### 3. Métricas de Visión Computacional
Al finalizar cada ronda y en el cierre global:
- **Precision**: $TP / (TP + FP)$
- **Recall**: $TP / (TP + FN)$
- **Accuracy**: $TP / (TP + FP + FN)$
- **Human Vision Benchmark**: Evaluación global al finalizar la 4ta ronda con asignación de rango (*Human Vision Engine*, *Vision Operator*, *Sharp Observer*, *Shelf Scanner*).

---

## Estructura del Proyecto

```
ir_challenge/
├── index.html              ← Punto de entrada HTML (layout 28% sidebar / 72% cooler)
├── style.css               ← Sistema de diseño Neobrutalista (rojo/negro/blanco, sombras duras, stickers)
├── game.js                 ← Motor de juego, cuenta regresiva 3s, hotspots, leaderboard y Web Audio API
├── hotspots.json           ← Coordenadas porcentuales y ground truth de las 4 rondas
├── manifest.json           ← Manifiesto de la aplicación web
├── assets/                 ← Recursos organizados y optimizados
│   ├── audio/              ← Pistas de soundtrack (final_boss_battle, playful_retro_arcade)
│   ├── cutouts/            ← Packshots y distractores con transparencia (beverages, groceries, parody)
│   ├── fridges/            ← Escenarios finales renderizados de refrigeradores
│   ├── raw/                ← Imágenes crudas de catálogo y referencia de enfriador (coca3.jpg)
│   ├── archive/            ← Archivo histórico de assets crudos y transparentes
│   └── fridge-01.png..04   ← Enlaces raíz retrocompatibles
├── scripts/                ← Scripts generadores y utilerías de Computer Vision
│   ├── build_fridges.py    ← Generador de los 4 escenarios de refrigerador
│   ├── packing_core.py     ← Motor de renderizado: marquesina, puertas dobles, parrillas
│   ├── fix_distractors_grabcut.py ← Limpieza de máscaras con GrabCut
│   ├── process_distractors.py     ← Procesamiento de distractores
│   └── organize_assets.py  ← Clasificación y organización de assets
├── server/                 ← Backend de Leaderboard Global (Cloudflare Workers + KV)
│   ├── worker.js           ← Código del Worker para API REST (/api/leaderboard, /api/score)
│   ├── wrangler.toml       ← Configuración de despliegue Cloudflare
│   └── README.md           ← Guía paso a paso para despliegue
├── CLAUDE.md               ← Este archivo de instrucciones operativas
├── README.md               ← Documentación general del proyecto y guía de uso
├── HANDOFF.md              ← Bitácora cronológica inmutable de sesiones de trabajo
├── SPEC.md                 ← Especificación funcional original
└── .gitignore
```

---

## Cómo Ejecutar Localmente

El juego requiere servirse vía HTTP (debido a la carga de `hotspots.json` vía `fetch`).

```powershell
# Opción 1: Node.js (ya probado y funcionando en el puerto 8080)
npx serve . -l 8080

# Opción 2: Python (usando el entorno conda si está disponible)
python -m http.server 8080
```

Abrir en navegador moderno en: **`http://localhost:8080/`** (optimizado para resolución de escritorio 16:9, 1366×768 a 1920×1080).

---

## Reglas para Agentes y Mantenimiento

1. **Uso de imágenes de marca**:
   - Uso interno como simulador de entrenamiento de auditoría de campo.
   - Las imágenes deben mantenerse libres de halos y con sus tapas/cabezas íntegras. El script `build_fridges.py` se encarga de posicionar los productos manteniendo holgura y proporciones exactas.
2. **Bitácora `HANDOFF.md`**:
   - **Regla estricta:** Al finalizar cada sesión se agrega una nueva entrada al final (`Entrada N`). Nunca se modifican ni eliminan entradas anteriores.
   - Toda decisión tomada o rechazada debe quedar registrada con su justificación.
3. **Sistema de Audio y Música**:
   - Efectos de sonido procedurales mediante Web Audio API (cero dependencias externas para respuestas instantáneas).
   - Música de fondo mediante `MusicPlayer` (`assets/audio/final_boss_battle.mp3`) con botón dedicado de pausa/reanudación (`#btn-music`) y volumen calibrado (0.35).
4. **Regeneración de escenarios con Python**:
   - Entorno Conda con OpenCV y Pillow: `conda activate computer_vision` -> `python build_fridges.py`.
5. **Permisos y comandos en el IDE**:
   - Los comandos de terminal disparan solicitudes de confirmación al usuario en el IDE. Preferir siempre la lectura y edición directa de archivos mediante las herramientas de workspace en lugar de ejecutar comandos de consola innecesarios.

