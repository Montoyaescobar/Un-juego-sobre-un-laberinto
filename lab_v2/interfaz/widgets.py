"""
widgets.py
Piezas reutilizables de la interfaz: botón, campo de texto e iconos dibujados con código.
"""

import pygame

from interfaz.tema import (TEXTO, MORADO, ROJO, ORO, texto, mezclar, fuente)


# ------------------------------------------------------------------ iconos
def icono_play(surf, rect, color):
    """Dibuja un triángulo de 'reproducir'. Recibe: surf, rect, color. Devuelve: nada."""
    x, y, w, h = rect
    pygame.draw.polygon(surf, color, [(x + w * 0.25, y + h * 0.15), (x + w * 0.25, y + h * 0.85),
                                      (x + w * 0.85, y + h * 0.5)])


def icono_pausa(surf, rect, color):
    """Dibuja dos barras de 'pausa'. Recibe: surf, rect, color. Devuelve: nada."""
    x, y, w, h = rect
    pygame.draw.rect(surf, color, (x + w * 0.22, y + h * 0.15, w * 0.2, h * 0.7), border_radius=2)
    pygame.draw.rect(surf, color, (x + w * 0.58, y + h * 0.15, w * 0.2, h * 0.7), border_radius=2)


def icono_atras(surf, rect, color):
    """Dibuja un triángulo hacia la izquierda. Recibe: surf, rect, color. Devuelve: nada."""
    x, y, w, h = rect
    pygame.draw.polygon(surf, color, [(x + w * 0.75, y + h * 0.15), (x + w * 0.75, y + h * 0.85),
                                      (x + w * 0.2, y + h * 0.5)])


def icono_inicio(surf, rect, color):
    """Dibuja |◀ (ir al inicio). Recibe: surf, rect, color. Devuelve: nada."""
    x, y, w, h = rect
    pygame.draw.rect(surf, color, (x + w * 0.15, y + h * 0.15, w * 0.12, h * 0.7))
    pygame.draw.polygon(surf, color, [(x + w * 0.85, y + h * 0.15), (x + w * 0.85, y + h * 0.85),
                                      (x + w * 0.3, y + h * 0.5)])


def icono_final(surf, rect, color):
    """Dibuja ▶| (ir al final). Recibe: surf, rect, color. Devuelve: nada."""
    x, y, w, h = rect
    pygame.draw.polygon(surf, color, [(x + w * 0.15, y + h * 0.15), (x + w * 0.15, y + h * 0.85),
                                      (x + w * 0.7, y + h * 0.5)])
    pygame.draw.rect(surf, color, (x + w * 0.73, y + h * 0.15, w * 0.12, h * 0.7))


# ------------------------------------------------------------------ botón
class Boton:
    """Botón redondeado con efecto al pasar el mouse."""

    def __init__(self, etiqueta, rect, accion, tecla="", color=MORADO, tam=24,
                 habilitado=True, icono=None):
        """
        Crea un botón.

        Recibe:
            etiqueta: texto del botón.
            rect: pygame.Rect (o tupla x, y, ancho, alto).
            accion: función sin argumentos que se llama al hacer clic.
            tecla: texto corto de la tecla rápida (solo se muestra, ej. "H").
            color: color de acento.
            tam: tamaño del texto.
            habilitado: si es False se ve apagado y no responde.
            icono: función de icono (ver arriba) o None.
        Devuelve:
            Nada (constructor).
        """
        self.etiqueta = etiqueta
        self.rect = pygame.Rect(rect)
        self.accion = accion
        self.tecla = tecla
        self.color = color
        self.tam = tam
        self.habilitado = habilitado
        self.icono = icono
        self.h = 0.0          # 0 = normal, 1 = con el mouse encima (animado)

    def actualizar(self, dt, mouse):
        """
        Anima el efecto de hover.

        Recibe:
            dt: segundos desde el cuadro anterior.
            mouse: posición (x, y) del mouse.
        Devuelve:
            Nada.
        """
        objetivo = 1.0 if (self.habilitado and self.rect.collidepoint(mouse)) else 0.0
        self.h += (objetivo - self.h) * min(1.0, dt * 14)

    def clic(self, pos):
        """
        Procesa un clic.

        Recibe:
            pos: posición (x, y) del clic.
        Devuelve:
            True si el clic fue en este botón (y estaba habilitado) y se ejecutó la acción.
        """
        if self.habilitado and self.rect.collidepoint(pos):
            self.accion()
            return True
        return False

    def dibujar(self, surf):
        """Dibuja el botón. Recibe: surf. Devuelve: nada."""
        h = self.h
        r = self.rect.inflate(int(h * 8), int(h * 4))
        if self.habilitado:
            base = mezclar((38, 32, 24), self.color, 0.16 + 0.30 * h)
            borde = mezclar(mezclar((96, 82, 54), self.color, 0.5), (255, 255, 255), 0.35 * h)
            color_texto = TEXTO
        else:
            base, borde, color_texto = (30, 28, 22), (58, 53, 40), (110, 105, 84)
        sombra = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        pygame.draw.rect(sombra, (0, 0, 0, 135), sombra.get_rect(), border_radius=5)
        surf.blit(sombra, (r.x + 3, r.y + 4))
        pygame.draw.rect(surf, base, r, border_radius=5)
        pygame.draw.rect(surf, borde, r, width=2, border_radius=5)
        pygame.draw.line(surf, mezclar(base, (231, 214, 157), 0.20),
                         (r.x + 7, r.y + 3), (r.right - 7, r.y + 3), 1)
        if self.habilitado:
            pygame.draw.rect(surf, self.color, (r.x + 7, r.y + 8, 3, r.h - 16))
            for yy in (r.y + 8, r.bottom - 9):
                pygame.draw.rect(surf, mezclar(self.color, (239, 218, 162), 0.28),
                                 (r.right - 10, yy, 3, 3))

        x_texto = r.centerx
        if self.icono is not None:
            lado = int(r.h * 0.5)
            self.icono(surf, pygame.Rect(r.x + 24, r.centery - lado // 2, lado, lado), color_texto)
            x_texto += 14
        texto(surf, self.etiqueta, self.tam, color_texto, (x_texto, r.centery), "center",
              negrita=True, sombra=False)
        if self.tecla:
            chip = fuente(14, True).render(self.tecla, True, (196, 189, 160) if self.habilitado
                                           else (96, 92, 74))
            ancho_texto = fuente(self.tam, True).size(self.etiqueta)[0]
            if (r.w - ancho_texto) / 2 - (14 if self.icono else 0) > chip.get_width() + 30:
                surf.blit(chip, chip.get_rect(midright=(r.right - 14, r.centery)))   # solo si cabe


# ------------------------------------------------------------------ campo de texto
class CampoTexto:
    """Campo para escribir el nombre (1 a 15 caracteres, sin ';')."""

    def __init__(self, rect, max_len=15):
        """
        Crea el campo.

        Recibe:
            rect: pygame.Rect del campo.
            max_len: máximo de caracteres.
        Devuelve:
            Nada (constructor).
        """
        self.rect = pygame.Rect(rect)
        self.max_len = max_len
        self.texto = ""
        self.error = ""

    def evento(self, e):
        """
        Procesa una tecla.

        Recibe:
            e: evento de pygame.
        Devuelve:
            "enter" si se presionó Enter; None en cualquier otro caso.
        """
        if e.type != pygame.KEYDOWN:
            return None
        if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return "enter"
        if e.key == pygame.K_BACKSPACE:
            self.texto = self.texto[:-1]
            self.error = ""
        elif e.unicode and e.unicode.isprintable():
            if e.unicode == ";":
                self.error = "El símbolo ; no se puede usar."
            elif len(self.texto) >= self.max_len:
                self.error = "Máximo %d caracteres." % self.max_len
            else:
                self.texto += e.unicode
                self.error = ""
        return None

    def valido(self):
        """Dice si el nombre sirve. Recibe: nada. Devuelve: True si tiene 1 a 15 caracteres."""
        return 1 <= len(self.texto.strip()) <= self.max_len

    def dibujar(self, surf, t):
        """
        Dibuja el campo con cursor parpadeante.

        Recibe:
            surf: superficie.
            t: tiempo en segundos (parpadeo).
        Devuelve:
            Nada.
        """
        pygame.draw.rect(surf, (13, 15, 10), self.rect, border_radius=4)
        pygame.draw.rect(surf, ORO if not self.error else ROJO, self.rect, width=2, border_radius=4)
        cursor = "|" if int(t * 2) % 2 == 0 else " "
        if self.texto:
            texto(surf, self.texto + cursor, 28, TEXTO, (self.rect.x + 14, self.rect.centery),
                  "midleft", sombra=False)
        else:
            texto(surf, "Escribe tu nombre" + cursor, 24, (128, 120, 96),
                  (self.rect.x + 14, self.rect.centery), "midleft", sombra=False)
        if self.error:
            texto(surf, self.error, 16, ROJO, (self.rect.x + 4, self.rect.bottom + 6), sombra=False)
