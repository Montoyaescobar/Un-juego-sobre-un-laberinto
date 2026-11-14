"""
ambiente.py
Ambiente vivo del campamento: humo y chispas que suben de la fogata, luciérnagas, niebla baja,
luz cálida que parpadea y una viñeta oscura en los bordes.

Solo dibuja. No cambia ninguna regla del juego ni usa las estructuras de datos del proyecto
(las listas de aquí son partículas visuales, no parte de la lógica).

Si el computador va lento, se reduce solo (menos luciérnagas, menos humo y sin niebla).
"""

import math
import random

import pygame

from interfaz.tema import brillo


class AmbienteRefugio:
    """Efectos de atmósfera del refugio: fuego, humo, luciérnagas, niebla y viñeta."""

    def __init__(self, ancho, alto, fuego=(550, 478)):
        """
        Prepara las partículas y pinta una sola vez la niebla y la viñeta.

        Recibe:
            ancho, alto: tamaño de la pantalla en píxeles.
            fuego: posición (x, y) de la hoguera.
        Devuelve:
            Nada (constructor).
        """
        self.ancho = ancho
        self.alto = alto
        self.fuego = fuego
        self.t = 0.0
        self.efectos = True              # False = "BAJO" en Ajustes
        self.calidad = 1                 # 1 = completo; 0 = reducido (si el equipo va lento)
        self._dt_suave = 1 / 60
        self._tiempo_lento = 0.0
        azar = random.Random(5)
        self.luciernagas = [{"x": azar.uniform(60, ancho - 60), "y": azar.uniform(200, alto - 70),
                             "fase": azar.uniform(0, math.tau), "vel": azar.uniform(0.25, 0.6),
                             "rad": azar.choice((14, 20, 28))} for _ in range(22)]
        self.humo = []                   # cada una: [x, y, vx, vy, edad, vida]
        self.chispas = []                # cada una: [x, y, vx, vy, vida]
        self._acum_humo = 0.0
        self._acum_chispa = 0.0
        self._puffs = {}                 # bocanadas de humo ya pintadas, por (radio, alfa)
        self._niebla = self._crear_niebla()
        self._vineta = self._crear_vineta()

    # ---------------- preparación (se hace una sola vez) ----------------
    def _crear_niebla(self):
        """
        (Interno) Pinta una banda de niebla suave y transparente.

        Recibe: nada.
        Devuelve:
            Una Surface con transparencia por píxel.
        """
        ancho, alto = 460, 90
        s = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        pasos = 18
        for i in range(pasos):
            k = i / pasos                                   # 0 en el borde, casi 1 en el centro
            r = pygame.Rect(0, 0, int(ancho * (1 - k * 0.9)), int(alto * (1 - k * 0.9)))
            r.center = (ancho // 2, alto // 2)
            pygame.draw.ellipse(s, (125, 145, 140, int(34 * (k ** 1.3)) + 2), r)
        return s

    def _crear_vineta(self):
        """
        (Interno) Pinta la viñeta: bordes y esquinas oscuros, centro limpio.

        Recibe: nada.
        Devuelve:
            Una Surface del tamaño de la pantalla con transparencia por píxel.
        """
        w, h = self.ancho // 8, self.alto // 8
        chica = pygame.Surface((w, h), pygame.SRCALPHA)
        for yy in range(h):
            for xx in range(w):
                dx = (xx + 0.5) / w * 2 - 1
                dy = (yy + 0.5) / h * 2 - 1
                d = math.hypot(dx * 0.9, dy)
                a = max(0.0, min(1.0, (d - 0.55) / 0.75)) ** 1.7
                chica.set_at((xx, yy), (2, 4, 8, int(175 * a)))
        return pygame.transform.smoothscale(chica, (self.ancho, self.alto))

    def _puff(self, radio, alfa):
        """
        (Interno) Devuelve una bocanada de humo (círculo suave y transparente), pintándola solo
        la primera vez que se pide ese tamaño y esa transparencia.

        Recibe:
            radio: radio en píxeles.
            alfa: transparencia máxima del centro (0 a 255).
        Devuelve:
            Una Surface con transparencia por píxel.
        """
        clave = (radio, alfa)
        s = self._puffs.get(clave)
        if s is None:
            s = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
            for r in range(radio, 0, -1):
                k = (1 - r / radio) ** 0.9
                pygame.draw.circle(s, (150, 152, 148, int(alfa * k)), (radio, radio), r)
            self._puffs[clave] = s
        return s

    def _pleno(self):
        """(Interno) True si se dibujan todos los efectos (no va lento y no se eligió "BAJO")."""
        return bool(self.efectos and self.calidad)

    # ---------------- animación ----------------
    def actualizar(self, dt, efectos=True):
        """
        Mueve el humo, las chispas y las luciérnagas, y baja la calidad si va lento.

        Recibe:
            dt: segundos desde el cuadro anterior.
            efectos: False cuando en Ajustes se eligieron los efectos "BAJO".
        Devuelve:
            Nada.
        """
        dt = min(dt, 0.1)
        self.t += dt
        self.efectos = efectos
        self._dt_suave += (dt - self._dt_suave) * 0.05
        if self.calidad and self._dt_suave > 1 / 28:         # menos de ~28 cuadros por segundo
            self._tiempo_lento += dt
            if self._tiempo_lento > 2.0:
                self.calidad = 0
        else:
            self._tiempo_lento = max(0.0, self._tiempo_lento - dt)

        fx, fy = self.fuego
        viento = 14 * math.sin(self.t * 0.35) + 8

        self._acum_humo += dt * (9 if self._pleno() else 4)
        while self._acum_humo >= 1:
            self._acum_humo -= 1
            if len(self.humo) < 60:
                self.humo.append([fx + random.uniform(-9, 9), fy - 30, random.uniform(-4, 4),
                                  random.uniform(-42, -26), 0.0, random.uniform(2.6, 3.8)])
        vivas = []
        for p in self.humo:
            p[4] += dt
            if p[4] < p[5]:
                p[0] += (p[2] + viento * (p[4] / p[5])) * dt
                p[1] += p[3] * dt
                vivas.append(p)
        self.humo = vivas

        self._acum_chispa += dt * 6
        while self._acum_chispa >= 1:
            self._acum_chispa -= 1
            if len(self.chispas) < 40:
                self.chispas.append([fx + random.uniform(-12, 12), fy - 24,
                                     random.uniform(-14, 14), random.uniform(-120, -60),
                                     random.uniform(0.7, 1.4)])
        vivas = []
        for c in self.chispas:
            c[4] -= dt
            if c[4] > 0:
                c[0] += (c[2] + viento * 0.4) * dt
                c[1] += c[3] * dt
                c[3] += 40 * dt                              # suben cada vez más despacio
                vivas.append(c)
        self.chispas = vivas

        for l in self.luciernagas:
            l["x"] += math.cos(self.t * l["vel"] + l["fase"]) * 18 * dt
            l["y"] += math.sin(self.t * l["vel"] * 1.3 + l["fase"]) * 12 * dt
            l["x"] = min(self.ancho - 20, max(20, l["x"]))
            l["y"] = min(self.alto - 50, max(180, l["y"]))

    # ---------------- dibujo (se llama en este orden desde el campamento) ----------------
    def dibujar_luz(self, surf):
        """
        Suma sobre la escena la luz cálida de la fogata, que parpadea.

        Recibe:
            surf: superficie donde se dibuja.
        Devuelve:
            Nada.
        """
        fx, fy = self.fuego
        t = self.t
        parpadeo = 0.5 * math.sin(t * 9.0) + 0.3 * math.sin(t * 13.7 + 1.3) \
            + 0.2 * math.sin(t * 5.1 + 0.4)
        inten = round(round((0.26 + 0.07 * parpadeo) * 50) / 50, 2)   # pasos de 0.02: pocas luces
        brillo(surf, (fx, fy + 10), 250, (255, 140, 55), inten)
        brillo(surf, (fx, fy), 90, (255, 190, 90), round(round((0.24 + 0.06 * parpadeo) * 50) / 50, 2))

    def dibujar_niebla(self, surf):
        """
        Dibuja bandas de niebla baja que se desplazan despacio (se omite si el equipo va lento).

        Recibe:
            surf: superficie donde se dibuja.
        Devuelve:
            Nada.
        """
        if not self._pleno():
            return
        for i in range(4):
            x = int((self.t * (7 + i * 3) + i * 310) % (self.ancho + 460)) - 460
            y = 330 + i * 95 + int(8 * math.sin(self.t * 0.5 + i))
            surf.blit(self._niebla, (x, y))

    def dibujar_humo(self, surf):
        """
        Dibuja el humo que sube de la fogata: crece, se ensancha y se desvanece.

        Recibe:
            surf: superficie donde se dibuja.
        Devuelve:
            Nada.
        """
        for x, y, _, _, edad, vida in self.humo:
            k = edad / vida
            radio = int(5 + 15 * k)
            alfa = (int(70 * (1 - k) ** 1.5) // 8) * 8        # pasos de 8: pocas bocanadas distintas
            if alfa < 6:
                continue
            surf.blit(self._puff(radio, alfa), (int(x) - radio, int(y) - radio))

    def dibujar_chispas(self, surf):
        """
        Dibuja las chispas naranjas que suben y se apagan.

        Recibe:
            surf: superficie donde se dibuja.
        Devuelve:
            Nada.
        """
        for x, y, _, _, vida in self.chispas:
            k = max(0.0, min(1.0, vida / 0.6))
            pygame.draw.rect(surf, (int(255 * k), int(170 * k), int(60 * k)), (int(x), int(y), 2, 2))

    def dibujar_luciernagas(self, surf):
        """
        Dibuja las luciérnagas: puntos verdes que parpadean y flotan.

        Recibe:
            surf: superficie donde se dibuja.
        Devuelve:
            Nada.
        """
        cuantas = len(self.luciernagas) if self._pleno() else len(self.luciernagas) // 2
        for l in self.luciernagas[:cuantas]:
            parpadeo = 0.5 + 0.5 * math.sin(self.t * l["vel"] * 5 + l["fase"] * 3)
            if parpadeo < 0.15:
                continue
            brillo(surf, (l["x"], l["y"]), l["rad"], (170, 255, 110), round(0.10 + 0.35 * parpadeo, 1))
            pygame.draw.rect(surf, (225, 255, 170), (int(l["x"]) - 1, int(l["y"]) - 1, 3, 3))

    def dibujar_vineta(self, surf):
        """
        Oscurece los bordes de la escena para dirigir la mirada al centro.

        Recibe:
            surf: superficie donde se dibuja.
        Devuelve:
            Nada.
        """
        surf.blit(self._vineta, (0, 0))
