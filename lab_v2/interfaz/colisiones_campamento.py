"""Colisiones del campamento basadas en la mascara nav_campamento.png (consulta O(1))."""
from __future__ import annotations

import math
from pathlib import Path

import pygame

ANCHO, ALTO = 1100, 720

COORD_UMBRAL: tuple[int, int] = (550, 205)
COORD_HOGUERA: tuple[int, int] = (550, 360)
COORD_SPAWN: tuple[float, float] = (550.0, 560.0)
COORD_MARA: tuple[int, int] = (315, 310)
COORD_NELA: tuple[int, int] = (315, 525)
COORD_TIZON: tuple[int, int] = (755, 325)
COORD_IVO: tuple[int, int] = (740, 510)

# Compatibilidad con módulos heredados
CENTRO_HOGUERA = COORD_HOGUERA
CENTRO_UMBRAL = COORD_UMBRAL
PUNTO_INICIO = COORD_SPAWN
SOBREVIVIENTES = {"mara": COORD_MARA, "ivo": COORD_IVO, "nela": COORD_NELA}
DUENDE = COORD_TIZON
LIMITE_NORTE = 180
MARGEN_LATERAL = 26
MARGEN_SUR = 28
TAM_CAJA_PERSONAJE = (18, 16)


def obtener_limites_campamento() -> tuple[int, int, int, int]:
    return (MARGEN_LATERAL, LIMITE_NORTE, ANCHO - MARGEN_LATERAL, ALTO - MARGEN_SUR)


def caja_personaje(x: float, y: float) -> pygame.Rect:
    return pygame.Rect(int(round(x)) - 9, int(round(y)) - 8, 18, 16)


def obtener_bloqueos_campamento(porton_rect=None) -> list[pygame.Rect]:
    return []


def es_posicion_valida(caja: pygame.Rect, bloqueos=None, limites=None) -> bool:
    caja = pygame.Rect(caja)
    if limites:
        min_x, min_y, max_x, max_y = limites
        cx, cy = caja.center
        if not (min_x <= cx <= max_x and min_y <= cy <= max_y):
            return False
    if bloqueos and caja.collidelist(bloqueos) != -1:
        return False
    return es_posicion_caminable(caja.centerx, caja.centery)


_NOMBRE_NAV = "nav_campamento.png"
_mascara: pygame.Mask | None = None


def _localizar_nav() -> Path:
    inicio = Path(__file__).resolve().parent
    for carpeta in (inicio, *inicio.parents):
        candidato = carpeta / _NOMBRE_NAV
        if candidato.is_file():
            return candidato
    raise FileNotFoundError(f"No se encontro {_NOMBRE_NAV}; ejecute herramientas/procesar_mascara_campamento.py")


def _obtener_mascara() -> pygame.Mask:
    """Carga perezosa (una sola vez) de la mascara: bit 1 = transitable."""
    global _mascara
    if _mascara is None:
        superficie = pygame.image.load(str(_localizar_nav()))
        if superficie.get_size() != (ANCHO, ALTO):
            superficie = pygame.transform.scale(superficie, (ANCHO, ALTO))
        _mascara = pygame.mask.from_threshold(superficie, (255, 255, 255), (128, 128, 128, 255))
    return _mascara


def _libre(mascara: pygame.Mask, px: int, py: int) -> bool:
    return 0 <= px < ANCHO and 0 <= py < ALTO and bool(mascara.get_at((px, py)))


def es_posicion_caminable(x: float, y: float, radio: int = 9) -> bool:
    """Comprueba centro y 4 vertices de la caja del viajero; fuera de limites = False."""
    mascara = _obtener_mascara()
    ix, iy = int(math.floor(x)), int(math.floor(y))
    r = int(radio)
    puntos = ((ix, iy), (ix - r, iy - r), (ix + r, iy - r), (ix - r, iy + r), (ix + r, iy + r))
    return all(_libre(mascara, px, py) for px, py in puntos)


def resolver_movimiento_campamento(
    pos_actual: list[float] | tuple[float, float],
    dx: float,
    dy: float,
    dt: float,
    velocidad: float = 190.0,
    radio: int = 9,
) -> tuple[float, float, str, bool]:
    """Movimiento con Wall Sliding: X e Y se evaluan por separado.

    Retorna (nueva_x, nueva_y, direccion, andando).
    """
    x, y = float(pos_actual[0]), float(pos_actual[1])
    direccion = "abajo"
    if dx == 0 and dy == 0:
        return x, y, direccion, False
    norma = math.hypot(dx, dy)
    ndx, ndy = dx / norma, dy / norma
    if abs(ndx) > abs(ndy):
        direccion = "derecha" if ndx > 0 else "izquierda"
    else:
        direccion = "abajo" if ndy > 0 else "arriba"
    paso_x = ndx * velocidad * dt
    paso_y = ndy * velocidad * dt
    nueva_x, nueva_y = x, y
    if paso_x and es_posicion_caminable(x + paso_x, y, radio):
        nueva_x = x + paso_x
    if paso_y and es_posicion_caminable(nueva_x, y + paso_y, radio):
        nueva_y = y + paso_y
    andando = (nueva_x != x) or (nueva_y != y)
    return nueva_x, nueva_y, direccion, andando


def validar_posicion_segura(
    pos_candidata: tuple[float, float] | list[float],
    fallback: tuple[float, float] = COORD_SPAWN,
) -> tuple[float, float]:
    """Devuelve la posicion si es transitable (y finita); si no, el fallback."""
    try:
        x, y = float(pos_candidata[0]), float(pos_candidata[1])
    except (TypeError, ValueError, IndexError, KeyError):
        return (float(fallback[0]), float(fallback[1]))
    if math.isfinite(x) and math.isfinite(y) and es_posicion_caminable(x, y):
        return (x, y)
    return (float(fallback[0]), float(fallback[1]))


def dibujar_debug_colisiones(superficie: pygame.Surface, alpha: int = 120) -> None:
    """Superpone rojo sobre las zonas solidas (caminable queda transparente)."""
    mascara = _obtener_mascara()
    solido = mascara.copy()
    solido.invert()
    capa = solido.to_surface(
        setcolor=(255, 0, 0, max(0, min(255, int(alpha)))), unsetcolor=(0, 0, 0, 0)
    )
    if capa.get_size() != superficie.get_size():
        capa = pygame.transform.scale(capa, superficie.get_size())
    superficie.blit(capa, (0, 0))
