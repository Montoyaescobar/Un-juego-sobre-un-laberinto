"""Genera nav_campamento.png (1100x720, 255=transitable, 0=solido) desde mascara_caminable."""
from __future__ import annotations

from pathlib import Path

import pygame

ANCHO, ALTO = 1100, 720
HOGUERA = (550, 360, 65)          # cx, cy, radio
UMBRAL = (490, 610, 170, 365)     # x0, x1, y0, y1 (pasillo continuo del claro al Umbral)
PUESTOS_NPCS = (
    (315, 310, 18),  # Mara
    (315, 525, 18),  # Nela
    (755, 325, 18),  # Tizón
    (740, 510, 18),  # Ivo
    (550, 560, 22),  # Spawn inicial
)
NOMBRES = ("mascara_caminable.png", "mascara_caminable.jpg", "mascara_caminable.jpeg")
SALIDA = "nav_campamento.png"


def localizar_raiz() -> Path:
    """Busca hacia arriba el primer directorio que contenga la mascara de entrada."""
    inicio = Path(__file__).resolve().parent
    for carpeta in (inicio, *inicio.parents):
        for nombre in NOMBRES:
            if (carpeta / nombre).is_file():
                return carpeta
    raise FileNotFoundError("No se encontro mascara_caminable.(png|jpg) en la jerarquia del proyecto")


def localizar_mascara(raiz: Path) -> Path:
    for nombre in NOMBRES:
        if (raiz / nombre).is_file():
            return raiz / nombre
    raise FileNotFoundError(raiz)


def generar(raiz: Path | None = None) -> Path:
    raiz = raiz or localizar_raiz()
    origen = pygame.image.load(str(localizar_mascara(raiz)))
    if origen.get_size() != (ANCHO, ALTO):
        # Reescalado sin suavizado para no crear colores intermedios.
        origen = pygame.transform.scale(origen, (ANCHO, ALTO))
    out = pygame.Surface((ANCHO, ALTO), depth=24)
    out.fill((0, 0, 0))
    blanco = (255, 255, 255)
    cx, cy, rad = HOGUERA
    x0, x1, y0, y1 = UMBRAL
    for x in range(ANCHO):
        for y in range(ALTO):
            r, g, b = origen.get_at((x, y))[:3]
            if (
                (g > 120 and g > r * 1.2 and g > b * 1.2)
                or (g > 85 and g > r * 1.8 and b < g * 0.75)  # verde oscuro de la rejilla
                or (x - cx) ** 2 + (y - cy) ** 2 <= rad * rad
                or (x0 <= x <= x1 and y0 <= y <= y1)
                or any((x - px) ** 2 + (y - py) ** 2 <= pr * pr for px, py, pr in PUESTOS_NPCS)
            ):
                out.set_at((x, y), blanco)
    destino = raiz / SALIDA
    pygame.image.save(out, str(destino))
    return destino

def main() -> None:
    destino = generar()
    chk = pygame.image.load(str(destino))
    print(f"{destino} {chk.get_size()} centro={chk.get_at((550, 360))[:3]}")


if __name__ == "__main__":
    main()


