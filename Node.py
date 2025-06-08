class Node:
    """
    Representa un nodo (vértice) en el grafo, identificado por un string (por ejemplo, "AS52257").
    """
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return f"Node({self.id})"
