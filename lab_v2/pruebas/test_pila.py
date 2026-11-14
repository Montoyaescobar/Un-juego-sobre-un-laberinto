"""
test_pila.py
Pruebas de la Pila. Se ejecutan desde la carpeta laberinto/ con:
    python -m unittest pruebas.test_pila -v

Cada prueba indica: qué se prueba, resultado esperado y (al correrla) el obtenido.
Sirven para la sección "Pruebas realizadas" del manual técnico.
"""

import unittest
from estructuras.pila import Pila
from estructuras.errores import EstructuraVaciaError


class TestPila(unittest.TestCase):

    def test_pila_nueva_esta_vacia(self):
        # Esperado: una pila recién creada está vacía y su tamaño es 0
        p = Pila()
        self.assertTrue(p.esta_vacia())
        self.assertEqual(p.tamanio(), 0)

    def test_apilar_aumenta_tamanio_y_cambia_tope(self):
        # Esperado: tras apilar 1 y 2, el tope es 2 y el tamaño es 2
        p = Pila()
        p.apilar(1)
        p.apilar(2)
        self.assertEqual(p.ver_tope(), 2)
        self.assertEqual(p.tamanio(), 2)
        self.assertFalse(p.esta_vacia())

    def test_orden_lifo(self):
        # Esperado: sale primero el último que entró (3, 2, 1)
        p = Pila()
        for x in (1, 2, 3):
            p.apilar(x)
        self.assertEqual(p.desapilar(), 3)
        self.assertEqual(p.desapilar(), 2)
        self.assertEqual(p.desapilar(), 1)
        self.assertTrue(p.esta_vacia())

    def test_ver_tope_no_quita(self):
        # Esperado: ver_tope no modifica el tamaño
        p = Pila()
        p.apilar("a")
        p.ver_tope()
        self.assertEqual(p.tamanio(), 1)

    def test_desapilar_pila_vacia_lanza_error(self):
        # Esperado: EstructuraVaciaError (el juego lo atrapa y no se cierra)
        with self.assertRaises(EstructuraVaciaError):
            Pila().desapilar()

    def test_ver_tope_pila_vacia_lanza_error(self):
        # Esperado: EstructuraVaciaError
        with self.assertRaises(EstructuraVaciaError):
            Pila().ver_tope()

    def test_guarda_tuplas(self):
        # Esperado: sirve para guardar posiciones (fila, columna) del laberinto
        p = Pila()
        p.apilar((2, 3))
        self.assertEqual(p.desapilar(), (2, 3))

    def test_vaciar(self):
        # Esperado: después de vaciar, está vacía y con tamaño 0
        p = Pila()
        p.apilar(1)
        p.apilar(2)
        p.vaciar()
        self.assertTrue(p.esta_vacia())
        self.assertEqual(p.tamanio(), 0)


if __name__ == "__main__":
    unittest.main()
