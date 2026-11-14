"""
test_lista_circular.py
Pruebas de la Lista Circular. Ejecutar:
    python -m unittest pruebas.test_lista_circular -v
"""

import unittest
from estructuras.lista_circular import ListaCircular
from estructuras.errores import EstructuraVaciaError, PosicionInvalidaError


def contenido(lista):
    """Ayuda de prueba: junta los datos de una vuelta en una lista de Python para comparar."""
    salida = []
    lista.recorrer(salida.append)
    return salida


class TestListaCircular(unittest.TestCase):

    def test_nueva_esta_vacia(self):
        # Esperado: vacía, tamaño 0, buscar devuelve -1
        l = ListaCircular()
        self.assertTrue(l.esta_vacia())
        self.assertEqual(l.tamanio(), 0)
        self.assertEqual(l.buscar(1), -1)

    def test_insertar_inicio_y_final(self):
        # Esperado: orden 0, 1, 2, 3 después de insertar así
        l = ListaCircular()
        l.insertar_final(2)
        l.insertar_inicio(1)
        l.insertar_final(3)
        l.insertar_inicio(0)
        self.assertEqual(contenido(l), [0, 1, 2, 3])
        self.assertEqual(l.tamanio(), 4)

    def test_insertar_posicion(self):
        # Esperado: se inserta en el inicio, en medio y al final
        l = ListaCircular()
        l.insertar_posicion(0, "A")
        l.insertar_posicion(1, "C")
        l.insertar_posicion(1, "B")
        l.insertar_posicion(3, "D")
        self.assertEqual(contenido(l), ["A", "B", "C", "D"])

    def test_insertar_posicion_invalida(self):
        # Esperado: PosicionInvalidaError
        l = ListaCircular()
        with self.assertRaises(PosicionInvalidaError):
            l.insertar_posicion(1, "x")
        with self.assertRaises(PosicionInvalidaError):
            l.insertar_posicion(-1, "x")

    def test_es_circular(self):
        # Esperado: avanzar() da la vuelta: A, B, C, A, B...
        l = ListaCircular()
        for x in ("A", "B", "C"):
            l.insertar_final(x)
        vistos = [l.avanzar() for _ in range(5)]
        self.assertEqual(vistos, ["A", "B", "C", "A", "B"])

    def test_eliminar_posicion_inicio_medio_final(self):
        # Esperado: se elimina bien en cada caso y se devuelve el dato
        l = ListaCircular()
        for x in (1, 2, 3, 4, 5):
            l.insertar_final(x)
        self.assertEqual(l.eliminar_posicion(0), 1)
        self.assertEqual(l.eliminar_posicion(1), 3)
        self.assertEqual(l.eliminar_posicion(2), 5)
        self.assertEqual(contenido(l), [2, 4])

    def test_eliminar_el_ultimo_mantiene_circularidad(self):
        # Esperado: tras borrar el último, insertar al final y dar vuelta sigue bien
        l = ListaCircular()
        for x in (1, 2, 3):
            l.insertar_final(x)
        l.eliminar_posicion(2)
        l.insertar_final(9)
        self.assertEqual(contenido(l), [1, 2, 9])
        vistos = [l.avanzar() for _ in range(4)]
        self.assertEqual(vistos, [1, 2, 9, 1])

    def test_eliminar_unico_elemento(self):
        # Esperado: queda vacía
        l = ListaCircular()
        l.insertar_final(7)
        self.assertEqual(l.eliminar_posicion(0), 7)
        self.assertTrue(l.esta_vacia())

    def test_eliminar_vacia_o_invalida(self):
        # Esperado: errores claros
        l = ListaCircular()
        with self.assertRaises(EstructuraVaciaError):
            l.eliminar_posicion(0)
        l.insertar_final(1)
        with self.assertRaises(PosicionInvalidaError):
            l.eliminar_posicion(5)

    def test_eliminar_dato(self):
        # Esperado: True si existía, False si no
        l = ListaCircular()
        for x in ("a", "b", "c"):
            l.insertar_final(x)
        self.assertTrue(l.eliminar_dato("b"))
        self.assertFalse(l.eliminar_dato("z"))
        self.assertEqual(contenido(l), ["a", "c"])

    def test_buscar(self):
        # Esperado: devuelve la posición o -1
        l = ListaCircular()
        for x in (10, 20, 30):
            l.insertar_final(x)
        self.assertEqual(l.buscar(20), 1)
        self.assertEqual(l.buscar(99), -1)

    def test_avanzar_vacia_lanza_error(self):
        # Esperado: EstructuraVaciaError
        with self.assertRaises(EstructuraVaciaError):
            ListaCircular().avanzar()


if __name__ == "__main__":
    unittest.main()
