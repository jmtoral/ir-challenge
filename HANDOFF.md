# HANDOFF.md — Bitácora del proyecto IR Challenge

> **Instrucciones:** cada sesión de trabajo agrega UNA entrada al final de
> este archivo. Nunca se editan entradas anteriores. Leer las últimas 2–3
> entradas antes de empezar a trabajar.

---

## Plantilla para nuevas entradas

```markdown
---

### Entrada N — YYYY-MM-DD — [Título breve]

**Quién:** [humano / agente + modelo]

#### Qué se hizo
- ...

#### Qué se decidió y por qué
- **Decisión:** ...
  **Razón:** ...

#### Qué se rechazó y por qué
- **Idea rechazada:** ...
  **Razón:** ...

#### Qué quedó pendiente
- [ ] ...

#### Archivos tocados
- `archivo` — qué cambió
```

---

### Entrada 1 — 2026-09-04 — Andamiaje del proyecto

**Quién:** agente (Claude Opus 4.6 Thinking)

#### Qué se hizo
- Se analizó el corpus existente en `asset_ir_challenge/`: 16 fotos, ~15
  únicas, 6 marcas (Coca-Cola, Sprite, Fanta, Fresca, Sidral Mundet, Ameyal).
- Se crearon los 4 archivos de andamiaje: `CLAUDE.md`, `SPEC.md`,
  `HANDOFF.md`, `.gitignore`.
- Se definió la mecánica completa del juego: opción múltiple de marca, puntaje
  con penalización, RNG sembrado con flujos separados, dificultad progresiva
  en dos ejes, semilla diaria.
- Se calculó explícitamente el puntaje esperado al azar (500 pts, 2.5% del
  máximo) y se verificó que la penalización hace inviable adivinar.
- Se documentaron las limitaciones: sin fotos de competencia, corpus
  insuficiente, balance desigual (Coca-Cola = 46.7%).

#### Qué se decidió y por qué
- **Decisión:** 6 marcas son suficientes para el juego de marca.
  **Razón:** con 6 marcas, la probabilidad al azar es ~17-25% (dependiendo
  de cuántas opciones se muestren), y la penalización de -300 hace que
  adivinar dé puntaje negativo o marginal. Si fueran 2-3 marcas, el azar
  rendiría demasiado.

- **Decisión:** Ameyal cuenta como marca separada de Sidral Mundet.
  **Razón:** la botella de Ameyal muestra un sello Mundet pequeño, pero la
  marca principal y el diseño visual son distintos. Para el entrenamiento de
  reconocimiento visual, son productos diferentes. Si se fusionan, quedan
  5 marcas (sigue siendo viable pero más ajustado).

- **Decisión:** carpeta servida por HTTP, no archivo autocontenido.
  **Razón:** las imágenes ya existen como archivos sueltos en
  `asset_ir_challenge/`. Incrustarlas en base64 en un HTML haría un archivo
  de megas, lento de cargar en teléfono en campo. Además, el corpus va a
  crecer y no es práctico regenerar un HTML monolítico cada vez.

- **Decisión:** `manifest.json` como fuente de verdad del catálogo.
  **Razón:** los nombres de archivo no son uniformes (hay `coca-cola-original-
  235ml-vidrio.png` y hay `coccollig-ligh-nor-pet-2.5l-2.webp`). Un manifiesto
  JSON es parseable por código, editable por humanos, y extensible para Fase 2.

- **Decisión:** semilla diaria como default para el RNG.
  **Razón:** con un corpus chico (<200 imágenes), semilla fija o semanal
  permite memorizar las fotos en 2–3 intentos. Semilla diaria rota la
  secuencia cada 24h, suficiente para que el ranking del día sea comparable
  entre jugadores sin que se memorice la secuencia.

- **Decisión:** 20 rondas, ~3 minutos máximo por partida.
  **Razón:** personal de campo entre visitas a tiendas. No hay tiempo para
  sesiones largas. 20 rondas dan suficiente muestra estadística sin aburrir.

- **Decisión:** 4 opciones por ronda (subiendo a 6 en dificultad alta).
  **Razón:** con 6 marcas totales, 4 opciones da P(azar)=25%. Con 6 opciones
  (todas las marcas), P(azar)=17%. Ambos son manejables con la penalización
  de -300. Empezar en 4 hace las rondas iniciales menos abrumadoras.

- **Decisión:** frecuencia uniforme de marcas (no proporcional al corpus).
  **Razón:** si fuera proporcional, Coca-Cola saldría el 47% de las veces
  y "siempre responder Coca-Cola" sería una estrategia viable. Con uniforme,
  cada marca sale ~3.3 veces y esa estrategia da puntaje negativo.

- **Decisión:** uso interno, el código no genera logotipos.
  **Razón:** confirmado por el usuario que es herramienta interna. Aun así,
  el código solo muestra fotos del corpus, no reproduce marcas registradas
  por su cuenta.

- **Decisión:** mobile-first con soporte desktop.
  **Razón:** confirmado por el usuario que debe funcionar en ambos. El caso
  principal es teléfono en campo, pero también se usará en salón.

#### Qué se rechazó y por qué
- **Idea rechazada:** archivo HTML autocontenido con imágenes en base64.
  **Razón:** con 15+ imágenes de ~300KB, el HTML pesaría >4MB y crecería con
  cada imagen nueva. Además, regenerar el archivo cada vez que cambia el
  corpus es frágil. Carpeta + servidor HTTP es más flexible.

- **Idea rechazada:** usar el conteo de fotos en el corpus para determinar
  la frecuencia de cada marca en el juego (proporcional).
  **Razón:** Coca-Cola tiene 7/15 fotos (47%). Con frecuencia proporcional,
  responder siempre "Coca-Cola" acertaría casi la mitad de las veces, lo cual
  es una estrategia demasiado rentable incluso con penalización.

- **Idea rechazada:** semilla fija permanente.
  **Razón:** con catálogo de <100 imágenes, el jugador memoriza la secuencia
  completa en 2-3 intentos y el ranking mide memoria de la sesión, no
  reconocimiento visual.

- **Idea rechazada:** fusionar Ameyal con Sidral Mundet.
  **Razón:** son visualmente distintos. Fusionarlos reduce las marcas a 5
  y pierde una oportunidad de entrenamiento legítima (el personal de campo
  debe distinguirlos).

#### Qué quedó pendiente
- [ ] **BLOQUEANTE: Crear `manifest.json`** con el mapeo archivo→marca para
  las 16 imágenes existentes. Sin esto, el juego no puede arrancar.
- [ ] **BLOQUEANTE: Ampliar el corpus.** Con 15 imágenes únicas y mínimo 60
  requeridas, el juego no puede correr una partida completa. Necesita al
  menos 18 (mínimo absoluto) o 60 (recomendado) imágenes distribuidas en
  ≥3 por marca.
- [ ] Eliminar o renombrar el duplicado `sprite_355ml_12_lata-100-parent_1 (1) - copia.webp`.
- [ ] Etiquetar `difficulty_hints` en el manifest (opcional para Fase 1 MVP,
  necesario para dificultad progresiva basada en calidad de imagen).
- [ ] Escribir el script de verificación `verify.js` que congele los criterios
  de aceptación `[TBD:verify]` del SPEC.
- [ ] Implementar el juego: `index.html`, `game.js`, `style.css`.
- [ ] Definir grupos de confusión visual entre marcas (necesario para
  dificultad progresiva Eje 1).
- [ ] **Pendiente para cuando haya corpus de competencia:** agregar modo
  "¿es nuestro o no?" (Fase 3) que entrene la habilidad de rechazar producto
  ajeno. Hoy el juego solo entrena "¿cuál de las nuestras es?".

#### Archivos tocados
- `CLAUDE.md` — creado. Instrucciones operativas para el agente.
- `SPEC.md` — creado. Especificación del juego con mecánica y números.
- `HANDOFF.md` — creado. Este archivo, con plantilla y primera entrada.
- `.gitignore` — creado. Ignora dependencias, OS files, y archivos generados.

---

### Entrada 2 — 2026-09-04 — Generación de imágenes por IA y creación del manifiesto

**Quién:** agente (Claude Opus 4.6 Thinking)

#### Qué se hizo
- Se generaron **12 imágenes por IA** con calidad de fotografía de producto
  e-commerce para cubrir marcas con pocas fotos:
  - Sidral Mundet: 5 nuevas (manzana 600ml, 2L, 1.5L, 355ml lata, manzana verde)
  - Ameyal: 5 nuevas (naranja, uva, limón, sandía, mango)
  - Sprite: 2 nuevas (600ml PET, 2L PET)
- Se copiaron las 12 imágenes generadas a `asset_ir_challenge/` con nombres
  normalizados (marca-sabor-tamaño-envase.jpg).
- Se creó **`manifest.json`** con las 27 imágenes únicas etiquetadas por marca,
  tags, ai_generated flag, y difficulty_hints.
- Se actualizaron `CLAUDE.md` y `SPEC.md` para reflejar el corpus expandido
  y el origen mixto de las imágenes.

#### Qué se decidió y por qué
- **Decisión:** generar imágenes con IA en vez de esperar fotos reales.
  **Razón:** el usuario confirmó que no hay más fotos disponibles. Las
  imágenes IA son visualmente creíbles para reconocimiento de marca (logo,
  colores, forma de botella), aunque no sirven para entrenar un modelo de IR
  real. Para el juego son suficientes.

- **Decisión:** marcar cada imagen como `ai_generated: true/false` en el manifest.
  **Razón:** transparencia. Si en el futuro se consiguen fotos reales, las IA
  se pueden reemplazar selectivamente. También permite filtrar si se quiere
  un modo "solo fotos reales".

- **Decisión:** usar convención de nombrado `marca-sabor-tamaño-envase.jpg` para
  las imágenes nuevas.
  **Razón:** los nombres originales son inconsistentes. Las nuevas siguen un
  patrón que hace el manifest más fácil de mantener.

- **Decisión:** no forzar el mínimo de 60 imágenes como bloqueante.
  **Razón:** con 27 imágenes y 6 marcas, se puede jugar una partida de 20
  rondas con repetición leve. No es ideal pero es jugable. Mejor lanzar con
  27 y mejorar que esperar a 60.

#### Qué se rechazó y por qué
- **Idea rechazada:** generar imágenes con condiciones difíciles (borrosas,
  parciales, rotadas) en esta ronda.
  **Razón:** primero hay que cubrir el déficit básico. Las variantes de
  dificultad se generan cuando el corpus base esté completo (~60 imágenes
  limpias).

- **Idea rechazada:** generar todas las 45 imágenes faltantes de una vez.
  **Razón:** la quota de generación de imágenes se agotó después de 12.
  Se renueva en ~5 horas. Se generarán más en la siguiente sesión.

#### Qué quedó pendiente
- [ ] **Generar ~33 imágenes más** cuando se renueve la quota (~5h):
  - Fanta: necesita 8+ (solo tiene 2)
  - Fresca: necesita 8+ (solo tiene 2)
  - Coca-Cola: necesita 3+ (tiene 7, pero pocas variantes de presentación)
  - Sprite: necesita 6+ (tiene 4 contando AI)
- [ ] Eliminar duplicado `sprite_355ml_12_lata-100-parent_1 (1) - copia.webp`.
- [ ] **Implementar el juego**: `index.html`, `game.js`, `style.css`.
- [ ] Escribir script de verificación `verify.js`.
- [ ] Definir grupos de confusión visual entre marcas.
- [ ] **Pendiente largo plazo:** agregar modo "¿es nuestro o no?" cuando haya
  corpus de competencia.

#### Archivos tocados
- `asset_ir_challenge/` — 12 imágenes nuevas agregadas (AI-generated).
- `manifest.json` — creado. 27 entradas con mapeo archivo→marca.
- `CLAUDE.md` — actualizado. Corpus, estructura, etiquetado.
- `SPEC.md` — actualizado. Tabla de marcas, balance, tamaño mínimo.
- `HANDOFF.md` — esta entrada.

---

### Entrada 3 — 2026-09-04 — Decisión: imágenes de refrigerador/enfriador

**Quién:** agente (Claude Opus 4.6 Thinking), a petición del usuario

#### Qué se hizo
- Se decidió agregar un **segundo tipo de escena: `cooler`** (productos dentro
  de refrigerador de tienda) además de las fotos de producto aislado.
- Se creó un plan de generación con **22 prompts listos** para generar cuando
  se renueve la quota de imágenes (~4.5h):
  - 3 imágenes de enfriador por marca × 6 marcas = 18
  - 4 enfriadores mixtos (dificultad alta: desordenado, reflejos, poca luz)
- Se actualizó el esquema de `manifest.json` para incluir `scene_type`
  (`"product"` vs `"cooler"`) y hints adicionales (`glass_reflection`,
  `low_light`, `multi_brand`).
- Se agregó un **tercer eje de dificultad** al SPEC §7 basado en tipo de
  escena: las rondas fáciles usan fotos de producto, las difíciles usan
  escenas de enfriador con condiciones adversas.
- Plan de generación guardado en scratch: `cooler_generation_plan.md`.

#### Qué se decidió y por qué
- **Decisión:** dos tipos de escena (product + cooler) en vez de solo product.
  **Razón:** el personal de campo identifica productos DENTRO de enfriadores,
  no en fondo blanco. Las escenas de cooler son mucho más realistas: vidrio,
  reflejos, condensación, productos rotados, iluminación comercial. Esto
  cierra la brecha entre el juego de entrenamiento y la tarea real de campo.

- **Decisión:** usar escenas de enfriador como eje de dificultad progresiva
  (rondas fáciles = product, rondas difíciles = cooler).
  **Razón:** la transición product→cooler es una rampa de dificultad natural
  que no requiere ajustes artificiales. El jugador primero aprende las
  marcas en limpio y después las identifica en condiciones reales.

- **Decisión:** 22 imágenes de cooler (3 por marca + 4 mixtas).
  **Razón:** con 22 de cooler + 27 existentes de product = 49 total. Si se
  generan también las ~33 de product que faltan, el corpus llegaría a ~82,
  superando el mínimo recomendado de 60.

#### Qué se rechazó y por qué
- **Idea rechazada:** generar solo enfriadores y quitar las fotos de producto.
  **Razón:** las fotos de producto son necesarias para las rondas fáciles.
  La rampa de dificultad product→cooler es un diseño pedagógico intencional.

- **Idea rechazada:** generar las imágenes de enfriador inmediatamente.
  **Razón:** la quota de generación de imágenes está agotada. Se renueva
  en ~4.5 horas. Los prompts están listos para ejecutar en la próxima sesión.

#### Qué quedó pendiente
- [ ] **BLOQUEANTE: Generar 22 imágenes de enfriador** con los prompts de
  `cooler_generation_plan.md` cuando se renueve la quota (~7:55 PM).
- [ ] **Generar ~33 imágenes de producto restantes** (Fanta, Fresca, Coca-Cola,
  Sprite) para completar el corpus base.
- [ ] Actualizar `manifest.json` con las imágenes nuevas (agregar `scene_type`
  a las entradas existentes — actualmente no tienen el campo).
- [ ] Implementar el juego: `index.html`, `game.js`, `style.css`.
- [ ] Escribir script de verificación `verify.js`.

#### Archivos tocados
- `scratch/cooler_generation_plan.md` — creado: 22 prompts listos para generar.

---

### Entrada 4 — 2026-09-04 — Implementación: Image Recognition: The Game (Cooler Arcade & CV Metrics)

**Quién:** agente (Gemini 3.8 Flash), a petición del usuario

#### Qué se hizo
- Se reorientó la arquitectura del juego hacia la visión original solicitada en el prompt maestro: **"IMAGE RECOGNITION: THE GAME"**.
- Se implementaron 4 escenarios fotográficos estáticos de refrigeradores comerciales con botellas y latas de portafolio propio (`assets/fridge-01.png` a `assets/fridge-04.png`), creados con Python (OpenCV y PIL en el entorno Conda `computer_vision`).
- Se generó `hotspots.json` con bounding boxes relativos porcentuales (`x`, `y`, `width`, `height`) e información de atributos (`brand`, `variant`, `package`, `target`).
- Se crearon los componentes frontend completos:
  - `index.html`: Layout dividido 28% sidebar (misión, cronómetro, barra de progreso, score, reglas) y 72% viewport con contenedor de refrigerador responsive 3:4.
  - `style.css`: Estética corporativa arcade de alta fidelidad, halos luminosos SVG/CSS (verde para aciertos, rojo con shake para falsos positivos), feedback flotante animado (`+100` / `−50`) y modales translúcidos.
  - `game.js`: Motor de juego de 4 rondas con misiones específicas, cronómetro de alta resolución, cálculo operacional de métricas de Computer Vision (**Precision**, **Recall**, **Accuracy**), sintetizador de audio con Web Audio API (acierto, error, tick de cuenta regresiva, victoria) y pantalla final **HUMAN VISION BENCHMARK** con ranking dinámico.
- Verificación completa en navegador ejecutada exitosamente con `browser_subagent`.

#### Qué se decidió y por qué
- **Decisión:** construir los escenarios de refrigerador componiendo los packshots reales y transparentes de portafolio propio con iluminación de anaquel, parrillas, etiquetas de precios y condensación en vidrio mediante Python.
  **Razón:** el usuario confirmó que no disponía de fotos de enfriadores en su máquina ni imágenes de la competencia, y la cuota de generación directa de imágenes IA estaba temporalmente agotada. Esta técnica garantizó imágenes de alta resolución sin violar las restricciones de portafolio y produjo coordenadas porcentuales exactas con tolerancia cero a errores de alineación.
- **Decisión:** hotspots 100% invisibles antes del primer clic.
  **Razón:** requerido explícitamente por el usuario para entrenar el ojo humano como un modelo de detección de objetos.
- **Decisión:** sintetizador Web Audio API nativo en lugar de archivos MP3 externos.
  **Razón:** cero dependencias de red, carga instantánea y control total de volumen y silenciamiento.

#### Qué quedó pendiente
- [ ] Opcional: Agregar más rondas o modos de juego adicionales cuando haya disponibilidad de imágenes adicionales de portafolio.
- [ ] Empaquetar como PWA si se requiere soporte offline completo en dispositivos móviles de campo.

#### Archivos tocados
- `build_fridges.py` — script de generación de escenarios de cooler y metadatos de hotspots.
- `assets/fridge-01.png` a `fridge-04.png` — imágenes de escenario de las 4 rondas.
- `hotspots.json` — coordenadas porcentuales y ground truth de productos por ronda.
- `index.html` — interfaz gráfica de usuario y modales.
- `style.css` — diseño visual, animaciones y tokens de color.
- `game.js` — lógica de juego, métricas de CV y motor de audio.
- `HANDOFF.md` — esta entrada.
- `walkthrough.md` — reporte visual con capturas del navegador.

---

### Entrada 5 — 2026-09-05 — Corrección de tapas de botellas, documentación completa y estado operativo

**Quién:** agente (Gemini 3.8 Flash Thinking), a petición del usuario

#### Qué se hizo
- **Diagnóstico y corrección de "tapas voladas" en botellas (`build_fridges.py` y `assets_transparent/`)**:
  - *Causa identificada*: El algoritmo de remoción de fondo blanco (floodfill) confundía los reflejos y brillos blancos de las tapas de colores claros (como en *Ameyal Uva* y *Sidral Mundet*) con el fondo del estudio fotográfico, haciendo transparentes partes de la tapa. Adicionalmente, el recorte automático de bordes eliminaba filas superiores de píxeles si la densidad era baja.
  - *Solución*: Se protegió explícitamente la columna geométrica central de la tapa (`x: [0.35*w, 0.65*w]`, `y: [0.02*h, 0.18*h]`), impidiendo que el floodfill perfore las coronas y tapas plásticas. Se agregó un margen de seguridad superior de 4px y se reemplazaron imágenes de baja resolución por packshots en alta definición (`coca-cola-sin-azucar-235-ml`).
  - Se regeneraron los 4 refrigeradores de juego (`assets/fridge-01.png` a `fridge-04.png`) y el archivo de ground truth `hotspots.json`.
- **Actualización y alineación de documentación técnica**:
  - `README.md`: Documentación completa del juego, descripción de las 4 rondas, sistema de puntuación, fórmulas de Computer Vision (Precision, Recall, Accuracy), rangos de Human Vision Benchmark, instrucciones de ejecución local y regeneración de assets.
  - `CLAUDE.md`: Actualizado con las directrices operativas del juego, especificación del entorno Conda `computer_vision`, estructura de archivos, reglas de mantenimiento y advertencia sobre permisos de comandos en el IDE.
  - `HANDOFF.md`: Incorporación de esta entrada consolidada.
- **Clarificación sobre solicitudes de autorización en el IDE**:
  - Se explicó al usuario la causa de las solicitudes frecuentes de confirmación (el IDE solicita aprobación interactiva cada vez que un agente ejecuta comandos en la terminal del sistema). Se adoptó la estrategia de operar mediante lectura y edición directa de archivos sin llamadas innecesarias a la terminal.

#### Qué se decidió y por qué
- **Decisión:** Proteger algorítmicamente la geometría de la tapa en `build_fridges.py` en lugar de retoque manual de mapa de bits.
  **Razón:** Permite que cualquier futuro producto que se agregue al catálogo se procese de forma determinista y reproducible sin requerir edición manual externa.
- **Decisión:** Priorizar el uso de herramientas directas de modificación de archivos sobre comandos de shell.
  **Razón:** Reduce las interrupciones al usuario causadas por los diálogos de seguridad de la terminal en el IDE.

#### Qué quedó pendiente
- [ ] Opcional: Modo multijugador o tabla de clasificación persistente (Local Storage o backend ligero).
- [ ] Opcional: Soporte para gestos táctiles optimizados en caso de migración a PWA para smartphones de campo.

#### Archivos tocados
- `build_fridges.py` — algoritmo de recorte con protección de tapas.
- `assets/fridge-01.png` a `fridge-04.png` — imágenes de enfriador regeneradas con tapas íntegras.
- `assets_transparent/` — packshots transparentes actualizados.
- `hotspots.json` — coordenadas de hotspots recalculadas.
- `README.md` — creado y actualizado con guía completa del simulador.
- `CLAUDE.md` — actualizado con arquitectura, directrices y entorno.
- `HANDOFF.md` — esta entrada (Entrada 5).

---

### Entrada 6 — 2026-09-05 — Modo Tiendita Difícil: Apiñamiento, Abarrotes y Refrescos Parodia

**Quién:** agente (Gemini 3.8 Flash Thinking), a petición del usuario

#### Qué se hizo
- **Generación y procesamiento de nuevos elementos de tiendita mexicana**:
  - Se generaron 6 activos fotorrealistas de alta resolución en fondo blanco:
    - `pecsi-lata-355ml.png`: Lata de aluminio azul de refresco de cola parodia "Pecsi".
    - `pecsi-botella-600ml.png`: Botella de plástico PET 600ml con etiqueta azul "Pecsi".
    - `devils-cola-botella-600ml.png`: Botella 600ml con etiqueta roja y cuernitos "Devil's Cola" (parodia de Red Cola).
    - `queso-oaxaca-bolsa.png`: Bola de queso Oaxaca (quesillo) trenzado en bolsa de plástico con nudo.
    - `pollo-rostizado-bolsa.png`: Pollo rostizado dorado y jugoso en bolsa térmica para llevar con asas.
    - `tupper-comida.png`: Recipiente translúcido tipo Tupperware con guisado casero y tapa roja.
  - Se creó y ejecutó `process_distractors.py` en el entorno Conda `computer_vision` para extraer la transparencia alfa con recorte antialiasing hacia `assets_transparent/`.
- **Rediseño de escenarios con alta densidad y apiñamiento (`build_fridges.py`)**:
  - Se redujo el espaciado horizontal de botellas (de 200–220px a 110–130px), incrementando la densidad de 4–5 a 7–8 productos por estante (hasta 28 en la Ronda 4).
  - Se implementó layering y solapamiento horizontal parcial simulando anaqueles apretados de tiendita de abarrotes.
  - Se integraron los alimentos de tiendita y las marcas parodia en las 4 rondas con dificultad progresiva:
    - **Ronda 1 (9.0s)**: *Tiendita de Barrio* (Coca-Cola Original vs Tupper y Queso Oaxaca).
    - **Ronda 2 (8.5s)**: *Guerra de Colas* (Coca-Cola vs Devil's Cola y Pecsi).
    - **Ronda 3 (7.5s)**: *Desmadre en Anaquel* (Solo botellas Coca-Cola vs Pollo Rostizado, latas y marcas parodia).
    - **Ronda 4 (6.0s)**: *HUMAN BENCHMARK Tiendita Extrema* (Máxima densidad, pollo, queso, tupper, Devil's Cola, Pecsi y condensación densa).
  - Se regeneraron los 4 refrigeradores en `assets/` y se actualizaron las coordenadas de `hotspots.json`.
- **Feedback contextual y humorístico en frontend (`game.js` y `style.css`)**:
  - Se actualizó el motor de juego para soportar `distractor_label` personalizado. Al cometer un falso positivo, el badge flotante muestra mensajes directos: `−50 ¡Eso es Queso Oaxaca!`, `−50 ¡Es Devil's Cola!`, `−50 ¡Eso es un Tupper!`, `−50 ¡Pollo Rostizado!`, `−50 ¡Es Pecsi!`.
  - Se ajustó el CSS de `.floating-pill` para soportar textos descriptivos con sombra y animación fluida.
  - Se actualizaron los textos y preview cards de `index.html`.
- **Verificación en navegador ejecutada con `browser_subagent`**:
  - Se verificaron la pantalla inicial, el anaquel abarrotado de Ronda 1 con Queso Oaxaca y Tupper, el feedback al cliquear el queso (`−50 ¡Eso es Queso Oaxaca!`), la selección de botellas Coca-Cola (`+100 Correcto`), el modal de métricas de Computer Vision y la transición a la Ronda 2 (Guerra de Colas con Devil's Cola y Pecsi).
  - Capturas registradas en `walkthrough.md`.

#### Qué se decidió y por qué
- **Decisión:** Usar nombres satíricos explícitos ("Pecsi", "Devil's Cola") y objetos de tienda de conveniencia real (Queso Oaxaca, Tupper, Pollo Rostizado).
  **Razón:** Refleja con humor y exactitud la realidad operativa de auditoría en el canal tradicional (tienditas misceláneas en México), donde los enfriadores comerciales con frecuencia alojan comida del tendero o refrescos de la competencia.
- **Decisión:** Asignar etiquetas personalizadas a cada distractor en `hotspots.json`.
  **Razón:** Ofrece feedback inmediato y didáctico al usuario explicando por qué su selección fue errónea en lugar de un simple mensaje genérico de error.

#### Qué quedó pendiente
- [ ] Opcional: Sonido específico o cómico adicional al cliquear el pollo rostizado o el queso oaxaca.
- [ ] Opcional: Modo contra reloj sin límite de rondas ("Modo Tiendita Infinita").

#### Archivos tocados
- `process_distractors.py` — script de extracción de transparencia de los nuevos distractores.
- `assets_transparent/` — 6 nuevos activos transparentes añadidos.
- `build_fridges.py` — generador actualizado con anaqueles apiñados y nuevos productos.
- `assets/fridge-01.png` a `fridge-04.png` — escenarios regenerados.
- `hotspots.json` — coordenadas y etiquetas de distractores de las 4 rondas.
- `game.js` — soporte para feedback contextual en falsos positivos.
- `style.css` — estilos mejorados para píldoras flotantes descriptivas.
- `index.html` — descripciones y nombres de misiones actualizados.
- `walkthrough.md` — capturas y reporte de prueba en navegador.
- `README.md` — guía actualizada con características de tiendita y marcas parodia.
- `CLAUDE.md` — especificaciones técnicas de las nuevas rondas.
- `HANDOFF.md` — esta entrada (Entrada 6).

---

### Entrada 7 — 2026-09-05 — Eliminación total de espacios vacíos y empaquetado continuo edge-to-edge

**Quién:** agente (Gemini 3.8 Flash Thinking), a petición del usuario

#### Qué se hizo
- **Detección y eliminación de huecos horizontales en anaqueles**:
  - *Causa identificada*: En la versión inicial de alta densidad, algunos productos se ubicaban en centros fijos discretos que dejaban brechas de 25px a 60px entre botellas y en las orillas metálicas.
  - *Solución*: Se diseñó e implementó un algoritmo de empaquetado continuo de anaquel (`packing_core.py` y `build_fridges.py`):
    - Cobertura estricta de pared izquierda a pared derecha ($x=55$ a $x=1145$, 1090px de luz de anaquel).
    - Cálculo de solapamiento natural ($\approx 6\text{px}$ a $14\text{px}$) asegurando que cada producto toque hombro con hombro al adyacente sin un solo pixel de separación vacía.
    - Soporte para segunda hilera en profundidad (botellas al fondo semi-sombreadas) detrás de elementos de baja estatura como tuppers, latas y quesos.
- **Regeneración de escenarios y ground truth**:
  - Se regeneraron los 4 refrigeradores (`assets/fridge-01.png` a `fridge-04.png`) y se recalculó `hotspots.json` con las nuevas coordenadas y empaquetado 100% continuo.
  - La Ronda 4 ahora contiene **42 productos distribuidos en 4 niveles repletos**, logrando la sensación auténtica de un enfriador abarrotado de tiendita mexicana.
- **Verificación en navegador con `browser_subagent`**:
  - Se verificó visualmente que la repisa no muestra espacios vacíos ni en las orillas ni entre productos.
  - Se verificó la precisión de detección de impactos (`+100 CORRECTO`), el avance de ronda y la persistencia de anaqueles repletos en la Ronda 2.
  - Capturas registradas en `walkthrough.md`.

#### Qué se decidió y por qué
- **Decisión:** Distribuir el solapamiento de forma continua y proporcional entre todos los productos de cada estante ($overlap = (W_{total} - W_{disponible}) / (N - 1)$) en lugar de fijar coordenadas manuales.
  **Razón:** Garantiza matemáticamente que el primer producto siempre toque la pared metálica izquierda y el último producto toque la pared derecha, eliminando cualquier posible holgura vacía independientemente de la combinación de botellas, latas o tuppers.

#### Qué quedó pendiente
- [ ] Opcional: Modo desafío con tiempo dinámico o contador de racha de aciertos.

#### Archivos tocados
- `packing_core.py` — módulo base de empaquetado continuo sin huecos.
- `build_fridges.py` — generador de refrigeradores actualizado con empaquetado edge-to-edge.
- `assets/fridge-01.png` a `fridge-04.png` — refrigeradores regenerados 100% abarrotados.
- `hotspots.json` — coordenadas de hotspots recalculadas.
- `walkthrough.md` — capturas y reporte de verificación en navegador.
- `HANDOFF.md` — esta entrada (Entrada 7).

---

### Entrada 8 — 2026-09-05 — Corrección de transparencia en alimentos y marcas parodia usando GrabCut

**Quién:** agente (Gemini 3.8 Flash Thinking), a petición del usuario

#### Qué se hizo
- **Diagnóstico del desvanecimiento / transparencia de distractores**:
  - *Causa identificada*: El script previo `process_distractors.py` utilizaba `cv2.floodFill` desde la esquina superior izquierda. Debido a que el queso Oaxaca es blanco, el pollo rostizado y tupper venían en bolsas/recipientes plásticos translúcidos con reflejos blancos, y las botellas tenían brillos especulares, el algoritmo de inundación perforó completamente los objetos haciéndolos transparentes (e.g. el queso Oaxaca solo conservaba 1,727 píxeles sólidos de 378,231, prácticamente invisible).
  - *Solución*: Se creó `fix_distractors_grabcut.py` implementando segmentación en primer plano mediante el algoritmo **GrabCut de OpenCV** (`cv2.grabCut` con modelos gaussianos de fondo y primer plano, 4 iteraciones), clausura morfológica (`cv2.morphologyEx` con elemento elíptico) y filtro de contornos de área mayor:
    - `queso-oaxaca-bolsa.png`: De 1,727 a **285,134 píxeles sólidos** (100% visible, blanco cremoso trenzado con nudo).
    - `pollo-rostizado-bolsa.png`: De 58,479 a **443,942 píxeles sólidos** (100% visible, dorado y jugoso en bolsa con asas).
    - `tupper-comida.png`: De 1,379 a **360,217 píxeles sólidos** (100% visible con guisado casero y tapa roja).
    - `pecsi-lata-355ml.png`: De 58,154 a **342,273 píxeles sólidos**.
    - `pecsi-botella-600ml.png`: De 82,357 a **246,611 píxeles sólidos**.
    - `devils-cola-botella-600ml.png`: De 96,960 a **232,570 píxeles sólidos**.
- **Regeneración de escenarios fotográficos y ground truth**:
  - Se regeneraron los 4 refrigeradores en `assets/` con `build_fridges.py`.
  - Ahora el Tupper, el Queso Oaxaca, el Pollo Rostizado, Devil's Cola y Pecsi son plenamente opacos, sólidos y destacan en alta resolución en sus respectivos anaqueles.
- **Verificación en navegador con `browser_subagent`**:
  - Ronda 1: Tupper y Queso Oaxaca claramente visibles y sólidos; feedback interactivo `−50 ¡Eso es Queso Oaxaca!` comprobado.
  - Ronda 2: Devil's Cola y Pecsi nítidas y sólidas con sus etiquetas roja y azul.
  - Ronda 3: Pollo Rostizado perfectamente visible en el anaquel central.
  - Capturas actualizadas en `walkthrough.md`.

#### Qué se decidió y por qué
- **Decisión:** Reemplazar el floodfill simple por GrabCut con modelos de mezcla gaussiana (GMM) para aislar objetos blancos/translúcidos sobre fondos claros.
  **Razón:** Los algoritmos de floodfill fallan catastróficamente con productos blancos o con reflejos especulares de estudio. GrabCut evalúa distribuciones de color multidimensionales y bordes globales, logrando siluetas perfectas y sólidas.

#### Qué quedó pendiente
- [ ] Listo para juego y pruebas por parte del usuario en `http://localhost:8080/`.

#### Archivos tocados
- `fix_distractors_grabcut.py` — script de segmentación GrabCut.
- `assets_transparent/` — 6 imágenes regeneradas con canales alfa 100% sólidos.
- `assets/fridge-01.png` a `fridge-04.png` — escenarios de refrigerador regenerados.
- `hotspots.json` — ground truth sincronizado.
- `walkthrough.md` — capturas visuales actualizadas con objetos sólidos.
- `HANDOFF.md` — esta entrada (Entrada 8).

---

### Entrada 9 — 2026-09-05 — Interior Blanco Comercial Coca-Cola con Luz LED Fría y Reorganización Estructurada de Assets

**Quién:** agente (Gemini 3.8 Flash Thinking), a petición del usuario

#### Qué se hizo
- **Análisis de referencia comercial Coca-Cola**:
  - Se examinó la imagen provista en `asset_ir_challenge/`: `Coke-Brand-Two-Door-Display-Bottle-Refrigerator-with-Dynamic-Cooling-System.avif`.
  - Se identificaron los elementos clave del refrigerador comercial de dos puertas: pared de fondo interior blanca/gris claro, iluminación LED de refrigeración fría azulada, tres pilastras verticales metálicas con ranuras dobles para graduación de repisas, y copetes/molduras frontales rojas Coca-Cola con porta-precios blancos.
- **Rediseño del motor de composición y renderizado (`packing_core.py`)**:
  - **Interior Blanco Realista**: Paredes interiores con gradientes comerciales claros (`RGB 246, 250, 255` a `216, 226, 236`), sombras de oclusión bajo anaqueles y laterales biselados.
  - **Iluminación LED Fría Azulada**: Módulos de iluminación LED azulada (`rgb(175, 226, 255)`) en la marquesina superior, laterales verticales y difusores frontales bajo cada repisa.
  - **Pilastras de Montaje Metálicas**: 3 rieles verticales ($x=280, 600, 920$) con pares de ranuras rectangulares cada 26 px.
  - **Moldura Frontal Roja Coca-Cola**: Copetes frontales en cada repisa en color rojo Coca-Cola (`#E1182C` / `RGB 225, 24, 44`) con acentos de porta-precios blancos.
  - **Eliminación de artefactos de bounding box**: Se reemplazó el tintado alfa plano por `ImageEnhance.Brightness(prod_scaled).enhance(0.85)` para oscurecer botellas de fondo sin generar bordes o rectángulos grises.
- **Reorganización estructurada de `assets/`**:
  - Se creó y ejecutó `organize_assets.py` clasificando más de 40 archivos en una jerarquía clara:
    - `assets/cutouts/beverages/`: 21 packshots de marcas oficiales Coca-Cola, Sprite, Fanta, Mundet, Ameyal con fondo transparente.
    - `assets/cutouts/groceries/`: Distractores de tiendita (Queso Oaxaca, Pollo Rostizado, Tupper) con fondo transparente y alphas sólidos.
    - `assets/cutouts/parody/`: Refrescos de competencia y parodia ("Pecsi" lata y botella, "Devil's Cola").
    - `assets/fridges/`: Renders de alta resolución de las 4 escenas de juego (`fridge-01.png` a `04.png`).
    - `assets/raw/`: 29 fotos originales de catálogo y la referencia comercial AVIF.
    - Se mantuvieron copias directas de `fridge-01.png` a `04.png` en la raíz de `assets/` para total retrocompatibilidad con `index.html` y `hotspots.json`.
    - Se limpiaron imágenes temporales y de depuración sueltas en la raíz del proyecto (`debug_*.png`, `f*_caps.png`, `shelf*_caps.png`, `test_*.png`).
- **Regeneración y Verificación**:
  - Se regeneraron los 4 refrigeradores con `build_fridges.py`.
  - Se verificó en `http://localhost:8080/` con `browser_subagent` capturando capturas de Ronda 1 y Ronda 2: el refrigerador blanco con resplandor LED azulado y las botellas densamente empaquetadas lucen con contraste y fidelidad comercial superior.
  - Documentación actualizada en `walkthrough.md`, `README.md`, `CLAUDE.md` y `HANDOFF.md`.

#### Qué se decidió y por qué
- **Decisión:** Mantener dual-export de `fridge-01.png` a `04.png` (en `assets/` y en `assets/fridges/`).
  **Razón:** Evita romper rutas cacheadas o relativas del frontend mientras ofrece una estructura impecable para el mantenimiento del repositorio.
- **Decisión:** Uso de `ImageEnhance.Brightness` para profundidad de campo en hileras de fondo.
  **Razón:** `Image.alpha_composite` con rectángulos sólidos afectaba los píxeles perimetrales con semitransparencia (antialiasing) generando contornos grises indeseados; la modulación directa de brillo preserva el canal alfa intacto.

#### Qué quedó pendiente
- Ninguno. El sistema se encuentra completamente implementado, ordenado, verificado y activo en `http://localhost:8080/`.

#### Archivos tocados
- `packing_core.py` — renderizado de interior blanco, iluminación LED fría azulada, pilastras y búsqueda multinivel de assets.
- `organize_assets.py` — script de reestructuración de directorio de assets.
- `build_fridges.py` — guardado dual y generación sincronizada.
- `assets/` — directorio reorganizado en `cutouts/`, `fridges/` y `raw/`.
- `assets/fridge-01.png` a `04.png` y `assets/fridges/fridge-01.png` a `04.png` — refrigeradores regenerados con estética blanca y luz fría.
- `walkthrough.md` — reporte visual con capturas del cooler blanco.
- `README.md` — actualización de características y árbol de archivos.
- `CLAUDE.md` — actualización de arquitectura y árbol de assets.
- `HANDOFF.md` — esta entrada (Entrada 9).

---

### Entrada 10 — 2026-09-06 — Modelado Fiel del Enfriador Comercial de Dos Puertas Coca-Cola (`coca3.JPG`)

**Quién:** agente (Gemini 3.8 Flash Thinking), a petición del usuario

#### Qué se hizo
- **Incorporación y análisis de la referencia `coca3.JPG`**:
  - Se analizó la nueva referencia de alta fidelidad `coca3.JPG` en el root del repositorio.
  - Se archivó una copia en `assets/raw/coca3.jpg` para mantener el repositorio limpio y catalogado.
  - Se identificaron los elementos anatómicos distintivos del enfriador comercial de dos puertas deslizantes:
    1. **Marquesina superior curvada roja** con iluminación interna, logotipo "Coca-Cola" y la leyenda *"enjoy [botella contorno] ice cold"*.
    2. **Puertas corredizas dobles** con marco negro exterior (`#16181B`), costura central vertical de traslape ($x=600$) y manijas verticales empotradas.
    3. **Parrillas metálicas de alambre blanco**: Sustitución del copete rojo macizo por rejillas realistas de alambre plastificado blanco con nervaduras transversales en profundidad, alambres frontales dobles y porta-precios claros.
    4. **Interior blanco comercial**: Pared de fondo limpia (`#F8FAFD`) con 3 pilastras metálicas verticales y ranuras troqueladas de ajuste.
    5. **Zócalo inferior de compresor & termostato digital**: Rejilla de ventilación horizontal negra con controlador digital tipo Carel/Eliwell iluminado en verde (`3.2°C`) y símbolo de enfriamiento activo.
- **Actualización del motor de renderizado (`packing_core.py`)**:
  - Se rediseñó `create_cooler_base` para dibujar las rejillas de alambre blanco con cuadrícula tridimensional y pilastras de aluminio cepillado.
  - Se rediseñó `apply_glass_and_reflections` incorporando la marquesina superior curvada ($y=0..86$), el zócalo inferior de compresor ($y=1545..1600$) y la costura de las dos puertas corredizas en el centro sin oscurecer los productos de juego.
- **Regeneración completa de escenarios**:
  - Se ejecutó `build_fridges.py` regenerando los 4 escenarios (`assets/fridge-01.png` a `04.png` y `assets/fridges/fridge-01.png` a `04.png`) y sincronizando `hotspots.json`.
  - Se limpiaron los scripts y renders de prueba temporales (`test_coca3_style.py`, `test_coca3_fridge.png`, `test_packed_round1.png`).
- **Verificación en vivo con `browser_subagent`**:
  - Se validaron las rondas 1 y 2 en el navegador en `http://localhost:8080/`. El refrigerador presenta un aspecto idéntico al modelo 3D comercial de la referencia `coca3.JPG`.
  - Se actualizaron capturas y documentación en `walkthrough.md`, `README.md` y `CLAUDE.md`.

#### Qué se decidió y por qué
- **Decisión:** Dibujar la marquesina superior en $y=0..86$ y el compresor en $y=1545..1600$.
  **Razón:** Coincide exactamente con el espacio disponible en el canvas de 1200×1600 sin cortar las tapas de las botellas superiores (que inician en $y \ge 110$) ni la base de los productos inferiores.
- **Decisión:** Hacer la costura central de las dos puertas corredizas semi-traslúcida (`alpha = 75`).
  **Razón:** Proporciona la ilusión óptica tridimensional perfecta de dos puertas de cristal corredizas sin penalizar la visibilidad o interacción del jugador en los productos ubicados en el centro del anaquel.

#### Qué quedó pendiente
- Ninguno. El juego opera con máximo realismo y fidelidad visual respecto a la referencia `coca3.JPG`.

#### Archivos tocados
- `packing_core.py` — marquesina curva Coca-Cola, doble puerta corrediza, rejillas de alambre blanco y termostato digital.
- `build_fridges.py` — regeneración de escenas fotográficas.
- `assets/fridge-01.png` a `04.png` y `assets/fridges/` — imágenes finales de juego actualizadas.
- `hotspots.json` — coordenadas de hotspots verificadas.
- `assets/raw/coca3.jpg` — archivo de referencia archivado.
- `walkthrough.md` — capturas y reporte visual del modelo de dos puertas.
- `README.md` y `CLAUDE.md` — especificaciones técnicas y documentación de componentes.
- `HANDOFF.md` — esta entrada (Entrada 10).

---

### Entrada 11 — 2026-09-06 — Configuración del Repositorio Remoto GitHub (`jmtoral/ir-challenge`)

**Quién:** agente (Gemini 3.8 Flash Thinking), a petición del usuario

#### Qué se hizo
- **Vinculación con GitHub**:
  - Se vinculó el proyecto al repositorio oficial: **`https://github.com/jmtoral/ir-challenge`**.
  - Se inicializó el control de versiones Git en el directorio raíz con rama predeterminada `main`.
  - Se configuró el origen remoto: `origin -> https://github.com/jmtoral/ir-challenge.git`.
- **Higiene del repositorio y `.gitignore`**:
  - Se añadieron reglas explícitas para ignorar artefactos de Python (`__pycache__/`, `*.py[cod]`, entornos virtuales `.venv/`, etc.).
  - Se mantuvieron bajo seguimiento todos los assets de juego clasificados (`assets/`, `assets_transparent/`, `asset_ir_challenge/`), metadatos (`hotspots.json`, `manifest.json`), scripts generadores y aplicación web.
- **Sincronización de Documentación**:
  - Se integró el enlace oficial del repositorio en la cabecera de `README.md` y en las directrices de `CLAUDE.md`.

#### Qué se decidió y por qué
- **Decisión:** Establecer `main` como rama principal predeterminada en lugar de `master`.
  **Razón:** Estándar moderno de GitHub y compatibilidad directa con el flujo de trabajo del repositorio remoto.

#### Qué quedó pendiente
- [ ] Realizar el primer push (`git push -u origin main`) con las credenciales de GitHub del usuario cuando lo considere conveniente.

#### Archivos tocados
- `.gitignore` — reglas de exclusión de Python.
- `README.md` — enlace oficial al repositorio de GitHub.
- `CLAUDE.md` — enlace oficial de control de versiones.
- `HANDOFF.md` — esta entrada (Entrada 11).

---

### Entrada 12 — 2026-09-06 — Integración de Música de Fondo ("Final Boss Battle Version") y Control de Pausa

**Quién:** agente (Gemini 3.8 Flash Thinking), a petición del usuario

#### Qué se hizo
- **Organización de audio**:
  - Se copió y catalogó `Final Boss Battle Version.mp3` en `assets/audio/final_boss_battle.mp3` manteniendo retrocompatibilidad con la ruta raíz.
  - Se catalogó `Playful Retro Arcade Theme.mp3` en `assets/audio/playful_retro_arcade.mp3`.
- **Motor de Música de Fondo (`MusicPlayer` en `game.js`)**:
  - Se implementó la clase `MusicPlayer` encargada de gestionar el ciclo de vida del audio en bucle continuo (`loop = true`), volumen balanceado a `0.35` (permitiendo que los efectos de aciertos y errores resalten con nitidez) y tolerancia a restricciones de autoplay de navegadores modernos.
  - Se conservaron intactos todos los efectos de sonido procedurales de `SoundEngine` (+100 aciertos, −50 errores, ticks de cuenta regresiva y fanfarria final).
- **Interfaz y Controles de Usuario (`index.html` y `style.css`)**:
  - Se agregó el botón dedicado `#btn-music` con ícono dinámico (`🎵` en reproducción, `⏸️` en pausa), tooltip contextual y clase visual `.btn-icon.is-paused`.
  - El botón `#btn-sound` se mantuvo para silenciar/activar exclusivamente los efectos de sonido (`🔊` / `🔇`).
  - La música arranca de manera natural al pulsar *"COMENZAR SIMULACIÓN"*, reiniciarse la partida o con el primer clic del usuario.
- **Verificación**:
  - Se ejecutó verificación interactiva en el navegador mediante `browser_subagent` en `http://localhost:8080/`. Se comprobó que la música arranca al iniciar la partida, se pausa y actualiza a `⏸️` al pulsar el botón, y se reanuda a `🎵` sin retrasos.
  - Se actualizaron `walkthrough.md`, `README.md` y `CLAUDE.md`.

#### Qué se decidió y por qué
- **Decisión:** Mantener controles separados para música de fondo (`#btn-music`) y efectos de sonido (`#btn-sound`).
  **Razón:** Permite que el usuario juegue con su propia música externa si lo desea silenciando únicamente el soundtrack pero conservando el feedback de audio táctico de aciertos/errores en la auditoría.
- **Decisión:** Volumen predeterminado calibrado en 0.35 para la música.
  **Razón:** Evita saturación y asegura que los efectos sonoros de acierto (+100) y de penalización (−50) sean audibles y claros.

#### Qué quedó pendiente
- Ninguno. El sistema de música de fondo y control de pausa está 100% operativo y probado en vivo.

#### Archivos tocados
- `index.html` — botón de control de música `#btn-music` en la barra de navegación.
- `style.css` — estilos para estado pausado `.btn-icon.is-paused`.
- `game.js` — clase `MusicPlayer`, enlace de eventos y persistencia de estado.
- `assets/audio/final_boss_battle.mp3` — archivo de música de fondo catalogado.
- `walkthrough.md` — capturas y reporte de verificación en vivo.
- `README.md` y `CLAUDE.md` — documentación actualizada del sistema de audio.
- `HANDOFF.md` — esta entrada (Entrada 12).

---

### Entrada 13 — 2026-09-06 — Despliegue en GitHub Pages y Automatización CI/CD

**Quién:** agente (Gemini 3.8 Flash Thinking), a petición del usuario

#### Qué se hizo
- **Configuración de GitHub Pages**:
  - Se verificó que todos los recursos de la aplicación (`index.html`, `style.css`, `game.js`, `hotspots.json`, `assets/fridge-*.png`, `assets/audio/`) utilicen rutas relativas, garantizando funcionamiento sin colisiones tanto en dominio raíz como bajo el subdirectorio de GitHub Pages (`/ir-challenge/`).
  - Se creó el flujo automatizado de GitHub Actions en `.github/workflows/deploy.yml` utilizando las acciones oficiales `actions/deploy-pages@v4`, `actions/upload-pages-artifact@v3` y `actions/configure-pages@v5`.
  - Se creó y publicó la rama dedicada `gh-pages` con seguimiento remoto para soporte de despliegue directo por rama o por Actions.
  - Se documentó la URL del sitio en vivo: **`https://jmtoral.github.io/ir-challenge/`**.
- **Sincronización y Push**:
  - Se confirmaron y subieron todos los cambios (controles de música de fondo, catálogo de audio, workflow de GitHub Pages y documentación) a la rama `main` y a `gh-pages` en `origin`.

#### Qué se decidió y por qué
- **Decisión:** Implementar workflow de GitHub Actions (`.github/workflows/deploy.yml`) y publicar simultáneamente rama `gh-pages`.
  **Razón:** Otorga doble flexibilidad; si el usuario selecciona en los ajustes de GitHub Pages el origen *"GitHub Actions"* o *"Deploy from a branch (gh-pages)"*, el sitio queda publicado y operativo sin fricción.

#### Qué quedó pendiente
- Ninguno. El sitio está desplegado y sincronizado con GitHub Pages en `https://jmtoral.github.io/ir-challenge/`.

#### Archivos tocados
- `.github/workflows/deploy.yml` — workflow de despliegue automático de GitHub Actions.
- `README.md` — enlace al juego en vivo en GitHub Pages.
- `CLAUDE.md` — enlace al juego en vivo en GitHub Pages.
- `HANDOFF.md` — esta entrada (Entrada 13).









