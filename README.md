# IMAGE RECOGNITION: THE GAME

> **Spot it. Classify it. Beat the clock.**

- **Juego en Vivo (GitHub Pages):** [https://jmtoral.github.io/ir-challenge/](https://jmtoral.github.io/ir-challenge/)
- **Repositorio Oficial:** [https://github.com/jmtoral/ir-challenge](https://github.com/jmtoral/ir-challenge)

Un simulador interactivo tipo arcade corporativo diseñado para entrenar la agudeza visual de personal de campo en la auditoría de anaquel y refrigeradores comerciales de bebidas, conectando la experiencia de juego con métricas operacionales reales de **Computer Vision** / **Image Recognition (IR)**.

---

## Características Principales

- **Diseño Visual Neobrutalista (Neo-Brutalism Pop Arcade):** Interfaz gráfica de alto impacto inspirada en el neobrutalismo, con paleta de rojo carmesí Coca-Cola (`#E1182C`), negro azabache (`#000000`) y acentos blancos/amarillos, bordes gruesos de `3.5px` a `4.5px`, sombras duras desfasadas sin desenfoque (`5px 5px 0px #000`), tarjetas modulares tipo stickers y botones táctiles con relieve físico.
- **Escenarios Reales de Refrigerador Comercial de Dos Puertas (Modelo Oficial `coca3.JPG`):** 4 fotografías en alta definición de enfriadores comerciales abarrotados (`assets/fridge-01.png` a `assets/fridge-04.png`), con marquesina superior roja curva Coca-Cola (*"enjoy ice cold"*), puertas corredizas dobles de cristal con marco negro, parrillas metálicas de alambre blanco con nervaduras en profundidad, interior blanco refrigerado con pilastras de aluminio, zócalo con compresor y termostato digital `3.2°C`, botellas pegadas hombro con hombro, reflejos y condensación.
- **Distractores Folclóricos de Abarrotes:** Alimentos y recipientes ajenos que suelen encontrarse en las tienditas mexicanas: **Queso Oaxaca** en bola trenzada dentro de bolsa plástica con nudo, **Tuppers** con comida casera y salsa, y **Pollo Rostizado** dorado en bolsa térmica.
- **Marcas de Competencia Paródicas:** Refrescos invasores diseñados para provocar falsos positivos: **"Pecsi"** (lata 355ml y botella 600ml) y **"Devil's Cola"** (botella de 600ml con etiqueta roja y líquido oscuro que simula a Red Cola).
- **Hotspots Invisibles Porcentuales:** Zonas interactivas invisibles mapeadas en coordenadas relativas (`hotspots.json`) que garantizan precisión y adaptación responsiva a cualquier tamaño de pantalla.
- **Feedback Inmediato y Contextual:**
  - **Acierto (Target):** Halo verde luminoso + badge flotante animado `+100 Correcto` + sonido armónico ascendente.
  - **Falso Positivo (Distractor):** Halo rojo con sacudida (*shake*) + badge contextual (`−50 ¡Eso es Queso Oaxaca!`, `−50 ¡Es Devil's Cola!`, `−50 ¡Eso es un Tupper!`, `−50 ¡Pollo Rostizado!`, `−50 ¡Es Pecsi!`) + zumbido grave.
- **Métricas de Computer Vision en Tiempo Real:**
  - **Precision:** $TP / (TP + FP)$ (recompensa la selectividad sin disparar a ciegas).
  - **Recall:** $TP / (TP + FN)$ (mide la exhaustividad al encontrar todos los objetivos).
  - **Accuracy:** Exactitud global de clasificación.
- **Human Vision Benchmark:** Pantalla final tras las 4 rondas con clasificación asignada según puntuación y precisión:
  - `Human Vision Engine` (Rendimiento sobrehumano).
  - `Vision Operator` (Nivel auditor profesional).
  - `Sharp Observer` (Nivel intermedio).
  - `Shelf Scanner` (Nivel inicial).
- **Audio Arcade Completo & Música de Fondo:**
  - **Música de fondo:** Pista de batalla arcade (*"Final Boss Battle Version"*) en bucle continuo a volumen calibrado con botón de pausa/reanudación dedicado (`btn-music` con ícono `🎵` / `⏸️`).
  - **Efectos de sonido:** Síntesis Web Audio API procedural nativa para aciertos (+100), errores (−50), ticks de tiempo y fanfarria final con botón de silenciar independiente (`btn-sound` con ícono `🔊` / `🔇`).

---

## Las 4 Rondas de Auditoría en Tiendita

| Ronda | Escenario | Misión | Tiempo Límite | Desafío Visual |
| :--- | :--- | :--- | :--- | :--- |
| **Ronda 1** | `fridge-01.png` | *Tiendita de Barrio* (Coca-Cola Original) | 9.0 s | Botellas apretadas en anaquel. Invasión de Queso Oaxaca y Tupper de guisado. |
| **Ronda 2** | `fridge-02.png` | *Guerra de Colas* (Todas las Coca-Cola) | 8.5 s | Cuidado con marcas parodia: Devil's Cola (etiqueta roja muy similar) y Pecsi. |
| **Ronda 3** | `fridge-03.png` | *Desmadre en Anaquel* (Solo Botellas) | 7.5 s | Pollo Rostizado en bolsa térmica ocupando anaquel; latas de Coca-Cola y Pecsi que deben ignorarse. |
| **Ronda 4** | `fridge-04.png` | *Tiendita Extrema* (Human Benchmark) | 6.0 s | Máxima densidad (28+ items apiñados), pollo, queso, tupper, colas pirata y condensación densa. |

---

## Sistema de Puntuación

- **Producto Correcto (True Positive):** `+100 pts`
- **Falso Positivo (Distractor / Alimentos / Competencia):** `−50 pts`
- **Objetivo no encontrado al expirar el tiempo (False Negative):** `−25 pts`
- **Bonus de Tiempo:** Si el jugador encuentra todos los objetivos antes del límite, la ronda concluye de inmediato otorgando `+20 pts` por cada segundo restante.

---

## Ejecución Local

Dado que la aplicación consume `hotspots.json` mediante `fetch`, debe ejecutarse a través de un servidor HTTP local:

### Con Node.js
```bash
npx serve . -l 8080
```

### Con Python
```bash
python -m http.server 8080
```

Abre tu navegador en:
```
http://localhost:8080/
```
*Recomendado: resolución de escritorio 16:9 (1366×768 a 1920×1080).*

---

## Estructura de Archivos Organizada

```text
ir_challenge/
├── index.html              # Interfaz y modales de juego
├── style.css               # Diseño visual, animaciones y tokens
├── game.js                 # Motor de juego, métricas de CV y audio Web Audio API
├── hotspots.json           # Ground truth y coordenadas porcentuales de las 4 rondas
├── build_fridges.py        # Generador de escenas fotográficas y metadatos de hotspots
├── packing_core.py         # Motor de renderizado con interior blanco y luces LED azuladas
├── assets/                 # Directorio central de recursos clasificados
│   ├── cutouts/            # Recortes limpios clasificados (beverages, groceries, parody)
│   ├── fridges/            # Renders de alta resolución de los refrigeradores
│   ├── raw/                # Fotos de catálogo y referencia comercial AVIF
│   └── fridge-01.png..04   # Enlaces directos para retrocompatibilidad
├── CLAUDE.md               # Directrices técnicas y operativas
├── README.md               # Este archivo de documentación
└── HANDOFF.md              # Bitácora histórica del desarrollo
```
```

---

## Regeneración de Escenarios (Opcional)

Si se añaden nuevos productos a `asset_ir_challenge/` o se requiere recalcular los refrigeradores y bounding boxes:
```powershell
# En el entorno Conda con OpenCV y Pillow instalados:
conda activate computer_vision
python build_fridges.py
```
Esto regenera automáticamente los 4 refrigeradores en `assets/` y actualiza las coordenadas de `hotspots.json`.

---

## Notas Técnicas

- **Fase actual:** Reconocimiento de Marca y Empaque en refrigerador (Cooler Arcade).
- **Uso previsto:** Herramienta interna de capacitación y benchmarking para equipos comerciales y de auditoría.
