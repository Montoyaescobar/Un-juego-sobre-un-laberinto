# Plan de Tareas: Corrección del Movimiento y Campamento

Este documento define la arquitectura y asignación de tareas para resolver el bug crítico de atasco y restricción de movimiento del personaje en la zona del **Campamento (Claro de Ceniza)** del juego.

---

## 1. Diagnóstico Técnico del Bug

Tras analizar el código fuente en `lab_v2/interfaz/pantallas.py`, se identificaron dos causas raíces complementarias que provocan que el personaje se quede trabado "en la nada":

1. **Colisiones y Límites Desalineados / Fantasmas (Problema de Entorno):**
   * **Muro invisible superior:** La condición `26 <= nx <= ANCHO - 26 and 244 <= ny <= ALTO - 28` en `actualizar()` establece una barrera horizontal invisible en `y = 244`. El claro visual dibujado con `ellipse` comienza en `y = 138`, por lo que el jugador se bloquea en mitad del claro abierto sin razón visual.
   * **Hitbox gigante de la hoguera:** La fogata visual tiene su centro en `(550, 478)` con un radio de aproximadamente 30-40 px, pero la caja de colisión `pygame.Rect(454, 432, 192, 97)` bloquea un rectángulo de 192x97 px, dejando enormes áreas vacías a los costados donde el personaje choca contra el aire.
   * **Hitbox excesivo del portón:** `self.porton.inflate(22, 18)` proyecta la colisión demasiado hacia abajo, dificultando el acercamiento natural al Umbral.
   * **Cajas de colisión de carpas, hamaca y carro:** Cajas rígidas que no se ajustan a los polígonos dibujados.

2. **Físicas y Actualización de Posición Defectuosas (Problema de Controlador):**
   * **Sobrescritura destructiva en movimiento diagonal:**
     ```python
     for nx, ny in ((self.personaje[0] + paso_x, self.personaje[1]),
                    (self.personaje[0], self.personaje[1] + paso_y)):
         caja = pygame.Rect(int(nx - 9), int(ny - 8), 18, 16)
         if ... and not any(caja.colliderect(r) for r in self.bloqueos):
             self.personaje[:] = [nx, ny]
     ```
     La tupla precalcula `(self.personaje[0], self.personaje[1] + paso_y)` con el valor inicial de X. En la primera iteración (eje X), `self.personaje` se actualiza con `nx = x + paso_x`. En la segunda iteración (eje Y), al cumplirse la condición, `self.personaje[:] = [nx, ny]` reemplaza el vector completo reescribiendo la posición X con el valor viejo anterior al movimiento. ¡El avance horizontal se anula por completo en cualquier movimiento diagonal!
   * **Falta de deslizamiento contra obstáculos (*Wall Sliding*):** Si hay un obstáculo en una esquina o diagonal, el personaje se frena en seco en lugar de continuar deslizándose por el eje libre.
   * **Gestión de teclas frágil:** `self.teclas` almacena eventos sueltos de `KEYDOWN`/`KEYUP`. Si la ventana pierde el foco o se acumula repetición de eventos, las teclas quedan pegadas o el personaje se congela.

---

## 2. Matriz Estricta de Asignación de Archivos (Zero-Conflict)

Para permitir que los 3 agentes trabajen **en paralelo sin riesgo de conflictos de git o sobrescrituras**, se establece una separación estricta y disjunta de archivos:

$$\text{Archivos}(\text{Agente 1}) \cap \text{Archivos}(\text{Agente 2}) = \emptyset$$

| Agente | Rol | Archivos Permitidos (Escritura / Modificación) | Archivos Prohibidos |
| :--- | :--- | :--- | :--- |
| **Agente 1** | Entorno, Mapas y Colisiones | • `lab_v2/interfaz/colisiones_campamento.py` *(nuevo)*<br>• `lab_v2/interfaz/ambiente.py`<br>• `lab_v2/interfaz/arte_pixel.py`<br>• `lab_v2/pruebas/test_colisiones_campamento.py` *(nuevo)* | **PROHIBIDO tocar:**<br>• `lab_v2/interfaz/pantallas.py`<br>• `lab_v2/interfaz/controlador_campamento.py`<br>• Cualquier archivo de `juego/` |
| **Agente 2** | Movimiento y Controlador | • `lab_v2/interfaz/controlador_campamento.py` *(nuevo)*<br>• `lab_v2/interfaz/pantallas.py`<br>• `lab_v2/pruebas/test_controlador_campamento.py` *(nuevo)* | **PROHIBIDO tocar:**<br>• `lab_v2/interfaz/colisiones_campamento.py`<br>• `lab_v2/interfaz/ambiente.py`<br>• `lab_v2/interfaz/arte_pixel.py`<br>• Cualquier archivo de `juego/` |
| **Agente 3** | Auditoría General (Solo Lectura) | • `AUDIT_CAMPAMENTO.md` *(nuevo, único archivo permitido)* | **MODO SOLO LECTURA:**<br>Prohibido modificar cualquier archivo existente del código fuente del juego. |

---

## 3. Contrato de Interfaz entre Agente 1 y Agente 2

Para garantizar la interoperabilidad sin acoplamiento directo durante el desarrollo en paralelo, se define el siguiente contrato que ambos agentes deben respetar:

### Módulo: `lab_v2/interfaz/colisiones_campamento.py` (Creado por Agente 1)
```python
import pygame

def obtener_limites_campamento() -> tuple[int, int, int, int]:
    """
    Devuelve los límites transitables del claro del campamento:
    (min_x, min_y, max_x, max_y)
    Elimina la barrera artificial en y=244 para permitir transitar
    la zona norte natural del claro (ej. min_y ≈ 140-150).
    """
    ...

def obtener_bloqueos_campamento(porton_rect: pygame.Rect = None) -> list[pygame.Rect]:
    """
    Devuelve la lista de cajas de colisión (pygame.Rect) ajustadas
    con precisión a los objetos visibles (hoguera reducida, carpas,
    hamaca, carro, portón y NPCs), sin colisionadores fantasma.
    """
    ...

def es_posicion_valida(caja: pygame.Rect, bloqueos: list[pygame.Rect], limites: tuple[int, int, int, int]) -> bool:
    """
    Verifica si una caja colisiona con algún bloqueo o sale de los límites.
    """
    ...
```

### Integración en `pantallas.py` y `controlador_campamento.py` (Implementado por Agente 2)
El Agente 2 importará y utilizará estas funciones con manejo defensivo para pruebas unitarias desacopladas:
```python
try:
    from interfaz.colisiones_campamento import (
        obtener_bloqueos_campamento,
        obtener_limites_campamento,
        es_posicion_valida
    )
except ImportError:
    # Fallback defensivo mientras Agente 1 finaliza su módulo
    ...
```

---

## 4. Tareas Específicas y Prompts de Inicio

---

### AGENTE 1: Entorno, Mapas y Colisiones del Campamento

* **Objetivo:**
  Crear el módulo especializado de colisiones del campamento `colisiones_campamento.py`, recalibrando todos los obstáculos (`bloqueos`) y límites del escenario para que coincidan con la estética visual del Claro de Ceniza, eliminando obstáculos invisibles, sobredimensionados o desalineados.
* **Archivos Asignados (Exclusivos):**
  1. `lab_v2/interfaz/colisiones_campamento.py` *(creación)*
  2. `lab_v2/interfaz/ambiente.py` *(revisión/ajuste de hoguera y niebla si aplica)*
  3. `lab_v2/interfaz/arte_pixel.py` *(coordinación de proporciones de fondo)*
  4. `lab_v2/pruebas/test_colisiones_campamento.py` *(creación de pruebas unitarias)*
* **Restricción Estricta:**
  NO modifiques bajo ninguna circunstancia `lab_v2/interfaz/pantallas.py` ni `lab_v2/interfaz/controlador_campamento.py`.
* **Criterios de Aceptación:**
  - La caja de la hoguera en `(550, 478)` ya no bloquea 192x97 px de espacio vacío a los costados; se ajusta al fuego real (radio ≈ 30-40 px).
  - El límite superior transitable ya no está clavado en `y = 244`, permitiendo caminar naturalmente hacia la parte superior del claro (respetando los pinos y la cerca).
  - El portón del Umbral permite acercarse a interactuar sin rebotar prematuramente.
  - Carpas, mesas, carro y hamaca tienen colisionadores proporcionales a su dibujo.
  - El archivo `lab_v2/pruebas/test_colisiones_campamento.py` valida todas las hitboxes y límites sin errores.

#### Prompt para Agente 1 (Copiar y pegar):
```text
Hola Agente 1. Eres el especialista en Entorno, Mapas y Colisiones del Campamento.
Tu misión exclusiva es corregir el bug donde el personaje se atasca en la nada en el campamento debido a colisionadores invisibles y límites del mapa desalineados.

TUS ARCHIVOS PERMITIDOS (EXCLUSIVOS):
- lab_v2/interfaz/colisiones_campamento.py (crear este módulo)
- lab_v2/interfaz/ambiente.py
- lab_v2/interfaz/arte_pixel.py
- lab_v2/pruebas/test_colisiones_campamento.py (crear pruebas de colisión)

REGLAS ESTRICTAS DE CONFLICTO:
- NO modifiques lab_v2/interfaz/pantallas.py (ese archivo es propiedad exclusiva del Agente 2).
- NO modifiques ningún archivo de lógica de juego (juego/).

TAREAS:
1. Crea lab_v2/interfaz/colisiones_campamento.py implementando:
   - obtener_limites_campamento() -> tuple[int, int, int, int]: Ajusta los límites reales transitables del Claro de Ceniza (amplía el límite norte que estaba artificialmente bloqueado en y=244 para que el jugador pueda recorrer la zona superior cerca del portón).
   - obtener_bloqueos_campamento(porton_rect=None) -> list[pygame.Rect]: Corrige las cajas de colisión. Especialmente:
     * Reduce la caja gigante de la hoguera (que medía 192x97 px para un fuego circular pequeño en (550, 478)) a una dimensión precisa y transitable por los costados.
     * Ajusta el portón del Umbral para que el personaje pueda acercarse a la puerta a interactuar sin chocar a 100px de distancia.
     * Calibra las cajas de colisión de las tiendas de campaña, la hamaca, el carro y los NPCs (Mara, Ivo, Nela y Tizón).
   - es_posicion_valida(caja, bloqueos, limites) -> bool: Función utilitaria para evaluar colisiones.
2. Revisa ambiente.py y arte_pixel.py para asegurar que la posición visual de los emisores (humo, fuego) y fondos coincidan con los nuevos límites y colisionadores.
3. Crea lab_v2/pruebas/test_colisiones_campamento.py con tests exhaustivos en unittest que verifiquen que:
   - Los límites amplían la libertad de movimiento.
   - Ningún collider sobredimensionado bloquea caminos obvios.
   - Las funciones devuelven objetos pygame.Rect válidos y consistentes.
4. Ejecuta las pruebas y confirma que pasen al 100%.
```

---

### AGENTE 2: Movimiento y Controlador del Jugador

* **Objetivo:**
  Crear el controlador de movimiento y físicas fluidas del personaje en el campamento (`controlador_campamento.py`) e integrarlo en `pantallas.py`. Resolver el error crítico de movimiento diagonal (sobreescritura del vector X), agregar deslizamiento contra muros (*wall sliding*) y mejorar la captura reactiva de teclas.
* **Archivos Asignados (Exclusivos):**
  1. `lab_v2/interfaz/controlador_campamento.py` *(creación)*
  2. `lab_v2/interfaz/pantallas.py` *(modificación exclusiva de la clase Campamento para integrar el nuevo controlador)*
  3. `lab_v2/pruebas/test_controlador_campamento.py` *(creación de pruebas unitarias)*
* **Restricción Estricta:**
  NO modifiques bajo ninguna circunstancia `lab_v2/interfaz/colisiones_campamento.py`, `lab_v2/interfaz/ambiente.py` ni `lab_v2/interfaz/arte_pixel.py`.
* **Criterios de Aceptación:**
  - El movimiento diagonal (WASD y flechas) funciona a velocidad normalizada constante sin que el avance horizontal se borre.
  - El personaje se desliza suavemente sobre obstáculos y paredes (*wall sliding* independiente en X e Y): si choca horizontalmente, sigue avanzando verticalmente y viceversa.
  - La captura de teclas responde de forma inmediata y no sufre de teclas atascadas o canceladas erróneamente.
  - Se integra de forma limpia en `Campamento.evento` y `Campamento.actualizar` en `pantallas.py`, utilizando el contrato con `interfaz.colisiones_campamento` (con fallback de seguridad).
  - El archivo `lab_v2/pruebas/test_controlador_campamento.py` y las pruebas preexistentes en `lab_v2/run_tests.py` pasan exitosamente.

#### Prompt para Agente 2 (Copiar y pegar):
```text
Hola Agente 2. Eres el especialista en Movimiento y Controlador del Jugador en el Campamento.
Tu misión exclusiva es corregir la física y la lógica de movimiento del personaje en el campamento para que el desplazamiento sea fluido, responsivo y sin bloqueos extraños.

TUS ARCHIVOS PERMITIDOS (EXCLUSIVOS):
- lab_v2/interfaz/controlador_campamento.py (crear este módulo)
- lab_v2/interfaz/pantallas.py (editar exclusivamente la clase Campamento para integrar el controlador)
- lab_v2/pruebas/test_controlador_campamento.py (crear pruebas del controlador)

REGLAS ESTRICTAS DE CONFLICTO:
- NO modifiques lab_v2/interfaz/colisiones_campamento.py, ambiente.py ni arte_pixel.py (propiedad exclusiva del Agente 1).
- Importa las colisiones desde `interfaz.colisiones_campamento` usando el contrato:
  obtener_bloqueos_campamento(porton_rect) y obtener_limites_campamento(), con fallback defensivo por si el archivo está siendo creado en paralelo.

TAREAS:
1. Crea lab_v2/interfaz/controlador_campamento.py:
   - Implementa una clase ControladorCampamento que gestione:
     * Detección de teclas (WASD / flechas) de forma sólida, sin atascamientos de eventos.
     * Normalización de vector (evitar que en diagonal se mueva a mayor velocidad o se distorsione).
     * Físicas con deslizamiento en paredes (Wall Sliding): evalúa paso_x y paso_y por separado; si un eje colisiona pero el otro está libre, el personaje debe continuar avanzando suavemente en el eje libre.
     * Hitbox del personaje: caja de tamaño apropiado con redondeo subpíxel suave.
     * Retorno de posición actualizada, dirección cardinal ("arriba", "abajo", "izquierda", "derecha") y estado andante (bool).
2. Modifica la clase Campamento en lab_v2/interfaz/pantallas.py:
   - Reemplaza el bucle for nx, ny in ((self.personaje[0] + paso_x, ...), ...) que causaba el bug de sobreescritura diagonal.
   - Instancia y delega el movimiento y la gestión de entrada en ControladorCampamento.
   - Reemplaza self.bloqueos fijos por la llamada a obtener_bloqueos_campamento(self.porton) y los límites por obtener_limites_campamento().
3. Crea lab_v2/pruebas/test_controlador_campamento.py:
   - Verifica que el movimiento diagonal actualice tanto X como Y simultáneamente.
   - Verifica el deslizamiento en muros ante colisión en un solo eje.
   - Verifica que la velocidad se mantenga uniforme en todas las direcciones.
4. Ejecuta las pruebas con python lab_v2/run_tests.py y asegura que todas pasen.
```

---

### AGENTE 3: Auditoría General del Campamento (Solo Lectura)

* **Objetivo:**
  Auditar de forma integral todos los componentes del Campamento (interfaz, cámara, HUD, diálogos, sonidos, transiciones entre pantallas y persistencia) para detectar cualquier otro defecto de lógica, inconsistencia gráfica o fuga de rendimiento.
* **Archivos Asignados (Exclusivos):**
  1. `AUDIT_CAMPAMENTO.md` *(creación; único archivo que tiene permitido escribir)*
* **Restricción Estricta:**
  MODO SOLO LECTURA. No modifiques ningún archivo de código (`.py`) existente en el repositorio.
* **Áreas Obligatorias de Auditoría:**
  1. **HUD e Interacción:** Visualización de mensajes temporales (`self.mensaje_tiempo`), formato de textos y etiquetas de sobrevivientes (Mara, Ivo, Nela, Tizón).
  2. **Ciclo de Guardado:** Persistencia del checkpoint (`checkpoint.json`), actualización de coordenadas, fragmentos y pistas en `App`.
  3. **Transiciones de Pantalla:** Flujo de entrada/salida entre `Menu`, `Campamento`, `Niveles`, `Juego`, `Victoria` y `Derrota`.
  4. **Efectos y Audio:** Reproducción de sonidos ("clic", "guardar", "pared"), comportamiento con modo efectos BAJO/ALTO en `AmbienteRefugio`.
  5. **Manejo de Excepciones y Casos Borde:** Redimensionado de ventana (`RESIZABLE`), teclas rápidas (`Esc`, `L`, `E`) y pérdida de foco.

#### Prompt para Agente 3 (Copiar y pegar):
```text
Hola Agente 3. Eres el Auditor de Calidad y Estabilidad del Campamento.
Tu misión es realizar una auditoría exhaustiva de solo lectura sobre todos los módulos del campamento en el juego para detectar bugs secundarios, problemas de rendimiento o inconsistencias de interfaz.

REGLA ESTRICTA DE SOLO LECTURA:
- NO modifiques ningún archivo de código fuente (.py) existente.
- Toda tu salida, análisis y recomendaciones deben quedar registrados exclusivamente en un archivo nuevo en la raíz del proyecto llamado: AUDIT_CAMPAMENTO.md.

MÓDULOS A REVISAR:
- lab_v2/interfaz/pantallas.py (secciones Campamento, Menu, Niveles)
- lab_v2/interfaz/app.py (guardado de checkpoint, transiciones, aviso_guardado)
- lab_v2/interfaz/ambiente.py (humo, luciérnagas, niebla, viñeta, ajuste de FPS)
- lab_v2/interfaz/arte_pixel.py (FondoRefugioPixel, pixelar_region)
- lab_v2/interfaz/efectos.py (reproducción de audio y partículas)
- lab_v2/interfaz/tema.py (colores, fuentes, dibujo de personajes)

ESTRUCTURA DE AUDIT_CAMPAMENTO.md:
1. Resumen Ejecutivo del Estado del Campamento.
2. Análisis Detallado por Área:
   - HUD e Indicaciones en Pantalla.
   - Interacciones con NPCs y Objetos (Tizón, Mara, Ivo, Nela, Umbral, armaduras).
   - Persistencia y Checkpoints (coordenadas, fragmentos, pistas, permisos de disco).
   - Transición de Pantallas y Ciclo de Vida (manejo de memoria, superficies).
   - Rendimiento Gráfico y Efectos Atmosféricos (calidad alta vs baja).
   - Audio y Efectos Sonoros.
3. Tabla de Hallazgos y Vulnerabilidades (clasificadas por Severidad: Crítica, Alta, Media, Baja).
4. Recomendaciones de Mejora y Buenas Prácticas para el equipo.
```

---

## 5. Verificación Final e Integración

Una vez que los tres agentes concluyan sus tareas en paralelo, el ciclo de integración se valida ejecutando la suite completa de pruebas:

```powershell
python lab_v2\run_tests.py
```

Y verificando manualmente la jugabilidad en el campamento:
```powershell
python lab_v2\main.py
```
*(Caminar con WASD en todas las direcciones, probar diagonales junto a la fogata, rodear las tiendas y aproximarse al Umbral sin atascos).*
