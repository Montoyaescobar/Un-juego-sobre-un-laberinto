"""
peligros.py
Reglas de salto del rotor y de las cuchillas con cadena, sin depender de Pygame.

La interfaz solo llama a estas funciones y dibuja el resultado. Todas son funciones puras:
reciben números (el tiempo t, la fase de cada peligro y cuánto dura el salto) y devuelven un
resultado, por lo que se pueden probar sin abrir ninguna ventana (pruebas/test_peligros.py).
"""

import math

VELOCIDAD_ROTOR = 2.8     # radianes por segundo a los que gira el rotor
UMBRAL_ROTOR = 0.58       # |sin(ángulo)| mayor que esto = cuchillas verticales = se puede pasar
VELOCIDAD_CADENA = 2.7    # radianes por segundo del péndulo de la cadena
UMBRAL_CADENA = 0.52      # |sin(ángulo)| mayor que esto = péndulo retirado = se puede pasar


def rotor_seguro(t, fase):
    """
    Dice si el rotor deja pasar en este instante (cuchillas casi verticales).

    Recibe:
        t: tiempo de la pantalla en segundos.
        fase: desfase propio del rotor (radianes).
    Devuelve:
        True si se puede cruzar. Complejidad O(1).
    """
    return abs(math.sin(t * VELOCIDAD_ROTOR + fase)) > UMBRAL_ROTOR


def cadena_segura(t, fase):
    """
    Dice si el péndulo de la cadena está retirado hacia un lado.

    Recibe:
        t: tiempo de la pantalla en segundos.
        fase: desfase propio de la cadena (radianes).
    Devuelve:
        True si el péndulo deja pasar. Complejidad O(1).
    """
    return abs(math.sin(t * VELOCIDAD_CADENA + fase)) > UMBRAL_CADENA


def puede_cruzar_rotor(salto_tiempo, t, fase):
    """
    Regla del rotor: hay que estar saltando Y que las cuchillas estén en su ventana verde.

    Recibe:
        salto_tiempo: segundos que le quedan al salto (0 o menos = no está saltando).
        t: tiempo de la pantalla en segundos.
        fase: desfase del rotor.
    Devuelve:
        True si el jugador cruza; False si el rotor lo atrapa. Complejidad O(1).
    """
    return salto_tiempo > 0 and rotor_seguro(t, fase)


def resultado_cuchillas(salto_tiempo, t, fase_cadena):
    """
    Regla de las cuchillas del suelo, con una cadena opcional colgando encima.

    Recibe:
        salto_tiempo: segundos que le quedan al salto.
        t: tiempo de la pantalla en segundos.
        fase_cadena: desfase de la cadena, o None si no hay cadena armada.
    Devuelve:
        "cadena" si el péndulo cruza el pasillo, "cuchillas" si no se saltó, "ok" si pasa.
        La cadena se revisa primero. Complejidad O(1).
    """
    if fase_cadena is not None and not cadena_segura(t, fase_cadena):
        return "cadena"
    if salto_tiempo <= 0:
        return "cuchillas"
    return "ok"
