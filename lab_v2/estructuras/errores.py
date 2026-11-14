"""
errores.py
Excepciones propias de las estructuras de datos.

Se usan para que el juego pueda atrapar el error (try/except) y NO se cierre
cuando se intenta, por ejemplo, desapilar una pila vacía.
"""


class ErrorEstructura(Exception):
    """Error base de todas las estructuras de datos del proyecto."""


class EstructuraVaciaError(ErrorEstructura):
    """Se intentó sacar, ver o eliminar un elemento en una estructura vacía."""


class PosicionInvalidaError(ErrorEstructura):
    """Se pidió una posición que no existe en la lista (negativa o muy grande)."""
