"""
efectos.py
Partículas (rastro, chispas, confeti) y sonidos generados por código (sin archivos de audio).
"""

import math
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
        if self.activo and not self.silenciado and nombre in self.efectos:
            self.efectos[nombre].play()

    def alternar(self):
        """Silencia o activa el sonido. Recibe: nada. Devuelve: True si queda con sonido."""
        self.silenciado = not self.silenciado
        return not self.silenciado
