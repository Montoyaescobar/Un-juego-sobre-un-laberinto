"""
pantallas.py
Todas las pantallas del juego: menú, niveles, partida, repetición, ranking y reglas.

Cada pantalla tiene tres métodos:
    evento(e)       -> reacciona al teclado y al mouse
    actualizar(dt)  -> mueve animaciones (dt = segundos desde el cuadro anterior)
    dibujar(surf)   -> pinta en la superficie

QUÉ ES BASE Y QUÉ ES EXTRA
    Base (reglas en juego/, con pruebas): movimiento, paredes, límite de movimientos, deshacer
    (Pila), pista BFS (Cola), patrullas de espectros (Lista circular), historial y repetición
    (Lista doble) y ranking (Árbol BST). Las estructuras viven en estructuras/.
    Reglas de salto del rotor y las cuchillas: juego/peligros.py (la pantalla solo las llama).
    Extras de la interfaz (decoración y jugabilidad opcional que NO usan las 5 estructuras):
    placa-trampa, rueda de hierro, esqueletos y espada, puente, velas, campamento, Tizón y
    armaduras. Están en la clase Juego y en Campamento; su estado es un diccionario simple.
"""

import math
import random

import pygame

from juego.generador import generar_laberinto
from juego.jugador import COSTO_PISTA, DIRECCIONES
from juego.peligros import (rotor_seguro, cadena_segura, puede_cruzar_rotor,
                           resultado_cuchillas)
from juego.partida import (Partida, NIVELES, JUGANDO, GANO, SIN_MOVIMIENTOS, ATRAPADO,
                           PUNTOS_POR_MOVIMIENTO_SOBRANTE)
from juego.solver import camino_mas_corto

from interfaz.efectos import Particulas
from interfaz.formato import plural, resumir_lista
from interfaz.ambiente import AmbienteRefugio
from interfaz.ambiente_laberinto import AmbienteLaberinto
from interfaz.ambiente_pantallas import (fondo_de, acento_de, ZONAS, remaches, separador,
                                         rayos, ceniza, llama)
from interfaz.arte_pixel import EscenaMenuPixel, FondoRefugioPixel, pixelar_region
from interfaz.render import (tablero_estatico, dibujar_portal, dibujar_jugador, dibujar_enemigo,
                             dibujar_pista, dibujar_trampa, dibujar_reliquia, dibujar_puas,
                             dibujar_puente, dibujar_vela, dibujar_trampa_giratoria,
                             dibujar_cadena, dibujar_esqueleto, dibujar_espada_verde, dibujar_rueda,
                             dibujar_eco, dibujar_radar, dibujar_estrella, dibujar_cofre,
                             dibujar_icono_item, dibujar_ranura_item, COLORES_RAREZA, Linterna)
from interfaz.tema import (ANCHO, ALTO, PANEL, BORDE, CIAN, ORO, ROJO, VERDE, MORADO,
                           TEXTO, APAGADO, OSCURIDAD_POR_BRILLO, NOMBRES_BRILLO, NOMBRES_EFECTOS,
                           paleta_de, fuente, texto, texto_ajustado, panel, brillo, mezclar, vineta)
from interfaz.widgets import (Boton, CampoTexto, icono_play, icono_pausa, icono_atras,
                              icono_inicio, icono_final)
try:
    from juego.inventario import (
        Inventario,
        CATALOGO_OBJETOS,
        CATEGORIA_ARMA,
        CATEGORIA_ARMADURA,
        CATEGORIA_HABILIDAD,
    )
except ImportError:
    CATEGORIA_ARMA = "arma"
    CATEGORIA_ARMADURA = "armadura"
    CATEGORIA_HABILIDAD = "habilidad"

    CATALOGO_OBJETOS = {
        "espada_ceniza": {
            "id": "espada_ceniza", "categoria": CATEGORIA_ARMA, "nombre": "Espada de Ceniza",
            "descripcion": "Hoja imbuida con fuego verde. Corta esqueletos frontales.",
            "rareza": "Común", "desbloqueado_inicio": True, "icono": "espada"
        },
        "daga_sombras": {
            "id": "daga_sombras", "categoria": CATEGORIA_ARMA, "nombre": "Daga de Sombras",
            "descripcion": "Ataca en ráfaga circular a enemigos adyacentes a corta distancia.",
            "rareza": "Rara", "desbloqueado_inicio": False, "icono": "daga"
        },
        "baston_centella": {
            "id": "baston_centella", "categoria": CATEGORIA_ARMA, "nombre": "Bastón de Centella",
            "descripcion": "Dispara un destello en línea recta que aturde a un enemigo 3s.",
            "rareza": "Épica", "desbloqueado_inicio": False, "icono": "baston"
        },
        "manto_viajero": {
            "id": "manto_viajero", "categoria": CATEGORIA_ARMADURA, "nombre": "Manto del Viajero",
            "descripcion": "Prenda ligera de tela reforzada. Atuendo inicial.",
            "rareza": "Común", "desbloqueado_inicio": True, "icono": "tunica"
        },
        "coraza_guardian": {
            "id": "coraza_guardian", "categoria": CATEGORIA_ARMADURA, "nombre": "Coraza del Guardián",
            "descripcion": "Armadura de placas rúnicas. Otorga +5 movimientos máximos por nivel.",
            "rareza": "Rara", "desbloqueado_inicio": False, "icono": "coraza"
        },
        "manto_bruma": {
            "id": "manto_bruma", "categoria": CATEGORIA_ARMADURA, "nombre": "Manto de Bruma",
            "descripcion": "Camuflaje espectral. Reduce en 2 casillas el radio de visión de los enemigos.",
            "rareza": "Épica", "desbloqueado_inicio": False, "icono": "manto"
        },
        "paso_ligero": {
            "id": "paso_ligero", "categoria": CATEGORIA_HABILIDAD, "nombre": "Paso Ligero",
            "descripcion": "Desplazamiento ágil en el campamento y mayor fluidez al deslizar muros.",
            "rareza": "Común", "desbloqueado_inicio": True, "icono": "bota"
        },
        "ojo_zahori": {
            "id": "ojo_zahori", "categoria": CATEGORIA_HABILIDAD, "nombre": "Ojo del Zahorí",
            "descripcion": "El resplandor de la linterna revela la dirección del cofre más cercano.",
            "rareza": "Rara", "desbloqueado_inicio": False, "icono": "ojo"
        },
        "escudo_eco": {
            "id": "escudo_eco", "categoria": CATEGORIA_HABILIDAD, "nombre": "Velo contra el Eco",
            "descripcion": "Retrasa la persecución de tu sombra (+2 pasos de gracia de la Cola).",
            "rareza": "Épica", "desbloqueado_inicio": False, "icono": "escudo"
        },
    }

    class Inventario:
        """Fallback de Inventario cuando juego/inventario.py aún no está presente."""

        def __init__(self, datos_guardados=None):
            self.desbloqueados = {
                k for k, v in CATALOGO_OBJETOS.items() if v.get("desbloqueado_inicio", False)
            }
            self.arma_equipada = "espada_ceniza"
            self.armadura_equipada = "manto_viajero"
            self.habilidad_equipada = "paso_ligero"
            self.oro = 0
            self.estrellas_totales = 0
            if isinstance(datos_guardados, dict):
                self.desbloqueados.update(datos_guardados.get("desbloqueados", []))
                self.arma_equipada = datos_guardados.get("arma_equipada", self.arma_equipada)
                self.armadura_equipada = datos_guardados.get("armadura_equipada", self.armadura_equipada)
                self.habilidad_equipada = datos_guardados.get("habilidad_equipada", self.habilidad_equipada)
                self.oro = int(datos_guardados.get("oro", 0))
                self.estrellas_totales = int(datos_guardados.get("estrellas_totales", 0))

        def obtener_coleccion(self):
            coleccion = []
            for id_item, base in CATALOGO_OBJETOS.items():
                desc = id_item in self.desbloqueados
                equipado = id_item in (self.arma_equipada, self.armadura_equipada, self.habilidad_equipada)
                if desc:
                    item = dict(base)
                    item["descubierto"] = True
                    item["equipado"] = equipado
                else:
                    item = {
                        "id": id_item,
                        "categoria": base["categoria"],
                        "nombre": "???",
                        "descripcion": "Artefacto desconocido. Abre cofres en el laberinto para descubrirlo.",
                        "rareza": base["rareza"],
                        "icono": "incognita",
                        "descubierto": False,
                        "equipado": False,
                    }
                coleccion.append(item)
            return coleccion

        def descubrir_item(self, id_item):
            if id_item not in CATALOGO_OBJETOS or id_item in self.desbloqueados:
                return False
            self.desbloqueados.add(id_item)
            return True

        def equipar(self, id_item):
            if id_item not in self.desbloqueados or id_item not in CATALOGO_OBJETOS:
                return False
            cat = CATALOGO_OBJETOS[id_item]["categoria"]
            if cat == CATEGORIA_ARMA:
                self.arma_equipada = id_item
            elif cat == CATEGORIA_ARMADURA:
                self.armadura_equipada = id_item
            elif cat == CATEGORIA_HABILIDAD:
                self.habilidad_equipada = id_item
            return True

        def sortear_botin(self):
            pendientes = [k for k in CATALOGO_OBJETOS if k not in self.desbloqueados]
            return pendientes[0] if pendientes else 60

        def to_dict(self):
            return {
                "desbloqueados": sorted(self.desbloqueados),
                "arma_equipada": self.arma_equipada,
                "armadura_equipada": self.armadura_equipada,
                "habilidad_equipada": self.habilidad_equipada,
                "oro": self.oro,
                "estrellas_totales": self.estrellas_totales,
            }

        @classmethod
        def from_dict(cls, datos):
            return cls(datos)


def _obtener_inventario(app):
    """Obtiene o inicializa la instancia de Inventario asociada a `app`."""
    inv = getattr(app, "inventario", None)
    if inv is None:
        inv = Inventario()
        setattr(app, "inventario", inv)
    return inv
from interfaz import colisiones_campamento
from interfaz.controlador_campamento import ControladorCampamento
try:
    from interfaz.colisiones_campamento import (
        obtener_bloqueos_campamento,
        obtener_limites_campamento,
        es_posicion_valida,
    )
except ImportError:
    from interfaz.controlador_campamento import (
        obtener_bloqueos_campamento,
        obtener_limites_campamento,
        es_posicion_valida,
    )

MOVIMIENTOS = {
    pygame.K_UP: "arriba", pygame.K_w: "arriba",
    pygame.K_DOWN: "abajo", pygame.K_s: "abajo",
    pygame.K_LEFT: "izquierda", pygame.K_a: "izquierda",
    pygame.K_RIGHT: "derecha", pygame.K_d: "derecha",
}
COLOR_NIVEL = {nombre: acento_de(nombre) for nombre in ("Fácil", "Medio", "Difícil")}

# Nombres del equipo para la pantalla de créditos. Escríbelos aquí, por ejemplo:
#     INTEGRANTES = ["Ana", "Luis", "Marta"]
INTEGRANTES = ["Jorge Mario Montoya", "Sebastian Paz Diaz", "Alejandro"]


class Pantalla:
    """Base de todas las pantallas."""

    def __init__(self, app):
        """
        Guarda la referencia a la aplicación.

        Recibe:
            app: la App (da acceso a sonidos, tabla de puntajes, fondo y cambio de pantalla).
        Devuelve:
            Nada (constructor).
        """
        self.app = app
        self.t = 0.0
        self.shake = 0.0          # temblor de pantalla en píxeles (decae solo)

    def evento(self, e):
        """Procesa un evento de pygame. Recibe: e. Devuelve: nada."""

    def actualizar(self, dt):
        """Avanza el tiempo. Recibe: dt. Devuelve: nada."""
        self.t += dt
        self.shake = max(0.0, self.shake - dt * 40)

    def dibujar(self, surf):
        """Pinta la pantalla. Recibe: surf. Devuelve: nada."""

    def _clics(self, e, botones):
        """
        (Interno) Pasa un clic izquierdo a una lista de botones.

        Recibe:
            e: evento de pygame.
            botones: lista de Boton.
        Devuelve:
            True si algún botón lo atendió.
        """
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for b in botones:
                if b.clic(e.pos):
                    self.app.sonidos.reproducir("clic")
                    return True
        return False


# =====================================================================================
#  MENÚ
# =====================================================================================
class Menu(Pantalla):
    """Menú principal en pixel art animado; las opciones cuelgan de un árbol antiguo."""

    CELDA = 32

    def __init__(self, app):
        """Prepara la escena nocturna y las cinco opciones principales."""
        super().__init__(app)
        self.escena = EscenaMenuPixel()
        # Luz de la fogata, niebla, humo y luciérnagas por encima de la escena pixelada.
        self.ambiente = AmbienteRefugio(ANCHO, ALTO, fuego=(368, 606))
        self.sel = 0 if app.punto_guardado is not None else 1
        self.mensaje = ""
        self.opciones = [
            ("CONTINUAR", pygame.Rect(726, 236, 330, 48), self.continuar, (157, 164, 132), True),
            ("NUEVA PARTIDA", pygame.Rect(726, 294, 330, 48), self.nueva_partida, ORO, False),
            ("AJUSTES", pygame.Rect(726, 352, 330, 48), self.ajustes, CIAN, False),
            ("CRÉDITOS", pygame.Rect(726, 410, 330, 48), self.creditos, APAGADO, False),
            ("SALIR", pygame.Rect(726, 468, 330, 48), app.salir, ROJO, False),
        ]
        self.hover = [0.0] * len(self.opciones)     # 0 a 1: cuánto se corre cada tabla al elegirla
        if hasattr(self.app.sonidos, "reproducir_musica"):
            self.app.sonidos.reproducir_musica("menu")

    def _disponible(self, indice):
        """Dice si una opción del menú se puede elegir. Recibe: indice (0 = CONTINUAR). Devuelve: True si hay punto seguro guardado (solo CONTINUAR lo exige)."""
        return indice != 0 or self.app.punto_guardado is not None

    def continuar(self):
        """Opción CONTINUAR: vuelve al último punto seguro del campamento. Recibe/devuelve: nada. Si no hay partida guardada solo muestra un mensaje."""
        if self.app.punto_guardado is None:
            self.mensaje = "Aún no hay una partida. Elige NUEVA PARTIDA."
            return
        self.app.ir_a(Campamento(self.app, self.app.punto_guardado))

    def nueva_partida(self):
        """Opción NUEVA PARTIDA: borra fragmentos y pistas, guarda el punto inicial y entra al campamento. Recibe/devuelve: nada."""
        self.app.antorcha_encendida = True
        self.app.punto_guardado = (550.0, 596.0)
        self.app.fragmentos_mapa = 0
        self.app.pistas_duende = 0
        self.app.guardar_checkpoint(self.app.punto_guardado)
        self.app.ir_a(Campamento(self.app, self.app.punto_guardado))

    def ajustes(self):
        """Opción AJUSTES: abre la pantalla de ajustes. Recibe/devuelve: nada."""
        self.app.ir_a(AjustesMenu(self.app))

    def creditos(self):
        """Opción CREDITS: abre la pantalla de créditos. Recibe/devuelve: nada."""
        self.app.ir_a(Creditos(self.app))

    # -- acciones
    def jugar(self):
        """Entra al refugio antes de iniciar una expedición."""
        self.app.ir_a(Campamento(self.app))

    def ranking(self):
        """Abre los mejores puntajes. Recibe/devuelve: nada."""
        self.app.ir_a(Ranking(self.app))

    def repeticion(self):
        """Abre la repetición de la última partida (si existe). Recibe/devuelve: nada."""
        if self.app.ultima_partida is not None:
            self.app.ir_a(Repeticion(self.app, self.app.ultima_partida, lambda: Menu(self.app)))

    def reglas(self):
        """Abre las reglas. Recibe/devuelve: nada."""
        self.app.ir_a(Reglas(self.app, lambda: Menu(self.app)))

    # -- demo
    def _nueva_demo(self):
        """(Interno) Genera otro laberinto (Pila) y calcula su solución (Cola/BFS)."""
        self.lab = generar_laberinto(8, 8, random.randrange(1000000000))
        self.camino = camino_mas_corto(self.lab, self.lab.entrada, self.lab.salida)
        self.estatico = tablero_estatico(self.lab, self.CELDA, random.randrange(1000))
        self.progreso = 0.0
        self.espera = 0.0
        self.aparece = 0.0

    def _pos_orbe(self):
        """(Interno) Posición en pantalla del orbe de la demo (interpolada entre casillas)."""
        i = min(int(self.progreso), len(self.camino) - 2)
        k = self.progreso - i
        a, b = self.camino[i], self.camino[i + 1]
        f = a[0] + (b[0] - a[0]) * k
        c = a[1] + (b[1] - a[1]) * k
        return (self.demo_origen[0] + (c + 0.5) * self.CELDA,
                self.demo_origen[1] + (f + 0.5) * self.CELDA)

    def evento(self, e):
        """Mouse y teclado seleccionan las tablillas del árbol."""
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i, (_, rect, accion, _, _) in enumerate(self.opciones):
                if rect.collidepoint(e.pos):
                    self.sel = i
                    if self._disponible(i):
                        self.app.sonidos.reproducir("clic")
                        accion()
                    else:
                        self.mensaje = "No hay punto de guardado todavía."
                    return
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 1) % len(self.opciones)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 1) % len(self.opciones)
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self._disponible(self.sel):
                    self.app.sonidos.reproducir("clic")
                    self.opciones[self.sel][2]()
                else:
                    self.mensaje = "No hay punto de guardado todavía."
            elif e.key == pygame.K_ESCAPE:
                self.app.salir()

    def actualizar(self, dt):
        """Actualiza la animación ambiental y la selección del mouse."""
        super().actualizar(dt)
        mouse = pygame.mouse.get_pos()
        for i, (_, rect, _, _, _) in enumerate(self.opciones):
            if rect.collidepoint(mouse):
                self.sel = i
        self.ambiente.actualizar(dt, self.app.efectos > 0)
        for i in range(len(self.hover)):
            objetivo = 1.0 if i == self.sel else 0.0
            self.hover[i] += (objetivo - self.hover[i]) * min(1.0, dt * 12)

    def dibujar(self, surf):
        """Pinta el menú como una escena nocturna pixelada con tablas interactivas."""
        self.escena.dibujar(surf, self.t)
        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        capa.fill((4, 8, 12, 68))
        surf.blit(capa, (0, 0))
        self.ambiente.dibujar_luz(surf)
        self.ambiente.dibujar_niebla(surf)
        self.ambiente.dibujar_humo(surf)
        self.ambiente.dibujar_luciernagas(surf)
        self.ambiente.dibujar_vineta(surf)
        texto(surf, "LABERINTO", 57, (214, 220, 196), (72, 93), negrita=True)
        texto(surf, "EL UMBRAL DE CENIZA", 19, ORO, (78, 159), negrita=True)
        texto(surf, "DONDE TERMINA EL BOSQUE, EMPIEZA EL LABERINTO.", 14,
              (163, 178, 170), (80, 192), sombra=False)
        pygame.draw.rect(surf, (177, 107, 53), (80, 223, 152 + int(10 * math.sin(self.t * 2)), 3))
        pygame.draw.rect(surf, (94, 126, 131), (232, 223, 38, 3))

        for i, (etiqueta, r0, _, color, _) in enumerate(self.opciones):
            activo = i == self.sel
            r = r0.move(-int(8 * self.hover[i]), 0)          # la tabla se corre; las cadenas quedan fijas
            disponible = self._disponible(i)
            tono = color if disponible else (88, 91, 77)
            pygame.draw.line(surf, (28, 25, 20), (r0.x + 22, r0.y - 24), (r0.x + 22, r0.y + 2), 4)
            pygame.draw.line(surf, (28, 25, 20), (r0.right - 22, r0.y - 24),
                             (r0.right - 22, r0.y + 2), 4)
            pygame.draw.rect(surf, (15, 18, 18), r.move(4, 5))
            pygame.draw.rect(surf, (43, 38, 29) if not activo else (61, 46, 28), r)
            pygame.draw.rect(surf, (93, 77, 52) if not activo else tono, r, 2 if not activo else 3)
            pygame.draw.line(surf, (119, 102, 69), (r.x + 7, r.y + 5), (r.right - 8, r.y + 5), 1)
            pygame.draw.rect(surf, (25, 24, 20), (r.x + 8, r.y + 11, 5, r.h - 22))
            pygame.draw.circle(surf, (172, 132, 69), (r.x + 20, r.centery), 3)
            pygame.draw.circle(surf, (172, 132, 69), (r.right - 14, r.centery), 3)
            if activo:
                brillo(surf, r.center, 86, tono, 0.15)
                pygame.draw.rect(surf, tono, (r.x + 8, r.y + 11, 5, r.h - 22))
            texto(surf, etiqueta, 20, tono if disponible else (109, 110, 99), r.center,
                  "center", negrita=True, sombra=False)
            if i == 0 and not disponible:
                texto(surf, "—", 16, (123, 116, 98), (r.right - 28, r.centery), "center",
                      sombra=False)
        for k, ayuda in enumerate(("↑ ↓  ELEGIR", "ENTER  CONFIRMAR", "F11  PANTALLA COMPLETA")):
            texto(surf, ayuda, 13, (176, 184, 170), (1056, 542 + k * 20), "topright",
                  sombra=True)
        if self.mensaje:
            texto_ajustado(surf, self.mensaje, 14, ORO, (1056, 616), 330, "topright", sombra=True)


class AjustesMenu(Pantalla):
    """Ajustes rápidos del sonido, antorcha y accesos a controles y puntajes."""

    def __init__(self, app):
        """Crea las ocho filas de ajustes y la escena de fondo. Recibe: app. Devuelve: nada (constructor)."""
        super().__init__(app)
        self.escena = EscenaMenuPixel()
        self.sel = 0
        self.filas = [pygame.Rect(340, 188 + i * 52, 420, 44) for i in range(8)]
        self.mensaje = ""

    def _activar(self, indice):
        """Ejecuta la fila elegida: sonido, antorcha inicial, controles, puntajes, repetición o volver. Recibe: indice de la fila. Devuelve: nada."""
        if indice == 0:
            encendido = self.app.sonidos.alternar()
            self.mensaje = "Sonido " + ("activado" if encendido else "silenciado")
        elif indice == 1:
            self.app.antorcha_encendida = not self.app.antorcha_encendida
            self.mensaje = "La antorcha iniciará " + ("encendida" if self.app.antorcha_encendida
                                                       else "cubierta")
        elif indice == 2:
            self.app.ir_a(Reglas(self.app, lambda: AjustesMenu(self.app)))
        elif indice == 3:
            self.app.ir_a(Ranking(self.app))
        elif indice == 4 and self.app.ultima_partida is not None:
            self.app.ir_a(Repeticion(self.app, self.app.ultima_partida,
                                      lambda: AjustesMenu(self.app)))
        elif indice == 4:
            self.mensaje = "Todavía no hay una partida para repetir."
        elif indice == 5:
            self.app.brillo = (self.app.brillo + 1) % len(OSCURIDAD_POR_BRILLO)
            self.app.guardar_checkpoint(self.app.punto_guardado or (550.0, 596.0))
            self.mensaje = "Brillo del laberinto: " + NOMBRES_BRILLO[self.app.brillo].lower()
        elif indice == 6:
            self.app.efectos = (self.app.efectos + 1) % len(NOMBRES_EFECTOS)
            self.app.guardar_checkpoint(self.app.punto_guardado or (550.0, 596.0))
            self.mensaje = "Efectos visuales: " + NOMBRES_EFECTOS[self.app.efectos].lower() + \
                (" (para equipos lentos)" if self.app.efectos == 0 else "")
        else:
            self.app.ir_a(Menu(self.app))

    def evento(self, e):
        """Maneja clic, flechas/W/S, Enter y Esc sobre las filas de ajustes. Recibe: e (evento de Pygame). Devuelve: nada."""
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i, r in enumerate(self.filas):
                if r.collidepoint(e.pos):
                    self._activar(i)
                    return
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_UP, pygame.K_w):
                self.sel = (self.sel - 1) % len(self.filas)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                self.sel = (self.sel + 1) % len(self.filas)
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._activar(self.sel)
            elif e.key == pygame.K_ESCAPE:
                self.app.ir_a(Menu(self.app))

    def actualizar(self, dt):
        """Avanza animaciones y resalta la fila bajo el mouse. Recibe: dt (segundos). Devuelve: nada."""
        super().actualizar(dt)
        for i, r in enumerate(self.filas):
            if r.collidepoint(pygame.mouse.get_pos()):
                self.sel = i

    def dibujar(self, surf):
        """Dibuja la escena, el panel y las filas con su estado actual. Recibe: surf (superficie). Devuelve: nada."""
        self.escena.dibujar(surf, self.t)
        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        capa.fill((3, 6, 9, 174))
        surf.blit(capa, (0, 0))
        panel(surf, pygame.Rect(290, 108, 520, 510), 238, (121, 98, 62), 3, (22, 23, 19))
        texto(surf, "AJUSTES DEL REFUGIO", 34, ORO, (ANCHO // 2, 132), "midtop", negrita=True)
        etiquetas = ["SONIDO", "ANTORCHA AL INICIAR", "CONTROLES", "MEJORES PUNTAJES",
                     "REPETICIÓN", "BRILLO DEL LABERINTO", "EFECTOS VISUALES", "VOLVER"]
        for i, (r, etiqueta) in enumerate(zip(self.filas, etiquetas)):
            activo = i == self.sel
            pygame.draw.rect(surf, (40, 35, 27) if not activo else (59, 48, 30), r)
            pygame.draw.rect(surf, ORO if activo else (89, 76, 52), r, 2)
            texto(surf, etiqueta, 17, TEXTO if activo else APAGADO, (r.x + 22, r.centery),
                  "midleft", negrita=activo, sombra=False)
            if i == 0:
                valor = "ACTIVO" if not self.app.sonidos.silenciado else "SILENCIO"
            elif i == 1:
                valor = "ENCENDIDA" if self.app.antorcha_encendida else "CUBIERTA"
            elif i == 4:
                valor = "DISPONIBLE" if self.app.ultima_partida is not None else "—"
            elif i == 5:
                valor = NOMBRES_BRILLO[self.app.brillo]
            elif i == 6:
                valor = NOMBRES_EFECTOS[self.app.efectos]
            else:
                valor = "↵"
            texto(surf, valor, 15, CIAN if activo else ORO, (r.right - 18, r.centery),
                  "midright", negrita=True, sombra=False)
        texto(surf, self.mensaje or "ENTER PARA ELEGIR  ·  ESC PARA VOLVER", 13, APAGADO,
              (ANCHO // 2, 606), "center", sombra=False)


class Creditos(Pantalla):
    """Pantalla breve de créditos con la escena animada del menú."""

    def __init__(self, app):
        """Crea la escena de fondo y el botón Volver. Recibe: app. Devuelve: nada (constructor)."""
        super().__init__(app)
        self.escena = EscenaMenuPixel()
        self.volver = Boton("Volver", (ANCHO // 2 - 110, 590, 220, 48),
                            lambda: app.ir_a(Menu(app)), "Esc", ORO, 21)

    def evento(self, e):
        """Esc, Enter o el botón Volver regresan al menú. Recibe: e (evento de Pygame). Devuelve: nada."""
        if self._clics(e, [self.volver]):
            return
        if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_RETURN):
            self.app.ir_a(Menu(self.app))

    def actualizar(self, dt):
        """Avanza animaciones y el estado del botón. Recibe: dt (segundos). Devuelve: nada."""
        super().actualizar(dt)
        self.volver.actualizar(dt, pygame.mouse.get_pos())

    def dibujar(self, surf):
        """Dibuja la escena oscurecida, el panel y las líneas de créditos. Recibe: surf. Devuelve: nada."""
        self.escena.dibujar(surf, self.t)
        capa = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        capa.fill((3, 6, 9, 180))
        surf.blit(capa, (0, 0))
        panel(surf, pygame.Rect(300, 130, 500, 430), 238, (121, 98, 62), 3, (22, 23, 19))
        texto(surf, "CRÉDITOS", 44, ORO, (ANCHO // 2, 164), "midtop", negrita=True)
        lineas = ["LABERINTO · EL UMBRAL DE CENIZA", "Aventura retro dark fantasy", "",
                  "Desarrollado en Python y Pygame", "Laberintos generados en cada expedición",
                  "Pila · deshacer    /    Cola · búsqueda de rutas",
                  "La luz es tuya. El camino, no."]
        if INTEGRANTES:
            lineas += ["", "Integrantes: " + "  ·  ".join(INTEGRANTES)]
        for i, linea in enumerate(lineas):
            texto(surf, linea, 18 if i else 20, TEXTO if i in (0, 6) else APAGADO,
                  (ANCHO // 2, 240 + i * 37), "center", negrita=i in (0, 6), sombra=False)
        self.volver.dibujar(surf)


# =====================================================================================
#  CAMPAMENTO / ZONA SEGURA
# =====================================================================================
RADIO_INTERACCION = 85      # SEC-08: radio normalizado para NPCs y lápidas
RADIO_OBJETO = 78           # SEC-08: radio normalizado (75-80px) para objetos del campamento
RADIO_ARMADURA = 75         # SEC-08: radio para armaduras decorativas
RADIO_UMBRAL = 135          # SEC-08: radio para el portón del Umbral


class Campamento(Pantalla):
    """Refugio explorable desde el que se accede al Umbral y a las expediciones."""

    VELOCIDAD = 190

    def __init__(self, app, posicion=None):
        """Prepara el refugio: personaje, árboles, bloqueos de colisión, armaduras y duende. Recibe: app y posicion inicial (opcional; si no, el punto guardado). Devuelve: nada (constructor)."""
        super().__init__(app)
        self.personaje = list(posicion or app.punto_guardado or (542.0, 590.0))
        self.teclas = set()
        self.direccion = "abajo"
        self.andando = False
        self.antorcha = app.antorcha_encendida
        self.fondo_pixel = FondoRefugioPixel()
        self.fuego_pos = (542, 368) if getattr(self.fondo_pixel, "usa_imagen", False) else (550, 478)
        self.ambiente = AmbienteRefugio(ANCHO, ALTO, fuego=self.fuego_pos)      # humo, luciérnagas, niebla y luz
        self.app.guardar_checkpoint(self.personaje)
        self.abriendo = False
        self.porton_anim = 0.0
        self.mensaje = "La puerta vuelve a abrirse al anochecer."
        self.mensaje_tiempo = 4.0
        self.particulas = Particulas()
        if getattr(self.fondo_pixel, "usa_imagen", False):
            self.pos_mara = (355, 345)
            self.pos_ivo = (705, 520)
            self.pos_nela = (355, 535)
            self.duende = (720, 345)
            self.umbral_pos = (544, 210)
        else:
            self.pos_mara = (370, 443)
            self.pos_ivo = (735, 526)
            self.pos_nela = (302, 558)
            self.duende = (803, 363)
            self.umbral_pos = (550, 294)
        self.armaduras = [{"x": 420, "y": 320, "estado": "quieta", "tiempo": 0.0,
                           "activada": False},
                          {"x": 665, "y": 320, "estado": "quieta", "tiempo": 0.0,
                           "activada": False}]
        azar = random.Random(17)
        self.arboles = []
        for _ in range(52):
            lado = azar.randrange(4)
            if lado == 0:
                x, y = azar.randrange(-10, 390), azar.randrange(-25, ALTO + 20)
            elif lado == 1:
                x, y = azar.randrange(710, ANCHO + 20), azar.randrange(-25, ALTO + 20)
            elif lado == 2:
                x, y = azar.randrange(-10, ANCHO + 10), azar.randrange(-35, 155)
            else:
                x, y = azar.randrange(-10, ANCHO + 10), azar.randrange(628, ALTO + 20)
            if 420 < x < 680 and y < 230:
                continue
            self.arboles.append((x, y, azar.randrange(22, 42), azar.randrange(0, 3)))
        self.porton = pygame.Rect(444, 86, 212, 194)
        self.limites = obtener_limites_campamento()
        self.bloqueos = obtener_bloqueos_campamento(self.porton)
        self.controlador = ControladorCampamento(
            posicion=self.personaje,
            velocidad=self.VELOCIDAD,
            limites=self.limites,
            bloqueos=self.bloqueos,
            usar_mascara=True,
        )
        self.controlador.posicion = self.personaje
        self._tiempo_paso = 0.0
        self._tiempo_polvo = 0.0
        if hasattr(self.app.sonidos, "reproducir_musica"):
            self.app.sonidos.reproducir_musica("campamento")

    def evento(self, e):
        """Teclas del campamento: Esc/Retroceso vuelven al menú, E/Enter/Espacio interactúan, L alterna la antorcha y las flechas/WASD se anotan para mover. Recibe: e. Devuelve: nada."""
        if e.type in (
            getattr(pygame, "WINDOWFOCUSLOST", -1),
            getattr(pygame, "WINDOWHIDDEN", -1),
            getattr(pygame, "WINDOWMINIMIZED", -1),
        ):
            self.teclas.clear()          # SEC-02: evita teclas pegadas tras Alt+Tab
            if hasattr(self, "controlador"):
                self.controlador.limpiar_teclas()
            return
        if self.abriendo:
            self.teclas.clear()
            if hasattr(self, "controlador"):
                self.controlador.limpiar_teclas()
            return
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.teclas.clear()
                if hasattr(self, "controlador"):
                    self.controlador.limpiar_teclas()
                self.app.guardar_checkpoint(self.personaje)
                self.app.ir_a(Menu(self.app))
                return
            elif e.key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE):
                self._interactuar(e.key)
                if self.abriendo:
                    self.teclas.clear()
                    if hasattr(self, "controlador"):
                        self.controlador.limpiar_teclas()
                return
            elif e.key == pygame.K_l:
                self.antorcha = not self.antorcha
                self.app.antorcha_encendida = self.antorcha
                return
            elif e.key in (pygame.K_i, pygame.K_TAB):
                self.teclas.clear()
                if hasattr(self, "controlador"):
                    self.controlador.limpiar_teclas()
                self.app.sonidos.reproducir("clic")
                self.app.ir_a(PantallaInventario(self.app, lambda: self))
                return
        if e.type == pygame.KEYDOWN and e.key in MOVIMIENTOS:
            self.teclas.add(e.key)
        elif e.type == pygame.KEYUP:
            self.teclas.discard(e.key)
        if hasattr(self, "controlador"):
            self.controlador.evento(e)

    def _candidatos_interaccion(self):
        """Construye la lista de elementos interactivos con posición, radio, distancia y etiqueta HUD."""
        x, y = self.personaje
        definiciones = [
            ("umbral", self.umbral_pos, RADIO_UMBRAL, "E  ·  ABRIR EL UMBRAL"),
            ("mara", self.pos_mara, RADIO_INTERACCION, "E  ·  HABLAR CON MARA"),
            ("ivo", self.pos_ivo, RADIO_INTERACCION, "E  ·  HABLAR CON IVO"),
            ("nela", self.pos_nela, RADIO_INTERACCION, "E  ·  HABLAR CON NELA"),
            ("tizon", self.duende, RADIO_INTERACCION, "E  ·  TRUEQUE CON TIZÓN"),
            ("lapidas", (166, 290), RADIO_INTERACCION, "E  ·  EXAMINAR LÁPIDAS"),
            ("hamaca", (266, 356), RADIO_OBJETO, "E  ·  EXAMINAR HAMACA"),
            ("mapa", (894, 536), RADIO_OBJETO, "E  ·  EXAMINAR MAPA"),
            ("hoguera", self.fuego_pos, RADIO_OBJETO, "E  ·  EXAMINAR HOGUERA"),
            ("carro", (138, 599), RADIO_OBJETO, "E  ·  EXAMINAR CARRO"),
        ]
        for armadura in self.armaduras:
            definiciones.append(
                ("armadura", (armadura["x"], armadura["y"]), RADIO_ARMADURA, "E  ·  EXAMINAR ARMADURA")
            )
        candidatos = []
        for clave, (px, py), radio, hud in definiciones:
            candidatos.append({
                "id": clave,
                "pos": (px, py),
                "radio": radio,
                "distancia": math.hypot(x - px, y - py),
                "hud": hud,
            })
        return candidatos

    def _interactuar(self, tecla=pygame.K_e):
        """Reacciona a E según el objeto más cercano: abre el Umbral, habla con los sobrevivientes, intercambia fragmentos con Tizón o describe el entorno. Recibe/devuelve: nada."""
        candidatos_en_rango = [
            c for c in self._candidatos_interaccion() if c["distancia"] < c["radio"]
        ]
        if not candidatos_en_rango:
            self.mensaje = "Acércate al Umbral, la hamaca o el mapa para interactuar."
            self.mensaje_tiempo = 3.5
            return

        objetivo = min(candidatos_en_rango, key=lambda c: c["distancia"])
        clave = objetivo["id"]
        if clave == "umbral":
            self.app.sonidos.reproducir("clic")
            self.app.guardar_checkpoint(self.personaje)
            self.abriendo = True
            self.mensaje = "El Umbral se está abriendo..."
            self.mensaje_tiempo = 3.5     # SEC-06: mensaje legible
        elif clave == "mara":
            self.mensaje = "Mara: la marca de tiza señala dónde volver si una placa despierta."
            self.mensaje_tiempo = 4.5
            if hasattr(self.app.sonidos, "reproducir_voz"):
                self.app.sonidos.reproducir_voz("mara")
        elif clave == "ivo":
            self.mensaje = "Ivo: cuando la puerta rechina, algo se mueve al otro lado."
            self.mensaje_tiempo = 4.5
            if hasattr(self.app.sonidos, "reproducir_voz"):
                self.app.sonidos.reproducir_voz("ivo")
        elif clave == "nela":
            self.mensaje = "Nela: vuelve con vida. La hoguera no puede esperar para siempre."
            self.mensaje_tiempo = 4.5
            if hasattr(self.app.sonidos, "reproducir_voz"):
                self.app.sonidos.reproducir_voz("nela")
        elif clave == "tizon":
            if hasattr(self.app.sonidos, "reproducir_voz"):
                self.app.sonidos.reproducir_voz("tizon")
            if tecla != pygame.K_e:          # SEC-09: el trueque exige E
                self.mensaje = "Tizón: pulsa E para confirmar el trueque."
                self.mensaje_tiempo = 3.5
            elif self.app.fragmentos_mapa > 0:
                self.app.fragmentos_mapa -= 1
                self.app.pistas_duende += 1
                self.app.guardar_checkpoint(self.personaje)
                self.mensaje = "Tizón cambia un fragmento por una pista gratis para tu próxima incursión."
                self.mensaje_tiempo = 5.0
                self.app.sonidos.reproducir("guardar")
            else:
                self.mensaje = "Tizón: trae un fragmento del laberinto. Te dará una pista gratis."
                self.mensaje_tiempo = 5.0
        elif clave == "lapidas":
            self.mensaje = "Las lápidas son anteriores al campamento. Una tiene tierra fresca."
            self.mensaje_tiempo = 4.5
        elif clave == "hamaca":
            self.mensaje = "La hamaca está vacía. Alguien dejó su capa junto al fuego."
            self.mensaje_tiempo = 4.5
        elif clave == "mapa":
            self.mensaje = "El mapa tiene rutas tachadas y una marca nueva bajo el bosque."
            self.mensaje_tiempo = 4.5
        elif clave == "hoguera":
            self.mensaje = "La hoguera mantiene a raya la niebla, por ahora."
            self.mensaje_tiempo = 4.5
        elif clave == "carro":
            self.mensaje = "El carro llegó cargado de tablones. Nadie recuerda quién lo empujó."
            self.mensaje_tiempo = 4.5
        elif clave == "armadura":
            self.mensaje = "La armadura no tiene a nadie dentro... pero acaba de moverse."
            self.mensaje_tiempo = 4.5

    def actualizar(self, dt):
        """Mueve al personaje con colisiones, anima las armaduras, el mensaje y las chispas, y abre el portón cuando se interactúa. Recibe: dt (segundos). Devuelve: nada."""
        super().actualizar(dt)
        if self.abriendo:
            self.porton_anim = min(1.0, self.porton_anim + dt * 1.7)
            if self.porton_anim >= 1.0:
                self.app.ir_a(Niveles(self.app))
                return
        teclas_activas = self.teclas or (
            self.controlador.teclas if hasattr(self, "controlador") else set()
        )
        dx = dy = 0
        if not self.abriendo:
            dx = (any(k in teclas_activas for k in (pygame.K_RIGHT, pygame.K_d))
                  - any(k in teclas_activas for k in (pygame.K_LEFT, pygame.K_a)))
            dy = (any(k in teclas_activas for k in (pygame.K_DOWN, pygame.K_s))
                  - any(k in teclas_activas for k in (pygame.K_UP, pygame.K_w)))
        x_ant, y_ant = float(self.personaje[0]), float(self.personaje[1])
        radio_hitbox = getattr(ControladorCampamento, "RADIO_HITBOX", 7.5)
        try:
            nx, ny, _, andando_resuelto = colisiones_campamento.resolver_movimiento_campamento(
                self.personaje,
                dx,
                dy,
                dt,
                velocidad=float(self.VELOCIDAD),
                radio=radio_hitbox,
                permitir_corner_slip=True,
            )
        except TypeError:
            nx, ny, _, andando_resuelto = colisiones_campamento.resolver_movimiento_campamento(
                self.personaje,
                dx,
                dy,
                dt,
                velocidad=float(self.VELOCIDAD),
                radio=radio_hitbox,
            )
        coordenadas = (float(nx), float(ny))
        efectivo_x = coordenadas[0] - x_ant
        efectivo_y = coordenadas[1] - y_ant
        self.andando = bool(
            not self.abriendo
            and (dx != 0 or dy != 0)
            and (andando_resuelto or abs(efectivo_x) > 1e-6 or abs(efectivo_y) > 1e-6)
        )
        if dx != 0 or dy != 0:
            self.direccion = ControladorCampamento.calcular_direccion(
                dx, dy, self.direccion, efectivo_x, efectivo_y
            )
        self.personaje[:] = coordenadas
        if hasattr(self, "controlador"):
            self.controlador.posicion = self.personaje
            self.controlador.direccion = self.direccion
            self.controlador.andando = self.andando
        self.app.punto_guardado = coordenadas
        if self.andando:
            if not hasattr(self, "_tiempo_polvo"):
                self._tiempo_polvo = 0.0
            if not hasattr(self, "_tiempo_paso"):
                self._tiempo_paso = 0.0
            self._tiempo_polvo -= dt
            if self._tiempo_polvo <= 0.0:
                self._tiempo_polvo = 0.06
                self.particulas.estela(
                    coordenadas[0] + random.uniform(-4.0, 4.0),
                    coordenadas[1] + 14.0 + random.uniform(-2.0, 2.0),
                    (138, 128, 102),
                    2,
                )
            self._tiempo_paso += dt
            if self._tiempo_paso >= 0.26:
                self._tiempo_paso %= 0.26
                self.app.sonidos.reproducir("paso")
        else:
            self._tiempo_polvo = 0.0
            self._tiempo_paso = 0.0
        for armadura in self.armaduras:
            distancia = math.hypot(self.personaje[0] - armadura["x"],
                                   self.personaje[1] - armadura["y"])
            if distancia > 112 and armadura["estado"] == "caida":
                armadura["estado"] = "levantando"
                armadura["tiempo"] = 0.0
            elif distancia >= 62 and armadura["estado"] == "quieta":     # SEC-03
                armadura["activada"] = False
            elif distancia < 62 and not armadura["activada"] and armadura["estado"] == "quieta":
                armadura["estado"] = "cayendo"
                armadura["tiempo"] = 0.0
                armadura["activada"] = True
                self.shake = max(self.shake, 2.0)
                self.app.sonidos.reproducir("pared")
                self.particulas.emitir(armadura["x"], armadura["y"], (145, 137, 107), 8, 52, 0.55, 2)
            if armadura["estado"] in ("cayendo", "levantando"):
                armadura["tiempo"] += dt
                if armadura["tiempo"] >= 0.35:
                    armadura["estado"] = "caida" if armadura["estado"] == "cayendo" else "quieta"
                    armadura["tiempo"] = 0.0
        if self.mensaje_tiempo > 0:
            self.mensaje_tiempo -= dt
        if random.random() < dt * 5:
            self.particulas.emitir(self.fuego_pos[0] + random.uniform(-20, 20),
                                   self.fuego_pos[1] - 10, ORO, 2, 26, 1.1, 2, -16)
        self.particulas.actualizar(dt)
        self.ambiente.actualizar(dt, self.app.efectos > 0)

    def _dibujar_arbol(self, surf, arbol):
        """Dibuja un pino del bosque. Recibe: surf y arbol (x, y, tamaño, variante). Devuelve: nada."""
        x, y, r, variante = arbol
        pygame.draw.ellipse(surf, (9, 12, 8), (x - r, y + r * 0.42, r * 2, r * 0.62))
        pygame.draw.rect(surf, (27, 25, 18), (x - max(2, r // 8), y + r * 0.24,
                                              max(4, r // 4), r * 0.95))
        base = (14 + variante * 3, 24 + variante * 2, 21)
        niveles = 4
        for i in range(niveles):
            yy = y - r + i * (r * 0.39)
            ancho = int(r * (0.33 + i * 0.22))
            # El viento mece más la punta del pino que la base (los pisos de arriba se mueven más).
            onda = math.sin(self.t * 1.3 + x * 0.05 + i * 0.35) * (niveles - i) * 0.7
            base_onda = onda * 0.6
            pygame.draw.polygon(surf, base, [(x + onda, yy), (x - ancho + base_onda, yy + r * 0.57),
                                             (x + ancho + base_onda, yy + r * 0.57)])
            pygame.draw.polygon(surf, (23, 39, 31), [(x + onda, yy + 3),
                              (x - max(2, ancho - 5) + base_onda, yy + r * 0.52),
                              (x - 2 + base_onda, yy + r * 0.48)])

    def _dibujar_cementerio(self, surf):
        """Dibuja las lápidas y la cerca del cementerio. Recibe: surf. Devuelve: nada."""
        pygame.draw.rect(surf, (22, 27, 24), (45, 258, 260, 65))
        pygame.draw.line(surf, (70, 73, 59), (54, 260), (300, 260), 2)
        for x in range(60, 304, 28):
            pygame.draw.line(surf, (57, 63, 54), (x, 260), (x, 316), 2)
        for x, y, h in ((80, 279, 27), (122, 286, 21), (175, 276, 34),
                        (224, 288, 22), (267, 278, 31)):
            color = (66, 71, 63)
            pygame.draw.rect(surf, color, (x - 10, y, 20, h))
            pygame.draw.rect(surf, color, (x - 5, y - 5, 10, 7))
            pygame.draw.rect(surf, (105, 106, 87), (x - 6, y + 5, 3, max(4, h - 9)))
            pygame.draw.line(surf, (34, 42, 40), (x, y + 9), (x, y + h - 3), 2)
        pygame.draw.rect(surf, (37, 40, 34), (203, 274, 17, 40))
        pygame.draw.rect(surf, (76, 73, 59), (209, 264, 5, 18))
        pygame.draw.rect(surf, (76, 73, 59), (202, 270, 19, 5))

    def _dibujar_carro(self, surf):
        """Dibuja el carro de carga con ruedas y cajas. Recibe: surf. Devuelve: nada."""
        pygame.draw.ellipse(surf, (10, 15, 13), (73, 606, 137, 18))
        pygame.draw.polygon(surf, (62, 47, 31), [(76, 568), (202, 568), (191, 603), (87, 603)])
        pygame.draw.polygon(surf, (99, 71, 42), [(82, 573), (194, 573), (186, 595), (90, 595)])
        for y in (577, 586, 595):
            pygame.draw.line(surf, (47, 38, 29), (84, y), (191, y), 2)
        pygame.draw.line(surf, (72, 51, 34), (185, 593), (231, 614), 5)
        for x in (91, 183):
            pygame.draw.circle(surf, (24, 26, 24), (x, 606), 13)
            pygame.draw.circle(surf, (90, 85, 68), (x, 606), 8, 3)
            pygame.draw.circle(surf, (130, 113, 79), (x, 606), 2)
        pygame.draw.rect(surf, (92, 75, 47), (119, 546, 37, 23))
        pygame.draw.rect(surf, (137, 109, 64), (119, 546, 37, 23), 2)
        pygame.draw.rect(surf, (73, 78, 69), (160, 552, 20, 16))
        pygame.draw.rect(surf, (113, 115, 96), (164, 548, 13, 7))

    def _dibujar_armadura(self, surf, armadura):
        """Dibuja una armadura según su estado (quieta, cayendo, caída, levantando). Recibe: surf y armadura (diccionario de estado). Devuelve: nada."""
        sprite = pygame.Surface((28, 45), pygame.SRCALPHA)
        metal, luz, sombra = (74, 83, 82), (142, 149, 132), (34, 43, 46)
        pygame.draw.rect(sprite, sombra, (9, 3, 11, 9))
        pygame.draw.rect(sprite, metal, (8, 2, 12, 9))
        pygame.draw.rect(sprite, luz, (10, 3, 3, 4))
        pygame.draw.rect(sprite, sombra, (11, 10, 9, 3))
        pygame.draw.rect(sprite, metal, (7, 13, 17, 15))
        pygame.draw.rect(sprite, luz, (9, 14, 4, 10))
        pygame.draw.rect(sprite, sombra, (15, 14, 7, 11))
        pygame.draw.rect(sprite, metal, (3, 14, 6, 9))
        pygame.draw.rect(sprite, luz, (3, 14, 2, 4))
        pygame.draw.rect(sprite, metal, (22, 14, 5, 9))
        pygame.draw.rect(sprite, sombra, (9, 28, 6, 12))
        pygame.draw.rect(sprite, metal, (16, 28, 6, 12))
        pygame.draw.rect(sprite, luz, (8, 38, 8, 4))
        pygame.draw.rect(sprite, luz, (16, 38, 8, 4))
        pygame.draw.line(sprite, (92, 75, 53), (25, 17), (27, 36), 2)
        estado = armadura["estado"]
        progreso = min(1.0, armadura["tiempo"] / 0.35) if estado in ("cayendo", "levantando") else 1.0
        if estado == "cayendo":
            giro = -int(86 * progreso)
        elif estado == "levantando":
            giro = -int(86 * (1 - progreso))
        elif estado == "caida":
            giro = -86
        else:
            giro = 0
        imagen = pygame.transform.rotate(sprite, giro)
        base_y = armadura["y"] + (9 if abs(giro) > 35 else 0)
        surf.blit(imagen, imagen.get_rect(midbottom=(armadura["x"], base_y)))

    def _dibujar_porton(self, surf):
        """Dibuja el portón del Umbral; se abre según porton_anim. Recibe: surf. Devuelve: nada."""
        x, y, w, h = self.porton
        brillo(surf, (x + w // 2, y + h - 6), 190, ORO, 0.12 + 0.04 * math.sin(self.t * 2))
        pygame.draw.rect(surf, (37, 35, 24), (x - 28, y - 20, w + 56, h + 24))
        pygame.draw.rect(surf, (91, 84, 54), (x - 28, y - 20, w + 56, h + 24), 5)
        for i in range(4):
            bx = x - 20 + i * 62
            pygame.draw.rect(surf, (81, 76, 50), (bx, y - 30, 58, 54))
            pygame.draw.line(surf, (133, 119, 74), (bx + 4, y - 28), (bx + 54, y - 28), 2)
        interior = pygame.Rect(x + 25, y + 23, w - 50, h - 23)
        pygame.draw.rect(surf, (8, 10, 7), interior)
        mitad = interior.centerx
        brillo(surf, (mitad, interior.centery), int(40 + self.porton_anim * 105), ORO,
               0.08 + self.porton_anim * 0.28)
        abertura = int(4 + self.porton_anim * (interior.w * 0.72))
        izquierda = pygame.Rect(interior.left, interior.top, (interior.w - abertura) // 2, interior.h)
        derecha = pygame.Rect(mitad + abertura // 2, interior.top,
                              (interior.w - abertura) // 2, interior.h)
        pygame.draw.rect(surf, (57, 51, 34), izquierda)
        pygame.draw.rect(surf, (57, 51, 34), derecha)
        pygame.draw.rect(surf, (117, 91, 50), izquierda, 2)
        pygame.draw.rect(surf, (117, 91, 50), derecha, 2)
        for panel_madera in (izquierda, derecha):
            for fila in range(4):
                yy = panel_madera.y + 14 + fila * 31
                pygame.draw.line(surf, (84, 68, 42), (panel_madera.x + 5, yy),
                                 (panel_madera.right - 5, yy), 4)
        pygame.draw.circle(surf, ORO, (izquierda.right - 7, interior.centery), 3)
        pygame.draw.circle(surf, ORO, (derecha.left + 7, interior.centery), 3)
        pygame.draw.rect(surf, (225, 182, 94), (mitad - abertura // 2, interior.y + 3,
                                                 max(2, abertura), interior.h - 6), 1)
        texto(surf, "EL UMBRAL", 17, ORO, (mitad, y + h + 14), "midtop", negrita=True)

    def _dibujar_hamaca(self, surf):
        """Dibuja la hamaca entre dos postes. Recibe: surf. Devuelve: nada."""
        oscilacion = math.sin(self.t * 1.2) * 3
        pygame.draw.line(surf, (91, 68, 41), (194, 376), (194, 322), 5)
        pygame.draw.line(surf, (91, 68, 41), (336, 377), (336, 322), 5)
        pygame.draw.line(surf, (151, 115, 62), (196, 328), (334, 328), 2)
        pygame.draw.polygon(surf, (91, 66, 42), [(198, 329), (224, 331 + oscilacion),
                         (300, 331 + oscilacion), (332, 329), (310, 350 + oscilacion),
                         (218, 350 + oscilacion)])
        pygame.draw.line(surf, (157, 116, 64), (218, 341 + oscilacion),
                         (311, 341 + oscilacion), 2)

    def _dibujar_hoguera(self, surf):
        """Dibuja la hoguera central con llama animada. Recibe: surf. Devuelve: nada."""
        cx, cy = 550, 478
        brillo(surf, (cx, cy), 150, ORO, 0.30 + 0.06 * math.sin(self.t * 8))
        pygame.draw.ellipse(surf, (12, 14, 9), (cx - 66, cy + 20, 132, 33))
        pygame.draw.ellipse(surf, (69, 56, 34), (cx - 58, cy - 10, 116, 66), 3)
        pygame.draw.line(surf, (79, 42, 24), (cx - 31, cy + 22), (cx + 28, cy - 2), 8)
        pygame.draw.line(surf, (101, 55, 29), (cx - 27, cy - 2), (cx + 32, cy + 22), 8)
        pulso = math.sin(self.t * 9)
        pygame.draw.polygon(surf, (203, 80, 31), [(cx - 24, cy + 11), (cx - 13, cy - 26 - pulso * 4),
                         (cx - 3, cy + 5), (cx + 5, cy - 34 + pulso * 3), (cx + 25, cy + 12)])
        pygame.draw.polygon(surf, (244, 163, 58), [(cx - 12, cy + 12), (cx - 4, cy - 12 - pulso * 2),
                         (cx + 3, cy + 1), (cx + 9, cy - 19 + pulso * 2), (cx + 15, cy + 12)])

    def _dibujar_sobreviviente(self, surf, x, y, nombre, tono):
        """Dibuja a un sobreviviente con su sombra y su etiqueta. Recibe: surf, x, y (posición), nombre (etiqueta) y tono (color de la cinta). Devuelve: nada."""
        pygame.draw.ellipse(surf, (10, 12, 8), (x - 17, y + 10, 34, 12))
        dx, dy = self.personaje[0] - x, self.personaje[1] - y        # mira hacia el viajero
        mira = ("derecha" if dx > 0 else "izquierda") if abs(dx) > abs(dy) \
            else ("abajo" if dy > 0 else "arriba")
        dibujar_jugador(surf, x, y, 34, self.t + x * 0.01, antorcha=False, direccion=mira)
        pygame.draw.rect(surf, tono, (x - 4, y - 13, 8, 3))
        self._etiquetas.append((nombre, x, y + 22, (200, 191, 150)))

    def _dibujar_duende(self, surf):
        """Dibuja a Tizón, el duende, con un pequeño salto animado. Recibe: surf. Devuelve: nada."""
        x, y = self.duende
        salto = int(math.sin(self.t * 4.5) * 2)
        pygame.draw.ellipse(surf, (9, 14, 12), (x - 19, y + 11, 38, 11))
        pygame.draw.polygon(surf, (29, 39, 31), [(x - 15, y - 6 + salto),
                         (x - 8, y - 18 + salto), (x + 10, y - 18 + salto),
                         (x + 17, y + 10), (x - 13, y + 10)])
        pygame.draw.polygon(surf, (82, 105, 63), [(x - 13, y - 12 + salto),
                         (x - 25, y - 22 + salto), (x - 9, y - 19 + salto)])
        pygame.draw.polygon(surf, (82, 105, 63), [(x + 12, y - 12 + salto),
                         (x + 26, y - 23 + salto), (x + 9, y - 18 + salto)])
        pygame.draw.ellipse(surf, (110, 137, 77), (x - 10, y - 23 + salto, 21, 20))
        pygame.draw.rect(surf, (39, 50, 37), (x - 5, y - 20 + salto, 13, 11))
        pygame.draw.rect(surf, (235, 185, 78), (x - 5, y - 16 + salto, 3, 2))
        pygame.draw.rect(surf, (235, 185, 78), (x + 4, y - 16 + salto, 3, 2))
        pygame.draw.polygon(surf, (77, 83, 51), [(x + 10, y - 4 + salto),
                         (x + 23, y + 2 + salto), (x + 21, y + 13), (x + 7, y + 9)])
        pygame.draw.rect(surf, (139, 100, 53), (x - 8, y + 6, 7, 7))
        pygame.draw.rect(surf, (95, 67, 41), (x + 2, y + 6, 8, 7))
        self._etiquetas.append(("TIZÓN · DUENDE", x, y + 25, (190, 198, 140)))

    def _objetivo_cercano(self):
        """Texto HUD del objetivo interactuable más cercano, o None. Recibe: nada. Devuelve: str o None."""
        candidatos_en_rango = [
            c for c in self._candidatos_interaccion() if c["distancia"] < c["radio"]
        ]
        if not candidatos_en_rango:
            return None
        mejor = min(candidatos_en_rango, key=lambda c: c["distancia"])
        return mejor["hud"]

    def dibujar(self, surf):
        """Dibuja todo el campamento (fondo, objetos, personajes, pixelado) y encima el HUD con las indicaciones. Recibe: surf. Devuelve: nada."""
        self._etiquetas = []          # rótulos de personajes: se pintan DESPUÉS del pixelado
        self.fondo_pixel.dibujar(surf, self.t)
        usa_img = getattr(self.fondo_pixel, "usa_imagen", False)
        if not usa_img:
            pygame.draw.ellipse(surf, (26, 34, 18), (50, 138, 1000, 650))
            pygame.draw.ellipse(surf, (69, 62, 39), (68, 150, 965, 616), 2)
            pygame.draw.polygon(surf, (48, 43, 28), [(469, 270), (631, 270), (714, 720), (389, 720)])
            pygame.draw.ellipse(surf, (68, 57, 35), (478, 270, 144, 310), 2)
            for arbol in sorted(self.arboles, key=lambda a: a[1]):
                self._dibujar_arbol(surf, arbol)

            self._dibujar_cementerio(surf)
            self._dibujar_porton(surf)
            # Refugios y objetos cotidianos del campamento.
            pygame.draw.polygon(surf, (68, 45, 31), [(94, 519), (177, 455), (260, 519)])
            pygame.draw.polygon(surf, (104, 76, 48), [(110, 514), (177, 468), (244, 514)])
            pygame.draw.rect(surf, (39, 31, 23), (143, 514, 69, 50))
            pygame.draw.rect(surf, (86, 62, 38), (143, 514, 69, 50), 2)
            pygame.draw.polygon(surf, (65, 57, 37), [(852, 459), (927, 405), (1000, 459)])
            pygame.draw.polygon(surf, (99, 84, 48), [(868, 454), (927, 418), (984, 454)])
            pygame.draw.rect(surf, (33, 31, 23), (896, 454, 63, 53))
            self._dibujar_hamaca(surf)
            self._dibujar_carro(surf)
            # Barriles, suministros y mapa clavado sobre una mesa.
            pygame.draw.rect(surf, (84, 59, 35), (830, 533, 54, 51))
            pygame.draw.rect(surf, (137, 102, 55), (830, 533, 54, 51), 2)
            pygame.draw.line(surf, (45, 36, 25), (832, 548), (882, 548), 3)
            pygame.draw.ellipse(surf, (91, 65, 38), (948, 536, 30, 42))
            pygame.draw.ellipse(surf, (140, 106, 58), (948, 536, 30, 12))
            pygame.draw.line(surf, (98, 75, 47), (850, 606), (975, 606), 8)
            pygame.draw.line(surf, (98, 75, 47), (862, 603), (862, 628), 5)
            pygame.draw.line(surf, (98, 75, 47), (963, 603), (963, 628), 5)
            pygame.draw.rect(surf, (162, 145, 93), (865, 580, 92, 34))
            pygame.draw.line(surf, (82, 78, 50), (877, 590), (936, 590), 1)
            pygame.draw.line(surf, (151, 62, 42), (903, 584), (922, 606), 2)
            self._dibujar_hoguera(surf)
        else:
            if self.porton_anim > 0:
                brillo(surf, (self.umbral_pos[0], 125), int(40 + self.porton_anim * 110), ORO,
                       0.15 + self.porton_anim * 0.35)
                abertura = int(4 + self.porton_anim * 50)
                pygame.draw.rect(surf, (225, 182, 94), (self.umbral_pos[0] - abertura // 2, 60,
                                                         max(2, abertura), 120))
            # Llama viva en la fogata central
            cx, cy = self.fuego_pos
            pulso = math.sin(self.t * 9)
            pygame.draw.polygon(surf, (203, 80, 31), [(cx - 14, cy + 8), (cx - 7, cy - 20 - pulso * 3),
                                                      (cx - 2, cy + 4), (cx + 4, cy - 26 + pulso * 2), (cx + 15, cy + 9)])
            pygame.draw.polygon(surf, (244, 163, 58), [(cx - 8, cy + 8), (cx - 2, cy - 8 - pulso * 2),
                                                      (cx + 2, cy), (cx + 6, cy - 14 + pulso * 2), (cx + 10, cy + 8)])

        self.ambiente.dibujar_luz(surf)
        self.ambiente.dibujar_niebla(surf)
        self.particulas.dibujar(surf)
        self.ambiente.dibujar_chispas(surf)
        self.ambiente.dibujar_humo(surf)
        # Y-Sorting unificado (SEC-14): viajero, NPCs y armaduras ordenados por su Y.
        entidades = [
            {"y": self.pos_mara[1], "dibujar": lambda: self._dibujar_sobreviviente(
                surf, self.pos_mara[0], self.pos_mara[1], "MARA · CARTÓGRAFA", (134, 112, 65))},
            {"y": self.pos_ivo[1], "dibujar": lambda: self._dibujar_sobreviviente(
                surf, self.pos_ivo[0], self.pos_ivo[1], "IVO · VIGÍA", (100, 113, 68))},
            {"y": self.pos_nela[1], "dibujar": lambda: self._dibujar_sobreviviente(
                surf, self.pos_nela[0], self.pos_nela[1], "NELA · CURANDERA", (132, 72, 52))},
            {"y": self.duende[1], "dibujar": lambda: self._dibujar_duende(surf)},
            {"y": self.personaje[1], "dibujar": lambda: dibujar_jugador(
                surf, self.personaje[0], self.personaje[1], 48, self.t,
                self.antorcha, self.direccion, self.andando)},
        ]
        for armadura in self.armaduras:
            entidades.append({"y": armadura["y"],
                              "dibujar": lambda a=armadura: self._dibujar_armadura(surf, a)})
        entidades.sort(key=lambda e: e["y"])
        for entidad in entidades:
            entidad["dibujar"]()
        self.ambiente.dibujar_luciernagas(surf)
        self.ambiente.dibujar_vineta(surf)

        # Píxeles nítidos en el mundo; los paneles y textos del HUD se pintan encima.
        pixelar_region(surf, pygame.Rect(0, 0, ANCHO, ALTO), 2)
        for nombre, ex, ey, color in self._etiquetas:     # letra nítida y legible
            texto(surf, nombre, 13, color, (ex, ey), "midtop", sombra=True)

        panel(surf, pygame.Rect(26, 22, 390, 112), 228)
        texto(surf, "CLARO DE CENIZA", 22, ORO, (45, 39), negrita=True)
        texto(surf, "REFUGIO  ·  SECTOR 00", 13, APAGADO, (47, 74), sombra=False)
        texto(surf, "Antorcha: " + ("encendida" if self.antorcha else "cubierta"), 13, CIAN,
              (47, 92), sombra=False)
        texto(surf, "Fragmentos: %d  ·  Pistas de Tizón: %d" %
              (self.app.fragmentos_mapa, self.app.pistas_duende), 13, ORO,
              (47, 108), sombra=False)

        objetivo = self._objetivo_cercano()          # SEC-11: indicador dinámico
        indicacion = objetivo or "WASD / FLECHAS · MOVER     E · INTERACTUAR     I / TAB · INVENTARIO     L · ANTORCHA"
        panel(surf, pygame.Rect(26, 638, 1048, 56), 228)
        texto(surf, indicacion, 15, ORO if objetivo else TEXTO,
              (ANCHO // 2, 656), "midtop", negrita=bool(objetivo))
        if self.mensaje_tiempo > 0:
            texto(surf, self.mensaje, 13, APAGADO, (ANCHO // 2, 678), "midtop", sombra=False)


# =====================================================================================
#  SELECCIÓN DE NIVEL
# =====================================================================================
class Niveles(Pantalla):
    """Tres tarjetas para elegir la dificultad."""

    def __init__(self, app):
        """Crea las tarjetas y el botón de volver. Recibe: app. Devuelve: nada."""
        super().__init__(app)
        self.claves = list(NIVELES.keys())
        self.tarjetas = [pygame.Rect(70 + i * 335, 170, 310, 400) for i in range(3)]
        self.alzar = [0.0, 0.0, 0.0]
        self.zonas = [fondo_de(NIVELES[c]["nombre"]) for c in self.claves]
        self._cabecera = pygame.Surface((self.tarjetas[0].w - 4, 92), pygame.SRCALPHA)
        self._cabecera.fill((0, 0, 0, 96))       # oscurece el paisaje para que se lea el nombre
        self.volver = Boton("Al campamento", (70, 620, 220, 52),
                            lambda: app.ir_a(Campamento(app)), "Esc", APAGADO, 20)
        if hasattr(self.app.sonidos, "reproducir_musica"):
            self.app.sonidos.reproducir_musica("menu")

    def _elegir(self, i):
        """(Interno) Empieza una partida con el nivel i. Recibe: i. Devuelve: nada."""
        self.app.sonidos.reproducir("clic")
        self.app.ir_a(Juego(self.app, NIVELES[self.claves[i]]))

    def evento(self, e):
        """Clic en tarjeta, teclas 1-3 o Esc. Recibe: e. Devuelve: nada."""
        if self._clics(e, [self.volver]):
            return
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i, r in enumerate(self.tarjetas):
                if r.collidepoint(e.pos):
                    self._elegir(i)
        elif e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_1, pygame.K_KP1):
                self._elegir(0)
            elif e.key in (pygame.K_2, pygame.K_KP2):
                self._elegir(1)
            elif e.key in (pygame.K_3, pygame.K_KP3):
                self._elegir(2)
            elif e.key == pygame.K_ESCAPE:
                self.app.ir_a(Campamento(self.app))

    def actualizar(self, dt):
        """Anima el hover de las tarjetas. Recibe: dt. Devuelve: nada."""
        super().actualizar(dt)
        mouse = pygame.mouse.get_pos()
        self.volver.actualizar(dt, mouse)
        for zona in self.zonas:
            zona.actualizar(dt)
        for i, r in enumerate(self.tarjetas):
            objetivo = 1.0 if r.collidepoint(mouse) else 0.0
            self.alzar[i] += (objetivo - self.alzar[i]) * min(1.0, dt * 12)

    def dibujar(self, surf):
        """Pinta el paisaje de la zona señalada y tres tarjetas, cada una con los colores de su zona. Recibe: surf. Devuelve: nada."""
        self.app.fondo.dibujar(surf, self.t)
        for i, zona in enumerate(self.zonas):          # el paisaje de la zona señalada se disuelve al fondo
            zona.dibujar(surf, self.t, 235 * self.alzar[i])
        texto(surf, "ELIGE UNA ZONA", 48, TEXTO, (ANCHO // 2, 70), "midtop", negrita=True)
        texto(surf, "Los sectores profundos tienen laberintos mayores y más presencias.",
              18, APAGADO, (ANCHO // 2, 132), "midtop", sombra=False)
        for i, base in enumerate(self.tarjetas):
            nivel = NIVELES[self.claves[i]]
            zona = self.zonas[i]
            color = COLOR_NIVEL[nivel["nombre"]]
            r = base.move(0, -int(self.alzar[i] * 12))
            brillo(surf, r.center, 260, color, 0.10 + 0.25 * self.alzar[i])
            panel(surf, r, 232, mezclar(BORDE, color, 0.35 + 0.5 * self.alzar[i]),
                  color=mezclar(PANEL, zona.paleta["oscuridad"], 0.6))
            surf.blit(zona.miniatura((r.w - 4, 92)), (r.x + 2, r.y + 2))
            surf.blit(self._cabecera, (r.x + 2, r.y + 2))
            pygame.draw.line(surf, mezclar(color, (235, 214, 148), 0.28),
                             (r.x + 14, r.y + 93), (r.right - 14, r.y + 93), 1)
            texto(surf, nivel["nombre"], 44, color, (r.centerx, r.y + 44), "center", negrita=True)
            texto(surf, ZONAS.get(nivel["nombre"], ""), 13, TEXTO, (r.centerx, r.y + 74), "center",
                  sombra=False)
            texto(surf, "%d" % (i + 1), 18, TEXTO, (r.right - 22, r.y + 14), "topright", sombra=False)
            lineas = [
                ("Tamaño", "%d × %d celdas" % (nivel["filas"], nivel["columnas"])),
                ("Enemigos", str(nivel["enemigos"])),
                ("Movimientos", "camino óptimo × %s" % str(nivel["factor"]).rstrip("0").rstrip(".")),
                ("Puntaje base", str(nivel["base"])),
            ]
            for k, (a, b) in enumerate(lineas):
                y = r.y + 130 + k * 46
                texto(surf, a, 18, APAGADO, (r.x + 26, y), sombra=False)
                texto(surf, b, 22, TEXTO, (r.x + 26, y + 20), sombra=False, negrita=True)
            for k in range(3):                      # dificultad: una antorcha encendida por nivel
                llama(surf, r.centerx - 28 + k * 28, r.bottom - 26, color, k <= i, self.t)
            remaches(surf, r, mezclar(BORDE, color, 0.4))
        self.volver.dibujar(surf)


# =====================================================================================
#  PARTIDA
# =====================================================================================
class Juego(Pantalla):
    """La partida: tablero animado, panel de información y pantallas de pausa / final."""

    AREA_W, AREA_H = 740, 680

    def __init__(self, app, nivel):
        """
        Crea la partida y todo lo necesario para dibujarla.

        Recibe:
            app: la App.
            nivel: diccionario de NIVELES.
        Devuelve:
            Nada (constructor).
        """
        super().__init__(app)
        self.nivel = nivel
        self.color_nivel = COLOR_NIVEL[nivel["nombre"]]
        self.zona = fondo_de(nivel["nombre"])     # paisaje propio de la zona, detrás del tablero
        self.inventario = _obtener_inventario(app)
        try:
            self.partida = Partida(nivel, inventario=self.inventario)
        except TypeError:
            self.partida = Partida(nivel)
        if hasattr(self.partida, "inventario") and getattr(self.partida, "inventario", None) is not None:
            self.inventario = self.partida.inventario
            app.inventario = self.inventario
        else:
            setattr(self.partida, "inventario", self.inventario)
        app.ultima_partida = self.partida
        lab = self.partida.laberinto
        self.cell = max(10, min(self.AREA_W // lab.ancho, self.AREA_H // lab.alto))
        self.tw, self.th = self.cell * lab.ancho, self.cell * lab.alto
        self.origen = (20 + (self.AREA_W - self.tw) // 2, 20 + (self.AREA_H - self.th) // 2)
        self.paleta = paleta_de(nivel["nombre"])
        self.estatico = tablero_estatico(lab, self.cell, paleta=self.paleta)
        self.vis_j = [float(lab.entrada[0]), float(lab.entrada[1])]
        self.direccion = "abajo"
        self.andando = False
        self.vis_e = [[float(e.posicion[0]), float(e.posicion[1])] for e in self.partida.enemigos]
        self.vis_eco = [float(lab.entrada[0]), float(lab.entrada[1])]
        origen_radar = self.partida.radar.inicio if self.partida.radar is not None else lab.entrada
        self.vis_radar = [float(origen_radar[0]), float(origen_radar[1])]
        self._contactos_radar = 0          # para saltar el punto de vuelta al origen tras un contacto
        self.linterna_on = app.antorcha_encendida
        self.linterna = Linterna((self.tw, self.th), int(self.cell * 4.5), self.paleta["oscuridad"])
        self.linterna_cubierta = Linterna((self.tw, self.th), int(self.cell * 1.55),
                                          self.paleta["oscuridad"])
        self.trampa = self._crear_trampa()
        self.puas = self._crear_puas()
        self.puente = self._crear_puente()
        self.rueda = self._crear_rueda()
        self.cadena = self._crear_cadena()
        self.rotatoria = self._crear_rotatoria()
        self.esqueletos = self._crear_esqueletos()
        self.velas = self._crear_velas()
        self._asegurar_coleccionables_partida()
        self.ambiente = AmbienteLaberinto(
            pygame.Rect(self.origen, (self.tw, self.th)), self.paleta,
            [self._px(*vela["casilla"]) for vela in self.velas], self.cell * 2.4)
        self._etiquetas = []              # carteles que se dibujan al final, nítidos y dentro del tablero
        self.salto_tiempo = 0.0
        self.salto_animacion = 0.0
        self.ataque_animacion = 0.0
        self.alerta = ""
        self.alerta_tiempo = 0.0
        self.particulas = Particulas()
        self.modo = "jugando"            # jugando | pausa | fin_espera | nombre | opciones
        self.espera = 0.0
        self.pop = 0.0
        self.t_fin = 0.0                 # segundos desde que apareció el panel final
        self._cabecera_hud = pygame.Surface((294, 80), pygame.SRCALPHA)
        self._cabecera_hud.fill((0, 0, 0, 100))
        self._cabecera_final = {True: pygame.Surface((596, 100), pygame.SRCALPHA),
                                False: pygame.Surface((596, 100), pygame.SRCALPHA)}
        self._cabecera_final[True].fill((0, 0, 0, 105))
        self._cabecera_final[False].fill((70, 0, 0, 150))
        self.campo = CampoTexto((ANCHO // 2 - 190, 452, 380, 48))
        self.guardado = None             # None = sin decidir, número = puesto, 0 = omitido
        self.peligro = 0.0

        x, w, h = 800, 260, 38
        self.b_pista = Boton("Pista  (−%d mov.)" % COSTO_PISTA, (x, 320, w, h), self.pedir_pista,
                             "H", ORO, 19)
        self.b_deshacer = Boton("Deshacer", (x, 364, w, h), self.deshacer, "U", CIAN, 19)
        self.b_luz = Boton("Antorcha", (x, 408, w, h), self.alternar_luz, "L", MORADO, 19)
        self.b_inventario = Boton("Códice / Inventario", (x, 452, w, h), self.abrir_inventario, "I", ORO, 19)
        self.b_pausa = Boton("Pausa", (x, 496, w, h), self.pausar, "Esc", APAGADO, 19)
        self.botones_hud = [self.b_pista, self.b_deshacer, self.b_luz, self.b_inventario, self.b_pausa]
        self.botones_pausa = []
        self.botones_fin = []
        self._armar_pausa()
        if hasattr(self.app.sonidos, "reproducir_musica"):
            self.app.sonidos.reproducir_musica("laberinto")

    # ------------------------------------------------------------ acciones del jugador
    def _crear_trampa(self):
        """Coloca una placa en un ramal lateral, cerca de la ruta segura principal."""
        lab = self.partida.laberinto
        segura = set(self.partida.solucion)
        vecinas = ((-1, 0), (1, 0), (0, -1), (0, 1))
        candidatas = []
        respaldo = []
        for f in range(lab.alto):
            for c in range(lab.ancho):
                if not lab.es_transitable(f, c) or (f, c) in segura:
                    continue
                camino = camino_mas_corto(lab, lab.entrada, (f, c))
                compartidas = [i for i, casilla in enumerate(camino) if casilla in segura]
                union = compartidas[-1]
                pasos_fuera = len(camino) - 1 - union
                grado = sum(lab.es_transitable(f + df, c + dc) for df, dc in vecinas)
                if pasos_fuera > 0 and grado >= 2:
                    respaldo.append((pasos_fuera, camino, union))
                    if 2 <= pasos_fuera <= 3:
                        candidatas.append((pasos_fuera, camino, union))
        if candidatas:
            _, camino, retorno = random.choice(candidatas)
        elif respaldo:
            _, camino, retorno = min(respaldo, key=lambda dato: dato[0])
        else:
            # Un mapa sin ramales transitables no necesita trampa de retorno.
            return {"placa": None, "retorno": None, "camino": [], "placa_indice": 0,
                    "retorno_indice": 0, "hallazgo": None, "hallazgo_tomado": False,
                    "estado": "desarmada", "restante": 2.0}
        indice_placa = len(camino) - 1
        hojas = []
        for f in range(lab.alto):
            for c in range(lab.ancho):
                if not lab.es_transitable(f, c) or (f, c) in segura:
                    continue
                grado = sum(lab.es_transitable(f + df, c + dc) for df, dc in vecinas)
                if grado != 1:
                    continue
                ruta = camino_mas_corto(lab, lab.entrada, (f, c))
                if len(ruta) > len(camino) and ruta[:len(camino)] == camino:
                    hojas.append(ruta[-1])
        hallazgo = None
        if hojas:
            hallazgo = max(hojas, key=lambda hoja: len(camino_mas_corto(lab, camino[-1], hoja)))
        return {"placa": camino[indice_placa], "retorno": camino[retorno],
                "camino": camino, "placa_indice": indice_placa, "retorno_indice": retorno,
                "hallazgo": hallazgo, "hallazgo_tomado": False,
                "estado": "armada", "restante": 2.0}

    def _crear_puas(self):
        """Sitúa cuchillas en un ramal opcional para enseñar el salto sin bloquear la salida."""
        lab = self.partida.laberinto
        segura = set(self.partida.solucion)
        ocupado = set(self.trampa["camino"])
        vecinas = ((-1, 0), (1, 0), (0, -1), (0, 1))
        candidatas = []
        for f in range(lab.alto):
            for c in range(lab.ancho):
                casilla = (f, c)
                if casilla in segura or casilla in ocupado or not lab.es_transitable(f, c):
                    continue
                camino = camino_mas_corto(lab, lab.entrada, casilla)
                grado = sum(lab.es_transitable(f + df, c + dc) for df, dc in vecinas)
                if camino and len(camino) >= 4 and grado >= 2:
                    candidatas.append(casilla)
        if not candidatas:
            return None
        return {"casilla": random.choice(candidatas), "estado": "armada"}

    def _crear_puente(self):
        """El camino principal cruza una pasarela de tablas y cuerdas."""
        camino = self.partida.solucion
        candidatas = []
        for i in range(1, len(camino) - 1):
            anterior, actual, siguiente = camino[i - 1], camino[i], camino[i + 1]
            if anterior[0] == actual[0] == siguiente[0]:
                candidatas.append((actual, "horizontal"))
            elif anterior[1] == actual[1] == siguiente[1]:
                candidatas.append((actual, "vertical"))
        if not candidatas:
            return None
        casilla, orientacion = random.choice(candidatas)
        return {"casilla": casilla, "orientacion": orientacion}

    def _crear_rueda(self):
        """Prepara un carril opcional largo para anticipar y esquivar la rueda."""
        lab = self.partida.laberinto
        ocupadas = set(self.partida.solucion) | set(self.trampa["camino"])
        if self.puas:
            ocupadas.add(self.puas["casilla"])
        candidatas = []
        for f in range(lab.alto):
            for c in range(lab.ancho):
                for df, dc, orientacion in ((0, 1, "horizontal"), (1, 0, "vertical")):
                    for longitud in range(4, 7):
                        camino = [(f + df * i, c + dc * i) for i in range(longitud)]
                        if any(pos in ocupadas or not lab.es_transitable(*pos) for pos in camino):
                            continue
                        aproximacion = camino_mas_corto(lab, lab.entrada, camino[0])
                        if not aproximacion or len(aproximacion) < 4:
                            continue
                        salidas = []
                        for pos in camino[1:-1]:
                            for vf, vc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                                lateral = (pos[0] + vf, pos[1] + vc)
                                if lateral not in camino and lab.es_transitable(*lateral):
                                    salidas.append(lateral)
                        if salidas:
                            candidatas.append((camino, orientacion, random.choice(salidas)))
        if not candidatas:
            return None
        longitud_maxima = max(len(c[0]) for c in candidatas)
        candidatas_largas = [c for c in candidatas if len(c[0]) == longitud_maxima]
        camino, orientacion, refugio = random.choice(candidatas_largas)
        duracion = 3.0 + (len(camino) - 4) * 0.35
        return {"camino": camino, "orientacion": orientacion, "refugio": refugio,
                "activador": camino[0], "estado": "dormida", "duracion": duracion,
                "restante": duracion}

    def _crear_cadena(self):
        """Cuelga un péndulo sobre la casilla de cuchillas para combinar ambos peligros."""
        if not self.puas:
            return None
        return {"casilla": self.puas["casilla"], "fase": random.uniform(0, math.tau),
                "estado": "armada"}

    def _crear_rotatoria(self):
        """Coloca un rotor en la ruta de salida: hay que saltar cuando abre su giro."""
        camino = self.partida.solucion
        ocupadas = set()
        if self.puente:
            ocupadas.add(self.puente["casilla"])
        if self.puas:
            ocupadas.add(self.puas["casilla"])
        candidatas = [casilla for casilla in camino[2:-2] if casilla not in ocupadas]
        if not candidatas:
            return None
        return {"casilla": random.choice(candidatas), "fase": random.uniform(0, math.tau),
                "estado": "armada"}

    def _crear_esqueletos(self):
        """Esconde esqueletos en ramales opcionales, lejos de la ruta principal y las trampas."""
        lab = self.partida.laberinto
        ocupadas = set(self.partida.solucion) | set(self.trampa["camino"])
        if self.puas:
            ocupadas.add(self.puas["casilla"])
        if self.rueda:
            ocupadas.update(self.rueda["camino"])
            ocupadas.add(self.rueda["refugio"])
        if self.puente:
            ocupadas.add(self.puente["casilla"])
        if self.rotatoria:
            ocupadas.add(self.rotatoria["casilla"])
        if self.trampa["hallazgo"] is not None:
            ocupadas.add(self.trampa["hallazgo"])
        patrullas = []
        for enemigo in self.partida.enemigos:
            enemigo.ruta.recorrer(patrullas.append)
        ocupadas.update(patrullas)
        entrada = lab.entrada
        candidatas = [(f, c) for f in range(lab.alto) for c in range(lab.ancho)
                      if lab.es_transitable(f, c) and (f, c) not in ocupadas
                      and abs(f - entrada[0]) + abs(c - entrada[1]) >= 3]
        random.shuffle(candidatas)
        cantidad = 1 if self.nivel["filas"] < 12 else 2 if self.nivel["filas"] < 16 else 3
        return [{"casilla": casilla, "vivo": True, "fase": random.uniform(0, math.tau)}
                for casilla in candidatas[:cantidad]]

    def _crear_velas(self):
        """Distribuye velas en paredes interiores cercanas a pasillos transitables."""
        lab = self.partida.laberinto
        candidatas = []
        for f in range(1, lab.alto - 1):
            for c in range(1, lab.ancho - 1):
                if lab.es_transitable(f, c):
                    continue
                if any(lab.es_transitable(f + df, c + dc)
                       for df, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))):
                    candidatas.append((f, c))
        random.shuffle(candidatas)
        cantidad = 3 if lab.alto < 12 else 5 if lab.alto < 16 else 7
        return [{"casilla": pos, "fase": random.uniform(0, math.tau)}
                for pos in candidatas[:cantidad]]

    def _asegurar_coleccionables_partida(self):
        """
        Garantiza que la partida exponga `estrellas`, `estrellas_recogidas`, `cofres`,
        `cofres_abiertos`, `recoger_estrella()`, `abrir_cofre()` y `estrellas_conseguidas()`
        incluso si `juego/partida.py` aún no los inicializó.
        """
        p = self.partida
        lab = p.laberinto
        segura = set(p.solucion)
        ocupadas = set(segura) | {lab.entrada, lab.salida}
        ocupadas.update(self.trampa["camino"])
        if self.trampa["hallazgo"] is not None:
            ocupadas.add(self.trampa["hallazgo"])
        if self.puas:
            ocupadas.add(self.puas["casilla"])
        if self.rueda:
            ocupadas.update(self.rueda["camino"])
        for esq in self.esqueletos:
            ocupadas.add(esq["casilla"])

        ramales = [
            (f, c)
            for f in range(lab.alto)
            for c in range(lab.ancho)
            if lab.es_transitable(f, c) and (f, c) not in ocupadas
        ]
        if len(ramales) < 4:
            ramales = [
                (f, c)
                for f in range(lab.alto)
                for c in range(lab.ancho)
                if lab.es_transitable(f, c) and (f, c) not in (lab.entrada, lab.salida)
            ]
        random.shuffle(ramales)

        if not hasattr(p, "estrellas"):
            p.estrellas = list(ramales[:3])
        if not hasattr(p, "estrellas_recogidas"):
            p.estrellas_recogidas = 0
        if not hasattr(p, "cofres"):
            usadas = set(p.estrellas)
            libres = [pos for pos in ramales if pos not in usadas]
            cant_cofres = 1 if self.nivel["filas"] < 12 else 2
            ocultos = [
                k for k in CATALOGO_OBJETOS
                if k not in self.inventario.desbloqueados
            ]
            random.shuffle(ocultos)
            cofres = []
            for idx, pos in enumerate(libres[:cant_cofres]):
                contenido = ocultos[idx] if idx < len(ocultos) else "oro_50"
                cofres.append({"casilla": pos, "abierto": False, "contenido": contenido})
            p.cofres = cofres
        if not hasattr(p, "cofres_abiertos"):
            p.cofres_abiertos = 0

        if not hasattr(p, "recoger_estrella"):
            def _recoger_estrella():
                pos = p.jugador.posicion
                if pos in p.estrellas:
                    p.estrellas.remove(pos)
                    p.estrellas_recogidas += 1
                    return True
                return False
            p.recoger_estrella = _recoger_estrella

        if not hasattr(p, "abrir_cofre"):
            def _abrir_cofre():
                pos = p.jugador.posicion
                for cofre in p.cofres:
                    if cofre.get("casilla") == pos and not cofre.get("abierto", False):
                        cofre["abierto"] = True
                        p.cofres_abiertos = getattr(p, "cofres_abiertos", 0) + 1
                        return cofre
                return None
            p.abrir_cofre = _abrir_cofre

        if not hasattr(p, "estrellas_conseguidas"):
            def _estrellas_conseguidas():
                if p.estado != GANO:
                    return 0
                rec = getattr(p, "estrellas_recogidas", 0)
                cof = getattr(p, "cofres_abiertos", 0)
                if rec >= 3:
                    return 3
                if rec >= 2 or cof >= 1:
                    return 2
                return 1
            p.estrellas_conseguidas = _estrellas_conseguidas

    def _procesar_botin_cofre(self, botin):
        """Extrae y registra en el inventario el ítem o recompensa de un cofre abierto."""
        id_item = None
        nombre_item = None
        if isinstance(botin, str):
            id_item = botin
        elif isinstance(botin, dict):
            if "id" in botin and botin["id"] in CATALOGO_OBJETOS:
                id_item = botin["id"]
                nombre_item = botin.get("nombre")
            elif isinstance(botin.get("item"), dict):
                id_item = botin["item"].get("id")
                nombre_item = botin["item"].get("nombre")
            elif isinstance(botin.get("item"), str):
                id_item = botin["item"]
            elif isinstance(botin.get("contenido"), dict):
                id_item = botin["contenido"].get("id")
                nombre_item = botin["contenido"].get("nombre")
            elif isinstance(botin.get("contenido"), str):
                id_item = botin["contenido"]
            elif "nombre" in botin and botin.get("nombre") != "???":
                nombre_item = botin["nombre"]

        if id_item and id_item in CATALOGO_OBJETOS:
            self.inventario.descubrir_item(id_item)
            nombre_item = nombre_item or CATALOGO_OBJETOS[id_item]["nombre"]
        elif not nombre_item:
            pendientes = [k for k in CATALOGO_OBJETOS if k not in self.inventario.desbloqueados]
            if pendientes:
                elegido = pendientes[0]
                self.inventario.descubrir_item(elegido)
                nombre_item = CATALOGO_OBJETOS[elegido]["nombre"]

        if nombre_item:
            return "¡NUEVO ARTEFACTO: %s!" % nombre_item
        oro_ganado = 50
        if isinstance(botin, int):
            oro_ganado = botin
        elif isinstance(botin, dict) and isinstance(botin.get("oro"), int):
            oro_ganado = botin["oro"]
        self.inventario.oro = getattr(self.inventario, "oro", 0) + oro_ganado
        return "¡COFRE DEL TESORO: +%d de Oro!" % oro_ganado

    def _rotatoria_segura(self):
        """Ventana legible del rotor: cuando las cuchillas están casi verticales."""
        if not self.rotatoria:
            return False
        return rotor_seguro(self.t, self.rotatoria["fase"])

    def _cadena_segura(self):
        """La cadena deja pasar mientras su péndulo está retirado hacia un lado."""
        if not self.cadena:
            return True
        return cadena_segura(self.t, self.cadena["fase"])

    def atacar(self):
        """Corta al esqueleto que está justo delante con la hoja encantada."""
        if self.modo != "jugando":
            return
        self.ataque_animacion = 0.28
        df, dc = DIRECCIONES[self.direccion]
        posicion = self.partida.jugador.posicion
        objetivo = (posicion[0] + df, posicion[1] + dc)
        esqueleto = next((e for e in self.esqueletos
                         if e["vivo"] and e["casilla"] == objetivo), None)
        self.app.sonidos.reproducir("clic" if esqueleto is None else "guardar")
        if esqueleto:
            esqueleto["vivo"] = False
            x, y = self._px(*objetivo)
            self.particulas.emitir(x, y, (94, 227, 104), 16, 120, 0.75, 3)
            self.alerta = "El esqueleto cae en brasas verdes."
        else:
            self.alerta = "La espada de fuego verde corta la niebla."
        self.alerta_tiempo = 1.4

    def _procesar_rueda(self):
        """Despierta la rueda al tocar su carril opcional."""
        if self.rueda and self.rueda["estado"] == "dormida" and \
                self.partida.jugador.posicion == self.rueda["activador"]:
            self.rueda["estado"] = "rodando"
            self.rueda["restante"] = self.rueda["duracion"]
            self.app.sonidos.reproducir("pared")
            self.shake = max(self.shake, 5.0)

    def saltar(self):
        """Prepara un salto breve para pasar sobre las cuchillas."""
        if self.modo == "jugando":
            self.salto_tiempo = 0.62
            self.salto_animacion = 0.38
            self.app.sonidos.reproducir("paso")

    def _procesar_trampa(self):
        """Activa la placa y desármala al volver a la marca dentro del tiempo límite."""
        if self.partida.estado != JUGANDO:
            return
        posicion = self.partida.jugador.posicion
        if self.trampa["estado"] == "armada" and posicion == self.trampa["placa"]:
            self.trampa["estado"] = "activa"
            self.trampa["restante"] = 2.0
            self.app.sonidos.reproducir("pared")
            self.shake = max(self.shake, 5.0)
        elif self.trampa["estado"] == "activa" and posicion == self.trampa["retorno"]:
            self.trampa["estado"] = "desarmada"
            self.app.sonidos.reproducir("deshacer")
        if self.trampa["estado"] == "desarmada" and self.trampa["hallazgo"] == posicion \
                and not self.trampa["hallazgo_tomado"]:
            self.trampa["hallazgo_tomado"] = True
            self.app.fragmentos_mapa += 1
            self.app.guardar_checkpoint(self.app.punto_guardado or (550.0, 596.0))
            x, y = self._px(*posicion)
            self.particulas.emitir(x, y, ORO, 18, 110, 0.9, 3)
            self.app.sonidos.reproducir("guardar")

    def _trampa_bloquea(self, direccion):
        """Durante el cierre solo permite retroceder por el corredor hasta la marca segura."""
        if self.trampa["estado"] != "activa":
            return False
        posicion = self.partida.jugador.posicion
        try:
            indice = self.trampa["camino"].index(posicion)
        except ValueError:
            return True
        if indice <= self.trampa["retorno_indice"]:
            return False
        df, dc = DIRECCIONES[direccion]
        siguiente = (posicion[0] + df, posicion[1] + dc)
        return siguiente != self.trampa["camino"][indice - 1]

    def mover(self, direccion):
        """
        Mueve al jugador (si hay pared, suena y tiembla un poco).

        Recibe:
            direccion: "arriba", "abajo", "izquierda" o "derecha".
        Devuelve:
            Nada.
        """
        if self.modo != "jugando":
            return
        self.direccion = direccion
        if self._trampa_bloquea(direccion):
            self.app.sonidos.reproducir("pared")
            self.shake = max(self.shake, 2.0)
            return
        df, dc = DIRECCIONES[direccion]
        posicion = self.partida.jugador.posicion
        destino = (posicion[0] + df, posicion[1] + dc)
        if any(e["vivo"] and e["casilla"] == destino for e in self.esqueletos):
            self.alerta = "El esqueleto bloquea el paso: míralo y pulsa F o X."
            self.alerta_tiempo = 1.8
            self.app.sonidos.reproducir("pared")
            return
        if self.rotatoria and self.rotatoria["estado"] == "armada" and \
                destino == self.rotatoria["casilla"]:
            if not puede_cruzar_rotor(self.salto_tiempo, self.t, self.rotatoria["fase"]):
                self.rotatoria["estado"] = "fallo"
                self.partida.estado = ATRAPADO
                self.alerta = "El rotor te alcanzó. Salta cuando las cuchillas brillen verde."
                self.alerta_tiempo = 2.0
                self._revisar_fin()
                return
            self.rotatoria["estado"] = "superada"
            self.salto_tiempo = 0.0
        if self.puas and self.puas["estado"] == "armada" and destino == self.puas["casilla"]:
            fase_cadena = (self.cadena["fase"] if self.cadena
                           and self.cadena["estado"] == "armada" else None)
            fallo = resultado_cuchillas(self.salto_tiempo, self.t, fase_cadena)
            if fallo == "cadena":
                self.cadena["estado"] = "fallo"
                self.partida.estado = ATRAPADO
                self.alerta = "La cadena cruza el pasillo. Espera a que se aparte y salta."
                self.alerta_tiempo = 2.0
                self._revisar_fin()
                return
            if fallo == "cuchillas":
                self.puas["estado"] = "fallo"
                self.partida.estado = ATRAPADO
                self.alerta = "Las cuchillas del suelo te alcanzaron. Pulsa Espacio antes de entrar."
                self.alerta_tiempo = 2.0
                self._revisar_fin()
                return
            self.puas["estado"] = "superada"
            if self.cadena:
                self.cadena["estado"] = "superada"
            self.salto_tiempo = 0.0
        estrellas_antes = getattr(self.partida, "estrellas_recogidas", 0)
        cofres_cerrados_antes = [
            c for c in getattr(self.partida, "cofres", [])
            if not c.get("abierto", False)
        ]
        if self.partida.mover(direccion):
            self._procesar_trampa()
            self._procesar_rueda()
            recogio_estrella = (
                self.partida.recoger_estrella()
                if hasattr(self.partida, "recoger_estrella")
                else False
            )
            botin_cofre = None
            if hasattr(self.partida, "abrir_cofre"):
                try:
                    botin_cofre = self.partida.abrir_cofre(self.inventario)
                except TypeError:
                    botin_cofre = self.partida.abrir_cofre()
            if not recogio_estrella and getattr(self.partida, "estrellas_recogidas", 0) > estrellas_antes:
                recogio_estrella = True
            if botin_cofre is None:
                for c_ant in cofres_cerrados_antes:
                    if c_ant.get("abierto", False):
                        botin_cofre = c_ant
                        break
            px_j, py_j = self._px(*self.partida.jugador.posicion)
            self.app.sonidos.reproducir("paso")
            if botin_cofre is not None:
                self.alerta = self._procesar_botin_cofre(botin_cofre)
                self.alerta_tiempo = 2.8
                self.particulas.emitir(px_j, py_j, ORO, 26, 135, 0.95, 3)
                self.app.sonidos.reproducir("guardar")
                self.app.guardar_checkpoint(self.app.punto_guardado or (550.0, 596.0))
            elif recogio_estrella:
                self.alerta = "+150 pts Estrella"
                self.alerta_tiempo = 2.2
                self.particulas.emitir(px_j, py_j, ORO, 22, 120, 0.9, 3)
                self.app.sonidos.reproducir("guardar")
        else:
            self.app.sonidos.reproducir("pared")
            self.shake = max(self.shake, 3.0)
            x, y = self._px(*self.vis_j)
            self.particulas.emitir(x, y, (170, 160, 220), 6, 50, 0.3, 2)
        self._revisar_fin()

    def deshacer(self):
        """Deshace el último movimiento (Pila). Recibe/devuelve: nada."""
        if self.modo != "jugando":
            return
        if self.partida.deshacer():
            self._procesar_trampa()
            self.app.sonidos.reproducir("deshacer")
        else:
            self.app.sonidos.reproducir("pared")
        self._revisar_fin()

    def esperar_turno(self):
        """
        Pasa un turno sin moverse (tecla Q). Cuesta 1 movimiento, los fantasmas avanzan y
        el eco se acerca un paso (cola de casillas pendientes). Recibe/devuelve: nada.
        """
        if self.modo != "jugando":
            return
        if self.partida.esperar():
            self.app.sonidos.reproducir("clic")
        self._revisar_fin()

    def pedir_pista(self):
        """Pide la pista (BFS con Cola). Recibe/devuelve: nada."""
        if self.modo != "jugando":
            return
        if self.app.pistas_duende > 0:
            camino = camino_mas_corto(self.partida.laberinto,
                                      self.partida.jugador.posicion,
                                      self.partida.laberinto.salida)
            if camino:
                self.partida.pista_actual = camino
                self.app.pistas_duende -= 1
                self.app.guardar_checkpoint(self.app.punto_guardado or (550.0, 596.0))
                self.app.sonidos.reproducir("pista")
                return
        if self.partida.pista():
            self.app.sonidos.reproducir("pista")
        else:
            self.app.sonidos.reproducir("pared")

    def alternar_luz(self):
        """Cubre o descubre la antorcha y cambia el radio de visión."""
        if self.modo == "jugando":
            self.linterna_on = not self.linterna_on
            self.app.antorcha_encendida = self.linterna_on

    def pausar(self):
        """Abre el menú de pausa. Recibe/devuelve: nada."""
        rueda_activa = self.rueda and self.rueda["estado"] == "rodando"
        if self.modo == "jugando" and self.trampa["estado"] != "activa" and not rueda_activa:
            self.modo = "pausa"

    def _revisar_fin(self):
        """(Interno) Si la partida terminó, lanza los efectos de victoria o derrota."""
        if self.partida.estado == JUGANDO or self.modo != "jugando":
            return
        self.modo = "fin_espera"
        self.espera = 1.1 if self.partida.estado == GANO else 0.65
        if self.partida.estado == GANO:
            self.app.sonidos.reproducir("ganar")
            if hasattr(self.app.sonidos, "reproducir_musica"):
                self.app.sonidos.reproducir_musica("victoria")
            self.particulas.confeti(ANCHO)
            x, y = self._px(*self.vis_j)
            self.particulas.emitir(x, y, ORO, 50, 220, 1.0, 4)
        else:
            self.app.sonidos.reproducir("perder")
            if hasattr(self.app.sonidos, "reproducir_musica"):
                self.app.sonidos.reproducir_musica("derrota")
            self.shake = max(self.shake, 18.0)

    # ------------------------------------------------------------ pausa y final
    def abrir_inventario(self):
        """Abre la pantalla interactiva de Inventario y Códice Oculto."""
        if self.modo not in ("jugando", "pausa"):
            return
        self.app.sonidos.reproducir("clic")
        self.app.ir_a(PantallaInventario(self.app, lambda: self))

    def _armar_pausa(self):
        """(Interno) Crea los botones del menú de pausa."""
        cx = ANCHO // 2
        self.botones_pausa = [
            Boton("Continuar", (cx - 160, 266, 320, 48), self._continuar, "Esc", CIAN, 22),
            Boton("Inventario y Códice", (cx - 160, 324, 320, 48), self.abrir_inventario, "I", ORO, 22),
            Boton("Reiniciar nivel", (cx - 160, 382, 320, 48), self._reiniciar, "", MORADO, 22),
            Boton("Volver al campamento", (cx - 160, 440, 320, 48),
                  lambda: self.app.ir_a(Campamento(self.app)),
                  "", ROJO, 22),
        ]

    def _continuar(self):
        """(Interno) Cierra la pausa."""
        self.modo = "jugando"

    def _reiniciar(self):
        """(Interno) Empieza otra partida del mismo nivel."""
        self.app.ir_a(Juego(self.app, self.nivel))

    def _armar_botones_fin(self):
        """(Interno) Crea los botones del panel final según la fase (nombre u opciones)."""
        cx = ANCHO // 2
        ver_rep = lambda: self.app.ir_a(Repeticion(self.app, self.partida,
                                                   lambda: Campamento(self.app)))
        menu = lambda: self.app.ir_a(Campamento(self.app))
        if self.modo == "nombre":
            self.botones_fin = [
                Boton("Guardar puntaje", (cx - 250, 540, 240, 50), self._guardar, "Enter", VERDE, 22),
                Boton("Omitir", (cx + 10, 540, 240, 50), self._omitir, "Esc", APAGADO, 22),
            ]
        elif self.partida.estado == GANO:
            self.botones_fin = [
                Boton("Ver ranking", (cx - 250, 520, 240, 48), lambda: self.app.ir_a(Ranking(self.app)),
                      "", ORO, 21),
                Boton("Ver repetición", (cx + 10, 520, 240, 48), ver_rep, "R", MORADO, 21),
                Boton("Jugar otra vez", (cx - 250, 576, 240, 48), self._reiniciar, "Enter", CIAN, 21),
                Boton("Campamento", (cx + 10, 576, 240, 48), menu, "Esc", APAGADO, 21),
            ]
        else:
            self.botones_fin = [
                Boton("Reintentar", (cx - 270, 458, 170, 50), self._reiniciar, "Enter", CIAN, 21),
                Boton("Repetición", (cx - 85, 458, 170, 50), ver_rep, "R", MORADO, 21),
                Boton("Campamento", (cx + 100, 458, 170, 50), menu, "Esc", APAGADO, 18),
            ]

    def _guardar(self):
        """(Interno) Guarda el puntaje en el árbol BST y calcula el puesto en el ranking."""
        if not self.campo.valido():
            self.campo.error = "Escribe de 1 a 15 caracteres."
            self.app.sonidos.reproducir("pared")
            return
        nombre = self.campo.texto.strip()
        puntaje = self.partida.puntaje()
        try:
            self.app.tabla.registrar(nombre, self.nivel["nombre"], puntaje)
        except ValueError:
            self.campo.error = "Ese nombre no sirve."
            return
        self.guardado = 0
        for i, fila in enumerate(self.app.tabla.mejores(100000)):
            if fila == (puntaje, nombre, self.nivel["nombre"]):
                self.guardado = i + 1
                break
        self.app.sonidos.reproducir("guardar")
        self.modo = "opciones"
        self.pop = 0.0
        self._armar_botones_fin()

    def _omitir(self):
        """(Interno) Sigue sin guardar el puntaje."""
        self.guardado = 0
        self.modo = "opciones"
        self.pop = 0.0
        self._armar_botones_fin()

    # ------------------------------------------------------------ eventos
    def evento(self, e):
        """Teclado y mouse según el estado de la partida. Recibe: e. Devuelve: nada."""
        if self.modo == "jugando":
            if self._clics(e, self.botones_hud):
                return
            if e.type == pygame.KEYDOWN:
                if e.key in MOVIMIENTOS:
                    self.mover(MOVIMIENTOS[e.key])
                elif e.key in (pygame.K_u, pygame.K_z, pygame.K_BACKSPACE):
                    self.deshacer()
                elif e.key == pygame.K_h:
                    self.pedir_pista()
                elif e.key == pygame.K_q:
                    self.esperar_turno()
                elif e.key == pygame.K_l:
                    self.alternar_luz()
                elif e.key == pygame.K_SPACE:
                    self.saltar()
                elif e.key in (pygame.K_f, pygame.K_x):
                    self.atacar()
                elif e.key in (pygame.K_i, pygame.K_TAB):
                    self.app.sonidos.reproducir("clic")
                    self.app.ir_a(PantallaInventario(self.app, lambda: self))
                elif e.key in (pygame.K_ESCAPE, pygame.K_p):
                    self.pausar()
        elif self.modo == "pausa":
            if self._clics(e, self.botones_pausa):
                return
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_p):
                self._continuar()
        elif self.modo == "nombre":
            if self._clics(e, self.botones_fin):
                return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self._omitir()
            elif self.campo.evento(e) == "enter":
                self._guardar()
        elif self.modo == "opciones":
            if self._clics(e, self.botones_fin):
                return
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._reiniciar()
                elif e.key == pygame.K_r:
                    self.botones_fin[1].accion()
                elif e.key == pygame.K_ESCAPE:
                    self.app.ir_a(Campamento(self.app))

    # ------------------------------------------------------------ animación
    def _px(self, fila, col):
        """(Interno) Centro en pantalla de una casilla (acepta posiciones decimales)."""
        return (self.origen[0] + (col + 0.5) * self.cell, self.origen[1] + (fila + 0.5) * self.cell)

    def _acercar(self, vis, objetivo, dt, velocidad=16.0):
        """(Interno) Desliza una posición visual hacia su casilla real. Devuelve lo que se movió."""
        k = min(1.0, dt * velocidad)
        dx, dy = objetivo[0] - vis[0], objetivo[1] - vis[1]
        vis[0] += dx * k
        vis[1] += dy * k
        return math.hypot(dx, dy)

    def actualizar(self, dt):
        """Anima personajes, partículas, botones y temporizadores. Recibe: dt. Devuelve: nada."""
        super().actualizar(dt)
        mouse = pygame.mouse.get_pos()
        for b in self.botones_hud + self.botones_pausa + self.botones_fin:
            b.actualizar(dt, mouse)
        self.salto_tiempo = max(0.0, self.salto_tiempo - dt)
        self.salto_animacion = max(0.0, self.salto_animacion - dt)
        self.ataque_animacion = max(0.0, self.ataque_animacion - dt)
        self.alerta_tiempo = max(0.0, self.alerta_tiempo - dt)
        self.ambiente.actualizar(dt, self.app.efectos > 0)
        self.zona.actualizar(dt)

        if self.modo == "jugando" and self.partida.estado == JUGANDO:
            if hasattr(self.partida, "actualizar_tiempo"):
                self.partida.actualizar_tiempo(dt)
            if self.partida.estado == ATRAPADO:
                self.alerta = "¡Un enemigo te ha alcanzado en las sombras!"
                self.alerta_tiempo = 2.0
                self.shake = max(self.shake, 7.0)
                self.app.sonidos.reproducir("pared")
                self._revisar_fin()

        self.b_deshacer.habilitado = self.partida.jugador.pasos_por_deshacer() > 0 \
            and self.modo == "jugando"
        self.b_pista.etiqueta = "Pista gratis" if self.app.pistas_duende else \
            "Pista  (−%d mov.)" % COSTO_PISTA
        self.b_pista.habilitado = self.modo == "jugando" and (
            self.app.pistas_duende > 0 or
            self.partida.jugador.movimientos_restantes() > COSTO_PISTA)
        rueda_activa = self.rueda and self.rueda["estado"] == "rodando"
        self.b_pausa.habilitado = self.modo == "jugando" and \
            self.trampa["estado"] != "activa" and not rueda_activa
        self.b_inventario.habilitado = self.modo == "jugando"
        self.b_luz.etiqueta = "Antorcha: " + ("abierta" if self.linterna_on else "cubierta")

        if self.modo == "jugando" and self.trampa["estado"] == "activa":
            self.trampa["restante"] = max(0.0, self.trampa["restante"] - dt)
            if self.trampa["restante"] <= 0:
                self.trampa["estado"] = "fallo"
                self.partida.estado = ATRAPADO
                self._revisar_fin()

        if self.modo == "jugando" and self.rueda and self.rueda["estado"] == "rodando":
            self.rueda["restante"] = max(0.0, self.rueda["restante"] - dt)
            progreso = 1 - self.rueda["restante"] / self.rueda["duracion"]
            tramo = progreso * (len(self.rueda["camino"]) - 1)
            indice = min(int(tramo), len(self.rueda["camino"]) - 2)
            mezcla_r = tramo - indice
            a = self.rueda["camino"][-1 - indice]
            b = self.rueda["camino"][-2 - indice]
            pos_rueda = (a[0] + (b[0] - a[0]) * mezcla_r,
                         a[1] + (b[1] - a[1]) * mezcla_r)
            jugador = self.partida.jugador.posicion
            distancia = abs(pos_rueda[0] - jugador[0]) + abs(pos_rueda[1] - jugador[1])
            if distancia < 0.42:
                self.rueda["estado"] = "aplastada"
                self.partida.estado = ATRAPADO
                self._revisar_fin()
            elif self.rueda["restante"] <= 0:
                if self.partida.jugador.posicion in self.rueda["camino"]:
                    self.rueda["estado"] = "aplastada"
                    self.partida.estado = ATRAPADO
                    self._revisar_fin()
                else:
                    self.rueda["estado"] = "encajada"

        if self.modo != "pausa":
            movido = self._acercar(self.vis_j, self.partida.jugador.posicion, dt)
            self.andando = movido > 0.05
            if movido > 0.05:
                x, y = self._px(*self.vis_j)
                self.particulas.estela(x, y, CIAN, max(2, self.cell // 9))
            if len(self.vis_e) != len(self.partida.enemigos):
                self.vis_e = [[float(e.posicion[0]), float(e.posicion[1])]
                              for e in self.partida.enemigos]
            for vis, enemigo in zip(self.vis_e, self.partida.enemigos):
                intervalo = max(0.05, float(getattr(enemigo, "intervalo_paso", 0.75) or 0.75))
                v_lerp = max(8.0, 1.0 / intervalo)
                mov_e = self._acercar(vis, enemigo.posicion, dt, v_lerp)
                en_persecucion = getattr(enemigo, "estado", "patrulla") == "persecucion"
                dist_j = (abs(enemigo.posicion[0] - self.partida.jugador.posicion[0])
                          + abs(enemigo.posicion[1] - self.partida.jugador.posicion[1]))
                if en_persecucion and dist_j <= 4:
                    ex, ey = self._px(*vis)
                    self.ambiente.emitir_pulso_enemigo(ex, ey, intenso=True)
                    if mov_e > 0.02 and random.random() < min(1.0, dt * 15):
                        self.particulas.estela(ex, ey, MORADO, max(2, self.cell // 10))
                elif en_persecucion:
                    ex, ey = self._px(*vis)
                    self.ambiente.emitir_pulso_enemigo(ex, ey, intenso=False)
            casilla_eco = self.partida.posicion_eco()
            if casilla_eco is not None:
                self._acercar(self.vis_eco, casilla_eco, dt)
            casilla_radar = self.partida.posicion_radar()
            if self.partida.radar is not None:
                if self.partida.radar.contactos != self._contactos_radar:
                    self._contactos_radar = self.partida.radar.contactos     # volvió a su origen
                    self.vis_radar = [float(self.partida.radar.inicio[0]),
                                      float(self.partida.radar.inicio[1])]
                elif casilla_radar is not None:
                    self._acercar(self.vis_radar, casilla_radar, dt)
            self.particulas.actualizar(dt)

            distancias = [abs(e.posicion[0] - self.partida.jugador.posicion[0])
                          + abs(e.posicion[1] - self.partida.jugador.posicion[1])
                          for e in self.partida.enemigos]
            distancias_persecucion = [
                abs(e.posicion[0] - self.partida.jugador.posicion[0])
                + abs(e.posicion[1] - self.partida.jugador.posicion[1])
                for e in self.partida.enemigos
                if getattr(e, "estado", "patrulla") == "persecucion"
            ]
            if casilla_eco is not None:           # el eco también enciende la viñeta de peligro
                distancias.append(abs(casilla_eco[0] - self.partida.jugador.posicion[0])
                                  + abs(casilla_eco[1] - self.partida.jugador.posicion[1]))
            if casilla_radar is not None:         # el radar también enciende la viñeta de peligro
                distancias.append(abs(casilla_radar[0] - self.partida.jugador.posicion[0])
                                  + abs(casilla_radar[1] - self.partida.jugador.posicion[1]))
            cerca = min(distancias) if distancias else 99
            cerca_persecucion = min(distancias_persecucion) if distancias_persecucion else 99
            if self.partida.estado == JUGANDO:
                objetivo = max(0.0, (5 - cerca) / 4.0)
                if cerca_persecucion <= 4:
                    objetivo = max(objetivo, min(1.0, (5.5 - cerca_persecucion) / 3.5))
                elif cerca_persecucion < 99:
                    objetivo = max(objetivo, 0.22)
            else:
                objetivo = 0.0
            vel_peligro = 8.0 if cerca_persecucion <= 4 else 6.0
            peligro_previo = self.peligro
            self.peligro += (objetivo - self.peligro) * min(1.0, dt * vel_peligro)
            self.ambiente.nivel_peligro = self.peligro
            if (
                self.peligro > 0.45
                or cerca_persecucion <= 3
                or (peligro_previo > 0.45 and self.partida.estado == JUGANDO)
            ):
                peligro_temblor = (
                    self.peligro if self.peligro > 0.4 else max(peligro_previo, 0.48)
                )
                self.shake = max(
                    self.shake,
                    (peligro_temblor - 0.4) * 6.0 * (0.6 + 0.4 * math.sin(self.t * 18)),
                )

        if hasattr(self.app.sonidos, "actualizar_persecucion"):
            self.app.sonidos.actualizar_persecucion(self.peligro, dt)

        if self.modo == "fin_espera":
            self.espera -= dt
            if self.espera <= 0:
                self.modo = "nombre" if self.partida.estado == GANO else "opciones"
                self.pop = 0.0
                self.t_fin = 0.0
                self._armar_botones_fin()
        if self.modo in ("nombre", "opciones"):
            self.pop = min(1.0, self.pop + dt * 3.2)
            self.t_fin += dt

    # ------------------------------------------------------------ dibujo
    def dibujar(self, surf):
        """Pinta tablero, personajes, información y las capas de pausa o final. Devuelve: nada."""
        p = self.partida
        lab = p.laberinto
        self.zona.dibujar(surf, self.t)

        marco = pygame.Rect(self.origen, (self.tw, self.th)).inflate(14, 14)
        brillo(surf, marco.center, int(max(marco.w, marco.h) * 0.75), MORADO, 0.12)
        pygame.draw.rect(surf, (40, 39, 26), marco, border_radius=3)
        pygame.draw.rect(surf, (113, 99, 59), marco, width=2, border_radius=3)
        surf.blit(self.estatico, self.origen)
        self._etiquetas = []

        for vela in self.velas:
            vx, vy = self._px(*vela["casilla"])
            dibujar_vela(surf, vx, vy, self.cell, self.t, vela["fase"])
        self.ambiente.dibujar_niebla(surf)

        if self.puente:
            bx, by = self._px(*self.puente["casilla"])
            dibujar_puente(surf, bx, by, self.cell, self.puente["orientacion"], self.t)

        if self.rueda:
            if self.rueda["estado"] == "rodando":
                progreso = 1 - self.rueda["restante"] / self.rueda["duracion"]
                tramo = progreso * (len(self.rueda["camino"]) - 1)
                indice = min(int(tramo), len(self.rueda["camino"]) - 2)
                mezcla_r = tramo - indice
                a = self.rueda["camino"][-1 - indice]
                b = self.rueda["camino"][-2 - indice]
                pos_rueda = (a[0] + (b[0] - a[0]) * mezcla_r,
                             a[1] + (b[1] - a[1]) * mezcla_r)
                rx, ry = self._px(*pos_rueda)
                dibujar_rueda(surf, rx, ry, self.cell, self.t)
                sx_refugio, sy_refugio = self._px(*self.rueda["refugio"])
                radio_refugio = max(4, self.cell // 5)
                pygame.draw.rect(surf, ORO, (int(sx_refugio - radio_refugio),
                                              int(sy_refugio - radio_refugio),
                                              radio_refugio * 2, radio_refugio * 2), 1)
            else:
                if self.rueda["estado"] == "dormida":
                    for pos in self.rueda["camino"]:
                        gx, gy = self._px(*pos)
                        if self.rueda["orientacion"] == "horizontal":
                            pygame.draw.line(surf, (68, 59, 43), (gx - self.cell // 3, gy),
                                             (gx + self.cell // 3, gy), 2)
                        else:
                            pygame.draw.line(surf, (68, 59, 43), (gx, gy - self.cell // 3),
                                             (gx, gy + self.cell // 3), 2)
                estacion = self.rueda["activador"] if self.rueda["estado"] == "encajada" \
                    else self.rueda["camino"][-1]
                rx, ry = self._px(*estacion)
                dibujar_rueda(surf, rx, ry, self.cell, 1.0 if self.rueda["estado"] == "encajada"
                              else self.t * 0.15)

        sx, sy = self._px(*lab.salida)
        dibujar_portal(surf, sx, sy, self.cell, self.t)
        if self.trampa["placa"] is not None:
            tx, ty = self._px(*self.trampa["placa"])
            rx, ry = self._px(*self.trampa["retorno"])
            dibujar_trampa(surf, tx, ty, self.cell, self.t, self.trampa["estado"], (rx, ry))
        if self.puas:
            px, py = self._px(*self.puas["casilla"])
            dibujar_puas(surf, px, py, self.cell, self.t,
                         activas=self.puas["estado"] == "armada")
            if self.puas["estado"] == "armada":
                jpos = self.partida.jugador.posicion
                distancia = abs(jpos[0] - self.puas["casilla"][0]) + \
                    abs(jpos[1] - self.puas["casilla"][1])
                if distancia <= 2:
                    indicacion = ("CADENA VERDE · ESPACIO + PASO" if self._cadena_segura()
                                  else "ESPERA LA CADENA · PREPARA ESPACIO") if self.cadena else \
                        "ESPACIO · SALTAR"
                    color_indicacion = VERDE if self.cadena and self._cadena_segura() else ORO
                    self._etiqueta(indicacion, 12, color_indicacion, px, py - self.cell * 0.75)
        if self.cadena and self.cadena["estado"] in ("armada", "superada"):
            cx_cadena, cy_cadena = self._px(*self.cadena["casilla"])
            dibujar_cadena(surf, cx_cadena, cy_cadena, self.cell, self.t,
                           self.cadena["fase"], self._cadena_segura())
        if self.rotatoria and self.rotatoria["estado"] in ("armada", "superada"):
            rx, ry = self._px(*self.rotatoria["casilla"])
            segura = self._rotatoria_segura() and self.rotatoria["estado"] == "armada"
            dibujar_trampa_giratoria(surf, rx, ry, self.cell, self.t, segura,
                                     self.rotatoria["fase"])
            jpos = self.partida.jugador.posicion
            distancia = abs(jpos[0] - self.rotatoria["casilla"][0]) + \
                abs(jpos[1] - self.rotatoria["casilla"][1])
            if distancia <= 2 and self.rotatoria["estado"] == "armada":
                self._etiqueta("GIRO VERDE · ESPACIO + PASO" if segura else "ESPERA EL GIRO VERDE",
                               12, VERDE if segura else ORO, rx, ry - self.cell * 0.68)
        if self.trampa["hallazgo"] is not None and not self.trampa["hallazgo_tomado"]:
            hx, hy = self._px(*self.trampa["hallazgo"])
            dibujar_reliquia(surf, hx, hy, self.cell, self.t)
        for cofre in getattr(p, "cofres", []):
            casilla_c = cofre.get("casilla") if isinstance(cofre, dict) else cofre
            abierto_c = cofre.get("abierto", False) if isinstance(cofre, dict) else False
            if casilla_c is not None:
                cx_c, cy_c = self._px(*casilla_c)
                dibujar_cofre(surf, cx_c, cy_c, self.cell, self.t, abierto=abierto_c)
        for estrella_pos in getattr(p, "estrellas", []):
            casilla_e = estrella_pos.get("casilla") if isinstance(estrella_pos, dict) else estrella_pos
            if casilla_e is not None:
                ex_s, ey_s = self._px(*casilla_e)
                dibujar_estrella(surf, ex_s, ey_s, self.cell, self.t)
        if p.pista_actual:
            dibujar_pista(surf, p.pista_actual, self.origen, self.cell, self.t)
        jx, jy = self._px(*self.vis_j)
        for vis in self.vis_e:
            ex, ey = self._px(*vis)
            dibujar_enemigo(surf, ex, ey, self.cell, self.t, (jx - ex, jy - ey))
        if self.partida.posicion_eco() is not None:
            ex, ey = self._px(*self.vis_eco)
            dibujar_eco(surf, ex, ey, self.cell, self.t)
        if self.partida.posicion_radar() is not None:
            rx, ry = self._px(*self.vis_radar)
            dibujar_radar(surf, rx, ry, self.cell, self.t)
        jpos = self.partida.jugador.posicion
        for esqueleto in self.esqueletos:
            if not esqueleto["vivo"]:
                continue
            ex, ey = self._px(*esqueleto["casilla"])
            dibujar_esqueleto(surf, ex, ey, self.cell, self.t, esqueleto["fase"])
            distancia = abs(jpos[0] - esqueleto["casilla"][0]) + \
                abs(jpos[1] - esqueleto["casilla"][1])
            if distancia <= 2:
                dx, dy = DIRECCIONES[self.direccion]
                delante = esqueleto["casilla"] == (jpos[0] + dx, jpos[1] + dy)
                etiqueta = "F / X · ATACAR" if delante else "ESQUELETO"
                color_etiqueta = (132, 240, 129) if delante else APAGADO
                self._etiqueta(etiqueta, 11, color_etiqueta, ex, ey - self.cell * 0.53)
        self.particulas.dibujar(surf)
        if self.salto_animacion > 0:
            fase_salto = 1 - self.salto_animacion / 0.38
            elevacion = int(math.sin(fase_salto * math.pi) * self.cell * 0.48)
            pygame.draw.ellipse(surf, (11, 13, 9),
                                (int(jx - self.cell * 0.22), int(jy + self.cell * 0.18),
                                 int(self.cell * 0.44), max(2, int(self.cell * 0.13))))
            jy -= elevacion
        dibujar_jugador(surf, jx, jy, self.cell, self.t, antorcha=self.linterna_on,
                        direccion=self.direccion, andando=self.andando,
                        saltando=self.salto_animacion > 0)
        if self.ataque_animacion > 0:
            progreso_ataque = 1 - self.ataque_animacion / 0.28
            dibujar_espada_verde(surf, jx, jy, self.cell, self.t, self.direccion,
                                 progreso_ataque)

        self.ambiente.dibujar_polvo(surf)
        luces = [(sx - self.origen[0], sy - self.origen[1])]
        luces.extend(self.ambiente.luces_para_linterna(self.origen))     # antorchas que parpadean
        for estrella_pos in getattr(p, "estrellas", []):
            casilla_e = estrella_pos.get("casilla") if isinstance(estrella_pos, dict) else estrella_pos
            if casilla_e is not None:
                ex_s, ey_s = self._px(*casilla_e)
                luces.append((ex_s - self.origen[0], ey_s - self.origen[1], 0.55))
        for cofre in getattr(p, "cofres", []):
            casilla_c = cofre.get("casilla") if isinstance(cofre, dict) else cofre
            abierto_c = cofre.get("abierto", False) if isinstance(cofre, dict) else False
            if casilla_c is not None and not abierto_c:
                cx_c, cy_c = self._px(*casilla_c)
                luces.append((cx_c - self.origen[0], cy_c - self.origen[1], 0.50))
        if self.ataque_animacion > 0:
            dxf, dyf = DIRECCIONES[self.direccion]
            luces.append((jx + dxf * self.cell * 0.48 - self.origen[0],
                          jy + dyf * self.cell * 0.48 - self.origen[1]))
        capa_luz = self.linterna if self.linterna_on else self.linterna_cubierta
        capa_luz.dibujar(surf, self.origen, (jx - self.origen[0], jy - self.origen[1]), luces,
                         OSCURIDAD_POR_BRILLO[self.app.brillo])
        self.ambiente.dibujar_luces(surf)
        pixelar_region(surf, pygame.Rect(self.origen, (self.tw, self.th)), 2)
        self._dibujar_etiquetas(surf)
        if self.trampa["estado"] == "activa":
            panel(surf, pygame.Rect(ANCHO // 2 - 218, 16, 436, 44), 238, ROJO, 4)
            texto(surf, "¡TRAMPA! REGRESA A LA MARCA  ·  %.1f s" % self.trampa["restante"],
                  15, ROJO, (ANCHO // 2, 29), "midtop", negrita=True)
        elif self.rueda and self.rueda["estado"] == "rodando":
            panel(surf, pygame.Rect(ANCHO // 2 - 218, 16, 436, 44), 238, ROJO, 4)
            texto(surf, "¡RUEDA DE HIERRO! SAL DEL CARRIL  ·  %.1f s" % self.rueda["restante"],
                  15, ROJO, (ANCHO // 2, 29), "midtop", negrita=True)
        self._dibujar_hud(surf)
        if self.alerta_tiempo > 0 and self.alerta:
            aviso = pygame.Rect(ANCHO // 2 - 230, ALTO - 52, 460, 36)
            color_aviso = (VERDE if "esqueleto" in self.alerta.lower()
                           else ROJO if "enemigo" in self.alerta.lower() else ORO)
            panel(surf, aviso, 232, color_aviso, 2)
            texto(surf, self.alerta, 14, TEXTO, (aviso.centerx, aviso.centery), "center",
                  negrita=True)

        if self.peligro > 0.02:
            critico = self.peligro > 0.45
            v = vineta(ROJO, 238 if critico else 210)
            freq_v = 16.0 if critico else 9.0
            pulso_v = (
                (0.72 + 0.42 * math.sin(self.t * freq_v))
                if critico
                else (0.65 + 0.35 * math.sin(self.t * freq_v))
            )
            v.set_alpha(int(255 * max(0.0, min(1.0, self.peligro * pulso_v))))
            surf.blit(v, (0, 0))

        if self.modo == "pausa":
            self._velo(surf, 170)
            panel(surf, pygame.Rect(ANCHO // 2 - 220, 190, 440, 320), 240)
            texto(surf, "PAUSA", 52, TEXTO, (ANCHO // 2, 214), "midtop", negrita=True)
            for b in self.botones_pausa:
                b.dibujar(surf)
        elif self.modo in ("nombre", "opciones"):
            self._velo(surf, 150)
            self._dibujar_final(surf)
        if self.modo in ("fin_espera", "nombre", "opciones"):
            self.particulas.dibujar(surf)      # el confeti cae también por encima del panel

    def _etiqueta(self, s, tam, color, x, y):
        """
        (Interno) Anota un cartel pequeño sobre el tablero; se dibuja al final, encima de la
        oscuridad, para que se lea bien y no quede cortado en los bordes.

        Recibe:
            s: el texto.
            tam: tamaño de la letra.
            color: color del texto.
            x, y: punto en pantalla donde debe quedar el centro de abajo del cartel.
        Devuelve:
            Nada.
        """
        self._etiquetas.append((s, tam, color, x, y))

    def _dibujar_etiquetas(self, surf):
        """
        (Interno) Dibuja los carteles anotados con _etiqueta sobre un fondo oscuro suave,
        empujándolos hacia adentro si se saldrían del tablero.

        Recibe:
            surf: superficie donde se dibuja.
        Devuelve:
            Nada.
        """
        limite = pygame.Rect(self.origen, (self.tw, self.th)).inflate(-6, -6)
        for s, tam, color, x, y in self._etiquetas:
            ancho, alto = fuente(tam, True).size(s)
            caja = pygame.Rect(0, 0, ancho + 14, alto + 6)
            caja.midbottom = (int(x), int(y))
            caja.clamp_ip(limite)
            fondo = pygame.Surface(caja.size, pygame.SRCALPHA)
            pygame.draw.rect(fondo, (8, 8, 6, 175), fondo.get_rect(), border_radius=4)
            surf.blit(fondo, caja.topleft)
            texto(surf, s, tam, color, caja.center, "center", negrita=True, sombra=False)

    def _velo(self, surf, alpha):
        """(Interno) Oscurece la pantalla detrás de un panel."""
        v = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        v.fill((6, 4, 16, alpha))
        surf.blit(v, (0, 0))

    def _dibujar_hud(self, surf):
        """(Interno) Panel derecho con los colores de la zona: movimientos, pila, enemigos, botones y estructuras en vivo."""
        p = self.partida
        j = p.jugador
        color = self.color_nivel
        r = pygame.Rect(780, 20, 300, 680)
        panel(surf, r, 228, mezclar(BORDE, color, 0.45),
              color=mezclar(PANEL, self.zona.paleta["oscuridad"], 0.55))
        # Encabezado: el paisaje de la zona detrás del nombre del nivel
        surf.blit(self.zona.miniatura((r.w - 6, 80)), (r.x + 3, r.y + 3))
        surf.blit(self._cabecera_hud, (r.x + 3, r.y + 3))
        pygame.draw.line(surf, mezclar(color, (235, 214, 148), 0.25),
                         (r.x + 3, r.y + 83), (r.right - 3, r.y + 83), 1)
        remaches(surf, r, mezclar(BORDE, color, 0.3), 8)
        texto(surf, self.nivel["nombre"].upper(), 34, color, (800, 34), negrita=True)
        texto(surf, "Laberinto %d × %d" % (self.nivel["filas"], self.nivel["columnas"]), 16,
              (205, 198, 168), (802, 76), sombra=False)
        estrellas_rec = min(3, max(0, int(getattr(p, "estrellas_recogidas", 0))))
        cadena_estrellas = " ".join("★" if k < estrellas_rec else "☆" for k in range(3))
        texto(surf, cadena_estrellas, 22, ORO, (1060, 42), "topright", negrita=True)
        texto(surf, "I / Tab · Códice", 12, CIAN, (1060, 76), "topright", sombra=False)

        # Barra de movimientos: con marcas cada 10 % y un borde que late cuando quedan pocos
        texto(surf, "MOVIMIENTOS", 15, APAGADO, (800, 108), sombra=False, negrita=True)
        restantes, total = j.movimientos_restantes(), j.max_movimientos
        frac = restantes / total if total else 0
        poco = frac < 0.2 and p.estado == JUGANDO
        barra = pygame.Rect(800, 132, 260, 20)
        pygame.draw.rect(surf, (14, 13, 9), barra, border_radius=10)
        tono = mezclar(ROJO, VERDE, min(1.0, frac * 1.6))
        if frac > 0:
            relleno = pygame.Rect(barra.x, barra.y, max(10, int(barra.w * frac)), barra.h)
            pygame.draw.rect(surf, tono, relleno, border_radius=10)
            pygame.draw.line(surf, mezclar(tono, (255, 255, 255), 0.35),
                             (relleno.x + 6, relleno.y + 4), (relleno.right - 6, relleno.y + 4), 1)
        for k in range(1, 10):
            x = barra.x + barra.w * k // 10
            pygame.draw.line(surf, (14, 13, 9), (x, barra.y + 3), (x, barra.bottom - 4), 1)
        borde = mezclar(BORDE, ROJO, 0.5 + 0.5 * math.sin(self.t * 8)) if poco else BORDE
        pygame.draw.rect(surf, borde, barra, 2, border_radius=10)
        texto(surf, "%d restantes de %d" % (restantes, total), 17, ROJO if poco else TEXTO,
              (800, 158), sombra=False)

        # Pila de deshacer (se dibuja como una torre de bloques; el de arriba brilla)
        texto(surf, "PASOS PARA DESHACER", 15, APAGADO, (800, 200), sombra=False, negrita=True)
        n = j.pasos_por_deshacer()
        texto(surf, str(n), 34, CIAN, (800, 220), negrita=True)
        alto_torre = min(n, 8)
        for k in range(alto_torre):
            bloque = pygame.Rect(1000, 262 - k * 9, 60, 7)
            pygame.draw.rect(surf, mezclar((58, 82, 50), CIAN, k / 8), bloque, border_radius=3)
            if k == alto_torre - 1:
                pygame.draw.rect(surf, (235, 240, 190), bloque, 1, border_radius=3)
                brillo(surf, bloque.center, 34, CIAN, 0.18)
        texto(surf, "PILA", 13, APAGADO, (1060, 202), "topright", sombra=False)

        texto(surf, "PRESENCIAS", 15, APAGADO, (800, 280), sombra=False, negrita=True)
        vivos = sum(e["vivo"] for e in self.esqueletos)
        texto_ajustado(surf, "%s  ·  %s" % (plural(len(p.enemigos), "espectro", "espectros"),
                                            plural(vivos, "esqueleto", "esqueletos")),
                       14, TEXTO, (800, 298), 260)
        texto_ajustado(surf, "F / X · ESPADA VERDE", 12, ORO, (800, 316), 150)
        texto_ajustado(surf, "Pistas gratis: %d" % self.app.pistas_duende, 12, ORO,
                       (1060, 316), 105, "topright")

        for b in self.botones_hud:
            b.dibujar(surf)

        # Estructuras en acción: un cuadro de color por estructura para reconocerlas de un vistazo
        base = 548
        separador(surf, 800, 1060, base - 10, BORDE)
        texto(surf, "REGISTRO DEL VIAJERO", 14, ORO, (800, base), sombra=False, negrita=True)
        radar_txt = ""
        if p.radar is not None:
            radar_txt = (" · radar a %d" % p.radar.pasos_pendientes()) if p.radar.activo \
                else " · radar dormido"
        lineas = [
            "Pila · deshacer: %s" % plural(n, "elemento", "elementos"),
            ("Cola · BFS: camino de %d casillas" % len(p.pista_actual)) if p.pista_actual
            else ("Cola · eco: %s en espera" % plural(p.eco.pasos_pendientes(), "paso", "pasos")
                  + radar_txt)
            if p.eco is not None else "Cola · BFS: lista para la pista",
            "Lista circular · rutas: %s" % resumir_lista([e.ruta.tamanio() for e in p.enemigos]),
            "Lista doble · historial: %s" % plural(p.historial.total(), "foto", "fotos"),
            "Árbol BST · puntajes: %d" % self.app.tabla.cantidad(),
            "Mapa fragmentado: %s" % ("recuperado" if self.trampa["hallazgo_tomado"] else
                                        "en ramal" if self.trampa["hallazgo"] is not None else "—"),
        ]
        marcas = (CIAN, ORO, (104, 168, 186), (178, 128, 176), (214, 106, 74), APAGADO)
        for i, linea in enumerate(lineas):
            y = base + 24 + i * 20
            pygame.draw.rect(surf, marcas[i], (800, y + 5, 7, 7))
            texto_ajustado(surf, linea, 15, TEXTO if i != 1 or p.pista_actual or p.eco is not None
                           else APAGADO,
                           (814, y), 246, tam_min=12)

    def _dibujar_final(self, surf):
        """(Interno) Panel de victoria o derrota con puntaje, nombre y botones."""
        p = self.partida
        gano = p.estado == GANO
        sube = int((1 - self._ease(self.pop)) * 50)
        rect = pygame.Rect(ANCHO // 2 - 300, (100 if gano else 150) + sube, 600, 530 if gano else 380)
        color = ORO if gano else ROJO
        aparece = self._ease(self.pop)
        if gano:
            rayos(surf, rect.center, self.t, ORO, 560, 12, 0.6 * aparece)       # rayos de victoria
        else:
            ceniza(surf, self.t, (190, 120, 100), 46, aparece)                  # ceniza de derrota
        brillo(surf, rect.center, 420, color, 0.12)
        panel(surf, rect, 245, mezclar(BORDE, color, 0.6),
              color=mezclar(PANEL, self.zona.paleta["oscuridad"], 0.55))
        surf.blit(self.zona.miniatura((rect.w - 4, 100)), (rect.x + 2, rect.y + 2))
        surf.blit(self._cabecera_final[gano], (rect.x + 2, rect.y + 2))
        pygame.draw.line(surf, mezclar(color, (235, 214, 148), 0.3),
                         (rect.x + 2, rect.y + 102), (rect.right - 2, rect.y + 102), 1)
        remaches(surf, rect, mezclar(BORDE, color, 0.5), 10)
        cx = ANCHO // 2
        if gano:
            texto(surf, "ENCONTRASTE LA PUERTA", 40, ORO, (cx, rect.y + 24), "midtop", negrita=True)
            estrellas_ganadas = (
                p.estrellas_conseguidas()
                if hasattr(p, "estrellas_conseguidas")
                else max(1, min(3, getattr(p, "estrellas_recogidas", 0)))
            )
            for idx_e in range(3):
                ex_f = cx + (idx_e - 1) * 64
                ey_f = rect.y + 82
                ganada = idx_e < estrellas_ganadas
                if ganada:
                    dibujar_estrella(surf, ex_f, ey_f, 44, self.t + idx_e * 0.4)
                else:
                    pygame.draw.circle(surf, (38, 35, 26), (ex_f, ey_f), 14)
                    pygame.draw.circle(surf, (96, 88, 62), (ex_f, ey_f), 14, 2)
            estrellas_txt = " ".join("★" if k < estrellas_ganadas else "☆" for k in range(3))
            texto(surf, "%s  ·  Nivel %s (%d mov.)" % (
                estrellas_txt, self.nivel["nombre"], p.jugador.movimientos), 18, ORO,
                  (cx, rect.y + 114), "midtop", negrita=True)
            sobrantes = p.jugador.movimientos_restantes()
            est_recogidas = getattr(p, "estrellas_recogidas", 0)
            filas = [("Base del nivel", "+%d" % self.nivel["base"]),
                     ("Movimientos sobrantes (%d × %d)" % (sobrantes, PUNTOS_POR_MOVIMIENTO_SOBRANTE),
                      "+%d" % (sobrantes * PUNTOS_POR_MOVIMIENTO_SOBRANTE)),
                     ("Estrellas recogidas (%d × 150)" % est_recogidas,
                      "+%d" % (est_recogidas * 150))]
            for i, (a, b) in enumerate(filas):
                y = rect.y + 146 + i * 26
                texto(surf, a, 18, TEXTO, (rect.x + 60, y), sombra=False)
                texto(surf, b, 18, VERDE, (rect.right - 60, y), "topright", sombra=False, negrita=True)
            separador(surf, rect.x + 50, rect.right - 50, rect.y + 230, BORDE)
            texto(surf, "PUNTAJE", 26, ORO, (rect.x + 60, rect.y + 242), negrita=True)
            mostrado = int(p.puntaje() * self._ease(min(1.0, self.t_fin / 1.2)))   # el puntaje sube
            texto(surf, str(mostrado), 48, ORO, (rect.right - 60, rect.y + 228), "topright",
                  negrita=True)
            if self.modo == "nombre":
                texto(surf, "Escribe tu nombre para guardarlo en el ranking", 18, APAGADO,
                      (cx, rect.y + 322), "midtop", sombra=False)
                self.campo.dibujar(surf, self.t)
            elif self.guardado:
                texto(surf, "¡Guardado! Quedaste en el puesto #%d" % self.guardado, 24, VERDE,
                      (cx, rect.y + 352), "midtop", negrita=True)
            else:
                texto(surf, "Puntaje no guardado", 20, APAGADO, (cx, rect.y + 352), "midtop",
                      sombra=False)
        else:
            titulo = ("EL ROTOR TE ALCANZÓ" if self.rotatoria and self.rotatoria["estado"] == "fallo"
                      else "LA CADENA TE GOLPEÓ" if self.cadena and self.cadena["estado"] == "fallo"
                      else "LA RUEDA TE APLASTÓ" if self.rueda and self.rueda["estado"] == "aplastada"
                      else "LAS CUCHILLAS TE ALCANZARON" if self.puas and self.puas["estado"] == "fallo"
                      else "LA TRAMPA TE ALCANZÓ" if self.trampa["estado"] == "fallo" else
                      "¡TE ATRAPARON!" if p.estado == ATRAPADO else "SIN MOVIMIENTOS")
            texto(surf, titulo, 52, ROJO, (cx, rect.y + 34), "midtop", negrita=True)
            detalle = ("Espera a que las cuchillas brillen verde, salta y cruza el rotor." \
                       if self.rotatoria and self.rotatoria["estado"] == "fallo" else
                       "Espera a que el péndulo se aparte, luego salta sobre las cuchillas." \
                       if self.cadena and self.cadena["estado"] == "fallo" else
                       "Abandona el carril antes de que la rueda llegue al hueco." \
                       if self.rueda and self.rueda["estado"] == "aplastada" else
                       "Debías pulsar Espacio y saltar antes de pisar las cuchillas." \
                       if self.puas and self.puas["estado"] == "fallo" else
                       "El mecanismo se cerró antes de que volvieras a la marca." \
                       if self.trampa["estado"] == "fallo" else
                       "Tu propio eco te alcanzó: no te quedes quieto." if p.causa == "eco"
                       else "Una presencia llegó hasta tu casilla." if p.estado == ATRAPADO
                       else "Gastaste todos los movimientos antes de llegar.")
            texto(surf, detalle, 21, TEXTO, (cx, rect.y + 120), "midtop", sombra=False)
            texto(surf, "Resististe %d movimiento%s" % (p.jugador.movimientos,
                                                      "" if p.jugador.movimientos == 1 else "s"), 20, APAGADO,
                  (cx, rect.y + 160), "midtop", sombra=False)
            texto(surf, "Tip: la pista (H) dibuja el camino más corto con BFS.", 18, ORO,
                  (cx, rect.y + 230), "midtop", sombra=False)
            texto(surf, "Los espectros no patrullan el camino más corto.", 16, APAGADO,
                  (cx, rect.y + 262), "midtop", sombra=False)
        for b in self.botones_fin:
            b.rect.y += sube
            b.dibujar(surf)
            b.rect.y -= sube

    @staticmethod
    def _ease(x):
        """(Interno) Suaviza una animación: empieza rápido y termina despacio."""
        return 1 - (1 - x) ** 3


# =====================================================================================
#  REPETICIÓN
# =====================================================================================
class Repeticion(Pantalla):
    """Reproduce la partida paso a paso, hacia adelante y atrás, con la Lista Doble."""

    def __init__(self, app, partida, volver):
        """
        Prepara la repetición.

        Recibe:
            app: la App.
            partida: la Partida cuyo historial se va a ver.
            volver: función que devuelve la pantalla a la que se vuelve al salir.
        Devuelve:
            Nada (constructor).
        """
        super().__init__(app)
        self.partida = partida
        self.volver = volver
        self.h = partida.historial
        self.h.ir_al_inicio()
        lab = partida.laberinto
        self.cell = max(10, min(740 // lab.ancho, 585 // lab.alto))
        self.tw, self.th = self.cell * lab.ancho, self.cell * lab.alto
        self.origen = (20 + (740 - self.tw) // 2, 20 + (585 - self.th) // 2)
        self.estatico = tablero_estatico(lab, self.cell, paleta=paleta_de(partida.nivel["nombre"]))
        foto = self.h.actual()
        self.vis_j = [float(foto[0][0]), float(foto[0][1])]
        self.vis_e = [[float(f), float(c)] for f, c in foto[1]]
        self.reproduciendo = False
        self.reloj = 0.0
        self.particulas = Particulas()
        self.camino_recorrido = []
        self._indice_cache = -1

        bx = 20 + (740 - (5 * 64 + 4 * 12)) // 2
        def pos(i):
            """Posición del botón número i de la fila de controles. Recibe: i. Devuelve: tupla (x, y, ancho, alto)."""
            return (bx + i * 76, 630, 64, 48)
        self.b_inicio = Boton("", pos(0), self.ir_inicio, "", MORADO, icono=icono_inicio)
        self.b_atras = Boton("", pos(1), self.atras, "", MORADO, icono=icono_atras)
        self.b_play = Boton("", pos(2), self.alternar, "", CIAN, icono=icono_play)
        self.b_adelante = Boton("", pos(3), self.adelante, "", MORADO, icono=icono_play)
        self.b_final = Boton("", pos(4), self.ir_final, "", MORADO, icono=icono_final)
        self.b_salir = Boton("Salir", (800, 630, 260, 48), self.salir, "Esc", APAGADO, 22)
        self.botones = [self.b_inicio, self.b_atras, self.b_play, self.b_adelante, self.b_final,
                        self.b_salir]

    # -- navegación por la lista doble
    def adelante(self):
        """Va al siguiente paso (cursor hacia adelante). Recibe/devuelve: nada."""
        self.reproduciendo = False
        self.h.adelante()

    def atras(self):
        """Va al paso anterior (cursor hacia atrás). Recibe/devuelve: nada."""
        self.reproduciendo = False
        self.h.atras()

    def ir_inicio(self):
        """Salta al primer paso. Recibe/devuelve: nada."""
        self.reproduciendo = False
        self.h.ir_al_inicio()

    def ir_final(self):
        """Salta al último paso. Recibe/devuelve: nada."""
        self.reproduciendo = False
        self.h.ir_al_final()

    def alternar(self):
        """Reproduce o pausa la repetición. Recibe/devuelve: nada."""
        if self.h.indice() >= self.h.total() - 1:
            self.h.ir_al_inicio()
        self.reproduciendo = not self.reproduciendo

    def ir_a_indice(self, destino):
        """
        Mueve el cursor de la lista doble hasta un paso concreto (clic en la línea de tiempo).

        Recibe:
            destino: número de paso, desde 0.
        Devuelve:
            Nada.
        """
        self.reproduciendo = False
        while self.h.indice() < destino and self.h.adelante():
            pass
        while self.h.indice() > destino and self.h.atras():
            pass

    def salir(self):
        """Vuelve a la pantalla anterior. Recibe/devuelve: nada."""
        self.app.ir_a(self.volver())

    def _linea_tiempo(self):
        """(Interno) Rect de la línea de tiempo clicable."""
        return pygame.Rect(20, 612, 740, 10)

    def evento(self, e):
        """Teclado y mouse de la repetición. Recibe: e. Devuelve: nada."""
        if self._clics(e, self.botones):
            return
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            lt = self._linea_tiempo().inflate(0, 16)
            if lt.collidepoint(e.pos):
                total = max(1, self.h.total() - 1)
                self.ir_a_indice(int(round((e.pos[0] - lt.x) / lt.w * total)))
        elif e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_RIGHT, pygame.K_d):
                self.adelante()
            elif e.key in (pygame.K_LEFT, pygame.K_a):
                self.atras()
            elif e.key == pygame.K_SPACE:
                self.alternar()
            elif e.key == pygame.K_HOME:
                self.ir_inicio()
            elif e.key == pygame.K_END:
                self.ir_final()
            elif e.key == pygame.K_ESCAPE:
                self.salir()

    def actualizar(self, dt):
        """Avanza la reproducción y anima los personajes. Recibe: dt. Devuelve: nada."""
        super().actualizar(dt)
        mouse = pygame.mouse.get_pos()
        for b in self.botones:
            b.actualizar(dt, mouse)
        self.b_play.icono = icono_pausa if self.reproduciendo else icono_play
        if self.reproduciendo:
            self.reloj += dt
            while self.reloj >= 0.14:
                self.reloj -= 0.14
                if not self.h.adelante():
                    self.reproduciendo = False
                    break
        foto = self.h.actual()
        k = min(1.0, dt * 14)
        for vis, objetivo in [(self.vis_j, foto[0])] + list(zip(self.vis_e, foto[1])):
            vis[0] += (objetivo[0] - vis[0]) * k
            vis[1] += (objetivo[1] - vis[1]) * k
        if self._indice_cache != self.h.indice():           # camino recorrido hasta este paso
            self._indice_cache = self.h.indice()
            self.camino_recorrido = []
            self.h.recorrer_hasta_actual(lambda f: self.camino_recorrido.append(f[0]))

    def _px(self, fila, col):
        """(Interno) Centro en pantalla de una casilla."""
        return (self.origen[0] + (col + 0.5) * self.cell, self.origen[1] + (fila + 0.5) * self.cell)

    def dibujar(self, surf):
        """Pinta la repetición. Recibe: surf. Devuelve: nada."""
        self.app.fondo.dibujar(surf, self.t)
        lab = self.partida.laberinto
        marco = pygame.Rect(self.origen, (self.tw, self.th)).inflate(14, 14)
        pygame.draw.rect(surf, (44, 38, 82), marco, border_radius=10)
        surf.blit(self.estatico, self.origen)
        sx, sy = self._px(*lab.salida)
        dibujar_portal(surf, sx, sy, self.cell, self.t)

        # Camino recorrido hasta el paso actual (recorrido de la lista doble)
        n = len(self.camino_recorrido)
        for i in range(1, n):
            a = self._px(*self.camino_recorrido[i - 1])
            b = self._px(*self.camino_recorrido[i])
            pygame.draw.line(surf, mezclar((20, 60, 90), CIAN, i / n), a, b, max(2, self.cell // 6))
        jx, jy = self._px(*self.vis_j)
        for vis in self.vis_e:
            ex, ey = self._px(*vis)
            dibujar_enemigo(surf, ex, ey, self.cell, self.t, (jx - ex, jy - ey))
        dibujar_jugador(surf, jx, jy, self.cell, self.t)

        # Línea de tiempo
        lt = self._linea_tiempo()
        pygame.draw.rect(surf, (14, 11, 30), lt, border_radius=5)
        total = max(1, self.h.total() - 1)
        ancho = int(lt.w * self.h.indice() / total)
        if ancho > 0:
            pygame.draw.rect(surf, CIAN, (lt.x, lt.y, ancho, lt.h), border_radius=5)
        pygame.draw.circle(surf, TEXTO, (lt.x + ancho, lt.centery), 8)

        for b in self.botones:
            b.dibujar(surf)

        # Panel de información
        panel(surf, pygame.Rect(780, 20, 300, 590), 215)
        texto(surf, "REPETICIÓN", 34, MORADO, (800, 34), negrita=True)
        texto(surf, "Paso %d de %d" % (self.h.indice() + 1, self.h.total()), 26, TEXTO, (800, 100),
              negrita=True)
        foto = self.h.actual()
        texto(surf, "Movimientos gastados: %d" % foto[2], 18, APAGADO, (800, 140), sombra=False)
        texto(surf, "Posición: fila %d, columna %d" % foto[0], 16, APAGADO, (800, 168), sombra=False)
        pygame.draw.line(surf, BORDE, (800, 214), (1060, 214), 1)
        texto(surf, "LISTA DOBLEMENTE ENLAZADA", 14, ORO, (800, 228), sombra=False, negrita=True)
        explic = ["Cada paso es un nodo que", "conoce al anterior y al", "siguiente. Por eso puedes",
                  "ir hacia adelante y hacia", "atrás sin volver a empezar.", "",
                  "Teclas:", "←  →   paso a paso", "Espacio   reproducir", "Inicio / Fin   extremos"]
        for i, linea in enumerate(explic):
            texto(surf, linea, 16, TEXTO if i < 5 else APAGADO, (800, 258 + i * 24), sombra=False)
        estado = self.partida.estado
        resultado = {GANO: ("¡Llegó a la salida!", VERDE), ATRAPADO: ("Lo atrapó una presencia", ROJO),
                     SIN_MOVIMIENTOS: ("Se quedó sin movimientos", ROJO)}.get(estado, ("Partida sin terminar", APAGADO))
        texto(surf, resultado[0], 20, resultado[1], (800, 540), negrita=True, sombra=False)


# =====================================================================================
#  RANKING (con el árbol BST dibujado)
# =====================================================================================
class Ranking(Pantalla):
    """Mejores puntajes: lista ordenada y el árbol BST dibujado con recorridos animados."""

    def __init__(self, app):
        """Crea botones y calcula la forma del árbol. Recibe: app. Devuelve: nada."""
        super().__init__(app)
        self.tabla = app.tabla
        self.seleccion = None            # id del nodo seleccionado
        self.resaltar = []               # ids en orden (recorrido o búsqueda) a mostrar
        self.visibles = 0                # cuántos del recorrido se muestran
        self.reloj = 0.0
        self.mensaje = "Toca un nodo para buscarlo, o elige un recorrido."
        self.confirmar = False
        self.area = pygame.Rect(440, 150, 630, 400)
        y = 628
        self.botones = [
            Boton("Inorden", (440, y, 150, 46), lambda: self.recorrer("inorden"), "", CIAN, 20),
            Boton("Preorden", (600, y, 150, 46), lambda: self.recorrer("preorden"), "", ORO, 20),
            Boton("Posorden", (760, y, 150, 46), lambda: self.recorrer("posorden"), "", VERDE, 20),
            Boton("Volver", (920, y, 150, 46), lambda: app.ir_a(Menu(app)), "Esc", APAGADO, 20),
        ]
        self.b_eliminar = Boton("Eliminar seleccionado", (40, 628, 360, 46), self.eliminar, "Supr",
                                ROJO, 20, habilitado=False)
        self.botones.append(self.b_eliminar)
        self._cargar()

    def _cargar(self):
        """(Interno) Lee del árbol la lista ordenada y los nodos para dibujar."""
        self.mejores = self.tabla.mejores(10)
        self.nodos = self.tabla.nodos_para_dibujar()
        self.por_id = {n["id"]: n for n in self.nodos}
        self.pos = {}
        total = len(self.nodos)
        if total:
            niveles = max(n["nivel"] for n in self.nodos) + 1
            dx = self.area.w / total
            dy = min(88, (self.area.h - 50) / max(1, niveles - 1)) if niveles > 1 else 0
            for n in self.nodos:
                self.pos[n["id"]] = (self.area.x + (n["id"] + 0.5) * dx, self.area.y + 34 + n["nivel"] * dy)
            self.radio = int(max(7, min(26, dx / 2 - 2)))

    def recorrer(self, tipo):
        """
        Anima un recorrido del árbol (inorden, preorden o posorden).

        Recibe:
            tipo: nombre del recorrido.
        Devuelve:
            Nada.
        """
        if not self.nodos:
            return
        self.resaltar = self.tabla.orden_recorrido(tipo)
        self.visibles = 0
        self.reloj = 0.0
        self.seleccion = None
        self.confirmar = False
        self.b_eliminar.habilitado = False
        self.mensaje = {
            "inorden": "INORDEN: izquierda → nodo → derecha. Sale de menor a mayor puntaje.",
            "preorden": "PREORDEN: nodo → izquierda → derecha. Así se guarda el archivo.",
            "posorden": "POSORDEN: izquierda → derecha → nodo. La raíz sale de última.",
        }[tipo]

    def seleccionar(self, nid):
        """
        Selecciona un nodo y anima la búsqueda desde la raíz hasta él.

        Recibe:
            nid: id del nodo.
        Devuelve:
            Nada.
        """
        n = self.por_id[nid]
        self.seleccion = nid
        self.confirmar = False
        self.b_eliminar.habilitado = True
        self.b_eliminar.etiqueta = "Eliminar seleccionado"
        self.resaltar = self.tabla.ids_camino_busqueda(n["clave"])
        self.visibles = 0
        self.reloj = 0.0
        pasos = []
        for i in self.resaltar:
            m = self.por_id[i]
            pasos.append(str(m["clave"]))
        self.mensaje = "Buscando %d: comparaciones %s  (%d paso%s)" % (
            n["clave"], " → ".join(pasos), len(pasos), "" if len(pasos) == 1 else "s")

    def eliminar(self):
        """Elimina el nodo seleccionado (pide confirmar con un segundo clic). Devuelve: nada."""
        if self.seleccion is None:
            return
        if not self.confirmar:
            self.confirmar = True
            self.b_eliminar.etiqueta = "¿Seguro? Haz clic otra vez"
            return
        n = self.por_id[self.seleccion]
        self.tabla.eliminar(n["clave"])
        self.seleccion, self.resaltar, self.visibles, self.confirmar = None, [], 0, False
        self.b_eliminar.habilitado = False
        self.b_eliminar.etiqueta = "Eliminar seleccionado"
        self.mensaje = "Puntaje eliminado del árbol."
        self._cargar()

    def evento(self, e):
        """Clics en nodos, botones y teclas. Recibe: e. Devuelve: nada."""
        if self._clics(e, self.botones):
            return
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for nid, (x, y) in self.pos.items():
                if math.hypot(e.pos[0] - x, e.pos[1] - y) <= self.radio + 4:
                    self.seleccionar(nid)
                    self.app.sonidos.reproducir("clic")
                    break
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                self.app.ir_a(Menu(self.app))
            elif e.key == pygame.K_DELETE:
                self.eliminar()

    def actualizar(self, dt):
        """Avanza la animación del recorrido. Recibe: dt. Devuelve: nada."""
        super().actualizar(dt)
        mouse = pygame.mouse.get_pos()
        for b in self.botones:
            b.actualizar(dt, mouse)
        if self.visibles < len(self.resaltar):
            self.reloj += dt
            while self.reloj >= 0.5 and self.visibles < len(self.resaltar):
                self.reloj -= 0.5
                self.visibles += 1
                self.app.sonidos.reproducir("paso")

    def dibujar(self, surf):
        """Pinta la lista y el árbol. Recibe: surf. Devuelve: nada."""
        self.app.fondo.dibujar(surf, self.t)
        texto(surf, "Mejores puntajes", 48, TEXTO, (40, 26), negrita=True)
        texto(surf, "Árbol binario de búsqueda: lo menor a la izquierda, lo mayor a la derecha", 17,
              APAGADO, (42, 88), sombra=False)

        # Lista
        lista = pygame.Rect(40, 130, 370, 480)
        panel(surf, lista, 215)
        if not self.mejores:
            texto(surf, "Aún no hay puntajes", 24, TEXTO, lista.center, "center", negrita=True)
            texto(surf, "Gana una partida para aparecer aquí", 16, APAGADO,
                  (lista.centerx, lista.centery + 34), "center", sombra=False)
        medallas = [ORO, (205, 210, 225), (205, 135, 80)]
        for i, (puntaje, nombre, nivel) in enumerate(self.mejores):
            y = lista.y + 16 + i * 46
            col = medallas[i] if i < 3 else (70, 64, 110)
            pygame.draw.circle(surf, col, (lista.x + 34, y + 20), 15)
            texto(surf, str(i + 1), 18, (20, 16, 40) if i < 3 else TEXTO, (lista.x + 34, y + 20),
                  "center", negrita=True, sombra=False)
            texto(surf, nombre, 21, TEXTO, (lista.x + 62, y + 4), negrita=True, sombra=False)
            texto(surf, nivel, 14, mezclar(APAGADO, COLOR_NIVEL.get(nivel, APAGADO), 0.6),
                  (lista.x + 62, y + 26), sombra=False)
            texto(surf, str(puntaje), 24, col if i < 3 else TEXTO, (lista.right - 20, y + 8), "topright",
                  negrita=True, sombra=False)

        # Árbol
        panel(surf, pygame.Rect(430, 130, 650, 440), 200)
        texto(surf, "ÁRBOL BST  ·  %d nodo%s" % (len(self.nodos), "" if len(self.nodos) == 1 else "s"),
              14, ORO, (448, 142), sombra=False, negrita=True)
        if not self.nodos:
            texto(surf, "El árbol está vacío", 22, APAGADO, self.area.center, "center", sombra=False)
        resaltados = {nid: k + 1 for k, nid in enumerate(self.resaltar[:self.visibles])}
        for n in self.nodos:                         # aristas
            for hijo in (n["izq"], n["der"]):
                if hijo is not None:
                    activa = n["id"] in resaltados and hijo in resaltados
                    pygame.draw.line(surf, ORO if activa else (90, 82, 140), self.pos[n["id"]],
                                     self.pos[hijo], 3 if activa else 2)
        for n in self.nodos:                         # nodos
            x, y = self.pos[n["id"]]
            en = n["id"] in resaltados
            base = ORO if n["nivel"] == 0 else MORADO
            if en:
                brillo(surf, (x, y), self.radio * 3, CIAN, 0.55)
            pygame.draw.circle(surf, mezclar((30, 26, 58), base, 0.75 if en else 0.45), (int(x), int(y)),
                               self.radio)
            pygame.draw.circle(surf, CIAN if en else mezclar(BORDE, base, 0.5), (int(x), int(y)),
                               self.radio, 3 if n["id"] == self.seleccion else 2)
            if self.radio >= 15:
                texto(surf, str(n["clave"]), 14 if self.radio < 22 else 16, TEXTO, (x, y), "center",
                      sombra=False, negrita=True)
            if en:
                texto(surf, str(resaltados[n["id"]]), 15, CIAN, (x, y - self.radio - 14), "center",
                      sombra=False, negrita=True)
        # Mensaje + detalle del nodo seleccionado
        texto(surf, self.mensaje, 16, TEXTO, (448, 536), sombra=False)
        if self.seleccion is not None:
            n = self.por_id[self.seleccion]
            texto(surf, "%s · %s · %d puntos" % (n["nombre"], n["nivel_juego"], n["clave"]), 18, ORO,
                  (448, 586), sombra=False, negrita=True)
        for b in self.botones:
            b.dibujar(surf)


# =====================================================================================
#  REGLAS
# =====================================================================================
class Reglas(Pantalla):
    """Cómo se juega, con los personajes dibujados como leyenda."""

    def __init__(self, app, volver):
        """Recibe: app y una función que devuelve la pantalla a la que se vuelve."""
        super().__init__(app)
        self.volver = volver
        self.boton = Boton("Volver", (ANCHO // 2 - 110, 636, 220, 50),
                           lambda: app.ir_a(volver()), "Esc", APAGADO, 24)

    def evento(self, e):
        """Esc, Enter o clic en el botón. Recibe: e. Devuelve: nada."""
        if self._clics(e, [self.boton]):
            return
        if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_F1):
            self.app.ir_a(self.volver())

    def actualizar(self, dt):
        """Anima el botón. Recibe: dt. Devuelve: nada."""
        super().actualizar(dt)
        self.boton.actualizar(dt, pygame.mouse.get_pos())

    def dibujar(self, surf):
        """Pinta las reglas. Recibe: surf. Devuelve: nada."""
        self.app.fondo.dibujar(surf, self.t)
        texto(surf, "Reglas y controles", 50, TEXTO, (ANCHO // 2, 30), "midtop", negrita=True)
        panel(surf, pygame.Rect(60, 110, 480, 500), 215)
        texto(surf, "OBJETIVO", 15, ORO, (86, 128), sombra=False, negrita=True)
        leyenda = [
            ("jugador", "Eres tú. Explora el refugio y cruza el Umbral para entrar al laberinto."),
            ("portal", "La salida del laberinto."),
            ("enemigo", "Espectro: patrulla una ruta y avanza cuando tú actúas. Si te alcanza, pierdes."),
        ]
        y = 164
        for icono, desc in leyenda:
            cx, cy = 110, y + 26
            if icono == "jugador":
                dibujar_jugador(surf, cx, cy, 52, self.t)
            elif icono == "portal":
                dibujar_portal(surf, cx, cy, 52, self.t)
            else:
                dibujar_enemigo(surf, cx, cy, 52, self.t)
            self._parrafo(surf, desc, 17, (160, y + 2), 360)
            y += 98
        reglas = ["Mover y deshacer gastan; chocar con paredes no.",
                  "Eco: copia tu camino; si te quedas quieto (Q) te alcanza. Radar rojo: si te toca, −5 mov.",
                  "Placa: vuelve en 2 s. Rueda: sal del carril. Rotor: salta al ver verde.",
                  "F / X derrota esqueletos de frente. Lo que sobre de movimientos da puntos."]
        for r in reglas:
            y = self._parrafo(surf, "•  " + r, 14, (86, y + 2), 430, APAGADO)

        panel(surf, pygame.Rect(560, 110, 480, 500), 215)
        texto(surf, "CONTROLES", 15, ORO, (586, 128), sombra=False, negrita=True)
        controles = [("W A S D  /  flechas", "Mover; también caminar por el campamento"),
                     ("E  /  Espacio", "Interactuar y cruzar el Umbral"),
                     ("U  /  Z  /  Retroceso", "Deshacer (Pila)"),
                     ("H", "Pista: camino más corto (BFS), −5 mov."),
                     ("L", "Cubrir / descubrir la antorcha"),
                     ("Espacio en el laberinto", "Saltar trampas y cuchillas"),
                     ("F  /  X", "Atacar al esqueleto que tienes delante"),
                     ("Q", "Esperar un turno: el eco se acerca"),
                     ("Esc  /  P", "Pausa"),
                     ("M  /  F11", "Sonido / pantalla completa")]
        for i, (tecla, desc) in enumerate(controles):
            yy = 164 + i * 42
            r = texto(surf, tecla, 17, CIAN, (586, yy), negrita=True, sombra=False)
            texto(surf, desc, 16, TEXTO, (586, yy + 21), sombra=False)
        self.boton.dibujar(surf)

    def _parrafo(self, surf, s, tam, pos, ancho, color=TEXTO):
        """
        (Interno) Escribe un texto largo cortándolo en líneas.

        Recibe:
            surf: superficie.
            s: texto.
            tam: tamaño de fuente.
            pos: esquina superior izquierda.
            ancho: ancho máximo en píxeles.
            color: color del texto.
        Devuelve:
            La coordenada y donde termina el párrafo.
        """
        from interfaz.tema import fuente
        f = fuente(tam)
        linea, y = "", pos[1]
        for palabra in s.split():
            prueba = (linea + " " + palabra).strip()
            if f.size(prueba)[0] > ancho and linea:
                texto(surf, linea, tam, color, (pos[0], y), sombra=False)
                y += tam + 6
                linea = palabra
            else:
                linea = prueba
        texto(surf, linea, tam, color, (pos[0], y), sombra=False)
        return y + tam + 10


# =====================================================================================
#  PANTALLA DE INVENTARIO Y CÓDICE OCULTO
# =====================================================================================
class PantallaInventario(Pantalla):
    """
    Pantalla interactiva de Inventario y Códice Oculto (accesible con I o Tab).
    - Panel Izquierdo: Silueta del Viajero y sus 3 ranuras equipadas (Arma, Armadura, Pasiva).
    - Panel Central: Cuadrícula por categorías (Armas, Armaduras, Habilidades) con contador
      "Colección: X / Y Descubiertos" y objetos ocultos en penumbra con candado y "???".
    - Panel Derecho: Ficha detallada del ítem seleccionado y botón "Equipar".
    """

    NOMBRES_CATEGORIA = {
        CATEGORIA_ARMA: "ARMAS",
        CATEGORIA_ARMADURA: "ARMADURAS",
        CATEGORIA_HABILIDAD: "HABILIDADES",
    }

    def __init__(self, app, volver=None):
        super().__init__(app)
        self.volver = volver or (lambda: Campamento(app))
        self.inventario = _obtener_inventario(app)
        self.particulas = Particulas()
        self.mensaje = ""
        self.mensaje_tiempo = 0.0
        self.coleccion = []
        self.casillas = []          # lista de (pygame.Rect, item_dict)
        self.ranuras_equipadas = [] # lista de (pygame.Rect, etiqueta_ranura, id_item)
        self.indice_sel = 0

        self.b_equipar = Boton("Equipar", (820, 554, 220, 46), self.equipar_seleccionado,
                               "Enter", ORO, 20)
        self.b_volver = Boton("Volver", (ANCHO // 2 - 110, 646, 220, 48), self.salir,
                              "Esc", APAGADO, 21)
        self._sincronizar_coleccion()

    def _esta_equipado(self, id_item):
        """Indica si `id_item` está equipado en alguna de las 3 ranuras del viajero."""
        inv = self.inventario
        return id_item in (
            getattr(inv, "arma_equipada", None),
            getattr(inv, "armadura_equipada", None),
            getattr(inv, "habilidad_equipada", None),
        )

    def _sincronizar_coleccion(self):
        """Construye la cuadrícula del códice agrupada en las 3 categorías y las 3 ranuras activas."""
        raw = self.inventario.obtener_coleccion()
        orden_cat = (CATEGORIA_ARMA, CATEGORIA_ARMADURA, CATEGORIA_HABILIDAD)
        agrupados = {cat: [] for cat in orden_cat}
        for item in raw:
            cat = item.get("categoria", CATEGORIA_ARMA)
            agrupados.setdefault(cat, []).append(item)

        self.coleccion = []
        self.casillas = []
        base_x = 330
        ancho_celda, alto_celda = 132, 92
        espacio_x = 14
        filas_y = (224, 356, 488)

        for fila_idx, cat in enumerate(orden_cat):
            items_cat = agrupados.get(cat, [])
            y = filas_y[fila_idx]
            for col_idx, item in enumerate(items_cat[:3]):
                x = base_x + col_idx * (ancho_celda + espacio_x)
                rect = pygame.Rect(x, y, ancho_celda, alto_celda)
                item_copia = dict(item)
                item_copia["equipado"] = self._esta_equipado(item_copia.get("id"))
                self.coleccion.append(item_copia)
                self.casillas.append((rect, item_copia))

        if self.coleccion:
            self.indice_sel = max(0, min(self.indice_sel, len(self.coleccion) - 1))

        inv = self.inventario
        definiciones_ranuras = [
            ("Arma", getattr(inv, "arma_equipada", "espada_ceniza")),
            ("Armadura", getattr(inv, "armadura_equipada", "manto_viajero")),
            ("Pasiva", getattr(inv, "habilidad_equipada", "paso_ligero")),
        ]
        self.ranuras_equipadas = []
        for i, (etiqueta, id_eq) in enumerate(definiciones_ranuras):
            rect_r = pygame.Rect(48, 366 + i * 78, 224, 66)
            self.ranuras_equipadas.append((rect_r, etiqueta, id_eq))

        self._actualizar_boton_equipar()

    def _item_seleccionado(self):
        """Retorna el diccionario del ítem actualmente seleccionado en el códice."""
        if not self.coleccion:
            return None
        return self.coleccion[self.indice_sel]

    def _actualizar_boton_equipar(self):
        """Actualiza el texto y estado habilitado del botón Equipar según el ítem seleccionado."""
        item = self._item_seleccionado()
        if item is None or not item.get("descubierto", False):
            self.b_equipar.etiqueta = "Bloqueado"
            self.b_equipar.habilitado = False
        elif self._esta_equipado(item.get("id")):
            self.b_equipar.etiqueta = "Equipado"
            self.b_equipar.habilitado = False
        else:
            self.b_equipar.etiqueta = "Equipar"
            self.b_equipar.habilitado = True

    def equipar_seleccionado(self):
        """Equipa el objeto seleccionado si ya fue descubierto."""
        item = self._item_seleccionado()
        if item is None or not item.get("descubierto", False):
            self.app.sonidos.reproducir("pared")
            return
        id_item = item.get("id")
        if self.inventario.equipar(id_item):
            self.app.sonidos.reproducir("guardar")
            self.mensaje = "¡Equipado: %s!" % item.get("nombre", "")
            self.mensaje_tiempo = 2.4
            self.particulas.emitir(930, 260, ORO, 20, 110, 0.85, 3)
            self.app.guardar_checkpoint(self.app.punto_guardado or (550.0, 596.0))
            self._sincronizar_coleccion()

    def salir(self):
        """Regresa a la pantalla previa (Juego o Campamento)."""
        self.app.ir_a(self.volver())

    def evento(self, e):
        """Maneja clics en la cuadrícula/ranuras, navegación por teclado y tecla Esc/I/Tab."""
        if self._clics(e, [self.b_equipar, self.b_volver]):
            return
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for idx, (rect, _) in enumerate(self.casillas):
                if rect.collidepoint(e.pos):
                    self.indice_sel = idx
                    self._actualizar_boton_equipar()
                    self.app.sonidos.reproducir("clic")
                    return
            for rect_r, _, id_eq in self.ranuras_equipadas:
                if rect_r.collidepoint(e.pos):
                    for idx, (_, it) in enumerate(self.casillas):
                        if it.get("id") == id_eq:
                            self.indice_sel = idx
                            self._actualizar_boton_equipar()
                            self.app.sonidos.reproducir("clic")
                            return
        elif e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_i, pygame.K_TAB, pygame.K_BACKSPACE):
                self.app.sonidos.reproducir("clic")
                self.salir()
            elif e.key in (pygame.K_RIGHT, pygame.K_d) and self.coleccion:
                self.indice_sel = (self.indice_sel + 1) % len(self.coleccion)
                self._actualizar_boton_equipar()
                self.app.sonidos.reproducir("clic")
            elif e.key in (pygame.K_LEFT, pygame.K_a) and self.coleccion:
                self.indice_sel = (self.indice_sel - 1) % len(self.coleccion)
                self._actualizar_boton_equipar()
                self.app.sonidos.reproducir("clic")
            elif e.key in (pygame.K_DOWN, pygame.K_s) and self.coleccion:
                self.indice_sel = (self.indice_sel + 3) % len(self.coleccion)
                self._actualizar_boton_equipar()
                self.app.sonidos.reproducir("clic")
            elif e.key in (pygame.K_UP, pygame.K_w) and self.coleccion:
                self.indice_sel = (self.indice_sel - 3) % len(self.coleccion)
                self._actualizar_boton_equipar()
                self.app.sonidos.reproducir("clic")
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_e):
                if self.b_equipar.habilitado:
                    self.equipar_seleccionado()

    def actualizar(self, dt):
        """Actualiza animaciones, partículas y botones del inventario."""
        super().actualizar(dt)
        mouse = pygame.mouse.get_pos()
        self.b_equipar.actualizar(dt, mouse)
        self.b_volver.actualizar(dt, mouse)
        self.particulas.actualizar(dt)
        if self.mensaje_tiempo > 0:
            self.mensaje_tiempo = max(0.0, self.mensaje_tiempo - dt)

    def dibujar(self, surf):
        """Dibuja los tres paneles del Inventario y Códice Oculto."""
        self.app.fondo.dibujar(surf, self.t)

        # Cabecera principal
        texto(surf, "INVENTARIO Y CÓDICE OCULTO", 38, ORO, (ANCHO // 2, 26),
              "midtop", negrita=True)
        texto(surf, "Equipa tus reliquias y descubre los artefactos ocultos en los cofres del laberinto",
              16, APAGADO, (ANCHO // 2, 72), "midtop", sombra=False)

        # -----------------------------------------------------------------
        # 1. PANEL IZQUIERDO: Silueta del Viajero + 3 Ranuras Equipadas
        # -----------------------------------------------------------------
        p_izq = pygame.Rect(30, 108, 260, 520)
        panel(surf, p_izq, 232, mezclar(BORDE, ORO, 0.35))
        remaches(surf, p_izq, BORDE, 8)
        texto(surf, "EL VIAJERO", 20, ORO, (p_izq.centerx, p_izq.y + 18), "midtop", negrita=True)
        separador(surf, p_izq.x + 18, p_izq.right - 18, p_izq.y + 48, BORDE)

        # Pedestal y silueta animada del Viajero
        pedestal = pygame.Rect(p_izq.x + 36, p_izq.y + 62, p_izq.w - 72, 168)
        pygame.draw.rect(surf, (14, 16, 13), pedestal, border_radius=8)
        pygame.draw.rect(surf, (78, 72, 48), pedestal, 2, border_radius=8)
        brillo(surf, pedestal.center, 76, ORO, 0.22 + 0.05 * math.sin(self.t * 3.0))
        dibujar_jugador(surf, pedestal.centerx, pedestal.centery + 18, 92, self.t,
                        antorcha=True, direccion="abajo", andando=False)

        oro_total = getattr(self.inventario, "oro", 0)
        texto(surf, "Oro acumulado: %d" % oro_total, 14, ORO,
              (p_izq.centerx, pedestal.bottom + 10), "midtop", negrita=True, sombra=False)

        # 3 Ranuras equipadas (Arma, Armadura, Pasiva)
        for rect_r, etiqueta_ranura, id_eq in self.ranuras_equipadas:
            datos_eq = CATALOGO_OBJETOS.get(id_eq, {})
            nombre_eq = datos_eq.get("nombre", "Sin equipar")
            icono_eq = datos_eq.get("icono", "espada")
            rareza_eq = datos_eq.get("rareza", "Común")
            col_rar = COLORES_RAREZA.get(rareza_eq, ORO)

            pygame.draw.rect(surf, (24, 26, 20), rect_r, border_radius=6)
            pygame.draw.rect(surf, mezclar(BORDE, col_rar, 0.55), rect_r, 2, border_radius=6)
            ico_box = pygame.Rect(rect_r.x + 8, rect_r.y + 8, 50, 50)
            pygame.draw.rect(surf, (16, 18, 14), ico_box, border_radius=5)
            dibujar_icono_item(surf, ico_box, icono_eq, descubierto=True, color_acento=col_rar)
            texto(surf, etiqueta_ranura.upper(), 12, APAGADO,
                  (ico_box.right + 12, rect_r.y + 12), sombra=False, negrita=True)
            texto_ajustado(surf, nombre_eq, 15, TEXTO,
                           (ico_box.right + 12, rect_r.y + 32), rect_r.w - 78, negrita=True)

        # -----------------------------------------------------------------
        # 2. PANEL CENTRAL: Cuadrícula de Categorías y Avance del Códice
        # -----------------------------------------------------------------
        p_cen = pygame.Rect(306, 108, 468, 520)
        panel(surf, p_cen, 232, mezclar(BORDE, CIAN, 0.35))
        remaches(surf, p_cen, BORDE, 8)
        texto(surf, "CÓDICE DE ARTEFACTOS", 20, CIAN, (p_cen.x + 24, p_cen.y + 18), negrita=True)

        total_items = len(self.coleccion)
        descubiertos = sum(1 for it in self.coleccion if it.get("descubierto", False))
        avance_txt = "Colección: %d / %d Descubiertos" % (descubiertos, total_items)
        texto(surf, avance_txt, 15, ORO, (p_cen.x + 24, p_cen.y + 48), negrita=True, sombra=False)

        # Barra de progreso de colección
        barra_prog = pygame.Rect(p_cen.x + 24, p_cen.y + 72, p_cen.w - 48, 10)
        pygame.draw.rect(surf, (14, 15, 11), barra_prog, border_radius=5)
        if total_items > 0 and descubiertos > 0:
            ancho_p = max(8, int(barra_prog.w * (descubiertos / total_items)))
            pygame.draw.rect(surf, ORO, (barra_prog.x, barra_prog.y, ancho_p, barra_prog.h),
                             border_radius=5)
        pygame.draw.rect(surf, BORDE, barra_prog, 1, border_radius=5)

        # Encabezados de las 3 categorías y dibujo de cada ranura
        etiquetas_filas = [
            ("ARMAS", 198),
            ("ARMADURAS", 330),
            ("HABILIDADES PASIVAS", 462),
        ]
        for titulo_cat, y_cat in etiquetas_filas:
            texto(surf, titulo_cat, 13, APAGADO, (330, y_cat), negrita=True, sombra=False)
            pygame.draw.line(surf, (62, 58, 42), (330, y_cat + 18), (750, y_cat + 18), 1)

        for idx, (rect_c, item) in enumerate(self.casillas):
            dibujar_ranura_item(
                surf,
                rect_c,
                item,
                seleccionado=(idx == self.indice_sel),
                equipado=self._esta_equipado(item.get("id")),
            )

        # -----------------------------------------------------------------
        # 3. PANEL DERECHO: Ficha del Ítem Seleccionado
        # -----------------------------------------------------------------
        p_der = pygame.Rect(790, 108, 280, 520)
        panel(surf, p_der, 232, mezclar(BORDE, ORO, 0.45))
        remaches(surf, p_der, BORDE, 8)
        texto(surf, "FICHA DE OBJETO", 20, ORO, (p_der.centerx, p_der.y + 18),
              "midtop", negrita=True)
        separador(surf, p_der.x + 18, p_der.right - 18, p_der.y + 48, BORDE)

        item_sel = self._item_seleccionado()
        if item_sel is not None:
            desc = bool(item_sel.get("descubierto", False))
            rareza = item_sel.get("rareza", "Común")
            col_rar = COLORES_RAREZA.get(rareza, ORO) if desc else (110, 104, 84)

            marco_ico = pygame.Rect(p_der.centerx - 54, p_der.y + 66, 108, 108)
            pygame.draw.rect(surf, (16, 18, 14), marco_ico, border_radius=8)
            pygame.draw.rect(surf, col_rar, marco_ico, 2, border_radius=8)
            dibujar_icono_item(surf, marco_ico.inflate(-16, -16),
                               item_sel.get("icono", "incognita"),
                               descubierto=desc, color_acento=col_rar)

            if desc:
                nombre_mostrar = item_sel.get("nombre", "Artefacto")
                cat_clave = item_sel.get("categoria", CATEGORIA_ARMA)
                cat_txt = self.NOMBRES_CATEGORIA.get(cat_clave, "ARTEFACTO")
                texto_ajustado(surf, nombre_mostrar, 22, TEXTO,
                               (p_der.centerx, marco_ico.bottom + 20), p_der.w - 28,
                               "midtop", negrita=True)
                texto(surf, "%s  ·  Rareza %s" % (cat_txt, rareza), 13, col_rar,
                      (p_der.centerx, marco_ico.bottom + 50), "midtop", negrita=True, sombra=False)
                separador(surf, p_der.x + 22, p_der.right - 22, marco_ico.bottom + 76, BORDE)
                lore = item_sel.get("descripcion", "")
                self._dibujar_parrafo(surf, lore, 15,
                                      (p_der.x + 22, marco_ico.bottom + 92),
                                      p_der.w - 44, TEXTO)
            else:
                texto(surf, "???", 26, (140, 132, 108),
                      (p_der.centerx, marco_ico.bottom + 20), "midtop", negrita=True)
                texto(surf, "CÓDICE OCULTO", 13, APAGADO,
                      (p_der.centerx, marco_ico.bottom + 52), "midtop", negrita=True, sombra=False)
                separador(surf, p_der.x + 22, p_der.right - 22, marco_ico.bottom + 76, BORDE)
                msg_oculto = (
                    "Artefacto desconocido. Abre cofres en el laberinto para descubrirlo."
                )
                self._dibujar_parrafo(surf, msg_oculto, 15,
                                      (p_der.x + 22, marco_ico.bottom + 92),
                                      p_der.w - 44, APAGADO)

        self.b_equipar.dibujar(surf)
        self.b_volver.dibujar(surf)
        self.particulas.dibujar(surf)

        if self.mensaje_tiempo > 0 and self.mensaje:
            texto(surf, self.mensaje, 15, VERDE, (p_der.centerx, p_der.bottom - 88),
                  "midtop", negrita=True)

    @staticmethod
    def _dibujar_parrafo(surf, s, tam, pos, ancho, color=TEXTO):
        """Renderiza un párrafo multi-línea ajustado al ancho del panel."""
        f = fuente(tam)
        linea, y = "", pos[1]
        for palabra in s.split():
            prueba = (linea + " " + palabra).strip()
            if f.size(prueba)[0] > ancho and linea:
                texto(surf, linea, tam, color, (pos[0], y), sombra=False)
                y += tam + 6
                linea = palabra
            else:
                linea = prueba
        if linea:
            texto(surf, linea, tam, color, (pos[0], y), sombra=False)
        return y + tam + 8

