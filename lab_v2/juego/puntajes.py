"""
puntajes.py
Tabla de MEJORES PUNTAJES guardada en un ÁRBOL BINARIO DE BÚSQUEDA propio.

Cómo se usa el árbol:
    - clave = puntaje, valor = (nombre, nivel).
    - Ranking (mayor a menor): recorrido INORDEN INVERSO (derecha, nodo, izquierda).
    - Buscar un puntaje: búsqueda binaria en el árbol.
    - Eliminar un puntaje: eliminación del BST (los 3 casos).
    - Para mostrar la forma del árbol se ofrecen inorden, preorden y posorden.
    - Se guarda en un archivo de texto en PREORDEN: al cargarlo e insertar en ese orden,
      el árbol queda con la misma forma que tenía.
"""

import os

from estructuras.arbol_bst import ArbolBST

# El archivo queda junto a main.py
ARCHIVO_POR_DEFECTO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "puntajes.txt")


class TablaPuntajes:
    """Mejores puntajes, ordenados con un BST y guardados en un archivo."""

    def __init__(self, archivo=None):
        """
        Crea la tabla y carga los puntajes guardados (si el archivo existe).

        Recibe:
            archivo: ruta del archivo de texto; si no se da, se usa puntajes.txt junto a main.py.
        Devuelve:
            Nada (constructor).
        """
        self.archivo = archivo or ARCHIVO_POR_DEFECTO
        self._arbol = ArbolBST()
        self.cargar()

    def registrar(self, nombre, nivel, puntaje):
        """
        Agrega un puntaje y guarda el archivo.

        Recibe:
            nombre: texto (no vacío, sin ';').
            nivel: texto con el nombre del nivel (sin ';').
            puntaje: entero mayor o igual a 0.
        Devuelve:
            Nada.
        Lanza:
            ValueError si algún dato no es válido.
        """
        if not isinstance(puntaje, int) or isinstance(puntaje, bool) or puntaje < 0:
            raise ValueError("El puntaje debe ser un entero mayor o igual a 0.")
        for texto in (nombre, nivel):
            if not isinstance(texto, str) or texto.strip() == "" or ";" in texto \
                    or "\n" in texto:
                raise ValueError("Nombre o nivel inválido.")
        self._arbol.insertar(puntaje, (nombre.strip(), nivel.strip()))
        self.guardar()

    def mejores(self, cantidad=10):
        """
        Los mejores puntajes, de mayor a menor (inorden inverso del BST).

        Recibe:
            cantidad: cuántos devolver como máximo.
        Devuelve:
            Lista de tuplas (puntaje, nombre, nivel).
        """
        resultado = []

        def tomar(clave, valor):
            """Función que el recorrido inorden inverso llama por cada nodo: guarda (puntaje, nombre, nivel) hasta llegar a 'cantidad'. Recibe: clave y valor. Devuelve: nada."""
            if len(resultado) < cantidad:
                resultado.append((clave, valor[0], valor[1]))

        self._arbol.inorden_inverso(tomar)
        return resultado

    def buscar(self, puntaje):
        """
        Busca un puntaje exacto en el árbol.

        Recibe:
            puntaje: entero a buscar.
        Devuelve:
            Tupla (nombre, nivel) o None si ese puntaje no existe.
        """
        return self._arbol.buscar(puntaje)

    def eliminar(self, puntaje):
        """
        Elimina un puntaje del árbol y guarda el archivo.

        Recibe:
            puntaje: entero a eliminar.
        Devuelve:
            True si lo eliminó, False si no existía.
        """
        eliminado = self._arbol.eliminar(puntaje)
        if eliminado:
            self.guardar()
        return eliminado

    def mejor(self):
        """
        El mejor puntaje registrado.

        Recibe: nada.
        Devuelve:
            Tupla (puntaje, nombre, nivel) o None si no hay puntajes.
        """
        if self._arbol.esta_vacio():
            return None
        clave, valor = self._arbol.maximo()
        return (clave, valor[0], valor[1])

    def cantidad(self):
        """Cuántos puntajes hay. Recibe: nada. Devuelve: un entero."""
        return self._arbol.tamanio()

    def recorrido(self, tipo):
        """
        Devuelve todos los puntajes en el orden de un recorrido del árbol.

        Recibe:
            tipo: "inorden", "preorden" o "posorden".
        Devuelve:
            Lista de tuplas (puntaje, nombre, nivel).
        Lanza:
            ValueError si el tipo no existe.
        """
        if tipo not in ("inorden", "preorden", "posorden"):
            raise ValueError("Recorrido desconocido: " + str(tipo))
        resultado = []
        self._recorrer(tipo, resultado)
        return resultado

    def _recorrer(self, tipo, resultado):
        """(Interno) Llena 'resultado' con el recorrido pedido del árbol."""
        def agregar(clave, valor):
            """Función que el recorrido del árbol llama por cada nodo: agrega (puntaje, nombre, nivel) a 'resultado'. Recibe: clave y valor. Devuelve: nada."""
            resultado.append((clave, valor[0], valor[1]))

        if tipo == "inorden":
            self._arbol.inorden(agregar)
        elif tipo == "preorden":
            self._arbol.preorden(agregar)
        else:
            self._arbol.posorden(agregar)

    def nodos_para_dibujar(self):
        """
        Los nodos del árbol listos para dibujar (usa ArbolBST.nodos_para_dibujar).

        Recibe: nada.
        Devuelve:
            Lista de diccionarios: id, clave, nombre, nivel, izq, der.
        """
        nodos = self._arbol.nodos_para_dibujar()
        for nodo in nodos:
            nodo["nombre"], nodo["nivel_juego"] = nodo.pop("valor")
        return nodos

    def orden_recorrido(self, tipo):
        """Ids de los nodos en el orden de un recorrido. Recibe: tipo. Devuelve: lista de ids."""
        return self._arbol.orden_recorrido(tipo)

    def ids_camino_busqueda(self, puntaje):
        """Ids visitados al buscar un puntaje. Recibe: puntaje. Devuelve: lista de ids."""
        return self._arbol.ids_camino_busqueda(puntaje)

    def guardar(self):
        """
        Guarda los puntajes en el archivo (en preorden, una línea por puntaje).

        Recibe: nada.
        Devuelve:
            True si se pudo guardar, False si hubo un error de archivo (el juego sigue).
        """
        lineas = []
        for puntaje, nombre, nivel in self.recorrido("preorden"):
            lineas.append("%d;%s;%s" % (puntaje, nivel, nombre))
        try:
            with open(self.archivo, "w", encoding="utf-8") as f:
                f.write("\n".join(lineas) + ("\n" if lineas else ""))
            return True
        except OSError:
            return False

    def cargar(self):
        """
        Lee el archivo y rellena el árbol. Las líneas dañadas se ignoran.

        Recibe: nada.
        Devuelve:
            Nada.
        """
        try:
            with open(self.archivo, "r", encoding="utf-8") as f:
                contenido = f.read()
        except (OSError, UnicodeDecodeError):
            return                               # sin archivo o ilegible: se empieza vacío
        for linea in contenido.splitlines():
            partes = linea.split(";", 2)
            if len(partes) != 3:
                continue
            try:
                puntaje = int(partes[0])
            except ValueError:
                continue
            nivel, nombre = partes[1].strip(), partes[2].strip()
            if puntaje >= 0 and nivel != "" and nombre != "":
                self._arbol.insertar(puntaje, (nombre, nivel))
