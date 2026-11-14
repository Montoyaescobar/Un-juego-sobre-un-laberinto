"""
test_controlador_campamento.py
Pruebas unitarias y de integración para ControladorCampamento y el movimiento en Campamento.
"""

import math
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

try:
    import pygame
    HAY_PYGAME = True
except ImportError:
    HAY_PYGAME = False

if HAY_PYGAME:
    import juego.puntajes as modulo_puntajes
    from interfaz.app import App
    from interfaz.controlador_campamento import (
        ControladorCampamento,
        obtener_bloqueos_campamento,
        obtener_limites_campamento,
        es_posicion_valida,
    )
    from interfaz.pantallas import Campamento


def evento_keydown(tecla):
    """Crea un evento KEYDOWN para pruebas."""
    return pygame.event.Event(pygame.KEYDOWN, key=tecla, unicode="", mod=0)


def evento_keyup(tecla):
    """Crea un evento KEYUP para pruebas."""
    return pygame.event.Event(pygame.KEYUP, key=tecla, mod=0)


@unittest.skipUnless(HAY_PYGAME, "Pygame no está instalado")
class TestControladorCampamento(unittest.TestCase):

    def setUp(self):
        self.limites_amplios = (0, 0, 1100, 720)

    def test_movimiento_diagonal_actualiza_ambos_ejes(self):
        """El movimiento diagonal debe actualizar X e Y simultáneamente sin sobrescribir X."""
        direcciones_diagonales = [
            ((pygame.K_d, pygame.K_w), 1, -1),
            ((pygame.K_d, pygame.K_s), 1, 1),
            ((pygame.K_a, pygame.K_w), -1, -1),
            ((pygame.K_a, pygame.K_s), -1, 1),
            ((pygame.K_RIGHT, pygame.K_UP), 1, -1),
            ((pygame.K_LEFT, pygame.K_DOWN), -1, 1),
        ]
        dt = 0.1
        for teclas, sig_x, sig_y in direcciones_diagonales:
            ctrl = ControladorCampamento(
                posicion=(500.0, 400.0),
                velocidad=190.0,
                limites=self.limites_amplios,
                bloqueos=[],
            )
            for k in teclas:
                ctrl.evento(evento_keydown(k))

            pos, _, andando = ctrl.actualizar(dt)
            esperado_delta = (190.0 / math.sqrt(2)) * dt

            self.assertTrue(andando)
            self.assertAlmostEqual(pos[0], 500.0 + sig_x * esperado_delta, places=5)
            self.assertAlmostEqual(pos[1], 400.0 + sig_y * esperado_delta, places=5)

    def test_velocidad_uniforme_en_todas_las_direcciones(self):
        """La distancia recorrida por unidad de tiempo debe ser igual en los 8 rumbos."""
        combinaciones = [
            (pygame.K_w,),
            (pygame.K_s,),
            (pygame.K_a,),
            (pygame.K_d,),
            (pygame.K_w, pygame.K_d),
            (pygame.K_w, pygame.K_a),
            (pygame.K_s, pygame.K_d),
            (pygame.K_s, pygame.K_a),
        ]
        dt = 0.25
        velocidad = 190.0
        distancia_esperada = velocidad * dt

        for teclas in combinaciones:
            ctrl = ControladorCampamento(
                posicion=(550.0, 400.0),
                velocidad=velocidad,
                limites=self.limites_amplios,
                bloqueos=[],
            )
            for k in teclas:
                ctrl.evento(evento_keydown(k))

            pos, _, andando = ctrl.actualizar(dt)
            distancia = math.hypot(pos[0] - 550.0, pos[1] - 400.0)
            self.assertTrue(andando)
            self.assertAlmostEqual(distancia, distancia_esperada, places=5)

    def test_deslizamiento_en_muro_vertical_bloquea_x_pero_avanza_y(self):
        """Si hay un muro bloqueando el eje X, el personaje se desliza por el eje Y."""
        # Hitbox en (500, 400) va de x=491 a x=509. Ponemos un muro vertical en x=510.
        muro_vertical = pygame.Rect(510, 300, 40, 200)
        ctrl = ControladorCampamento(
            posicion=(500.0, 400.0),
            velocidad=190.0,
            limites=self.limites_amplios,
            bloqueos=[muro_vertical],
        )
        ctrl.evento(evento_keydown(pygame.K_d))
        ctrl.evento(evento_keydown(pygame.K_s))

        pos, _, andando = ctrl.actualizar(0.1)
        avance_diagonal = (190.0 / math.sqrt(2)) * 0.1

        self.assertTrue(andando)
        self.assertAlmostEqual(pos[0], 500.0, places=5)
        self.assertAlmostEqual(pos[1], 400.0 + avance_diagonal, places=5)

    def test_deslizamiento_en_muro_horizontal_bloquea_y_pero_avanza_x(self):
        """Si hay un muro bloqueando el eje Y, el personaje se desliza por el eje X."""
        # Hitbox en (500, 400) va de y=392 a y=408. Ponemos un muro horizontal arriba en y=350..391.
        muro_horizontal = pygame.Rect(400, 350, 200, 41)
        ctrl = ControladorCampamento(
            posicion=(500.0, 400.0),
            velocidad=190.0,
            limites=self.limites_amplios,
            bloqueos=[muro_horizontal],
        )
        ctrl.evento(evento_keydown(pygame.K_d))
        ctrl.evento(evento_keydown(pygame.K_w))

        pos, _, andando = ctrl.actualizar(0.1)
        avance_diagonal = (190.0 / math.sqrt(2)) * 0.1

        self.assertTrue(andando)
        self.assertAlmostEqual(pos[0], 500.0 + avance_diagonal, places=5)
        self.assertAlmostEqual(pos[1], 400.0, places=5)

    def test_gestion_teclas_opuestas_y_perdida_de_foco(self):
        """Teclas opuestas se cancelan y la pérdida de foco limpia las teclas activas."""
        ctrl = ControladorCampamento(
            posicion=(500.0, 400.0),
            limites=self.limites_amplios,
            bloqueos=[],
        )
        ctrl.evento(evento_keydown(pygame.K_a))
        ctrl.evento(evento_keydown(pygame.K_d))
        self.assertEqual(ctrl.vector_entrada(), (0, 0))

        pos, _, andando = ctrl.actualizar(0.1)
        self.assertFalse(andando)
        self.assertEqual(pos, [500.0, 400.0])

        # Soltar una de las teclas opuestas retoma el movimiento inmediato hacia la otra
        ctrl.evento(evento_keyup(pygame.K_a))
        self.assertEqual(ctrl.vector_entrada(), (1, 0))

        # Perder foco limpia las teclas para evitar atascos
        evento_foco = pygame.event.Event(getattr(pygame, "WINDOWFOCUSLOST", pygame.ACTIVEEVENT), gain=0)
        ctrl.evento(evento_foco)
        self.assertEqual(len(ctrl.teclas), 0)
        self.assertFalse(ctrl.andando)

    def test_hitbox_subpixel_y_direcciones_cardinales(self):
        """Verifica el redondeo subpíxel de la hitbox y las 4 direcciones cardinales."""
        ctrl = ControladorCampamento(posicion=(500.4, 400.6), limites=self.limites_amplios, bloqueos=[])
        caja = ctrl.obtener_caja()
        self.assertEqual(caja.size, (18, 16))
        self.assertEqual(caja.topleft, (round(500.4 - 9), round(400.6 - 8)))

        self.assertEqual(ControladorCampamento.calcular_direccion(0, -1), "arriba")
        self.assertEqual(ControladorCampamento.calcular_direccion(0, 1), "abajo")
        self.assertEqual(ControladorCampamento.calcular_direccion(-1, 0), "izquierda")
        self.assertEqual(ControladorCampamento.calcular_direccion(1, 0), "derecha")

    def test_integracion_en_pantalla_campamento(self):
        """Verifica que la pantalla Campamento delegue el movimiento diagonal en ControladorCampamento."""
        with tempfile.TemporaryDirectory() as carpeta:
            antes = modulo_puntajes.ARCHIVO_POR_DEFECTO
            modulo_puntajes.ARCHIVO_POR_DEFECTO = os.path.join(carpeta, "p.txt")
            cp_original = App._archivo_checkpoint
            App._archivo_checkpoint = staticmethod(lambda: Path(carpeta) / "cp" / "checkpoint.json")
            try:
                app = App()
                camp = Campamento(app, posicion=(550.0, 596.0))
                self.assertIsInstance(camp.controlador, ControladorCampamento)

                x0, y0 = camp.personaje
                camp.evento(evento_keydown(pygame.K_d))
                camp.evento(evento_keydown(pygame.K_w))
                camp.actualizar(1 / 60)

                self.assertGreater(camp.personaje[0], x0)
                self.assertLess(camp.personaje[1], y0)
                self.assertTrue(camp.andando)
                self.assertEqual(app.punto_guardado, tuple(camp.personaje))
            finally:
                App._archivo_checkpoint = staticmethod(cp_original)
                modulo_puntajes.ARCHIVO_POR_DEFECTO = antes


if __name__ == "__main__":
    unittest.main()
