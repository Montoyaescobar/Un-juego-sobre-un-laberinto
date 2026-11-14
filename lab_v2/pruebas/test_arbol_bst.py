"""
test_arbol_bst.py
Pruebas del Árbol Binario de Búsqueda. Ejecutar:
    python -m unittest pruebas.test_arbol_bst -v
"""

import unittest
from estructuras.arbol_bst import ArbolBST
from estructuras.errores import EstructuraVaciaError


def armar():
    r"""
    Arma el árbol de ejemplo:
              50
            /    \
          30      70
         /  \    /  \
       20   40  60   80
    """
    a = ArbolBST()
    for clave in (50, 30, 70, 20, 40, 60, 80):
        a.insertar(clave, "J" + str(clave))
    return a


def claves(recorrido):
    """Ayuda de prueba: ejecuta un recorrido y devuelve las claves en una lista de Python."""
    salida = []
    recorrido(lambda clave, valor: salida.append(clave))
    return salida


class TestArbolBST(unittest.TestCase):

    def test_arbol_nuevo_vacio(self):
        # Esperado: vacío, tamaño 0, altura 0
        a = ArbolBST()
        self.assertTrue(a.esta_vacio())
        self.assertEqual(a.tamanio(), 0)
        self.assertEqual(a.altura(), 0)

    def test_insertar_y_buscar(self):
        # Esperado: buscar devuelve el valor; una clave ausente devuelve None
        a = armar()
        self.assertEqual(a.tamanio(), 7)
        self.assertEqual(a.buscar(60), "J60")
        self.assertIsNone(a.buscar(99))
        self.assertTrue(a.contiene(20))
        self.assertFalse(a.contiene(21))

    def test_recorridos(self):
        # Esperado: los tres recorridos clásicos del árbol de ejemplo
        a = armar()
        self.assertEqual(claves(a.inorden), [20, 30, 40, 50, 60, 70, 80])
        self.assertEqual(claves(a.preorden), [50, 30, 20, 40, 70, 60, 80])
        self.assertEqual(claves(a.posorden), [20, 40, 30, 60, 80, 70, 50])
        self.assertEqual(claves(a.inorden_inverso), [80, 70, 60, 50, 40, 30, 20])

    def test_minimo_maximo_altura(self):
        # Esperado: mínimo 20, máximo 80, altura 3
        a = armar()
        self.assertEqual(a.minimo(), (20, "J20"))
        self.assertEqual(a.maximo(), (80, "J80"))
        self.assertEqual(a.altura(), 3)

    def test_eliminar_hoja(self):
        # Esperado: caso 1 (sin hijos)
        a = armar()
        self.assertTrue(a.eliminar(20))
        self.assertEqual(claves(a.inorden), [30, 40, 50, 60, 70, 80])
        self.assertEqual(a.tamanio(), 6)

    def test_eliminar_con_un_hijo(self):
        # Esperado: caso 2 (un hijo): el hijo sube
        a = armar()
        a.eliminar(20)
        a.eliminar(30)                         # 30 queda solo con el hijo 40
        self.assertEqual(claves(a.inorden), [40, 50, 60, 70, 80])
        self.assertEqual(claves(a.preorden), [50, 40, 70, 60, 80])

    def test_eliminar_con_dos_hijos(self):
        # Esperado: caso 3 (dos hijos): se reemplaza por el sucesor (60)
        a = armar()
        self.assertTrue(a.eliminar(50))        # la raíz tiene dos hijos
        self.assertEqual(claves(a.inorden), [20, 30, 40, 60, 70, 80])
        self.assertEqual(claves(a.preorden), [60, 30, 20, 40, 70, 80])

    def test_eliminar_clave_inexistente(self):
        # Esperado: False y el tamaño no cambia
        a = armar()
        self.assertFalse(a.eliminar(999))
        self.assertEqual(a.tamanio(), 7)

    def test_eliminar_hasta_vaciar(self):
        # Esperado: el árbol queda vacío
        a = ArbolBST()
        a.insertar(5, "x")
        self.assertTrue(a.eliminar(5))
        self.assertTrue(a.esta_vacio())

    def test_claves_repetidas(self):
        # Esperado: se guardan las dos; al eliminar una, la otra conserva su valor
        a = ArbolBST()
        a.insertar(100, "Ana")
        a.insertar(100, "Beto")
        self.assertEqual(a.tamanio(), 2)
        self.assertEqual(claves(a.inorden), [100, 100])
        a.eliminar(100)
        self.assertEqual(a.tamanio(), 1)
        self.assertEqual(a.buscar(100), "Beto")

    def test_minimo_maximo_vacio(self):
        # Esperado: EstructuraVaciaError
        with self.assertRaises(EstructuraVaciaError):
            ArbolBST().minimo()
        with self.assertRaises(EstructuraVaciaError):
            ArbolBST().maximo()

    def test_vaciar(self):
        # Esperado: queda vacío
        a = armar()
        a.vaciar()
        self.assertTrue(a.esta_vacio())
        self.assertEqual(a.tamanio(), 0)

    def test_nodos_para_dibujar(self):
        # Esperado: ids en inorden (0..6), niveles correctos y enlaces a los hijos
        nodos = armar().nodos_para_dibujar()
        self.assertEqual([n["clave"] for n in nodos], [20, 30, 40, 50, 60, 70, 80])
        self.assertEqual([n["id"] for n in nodos], [0, 1, 2, 3, 4, 5, 6])
        self.assertEqual([n["nivel"] for n in nodos], [2, 1, 2, 0, 2, 1, 2])
        raiz = nodos[3]
        self.assertEqual((raiz["izq"], raiz["der"]), (1, 5))
        self.assertEqual(nodos[0]["izq"], None)
        self.assertEqual(ArbolBST().nodos_para_dibujar(), [])

    def test_orden_recorrido_en_ids(self):
        # Esperado: coincide con los recorridos de siempre (ids: 20=0,30=1,40=2,50=3,60=4,70=5,80=6)
        a = armar()
        self.assertEqual(a.orden_recorrido("inorden"), [0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(a.orden_recorrido("preorden"), [3, 1, 0, 2, 5, 4, 6])
        self.assertEqual(a.orden_recorrido("posorden"), [0, 2, 1, 4, 6, 5, 3])
        with self.assertRaises(ValueError):
            a.orden_recorrido("raro")

    def test_camino_de_busqueda(self):
        # Esperado: raíz -> ... -> nodo; si no existe, termina donde se cortó
        a = armar()
        self.assertEqual(a.ids_camino_busqueda(40), [3, 1, 2])
        self.assertEqual(a.ids_camino_busqueda(50), [3])
        self.assertEqual(a.ids_camino_busqueda(65), [3, 5, 4])
        self.assertEqual(ArbolBST().ids_camino_busqueda(1), [])


if __name__ == "__main__":
    unittest.main()
