# Simulador en Tiempo Real — Control Automático de Brillo de Pantalla

**Trabajo Práctico Integrador — Teoría de Control (K4011) — UTN FRBA**
Riolffi, Ignacio Joaquín · Rohling Insua, Nataly Sofia

Este documento explica cómo funciona el dashboard y da un paso a paso para reproducir cada uno de los 5 escenarios de prueba descriptos en el informe, de forma que se puedan mostrar en vivo, sumado a probar cualquier otro caso que pueda surgir.

---

## 1. Explicacion del Dashboard

Es una simulación interactiva, en el navegador, del sistema de control de brillo de pantalla en donde un controlador **PI (Proporcional-Integral)** ajusta el duty cycle de la retroiluminación para que el brillo total de la pantalla se mantenga cerca de un valor de referencia (setpoint), a pesar de los cambios en la luz ambiente.

No requiere instalar nada: es un único archivo HTML que corre 100% en el navegador (no usa internet ni backend).

### Relación con Diagrama de Bloques

| Bloque del diagrama | Dónde está en el dashboard |
|---|---|
| Referencia / Setpoint — r(t) | Slider "Valor nominal — Setpoint θi" |
| Controlador C(s) — PI | Sliders "Kp — Ganancia proporcional" y "Ki — Ganancia integral" |
| Actuador — PWM + LEDs | Salida `u[k]` = duty cycle, gráfico 3 |
| Proceso P(s) — Planta (pantalla) | Slider "PLANTA_K — Aporte máx. pantalla" |
| Perturbación d(t) — luz ambiente | Sliders "Luz ambiente base" y "Amplitud/Duración — perturbación externa" |
| Sensor H(s) — BH1750 | Slider "Ruido del sensor — σ BH1750" |
| Salida y(t) — brillo total | Gráfico 6 (θo) |

---

## 2. Funcionamiento del Modelo

En cada ciclo de simulación (cada `DT = 0.5 s`, igual que el sensor real a 2 Hz):

1. Se calcula la luz ambiente actual (base + perturbación, si hay alguna activa).
2. Se calcula el **brillo total** de la pantalla: `ambiente + duty × brillo_máximo`.
3. El sensor "lee" ese brillo total, pero con un poco de ruido aleatorio (así se simula la imprecisión real del BH1750).
4. Se calcula el **error**: `setpoint − lectura_del_sensor`.
5. El controlador PI usa ese error para ajustar el duty cycle (0% a 100%, nunca se pasa de los límites físicos del actuador).
6. Se repite.

Todo esto se grafica en tiempo real en los 6 gráficos de la pantalla.

---

## 3. Controles del panel lateral

| Control | Qué hace | Rango |
|---|---|---|
| **Valor nominal — Setpoint θi** | El brillo objetivo que el sistema intenta mantener | 100 – 1000 lux |
| **Umbral de error admisible** | Cuánto se puede desviar el sistema del setpoint y seguir considerándose "estable" (banda verde en el gráfico de error) | 5 – 200 lux |
| **Kp** | Qué tan fuerte reacciona el controlador al error del instante actual | 0.0001 – 0.003 |
| **Ki** | Qué tan rápido el controlador elimina el error residual acumulado en el tiempo | 0.00001 – 0.0005 |
| **Ruido del sensor — σ BH1750** | Cuánto "tiembla" la lectura del sensor por imprecisión del BH1750, aunque la luz real no cambie | 0 – 50 lux |
| **PLANTA_K — Aporte máx. pantalla** | Cuánto lux aporta la retroiluminación cuando está al 100% de duty cycle. En el TP este valor es fijo en 700 lux; acá se dejó ajustable para poder explorar otros casos, por ejemplo otras pantallas | 100 – 1500 lux |
| **Luz ambiente base** | El nivel de luz del entorno antes de aplicar cualquier perturbación. Se puede mover en cualquier momento, incluso con la simulación corriendo (sirve para simular un escalón) | 0 – 700 lux |
| **Velocidad de la simulación** | Solo cambia qué tan rápido se ve avanzar el reloj en pantalla. No afecta el modelo ni los resultados | 1x (lento) – 10x (rápido) |
| **Amplitud — perturbación externa** | Cuánto sube (+) o baja (−) la luz ambiente durante una perturbación temporal (pulso tipo flash) | −300 a +300 lux |
| **Duración — perturbación externa** | Cuánto dura el pulso antes de que la luz ambiente vuelva sola a su valor de partida | 1 – 20 s |

**Botón "🌤 Inyectar perturbación externa"**: dispara la perturbación temporal configurada con Amplitud + Duración. Después de ese tiempo, la luz ambiente vuelve sola al valor de "Luz ambiente base".

**Botón Start/Stop** (arriba a la derecha): pausa o reanuda la simulación sin perder el historial de datos.

> El duty cycle inicial del sistema está fijo en **43%**, igual que en el informe (condición de reposo en iluminación moderada).

---

## 4. Cómo leer la pantalla

- **5 tarjetas de métricas** (arriba): valores instantáneos — θi Entrada, error actual e[k], salida controlador (%), θo Respuesta planta y realimentación f(σ).
- **Indicador "● Estable / ● Fuera de banda"** (arriba a la derecha): se pone verde cuando el error está dentro del margen aceptado, y rojo cuando no.
- **6 gráficos**, cada uno con su leyenda de colores arriba:
  1. Panorama general (setpoint, brillo total y lectura del sensor juntos)
  2. Señal de Error, con la banda de tolerancia sombreada
  3. Duty cycle del controlador (0–100%)
  4. Luz ambiente (con la perturbación, si está activa)
  5. Lectura del sensor sola
  6. Brillo total de la pantalla solo

---

## 5. Paso a paso: cómo mostrar cada escenario del TP

Antes de cada escenario, conviene **dejar los parámetros del controlador en los valores del informe** (son los que vienen por defecto al abrir el archivo):

- Setpoint θi: **500 lux**
- Umbral de error admisible: **50 lux**
- Kp — Ganancia proporcional: **0.0008**
- Ki — Ganancia integral: **0.0001**
- Ruido del sensor — σ BH1750: **8 lux**
- PLANTA_K — Aporte máx. pantalla: **700 lux**

Si tocaste algo mientras probabas, lo más simple es **recargar la página** (F5) para volver a estos valores por defecto.

---

### Escenario 1 — Escalón de subida (200 → 600 lux)

*Simula pasar de un ambiente oscuro a uno muy iluminado (por ejemplo, encender la luz de una habitación).*

1. Con la simulación detenida, poné **"Luz ambiente base"** en **200 lux**.
2. Apretá **▶ Start**.
3. Dejá correr ~15 segundos (mirá el eje de tiempo del gráfico).
4. A los **15 s**, arrastrá el slider de **"Luz ambiente base"** hasta **600 lux**. El cambio se aplica al instante, como un escalón.

---

### Escenario 2 — Escalón de bajada (400 → 80 lux)

*Simula apagar la luz principal de una habitación.*

1. Simulación detenida, **"Luz ambiente base"** en **400 lux**.
2. **▶ Start**.
3. A los **15 s**, bajá el slider de **"Luz ambiente base"** a **80 lux**.
---

### Escenario 3 — Condiciones adversas (300 ± 60 lux, ruido continuo)

*Simula nubes pasando frente a una ventana, sombras o reflejos variables.*
1. Simulación detenida, **"Luz ambiente base"** en **300 lux**. **▶ Start**.
2. Cada 2–3 segundos, movés a mano el slider entre **240 y 360 lux** (±60 sobre 300), de forma irregular, simulando el "parpadeo" de nubes.

---

### Escenario 4 — Saturación del actuador (650 lux constante)

*Simula uso bajo luz solar directa o ambiente muy iluminado.*

1. Simulación detenida, **"Luz ambiente base"** en **650 lux** (no hace falta tocar nada más).
2. **▶ Start** y dejar correr.
---

### Escenario 5 — Perturbación instantánea y breve (flash de 1200 lux por 2 s)

*Simula un flash de cámara o un reflejo directo de sol sobre el sensor.*

> ⚠️ **Nota importante:** los sliders actuales no llegan a un pulso de +900 lux (necesario para pasar de 300 a 1200 lux), porque el slider de "Amplitud — perturbación externa" tiene un tope de +300 lux. Con los controles actuales solo se puede llegar a un pulso de 300 → 600 lux, que muestra el mismo comportamiento cualitativo.

**Con los controles actuales (pulso aproximado, hasta 600 lux):**
1. Simulación detenida, **"Luz ambiente base"** en **300 lux**. **▶ Start**.
2. Dejá correr hasta los **10 s**.
3. Poné **"Amplitud — perturbación externa"** en **+300 lux** y **"Duración — perturbación externa"** en **2 s**.
4. A los 10 s, apretá **🌤 Inyectar perturbación externa**.

---

### Escenario 6 — Falla interna: degradación de LEDs

1. Dejá los parámetros por defecto. **"Luz ambiente base"** en un valor bajo, por ejemplo **200 lux** (para que el sistema realmente necesite del aporte de la pantalla).
2. **▶ Start** y dejá correr unos segundos para ver el sistema estabilizado normalmente.
3. Mientras corre, bajá el slider **"PLANTA_K — Aporte máx. pantalla"** de 700 a un valor bajo, por ejemplo **250 lux** — esto simula LEDs muy degradados que ya no aportan el brillo de fábrica.

---

## 6. Archivo

- `tfi_realtime_PI.html` — el dashboard completo, autocontenido, se abre con doble clic en cualquier navegador moderno (Chrome, Firefox, Edge).
