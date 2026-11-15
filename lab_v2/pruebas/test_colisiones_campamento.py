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
        """Verifica camino continuo y despejado hasta el portón del Umbral (550, 205)."""
        self.assertTrue(es_posicion_caminable(COORD_UMBRAL[0], COORD_UMBRAL[1]))
        for y in range(205, 360, 20):
            self.assertTrue(
                es_posicion_caminable(550, y),
                f"Punto (550, {y}) del pasillo al Umbral debe ser transitable"
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
        pos_ini = (550.0, 500.0)
        nx, ny, dir_, andando = resolver_movimiento_campamento(
            pos_ini, dx=0, dy=-1, dt=0.1, velocidad=100.0
        )
        self.assertAlmostEqual(nx, 550.0)
        self.assertLess(ny, 500.0)
        self.assertTrue(andando)
        self.assertEqual(dir_, "arriba")

    def test_validar_posicion_segura(self):
        """Evalúa que validar_posicion_segura devuelva la posición si es transitable o fallback si colisiona."""
        p_ok = validar_posicion_segura((550.0, 560.0))
        self.assertEqual(p_ok, (550.0, 560.0))

        p_bad = validar_posicion_segura((-999.0, -999.0))
        self.assertEqual(p_bad, COORD_SPAWN)

        p_nan = validar_posicion_segura((float("inf"), float("nan")))
        self.assertEqual(p_nan, COORD_SPAWN)


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
