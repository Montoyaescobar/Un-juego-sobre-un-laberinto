"""
test_generador.py
Pruebas del generador de laberintos (usa la Pila). Ejecutar:
    python -m unittest pruebas.test_generador -v
"""

import unittest
from juego.generador import generar_laberinto
from juego.laberinto import LIBRE


def celdas_alcanzables(lab):
    """Ayuda de prueba: recorre el laberinto desde la entrada y cuenta casillas libres alcanzadas."""
    visitadas = {lab.entrada}
    pendientes = [lab.entrada]
    while pendientes:
        f, c = pendientes.pop()
        for df, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            vecina = (f + df, c + dc)
            if vecina not in visitadas and lab.es_transitable(*vecina):
                visitadas.add(vecina)
                pendientes.append(vecina)
    return len(visitadas)


class TestGenerador(unittest.TestCase):

    def test_tamano_correcto(self):
        # Esperado: alto = 2*filas+1, ancho = 2*columnas+1
        lab = generar_laberinto(5, 7, semilla=1)
        self.assertEqual(lab.alto, 11)
        self.assertEqual(lab.ancho, 15)

    def test_entrada_y_salida_libres(self):
        # Esperado: entrada y salida son caminos
        lab = generar_laberinto(8, 8, semilla=2)
        self.assertTrue(lab.es_transitable(*lab.entrada))
        self.assertTrue(lab.es_transitable(*lab.salida))

    def test_borde_siempre_pared(self):
        # Esperado: nadie se puede salir del tablero
        lab = generar_laberinto(6, 6, semilla=3)
        for c in range(lab.ancho):
            self.assertFalse(lab.es_transitable(0, c))
            self.assertFalse(lab.es_transitable(lab.alto - 1, c))
        for f in range(lab.alto):
            self.assertFalse(lab.es_transitable(f, 0))
            self.assertFalse(lab.es_transitable(f, lab.ancho - 1))

    def test_salida_alcanzable(self):
        # Esperado: desde la entrada se puede llegar a TODAS las casillas libres (incluida la salida)
        for semilla in range(20):
            lab = generar_laberinto(10, 10, semilla=semilla)
            libres = sum(fila.count(LIBRE) for fila in lab.matriz)
            self.assertEqual(celdas_alcanzables(lab), libres)

    def test_laberinto_perfecto(self):
        # Esperado: sin ciclos -> casillas libres = 2*celdas - 1 (celdas + muros abiertos)
        lab = generar_laberinto(9, 9, semilla=5)
        libres = sum(fila.count(LIBRE) for fila in lab.matriz)
        self.assertEqual(libres, 2 * 9 * 9 - 1)

    def test_misma_semilla_mismo_laberinto(self):
        # Esperado: reproducible
        a = generar_laberinto(8, 8, semilla=42)
        b = generar_laberinto(8, 8, semilla=42)
        self.assertEqual(a.matriz, b.matriz)

    def test_tamanos_invalidos(self):
        # Esperado: ValueError (el menú nunca los manda, pero la función se protege)
        for malo in (0, 1, 31, -5, "8", 3.5, None, True):
            with self.assertRaises(ValueError):
                generar_laberinto(malo, 8)
            with self.assertRaises(ValueError):
                generar_laberinto(8, malo)

    def test_tamano_minimo_y_maximo(self):
        # Esperado: 2x2 y 30x30 funcionan
        generar_laberinto(2, 2, semilla=1)
        generar_laberinto(30, 30, semilla=1)


if __name__ == "__main__":
    unittest.main()
