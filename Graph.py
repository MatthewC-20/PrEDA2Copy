from Node import Node
from Arista import Arista

class Graph:
    """
    Grafo dirigido implementado con lista de adyacencia y TAD orientado a objetos.
    """
    def __init__(self):
        self.nodos = {}         # dict: id (str) -> Node
        self.ady = {}           # dict: Node -> list[Node]
        self.aristas = []       # lista de objetos Arista

    def agregar_nodo(self, id_nodo):
        if id_nodo not in self.nodos:
            nodo = Node(id_nodo)
            self.nodos[id_nodo] = nodo
            self.ady[nodo] = []

    def agregar_arista(self, id_origen, id_destino):
        # Asegura que ambos nodos existan
        self.agregar_nodo(id_origen)
        self.agregar_nodo(id_destino)
        origen = self.nodos[id_origen]
        destino = self.nodos[id_destino]

        # Crea objeto Arista y lo guarda
        arista = Arista(origen, destino)
        self.aristas.append(arista)

        # Agrega la arista a la lista de adyacencia
        self.ady[origen].append(destino)

    def __repr__(self):
        return f"Graph(nodos={len(self.nodos)}, aristas={len(self.aristas)})"
