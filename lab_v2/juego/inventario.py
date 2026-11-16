"""
inventario.py
Códice Oculto de ítems (armas, armaduras, habilidades) e Inventario con persistencia.

Los ítems no descubiertos aparecen como "???" en la colección. El estado se serializa
a un diccionario compatible con JSON (to_dict / from_dict) para checkpoint.json.
"""

import random

DESCRIPCION_INCOGNITA = ("Objeto desconocido. Explora los ramales del laberinto y "
                         "abre cofres para revelarlo.")
ORO_BOLSA = 60

ARMA = CATEGORIA_ARMA = "arma"
ARMADURA = CATEGORIA_ARMADURA = "armadura"
HABILIDAD = CATEGORIA_HABILIDAD = "habilidad"

CATALOGO_OBJETOS = {
    # ---- Armas ----
    "espada_ceniza": {"categoria": ARMA, "nombre": "Espada de Ceniza",
                      "descripcion": "Hoja forjada con brasas apagadas. Fiel compañera del viajero.",
                      "icono": "espada", "inicial": True, "rareza": "Común"},
    "daga_sombras": {"categoria": ARMA, "nombre": "Daga de Sombras",
                     "descripcion": "Ligera y silenciosa; se funde con la penumbra del laberinto.",
                     "icono": "daga", "inicial": False, "rareza": "Rara"},
    "baston_centella": {"categoria": ARMA, "nombre": "Bastón de Centella",
                        "descripcion": "Vara tallada que chispea al contacto con la magia antigua.",
                        "icono": "baston", "inicial": False, "rareza": "Épica"},
    # ---- Armaduras ----
    "manto_viajero": {"categoria": ARMADURA, "nombre": "Manto de Viajero",
                      "descripcion": "Capa gastada por mil caminos; protege del frío y poco más.",
                      "icono": "tunica", "inicial": True, "rareza": "Común"},
    "coraza_guardian": {"categoria": ARMADURA, "nombre": "Coraza del Guardián",
                        "descripcion": "Placas pesadas que un viejo guardián dejó atrás.",
                        "icono": "coraza", "inicial": False, "rareza": "Rara"},
    "manto_bruma": {"categoria": ARMADURA, "nombre": "Manto de Bruma",
                    "descripcion": "Tejido de niebla que dificulta ser visto.",
                    "icono": "manto", "inicial": False, "rareza": "Épica"},
    # ---- Habilidades ----
    "paso_ligero": {"categoria": HABILIDAD, "nombre": "Paso Ligero",
                    "descripcion": "Tus pies apenas rozan el suelo del laberinto.",
                    "icono": "bota", "inicial": True, "rareza": "Común"},
    "ojo_zahori": {"categoria": HABILIDAD, "nombre": "Ojo Zahorí",
                    "descripcion": "Percibe lo oculto entre los muros.",
                    "icono": "ojo", "inicial": False, "rareza": "Rara"},
    "escudo_eco": {"categoria": HABILIDAD, "nombre": "Escudo de Eco",
                    "descripcion": "Un resonar protector que desvía el peligro.",
                    "icono": "escudo", "inicial": False, "rareza": "Épica"},
}

_RANURA = {ARMA: "arma_equipada", ARMADURA: "armadura_equipada",
           HABILIDAD: "habilidad_equipada"}


def _inicial_de(categoria):
    """(Interno) Id del ítem inicial de una categoría."""
    for id_item, datos in CATALOGO_OBJETOS.items():
        if datos["categoria"] == categoria and datos["inicial"]:
            return id_item
    return None


class Inventario:
    """Ítems descubiertos, equipo actual, oro y estrellas acumuladas."""

    def __init__(self, datos_guardados=None):
        """
        Recibe:
            datos_guardados: diccionario de to_dict() (opcional). Si es None, estado inicial.
        """
        self.desbloqueados = {i for i, d in CATALOGO_OBJETOS.items() if d["inicial"]}
        self.arma_equipada = _inicial_de(ARMA)
        self.armadura_equipada = _inicial_de(ARMADURA)
        self.habilidad_equipada = _inicial_de(HABILIDAD)
        self.oro = 0
        self.estrellas_totales = 0
        if datos_guardados:
            self._cargar(datos_guardados)

    def _cargar(self, datos):
        """(Interno) Aplica un diccionario guardado ignorando datos inválidos."""
        for id_item in datos.get("desbloqueados", []):
            if id_item in CATALOGO_OBJETOS:
                self.desbloqueados.add(id_item)
        for ranura in _RANURA.values():
            valor = datos.get(ranura)
            if valor in self.desbloqueados and CATALOGO_OBJETOS[valor]["categoria"] == \
                    [c for c, r in _RANURA.items() if r == ranura][0]:
                setattr(self, ranura, valor)
        self.oro = max(0, int(datos.get("oro", 0)))
        self.estrellas_totales = max(0, int(datos.get("estrellas_totales", 0)))

    def obtener_coleccion(self):
        """
        Devuelve la lista de todos los ítems del catálogo; los no descubiertos van
        enmascarados (nombre "???", icono "incognita", descubierto False).
        """
        coleccion = []
        for id_item, datos in CATALOGO_OBJETOS.items():
            if id_item in self.desbloqueados:
                coleccion.append({"id": id_item, "categoria": datos["categoria"],
                                  "nombre": datos["nombre"],
                                  "descripcion": datos["descripcion"],
                                  "icono": datos["icono"],
                                  "rareza": datos.get("rareza", "Común"),
                                  "descubierto": True})
            else:
                coleccion.append({"id": id_item, "categoria": datos["categoria"],
                                  "nombre": "???", "descripcion": DESCRIPCION_INCOGNITA,
                                  "icono": "incognita",
                                  "rareza": datos.get("rareza", "Común"),
                                  "descubierto": False})
        return coleccion

    def descubrir_item(self, id_item):
        """Desbloquea el ítem. Devuelve True si existía y era nuevo."""
        if id_item not in CATALOGO_OBJETOS or id_item in self.desbloqueados:
            return False
        self.desbloqueados.add(id_item)
        return True

    def equipar(self, id_item):
        """Equipa un ítem descubierto en su ranura. Devuelve True si se pudo."""
        if id_item not in CATALOGO_OBJETOS or id_item not in self.desbloqueados:
            return False
        setattr(self, _RANURA[CATALOGO_OBJETOS[id_item]["categoria"]], id_item)
        return True

    def sortear_botin(self):
        """Devuelve el id de un ítem no descubierto, o ORO_BOLSA (60) si ya están todos."""
        pendientes = sorted(set(CATALOGO_OBJETOS) - self.desbloqueados)
        if not pendientes:
            return ORO_BOLSA
        return random.choice(pendientes)

    def to_dict(self):
        """Estado serializable a JSON."""
        return {"desbloqueados": sorted(self.desbloqueados),
                "arma_equipada": self.arma_equipada,
                "armadura_equipada": self.armadura_equipada,
                "habilidad_equipada": self.habilidad_equipada,
                "oro": self.oro,
                "estrellas_totales": self.estrellas_totales}

    @classmethod
    def from_dict(cls, datos):
        """Reconstruye un Inventario desde to_dict()."""
        return cls(datos)
