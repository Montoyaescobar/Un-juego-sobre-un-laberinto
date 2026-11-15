"""
app.py
La aplicación gráfica: crea la ventana, lleva el ciclo principal (eventos, animación, dibujo)
y cambia entre pantallas con una transición suave.
"""

import math
import random
import sys
import json
import os
from pathlib import Path

import pygame

from juego.puntajes import TablaPuntajes
from interfaz import colisiones_campamento
from interfaz.efectos import Sonidos
from interfaz.pantallas import Menu
from interfaz.tema import (ANCHO, ALTO, ROJO, TEXTO, APAGADO, BRILLO_INICIAL, OSCURIDAD_POR_BRILLO,
                           EFECTOS_INICIAL, NOMBRES_EFECTOS, Fondo, capa_crt, panel, texto)

try:
    from interfaz.colisiones_campamento import validar_posicion_segura
except ImportError:
    validar_posicion_segura = None

DURACION_TRANSICION = 0.35      # segundos que tarda en disolverse la pantalla anterior
COORD_SPAWN_FALLBACK = (550.0, 560.0)


class App:
    """Ventana + ciclo del juego."""

    def __init__(self):
        """
        Inicia pygame, la ventana, el audio y las piezas compartidas por todas las pantallas.

        Recibe: nada.
        Devuelve: nada (constructor).
        """
        pygame.init()
        pygame.display.set_caption("LABERINTO // EL UMBRAL DE CENIZA")
        try:
            self.ventana = pygame.display.set_mode((ANCHO, ALTO), pygame.SCALED | pygame.RESIZABLE)
        except pygame.error:
            self.ventana = pygame.display.set_mode((ANCHO, ALTO))
        self.lienzo = pygame.Surface((ANCHO, ALTO))
        self.reloj = pygame.time.Clock()
        pygame.key.set_repeat(220, 85)
        self.sonidos = Sonidos()
        self.tabla = TablaPuntajes()
        self.fondo = Fondo()
        self.crt = capa_crt()
        self.ultima_partida = None
        self.antorcha_encendida = True
        self.fragmentos_mapa = 0
        self.pistas_duende = 0
        self.brillo = BRILLO_INICIAL     # 0 normal, 1 alto, 2 muy alto (se guarda)
        self.efectos = EFECTOS_INICIAL   # 0 bajo, 1 alto: humo, niebla, polvo y brasas (se guarda)
        self.aviso_guardado = ""       # texto del aviso si no se pudo guardar el punto seguro
        self.aviso_tiempo = 0.0        # segundos que le quedan al aviso en pantalla
        self.punto_guardado = self._cargar_checkpoint()
        self.corriendo = True
        self.fade = 1.0                  # solo al abrir el juego: sale del negro
        self.transicion = 0.0            # 1 = recién cambió de pantalla; baja a 0 mientras se disuelve
        self.instantanea = None          # copia del último cuadro de la pantalla anterior
        self._velo_transicion = pygame.Surface((ANCHO, ALTO))
        self._velo_transicion.fill((0, 0, 0))
        self.pantalla = Menu(self)

    def ir_a(self, pantalla):
        """
        Cambia de pantalla: la nueva queda activa al instante y la anterior se disuelve
        encima (con un leve oscurecimiento en el medio) en lugar de cambiar de golpe.

        Recibe:
            pantalla: la nueva Pantalla.
        Devuelve:
            Nada.
        """
        self.instantanea = self.lienzo.copy()
        self.transicion = 1.0
        self.pantalla = pantalla

    def salir(self):
        """Cierra el juego. Recibe/devuelve: nada."""
        self.corriendo = False

    @staticmethod
    def _archivo_checkpoint():
        """Ubicación del punto seguro del jugador, fuera de la carpeta del proyecto."""
        raiz = Path(os.environ.get("APPDATA", Path.home() / ".local" / "share"))
        return raiz / "LaberintoUmbral" / "checkpoint.json"

    def _cargar_checkpoint(self):
        """Recupera el último refugio guardado si el archivo es válido, acotando y validando la posición."""
        try:
            datos = json.loads(self._archivo_checkpoint().read_text(encoding="utf-8"))
            self.antorcha_encendida = bool(datos.get("antorcha", True))
            self.fragmentos_mapa = max(0, int(datos.get("fragmentos_mapa", 0)))
            self.pistas_duende = max(0, int(datos.get("pistas_duende", 0)))
            self.brillo = min(len(OSCURIDAD_POR_BRILLO) - 1, max(0, int(datos.get("brillo", self.brillo))))
            self.efectos = min(len(NOMBRES_EFECTOS) - 1, max(0, int(datos.get("efectos", self.efectos))))
            raw_x = float(datos["x"])
            raw_y = float(datos["y"])
            if not (math.isfinite(raw_x) and math.isfinite(raw_y)):
                return COORD_SPAWN_FALLBACK
            x = max(60.0, min(ANCHO - 60.0, raw_x))
            y = max(180.0, min(ALTO - 60.0, raw_y))
            validador = validar_posicion_segura or getattr(colisiones_campamento, "validar_posicion_segura", None)
            if callable(validador):
                pos_segura = validador((x, y))
                return (float(pos_segura[0]), float(pos_segura[1]))
            if raw_x != x or raw_y != y:
                return COORD_SPAWN_FALLBACK
            if hasattr(colisiones_campamento, "es_posicion_valida") and hasattr(colisiones_campamento, "caja_personaje"):
                caja = colisiones_campamento.caja_personaje(x, y)
                bloqueos = colisiones_campamento.obtener_bloqueos_campamento()
                limites = colisiones_campamento.obtener_limites_campamento()
                if not colisiones_campamento.es_posicion_valida(caja, bloqueos, limites):
                    return COORD_SPAWN_FALLBACK
            return (x, y)
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            return None

    def guardar_checkpoint(self, posicion):
        """Guarda la posición segura actual y la preferencia de antorcha mediante escritura atómica."""
        self.punto_guardado = (float(posicion[0]), float(posicion[1]))
        archivo = Path(self._archivo_checkpoint())
        temp_archivo = archivo.with_name(archivo.name + ".tmp")
        try:
            archivo.parent.mkdir(parents=True, exist_ok=True)
            contenido = json.dumps({"x": self.punto_guardado[0],
                                    "y": self.punto_guardado[1],
                                    "antorcha": self.antorcha_encendida,
                                    "fragmentos_mapa": self.fragmentos_mapa,
                                    "pistas_duende": self.pistas_duende,
                                    "brillo": self.brillo,
                                    "efectos": self.efectos})
            temp_archivo.write_text(contenido, encoding="utf-8")
            temp_archivo.replace(archivo)
            self.aviso_guardado = ""
            self.aviso_tiempo = 0.0
        except OSError:
            try:
                if temp_archivo.exists():
                    temp_archivo.unlink()
            except OSError:
                pass
            # La partida sigue funcionando aunque el sistema no permita guardar, pero se avisa.
            self.aviso_guardado = "No se pudo guardar tu punto seguro en esta carpeta."
            self.aviso_tiempo = 7.0

    def paso(self, dt, eventos=()):
        """
        Un cuadro del juego: procesa eventos, anima y dibuja.

        Recibe:
            dt: segundos desde el cuadro anterior.
            eventos: lista de eventos de pygame a procesar.
        Devuelve:
            Nada.
        """
        for e in eventos:
            if e.type == pygame.QUIT:
                posicion = getattr(self.pantalla, "personaje", None)
                if posicion is not None:
                    self.guardar_checkpoint(posicion)
                self.salir()
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_m and self._puede_silenciar():
                self.sonidos.alternar()
            else:
                self.pantalla.evento(e)
        self.fondo.actualizar(dt)
        self.pantalla.actualizar(dt)
        self.pantalla.dibujar(self.lienzo)
        self._dibujar_transicion(dt)
        self.lienzo.blit(self.crt, (0, 0))
        if self.fade > 0:
            self.fade = max(0.0, self.fade - dt * 4)
            self._velo_transicion.set_alpha(int(255 * self.fade))
            self.lienzo.blit(self._velo_transicion, (0, 0))
        if self.aviso_tiempo > 0:
            self.aviso_tiempo = max(0.0, self.aviso_tiempo - dt)
            self._dibujar_aviso()
        dx = dy = 0
        if self.pantalla.shake > 0.5:
            dx = random.randint(-int(self.pantalla.shake), int(self.pantalla.shake))
            dy = random.randint(-int(self.pantalla.shake), int(self.pantalla.shake))
        self.ventana.fill((0, 0, 0))
        self.ventana.blit(self.lienzo, (dx, dy))

    def _dibujar_transicion(self, dt):
        """
        (Interno) Mezcla la copia de la pantalla anterior sobre la nueva mientras dura la transición.

        Recibe:
            dt: segundos desde el cuadro anterior.
        Devuelve:
            Nada.
        """
        if self.transicion <= 0 or self.instantanea is None:
            self.transicion = 0.0
            self.instantanea = None
            return
        self.transicion = max(0.0, self.transicion - dt / DURACION_TRANSICION)
        k = self.transicion
        self.instantanea.set_alpha(int(255 * k * k * (3 - 2 * k)))     # suavizado (smoothstep)
        self.lienzo.blit(self.instantanea, (0, 0))
        oscuro = int(110 * math.sin(math.pi * k))                      # más oscuro en la mitad
        if oscuro > 0:
            self._velo_transicion.set_alpha(oscuro)
            self.lienzo.blit(self._velo_transicion, (0, 0))

    def _dibujar_aviso(self):
        """
        Dibuja arriba un cartel rojo cuando no se pudo guardar el punto seguro.

        Recibe: nada (usa self.aviso_guardado). Devuelve: nada.
        """
        marco = pygame.Rect(ANCHO // 2 - 340, 8, 680, 50)
        panel(self.lienzo, marco, 235, ROJO)
        texto(self.lienzo, self.aviso_guardado, 15, TEXTO, (ANCHO // 2, 15), "midtop",
              negrita=True, sombra=False)
        texto(self.lienzo, "Puedes seguir jugando, pero el campamento no se recordará al cerrar.",
              13, APAGADO, (ANCHO // 2, 35), "midtop", sombra=False)

    def _puede_silenciar(self):
        """(Interno) La tecla M no debe silenciar mientras se escribe el nombre."""
        return getattr(self.pantalla, "modo", "") != "nombre"

    def correr(self):
        """Ciclo principal: repite cuadros hasta que se cierre la ventana. Recibe/devuelve: nada."""
        while self.corriendo:
            dt = min(self.reloj.tick(60) / 1000.0, 0.05)
            self.paso(dt, pygame.event.get())
            pygame.display.flip()
        pygame.quit()
        sys.exit(0)
