"""
partida.py
Una partida completa: junta el laberinto, el jugador, los enemigos y el historial.

Es el "director" del juego: la consola (main.py) y, más adelante, la interfaz gráfica
solo le piden cosas (mover, deshacer, pista) y dibujan lo que la partida les dice.

Dónde se usa cada estructura:
    Pila           -> generar el laberinto (generador.py), deshacer movimiento (jugador.py)
                      y reconstruir el camino del BFS (solver.py)
    Cola           -> BFS del camino más corto (solver.py): pista, límite de movimientos
                      y ubicación de enemigos
    Lista circular -> ruta de patrulla de cada enemigo (enemigo.py)
    Cola           -> (también) el ECO: repite el recorrido del jugador N pasos después (eco.py)
    Cola           -> (también) el RADAR: punto rojo que persigue por el camino más corto (radar.py)
    Lista doble    -> historial / repetición de la partida (historial.py)
    Árbol BST      -> mejores puntajes (puntajes.py)

Turnos: cada vez que el jugador se mueve o deshace, cada enemigo da un paso.
Se gana llegando a la salida; se pierde si se acaban los movimientos o un enemigo te alcanza.
Las rutas de los enemigos nunca tocan el camino más corto a la salida, así que siempre
existe una forma de ganar sin cruzarse con ellos.
"""

import random

from juego.generador import generar_laberinto
from juego.jugador import Jugador
from juego.solver import camino_mas_corto
from juego.enemigo import Enemigo, crear_ruta_patrulla
from juego.eco import Eco
from juego.radar import Radar, casilla_lejana, PENALIZACION_RADAR
from juego.historial import Historial

JUGANDO = "jugando"
GANO = "gano"
SIN_MOVIMIENTOS = "sin_movimientos"
ATRAPADO = "atrapado"

NIVELES = {
    "1": {"nombre": "Fácil", "filas": 8, "columnas": 8, "factor": 3.0, "enemigos": 1, "base": 100, "eco": 8, "radar": 4},
    "2": {"nombre": "Medio", "filas": 12, "columnas": 12, "factor": 2.5, "enemigos": 2, "base": 200, "eco": 6, "radar": 3},
    "3": {"nombre": "Difícil", "filas": 16, "columnas": 16, "factor": 2.0, "enemigos": 3, "base": 300, "eco": 5, "radar": 2},
}

PUNTOS_POR_MOVIMIENTO_SOBRANTE = 10
DISTANCIA_MINIMA_ENTRADA = 6       # los enemigos no patrullan pegados a la entrada


class Partida:
    """Estado completo de una partida de laberinto."""

    def __init__(self, nivel, semilla=None):
        """
        Crea la partida: genera el laberinto, calcula el límite de movimientos con BFS,
        pone a los enemigos y guarda la primera foto del historial.

        Recibe:
            nivel: diccionario de NIVELES (nombre, filas, columnas, factor, enemigos, base).
            semilla: número opcional para que salga siempre la misma partida (pruebas).
        Devuelve:
            Nada (constructor).
        """
        self.nivel = nivel
        self._azar = random.Random(semilla)
        self.laberinto = generar_laberinto(nivel["filas"], nivel["columnas"],
                                           self._azar.randrange(1000000000))
        self.solucion = camino_mas_corto(self.laberinto, self.laberinto.entrada,
                                         self.laberinto.salida)
        pasos_optimos = len(self.solucion) - 1
        self.jugador = Jugador(self.laberinto, int(pasos_optimos * nivel["factor"]) + 10)
        self.enemigos = self._crear_enemigos(nivel["enemigos"])
        retraso_eco = nivel.get("eco", 0)           # 0 = sin eco (las pruebas lo apagan)
        self.eco = Eco(retraso_eco, self.laberinto.entrada) if retraso_eco else None
        cada_radar = nivel.get("radar", 0)          # 0 = sin radar (las pruebas lo apagan)
        if cada_radar:
            origen_radar = casilla_lejana(self.laberinto, self.laberinto.entrada,
                                          set(self.solucion))
            self.radar = Radar(self.laberinto, origen_radar, cada_radar)
        else:
            self.radar = None
        self.causa = ""                              # "enemigo" o "eco" si te atrapan
        self.historial = Historial()
        self.estado = JUGANDO
        self.pista_actual = None
        self._registrar()

    # ---------------- acciones del jugador ----------------
    def mover(self, direccion):
        """
        Mueve al jugador y luego a los enemigos.

        Recibe:
            direccion: "arriba", "abajo", "izquierda" o "derecha".
        Devuelve:
            True si el jugador se movió; False si había pared o la partida ya terminó.
        """
        if self.estado != JUGANDO:
            return False
        anterior = self.jugador.posicion
        if not self.jugador.mover(direccion):
            return False
        self._despues_de_accion(anterior)
        return True

    def deshacer(self):
        """
        Deshace el último movimiento del jugador (Pila) y mueve a los enemigos.

        Recibe: nada.
        Devuelve:
            True si se pudo deshacer; False si no había nada que deshacer.
        """
        if self.estado != JUGANDO:
            return False
        anterior = self.jugador.posicion
        if not self.jugador.deshacer():
            return False
        self._despues_de_accion(anterior)
        return True

    def esperar(self):
        """
        Pasa un turno sin moverse (cuesta 1 movimiento). Los enemigos avanzan y el eco se
        acerca un paso (desencola una casilla pendiente sin que se encole otra).

        Recibe: nada.
        Devuelve:
            True si se pasó el turno; False si la partida ya terminó.
        """
        if self.estado != JUGANDO:
            return False
        anterior = self.jugador.posicion
        if not self.jugador.esperar():
            return False
        self._despues_de_accion(anterior, esperando=True)
        return True

    def pista(self):
        """
        Pide la pista (camino más corto a la salida por BFS). Cuesta movimientos y los
        enemigos no se mueven.

        Recibe: nada.
        Devuelve:
            True si hay pista (queda guardada en pista_actual); False si no se pudo dar.
        """
        if self.estado != JUGANDO:
            return False
        camino = self.jugador.pedir_pista()
        if camino is None:
            return False
        self.pista_actual = camino
        return True

    # ---------------- consulta ----------------
    def puntaje(self):
        """
        Puntaje de la partida: base del nivel + 10 por cada movimiento que sobró.
        Solo cuenta si se ganó.

        Recibe: nada.
        Devuelve:
            Un entero (0 si no se ha ganado).
        """
        if self.estado != GANO:
            return 0
        return (self.nivel["base"]
                + self.jugador.movimientos_restantes() * PUNTOS_POR_MOVIMIENTO_SOBRANTE)

    def posiciones_enemigos(self):
        """
        Posiciones actuales de los enemigos.

        Recibe: nada.
        Devuelve:
            Una tupla de tuplas (fila, columna).
        """
        return tuple(e.posicion for e in self.enemigos)

    def dibujar(self):
        """
        Dibuja el estado actual como texto.

        Recibe: nada.
        Devuelve:
            Un string con el laberinto, el jugador, los enemigos y la pista si la hay.
        """
        return self.laberinto.como_texto(self.jugador.posicion, self.posiciones_enemigos(),
                                         self.pista_actual, self.posicion_eco(),
                                         self.posicion_radar())

    # ---------------- internos ----------------
    def _chocan(self):
        """(Interno) True si algún enemigo está en la misma casilla que el jugador."""
        for enemigo in self.enemigos:
            if enemigo.posicion == self.jugador.posicion:
                return True
        return False

    def _despues_de_accion(self, anterior, esperando=False):
        """
        (Interno) Se llama después de cada movimiento o deshacer del jugador:
        revisa si ganó, si caminó hacia un enemigo, mueve a los enemigos, vuelve a revisar
        el choque, mueve al eco (Cola) y revisa si lo atrapó, revisa los movimientos y
        guarda la foto en el historial.

        Recibe:
            anterior: casilla donde estaba el jugador antes de su acción.
            esperando: True si el jugador pasó el turno sin moverse.
        """
        self.pista_actual = None
        if self.jugador.gano():
            self.estado = GANO
        elif self._chocan():                 # el jugador caminó hacia un enemigo
            self.estado = ATRAPADO
            self.causa = "enemigo"
        else:
            for enemigo in self.enemigos:
                enemigo.avanzar()
            if self._chocan():               # un enemigo caminó hacia el jugador
                self.estado = ATRAPADO
                self.causa = "enemigo"
            elif self._eco_atrapa(anterior, esperando):
                self.estado = ATRAPADO
                self.causa = "eco"
            else:
                self._radar_turno()
                if self.jugador.perdio():
                    self.estado = SIN_MOVIMIENTOS
        self._registrar()

    def _radar_turno(self):
        """
        (Interno) Mueve al radar un turno (Cola + BFS). Si toca al jugador, este pierde
        PENALIZACION_RADAR movimientos y el radar vuelve a su origen. No termina la partida.

        Recibe: nada.
        Devuelve: nada.
        """
        if self.radar is None:
            return
        self.radar.turno(self.jugador.posicion)
        if self.radar.toca(self.jugador.posicion):
            self.jugador.penalizar(PENALIZACION_RADAR)
            self.radar.reiniciar()

    def posicion_radar(self):
        """
        Casilla del radar para dibujarlo.

        Recibe: nada.
        Devuelve:
            La tupla (fila, columna), o None si no hay radar o todavía está dormido.
        """
        if self.radar is None or not self.radar.activo:
            return None
        return self.radar.posicion

    def _eco_atrapa(self, anterior, esperando):
        """
        (Interno) Mueve al eco un turno y dice si atrapó al jugador.

        Recibe:
            anterior: casilla donde estaba el jugador antes de su acción.
            esperando: True si el jugador pasó el turno sin moverse.
        Devuelve:
            True si el eco atrapó al jugador; False si no hay eco o no lo alcanzó.
        """
        if self.eco is None:
            return False
        self.eco.turno(self.jugador.posicion, esperando)
        return self.eco.atrapa(self.jugador.posicion, anterior)

    def posicion_eco(self):
        """
        Casilla del eco para dibujarlo.

        Recibe: nada.
        Devuelve:
            La tupla (fila, columna), o None si no hay eco o todavía está dormido.
        """
        if self.eco is None or not self.eco.activo:
            return None
        return self.eco.posicion

    def _registrar(self):
        """(Interno) Guarda una foto de la partida en el historial (lista doble)."""
        self.historial.registrar(self.jugador.posicion, self.posiciones_enemigos(),
                                 self.jugador.movimientos)

    def _crear_enemigos(self, cantidad):
        """
        (Interno) Crea enemigos con rutas de patrulla que no tocan el camino más corto a la
        salida ni quedan cerca de la entrada. Si no encuentra rutas buenas, pone menos enemigos.

        Recibe:
            cantidad: cuántos enemigos se quieren.
        Devuelve:
            Una lista de Enemigo.
        """
        prohibidas = set(self.solucion)
        candidatas = []
        for f in range(self.laberinto.alto):
            for c in range(self.laberinto.ancho):
                if self.laberinto.es_transitable(f, c) and (f, c) not in prohibidas:
                    candidatas.append((f, c))

        enemigos = []
        intentos = 0
        while len(enemigos) < cantidad and candidatas and intentos < 400:
            intentos += 1
            a = self._azar.choice(candidatas)
            b = self._azar.choice(candidatas)
            camino = camino_mas_corto(self.laberinto, a, b)
            if camino is None or not 6 <= len(camino) - 1 <= 20:
                continue
            if self._ruta_valida(camino, prohibidas):
                enemigos.append(Enemigo(crear_ruta_patrulla(camino)))
        return enemigos

    def _ruta_valida(self, camino, prohibidas):
        """
        (Interno) Revisa que ninguna casilla de la ruta esté en el camino a la salida
        ni muy cerca de la entrada.

        Recibe:
            camino: lista de tuplas de la ruta.
            prohibidas: conjunto de casillas del camino más corto a la salida.
        Devuelve:
            True si la ruta sirve.
        """
        ef, ec = self.laberinto.entrada
        for casilla in camino:
            if casilla in prohibidas:
                return False
            if abs(casilla[0] - ef) + abs(casilla[1] - ec) < DISTANCIA_MINIMA_ENTRADA:
                return False
        return True
