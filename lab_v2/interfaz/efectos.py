"""
efectos.py
Partículas (rastro, chispas, confeti) y sonidos generados por código (sin archivos de audio).
"""

import math
import os
import random
from array import array

import pygame

from interfaz.tema import mezclar, FONDO


class Particulas:
    """Sistema de partículas sencillo: cada partícula nace, se mueve y se desvanece."""

    def __init__(self):
        """Crea el sistema vacío. Recibe: nada. Devuelve: nada."""
        self.lista = []     # [x, y, vx, vy, vida, vida_max, color, tam, gravedad, forma]

    def emitir(self, x, y, color, cantidad=8, velocidad=60, vida=0.6, tam=3, gravedad=0.0):
        """
        Lanza partículas en todas direcciones.

        Recibe:
            x, y: punto de origen en pantalla.
            color: color de las partículas.
            cantidad: cuántas.
            velocidad: rapidez máxima en píxeles/segundo.
            vida: segundos que duran.
            tam: radio en píxeles.
            gravedad: aceleración hacia abajo.
        Devuelve:
            Nada.
        """
        for _ in range(cantidad):
            ang = random.uniform(0, math.tau)
            v = random.uniform(0.2, 1.0) * velocidad
            self.lista.append([x, y, math.cos(ang) * v, math.sin(ang) * v,
                               vida * random.uniform(0.6, 1.0), vida, color, tam, gravedad, "c"])

    def estela(self, x, y, color, tam=3):
        """
        Deja una partícula quieta que se apaga (rastro del jugador).

        Recibe:
            x, y: posición.
            color: color.
            tam: radio.
        Devuelve:
            Nada.
        """
        self.lista.append([x + random.uniform(-2, 2), y + random.uniform(-2, 2),
                           random.uniform(-6, 6), random.uniform(-6, 6), 0.45, 0.45, color,
                           tam, 0.0, "c"])

    def confeti(self, ancho, cantidad=140):
        """
        Lluvia de confeti desde arriba de la pantalla.

        Recibe:
            ancho: ancho de la pantalla.
            cantidad: cuántos pedacitos.
        Devuelve:
            Nada.
        """
        colores = ((255, 200, 80), (80, 220, 255), (255, 110, 160), (150, 110, 255), (90, 230, 150))
        for _ in range(cantidad):
            self.lista.append([random.uniform(0, ancho), random.uniform(-200, -10),
                               random.uniform(-40, 40), random.uniform(60, 200),
                               random.uniform(2.5, 4.5), 4.5, random.choice(colores),
                               random.randint(4, 8), 60.0, "r"])

    def actualizar(self, dt):
        """Mueve y apaga las partículas. Recibe: dt (segundos). Devuelve: nada."""
        vivas = []
        for p in self.lista:
            p[4] -= dt
            if p[4] > 0:
                p[2] *= 0.985
                p[3] += p[8] * dt
                p[0] += p[2] * dt
                p[1] += p[3] * dt
                vivas.append(p)
        self.lista = vivas

    def dibujar(self, surf):
        """Dibuja las partículas (se ven cada vez más oscuras al apagarse). Recibe: surf."""
        for x, y, _, _, vida, vida_max, color, tam, _, forma in self.lista:
            k = max(0.0, min(1.0, vida / vida_max))
            c = mezclar(FONDO, color, k)
            if forma == "c":
                pygame.draw.circle(surf, c, (int(x), int(y)), max(1, int(tam * (0.4 + 0.6 * k))))
            else:
                pygame.draw.rect(surf, c, (int(x), int(y), tam, max(2, tam // 2)))


class Sonidos:
    """Efectos de sonido generados con ondas (si no hay audio, el juego sigue en silencio)."""

    RATE = 22050

    def __init__(self):
        """
        Intenta iniciar el audio y crear los sonidos.

        Recibe: nada.
        Devuelve:
            Nada (constructor). Si falla, self.activo queda en False.
        """
        self.activo = False
        self.silenciado = False
        self.efectos = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=self.RATE, size=-16, channels=1)
            self.efectos = {
                "paso": self._crear([(190, 45)], 0.16),
                "pared": self._crear([(95, 90)], 0.22, "cuadrada"),
                "deshacer": self._crear([(360, 55), (250, 70)], 0.18),
                "pista": self._crear([(660, 70), (880, 110)], 0.2),
                "clic": self._crear([(520, 30)], 0.15),
                "ganar": self._crear([(523, 120), (659, 120), (784, 120), (1046, 320)], 0.25),
                "perder": self._crear([(330, 170), (262, 170), (196, 170), (131, 420)], 0.25,
                                      "cuadrada"),
                "guardar": self._crear([(784, 80), (1046, 200)], 0.22),
            }
            self.activo = True
        except (pygame.error, NotImplementedError, OSError):
            self.activo = False
        self._iniciar_voces()
        self._iniciar_audio_adaptativo()

    # ------------------------------------------------------------------
    # Pasos organicos, musica de fondo y audio de persecucion
    # ------------------------------------------------------------------
    CANAL_PERSECUCION = 6
    VOLUMEN_MUSICA = 0.55
    PISTAS = {
        "menu": ("musica_menu",),
        "campamento": ("musica_campamento",),
        "laberinto": ("musica_laberinto",),
        "persecucion": ("musica_persecucion", "musica_persecusion"),
        "victoria": ("musica_victoria",),
        "derrota": ("musica_derrota",),
    }

    @staticmethod
    def _carpetas_audio(sub):
        """(Interno) Carpetas donde buscar audio: sonidos/<sub>, sonidos, raiz de lab_v2 y su padre."""
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return (os.path.join(base, "sonidos", sub), os.path.join(base, "sonidos"),
                base, os.path.dirname(base))

    def _buscar_archivo(self, nombres, sub):
        """(Interno) Devuelve la ruta del primer archivo mp3 existente o None."""
        for carpeta in self._carpetas_audio(sub):
            for nombre in nombres:
                ruta = os.path.join(carpeta, nombre + ".mp3")
                if os.path.isfile(ruta):
                    return ruta
        return None

    def _iniciar_audio_adaptativo(self):
        """(Interno) Carga pasos y persecucion; reserva el canal 6. Nunca lanza errores."""
        self.sonidos_pasos = []
        self._ultimo_paso = -1
        self.canal_persecucion = None
        self.sonido_persecucion = None
        self.volumen_persecucion = 0.0
        self.pista_actual = None
        if not self.activo:
            return
        for i in range(1, 5):
            ruta = self._buscar_archivo(("paso%d" % i,), "sfx")
            if ruta:
                try:
                    self.sonidos_pasos.append(pygame.mixer.Sound(ruta))
                except (pygame.error, FileNotFoundError, OSError):
                    pass
        try:
            pygame.mixer.set_reserved(self.CANAL_PERSECUCION + 1)  # canales 0..6 reservados
            self.canal_persecucion = pygame.mixer.Channel(self.CANAL_PERSECUCION)
            ruta = self._buscar_archivo(self.PISTAS["persecucion"], "musica")
            if ruta:
                self.sonido_persecucion = pygame.mixer.Sound(ruta)
        except (pygame.error, NotImplementedError, OSError):
            self.canal_persecucion = None
            self.sonido_persecucion = None

    def reproducir_paso(self):
        """Suena un paso al azar entre los disponibles, nunca el mismo dos veces seguidas."""
        try:
            if not self.activo or self.silenciado:
                return False
            n = len(self.sonidos_pasos)
            if n == 0:
                return False
            opciones = [i for i in range(n) if i != self._ultimo_paso]
            idx = random.choice(opciones)
            self._ultimo_paso = idx
            self.sonidos_pasos[idx].play()
            return True
        except (pygame.error, AttributeError):
            return False

    def reproducir_musica(self, pista_id, bucle=True, fade_ms=1200):
        """
        Reproduce musica de fondo con fade-in (pygame.mixer.music).

        Recibe: pista_id ("menu", "campamento", "laberinto", "persecucion", "victoria",
            "derrota" o nombre de archivo), bucle, fade_ms.
        Devuelve: True si empezo a sonar; False si no hay audio o pista.
        """
        try:
            if not self.activo:
                return False
            clave = str(pista_id).lower()
            if clave == "persecusion":
                clave = "persecucion"
            nombres = self.PISTAS.get(clave, (clave, "musica_" + clave))
            ruta = self._buscar_archivo(nombres, "musica")
            if ruta is None:
                return False
            if self.pista_actual == clave and pygame.mixer.music.get_busy():
                return True
            pygame.mixer.music.set_volume(0.0 if self.silenciado else self.VOLUMEN_MUSICA)
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.play(-1 if bucle else 0, fade_ms=max(0, int(fade_ms)))
            self.pista_actual = clave
            return True
        except (pygame.error, FileNotFoundError, OSError, AttributeError):
            return False

    def detener_musica(self, fade_ms=1000):
        """Detiene la musica de fondo con fade-out. Nunca lanza errores."""
        try:
            self.pista_actual = None
            if not self.activo:
                return
            if fade_ms and fade_ms > 0:
                pygame.mixer.music.fadeout(int(fade_ms))
            else:
                pygame.mixer.music.stop()
        except (pygame.error, AttributeError):
            pass

    def actualizar_persecucion(self, nivel_peligro, dt):
        """
        Modula el volumen de la persecucion con lerp continuo hacia el peligro.

        Recibe: nivel_peligro (0 a 1), dt (segundos).
        Devuelve: el volumen actual del canal (0 a 1).
        """
        try:
            objetivo = max(0.0, min(1.0, float(nivel_peligro)))
            if self.silenciado:
                objetivo = 0.0
            # Sube rapido, baja lento para desvanecer sin cortes bruscos.
            velocidad = 4.0 if objetivo > self.volumen_persecucion else 1.5
            k = 1.0 - math.exp(-velocidad * max(0.0, float(dt)))
            self.volumen_persecucion += (objetivo - self.volumen_persecucion) * k
            if self.volumen_persecucion < 0.005 and objetivo == 0.0:
                self.volumen_persecucion = 0.0
            canal, sonido = self.canal_persecucion, self.sonido_persecucion
            if not self.activo or canal is None or sonido is None:
                return self.volumen_persecucion
            if self.volumen_persecucion > 0.0:
                if not canal.get_busy():
                    canal.set_volume(self.volumen_persecucion)
                    canal.play(sonido, loops=-1)
                canal.set_volume(self.volumen_persecucion)
            elif canal.get_busy():
                canal.stop()
            return self.volumen_persecucion
        except (pygame.error, AttributeError, TypeError, ValueError):
            return getattr(self, "volumen_persecucion", 0.0)

    VOCES = ("mara", "tizon", "nela", "ivo")

    def _iniciar_voces(self):
        """(Interno) Reserva un canal para voces y carga las pistas. Nunca lanza errores."""
        self.voces = {}
        self.canal_voz = None
        if not self.activo:
            return
        try:
            pygame.mixer.set_reserved(1)           # el canal 0 queda solo para voces
            self.canal_voz = pygame.mixer.Channel(0)
        except (pygame.error, NotImplementedError, OSError):
            self.canal_voz = None
            return
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        carpetas = (os.path.join(base, "sonidos", "voces"), base, os.path.dirname(base))
        for nombre in self.VOCES:
            for carpeta in carpetas:
                for archivo in (nombre + ".mp3", "voz" + nombre + ".mp3"):
                    ruta = os.path.join(carpeta, archivo)
                    if nombre in self.voces or not os.path.isfile(ruta):
                        continue
                    try:
                        self.voces[nombre] = pygame.mixer.Sound(ruta)
                    except (pygame.error, FileNotFoundError, OSError):
                        pass

    def reproducir_voz(self, nombre_npc):
        """
        Reproduce la voz de un personaje sin interrumpir una voz en curso (anti-spam).

        Recibe: nombre_npc ("mara", "tizon", "nela" o "ivo").
        Devuelve: True si empezo a sonar; False si el canal esta ocupado o no hay voz/audio.
        """
        try:
            if not self.activo or self.silenciado or self.canal_voz is None:
                return False
            if self.canal_voz.get_busy():
                return False
            voz = self.voces.get(str(nombre_npc).lower())
            if voz is None:
                return False
            self.canal_voz.play(voz)
            return True
        except (pygame.error, AttributeError):
            return False

    def voz_ocupada(self):
        """Devuelve True si hay una voz sonando. Recibe: nada."""
        try:
            return bool(self.canal_voz and self.canal_voz.get_busy())
        except pygame.error:
            return False

    def detener_voz(self):
        """Corta la voz actual. Recibe: nada. Devuelve: nada."""
        try:
            if self.canal_voz:
                self.canal_voz.stop()
        except pygame.error:
            pass

    def _crear(self, notas, volumen, forma="seno"):
        """
        (Interno) Construye un sonido con una lista de notas.

        Recibe:
            notas: lista de (frecuencia en Hz, duración en ms).
            volumen: 0 a 1.
            forma: "seno" o "cuadrada".
        Devuelve:
            Un pygame.mixer.Sound.
        """
        datos = array("h")
        for frecuencia, ms in notas:
            n = int(self.RATE * ms / 1000)
            for i in range(n):
                envolvente = min(1.0, i / 120, (n - i) / 400)
                onda = math.sin(math.tau * frecuencia * i / self.RATE)
                if forma == "cuadrada":
                    onda = 1.0 if onda >= 0 else -1.0
                    onda *= 0.55
                datos.append(int(32767 * volumen * max(0.0, envolvente) * onda))
        return pygame.mixer.Sound(buffer=datos.tobytes())

    def reproducir(self, nombre):
        """
        Suena un efecto.

        Recibe:
            nombre: "paso", "pared", "deshacer", "pista", "clic", "ganar", "perder" o "guardar".
        Devuelve:
            Nada.
        """
        if nombre == "paso" and self.activo and self.sonidos_pasos:
            self.reproducir_paso()
            return
        if self.activo and not self.silenciado and nombre in self.efectos:
            self.efectos[nombre].play()

    def alternar(self):
        """Silencia o activa el sonido. Recibe: nada. Devuelve: True si queda con sonido."""
        self.silenciado = not self.silenciado
        return not self.silenciado
