"""
test_interfaz.py
Pruebas de la interfaz gráfica (se ejecutan sin abrir ventana, con el controlador "dummy" de SDL).
Se omiten solas si Pygame no está instalado. Ejecutar:
    python -m unittest pruebas.test_interfaz -v
"""

import math
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
    from juego.partida import NIVELES, JUGANDO, GANO, ATRAPADO
    from juego.solver import camino_mas_corto
    from juego.enemigo import Enemigo, crear_ruta_patrulla

    FLECHAS = {(-1, 0): pygame.K_UP, (1, 0): pygame.K_DOWN, (0, -1): pygame.K_LEFT, (0, 1): pygame.K_RIGHT}


def tecla(k, caracter=""):
    """Ayuda de prueba: evento de tecla presionada."""
    return pygame.event.Event(pygame.KEYDOWN, key=k, unicode=caracter, mod=0)


@unittest.skipUnless(HAY_PYGAME, "Pygame no está instalado")
class TestInterfaz(unittest.TestCase):

    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.antes = modulo_puntajes.ARCHIVO_POR_DEFECTO
        modulo_puntajes.ARCHIVO_POR_DEFECTO = os.path.join(self.carpeta.name, "p.txt")
        # El punto seguro de la prueba se guarda en una carpeta temporal, no en %APPDATA%.
        self.checkpoint_original = App._archivo_checkpoint
        App._archivo_checkpoint = staticmethod(
            lambda: Path(self.carpeta.name) / "cp" / "checkpoint.json")
        self.app = App()

    def tearDown(self):
        App._archivo_checkpoint = staticmethod(self.checkpoint_original)
        modulo_puntajes.ARCHIVO_POR_DEFECTO = self.antes
        self.carpeta.cleanup()      # no se llama pygame.quit(): las fuentes guardadas quedarían inválidas

    def cuadros(self, n=1, eventos=()):
        """Avanza n cuadros; los eventos se entregan en el primero."""
        for i in range(n):
            self.app.paso(1 / 60, eventos if i == 0 else ())

    def siguiente_casilla(self, juego):
        """Casilla a la que llevaría el siguiente paso del camino más corto."""
        p = juego.partida
        cam = camino_mas_corto(p.laberinto, p.jugador.posicion, p.laberinto.salida)
        return cam[0], cam[1]

    def paso_optimo(self, juego, saltar_rotor=True):
        """
        Da un paso por el camino más corto con una tecla de flecha.

        El rotor bloquea una casilla de la ruta principal: si el siguiente paso entra en él y
        saltar_rotor es True, se coloca el reloj de la pantalla en la ventana verde del rotor
        y se pulsa Espacio justo antes de mover (así la prueba no depende del azar del tiempo).
        """
        actual, destino = self.siguiente_casilla(juego)
        rotor = juego.rotatoria
        if saltar_rotor and rotor and rotor["estado"] == "armada" and rotor["casilla"] == destino:
            juego.t = ((math.pi / 2 - rotor["fase"]) % math.tau) / 2.8   # sin(...) = 1
            self.cuadros(1, [tecla(pygame.K_SPACE)])
            juego.t = ((math.pi / 2 - rotor["fase"]) % math.tau) / 2.8
        d = (destino[0] - actual[0], destino[1] - actual[1])
        self.cuadros(3, [tecla(FLECHAS[d])])

    def ganar(self, juego):
        """Gana por el camino más corto, saltando el rotor cuando toca. Luego pasa la espera."""
        juego.partida.enemigos = []        # sin fantasmas: la prueba trata del flujo de ganar
        juego.vis_e = []
        while juego.partida.estado == JUGANDO:
            self.paso_optimo(juego)
        self.cuadros(90)          # pasa la espera del final

    def llegar_junto_al_rotor(self, juego):
        """Camina hasta la casilla anterior al rotor. Devuelve el rotor, o None si no hay."""
        juego.partida.enemigos = []
        juego.vis_e = []
        rotor = juego.rotatoria
        if not rotor:
            return None
        while self.siguiente_casilla(juego)[1] != rotor["casilla"]:
            self.paso_optimo(juego, saltar_rotor=False)
        return rotor

    def test_todas_las_pantallas_se_dibujan(self):
        # Esperado: ninguna pantalla lanza error al dibujarse
        pantallas = [P.Menu(self.app), P.Niveles(self.app), P.Reglas(self.app, lambda: P.Menu(self.app)),
                     P.Ranking(self.app), P.AjustesMenu(self.app), P.Creditos(self.app),
                     P.Campamento(self.app)]
        pantallas += [P.Juego(self.app, n) for n in NIVELES.values()]
        for pantalla in pantallas:
            self.app.ir_a(pantalla)
            self.cuadros(5)
        juego = P.Juego(self.app, NIVELES["1"])
        self.app.ir_a(P.Repeticion(self.app, juego.partida, lambda: P.Menu(self.app)))
        self.cuadros(5)

    def test_sonidos_creados(self):
        # Esperado: con audio disponible se crean los efectos requeridos
        self.assertTrue(self.app.sonidos.activo)
        self.assertGreaterEqual(len(self.app.sonidos.efectos), 8)
        for nombre in ("paso", "pared", "deshacer", "pista", "clic", "ganar", "perder", "guardar",
                       "hover", "conteo", "conteo_fin"):
            self.assertIn(nombre, self.app.sonidos.efectos)

    def test_ajuste_de_brillo_cicla_se_guarda_y_dibuja(self):
        # Esperado: la fila BRILLO cambia entre 3 niveles, se guarda y el laberinto se dibuja
        ajustes = P.AjustesMenu(self.app)
        self.app.ir_a(ajustes)
        inicial = self.app.brillo
        for paso in range(1, 4):
            ajustes._activar(5)
            self.assertEqual(self.app.brillo, (inicial + paso) % 3)
            self.cuadros(2)
        self.app.brillo = 2
        self.app.guardar_checkpoint((550.0, 596.0))
        self.assertEqual(App._archivo_checkpoint().exists(), True)
        self.app.ir_a(P.Juego(self.app, NIVELES["3"]))
        self.cuadros(3)

    def test_ajuste_de_efectos_alterna_y_se_guarda(self):
        # Esperado: la fila EFECTOS VISUALES alterna BAJO/ALTO, se guarda y el laberinto se dibuja
        ajustes = P.AjustesMenu(self.app)
        self.app.ir_a(ajustes)
        inicial = self.app.efectos
        ajustes._activar(6)
        self.assertEqual(self.app.efectos, 1 - inicial)
        self.cuadros(2)
        self.app.efectos = 0
        self.app.guardar_checkpoint((550.0, 596.0))
        self.app.ir_a(P.Juego(self.app, NIVELES["3"]))
        self.cuadros(10)
        self.app.efectos = 1
        self.cuadros(10)

    def test_panel_derecho_con_muchos_enemigos(self):
        # Esperado: con 6 espectros el panel se dibuja sin error (las rutas se resumen "+N")
        self.app.ir_a(P.Juego(self.app, NIVELES["3"]))
        juego = self.app.pantalla
        c = juego.partida.solucion
        juego.partida.enemigos = [Enemigo(crear_ruta_patrulla([c[2], c[1]])) for _ in range(6)]
        juego.vis_e = [[float(c[2][0]), float(c[2][1])] for _ in range(6)]
        self.cuadros(3)

    def test_continuar_depende_del_punto_seguro(self):
        # Esperado: CONTINUE solo está disponible si existe un punto seguro guardado
        self.app.punto_guardado = None
        self.assertFalse(P.Menu(self.app)._disponible(0))
        self.app.punto_guardado = (550.0, 596.0)
        self.assertTrue(P.Menu(self.app)._disponible(0))

    def test_flujo_ganar_y_guardar(self):
        # Esperado: ganar -> pide nombre -> Enter guarda en el árbol -> puesto #1
        self.app.ir_a(P.Juego(self.app, NIVELES["1"]))
        juego = self.app.pantalla
        self.ganar(juego)
        self.assertEqual(juego.partida.estado, GANO)
        self.assertEqual(juego.modo, "nombre")
        for letra in "Ana":
            self.cuadros(1, [tecla(ord(letra.lower()), letra)])
        self.cuadros(1, [tecla(pygame.K_RETURN)])
        self.assertEqual(juego.modo, "opciones")
        self.assertEqual(juego.guardado, 1)
        self.assertEqual(self.app.tabla.cantidad(), 1)
        self.assertEqual(self.app.tabla.mejor()[1], "Ana")

    def test_rotor_con_salto_deja_pasar(self):
        # Esperado: con Espacio y la ventana verde abierta el rotor queda "superada"
        self.app.ir_a(P.Juego(self.app, NIVELES["1"]))
        juego = self.app.pantalla
        rotor = self.llegar_junto_al_rotor(juego)
        if rotor is None:
            self.skipTest("este laberinto no colocó rotor")
        self.paso_optimo(juego)
        self.assertEqual(rotor["estado"], "superada")
        self.assertEqual(juego.partida.estado, JUGANDO)

    def test_rotor_sin_salto_atrapa(self):
        # Esperado: entrar al rotor sin saltar termina la partida como ATRAPADO
        self.app.ir_a(P.Juego(self.app, NIVELES["1"]))
        juego = self.app.pantalla
        rotor = self.llegar_junto_al_rotor(juego)
        if rotor is None:
            self.skipTest("este laberinto no colocó rotor")
        self.paso_optimo(juego, saltar_rotor=False)
        self.assertEqual(rotor["estado"], "fallo")
        self.assertEqual(juego.partida.estado, ATRAPADO)

    def test_aviso_si_no_se_puede_guardar_el_punto_seguro(self):
        # Esperado: si la carpeta no permite escribir, se muestra un aviso y el juego sigue
        with tempfile.TemporaryDirectory() as carpeta:
            bloqueo = Path(carpeta) / "archivo.txt"
            bloqueo.write_text("no soy una carpeta", encoding="utf-8")
            prueba = staticmethod(lambda: bloqueo / "sub" / "checkpoint.json")
            guardado = App._archivo_checkpoint
            App._archivo_checkpoint = prueba
            try:
                self.app.guardar_checkpoint((550.0, 596.0))
                self.assertGreater(self.app.aviso_tiempo, 0)
                self.assertNotEqual(self.app.aviso_guardado, "")
                self.cuadros(3)                       # dibujar el aviso no debe fallar
            finally:
                App._archivo_checkpoint = staticmethod(guardado)

    def test_nombre_invalido_no_guarda(self):
        # Esperado: vacío no guarda; el símbolo ; no se puede escribir
        self.app.ir_a(P.Juego(self.app, NIVELES["1"]))
        juego = self.app.pantalla
        self.ganar(juego)
        self.cuadros(1, [tecla(pygame.K_RETURN)])
        self.assertEqual(juego.modo, "nombre")
        self.assertNotEqual(juego.campo.error, "")
        self.cuadros(1, [tecla(ord(";"), ";")])
        self.assertEqual(juego.campo.texto, "")
        self.assertEqual(self.app.tabla.cantidad(), 0)

    def test_nombre_largo_se_limita(self):
        # Esperado: máximo 15 caracteres
        self.app.ir_a(P.Juego(self.app, NIVELES["1"]))
        juego = self.app.pantalla
        self.ganar(juego)
        for _ in range(20):
            self.cuadros(1, [tecla(ord("x"), "x")])
        self.assertEqual(len(juego.campo.texto), 15)

    def test_omitir_no_guarda(self):
        # Esperado: Esc en la fase de nombre pasa a opciones sin guardar
        self.app.ir_a(P.Juego(self.app, NIVELES["1"]))
        juego = self.app.pantalla
        self.ganar(juego)
        self.cuadros(1, [tecla(pygame.K_ESCAPE)])
        self.assertEqual(juego.modo, "opciones")
        self.assertEqual(self.app.tabla.cantidad(), 0)

    def test_derrota_por_enemigo(self):
        # Esperado: un fantasma que te alcanza termina la partida (sin pedir nombre)
        self.app.ir_a(P.Juego(self.app, NIVELES["1"]))
        juego = self.app.pantalla
        c = juego.partida.solucion
        juego.partida.enemigos = [Enemigo(crear_ruta_patrulla([c[2], c[1]]), intervalo_paso=0.05)]
        juego.vis_e = [[float(c[2][0]), float(c[2][1])]]
        d = (c[1][0] - c[0][0], c[1][1] - c[0][1])
        self.cuadros(3, [tecla(FLECHAS[d])])
        self.cuadros(90)
        self.assertEqual(juego.partida.estado, ATRAPADO)
        self.assertEqual(juego.modo, "opciones")
        self.assertEqual(self.app.tabla.cantidad(), 0)

    def test_pausa_bloquea_movimientos(self):
        # Esperado: en pausa las flechas no mueven; Esc continúa
        self.app.ir_a(P.Juego(self.app, NIVELES["1"]))
        juego = self.app.pantalla
        self.cuadros(1, [tecla(pygame.K_ESCAPE)])
        self.assertEqual(juego.modo, "pausa")
        antes = juego.partida.jugador.posicion
        for k in FLECHAS.values():
            self.cuadros(1, [tecla(k)])
        self.assertEqual(juego.partida.jugador.posicion, antes)
        self.cuadros(1, [tecla(pygame.K_ESCAPE)])
        self.assertEqual(juego.modo, "jugando")

    def test_pista_y_deshacer_desde_el_teclado(self):
        # Esperado: H da pista (cuesta 5), U deshace el último paso
        self.app.ir_a(P.Juego(self.app, NIVELES["1"]))
        juego = self.app.pantalla
        self.cuadros(1, [tecla(pygame.K_h)])
        self.assertIsNotNone(juego.partida.pista_actual)
        self.assertEqual(juego.partida.jugador.movimientos, 5)
        self.paso_optimo(juego)
        pila = juego.partida.jugador.pasos_por_deshacer()
        self.cuadros(1, [tecla(pygame.K_u)])
        self.assertEqual(juego.partida.jugador.pasos_por_deshacer(), pila - 1)

    def test_repeticion_navega_con_la_lista_doble(self):
        # Esperado: adelante / atrás / extremos / línea de tiempo mueven el cursor del historial
        self.app.ir_a(P.Juego(self.app, NIVELES["1"]))
        juego = self.app.pantalla
        for _ in range(6):
            self.paso_optimo(juego)
        rep = P.Repeticion(self.app, juego.partida, lambda: P.Menu(self.app))
        self.app.ir_a(rep)
        self.assertEqual(rep.h.indice(), 0)
        rep.adelante()
        rep.adelante()
        self.assertEqual(rep.h.indice(), 2)
        rep.atras()
        self.assertEqual(rep.h.indice(), 1)
        rep.ir_final()
        self.assertEqual(rep.h.indice(), rep.h.total() - 1)
        rep.ir_a_indice(3)
        self.assertEqual(rep.h.indice(), 3)
        rep.ir_inicio()
        self.assertEqual(rep.h.indice(), 0)
        rep.alternar()
        self.cuadros(60)
        self.assertGreater(rep.h.indice(), 0)

    def test_ranking_buscar_recorrer_y_eliminar(self):
        # Esperado: el árbol se dibuja, se puede recorrer, buscar y eliminar con confirmación
        for nombre, puntos in (("Ana", 500), ("Beto", 900), ("Cami", 300), ("Dani", 700)):
            self.app.tabla.registrar(nombre, "Fácil", puntos)
        ranking = P.Ranking(self.app)
        self.app.ir_a(ranking)
        self.cuadros(3)
        self.assertEqual(len(ranking.nodos), 4)
        ranking.recorrer("preorden")
        self.assertEqual(len(ranking.resaltar), 4)
        self.cuadros(150)
        self.assertEqual(ranking.visibles, 4)
        nid = [n["id"] for n in ranking.nodos if n["clave"] == 700][0]
        ranking.seleccionar(nid)
        self.assertEqual([ranking.por_id[i]["clave"] for i in ranking.resaltar], [500, 900, 700])
        ranking.eliminar()                         # primer clic: pide confirmar
        self.assertEqual(self.app.tabla.cantidad(), 4)
        ranking.eliminar()                         # segundo clic: elimina
        self.assertEqual(self.app.tabla.cantidad(), 3)
        self.assertIsNone(self.app.tabla.buscar(700))


if __name__ == "__main__":
    unittest.main()
