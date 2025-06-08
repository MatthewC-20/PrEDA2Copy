import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx
import numpy as np

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
        self.pos = self._compute_layout()
        self.start_node: str | None = None
        self.end_node: str | None = None
        self.anim = None
        self.bfs_window = None
        self.dfs_window = None
        self.create_widgets()

    def _compute_layout(self):
        n = self.G_nx.number_of_nodes()
        try:
            return nx.planar_layout(self.G_nx, scale=2)
        except nx.NetworkXException:
            return nx.spring_layout(
                self.G_nx, seed=42, k=2 / np.sqrt(n), iterations=200
            )

    def create_widgets(self):
        ttk.Label(self, text="Inicio:").grid(row=0, column=0, sticky="w")
        self.start_label = ttk.Label(self, text="-")
        self.start_label.grid(row=0, column=1, sticky="w")
        ttk.Label(self, text="Destino:").grid(row=1, column=0, sticky="w")
        self.end_label = ttk.Label(self, text="-")
        self.end_label.grid(row=1, column=1, sticky="w")
        ttk.Button(self, text="Buscar", command=self.run).grid(row=2, column=0, columnspan=2, pady=4)

        self.fig, self.ax1 = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=3, column=0, columnspan=2)
        self.canvas.mpl_connect("button_press_event", self.on_canvas_click)

        self.text = tk.Text(self, width=40, height=4)
        self.text.grid(row=4, column=0, columnspan=2)
        self.draw_base()

    def on_canvas_click(self, event):
        if event.inaxes != self.ax1:
            return
        if event.xdata is None or event.ydata is None:
            return
        x, y = event.xdata, event.ydata
        closest = None
        min_dist = float("inf")
        for node, (nx_pos, ny_pos) in self.pos.items():
            dist = (nx_pos - x) ** 2 + (ny_pos - y) ** 2
            if dist < min_dist:
                min_dist = dist
                closest = node
        if min_dist > 0.05:
            return
        if self.start_node is None:
            self.start_node = closest
            self.start_label.config(text=closest)
        elif self.end_node is None:
            self.end_node = closest
            self.end_label.config(text=closest)
        else:
            self.start_node = closest
            self.start_label.config(text=closest)
            self.end_node = None
            self.end_label.config(text="-")
        self.draw_base()

    def draw_base(self):
        self.ax1.clear()
        nx.draw(
            self.G_nx,
            self.pos,
            ax=self.ax1,
            node_color="lightgray",
            edge_color="gray",
            with_labels=True,
            arrowsize=10,
        )
        if self.start_node:
            nx.draw_networkx_nodes(
                self.G_nx, self.pos, ax=self.ax1, nodelist=[self.start_node], node_color="blue"
            )
        if self.end_node:
            nx.draw_networkx_nodes(
                self.G_nx, self.pos, ax=self.ax1, nodelist=[self.end_node], node_color="orange"
            )
        self.ax1.set_title("Recorrido")
        self.canvas.draw()

    def run(self):
        start = self.start_node
        end = self.end_node
        if not start or not end:
            messagebox.showwarning(
                "Seleccion requerida", "Seleccione nodo de inicio y destino"
            )
            return
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

        self.draw_results(path_bfs, tree_bfs, path_dfs, tree_dfs)

    def draw_results(self, path_bfs, tree_bfs, path_dfs, tree_dfs):
        self.draw_tree_windows(tree_bfs, tree_dfs)
        self.animate_paths(path_bfs, path_dfs)

    def draw_tree_windows(self, tree_bfs, tree_dfs):
        self._show_tree(tree_bfs, "BFS", "green")
        self._show_tree(tree_dfs, "DFS", "red")

    def _show_tree(self, tree, title, color):
        if not tree:
            return
        attr = f"{title.lower()}_window"
        old_win = getattr(self, attr, None)
        if old_win is not None and old_win.winfo_exists():
            old_win.destroy()
        window = tk.Toplevel(self)
        setattr(self, attr, window)
        window.title(f"Arbol {title}")
        fig, ax = plt.subplots(figsize=(5, 5))
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.get_tk_widget().pack()

        G = nx.DiGraph()
        for child, parent in tree.items():
            if parent:
                G.add_edge(parent.id, child.id)

        try:
            pos = nx.planar_layout(G)
        except nx.NetworkXException:
            pos = nx.spring_layout(G, seed=1)

        nx.draw(G, pos, ax=ax, with_labels=True, arrowsize=10, edge_color=color, node_color="lightgray")
        ax.set_title(f"Arbol {title}")
        fig.tight_layout()
        canvas.draw()
        window.focus()

    def animate_paths(self, path_bfs, path_dfs):
        self.anim = None
        max_steps = max(len(path_bfs or []), len(path_dfs or []))

        def update(i):
            self.draw_base()
            if path_bfs:
                edges_bfs = list(zip(path_bfs, path_bfs[1 : i + 1]))
                nodes_bfs = path_bfs[: i + 1]
                nx.draw_networkx_nodes(
                    self.G_nx, self.pos, ax=self.ax1, nodelist=nodes_bfs, node_color="green"
                )
                nx.draw_networkx_edges(
                    self.G_nx, self.pos, ax=self.ax1, edgelist=edges_bfs, edge_color="green", width=2
                )
            if path_dfs:
                edges_dfs = list(zip(path_dfs, path_dfs[1 : i + 1]))
                nodes_dfs = path_dfs[: i + 1]
                nx.draw_networkx_nodes(
                    self.G_nx, self.pos, ax=self.ax1, nodelist=nodes_dfs, node_color="red"
                )
                nx.draw_networkx_edges(
                    self.G_nx,
                    self.pos,
                    ax=self.ax1,
                    edgelist=edges_dfs,
                    edge_color="red",
                    width=2,
                    style="dashed",
                )

        if max_steps > 0:
            self.anim = animation.FuncAnimation(
                self.fig, update, frames=max_steps, interval=800, repeat=False
            )
        self.canvas.draw()


if __name__ == '__main__':
    app = App()
    app.mainloop()
