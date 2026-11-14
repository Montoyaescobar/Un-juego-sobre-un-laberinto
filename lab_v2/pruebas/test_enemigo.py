"""
test_enemigo.py
Pruebas de los enemigos (usan la Lista Circular). Ejecutar:
    python -m unittest pruebas.test_enemigo -v
"""

import unittest
from juego.enemigo import Enemigo, crear_ruta_patrulla


def casillas(ruta):
    """Ayuda de prueba: una vuelta de la lista circular como lista de Python."""
    salida = []
    ruta.recorrer(salida.append)
    return salida


class TestEnemigo(unittest.TestCase):

    def test_ruta_ida_y_vuelta(self):
        # Esperado: A B C -> A B C B (la vuelta no repite los extremos)
        ruta = crear_ruta_patrulla([(1, 1), (1, 2), (1, 3)])
        self.assertEqual(casillas(ruta), [(1, 1), (1, 2), (1, 3), (1, 2)])

    def test_ruta_de_dos_casillas(self):
        # Esperado: A B
        ruta = crear_ruta_patrulla([(1, 1), (1, 2)])
        self.assertEqual(casillas(ruta), [(1, 1), (1, 2)])

    def test_enemigo_empieza_en_la_primera(self):
        # Esperado: la posición inicial es el inicio de la ruta
        e = Enemigo(crear_ruta_patrulla([(1, 1), (1, 2), (1, 3)]))
        self.assertEqual(e.posicion, (1, 1))

    def test_patrulla_sin_fin(self):
        # Esperado: da la vuelta y vuelve al inicio (propiedad de la lista circular)
        e = Enemigo(crear_ruta_patrulla([(1, 1), (1, 2), (1, 3)]))
        vistas = [e.avanzar() for _ in range(8)]
        self.assertEqual(vistas, [(1, 2), (1, 3), (1, 2), (1, 1),
                                  (1, 2), (1, 3), (1, 2), (1, 1)])

    def test_pasos_siempre_a_casillas_vecinas(self):
        # Esperado: en cada turno el enemigo se mueve exactamente 1 casilla
        e = Enemigo(crear_ruta_patrulla([(1, 1), (1, 2), (1, 3), (2, 3), (3, 3)]))
        anterior = e.posicion
        for _ in range(30):
            nueva = e.avanzar()
            self.assertEqual(abs(nueva[0] - anterior[0]) + abs(nueva[1] - anterior[1]), 1)
            anterior = nueva


if __name__ == "__main__":
    unittest.main()
