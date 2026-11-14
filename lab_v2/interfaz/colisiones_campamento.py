"""
colisiones_campamento.py
Límites transitables y cajas de colisión del Claro de Ceniza (campamento explorable).

Todas las cajas están calibradas sobre las coordenadas con las que `pantallas.Campamento`
dibuja cada objeto, para que el personaje choque con lo que se ve y no "con la nada":

    * Hoguera: se ajusta al anillo de piedras y la llama (≈ 76x60 px, radio ≈ 38 px)
      en lugar del antiguo bloque de 192x97 px.
    * Límite norte: baja de y=244 a y=150, de modo que se puede recorrer el claro hasta
      el pie del Umbral (el propio portón y la cerca del cementerio siguen bloqueando).
    * Portón: la caja termina 4 px por encima de la base de las puertas, así el viajero
      llega al rótulo "EL UMBRAL" sin rebotar antes.
    * Carpas, hamaca, carro, cajas/mesa del mapa, cementerio y sobrevivientes (Mara, Ivo,
      Nela y Tizón): cajas proporcionales a su dibujo (las carpas triangulares se aproximan
      con franjas escalonadas).

Contrato (ver TASKS.md, sección 3):
    obtener_limites_campamento()              -> (min_x, min_y, max_x, max_y)
    obtener_bloqueos_campamento(porton_rect)  -> list[pygame.Rect]
    es_posicion_valida(caja, bloqueos, limites) -> bool

Los límites se expresan sobre el CENTRO del personaje (igual que la comprobación original
`26 <= nx <= ANCHO - 26`): `es_posicion_valida` compara `caja.center` contra ellos.

Solo describe geometría: no dibuja (salvo la ayuda de depuración) ni cambia reglas del juego.
"""

import pygame

from interfaz.tema import ANCHO, ALTO

# ------------------------------------------------------------------------------------
#  Referencias visuales compartidas (coinciden con el dibujo de pantallas.Campamento)
# ------------------------------------------------------------------------------------
CENTRO_HOGUERA = (550, 478)
PORTON_POR_DEFECTO = (444, 86, 212, 194)          # x, y, ancho, alto del portón del Umbral
CENTRO_UMBRAL = (550, 294)                        # punto de interacción del portón
RADIO_UMBRAL = 135
PUNTO_INICIO = (550.0, 596.0)                     # aparición por defecto en el campamento

SOBREVIVIENTES = {"mara": (370, 443), "ivo": (735, 526), "nela": (302, 558)}
DUENDE = (803, 363)                               # Tizón

# Límites del centro del personaje: (min_x, min_y, max_x, max_y).
MARGEN_LATERAL = 26
LIMITE_NORTE = 150                                # antes 244: muro invisible en mitad del claro
MARGEN_SUR = 28                                   # el HUD inferior empieza en y=638

# Caja del personaje que se recomienda usar con este módulo (ancho, alto).
TAM_CAJA_PERSONAJE = (18, 16)


def obtener_limites_campamento() -> tuple[int, int, int, int]:
    """
    Devuelve los límites transitables del claro para el centro del personaje.

    Recibe: nada.
    Devuelve:
        (min_x, min_y, max_x, max_y). El norte llega a y=150 (zona alta del claro, al pie del
        Umbral); la barrera artificial de y=244 desaparece.
    """
    return (MARGEN_LATERAL, LIMITE_NORTE, ANCHO - MARGEN_LATERAL, ALTO - MARGEN_SUR)


def _caja_porton(porton_rect: pygame.Rect) -> pygame.Rect:
    """
    (Interno) Caja del portón: cubre el marco dibujado (28 px a cada lado y las almenas
    30 px por encima) y termina 4 px antes de la base de las puertas.

    Recibe: porton_rect (Rect del portón tal como lo dibuja el campamento).
    Devuelve: un pygame.Rect.
    """
    p = pygame.Rect(porton_rect)
    return pygame.Rect(p.x - 28, p.y - 30, p.w + 56, p.h + 26)


def _caja_personaje_quieto(x: int, y: int) -> pygame.Rect:
    """(Interno) Caja de un sobreviviente de pie: torso y pies (24x22 px). Devuelve: Rect."""
    return pygame.Rect(x - 12, y - 8, 24, 22)


def obtener_bloqueos_campamento(porton_rect: pygame.Rect = None) -> list[pygame.Rect]:
    """
    Devuelve las cajas de colisión ajustadas a los objetos visibles del campamento.

    Recibe:
        porton_rect: Rect del portón del Umbral (opcional; por defecto (444, 86, 212, 194)).
    Devuelve:
        Una lista NUEVA de pygame.Rect (se puede modificar sin afectar otras llamadas).
    """
    porton = pygame.Rect(porton_rect) if porton_rect is not None else pygame.Rect(PORTON_POR_DEFECTO)
    hx, hy = CENTRO_HOGUERA
    bloqueos = [
        # Portón del Umbral.
        _caja_porton(porton),
        # Hoguera: anillo de piedras y troncos (radio ≈ 38 px); se rodea por ambos costados.
        pygame.Rect(hx - 38, hy - 22, 76, 60),
        # Carpa oeste: triángulo (94,519)-(177,455)-(260,519) + entrada (143,514,69,50).
        pygame.Rect(148, 466, 58, 22),
        pygame.Rect(114, 488, 126, 31),
        pygame.Rect(143, 519, 69, 45),
        # Carpa este: triángulo (852,459)-(927,405)-(1000,459) + entrada (896,454,63,53).
        pygame.Rect(900, 414, 54, 22),
        pygame.Rect(866, 436, 122, 23),
        pygame.Rect(896, 459, 63, 48),
        # Suministros: caja de madera, barril y mesa con el mapa.
        pygame.Rect(830, 533, 54, 51),
        pygame.Rect(948, 536, 30, 42),
        pygame.Rect(850, 580, 125, 34),
        # Hamaca: tela entre los postes (x 194 y 336) y los propios postes hasta el suelo.
        pygame.Rect(190, 322, 150, 34),
        pygame.Rect(190, 322, 9, 56),
        pygame.Rect(331, 322, 9, 56),
        # Cementerio cercado (lápidas y cerca).
        pygame.Rect(45, 258, 260, 65),
        # Carro: plataforma y ruedas, más la carga apilada encima.
        pygame.Rect(76, 568, 126, 51),
        pygame.Rect(119, 546, 61, 22),
    ]
    for x, y in SOBREVIVIENTES.values():
        bloqueos.append(_caja_personaje_quieto(x, y))
    # Tizón es más bajo y ancho que los sobrevivientes.
    bloqueos.append(pygame.Rect(DUENDE[0] - 14, DUENDE[1] - 11, 28, 24))
    return bloqueos


def es_posicion_valida(caja: pygame.Rect, bloqueos: list[pygame.Rect],
                       limites: tuple[int, int, int, int]) -> bool:
    """
    Verifica si una caja del personaje está dentro de los límites y no choca con nada.

    Recibe:
        caja: pygame.Rect del personaje en la posición candidata.
        bloqueos: lista de pygame.Rect obstáculo.
        limites: (min_x, min_y, max_x, max_y) aplicados al CENTRO de la caja.
    Devuelve:
        True si la posición es transitable; False si sale de los límites o colisiona.
    """
    caja = pygame.Rect(caja)
    min_x, min_y, max_x, max_y = limites
    cx, cy = caja.center
    if not (min_x <= cx <= max_x and min_y <= cy <= max_y):
        return False
    return caja.collidelist(bloqueos) == -1


def caja_personaje(x: float, y: float) -> pygame.Rect:
    """
    Caja estándar del personaje centrada en (x, y), con el mismo tamaño que usaba el
    campamento (18x16 px). Útil para el controlador y las pruebas.

    Recibe: x, y (posición del centro, admite decimales).
    Devuelve: un pygame.Rect.
    """
    w, h = TAM_CAJA_PERSONAJE
    return pygame.Rect(int(round(x)) - w // 2, int(round(y)) - h // 2, w, h)


def dibujar_colisiones(surf, bloqueos=None, limites=None, color=(255, 60, 60)):
    """
    Ayuda de depuración: dibuja el contorno de las cajas de colisión y de los límites.

    Recibe: surf, bloqueos (opcional), limites (opcional) y color.
    Devuelve: nada.
    """
    for r in (bloqueos if bloqueos is not None else obtener_bloqueos_campamento()):
        pygame.draw.rect(surf, color, r, 1)
    min_x, min_y, max_x, max_y = limites or obtener_limites_campamento()
    pygame.draw.rect(surf, (90, 200, 255), (min_x, min_y, max_x - min_x, max_y - min_y), 1)
