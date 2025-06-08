class Arista:
    """
    Representa una arista dirigida entre dos nodos del grafo.
    """
    def __init__(self, origen, destino):
        self.origen = origen    # instancia de Node
        self.destino = destino  # instancia de Node

    def __repr__(self):
        return f"Arista({self.origen.id} -> {self.destino.id})"