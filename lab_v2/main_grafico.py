"""
main_grafico.py
Juego del LABERINTO con interfaz gráfica (Pygame).

Ejecutar:   python main_grafico.py
Necesita:   pip install pygame

(La versión de consola sigue funcionando con:  python main_consola.py)
"""

import sys

try:
    import pygame  # noqa: F401
except ImportError:
    print("Falta instalar Pygame. Ábrelo con:")
    print("    pip install pygame")
    sys.exit(1)

from interfaz.app import App

if __name__ == "__main__":
    App().correr()
