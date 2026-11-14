"""
test_colisiones_campamento.py
Pruebas de los límites y cajas de colisión del Claro de Ceniza (interfaz/colisiones_campamento.py).
Se ejecutan sin ventana y se omiten solas si no hay Pygame:
    python -m unittest pruebas.test_colisiones_campamento -v
"""

import math
import os
import unittest
from collections import deque

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

try:
    import pygame
    HAY_PYGAME = True
except ImportError:
    HAY_PYGAME = False

if HAY_PYGAME:
    from interfaz.tema import ANCHO, ALTO
    from interfaz.colisiones_campamento import (
        CENTRO_HOGUERA, CENTRO_UMBRAL, RADIO_UMBRAL, PUNTO_INICIO, SOBREVIVIENTES, DUENDE,
        caja_personaje, es_posicion_valida, obtener_bloqueos_campamento,
        obtener_limites_campamento,
    )

PORTON_CAMPAMENTO = (444, 86, 212, 194)           # el Rect que usa pantallas.Campamento
LIMITES_ANTIGUOS = (26, 244, ANCHO - 26, ALTO - 28) if HAY_PYGAME else None


def _libre(x, y, bloqueos, limites):
    """Atajo: ¿el personaje centrado en (x, y) puede estar ahí?"""
    return es_posicion_valida(caja_personaje(x, y), bloqueos, limites)


def _alcanzables(bloqueos, limites, inicio, paso=4):
    """Inunda la rejilla de posiciones válidas desde 'inicio' (BFS). Devuelve un set de (x, y)."""
    x0, y0 = int(inicio[0]), int(inicio[1])
    vistos = {(x0, y0)}
    cola = deque([(x0, y0)])
    while cola:
        x, y = cola.popleft()
        for dx, dy in ((paso, 0), (-paso, 0), (0, paso), (0, -paso)):
            n = (x + dx, y + dy)
            if n not in vistos and _libre(n[0], n[1], bloqueos, limites):
                vistos.add(n)
                cola.append(n)
    return vistos


@unittest.skipUnless(HAY_PYGAME, "Pygame no está instalado")
class TestContrato(unittest.TestCase):

    def test_limites_es_tupla_de_cuatro_enteros(self):
        limites = obtener_limites_campamento()
        self.assertIsInstance(limites, tuple)
        self.assertEqual(len(limites), 4)
        self.assertTrue(all(isinstance(v, int) for v in limites))
        min_x, min_y, max_x, max_y = limites
        self.assertLess(min_x, max_x)
        self.assertLess(min_y, max_y)

    def test_bloqueos_son_rects_validos(self):
        for porton in (None, pygame.Rect(PORTON_CAMPAMENTO)):
            bloqueos = obtener_bloqueos_campamento(porton)
            self.assertIsInstance(bloqueos, list)
            self.assertGreater(len(bloqueos), 0)
            for r in bloqueos:
                self.assertIsInstance(r, pygame.Rect)
                self.assertGreater(r.w, 0)
                self.assertGreater(r.h, 0)

    def test_resultado_determinista_y_lista_nueva(self):
        a = obtener_bloqueos_campamento()
        b = obtener_bloqueos_campamento(pygame.Rect(PORTON_CAMPAMENTO))
        self.assertEqual(a, b)
        a.clear()
        self.assertEqual(obtener_bloqueos_campamento(), b)  # modificar una no afecta a otras

    def test_porton_sigue_al_rect_recibido(self):
        base = obtener_bloqueos_campamento(pygame.Rect(PORTON_CAMPAMENTO))[0]
        movido = obtener_bloqueos_campamento(pygame.Rect(PORTON_CAMPAMENTO).move(30, 10))[0]
        self.assertEqual(movido.topleft, (base.x + 30, base.y + 10))
        self.assertEqual(movido.size, base.size)


@unittest.skipUnless(HAY_PYGAME, "Pygame no está instalado")
class TestEsPosicionValida(unittest.TestCase):

    def setUp(self):
        self.limites = (0, 0, 100, 100)
        self.bloqueos = [pygame.Rect(40, 40, 20, 20)]

    def test_libre_dentro_de_limites(self):
        self.assertTrue(es_posicion_valida(pygame.Rect(5, 5, 10, 10), self.bloqueos, self.limites))

    def test_colision_con_bloqueo(self):
        self.assertFalse(es_posicion_valida(pygame.Rect(45, 45, 10, 10), self.bloqueos, self.limites))

    def test_tocar_el_borde_no_es_colision(self):
        # El Rect (30, 40, 10, 10) termina justo en x=40: pygame no lo considera choque.
        self.assertTrue(es_posicion_valida(pygame.Rect(30, 40, 10, 10), self.bloqueos, self.limites))

    def test_fuera_de_limites_por_el_centro(self):
        self.assertFalse(es_posicion_valida(pygame.Rect(96, 5, 10, 10), self.bloqueos, self.limites))
        self.assertFalse(es_posicion_valida(pygame.Rect(5, -10, 10, 10), self.bloqueos, self.limites))
        self.assertTrue(es_posicion_valida(pygame.Rect(95, 95, 10, 10), self.bloqueos, self.limites))

    def test_sin_bloqueos(self):
        self.assertTrue(es_posicion_valida(pygame.Rect(5, 5, 10, 10), [], self.limites))

    def test_acepta_tuplas_como_caja(self):
        self.assertFalse(es_posicion_valida((45, 45, 10, 10), self.bloqueos, self.limites))


@unittest.skipUnless(HAY_PYGAME, "Pygame no está instalado")
class TestCalibracion(unittest.TestCase):

    def setUp(self):
        self.porton = pygame.Rect(PORTON_CAMPAMENTO)
        self.bloqueos = obtener_bloqueos_campamento(self.porton)
        self.limites = obtener_limites_campamento()

    def test_limite_norte_ya_no_esta_en_244(self):
        min_x, min_y, max_x, max_y = self.limites
        self.assertLess(min_y, 244)
        self.assertGreaterEqual(min_y, 138)          # no sale del claro dibujado (y=138)
        self.assertLessEqual(min_y, 150)

    def test_limites_amplian_la_libertad(self):
        a = self.limites
        b = LIMITES_ANTIGUOS
        self.assertLessEqual(a[0], b[0])
        self.assertLessEqual(a[1], b[1])
        self.assertGreaterEqual(a[2], b[2])
        self.assertGreaterEqual(a[3], b[3])
        area_nueva = (a[2] - a[0]) * (a[3] - a[1])
        area_vieja = (b[2] - b[0]) * (b[3] - b[1])
        self.assertGreater(area_nueva, area_vieja)

    def test_hoguera_ajustada_al_fuego(self):
        hx, hy = CENTRO_HOGUERA
        cajas = [r for r in self.bloqueos if r.collidepoint(hx, hy)]
        self.assertEqual(len(cajas), 1, "Debe haber exactamente una caja sobre la hoguera")
        hoguera = cajas[0]
        self.assertLessEqual(hoguera.w, 2 * 40)       # radio ≤ 40 px
        self.assertLessEqual(hoguera.h, 2 * 40)
        self.assertGreaterEqual(hoguera.w, 2 * 30)    # pero cubre el fuego (radio ≥ 30 px)
        self.assertLess(hoguera.w * hoguera.h, 192 * 97 / 2)
        self.assertNotIn(pygame.Rect(454, 432, 192, 97), self.bloqueos)

    def test_costados_de_la_hoguera_transitables(self):
        hx, hy = CENTRO_HOGUERA
        for dx in (-70, -60, 60, 70):                 # antes se chocaba "contra el aire" aquí
            self.assertTrue(_libre(hx + dx, hy, self.bloqueos, self.limites), dx)
        self.assertTrue(_libre(hx, hy - 50, self.bloqueos, self.limites))
        self.assertTrue(_libre(hx, hy + 50, self.bloqueos, self.limites))
        self.assertFalse(_libre(hx, hy, self.bloqueos, self.limites))

    def test_porton_permite_acercarse_y_bloquea_las_puertas(self):
        ux, uy = CENTRO_UMBRAL
        mas_cerca = None
        for y in range(uy + 40, self.porton.top, -1):
            if not _libre(ux, y, self.bloqueos, self.limites):
                break
            mas_cerca = y
        self.assertIsNotNone(mas_cerca)
        self.assertLessEqual(mas_cerca, self.porton.bottom + 10)   # llega al pie de las puertas
        self.assertLess(math.hypot(0, mas_cerca - uy), RADIO_UMBRAL)
        self.assertFalse(_libre(ux, self.porton.centery, self.bloqueos, self.limites))
        self.assertFalse(_libre(ux, self.porton.bottom - 12, self.bloqueos, self.limites))

    def test_porton_no_se_infla_hacia_abajo(self):
        caja = self.bloqueos[0]
        self.assertLessEqual(caja.bottom, self.porton.bottom)
        self.assertLess(caja.bottom, self.porton.inflate(22, 18).bottom)

    def test_ningun_bloqueo_es_gigante(self):
        # Solo el portón (estructura enorme y visible) puede superar 17 000 px²;
        # el mayor resto es el cementerio cercado (260x65), menor que la vieja hoguera (192x97).
        for r in self.bloqueos[1:]:
            self.assertLess(r.w * r.h, 17000, r)
            self.assertLessEqual(r.w, 270, r)

    def test_ningun_bloqueo_fuera_de_pantalla(self):
        pantalla = pygame.Rect(0, 0, ANCHO, ALTO)
        for r in self.bloqueos:
            self.assertTrue(pantalla.contains(r), r)

    def test_objetos_visibles_siguen_bloqueando(self):
        solidos = {
            "carpa oeste": (177, 500), "entrada carpa oeste": (177, 540),
            "carpa este": (927, 445), "entrada carpa este": (927, 480),
            "caja de suministros": (857, 558), "barril": (963, 557), "mesa del mapa": (910, 597),
            "hamaca": (265, 338), "carro": (139, 590), "lápidas": (175, 290),
            "Tizón": DUENDE,
        }
        solidos.update({nombre: pos for nombre, pos in SOBREVIVIENTES.items()})
        for nombre, (x, y) in solidos.items():
            self.assertTrue(any(r.collidepoint(x, y) for r in self.bloqueos), nombre)

    def test_carpas_no_bloquean_esquinas_vacias(self):
        # Esquinas superiores de los antiguos rectángulos, fuera del triángulo dibujado.
        for x, y in ((104, 472), (250, 472), (854, 422), (990, 422)):
            self.assertTrue(_libre(x, y, self.bloqueos, self.limites), (x, y))

    def test_huecos_que_antes_eran_fantasma(self):
        # Puntos visualmente vacíos que las cajas viejas bloqueaban.
        for x, y in ((220, 630), (360, 380), (916, 556), (255, 545)):
            self.assertTrue(_libre(x, y, self.bloqueos, self.limites), (x, y))


@unittest.skipUnless(HAY_PYGAME, "Pygame no está instalado")
class TestRecorrido(unittest.TestCase):
    """Comprueba con una inundación (BFS) que no hay caminos obvios cortados."""

    @classmethod
    def setUpClass(cls):
        cls.bloqueos = obtener_bloqueos_campamento(pygame.Rect(PORTON_CAMPAMENTO))
        cls.limites = obtener_limites_campamento()
        cls.zona = _alcanzables(cls.bloqueos, cls.limites, PUNTO_INICIO)

    def _cerca(self, objetivo, radio):
        ox, oy = objetivo
        return any(math.hypot(x - ox, y - oy) < radio for x, y in self.zona)

    def test_punto_de_inicio_valido(self):
        self.assertTrue(_libre(*PUNTO_INICIO, self.bloqueos, self.limites))

    def test_se_llega_al_umbral(self):
        self.assertTrue(self._cerca(CENTRO_UMBRAL, RADIO_UMBRAL - 40))

    def test_se_llega_a_todos_los_interactuables(self):
        # Mismos centros y radios que Campamento._interactuar.
        objetivos = {
            "Mara": ((370, 443), 72), "Ivo": ((735, 526), 72), "Nela": ((302, 558), 72),
            "hamaca": ((266, 356), 120), "mapa": ((894, 536), 130),
            "hoguera": (CENTRO_HOGUERA, 125), "carro": ((138, 599), 110),
            "Tizón": (DUENDE, 85), "lápidas": ((166, 290), 140),
            "armadura oeste": ((398, 344), 62), "armadura este": ((702, 344), 62),
        }
        for nombre, (pos, radio) in objetivos.items():
            self.assertTrue(self._cerca(pos, radio), nombre)

    def test_se_rodea_la_hoguera_por_ambos_lados(self):
        hx, hy = CENTRO_HOGUERA
        oeste = any(x < hx - 40 and abs(y - hy) < 10 for x, y in self.zona)
        este = any(x > hx + 40 and abs(y - hy) < 10 for x, y in self.zona)
        norte = any(abs(x - hx) < 10 and y < hy - 30 for x, y in self.zona)
        self.assertTrue(oeste and este and norte)

    def test_zona_norte_recorrible(self):
        # Ahora se puede caminar por encima de y=244 (antes imposible).
        self.assertTrue(any(y < 244 for _, y in self.zona))
        self.assertTrue(any(y < 200 and x < 400 for x, y in self.zona))
        self.assertTrue(any(y < 200 and x > 700 for x, y in self.zona))

    def test_area_recorrible_mayor_que_la_antigua(self):
        antiguos = [pygame.Rect(444, 86, 212, 194).inflate(22, 18), pygame.Rect(95, 463, 162, 105),
                    pygame.Rect(844, 414, 154, 100), pygame.Rect(826, 533, 143, 64),
                    pygame.Rect(454, 432, 192, 97), pygame.Rect(176, 322, 178, 68),
                    pygame.Rect(354, 427, 32, 30), pygame.Rect(719, 510, 32, 30),
                    pygame.Rect(64, 568, 158, 65), pygame.Rect(286, 542, 32, 30)]
        zona_vieja = _alcanzables(antiguos, LIMITES_ANTIGUOS, PUNTO_INICIO)
        self.assertGreater(len(self.zona), len(zona_vieja))


if __name__ == "__main__":
    unittest.main()
