"""
test_ambiente.py
Pruebas del ambiente del campamento (humo, chispas, luciérnagas, niebla, luz y viñeta).
Se ejecutan sin ventana (controlador "dummy" de SDL) y se omiten solas si no hay Pygame:
    python -m unittest pruebas.test_ambiente -v
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
    from interfaz.ambiente import AmbienteRefugio


@unittest.skipUnless(HAY_PYGAME, "Pygame no está instalado")
class TestAmbiente(unittest.TestCase):

    def setUp(self):
        pygame.init()
        self.superficie = pygame.Surface((1100, 720))
        self.ambiente = AmbienteRefugio(1100, 720)

    def test_dibujar_todo_no_falla(self):
        # Esperado: 10 segundos de animación y dibujo sin errores
        for _ in range(600):
            self.ambiente.actualizar(1 / 60)
            self.ambiente.dibujar_luz(self.superficie)
            self.ambiente.dibujar_niebla(self.superficie)
            self.ambiente.dibujar_chispas(self.superficie)
            self.ambiente.dibujar_humo(self.superficie)
            self.ambiente.dibujar_luciernagas(self.superficie)
            self.ambiente.dibujar_vineta(self.superficie)

    def test_las_particulas_no_crecen_sin_limite(self):
        # Esperado: humo y chispas se mantienen dentro de su tope
        for _ in range(1200):
            self.ambiente.actualizar(1 / 60)
        self.assertLessEqual(len(self.ambiente.humo), 60)
        self.assertLessEqual(len(self.ambiente.chispas), 40)

    def test_luciernagas_dentro_de_la_pantalla(self):
        # Esperado: nunca se salen del área visible
        for _ in range(900):
            self.ambiente.actualizar(1 / 60)
        for l in self.ambiente.luciernagas:
            self.assertTrue(20 <= l["x"] <= 1080 and 180 <= l["y"] <= 670)

    def test_baja_la_calidad_si_va_lento(self):
        # Esperado: a 15 cuadros por segundo la calidad pasa a 0; a 60 se mantiene en 1
        rapido = AmbienteRefugio(1100, 720)
        for _ in range(300):
            rapido.actualizar(1 / 60)
        self.assertEqual(rapido.calidad, 1)
        for _ in range(200):
            self.ambiente.actualizar(1 / 15)
        self.assertEqual(self.ambiente.calidad, 0)

    def test_con_calidad_baja_tambien_dibuja(self):
        # Esperado: sin niebla y con menos luciérnagas, pero sin errores
        self.ambiente.calidad = 0
        self.ambiente.dibujar_niebla(self.superficie)
        self.ambiente.dibujar_luciernagas(self.superficie)


if __name__ == "__main__":
    unittest.main()
