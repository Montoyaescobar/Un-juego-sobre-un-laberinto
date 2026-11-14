# Laberinto – Proyecto final de Estructuras de Datos

**Juego:** Laberinto con interfaz gráfica (Pygame) y versión de consola
**Identidad visual:** aventura retro dark fantasy en pixel art, bosque nocturno, ruinas y luz de antorcha
**Integrantes:** Jorge Mario Montoya, Sebastian Paz Diaz, Alejandro _(falta el apellido de Alejandro; hay que escribirlo también en `INTEGRANTES` de `interfaz/pantallas.py` para los créditos)_
**Lenguaje:** Python 3.10 o superior · **Librería gráfica:** Pygame (solo dibuja; las estructuras son propias)

## Cómo ejecutarlo

Desde la carpeta del proyecto:

    pip install pygame        # una sola vez
    python main.py            # inicio predeterminado: juego gráfico pixel art
    python main_grafico.py    # también abre la interfaz gráfica
    python main_consola.py    # versión de consola (no necesita Pygame)
    python run_tests.py       # correr todas las pruebas (las de la interfaz necesitan Pygame y se omiten solas sin él)

En Visual Studio: Archivo > Abrir > Carpeta, elegir esta carpeta; en "Entornos de Python"
instalar el paquete `pygame`; clic derecho en `main.py` > "Establecer como archivo de
inicio" y F5.

## Cómo se juega

La pantalla inicial muestra un viajero junto a una fogata, ruinas y una fortaleza lejana. Elige
NEW GAME para empezar en el Claro de Ceniza o CONTINUE para volver al último punto seguro del
campamento. Explora el refugio y cruza la puerta gigante para elegir una zona del laberinto.

- En el menú: flechas o W/S = elegir · Enter = confirmar · Esc = salir
- En el campamento: W A S D o flechas = mover · E o Espacio = interactuar · L = antorcha · Esc = menú
- En el laberinto: W A S D o flechas = mover · Espacio = saltar trampas
- F o X = atacar con la espada encantada al esqueleto que tienes delante
- U, Z o Retroceso = deshacer (cuenta como movimiento)
- H = pista: dibuja el camino más corto (cuesta 5 movimientos)
- L = cubrir o descubrir la antorcha: cubierta, el campo de visión se reduce
- Una placa en un ramal lateral activa una trampa; vuelve a la marca del suelo en 2 segundos
- Tras desarmarla puedes explorar ese ramal y recuperar un fragmento de mapa
- Los esqueletos vigilan ramales opcionales; oriéntate hacia uno y pulsa F o X para derribarlo con la espada de fuego verde
- El rotor de cuchillas bloquea una casilla de la ruta principal: espera su brillo verde, pulsa Espacio y avanza
- En el ramal de cuchillas del suelo, espera a que la cadena colgante se aparte, salta y cruza
- Cambia fragmentos con Tizón, el duende, por pistas gratis para futuras incursiones; se guardan entre sesiones
- En algunos ramales, una rueda de hierro baja por un carril largo durante unos 3–4 segundos: sal del carril o busca el refugio marcado
- El rotor está en la ruta principal; la rueda y las cuchillas con cadena están en ramales opcionales
- Esc o P = pausa · M = sonido · F11 = pantalla completa
- La versión de consola mantiene el laberinto original: w/a/s/d, u, h y q

Puntaje al ganar = base del nivel (100 / 200 / 300) + 10 por cada movimiento que sobre.
Menú: Continue, New Game, Settings, Credits y Exit. Settings incluye sonido, antorcha inicial,
controles, mejores puntajes, repetición, brillo del laberinto (normal, alto o muy alto) y efectos visuales (alto o bajo, para equipos lentos). El punto seguro del campamento se guarda entre sesiones.

## Estructuras de datos (hechas desde cero con nodos y punteros)

| Estructura | Archivo | Uso en el juego |
|---|---|---|
| Pila | `estructuras/pila.py` | Backtracking al generar el laberinto (`generador.py`), deshacer movimiento (`jugador.py`) y armar el camino del BFS (`solver.py`) |
| Cola | `estructuras/cola.py` | BFS del camino más corto (`solver.py`): pista, límite de movimientos y ubicación de enemigos. **ECO** (`eco.py`): guarda el recorrido del jugador y lo repite N pasos después. **RADAR** (`radar.py`): BFS desde el punto rojo hasta el jugador; la ruta se guarda en una Cola y se desencola un paso cada N turnos |
| Lista circular | `estructuras/lista_circular.py` | Ruta de patrulla de cada enemigo (`enemigo.py`) |
| Lista doble | `estructuras/lista_doble.py` | Historial y repetición de la partida, adelante y atrás (`historial.py`) |
| Árbol BST | `estructuras/arbol_bst.py` | Mejores puntajes: ranking, buscar, eliminar y recorridos (`puntajes.py`) |

## Interfaz gráfica

- Menú pixel art animado: viajero encapuchado, fogata, luna, ruinas, castillo lejano y opciones
  colgadas de un árbol antiguo. Las llamas, las brasas y la niebla se mueven.
- Tablero de piedra pixelado, viajero con antorcha, espectros, puerta de salida, puente de tablas
  con cuerdas, cuchillas saltables y rueda de hierro en ramales opcionales.
- El viajero tiene fotogramas pixel art para caminar, mirar en cuatro direcciones y saltar;
  la llama y los espectros también se animan.
- Velas animadas iluminan tramos de pared; los esqueletos pueden derrotarse con cortes de espada
  que dejan una estela de fuego verde.
- Trampa giratoria con una ventana de salto señalada en verde y péndulo de cadena que se balancea
  sobre las cuchillas del suelo.
- Campamento explorable con pinos, cementerio, hoguera, hamaca, carro de carga, supervivientes,
  un duende y armaduras que caen cuando el jugador se acerca.
- La antorcha ilumina el camino; cubrirla reduce el campo de visión durante la exploración.
- Filtro CRT sutil, textura pixelada y paleta de azul nocturno, piedra fría y fuego ámbar.
- Cada zona tiene su propio paisaje y color (`interfaz/ambiente_pantallas.py`): bosque de musgo
  (Fácil), cripta helada (Medio) y ruinas de ceniza (Difícil). Se ve detrás del tablero, en las
  tarjetas de niveles, en el encabezado del panel derecho y en la pantalla final.
- Menú con luz de fogata, niebla, humo y luciérnagas; las tablas se corren al elegirlas.
- Las pantallas ya no cambian de golpe: la anterior se disuelve sobre la nueva (`App.ir_a`).
- Pantalla final: rayos de luz al ganar, ceniza al perder y puntaje que sube hasta el total.
- Panel "Estructuras en acción" que muestra en vivo el tamaño de la pila, el BFS, las rutas
  circulares, el historial y el árbol.
- Repetición con línea de tiempo: recorre la lista doble hacia adelante y hacia atrás.
- Ranking con el árbol BST dibujado: se animan inorden, preorden y posorden, y al tocar un nodo
  se ve la búsqueda desde la raíz.
- Los sonidos se generan por código (no hay archivos de audio) y el juego funciona sin audio.
- Si el punto seguro no se puede guardar (carpeta sin permisos), aparece un aviso rojo arriba y el
  juego sigue funcionando.

## Qué es base y qué es extra

- **Base (lo que se califica):** las 5 estructuras de `estructuras/`, el laberinto, el BFS, el jugador
  con deshacer, los espectros con ruta circular, el historial con repetición y el ranking BST. Sus
  reglas viven en `juego/` y tienen pruebas.
- **Reglas del rotor y las cuchillas:** `juego/peligros.py` (funciones puras con pruebas en
  `pruebas/test_peligros.py`). La pantalla solo las llama y dibuja.
- **Extras de la interfaz (no usan las 5 estructuras):** campamento explorable, Tizón y los trueques,
  placa-trampa, rueda de hierro, esqueletos con espada, puente, velas, armaduras y efectos CRT.
  Su lógica está en `interfaz/pantallas.py` (clases `Juego` y `Campamento`) como diccionarios simples.
- El juego **no garantiza** una ruta sin obstáculos: la ruta principal tiene un rotor que exige saltar
  con Espacio cuando las cuchillas brillan en verde. Los demás peligros están en ramales opcionales.

## Organización del código

- `estructuras/` – las 5 estructuras, los nodos y los errores propios
- `juego/` – `laberinto`, `generador`, `solver` (BFS), `jugador`, `enemigo`, `peligros`, `eco`, `radar`, `historial`, `puntajes` y `partida` (junta todo)
- `interfaz/` – interfaz gráfica: `app`, `pantallas`, `render`, `arte_pixel`, `efectos`, `ambiente`, `ambiente_laberinto`, `widgets`, `tema`
- `pruebas/` – pruebas unitarias de cada estructura, del juego y de la interfaz
- `main.py` – arranca el juego gráfico por defecto
- `main_grafico.py` – entrada explícita para la interfaz gráfica
- `main_consola.py` – menús y partida en consola
- `puntajes.txt` – se crea solo al guardar el primer puntaje


## El ECO (mecánica con Cola)

Un fantasma translúcido azul repite tu recorrido unos pasos después (8 en Fácil, 6 en Medio, 5 en Difícil).

- Cada vez que te mueves o deshaces, tu casilla se **encola**. Cuando hay más casillas
  pendientes que el retraso, el eco **desencola** la del frente y se coloca ahí. Por ser FIFO,
  camina exactamente por donde tú caminaste.
- Si **esperas** (tecla `Q` en la interfaz, `e` en consola; cuesta 1 movimiento), no se encola nada pero el
  eco desencola una casilla: se acerca un paso. Si se vacía la cola, está encima de ti.
- Si el eco y tú quedan en la misma casilla (o se cruzan en un pasillo), pierdes.
- Mientras no te detengas, nunca te alcanza, y como solo pisa casillas ya recorridas nunca
  bloquea el camino que falta. Está en `juego/eco.py`; pruebas en `pruebas/test_eco.py`.
- Además, `pruebas/test_aleatorio.py` machaca todas las pantallas con teclas y clics al azar para
  comprobar que nada cierra el juego.

## El RADAR (segunda mecánica con Cola)

Un punto rojo aparece en una casilla lejana de la entrada y fuera del camino más corto. Empieza
dormido (6 turnos) y luego te persigue por el camino más corto, más despacio que tú: un paso cada
4 acciones en Fácil, cada 3 en Medio y cada 2 en Difícil.

- Cada vez que le toca moverse, calcula con **BFS** (`solver.camino_mas_corto`, que usa una Cola) la
  ruta hasta ti, la **encola** casilla por casilla y **desencola** un paso. Está en `juego/radar.py`.
- Si te toca **no pierdes la partida**: se descuentan 5 movimientos y el punto vuelve a su origen y
  se duerme otros 6 turnos. Castiga quedarse quieto, deshacer o dar vueltas.
- Como aparece lejos, a veces se cruza contigo de frente; aun así los niveles tienen margen y las
  pruebas comprueban que el camino más corto siempre se puede completar.
- En consola se dibuja como `R`. Pruebas en `pruebas/test_radar.py` (18).

## Ambiente del campamento (solo visual)

`interfaz/ambiente.py` agrega al refugio humo y chispas que suben de la fogata, luz cálida que
parpadea, luciérnagas, niebla baja, pinos que se mecen con el viento, sobrevivientes que miran al
viajero y una viñeta en los bordes. Solo dibuja: no usa las estructuras ni cambia reglas. Si el
computador va lento, el ambiente se reduce solo (sin niebla y con menos partículas).
Pruebas en `pruebas/test_ambiente.py` (necesitan Pygame).

## Ambiente del laberinto (solo visual)

Cada nivel tiene sus colores (`PALETAS_NIVEL` en `interfaz/tema.py`): bosque con musgo en Fácil,
cripta azulada en Medio y ceniza rojiza en Difícil. Las paredes tienen cara superior, cara de enfrente
con ladrillos y sombra sobre el suelo; el suelo tiene baldosas, musgo, grietas y charcos
(`tablero_estatico` en `interfaz/render.py`). `interfaz/ambiente_laberinto.py` agrega antorchas que
parpadean e iluminan lo cercano, brasas, polvo y niebla baja. En Ajustes, "Efectos visuales: BAJO"
quita niebla, polvo y brasas; si el equipo va lento, se reduce solo. Los carteles de ayuda
("GIRO VERDE · ESPACIO + PASO", etc.) se dibujan al final y quedan siempre dentro del tablero.
Pruebas en `pruebas/test_ambiente_laberinto.py` (necesitan Pygame).

## Ambiente del laberinto (solo visual)

Cada nivel tiene sus colores (`PALETAS_NIVEL` en `interfaz/tema.py`): bosque con musgo en Fácil,
cripta azulada en Medio y ceniza rojiza en Difícil. Las paredes tienen cara superior, cara de enfrente
con ladrillos y sombra sobre el suelo; el suelo tiene baldosas, musgo, grietas y charcos
(`tablero_estatico` en `interfaz/render.py`). `interfaz/ambiente_laberinto.py` agrega antorchas que
parpadean e iluminan lo cercano, brasas, polvo y niebla baja. En Ajustes, "Efectos visuales: BAJO"
quita niebla, polvo y brasas; si el equipo va lento, se reduce solo. Los carteles de ayuda
("GIRO VERDE · ESPACIO + PASO", etc.) se dibujan al final y quedan siempre dentro del tablero.
Pruebas en `pruebas/test_ambiente_laberinto.py` (necesitan Pygame).
