"""
solver.py
Camino más corto en el laberinto con BFS (búsqueda en anchura) usando la COLA propia.

Cómo funciona (explicación para la sustentación):
    1. Se encola la casilla de origen.
    2. Mientras la cola NO esté vacía: se DESENCOLA una casilla, se miran sus 4 vecinas
       libres que no se hayan visitado y se ENCOLAN, anotando de quién viene cada una
       (diccionario "padres").
    3. Como la cola es FIFO, primero se visitan todas las casillas a 1 paso, luego a 2 pasos,
       etc. Por eso la primera vez que se llega al destino es por el camino MÁS CORTO.
    4. Para armar el camino se sigue la cadena de "padres" desde el destino hasta el origen
       APILANDO cada casilla en una Pila; al desapilar salen en orden origen -> destino.

Complejidad: O(filas * columnas), cada casilla entra y sale de la cola una sola vez.
Se usa en: la pista (botón h), el límite de movimientos y la ubicación de los enemigos.
"""

from estructuras.cola import Cola
from estructuras.pila import Pila

_VECINOS = ((-1, 0), (1, 0), (0, -1), (0, 1))


def camino_mas_corto(laberinto, origen, destino):
    """
    Calcula el camino más corto entre dos casillas con BFS.

    Recibe:
        laberinto: el Laberinto.
        origen: tupla (fila, columna) de inicio.
        destino: tupla (fila, columna) de llegada.
    Devuelve:
        Una lista de tuplas (fila, columna) desde el origen hasta el destino (ambos incluidos),
        o None si alguno de los dos no es transitable o no hay camino.
    """
    if not laberinto.es_transitable(*origen) or not laberinto.es_transitable(*destino):
        return None

    cola = Cola()
    cola.encolar(origen)
    padres = {origen: None}          # casilla -> casilla desde la que se llegó a ella

    while not cola.esta_vacia():
        actual = cola.desencolar()
        if actual == destino:
            break
        for df, dc in _VECINOS:
            vecina = (actual[0] + df, actual[1] + dc)
            if vecina not in padres and laberinto.es_transitable(vecina[0], vecina[1]):
                padres[vecina] = actual
                cola.encolar(vecina)

    if destino not in padres:
        return None

    # Se reconstruye de atrás hacia adelante con una Pila para que salga en el orden correcto
    pila = Pila()
    paso = destino
    while paso is not None:
        pila.apilar(paso)
        paso = padres[paso]
    camino = []
    while not pila.esta_vacia():
        camino.append(pila.desapilar())
    return camino
