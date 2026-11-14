r"""
arbol_bst.py
Árbol binario de búsqueda (BST) implementado desde cero.

Regla: para cada nodo, lo menor va a su izquierda y lo mayor (o igual) a su derecha.

              50
            /    \
          30      70
         /  \    /  \
       20   40  60   80

Uso en el juego del laberinto:
    - Tabla de MEJORES PUNTAJES (clave = puntaje, valor = nombre del jugador).

Se permiten claves repetidas (dos jugadores con el mismo puntaje): las repetidas van a la derecha.

Tabla de complejidad (n = nodos, h = altura del árbol):
    | Operación                     | Promedio  | Peor caso (árbol "chueco") |
    |-------------------------------|-----------|----------------------------|
    | insertar                      | O(log n)  | O(n)                       |
    | buscar                        | O(log n)  | O(n)                       |
    | eliminar                      | O(log n)  | O(n)                       |
    | inorden / preorden / posorden | O(n)      | O(n)                       |
"""

from estructuras.nodo import NodoArbol
from estructuras.errores import EstructuraVaciaError


class ArbolBST:
    """Árbol binario de búsqueda con pares (clave, valor)."""

    def __init__(self):
        """
        Crea un árbol vacío.

        Recibe: nada.
        Devuelve: nada (constructor).
        """
        self._raiz = None
        self._tamanio = 0

    # ---------------- insertar ----------------
    def insertar(self, clave, valor=None):
        """
        Inserta un par (clave, valor) en su lugar correcto.

        Recibe:
            clave: lo que ordena el árbol (ej. puntaje). Debe poder compararse con <.
            valor: dato asociado (ej. nombre del jugador).
        Devuelve:
            Nada.
        """
        nuevo = NodoArbol(clave, valor)
        if self._raiz is None:
            self._raiz = nuevo
        else:
            actual = self._raiz
            while True:                       # bajar hasta encontrar el hueco
                if clave < actual.clave:
                    if actual.izquierdo is None:
                        actual.izquierdo = nuevo
                        break
                    actual = actual.izquierdo
                else:
                    if actual.derecho is None:
                        actual.derecho = nuevo
                        break
                    actual = actual.derecho
        self._tamanio += 1

    # ---------------- buscar ----------------
    def buscar(self, clave):
        """
        Busca una clave.

        Recibe:
            clave: la clave a buscar.
        Devuelve:
            El valor asociado a la clave, o None si la clave no está.
            (Para saber con certeza si existe, usar contiene().)
        """
        nodo = self._buscar_nodo(clave)
        return None if nodo is None else nodo.valor

    def contiene(self, clave):
        """
        Dice si una clave está en el árbol.

        Recibe:
            clave: la clave a buscar.
        Devuelve:
            True si está, False si no.
        """
        return self._buscar_nodo(clave) is not None

    def _buscar_nodo(self, clave):
        """
        (Interno) Devuelve el nodo con esa clave, o None.

        Recibe:
            clave: la clave a buscar.
        Devuelve:
            El NodoArbol encontrado o None.
        """
        actual = self._raiz
        while actual is not None:
            if clave == actual.clave:
                return actual
            if clave < actual.clave:
                actual = actual.izquierdo
            else:
                actual = actual.derecho
        return None

    # ---------------- eliminar ----------------
    def eliminar(self, clave):
        """
        Elimina UN nodo con esa clave (el primero que encuentre bajando desde la raíz).

        Recibe:
            clave: la clave a eliminar.
        Devuelve:
            True si lo eliminó, False si la clave no estaba.
        """
        self._raiz, eliminado = self._eliminar_nodo(self._raiz, clave)
        if eliminado:
            self._tamanio -= 1
        return eliminado

    def _eliminar_nodo(self, nodo, clave):
        """
        (Interno, recursivo) Elimina la clave dentro del subárbol de 'nodo'.

        Tres casos al encontrar el nodo:
            1. Sin hijos            -> se quita (queda None).
            2. Con un solo hijo     -> el hijo ocupa su lugar.
            3. Con dos hijos        -> se reemplaza por su SUCESOR (el menor del subárbol
                                       derecho) y luego se quita ese sucesor.

        Recibe:
            nodo: raíz del subárbol donde buscar.
            clave: la clave a eliminar.
        Devuelve:
            (nueva_raiz_del_subarbol, fue_eliminado)
        """
        if nodo is None:
            return None, False
        if clave < nodo.clave:
            nodo.izquierdo, eliminado = self._eliminar_nodo(nodo.izquierdo, clave)
            return nodo, eliminado
        if clave > nodo.clave:
            nodo.derecho, eliminado = self._eliminar_nodo(nodo.derecho, clave)
            return nodo, eliminado

        # clave == nodo.clave: este es el nodo a eliminar
        if nodo.izquierdo is None:
            return nodo.derecho, True
        if nodo.derecho is None:
            return nodo.izquierdo, True
        sucesor = nodo.derecho
        while sucesor.izquierdo is not None:
            sucesor = sucesor.izquierdo
        nodo.clave = sucesor.clave
        nodo.valor = sucesor.valor
        nodo.derecho = self._quitar_minimo(nodo.derecho)
        return nodo, True

    def _quitar_minimo(self, nodo):
        """
        (Interno, recursivo) Quita el nodo más a la izquierda de un subárbol.

        Recibe:
            nodo: raíz del subárbol.
        Devuelve:
            La nueva raíz del subárbol sin ese mínimo.
        """
        if nodo.izquierdo is None:
            return nodo.derecho
        nodo.izquierdo = self._quitar_minimo(nodo.izquierdo)
        return nodo

    # ---------------- recorridos ----------------
    def inorden(self, accion):
        """
        Recorrido INORDEN: izquierda, nodo, derecha -> de menor a mayor clave.

        Recibe:
            accion: función accion(clave, valor) que se llama en cada nodo.
        Devuelve:
            Nada.
        """
        self._inorden(self._raiz, accion)

    def _inorden(self, nodo, accion):
        """(Interno) Parte recursiva del inorden."""
        if nodo is not None:
            self._inorden(nodo.izquierdo, accion)
            accion(nodo.clave, nodo.valor)
            self._inorden(nodo.derecho, accion)

    def preorden(self, accion):
        """
        Recorrido PREORDEN: nodo, izquierda, derecha.

        Recibe:
            accion: función accion(clave, valor) que se llama en cada nodo.
        Devuelve:
            Nada.
        """
        self._preorden(self._raiz, accion)

    def _preorden(self, nodo, accion):
        """(Interno) Parte recursiva del preorden."""
        if nodo is not None:
            accion(nodo.clave, nodo.valor)
            self._preorden(nodo.izquierdo, accion)
            self._preorden(nodo.derecho, accion)

    def posorden(self, accion):
        """
        Recorrido POSORDEN: izquierda, derecha, nodo.

        Recibe:
            accion: función accion(clave, valor) que se llama en cada nodo.
        Devuelve:
            Nada.
        """
        self._posorden(self._raiz, accion)

    def _posorden(self, nodo, accion):
        """(Interno) Parte recursiva del posorden."""
        if nodo is not None:
            self._posorden(nodo.izquierdo, accion)
            self._posorden(nodo.derecho, accion)
            accion(nodo.clave, nodo.valor)

    def inorden_inverso(self, accion):
        """
        Inorden al revés: derecha, nodo, izquierda -> de MAYOR a menor clave.
        Es el orden que se usa para mostrar el ranking (mejor puntaje primero).

        Recibe:
            accion: función accion(clave, valor) que se llama en cada nodo.
        Devuelve:
            Nada.
        """
        self._inorden_inverso(self._raiz, accion)

    def _inorden_inverso(self, nodo, accion):
        """(Interno) Parte recursiva del inorden inverso."""
        if nodo is not None:
            self._inorden_inverso(nodo.derecho, accion)
            accion(nodo.clave, nodo.valor)
            self._inorden_inverso(nodo.izquierdo, accion)

    # ---------------- apoyo para dibujar el árbol (interfaz gráfica) ----------------
    def _ids_por_nodo(self):
        """
        (Interno) Numera los nodos 0, 1, 2... en orden INORDEN (de menor a mayor clave).

        Recibe: nada.
        Devuelve:
            Un diccionario {id(nodo): número}.
        """
        ids = {}
        contador = 0

        def visitar(nodo):
            nonlocal contador
            if nodo is None:
                return
            visitar(nodo.izquierdo)
            ids[id(nodo)] = contador
            contador += 1
            visitar(nodo.derecho)

        visitar(self._raiz)
        return ids

    def nodos_para_dibujar(self):
        """
        Describe todos los nodos para que la interfaz pueda dibujar el árbol.
        El número de cada nodo es su posición en el inorden, así que sirve de coordenada x.

        Recibe: nada.
        Devuelve:
            Lista de diccionarios con: id, clave, valor, nivel (0 = raíz), izq y der
            (id del hijo o None).
        """
        ids = self._ids_por_nodo()
        resultado = []

        def visitar(nodo, nivel):
            if nodo is None:
                return
            visitar(nodo.izquierdo, nivel + 1)
            resultado.append({
                "id": ids[id(nodo)], "clave": nodo.clave, "valor": nodo.valor, "nivel": nivel,
                "izq": None if nodo.izquierdo is None else ids[id(nodo.izquierdo)],
                "der": None if nodo.derecho is None else ids[id(nodo.derecho)],
            })
            visitar(nodo.derecho, nivel + 1)

        visitar(self._raiz, 0)
        return resultado

    def orden_recorrido(self, tipo):
        """
        Números (ids) de los nodos en el orden de un recorrido: sirve para animarlo.

        Recibe:
            tipo: "inorden", "preorden" o "posorden".
        Devuelve:
            Lista de ids en el orden en que el recorrido visita los nodos.
        Lanza:
            ValueError si el tipo no existe.
        """
        if tipo not in ("inorden", "preorden", "posorden"):
            raise ValueError("Recorrido desconocido: " + str(tipo))
        ids = self._ids_por_nodo()
        orden = []

        def visitar(nodo):
            if nodo is None:
                return
            if tipo == "preorden":
                orden.append(ids[id(nodo)])
            visitar(nodo.izquierdo)
            if tipo == "inorden":
                orden.append(ids[id(nodo)])
            visitar(nodo.derecho)
            if tipo == "posorden":
                orden.append(ids[id(nodo)])

        visitar(self._raiz)
        return orden

    def ids_camino_busqueda(self, clave):
        """
        Ids de los nodos que visita buscar(clave), desde la raíz (para animar la búsqueda).

        Recibe:
            clave: la clave que se busca.
        Devuelve:
            Lista de ids en el orden visitado (termina en el nodo encontrado, o en el último
            nodo visitado si la clave no existe).
        """
        ids = self._ids_por_nodo()
        camino = []
        actual = self._raiz
        while actual is not None:
            camino.append(ids[id(actual)])
            if clave == actual.clave:
                break
            actual = actual.izquierdo if clave < actual.clave else actual.derecho
        return camino

    # ---------------- utilidades ----------------
    def minimo(self):
        """
        Menor clave del árbol.

        Recibe: nada.
        Devuelve:
            Tupla (clave, valor).
        Lanza:
            EstructuraVaciaError si el árbol está vacío.
        """
        if self._raiz is None:
            raise EstructuraVaciaError("El árbol está vacío.")
        actual = self._raiz
        while actual.izquierdo is not None:
            actual = actual.izquierdo
        return actual.clave, actual.valor

    def maximo(self):
        """
        Mayor clave del árbol (el mejor puntaje).

        Recibe: nada.
        Devuelve:
            Tupla (clave, valor).
        Lanza:
            EstructuraVaciaError si el árbol está vacío.
        """
        if self._raiz is None:
            raise EstructuraVaciaError("El árbol está vacío.")
        actual = self._raiz
        while actual.derecho is not None:
            actual = actual.derecho
        return actual.clave, actual.valor

    def altura(self):
        """
        Altura del árbol (vacío = 0, solo raíz = 1).

        Recibe: nada.
        Devuelve:
            Un entero.
        """
        return self._altura(self._raiz)

    def _altura(self, nodo):
        """(Interno) Altura recursiva de un subárbol."""
        if nodo is None:
            return 0
        izq = self._altura(nodo.izquierdo)
        der = self._altura(nodo.derecho)
        return 1 + (izq if izq > der else der)

    def esta_vacio(self):
        """
        Dice si el árbol no tiene nodos.

        Recibe: nada.
        Devuelve:
            True si está vacío, False si no.
        """
        return self._raiz is None

    def tamanio(self):
        """
        Cantidad de nodos.

        Recibe: nada.
        Devuelve:
            Un entero.
        """
        return self._tamanio

    def vaciar(self):
        """Deja el árbol vacío. Recibe: nada. Devuelve: nada."""
        self._raiz = None
        self._tamanio = 0
