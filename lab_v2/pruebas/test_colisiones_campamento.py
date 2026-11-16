"""
test_colisiones_campamento.py
Suite de pruebas de máscara de navegación, físicas y validación de entidades (Wave 2 - [T-07] y [T-08]).
"""
import math
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from interfaz import colisiones_campamento as cc
from interfaz.colisiones_campamento import (
    ANCHO, ALTO, COORD_HOGUERA, COORD_UMBRAL, COORD_SPAWN,
    COORD_MARA, COORD_NELA, COORD_TIZON, COORD_IVO,
    es_posicion_caminable, resolver_movimiento_campamento, validar_posicion_segura
)


class TestColisionesCampamento(unittest.TestCase):
    """Pruebas unitarias de máscara de navegación y física de colisiones [T-07]."""

    def test_mascara_cargada_correctamente(self):
        """Verifica que la máscara de navegación exista y tenga dimensiones 1100x720."""
        mascara = cc._obtener_mascara()
        self.assertIsNotNone(mascara)
        self.assertEqual(mascara.get_size(), (1100, 720))

    def test_hoguera_transitable(self):
        """Verifica que el centro de la hoguera (550, 360) y su perímetro sean transitables."""
        self.assertTrue(es_posicion_caminable(COORD_HOGUERA[0], COORD_HOGUERA[1]))
        for dx, dy in ((-20, 0), (20, 0), (0, -20), (0, 20)):
            self.assertTrue(es_posicion_caminable(COORD_HOGUERA[0] + dx, COORD_HOGUERA[1] + dy))

    def test_acceso_umbral_despejado(self):
        """Verifica camino continuo y despejado hasta el portón del Umbral."""
        self.assertTrue(es_posicion_caminable(COORD_UMBRAL[0], COORD_UMBRAL[1]))
        for y in range(int(COORD_UMBRAL[1]), int(COORD_HOGUERA[1]), 20):
            self.assertTrue(
                es_posicion_caminable(COORD_UMBRAL[0], y),
                f"Punto ({COORD_UMBRAL[0]}, {y}) del pasillo al Umbral debe ser transitable"
            )

    def test_obstaculos_solidos(self):
        """Verifica que las coordenadas exteriores y sólidas devuelvan False."""
        self.assertFalse(es_posicion_caminable(-10, 300))
        self.assertFalse(es_posicion_caminable(1150, 300))
        self.assertFalse(es_posicion_caminable(550, -50))
        self.assertFalse(es_posicion_caminable(550, 800))
        self.assertFalse(es_posicion_caminable(50, 50))
        self.assertFalse(es_posicion_caminable(1050, 50))

    def test_wall_sliding_ejes(self):
        """Simula movimiento diagonal contra un obstáculo confirmando avance por ejes independientes."""
        pos_ini = (float(COORD_HOGUERA[0]), 500.0)
        nx, ny, dir_, andando = resolver_movimiento_campamento(
            pos_ini, dx=0, dy=-1, dt=0.1, velocidad=100.0
        )
        self.assertAlmostEqual(nx, float(COORD_HOGUERA[0]))
        self.assertLess(ny, 500.0)
        self.assertTrue(andando)
        self.assertEqual(dir_, "arriba")

    def test_validar_posicion_segura(self):
        """Evalúa que validar_posicion_segura devuelva la posición si es transitable o fallback si colisiona."""
        p_ok = validar_posicion_segura(COORD_SPAWN)
        self.assertEqual(p_ok, COORD_SPAWN)

        p_bad = validar_posicion_segura((-999.0, -999.0))
        self.assertEqual(p_bad, COORD_SPAWN)

        p_nan = validar_posicion_segura((float("inf"), float("nan")))
        self.assertEqual(p_nan, COORD_SPAWN)


class TestCinematicaSubsteppingYSlipping(unittest.TestCase):
    """Suite de pruebas cinemáticas de tolerancia, velocidad y esquinas [T-04] y [T-05]."""

    def _con_mascara_sintetica(self, mascara: pygame.Mask):
        """Contexto auxiliar que reemplaza temporalmente la máscara de navegación."""
        class _Ctx:
            def __enter__(self_ctx):
                self_ctx.anterior = cc._mascara
                cc._mascara = mascara
                return mascara

            def __exit__(self_ctx, exc_type, exc, tb):
                cc._mascara = self_ctx.anterior

        return _Ctx()

    def test_contrato_api_hitbox_radial(self):
        """Verifica la firma actualizada de es_posicion_caminable con muestreo radial [T-01]."""
        mascara = pygame.Mask((ANCHO, ALTO), fill=True)
        with self._con_mascara_sintetica(mascara):
            self.assertTrue(es_posicion_caminable(500.0, 360.0, radio=7.5, muestreo_radial=True))

    def test_substepping_aproximacion_milimetrica(self):
        """Ante un muro a 1.5 px, un paso de 3.0 px debe avanzar ~1.5 px (<= 0.25 px del borde)."""
        mascara = pygame.Mask((ANCHO, ALTO), fill=True)
        # Con radio=7.5, en x=501.5 el extremo derecho cae en x=509. Muro sólido desde px=509.
        for py in range(ALTO):
            for px in range(509, ANCHO):
                mascara.set_at((px, py), 0)

        with self._con_mascara_sintetica(mascara):
            nx, ny, dir_, andando = resolver_movimiento_campamento(
                (500.0, 360.0),
                dx=1.0,
                dy=0.0,
                dt=3.0 / 190.0,
                velocidad=190.0,
                radio=7.5,
            )
            avance = nx - 500.0
            self.assertTrue(andando, "El personaje debe avanzar hasta el muro mediante sub-stepping")
            self.assertGreater(avance, 1.0, "No debe frenarse en seco en 0.0 px")
            self.assertAlmostEqual(avance, 1.5, delta=0.35)
            self.assertAlmostEqual(ny, 360.0, places=4)
            self.assertEqual(dir_, "derecha")

    def test_conservacion_velocidad_deslizamiento(self):
        """En colisión diagonal contra un muro vertical, el eje Y conserva 100% de velocidad (190 * dt)."""
        mascara = pygame.Mask((ANCHO, ALTO), fill=True)
        # Muro vertical inmediato a la derecha de x=500.0 (bloquea avance en +X)
        for py in range(ALTO):
            for px in range(508, ANCHO):
                mascara.set_at((px, py), 0)

        dt = 0.1
        velocidad = 190.0
        with self._con_mascara_sintetica(mascara):
            nx, ny, _, andando = resolver_movimiento_campamento(
                (500.0, 360.0),
                dx=1.0,
                dy=1.0,
                dt=dt,
                velocidad=velocidad,
                radio=7.5,
            )
            self.assertTrue(andando)
            self.assertLessEqual(nx - 500.0, 0.5)
            self.assertAlmostEqual(
                ny - 360.0,
                velocidad * dt,
                delta=0.25,
                msg="El eje libre debe conservar la velocidad completa 190 * dt sin penalización 0.707",
            )

    def test_corner_slipping_esquinas(self):
        """Impactar cardinalmente la arista de una esquina despejada en >60% debe desviar al espacio libre."""
        mascara = pygame.Mask((ANCHO, ALTO), fill=True)
        # Esquina que roza únicamente el borde inferior derecho de la hitbox (y >= 365)
        for py in range(365, ALTO):
            for px in range(508, 560):
                mascara.set_at((px, py), 0)

        with self._con_mascara_sintetica(mascara):
            nx, ny, _, andando = resolver_movimiento_campamento(
                (500.0, 360.0),
                dx=1.0,
                dy=0.0,
                dt=0.05,
                velocidad=190.0,
                radio=7.5,
                permitir_corner_slip=True,
            )
            self.assertTrue(andando, "Corner slipping debe evitar el atasco frontal en la esquina")
            self.assertLess(ny, 360.0, "Debe deslizarse suavemente hacia arriba para rodear la esquina")

    def test_recorrido_perimetral_hoguera_y_carpas(self):
        """Recorrido perimetral 360° alrededor de hoguera (550, 360) y puestos de Mara y Nela sin atascos [T-05]."""
        objetivos = [
            ("Hoguera", COORD_HOGUERA, 45.0),
            ("Mara", COORD_MARA, 35.0),
            ("Nela", COORD_NELA, 35.0),
        ]
        pasos_angulares = 36
        dt = 1.0 / 60.0
        for nombre, (cx, cy), radio_orbita in objetivos:
            for i in range(pasos_angulares):
                theta = (2.0 * math.pi * i) / pasos_angulares
                px = cx + radio_orbita * math.cos(theta)
                py = cy + radio_orbita * math.sin(theta)
                if not es_posicion_caminable(px, py):
                    continue
                tx = -math.sin(theta)
                ty = math.cos(theta)
                nx, ny, _, andando = resolver_movimiento_campamento(
                    (px, py), dx=tx, dy=ty, dt=dt, velocidad=190.0
                )
                self.assertTrue(
                    andando and (nx != px or ny != py),
                    f"Atasco en trayectoria perimetral 360° de {nombre} en ángulo {i * 10}° ({px:.1f}, {py:.1f})",
                )


class TestValidacionCruzadaEntidades(unittest.TestCase):
    """Validación cruzada de coordenadas y radios de entidades [T-08]."""

    def test_npcs_en_posiciones_transitables(self):
        """Comprueba que todos los NPCs y Spawn caen en píxeles transitables de la máscara."""
        puestos = {
            "Mara": COORD_MARA,
            "Nela": COORD_NELA,
            "Tizón": COORD_TIZON,
            "Ivo": COORD_IVO,
            "Spawn": COORD_SPAWN,
            "Hoguera": COORD_HOGUERA,
            "Umbral": COORD_UMBRAL,
        }
        for nombre, (x, y) in puestos.items():
            self.assertTrue(
                es_posicion_caminable(x, y),
                f"El puesto de {nombre} ({x}, {y}) debe estar en zona transitable"
            )

    def test_radios_interaccion_sin_solapamiento_destructivo(self):
        """Verifica que los radios de interacción de los NPCs no se solapen (SEC-08)."""
        npcs = [
            ("Mara", COORD_MARA),
            ("Nela", COORD_NELA),
            ("Tizón", COORD_TIZON),
            ("Ivo", COORD_IVO),
        ]
        radio_interaccion = 75
        for i in range(len(npcs)):
            for j in range(i + 1, len(npcs)):
                n1, p1 = npcs[i]
                n2, p2 = npcs[j]
                dist = math.hypot(p1[0] - p2[0], p1[1] - p2[1])
                self.assertGreater(
                    dist, radio_interaccion,
                    f"Los NPCs {n1} y {n2} están demasiado cerca ({dist:.1f}px <= {radio_interaccion}px)"
                )


if __name__ == "__main__":
    unittest.main()
