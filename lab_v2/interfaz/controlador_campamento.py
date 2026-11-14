"""
controlador_campamento.py
Controlador de movimiento y físicas con deslizamiento (wall sliding) para el Campamento.
"""

import math
import pygame

from interfaz.tema import ANCHO, ALTO

try:
    from interfaz.colisiones_campamento import (
        obtener_bloqueos_campamento,
        obtener_limites_campamento,
        es_posicion_valida,
    )
except ImportError:
    # Fallback defensivo mientras Agente 1 finaliza su módulo
    def obtener_limites_campamento() -> tuple[int, int, int, int]:
        """
        Devuelve los límites transitables del claro del campamento:
        (min_x, min_y, max_x, max_y).
        """
        return (26, 148, ANCHO - 26, ALTO - 28)

    def obtener_bloqueos_campamento(porton_rect: pygame.Rect = None) -> list[pygame.Rect]:
        """
        Devuelve las cajas de colisión ajustadas a los objetos visibles del campamento.
        """
        porton = porton_rect or pygame.Rect(444, 86, 212, 194)
        bloqueo_porton = pygame.Rect(porton.x + 12, porton.y, porton.w - 24, porton.h - 8)
        return [
            bloqueo_porton,
            pygame.Rect(114, 478, 126, 84),   # Carpa izquierda
            pygame.Rect(868, 424, 116, 82),   # Carpa derecha
            pygame.Rect(832, 536, 136, 62),   # Suministros y mesa del mapa
            pygame.Rect(518, 458, 64, 42),    # Hoguera central (ajustada al fuego real)
            pygame.Rect(192, 326, 146, 32),   # Hamaca
            pygame.Rect(356, 430, 28, 26),    # Mara
            pygame.Rect(721, 513, 28, 26),    # Ivo
            pygame.Rect(78, 568, 126, 44),    # Carro de carga
            pygame.Rect(288, 545, 28, 26),    # Nela
            pygame.Rect(789, 350, 28, 26),    # Tizón
        ]

    def es_posicion_valida(
        caja: pygame.Rect,
        bloqueos: list[pygame.Rect],
        limites: tuple[int, int, int, int],
    ) -> bool:
        """
        Verifica si una caja colisiona con algún bloqueo o sale de los límites.
        """
        min_x, min_y, max_x, max_y = limites
        if caja.left < min_x or caja.right > max_x or caja.top < min_y or caja.bottom > max_y:
            return False
        return not any(caja.colliderect(r) for r in bloqueos)


class ControladorCampamento:
    """
    Gestiona la entrada de teclado, la normalización de velocidad y las físicas
    con deslizamiento en muros (wall sliding) del personaje en el campamento.
    """

    VELOCIDAD_BASE = 190.0
    ANCHO_HITBOX = 18
    ALTO_HITBOX = 16

    TECLAS_ARRIBA = (pygame.K_UP, pygame.K_w)
    TECLAS_ABAJO = (pygame.K_DOWN, pygame.K_s)
    TECLAS_IZQUIERDA = (pygame.K_LEFT, pygame.K_a)
    TECLAS_DERECHA = (pygame.K_RIGHT, pygame.K_d)
    TECLAS_MOVIMIENTO = frozenset(
        TECLAS_ARRIBA + TECLAS_ABAJO + TECLAS_IZQUIERDA + TECLAS_DERECHA
    )

    def __init__(
        self,
        posicion=(550.0, 596.0),
        velocidad: float = VELOCIDAD_BASE,
        limites: tuple[int, int, int, int] = None,
        bloqueos: list[pygame.Rect] = None,
    ):
        """
        Inicializa el controlador del personaje en el campamento.

        Recibe:
            posicion: tupla o lista (x, y) inicial del personaje.
            velocidad: rapidez de desplazamiento en píxeles por segundo.
            limites: tupla (min_x, min_y, max_x, max_y) del escenario.
            bloqueos: lista de pygame.Rect con los obstáculos del escenario.
        """
        self.posicion = [float(posicion[0]), float(posicion[1])]
        self.velocidad = float(velocidad)
        self.limites = limites if limites is not None else obtener_limites_campamento()
        self.bloqueos = list(bloqueos) if bloqueos is not None else obtener_bloqueos_campamento()
        self.teclas: set[int] = set()
        self.direccion = "abajo"
        self.andando = False

    def evento(self, e) -> None:
        """
        Procesa un evento de Pygame para actualizar el estado de teclas de movimiento.
        Limpia las teclas retenidas si la ventana pierde el foco.
        """
        if e.type == pygame.KEYDOWN:
            if e.key in self.TECLAS_MOVIMIENTO:
                self.teclas.add(e.key)
        elif e.type == pygame.KEYUP:
            self.teclas.discard(e.key)
        elif e.type in (
            getattr(pygame, "WINDOWFOCUSLOST", -1),
            getattr(pygame, "WINDOWHIDDEN", -1),
            getattr(pygame, "WINDOWMINIMIZED", -1),
        ):
            self.limpiar_teclas()
        elif e.type == getattr(pygame, "ACTIVEEVENT", -1) and getattr(e, "gain", 1) == 0:
            self.limpiar_teclas()

    procesar_evento = evento

    def limpiar_teclas(self) -> None:
        """Limpia todas las teclas activas y detiene el estado de marcha."""
        self.teclas.clear()
        self.andando = False

    def obtener_caja(self, x: float = None, y: float = None) -> pygame.Rect:
        """
        Devuelve la hitbox del personaje centrada en (x, y) con redondeo subpíxel suave.
        """
        px = self.posicion[0] if x is None else float(x)
        py = self.posicion[1] if y is None else float(y)
        return pygame.Rect(
            int(round(px - self.ANCHO_HITBOX / 2)),
            int(round(py - self.ALTO_HITBOX / 2)),
            self.ANCHO_HITBOX,
            self.ALTO_HITBOX,
        )

    caja_colision = obtener_caja

    def _teclas_activas(self, estado_teclas=None) -> set[int]:
        """
        Obtiene el conjunto de teclas de movimiento activas combinando eventos
        registrados y, si se provee o la ventana tiene foco activo, el estado de teclado.
        """
        if estado_teclas is not None:
            if isinstance(estado_teclas, (set, frozenset, dict)):
                return {k for k in self.TECLAS_MOVIMIENTO if k in estado_teclas}
            return {k for k in self.TECLAS_MOVIMIENTO if estado_teclas[k]}

        if self.teclas:
            return self.teclas

        if pygame.display.get_init() and pygame.key.get_focused():
            pulsadas = pygame.key.get_pressed()
            return {k for k in self.TECLAS_MOVIMIENTO if pulsadas[k]}

        return self.teclas

    def vector_entrada(self, estado_teclas=None) -> tuple[int, int]:
        """
        Calcula la intención direccional discreta (dx, dy) en {-1, 0, 1}.
        Teclas opuestas presionadas al mismo tiempo se anulan mutuamente.
        """
        activas = self._teclas_activas(estado_teclas)
        dx = int(any(k in activas for k in self.TECLAS_DERECHA)) - int(
            any(k in activas for k in self.TECLAS_IZQUIERDA)
        )
        dy = int(any(k in activas for k in self.TECLAS_ABAJO)) - int(
            any(k in activas for k in self.TECLAS_ARRIBA)
        )
        return dx, dy

    def vector_velocidad(self, estado_teclas=None) -> tuple[float, float]:
        """
        Devuelve el vector de velocidad (vx, vy) normalizado para mantener
        rapidez uniforme tanto en movimiento cardinal como en diagonal.
        """
        dx, dy = self.vector_entrada(estado_teclas)
        if dx == 0 and dy == 0:
            return 0.0, 0.0
        norma = math.hypot(dx, dy)
        return (dx / norma) * self.velocidad, (dy / norma) * self.velocidad

    @staticmethod
    def calcular_direccion(dx: int, dy: int, direccion_actual: str = "abajo") -> str:
        """
        Determina la dirección cardinal del sprite a partir del vector (dx, dy).
        """
        if dx == 0 and dy == 0:
            return direccion_actual
        if dy < 0 and abs(dy) >= abs(dx):
            return "arriba"
        if dy > 0 and abs(dy) >= abs(dx):
            return "abajo"
        if dx < 0:
            return "izquierda"
        return "derecha"

    def _es_valida(
        self,
        nx: float,
        ny: float,
        caja: pygame.Rect,
        bloqueos: list[pygame.Rect],
        limites: tuple[int, int, int, int],
    ) -> bool:
        """
        Evalúa si la coordenada candidata y su hitbox respetan los límites y bloqueos.
        """
        min_x, min_y, max_x, max_y = limites
        if not (min_x <= nx <= max_x and min_y <= ny <= max_y):
            return False
        return es_posicion_valida(caja, bloqueos, limites)

    def actualizar(
        self,
        dt: float,
        bloqueos: list[pygame.Rect] = None,
        limites: tuple[int, int, int, int] = None,
        bloqueado: bool = False,
        estado_teclas=None,
    ) -> tuple[list[float], str, bool]:
        """
        Actualiza la posición del personaje aplicando normalización diagonal y
        deslizamiento independiente por eje (Wall Sliding).

        Recibe:
            dt: delta de tiempo en segundos.
            bloqueos: lista opcional de pygame.Rect de colisión.
            limites: tupla opcional (min_x, min_y, max_x, max_y).
            bloqueado: si es True (ej. abriendo el Umbral), impide moverse.
            estado_teclas: conjunto o secuencia opcional de teclas presionadas.
        Devuelve:
            Tupla (posicion, direccion, andando).
        """
        if bloqueado:
            self.andando = False
            return self.posicion, self.direccion, self.andando

        dx, dy = self.vector_entrada(estado_teclas)
        self.andando = bool(dx or dy)
        if not self.andando or dt <= 0.0:
            return self.posicion, self.direccion, self.andando

        self.direccion = self.calcular_direccion(dx, dy, self.direccion)
        norma = math.hypot(dx, dy)
        paso_x = (dx / norma) * self.velocidad * dt
        paso_y = (dy / norma) * self.velocidad * dt

        bloqueos_activos = self.bloqueos if bloqueos is None else bloqueos
        limites_activos = self.limites if limites is None else limites

        # Eje X: evaluar desplazamiento horizontal de forma independiente
        if paso_x != 0.0:
            nx = self.posicion[0] + paso_x
            caja_x = self.obtener_caja(nx, self.posicion[1])
            if self._es_valida(nx, self.posicion[1], caja_x, bloqueos_activos, limites_activos):
                self.posicion[0] = nx

        # Eje Y: evaluar desplazamiento vertical conservando el nuevo valor de X
        if paso_y != 0.0:
            ny = self.posicion[1] + paso_y
            caja_y = self.obtener_caja(self.posicion[0], ny)
            if self._es_valida(self.posicion[0], ny, caja_y, bloqueos_activos, limites_activos):
                self.posicion[1] = ny

        return self.posicion, self.direccion, self.andando
