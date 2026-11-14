"""
test_ambiente_laberinto.py
Pruebas del ambiente del laberinto (antorchas, brasas, polvo, niebla), de las paletas por nivel
y del interruptor de efectos. Se ejecutan sin ventana (controlador "dummy" de SDL) y se omiten
solas si no hay Pygame:
    python -m unittest pruebas.test_ambiente_laberinto -v
"""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

try:
    import pygame
    HAY_PYGAME = True
except ImportError:
    HAY_PYGAME = False

if HAY_PYGAME:
    from interfaz.ambiente_laberinto import AmbienteLaberinto
    from interfaz.render import Linterna, tablero_estatico
    from interfaz.tema import PALETA_BASE, PALETAS_NIVEL, paleta_de
    from juego.partida import NIVELES, Partida


@unittest.skipUnless(HAY_PYGAME, "Pygame no está instalado")
class TestPaletas(unittest.TestCase):

    def test_cada_nivel_tiene_sus_colores(self):
        # Esperado: los tres niveles existen, son distintos entre sí y tienen todas las claves
        for nivel in NIVELES.values():
            paleta = paleta_de(nivel["nombre"])
            self.assertIsNot(paleta, PALETA_BASE)
            for clave in PALETA_BASE:
                self.assertIn(clave, paleta)
        paredes = {tuple(p["pared"]) for p in PALETAS_NIVEL.values()}
        self.assertEqual(len(paredes), len(PALETAS_NIVEL))

    def test_nivel_desconocido_usa_la_paleta_base(self):
        # Esperado: un nombre raro no rompe nada
        self.assertIs(paleta_de("no existe"), PALETA_BASE)

    def test_el_tablero_se_dibuja_con_y_sin_paleta(self):
        # Esperado: el tamaño es ancho*cell x alto*cell en los tres niveles
        pygame.init()
        for nivel in NIVELES.values():
            lab = Partida(nivel).laberinto
            for paleta in (None, paleta_de(nivel["nombre"])):
                s = tablero_estatico(lab, 30, paleta=paleta)
                self.assertEqual(s.get_size(), (lab.ancho * 30, lab.alto * 30))


@unittest.skipUnless(HAY_PYGAME, "Pygame no está instalado")
class TestAmbienteLaberinto(unittest.TestCase):

    def setUp(self):
        pygame.init()
        self.rect = pygame.Rect(20, 20, 600, 600)
        self.fuentes = [(100, 100), (300, 200), (500, 450)]
        self.ambiente = AmbienteLaberinto(self.rect, paleta_de("Medio"), self.fuentes, 70)
        self.superficie = pygame.Surface((1100, 720))

    def test_dibujar_todo_no_falla(self):
        # Esperado: 10 segundos de animación y dibujo sin errores
        linterna = Linterna((600, 600), 130, (4, 7, 15))
        for _ in range(600):
            self.ambiente.actualizar(1 / 60)
            self.ambiente.dibujar_niebla(self.superficie)
            self.ambiente.dibujar_polvo(self.superficie)
            linterna.dibujar(self.superficie, (20, 20), (300, 300),
                             self.ambiente.luces_para_linterna((20, 20)), 196)
            self.ambiente.dibujar_luces(self.superficie)

    def test_el_parpadeo_se_mantiene_cerca_de_uno(self):
        # Esperado: nunca apaga la luz ni la dispara: entre 0.8 y 1.2
        for _ in range(900):
            self.ambiente.actualizar(1 / 60)
            for i in range(len(self.fuentes)):
                self.assertTrue(0.8 <= self.ambiente.factor_luz(i) <= 1.2)

    def test_las_brasas_no_crecen_sin_limite(self):
        # Esperado: se mantienen dentro del tope
        for _ in range(1800):
            self.ambiente.actualizar(1 / 60)
        self.assertLessEqual(len(self.ambiente.brasas), AmbienteLaberinto.MAX_BRASAS)

    def test_el_polvo_se_queda_dentro_del_tablero(self):
        # Esperado: ninguna mota se sale del rectángulo
        for _ in range(1200):
            self.ambiente.actualizar(1 / 60)
        for x, y, _, _, _ in self.ambiente.polvo:
            self.assertTrue(self.rect.left <= x <= self.rect.right)
            self.assertTrue(self.rect.top <= y <= self.rect.bottom)

    def test_efectos_bajo_quita_las_particulas(self):
        # Esperado: con efectos BAJO no hay brasas, y al volver a ALTO regresan
        for _ in range(300):
            self.ambiente.actualizar(1 / 60)
        self.assertGreater(len(self.ambiente.brasas), 0)
        self.ambiente.actualizar(1 / 60, efectos=False)
        self.assertEqual(self.ambiente.brasas, [])
        for _ in range(300):
            self.ambiente.actualizar(1 / 60, efectos=True)
        self.assertGreater(len(self.ambiente.brasas), 0)

    def test_baja_la_calidad_si_va_lento(self):
        # Esperado: a 15 cuadros por segundo la calidad pasa a 0; a 60 se mantiene en 1
        lento = AmbienteLaberinto(self.rect, paleta_de("Fácil"), self.fuentes, 70)
        rapido = AmbienteLaberinto(self.rect, paleta_de("Fácil"), self.fuentes, 70)
        for _ in range(300):
            lento.actualizar(1 / 15)
            rapido.actualizar(1 / 60)
        self.assertEqual(lento.calidad, 0)
        self.assertEqual(rapido.calidad, 1)

    def test_las_luces_de_la_linterna_son_relativas_al_tablero(self):
        # Esperado: cada antorcha sale como (x, y, escala) con x, y relativos al origen
        luces = self.ambiente.luces_para_linterna((20, 20))
        self.assertEqual(len(luces), len(self.fuentes))
        for (x, y, escala), (fx, fy) in zip(luces, self.fuentes):
            self.assertEqual((x, y), (fx - 20, fy - 20))
            self.assertGreater(escala, 0)

    def test_linterna_acepta_luces_con_y_sin_escala(self):
        # Esperado: el formato viejo (x, y) y el nuevo (x, y, escala) funcionan juntos
        linterna = Linterna((600, 600), 130)
        linterna.dibujar(self.superficie, (20, 20), (300, 300),
                         [(100, 100), (200, 200, 1.15), (400, 400, 0.85)], 196)


if __name__ == "__main__":
    unittest.main()
