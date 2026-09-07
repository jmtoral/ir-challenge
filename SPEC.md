# SPEC.md — Especificación del juego IR Challenge

> **Estado:** BORRADOR — los criterios de aceptación numéricos están marcados
> como `[TBD:verify]` y se congelan después de correr el script de verificación
> contra el corpus real.

## 1. Objetivo del juego

Entrenar la identificación visual de **marca** del portafolio propio. El
jugador ve una foto de producto y selecciona la marca correcta entre N
opciones lo más rápido posible.

### 1.1 Limitaciones conocidas

1. **Solo portafolio propio.** El corpus contiene únicamente fotos de marcas
   propias (Coca-Cola Company / FEMSA). No hay imágenes de competencia y no
   se van a conseguir en el corto plazo.

2. **El juego entrena "¿cuál de las nuestras es?", no "¿es de las nuestras?".**
   Un sistema de IR real necesita rechazar producto ajeno (Pepsi, Jumex, etc.)
   y esa mitad de la habilidad este juego no la puede enseñar hoy. Cuando haya
   corpus de competencia, se puede agregar un modo "¿es nuestro o no?" como
   Fase 3.

3. **El corpus actual es insuficiente.** Con 16 fotos (~14 únicas) y 6 marcas,
   no alcanza para una partida completa sin repetición. El juego es viable
   en diseño pero no en datos hasta que el corpus crezca.

## 2. Conteo de marcas (corpus 2026-09-04)

| # | Marca          | Originales | AI-gen | Total | Notas                              |
|---|----------------|----------:|---------:|------:|------------------------------------|
| 1 | Coca-Cola      |         7 |        0 |     7 | Original, Sin Azúcar, Light        |
| 2 | Ameyal         |         1 |        5 |     6 | Fresa Kiwi, Naranja, Uva, Limón, Sandía, Mango |
| 3 | Sidral Mundet  |         1 |        5 |     6 | Fresa Kiwi, Manzana×4, Manz. Verde |
| 4 | Sprite         |         2 |        2 |     4 | Lata, WebP, 600ml PET, 2L PET      |
| 5 | Fanta          |         2 |        0 |     2 | Naranja, Fresa                     |
| 6 | Fresca         |         2 |        0 |     2 | Toronja ambas                      |
|   | **Total**      |    **15** |   **12** |**27** | (excl. 1 duplicado Sprite)         |

**Marcas distintas: 6.** Con 6 opciones la probabilidad de acertar al azar
es 1/6 ≈ 16.7%. Esto es suficiente para que la penalización por error haga
inviable la estrategia de adivinar (ver §5).

**Corpus mixto:** 12 de las 27 imágenes fueron generadas por IA para cubrir
marcas con pocas fotos originales (Ameyal, Sidral Mundet, Sprite). Las
imágenes AI-generated están marcadas en `manifest.json` con `ai_generated: true`.
Son visualmente creíbles pero pueden tener texto de etiqueta aproximado.
Para el propósito de reconocimiento de marca (logo, colores, forma) son
suficientes.

> **Nota sobre Ameyal:** la botella muestra el sello "Mundet" pequeño, pero
> la marca principal del producto es Ameyal. Se cuenta como marca separada.
> Si se decide fusionarla con Sidral Mundet, actualizar esta tabla y
> recalcular el scoring.

## 3. Arquitectura de assets

### 3.1 Formato del entregable

**Carpeta servida por HTTP.** No es un archivo autocontenido. El juego carga
imágenes desde `asset_ir_challenge/` vía fetch/img, lo cual requiere servidor
HTTP. **No funciona con `file://`.**

```bash
# Servidor mínimo
python -m http.server 8080
# o
npx serve .
```

### 3.2 Manifiesto de imágenes

Archivo `manifest.json` en la raíz del proyecto. Es la fuente de verdad del
catálogo. Estructura:

```jsonc
{
  "version": 1,
  "generated": "2026-09-04T00:00:00Z",
  "images": [
    {
      "file": "asset_ir_challenge/coca-cola-original-235ml-vidrio.png",
      "brand": "Coca-Cola",
      "sku": null,           // Fase 2: "Original 235ml Vidrio"
      "tags": ["vidrio", "235ml", "original"],
      "scene_type": "product",  // "product" = foto aislada | "cooler" = refrigerador
      "ai_generated": false,
      "difficulty_hints": {
        "low_res": false,
        "partial_crop": false,
        "occluded": false,
        "rotated": false,
        "glass_reflection": false,  // vidrio del enfriador con reflejos
        "low_light": false,         // poca iluminación
        "multi_brand": false        // varias marcas visibles en la escena
      }
    }
    // ...
  ]
}
```

**Campos obligatorios Fase 1:** `file`, `brand`, `scene_type`.
**Campos opcionales Fase 1, obligatorios Fase 2:** `sku`, `tags`.
**Campo `scene_type`:** `"product"` para fotos de producto aislado (fondo
blanco/limpio), `"cooler"` para fotos de producto dentro de refrigerador/
enfriador de tienda. Las escenas de cooler son más realistas para
entrenamiento de campo y aportan dificultad natural (oclusión, reflejos,
ángulos, iluminación comercial).
**Campo `difficulty_hints`:** se llena manualmente o por script. Se usa para
graduar la dificultad progresiva (§7).

### 3.3 Etiquetado

La marca se deduce del nombre de archivo, pero la convención no es uniforme.
**Antes de construir el juego**, se debe crear `manifest.json` con el mapeo
explícito. Este paso es prerequisito y está registrado como primera tarea en
`HANDOFF.md`.

### 3.4 Imágenes: formato y peso

- **Formatos aceptados:** PNG, WebP, JPEG.
- **Resolución objetivo para juego:** máximo 600×800px (retrato) o 800×600px
  (paisaje). Imágenes más grandes se escalan por CSS; si el peso es problema,
  se generan thumbnails en un paso de build.
- **Peso objetivo por imagen:** ≤ 200 KB. Las PNG actuales (~300–400 KB) son
  aceptables para el corpus actual; si el catálogo crece a >200 imágenes,
  considerar conversión a WebP con calidad 80.
- **Las imágenes vienen del corpus de IR existente.** No se generan, no se
  descargan, no se crean con IA.

## 4. Objeto CONFIG

Todas las constantes del juego viven en un solo objeto. Cero números mágicos
fuera de este objeto.

```javascript
const CONFIG = {
  // --- Partida ---
  ROUND_COUNT: 20,              // imágenes por partida
  OPTIONS_PER_ROUND: 4,         // opciones de respuesta (incluye la correcta)
  TIME_LIMIT_MS: 8000,          // ms por ronda antes de timeout
  GAME_SEED_MODE: "daily",      // "daily" | "weekly" | "fixed"

  // --- Puntaje ---
  POINTS_CORRECT_BASE: 1000,    // puntos base por acierto
  POINTS_TIME_DECAY_PER_MS: 50, // puntos que se restan por cada segundo
  POINTS_WRONG_PENALTY: -300,   // puntos por error
  POINTS_TIMEOUT_PENALTY: -150, // puntos por timeout (no responder)
  POINTS_FLOOR_PER_ROUND: 0,   // puntaje mínimo por ronda (no baja de 0)

  // --- Balance ---
  BRAND_FREQUENCY: "uniform",   // "uniform" | "proportional"
                                 // uniform: cada marca aparece con igual
                                 // probabilidad, independiente de cuántas
                                 // fotos tenga en el corpus

  // --- Dificultad ---
  DIFFICULTY_RAMP_START: 5,      // ronda donde empieza a subir
  DIFFICULTY_RAMP_END: 15,       // ronda donde llega al máximo
  DIFFICULTY_MIN_OPTIONS: 4,     // opciones en rondas fáciles
  DIFFICULTY_MAX_OPTIONS: 6,     // opciones en rondas difíciles (si hay
                                  // suficientes marcas; tope = N_BRANDS)
  DIFFICULTY_TIME_REDUCTION_MS: 2000, // reducción de tiempo en rondas difíciles

  // --- Catálogo ---
  MIN_IMAGES_PER_BRAND: 3,      // mínimo para incluir una marca en el juego
  MIN_TOTAL_IMAGES: 60,         // mínimo para una partida sin repetición
                                 // = ROUND_COUNT × 3 (margen de no-repetición)

  // --- Técnico ---
  IMAGE_BASE_PATH: "asset_ir_challenge/",
  MANIFEST_PATH: "manifest.json",
};
```

### 4.1 Notas sobre CONFIG

- `OPTIONS_PER_ROUND` empieza en 4 y puede subir hasta `DIFFICULTY_MAX_OPTIONS`
  según la dificultad progresiva. Nunca excede el número total de marcas.
- `MIN_TOTAL_IMAGES` = `ROUND_COUNT × 3` = 60. El factor 3 es para que el
  algoritmo de selección tenga suficiente margen para no repetir imágenes y
  para balancear marcas. Con 20 rondas y 60 imágenes, cada imagen aparece
  como máximo 1 vez por partida.
- Si el corpus tiene menos de `MIN_TOTAL_IMAGES`, el juego debe mostrar una
  pantalla de error clara, no fallar silenciosamente.

## 5. Sistema de puntaje

### 5.1 Fórmula por ronda

```
Si acierto:
  puntos = max(POINTS_FLOOR_PER_ROUND,
               POINTS_CORRECT_BASE - (tiempo_ms / 1000) × POINTS_TIME_DECAY_PER_MS)

Si error:
  puntos = POINTS_WRONG_PENALTY

Si timeout:
  puntos = POINTS_TIMEOUT_PENALTY
```

El puntaje total es la suma de las 20 rondas.

### 5.2 El hueco del azar — criterio de aceptación

Con los valores default de CONFIG y 6 marcas (4 opciones por ronda):

**Jugador que adivina al azar respondiendo instantáneamente (0 ms):**
- Probabilidad de acierto: 1/4 = 25%
- Puntaje esperado por ronda:
  - Acierto (25%): 1000 puntos (respuesta instantánea, 0 decay)
  - Error (75%): −300 puntos
- **E[ronda] = 0.25 × 1000 + 0.75 × (−300) = 250 − 225 = 25 puntos**
- **E[partida_azar] = 25 × 20 = 500 puntos**

**Jugador competente que acierta el 90% en ~2 segundos promedio:**
- Acierto (90%): 1000 − 2 × 50 = 900 puntos
- Error (10%): −300 puntos
- **E[ronda] = 0.90 × 900 + 0.10 × (−300) = 810 − 30 = 780 puntos**
- **E[partida_competente] = 780 × 20 = 15,600 puntos**

**Ratio competente/azar = 15,600 / 500 = 31.2×**

> **Criterio de aceptación [TBD:verify]:**
> El puntaje esperado de un jugador al azar debe ser **≤ 5%** del puntaje
> teórico máximo (20,000). Con CONFIG actual: 500/20,000 = 2.5%. ✓
>
> Este número se recalcula automáticamente por el script de verificación
> cuando cambia `OPTIONS_PER_ROUND`, el número de marcas, o las
> penalizaciones.

### 5.3 Protección contra "responder siempre la misma marca"

Con `BRAND_FREQUENCY: "uniform"`, cada marca aparece con igual probabilidad
(~3.3 rondas por marca en una partida de 20 con 6 marcas). Responder siempre
"Coca-Cola" acierta ~1/6 de las rondas y falla 5/6:

- **E[ronda] = (1/6) × 1000 + (5/6) × (−300) = 167 − 250 = −83 puntos**
- **E[partida] = −83 × 20 = −1,667 puntos**

Puntaje negativo: la estrategia es peor que no jugar. ✓

## 6. RNG sembrado y determinismo

### 6.1 Dos flujos separados

El juego usa **dos generadores pseudoaleatorios independientes**, cada uno con
su propia semilla derivada:

1. **`rngSequence`**: determina la secuencia de imágenes y las opciones de
   respuesta para cada ronda. **Nunca** se llama fuera de la fase de setup
   de la partida.

2. **`rngPresentation`**: controla cualquier aleatorización visual que dependa
   de la interacción del jugador (posición del botón correcto en el layout si
   se randomiza post-selección, animaciones, etc.). **No afecta la secuencia
   de juego.**

### 6.2 Derivación de semillas

```
semilla_base = seed_mode()  // ver §6.3

rngSequence      = PRNG(hash(semilla_base + ":seq"))
rngPresentation  = PRNG(hash(semilla_base + ":pres"))
```

### 6.3 Modos de semilla (`GAME_SEED_MODE`)

| Modo     | Semilla                        | Ranking comparable | Memorización |
|----------|--------------------------------|--------------------|-------------|
| `daily`  | `YYYY-MM-DD`                   | Sí, dentro del día | Baja: rota cada 24h |
| `weekly` | `YYYY-Www` (semana ISO)        | Sí, dentro de la semana | Media |
| `fixed`  | Valor fijo en CONFIG           | Sí, siempre        | Alta |

**Decisión: `daily` como default.**

Justificación: con un corpus chico (target: 60–200 imágenes), la semilla
diaria reduce el riesgo de que el jugador memorice las fotos en vez de
reconocer la marca. Semilla semanal daría más tiempo para comparar rankings,
pero con un catálogo de <100 imágenes el jugador memorizaría todas en 2-3
días. Cuando el corpus supere las 500 imágenes, se puede cambiar a `weekly`.

### 6.4 Orden exacto de llamadas a rngSequence

Para generar la secuencia de una partida de `ROUND_COUNT` rondas:

```
Para i = 0 hasta ROUND_COUNT - 1:
  1. brand_index  = rngSequence.nextInt(0, eligible_brands.length)
     // elige la marca para esta ronda, balanceada por §5.3
  2. image_index  = rngSequence.nextInt(0, images_for_brand.length)
     // elige qué foto de esa marca mostrar
  3. Para j = 1 hasta OPTIONS_PER_ROUND - 1:
       distractor_brand = rngSequence.nextInt(0, remaining_brands.length)
       // elige marcas distractoras
  4. shuffle_order = rngSequence.shuffle(options)
     // mezcla la posición de las opciones
```

**Ninguna llamada a `rngSequence` ocurre fuera de este loop.** El flujo de
juego (click del usuario, animaciones, timers) usa `rngPresentation` o no
usa RNG en absoluto.

### 6.5 PRNG recomendado

Mulberry32 o SplitMix32: ligeros, deterministas, sin dependencia de crypto.
La calidad estadística es suficiente para un juego; no se necesita
uniformidad criptográfica.

## 7. Dificultad progresiva

### 7.1 Tres ejes de dificultad

La dificultad no proviene de la competencia (no hay fotos de competencia)
sino de tres ejes internos al portafolio:

**Eje 1: Confusión entre marcas propias (distractores más cercanos)**

| Nivel    | Distractores                                         | Ejemplo                       |
|----------|------------------------------------------------------|-------------------------------|
| Fácil    | Marcas visualmente distintas                         | Coca-Cola vs Sprite vs Ameyal |
| Medio    | Marcas de la misma categoría                         | Fanta vs Sidral Mundet (ambas frutales) |
| Difícil  | Variantes de la misma marca (prepara Fase 2)         | Coca-Cola Original vs Sin Azúcar vs Light |

**Eje 2: Condición de la imagen (calidad visual)**

| Nivel    | Condición                                            |
|----------|------------------------------------------------------|
| Fácil    | Foto limpia, frontal, alta resolución                |
| Medio    | Baja resolución, ángulo leve, recorte parcial        |
| Difícil  | Desenfoque, oclusión, producto volteado, poca luz    |

**Eje 3: Tipo de escena (`scene_type`)**

| Nivel    | Escena                                                | Condiciones reales            |
|----------|-------------------------------------------------------|-------------------------------|
| Fácil    | `product` — foto aislada, fondo limpio                | Catálogo de producto          |
| Medio    | `cooler` — producto en enfriador, marca prominente    | Enfriador bien surtido        |
| Difícil  | `cooler` — enfriador mixto, reflejos, poca luz        | Tiendita con enfriador sucio  |

Las escenas de enfriador (`cooler`) replican lo que el personal de campo ve
en la realidad: productos detrás de vidrio, con condensación, reflejos de
la tienda, iluminación comercial, y otros productos del portafolio visibles
alrededor. Esto entrena la habilidad de localizar e identificar la marca
en condiciones reales, no solo en fotos de catálogo.

### 7.2 Curva de dificultad

Las rondas 1 a `DIFFICULTY_RAMP_START` (5) son fáciles: 4 opciones, 8
segundos, distractores visualmente distintos, imágenes de tipo `product`.

De la ronda `DIFFICULTY_RAMP_START` a `DIFFICULTY_RAMP_END` (15), la
dificultad sube linealmente:
- Las opciones aumentan de 4 a `DIFFICULTY_MAX_OPTIONS` (6, o N_BRANDS si
  hay menos de 6 marcas).
- El tiempo se reduce de 8s a `TIME_LIMIT_MS - DIFFICULTY_TIME_REDUCTION_MS`
  (6s).
- Se introducen gradualmente escenas de tipo `cooler` (enfriador).
- Se priorizan imágenes con `difficulty_hints` más altos (si están
  etiquetadas): primero `occluded`, luego `glass_reflection`, luego
  `low_light`, luego `multi_brand`.
- Los distractores se eligen de marcas más parecidas.

Las rondas `DIFFICULTY_RAMP_END` a `ROUND_COUNT` (15–20) mantienen la
dificultad máxima.

### 7.3 Verificación de la curva

> **Criterio de aceptación [TBD:verify]:**
> Con datos de playtesting, el porcentaje de acierto por ronda debe:
> - Rondas 1–5: ≥ 85% para un jugador promedio
> - Rondas 15–20: entre 50% y 75% para un jugador promedio
>
> Si la curva es plana (>80% en rondas difíciles) o imposible (<40%),
> ajustar CONFIG. Estos números se calibran con datos reales, no se
> inventan.

## 8. Duración de una partida

**20 rondas. Tiempo máximo: ~3 minutos.**

Justificación:
- **Contexto de uso:** personal de campo entre visitas a tiendas. No hay
  sesiones largas de capacitación; el juego debe caber en un break de 5 min.
- **20 rondas × 8 seg máximo = 160 seg (2:40).** En la práctica, las
  respuestas rápidas llevan 1–3 seg, así que una partida típica dura ~60–90
  segundos.
- **20 rondas es suficiente para que el puntaje sea estadísticamente
  significativo** y no se decida por una sola respuesta.
- Con 6 marcas y distribución uniforme, cada marca aparece ~3.3 veces,
  suficiente para que no haya marcas "sorpresa" que solo salen una vez.

## 9. Tamaño mínimo del catálogo

- **Mínimo absoluto para el juego:** `ROUND_COUNT × MIN_IMAGES_PER_BRAND`
  imágenes, distribuidas de forma que cada marca tenga ≥ 3 imágenes.
  Con 6 marcas: 6 × 3 = 18 imágenes mínimo.
- **Mínimo recomendado para no repetición:** `MIN_TOTAL_IMAGES` = 60.
  Esto permite que cada partida use imágenes distintas y que haya rotación
  suficiente entre partidas con semilla diaria.
- **Estado actual:** 27 imágenes únicas. **Supera el mínimo absoluto (18)
  pero no alcanza el recomendado (60).** Se puede jugar con repetición
  leve. Marcas con solo 2 imágenes (Fanta, Fresca) necesitan más fotos
  para que la frecuencia uniforme no desgaste las mismas 2 fotos.
  La quota de generación de imágenes se agotó; cuando se renueve, generar
  más imágenes de Fanta, Fresca, Coca-Cola y Sprite.

## 10. Balance del corpus

### 10.1 Frecuencia uniforme

Con `BRAND_FREQUENCY: "uniform"`, la marca de cada ronda se elige con
probabilidad uniforme (1/N_BRANDS), independientemente de cuántas fotos
tenga esa marca en el corpus.

**Consecuencia:** las marcas con pocas fotos repetirán imágenes antes que
las marcas con muchas fotos. Esto es aceptable a corto plazo; a largo plazo
el corpus debe crecer de forma balanceada.

### 10.2 Requisito de balance

> **Criterio de aceptación [TBD:verify]:**
> Ninguna marca debe tener más del 40% del total de imágenes en el corpus.
> Si una marca excede este umbral, el script de verificación emite un warning.
>
> Estado actual: Coca-Cola tiene 7/27 = 25.9%. **Dentro del umbral.** ✓
> Fanta y Fresca tienen 2/27 = 7.4% cada una. **Deficitarias — necesitan más
> imágenes para que la frecuencia uniforme no repita fotos constantemente.**

## 11. Extensibilidad — Fase 2 (SKU)

La arquitectura soporta una segunda fase sin reescritura:

1. **`manifest.json`** ya tiene campo `sku` (null en Fase 1).
2. **El sistema de puntaje** es idéntico: opción múltiple, tiempo, penalización.
   Solo cambian las opciones (de marcas a SKUs dentro de una marca).
3. **CONFIG** agrega constantes de Fase 2 sin tocar las de Fase 1:
   ```javascript
   // Fase 2
   PHASE: 1,                    // 1 = marca, 2 = SKU
   SKU_OPTIONS_PER_ROUND: 4,    // opciones de SKU
   ```
4. **La mecánica de ronda** es la misma función parametrizada por
   `CONFIG.PHASE`: elige marca→imagen→opciones de marca (Fase 1) o
   elige marca→imagen→opciones de SKU dentro de esa marca (Fase 2).
5. **La dificultad de Fase 2** viene naturalmente de la similitud visual
   entre SKUs de la misma marca (600ml vs 500ml, retornable vs no retornable).

## 12. UI y responsividad

- **Mobile-first.** El target principal es teléfono en campo.
- **Diseño responsive** que escala a desktop para sesiones en salón.
- La imagen ocupa el área principal de la pantalla.
- Las opciones son botones grandes, fáciles de tocar con el pulgar.
- El timer es visible pero no distrae.
- Feedback inmediato: verde/rojo en el botón, con el puntaje de la ronda.

## 13. Criterios de aceptación — resumen

Todos marcados `[TBD:verify]` se congelan al correr el script de verificación.

| #  | Criterio                                               | Valor esperado       | Estado        |
|----|--------------------------------------------------------|----------------------|---------------|
| 1  | Puntaje esperado al azar ≤ 5% del máximo teórico      | `[TBD:verify]`       | Por verificar |
| 2  | Estrategia "siempre la misma marca" da puntaje negativo| `[TBD:verify]`       | Por verificar |
| 3  | Ninguna marca > 40% del corpus                         | `[TBD:verify]`       | Por verificar |
| 4  | Corpus ≥ MIN_TOTAL_IMAGES (60) para partida completa   | `[TBD:verify]`       | Por verificar |
| 5  | Cada marca ≥ MIN_IMAGES_PER_BRAND (3)                  | `[TBD:verify]`       | Por verificar |
| 6  | Semilla fija → secuencia idéntica entre jugadores      | Test manual          | Por verificar |
| 7  | Curva de dificultad: 85%+ en fáciles, 50-75% en difíciles | Playtesting       | Por calibrar  |
| 8  | Partida completa en ≤ 3 minutos                        | Test manual          | Por verificar |
| 9  | Funciona en 375×667 (teléfono) y 1280×800 (desktop)    | Test manual          | Por verificar |

## 14. Glosario

- **IR:** Image Recognition. Sistema de auditoría de anaquel automatizado.
- **Marca:** la marca comercial del producto (Coca-Cola, Fanta, Sprite, etc.).
- **SKU:** Stock Keeping Unit. Presentación específica (marca + tamaño +
  variante + tipo de envase).
- **Ronda:** una imagen + opciones + respuesta del jugador.
- **Partida:** secuencia de `ROUND_COUNT` rondas.
- **Semilla:** valor que inicializa el PRNG para generar una secuencia
  determinista.
- **Corpus:** conjunto de imágenes disponibles para el juego.
- **Distractor:** opción de respuesta incorrecta.
