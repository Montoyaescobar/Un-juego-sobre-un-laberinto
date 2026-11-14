"""
test_peligros.py
Pruebas de las reglas del rotor y las cuchillas (sin ventana ni Pygame).
    python -m unittest pruebas.test_peligros -v
"""

import math
import unittest

from juego.peligros import (rotor_seguro, cadena_segura, puede_cruzar_rotor,
                            resultado_cuchillas, VELOCIDAD_ROTOR, VELOCIDAD_CADENA)


def t_para(velocidad, fase, seno):
    """Ayuda de prueba: tiempo en el que sin(t * velocidad + fase) vale 'seno' (entre -1 y 1)."""
    return ((math.asin(seno) - fase) % math.tau) / velocidad


class TestPeligros(unittest.TestCase):

    def test_rotor_seguro_en_la_ventana_verde(self):
        # Esperado: con el seno en 1 el rotor deja pasar; con el seno en 0 no
        self.assertTrue(rotor_seguro(t_para(VELOCIDAD_ROTOR, 0.7, 1.0), 0.7))
        self.assertFalse(rotor_seguro(t_para(VELOCIDAD_ROTOR, 0.7, 0.0), 0.7))

    def test_cadena_segura_cuando_el_pendulo_esta_retirado(self):
        # Esperado: seno -1 (retirado a un lado) deja pasar; seno 0 (en el centro) no
        self.assertTrue(cadena_segura(t_para(VELOCIDAD_CADENA, 2.0, -1.0), 2.0))
        self.assertFalse(cadena_segura(t_para(VELOCIDAD_CADENA, 2.0, 0.0), 2.0))

    def test_rotor_exige_salto_y_ventana(self):
        # Esperado: solo cruza si está saltando y la ventana está abierta
        abierto = t_para(VELOCIDAD_ROTOR, 0.0, 1.0)
        cerrado = t_para(VELOCIDAD_ROTOR, 0.0, 0.0)
        self.assertTrue(puede_cruzar_rotor(0.5, abierto, 0.0))
        self.assertFalse(puede_cruzar_rotor(0.0, abierto, 0.0))     # sin salto
        self.assertFalse(puede_cruzar_rotor(0.5, cerrado, 0.0))     # ventana cerrada

    def test_cuchillas_sin_cadena(self):
        # Esperado: sin cadena solo importa el salto
        self.assertEqual(resultado_cuchillas(0.4, 1.0, None), "ok")
        self.assertEqual(resultado_cuchillas(0.0, 1.0, None), "cuchillas")

    def test_cuchillas_con_cadena(self):
        # Esperado: la cadena se revisa primero; con péndulo retirado y salto se pasa
        retirado = t_para(VELOCIDAD_CADENA, 0.0, 1.0)
        centro = t_para(VELOCIDAD_CADENA, 0.0, 0.0)
        self.assertEqual(resultado_cuchillas(0.4, retirado, 0.0), "ok")
        self.assertEqual(resultado_cuchillas(0.4, centro, 0.0), "cadena")
        self.assertEqual(resultado_cuchillas(0.0, centro, 0.0), "cadena")
        self.assertEqual(resultado_cuchillas(0.0, retirado, 0.0), "cuchillas")


if __name__ == "__main__":
    unittest.main()
