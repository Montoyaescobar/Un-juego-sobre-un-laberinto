"""
test_partida.py
Pruebas de la partida completa (laberinto + jugador + enemigos + historial).
Ejecutar:  python -m unittest pruebas.test_partida -v
"""

import unittest
from juego.partida import (Partida, NIVELES, JUGANDO, GANO, SIN_MOVIMIENTOS, ATRAPADO)
from juego.solver import camino_mas_corto
from juego.enemigo import Enemigo, crear_ruta_patrulla

NIVEL_CHICO = {"nombre": "Prueba", "filas": 4, "columnas": 4, "factor": 3.0,
               "enemigos": 0, "base": 100}


def direccion(desde, hasta):
    """Ayuda de prueba: nombre de la dirección para ir de una casilla a su vecina."""
    df, dc = hasta[0] - desde[0], hasta[1] - desde[1]
    return {(-1, 0): "arriba", (1, 0): "abajo", (0, -1): "izquierda", (0, 1): "derecha"}[(df, dc)]


def jugar_camino_optimo(partida):
    """Ayuda de prueba: juega el camino más corto completo. Devuelve True si cada paso fue válido."""
    camino = camino_mas_corto(partida.laberinto, partida.jugador.posicion,
                              partida.laberinto.salida)
    for i in range(len(camino) - 1):
        if not partida.mover(direccion(camino[i], camino[i + 1])):
            return False
    return True


class TestPartida(unittest.TestCase):

    def test_estado_inicial(self):
        # Esperado: jugando, 1 foto en el historial, límite = óptimo*factor + 10
        p = Partida(NIVEL_CHICO, semilla=1)
        optimo = len(p.solucion) - 1
        self.assertEqual(p.estado, JUGANDO)
        self.assertEqual(p.historial.total(), 1)
        self.assertEqual(p.jugador.max_movimientos, int(optimo * 3.0) + 10)

    def test_misma_semilla_misma_partida(self):
        # Esperado: reproducible (laberinto y enemigos)
        a = Partida(NIVELES["2"], semilla=7)
        b = Partida(NIVELES["2"], semilla=7)
        self.assertEqual(a.laberinto.matriz, b.laberinto.matriz)
        self.assertEqual(a.posiciones_enemigos(), b.posiciones_enemigos())

    def test_cantidad_de_enemigos(self):
        # Esperado: cada nivel pone los enemigos que pide
        for nivel in NIVELES.values():
            p = Partida(nivel, semilla=3)
            self.assertEqual(len(p.enemigos), nivel["enemigos"])

    def test_rutas_no_tocan_el_camino_a_la_salida(self):
        # Esperado: siempre se puede ganar sin cruzarse con un enemigo
        for semilla in range(25):
            for nivel in NIVELES.values():
                p = Partida(nivel, semilla=semilla)
                prohibidas = set(p.solucion)
                for enemigo in p.enemigos:
                    ruta = []
                    enemigo.ruta.recorrer(ruta.append)
                    for casilla in ruta:
                        self.assertNotIn(casilla, prohibidas)
                        self.assertTrue(p.laberinto.es_transitable(*casilla))

    def test_ganar_por_el_camino_optimo(self):
        # Esperado: en todos los niveles y varias semillas se gana, sin que un enemigo atrape
        for semilla in range(15):
            for nivel in NIVELES.values():
                p = Partida(nivel, semilla=semilla)
                self.assertTrue(jugar_camino_optimo(p))
                self.assertEqual(p.estado, GANO)

    def test_puntaje(self):
        # Esperado: base + 10 por movimiento sobrante; 0 si no se ganó
        p = Partida(NIVEL_CHICO, semilla=2)
        self.assertEqual(p.puntaje(), 0)
        jugar_camino_optimo(p)
        esperado = 100 + p.jugador.movimientos_restantes() * 10
        self.assertEqual(p.puntaje(), esperado)

    def test_historial_guarda_cada_accion(self):
        # Esperado: 1 foto inicial + 1 por cada movimiento
        p = Partida(NIVEL_CHICO, semilla=2)
        jugar_camino_optimo(p)
        self.assertEqual(p.historial.total(), len(p.solucion))   # (pasos) + inicial
        p.historial.ir_al_final()
        self.assertEqual(p.historial.actual()[0], p.laberinto.salida)

    def test_pared_no_cambia_nada(self):
        # Esperado: chocar con pared no mueve a los enemigos ni agrega fotos
        p = Partida(NIVELES["1"], semilla=4)
        antes = p.posiciones_enemigos()
        for d in ("arriba", "izquierda"):         # desde (1,1) siempre hay pared arriba y a la izquierda
            self.assertFalse(p.mover(d))
        self.assertEqual(p.posiciones_enemigos(), antes)
        self.assertEqual(p.historial.total(), 1)

    def test_deshacer_mueve_enemigos_y_registra(self):
        # Esperado: deshacer cuenta como acción: enemigos avanzan y hay nueva foto
        p = Partida(NIVELES["1"], semilla=4)
        p.mover(direccion(p.solucion[0], p.solucion[1]))
        antes = p.posiciones_enemigos()
        self.assertTrue(p.deshacer())
        self.assertNotEqual(p.posiciones_enemigos(), antes)
        self.assertEqual(p.historial.total(), 3)

    def test_enemigo_camina_hacia_el_jugador(self):
        # Esperado: el enemigo llega a la casilla del jugador -> ATRAPADO
        p = Partida(NIVEL_CHICO, semilla=5)
        a, b, c = p.solucion[2], p.solucion[1], p.solucion[0]
        p.enemigos = [Enemigo(crear_ruta_patrulla([a, b]))]   # empieza en a, su próximo paso es b
        p.mover(direccion(c, b))                              # el jugador va a b
        self.assertEqual(p.estado, ATRAPADO)

    def test_jugador_camina_hacia_el_enemigo(self):
        # Esperado: el jugador entra a la casilla de un enemigo -> ATRAPADO
        p = Partida(NIVEL_CHICO, semilla=5)
        b, c = p.solucion[1], p.solucion[0]
        p.enemigos = [Enemigo(crear_ruta_patrulla([b, p.solucion[2]]))]   # enemigo parado en b
        p.mover(direccion(c, b))
        self.assertEqual(p.estado, ATRAPADO)
        self.assertFalse(p.mover("derecha"))        # ya no se puede seguir jugando

    def test_perder_por_movimientos(self):
        # Esperado: al gastar todos los movimientos sin llegar -> SIN_MOVIMIENTOS
        p = Partida(NIVEL_CHICO, semilla=6)
        p.jugador.max_movimientos = 2
        p.enemigos = []
        p.mover(direccion(p.solucion[0], p.solucion[1]))
        p.deshacer()
        self.assertEqual(p.estado, SIN_MOVIMIENTOS)

    def test_pista(self):
        # Esperado: da el camino desde donde está hasta la salida y cuesta 5 movimientos
        p = Partida(NIVEL_CHICO, semilla=2)
        self.assertTrue(p.pista())
        self.assertEqual(p.pista_actual[0], p.jugador.posicion)
        self.assertEqual(p.pista_actual[-1], p.laberinto.salida)
        self.assertEqual(p.jugador.movimientos, 5)
        self.assertEqual(p.jugador.pistas_usadas, 1)

    def test_pista_se_borra_al_mover(self):
        # Esperado: después de moverse la pista vieja desaparece del dibujo
        p = Partida(NIVEL_CHICO, semilla=2)
        p.pista()
        p.mover(direccion(p.solucion[0], p.solucion[1]))
        self.assertIsNone(p.pista_actual)

    def test_pista_sin_movimientos_suficientes(self):
        # Esperado: no se da y no se cobra
        p = Partida(NIVEL_CHICO, semilla=2)
        p.jugador.max_movimientos = 5
        self.assertFalse(p.pista())
        self.assertEqual(p.jugador.movimientos, 0)

    def test_dibujo_tiene_los_simbolos(self):
        # Esperado: J, E y S aparecen en el dibujo
        p = Partida(NIVELES["1"], semilla=8)
        texto = p.dibujar()
        self.assertIn("J ", texto)
        self.assertIn("E ", texto)
        self.assertIn("S ", texto)


if __name__ == "__main__":
    unittest.main()
