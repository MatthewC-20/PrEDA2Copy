import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx

from Graph import Graph

# Algoritmos BFS y DFS con obtencion de arboles

def construir_grafo() -> Graph:
    g = Graph()
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
    for o, d in aristas:
        g.agregar_arista(o, d)
    return g


def bfs_with_tree(graph: Graph, start_id: str, goal_id: str):
    start = graph.nodos.get(start_id)
    goal = graph.nodos.get(goal_id)
    if not start or not goal:
        return None, {}

    from collections import deque
    queue = deque([start])
    visited = {start}
    pred = {start: None}
    while queue:
        current = queue.popleft()
        if current == goal:
            break
        for nb in graph.ady[current]:
            if nb not in visited:
                visited.add(nb)
                pred[nb] = current
                queue.append(nb)
    if goal not in pred:
        return None, pred
    path = []
    node = goal
    while node:
        path.append(node.id)
        node = pred[node]
    return path[::-1], pred


def dfs_with_tree(graph: Graph, start_id: str, goal_id: str):
    start = graph.nodos.get(start_id)
    goal = graph.nodos.get(goal_id)
    if not start or not goal:
        return None, {}
    visited = set()
    pred = {start: None}
    path = []
    found = False

    def dfs(node):
        nonlocal found
        visited.add(node)
        if node == goal:
            found = True
            return
        for nb in graph.ady[node]:
            if nb not in visited and not found:
                pred[nb] = node
                dfs(nb)

    dfs(start)
    if not found:
        return None, pred
    node = goal
    while node:
        path.append(node.id)
        node = pred.get(node)
    return path[::-1], pred


def to_networkx(graph: Graph) -> nx.DiGraph:
    G = nx.DiGraph()
    for nodo in graph.nodos.values():
        G.add_node(nodo.id)
    for nodo, vecinos in graph.ady.items():
        for v in vecinos:
            G.add_edge(nodo.id, v.id)
    return G


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Recorridos BFS y DFS")
        self.graph = construir_grafo()
        self.G_nx = to_networkx(self.graph)
        self.pos = nx.spring_layout(self.G_nx, seed=42)
        self.create_widgets()
        self.selecting_end = False

    def create_widgets(self):
        nodos = sorted(self.graph.nodos.keys())
        self.start_var = tk.StringVar(value=nodos[0])
        self.end_var = tk.StringVar(value=nodos[-1])

        ttk.Label(self, text="Nodo inicio:").grid(row=0, column=0, sticky="w")
        ttk.OptionMenu(self, self.start_var, self.start_var.get(), *nodos).grid(row=0, column=1, sticky="ew")
        ttk.Label(self, text="Nodo destino:").grid(row=1, column=0, sticky="w")
        ttk.OptionMenu(self, self.end_var, self.end_var.get(), *nodos).grid(row=1, column=1, sticky="ew")
        ttk.Button(self, text="Buscar", command=self.run).grid(row=2, column=0, columnspan=2, pady=4)

        self.text = tk.Text(self, width=40, height=4)
        self.text.grid(row=3, column=0, columnspan=2)

        self.fig, (self.ax1, self.ax2) = plt.subplots(1,2, figsize=(10,5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=4, column=0, columnspan=2)
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.draw_base_graph()

    def draw_base_graph(self):
        self.ax1.clear()
        nx.draw(self.G_nx, self.pos, ax=self.ax1, node_color='lightgray',
                 edge_color='gray', with_labels=True, arrowsize=10)
        if self.start_var.get():
            nx.draw_networkx_nodes(self.G_nx, self.pos, ax=self.ax1,
                                   nodelist=[self.start_var.get()],
                                   node_color='yellow')
        if self.end_var.get():
            nx.draw_networkx_nodes(self.G_nx, self.pos, ax=self.ax1,
                                   nodelist=[self.end_var.get()],
                                   node_color='orange')
        self.ax1.set_title('Selecciona nodos')
        self.canvas.draw()

    def on_click(self, event):
        if event.inaxes != self.ax1 or event.xdata is None:
            return
        x, y = event.xdata, event.ydata
        closest = None
        min_dist = float('inf')
        for node, (nx_, ny_) in self.pos.items():
            d = (x - nx_)**2 + (y - ny_)**2
            if d < min_dist:
                min_dist = d
                closest = node
        if min_dist > 0.05:
            return
        if not self.selecting_end:
            self.start_var.set(closest)
            self.selecting_end = True
        else:
            self.end_var.set(closest)
            self.selecting_end = False
        self.draw_base_graph()
    def run(self):
        start = self.start_var.get()
        end = self.end_var.get()
        try:
            path_bfs, tree_bfs = bfs_with_tree(self.graph, start, end)
            path_dfs, tree_dfs = dfs_with_tree(self.graph, start, end)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.text.delete("1.0", tk.END)
        if path_bfs:
            self.text.insert(tk.END, f"BFS path: {' -> '.join(path_bfs)}\n")
        else:
            self.text.insert(tk.END, "BFS: camino no encontrado\n")
        if path_dfs:
            self.text.insert(tk.END, f"DFS path: {' -> '.join(path_dfs)}\n")
        else:
            self.text.insert(tk.END, "DFS: camino no encontrado\n")

        self.draw_tree(tree_bfs, tree_dfs)
        if path_bfs:
            self.animate_path(path_bfs, 'green', '-')
            delay = 500 * len(path_bfs) + 500
        else:
            delay = 0
        if path_dfs:
            self.after(delay, lambda: self.animate_path(path_dfs, 'red', 'dashed'))

    def draw_tree(self, tree_bfs, tree_dfs):
        self.ax1.clear()
        self.ax2.clear()
        self.draw_base_graph()

        tree_graph = nx.DiGraph()
        for child, parent in tree_bfs.items():
            if parent:
                tree_graph.add_edge(parent.id, child.id, tipo='BFS')
        for child, parent in tree_dfs.items():
            if parent and (parent.id, child.id) not in tree_graph.edges:
                tree_graph.add_edge(parent.id, child.id, tipo='DFS')
        pos_tree = nx.spring_layout(tree_graph, seed=1)
        colors = ['green' if d['tipo']== 'BFS' else 'red' for _,_,d in tree_graph.edges(data=True)]
        nx.draw(tree_graph, pos_tree, ax=self.ax2, with_labels=True, arrowsize=10, edge_color=colors)
        self.ax2.set_title('Arboles')
        self.canvas.draw()

    def animate_path(self, path, color, style, idx=1):
        self.ax1.clear()
        nx.draw(self.G_nx, self.pos, ax=self.ax1, node_color='lightgray',
                 edge_color='gray', with_labels=True, arrowsize=10)
        if self.start_var.get():
            nx.draw_networkx_nodes(self.G_nx, self.pos, ax=self.ax1,
                                   nodelist=[self.start_var.get()],
                                   node_color='yellow')
        if self.end_var.get():
            nx.draw_networkx_nodes(self.G_nx, self.pos, ax=self.ax1,
                                   nodelist=[self.end_var.get()],
                                   node_color='orange')
        nodes = path[:idx]
        edges = list(zip(path[:idx-1], path[1:idx]))
        nx.draw_networkx_nodes(self.G_nx, self.pos, ax=self.ax1,
                               nodelist=nodes, node_color=color)
        nx.draw_networkx_edges(self.G_nx, self.pos, ax=self.ax1,
                               edgelist=edges, edge_color=color,
                               width=2, style=style)
        self.ax1.set_title('Recorrido')
        self.canvas.draw()
        if idx < len(path):
            self.after(500, lambda: self.animate_path(path, color, style, idx+1))


if __name__ == '__main__':
    app = App()
    app.mainloop()

