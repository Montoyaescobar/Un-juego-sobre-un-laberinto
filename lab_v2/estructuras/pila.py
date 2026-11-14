"""
pila.py
Pila (Stack) implementada desde cero con nodos y referencias.

Regla de la pila: LIFO (Last In, First Out) -> el último que entra es el primero que sale.

    tope -> [C] -> [B] -> [A] -> None

Uso en el juego del laberinto:
    - Backtracking al GENERAR el laberinto (guardar el camino para devolverse).
    - DESHACER movimiento del jugador.

Tabla de complejidad (n = cantidad de elementos):
    | Operación   | Complejidad |
    |-------------|-------------|
    | apilar      | O(1)        |
    | desapilar   | O(1)        |
    | ver_tope    | O(1)        |
    | esta_vacia  | O(1)        |
    | tamanio     | O(1)        |
"""

from estructuras.nodo import Nodo
from estructuras.errores import EstructuraVaciaError


class Pila:
    """Pila con nodos enlazados. NO usa list, deque ni ninguna colección del lenguaje."""

    def __init__(self):
        """
        Crea una pila vacía.

        Recibe: nada.
        Devuelve: nada (constructor).
        """
        self._tope = None      # referencia al nodo de arriba
        self._tamanio = 0      # contador, así tamanio() es O(1)

    def apilar(self, dato):
        """
        Pone un dato encima de la pila.

        Recibe:
            dato: el valor a guardar.
        Devuelve:
            Nada.
        """
        nuevo = Nodo(dato)
        nuevo.siguiente = self._tope   # el nuevo apunta al que era el tope
        self._tope = nuevo             # ahora el nuevo es el tope
        self._tamanio += 1

    def desapilar(self):
        """
        Quita y devuelve el dato que está en el tope.

        Recibe: nada.
        Devuelve:
            El dato que estaba en el tope.
        Lanza:
            EstructuraVaciaError si la pila está vacía.
        """
        if self.esta_vacia():
            raise EstructuraVaciaError("No se puede desapilar: la pila está vacía.")
        dato = self._tope.dato
        self._tope = self._tope.siguiente   # el tope baja un nodo
        self._tamanio -= 1
        return dato

    def ver_tope(self):
        """
        Devuelve el dato del tope SIN quitarlo.

        Recibe: nada.
        Devuelve:
            El dato del tope.
        Lanza:
            EstructuraVaciaError si la pila está vacía.
        """
        if self.esta_vacia():
            raise EstructuraVaciaError("No hay tope: la pila está vacía.")
        return self._tope.dato

    def esta_vacia(self):
        """
        Dice si la pila no tiene elementos.

        Recibe: nada.
        Devuelve:
            True si está vacía, False si tiene al menos un elemento.
        """
        return self._tope is None

    def tamanio(self):
        """
        Cantidad de elementos que hay en la pila.

        Recibe: nada.
        Devuelve:
            Un entero (0 si está vacía).
        """
        return self._tamanio

    def vaciar(self):
        """
        Deja la pila vacía (útil al reiniciar una partida).

        Recibe: nada.
        Devuelve: nada.
        """
        self._tope = None
        self._tamanio = 0

    def __str__(self):
        """Texto para depurar: muestra de tope a fondo, ej. 'Pila(tope -> 3, 2, 1)'."""
        texto = ""
        actual = self._tope
        while actual is not None:
            texto += str(actual.dato)
            if actual.siguiente is not None:
                texto += ", "
            actual = actual.siguiente
        return "Pila(tope -> " + texto + ")"
