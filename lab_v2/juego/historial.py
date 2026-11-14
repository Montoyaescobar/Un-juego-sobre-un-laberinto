"""
historial.py
Historial de la partida guardado en una LISTA DOBLEMENTE ENLAZADA propia.

Cómo se usa la lista doble:
    - Después de cada acción se guarda una "foto" de la partida (dónde está el jugador,
      dónde están los enemigos, cuántos movimientos van) al final de la lista.
    - Para la REPETICIÓN se mueve un cursor por la lista hacia ADELANTE y hacia ATRÁS
      (justo para lo que sirve una lista doble: cada nodo conoce al anterior y al siguiente).
"""

from estructuras.lista_doble import ListaDoble


class Historial:
    """Camino recorrido en la partida, navegable en ambos sentidos."""

    def __init__(self):
        """
        Crea un historial vacío.

        Recibe: nada.
        Devuelve: nada (constructor).
        """
        self._lista = ListaDoble()
        self._indice = 0               # posición del cursor (para mostrar "paso 3 de 40")

    def registrar(self, posicion_jugador, posiciones_enemigos, movimientos):
        """
        Guarda una foto de la partida al final del historial.

        Recibe:
            posicion_jugador: tupla (fila, columna) del jugador.
            posiciones_enemigos: tupla/lista con las posiciones de los enemigos.
            movimientos: movimientos gastados hasta ese momento.
        Devuelve:
            Nada.
        """
        self._lista.insertar_final((posicion_jugador, tuple(posiciones_enemigos), movimientos))

    def actual(self):
        """
        Foto donde está el cursor.

        Recibe: nada.
        Devuelve:
            Tupla (posicion_jugador, posiciones_enemigos, movimientos).
        Lanza:
            EstructuraVaciaError si no hay fotos.
        """
        return self._lista.ver_actual()

    def adelante(self):
        """
        Avanza el cursor una foto.

        Recibe: nada.
        Devuelve:
            True si avanzó, False si ya estaba en la última.
        """
        if self._lista.adelante():
            self._indice += 1
            return True
        return False

    def atras(self):
        """
        Retrocede el cursor una foto.

        Recibe: nada.
        Devuelve:
            True si retrocedió, False si ya estaba en la primera.
        """
        if self._lista.atras():
            self._indice -= 1
            return True
        return False

    def recorrer_hasta_actual(self, accion):
        """
        Recorre las fotos desde la primera hasta la actual (camino recorrido hasta ahí).

        Recibe:
            accion: función que recibe cada foto (posicion_jugador, enemigos, movimientos).
        Devuelve:
            Nada.
        """
        self._lista.recorrer_hasta_actual(accion)

    def ir_al_inicio(self):
        """Pone el cursor en la primera foto. Recibe: nada. Devuelve: nada."""
        self._lista.ir_al_inicio()
        self._indice = 0

    def ir_al_final(self):
        """Pone el cursor en la última foto. Recibe: nada. Devuelve: nada."""
        self._lista.ir_al_final()
        self._indice = self._lista.tamanio() - 1 if self._lista.tamanio() > 0 else 0

    def indice(self):
        """Posición del cursor, desde 0. Recibe: nada. Devuelve: un entero."""
        return self._indice

    def total(self):
        """Cantidad de fotos guardadas. Recibe: nada. Devuelve: un entero."""
        return self._lista.tamanio()
