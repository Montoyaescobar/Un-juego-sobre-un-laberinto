"""
main_consola.py
Juego del LABERINTO (versión consola) – Proyecto final de Estructuras de Datos.

Ejecutar:   python main_consola.py

Estructuras propias (carpeta estructuras/) y dónde se usan:
    Pila           -> generar el laberinto (backtracking), deshacer movimiento
    Cola           -> BFS: pista y camino más corto
    Lista circular -> ruta de patrulla de los enemigos
    Lista doble    -> repetición de la partida (adelante / atrás)
    Árbol BST      -> mejores puntajes
"""

from juego.partida import (Partida, NIVELES, JUGANDO, GANO, SIN_MOVIMIENTOS, ATRAPADO)
from juego.puntajes import TablaPuntajes

TECLAS = {
    "w": "arriba",
    "s": "abajo",
    "a": "izquierda",
    "d": "derecha",
}


# ---------------------------------------------------------------- entrada segura
def pedir(mensaje, minuscula=True):
    """
    Pide un texto sin que el programa se caiga si se cierra la entrada (Ctrl+C / Ctrl+Z).

    Recibe:
        mensaje: texto que se muestra al pedir el dato.
        minuscula: si es True, el texto se devuelve en minúscula.
    Devuelve:
        El texto escrito sin espacios en los bordes, o None si se cortó la entrada.
    """
    try:
        texto = input(mensaje).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None
    return texto.lower() if minuscula else texto


def pedir_entero(mensaje):
    """
    Pide un número entero.

    Recibe:
        mensaje: texto que se muestra al pedir el dato.
    Devuelve:
        El entero, o None si escribió algo que no es un número (se avisa del error).
    """
    texto = pedir(mensaje)
    if texto is None:
        return None
    try:
        return int(texto)
    except ValueError:
        print(">> Eso no es un número entero.")
        return None


def pedir_nombre():
    """
    Pide el nombre del jugador hasta que sea válido (1 a 15 caracteres, sin ';').

    Recibe: nada.
    Devuelve:
        El nombre. Si se corta la entrada devuelve "Anónimo".
    """
    while True:
        nombre = pedir("Escribe tu nombre (máx. 15 letras): ", minuscula=False)
        if nombre is None:
            return "Anónimo"
        if nombre == "" or len(nombre) > 15 or ";" in nombre:
            print(">> Nombre inválido. Usa de 1 a 15 caracteres y sin ';'.")
        else:
            return nombre


# ---------------------------------------------------------------- pantallas
def mostrar_reglas():
    """Muestra las reglas y controles. Recibe: nada. Devuelve: nada."""
    print("\n=== REGLAS ===")
    print("- Llega desde la entrada (J) hasta la salida (S). No puedes atravesar paredes (##).")
    print("- Tienes un límite de movimientos: si se acaban, pierdes.")
    print("- Los enemigos (E) patrullan y dan un paso cada vez que tú te mueves o deshaces.")
    print("  Si un enemigo y tú quedan en la misma casilla, pierdes (se dibuja X).")
    print("- Deshacer (u) te devuelve un paso, pero cuenta como movimiento.")
    print("- El ECO (e minúscula) repite tu recorrido unos pasos después. Si lo alcanzas, o te")
    print("  alcanza, pierdes. Esperar (e) gasta un movimiento y el eco se acerca un paso.")
    print("- El RADAR (R mayúscula) te persigue por el camino más corto, más despacio que tú.")
    print("  Si te toca, no pierdes: se descuentan 5 movimientos y vuelve a su origen.")
    print("- Pista (h): dibuja con puntos el camino más corto a la salida y cuesta 5 movimientos.")
    print("- Si ganas: puntaje = base del nivel + 10 por cada movimiento que te sobre.")
    print("\nControles:  w = arriba   s = abajo   a = izquierda   d = derecha")
    print("            u = deshacer   e = esperar   h = pista   q = rendirte y volver al menú\n")


def elegir_nivel():
    """
    Pregunta el nivel hasta que el usuario escriba una opción válida.

    Recibe: nada.
    Devuelve:
        El diccionario del nivel elegido, o None si quiere volver al menú.
    """
    while True:
        print("\nElige el nivel:")
        for clave, nivel in NIVELES.items():
            print("  %s) %s (%dx%d, %d enemigo(s))"
                  % (clave, nivel["nombre"], nivel["filas"], nivel["columnas"], nivel["enemigos"]))
        print("  0) Volver")
        opcion = pedir("Opción: ")
        if opcion is None or opcion == "0":
            return None
        if opcion in NIVELES:
            return NIVELES[opcion]
        print(">> Opción inválida, intenta de nuevo.")


def ver_repeticion(partida):
    """
    Repite la partida paso a paso, hacia adelante y hacia atrás (usa la Lista Doble).

    Recibe:
        partida: la Partida que se quiere repasar.
    Devuelve:
        Nada.
    """
    historial = partida.historial
    historial.ir_al_inicio()
    while True:
        posicion_jugador, posiciones_enemigos, movimientos = historial.actual()
        print()
        print(partida.laberinto.como_texto(posicion_jugador, posiciones_enemigos))
        print("Repetición: paso %d de %d | Movimientos gastados: %d"
              % (historial.indice() + 1, historial.total(), movimientos))
        opcion = pedir("n = siguiente, p = anterior, i = inicio, f = final, q = salir: ")
        if opcion is None or opcion == "q":
            return
        if opcion == "n":
            if not historial.adelante():
                print(">> Ya estás en el último paso.")
        elif opcion == "p":
            if not historial.atras():
                print(">> Ya estás en el primer paso.")
        elif opcion == "i":
            historial.ir_al_inicio()
        elif opcion == "f":
            historial.ir_al_final()
        else:
            print(">> Opción inválida. Usa n, p, i, f o q.")


def jugar(tabla):
    """
    Una partida completa: elegir nivel, jugar, mostrar el resultado y guardar el puntaje.

    Recibe:
        tabla: la TablaPuntajes donde se guarda el puntaje si se gana.
    Devuelve:
        La Partida jugada (para poder ver su repetición), o None si no se llegó a jugar.
    """
    nivel = elegir_nivel()
    if nivel is None:
        return None
    partida = Partida(nivel)
    jugador = partida.jugador

    while partida.estado == JUGANDO:
        print()
        print(partida.dibujar())
        print("Nivel %s | Movimientos restantes: %d | Pasos por deshacer: %d"
              % (nivel["nombre"], jugador.movimientos_restantes(), jugador.pasos_por_deshacer()))
        tecla = pedir("Movimiento (w/a/s/d, u = deshacer, e = esperar, h = pista, q = salir): ")

        if tecla in TECLAS:
            if not partida.mover(TECLAS[tecla]):
                print(">> ¡Pared! No puedes pasar por ahí.")
        elif tecla == "u":
            if not partida.deshacer():
                print(">> No hay movimientos para deshacer.")
        elif tecla == "e":
            partida.esperar()
        elif tecla == "h":
            if not partida.pista():
                print(">> No se puede dar la pista (te quedan muy pocos movimientos).")
        elif tecla is None or tecla == "q":
            print("Te rendiste. Volviendo al menú...")
            return partida
        else:
            print(">> Tecla inválida. Usa w, a, s, d, u, h o q.")

    print()
    print(partida.dibujar())
    if partida.estado == GANO:
        puntaje = partida.puntaje()
        print("¡GANASTE! Llegaste a la salida con %d movimientos. Puntaje: %d"
              % (jugador.movimientos, puntaje))
        tabla.registrar(pedir_nombre(), nivel["nombre"], puntaje)
        print("Puntaje guardado.")
    elif partida.estado == ATRAPADO:
        print("PERDISTE: ¡tu eco te alcanzó!" if partida.causa == "eco"
              else "PERDISTE: ¡un enemigo te atrapó!")
    elif partida.estado == SIN_MOVIMIENTOS:
        print("PERDISTE: se acabaron los movimientos.")

    if pedir("¿Quieres ver la repetición de la partida? (s/n): ") == "s":
        ver_repeticion(partida)
    return partida


def mostrar_ranking(tabla):
    """
    Muestra los 10 mejores puntajes (inorden inverso del árbol).

    Recibe:
        tabla: la TablaPuntajes.
    Devuelve:
        Nada.
    """
    mejores = tabla.mejores(10)
    if not mejores:
        print("\nAún no hay puntajes. ¡Sé el primero!")
        return
    print("\n=== MEJORES PUNTAJES ===")
    for lugar, (puntaje, nombre, nivel) in enumerate(mejores, start=1):
        print("%2d. %-15s %-8s %5d" % (lugar, nombre, nivel, puntaje))


def mostrar_recorridos(tabla):
    """
    Muestra los puntajes en inorden, preorden y posorden (para ver cómo es el árbol).

    Recibe:
        tabla: la TablaPuntajes.
    Devuelve:
        Nada.
    """
    if tabla.cantidad() == 0:
        print("\nEl árbol está vacío.")
        return
    for tipo in ("inorden", "preorden", "posorden"):
        puntajes = [str(p) for p, _, _ in tabla.recorrido(tipo)]
        print("%-9s: %s" % (tipo, ", ".join(puntajes)))


def menu_puntajes(tabla):
    """
    Submenú de puntajes: ranking, buscar, eliminar y ver recorridos del árbol.

    Recibe:
        tabla: la TablaPuntajes.
    Devuelve:
        Nada.
    """
    while True:
        print("\n--- PUNTAJES ---")
        print("1) Ver ranking")
        print("2) Buscar un puntaje")
        print("3) Eliminar un puntaje")
        print("4) Ver el árbol (inorden, preorden, posorden)")
        print("0) Volver")
        opcion = pedir("Opción: ")
        if opcion is None or opcion == "0":
            return
        if opcion == "1":
            mostrar_ranking(tabla)
        elif opcion == "2":
            puntaje = pedir_entero("¿Qué puntaje buscas? ")
            if puntaje is not None:
                encontrado = tabla.buscar(puntaje)
                if encontrado is None:
                    print(">> No hay nadie con %d puntos." % puntaje)
                else:
                    print(">> %d puntos: %s (%s)" % (puntaje, encontrado[0], encontrado[1]))
        elif opcion == "3":
            puntaje = pedir_entero("¿Qué puntaje quieres eliminar? ")
            if puntaje is not None:
                if pedir("¿Seguro que quieres eliminar un puntaje de %d? (s/n): " % puntaje) == "s":
                    if tabla.eliminar(puntaje):
                        print(">> Puntaje eliminado.")
                    else:
                        print(">> Ese puntaje no existe.")
        elif opcion == "4":
            mostrar_recorridos(tabla)
        else:
            print(">> Opción inválida, intenta de nuevo.")


def menu_principal():
    """Menú principal en bucle hasta que el usuario elija salir. Recibe/devuelve: nada."""
    tabla = TablaPuntajes()
    ultima_partida = None
    while True:
        print("\n===== LABERINTO =====")
        print("1) Jugar")
        print("2) Mejores puntajes")
        print("3) Ver repetición de la última partida")
        print("4) Reglas")
        print("5) Salir")
        opcion = pedir("Opción: ")
        if opcion == "1":
            partida = jugar(tabla)
            if partida is not None:
                ultima_partida = partida
        elif opcion == "2":
            menu_puntajes(tabla)
        elif opcion == "3":
            if ultima_partida is None:
                print(">> Todavía no has jugado ninguna partida.")
            else:
                ver_repeticion(ultima_partida)
        elif opcion == "4":
            mostrar_reglas()
        elif opcion is None or opcion == "5":
            print("¡Hasta pronto!")
            return
        else:
            print(">> Opción inválida, intenta de nuevo.")


if __name__ == "__main__":
    menu_principal()
