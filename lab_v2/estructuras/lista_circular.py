"""
lista_circular.py
Lista circular simple implementada desde cero.

El último nodo apunta de nuevo al primero, así que se puede dar vueltas sin fin:

        +--> [A] -> [B] -> [C] --+
        |                        |
        +------------------------+

Se guarda un puntero al ÚLTIMO nodo (_ultimo); el primero siempre es _ultimo.siguiente.
Así insertar al inicio y al final es O(1).

Uso en el juego del laberinto:
    - Ruta de patrulla de los enemigos (al llegar al último punto vuelven al primero).
    - Turnos.

Tabla de complejidad (n = cantidad de elementos):
    | Operación          | Complejidad |
    |--------------------|-------------|
    | insertar_inicio    | O(1)        |
    | insertar_final     | O(1)        |
    | insertar_posicion  | O(n)        |
    | eliminar_posicion  | O(n)        |
    | eliminar_dato      | O(n)        |
    | buscar             | O(n)        |
    | recorrer           | O(n)        |
    | avanzar (cursor)   | O(1)        |
"""

from estructuras.nodo import Nodo
from estructuras.errores import EstructuraVaciaError, PosicionInvalidaError


class ListaCircular:
    """Lista circular simple. Posiciones numeradas desde 0."""

    def __init__(self):
        """
        Crea una lista circular vacía.

        Recibe: nada.
        Devuelve: nada (constructor).
        """
        self._ultimo = None     # el primero es self._ultimo.siguiente
        self._tamanio = 0
        self._actual = None     # cursor para dar vueltas con avanzar()

    # ---------------- inserciones ----------------
    def insertar_inicio(self, dato):
        """
        Inserta un dato como primer elemento.

        Recibe:
            dato: valor a guardar.
        Devuelve:
            Nada.
        """
        nuevo = Nodo(dato)
        if self.esta_vacia():
            nuevo.siguiente = nuevo        # se apunta a sí mismo
            self._ultimo = nuevo
            self._actual = nuevo
        else:
            nuevo.siguiente = self._ultimo.siguiente   # apunta al antiguo primero
            self._ultimo.siguiente = nuevo             # el último ahora apunta al nuevo
        self._tamanio += 1

    def insertar_final(self, dato):
        """
        Inserta un dato como último elemento.

        Recibe:
            dato: valor a guardar.
        Devuelve:
            Nada.
        """
        self.insertar_inicio(dato)          # misma operación de enlace...
        if self._tamanio > 1:
            self._ultimo = self._ultimo.siguiente   # ...y el nuevo pasa a ser el último

    def insertar_posicion(self, posicion, dato):
        """
        Inserta un dato en una posición (0 = inicio, tamaño = final).

        Recibe:
            posicion: entero entre 0 y tamanio().
            dato: valor a guardar.
        Devuelve:
            Nada.
        Lanza:
            PosicionInvalidaError si la posición está fuera de rango.
        """
        if not isinstance(posicion, int) or posicion < 0 or posicion > self._tamanio:
            raise PosicionInvalidaError("Posición inválida: " + str(posicion))
        if posicion == 0:
            self.insertar_inicio(dato)
        elif posicion == self._tamanio:
            self.insertar_final(dato)
        else:
            anterior = self._nodo_en(posicion - 1)
            nuevo = Nodo(dato)
            nuevo.siguiente = anterior.siguiente
            anterior.siguiente = nuevo
            self._tamanio += 1

    # ---------------- eliminaciones ----------------
    def eliminar_posicion(self, posicion):
        """
        Elimina el elemento de una posición y lo devuelve.

        Recibe:
            posicion: entero entre 0 y tamanio()-1.
        Devuelve:
            El dato eliminado.
        Lanza:
            EstructuraVaciaError si la lista está vacía.
            PosicionInvalidaError si la posición no existe.
        """
        if self.esta_vacia():
            raise EstructuraVaciaError("No se puede eliminar: la lista está vacía.")
        if not isinstance(posicion, int) or posicion < 0 or posicion >= self._tamanio:
            raise PosicionInvalidaError("Posición inválida: " + str(posicion))

        if self._tamanio == 1:                 # único elemento
            dato = self._ultimo.dato
            self._ultimo = None
            self._actual = None
            self._tamanio = 0
            return dato

        # El "anterior" del primero es el último (por ser circular)
        anterior = self._ultimo if posicion == 0 else self._nodo_en(posicion - 1)
        borrado = anterior.siguiente
        anterior.siguiente = borrado.siguiente     # se salta el nodo borrado
        if borrado is self._ultimo:                # si borramos el último, el último es el anterior
            self._ultimo = anterior
        if borrado is self._actual:                # que el cursor no quede apuntando a un nodo borrado
            self._actual = borrado.siguiente
        self._tamanio -= 1
        return borrado.dato

    def eliminar_dato(self, dato):
        """
        Elimina la primera aparición de un dato.

        Recibe:
            dato: valor a eliminar.
        Devuelve:
            True si lo encontró y eliminó, False si no estaba.
        """
        posicion = self.buscar(dato)
        if posicion == -1:
            return False
        self.eliminar_posicion(posicion)
        return True

    # ---------------- consulta ----------------
    def buscar(self, dato):
        """
        Busca un dato (una sola vuelta).

        Recibe:
            dato: valor a buscar.
        Devuelve:
            La posición (desde 0) de la primera aparición, o -1 si no está.
        """
        if self.esta_vacia():
            return -1
        nodo = self._ultimo.siguiente
        for posicion in range(self._tamanio):
            if nodo.dato == dato:
                return posicion
            nodo = nodo.siguiente
        return -1

    def recorrer(self, accion):
        """
        Recorre la lista UNA vuelta completa, del primero al último.

        Recibe:
            accion: función que recibe cada dato (ej. print).
        Devuelve:
            Nada.
        """
        if self.esta_vacia():
            return
        nodo = self._ultimo.siguiente
        for _ in range(self._tamanio):
            accion(nodo.dato)
            nodo = nodo.siguiente

    def avanzar(self):
        """
        Devuelve el dato donde está el cursor y lo mueve al siguiente.
        Al pasar el último vuelve al primero (de ahí lo "circular").

        Recibe: nada.
        Devuelve:
            El dato actual del cursor.
        Lanza:
            EstructuraVaciaError si la lista está vacía.
        """
        if self.esta_vacia():
            raise EstructuraVaciaError("No hay elementos para avanzar.")
        dato = self._actual.dato
        self._actual = self._actual.siguiente
        return dato

    def ver_actual(self):
        """
        Devuelve el dato del cursor sin moverlo.

        Recibe: nada.
        Devuelve:
            El dato donde está el cursor.
        Lanza:
            EstructuraVaciaError si la lista está vacía.
        """
        if self.esta_vacia():
            raise EstructuraVaciaError("No hay elementos.")
        return self._actual.dato

    def reiniciar_cursor(self):
        """
        Pone el cursor otra vez en el primer elemento.

        Recibe: nada.
        Devuelve: nada.
        """
        if not self.esta_vacia():
            self._actual = self._ultimo.siguiente

    def esta_vacia(self):
        """
        Dice si la lista no tiene elementos.

        Recibe: nada.
        Devuelve:
            True si está vacía, False si no.
        """
        return self._ultimo is None

    def tamanio(self):
        """
        Cantidad de elementos.

        Recibe: nada.
        Devuelve:
            Un entero.
        """
        return self._tamanio

    def _nodo_en(self, posicion):
        """
        (Interno) Devuelve el NODO que está en una posición ya validada.

        Recibe:
            posicion: entero entre 0 y tamanio()-1.
        Devuelve:
            El nodo en esa posición.
        """
        nodo = self._ultimo.siguiente
        for _ in range(posicion):
            nodo = nodo.siguiente
        return nodo

    def __str__(self):
        """Texto para depurar: 'ListaCircular(A -> B -> C -> (vuelve al inicio))'."""
        texto = ""
        if not self.esta_vacia():
            nodo = self._ultimo.siguiente
            for i in range(self._tamanio):
                texto += str(nodo.dato) + " -> "
                nodo = nodo.siguiente
        return "ListaCircular(" + texto + "(vuelve al inicio))"
