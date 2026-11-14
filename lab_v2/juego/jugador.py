"""
jugador.py
El jugador: se mueve por el laberinto y puede DESHACER movimientos con la PILA propia.

Cómo se usa la pila:
    - Cada vez que el jugador se mueve, la posición de donde VENÍA se apila.
    - deshacer() desapila y lo devuelve a esa posición (el último movimiento se
      deshace primero: LIFO).

Reglas del juego:
    - Cada movimiento y cada deshacer cuentan como 1 movimiento (deshacer cuesta).
    - Si se acaban los movimientos antes de llegar a la salida, se pierde.
    - Pedir una pista (camino más corto a la salida, calculado con BFS y la Cola)
      cuesta 5 movimientos.
"""

from estructuras.pila import Pila
from juego.solver import camino_mas_corto

COSTO_PISTA = 5      # una pista cuesta 5 movimientos

DIRECCIONES = {
    "arriba": (-1, 0),
    "abajo": (1, 0),
    "izquierda": (0, -1),
    "derecha": (0, 1),
}


class Jugador:
    """Jugador con posición, contador de movimientos y pila para deshacer."""

    def __init__(self, laberinto, max_movimientos):
        """
        Crea el jugador en la entrada del laberinto.

        Recibe:
            laberinto: el Laberinto donde juega.
            max_movimientos: entero, límite de movimientos antes de perder.
        Devuelve:
            Nada (constructor).
        """
        self.laberinto = laberinto
        self.posicion = laberinto.entrada
        self.movimientos = 0
        self.max_movimientos = max_movimientos
        self.pistas_usadas = 0
        self._pila_pasos = Pila()          # posiciones anteriores, para deshacer

    def mover(self, direccion):
        """
        Intenta mover al jugador una casilla.

        Recibe:
            direccion: "arriba", "abajo", "izquierda" o "derecha".
        Devuelve:
            True si se movió; False si hay pared, ya terminó la partida o no quedan movimientos.
        Lanza:
            ValueError si la dirección no existe.
        """
        if direccion not in DIRECCIONES:
            raise ValueError("Dirección desconocida: " + str(direccion))
        if self.partida_terminada():
            return False
        df, dc = DIRECCIONES[direccion]
        nueva = (self.posicion[0] + df, self.posicion[1] + dc)
        if not self.laberinto.es_transitable(nueva[0], nueva[1]):
            return False                    # choque con pared: no cuesta movimiento
        self._pila_pasos.apilar(self.posicion)
        self.posicion = nueva
        self.movimientos += 1
        return True

    def deshacer(self):
        """
        Deshace el último movimiento (vuelve a la casilla anterior). Cuenta como 1 movimiento.

        Recibe: nada.
        Devuelve:
            True si se pudo deshacer; False si no hay nada que deshacer o la partida terminó.
        """
        if self.partida_terminada() or self._pila_pasos.esta_vacia():
            return False
        self.posicion = self._pila_pasos.desapilar()
        self.movimientos += 1
        return True

    def esperar(self):
        """
        Pasa un turno sin moverse (cuesta 1 movimiento). Sirve para dejar pasar a un enemigo,
        pero el eco se acerca mientras tanto.

        Recibe: nada.
        Devuelve:
            True si se gastó el turno; False si la partida ya terminó.
        """
        if self.partida_terminada():
            return False
        self.movimientos += 1
        return True

    def penalizar(self, cantidad):
        """
        Gasta de golpe varios movimientos (lo usa el radar cuando toca al jugador).

        Recibe:
            cantidad: entero mayor o igual a 0, cuántos movimientos se pierden.
        Devuelve:
            Nada. Si la partida ya terminó, no hace nada.
        """
        if self.partida_terminada() or cantidad <= 0:
            return
        self.movimientos += cantidad

    def pedir_pista(self):
        """
        Calcula el camino más corto desde donde está el jugador hasta la salida (BFS con Cola).
        Cuesta COSTO_PISTA movimientos y solo se puede pedir si sobran más de esos movimientos.

        Recibe: nada.
        Devuelve:
            Lista de tuplas (fila, columna) desde la posición actual hasta la salida,
            o None si no se puede dar la pista (partida terminada o pocos movimientos).
        """
        if self.partida_terminada() or self.movimientos_restantes() <= COSTO_PISTA:
            return None
        camino = camino_mas_corto(self.laberinto, self.posicion, self.laberinto.salida)
        if camino is None:
            return None
        self.movimientos += COSTO_PISTA
        self.pistas_usadas += 1
        return camino

    def pasos_por_deshacer(self):
        """
        Cuántos movimientos se podrían deshacer.

        Recibe: nada.
        Devuelve:
            Un entero (tamaño de la pila).
        """
        return self._pila_pasos.tamanio()

    def movimientos_restantes(self):
        """
        Movimientos que le quedan al jugador.

        Recibe: nada.
        Devuelve:
            Un entero (nunca negativo).
        """
        restantes = self.max_movimientos - self.movimientos
        return restantes if restantes > 0 else 0

    def gano(self):
        """
        Dice si el jugador está en la salida.

        Recibe: nada.
        Devuelve:
            True si llegó a la salida.
        """
        return self.posicion == self.laberinto.salida

    def perdio(self):
        """
        Dice si el jugador se quedó sin movimientos sin llegar a la salida.

        Recibe: nada.
        Devuelve:
            True si perdió.
        """
        return (not self.gano()) and self.movimientos >= self.max_movimientos

    def partida_terminada(self):
        """
        Dice si la partida ya acabó (ganó o perdió).

        Recibe: nada.
        Devuelve:
            True si terminó.
        """
        return self.gano() or self.perdio()
