"""Arte procedural en baja resolución para escenas pixeladas del juego."""

import math
import random
from pathlib import Path

import pygame


class EscenaMenuPixel:
    """Fondo animado del menú: ruinas, viajero, hoguera, pinos, luna y árbol antiguo."""

    TAM = (550, 360)

    def __init__(self):
        """Crea el fondo pixelado, las estrellas y las brasas del menú. Recibe: nada. Devuelve: nada (constructor)."""
        self.base = pygame.Surface(self.TAM)
        self._crear_fondo()
        azar = random.Random(391)
        self.estrellas = [(azar.randrange(550), azar.randrange(20, 180), azar.choice((1, 1, 2)))
                          for _ in range(64)]
        self.brasas = [(azar.uniform(-1.1, 1.1), azar.uniform(0.05, 1.0),
                        azar.uniform(0.25, 1.0), azar.uniform(0, math.tau)) for _ in range(34)]

    def _crear_fondo(self):
        """Pinta una sola vez el cielo, la luna, las ruinas, los pinos y el suelo sobre self.base. Recibe/devuelve: nada."""
        s = self.base
        for y in range(360):
            k = y / 360
            c = (int(19 - 11 * k), int(37 - 22 * k), int(57 - 32 * k))
            pygame.draw.line(s, c, (0, y), (549, y))

        # Luna y cielo profundo.
        pygame.draw.circle(s, (73, 113, 132), (112, 72), 48)
        pygame.draw.circle(s, (178, 197, 157), (112, 72), 34)
        pygame.draw.rect(s, (178, 197, 157), (83, 47, 48, 48))
        for x, y, w in ((91, 57, 22), (119, 78, 14), (99, 89, 12)):
            pygame.draw.rect(s, (139, 166, 144), (x, y, w, 3))
        for x, y, r in self._puntos_cielo():
            pygame.draw.rect(s, (127, 160, 170), (x, y, r, r))

        # Montañas, bosque y castillo lejano en silueta.
        pygame.draw.polygon(s, (28, 49, 62), [(0, 156), (56, 102), (103, 154), (148, 118),
                                              (211, 166), (282, 117), (352, 159), (420, 110),
                                              (550, 162), (550, 248), (0, 248)])
        pygame.draw.rect(s, (20, 34, 46), (263, 105, 72, 75))
        pygame.draw.rect(s, (20, 34, 46), (253, 122, 92, 60))
        for x, h in ((254, 29), (271, 42), (293, 55), (317, 35)):
            pygame.draw.rect(s, (20, 34, 46), (x, 151 - h, 13, h))
            pygame.draw.polygon(s, (20, 34, 46), [(x - 3, 151 - h), (x + 6, 137 - h),
                                                  (x + 16, 151 - h)])
        for x, y in ((273, 132), (300, 128), (314, 148)):
            pygame.draw.rect(s, (181, 120, 63), (x, y, 3, 6))
        for x, y, h in ((18, 179, 72), (60, 184, 54), (118, 178, 68),
                        (182, 186, 48), (354, 180, 60), (404, 177, 75), (487, 179, 64)):
            self._pino(s, x, y, h, (18, 34, 39))

        # Camino de ceniza y ruinas en primer plano.
        pygame.draw.polygon(s, (28, 37, 37), [(0, 215), (134, 218), (236, 205), (354, 220),
                                              (550, 205), (550, 360), (0, 360)])
        pygame.draw.polygon(s, (37, 48, 45), [(150, 225), (276, 214), (390, 225), (430, 360),
                                              (90, 360)])
        for x, y, w, h in ((9, 247, 76, 26), (33, 226, 37, 18), (459, 236, 78, 25),
                           (486, 215, 48, 20), (0, 315, 86, 45), (452, 321, 98, 39)):
            pygame.draw.rect(s, (34, 48, 51), (x, y, w, h))
            pygame.draw.rect(s, (54, 68, 65), (x + 3, y + 3, max(1, w - 10), 3))
            pygame.draw.rect(s, (13, 25, 30), (x + w - 6, y + 5, 4, max(1, h - 7)))
        for x, y in ((24, 281), (74, 300), (116, 336), (429, 293), (485, 281), (519, 335),
                     (213, 331), (348, 348), (286, 311)):
            pygame.draw.rect(s, (75, 77, 65), (x, y, 23, 5))
            pygame.draw.rect(s, (18, 29, 31), (x + 4, y + 5, 4, 2))

        # Gran árbol retorcido: deja el tronco derecho libre para colgar las opciones.
        tronco = [(426, 360), (452, 360), (448, 319), (458, 286), (450, 250),
                  (471, 222), (465, 198), (488, 168), (485, 146), (506, 118),
                  (496, 108), (472, 133), (468, 169), (446, 191), (439, 222),
                  (421, 243), (425, 275), (409, 299), (418, 330)]
        pygame.draw.polygon(s, (23, 32, 32), tronco)
        pygame.draw.polygon(s, (48, 55, 46), [(433, 354), (443, 347), (436, 306),
                                              (452, 276), (443, 245), (458, 216),
                                              (450, 191), (473, 162), (470, 146),
                                              (455, 172), (438, 194), (432, 228),
                                              (414, 253), (419, 284), (405, 313)])
        ramas = [((453, 214), (407, 169), (363, 151)), ((462, 176), (431, 124), (389, 95)),
                 ((473, 148), (500, 102), (539, 78)), ((442, 231), (402, 216), (372, 194)),
                 ((487, 126), (475, 75), (448, 48)), ((446, 195), (414, 165), (395, 142))]
        for a, b, c in ramas:
            pygame.draw.lines(s, (22, 31, 32), False, (a, b, c), 9)
            pygame.draw.lines(s, (45, 51, 43), False, (a, b, c), 3)
        pygame.draw.polygon(s, (18, 28, 28), [(415, 360), (437, 339), (412, 349),
                                              (393, 360), (455, 360), (449, 341), (465, 360)])

        # Pinos cercanos enmarcan el campamento.
        for x, h, col in ((6, 212, (13, 26, 31)), (65, 154, (17, 31, 33)),
                          (529, 207, (12, 25, 29)), (384, 138, (17, 31, 34))):
            self._pino(s, x, 253, h, col)

    @staticmethod
    def _puntos_cielo():
        """Genera posiciones fijas de estrellas (semilla constante). Recibe: nada. Devuelve: lista de (x, y, tamaño)."""
        azar = random.Random(77)
        return [(azar.randrange(550), azar.randrange(175), azar.choice((1, 1, 2))) for _ in range(48)]

    @staticmethod
    def _pino(surf, x, y, alto, color):
        """Dibuja un pino por capas triangulares. Recibe: surf, x, y (base), alto y color. Devuelve: nada."""
        pygame.draw.rect(surf, (25, 28, 25), (x - 3, y - 10, 7, 13))
        niveles = max(3, alto // 27)
        for i in range(niveles):
            yy = y - alto + i * (alto // niveles)
            ancho = 8 + int((i + 1) * alto * 0.22)
            pygame.draw.polygon(surf, color, [(x, yy), (x - ancho, yy + alto // niveles + 7),
                                              (x + ancho, yy + alto // niveles + 7)])
            pygame.draw.polygon(surf, (28, 48, 48), [(x, yy + 4),
                              (x - max(2, ancho - 5), yy + alto // niveles + 4),
                              (x - 2, yy + alto // niveles - 2)])

    def dibujar(self, surf, t):
        """Dibuja un cuadro de la escena: niebla, estrellas, fogata, viajero y brasas, escalado a la superficie. Recibe: surf y t (tiempo en segundos). Devuelve: nada."""
        escena = self.base.copy()

        # Niebla en bandas pixeladas que cruza lentamente las ruinas.
        niebla = pygame.Surface(self.TAM, pygame.SRCALPHA)
        for i in range(4):
            x = int((t * (8 + i * 3) + i * 177) % 700) - 150
            y = 213 + i * 25
            pygame.draw.rect(niebla, (97, 127, 129, 21 - i * 2), (x, y, 164, 5 + i))
            pygame.draw.rect(niebla, (84, 112, 119, 13), (x - 45, y + 5, 225, 3))
        escena.blit(niebla, (0, 0))

        # Halo cálido local y luz de luna suave.
        halo = pygame.Surface(self.TAM, pygame.SRCALPHA)
        pygame.draw.circle(halo, (193, 83, 25, 24), (180, 295), 67)
        pygame.draw.circle(halo, (206, 137, 71, 15), (112, 72), 51)
        escena.blit(halo, (0, 0))

        self._viajero_sentado(escena, t)
        self._hoguera(escena, t)
        for rx, ry, speed, fase in self.brasas:
            y = 302 - ((t * speed * 34 + fase * 15) % 112)
            x = 179 + rx * (8 + (302 - y) * 0.34) + math.sin(t * 2 + fase) * 4
            brillo = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 8 + fase))
            color = (244, int(91 + 87 * brillo), int(34 + 25 * brillo))
            pygame.draw.rect(escena, color, (int(x), int(y), 2 if brillo > 0.55 else 1, 2))

        imagen = pygame.transform.scale(escena, surf.get_size())
        surf.blit(imagen, (0, 0))

    @staticmethod
    def _viajero_sentado(surf, t):
        """Dibuja al viajero encapuchado junto al fuego. Recibe: t (tiempo en segundos). Devuelve: nada."""
        rebote = int(math.sin(t * 2.2) * 1)
        pygame.draw.ellipse(surf, (11, 20, 23), (122, 307, 101, 19))
        # Capa apoyada en una piedra, hecha con grupos de píxeles.
        pygame.draw.polygon(surf, (16, 25, 30), [(145, 267 + rebote), (169, 258 + rebote),
                         (190, 267 + rebote), (203, 301), (178, 310), (139, 301)])
        pygame.draw.polygon(surf, (40, 50, 54), [(151, 269 + rebote), (170, 265 + rebote),
                         (185, 274 + rebote), (176, 291), (145, 297)])
        pygame.draw.rect(surf, (22, 29, 31), (151, 285, 13, 18))
        pygame.draw.rect(surf, (20, 28, 30), (165, 293, 24, 10))
        pygame.draw.rect(surf, (43, 50, 48), (168, 298, 22, 5))
        pygame.draw.polygon(surf, (15, 23, 28), [(150, 259 + rebote), (159, 247 + rebote),
                         (176, 245 + rebote), (187, 257 + rebote), (180, 274 + rebote),
                         (154, 274 + rebote)])
        pygame.draw.polygon(surf, (47, 58, 60), [(156, 260 + rebote), (162, 250 + rebote),
                         (174, 249 + rebote), (181, 259 + rebote), (174, 265 + rebote)])
        pygame.draw.rect(surf, (9, 16, 21), (161, 257 + rebote, 18, 11))
        pygame.draw.rect(surf, (138, 75, 39), (178, 272, 4, 18))
        pygame.draw.rect(surf, (101, 66, 37), (178, 267, 4, 7))

    @staticmethod
    def _hoguera(surf, t):
        """Dibuja la fogata con llama que parpadea. Recibe: t (tiempo en segundos). Devuelve: nada."""
        cx, cy = 184, 306
        fase = math.sin(t * 11)
        pygame.draw.ellipse(surf, (15, 22, 22), (cx - 43, cy + 5, 84, 13))
        pygame.draw.line(surf, (71, 43, 30), (cx - 23, cy + 2), (cx + 24, cy - 10), 6)
        pygame.draw.line(surf, (84, 45, 26), (cx - 21, cy - 10), (cx + 22, cy + 4), 6)
        pygame.draw.polygon(surf, (151, 52, 26), [(cx - 20, cy - 6), (cx - 9, cy - 32 - int(fase * 3)),
                         (cx - 1, cy - 10), (cx + 7, cy - 38 + int(fase * 2)), (cx + 20, cy - 4)])
        pygame.draw.polygon(surf, (232, 112, 39), [(cx - 10, cy - 4), (cx - 4, cy - 24 - int(fase * 2)),
                         (cx + 1, cy - 10), (cx + 8, cy - 28 + int(fase * 2)), (cx + 13, cy - 3)])
        pygame.draw.polygon(surf, (255, 195, 89), [(cx - 3, cy - 4), (cx + 1, cy - 16),
                                                  (cx + 6, cy - 4)])


class FondoRefugioPixel:
    """Fondo para el campamento explorable: carga LobbyWalppaper.jpg o genera fondo procedural de respaldo."""

    TAM = (1100, 720)

    def __init__(self):
        """Carga la imagen de fondo de la lobby o genera el fondo procedural si no se encuentra."""
        self.usa_imagen = False
        self.base = None
        rutas = [
            Path(__file__).parent / "LobbyWalppaper.jpg",
            Path(__file__).resolve().parent / "LobbyWalppaper.jpg",
            Path(__file__).resolve().parents[1] / "LobbyWalppaper.jpg",
            Path(__file__).resolve().parents[2] / "LobbyWalppaper.jpg",
            Path("LobbyWalppaper.jpg"),
            Path("lab_v2/interfaz/LobbyWalppaper.jpg"),
        ]
        for ruta in rutas:
            if ruta.exists():
                try:
                    img = pygame.image.load(str(ruta))
                    self.base = pygame.transform.scale(img, (1100, 720))
                    self.usa_imagen = True
                    break
                except pygame.error:
                    pass

        if not self.usa_imagen:
            self.TAM = (550, 360)
            self.base = pygame.Surface(self.TAM)
            for y in range(360):
                k = y / 360
                pygame.draw.line(self.base, (int(22 - 16 * k), int(40 - 29 * k), int(52 - 37 * k)),
                                 (0, y), (549, y))
            pygame.draw.circle(self.base, (53, 78, 85), (275, 61), 38)
            pygame.draw.circle(self.base, (127, 143, 127), (275, 61), 24)
            pygame.draw.rect(self.base, (127, 143, 127), (256, 48, 39, 27))
            pygame.draw.polygon(self.base, (21, 34, 43), [(0, 172), (82, 111), (154, 171),
                             (250, 117), (332, 168), (428, 107), (550, 171), (550, 270), (0, 270)])
            # Fortaleza del horizonte: solo se ve la silueta detrás del portón.
            pygame.draw.rect(self.base, (15, 26, 36), (224, 99, 108, 85))
            pygame.draw.rect(self.base, (15, 26, 36), (209, 121, 139, 67))
            for x, y, w, h in ((218, 88, 24, 65), (254, 72, 25, 82), (294, 91, 24, 62)):
                pygame.draw.rect(self.base, (15, 26, 36), (x, y, w, h))
                pygame.draw.polygon(self.base, (15, 26, 36), [(x - 4, y), (x + w // 2, y - 17),
                                                              (x + w + 4, y)])
            for x, y in ((233, 123), (264, 114), (302, 126)):
                pygame.draw.rect(self.base, (117, 91, 57), (x, y, 3, 8))
            for x, y, h in ((16, 213, 140), (85, 225, 116), (162, 208, 145),
                            (390, 216, 138), (470, 226, 118), (530, 202, 157)):
                EscenaMenuPixel._pino(self.base, x, y, h, (12, 25, 29))
            pygame.draw.rect(self.base, (12, 22, 25), (0, 266, 550, 94))
            for x in range(16, 550, 33):
                pygame.draw.rect(self.base, (20, 31, 31), (x, 284 + (x % 4) * 4, 17, 5))

    def dibujar(self, surf, t):
        """Dibuja el fondo con bandas de niebla en movimiento. Recibe: surf y t (tiempo en segundos). Devuelve: nada."""
        if self.usa_imagen and self.base is not None:
            surf.blit(self.base, (0, 0))
            velo = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            for i in range(4):
                x = int((t * (6 + i * 2) + i * 180) % (surf.get_width() + 240)) - 120
                pygame.draw.rect(velo, (115, 137, 132, 12), (x, 180 + i * 40, 240, 8))
            surf.blit(velo, (0, 0))
        else:
            escena = self.base.copy()
            velo = pygame.Surface(self.TAM, pygame.SRCALPHA)
            for i in range(5):
                x = int((t * (6 + i * 2) + i * 138) % 680) - 120
                pygame.draw.rect(velo, (115, 137, 132, 16), (x, 210 + i * 21, 190, 5))
            escena.blit(velo, (0, 0))
            surf.blit(pygame.transform.scale(escena, surf.get_size()), (0, 0))


def pixelar_region(surf, rect, bloque=2):
    """Reduce una región y la amplía con nearest-neighbor para crear píxeles definidos."""
    r = pygame.Rect(rect).clip(surf.get_rect())
    if r.w < bloque * 2 or r.h < bloque * 2:
        return
    chico = pygame.transform.scale(surf.subsurface(r), (max(1, r.w // bloque), max(1, r.h // bloque)))
    surf.blit(pygame.transform.scale(chico, r.size), r.topleft)
