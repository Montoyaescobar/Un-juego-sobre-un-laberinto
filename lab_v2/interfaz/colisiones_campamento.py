"""Colisiones del campamento basadas en la mascara nav_campamento.png (consulta O(1))."""
from __future__ import annotations

import math
from pathlib import Path

import pygame

ANCHO, ALTO = 1100, 720

COORD_UMBRAL: tuple[int, int] = (544, 210)
COORD_HOGUERA: tuple[int, int] = (542, 368)
COORD_SPAWN: tuple[float, float] = (542.0, 590.0)
COORD_MARA: tuple[int, int] = (355, 345)
COORD_NELA: tuple[int, int] = (355, 535)
COORD_TIZON: tuple[int, int] = (720, 345)
COORD_IVO: tuple[int, int] = (705, 520)

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


_DIAG = math.sqrt(2.0) / 2.0
_EPS_CONTACTO = 1e-6
_ITER_BUSQUEDA = 5          # 5 iteraciones: precision <= paso/32 (<0.25 px para pasos <= 8 px)
_MAX_NUDGE = 3.0            # micro-empuje lateral maximo por fotograma (px)
_MAX_OFFSET_SLIP = 4        # desplazamiento lateral maximo evaluado para esquinas (px)


def es_posicion_caminable(x: float, y: float, radio: float = 7.5, muestreo_radial: bool = True) -> bool:
    """Hitbox redondeada en los pies: centro + 4 cardinales (r) + 4 diagonales (0.707 r).

    Con muestreo_radial=False solo se comprueba el centro. Fuera de limites = False.
    """
    mascara = _obtener_mascara()
    ix, iy = int(math.floor(x)), int(math.floor(y))
    if not _libre(mascara, ix, iy):
        return False
    if not muestreo_radial:
        return True
    r = float(radio)
    d = r * _DIAG
    desplazamientos = (
        (r, 0.0), (-r, 0.0), (0.0, r), (0.0, -r),
        (d, d), (-d, d), (d, -d), (-d, -d),
    )
    for ox, oy in desplazamientos:
        if not _libre(mascara, int(math.floor(x + ox)), int(math.floor(y + oy))):
            return False
    return True


def _aproximar_eje(x: float, y: float, paso: float, es_x: bool, radio: float = 7.5) -> float:
    """Distancia (con signo) transitable en un eje, hasta <= |paso|/32 del contacto.

    Si el paso completo es libre lo devuelve; si no, busqueda binaria de 5 iteraciones.
    """
    if paso == 0:
        return 0.0

    def libre(t: float) -> bool:
        return es_posicion_caminable(x + t, y, radio) if es_x else es_posicion_caminable(x, y + t, radio)

    if libre(paso):
        return paso
    if not libre(0.0):
        return 0.0  # ya incrustado: no empeorar ni inventar movimiento
    bajo, alto = 0.0, paso
    for _ in range(_ITER_BUSQUEDA):
        medio = (bajo + alto) / 2.0
        if libre(medio):
            bajo = medio
        else:
            alto = medio
    return bajo


def _corner_slip(x: float, y: float, paso: float, es_x: bool, radio: float) -> tuple[float, float]:
    """Rodea una esquina en movimiento cardinal bloqueado; devuelve (x, y) nuevos o la original."""
    # Offsets crecientes; el lado con menor offset gana (esquina mas cercana).
    for off in range(1, _MAX_OFFSET_SLIP + 1):
        for signo in (-1.0, 1.0):
            lat = signo * off
            if es_x:
                px, py = x, y + lat
                libre = es_posicion_caminable(px, py, radio) and es_posicion_caminable(px + paso, py, radio)
            else:
                px, py = x + lat, y
                libre = es_posicion_caminable(px, py, radio) and es_posicion_caminable(px, py + paso, radio)
            if not libre:
                continue
            empuje = signo * min(float(off), _MAX_NUDGE)
            if es_x:
                ny = y + _aproximar_eje(x, y, empuje, False, radio)
                nx = x + _aproximar_eje(x, ny, paso, True, radio)
                return nx, ny
            nx = x + _aproximar_eje(x, y, empuje, True, radio)
            ny = y + _aproximar_eje(nx, y, paso, False, radio)
            return nx, ny
    return x, y


def calcular_deslizamiento_tangencial(
    pos_actual: list[float] | tuple[float, float],
    paso_x: float,
    paso_y: float,
    radio: float = 7.5,
) -> tuple[float, float]:
    """Wall sliding real: devuelve la nueva (x, y) tras aplicar los pasos deseados.

    Si un eje esta bloqueado, el 100% de la magnitud de velocidad pasa al eje libre.
    """
    x, y = float(pos_actual[0]), float(pos_actual[1])
    modulo = math.hypot(paso_x, paso_y)
    if paso_x == 0 and paso_y == 0:
        return x, y
    if paso_x == 0 or paso_y == 0:
        mx = _aproximar_eje(x, y, paso_x, True, radio)
        my = _aproximar_eje(x + mx, y, paso_y, False, radio)
        return x + mx, y + my
    # Diagonal: probar ambos ejes con su paso nominal desde la posicion inicial.
    mx = _aproximar_eje(x, y, paso_x, True, radio)
    bloq_x = abs(mx) < abs(paso_x) - _EPS_CONTACTO
    my = _aproximar_eje(x + mx, y, paso_y, False, radio)
    bloq_y = abs(my) < abs(paso_y) - _EPS_CONTACTO
    if bloq_x and not bloq_y:
        # Transferir toda la velocidad al eje Y.
        sy = math.copysign(modulo, paso_y)
        my = _aproximar_eje(x + mx, y, sy, False, radio)
    elif bloq_y and not bloq_x:
        sx = math.copysign(modulo, paso_x)
        mx = _aproximar_eje(x, y + my, sx, True, radio)
    return x + mx, y + my


def resolver_movimiento_campamento(
    pos_actual: list[float] | tuple[float, float],
    dx: float,
    dy: float,
    dt: float,
    velocidad: float = 190.0,
    radio: float = 7.5,
    permitir_corner_slip: bool = True,
) -> tuple[float, float, str, bool]:
    """Movimiento con sub-stepping, wall sliding a velocidad completa y corner slipping.

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
    nueva_x, nueva_y = calcular_deslizamiento_tangencial((x, y), paso_x, paso_y, radio)
    if permitir_corner_slip and (dx == 0) != (dy == 0):
        es_x = dx != 0
        paso = paso_x if es_x else paso_y
        avance = abs(nueva_x - x) if es_x else abs(nueva_y - y)
        if avance < abs(paso) - _EPS_CONTACTO:
            sx, sy = _corner_slip(nueva_x, nueva_y, paso - (nueva_x - x if es_x else nueva_y - y), es_x, radio)
            nueva_x, nueva_y = sx, sy
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
