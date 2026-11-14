"""
nodo.py
Los "ladrillos" con los que se construyen todas las estructuras.
Cada nodo guarda un dato y referencias (punteros) a otros nodos.

    Nodo        -> pila, cola, lista circular      [dato | siguiente]
    NodoDoble   -> lista doblemente enlazada       [anterior | dato | siguiente]
    NodoArbol   -> árbol binario de búsqueda       [izquierdo | clave, valor | derecho]
"""


class Nodo:
    """Nodo de enlace simple (un solo puntero: siguiente)."""

    def __init__(self, dato):
        """
        Crea un nodo.

        Recibe:
            dato: cualquier valor a guardar (número, tupla, objeto...).
        Devuelve:
            Nada (constructor). El nodo queda sin siguiente (None).
        """
        self.dato = dato
        self.siguiente = None


class NodoDoble:
    """Nodo de enlace doble (dos punteros: anterior y siguiente)."""

    def __init__(self, dato):
        """
        Crea un nodo doble.

        Recibe:
            dato: cualquier valor a guardar.
        Devuelve:
            Nada (constructor). anterior y siguiente quedan en None.
        """
        self.dato = dato
        self.anterior = None
        self.siguiente = None


class NodoArbol:
    """Nodo de árbol binario: un hijo izquierdo y uno derecho."""

    def __init__(self, clave, valor=None):
        """
        Crea un nodo de árbol.

        Recibe:
            clave: valor con el que se ordena el árbol (ej. el puntaje).
            valor: dato asociado a la clave (ej. el nombre del jugador).
        Devuelve:
            Nada (constructor). Sin hijos al inicio.
        """
        self.clave = clave
        self.valor = valor
        self.izquierdo = None
        self.derecho = None
