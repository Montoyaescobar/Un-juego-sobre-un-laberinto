"""
render.py
Dibujo del tablero y de los personajes: concreto húmedo, viajero, espectros y salida,
pista y linterna. Solo dibuja lo que le dice la lógica del juego.
"""

import math
import random

import pygame

from interfaz.tema import (PALETA_BASE, ORO, ROJO, CIAN, VERDE, MORADO, TEXTO, APAGADO, BORDE,
                           mezclar, brillo, texto, texto_ajustado)


def tablero_estatico(lab, cell, semilla=3, paleta=None):
    """
    Dibuja UNA vez la parte que no cambia del laberinto (paredes y piso) en una superficie.

    Las paredes tienen profundidad: la cara de arriba es clara y, cuando hay piso debajo,
    se ve la cara de enfrente (más oscura, con ladrillos) y una sombra sobre el suelo. El piso
    varía: baldosas, musgo junto a las paredes, grietas, charcos y piedrecitas.

    Recibe:
        lab: el Laberinto.
        cell: tamaño de cada casilla en píxeles.
        semilla: para que las pequeñas variaciones de la piedra queden siempre iguales.
        paleta: colores del nivel (ver tema.paleta_de); si es None se usan los colores base.
    Devuelve:
        Una Surface de (ancho*cell) x (alto*cell).
    """
    paleta = paleta or PALETA_BASE
    color_pared, color_piso, musgo = paleta["pared"], paleta["piso"], paleta["musgo"]
    surf = pygame.Surface((lab.ancho * cell, lab.alto * cell))
    azar = random.Random(semilla)

    def pared(f, c):
        """Dice si la casilla (f, c) es pared. Recibe: f (fila) y c (columna). Devuelve: True si no es transitable."""
        return not lab.es_transitable(f, c)

    # Sombras que las paredes dejan en el suelo (se crean una vez y se reutilizan).
    grosor_ao = max(2, int(cell * 0.34))
    ao_izq = pygame.Surface((grosor_ao, cell), pygame.SRCALPHA)
    for i in range(grosor_ao):
        pygame.draw.line(ao_izq, (0, 0, 0, int(118 * (1 - i / grosor_ao) ** 2)), (i, 0), (i, cell))
    largo_proyectada = max(3, int(cell * 0.55))
    sombra_pared = pygame.Surface((cell, largo_proyectada), pygame.SRCALPHA)
    for i in range(largo_proyectada):
        pygame.draw.line(sombra_pared, (0, 0, 0, int(165 * (1 - i / largo_proyectada) ** 1.6)),
                         (0, i), (cell, i))
    alto_frente = max(3, int(cell * 0.42))           # altura de la cara de enfrente de la pared

    for f in range(lab.alto):
        for c in range(lab.ancho):
            x, y = c * cell, f * cell
            if pared(f, c):
                v = azar.randint(-9, 8)
                col = (max(0, color_pared[0] + v), max(0, color_pared[1] + v),
                       max(0, color_pared[2] + v))
                debajo_libre = not pared(f + 1, c)
                # Cara de arriba: la piedra vista desde arriba, con un borde biselado.
                pygame.draw.rect(surf, col, (x, y, cell, cell))
                inset = max(1, cell // 10)
                interior = mezclar(col, (24, 24, 15), 0.10)
                pygame.draw.rect(surf, interior,
                                 (x + inset, y + inset, cell - inset * 2, cell - inset * 2))
                pygame.draw.line(surf, mezclar(col, (214, 206, 150), 0.28),
                                 (x + inset, y + inset), (x + cell - inset, y + inset), 1)
                # Junta de bloques: media casilla desplazada en filas alternas, como un muro real.
                junta = mezclar(interior, (10, 11, 7), 0.30)
                if (f + c) % 3 == 0:
                    pygame.draw.line(surf, junta, (x + cell // 2, y + inset),
                                     (x + cell // 2, y + cell - inset), 1)
                if (f + c) % 2 == 0 and cell >= 14:
                    pygame.draw.line(surf, junta, (x + inset, y + cell // 2),
                                     (x + cell - inset, y + cell // 2), 1)
                if debajo_libre:
                    # Cara de enfrente: más oscura, con ladrillos, y un filo claro donde se dobla.
                    frente = pygame.Rect(x, y + cell - alto_frente, cell, alto_frente)
                    pygame.draw.rect(surf, mezclar(col, (6, 7, 5), 0.46), frente)
                    pygame.draw.line(surf, mezclar(col, (230, 222, 165), 0.38),
                                     (frente.x, frente.y - 1), (frente.right - 1, frente.y - 1), 1)
                    ladrillo = mezclar(col, (4, 5, 3), 0.62)
                    pygame.draw.line(surf, ladrillo, (frente.x, frente.y + frente.h // 2),
                                     (frente.right - 1, frente.y + frente.h // 2), 1)
                    corte = x + (cell // 3 if (f + c) % 2 == 0 else (cell * 2) // 3)
                    pygame.draw.line(surf, ladrillo, (corte, frente.y + 1),
                                     (corte, frente.y + frente.h // 2), 1)
                    pygame.draw.line(surf, ladrillo, (x + cell // 2, frente.y + frente.h // 2),
                                     (x + cell // 2, frente.bottom - 1), 1)
                    pygame.draw.line(surf, mezclar(col, (0, 0, 0), 0.80),
                                     (frente.x, frente.bottom - 1), (frente.right - 1, frente.bottom - 1), 1)
                if not pared(f - 1, c):
                    pygame.draw.line(surf, mezclar(col, (223, 214, 153), 0.36), (x, y),
                                     (x + cell - 1, y), 2)
                if not pared(f, c - 1):
                    pygame.draw.line(surf, mezclar(col, (208, 199, 139), 0.20), (x, y),
                                     (x, y + cell - 1), 1)
                if not pared(f, c + 1):
                    pygame.draw.line(surf, mezclar(col, (0, 0, 0), 0.42), (x + cell - 1, y),
                                     (x + cell - 1, y + cell - 1), 1)
                if cell >= 14 and azar.random() < 0.12:
                    gx, gy = x + azar.randint(3, cell - 4), y + azar.randint(3, cell - 4)
                    pygame.draw.line(surf, mezclar(col, (8, 9, 5), 0.55), (gx, gy),
                                     (gx + azar.randint(-3, 3), gy + azar.randint(2, 5)), 1)
                if cell >= 14 and azar.random() < 0.16:
                    # Musgo que cuelga de la cara de arriba de la pared.
                    for _ in range(azar.randint(2, 4)):
                        mx, my = x + azar.randint(2, cell - 3), y + azar.randint(1, cell // 2)
                        pygame.draw.rect(surf, mezclar(col, musgo, 0.55), (mx, my, 2, 2))
            else:
                # Baldosas: dos tonos que alternan y se desplazan fila a fila.
                v = azar.randint(-4, 5) + (3 if (f + c) % 2 == 0 else -2)
                col = (max(0, color_piso[0] + v), max(0, color_piso[1] + v),
                       max(0, color_piso[2] + v))
                pygame.draw.rect(surf, col, (x, y, cell, cell))
                pygame.draw.rect(surf, mezclar(col, (112, 105, 69), 0.10),
                                 (x + 1, y + 1, cell - 2, cell - 2), 1)
                pygame.draw.line(surf, mezclar(col, (5, 6, 4), 0.38),
                                 (x + 2, y + cell - 2), (x + cell - 2, y + cell - 2), 1)
                if cell >= 14:
                    cerca_pared = any(pared(f + df, c + dc)
                                      for df, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)))
                    suerte = azar.random()
                    if cerca_pared and suerte < 0.30:
                        # Musgo pegado a las paredes: unas pocas motas en un rincón.
                        bx = x + (azar.choice((3, cell - 6)))
                        by = y + (azar.choice((3, cell - 6)))
                        for _ in range(azar.randint(4, 7)):
                            pygame.draw.rect(surf, mezclar(col, musgo, azar.uniform(0.45, 0.85)),
                                             (bx + azar.randint(-2, 3), by + azar.randint(-2, 3), 2, 2))
                    elif suerte < 0.40:
                        # Grieta: una línea quebrada.
                        gx, gy = x + azar.randint(4, cell - 5), y + azar.randint(3, cell // 2)
                        oscuro = mezclar(col, (4, 5, 3), 0.55)
                        for _ in range(3):
                            nx, ny = gx + azar.randint(-3, 3), gy + azar.randint(2, 4)
                            pygame.draw.line(surf, oscuro, (gx, gy), (nx, ny), 1)
                            gx, gy = nx, ny
                    elif suerte < 0.46:
                        # Charco: óvalo oscuro con un reflejo frío.
                        charco = pygame.Rect(x + cell // 5, y + cell // 2, int(cell * 0.55),
                                             max(3, int(cell * 0.26)))
                        pygame.draw.ellipse(surf, mezclar(col, (14, 24, 34), 0.60), charco)
                        pygame.draw.line(surf, mezclar(col, (120, 160, 185), 0.45),
                                         (charco.x + 3, charco.y + 1), (charco.x + charco.w // 2, charco.y + 1), 1)
                    elif suerte < 0.60:
                        gx, gy = x + azar.randint(3, cell - 4), y + azar.randint(3, cell - 4)
                        pygame.draw.circle(surf, mezclar(color_piso, (124, 112, 66), 0.30), (gx, gy), 1)
                if pared(f, c - 1):
                    surf.blit(ao_izq, (x, y))
                if pared(f - 1, c):
                    # Sombra que la pared proyecta sobre el suelo, justo debajo de su cara de enfrente.
                    surf.blit(sombra_pared, (x, y))

    # Marca de tiza en la entrada.
    ef, ec = lab.entrada
    centro = (int((ec + 0.5) * cell), int((ef + 0.5) * cell))
    pygame.draw.circle(surf, mezclar(color_piso, paleta["luz"], 0.38), centro, int(cell * 0.36), 1)
    pygame.draw.line(surf, mezclar(color_piso, paleta["luz"], 0.48), (centro[0] - cell // 5, centro[1]),
                     (centro[0] + cell // 5, centro[1]), 1)
    return surf


def dibujar_portal(surf, cx, cy, cell, t):
    """
    Dibuja la salida como una puerta de servicio iluminada desde el otro lado.

    Recibe:
        surf: superficie.
        cx, cy: centro en pantalla.
        cell: tamaño de casilla.
        t: tiempo en segundos.
    Devuelve:
        Nada.
    """
    pulso = 0.78 + 0.18 * math.sin(t * 3.1) + 0.04 * math.sin(t * 13)
    brillo(surf, (cx, cy), int(cell * 1.3), ORO, 0.42 * pulso)
    w, h = max(8, int(cell * 0.58)), max(12, int(cell * 0.80))
    marco = pygame.Rect(int(cx - w / 2), int(cy - h / 2), w, h)
    pygame.draw.rect(surf, (27, 24, 14), marco.inflate(4, 4))
    pygame.draw.rect(surf, mezclar((69, 56, 31), ORO, 0.38 * pulso), marco, 2)
    puerta = marco.inflate(-4, -4)
    pygame.draw.rect(surf, (31, 29, 18), puerta)
    rendija = pygame.Rect(puerta.centerx - max(1, cell // 16), puerta.y + 2,
                          max(2, cell // 8), max(4, puerta.h - 4))
    pygame.draw.rect(surf, mezclar(ORO, (255, 242, 182), pulso), rendija)
    pygame.draw.circle(surf, (248, 220, 135), (puerta.right - 3, puerta.centery), 1)
    pygame.draw.line(surf, (240, 210, 119), (marco.x + 2, marco.bottom - 2),
                     (marco.right - 2, marco.bottom - 2), 1)


_sprites_jugador = {}


def _sprite_jugador(direccion, paso, antorcha, saltando, arma="espada_ceniza"):
    """Construye y guarda un fotograma de 18 × 24 píxeles del viajero."""
    clave = (direccion, paso, antorcha, saltando, arma)
    if clave in _sprites_jugador:
        return _sprites_jugador[clave]
    espejo = direccion == "derecha"
    vista = "izquierda" if espejo else direccion
    s = pygame.Surface((18, 24), pygame.SRCALPHA)
    sombra, capa, tela, filo = (12, 19, 26), (26, 39, 49), (53, 67, 70), (108, 116, 105)
    metal, cuero, piel = (97, 108, 105), (119, 77, 43), (177, 145, 100)
    step = (-1 if paso == 0 else 1) if paso in (0, 1) else 0

    # Capa y piernas: el dobladillo cambia de forma en cada fotograma de marcha.
    hem = step * 2 if not saltando else 0
    pygame.draw.polygon(s, sombra, [(5, 7), (12, 7), (15, 12), (16 + hem, 21),
                                    (11, 20), (8, 22), (3 - hem, 21), (4, 12)])
    pygame.draw.polygon(s, capa, [(6, 8), (11, 8), (13, 13), (14 + hem, 19),
                                  (10, 19), (8, 20), (5 - hem, 19), (5, 12)])
    pygame.draw.rect(s, (77, 89, 85), (6, 13, 2, 5))
    pygame.draw.rect(s, (40, 50, 54), (10, 13, 2, 5))
    pierna_a = 5 + step
    pierna_b = 10 - step
    if saltando:
        pygame.draw.rect(s, sombra, (5, 18, 4, 3))
        pygame.draw.rect(s, sombra, (10, 17, 4, 3))
        pygame.draw.rect(s, (122, 130, 112), (4, 17, 4, 2))
        pygame.draw.rect(s, (122, 130, 112), (11, 16, 4, 2))
    else:
        pygame.draw.rect(s, sombra, (pierna_a, 18, 4, 4))
        pygame.draw.rect(s, sombra, (pierna_b, 18, 4, 4))
        pygame.draw.rect(s, (107, 84, 56), (pierna_a - 1, 21, 5, 2))
        pygame.draw.rect(s, (107, 84, 56), (pierna_b, 21, 5, 2))

    # Cota gastada y correas de cuero.
    pygame.draw.rect(s, metal, (6, 9, 7, 8))
    pygame.draw.rect(s, (128, 133, 117), (7, 10, 2, 5))
    pygame.draw.rect(s, (61, 67, 64), (10, 10, 2, 5))
    pygame.draw.line(s, cuero, (6, 10), (12, 15), 1)
    pygame.draw.rect(s, (173, 139, 75), (8, 15, 4, 2))

    # Capucha de cuervo; la vista trasera oculta el rostro.
    pygame.draw.polygon(s, sombra, [(5, 7), (4, 4), (6, 1), (12, 1), (15, 5), (14, 9), (11, 11), (6, 10)])
    pygame.draw.polygon(s, tela, [(6, 6), (6, 3), (8, 2), (12, 2), (14, 5), (13, 8), (10, 10), (7, 9)])
    if vista == "arriba":
        pygame.draw.line(s, filo, (8, 3), (11, 7), 1)
        pygame.draw.rect(s, sombra, (7, 7, 6, 3))
    elif vista == "izquierda":
        pygame.draw.rect(s, sombra, (6, 5, 7, 4))
        pygame.draw.rect(s, piel, (6, 6, 2, 2))
        pygame.draw.rect(s, (227, 190, 111), (6, 6, 1, 1))
    else:
        pygame.draw.rect(s, sombra, (6, 5, 7, 4))
        pygame.draw.rect(s, piel, (7, 6, 5, 2))
        pygame.draw.rect(s, (227, 190, 111), (8, 6, 1, 1))
        pygame.draw.rect(s, (227, 190, 111), (11, 6, 1, 1))

    # Brazos abiertos en el salto; si no, el viajero sostiene su antorcha.
    if saltando:
        pygame.draw.line(s, tela, (6, 10), (2, 7), 2)
        pygame.draw.line(s, tela, (13, 10), (16, 7), 2)
    if antorcha:
        if vista == "izquierda":
            pygame.draw.line(s, cuero, (5, 12), (2, 8), 2)
            pygame.draw.rect(s, (160, 105, 49), (1, 5, 3, 4))
        else:
            pygame.draw.line(s, cuero, (13, 12), (16, 8), 2)
            pygame.draw.rect(s, (160, 105, 49), (15, 5, 3, 4))
    lado_espada = 14 if vista == "izquierda" else 2
    if arma == "daga_sombras":
        pygame.draw.line(s, (36, 18, 52), (lado_espada, 13), (lado_espada - 2, 18), 2)
        pygame.draw.line(s, (180, 70, 240), (lado_espada, 13), (lado_espada - 2, 18), 1)
        pygame.draw.rect(s, (70, 50, 90), (lado_espada - 1, 12, 3, 2))
    elif arma == "baston_centella":
        pygame.draw.line(s, (86, 56, 34), (lado_espada, 11), (lado_espada - 1, 21), 1)
        pygame.draw.rect(s, (100, 230, 255), (lado_espada - 1, 9, 3, 3))
        pygame.draw.rect(s, (225, 250, 255), (lado_espada, 10, 1, 1))
    else:
        pygame.draw.line(s, (40, 65, 46), (lado_espada, 13), (lado_espada - 2, 18), 2)
        pygame.draw.line(s, (122, 183, 113), (lado_espada, 13), (lado_espada - 2, 18), 1)
        pygame.draw.rect(s, (151, 111, 63), (lado_espada - 1, 12, 3, 2))
    if espejo:
        s = pygame.transform.flip(s, True, False)
    _sprites_jugador[clave] = s
    return s


def dibujar_jugador(surf, cx, cy, cell, t, antorcha=True, direccion="abajo",
                    andando=False, saltando=False, arma="espada_ceniza"):
    """Dibuja al viajero en pixel art con marcha, respiración, salto y llama animada."""
    paso = 2 if saltando else int(t * 9) % 2 if andando else 2 + int((t % 1.6) > 0.8)
    sprite = _sprite_jugador(direccion, paso, antorcha, saltando, arma)
    ancho, alto = max(12, int(cell * 0.74)), max(18, int(cell * 0.94))
    sprite = pygame.transform.scale(sprite, (ancho, alto))
    balanceo = int(math.sin(t * 12) * 1.4) if andando else int(math.sin(t * 2.2) * 0.7)
    if saltando:
        balanceo = 0
    destino = sprite.get_rect(midbottom=(int(cx), int(cy + cell * 0.36 + balanceo)))
    pygame.draw.ellipse(surf, (10, 13, 13), (destino.x + ancho // 4, destino.bottom - 3,
                                               max(3, ancho // 2), max(2, cell // 8)))
    sx = 0.12 if direccion == "izquierda" else 0.88 if direccion == "derecha" else 0.87
    sy = 0.31
    farol = (destino.x + int(ancho * sx), destino.y + int(alto * sy))
    pulso = 0.74 + 0.20 * math.sin(t * 7.0) + 0.06 * math.sin(t * 17.0)
    if antorcha:
        brillo(surf, farol, max(5, int(cell * 0.72 * pulso)), ORO, 0.56)
    surf.blit(sprite, destino)
    if antorcha:
        alto_llama = max(3, int(alto * (0.16 + 0.025 * math.sin(t * 13))))
        pygame.draw.rect(surf, (215, 90, 32), (farol[0] - 2, farol[1] - alto_llama, 5, alto_llama))
        pygame.draw.rect(surf, (255, 203, 104), (farol[0] - 1, farol[1] - alto_llama + 1, 2,
                                                   max(1, alto_llama - 2)))


def dibujar_trampa(surf, cx, cy, cell, t, estado, retorno=None):
    """Dibuja una placa de presión y la marca segura a la que hay que volver."""
    radio = max(4, int(cell * 0.34))
    if retorno is not None and estado in ("armada", "activa"):
        rx, ry = retorno
        pygame.draw.circle(surf, mezclar((27, 25, 16), ORO, 0.28), (int(rx), int(ry)),
                           max(3, int(cell * 0.24)), 1)
        pygame.draw.line(surf, (148, 113, 53), (rx - 3, ry), (rx + 3, ry), 1)
    if estado == "activa":
        brillo(surf, (cx, cy), int(cell * 0.95), ROJO, 0.40 + 0.22 * math.sin(t * 18))
        color = (164, 54, 37)
        pygame.draw.rect(surf, color, (int(cx - radio), int(cy - radio), radio * 2, radio * 2))
        for i in range(-1, 2):
            x = int(cx + i * radio * 0.48)
            pygame.draw.polygon(surf, (230, 183, 115), [
                (x - 2, cy + 2), (x, cy - radio * 0.55), (x + 2, cy + 2)])
    elif estado == "desarmada":
        pygame.draw.rect(surf, (27, 27, 19), (int(cx - radio), int(cy - radio), radio * 2, radio * 2))
        pygame.draw.line(surf, (106, 78, 43), (cx - radio + 2, cy), (cx + radio - 2, cy), 1)
        pygame.draw.line(surf, (106, 78, 43), (cx, cy - radio + 2), (cx, cy + radio - 2), 1)
    else:
        brillo(surf, (cx, cy), int(cell * 0.55), ORO, 0.20 + 0.08 * math.sin(t * 2))
        pygame.draw.rect(surf, (65, 58, 35), (int(cx - radio), int(cy - radio), radio * 2, radio * 2))
        pygame.draw.rect(surf, (158, 119, 58),
                         (int(cx - radio), int(cy - radio), radio * 2, radio * 2), 1)
        pygame.draw.line(surf, (188, 145, 74), (cx - radio + 2, cy - 2), (cx + radio - 2, cy + 2), 1)


def dibujar_reliquia(surf, cx, cy, cell, t):
    """Dibuja un pequeño fragmento de mapa guardado en el ramal de la trampa."""
    brillo(surf, (cx, cy), int(cell * 0.72), ORO, 0.32 + 0.08 * math.sin(t * 4))
    w, h = max(8, int(cell * 0.48)), max(6, int(cell * 0.34))
    caja = pygame.Rect(int(cx - w / 2), int(cy - h / 2), w, h)
    pygame.draw.rect(surf, (107, 74, 36), caja)
    pygame.draw.rect(surf, (228, 181, 88), caja, 1)
    pygame.draw.line(surf, (40, 36, 23), (caja.x + 2, caja.centery),
                     (caja.right - 2, caja.centery), 1)
    pygame.draw.circle(surf, (247, 218, 133), (caja.centerx, caja.centery), 2)


def dibujar_puas(surf, cx, cy, cell, t, activas=True):
    """Dibuja una hilera de cuchillas pixeladas en una casilla del corredor."""
    w = max(10, int(cell * 0.78))
    h = max(4, int(cell * 0.22))
    base = pygame.Rect(int(cx - w / 2), int(cy + cell * 0.18), w, h)
    pygame.draw.rect(surf, (26, 29, 27), base)
    pygame.draw.rect(surf, (104, 99, 78), base, 1)
    pygame.draw.line(surf, (150, 134, 96), (base.x + 2, base.y + 1),
                     (base.right - 2, base.y + 1), 1)
    fase = 0.5 + 0.5 * math.sin(t * 5.5)
    alto = cell * (0.27 + 0.05 * fase) if activas else cell * 0.10
    puntas = 5 if cell < 24 else 7
    for i in range(puntas):
        x = base.x + 2 + i * max(2, (w - 4) // max(1, puntas - 1))
        pygame.draw.polygon(surf, (91, 101, 99), [(x - 2, base.y), (x, base.y - alto),
                                                   (x + 2, base.y)])
        pygame.draw.line(surf, (189, 184, 157), (x, base.y - alto), (x, base.y), 1)
    if activas:
        for i in (-1, 1):
            pygame.draw.rect(surf, (139, 69, 43), (int(cx + i * w * 0.42), base.y + 1, 2, 2))


def dibujar_puente(surf, cx, cy, cell, orientacion="horizontal", t=0.0):
    """Pasarela pequeña de tablones, cuerda y postes sobre el suelo oscuro."""
    ancho = max(10, int(cell * 0.88))
    alto = max(10, int(cell * 0.76))
    caja = pygame.Rect(int(cx - ancho / 2), int(cy - alto / 2), ancho, alto)
    pygame.draw.rect(surf, (13, 19, 20), caja)
    pygame.draw.rect(surf, (67, 62, 48), caja, 1)
    if orientacion == "horizontal":
        for i in range(4):
            y = caja.y + 2 + i * max(2, (alto - 5) // 4)
            pygame.draw.rect(surf, (91 + (i % 2) * 12, 63, 39),
                             (caja.x + 2, y, caja.w - 4, max(2, alto // 6)))
            pygame.draw.line(surf, (127, 95, 58), (caja.x + 3, y), (caja.right - 3, y), 1)
        for x in (caja.x + 2, caja.right - 4):
            pygame.draw.rect(surf, (91, 72, 48), (x, caja.y - 2, 3, caja.h + 4))
        pygame.draw.line(surf, (137, 111, 73), (caja.x + 3, caja.y + 1),
                         (caja.right - 3, caja.y + 1), 1)
        pygame.draw.line(surf, (137, 111, 73), (caja.x + 3, caja.bottom - 1),
                         (caja.right - 3, caja.bottom - 1), 1)
    else:
        for i in range(4):
            x = caja.x + 2 + i * max(2, (ancho - 5) // 4)
            pygame.draw.rect(surf, (91 + (i % 2) * 12, 63, 39),
                             (x, caja.y + 2, max(2, ancho // 6), caja.h - 4))
            pygame.draw.line(surf, (127, 95, 58), (x, caja.y + 3), (x, caja.bottom - 3), 1)
        for y in (caja.y + 2, caja.bottom - 4):
            pygame.draw.rect(surf, (91, 72, 48), (caja.x - 2, y, caja.w + 4, 3))
        pygame.draw.line(surf, (137, 111, 73), (caja.x + 1, caja.y + 3),
                         (caja.x + 1, caja.bottom - 3), 1)
        pygame.draw.line(surf, (137, 111, 73), (caja.right - 1, caja.y + 3),
                         (caja.right - 1, caja.bottom - 3), 1)
    # Un tablón flojo oscila apenas, delatando que el puente está viejo.
    tick = int(math.sin(t * 4) * 1)
    if orientacion == "horizontal":
        pygame.draw.rect(surf, (145, 97, 52), (caja.centerx - 1, caja.centery + tick, 3, 2))
    else:
        pygame.draw.rect(surf, (145, 97, 52), (caja.centerx + tick, caja.centery - 1, 2, 3))


def dibujar_rueda(surf, cx, cy, cell, t):
    """Rueda de hierro con radios pixelados y una animación corta de giro."""
    radio = max(5, int(cell * 0.43))
    centro = (int(cx), int(cy))
    pygame.draw.circle(surf, (13, 17, 18), centro, radio + 2)
    pygame.draw.circle(surf, (70, 79, 78), centro, radio)
    pygame.draw.circle(surf, (145, 148, 130), centro, radio - 2, 2)
    pygame.draw.circle(surf, (39, 48, 50), centro, max(2, radio // 2))
    rot = t * 5.2
    for i in range(6):
        a = rot + math.tau * i / 6
        x = int(cx + math.cos(a) * radio * 0.76)
        y = int(cy + math.sin(a) * radio * 0.76)
        pygame.draw.line(surf, (179, 169, 137), centro, (x, y), max(1, cell // 18))
        pygame.draw.rect(surf, (94, 72, 50), (x - 1, y - 1, 3, 3))
    pygame.draw.circle(surf, (179, 139, 79), centro, max(2, radio // 5))


def dibujar_enemigo(surf, cx, cy, cell, t, mirar=(0, 1)):
    """
    Dibuja un espectro alto, de ojos hundidos, que mira hacia el jugador.

    Recibe:
        surf: superficie.
        cx, cy: centro en pantalla.
        cell: tamaño de casilla.
        t: tiempo en segundos.
        mirar: vector (dx, dy) hacia donde miran los ojos.
    Devuelve:
        Nada.
    """
    frame = int(t * 6 + cx * 0.05) % 4
    sprite = _sprite_espectro(frame)
    ancho, alto = max(10, int(cell * 0.72)), max(14, int(cell * 0.94))
    sprite = pygame.transform.scale(sprite, (ancho, alto))
    bob = int(math.sin(t * 3.2 + cx * 0.05) * cell * 0.06)
    cy += bob
    brillo(surf, (cx, cy), int(cell * 0.84), ROJO, 0.22 + 0.08 * math.sin(t * 4))
    destino = sprite.get_rect(midbottom=(int(cx), int(cy + cell * 0.30)))
    pygame.draw.ellipse(surf, (9, 13, 16), (destino.x + ancho // 4, destino.bottom - 2,
                                               max(3, ancho // 2), max(2, cell // 9)))
    surf.blit(sprite, destino)
    if frame != 3:
        norma = math.hypot(*mirar) or 1.0
        dx, dy = mirar[0] / norma * ancho * 0.025, mirar[1] / norma * alto * 0.025
        ojo_y = destino.y + int(alto * 0.38)
        for lado in (-1, 1):
            ojo_x = int(cx + lado * ancho * 0.13)
            pygame.draw.rect(surf, (243, 171, 64), (ojo_x, ojo_y, max(2, ancho // 8), max(2, alto // 12)))
            pygame.draw.rect(surf, (255, 228, 135),
                             (int(ojo_x + dx), int(ojo_y + dy), 1, 1))


_sprites_espectro = {}


def _sprite_espectro(frame):
    """Fotogramas pixelados de un espectro de capa rota."""
    if frame in _sprites_espectro:
        return _sprites_espectro[frame]
    s = pygame.Surface((18, 24), pygame.SRCALPHA)
    sombra, tela, metal = (12, 19, 25), (37, 47, 50), (70, 75, 67)
    borde = (97, 68, 48)
    onda = (-2, 0, 2, 1)[frame]
    pygame.draw.polygon(s, sombra, [(5, 4), (8, 1), (12, 2), (15, 7), (14, 14),
                                   (17, 22 + onda), (13, 20), (10, 23 - onda),
                                   (7, 20), (3, 22 + onda), (4, 13)])
    pygame.draw.polygon(s, tela, [(6, 5), (8, 3), (12, 3), (14, 8), (13, 14),
                                  (15, 20 + onda), (12, 19), (10, 21 - onda),
                                  (7, 19), (5, 20 + onda), (5, 12)])
    pygame.draw.rect(s, metal, (6, 11, 7, 5))
    pygame.draw.line(s, borde, (7, 12), (12, 16), 1)
    pygame.draw.polygon(s, (9, 14, 18), [(6, 6), (8, 3), (12, 4), (13, 8), (11, 10), (7, 9)])
    pygame.draw.rect(s, (214, 87, 47), (7, 7, 2, 1))
    pygame.draw.rect(s, (214, 87, 47), (11, 7, 2, 1))
    if frame == 1:
        pygame.draw.rect(s, (50, 69, 72), (15, 12, 2, 4))
    elif frame == 2:
        pygame.draw.rect(s, (50, 69, 72), (2, 14, 2, 3))
    _sprites_espectro[frame] = s
    return s


def dibujar_vela(surf, cx, cy, cell, t, fase=0.0):
    """Vela pixelada en una pared, con soporte oxidado y una llama que ilumina."""
    llama_y = cy - cell * 0.13
    pulso = math.sin(t * 11 + fase)
    brillo(surf, (cx, llama_y), max(4, int(cell * 0.72)), ORO,
           0.28 + 0.08 * math.sin(t * 5 + fase))
    pygame.draw.rect(surf, (46, 40, 29), (int(cx - cell * 0.13), int(cy + cell * 0.03),
                                           max(3, int(cell * 0.27)), max(2, int(cell * 0.08))))
    pygame.draw.rect(surf, (108, 82, 48), (int(cx - cell * 0.09), int(cy - cell * 0.22),
                                            max(3, int(cell * 0.18)), max(5, int(cell * 0.30))))
    pygame.draw.line(surf, (160, 126, 69), (int(cx - cell * 0.18), int(cy + cell * 0.10)),
                     (int(cx + cell * 0.18), int(cy + cell * 0.10)), max(1, cell // 18))
    pygame.draw.rect(surf, (48, 40, 27), (int(cx - 1), int(cy - cell * 0.29), 2, 3))
    pygame.draw.polygon(surf, (203, 75, 30), [
        (int(cx - cell * 0.10), int(cy - cell * 0.20)),
        (int(cx - cell * 0.07), int(llama_y - cell * (0.18 + 0.04 * pulso))),
        (int(cx), int(cy - cell * 0.19)),
        (int(cx + cell * 0.08), int(llama_y - cell * (0.16 - 0.03 * pulso))),
        (int(cx + cell * 0.11), int(cy - cell * 0.20))])
    pygame.draw.rect(surf, (255, 205, 109), (int(cx - 2), int(llama_y - 3), 4, 5))


def dibujar_trampa_giratoria(surf, cx, cy, cell, t, segura=False, fase=0.0):
    """Mecanismo de piso con eje central y cuchillas que barren alrededor."""
    centro = (int(cx), int(cy))
    radio = max(5, int(cell * 0.42))
    color_luz = (78, 205, 121) if segura else (166, 69, 46)
    brillo(surf, centro, int(cell * 0.80), color_luz,
           0.24 + 0.10 * math.sin(t * 10))
    pygame.draw.circle(surf, (20, 26, 25), centro, radio + 2)
    pygame.draw.circle(surf, (76, 78, 64), centro, radio, 1)
    angulo = t * 2.8 + fase
    for i in range(3):
        a = angulo + math.tau * i / 3
        punta = (int(cx + math.cos(a) * radio), int(cy + math.sin(a) * radio))
        pygame.draw.line(surf, (24, 27, 25), centro, punta, max(3, cell // 7))
        pygame.draw.line(surf, (130, 140, 133), centro, punta, max(1, cell // 15))
        tangente = (-math.sin(a), math.cos(a))
        filo = (int(punta[0] + tangente[0] * cell * 0.13),
                int(punta[1] + tangente[1] * cell * 0.13))
        pygame.draw.polygon(surf, (70, 79, 78), [
            (punta[0] - 2, punta[1] - 2), (filo[0], filo[1]),
            (punta[0] + 2, punta[1] + 2)])
        pygame.draw.line(surf, (195, 196, 177), punta, filo, 1)
    pygame.draw.circle(surf, (29, 34, 31), centro, max(3, cell // 9))
    pygame.draw.circle(surf, (183, 160, 103) if not segura else (153, 255, 169),
                       centro, max(1, cell // 17))


def dibujar_cadena(surf, cx, cy, cell, t, fase=0.0, segura=False):
    """Cadena colgante y péndulo de hierro que oscila sobre las cuchillas."""
    techo_y = int(cy - cell * 0.47)
    angulo = math.sin(t * 2.7 + fase) * 0.72
    fin_x = int(cx + math.sin(angulo) * cell * 0.38)
    fin_y = int(techo_y + math.cos(angulo) * cell * 0.60)
    pygame.draw.line(surf, (25, 29, 28), (int(cx), techo_y), (fin_x, fin_y), max(3, cell // 12))
    enlaces = 6
    for i in range(enlaces):
        k = (i + 1) / enlaces
        x = int(cx + (fin_x - cx) * k)
        y = int(techo_y + (fin_y - techo_y) * k)
        pygame.draw.rect(surf, (132, 133, 119), (x - 2, y - 2, 4, 3))
        pygame.draw.rect(surf, (53, 61, 61), (x - 1, y - 1, 2, 2))
    pygame.draw.rect(surf, (82, 91, 86), (int(cx - cell * 0.14), techo_y - 2,
                                           max(5, int(cell * 0.28)), 4))
    color_peso = (115, 157, 105) if segura else (78, 74, 62)
    pygame.draw.circle(surf, (23, 29, 28), (fin_x, fin_y), max(4, cell // 8))
    pygame.draw.circle(surf, color_peso, (fin_x, fin_y), max(3, cell // 10))
    pygame.draw.rect(surf, (176, 175, 151), (fin_x - 2, fin_y - 1, 2, 2))


def dibujar_esqueleto(surf, cx, cy, cell, t, fase=0.0):
    """Esqueleto pixelado con huesos agrietados y una brasa verdosa en el pecho."""
    escala = max(0.7, cell / 38)
    x, y = int(cx), int(cy + math.sin(t * 2.6 + fase) * cell * 0.035)
    hueso, sombra, hierro = (166, 163, 132), (63, 65, 53), (75, 80, 69)
    brillo(surf, (x, y), int(cell * 0.53), (70, 155, 82),
           0.13 + 0.05 * math.sin(t * 4 + fase))
    pygame.draw.ellipse(surf, (10, 13, 12), (x - int(cell * 0.24), y + int(cell * 0.28),
                                               int(cell * 0.48), max(3, int(cell * 0.12))))
    cabeza = max(4, int(cell * 0.16))
    pygame.draw.rect(surf, sombra, (x - cabeza - 1, y - int(cell * 0.43) - 1,
                                    cabeza * 2 + 2, cabeza * 2 + 2))
    pygame.draw.rect(surf, hueso, (x - cabeza, y - int(cell * 0.43), cabeza * 2, cabeza * 2))
    pygame.draw.rect(surf, (20, 25, 22), (x - int(cell * 0.11), y - int(cell * 0.34),
                                           max(2, int(cell * 0.075)), max(2, int(cell * 0.075))))
    pygame.draw.rect(surf, (20, 25, 22), (x + int(cell * 0.045), y - int(cell * 0.34),
                                           max(2, int(cell * 0.075)), max(2, int(cell * 0.075))))
    pygame.draw.rect(surf, (94, 183, 91), (x - 1, y - int(cell * 0.33), 2, 2))
    pygame.draw.line(surf, hueso, (x - int(cell * 0.15), y - int(cell * 0.10)),
                     (x + int(cell * 0.15), y - int(cell * 0.10)), max(2, int(2 * escala)))
    pygame.draw.line(surf, hueso, (x, y - int(cell * 0.17)),
                     (x, y + int(cell * 0.21)), max(2, int(3 * escala)))
    for i in range(3):
        yy = y - int(cell * 0.03) + i * max(2, int(cell * 0.08))
        pygame.draw.arc(surf, hueso, (x - int(cell * 0.19), yy - 3,
                                      int(cell * 0.38), max(5, int(cell * 0.19))),
                        0.15, math.pi - 0.15, max(1, int(2 * escala)))
    pygame.draw.line(surf, hierro, (x - int(cell * 0.16), y - int(cell * 0.07)),
                     (x - int(cell * 0.31), y + int(cell * 0.12)), max(2, int(3 * escala)))
    pygame.draw.line(surf, hueso, (x - int(cell * 0.31), y + int(cell * 0.12)),
                     (x - int(cell * 0.22), y + int(cell * 0.19)), max(2, int(2 * escala)))
    pygame.draw.line(surf, hierro, (x + int(cell * 0.16), y - int(cell * 0.07)),
                     (x + int(cell * 0.29), y + int(cell * 0.13)), max(2, int(3 * escala)))
    for dx in (-1, 1):
        hx = x + dx * int(cell * 0.29)
        pygame.draw.rect(surf, hueso, (hx - 2, y + int(cell * 0.11), 5, 3))
    for i, offset in enumerate((-1, 1)):
        pierna_x = x + int(cell * 0.09 * offset)
        pygame.draw.line(surf, hueso, (x + offset * 2, y + int(cell * 0.20)),
                         (pierna_x, y + int(cell * 0.36)), max(2, int(3 * escala)))
        pygame.draw.line(surf, sombra, (pierna_x, y + int(cell * 0.36)),
                         (pierna_x + offset * int(cell * 0.08), y + int(cell * 0.43)),
                         max(2, int(3 * escala)))
    pygame.draw.rect(surf, (91, 100, 79), (x - int(cell * 0.18), y - int(cell * 0.19),
                                            max(4, int(cell * 0.36)), max(3, int(cell * 0.06))))


def dibujar_espada_verde(surf, cx, cy, cell, t, direccion, progreso):
    """Retrocompatibilidad: tajo de la espada de ceniza."""
    dibujar_ataque_arma(surf, cx, cy, cell, t, direccion, progreso, arma_id="espada_ceniza")


def _ataque_daga(surf, cx, cy, cell, t, dx, dy, px, py, progreso):
    """Tajo ágil y curvo de estela umbría con niebla nocturna."""
    morado = (180, 70, 240)
    p = max(0.0, min(1.0, progreso))
    alpha = max(0.0, 1.0 - p * 0.5)
    puntos = []
    for i in range(9):
        k = i / 8
        ang = (k - 0.5) * 2.2 + (p - 0.5) * 0.8
        fwd = cell * (0.25 + 0.42 * math.cos(ang))
        lat = cell * 0.5 * math.sin(ang)
        puntos.append((int(cx + dx * fwd + px * lat), int(cy + dy * fwd + py * lat)))
    brillo(surf, puntos[len(puntos) // 2], max(5, int(cell * 0.6)), (60, 20, 100), 0.42 * alpha)
    brillo(surf, puntos[-1], max(4, int(cell * 0.35)), morado, 0.45 * alpha)
    pygame.draw.lines(surf, (50, 18, 80), False, puntos, max(4, cell // 7))
    pygame.draw.lines(surf, morado, False, puntos, max(2, cell // 14))
    pygame.draw.lines(surf, (235, 190, 255), False, puntos[3:], max(1, cell // 34))
    for i in range(4):
        nx = cx + dx * cell * (0.2 + i * 0.16) + px * math.sin(t * 7 + i * 1.7) * cell * 0.25
        ny = cy + dy * cell * (0.2 + i * 0.16) + py * math.sin(t * 7 + i * 1.7) * cell * 0.25
        brillo(surf, (nx, ny), max(3, int(cell * 0.22)), (40, 14, 70), 0.30 * alpha)


def _ataque_baston(surf, cx, cy, cell, t, dx, dy, px, py, progreso):
    """Destello y haz frontal de centellas eléctricas."""
    cian = (100, 230, 255)
    p = max(0.0, min(1.0, progreso))
    alpha = max(0.0, 1.0 - p * 0.45)
    ini = (cx + dx * cell * 0.15, cy + dy * cell * 0.15)
    fin = (cx + dx * cell * 0.85, cy + dy * cell * 0.85)
    brillo(surf, ini, max(5, int(cell * 0.45)), cian, 0.5 * alpha)
    brillo(surf, fin, max(5, int(cell * 0.4)), cian, 0.35 * alpha)
    for rayo in range(2):
        pts = [(int(ini[0]), int(ini[1]))]
        for i in range(1, 7):
            k = i / 6
            off = math.sin(t * 40 + i * 2.3 + rayo * 3.1) * cell * 0.12 * (1 if i < 6 else 0)
            pts.append((int(ini[0] + (fin[0] - ini[0]) * k + px * off),
                        int(ini[1] + (fin[1] - ini[1]) * k + py * off)))
        pygame.draw.lines(surf, (30, 100, 140), False, pts, max(3, cell // 10) if rayo == 0 else 2)
        pygame.draw.lines(surf, cian if rayo == 0 else (225, 250, 255), False, pts,
                          max(1, cell // 22))
    oro = (255, 215, 90)
    for i in range(5):
        k = 0.25 + 0.15 * i
        salt = math.sin(t * 23 + i * 1.9) * cell * 0.22
        x = cx + dx * cell * k + px * salt
        y = cy + dy * cell * k + py * salt
        pygame.draw.rect(surf, oro, (int(x), int(y), max(2, cell // 18), max(2, cell // 18)))


def dibujar_ataque_arma(surf, cx, cy, cell, t, direccion, progreso, arma_id="espada_ceniza"):
    """Dibuja el ataque del arma equipada (espada_ceniza, daga_sombras, baston_centella)."""
    vectores = {"arriba": (0, -1), "abajo": (0, 1),
                "izquierda": (-1, 0), "derecha": (1, 0)}
    dx, dy = vectores.get(direccion, (0, 1))
    px, py = -dy, dx
    if arma_id == "daga_sombras":
        _ataque_daga(surf, cx, cy, cell, t, dx, dy, px, py, progreso)
        return
    if arma_id == "baston_centella":
        _ataque_baston(surf, cx, cy, cell, t, dx, dy, px, py, progreso)
        return
    barrido = math.cos(max(0.0, min(1.0, progreso)) * math.pi) * 0.28
    hilt = (int(cx + dx * cell * 0.08 - px * cell * 0.10),
            int(cy + dy * cell * 0.08 - py * cell * 0.10))
    punta = (int(cx + dx * cell * 0.67 + px * cell * barrido),
             int(cy + dy * cell * 0.67 + py * cell * barrido))
    alpha = max(0.0, min(1.0, 1.0 - progreso * 0.42))
    verde = (75, 221, 104)
    brillo(surf, punta, max(5, int(cell * 0.54)), verde, 0.38 * alpha)
    pygame.draw.line(surf, (29, 56, 38), hilt, punta, max(4, cell // 8))
    pygame.draw.line(surf, (118, 240, 137), hilt, punta, max(2, cell // 18))
    pygame.draw.line(surf, (207, 255, 194),
                     (int((hilt[0] + punta[0]) / 2), int((hilt[1] + punta[1]) / 2)),
                     punta, max(1, cell // 34))
    pygame.draw.line(surf, (184, 139, 75),
                     (hilt[0] - int(px * cell * 0.11), hilt[1] - int(py * cell * 0.11)),
                     (hilt[0] + int(px * cell * 0.11), hilt[1] + int(py * cell * 0.11)),
                     max(2, cell // 12))
    for i in range(3):
        k = 0.34 + i * 0.22
        ex = int(hilt[0] + (punta[0] - hilt[0]) * k)
        ey = int(hilt[1] + (punta[1] - hilt[1]) * k)
        salt = math.sin(t * 19 + i * 2.1) * cell * 0.07
        pygame.draw.rect(surf, (119, 255, 111),
                         (int(ex + px * salt), int(ey + py * salt), max(2, cell // 18),
                          max(2, cell // 18)))


def dibujar_pista(surf, camino, origen, cell, t):
    """
    Dibuja el camino sugerido como puntos dorados que parpadean en ola.

    Recibe:
        surf: superficie.
        camino: lista de casillas (fila, columna) devuelta por el BFS.
        origen: esquina (x, y) del tablero en pantalla.
        cell: tamaño de casilla.
        t: tiempo en segundos.
    Devuelve:
        Nada.
    """
    ox, oy = origen
    for i, (f, c) in enumerate(camino):
        b = 0.5 + 0.5 * math.sin(i * 0.45 - t * 6)
        x, y = ox + (c + 0.5) * cell, oy + (f + 0.5) * cell
        brillo(surf, (x, y), int(cell * 0.55), ORO, 0.35 * b)
        pygame.draw.rect(surf, mezclar((98, 75, 33), ORO, b),
                         (int(x - cell * 0.09), int(y - cell * 0.09),
                          max(3, int(cell * 0.18)), max(3, int(cell * 0.18))))


class Linterna:
    """Oscurece el tablero salvo alrededor del jugador (y un resplandor en la salida y las antorchas)."""

    def __init__(self, tam_tablero, radio, tinte=(7, 9, 4)):
        """
        Prepara la capa oscura y los "agujeros" de luz.

        Recibe:
            tam_tablero: (ancho, alto) del tablero en píxeles.
            radio: radio de la luz del jugador.
            tinte: color de la oscuridad (cada nivel tiene el suyo).
        Devuelve:
            Nada (constructor).
        """
        self.capa = pygame.Surface(tam_tablero, pygame.SRCALPHA)
        self.tinte = tinte
        self.grande = self._agujero(radio)
        self.radio_chico = max(2, int(radio * 0.42))
        self.chico = self._agujero(self.radio_chico)
        self._agujeros = {self.radio_chico: self.chico}      # luces ya pintadas, por radio

    @staticmethod
    def _agujero(radio):
        """(Interno) Círculo de luz: transparente al centro y opaco hacia el borde."""
        s = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
        for r in range(radio, 0, -1):
            a = min(255, int(330 * (1 - r / radio) ** 0.85))
            pygame.draw.circle(s, (0, 0, 0, a), (radio, radio), r)
        return s

    def _agujero_escalado(self, escala):
        """
        (Interno) Devuelve un agujero de luz pequeño con el tamaño pedido, pintándolo solo la
        primera vez (el parpadeo usa pocos tamaños distintos, así que no pesa).

        Recibe:
            escala: 1.0 es el tamaño normal; 1.2 es 20 % más grande.
        Devuelve:
            Una Surface con transparencia por píxel.
        """
        radio = max(2, int(self.radio_chico * escala) // 2 * 2)
        if radio not in self._agujeros:
            self._agujeros[radio] = self._agujero(radio)
        return self._agujeros[radio]

    def dibujar(self, surf, origen, luz_jugador, otras_luces=(), oscuridad=232):
        """
        Dibuja la oscuridad sobre el tablero.

        Recibe:
            surf: superficie.
            origen: esquina (x, y) del tablero en pantalla.
            luz_jugador: posición (x, y) del jugador RELATIVA al tablero.
            otras_luces: luces pequeñas relativas al tablero: (x, y) o (x, y, escala), donde
                escala hace la luz más grande o más chica (así parpadean las antorchas).
            oscuridad: opacidad 0-255 de la capa oscura (menor = el laberinto se ve más).
        Devuelve:
            Nada.
        """
        self.capa.fill((*self.tinte, oscuridad))
        rg = self.grande.get_width() // 2
        self.capa.blit(self.grande, (int(luz_jugador[0]) - rg, int(luz_jugador[1]) - rg),
                       special_flags=pygame.BLEND_RGBA_SUB)
        for luz in otras_luces:
            agujero = self._agujero_escalado(luz[2] if len(luz) > 2 else 1.0)
            rc = agujero.get_width() // 2
            self.capa.blit(agujero, (int(luz[0]) - rc, int(luz[1]) - rc),
                           special_flags=pygame.BLEND_RGBA_SUB)
        surf.blit(self.capa, origen)


def dibujar_eco(surf, cx, cy, cell, t):
    """
    Dibuja el ECO: una silueta translúcida de azul pálido que flota y parpadea.

    Recibe:
        surf: superficie.
        cx, cy: centro en pantalla.
        cell: tamaño de casilla.
        t: tiempo en segundos (para flotar y parpadear).
    Devuelve:
        Nada.
    """
    r = max(6, int(cell * 0.42))
    lado = r * 4
    c = lado // 2
    flota = math.sin(t * 3) * cell * 0.05
    alfa = int(150 + 45 * math.sin(t * 5))
    capa = pygame.Surface((lado, lado), pygame.SRCALPHA)
    cabeza = (c, int(c - r * 0.45 + flota))
    pygame.draw.circle(capa, (170, 225, 255, alfa), cabeza, max(2, int(r * 0.42)))
    tunica = [(c - r * 0.45, c - r * 0.05 + flota), (c + r * 0.45, c - r * 0.05 + flota)]
    for i in range(5):                                     # orilla inferior ondulada
        x = c + r * 0.62 - i * (r * 1.24 / 4)
        y = c + r * (0.85 if i % 2 == 0 else 0.6) + flota + math.sin(t * 6 + i) * r * 0.06
        tunica.append((x, y))
    pygame.draw.polygon(capa, (130, 205, 255, int(alfa * 0.85)), tunica)
    for lado_ojo in (-1, 1):
        pygame.draw.circle(capa, (20, 40, 80, 230),
                           (int(c + lado_ojo * r * 0.18), int(cabeza[1])), max(1, int(r * 0.08)))
    brillo(surf, (cx, cy), int(cell * 1.05), (70, 150, 255), 0.6)
    surf.blit(capa, (int(cx) - c, int(cy) - c))


def dibujar_radar(surf, cx, cy, cell, t):
    """
    Dibuja el RADAR: un punto rojo que late y emite un anillo que se expande y se desvanece.

    Recibe:
        surf: superficie.
        cx, cy: centro en pantalla.
        cell: tamaño de casilla.
        t: tiempo en segundos (para el latido y el anillo).
    Devuelve:
        Nada.
    """
    r = max(4, int(cell * 0.22))
    fase = (t * 1.2) % 1.0                                   # 0 a 1: avance del anillo
    pulso = 0.5 + 0.5 * math.sin(t * 6)
    brillo(surf, (cx, cy), int(cell * (0.9 + 0.2 * pulso)), (255, 40, 40), 0.55)
    lado = int(cell * 2)
    c = lado // 2
    capa = pygame.Surface((lado, lado), pygame.SRCALPHA)
    anillo = int(r * (1.4 + 1.6 * fase))
    pygame.draw.circle(capa, (255, 70, 70, max(0, int(200 * (1.0 - fase)))), (c, c), anillo, 2)
    pygame.draw.circle(capa, (255, 60, 60, 255), (c, c), r)
    pygame.draw.circle(capa, (255, 200, 200, 255), (c - r // 3, c - r // 3), max(1, r // 3))
    surf.blit(capa, (int(cx) - c, int(cy) - c))


# =====================================================================================
#  COLECCIONABLES (ESTRELLAS Y COFRES) E ICONOS DE INVENTARIO / CÓDICE OCULTO
# =====================================================================================
COLORES_RAREZA = {
    "Común": (168, 176, 152),
    "Rara": (92, 184, 230),
    "Épica": (214, 132, 240),
    "Legendaria": ORO,
}


def dibujar_estrella(surf, cx, cy, cell, t):
    """
    Dibuja una gema/estrella dorada coleccionable con levitación senoidal
    (math.sin(t * 3.5) * 3 px), halo brillante y polvo dorado alrededor.

    Recibe:
        surf: superficie de pygame.
        cx, cy: centro de la casilla en pantalla.
        cell: tamaño de la casilla en píxeles.
        t: tiempo en segundos.
    Devuelve:
        Nada.
    """
    flota = math.sin(t * 3.5) * 3.0
    pulso = 0.78 + 0.22 * math.sin(t * 5.0 + cx * 0.03)
    x = int(cx)
    y = int(cy + flota)

    # Sombra suave en el suelo que se encoge cuando la estrella sube.
    sombra_w = max(6, int(cell * (0.36 - 0.03 * math.sin(t * 3.5))))
    sombra_h = max(3, int(cell * 0.14))
    pygame.draw.ellipse(surf, (10, 12, 9),
                        (x - sombra_w // 2, int(cy + cell * 0.28), sombra_w, sombra_h))

    # Halo brillante dorado.
    brillo(surf, (x, y), max(6, int(cell * 0.85 * pulso)), ORO, 0.48 * pulso)

    # Polvo dorado orbital sutil.
    radio_polvo = max(5, int(cell * 0.36))
    for i in range(4):
        ang = t * 2.4 + i * (math.tau / 4)
        px = int(x + math.cos(ang) * radio_polvo)
        py = int(y + math.sin(ang * 1.3) * (radio_polvo * 0.65))
        tam_p = 2 if (i + int(t * 4)) % 2 == 0 else 1
        pygame.draw.rect(surf, (255, 232, 148), (px, py, tam_p, tam_p))

    # Cuerpo de estrella/gema de 5 puntas (con facetas interiores).
    r_ext = max(5, int(cell * 0.34))
    r_int = max(2, int(r_ext * 0.44))
    puntos = []
    for i in range(10):
        ang = -math.pi / 2 + i * (math.pi / 5)
        r = r_ext if i % 2 == 0 else r_int
        puntos.append((int(x + math.cos(ang) * r), int(y + math.sin(ang) * r)))

    pygame.draw.polygon(surf, (168, 112, 28), [(px, py + 1) for px, py in puntos])
    pygame.draw.polygon(surf, (246, 198, 76), puntos)
    pygame.draw.polygon(surf, (255, 240, 170), puntos, 1)
    # Núcleo centelleante.
    pygame.draw.circle(surf, (255, 250, 210), (x, y), max(1, int(r_int * 0.65)))


def dibujar_cofre(surf, cx, cy, cell, t, abierto=False):
    """
    Dibuja un cofre de madera noble y herrajes de bronce.
    Si abierto=False: tapa cerrada, candado frontal y brillo ámbar tenue.
    Si abierto=True: tapa abierta mostrando el resplandor interior del botín.

    Recibe:
        surf: superficie de pygame.
        cx, cy: centro de la casilla en pantalla.
        cell: tamaño de la casilla en píxeles.
        t: tiempo en segundos.
        abierto: True si el cofre ya fue abierto.
    Devuelve:
        Nada.
    """
    x, y = int(cx), int(cy)
    w = max(10, int(cell * 0.64))
    h = max(8, int(cell * 0.48))
    pulso = 0.75 + 0.25 * math.sin(t * 4.0 + cx * 0.04)

    # Sombra en el piso.
    pygame.draw.ellipse(surf, (9, 12, 10),
                        (x - w // 2 - 2, y + h // 2 - 2, w + 4, max(4, cell // 6)))

    madera_oscura = (68, 43, 24)
    madera_clara = (108, 69, 37)
    bronce = (196, 152, 74)
    bronce_luz = (242, 206, 122)

    if not abierto:
        # Brillo ámbar de cofre cerrado esperando ser descubierto.
        brillo(surf, (x, y), max(6, int(cell * 0.78)), ORO, 0.32 * pulso)

        caja = pygame.Rect(x - w // 2, y - h // 2 + 2, w, h)
        # Base del cofre.
        pygame.draw.rect(surf, madera_oscura, caja, border_radius=2)
        # Tapa abovedada superior.
        tapa = pygame.Rect(caja.x, caja.y - max(2, h // 5), caja.w, max(4, h // 2))
        pygame.draw.rect(surf, madera_clara, tapa, border_radius=3)
        # Bandas y bordes de bronce.
        pygame.draw.rect(surf, bronce, caja, 1, border_radius=2)
        pygame.draw.line(surf, (32, 20, 12),
                         (caja.x + 1, caja.centery), (caja.right - 2, caja.centery), 2)
        for bx in (caja.x + max(2, w // 5), caja.right - max(3, w // 5) - 1):
            pygame.draw.line(surf, bronce, (bx, tapa.y + 1), (bx, caja.bottom - 2), max(1, w // 10))
        # Cerradura central con destello ámbar.
        cerradura = pygame.Rect(x - 2, caja.centery - 2, 5, 5)
        pygame.draw.rect(surf, bronce_luz, cerradura, border_radius=1)
        pygame.draw.rect(surf, (40, 28, 14), (x - 1, caja.centery, 2, 2))
    else:
        # Resplandor interior dorado/cian cuando está abierto.
        brillo(surf, (x, y - 2), max(6, int(cell * 0.68)), (255, 215, 110), 0.26 * pulso)

        base_h = max(5, int(h * 0.62))
        base = pygame.Rect(x - w // 2, y + h // 2 - base_h, w, base_h)
        tapa_abierta = pygame.Rect(x - w // 2, base.y - max(4, int(h * 0.52)),
                                   w, max(4, int(h * 0.45)))
        # Tapa levantada detrás.
        pygame.draw.rect(surf, (52, 33, 18), tapa_abierta, border_radius=2)
        pygame.draw.rect(surf, bronce, tapa_abierta, 1, border_radius=2)
        # Interior iluminado con fulgor dorado.
        interior = pygame.Rect(base.x + 2, base.y - 2, base.w - 4, 5)
        pygame.draw.rect(surf, mezclar(ORO, (255, 248, 195), 0.55 * pulso), interior)
        # Base de madera y herrajes.
        pygame.draw.rect(surf, madera_oscura, base, border_radius=2)
        pygame.draw.rect(surf, bronce, base, 1, border_radius=2)
        for bx in (base.x + max(2, w // 5), base.right - max(3, w // 5) - 1):
            pygame.draw.line(surf, bronce, (bx, base.y + 1), (bx, base.bottom - 2), max(1, w // 10))


def dibujar_icono_item(surf, rect, tipo_icono, descubierto=True, color_acento=None):
    """
    Dibuja el icono pixel-art de un objeto del códice dentro de `rect`.
    Si descubierto=False (o tipo_icono == 'incognita'), dibuja un candado / silueta en penumbra.

    Recibe:
        surf: superficie de pygame.
        rect: pygame.Rect donde centrar el icono.
        tipo_icono: 'espada', 'daga', 'baston', 'tunica', 'coraza', 'manto',
                    'bota', 'ojo', 'escudo' o 'incognita'.
        descubierto: False para mostrar candado y silueta oculta.
        color_acento: color opcional de rareza.
    Devuelve:
        Nada.
    """
    r = pygame.Rect(rect)
    cx, cy = r.centerx, r.centery
    escala = min(r.w, r.h)
    rad = max(8, int(escala * 0.36))

    if not descubierto or tipo_icono == "incognita":
        # Silueta oscura con candado de bronce apagado.
        pygame.draw.circle(surf, (18, 20, 17), (cx, cy), rad + 2)
        arco = pygame.Rect(cx - rad // 2, cy - rad + 2, rad, rad)
        pygame.draw.arc(surf, (96, 90, 70), arco, 0, math.pi, max(2, rad // 4))
        cuerpo = pygame.Rect(cx - int(rad * 0.68), cy - 2, int(rad * 1.36), int(rad * 0.95))
        pygame.draw.rect(surf, (44, 41, 33), cuerpo, border_radius=3)
        pygame.draw.rect(surf, (112, 102, 76), cuerpo, 2, border_radius=3)
        pygame.draw.circle(surf, (20, 19, 15), (cx, cuerpo.centery - 1), max(2, rad // 5))
        pygame.draw.line(surf, (20, 19, 15), (cx, cuerpo.centery), (cx, cuerpo.bottom - 3), 2)
        return

    acento = color_acento or ORO
    brillo(surf, (cx, cy), int(rad * 1.45), acento, 0.22)

    if tipo_icono == "espada":
        # Espada de Ceniza (fuego verde).
        p1 = (cx - int(rad * 0.65), cy + int(rad * 0.65))
        p2 = (cx + int(rad * 0.72), cy - int(rad * 0.72))
        pygame.draw.line(surf, (46, 92, 58), p1, p2, max(4, rad // 3))
        pygame.draw.line(surf, (124, 242, 138), p1, p2, max(2, rad // 5))
        guarda_a = (cx - int(rad * 0.55), cy + int(rad * 0.10))
        guarda_b = (cx - int(rad * 0.10), cy + int(rad * 0.55))
        pygame.draw.line(surf, ORO, guarda_a, guarda_b, max(3, rad // 4))
        pygame.draw.circle(surf, (238, 196, 102), p1, max(2, rad // 5))
    elif tipo_icono == "daga":
        # Daga de Sombras (hojas gemelas curvas).
        for dx, col in ((-3, (118, 168, 224)), (3, (176, 218, 255))):
            pygame.draw.polygon(surf, col, [
                (cx + dx, cy - int(rad * 0.75)),
                (cx + dx + int(rad * 0.32), cy + int(rad * 0.15)),
                (cx + dx, cy + int(rad * 0.45)),
                (cx + dx - int(rad * 0.22), cy + int(rad * 0.10)),
            ])
        pygame.draw.line(surf, ORO, (cx - int(rad * 0.5), cy + int(rad * 0.35)),
                         (cx + int(rad * 0.5), cy + int(rad * 0.35)), 3)
        pygame.draw.rect(surf, (92, 66, 44), (cx - 2, cy + int(rad * 0.35), 5, int(rad * 0.42)))
    elif tipo_icono == "baston":
        # Bastón de Centella (vara arcana con orbe eléctrico).
        pygame.draw.line(surf, (122, 84, 48),
                         (cx - int(rad * 0.55), cy + int(rad * 0.75)),
                         (cx + int(rad * 0.38), cy - int(rad * 0.38)), max(3, rad // 4))
        orbe = (cx + int(rad * 0.42), cy - int(rad * 0.42))
        pygame.draw.circle(surf, (214, 132, 240), orbe, max(4, int(rad * 0.42)))
        pygame.draw.circle(surf, (255, 240, 200), orbe, max(2, int(rad * 0.22)))
    elif tipo_icono == "tunica":
        # Manto del Viajero.
        pts = [
            (cx - int(rad * 0.35), cy - int(rad * 0.65)),
            (cx + int(rad * 0.35), cy - int(rad * 0.65)),
            (cx + int(rad * 0.72), cy - int(rad * 0.15)),
            (cx + int(rad * 0.52), cy + int(rad * 0.72)),
            (cx - int(rad * 0.52), cy + int(rad * 0.72)),
            (cx - int(rad * 0.72), cy - int(rad * 0.15)),
        ]
        pygame.draw.polygon(surf, (68, 86, 78), pts)
        pygame.draw.polygon(surf, (158, 176, 152), pts, 2)
        pygame.draw.line(surf, ORO, (cx, cy - int(rad * 0.55)), (cx, cy + int(rad * 0.68)), 2)
    elif tipo_icono == "coraza":
        # Coraza del Guardián.
        pecho = pygame.Rect(cx - int(rad * 0.62), cy - int(rad * 0.58),
                            int(rad * 1.24), int(rad * 1.20))
        pygame.draw.rect(surf, (94, 118, 136), pecho, border_radius=4)
        pygame.draw.rect(surf, (182, 214, 238), pecho, 2, border_radius=4)
        pygame.draw.line(surf, ORO, (cx, pecho.y + 3), (cx, pecho.bottom - 3), 2)
        pygame.draw.line(surf, ORO, (pecho.x + 4, cy), (pecho.right - 4, cy), 2)
    elif tipo_icono == "manto":
        # Manto de Bruma.
        pts = [
            (cx, cy - int(rad * 0.78)),
            (cx + int(rad * 0.68), cy - int(rad * 0.15)),
            (cx + int(rad * 0.56), cy + int(rad * 0.72)),
            (cx, cy + int(rad * 0.52)),
            (cx - int(rad * 0.56), cy + int(rad * 0.72)),
            (cx - int(rad * 0.68), cy - int(rad * 0.15)),
        ]
        pygame.draw.polygon(surf, (92, 64, 118), pts)
        pygame.draw.polygon(surf, (208, 160, 244), pts, 2)
    elif tipo_icono == "bota":
        # Paso Ligero.
        pts = [
            (cx - int(rad * 0.35), cy - int(rad * 0.65)),
            (cx + int(rad * 0.15), cy - int(rad * 0.65)),
            (cx + int(rad * 0.15), cy + int(rad * 0.15)),
            (cx + int(rad * 0.68), cy + int(rad * 0.32)),
            (cx + int(rad * 0.68), cy + int(rad * 0.68)),
            (cx - int(rad * 0.45), cy + int(rad * 0.68)),
        ]
        pygame.draw.polygon(surf, (132, 92, 52), pts)
        pygame.draw.polygon(surf, ORO, pts, 2)
    elif tipo_icono == "ojo":
        # Ojo del Zahorí.
        pts = [
            (cx - int(rad * 0.78), cy),
            (cx, cy - int(rad * 0.48)),
            (cx + int(rad * 0.78), cy),
            (cx, cy + int(rad * 0.48)),
        ]
        pygame.draw.polygon(surf, (42, 68, 78), pts)
        pygame.draw.polygon(surf, (124, 214, 242), pts, 2)
        pygame.draw.circle(surf, ORO, (cx, cy), max(3, int(rad * 0.28)))
        pygame.draw.circle(surf, (20, 22, 18), (cx, cy), max(1, int(rad * 0.12)))
    else:
        # Escudo / Velo contra el Eco (por defecto).
        pts = [
            (cx - int(rad * 0.62), cy - int(rad * 0.62)),
            (cx + int(rad * 0.62), cy - int(rad * 0.62)),
            (cx + int(rad * 0.56), cy + int(rad * 0.12)),
            (cx, cy + int(rad * 0.76)),
            (cx - int(rad * 0.56), cy + int(rad * 0.12)),
        ]
        pygame.draw.polygon(surf, (64, 98, 128), pts)
        pygame.draw.polygon(surf, acento, pts, 2)
        pygame.draw.circle(surf, (235, 222, 168), (cx, cy - 2), max(2, rad // 4))


def dibujar_ranura_item(surf, rect, item, seleccionado=False, equipado=False):
    """
    Dibuja una casilla interactiva del inventario / Códice Oculto.
    Si item['descubierto'] es False: casilla en penumbra con borde tenue, candado y título '???'.
    Si item['descubierto'] es True: icono del objeto con su color de rareza y nombre visible.

    Recibe:
        surf: superficie de pygame.
        rect: pygame.Rect de la casilla.
        item: diccionario del ítem (con claves 'descubierto', 'nombre', 'icono', 'rareza', etc.).
        seleccionado: True si la casilla está seleccionada por el usuario.
        equipado: True si el ítem está actualmente equipado.
    Devuelve:
        Nada.
    """
    r = pygame.Rect(rect)
    descubierto = bool(item.get("descubierto", False))
    rareza = item.get("rareza", "Común")
    color_rareza = COLORES_RAREZA.get(rareza, ORO)

    if not descubierto:
        fondo = (16, 17, 14) if not seleccionado else (28, 28, 22)
        borde = (64, 60, 46) if not seleccionado else ORO
        pygame.draw.rect(surf, fondo, r, border_radius=6)
        pygame.draw.rect(surf, borde, r, 2 if not seleccionado else 3, border_radius=6)
        icono_rect = pygame.Rect(r.x + 8, r.y + 6, r.w - 16, max(24, r.h - 30))
        dibujar_icono_item(surf, icono_rect, "incognita", descubierto=False)
        texto(surf, "???", 14, (118, 112, 92) if not seleccionado else ORO,
              (r.centerx, r.bottom - 13), "center", negrita=True, sombra=False)
        return

    fondo = mezclar((26, 28, 22), color_rareza, 0.16 if not seleccionado else 0.28)
    borde = ORO if seleccionado else mezclar(BORDE, color_rareza, 0.65)
    pygame.draw.rect(surf, fondo, r, border_radius=6)
    if seleccionado:
        brillo(surf, r.center, max(24, int(min(r.w, r.h) * 0.75)), color_rareza, 0.22)
    pygame.draw.rect(surf, borde, r, 3 if seleccionado else 2, border_radius=6)

    icono_rect = pygame.Rect(r.x + 8, r.y + 6, r.w - 16, max(24, r.h - 30))
    dibujar_icono_item(surf, icono_rect, item.get("icono", "espada"),
                       descubierto=True, color_acento=color_rareza)

    nombre = item.get("nombre", "Artefacto")
    texto_ajustado(surf, nombre, 12, TEXTO if seleccionado else (210, 204, 178),
                   (r.centerx, r.bottom - 12), r.w - 10, "center", negrita=seleccionado)

    if equipado or item.get("equipado", False):
        insignia = pygame.Rect(r.right - 22, r.y + 4, 18, 16)
        pygame.draw.rect(surf, (32, 58, 34), insignia, border_radius=3)
        pygame.draw.rect(surf, VERDE, insignia, 1, border_radius=3)
        texto(surf, "E", 11, VERDE, insignia.center, "center", negrita=True, sombra=False)

