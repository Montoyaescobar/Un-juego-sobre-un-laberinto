"""
formato.py
Funciones pequeñas para escribir textos del panel (singular/plural y listas largas).
No usa Pygame, así que se prueba sin ventana (pruebas/test_formato.py).
"""


def plural(n, singular, plural_):
    """
    Escribe una cantidad con su palabra en singular o plural.

    Recibe:
        n: la cantidad (entero).
        singular: palabra para n == 1 (ej. "foto").
        plural_: palabra para cualquier otro n (ej. "fotos").
    Devuelve:
        Texto como "1 foto" o "2 fotos". Complejidad O(1).
    """
    return "%d %s" % (n, singular if n == 1 else plural_)


def resumir_lista(valores, maximo=3):
    """
    Muestra los primeros números de una lista y cuántos más hay, para que quepa en el panel.

    Recibe:
        valores: lista de números.
        maximo: cuántos mostrar completos (por defecto 3).
    Devuelve:
        "—" si la lista está vacía; si no, "32, 30, 28 +2" (el +2 son los que no se muestran).
        Complejidad O(maximo).
    """
    if not valores:
        return "—"
    texto = ", ".join(str(v) for v in valores[:maximo])
    resto = len(valores) - maximo
    return texto + (" +%d" % resto if resto > 0 else "")
