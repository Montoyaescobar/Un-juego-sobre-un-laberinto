"""
test_lista_doble.py
Pruebas de la Lista Doblemente Enlazada. Ejecutar:
    python -m unittest pruebas.test_lista_doble -v
"""

import unittest
from estructuras.lista_doble import ListaDoble
from estructuras.errores import EstructuraVaciaError, PosicionInvalidaError


def adelante(lista):
    """Ayuda de prueba: datos de cabeza a cola en una lista de Python."""
    salida = []
    lista.recorrer_adelante(salida.append)
    return salida


def atras(lista):
    """Ayuda de prueba: datos de cola a cabeza en una lista de Python."""
    salida = []
    lista.recorrer_atras(salida.append)
    return salida


class TestListaDoble(unittest.TestCase):

    def test_nueva_esta_vacia(self):
        # Esperado: vacía y tamaño 0
        l = ListaDoble()
        self.assertTrue(l.esta_vacia())
        self.assertEqual(l.tamanio(), 0)

    def test_insertar_inicio_y_final(self):
        # Esperado: 0, 1, 2, 3 hacia adelante y 3, 2, 1, 0 hacia atrás
        l = ListaDoble()
        l.insertar_final(2)
        l.insertar_inicio(1)
        l.insertar_final(3)
        l.insertar_inicio(0)
        self.assertEqual(adelante(l), [0, 1, 2, 3])
        self.assertEqual(atras(l), [3, 2, 1, 0])

    def test_insertar_posicion(self):
        # Esperado: inicio, medio (cerca de cada extremo) y final
        l = ListaDoble()
        l.insertar_posicion(0, "A")
        l.insertar_posicion(1, "E")
        l.insertar_posicion(1, "B")
        l.insertar_posicion(2, "C")
        l.insertar_posicion(3, "D")
        self.assertEqual(adelante(l), ["A", "B", "C", "D", "E"])
        self.assertEqual(atras(l), ["E", "D", "C", "B", "A"])

    def test_insertar_posicion_invalida(self):
        # Esperado: PosicionInvalidaError
        l = ListaDoble()
        with self.assertRaises(PosicionInvalidaError):
            l.insertar_posicion(3, "x")

    def test_eliminar_inicio_medio_final(self):
        # Esperado: se enlazan bien ambos sentidos tras cada eliminación
        l = ListaDoble()
        for x in (1, 2, 3, 4, 5):
            l.insertar_final(x)
        self.assertEqual(l.eliminar_posicion(0), 1)
        self.assertEqual(l.eliminar_posicion(2), 4)
        self.assertEqual(l.eliminar_posicion(2), 5)
        self.assertEqual(adelante(l), [2, 3])
        self.assertEqual(atras(l), [3, 2])

    def test_eliminar_unico(self):
        # Esperado: queda vacía
        l = ListaDoble()
        l.insertar_final(1)
        l.eliminar_posicion(0)
        self.assertTrue(l.esta_vacia())

    def test_eliminar_errores(self):
        # Esperado: vacía -> EstructuraVaciaError; posición mala -> PosicionInvalidaError
        l = ListaDoble()
        with self.assertRaises(EstructuraVaciaError):
            l.eliminar_posicion(0)
        l.insertar_final(1)
        with self.assertRaises(PosicionInvalidaError):
            l.eliminar_posicion(1)

    def test_eliminar_dato_y_buscar(self):
        # Esperado: buscar da la posición; eliminar_dato True/False
        l = ListaDoble()
        for x in ("a", "b", "c"):
            l.insertar_final(x)
        self.assertEqual(l.buscar("c"), 2)
        self.assertEqual(l.buscar("z"), -1)
        self.assertTrue(l.eliminar_dato("b"))
        self.assertFalse(l.eliminar_dato("b"))
        self.assertEqual(adelante(l), ["a", "c"])

    def test_navegar_con_cursor(self):
        # Esperado: el cursor va adelante y atrás y se detiene en los extremos
        l = ListaDoble()
        for x in (1, 2, 3):
            l.insertar_final(x)
        self.assertEqual(l.ver_actual(), 1)
        self.assertFalse(l.atras())            # ya está en el primero
        self.assertTrue(l.adelante())
        self.assertTrue(l.adelante())
        self.assertEqual(l.ver_actual(), 3)
        self.assertFalse(l.adelante())         # ya está en el último
        self.assertTrue(l.atras())
        self.assertEqual(l.ver_actual(), 2)
        l.ir_al_final()
        self.assertEqual(l.ver_actual(), 3)
        l.ir_al_inicio()
        self.assertEqual(l.ver_actual(), 1)

    def test_borrar_nodo_del_cursor(self):
        # Esperado: el cursor se mueve a un vecino válido
        l = ListaDoble()
        for x in (1, 2, 3):
            l.insertar_final(x)
        l.adelante()                           # cursor en 2
        l.eliminar_posicion(1)
        self.assertEqual(l.ver_actual(), 3)

    def test_ver_actual_vacia(self):
        # Esperado: EstructuraVaciaError
        with self.assertRaises(EstructuraVaciaError):
            ListaDoble().ver_actual()

    def test_recorrer_hasta_actual(self):
        # Esperado: va de la cabeza hasta el cursor, inclusive
        l = ListaDoble()
        for x in (1, 2, 3, 4):
            l.insertar_final(x)
        vistos = []
        l.recorrer_hasta_actual(vistos.append)
        self.assertEqual(vistos, [1])
        l.adelante()
        l.adelante()
        vistos = []
        l.recorrer_hasta_actual(vistos.append)
        self.assertEqual(vistos, [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
