# Auditoría General de Calidad, Rendimiento y Estabilidad: Zona del Campamento

**Fecha:** 14 de Noviembre de 2026  
**Auditor:** Agente 3 (Auditoría General y Calidad del Software)  
**Proyecto:** *Laberinto: El Umbral de Ceniza* (`lab_v2`)  
**Alcance:** Campamento (*Claro de Ceniza*), ciclo de vida, persistencia, interfaz gráfica, efectos, audio y casos borde.

---

## 1. Resumen Ejecutivo del Estado del Campamento

La zona del **Campamento (*Claro de Ceniza*)** constituye el núcleo narrativo, punto de retorno y centro de preparación del jugador antes de descender al laberinto. A nivel estético y conceptual, el campamento cuenta con un apartado visual pixel-art atmosférico sobresaliente, efectos procedimentales envolventes (niebla, fuego, luciérnagas) y un sistema de control directo.

Sin embargo, tras una inspección técnica estricta y exhaustiva de solo lectura sobre el código fuente (`pantallas.py`, `app.py`, `ambiente.py`, `arte_pixel.py`, `efectos.py`, `tema.py` y `render.py`), se concluye que **el campamento presentaba vulnerabilidades y defectos de diseño secundarios importantes más allá de los problemas primarios de colisión y física diagonal asignados a los Agentes 1 y 2**.

Entre los hallazgos más destacados se encuentran:
1. **Riesgo crítico de corrupción de partidas guardadas:** La persistencia de `checkpoint.json` se realiza sin atomicidad (escritura directa no transaccional), provocando la pérdida total irreversible de fragmentos y pistas acumuladas si el juego se cierra o interrumpe durante el guardado.
2. **Desincronización y bugs de lógica en interacción:** El mensaje de apertura del Umbral nunca se muestra debido a un temporizador en cero (`self.mensaje_tiempo = 0`), y las armaduras caídas quedan permanentemente trabadas en estado inerte si el jugador se aproxima mientras se están levantando.
3. **Pérdida de control por pérdida de foco (*Sticky Keys*):** El gestor de eventos de teclado retiene teclas indefinidamente ante cambios de foco de ventana (Alt+Tab), haciendo que el personaje camine automáticamente contra paredes.
4. **Sobrecarga de renderizado y asignaciones continuas de memoria:** La función `pixelar_region` ejecuta dos reescalados completos de 1100×720 por cuadro en CPU sin aceleración por hardware, y las transiciones de pantalla instancian superficies completas por cuadro generando presión innecesaria sobre el recolector de basura (*Garbage Collector*).

A continuación se detalla el análisis técnico por subsistemas, seguido del catálogo de hallazgos clasificados por severidad y el plan de mitigación recomendado.

---

## 2. Análisis Detallado por Área

### 2.1. HUD e Indicaciones en Pantalla

El HUD del campamento se divide en dos bloques principales:
- **Panel Superior Izquierdo (`y=22` a `y=134`):** Información general del Claro de Ceniza, estado de la antorcha, fragmentos recolectados y pistas acumuladas.
- **Panel Inferior (`y=638` a `y=694`):** Indicaciones contextuales de interacción y mensajes temporales (`self.mensaje`).

#### Defectos Identificados:
1. **Mensaje de Apertura del Umbral Invisible:**
   En `Campamento._interactuar()` (`lab_v2/interfaz/pantallas.py`, línea 505):
   ```python
   if math.hypot(x - 550, y - 294) < 135:
       self.app.sonidos.reproducir("clic")
       self.app.guardar_checkpoint(self.personaje)
       self.abriendo = True
       self.mensaje = "El Umbral se está abriendo..."
       self.mensaje_tiempo = 0
   ```
   En `Campamento.dibujar()` (líneas 860-861):
   ```python
   if self.mensaje_tiempo > 0:
       texto(surf, self.mensaje, 13, APAGADO, (ANCHO // 2, 678), "midtop", sombra=False)
   ```
   Al asignar `self.mensaje_tiempo = 0`, la condición `mensaje_tiempo > 0` se evalúa como `False` inmediatamente en el siguiente cuadro. El jugador nunca llega a leer la confirmación de apertura del portón, lo que genera confusión si el tiempo de animación es largo o si el jugador esperaba una respuesta visual inmediata.
2. **Ausencia de Indicadores Contextuales para Sobrevivientes y Objetos:**
   En `Campamento.dibujar()` (líneas 851-856), la variable `indicacion` solo contempla proximidad al portón (`cerca_porton`) o a Tizón (`cerca_duende`):
   ```python
   indicacion = "E  ·  ABRIR EL UMBRAL" if cerca_porton else \
       "E  ·  TRUEQUE CON TIZÓN" if cerca_duende else \
       "WASD / FLECHAS · MOVER     E · INTERACTUAR     L · ANTORCHA"
   ```
   Cuando el jugador se acerca a Mara, Ivo, Nela, la hamaca, el carro de suministros, la hoguera o el mapa, la barra inferior continúa mostrando la leyenda genérica. No existe retroalimentación visual de que dichos elementos son interactivos hasta que el usuario presiona fortuitamente la tecla `E`.
3. **Riesgo de Desbordamiento de Texto en Diálogos Largos:**
   El mensaje de trueque de Tizón mide 74 caracteres:
   `"Tizón cambia un fragmento por una pista gratis para tu próxima incursión."`
   Este texto se dibuja mediante `texto()` sin limitación de ancho ni ajuste automático de línea (`texto_ajustado`), arriesgando solapamientos o desbordamiento fuera de los márgenes útiles del panel si se altera la fuente o se escala la resolución.
4. **Artefacto de Profundidad en Etiquetas de Sobrevivientes:**
   Las etiquetas (`MARA · CARTÓGRAFA`, `IVO · VIGÍA`, `NELA · CURANDERA`, `TIZÓN · DUENDE`) se añaden a `self._etiquetas` y se renderizan **después** de ejecutar `pixelar_region` y **después** de pintar a todos los personajes. Si el personaje del jugador se posiciona debajo de un sobreviviente (`personaje.y > npc.y`), el texto del NPC se dibuja por encima de la cabeza y torso del jugador, rompiendo la coherencia de oclusión en perspectiva cenital.

---

### 2.2. Interacciones con NPCs y Objetos

El Claro de Ceniza contiene 7 puntos de interés interactivos: el Umbral, Mara, Ivo, Nela, la hamaca, el mapa de expedición, la hoguera, el carro, las lápidas de cementerio, el duende Tizón y dos armaduras mecánicas decorativas.

#### Defectos Identificados:
1. **Bug Crítico en el Autómata de Estados de las Armaduras:**
   En `Campamento.actualizar()` (líneas 578-597):
   ```python
   for armadura in self.armaduras:
       distancia = math.hypot(self.personaje[0] - armadura["x"],
                              self.personaje[1] - armadura["y"])
       if distancia > 112 and armadura["estado"] == "caida":
           armadura["estado"] = "levantando"
           armadura["tiempo"] = 0.0
       elif distancia > 112 and armadura["estado"] == "quieta":
           armadura["activada"] = False
       elif distancia < 62 and not armadura["activada"] and armadura["estado"] == "quieta":
           armadura["estado"] = "cayendo"
           armadura["tiempo"] = 0.0
           armadura["activada"] = True
           ...
       if armadura["estado"] in ("cayendo", "levantando"):
           armadura["tiempo"] += dt
           if armadura["tiempo"] >= 0.35:
               armadura["estado"] = "caida" if armadura["estado"] == "cayendo" else "quieta"
               armadura["tiempo"] = 0.0
   ```
   **Causa Raíz de Inmovilidad:**
   - Cuando la armadura cae y el jugador se distancia a `distancia > 112`, la primera condición `if` cambia el estado a `"levantando"`. Por estructura `if ... elif`, la cláusula `elif distancia > 112 and armadura["estado"] == "quieta"` se ignora.
   - Si durante los 0.35 segundos de reincorporación el jugador reingresa al rango `distancia <= 112`, la armadura alcanza el estado `"quieta"`, pero `armadura["activada"]` permanece en `True`.
   - Como la condición para reactivarse exige `not armadura["activada"]`, la armadura **nunca vuelve a caerse** mientras el jugador permanezca en la zona central. El objeto queda permanently deshabilitado.
2. **Solapamiento y Enmascaramiento de Radios de Interacción:**
   - **Hamaca vs. Lápidas:** La hamaca `(266, 356, radio 120)` y las lápidas `(166, 290, radio 140)` distan entre sí 119.8 px. Dado que la hamaca antecede a las lápidas en la cadena `if-elif`, el sector este del cementerio queda enmascarado por la descripción de la hamaca.
   - **Tizón vs. Armadura Este:** Tizón `(803, 363, radio 85)` y la armadura derecha `(702, 344, radio 78)` distan 102.8 px. En la franja intermedia `(x ≈ 750)`, el diálogo de Tizón absorbe la interacción e impide inspeccionar la armadura.
3. **Transacción Instantánea sin Confirmación con Tizón:**
   Presionar `E`, `Enter` o `Espacio` cerca de Tizón descuenta de inmediato un fragmento de mapa a cambio de una pista:
   ```python
   elif math.hypot(x - self.duende[0], y - self.duende[1]) < 85:
       if self.app.fragmentos_mapa > 0:
           self.app.fragmentos_mapa -= 1
           self.app.pistas_duende += 1
           self.app.guardar_checkpoint(self.personaje)
   ```
   En el juego principal, la tecla `Espacio` se utiliza frecuentemente para saltar obstáculos y trampas de rotor. Un jugador que presione `Espacio` por inercia cerca de Tizón consumirá fragmentos valiosos sin confirmación ni diálogo de consentimiento.

---

### 2.3. Persistencia y Checkpoints

La persistencia del juego se centraliza en `App._archivo_checkpoint()`, `App.guardar_checkpoint()` y `App._cargar_checkpoint()` (`lab_v2/interfaz/app.py`, líneas 81-120).

```json
{
  "x": 550.0,
  "y": 596.0,
  "antorcha": true,
  "fragmentos_mapa": 0,
  "pistas_duende": 0,
  "brillo": 1,
  "efectos": 1
}
```

#### Defectos Identificados:
1. **Escritura Directa No Atómica (Riesgo Crítico de Corrupción):**
   ```python
   archivo.parent.mkdir(parents=True, exist_ok=True)
   archivo.write_text(json.dumps({...}), encoding="utf-8")
   ```
   `write_text()` trunca el archivo a 0 bytes antes de volcar el flujo de caracteres. Si el proceso de Python es cerrado forzosamente, el sistema operativo se suspende o se produce un fallo de energía en ese instante, el archivo queda en blanco o con JSON incompleto.
   Al reiniciar, `_cargar_checkpoint()` ejecuta:
   ```python
   except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
       return None
   ```
   Al recibir `None`, `Menu` desactiva la opción "CONTINUAR" y **borra de facto todo el progreso acumulado del jugador** (fragmentos y pistas conseguidas en incursiones previas).
2. **Falta de Validación de Coordenadas de Reaparición (*Spawn Clamping*):**
   `_cargar_checkpoint()` recupera `(float(datos["x"]), float(datos["y"]))` sin cotejar si la posición se encuentra dentro de los límites transitables actuales del Claro de Ceniza o sobre un objeto colisionable nuevo. Si las colisiones se ajustan entre versiones del juego, un checkpoint previo puede dejar al personaje atrapado permanentemente dentro de un collider o fuera de los límites visibles.
3. **Disparidad de Guardado en Evento `QUIT`:**
   En `App.paso()` (línea 133):
   ```python
   if e.type == pygame.QUIT:
       posicion = getattr(self.pantalla, "personaje", None)
       if posicion is not None:
           self.guardar_checkpoint(posicion)
       self.salir()
   ```
   Si el usuario cierra la ventana mientras está en `AjustesMenu`, `Niveles` o `Creditos`, `getattr(self.pantalla, "personaje", None)` es `None`. Si bien la posición previa quedó en memoria, no se asegura un flush formal antes del apagado.

---

### 2.4. Transición de Pantallas y Ciclo de Vida

El ciclo de cambio de pantalla opera mediante `App.ir_a(pantalla)`, almacenando una instantánea (`self.instantanea = self.lienzo.copy()`) y disolviéndola con una curva *smoothstep* durante 0.35 segundos (`DURACION_TRANSICION = 0.35`).

#### Defectos Identificados:
1. **Asignación Continuada de Superficies en Bucle de Renderizado:**
   En `App._dibujar_transicion()` (líneas 180-184):
   ```python
   oscuro = int(110 * math.sin(math.pi * k))
   if oscuro > 0:
       velo = pygame.Surface((ANCHO, ALTO))
       velo.set_alpha(oscuro)
       self.lienzo.blit(velo, (0, 0))
   ```
   Y en `App.paso()` durante el fade inicial (líneas 149-152):
   ```python
   velo = pygame.Surface((ANCHO, ALTO))
   velo.set_alpha(int(255 * self.fade))
   self.lienzo.blit(velo, (0, 0))
   ```
   En cada fotograma de la transición se asigna dinámicamente en memoria una nueva superficie RGBA de 1100×720 píxeles. Esto supone crear y destruir más de 25 superficies de alta resolución en un lapso de 350 ms, forzando ciclos de recolección de basura (*GC pauses*) que generan micro-tirones (*stuttering*).
2. **Filtrado Prematuro de Eventos en Pantallas Entrantes:**
   En `App.ir_a()`, la pantalla activa se reemplaza instantáneamente en `self.pantalla = pantalla`. Durante los 0.35 s de la transición, la pantalla destino procesa eventos de teclado y mouse en `App.paso()` a pesar de que el usuario aún percibe visualmente la pantalla anterior. Clics accidentales o pulsaciones de teclas pueden disparar botones o acciones antes de que la escena sea visible.

---

### 2.5. Rendimiento Gráfico y Efectos Atmosféricos

El ambiente del campamento combina un fondo procedural en baja resolución (`FondoRefugioPixel`, 550×360), un conjunto de emisores de partículas y atmósfera (`AmbienteRefugio`: humo, chispas, luciérnagas, niebla, viñeta) y un post-procesado con `pixelar_region`.

#### Defectos Identificados:
1. **Cuello de Botella por Doble Escalado Completo en `pixelar_region`:**
   En `Campamento.dibujar()` (línea 838):
   ```python
   pixelar_region(surf, pygame.Rect(0, 0, ANCHO, ALTO), 2)
   ```
   En `arte_pixel.py`:
   ```python
   def pixelar_region(surf, rect, bloque=2):
       ...
       chico = pygame.transform.scale(surf.subsurface(r), (max(1, r.w // bloque), max(1, r.h // bloque)))
       surf.blit(pygame.transform.scale(chico, r.size), r.topleft)
   ```
   Esta rutina toma la superficie entera de 1100×720, ejecuta un *downscale* por software a 550×360 y luego un *upscale* a 1100×720 con blit de retorno a 60 FPS. Al carecer de aceleración de renderizado rápido (advertencia de SDL en logs: `Warning: no fast renderer available`), este proceso consume una porción desproporcionada del presupuesto de tiempo de CPU por fotograma.
2. **Degradación Irreversible del Modo de Rendimiento en `AmbienteRefugio`:**
   En `AmbienteRefugio.actualizar()` (líneas 130-136):
   ```python
   self._dt_suave += (dt - self._dt_suave) * 0.05
   if self.calidad and self._dt_suave > 1 / 28:
       self._tiempo_lento += dt
       if self._tiempo_lento > 2.0:
           self.calidad = 0
   else:
       self._tiempo_lento = max(0.0, self._tiempo_lento - dt)
   ```
   Si el equipo sufre una ralentización puntual superior a 2 segundos (por ejemplo, durante la apertura de otra aplicación en segundo plano o inicialización de SDL), `self.calidad` pasa a `0` (desactivando la niebla y reduciendo luciérnagas). **No existe ningún mecanismo de recuperación**: una vez que `self.calidad` cae a `0`, la condición `if self.calidad ...` jamás vuelve a evaluarse, condenando la sesión a calidad degradada de forma permanente.
3. **Ordenación Redundante en Cada Fotograma de Pinos Estáticos:**
   En `Campamento.dibujar()` (línea 792):
   ```python
   for arbol in sorted(self.arboles, key=lambda a: a[1]):
       self._dibujar_arbol(surf, arbol)
   ```
   Los 52 pinos se generan con posiciones fijas en `__init__`. Ordenar la lista en cada ciclo a 60 FPS representa 3120 llamadas inútiles a `sorted()` por minuto.
4. **Instanciación Repetitiva en `FondoRefugioPixel.dibujar()`:**
   En cada cuadro se ejecutan:
   - `escena = self.base.copy()` (duplicación de superficie de 550×360)
   - `velo = pygame.Surface(self.TAM, pygame.SRCALPHA)` (creación de superficie alfa nueva)
   - `pygame.transform.scale(escena, surf.get_size())` (reescalado a pantalla completa).

---

### 2.6. Audio y Efectos Sonoros

El sistema de sonido sintetiza ondas cuadradas y senoidales en memoria mediante `array("h")` (`efectos.py`). En el campamento se utilizan los efectos `"clic"`, `"guardar"` y `"pared"`.

#### Defectos Identificados:
1. **Campamento Silente Durante el Desplazamiento:**
   A diferencia del laberinto (donde cada paso emite el sonido procedural `"paso"`), en el campamento el movimiento es completamente silencioso. No existe retroalimentación acústica de los pasos sobre la hierba o ceniza.
2. **Inconsistencia de Efecto de Audio en la Apertura del Umbral:**
   Al activar la apertura del gran portón de piedra del Umbral (línea 502), se reproduce el sonido `"clic"`, idéntico al clic de un botón de menú de ajustes, restándole peso dramático a la entrada de la mazmorra.
3. **Falta de Retroalimentación en la Antorcha (`K_l`):**
   Alternar la antorcha con la tecla `L` no produce ningún chasquido, encendido ni sonido de ignición.
4. **Ausencia de Audio de Impacto en Colisiones:**
   Chocar contra los límites del claro, la hoguera o las tiendas de campaña no reproduce el sonido `"pared"`, impidiendo al jugador percibir auditivamente los topes del escenario.

---

### 2.7. Manejo de Excepciones y Casos Borde

1. **Retención de Teclas por Pérdida de Foco (*Sticky Keys*):**
   En `Campamento.evento()`, las teclas de movimiento se incorporan a `self.teclas` al recibir `KEYDOWN` y se eliminan al recibir `KEYUP`. Si el usuario pulsa `W` y ejecuta `Alt+Tab` o hace clic fuera de la ventana, el sistema operativo nunca emite el evento `KEYUP` hacia Pygame. Al recuperar el foco, `K_w` permanece en `self.teclas`, causando que el personaje camine automáticamente y sin freno hacia el norte.
2. **Falta de Manejo del Evento `VIDEORESIZE`:**
   En `app.py`, la ventana se inicializa con `pygame.RESIZABLE`. No obstante, `App.paso()` no captura el evento `pygame.VIDEORESIZE`. En plataformas donde `pygame.SCALED` presenta limitaciones de controlador (como SDL dummy o backends sin aceleración directa), redimensionar manualmente la ventana genera barras negras estáticas sin reajuste del viewport.

---

## 3. Matriz de Hallazgos y Vulnerabilidades

| ID | Área | Descripción del Hallazgo | Archivo Afectado | Severidad | Impacto |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **SEC-01** | Persistencia | Escritura de `checkpoint.json` no atómica (`write_text` directo). | `lab_v2/interfaz/app.py` | **CRÍTICA** | Corrupción total irreversible del punto guardado ante cierre forzado o fallo de energía. |
| **SEC-02** | Controles | Pérdida de foco de ventana (Alt+Tab) retiene teclas en `self.teclas` (*Sticky Keys*). | `lab_v2/interfaz/pantallas.py` | **ALTA** | El personaje se mueve solo de forma descontrolada sin intervención del jugador. |
| **SEC-03** | Lógica / NPCs | Bloqueo permanente de reactivación de las armaduras al levantarse. | `lab_v2/interfaz/pantallas.py` | **ALTA** | Las armaduras caen una sola vez y quedan congeladas de por vida. |
| **SEC-04** | Rendimiento | Doble reescalado completo por software en CPU en `pixelar_region` a 60 FPS. | `lab_v2/interfaz/arte_pixel.py`<br>`lab_v2/interfaz/pantallas.py` | **ALTA** | Caídas severas de tasa de cuadros en hardware moderado o controladores software. |
| **SEC-05** | Persistencia | Falta de validación y acotamiento (*clamp*) en coordenadas cargadas del checkpoint. | `lab_v2/interfaz/app.py` | **ALTA** | Personaje atrapado en colisiones o fuera del mapa tras actualizaciones de colisionadores. |
| **SEC-06** | UI / HUD | Mensaje `"El Umbral se está abriendo..."` nunca se dibuja por `mensaje_tiempo = 0`. | `lab_v2/interfaz/pantallas.py` | **MEDIA** | Falta de retroalimentación crítica al abrir el acceso a los niveles. |
| **SEC-07** | Rendimiento | Asignación y destrucción de superficies RGBA de 1100×720 por cuadro en transiciones. | `lab_v2/interfaz/app.py` | **MEDIA** | *Spikes* del recolector de basura (*GC*) y micro-tirones perceptibles en transiciones. |
| **SEC-08** | Interacción | Enmascaramiento y colisión de radios de interacción (Hamaca vs Lápidas, Hoguera vs Mara). | `lab_v2/interfaz/pantallas.py` | **MEDIA** | Dificultad para interactuar con ciertos elementos situados en zonas de solapamiento. |
| **SEC-09** | Jugabilidad | Trueque accidental e irreversible con Tizón con la tecla Espacio sin confirmación. | `lab_v2/interfaz/pantallas.py` | **MEDIA** | Pérdida accidental de fragmentos de mapa por hábito de salto del laberinto. |
| **SEC-10** | Rendimiento | Imposibilidad de recuperar calidad visual alta en `AmbienteRefugio` tras un bajón temporal. | `lab_v2/interfaz/ambiente.py` | **MEDIA** | Pérdida permanente de niebla y reducción de partículas hasta reiniciar el juego. |
| **SEC-11** | UI / HUD | Ausencia de indicadores contextuales de interacción para sobrevivientes y utilería. | `lab_v2/interfaz/pantallas.py` | **MEDIA** | Jugadores novatos no descubren que Mara, Ivo, Nela o los objetos tienen texto narrativo. |
| **SEC-12** | Rendimiento | Copia de superficie y creación de `Surface` alfa por cuadro en `FondoRefugioPixel`. | `lab_v2/interfaz/arte_pixel.py` | **MEDIA** | Carga redundante de CPU/memoria en el renderizado del fondo. |
| **SEC-13** | UI / HUD | Textos largos de diálogo (`texto()`) sin truncado ni ajuste (`texto_ajustado()`). | `lab_v2/interfaz/pantallas.py` | **BAJA** | Riesgo de desbordamiento de cadenas narrativas en traducciones o cambios de fuente. |
| **SEC-14** | UI / Visual | Superposición de etiquetas de sobrevivientes sobre el personaje del viajero. | `lab_v2/interfaz/pantallas.py` | **BAJA** | Falla de ordenación visual (*Z-order* / *Y-sorting*) en perspectiva cenital. |
| **SEC-15** | Rendimiento | Ordenación `sorted(self.arboles)` en cada fotograma a pesar de ser estáticos. | `lab_v2/interfaz/pantallas.py` | **BAJA** | Desperdicio de ciclos de CPU sin impacto en el resultado visual. |
| **SEC-16** | Audio | Ausencia de sonido de pasos (`"paso"`) al desplazarse por el Claro de Ceniza. | `lab_v2/interfaz/pantallas.py` | **BAJA** | Sensación de desconexión motriz y falta de ambientación acústica. |
| **SEC-17** | Audio | Sonido `"clic"` genérico de botón al accionar el Umbral de piedra. | `lab_v2/interfaz/pantallas.py` | **BAJA** | Menor inmersión y disonancia de efectos de sonido. |
| **SEC-18** | Audio | Ausencia de sonido al accionar la antorcha con `K_l` en el campamento. | `lab_v2/interfaz/pantallas.py` | **BAJA** | Falta de confirmación acústica de cambio de estado. |

---

## 4. Recomendaciones de Mejora y Buenas Prácticas

Para garantizar la estabilidad y calidad de producción del juego en los ciclos posteriores a la intervención de los Agentes 1 y 2, se recomienda adoptar las siguientes medidas:

### 4.1. Robustecimiento de la Persistencia (Mitigación SEC-01 y SEC-05)
Implementar escritura atómica mediante reemplazo de archivo temporal en `guardar_checkpoint()`:
```python
def guardar_checkpoint(self, posicion):
    self.punto_guardado = (float(posicion[0]), float(posicion[1]))
    archivo = self._archivo_checkpoint()
    temp_archivo = archivo.with_suffix(".tmp")
    try:
        archivo.parent.mkdir(parents=True, exist_ok=True)
        datos = json.dumps({
            "x": self.punto_guardado[0],
            "y": self.punto_guardado[1],
            "antorcha": self.antorcha_encendida,
            "fragmentos_mapa": self.fragmentos_mapa,
            "pistas_duende": self.pistas_duende,
            "brillo": self.brillo,
            "efectos": self.efectos
        })
        temp_archivo.write_text(datos, encoding="utf-8")
        temp_archivo.replace(archivo)  # Operación atómica a nivel de sistema operativo
    except OSError:
        self.aviso_guardado = "No se pudo guardar tu punto seguro en esta carpeta."
        self.aviso_tiempo = 7.0
```
Asimismo, en `_cargar_checkpoint()` agregar validación de límites:
```python
x = max(60.0, min(ANCHO - 60.0, float(datos.get("x", 550.0))))
y = max(160.0, min(ALTO - 60.0, float(datos.get("y", 596.0))))
return (x, y)
```

### 4.2. Corrección del Estado de las Armaduras (Mitigación SEC-03)
Asegurar que al completar la transición a `"quieta"`, si el jugador no está en rango crítico (`< 62`), la armadura vuelva a quedar armada:
```python
if armadura["estado"] in ("cayendo", "levantando"):
    armadura["tiempo"] += dt
    if armadura["tiempo"] >= 0.35:
        armadura["estado"] = "caida" if armadura["estado"] == "cayendo" else "quieta"
        armadura["tiempo"] = 0.0
        if armadura["estado"] == "quieta" and distancia >= 62:
            armadura["activada"] = False
```

### 4.3. Prevención de Teclas Pegadas por Pérdida de Foco (Mitigación SEC-02)
En `App.paso()` o en `Campamento.evento()`, escuchar eventos de foco y vaciar el conjunto de teclas activas:
```python
if e.type in (pygame.ACTIVEEVENT, getattr(pygame, "WINDOWFOCUSLOST", 32777)):
    if hasattr(e, "gain") and not e.gain:
        self.teclas.clear()
```

### 4.4. Optimización de Memoria y Reutilización de Superficies (Mitigación SEC-07 y SEC-15)
1. **Preasignación de la capa de velo:** Instanciar en `App.__init__` una única superficie de oscurecimiento:
   ```python
   self._superficie_velo = pygame.Surface((ANCHO, ALTO))
   self._superficie_velo.fill((0, 0, 0))
   ```
   Y reutilizarla en `_dibujar_transicion()` alterando únicamente `set_alpha()`.
2. **Preordenación de árboles:** Ordenar los árboles una única vez en `Campamento.__init__`:
   ```python
   self.arboles.sort(key=lambda a: a[1])
   ```
   Eliminando `sorted()` del método `dibujar()`.

### 4.5. Recuperación Dinámica de FPS en `AmbienteRefugio` (Mitigación SEC-10)
Permitir que la calidad gráfica se restablezca si el framerate vuelve a superar los 45 FPS de forma sostenida:
```python
if self.calidad and self._dt_suave > 1 / 28:
    self._tiempo_lento += dt
    if self._tiempo_lento > 2.0:
        self.calidad = 0
elif not self.calidad and self._dt_suave < 1 / 45:
    self._tiempo_lento -= dt
    if self._tiempo_lento <= -3.0:
        self.calidad = 1
        self._tiempo_lento = 0.0
```

### 4.6. Pulido de Experiencia de Usuario y HUD (Mitigación SEC-06, SEC-08, SEC-11)
- Asignar `self.mensaje_tiempo = 3.0` al abrir el Umbral para permitir la visualización de `"El Umbral se está abriendo..."`.
- Extender la lógica contextual de `indicacion` para detectar proximidad a sobrevivientes (`"E  ·  HABLAR CON MARA"`, etc.).
- Introducir un diálogo o confirmación de 2 pasos antes de que Tizón absorba un fragmento de mapa.

---
*Fin del Informe de Auditoría — Preparado por Agente 3.*