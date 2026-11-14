"""
test_aleatorio.py
Prueba de estrés de la interfaz: teclas y clics al azar sobre cada pantalla y cada nivel
(con el modo "dummy" de Pygame, sin abrir ventana) para comprobar que NADA cierra el juego.
Se omite sola si Pygame no está instalado. Ejecutar:
    python -m unittest pruebas.test_aleatorio -v
"""

import os
import random
import tempfile
import unittest

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
    from interfaz import pantallas as P
    from juego.partida import NIVELES, ATRAPADO

CUADROS = 120          # cuadros por pantalla y por semilla (el conteo total se ve al final)
SEMILLAS = (1, 2)


def tecla(k, caracter=""):
    """Ayuda de prueba: evento de tecla presionada."""
    return pygame.event.Event(pygame.KEYDOWN, key=k, unicode=caracter, mod=0)


@unittest.skipUnless(HAY_PYGAME, "Pygame no está instalado")
class TestAleatorio(unittest.TestCase):

    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.antes = modulo_puntajes.ARCHIVO_POR_DEFECTO
        modulo_puntajes.ARCHIVO_POR_DEFECTO = os.path.join(self.carpeta.name, "p.txt")
        self.app = App()
        self.teclas = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_w,
                       pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_SPACE, pygame.K_RETURN,
                       pygame.K_f, pygame.K_x, pygame.K_e, pygame.K_q, pygame.K_l, pygame.K_h,
                       pygame.K_u, pygame.K_z, pygame.K_ESCAPE, pygame.K_p, pygame.K_m,
                       pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_BACKSPACE, pygame.K_DELETE]

    def tearDown(self):
        modulo_puntajes.ARCHIVO_POR_DEFECTO = self.antes
        self.carpeta.cleanup()

    def machacar(self, pantalla, semilla):
        """Entrega teclas y clics al azar durante CUADROS cuadros. Si algo falla, la prueba falla."""
        azar = random.Random(semilla)
        self.app.ir_a(pantalla)
        for _ in range(CUADROS):
            eventos = []
            if azar.random() < 0.4:
                eventos.append(tecla(azar.choice(self.teclas)))
            if azar.random() < 0.03:
                eventos.append(pygame.event.Event(
                    pygame.MOUSEBUTTONDOWN, pos=(azar.randint(0, 1099), azar.randint(0, 719)), button=1))
            self.app.paso(1 / 60, eventos)

    def test_pantallas_con_teclas_al_azar(self):
        # Esperado: ninguna pantalla lanza una excepción con entradas al azar
        self.app.pantalla.nueva_partida()
        fabricas = (lambda: P.Menu(self.app), lambda: P.Campamento(self.app),
                    lambda: P.Niveles(self.app), lambda: P.Ranking(self.app),
                    lambda: P.AjustesMenu(self.app), lambda: P.Creditos(self.app),
                    lambda: P.Reglas(self.app, lambda: P.Menu(self.app)))
        for fabrica in fabricas:
            for semilla in SEMILLAS:
                self.machacar(fabrica(), semilla)

    def test_cada_nivel_con_teclas_al_azar(self):
        # Esperado: los 3 niveles aguantan teclas al azar (incluida la tecla Q de esperar)
        for nivel in NIVELES.values():
            for semilla in SEMILLAS:
                self.machacar(P.Juego(self.app, nivel), semilla)

    def test_repeticion_con_teclas_al_azar(self):
        # Esperado: la repetición de una partida jugada al azar tampoco falla
        juego = P.Juego(self.app, NIVELES["1"])
        self.machacar(juego, 7)
        self.machacar(P.Repeticion(self.app, juego.partida, lambda: P.Menu(self.app)), 8)

    def test_tecla_q_espera_un_turno_y_el_eco_atrapa_si_te_quedas_quieto(self):
        # Esperado: Q gasta 1 movimiento; esperar sin parar termina atrapado por el eco
        self.app.ir_a(P.Juego(self.app, NIVELES["1"]))
        juego = self.app.pantalla
        juego.partida.enemigos = []                  # solo queremos probar el eco
        juego.vis_e = []
        for direccion in (pygame.K_DOWN, pygame.K_RIGHT):   # un par de pasos si hay camino
            self.app.paso(1 / 60, [tecla(direccion)])
        antes = juego.partida.jugador.movimientos
        self.app.paso(1 / 60, [tecla(pygame.K_q)])
        self.assertEqual(juego.partida.jugador.movimientos, antes + 1)
        for _ in range(30):
            self.app.paso(1 / 60, [tecla(pygame.K_q)])
        self.assertEqual(juego.partida.estado, ATRAPADO)
        self.assertEqual(juego.partida.causa, "eco")


if __name__ == "__main__":
    unittest.main()
