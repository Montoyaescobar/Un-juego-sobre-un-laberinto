"""
laberinto.py
El tablero del juego: una cuadrícula de paredes y caminos.

El laberinto se guarda como una matriz de (2*filas+1) x (2*columnas+1):
las posiciones impares (1,1), (1,3), (3,1)... son "celdas" y las pares son
los muros entre ellas. Así, abrir un muro = unir dos celdas.

    ########
    #J     #     J = jugador (entrada en (1,1)), E = enemigo
    ###### #     S = salida (esquina de abajo a la derecha)
    #     S#
    ########
"""

PARED = "#"
LIBRE = " "


class Laberinto:
    """Cuadrícula del laberinto (solo guarda el mapa; no sabe generarse solo)."""

    def __init__(self, filas_celdas, columnas_celdas):
        """
        Crea un laberinto con TODO en pared (el generador abre los caminos).

        Recibe:
            filas_celdas: cantidad de celdas de alto.
            columnas_celdas: cantidad de celdas de ancho.
        Devuelve:
            Nada (constructor).
        """
        self.filas_celdas = filas_celdas
        self.columnas_celdas = columnas_celdas
        self.alto = 2 * filas_celdas + 1
        self.ancho = 2 * columnas_celdas + 1
        self.matriz = [[PARED] * self.ancho for _ in range(self.alto)]
        self.entrada = (1, 1)
        self.salida = (self.alto - 2, self.ancho - 2)

    def dentro(self, fila, columna):
        """
        Dice si una posición está dentro del tablero.

        Recibe:
            fila, columna: coordenadas.
        Devuelve:
            True si está dentro, False si no.
        """
        return 0 <= fila < self.alto and 0 <= columna < self.ancho

    def es_transitable(self, fila, columna):
        """
        Dice si se puede caminar por una posición (dentro del tablero y no es pared).

        Recibe:
            fila, columna: coordenadas.
        Devuelve:
            True si es camino libre, False si es pared o está fuera.
        """
        return self.dentro(fila, columna) and self.matriz[fila][columna] == LIBRE

    def abrir(self, fila, columna):
        """
        Convierte una posición en camino libre (derriba el muro).

        Recibe:
            fila, columna: coordenadas dentro del tablero.
        Devuelve:
            Nada.
        """
        self.matriz[fila][columna] = LIBRE

    def como_texto(self, posicion_jugador=None, enemigos=None, pista=None, eco=None, radar=None):
        """
        Dibuja el laberinto como texto para la consola (cada casilla ocupa 2 caracteres).

        Recibe:
            posicion_jugador: tupla (fila, columna) donde dibujar la J, o None.
            enemigos: posiciones (tuplas) donde dibujar enemigos E, o None.
            pista: casillas (tuplas) del camino sugerido, dibujadas como puntos, o None.
            eco: casilla (tupla) donde dibujar el eco (una e minúscula), o None.
            radar: casilla (tupla) donde dibujar el radar (una R), o None.
        Devuelve:
            Un string con todo el laberinto
            (J = jugador, E = enemigo, e = eco, R = radar, X = choque, S = salida, ## = pared, . = pista).
        """
        casillas_enemigos = set(enemigos) if enemigos else set()
        casillas_pista = set(pista) if pista else set()
        texto = ""
        for f in range(self.alto):
            linea = ""
            for c in range(self.ancho):
                pos = (f, c)
                if pos == posicion_jugador and (pos in casillas_enemigos or pos == eco):
                    linea += "X "
                elif pos == posicion_jugador:
                    linea += "J "
                elif pos in casillas_enemigos:
                    linea += "E "
                elif pos == eco:
                    linea += "e "
                elif pos == radar:
                    linea += "R "
                elif pos == self.salida:
                    linea += "S "
                elif self.matriz[f][c] == PARED:
                    linea += "##"
                elif pos in casillas_pista:
                    linea += ". "
                else:
                    linea += "  "
            texto += linea + "\n"
        return texto
