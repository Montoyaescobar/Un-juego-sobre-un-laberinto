"""
test_solver.py
Pruebas del BFS (usa la Cola). Ejecutar:
    python -m unittest pruebas.test_solver -v
"""

import unittest
from juego.laberinto import Laberinto
from juego.generador import generar_laberinto
from juego.solver import camino_mas_corto


def son_vecinas(a, b):
    """Ayuda de prueba: dos casillas están pegadas (distancia 1)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1


class TestSolver(unittest.TestCase):

    def test_pasillo(self):
        # Esperado: camino recto de la entrada a la salida
        lab = Laberinto(1, 3)
        for c in range(1, lab.ancho - 1):
            lab.abrir(1, c)
        self.assertEqual(camino_mas_corto(lab, lab.entrada, lab.salida),
                         [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5)])

    def test_origen_igual_destino(self):
        # Esperado: el camino es solo esa casilla
        lab = Laberinto(1, 2)
        lab.abrir(1, 1)
        self.assertEqual(camino_mas_corto(lab, (1, 1), (1, 1)), [(1, 1)])

    def test_sin_camino(self):
        # Esperado: None cuando hay una pared que separa origen y destino
        lab = Laberinto(1, 3)
        lab.abrir(1, 1)
        lab.abrir(1, 5)
        self.assertIsNone(camino_mas_corto(lab, (1, 1), (1, 5)))

    def test_destino_o_origen_en_pared(self):
        # Esperado: None
        lab = Laberinto(1, 2)
        lab.abrir(1, 1)
        self.assertIsNone(camino_mas_corto(lab, (1, 1), (0, 0)))
        self.assertIsNone(camino_mas_corto(lab, (0, 0), (1, 1)))

    def test_es_el_mas_corto_en_zona_abierta(self):
        # Esperado: en un área sin paredes interiores la distancia es la de Manhattan (8 pasos)
        lab = Laberinto(3, 3)
        for f in range(1, lab.alto - 1):
            for c in range(1, lab.ancho - 1):
                lab.abrir(f, c)
        camino = camino_mas_corto(lab, (1, 1), (5, 5))
        self.assertEqual(len(camino) - 1, 8)

    def test_en_laberintos_generados(self):
        # Esperado: empieza en la entrada, termina en la salida, casillas libres y vecinas entre sí
        for semilla in range(15):
            lab = generar_laberinto(10, 10, semilla=semilla)
            camino = camino_mas_corto(lab, lab.entrada, lab.salida)
            self.assertEqual(camino[0], lab.entrada)
            self.assertEqual(camino[-1], lab.salida)
            for i in range(len(camino) - 1):
                self.assertTrue(son_vecinas(camino[i], camino[i + 1]))
                self.assertTrue(lab.es_transitable(*camino[i]))


if __name__ == "__main__":
    unittest.main()
