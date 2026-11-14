"""
test_puntajes.py
Pruebas de la tabla de puntajes (usa el Árbol BST). Ejecutar:
    python -m unittest pruebas.test_puntajes -v
"""

import os
import tempfile
import unittest
from juego.puntajes import TablaPuntajes


class TestPuntajes(unittest.TestCase):

    def setUp(self):
        # Cada prueba usa un archivo temporal propio
        self.carpeta = tempfile.TemporaryDirectory()
        self.ruta = os.path.join(self.carpeta.name, "puntajes.txt")

    def tearDown(self):
        self.carpeta.cleanup()

    def llenar(self):
        t = TablaPuntajes(self.ruta)
        for nombre, nivel, puntos in (("Ana", "Fácil", 500), ("Beto", "Medio", 900),
                                      ("Cami", "Difícil", 700), ("Dani", "Fácil", 300)):
            t.registrar(nombre, nivel, puntos)
        return t

    def test_tabla_vacia(self):
        # Esperado: sin puntajes, mejor() es None y el ranking vacío
        t = TablaPuntajes(self.ruta)
        self.assertEqual(t.cantidad(), 0)
        self.assertIsNone(t.mejor())
        self.assertEqual(t.mejores(), [])

    def test_ranking_de_mayor_a_menor(self):
        # Esperado: 900, 700, 500, 300
        t = self.llenar()
        self.assertEqual([p for p, _, _ in t.mejores()], [900, 700, 500, 300])
        self.assertEqual(t.mejor(), (900, "Beto", "Medio"))

    def test_limite_de_ranking(self):
        # Esperado: solo devuelve los N mejores
        t = self.llenar()
        self.assertEqual([p for p, _, _ in t.mejores(2)], [900, 700])

    def test_buscar(self):
        # Esperado: devuelve (nombre, nivel) o None
        t = self.llenar()
        self.assertEqual(t.buscar(700), ("Cami", "Difícil"))
        self.assertIsNone(t.buscar(1))

    def test_eliminar(self):
        # Esperado: se quita del ranking; eliminar algo que no existe da False
        t = self.llenar()
        self.assertTrue(t.eliminar(900))
        self.assertFalse(t.eliminar(900))
        self.assertEqual([p for p, _, _ in t.mejores()], [700, 500, 300])

    def test_recorridos(self):
        # Esperado: inorden ordenado de menor a mayor; los tres devuelven todos los nodos
        t = self.llenar()
        self.assertEqual([p for p, _, _ in t.recorrido("inorden")], [300, 500, 700, 900])
        self.assertEqual([p for p, _, _ in t.recorrido("preorden")], [500, 300, 900, 700])
        self.assertEqual([p for p, _, _ in t.recorrido("posorden")], [300, 700, 900, 500])
        with self.assertRaises(ValueError):
            t.recorrido("raro")

    def test_puntajes_repetidos(self):
        # Esperado: se guardan ambos
        t = TablaPuntajes(self.ruta)
        t.registrar("Ana", "Fácil", 400)
        t.registrar("Beto", "Fácil", 400)
        self.assertEqual(t.cantidad(), 2)

    def test_se_guarda_y_se_carga(self):
        # Esperado: otra tabla sobre el mismo archivo ve lo mismo y con la misma forma de árbol
        t = self.llenar()
        t2 = TablaPuntajes(self.ruta)
        self.assertEqual(t2.mejores(), t.mejores())
        self.assertEqual(t2.recorrido("preorden"), t.recorrido("preorden"))

    def test_archivo_danado_no_rompe(self):
        # Esperado: se ignoran las líneas malas y se cargan las buenas
        with open(self.ruta, "w", encoding="utf-8") as f:
            f.write("basura\n500;Fácil;Ana\nabc;Medio;Beto\n;;\n-5;Fácil;Luis\n700;Medio;Cami\n")
        t = TablaPuntajes(self.ruta)
        self.assertEqual([p for p, _, _ in t.mejores()], [700, 500])

    def test_datos_invalidos(self):
        # Esperado: ValueError y no se agrega nada
        t = TablaPuntajes(self.ruta)
        for nombre, nivel, puntos in (("", "Fácil", 10), ("A;B", "Fácil", 10),
                                      ("Ana", "Fácil", -1), ("Ana", "Fácil", "10"),
                                      ("Ana", "", 10), (None, "Fácil", 10)):
            with self.assertRaises(ValueError):
                t.registrar(nombre, nivel, puntos)
        self.assertEqual(t.cantidad(), 0)


if __name__ == "__main__":
    unittest.main()
