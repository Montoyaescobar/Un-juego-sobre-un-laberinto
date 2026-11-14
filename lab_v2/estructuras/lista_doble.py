"""
lista_doble.py
Lista doblemente enlazada implementada desde cero.

Cada nodo conoce al anterior y al siguiente, así se puede ir en AMBOS sentidos:

    None <- [A] <-> [B] <-> [C] -> None
            ^                ^
         cabeza            cola

Uso en el juego del laberinto:
    - CAMINO RECORRIDO del jugador, navegable hacia adelante y hacia atrás
      (modo repetición de la partida).

Tabla de complejidad (n = cantidad de elementos):
    | Operación                 | Complejidad |
    |---------------------------|-------------|
    | insertar_inicio / final   | O(1)        |
    | insertar_posicion         | O(n)        |
    | eliminar_posicion         | O(n)        |
    | eliminar_dato             | O(n)        |
    | buscar                    | O(n)        |
    | recorrer_adelante / atras | O(n)        |
    | adelante / atras (cursor) | O(1)        |
"""

from estructuras.nodo import NodoDoble
from estructuras.errores import EstructuraVaciaError, PosicionInvalidaError


class ListaDoble:
    """Lista doblemente enlazada. Posiciones numeradas desde 0."""

    def __init__(self):
        """
        Crea una lista vacía.

        Recibe: nada.
        Devuelve: nada (constructor).
        """
        self._cabeza = None     # primer nodo
        self._cola = None       # último nodo
        self._tamanio = 0
        self._actual = None     # cursor para navegar con adelante() / atras()

    # ---------------- inserciones ----------------
    def insertar_inicio(self, dato):
        """
        Inserta un dato como primer elemento.

        Recibe:
            dato: valor a guardar.
        Devuelve:
            Nada.
        """
        nuevo = NodoDoble(dato)
        if self.esta_vacia():
            self._cabeza = nuevo
            self._cola = nuevo
        else:
            nuevo.siguiente = self._cabeza
            self._cabeza.anterior = nuevo
            self._cabeza = nuevo
        if self._actual is None:
            self._actual = nuevo
        self._tamanio += 1

    def insertar_final(self, dato):
        """
        Inserta un dato como último elemento.

        Recibe:
            dato: valor a guardar.
        Devuelve:
            Nada.
        """
        nuevo = NodoDoble(dato)
        if self.esta_vacia():
            self._cabeza = nuevo
            self._cola = nuevo
        else:
            nuevo.anterior = self._cola
            self._cola.siguiente = nuevo
            self._cola = nuevo
        if self._actual is None:
            self._actual = nuevo
        self._tamanio += 1

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
            siguiente = self._nodo_en(posicion)     # el que quedará después del nuevo
            anterior = siguiente.anterior
            nuevo = NodoDoble(dato)
            nuevo.anterior = anterior
            nuevo.siguiente = siguiente
            anterior.siguiente = nuevo
            siguiente.anterior = nuevo
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

        nodo = self._nodo_en(posicion)
        # Se "puentea" el nodo: el de atrás y el de adelante se enlazan entre sí
        if nodo.anterior is not None:
            nodo.anterior.siguiente = nodo.siguiente
        else:
            self._cabeza = nodo.siguiente      # era la cabeza
        if nodo.siguiente is not None:
            nodo.siguiente.anterior = nodo.anterior
        else:
            self._cola = nodo.anterior         # era la cola
        if nodo is self._actual:               # el cursor no puede quedar en un nodo borrado
            self._actual = nodo.siguiente if nodo.siguiente is not None else nodo.anterior
        self._tamanio -= 1
        return nodo.dato

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

    # ---------------- consulta y recorridos ----------------
    def buscar(self, dato):
        """
        Busca un dato de la cabeza hacia la cola.

        Recibe:
            dato: valor a buscar.
        Devuelve:
            La posición (desde 0) de la primera aparición, o -1 si no está.
        """
        nodo = self._cabeza
        posicion = 0
        while nodo is not None:
            if nodo.dato == dato:
                return posicion
            nodo = nodo.siguiente
            posicion += 1
        return -1

    def recorrer_adelante(self, accion):
        """
        Recorre de la cabeza a la cola.

        Recibe:
            accion: función que recibe cada dato (ej. print).
        Devuelve:
            Nada.
        """
        nodo = self._cabeza
        while nodo is not None:
            accion(nodo.dato)
            nodo = nodo.siguiente

    def recorrer_atras(self, accion):
        """
        Recorre de la cola a la cabeza (sentido contrario).

        Recibe:
            accion: función que recibe cada dato (ej. print).
        Devuelve:
            Nada.
        """
        nodo = self._cola
        while nodo is not None:
            accion(nodo.dato)
            nodo = nodo.anterior

    def recorrer_hasta_actual(self, accion):
        """
        Recorre de la cabeza hasta el cursor (incluido). Sirve para dibujar el camino
        recorrido hasta el paso que se está viendo.

        Recibe:
            accion: función que recibe cada dato.
        Devuelve:
            Nada.
        """
        nodo = self._cabeza
        while nodo is not None:
            accion(nodo.dato)
            if nodo is self._actual:
                break
            nodo = nodo.siguiente

    # ---------------- cursor (navegar adelante / atrás) ----------------
    def ver_actual(self):
        """
        Devuelve el dato donde está el cursor.

        Recibe: nada.
        Devuelve:
            El dato actual.
        Lanza:
            EstructuraVaciaError si la lista está vacía.
        """
        if self.esta_vacia():
            raise EstructuraVaciaError("No hay elementos.")
        return self._actual.dato

    def adelante(self):
        """
        Mueve el cursor un paso hacia adelante (hacia la cola).

        Recibe: nada.
        Devuelve:
            True si se pudo mover, False si ya estaba en el último.
        """
        if self._actual is not None and self._actual.siguiente is not None:
            self._actual = self._actual.siguiente
            return True
        return False

    def atras(self):
        """
        Mueve el cursor un paso hacia atrás (hacia la cabeza).

        Recibe: nada.
        Devuelve:
            True si se pudo mover, False si ya estaba en el primero.
        """
        if self._actual is not None and self._actual.anterior is not None:
            self._actual = self._actual.anterior
            return True
        return False

    def ir_al_inicio(self):
        """Pone el cursor en el primer elemento. Recibe: nada. Devuelve: nada."""
        self._actual = self._cabeza

    def ir_al_final(self):
        """Pone el cursor en el último elemento. Recibe: nada. Devuelve: nada."""
        self._actual = self._cola

    def esta_vacia(self):
        """
        Dice si la lista no tiene elementos.

        Recibe: nada.
        Devuelve:
            True si está vacía, False si no.
        """
        return self._cabeza is None

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
        (Interno) Devuelve el NODO de una posición ya validada.
        Parte desde el extremo más cercano (cabeza o cola) para recorrer menos.

        Recibe:
            posicion: entero entre 0 y tamanio()-1.
        Devuelve:
            El nodo en esa posición.
        """
        if posicion <= self._tamanio // 2:
            nodo = self._cabeza
            for _ in range(posicion):
                nodo = nodo.siguiente
        else:
            nodo = self._cola
            for _ in range(self._tamanio - 1 - posicion):
                nodo = nodo.anterior
        return nodo

    def __str__(self):
        """Texto para depurar: 'ListaDoble(A <-> B <-> C)'."""
        texto = ""
        nodo = self._cabeza
        while nodo is not None:
            texto += str(nodo.dato)
            if nodo.siguiente is not None:
                texto += " <-> "
            nodo = nodo.siguiente
        return "ListaDoble(" + texto + ")"
