"""
ambiente_laberinto.py
Ambiente vivo del laberinto: antorchas que parpadean con luz cálida, brasas que suben de ellas,
polvo flotando y niebla baja que se desplaza. Cada nivel usa sus propios colores (ver tema.py).

Solo dibuja. No cambia ninguna regla del juego ni usa las estructuras de datos del proyecto
(las listas de aquí son partículas visuales, no parte de la lógica).

Cuida el rendimiento: las luces parpadean con pocos tamaños distintos (así se reutilizan dibujos
guardados), hay un tope de partículas y, si el equipo va lento o el jugador elige efectos
"BAJO" en Ajustes, se quitan la niebla, el polvo y las brasas.
"""

import math
import random

import pygame

from interfaz.tema import brillo, mezclar


class AmbienteLaberinto:
    """Efectos de atmósfera de una partida: antorchas, brasas, polvo y niebla."""

    MAX_BRASAS = 60

    def __init__(self, rect, paleta, fuentes, radio_luz, semilla=11):
        """
        Prepara las partículas y pinta una sola vez la niebla.

        Recibe:
            rect: pygame.Rect del tablero en pantalla (los efectos no se salen de ahí).
            paleta: colores del nivel (ver tema.paleta_de).
            fuentes: lista de posiciones (x, y) en pantalla de las antorchas.
            radio_luz: radio en píxeles del halo cálido de cada antorcha.
            semilla: para que las fases del parpadeo siempre salgan iguales.
        Devuelve:
            Nada (constructor).
        """
        self.rect = pygame.Rect(rect)
        self.paleta = paleta
        self.fuentes = list(fuentes)
        self.radio_luz = max(8, int(radio_luz))
        self.t = 0.0
        self.efectos = True              # False = "BAJO" en Ajustes
        self.calidad = 1                 # 1 = completo; 0 = reducido (si el equipo va lento)
        self._dt_suave = 1 / 60
        self._tiempo_lento = 0.0
        azar = random.Random(semilla)
        self.fases = [azar.uniform(0, math.tau) for _ in self.fuentes]
        cantidad = max(12, min(48, self.rect.w * self.rect.h // 9000))
        self.polvo = [[azar.uniform(self.rect.left, self.rect.right),
                    azar.uniform(self.rect.top, self.rect.bottom),
                    azar.uniform(-5, 5), azar.uniform(-4, 2), azar.uniform(0, math.tau)]
                    for _ in range(cantidad)]
        self.brasas = []                 # cada una: [x, y, vx, vy, vida]
        self._acum = [0.0] * len(self.fuentes)
        self.bandas = [[azar.uniform(0, 1), azar.uniform(0.15, 0.85), azar.uniform(0.6, 1.4)]
                    for _ in range(3)]
        self._niebla = self._crear_niebla(paleta["niebla"])

    # ---------------- preparación (se hace una sola vez) ----------------
    @staticmethod
    def _crear_niebla(color):
        """
        (Interno) Pinta una banda de niebla suave y transparente.

        Recibe:
            color: tinte de la niebla (r, g, b).
        Devuelve:
            Una Surface con transparencia por píxel.
        """
        ancho, alto = 380, 80
        s = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        pasos = 16
        for i in range(pasos):
            k = i / pasos                                   # 0 en el borde, casi 1 en el centro
            r = pygame.Rect(0, 0, int(ancho * (1 - k * 0.9)), int(alto * (1 - k * 0.9)))
            r.center = (ancho // 2, alto // 2)
            pygame.draw.ellipse(s, (*color, int(30 * (k ** 1.3)) + 2), r)
        return s

    def _pleno(self):
        """(Interno) True si se pueden dibujar los efectos pesados (niebla, polvo y brasas)."""
        return bool(self.efectos and self.calidad)

    # ---------------- animación ----------------
    def factor_luz(self, indice):
        """
        Cuánto brilla una antorcha ahora: parpadea sin ritmo fijo, entre 0.85 y 1.15.
        Se redondea a pasos de 0.05 para que las luces ya dibujadas se reutilicen.

        Recibe:
            indice: número de la antorcha (la posición en la lista de fuentes).
        Devuelve:
            Un número cercano a 1.0.
        """
        t, f = self.t, self.fases[indice]
        onda = 0.5 * math.sin(t * 9.0 + f) + 0.3 * math.sin(t * 13.7 + f * 2.1) \
            + 0.2 * math.sin(t * 5.3 + f * 0.7)
        return round((1.0 + 0.15 * onda) / 0.05) * 0.05

    def luces_para_linterna(self, origen):
        """
        Las antorchas como luces de la capa oscura: huecos que crecen y se encogen al parpadear.

        Recibe:
            origen: esquina (x, y) del tablero en pantalla.
        Devuelve:
            Lista de (x, y, escala) con x, y relativos al tablero.
        """
        return [(x - origen[0], y - origen[1], self.factor_luz(i))
                for i, (x, y) in enumerate(self.fuentes)]

    def actualizar(self, dt, efectos=True):
        """
        Mueve el polvo y las brasas, y baja la calidad si el equipo va lento.

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
        if not self._pleno():
            self.brasas = []
            return

        r = self.rect
        for m in self.polvo:
            m[0] += (m[2] + math.sin(self.t * 0.6 + m[4]) * 4) * dt
            m[1] += m[3] * dt
            if m[0] < r.left:
                m[0] = r.right
            elif m[0] > r.right:
                m[0] = r.left
            if m[1] < r.top:
                m[1] = r.bottom
            elif m[1] > r.bottom:
                m[1] = r.top

        ritmo = 1.3 * self.paleta["brasas"]
        for i, (x, y) in enumerate(self.fuentes):
            self._acum[i] += dt * ritmo
            while self._acum[i] >= 1:
                self._acum[i] -= 1
                if len(self.brasas) < self.MAX_BRASAS:
                    self.brasas.append([x + random.uniform(-3, 3), y - 4,
                                        random.uniform(-9, 9), random.uniform(-38, -18),
                                        random.uniform(0.6, 1.3)])
        vivas = []
        for b in self.brasas:
            b[4] -= dt
            if b[4] > 0:
                b[0] += b[2] * dt
                b[1] += b[3] * dt
                b[3] += 16 * dt                              # suben cada vez más despacio
                vivas.append(b)
        self.brasas = vivas

    # ---------------- dibujo (en este orden desde la partida) ----------------
    def dibujar_niebla(self, surf):
        """
        Dibuja bandas de niebla baja que se desplazan despacio sobre el suelo.

        Recibe:
            surf: superficie donde se dibuja.
        Devuelve:
            Nada.
        """
        if not self._pleno():
            return
        previo = surf.get_clip()
        surf.set_clip(self.rect)
        ancho_total = self.rect.w + self._niebla.get_width()
        for i, (inicio, altura, vel) in enumerate(self.bandas):
            x = self.rect.left - self._niebla.get_width() + int(
                (inicio * ancho_total + self.t * 9 * vel) % ancho_total)
            y = self.rect.top + int(self.rect.h * altura) + int(8 * math.sin(self.t * 0.5 + i))
            surf.blit(self._niebla, (x, y))
        surf.set_clip(previo)

    def dibujar_polvo(self, surf):
        """
        Dibuja motas de polvo flotando; solo se ven donde llega la luz (se pinta antes de la oscuridad).

        Recibe:
            surf: superficie donde se dibuja.
        Devuelve:
            Nada.
        """
        if not self._pleno():
            return
        base = self.paleta["piso"]
        for x, y, _, _, fase in self.polvo:
            b = 0.5 + 0.5 * math.sin(self.t * 1.3 + fase)
            pygame.draw.rect(surf, mezclar(base, self.paleta["polvo"], 0.25 + 0.5 * b),
                            (int(x), int(y), 2, 2))

    def dibujar_luces(self, surf):
        """
        Suma sobre la imagen el halo cálido de cada antorcha (parpadea) y sus brasas.
        Se pinta DESPUÉS de la oscuridad para que la luz se vea de verdad.

        Recibe:
            surf: superficie donde se dibuja.
        Devuelve:
            Nada.
        """
        previo = surf.get_clip()
        surf.set_clip(self.rect)
        for i, (x, y) in enumerate(self.fuentes):
            f = self.factor_luz(i)
            brillo(surf, (x, y), int(self.radio_luz * (0.9 + 0.1 * f)), self.paleta["luz"],
                   round(0.30 * f, 2))
        if self._pleno():
            for x, y, _, _, vida in self.brasas:
                k = max(0.0, min(1.0, vida / 0.5))
                pygame.draw.rect(surf, mezclar((60, 20, 8), self.paleta["luz"], k),
                                (int(x), int(y), 2, 2))
        surf.set_clip(previo)
