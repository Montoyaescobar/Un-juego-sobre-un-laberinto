"""
test_ambiente_pantallas.py
Pruebas del ambiente visual de las pantallas (paisaje por zona, piezas decorativas, transición
entre pantallas y pantalla final). Se ejecutan sin abrir ventana, con el controlador "dummy" de SDL.
Se omiten solas si Pygame no está instalado. Ejecutar:
    python -m unittest pruebas.test_ambiente_pantallas -v
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
    from interfaz import ambiente_pantallas as AP
    from interfaz import pantallas as P
    from interfaz.app import App, DURACION_TRANSICION
    from interfaz.tema import ANCHO, ALTO, PALETAS_NIVEL
    from juego.partida import NIVELES, GANO, ATRAPADO


@unittest.skipUnless(HAY_PYGAME, "Pygame no está instalado")
class TestFondoNivel(unittest.TestCase):

    def setUp(self):
        pygame.init()
        self.lienzo = pygame.Surface((ANCHO, ALTO))

    def test_cada_zona_tiene_acento_y_nombre(self):
        # Esperado: las tres zonas tienen color de acento y nombre propio, todos distintos
        zonas = list(PALETAS_NIVEL.keys())
        self.assertEqual(len(zonas), 3)
        self.assertEqual(len({AP.acento_de(z) for z in zonas}), 3)
        self.assertEqual(len({AP.ZONAS[z] for z in zonas}), 3)

    def test_zona_desconocida_no_falla(self):
        # Esperado: un nombre que no existe usa el acento base y un paisaje por defecto
        self.assertEqual(AP.acento_de("Imposible"), AP.ACENTO_BASE)
        AP.fondo_de("Imposible").dibujar(self.lienzo, 0.0)

    def test_fondo_se_reutiliza(self):
        # Esperado: pedir dos veces la misma zona devuelve el mismo objeto (se pinta una sola vez)
        self.assertIs(AP.fondo_de("Medio"), AP.fondo_de("Medio"))

    def test_cada_zona_se_dibuja_y_se_anima(self):
        # Esperado: ninguna zona falla al dibujarse, ni con transparencia, ni al animarse
        for nombre in PALETAS_NIVEL:
            fondo = AP.fondo_de(nombre)
            for alfa in (255, 128, 0):
                fondo.dibujar(self.lienzo, 1.5, alfa)
            antes = [m[1] for m in fondo.motas]
            fondo.actualizar(0.5)
            self.assertNotEqual(antes, [m[1] for m in fondo.motas])
            for m in fondo.motas:                      # siempre dentro de la pantalla (con margen)
                self.assertTrue(-11 <= m[1] <= ALTO + 11)

    def test_motas_suben_o_bajan_segun_la_zona(self):
        # Esperado: en Fácil y Difícil suben (y disminuye); en Medio caen (y aumenta)
        for nombre, sube in (("Fácil", True), ("Medio", False), ("Difícil", True)):
            fondo = AP.FondoNivel(nombre)
            y0 = fondo.motas[0][1]
            fondo.actualizar(0.01)
            self.assertEqual(fondo.motas[0][1] < y0, sube, nombre)

    def test_alfa_cero_no_cambia_el_lienzo_ni_el_paisaje(self):
        # Esperado: con alfa 0 no se dibuja nada y el paisaje conserva su opacidad completa
        fondo = AP.fondo_de("Fácil")
        fondo.dibujar(self.lienzo, 0.0, 0)
        fondo.dibujar(self.lienzo, 0.0, 100)
        self.assertEqual(fondo.estatico.get_alpha(), 255)

    def test_miniatura_tiene_el_tamano_pedido_y_se_guarda(self):
        # Esperado: la miniatura mide lo pedido y la segunda vez es la misma superficie
        fondo = AP.fondo_de("Difícil")
        mini = fondo.miniatura((306, 92))
        self.assertEqual(mini.get_size(), (306, 92))
        self.assertIs(fondo.miniatura((306, 92)), mini)
        self.assertEqual(fondo.miniatura((294, 80)).get_size(), (294, 80))

    def test_piezas_decorativas_se_dibujan(self):
        # Esperado: remaches, separador, rayos, ceniza y llamas no fallan con valores límite
        AP.remaches(self.lienzo, pygame.Rect(10, 10, 100, 80), (90, 80, 50))
        AP.separador(self.lienzo, 10, 200, 50, (90, 80, 50))
        for intensidad in (0.0, 0.6, 1.0):
            AP.rayos(self.lienzo, (500, 300), 2.0, (232, 177, 74), 560, 12, intensidad)
            AP.ceniza(self.lienzo, 2.0, (190, 120, 100), 46, intensidad)
        AP.llama(self.lienzo, 100, 100, (232, 98, 58), True, 0.5)
        AP.llama(self.lienzo, 100, 100, (232, 98, 58), False, 0.5)


@unittest.skipUnless(HAY_PYGAME, "Pygame no está instalado")
class TestTransicionYPantallas(unittest.TestCase):

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

    def cuadros(self, n):
        for _ in range(n):
            self.app.paso(1 / 60, ())

    def test_cambiar_de_pantalla_es_inmediato_pero_se_disuelve(self):
        # Esperado: la pantalla nueva queda activa al instante y la transición termina sola
        nueva = P.Niveles(self.app)
        self.app.ir_a(nueva)
        self.assertIs(self.app.pantalla, nueva)
        self.assertEqual(self.app.transicion, 1.0)
        self.assertIsNotNone(self.app.instantanea)
        self.cuadros(int(DURACION_TRANSICION * 60) + 3)
        self.assertEqual(self.app.transicion, 0.0)
        self.assertIsNone(self.app.instantanea)

    def test_transicion_baja_en_cada_cuadro(self):
        # Esperado: el valor baja de forma continua (nunca sube ni se salta)
        self.app.ir_a(P.Menu(self.app))
        anterior = self.app.transicion
        for _ in range(10):
            self.cuadros(1)
            self.assertLess(self.app.transicion, anterior)
            anterior = self.app.transicion

    def test_dos_cambios_seguidos_no_fallan(self):
        # Esperado: cambiar de pantalla en plena transición reinicia la disolución sin errores
        self.app.ir_a(P.Niveles(self.app))
        self.cuadros(3)
        self.app.ir_a(P.Juego(self.app, NIVELES["1"]))
        self.assertEqual(self.app.transicion, 1.0)
        self.cuadros(30)

    def test_niveles_dibuja_con_el_mouse_sobre_cada_tarjeta(self):
        # Esperado: al señalar cada tarjeta aparece el paisaje de su zona sin errores
        niveles = P.Niveles(self.app)
        self.app.ir_a(niveles)
        original = pygame.mouse.get_pos
        try:
            for i, tarjeta in enumerate(niveles.tarjetas):
                pygame.mouse.get_pos = lambda t=tarjeta: t.center
                self.cuadros(20)
                self.assertGreater(niveles.alzar[i], 0.5)
        finally:
            pygame.mouse.get_pos = original          # no afecta a las demás pruebas

    def test_cada_nivel_usa_el_paisaje_de_su_zona(self):
        # Esperado: la partida de cada nivel dibuja con el fondo de su propia zona
        for nivel in NIVELES.values():
            juego = P.Juego(self.app, nivel)
            self.assertIs(juego.zona, AP.fondo_de(nivel["nombre"]))
            self.app.ir_a(juego)
            self.cuadros(3)

    def test_menu_anima_la_tabla_elegida(self):
        # Esperado: la opción elegida se corre (hover sube) y las demás vuelven a 0
        menu = P.Menu(self.app)
        self.app.ir_a(menu)
        menu.sel = 1
        self.cuadros(30)
        self.assertGreater(menu.hover[1], 0.9)
        self.assertLess(menu.hover[0], 0.1)

    def test_pantalla_final_victoria_y_derrota_se_dibujan(self):
        # Esperado: ambos paneles finales se dibujan en todas las zonas y el puntaje sube hasta el total
        for nivel in NIVELES.values():
            for estado in (GANO, ATRAPADO):
                juego = P.Juego(self.app, nivel)
                juego.partida.estado = estado
                juego.modo = "opciones"
                juego._armar_botones_fin()
                self.app.ir_a(juego)
                self.cuadros(90)
                self.assertGreaterEqual(juego.t_fin, 1.2)
                self.assertEqual(juego.pop, 1.0)

    def test_t_fin_arranca_en_cero_y_solo_corre_en_el_panel_final(self):
        # Esperado: durante la partida t_fin no avanza; solo cuenta cuando aparece el panel final
        juego = P.Juego(self.app, NIVELES["1"])
        self.app.ir_a(juego)
        self.cuadros(10)
        self.assertEqual(juego.t_fin, 0.0)


if __name__ == "__main__":
    unittest.main()
