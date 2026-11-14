"""
generador.py
Genera un laberinto aleatorio con el algoritmo de BACKTRACKING (DFS) usando la PILA propia.

Cómo funciona (se puede explicar así en la sustentación):
    1. Se abre la celda de entrada y se APILA.
    2. Mientras la pila NO esté vacía:
         - Se mira el TOPE (la celda donde estamos).
         - Si tiene vecinas sin visitar (a 2 casillas): se elige una al azar,
           se derriba el muro entre las dos, se abre la vecina y se APILA.
         - Si no tiene vecinas sin visitar: es un callejón, se DESAPILA (backtracking:
           se devuelve a la celda anterior).
    3. Al vaciarse la pila, todas las celdas quedaron conectadas: el laberinto es
       "perfecto" (hay exactamente un camino entre dos celdas cualesquiera).

Complejidad: O(filas * columnas), cada celda se apila y desapila una vez.
"""

import random

from estructuras.pila import Pila
from juego.laberinto import Laberinto, PARED

MIN_CELDAS = 2
MAX_CELDAS = 30

# Saltos de 2 casillas: arriba, abajo, izquierda, derecha
SALTOS = ((-2, 0), (2, 0), (0, -2), (0, 2))


def _vecinas_sin_visitar(laberinto, fila, columna):
    """
    Busca las celdas vecinas (a 2 casillas) que todavía son pared, o sea, sin visitar.

    Recibe:
        laberinto: el Laberinto que se está generando.
        fila, columna: celda actual.
    Devuelve:
        Una lista pequeña de tuplas (fila, columna) con las vecinas disponibles.
    """
    vecinas = []
    for df, dc in SALTOS:
        nf, nc = fila + df, columna + dc
        if laberinto.dentro(nf, nc) and laberinto.matriz[nf][nc] == PARED \
                and 1 <= nf <= laberinto.alto - 2 and 1 <= nc <= laberinto.ancho - 2:
            vecinas.append((nf, nc))
    return vecinas


def generar_laberinto(filas, columnas, semilla=None):
    """
    Genera un laberinto perfecto aleatorio con backtracking y Pila.

    Recibe:
        filas: celdas de alto (entero entre 2 y 30).
        columnas: celdas de ancho (entero entre 2 y 30).
        semilla: número opcional; con la misma semilla sale el mismo laberinto
                 (sirve para pruebas).
    Devuelve:
        Un Laberinto listo para jugar.
    Lanza:
        ValueError si filas o columnas no son enteros en el rango permitido.
    """
    for medida in (filas, columnas):
        if not isinstance(medida, int) or isinstance(medida, bool) \
                or medida < MIN_CELDAS or medida > MAX_CELDAS:
            raise ValueError("El tamaño debe ser un entero entre %d y %d."
                             % (MIN_CELDAS, MAX_CELDAS))

    azar = random.Random(semilla)
    laberinto = Laberinto(filas, columnas)
    pila = Pila()

    inicio = laberinto.entrada
    laberinto.abrir(*inicio)
    pila.apilar(inicio)

    while not pila.esta_vacia():
        fila, columna = pila.ver_tope()
        vecinas = _vecinas_sin_visitar(laberinto, fila, columna)
        if vecinas:
            nf, nc = azar.choice(vecinas)
            laberinto.abrir((fila + nf) // 2, (columna + nc) // 2)   # derriba el muro del medio
            laberinto.abrir(nf, nc)
            pila.apilar((nf, nc))
        else:
            pila.desapilar()        # backtracking: callejón, vuelve atrás

    return laberinto
