"""
test_eco.py
Pruebas del ECO (usa la Cola propia): el fantasma que repite el recorrido del jugador.
Se ejecutan sin ventana. Ejecutar:
    python -m unittest pruebas.test_eco -v
"""

import unittest

from estructuras.cola import Cola
from juego.eco import Eco
from juego.jugador import Jugador
from juego.laberinto import Laberinto
from juego.partida import Partida, NIVELES, JUGANDO, GANO, ATRAPADO
from juego.solver import camino_mas_corto

NIVEL_ECO = {"nombre": "Prueba", "filas": 4, "columnas": 4, "factor": 3.0,
             "enemigos": 0, "base": 100, "eco": 3}


def direccion(desde, hasta):
    """Ayuda de prueba: nombre de la dirección para ir de una casilla a su vecina."""
    d = (hasta[0] - desde[0], hasta[1] - desde[1])
    return {(-1, 0): "arriba", (1, 0): "abajo", (0, -1): "izquierda", (0, 1): "derecha"}[d]


class TestEco(unittest.TestCase):

    def test_retraso_invalido(self):
        # Esperado: ValueError con retrasos que no son enteros >= 1
        for malo in (0, -2, "3", 2.5, None, True):
            with self.assertRaises(ValueError):
                Eco(malo, (1, 1))

    def test_eco_nuevo_esta_dormido(self):
        # Esperado: sin pasos pendientes, inactivo y no atrapa aunque coincida la casilla
        e = Eco(3, (1, 1))
        self.assertFalse(e.activo)
        self.assertEqual(e.pasos_pendientes(), 0)
        self.assertEqual(e.posicion, (1, 1))
        self.assertFalse(e.atrapa((1, 1)))

    def test_usa_la_cola_propia(self):
        # Esperado: los pasos pendientes se guardan en la Cola de estructuras/
        self.assertIsInstance(Eco(2, (1, 1))._pasos, Cola)

    def test_no_se_mueve_hasta_superar_el_retraso(self):
        # Esperado: con retraso 3, los 3 primeros turnos no mueven al eco; el 4.º sí
        e = Eco(3, (1, 1))
        camino = [(1, 2), (1, 3), (1, 4), (1, 5)]
        resultados = [e.turno(c) for c in camino]
        self.assertEqual(resultados, [False, False, False, True])
        self.assertTrue(e.activo)
        self.assertEqual(e.posicion, (1, 2))

    def test_repite_el_recorrido_en_orden_fifo(self):
        # Esperado: el eco recorre las mismas casillas, en el mismo orden, 2 pasos atrás
        e = Eco(2, (1, 1))
        camino = [(1, 2), (1, 3), (1, 4), (2, 4), (3, 4), (3, 3)]
        vistas = []
        for c in camino:
            e.turno(c)
            vistas.append(e.posicion)
        self.assertEqual(vistas, [(1, 1), (1, 1), (1, 2), (1, 3), (1, 4), (2, 4)])

    def test_pendientes_nunca_pasan_del_retraso(self):
        # Esperado: mientras el jugador se mueve, la cola guarda como máximo 'retraso' casillas
        e = Eco(4, (1, 1))
        for i in range(20):
            e.turno((1, 2 + i))
            self.assertLessEqual(e.pasos_pendientes(), 4)

    def test_esperar_acerca_al_eco(self):
        # Esperado: cada espera desencola una casilla; al vaciarse, el eco está sobre el jugador
        e = Eco(3, (1, 1))
        for c in [(1, 2), (1, 3), (1, 4)]:
            e.turno(c)
        self.assertEqual(e.pasos_pendientes(), 3)
        self.assertTrue(e.turno((1, 4), esperando=True))
        self.assertEqual(e.pasos_pendientes(), 2)
        e.turno((1, 4), esperando=True)
        e.turno((1, 4), esperando=True)
        self.assertEqual(e.pasos_pendientes(), 0)
        self.assertEqual(e.posicion, (1, 4))
        self.assertTrue(e.atrapa((1, 4)))

    def test_esperar_sin_pendientes_no_mueve(self):
        # Esperado: un eco sin casillas pendientes no se mueve ni se activa
        e = Eco(3, (1, 1))
        self.assertFalse(e.turno((1, 1), esperando=True))
        self.assertFalse(e.activo)

    def test_atrapa_por_cruce(self):
        # Esperado: intercambiar casillas en un turno también cuenta como atrapar
        e = Eco(1, (1, 1))
        e.activo = True
        e.posicion, e.anterior = (1, 2), (1, 3)
        self.assertTrue(e.atrapa((1, 3), (1, 2)))
        self.assertFalse(e.atrapa((1, 3)))


class TestJugadorEsperar(unittest.TestCase):

    def test_esperar_cuesta_un_movimiento(self):
        # Esperado: no cambia de casilla y gasta 1 movimiento
        lab = Laberinto(1, 2)
        for c in range(1, 4):
            lab.abrir(1, c)
        j = Jugador(lab, 5)
        self.assertTrue(j.esperar())
        self.assertEqual(j.movimientos, 1)
        self.assertEqual(j.posicion, lab.entrada)

    def test_no_se_puede_esperar_si_ya_termino(self):
        # Esperado: False cuando se acabaron los movimientos
        lab = Laberinto(1, 2)
        for c in range(1, 4):
            lab.abrir(1, c)
        j = Jugador(lab, 1)
        j.esperar()
        self.assertFalse(j.esperar())
        self.assertEqual(j.movimientos, 1)


class TestEcoEnPartida(unittest.TestCase):

    def test_niveles_tienen_eco_y_pruebas_sin_eco(self):
        # Esperado: los 3 niveles traen eco; un nivel sin la clave "eco" no lo crea
        for nivel in NIVELES.values():
            self.assertIsNotNone(Partida(nivel, semilla=1).eco)
        sin_eco = dict(NIVEL_ECO)
        del sin_eco["eco"]
        self.assertIsNone(Partida(sin_eco, semilla=1).eco)

    def test_camino_optimo_nunca_es_atrapado_por_el_eco(self):
        # Esperado: si el jugador no se detiene, el eco jamás lo alcanza y se gana
        for semilla in range(12):
            for nivel in NIVELES.values():
                p = Partida(nivel, semilla=semilla)
                camino = camino_mas_corto(p.laberinto, p.jugador.posicion, p.laberinto.salida)
                for i in range(len(camino) - 1):
                    self.assertTrue(p.mover(direccion(camino[i], camino[i + 1])))
                self.assertEqual(p.estado, GANO)

    def test_esperar_cuesta_movimiento_y_mueve_a_los_enemigos(self):
        # Esperado: gasta 1 movimiento; se guarda una foto (los enemigos son autónomos en tiempo)
        p = Partida(NIVELES["1"], semilla=4)
        antes = p.posiciones_enemigos()
        self.assertTrue(p.esperar())
        self.assertEqual(p.jugador.movimientos, 1)
        self.assertEqual(p.posiciones_enemigos(), antes)
        self.assertEqual(p.historial.total(), 2)

    def test_esperar_demasiado_te_atrapa_el_eco(self):
        # Esperado: tras 2 pasos y 2 esperas el eco llega a la casilla del jugador
        p = Partida(NIVEL_ECO, semilla=5)
        c = p.solucion
        p.mover(direccion(c[0], c[1]))
        p.mover(direccion(c[1], c[2]))
        self.assertEqual(p.estado, JUGANDO)
        p.esperar()
        self.assertEqual(p.estado, JUGANDO)
        p.esperar()
        self.assertEqual(p.estado, ATRAPADO)
        self.assertEqual(p.causa, "eco")
        self.assertFalse(p.esperar())

    def test_deshacer_tambien_encola(self):
        # Esperado: deshacer cuenta como un paso del recorrido (la cola crece)
        p = Partida(NIVEL_ECO, semilla=5)
        c = p.solucion
        p.mover(direccion(c[0], c[1]))
        p.mover(direccion(c[1], c[2]))
        p.deshacer()
        self.assertEqual(p.eco.pasos_pendientes(), 3)

    def test_cruzarse_con_el_eco_al_deshacer(self):
        # Esperado: con retraso 1, deshacer hace que jugador y eco intercambien casillas -> atrapa
        nivel = dict(NIVEL_ECO, eco=1)
        p = Partida(nivel, semilla=5)
        c = p.solucion
        p.mover(direccion(c[0], c[1]))
        p.mover(direccion(c[1], c[2]))
        self.assertEqual(p.posicion_eco(), c[1])
        self.assertEqual(p.estado, JUGANDO)
        p.deshacer()
        self.assertEqual(p.estado, ATRAPADO)
        self.assertEqual(p.causa, "eco")

    def test_el_eco_se_dibuja_en_consola(self):
        # Esperado: una e minúscula en la casilla del eco una vez que despierta
        nivel = dict(NIVEL_ECO, eco=1)
        p = Partida(nivel, semilla=5)
        self.assertIsNone(p.posicion_eco())
        c = p.solucion
        p.mover(direccion(c[0], c[1]))
        p.mover(direccion(c[1], c[2]))
        self.assertEqual(p.posicion_eco(), c[1])
        self.assertIn("e ", p.dibujar())


if __name__ == "__main__":
    unittest.main()
