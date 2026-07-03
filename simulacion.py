"""
lumibright_sim.py
=================
Simulación del Sistema de Control Automático de Brillo de Pantalla — LumiBright
Controlador PI Discreto | Teoría de Control | UTN-FRBA | K4011

Autores : Riolffi, Ignacio Joaquín — Rohling Insua, Nataly Sofía
Profesor: Omar Oscár Civale
Fecha   : 2026

Dependencias: numpy, matplotlib
Uso          : python lumibright_sim.py
Salida       : carpeta graficos/ con PNG por escenario + comparativo

════════════════════════════════════════════════════════════
MODELO DEL SISTEMA
════════════════════════════════════════════════════════════
El sistema ajusta el duty cycle PWM de la retroiluminación para que la
iluminancia TOTAL percibida por el usuario sea igual al setpoint.

  lux_total[k] = lux_ambiente[k] + lux_pantalla[k]
  lux_pantalla[k] = duty[k] * PLANTA_K   (modelo lineal de la planta)

  setpoint = 500 lux  (iluminancia total objetivo — ISO 9241)
  e[k]     = setpoint - lux_total[k]     (error: cuánto falta o sobra)

  Si e > 0  → la pantalla aporta poco → subir duty cycle
  Si e < 0  → la pantalla aporta demasiado → bajar duty cycle

El controlador PI calcula el ajuste incremental del duty cycle hasta que
lux_total converja al setpoint, independientemente de lux_ambiente.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# 0. CONFIGURACIÓN GENERAL
# ─────────────────────────────────────────────────────────────────────────────

OUTPUT_DIR = Path("graficos")
OUTPUT_DIR.mkdir(exist_ok=True)

plt.rcParams.update({
    "figure.dpi"       : 150,
    "axes.grid"        : True,
    "grid.alpha"       : 0.35,
    "axes.spines.top"  : False,
    "axes.spines.right": False,
    "font.size"        : 10,
})

# ─────────────────────────────────────────────────────────────────────────────
# 1. PARÁMETROS DEL SISTEMA
# ─────────────────────────────────────────────────────────────────────────────

SETPOINT   = 500.0   # [lux] — iluminancia total objetivo (ISO 9241)
PLANTA_K   = 700.0   # [lux / duty] — aporte máximo de la retroiluminación
                      # (duty=1 → 700 lux; duty=0 → 0 lux)
Kp         = 0.0008  # Ganancia proporcional del controlador PI
Ki         = 0.0001  # Ganancia integral del controlador PI
DT         = 0.5     # [s]   — período de muestreo (2 Hz según BH1750)
T_SIM      = 40.0    # [s]   — duración total de simulación
DUTY_MIN   = 0.0     # Límite inferior del actuador
DUTY_MAX   = 1.0     # Límite superior del actuador
RUIDO_STD  = 8.0     # [lux] — desviación estándar del ruido del sensor

N = int(T_SIM / DT)  # número de pasos de simulación

# ─────────────────────────────────────────────────────────────────────────────
# 2. CONTROLADOR PI DISCRETO (Euler hacia adelante + anti-windup)
# ─────────────────────────────────────────────────────────────────────────────

def pi_step(error, integral_prev, duty_prev):
    """
    Un paso del controlador PI discreto.

    Fórmula de recurrencia:
        u[k] = u[k-1] + Kp * e[k] + Ki * dt * Σe

    Parámetros
    ----------
    error        : float  — e[k] = setpoint - lux_total medido
    integral_prev: float  — acumulado integral hasta k-1
    duty_prev    : float  — duty cycle del ciclo anterior

    Retorna
    -------
    duty_nuevo   : float  — duty cycle calculado y saturado [0,1]
    integral_new : float  — integral actualizada (con anti-windup)
    """
    integral_cand = integral_prev + error * DT
    delta_u       = Kp * error + Ki * integral_cand
    duty_cand     = duty_prev + delta_u

    # Anti-windup: congela integral si el actuador está en los límites
    if DUTY_MIN < duty_cand < DUTY_MAX:
        integral_new = integral_cand
    else:
        integral_new = integral_prev

    duty_nuevo = np.clip(duty_prev + Kp * error + Ki * integral_new,
                         DUTY_MIN, DUTY_MAX)
    return duty_nuevo, integral_new


# ─────────────────────────────────────────────────────────────────────────────
# 3. MODELO DE LA PLANTA + SENSOR
# ─────────────────────────────────────────────────────────────────────────────

def lux_total_medido(duty, lux_ambiente, ruido=True):
    """
    Calcula la iluminancia total percibida por el sensor BH1750.

    lux_total = lux_ambiente + duty * PLANTA_K + ruido_gaussiano

    El sensor no distingue entre luz externa y luz de la pantalla;
    mide la iluminancia combinada que llega a su fotodiodo.
    """
    lux = lux_ambiente + duty * PLANTA_K
    if ruido:
        lux += np.random.normal(0, RUIDO_STD)
    return max(0.0, lux)


# ─────────────────────────────────────────────────────────────────────────────
# 4. SIMULACIÓN DEL LAZO CERRADO
# ─────────────────────────────────────────────────────────────────────────────

def simular(perfil_lux_amb, nombre, duty_inicial=0.5, ruido=True):
    """
    Ejecuta la simulación completa del lazo cerrado para un perfil dado.

    Condición inicial: duty_inicial define el brillo de partida.
    El controlador lleva la iluminancia total al SETPOINT ajustando duty.
    """
    tiempo       = np.arange(N) * DT
    lux_amb_arr  = np.array(perfil_lux_amb)
    lux_tot_arr  = np.zeros(N)
    error_arr    = np.zeros(N)
    duty_arr     = np.zeros(N)
    integral_arr = np.zeros(N)

    duty     = duty_inicial
    integral = 0.0

    for k in range(N):
        lux_amb  = lux_amb_arr[k]
        lux_med  = lux_total_medido(duty, lux_amb, ruido)
        error    = SETPOINT - lux_med

        duty, integral = pi_step(error, integral, duty)

        lux_tot_arr[k]  = lux_med
        error_arr[k]    = error
        duty_arr[k]     = duty
        integral_arr[k] = integral

    return {
        "nombre"      : nombre,
        "tiempo"      : tiempo,
        "lux_ambiente": lux_amb_arr,
        "lux_total"   : lux_tot_arr,
        "error"       : error_arr,
        "duty"        : duty_arr * 100,   # [%] para graficar
        "integral"    : integral_arr,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 5. PERFILES DE LUZ AMBIENTE
# ─────────────────────────────────────────────────────────────────────────────

def perfil_escalon_subida():
    """Escenario 1: luz ambiente sube de 200 → 600 lux a los 15 s.
    (ej. usuario sale de un interior a un pasillo bien iluminado)"""
    p = np.full(N, 200.0)
    p[int(15 / DT):] = 600.0
    return p

def perfil_escalon_bajada():
    """Escenario 2: luz ambiente baja de 400 → 80 lux a los 15 s.
    (ej. usuario apaga la luz de la habitación)"""
    p = np.full(N, 400.0)
    p[int(15 / DT):] = 80.0
    return p

def perfil_ruido():
    """Escenario 3: luz ambiente ≈ 300 lux con variaciones aleatorias ±60 lux.
    (ej. paso de nubes, reflejos, sombras intermitentes)"""
    np.random.seed(7)
    return np.clip(300.0 + np.random.uniform(-60, 60, N), 0, None)

def perfil_saturacion():
    """Escenario 4: luz ambiente muy alta (650 lux constante) → actuador
    satura en 0 % porque la pantalla no puede reducir la luz externa."""
    return np.full(N, 650.0)


# ─────────────────────────────────────────────────────────────────────────────
# 6. GRAFICADO POR ESCENARIO
# ─────────────────────────────────────────────────────────────────────────────

COLORES = {
    "ambiente" : "#4C72B0",
    "total"    : "#DD8452",
    "setpoint" : "#55A868",
    "error"    : "#C44E52",
    "duty"     : "#8172B2",
}

def graficar_escenario(res, idx):
    fig = plt.figure(figsize=(11, 8.5))
    fig.suptitle(
        f"Escenario {idx}: {res['nombre']}",
        fontsize=13, fontweight="bold", y=0.99
    )
    gs = gridspec.GridSpec(3, 1, hspace=0.52)
    t  = res["tiempo"]

    # ── Panel 1: iluminancia ambiente vs total vs setpoint ──────────────────
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(t, res["lux_ambiente"], color=COLORES["ambiente"],
             lw=2.0, label="Luz ambiente [lux]", zorder=3)
    ax1.plot(t, res["lux_total"],   color=COLORES["total"],
             lw=1.5, alpha=0.85, label="Lux total medido (sensor)", zorder=2)
    ax1.axhline(SETPOINT, color=COLORES["setpoint"],
                lw=1.3, ls="--", label=f"Setpoint ({SETPOINT} lux)")
    ax1.set_ylabel("Iluminancia [lux]")
    ax1.set_title("Señal de entrada, retroalimentación y referencia")
    ax1.legend(loc="lower right", fontsize=8)

    # ── Panel 2: error e[k] ─────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[1])
    ax2.plot(t, res["error"], color=COLORES["error"], lw=1.6, label="Error e[k]")
    ax2.axhline(0,   color="black", lw=0.8)
    ax2.axhline(+25, color="gray",  lw=0.9, ls=":", alpha=0.7, label="Banda ±50 lux")
    ax2.axhline(-25, color="gray",  lw=0.9, ls=":", alpha=0.7)
    ax2.fill_between(t, -25, 25, alpha=0.08, color="gray")
    ax2.set_ylabel("Error [lux]")
    ax2.set_title("Señal de error: e[k] = setpoint − lux_total")
    ax2.legend(loc="upper right", fontsize=8)

    # ── Panel 3: duty cycle PWM ─────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[2])
    ax3.plot(t, res["duty"], color=COLORES["duty"], lw=1.6, label="Duty cycle")
    ax3.axhline(100, color="red", lw=0.8, ls="--", alpha=0.55, label="Límite 100 %")
    ax3.axhline(0,   color="red", lw=0.8, ls="--", alpha=0.55, label="Límite 0 %")
    ax3.set_ylim(-5, 110)
    ax3.set_ylabel("Duty cycle [%]")
    ax3.set_xlabel("Tiempo [s]")
    ax3.set_title("Señal de control: acción del actuador PWM")
    ax3.legend(loc="upper right", fontsize=8)

    path = OUTPUT_DIR / f"escenario_{idx}.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {path}")
    return path


# ─────────────────────────────────────────────────────────────────────────────
# 7. GRÁFICO COMPARATIVO
# ─────────────────────────────────────────────────────────────────────────────

def graficar_comparativo(resultados):
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5))
    fig.suptitle(
        "LumiBright — Comparativo de escenarios\nError e[k] = setpoint − lux_total",
        fontsize=12, fontweight="bold"
    )
    cols = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]

    for ax, res, color in zip(axes.flat, resultados, cols):
        t = res["tiempo"]
        ax.plot(t, res["error"], color=color, lw=1.5, label="Error")
        ax.axhline(0,   color="black", lw=0.7)
        ax.axhline(+25, color="gray",  lw=0.8, ls=":", alpha=0.7, label="±25 lux")
        ax.axhline(-25, color="gray",  lw=0.8, ls=":", alpha=0.7)
        ax.fill_between(t, -25, 25, alpha=0.07, color="gray")
        ax.set_title(res["nombre"], fontsize=8.5, fontweight="bold")
        ax.set_xlabel("Tiempo [s]", fontsize=8)
        ax.set_ylabel("Error [lux]", fontsize=8)
        ax.legend(fontsize=7, loc="upper right")
        ax.tick_params(labelsize=8)

    plt.tight_layout()
    path = OUTPUT_DIR / "comparativo_escenarios.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {path}")


# ─────────────────────────────────────────────────────────────────────────────
# 8. REPORTE DE MÉTRICAS
# ─────────────────────────────────────────────────────────────────────────────

BANDA = 50.0

def reportar(res):
    ee      = res["error"][int(25 / DT):]
    max_ee  = np.max(np.abs(ee))
    mean_ee = np.mean(np.abs(ee))
    ok      = max_ee <= BANDA
    print(f"\n  ► {res['nombre']}")
    print(f"    Error máx.  (estado estable): {max_ee:7.2f} lux")
    print(f"    Error medio (estado estable): {mean_ee:7.2f} lux")
    print(f"    Duty cycle final            : {res['duty'][-1]:7.2f} %")
    print(f"    Dentro de banda ±{BANDA} lux  : {'✓ SÍ' if ok else '✗ NO'}")


# ─────────────────────────────────────────────────────────────────────────────
# 9. PUNTO DE ENTRADA
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 64)
    print("  LumiBright — Simulación del controlador PI de brillo")
    print(f"  Setpoint: {SETPOINT} lux | Kp={Kp} | Ki={Ki} | dt={DT} s")
    print(f"  Planta: duty × {PLANTA_K} lux | Ruido sensor: σ={RUIDO_STD} lux")
    print("=" * 64)

    np.random.seed(0)

    escenarios = [
        ("1 — Escalón (subida 200→600 lux a 15 s)",   perfil_escalon_subida()),
        ("2 — Escalón (bajada 400→80 lux a 15 s)",    perfil_escalon_bajada()),
        ("3 — Ruido del sensor (±60 lux)",             perfil_ruido()),
        ("4 — Saturación (650 lux, duty → 0%)",        perfil_saturacion()),
    ]

    resultados = []
    print("\n[1/3] Simulando escenarios...")
    for nombre, perfil in escenarios:
        res = simular(perfil, nombre, duty_inicial=0.43, ruido=True)
        resultados.append(res)
        reportar(res)

    print("\n[2/3] Gráficos individuales...")
    for i, res in enumerate(resultados, 1):
        graficar_escenario(res, i)

    print("\n[3/3] Gráfico comparativo...")
    graficar_comparativo(resultados)

    print(f"\n{'='*64}")
    print(f"  Completado. Gráficos en: ./{OUTPUT_DIR}/")
    print("="*64)
