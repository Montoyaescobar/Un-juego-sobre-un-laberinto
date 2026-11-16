"""
test_enemigo.py
Pruebas de los enemigos (usan la Lista Circular). Ejecutar:
    python -m unittest pruebas.test_enemigo -v
"""

import unittest
from juego.enemigo import Enemigo, crear_ruta_patrulla
from juego.laberinto import Laberinto
from juego.partida import NIVELES
from juego.solver import camino_mas_corto


def casillas(ruta):
    """Ayuda de prueba: una vuelta de la lista circular como lista de Python."""
    salida = []
    ruta.recorrer(salida.append)
    return salida


def crear_laberinto_abierto(filas=3, columnas=3):
    """Ayuda de prueba: laberinto pequeño con todas sus celdas y pasillos abiertos."""
    lab = Laberinto(filas, columnas)
    for f in range(1, lab.alto - 1):
        for c in range(1, lab.ancho - 1):
            lab.abrir(f, c)
    return lab


class TestEnemigo(unittest.TestCase):

    def test_ruta_ida_y_vuelta(self):
        # Esperado: A B C -> A B C B (la vuelta no repite los extremos)
        ruta = crear_ruta_patrulla([(1, 1), (1, 2), (1, 3)])
        self.assertEqual(casillas(ruta), [(1, 1), (1, 2), (1, 3), (1, 2)])

    def test_ruta_de_dos_casillas(self):
        # Esperado: A B
        ruta = crear_ruta_patrulla([(1, 1), (1, 2)])
        self.assertEqual(casillas(ruta), [(1, 1), (1, 2)])

    def test_enemigo_empieza_en_la_primera(self):
        # Esperado: la posición inicial es el inicio de la ruta
        e = Enemigo(crear_ruta_patrulla([(1, 1), (1, 2), (1, 3)]))
        self.assertEqual(e.posicion, (1, 1))

    def test_patrulla_sin_fin(self):
        # Esperado: da la vuelta y vuelve al inicio (propiedad de la lista circular)
        e = Enemigo(crear_ruta_patrulla([(1, 1), (1, 2), (1, 3)]))
        vistas = [e.avanzar() for _ in range(8)]
        self.assertEqual(vistas, [(1, 2), (1, 3), (1, 2), (1, 1),
                                  (1, 2), (1, 3), (1, 2), (1, 1)])

    def test_pasos_siempre_a_casillas_vecinas(self):
        # Esperado: en cada turno el enemigo se mueve exactamente 1 casilla
        e = Enemigo(crear_ruta_patrulla([(1, 1), (1, 2), (1, 3), (2, 3), (3, 3)]))
        anterior = e.posicion
        for _ in range(30):
            nueva = e.avanzar()
            self.assertEqual(abs(nueva[0] - anterior[0]) + abs(nueva[1] - anterior[1]), 1)
            anterior = nueva

    def test_acumulacion_tiempo(self):
        # Esperado: dt < intervalo_paso acumula tiempo pero no altera la posición
        lab = crear_laberinto_abierto()
        e = Enemigo(
            crear_ruta_patrulla([(1, 1), (1, 2), (1, 3)]),
            dificultad="Medio",
            intervalo_paso=0.5,
            rango_vision=7,
        )
        self.assertFalse(e.actualizar(0.2, (5, 5), lab))
        self.assertEqual(e.posicion, (1, 1))
        self.assertFalse(e.actualizar(0.2, (5, 5), lab))
        self.assertEqual(e.posicion, (1, 1))

    def test_paso_autonomo_al_vencer_intervalo(self):
        # Esperado: al acumular dt >= intervalo_paso el enemigo avanza autónomamente
        lab = crear_laberinto_abierto()
        e = Enemigo(
            crear_ruta_patrulla([(1, 1), (1, 2), (1, 3)]),
            dificultad="Medio",
            intervalo_paso=0.5,
            rango_vision=7,
        )
        self.assertFalse(e.actualizar(0.25, (5, 5), lab))
        self.assertEqual(e.posicion, (1, 1))
        self.assertTrue(e.actualizar(0.25, (5, 5), lab))
        self.assertEqual(e.posicion, (1, 2))

    def test_persecucion_bfs(self):
        # Esperado: con el jugador a 3 casillas y dentro de rango, elige la casilla
        # que reduce el camino más corto hacia el jugador (BFS) en lugar de su patrulla.
        lab = crear_laberinto_abierto()
        e = Enemigo(
            crear_ruta_patrulla([(1, 1), (2, 1)]),
            dificultad="Medio",
            intervalo_paso=0.5,
            rango_vision=7,
        )
        jugador = (1, 4)
        distancia_inicial = len(camino_mas_corto(lab, e.posicion, jugador)) - 1
        self.assertEqual(distancia_inicial, 3)

        dio_paso = e.actualizar(0.5, jugador, lab)
        self.assertTrue(dio_paso)
        self.assertEqual(e.posicion, (1, 2))
        distancia_nueva = len(camino_mas_corto(lab, e.posicion, jugador)) - 1
        self.assertLess(distancia_nueva, distancia_inicial)

    def test_enemigo_ignora_jugador_lejos(self):
        # Esperado: si el jugador está fuera de rango_vision, sigue su patrulla circular
        lab = crear_laberinto_abierto()
        e = Enemigo(
            crear_ruta_patrulla([(1, 1), (2, 1)]),
            dificultad="Fácil",
            intervalo_paso=0.5,
            rango_vision=2,
        )
        dio_paso = e.actualizar(0.5, (1, 4), lab)
        self.assertTrue(dio_paso)
        self.assertEqual(e.posicion, (2, 1))

    def test_escalado_dificultad(self):
        # Esperado: Fácil tiene un intervalo_paso mayor (más lento) que Difícil
        intervalo_facil = NIVELES["1"]["intervalo_enemigo"]
        intervalo_dificil = NIVELES["3"]["intervalo_enemigo"]
        self.assertGreater(intervalo_facil, intervalo_dificil)

        e_facil = Enemigo(
            crear_ruta_patrulla([(1, 1), (1, 2)]),
            dificultad="Fácil",
            intervalo_paso=intervalo_facil,
            rango_vision=NIVELES["1"]["rango_enemigo"],
        )
        e_dificil = Enemigo(
            crear_ruta_patrulla([(1, 1), (1, 2)]),
            dificultad="Difícil",
            intervalo_paso=intervalo_dificil,
            rango_vision=NIVELES["3"]["rango_enemigo"],
        )
        self.assertGreater(e_facil.intervalo_paso, e_dificil.intervalo_paso)


if __name__ == "__main__":
    unittest.main()
