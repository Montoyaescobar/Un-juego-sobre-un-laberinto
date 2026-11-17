"""
test_audio_polish.py
Pruebas del pulido de audio: pasos consecutivos, hover del menú y conteo del puntaje final.
Se ejecutan sin ventana ni dispositivo de audio (controladores "dummy" de SDL).
"""

import os
import tempfile
import time
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
    from interfaz import pantallas as P
    from interfaz.efectos import Sonidos
    from juego.partida import NIVELES, GANO


class _EspiaSonido:
    """Envuelve un pygame.mixer.Sound y guarda el canal que devolvió play() (None = descartado)."""

    def __init__(self, sonido, canales):
        self.sonido = sonido
        self.canales = canales

    def play(self, *a, **k):
        canal = self.sonido.play(*a, **k)
        self.canales.append(canal)
        return canal


class _SonidosFalsos:
    """Registra los nombres de efectos pedidos."""

    def __init__(self):
        self.eventos = []

    def reproducir(self, nombre):
        self.eventos.append(nombre)

    def __getattr__(self, nombre):
        # Cualquier otro método de audio (música, persecución...) es inofensivo.
        return lambda *a, **k: None


def tecla(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k, unicode="", mod=0)


@unittest.skipUnless(HAY_PYGAME, "Pygame no está instalado")
class TestAudioPolish(unittest.TestCase):

    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.antes = modulo_puntajes.ARCHIVO_POR_DEFECTO
        modulo_puntajes.ARCHIVO_POR_DEFECTO = os.path.join(self.carpeta.name, "p.txt")
        self.checkpoint_original = App._archivo_checkpoint
        App._archivo_checkpoint = staticmethod(
            lambda: Path(self.carpeta.name) / "cp" / "checkpoint.json")
        self.app = App()
        self.falsos = _SonidosFalsos()

    def tearDown(self):
        App._archivo_checkpoint = staticmethod(self.checkpoint_original)
        modulo_puntajes.ARCHIVO_POR_DEFECTO = self.antes
        self.carpeta.cleanup()

    # ---------------------------------------------------------------- pasos
    def test_pasos_consecutivos_sin_omision(self):
        s = Sonidos()
        if not s.activo or not s.sonidos_pasos:
            self.skipTest("Sin audio o sin muestras de pasos disponibles")
        canales = []
        s.sonidos_pasos = [_EspiaSonido(x, canales) for x in s.sonidos_pasos]
        for _ in range(10):
            self.assertTrue(s.reproducir_paso())
            time.sleep(0.1)
        self.assertEqual(len(canales), 10)
        self.assertTrue(all(c is not None for c in canales),
                        "Algún paso se descartó por falta de canal")

    def test_pasos_en_rafaga_no_repiten_muestra(self):
        s = Sonidos()
        if not s.activo or len(s.sonidos_pasos) < 2:
            self.skipTest("Se necesitan al menos 2 muestras de pasos")
        usados = []
        for _ in range(10):
            s.reproducir_paso()
            usados.append(s._ultimo_paso)
        self.assertTrue(all(a != b for a, b in zip(usados, usados[1:])))

    # ---------------------------------------------------------------- hover
    def test_sonido_hover_menu(self):
        self.app.sonidos = self.falsos
        menu = P.Menu(self.app)
        self.app.ir_a(menu)
        self.falsos.eventos.clear()
        # Teclado
        sel0 = menu.sel
        menu.evento(tecla(pygame.K_DOWN))
        self.assertNotEqual(menu.sel, sel0)
        self.assertEqual(self.falsos.eventos, ["hover"])
        menu.evento(tecla(pygame.K_UP))
        self.assertEqual(self.falsos.eventos, ["hover", "hover"])
        self.assertEqual(menu.sel, sel0)
        # Mouse: moverlo sobre otra opción
        self.falsos.eventos.clear()
        destino = (sel0 + 2) % len(menu.opciones)
        rect = menu.opciones[destino][1]
        original = pygame.mouse.get_pos
        pygame.mouse.get_pos = lambda: rect.center
        try:
            menu.actualizar(1 / 60)
            self.assertEqual(menu.sel, destino)
            self.assertEqual(self.falsos.eventos, ["hover"])
            # Sin cambio de selección no vuelve a sonar
            menu.actualizar(1 / 60)
            self.assertEqual(self.falsos.eventos, ["hover"])
        finally:
            pygame.mouse.get_pos = original

    # --------------------------------------------------------------- conteo
    def _ganar(self, juego):
        """Fuerza el estado GANO y avanza hasta que se muestre la pantalla final."""
        juego.partida.enemigos = []
        juego.vis_e = []
        juego.partida.estado = GANO
        juego._revisar_fin()
        for _ in range(200):
            self.app.paso(1 / 60, ())
            if juego.modo in ("nombre", "opciones"):
                break

    def test_conteo_puntaje_final(self):
        self.app.ir_a(P.Juego(self.app, NIVELES["1"]))
        juego = self.app.pantalla
        self._ganar(juego)
        self.assertEqual(juego.partida.estado, GANO)
        self.assertIn(juego.modo, ("nombre", "opciones"))
        self.app.sonidos = self.falsos
        # Reinicia la animación del conteo
        juego.t_fin = 0.0
        juego._ultimo_puntaje_mostrado = 0
        juego._conteo_fin_sonado = False
        self.falsos.eventos.clear()
        for _ in range(150):   # 2.5 s > 1.2 s de animación
            self.app.paso(1 / 60, ())
        eventos = self.falsos.eventos
        self.assertGreater(eventos.count("conteo"), 0)
        self.assertEqual(eventos.count("conteo_fin"), 1)
        # conteo_fin llega después del último "conteo"
        ultimo_conteo = max(i for i, e in enumerate(eventos) if e == "conteo")
        self.assertLess(ultimo_conteo, eventos.index("conteo_fin"))
        # Más cuadros: no vuelve a sonar
        for _ in range(60):
            self.app.paso(1 / 60, ())
        self.assertEqual(self.falsos.eventos.count("conteo_fin"), 1)

    # ------------------------------------------------------------ efectos
    def test_efectos_disponibles(self):
        s = Sonidos()
        if not s.activo:
            self.skipTest("Sin dispositivo de audio")
        for nombre in ("hover", "conteo", "conteo_fin"):
            self.assertIn(nombre, s.efectos)
            self.assertTrue(callable(s.efectos[nombre].play))
        for nombre in ("hover", "conteo", "conteo_fin"):
            s.reproducir(nombre)   # no debe lanzar excepción


if __name__ == "__main__":
    unittest.main()
