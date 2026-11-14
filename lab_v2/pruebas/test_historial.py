"""
test_historial.py
Pruebas del historial / repetición (usa la Lista Doble). Ejecutar:
    python -m unittest pruebas.test_historial -v
"""

import unittest
from juego.historial import Historial
from estructuras.errores import EstructuraVaciaError


def armar():
    """Historial de ejemplo con 3 fotos."""
    h = Historial()
    h.registrar((1, 1), ((5, 5),), 0)
    h.registrar((1, 2), ((5, 6),), 1)
    h.registrar((1, 3), ((5, 7),), 2)
    return h


class TestHistorial(unittest.TestCase):

    def test_vacio(self):
        # Esperado: total 0 y pedir la foto actual da error controlado
        h = Historial()
        self.assertEqual(h.total(), 0)
        with self.assertRaises(EstructuraVaciaError):
            h.actual()

    def test_registrar_y_total(self):
        # Esperado: 3 fotos, el cursor queda en la primera
        h = armar()
        self.assertEqual(h.total(), 3)
        self.assertEqual(h.indice(), 0)
        self.assertEqual(h.actual(), ((1, 1), ((5, 5),), 0))

    def test_adelante_y_atras(self):
        # Esperado: se puede ir y volver, y se detiene en los extremos
        h = armar()
        self.assertFalse(h.atras())
        self.assertTrue(h.adelante())
        self.assertTrue(h.adelante())
        self.assertEqual(h.actual()[0], (1, 3))
        self.assertEqual(h.indice(), 2)
        self.assertFalse(h.adelante())
        self.assertTrue(h.atras())
        self.assertEqual(h.actual()[0], (1, 2))
        self.assertEqual(h.indice(), 1)

    def test_inicio_y_final(self):
        # Esperado: saltar a los extremos
        h = armar()
        h.ir_al_final()
        self.assertEqual(h.actual()[0], (1, 3))
        self.assertEqual(h.indice(), 2)
        h.ir_al_inicio()
        self.assertEqual(h.actual()[0], (1, 1))
        self.assertEqual(h.indice(), 0)

    def test_recorrer_hasta_actual(self):
        # Esperado: las fotos desde el inicio hasta el cursor
        h = armar()
        h.adelante()
        posiciones = []
        h.recorrer_hasta_actual(lambda foto: posiciones.append(foto[0]))
        self.assertEqual(posiciones, [(1, 1), (1, 2)])


if __name__ == "__main__":
    unittest.main()
