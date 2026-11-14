"""
test_formato.py
Pruebas de los textos del panel derecho (sin ventana ni Pygame).
    python -m unittest pruebas.test_formato -v
"""

import unittest

from interfaz.formato import plural, resumir_lista


class TestFormato(unittest.TestCase):

    def test_plural_singular_y_plural(self):
        # Esperado: solo el 1 usa singular ("1 foto", no "1 fotos")
        self.assertEqual(plural(1, "foto", "fotos"), "1 foto")
        self.assertEqual(plural(0, "foto", "fotos"), "0 fotos")
        self.assertEqual(plural(2, "foto", "fotos"), "2 fotos")

    def test_resumir_lista_vacia(self):
        self.assertEqual(resumir_lista([]), "—")

    def test_resumir_lista_corta_no_agrega_resto(self):
        self.assertEqual(resumir_lista([32, 30]), "32, 30")
        self.assertEqual(resumir_lista([32, 30, 28]), "32, 30, 28")

    def test_resumir_lista_larga_cuenta_los_que_faltan(self):
        # Esperado: antes se cortaba como "32, 28, 3…"; ahora dice cuántos faltan
        self.assertEqual(resumir_lista([32, 28, 30, 26, 24]), "32, 28, 30 +2")


if __name__ == "__main__":
    unittest.main()
