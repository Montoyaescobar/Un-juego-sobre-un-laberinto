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
    """Enemigo que recorre su ruta circular un paso por turno."""

    def __init__(self, ruta):
        """
        Crea el enemigo en la primera casilla de su ruta.

        Recibe:
            ruta: ListaCircular de casillas (ver crear_ruta_patrulla).
        Devuelve:
            Nada (constructor).
        """
        self.ruta = ruta
        self.ruta.reiniciar_cursor()
        self.posicion = self.ruta.avanzar()

    def avanzar(self):
        """
        Mueve al enemigo a la siguiente casilla de su ruta.

        Recibe: nada.
        Devuelve:
            La nueva posición (fila, columna).
        """
        self.posicion = self.ruta.avanzar()
        return self.posicion
