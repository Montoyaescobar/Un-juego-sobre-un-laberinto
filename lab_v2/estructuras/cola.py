"""
cola.py
Cola (Queue) implementada desde cero con nodos y referencias.

Regla de la cola: FIFO (First In, First Out) -> el primero que entra es el primero que sale.

    frente -> [A] -> [B] -> [C] -> None
                              ^
                            final

Uso en el juego del laberinto:
    - BFS (búsqueda en anchura) para encontrar el camino más corto (pista).
    - Cola de eventos / enemigos en espera.

Tabla de complejidad (n = cantidad de elementos):
    | Operación    | Complejidad |
    |--------------|-------------|
    | encolar      | O(1)        |
    | desencolar   | O(1)        |
    | ver_frente   | O(1)        |
    | esta_vacia   | O(1)        |
    | tamanio      | O(1)        |
(O(1) porque se guarda un puntero al frente Y otro al final: nunca se recorre.)
"""

from estructuras.nodo import Nodo
from estructuras.errores import EstructuraVaciaError


class Cola:
    """Cola con nodos enlazados. NO usa list, deque ni colecciones del lenguaje."""

    def __init__(self):
        """
        Crea una cola vacía.

        Recibe: nada.
        Devuelve: nada (constructor).
        """
        self._frente = None    # nodo que saldrá primero
        self._final = None     # último nodo que entró
        self._tamanio = 0

    def encolar(self, dato):
        """
        Agrega un dato al final de la cola.

        Recibe:
            dato: el valor a guardar.
        Devuelve:
            Nada.
        """
        nuevo = Nodo(dato)
        if self.esta_vacia():
            self._frente = nuevo          # único elemento: es frente y final
        else:
            self._final.siguiente = nuevo  # el último actual apunta al nuevo
        self._final = nuevo
        self._tamanio += 1

    def desencolar(self):
        """
        Quita y devuelve el dato del frente.

        Recibe: nada.
        Devuelve:
            El dato que estaba al frente.
        Lanza:
            EstructuraVaciaError si la cola está vacía.
        """
        if self.esta_vacia():
            raise EstructuraVaciaError("No se puede desencolar: la cola está vacía.")
        dato = self._frente.dato
        self._frente = self._frente.siguiente
        if self._frente is None:           # se vació: también hay que limpiar el final
            self._final = None
        self._tamanio -= 1
        return dato

    def ver_frente(self):
        """
        Devuelve el dato del frente SIN quitarlo.

        Recibe: nada.
        Devuelve:
            El dato del frente.
        Lanza:
            EstructuraVaciaError si la cola está vacía.
        """
        if self.esta_vacia():
            raise EstructuraVaciaError("No hay frente: la cola está vacía.")
        return self._frente.dato

    def esta_vacia(self):
        """
        Dice si la cola no tiene elementos.

        Recibe: nada.
        Devuelve:
            True si está vacía, False si no.
        """
        return self._frente is None

    def tamanio(self):
        """
        Cantidad de elementos en la cola.

        Recibe: nada.
        Devuelve:
            Un entero (0 si está vacía).
        """
        return self._tamanio

    def vaciar(self):
        """
        Deja la cola vacía.

        Recibe: nada.
        Devuelve: nada.
        """
        self._frente = None
        self._final = None
        self._tamanio = 0

    def __str__(self):
        """Texto para depurar: 'Cola(frente -> 1, 2, 3)'."""
        texto = ""
        actual = self._frente
        while actual is not None:
            texto += str(actual.dato)
            if actual.siguiente is not None:
                texto += ", "
            actual = actual.siguiente
        return "Cola(frente -> " + texto + ")"
