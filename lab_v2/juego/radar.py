"""
radar.py
El RADAR: un punto rojo que aparece lejos del camino principal y persigue al jugador por el
camino MÁS CORTO (BFS), pero más despacio que él.

Cómo usa la COLA propia (estructuras/cola.py), en pocas frases:
    1. Cada vez que le toca moverse, el radar calcula con BFS (solver.camino_mas_corto, que usa
       una Cola) la ruta desde donde está hasta donde está el jugador.
    2. Esa ruta se guarda en una COLA de casillas pendientes (se encola casilla por casilla).
    3. El radar DESENCOLA la primera casilla y se coloca ahí: da un paso por el camino más corto.
    4. Se mueve una vez cada "cada" turnos del jugador (cada=3 significa un paso por cada 3
       acciones del jugador), o sea que es más lento que el jugador.

Qué pasa si te toca: no pierdes la partida; pierdes PENALIZACION_RADAR movimientos y el punto
vuelve a su casilla de origen y se "duerme" ESPERA_RADAR turnos antes de volver a perseguirte.
El radar castiga quedarse quieto, dar vueltas o deshacer. Como aparece en una casilla lejana,
también puede cruzarse con el jugador de frente; aun así solo cuesta movimientos y los niveles
tienen margen para pagarlos (las pruebas lo comprueban recorriendo el camino más corto).

Lo que usa de Cola: la ruta pendiente (self._ruta) y, dentro de casilla_lejana, un BFS completo.
"""

from estructuras.cola import Cola
from juego.solver import camino_mas_corto

PENALIZACION_RADAR = 5   # movimientos que se pierden cuando el radar toca al jugador
ESPERA_RADAR = 6         # turnos que el radar duerme al empezar y después de cada contacto

_VECINOS = ((-1, 0), (1, 0), (0, -1), (0, 1))


def casilla_lejana(laberinto, origen, evitar=()):
    """
    Busca la casilla transitable más lejana de "origen" (en pasos) que no esté en "evitar".
    Usa un BFS completo con la Cola propia: cada casilla entra y sale una sola vez.

    Recibe:
        laberinto: el Laberinto.
        origen: casilla (fila, columna) desde donde se mide la distancia.
        evitar: conjunto de casillas que no se pueden elegir (por ejemplo, el camino principal).
    Devuelve:
        Una tupla (fila, columna). Si no hay ninguna casilla válida, devuelve "origen".
        Complejidad O(filas * columnas).
    """
    distancia = {origen: 0}
    cola = Cola()
    cola.encolar(origen)
    mejor = origen
    mejor_distancia = -1
    while not cola.esta_vacia():
        casilla = cola.desencolar()
        d = distancia[casilla]
        if casilla not in evitar and d > mejor_distancia:
            mejor = casilla
            mejor_distancia = d
        for df, dc in _VECINOS:
            vecina = (casilla[0] + df, casilla[1] + dc)
            if vecina not in distancia and laberinto.es_transitable(vecina[0], vecina[1]):
                distancia[vecina] = d + 1
                cola.encolar(vecina)
    return mejor


class Radar:
    """Punto rojo que persigue al jugador por el camino más corto, un paso cada N turnos."""

    def __init__(self, laberinto, inicio, cada, espera=ESPERA_RADAR):
        """
        Crea el radar, dormido en su casilla de origen.

        Recibe:
            laberinto: el Laberinto donde se mueve.
            inicio: casilla (fila, columna) donde aparece y a donde vuelve tras un contacto.
            cada: entero mayor o igual a 1; da un paso cada "cada" turnos del jugador.
            espera: entero mayor o igual a 0; turnos que duerme antes de empezar a perseguir.
        Devuelve:
            Nada (constructor).
        Lanza:
            ValueError si "cada" o "espera" no son enteros válidos.
        """
        if not isinstance(cada, int) or isinstance(cada, bool) or cada < 1:
            raise ValueError("El radar debe moverse cada un número entero de turnos >= 1.")
        if not isinstance(espera, int) or isinstance(espera, bool) or espera < 0:
            raise ValueError("La espera del radar debe ser un entero >= 0.")
        self.laberinto = laberinto
        self.inicio = inicio
        self.posicion = inicio
        self.cada = cada
        self.espera = espera
        self.activo = False          # despierta cuando termina la espera
        self.contactos = 0           # cuántas veces ha tocado al jugador
        self._turnos = 0             # turnos del jugador desde que se durmió
        self._ruta = Cola()          # casillas que le faltan para llegar al jugador

    def turno(self, posicion_jugador):
        """
        Avanza un turno del radar. Dormido no hace nada; despierto, se mueve una vez cada
        "cada" turnos: calcula la ruta con BFS, la encola y desencola un paso.

        Recibe:
            posicion_jugador: casilla (fila, columna) del jugador después de su acción.
        Devuelve:
            True si el radar se movió en este turno, False si se quedó quieto.
            Complejidad O(1) si no se mueve, O(filas * columnas) cuando recalcula la ruta.
        """
        self._turnos += 1
        if self._turnos <= self.espera:
            return False
        self.activo = True
        if (self._turnos - self.espera - 1) % self.cada != 0:
            return False
        camino = camino_mas_corto(self.laberinto, self.posicion, posicion_jugador)
        self._ruta.vaciar()
        if camino is None:
            return False
        for casilla in camino[1:]:               # camino[0] es donde ya está el radar
            self._ruta.encolar(casilla)
        if self._ruta.esta_vacia():
            return False
        self.posicion = self._ruta.desencolar()
        return True

    def toca(self, posicion_jugador):
        """
        Dice si el radar está sobre el jugador. Un radar dormido nunca toca.

        Recibe:
            posicion_jugador: casilla (fila, columna) del jugador.
        Devuelve:
            True si están en la misma casilla. Complejidad O(1).
        """
        return self.activo and self.posicion == posicion_jugador

    def reiniciar(self):
        """
        Tras un contacto: cuenta el contacto, vuelve al origen y se duerme otra vez.

        Recibe: nada.
        Devuelve: nada.
        """
        self.contactos += 1
        self.posicion = self.inicio
        self.activo = False
        self._turnos = 0
        self._ruta.vaciar()

    def pasos_pendientes(self):
        """
        Cuántas casillas le faltan por recorrer en la ruta que calculó.

        Recibe: nada.
        Devuelve:
            Un entero (tamaño de la cola). Complejidad O(1).
        """
        return self._ruta.tamanio()
