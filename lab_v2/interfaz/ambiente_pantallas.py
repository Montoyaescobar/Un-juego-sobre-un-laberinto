"""
ambiente_pantallas.py
Ambiente visual de las pantallas que no son el tablero: un paisaje propio para cada zona
(bosque, cripta y ruinas de ceniza) y piezas decorativas compartidas (remaches, separadores,
rayos de victoria, ceniza de derrota y llamas de dificultad).

La interfaz SOLO dibuja: aquí no hay reglas del juego ni estructuras de datos.
"""

import math
import random

import pygame

from interfaz.tema import ANCHO, ALTO, degradado, mezclar, paleta_de, brillo

# Color de acento de cada zona (nombres, brillos y bordes de sus tarjetas y del HUD).
ACENTO = {"Fácil": (126, 196, 98), "Medio": (112, 176, 214), "Difícil": (232, 98, 58)}
ACENTO_BASE = (232, 177, 74)

# Nombre de cada zona, para las tarjetas de la pantalla de niveles.
ZONAS = {"Fácil": "BOSQUE DE MUSGO", "Medio": "CRIPTA HELADA", "Difícil": "RUINAS DE CENIZA"}

HORIZONTE = 560          # altura (y) donde termina el paisaje y empieza el suelo
_fondos = {}             # un solo FondoNivel por zona (pintarlo cuesta; se reutiliza)
_capa_rayos = None       # superficie transparente compartida por rayos()


def acento_de(nombre):
    """
    Devuelve el color de acento de una zona.

    Recibe:
        nombre: nombre del nivel ("Fácil", "Medio" o "Difícil").
    Devuelve:
        Un color (r, g, b); si el nombre no existe, el dorado base (nunca falla).
    """
    return ACENTO.get(nombre, ACENTO_BASE)


def fondo_de(nombre):
    """
    Devuelve el fondo de una zona; lo crea la primera vez y después lo reutiliza.

    Recibe:
        nombre: nombre del nivel.
    Devuelve:
        Un FondoNivel.
    """
    if nombre not in _fondos:
        _fondos[nombre] = FondoNivel(nombre)
    return _fondos[nombre]


class FondoNivel:
    """Paisaje de una zona: bosque (Fácil), cripta (Medio) o ruinas de ceniza (Difícil)."""

    def __init__(self, nombre, semilla=3):
        """
        Pinta el paisaje una sola vez y reparte las motas que flotan encima.

        Recibe:
            nombre: nombre del nivel; si no existe se usa la paleta base.
            semilla: para que el paisaje siempre quede igual.
        Devuelve:
            Nada (constructor).
        """
        self.nombre = nombre
        self.paleta = paleta_de(nombre)
        azar = random.Random(semilla)
        self.estatico = self._pintar(azar)
        # Cada mota: [x, y, velocidad relativa, fase]
        self.motas = [[azar.uniform(0, ANCHO), azar.uniform(0, ALTO), azar.uniform(0.4, 1.0),
                       azar.uniform(0, math.tau)] for _ in range(46)]
        # Sentido de las motas: Fácil y Difícil suben (luciérnagas y brasas); Medio cae (polvo frío).
        self.sentido = {"Fácil": -0.5, "Medio": 0.6, "Difícil": -1.0}.get(nombre, -0.4)
        self._miniaturas = {}

    # ------------------------------------------------------------ pintura (una sola vez)
    def _pintar(self, azar):
        """
        (Interno) Pinta el cielo, el resplandor del horizonte, las siluetas y el suelo.

        Recibe:
            azar: generador aleatorio con semilla.
        Devuelve:
            Una Surface del tamaño de la ventana.
        """
        p = self.paleta
        s = pygame.Surface((ANCHO, ALTO))
        arriba = mezclar(p["oscuridad"], p["niebla"], 0.16)
        abajo = mezclar(p["oscuridad"], p["piso"], 0.55)
        s.blit(degradado((ANCHO, ALTO), arriba, abajo), (0, 0))
        # Resplandor en el horizonte: más fuerte donde hay más brasas.
        brillo(s, (ANCHO // 2, HORIZONTE), 600, p["luz"], round(0.10 * p["brasas"], 2))
        lejos = mezclar(p["oscuridad"], p["pared"], 0.24)
        cerca = mezclar(p["oscuridad"], p["pared"], 0.10)
        if self.nombre == "Fácil":
            self._bosque(s, azar, lejos, cerca)
        elif self.nombre == "Medio":
            self._cripta(s, azar, lejos, cerca)
        else:
            self._ruinas(s, azar, lejos, cerca)
        pygame.draw.rect(s, mezclar(p["oscuridad"], p["piso"], 0.8),
                         (0, HORIZONTE, ANCHO, ALTO - HORIZONTE))
        pygame.draw.line(s, mezclar(p["piso"], p["luz"], 0.25), (0, HORIZONTE), (ANCHO, HORIZONTE), 2)
        return s

    @staticmethod
    def _pino(s, x, base, alto, color):
        """(Interno) Dibuja un pino de cuatro pisos. Recibe: s, x, base, alto, color. Devuelve: nada."""
        pygame.draw.rect(s, color, (x - 5, base - 24, 10, 24))
        for i in range(4):
            y = base - alto + i * (alto // 5)
            ancho = 24 + i * 16
            pygame.draw.polygon(s, color, [(x, y), (x - ancho, y + alto // 3),
                                           (x + ancho, y + alto // 3)])

    def _bosque(self, s, azar, lejos, cerca):
        """(Interno) Bosque de pinos en dos planos. Recibe: s, azar, lejos, cerca. Devuelve: nada."""
        for _ in range(11):
            self._pino(s, azar.randrange(-20, ANCHO + 20), HORIZONTE - 30,
                       azar.randrange(150, 260), lejos)
        for _ in range(8):
            self._pino(s, azar.randrange(-30, ANCHO + 30), HORIZONTE + 6,
                       azar.randrange(250, 400), cerca)

    def _cripta(self, s, azar, lejos, cerca):
        """(Interno) Arcos de piedra, columnas, cadenas y un haz de luz. Recibe: s, azar, lejos, cerca. Devuelve: nada."""
        p = self.paleta
        for x in range(-40, ANCHO + 200, 230):
            pygame.draw.rect(s, lejos, (x, 160, 36, HORIZONTE - 160))
            pygame.draw.rect(s, mezclar(lejos, p["pared"], 0.25), (x - 8, 150, 52, 16))
            marco = pygame.Rect(x + 36, 40, 194, 240)
            for i in range(12):                              # arco grueso hecho con varios arcos finos
                pygame.draw.arc(s, lejos, marco.inflate(-2 * i, -2 * i), 0, math.pi, 2)
        for _ in range(6):                                   # cadenas colgantes
            x = azar.randrange(40, ANCHO - 40)
            largo = azar.randrange(80, 230)
            pygame.draw.line(s, cerca, (x, 0), (x, largo), 2)
            for y in range(10, largo, 14):
                pygame.draw.circle(s, cerca, (x, y), 3, 1)
        haz = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        pygame.draw.polygon(haz, (*p["niebla"], 16), [(300, 0), (420, 0), (640, HORIZONTE), (420, HORIZONTE)])
        s.blit(haz, (0, 0))

    def _ruinas(self, s, azar, lejos, cerca):
        """(Interno) Columnas rotas, una puerta en ruinas y pedazos caídos. Recibe: s, azar, lejos, cerca. Devuelve: nada."""
        p = self.paleta
        # Puerta en ruinas al fondo: el umbral de ceniza.
        pygame.draw.rect(s, lejos, (ANCHO // 2 - 140, 220, 280, HORIZONTE - 220))
        pygame.draw.polygon(s, lejos, [(ANCHO // 2 - 140, 220), (ANCHO // 2 - 90, 160),
                                       (ANCHO // 2 - 30, 200), (ANCHO // 2 + 20, 150),
                                       (ANCHO // 2 + 140, 220)])
        pygame.draw.rect(s, mezclar(p["oscuridad"], p["luz"], 0.30),
                         (ANCHO // 2 - 48, 310, 96, HORIZONTE - 310))
        for _ in range(9):                                   # columnas rotas con la punta en sierra
            x = azar.randrange(-10, ANCHO - 10)
            alto = azar.randrange(120, 330)
            ancho = azar.randrange(30, 52)
            tope = HORIZONTE - alto
            color = lejos if azar.random() < 0.5 else cerca
            pygame.draw.polygon(s, color, [
                (x, HORIZONTE), (x, tope + 14), (x + ancho // 3, tope),
                (x + ancho // 2, tope + 22), (x + ancho, tope + 6), (x + ancho, HORIZONTE)])
        for _ in range(22):                                  # escombros en el suelo
            x = azar.randrange(0, ANCHO)
            pygame.draw.rect(s, cerca, (x, HORIZONTE - azar.randrange(4, 14),
                                        azar.randrange(8, 26), azar.randrange(5, 14)))

    # ------------------------------------------------------------ animación y dibujo
    def actualizar(self, dt):
        """Mueve las motas: suben o bajan y reaparecen del otro lado. Recibe: dt (segundos). Devuelve: nada."""
        for m in self.motas:
            m[1] += self.sentido * 30 * m[2] * dt
            if m[1] < -10:
                m[1] = ALTO + 10
            elif m[1] > ALTO + 10:
                m[1] = -10

    def dibujar(self, surf, t, alfa=255):
        """
        Dibuja el paisaje y las motas que flotan.

        Recibe:
            surf: superficie donde dibujar.
            t: tiempo en segundos (parpadeo).
            alfa: 0 a 255; menos de 255 lo mezcla con lo que ya hay (sirve para disolver).
        Devuelve:
            Nada.
        """
        alfa = max(0, min(255, int(alfa)))
        if alfa <= 0:
            return
        if alfa < 255:
            self.estatico.set_alpha(alfa)
            surf.blit(self.estatico, (0, 0))
            self.estatico.set_alpha(255)
        else:
            surf.blit(self.estatico, (0, 0))
        k = alfa / 255.0
        polvo = self.paleta["polvo"]
        for x, y, v, fase in self.motas:
            b = 0.5 + 0.5 * math.sin(t * 1.4 + fase * 3)
            px = int(x + math.sin(t * 0.6 * v + fase) * 14)
            lado = 3 if v > 0.7 else 2
            pygame.draw.rect(surf, mezclar(self.paleta["oscuridad"], polvo, k * (0.35 + 0.65 * b)),
                             (px, int(y), lado, lado))
            if v > 0.88 and b > 0.6:                         # unas pocas brillan de verdad
                brillo(surf, (px, y), 12, polvo, 0.3)

    def miniatura(self, tam):
        """
        Devuelve el paisaje reducido (para el encabezado de una tarjeta o del HUD).

        Recibe:
            tam: (ancho, alto) en píxeles.
        Devuelve:
            Una Surface de ese tamaño (se guarda para no recalcularla).
        """
        tam = (max(1, int(tam[0])), max(1, int(tam[1])))
        if tam not in self._miniaturas:
            alto_recorte = min(ALTO, max(1, int(ANCHO * tam[1] / tam[0])))
            y0 = max(0, min(250, ALTO - alto_recorte))
            region = self.estatico.subsurface((0, y0, ANCHO, alto_recorte))
            try:
                self._miniaturas[tam] = pygame.transform.smoothscale(region, tam)
            except (pygame.error, ValueError):
                self._miniaturas[tam] = pygame.transform.scale(region, tam)
        return self._miniaturas[tam]


# ====================================================================== piezas decorativas
def remaches(surf, rect, color, margen=9):
    """
    Dibuja un remache en cada esquina de un panel.

    Recibe:
        surf: superficie.
        rect: pygame.Rect del panel.
        color: color del metal.
        margen: distancia a cada esquina.
    Devuelve:
        Nada.
    """
    for x in (rect.x + margen, rect.right - margen):
        for y in (rect.y + margen, rect.bottom - margen):
            pygame.draw.circle(surf, mezclar(color, (0, 0, 0), 0.5), (x + 1, y + 1), 3)
            pygame.draw.circle(surf, color, (x, y), 3)


def separador(surf, x1, x2, y, color):
    """
    Dibuja una línea con un rombo en el centro.

    Recibe:
        surf: superficie.
        x1, x2: extremos de la línea.
        y: altura.
        color: color de la línea.
    Devuelve:
        Nada.
    """
    medio = (x1 + x2) // 2
    pygame.draw.line(surf, color, (x1, y), (medio - 10, y), 1)
    pygame.draw.line(surf, color, (medio + 10, y), (x2, y), 1)
    pygame.draw.polygon(surf, color, [(medio, y - 5), (medio + 6, y), (medio, y + 5), (medio - 6, y)])


def rayos(surf, centro, t, color, radio=520, cantidad=12, intensidad=0.5):
    """
    Dibuja rayos de luz que giran despacio (pantalla de victoria).

    Recibe:
        surf: superficie.
        centro: (x, y) de donde salen.
        t: tiempo en segundos.
        color: color de la luz.
        radio: largo de los rayos.
        cantidad: cuántos rayos.
        intensidad: 0 a 1.
    Devuelve:
        Nada.
    """
    global _capa_rayos
    if _capa_rayos is None:
        _capa_rayos = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    _capa_rayos.fill((0, 0, 0, 0))
    media = math.pi / cantidad * 0.55 / 2
    alfa = max(0, min(255, int(70 * intensidad)))
    for i in range(cantidad):
        ang = t * 0.12 + i * math.tau / cantidad
        puntos = [centro,
                  (centro[0] + math.cos(ang - media) * radio, centro[1] + math.sin(ang - media) * radio),
                  (centro[0] + math.cos(ang + media) * radio, centro[1] + math.sin(ang + media) * radio)]
        pygame.draw.polygon(_capa_rayos, (*color, alfa), puntos)
    surf.blit(_capa_rayos, (0, 0))


def ceniza(surf, t, color, cantidad=46, intensidad=1.0):
    """
    Dibuja ceniza que cae por toda la pantalla (pantalla de derrota). No guarda estado: cada
    mota se calcula solo con el tiempo.

    Recibe:
        surf: superficie.
        t: tiempo en segundos.
        color: color de la ceniza.
        cantidad: número de motas.
        intensidad: 0 a 1.
    Devuelve:
        Nada.
    """
    for i in range(cantidad):
        vel = 16 + (i * 7) % 23
        x = (i * 211) % ANCHO + math.sin(t * 0.8 + i) * 18
        y = (t * vel + i * 97) % (ALTO + 20) - 10
        tono = mezclar((0, 0, 0), color, intensidad * (0.35 + 0.065 * ((i * 37) % 10)))
        lado = 3 if i % 3 == 0 else 2
        pygame.draw.rect(surf, tono, (int(x), int(y), lado, lado))


def llama(surf, x, y, color, encendida, t=0.0, tam=1.0):
    """
    Dibuja una antorcha pequeña (sirve para marcar la dificultad de un nivel).

    Recibe:
        surf: superficie.
        x, y: posición de la base de la llama.
        color: color de la llama.
        encendida: True = llama viva; False = solo el contorno apagado.
        t: tiempo en segundos (parpadeo).
        tam: factor de tamaño.
    Devuelve:
        Nada.
    """
    pygame.draw.rect(surf, (70, 52, 36), (x - 2, y, 4, int(12 * tam)))
    k = int(math.sin(t * 9 + x) * 2) if encendida else 0
    contorno = [(x - 6 * tam, y), (x - 3 * tam, y - 10 * tam), (x, y - 16 * tam - k),
                (x + 3 * tam, y - 9 * tam), (x + 6 * tam, y)]
    if encendida:
        pygame.draw.polygon(surf, color, contorno)
        pygame.draw.polygon(surf, mezclar(color, (255, 235, 170), 0.6),
                            [(x - 3 * tam, y), (x, y - 8 * tam), (x + 3 * tam, y)])
    else:
        pygame.draw.polygon(surf, (62, 56, 50), contorno, 1)
