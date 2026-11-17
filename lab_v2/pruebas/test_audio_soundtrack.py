"""
test_audio_soundtrack.py
Pruebas de la banda sonora: archivos de audio, pasos organicos, fader de persecucion
y musica solicitada por cada pantalla (sin ventana ni dispositivo de audio reales).
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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
    from interfaz.efectos import Sonidos
    from juego.partida import NIVELES, GANO, ATRAPADO


class _SonidoFalso:
    def __init__(self):
        self.reproducciones = 0

    def play(self):
        self.reproducciones += 1


class _CanalFalso:
    def __init__(self):
        self.ocupado = False
        self.volumenes = []
        self.paradas = 0

    def get_busy(self):
        return self.ocupado

    def set_volume(self, v):
        self.volumenes.append(v)

    def play(self, sonido, loops=0):
        self.ocupado = True

    def stop(self):
        self.ocupado = False
        self.paradas += 1


def _sonidos_falsos(pasos=4):
    """Sonidos sin audio real, con la logica de la clase verdadera."""
    s = Sonidos.__new__(Sonidos)
    s.activo = True
    s.silenciado = False
    s.sonidos_pasos = [_SonidoFalso() for _ in range(pasos)]
    s._ultimo_paso = -1
    s.canal_persecucion = _CanalFalso()
    s.sonido_persecucion = object()
    s.volumen_persecucion = 0.0
    s.pista_actual = None
    return s


@unittest.skipUnless(HAY_PYGAME, "Pygame no está instalado")
class TestAudioSoundtrack(unittest.TestCase):

    RAIZ = Path(__file__).resolve().parent.parent

    def test_localizacion_archivos_audio(self):
        # Esperado: las 6 pistas y los 4 pasos existen y el buscador los detecta
        s = Sonidos.__new__(Sonidos)
        self.assertEqual(set(Sonidos.PISTAS),
                         {"menu", "campamento", "laberinto", "persecucion", "victoria", "derrota"})
        for clave, nombres in Sonidos.PISTAS.items():
            with self.subTest(pista=clave):
                ruta = s._buscar_archivo(nombres, "musica")
                self.assertIsNotNone(ruta, "no se detecta la pista " + clave)
                self.assertTrue(os.path.isfile(ruta))
                self.assertGreater(os.path.getsize(ruta), 0)
        for i in range(1, 5):
            with self.subTest(paso=i):
                ruta = s._buscar_archivo(("paso%d" % i,), "sfx")
                self.assertIsNotNone(ruta, "no se detecta paso%d" % i)
                self.assertTrue(os.path.isfile(ruta))
        self.assertIsNone(s._buscar_archivo(("no_existe_xyz",), "sfx"))

    def test_antirepeticion_pasos(self):
        # Esperado: en 40 llamadas seguidas nunca suena el mismo paso dos veces seguidas
        s = _sonidos_falsos(4)
        secuencia = []
        for _ in range(40):
            antes = [p.reproducciones for p in s.sonidos_pasos]
            self.assertTrue(s.reproducir_paso())
            despues = [p.reproducciones for p in s.sonidos_pasos]
            cambios = [i for i in range(4) if despues[i] != antes[i]]
            self.assertEqual(len(cambios), 1)
            secuencia.append(cambios[0])
        self.assertEqual(len(secuencia), 40)
        for a, b in zip(secuencia, secuencia[1:]):
            self.assertNotEqual(a, b)
        self.assertGreater(len(set(secuencia)), 1)

    def test_antirepeticion_pasos_con_azar_adverso(self):
        # Esperado: aun si el azar eligiera siempre el primero, no hay repeticion
        s = _sonidos_falsos(4)
        with mock.patch("interfaz.efectos.random.choice", side_effect=lambda ops: ops[0]):
            secuencia = []
            for _ in range(40):
                s.reproducir_paso()
                secuencia.append(s._ultimo_paso)
        for a, b in zip(secuencia, secuencia[1:]):
            self.assertNotEqual(a, b)

    def test_fader_persecucion_atenuacion_suave(self):
        # Esperado: el volumen sube por interpolacion y baja sin saltos al llegar peligro=0
        s = _sonidos_falsos()
        dt = 1 / 60
        subida = [s.actualizar_persecucion(1.0, dt) for _ in range(120)]
        self.assertGreater(subida[0], 0.0)
        self.assertLess(subida[0], 0.2)                 # no salta de golpe al objetivo
        for a, b in zip(subida, subida[1:]):
            self.assertGreaterEqual(b, a)
        self.assertGreater(subida[-1], 0.95)
        self.assertLessEqual(subida[-1], 1.0)
        self.assertTrue(s.canal_persecucion.get_busy())

        intermedio = s.actualizar_persecucion(0.5, dt)  # peligro parcial: modula
        self.assertLess(intermedio, subida[-1])
        self.assertGreater(intermedio, 0.5)

        pico = s.volumen_persecucion
        bajada = [s.actualizar_persecucion(0.0, dt) for _ in range(600)]
        self.assertEqual(s.canal_persecucion.paradas > 0, True)
        previo = pico
        paso_max = 0.0
        for v in bajada:
            self.assertLessEqual(v, previo)
            if v > 0.0:
                paso_max = max(paso_max, previo - v)
            previo = v
        self.assertLess(paso_max, 0.05)                 # sin cortes bruscos
        self.assertGreater(bajada[0], pico * 0.9)       # el primer cuadro apenas baja
        self.assertEqual(bajada[-1], 0.0)
        self.assertFalse(s.canal_persecucion.get_busy())
        # Mientras se atenuaba, el volumen del canal se fue ajustando gradualmente
        self.assertGreater(len(s.canal_persecucion.volumenes), 100)

    def test_fader_persecucion_limites_y_silencio(self):
        # Esperado: el peligro se acota a [0,1] y silenciar lleva el volumen a 0
        s = _sonidos_falsos()
        for _ in range(300):
            v = s.actualizar_persecucion(5.0, 1 / 30)
        self.assertLessEqual(v, 1.0)
        s.silenciado = True
        for _ in range(600):
            v = s.actualizar_persecucion(1.0, 1 / 30)
        self.assertEqual(v, 0.0)


@unittest.skipUnless(HAY_PYGAME, "Pygame no está instalado")
class TestInvocacionMusicaPantallas(unittest.TestCase):

    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.antes = modulo_puntajes.ARCHIVO_POR_DEFECTO
        modulo_puntajes.ARCHIVO_POR_DEFECTO = os.path.join(self.carpeta.name, "p.txt")
        self.checkpoint_original = App._archivo_checkpoint
        App._archivo_checkpoint = staticmethod(
            lambda: Path(self.carpeta.name) / "cp" / "checkpoint.json")
        self.app = App()
        self.parche = mock.patch.object(self.app.sonidos, "reproducir_musica", create=True)
        self.musica = self.parche.start()

    def tearDown(self):
        self.parche.stop()
        App._archivo_checkpoint = staticmethod(self.checkpoint_original)
        modulo_puntajes.ARCHIVO_POR_DEFECTO = self.antes
        self.carpeta.cleanup()

    def pistas(self):
        return [c.args[0] for c in self.musica.call_args_list]

    def test_invocacion_musica_pantallas(self):
        # Esperado: cada pantalla pide su pista
        P.Menu(self.app)
        self.assertEqual(self.pistas()[-1], "menu")

        self.musica.reset_mock()
        P.Campamento(self.app)
        self.assertEqual(self.pistas()[-1], "campamento")

        self.musica.reset_mock()
        P.Niveles(self.app)
        self.assertEqual(self.pistas()[-1], "menu")

        self.musica.reset_mock()
        nivel = next(iter(NIVELES.values()))
        juego = P.Juego(self.app, nivel)
        self.assertEqual(self.pistas()[-1], "laberinto")

        self.musica.reset_mock()
        juego.partida.estado = GANO
        juego._revisar_fin()
        self.assertEqual(self.pistas(), ["victoria"])

        self.musica.reset_mock()
        juego = P.Juego(self.app, nivel)
        self.musica.reset_mock()
        juego.partida.estado = ATRAPADO
        juego._revisar_fin()
        self.assertEqual(self.pistas(), ["derrota"])

    def test_pistas_solicitadas_existen(self):
        # Esperado: todo nombre de pista pedido por las pantallas esta en el catalogo
        P.Menu(self.app)
        P.Campamento(self.app)
        juego = P.Juego(self.app, next(iter(NIVELES.values())))
        juego.partida.estado = GANO
        juego._revisar_fin()
        for pista in self.pistas():
            self.assertIn(pista, Sonidos.PISTAS)


if __name__ == "__main__":
    unittest.main()
