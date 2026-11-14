"""
tema.py
Colores, fuentes y utilidades de dibujo compartidas por toda la interfaz gráfica.

La interfaz SOLO dibuja: todas las reglas del juego y las estructuras de datos
viven en juego/ y estructuras/ (la librería gráfica no reemplaza nada de eso).
"""

import math
import random

import pygame

ANCHO, ALTO = 1100, 720

FONDO = (9, 10, 7)
FONDO_ARRIBA = (28, 43, 55)
PARED = (91, 99, 94)
PISO = (31, 37, 34)
CIAN = (187, 212, 116)        # fósforo verdoso de monitor viejo
ORO = (232, 177, 74)          # luz de farol / latón envejecido
ROJO = (200, 68, 49)          # óxido y peligro
VERDE = (151, 174, 87)
MORADO = (139, 91, 57)        # cuero y madera oscura
TEXTO = (230, 222, 190)
APAGADO = (151, 143, 111)
PANEL = (20, 21, 15)
BORDE = (92, 87, 55)

_fuentes = {}
_degradados = {}
_resplandores = {}


# Brillo del laberinto: opacidad de la capa oscura fuera de la luz (menor = se ve más).
OSCURIDAD_POR_BRILLO = (232, 196, 160)
NOMBRES_BRILLO = ("NORMAL", "ALTO", "MUY ALTO")
BRILLO_INICIAL = 1

# Efectos visuales (humo, niebla, polvo, brasas, luces que parpadean). "BAJO" es para equipos lentos.
NOMBRES_EFECTOS = ("BAJO", "ALTO")
EFECTOS_INICIAL = 1

# Colores del laberinto según el nivel: cada uno tiene su propio ambiente.
#   pared / piso: color base de la piedra y del suelo      musgo: manchas verdes o rojizas del suelo
#   luz: color de las antorchas                            niebla / polvo: tinte de la atmósfera
#   oscuridad: color de la capa oscura fuera de la luz     brasas: cuántas chispas sueltan las antorchas
PALETA_BASE = {"pared": PARED, "piso": PISO, "musgo": (62, 82, 48), "luz": ORO,
               "niebla": (125, 145, 140), "polvo": (190, 200, 150), "oscuridad": (7, 9, 4),
               "brasas": 1.0}
PALETAS_NIVEL = {
    # Fácil: bosque, piedra cubierta de musgo y luz de antorcha dorada.
    "Fácil": {"pared": (92, 112, 86), "piso": (36, 48, 34), "musgo": (74, 128, 60),
              "luz": (255, 198, 96), "niebla": (120, 170, 130), "polvo": (190, 235, 150),
              "oscuridad": (5, 12, 6), "brasas": 0.8},
    # Medio: cripta fría de piedra azulada y antorchas más anaranjadas.
    "Medio": {"pared": (82, 96, 118), "piso": (28, 36, 48), "musgo": (58, 104, 112),
              "luz": (255, 170, 84), "niebla": (110, 140, 190), "polvo": (165, 195, 245),
              "oscuridad": (4, 7, 15), "brasas": 1.0},
    # Difícil: ceniza y óxido, luz rojiza y muchas brasas.
    "Difícil": {"pared": (112, 84, 78), "piso": (42, 31, 29), "musgo": (112, 58, 40),
                "luz": (255, 122, 62), "niebla": (170, 110, 92), "polvo": (255, 155, 96),
                "oscuridad": (15, 5, 4), "brasas": 1.6},
}


def paleta_de(nombre):
    """
    Devuelve los colores del laberinto de un nivel.

    Recibe:
        nombre: nombre del nivel ("Fácil", "Medio" o "Difícil").
    Devuelve:
        Un diccionario de colores; si el nombre no existe, la paleta base (nunca falla).
    """
    return PALETAS_NIVEL.get(nombre, PALETA_BASE)


def fuente(tam, negrita=False):
    """
    Devuelve una fuente (guardada para no crearla mil veces).

    Recibe:
        tam: tamaño en píxeles.
        negrita: True para negrita.
    Devuelve:
        Un pygame.font.Font.
    """
    clave = (tam, negrita)
    if clave not in _fuentes:
        _fuentes[clave] = pygame.font.SysFont(
            "consolas,couriernew,dejavusansmono,monospace", tam, bold=negrita)
    return _fuentes[clave]


def mezclar(a, b, t):
    """
    Mezcla dos colores.

    Recibe:
        a, b: colores (r, g, b).
        t: 0 devuelve a, 1 devuelve b.
    Devuelve:
        El color mezclado.
    """
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def texto(surf, s, tam, color, pos, ancla="topleft", negrita=False, sombra=True):
    """
    Dibuja un texto.

    Recibe:
        surf: superficie donde dibujar.
        s: el texto.
        tam: tamaño de la fuente.
        color: color del texto.
        pos: posición (x, y) respecto al punto de anclaje.
        ancla: atributo del rect: "topleft", "center", "midtop", "topright"...
        negrita: True para negrita.
        sombra: True para dibujar una sombra suave.
    Devuelve:
        El rect donde quedó el texto.
    """
    f = fuente(tam, negrita)
    img = f.render(s, True, color)
    r = img.get_rect()
    setattr(r, ancla, pos)
    if sombra:
        sh = f.render(s, True, (0, 0, 0))
        sh.set_alpha(110)
        surf.blit(sh, r.move(2, 2))
    surf.blit(img, r)
    return r


def degradado(tam, arriba, abajo):
    """
    Superficie con degradado vertical (se guarda para reutilizarla).

    Recibe:
        tam: (ancho, alto).
        arriba, abajo: colores de los extremos.
    Devuelve:
        Una Surface.
    """
    clave = (tam, arriba, abajo)
    s = _degradados.get(clave)
    if s is None:
        s = pygame.Surface(tam)
        for y in range(tam[1]):
            pygame.draw.line(s, mezclar(arriba, abajo, y / max(1, tam[1] - 1)), (0, y), (tam[0], y))
        _degradados[clave] = s
    return s


def resplandor(radio, color, intensidad=1.0):
    """
    Superficie con un brillo circular para sumar a la imagen (efecto de luz).

    Recibe:
        radio: radio del brillo en píxeles.
        color: color de la luz.
        intensidad: 0 a 1.
    Devuelve:
        Una Surface (negra por fuera, se dibuja con BLEND_RGB_ADD).
    """
    radio = max(2, int(radio))
    clave = (radio, color, round(intensidad, 2))
    s = _resplandores.get(clave)
    if s is None:
        s = pygame.Surface((radio * 2, radio * 2))
        s.fill((0, 0, 0))
        for r in range(radio, 0, -2):
            k = (1 - r / radio) ** 2 * intensidad
            pygame.draw.circle(s, (min(255, int(color[0] * k)), min(255, int(color[1] * k)),
                                   min(255, int(color[2] * k))), (radio, radio), r)
        _resplandores[clave] = s
    return s


def brillo(surf, centro, radio, color, intensidad=1.0):
    """
    Suma un brillo de luz sobre la imagen.

    Recibe:
        surf: superficie.
        centro: (x, y).
        radio: radio del brillo.
        color: color de la luz.
        intensidad: 0 a 1.
    Devuelve:
        Nada.
    """
    g = resplandor(radio, color, intensidad)
    r = g.get_width() // 2
    surf.blit(g, (int(centro[0]) - r, int(centro[1]) - r), special_flags=pygame.BLEND_RGB_ADD)


def panel(surf, rect, alpha=215, borde=BORDE, radio=7, color=PANEL):
    """
    Dibuja un panel redondeado semitransparente.

    Recibe:
        surf: superficie.
        rect: pygame.Rect del panel.
        alpha: opacidad 0-255.
        borde: color del borde.
        radio: redondeo de las esquinas.
        color: color de relleno.
    Devuelve:
        Nada.
    """
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), s.get_rect(), border_radius=radio)
    pygame.draw.rect(s, (*borde, 255), s.get_rect(), width=2, border_radius=radio)
    if rect.w > 18 and rect.h > 18:
        pygame.draw.line(s, (*mezclar(borde, (220, 194, 121), 0.28), 150),
                         (radio, 2), (s.get_width() - radio, 2), 1)
    surf.blit(s, rect.topleft)


_vignetas = {}


def vineta(color, alpha_max=200):
    """
    Superficie del tamaño de la ventana con los bordes teñidos (sirve de alerta de peligro).

    Recibe:
        color: color del borde.
        alpha_max: opacidad máxima en el borde.
    Devuelve:
        Una Surface con transparencia.
    """
    clave = (color, alpha_max)
    s = _vignetas.get(clave)
    if s is None:
        s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        grosor = 90
        for i in range(grosor):
            a = int(alpha_max * (1 - i / grosor) ** 2)
            pygame.draw.rect(s, (*color, a), (i, i, ANCHO - 2 * i, ALTO - 2 * i), 1)
        _vignetas[clave] = s
    return s


class Fondo:
    """Fondo de bosque y ruinas con una fortaleza distante, niebla y ceniza."""

    def __init__(self, cantidad=70, semilla=7):
        """
        Crea las motas en posiciones al azar.

        Recibe:
            cantidad: número de motas.
            semilla: para que siempre queden igual.
        Devuelve:
            Nada (constructor).
        """
        azar = random.Random(semilla)
        self.motas = [[azar.uniform(0, ANCHO), azar.uniform(0, ALTO), azar.uniform(4, 17),
                       azar.uniform(0.7, 1.6), azar.uniform(0, 6.28)] for _ in range(cantidad)]
        self.detalle = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        # Silueta de una fortaleza y árboles altos; el tablero tapa parte del paisaje.
        pygame.draw.polygon(self.detalle, (9, 20, 31, 175),
                            [(0, 240), (120, 152), (235, 218), (362, 132), (512, 222),
                             (674, 144), (828, 228), (1005, 158), (1100, 219), (1100, 490),
                             (0, 490)])
        pygame.draw.rect(self.detalle, (8, 16, 26, 205), (475, 170, 174, 240))
        pygame.draw.rect(self.detalle, (8, 16, 26, 205), (451, 223, 222, 191))
        for x, y, w, h in ((461, 139, 42, 176), (521, 106, 48, 216), (600, 151, 43, 180)):
            pygame.draw.rect(self.detalle, (8, 16, 26, 210), (x, y, w, h))
            pygame.draw.polygon(self.detalle, (8, 16, 26, 210),
                                [(x - 9, y), (x + w // 2, y - 34), (x + w + 9, y)])
        for x, y in ((477, 187), (537, 162), (617, 201), (567, 254), (500, 284), (641, 317)):
            pygame.draw.rect(self.detalle, (164, 107, 58, 150), (x, y, 5, 11))
        for x, base, h in ((0, 560, 300), (72, 536, 248), (1040, 547, 312), (970, 565, 250)):
            pygame.draw.rect(self.detalle, (8, 18, 24, 205), (x + 16, base - 20, 12, h))
            for i in range(5):
                y = base - h + i * 52
                ancho = 22 + i * 12
                pygame.draw.polygon(self.detalle, (8, 18, 24, 205),
                                    [(x + 22, y), (x + 22 - ancho, y + 70),
                                     (x + 22 + ancho, y + 70)])
        # Ruined pillars frame the level without obscuring its center.
        for x in (18, 1060):
            pygame.draw.rect(self.detalle, (15, 27, 31, 165), (x, 322, 23, 218))
            pygame.draw.rect(self.detalle, (31, 44, 45, 175), (x - 8, 313, 39, 17))
            pygame.draw.rect(self.detalle, (9, 18, 22, 190), (x - 5, 530, 34, 14))

    def actualizar(self, dt):
        """Sube las motas despacio. Recibe: dt (segundos). Devuelve: nada."""
        for m in self.motas:
            m[1] -= m[2] * dt
            if m[1] < -10:
                m[1] = ALTO + 10

    def dibujar(self, surf, t):
        """
        Dibuja el fondo.

        Recibe:
            surf: superficie.
            t: tiempo en segundos (para el parpadeo).
        Devuelve:
            Nada.
        """
        surf.blit(degradado((ANCHO, ALTO), FONDO_ARRIBA, FONDO), (0, 0))

        # El fondo queda deliberadamente oscuro para que destaquen los elementos del nivel.
        surf.blit(self.detalle, (0, 0))
        fase = 0.5 + 0.5 * math.sin(t * 2.3)
        luz = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        pygame.draw.ellipse(luz, (139, 93, 51, int(16 + 11 * fase)), (150, 170, 800, 460))
        surf.blit(luz, (0, 0))

        # Bandas de niebla geométrica y ceniza suspendida.
        niebla = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        for i in range(4):
            x = int((t * (9 + i * 4) + i * 261) % (ANCHO + 300)) - 150
            y = 333 + i * 77
            pygame.draw.rect(niebla, (111, 140, 143, 17 - i * 2), (x, y, 260, 8 + i))
            pygame.draw.rect(niebla, (94, 122, 130, 10), (x - 65, y + 8, 330, 4))
        surf.blit(niebla, (0, 0))

        for x, y, _, tam, fase in self.motas:
            b = 0.5 + 0.5 * math.sin(t * 1.1 + fase)
            tono = mezclar((68, 90, 92), (199, 155, 93), 0.10 + 0.26 * b)
            pygame.draw.rect(surf, tono, (int(x), int(y), max(1, int(tam * 0.26)), 2))


_crt = None


def capa_crt():
    """Líneas de barrido y viñeta tenue, compartidas por todas las pantallas."""
    global _crt
    if _crt is None:
        _crt = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        for y in range(1, ALTO, 3):
            pygame.draw.line(_crt, (0, 0, 0, 20), (0, y), (ANCHO, y))
        for i in range(42):
            a = int(16 * (1 - i / 42) ** 2)
            pygame.draw.rect(_crt, (0, 0, 0, a), (i, i, ANCHO - 2 * i, ALTO - 2 * i), 1)
    return _crt


def texto_ajustado(surf, s, tam, color, pos, ancho_max, ancla="topleft", negrita=False,
                   sombra=False, tam_min=11):
    """
    Dibuja un texto que nunca se sale del ancho dado: primero achica la letra y, si aún no
    cabe, lo corta con "…".

    Recibe:
        surf, s, tam, color, pos, ancla, negrita, sombra: igual que texto().
        ancho_max: ancho máximo permitido en píxeles.
        tam_min: tamaño de letra mínimo antes de cortar el texto.
    Devuelve:
        El rect donde quedó el texto.
    """
    while tam > tam_min and fuente(tam, negrita).size(s)[0] > ancho_max:
        tam -= 1
    while len(s) > 1 and fuente(tam, negrita).size(s)[0] > ancho_max:
        s = s[:-2].rstrip() + "…"
    return texto(surf, s, tam, color, pos, ancla, negrita, sombra)
