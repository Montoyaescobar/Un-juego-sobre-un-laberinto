"""
test_codice_arma.py
Pruebas de ataques de armas, sprites del jugador y Códice de Mecánicas (PantallaCodiceGuia).
Se ejecutan sin ventana (controlador "dummy" de SDL). Ejecutar:
    python -m unittest pruebas.test_codice_arma -v
"""

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
    from interfaz import pantallas as P
    from interfaz import render as R
    from juego.partida import NIVELES

ARMAS = ("espada_ceniza", "daga_sombras", "baston_centella")


def tecla(k, caracter=""):
    return pygame.event.Event(pygame.KEYDOWN, key=k, unicode=caracter, mod=0)


def clic(pos):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1)


def bytes_superficie(surf):
    return pygame.image.tostring(surf, "RGBA")


@unittest.skipUnless(HAY_PYGAME, "Pygame no está instalado")
class TestCodiceArma(unittest.TestCase):

    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.antes = modulo_puntajes.ARCHIVO_POR_DEFECTO
        modulo_puntajes.ARCHIVO_POR_DEFECTO = os.path.join(self.carpeta.name, "p.txt")
        self.checkpoint_original = App._archivo_checkpoint
        App._archivo_checkpoint = staticmethod(
            lambda: Path(self.carpeta.name) / "cp" / "checkpoint.json")
        self.app = App()

    def tearDown(self):
        App._archivo_checkpoint = staticmethod(self.checkpoint_original)
        modulo_puntajes.ARCHIVO_POR_DEFECTO = self.antes
        self.carpeta.cleanup()

    def cuadros(self, n=1, eventos=()):
        for i in range(n):
            self.app.paso(1 / 60, eventos if i == 0 else ())

    # ------------------------------------------------------------ ataques
    def test_render_armas_distintas(self):
        """dibujar_ataque_arma renderiza sin excepciones y de forma distinta por arma."""
        imagenes = {}
        for arma in ARMAS:
            surf = pygame.Surface((160, 160), pygame.SRCALPHA)
            for direccion in ("arriba", "abajo", "izquierda", "derecha"):
                for progreso in (0.0, 0.5, 1.0):
                    R.dibujar_ataque_arma(surf, 80, 80, 48, 0.4, direccion, progreso, arma)
            surf2 = pygame.Surface((160, 160), pygame.SRCALPHA)
            R.dibujar_ataque_arma(surf2, 80, 80, 48, 0.4, "derecha", 0.5, arma_id=arma)
            imagenes[arma] = bytes_superficie(surf2)
            self.assertTrue(pygame.mask.from_surface(surf2).count() > 0,
                            f"{arma} no dibujó nada")
        self.assertEqual(len(set(imagenes.values())), len(ARMAS))
        # La envoltura de pantallas también debe funcionar
        surf = pygame.Surface((160, 160), pygame.SRCALPHA)
        for arma in ARMAS:
            P.dibujar_ataque_arma(surf, 80, 80, 48, 0.4, "abajo", 0.5, arma)

    def test_sprite_jugador_con_armas(self):
        """dibujar_jugador genera sprites diferenciados según el arma equipada."""
        imagenes = {}
        for arma in ARMAS:
            surf = pygame.Surface((96, 96), pygame.SRCALPHA)
            R.dibujar_jugador(surf, 48, 48, 48, 0.0, antorcha=False, direccion="abajo",
                              andando=False, arma=arma)
            self.assertTrue(pygame.mask.from_surface(surf).count() > 0)
            imagenes[arma] = bytes_superficie(surf)
        self.assertEqual(len(set(imagenes.values())), len(ARMAS),
                         "los sprites no se diferencian por arma")
        for direccion in ("arriba", "abajo", "izquierda", "derecha"):
            surf = pygame.Surface((96, 96), pygame.SRCALPHA)
            for arma in ARMAS:
                R.dibujar_jugador(surf, 48, 48, 48, 0.3, direccion=direccion,
                                  andando=True, saltando=(arma == "daga_sombras"), arma=arma)

    # ------------------------------------------------------------ códice
    def test_pantalla_codice_elementos(self):
        """El Códice contiene y describe Radar, Eco, trampas y coleccionables."""
        pantalla = P.PantallaCodiceGuia(self.app)
        por_id = {e["id"]: e for e in pantalla.entradas}
        self.assertEqual(set(pantalla.categorias), {"Trampas", "Entidades", "Coleccionables"})

        self.assertIn("orbe_carmesi", por_id)
        self.assertIn("Orbe Carmesí", por_id["orbe_carmesi"]["nombre"])
        self.assertIn("Radar", por_id["orbe_carmesi"]["nombre"])
        self.assertIn("eco", por_id)
        trampas = [e for e in pantalla.entradas if e["categoria"] == "Trampas"]
        colec = [e for e in pantalla.entradas if e["categoria"] == "Coleccionables"]
        self.assertGreaterEqual(len(trampas), 5)
        self.assertGreaterEqual(len(colec), 3)
        for e in pantalla.entradas:
            self.assertTrue(e["nombre"] and e["subtitulo"])
            self.assertGreater(len(e["descripcion"]), 40)
            self.assertTrue(e["consejos"])

        # Cada entrada se puede seleccionar y dibujar sin errores.
        self.app.ir_a(pantalla)
        for i in range(len(pantalla.entradas)):
            pantalla._seleccionar(i, sonar=False)
            self.assertIs(pantalla.entrada_actual(), pantalla.entradas[i])
            self.cuadros(2)

    # ------------------------------------------------------------ acceso
    def test_acceso_codice_en_juego(self):
        """Juego abre PantallaCodiceGuia con la tecla C y con el botón del HUD."""
        # Con la tecla K_c
        juego = P.Juego(self.app, NIVELES["1"])
        self.app.ir_a(juego)
        self.cuadros(1, [tecla(pygame.K_c, "c")])
        self.assertIsInstance(self.app.pantalla, P.PantallaCodiceGuia)
        # Volver con C regresa al mismo Juego
        self.cuadros(1, [tecla(pygame.K_c, "c")])
        self.assertIs(self.app.pantalla, juego)

        # Con el botón del HUD
        self.assertIn(juego.b_codice, juego.botones_hud)
        self.assertTrue(juego.b_codice.habilitado or juego.modo == "jugando")
        centro = juego.b_codice.rect.center
        self.cuadros(1)
        self.cuadros(1, [clic(centro)])
        self.assertIsInstance(self.app.pantalla, P.PantallaCodiceGuia)
        self.cuadros(1, [tecla(pygame.K_ESCAPE)])
        self.assertIs(self.app.pantalla, juego)


if __name__ == "__main__":
    unittest.main()
