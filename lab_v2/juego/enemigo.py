"""
enemigo.py
Enemigos que patrullan una ruta cerrada guardada en una LISTA CIRCULAR propia.

Cómo se usa la lista circular:
    - La ruta de patrulla es una lista circular de casillas. Cada turno el enemigo llama a
      avanzar() de la lista, que le da la siguiente casilla; al llegar a la última, la lista
      da la vuelta sola y vuelve a la primera. Por eso el enemigo patrulla SIN FIN.
    - Ruta de ejemplo (ida y vuelta por un pasillo):  A -> B -> C -> B -> (vuelve a A)
"""

from estructuras.lista_circular import ListaCircular
from juego.solver import camino_mas_corto


def crear_ruta_patrulla(camino):
    """
    Convierte un camino A...B en una ruta cerrada de ida y vuelta (lista circular).

    Recibe:
        camino: lista de tuplas (fila, columna) de A a B, con casillas vecinas entre sí.
    Devuelve:
        Una ListaCircular con A..B y luego B-1..A+1, de modo que TODAS las casillas
        consecutivas (también del último al primero) son vecinas.
    """
    ruta = ListaCircular()
    for casilla in camino:
        ruta.insertar_final(casilla)
    for i in range(len(camino) - 2, 0, -1):      # el regreso, sin repetir los extremos
        ruta.insertar_final(camino[i])
    return ruta


class Enemigo:
    """Enemigo autónomo en tiempo real: patrulla su ruta circular o persigue con BFS."""

    def __init__(self, ruta, dificultad="1", intervalo_paso=1.0, rango_vision=4):
        """
        Crea el enemigo en la primera casilla de su ruta.

        Recibe:
            ruta: ListaCircular de casillas (ver crear_ruta_patrulla).
            dificultad: identificador del nivel.
            intervalo_paso: segundos entre pasos.
            rango_vision: distancia (en pasos BFS) a la que empieza a perseguir.
        """
        self.ruta = ruta
        self.dificultad = dificultad
        self.intervalo_paso = intervalo_paso
        self.rango_vision = rango_vision
        self.tiempo_acumulado = 0.0
        self.progreso_paso = 0.0
        self.estado = "patrulla"
        self.ruta.reiniciar_cursor()
        self.posicion = self.ruta.avanzar()
        self._objetivo_patrulla = self.posicion

    def actualizar(self, dt, pos_jugador, laberinto):
        """
        Acumula tiempo y, al cumplirse el intervalo, da un paso.

        Devuelve:
            True si dio un paso en este frame.
        """
        self.tiempo_acumulado += dt
        if self.intervalo_paso <= 0:
            self.progreso_paso = 1.0
        else:
            self.progreso_paso = min(1.0, self.tiempo_acumulado / self.intervalo_paso)
        if self.tiempo_acumulado < self.intervalo_paso:
            return False
        self.tiempo_acumulado -= self.intervalo_paso
        if self.tiempo_acumulado >= self.intervalo_paso:   # evita ráfagas tras un dt enorme
            self.tiempo_acumulado = 0.0
        self.progreso_paso = 0.0

        camino = camino_mas_corto(laberinto, self.posicion, pos_jugador)
        if camino is not None and len(camino) - 1 <= self.rango_vision:
            self.estado = "persecucion"
            if len(camino) > 1:
                self.posicion = camino[1]
                return True
            return False

        self.estado = "patrulla"
        if self.posicion == self._objetivo_patrulla:
            self._objetivo_patrulla = self.ruta.avanzar()
        if self.posicion == self._objetivo_patrulla:
            return False
        vuelta = camino_mas_corto(laberinto, self.posicion, self._objetivo_patrulla)
        if vuelta is None or len(vuelta) < 2:
            self.posicion = self._objetivo_patrulla
        else:
            self.posicion = vuelta[1]
        return True

    def avanzar(self):
        """
        Mueve al enemigo a la siguiente casilla de su ruta (llamada forzada).

        Devuelve:
            La nueva posición (fila, columna).
        """
        self.posicion = self.ruta.avanzar()
        self._objetivo_patrulla = self.posicion
        return self.posicion
