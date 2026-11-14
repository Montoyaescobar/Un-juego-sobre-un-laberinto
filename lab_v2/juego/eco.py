"""
eco.py
El ECO: un fantasma translúcido que repite, unos pasos más tarde, el recorrido del jugador.

Cómo se usa la COLA propia (estructuras/cola.py), en pocas frases:
    - Cada vez que el jugador se mueve (o deshace), su nueva casilla se ENCOLA al final.
    - Cuando en la cola hay más casillas que el "retraso", el eco DESENCOLA la del frente y
      se coloca ahí. Por ser FIFO (el primero que entra es el primero que sale), el eco camina
      exactamente por donde caminó el jugador, N pasos atrás.
    - Si el jugador ESPERA (no se mueve), no se encola nada, pero el eco igual desencola una
      casilla: se acerca un paso. Si se vacía la cola, el eco ya está sobre el jugador.
    - Si el eco queda en la misma casilla que el jugador, lo atrapa.

Como solo recorre casillas por las que el jugador ya pasó, el eco nunca bloquea el camino
que aún no se ha recorrido.
"""

from estructuras.cola import Cola


class Eco:
    """Fantasma que repite el camino del jugador con un retraso de N pasos."""

    def __init__(self, retraso, inicio):
        """
        Crea el eco, dormido en la entrada, hasta que el jugador se aleje lo suficiente.

        Recibe:
            retraso: entero mayor o igual a 1, cuántos pasos detrás del jugador camina el eco.
            inicio: casilla (fila, columna) donde espera el eco (la entrada del laberinto).
        Devuelve:
            Nada (constructor).
        Lanza:
            ValueError si el retraso no es un entero mayor o igual a 1.
        """
        if not isinstance(retraso, int) or isinstance(retraso, bool) or retraso < 1:
            raise ValueError("El retraso del eco debe ser un entero mayor o igual a 1.")
        self.retraso = retraso
        self.posicion = inicio
        self.anterior = inicio        # casilla donde estaba antes de su último paso
        self.activo = False           # empieza a existir cuando da su primer paso
        self._pasos = Cola()          # casillas del jugador que el eco todavía no repite

    def turno(self, posicion_jugador, esperando=False):
        """
        Avanza un turno del eco.

        Si el jugador se movió, encola su casilla y el eco desencola (da un paso) en cuanto
        haya más casillas pendientes que el retraso. Si el jugador esperó, no se encola nada
        y el eco desencola una casilla pendiente, si la hay (se acerca un paso).

        Recibe:
            posicion_jugador: casilla (fila, columna) del jugador después de su acción.
            esperando: True si el jugador pasó el turno sin moverse.
        Devuelve:
            True si el eco se movió en este turno, False si se quedó quieto.
            Complejidad O(1) (encolar y desencolar son O(1)).
        """
        self.anterior = self.posicion
        if esperando:
            limite = 0
        else:
            self._pasos.encolar(posicion_jugador)
            limite = self.retraso
        if self._pasos.tamanio() > limite:
            self.posicion = self._pasos.desencolar()
            self.activo = True
            return True
        return False

    def atrapa(self, posicion_jugador, posicion_anterior_jugador=None):
        """
        Dice si el eco atrapó al jugador: misma casilla, o cruzarse en un pasillo
        (cada uno ocupa la casilla donde estaba el otro un instante antes).

        Recibe:
            posicion_jugador: casilla actual del jugador.
            posicion_anterior_jugador: casilla donde estaba el jugador antes de su acción,
                o None si no se quiere revisar el cruce.
        Devuelve:
            True si lo atrapa. Un eco dormido nunca atrapa. Complejidad O(1).
        """
        if not self.activo:
            return False
        if self.posicion == posicion_jugador:
            return True
        return (posicion_anterior_jugador is not None
                and self.posicion == posicion_anterior_jugador
                and self.anterior == posicion_jugador)

    def pasos_pendientes(self):
        """
        Cuántas casillas del recorrido del jugador faltan por repetir.

        Recibe: nada.
        Devuelve:
            Un entero (tamaño de la cola). Complejidad O(1).
        """
        return self._pasos.tamanio()
