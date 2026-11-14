"""
test_jugador.py
Pruebas del jugador (movimiento, deshacer con Pila, ganar y perder). Ejecutar:
    python -m unittest pruebas.test_jugador -v
"""

import unittest
from juego.laberinto import Laberinto
from juego.jugador import Jugador


def laberinto_pasillo(columnas=2):
    """
    Laberinto de prueba hecho a mano: un pasillo recto de la entrada a la salida.

    Recibe:
        columnas: celdas de ancho (más columnas = pasillo más largo).
    Devuelve:
        Un Laberinto de 1 fila con todo el pasillo abierto (entrada (1,1), salida al final).
    """
    lab = Laberinto(1, columnas)
    for c in range(1, lab.ancho - 1):
        lab.abrir(1, c)
    return lab


class TestJugador(unittest.TestCase):

    def test_empieza_en_la_entrada(self):
        # Esperado: posición = entrada, 0 movimientos
        lab = laberinto_pasillo()
        j = Jugador(lab, 10)
        self.assertEqual(j.posicion, lab.entrada)
        self.assertEqual(j.movimientos, 0)

    def test_mover_a_camino_libre(self):
        # Esperado: se mueve y cuenta 1 movimiento
        j = Jugador(laberinto_pasillo(), 10)
        self.assertTrue(j.mover("derecha"))
        self.assertEqual(j.posicion, (1, 2))
        self.assertEqual(j.movimientos, 1)

    def test_pared_no_mueve_ni_cuesta(self):
        # Esperado: False, la posición y los movimientos no cambian
        j = Jugador(laberinto_pasillo(), 10)
        self.assertFalse(j.mover("arriba"))
        self.assertFalse(j.mover("izquierda"))
        self.assertEqual(j.posicion, (1, 1))
        self.assertEqual(j.movimientos, 0)

    def test_direccion_invalida(self):
        # Esperado: ValueError
        with self.assertRaises(ValueError):
            Jugador(laberinto_pasillo(), 10).mover("diagonal")

    def test_deshacer_vuelve_atras_y_cuesta(self):
        # Esperado: vuelve a la casilla anterior y cuenta como movimiento
        j = Jugador(laberinto_pasillo(), 10)
        j.mover("derecha")
        self.assertEqual(j.pasos_por_deshacer(), 1)
        self.assertTrue(j.deshacer())
        self.assertEqual(j.posicion, (1, 1))
        self.assertEqual(j.movimientos, 2)
        self.assertEqual(j.pasos_por_deshacer(), 0)

    def test_deshacer_es_lifo(self):
        # Esperado: se deshace primero el ÚLTIMO movimiento
        j = Jugador(laberinto_pasillo(4), 10)
        j.mover("derecha")
        j.mover("derecha")
        j.deshacer()
        self.assertEqual(j.posicion, (1, 2))
        j.deshacer()
        self.assertEqual(j.posicion, (1, 1))

    def test_deshacer_sin_pasos(self):
        # Esperado: False y no cambia nada
        j = Jugador(laberinto_pasillo(), 10)
        self.assertFalse(j.deshacer())
        self.assertEqual(j.movimientos, 0)

    def test_ganar(self):
        # Esperado: al llegar a la salida gano() es True y la partida termina
        j = Jugador(laberinto_pasillo(), 10)
        j.mover("derecha")
        j.mover("derecha")
        self.assertTrue(j.gano())
        self.assertTrue(j.partida_terminada())
        self.assertFalse(j.perdio())

    def test_perder_por_movimientos(self):
        # Esperado: con 2 movimientos de límite y sin llegar, pierde y ya no se puede mover
        j = Jugador(laberinto_pasillo(), 2)
        j.mover("derecha")
        j.deshacer()
        self.assertTrue(j.perdio())
        self.assertFalse(j.mover("derecha"))
        self.assertFalse(j.deshacer())
        self.assertEqual(j.movimientos_restantes(), 0)

    def test_ganar_en_el_ultimo_movimiento(self):
        # Esperado: si llega justo con el último movimiento, GANA (no pierde)
        j = Jugador(laberinto_pasillo(), 2)
        j.mover("derecha")
        j.mover("derecha")
        self.assertTrue(j.gano())
        self.assertFalse(j.perdio())


if __name__ == "__main__":
    unittest.main()
