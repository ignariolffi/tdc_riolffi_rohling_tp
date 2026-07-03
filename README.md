# Dashboard - Simulación de Control Automático de Brillo

## Descripción

Este dashboard fue desarrollado como complemento del Trabajo Final Integrador (TFI) de **Teoría de Control** de la **UTN-FRBA**.

Su objetivo es mostrar de forma gráfica el funcionamiento de un sistema de control automático de brillo de pantalla mediante un **controlador PI**, permitiendo modificar distintos parámetros y observar cómo cambia la respuesta del sistema frente a diferentes condiciones de iluminación.

La simulación representa el comportamiento de un dispositivo que ajusta automáticamente el brillo de su pantalla según la luz del ambiente.

---

## Requisitos

No es necesario instalar ningún programa.

Solo se debe abrir el archivo **dashboard_tdc_riolffi_rohling.html** en un navegador moderno como Google Chrome, Microsoft Edge o Mozilla Firefox.

---

## Importante

> **Este dashboard no es responsive.**

Fue diseñado para utilizarse en computadoras de escritorio y funciona correctamente únicamente cuando **todo el contenido entra en pantalla**. Si la resolución del monitor es baja o el navegador tiene un nivel de zoom elevado, algunos elementos pueden verse desalineados.

Se recomienda utilizar una resolución de **1920 × 1080** o superior y mantener el navegador en pantalla completa con un zoom del **100%**.

---

# Funcionamiento

El dashboard permite modificar distintos parámetros del controlador y del sistema mientras la simulación se ejecuta automáticamente.

Cada vez que se cambia un valor, todas las métricas y los gráficos se recalculan y actualizan en tiempo real.

---

# Escenarios de prueba

Se pueden seleccionar cinco escenarios para analizar el comportamiento del controlador.

## Escalón de subida

La iluminación ambiente aumenta bruscamente.

Simula situaciones como encender una lámpara o ingresar a un ambiente más iluminado.

---

## Escalón de bajada

La iluminación ambiente disminuye de forma repentina.

Representa, por ejemplo, apagar una luz o pasar a un lugar con menor iluminación.

---

## Ruido del sensor

La iluminación presenta pequeñas variaciones aleatorias.

Permite observar cómo responde el controlador frente a perturbaciones continuas.

---

## Saturación

La iluminación ambiente supera la capacidad máxima de compensación del sistema.

En este caso el controlador llega al límite de actuación del actuador.

---

## Flash

Se produce un aumento muy intenso de la iluminación durante unos segundos.

Luego el controlador intenta devolver el sistema al estado estable.

---

# Parámetros configurables

## Valor de entrada (Referencia)

Es el valor de iluminancia que el sistema intenta mantener.

Se expresa en **lux**.

Al aumentar este valor, el controlador intentará obtener una iluminación total mayor.

---

## Kp (Ganancia proporcional)

Determina qué tan rápido responde el controlador ante un error.

- Valores bajos producen una respuesta más lenta.
- Valores altos hacen que el sistema reaccione más rápido, aunque si son demasiado elevados pueden generar oscilaciones.

---

## Ki (Ganancia integral)

Corrige el error acumulado con el paso del tiempo.

Su función principal es eliminar el error permanente una vez que el sistema alcanza el estado estable.

Si este valor es demasiado grande, la respuesta puede volverse inestable.

---

## Ruido del sensor (σ)

Representa las pequeñas imprecisiones de la medición del sensor de luz.

Al aumentar este parámetro:

- la medición será menos precisa;
- aparecerán mayores variaciones en las curvas;
- el controlador deberá realizar más correcciones.

---

## Duty Cycle inicial

Es el porcentaje de brillo con el que comienza la simulación.

Solo define la condición inicial del sistema. Luego el controlador modifica automáticamente este valor según las condiciones de iluminación.

---

## Duración de la simulación

Permite elegir cuánto tiempo dura la simulación.

Un tiempo mayor permite observar mejor el comportamiento durante el estado transitorio y el estado estable.

---

# Indicadores

En la parte superior del dashboard se muestran diferentes métricas calculadas automáticamente.

## Error máximo

Indica el mayor error registrado durante el estado estable.

Se utiliza para verificar si el sistema cumple con la banda de tolerancia de **±50 lux**.

---

## Error medio

Muestra el promedio del error una vez estabilizado el sistema.

Mientras menor sea este valor, mayor será la precisión del controlador.

---

## Duty Cycle final

Indica el porcentaje de brillo con el que finaliza la simulación.

Representa la acción final realizada por el controlador sobre el actuador.

---

## Valor de referencia

Muestra el valor de entrada (setpoint) seleccionado para la simulación.

---

# Gráficos

El dashboard presenta tres gráficos principales.

## Señales de iluminancia

Muestra:

- La iluminación ambiente.
- La iluminación total medida por el sensor.
- El valor de referencia (setpoint).

Permite observar cómo el controlador intenta mantener la iluminación total cercana al valor deseado.

---

## Señal de error

Representa la diferencia entre la referencia y la iluminación medida.

También muestra la banda de **±50 lux**, utilizada para determinar si el sistema se encuentra estable.

---

## Señal de control

Representa la evolución del **Duty Cycle PWM**, es decir, la señal que el controlador envía al actuador para aumentar o disminuir el brillo de la pantalla.

---

# Objetivo del dashboard

El objetivo de este dashboard es complementar la simulación desarrollada para el Trabajo Práctico Integrador, permitiendo visualizar de manera interactiva cómo afectan los distintos parámetros del controlador PI y las perturbaciones del entorno al comportamiento del sistema.

De esta forma resulta más sencillo comprender la respuesta del controlador, analizar su estabilidad y comparar el comportamiento del sistema en cada uno de los escenarios propuestos.
