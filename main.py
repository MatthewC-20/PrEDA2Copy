import matplotlib.pyplot as plt
import networkx as nx
from Graph import Graph
from BFS import bfs_shortest_path
from DFS import dfs_path
def construir_grafo() -> Graph:
    g = Graph()
    # Lista de aristas extraídas de la topología (AS52257 -> ... -> AS2914)
    aristas = [
        ("AS52257", "AS27947"),
        ("AS27947", "AS6762"),
        ("AS6762", "AS3491"), ("AS6762", "AS1299"), ("AS6762", "AS23520"),
        ("AS3491", "AS3356"), ("AS3491", "AS7922"), ("AS3491", "AS6461"),
        ("AS1299", "AS3257"), ("AS1299", "AS6939"), ("AS1299", "AS5511"),
        ("AS1299", "AS174"),  ("AS1299", "AS6453"), ("AS1299", "AS12956"),
        ("AS1299", "AS3320"), ("AS1299", "AS701"),  ("AS1299", "AS7018"),
        ("AS23520", "AS6830"),
        ("AS3356", "AS2914"), ("AS7922", "AS2914"), ("AS6461", "AS2914"),
        ("AS3257", "AS2914"), ("AS6939", "AS2914"), ("AS5511", "AS2914"),
        ("AS174",  "AS2914"), ("AS6453", "AS2914"), ("AS12956","AS2914"),
        ("AS3320", "AS2914"), ("AS701",  "AS2914"), ("AS7018", "AS2914"),
        ("AS6830", "AS2914"),
    ]
    for origen, destino in aristas:
        g.agregar_arista(origen, destino)
    return g


def graficar(g: Graph, ruta: list[str], titulo: str, color: str):
    # Construye un grafo NetworkX para la visualización
    G_nx = nx.DiGraph()
    for nodo in g.nodos.values():
        G_nx.add_node(nodo.id)
    for nodo, vecinos in g.ady.items():
        for v in vecinos:
            G_nx.add_edge(nodo.id, v.id)

    pos = nx.spring_layout(G_nx, seed=42)
    plt.figure(figsize=(10, 6))
    nx.draw_networkx_nodes(G_nx, pos, node_size=800, node_color='lightgray')
    nx.draw_networkx_labels(G_nx, pos, font_size=8)
    nx.draw_networkx_edges(
        G_nx,
        pos,
        edge_color='gray',
        alpha=0.5,
        arrows=True,
        arrowstyle='-|>',
        arrowsize=20,
        connectionstyle='arc3,rad=0.2',
    )
    # Resalta la ruta encontrada
    if ruta:
        aristas_ruta = list(zip(ruta, ruta[1:]))
        nx.draw_networkx_nodes(G_nx, pos, nodelist=ruta, node_color=color, node_size=800)
        nx.draw_networkx_edges(
            G_nx,
            pos,
            edgelist=aristas_ruta,
            edge_color=color,
            width=2,
            arrows=True,
            arrowstyle='-|>',
            arrowsize=20,
            connectionstyle='arc3,rad=0.2',
        )
    plt.title(titulo)
    plt.axis('off')


def main():
    grafo = construir_grafo()

    # Mostrar los nodos disponibles
    print("Nodos disponibles:")
    nodos_disponibles = sorted(grafo.nodos.keys())
    for i, nodo in enumerate(nodos_disponibles):
        print(f"{i + 1}. {nodo}", end="\t")
        if (i + 1) % 5 == 0:  # 5 nodos por línea
            print()
    print("\n")

    # Solicitar nodos de inicio y fin
    start = input("Ingresa el nodo de inicio (ejemplo: AS52257): ")
    end = input("Ingresa el nodo de destino (ejemplo: AS2914): ")

    # Verificar que los nodos existan
    if start not in grafo.nodos:
        print(f"Error: El nodo {start} no existe en el grafo.")
        return
    if end not in grafo.nodos:
        print(f"Error: El nodo {end} no existe en el grafo.")
        return

    ruta_bfs = bfs_shortest_path(grafo, start, end)
    ruta_dfs = dfs_path(grafo, start, end)

    if ruta_bfs:
        print("Ruta BFS (más corta):", ruta_bfs)
        graficar(grafo, ruta_bfs, f"BFS: Ruta más corta de {start} a {end}", 'green')
    else:
        print(f"No se encontró ruta BFS de {start} a {end}")

    if ruta_dfs:
        print("Ruta DFS (profunda):", ruta_dfs)
        graficar(grafo, ruta_dfs, f"DFS: Ruta profunda de {start} a {end}", 'red')
    else:
        print(f"No se encontró ruta DFS de {start} a {end}")

    if ruta_bfs or ruta_dfs:
        plt.show()


if __name__ == "__main__":
    main()

