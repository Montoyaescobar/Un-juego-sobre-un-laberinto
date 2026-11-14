"""
test_radar.py
Pruebas del RADAR (usa la Cola propia): el punto rojo que persigue por el camino más corto.
Se ejecutan sin ventana. Ejecutar:
    python -m unittest pruebas.test_radar -v
"""

import unittest

from estructuras.cola import Cola
from juego.jugador import Jugador
from juego.laberinto import Laberinto
from juego.partida import Partida, NIVELES, JUGANDO, GANO, SIN_MOVIMIENTOS
from juego.radar import Radar, casilla_lejana, PENALIZACION_RADAR, ESPERA_RADAR
from juego.solver import camino_mas_corto

NIVEL_RADAR = {"nombre": "Prueba", "filas": 4, "columnas": 4, "factor": 3.0,
               "enemigos": 0, "base": 100, "radar": 2}


def pasillo(columnas_celdas=3):
    """Ayuda de prueba: laberinto de una sola fila, todo abierto de entrada a salida."""
    lab = Laberinto(1, columnas_celdas)
    for c in range(1, lab.ancho - 1):
        lab.abrir(1, c)
    return lab


class TestRadar(unittest.TestCase):

    def test_parametros_invalidos(self):
        # Esperado: ValueError con "cada" que no es entero >= 1 o espera que no es entero >= 0
        lab = pasillo()
        for malo in (0, -1, "2", 1.5, None, True):
            with self.assertRaises(ValueError):
                Radar(lab, (1, 5), malo)
        for malo in (-1, "2", 1.5, None, True):
            with self.assertRaises(ValueError):
                Radar(lab, (1, 5), 1, malo)

    def test_radar_nuevo_esta_dormido(self):
        # Esperado: inactivo, sin ruta pendiente y no toca aunque coincida la casilla
        r = Radar(pasillo(), (1, 5), 1)
        self.assertFalse(r.activo)
        self.assertEqual(r.pasos_pendientes(), 0)
        self.assertFalse(r.toca((1, 5)))

    def test_duerme_durante_la_espera(self):
        # Esperado: durante "espera" turnos no se mueve ni despierta; luego sí
        r = Radar(pasillo(), (1, 5), 1, espera=3)
        for _ in range(3):
            self.assertFalse(r.turno((1, 1)))
            self.assertFalse(r.activo)
            self.assertEqual(r.posicion, (1, 5))
        self.assertTrue(r.turno((1, 1)))
        self.assertTrue(r.activo)
        self.assertEqual(r.posicion, (1, 4))

    def test_se_acerca_por_el_camino_mas_corto(self):
        # Esperado: en un pasillo avanza una casilla por turno hacia el jugador (cada=1)
        r = Radar(pasillo(), (1, 5), 1, espera=0)
        r.turno((1, 1))
        self.assertEqual(r.posicion, (1, 4))
        r.turno((1, 1))
        self.assertEqual(r.posicion, (1, 3))
        self.assertEqual(r.pasos_pendientes(), 2)    # le faltan (1, 2) y (1, 1) hasta el jugador

    def test_se_mueve_una_vez_cada_n_turnos(self):
        # Esperado: con cada=3 da un paso en 1 de cada 3 turnos
        r = Radar(pasillo(), (1, 5), 3, espera=0)
        movimientos = [r.turno((1, 1)) for _ in range(6)]
        self.assertEqual(movimientos, [True, False, False, True, False, False])

    def test_toca_y_reiniciar(self):
        # Esperado: al llegar a la casilla del jugador lo toca; reiniciar lo duerme en el origen
        r = Radar(pasillo(), (1, 2), 1, espera=0)
        r.turno((1, 1))
        self.assertTrue(r.toca((1, 1)))
        r.reiniciar()
        self.assertEqual(r.contactos, 1)
        self.assertEqual(r.posicion, (1, 2))
        self.assertFalse(r.activo)
        self.assertFalse(r.toca((1, 2)))

    def test_ya_encima_no_se_mueve(self):
        # Esperado: si el radar ya está en la casilla del jugador, no da ningún paso
        r = Radar(pasillo(), (1, 1), 1, espera=0)
        self.assertFalse(r.turno((1, 1)))

    def test_casilla_lejana_en_pasillo(self):
        # Esperado: la más lejana de la entrada es el otro extremo
        lab = pasillo()
        self.assertEqual(casilla_lejana(lab, lab.entrada), (1, 5))

    def test_casilla_lejana_evita_el_camino(self):
        # Esperado: con un ramal lateral, elige el final del ramal y no una casilla del camino
        lab = Laberinto(2, 3)
        for c in range(1, 6):
            lab.abrir(1, c)                     # camino principal: fila 1 y bajada por la columna 5
        lab.abrir(2, 5)
        lab.abrir(3, 5)
        for f, c in ((2, 1), (3, 1), (3, 2), (3, 3)):
            lab.abrir(f, c)                     # ramal lateral que sale de la entrada
        evitar = set(camino_mas_corto(lab, lab.entrada, lab.salida))
        self.assertEqual(casilla_lejana(lab, lab.entrada, evitar), (3, 3))

    def test_casilla_lejana_sin_opciones_devuelve_el_origen(self):
        # Esperado: si todas las casillas están en "evitar", devuelve el origen
        lab = pasillo()
        todas = set(camino_mas_corto(lab, lab.entrada, lab.salida))
        self.assertEqual(casilla_lejana(lab, lab.entrada, todas), lab.entrada)

    def test_jugador_penalizar(self):
        # Esperado: gasta movimientos de golpe; con 0 o negativo no hace nada
        j = Jugador(pasillo(), 20)
        j.penalizar(5)
        self.assertEqual(j.movimientos, 5)
        j.penalizar(0)
        j.penalizar(-3)
        self.assertEqual(j.movimientos, 5)


class TestRadarEnPartida(unittest.TestCase):

    def test_niveles_tienen_radar_y_pruebas_sin_radar(self):
        # Esperado: los 3 niveles reales traen radar; un nivel sin la clave no lo crea
        for nivel in NIVELES.values():
            self.assertIsNotNone(Partida(nivel, semilla=1).radar)
        sin = dict(NIVEL_RADAR)
        del sin["radar"]
        p = Partida(sin, semilla=1)
        self.assertIsNone(p.radar)
        self.assertIsNone(p.posicion_radar())

    def test_radar_empieza_fuera_del_camino_principal(self):
        # Esperado: el origen del radar no está en el camino más corto a la salida
        for semilla in range(10):
            p = Partida(NIVELES["2"], semilla=semilla)
            self.assertNotIn(p.radar.inicio, set(p.solucion))

    def test_radar_dormido_no_se_ve_ni_penaliza(self):
        # Esperado: durante la espera no se dibuja ni cuesta movimientos extra
        p = Partida(NIVEL_RADAR, semilla=3)
        for _ in range(ESPERA_RADAR):
            p.esperar()
        self.assertIsNone(p.posicion_radar())
        self.assertEqual(p.jugador.movimientos, ESPERA_RADAR)

    def test_contacto_penaliza_y_no_termina_la_partida(self):
        # Esperado: el radar acaba tocando a un jugador quieto; se descuentan
        # PENALIZACION_RADAR movimientos, el radar vuelve a dormir y la partida sigue
        p = Partida(NIVEL_RADAR, semilla=3)
        p.radar = Radar(p.laberinto, p.laberinto.salida, 1, espera=0)
        turnos = 0
        while p.radar.contactos == 0 and turnos < 200:
            p.esperar()
            turnos += 1
            self.assertEqual(p.estado, JUGANDO)
        self.assertEqual(p.radar.contactos, 1)
        self.assertEqual(p.jugador.movimientos, turnos + PENALIZACION_RADAR)
        self.assertIsNone(p.posicion_radar())
        self.assertEqual(p.causa, "")

    def test_penalizacion_puede_dejar_sin_movimientos(self):
        # Esperado: si la penalización agota los movimientos, el estado es SIN_MOVIMIENTOS
        p = Partida(NIVEL_RADAR, semilla=3)
        p.radar = Radar(p.laberinto, p.laberinto.salida, 1, espera=0)
        p.jugador.max_movimientos = p.jugador.movimientos + 3     # casi sin margen
        for _ in range(200):
            if p.estado != JUGANDO:
                break
            p.esperar()
        self.assertEqual(p.estado, SIN_MOVIMIENTOS)

    def test_el_radar_no_impide_ganar(self):
        # Esperado: recorriendo el camino más corto de corrido, el radar puede cruzarse
        # (y cobrar movimientos), pero el jugador siempre llega a la salida con margen
        for clave, nivel in NIVELES.items():
            for semilla in range(30):
                nivel_sin_enemigos = dict(nivel, enemigos=0, eco=0)
                p = Partida(nivel_sin_enemigos, semilla=semilla)
                for casilla in p.solucion[1:]:
                    d = (casilla[0] - p.jugador.posicion[0], casilla[1] - p.jugador.posicion[1])
                    nombre = {(-1, 0): "arriba", (1, 0): "abajo",
                              (0, -1): "izquierda", (0, 1): "derecha"}[d]
                    p.mover(nombre)
                self.assertEqual(p.estado, GANO, "nivel %s, semilla %d" % (clave, semilla))

    def test_consola_dibuja_el_radar(self):
        # Esperado: el texto del laberinto muestra una R donde está el radar
        lab = pasillo()
        self.assertIn("R ", lab.como_texto((1, 1), None, None, None, (1, 3)))


if __name__ == "__main__":
    unittest.main()
