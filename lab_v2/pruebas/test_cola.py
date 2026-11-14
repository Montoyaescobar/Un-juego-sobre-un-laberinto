"""
test_cola.py
Pruebas de la Cola. Ejecutar desde la carpeta del proyecto:
    python -m unittest pruebas.test_cola -v
"""

import unittest
from estructuras.cola import Cola
from estructuras.errores import EstructuraVaciaError


class TestCola(unittest.TestCase):

    def test_cola_nueva_esta_vacia(self):
        # Esperado: vacía y tamaño 0
        c = Cola()
        self.assertTrue(c.esta_vacia())
        self.assertEqual(c.tamanio(), 0)

    def test_orden_fifo(self):
        # Esperado: sale primero el primero que entró (1, 2, 3)
        c = Cola()
        for x in (1, 2, 3):
            c.encolar(x)
        self.assertEqual(c.desencolar(), 1)
        self.assertEqual(c.desencolar(), 2)
        self.assertEqual(c.desencolar(), 3)
        self.assertTrue(c.esta_vacia())

    def test_ver_frente_no_quita(self):
        # Esperado: el frente es el primero y el tamaño no cambia
        c = Cola()
        c.encolar("a")
        c.encolar("b")
        self.assertEqual(c.ver_frente(), "a")
        self.assertEqual(c.tamanio(), 2)

    def test_encolar_despues_de_vaciar(self):
        # Esperado: la cola sigue funcionando después de quedar vacía (se limpia el final)
        c = Cola()
        c.encolar(1)
        c.desencolar()
        c.encolar(2)
        c.encolar(3)
        self.assertEqual(c.desencolar(), 2)
        self.assertEqual(c.desencolar(), 3)

    def test_desencolar_vacia_lanza_error(self):
        # Esperado: EstructuraVaciaError
        with self.assertRaises(EstructuraVaciaError):
            Cola().desencolar()

    def test_ver_frente_vacia_lanza_error(self):
        # Esperado: EstructuraVaciaError
        with self.assertRaises(EstructuraVaciaError):
            Cola().ver_frente()

    def test_guarda_tuplas(self):
        # Esperado: sirve para posiciones del BFS
        c = Cola()
        c.encolar((1, 1))
        self.assertEqual(c.desencolar(), (1, 1))

    def test_vaciar(self):
        # Esperado: queda vacía
        c = Cola()
        c.encolar(1)
        c.vaciar()
        self.assertTrue(c.esta_vacia())
        self.assertEqual(c.tamanio(), 0)


if __name__ == "__main__":
    unittest.main()
