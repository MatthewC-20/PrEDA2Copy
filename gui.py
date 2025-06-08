import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
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
        self.start_node: str | None = None
        self.end_node: str | None = None
        self.anim = None
        self.bfs_window = None
        self.dfs_window = None
        self.pos = self._compute_layout()
        self.create_widgets()

    def _compute_layout(self):
        n = self.G_nx.number_of_nodes()
        try:
            from networkx.drawing.nx_agraph import graphviz_layout
            # Usar 'dot' para layout jerárquico con nodo raíz arriba
            pos = graphviz_layout(self.G_nx, prog="dot")
        except Exception:
            try:
                pos = nx.planar_layout(self.G_nx, scale=8)
            except nx.NetworkXException:
                pos = nx.spring_layout(
                    self.G_nx, seed=42, k=8 / np.sqrt(n), iterations=3000
                )
        
        # Ajustar layout para asegurar que el nodo inicial esté arriba al centro
        if self.start_node:
            # Calcular el centro horizontal
            xs = [p[0] for p in pos.values()]
            x_center = (max(xs) + min(xs)) / 2
            
            # Calcular la coordenada y más alta (superior)
            ys = [p[1] for p in pos.values()]
            y_top = max(ys) + 0.2
            
            # Colocar el nodo inicial en la parte superior central
            pos[self.start_node] = (x_center, y_top)
            
            # Reajustar el layout a partir de la nueva posición del nodo inicial
            pos = nx.spring_layout(
                self.G_nx, pos=pos, fixed=[self.start_node], seed=42, 
                k=8 / np.sqrt(n), iterations=1000
            )
        
        return pos

    def _resize_figure(self):
        xs = [p[0] for p in self.pos.values()]
        ys = [p[1] for p in self.pos.values()]
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)
        w = max(10, width * 6)  # Aumentado el tamaño base y la escala
        h = max(6, height * 6)  # Aumentado el tamaño base y la escala
        self.fig.set_size_inches(w, h)

    def create_widgets(self):
        ttk.Label(self, text="Inicio:").grid(row=0, column=0, sticky="w")
        self.start_label = ttk.Label(self, text="-")
        self.start_label.grid(row=0, column=1, sticky="w")
        ttk.Label(self, text="Destino:").grid(row=1, column=0, sticky="w")
        self.end_label = ttk.Label(self, text="-")
        self.end_label.grid(row=1, column=1, sticky="w")
        ttk.Button(self, text="Buscar", command=self.run).grid(row=2, column=0, columnspan=2, pady=4)

        self.fig = plt.Figure(figsize=(14, 6))  # Figura más grande
        gs = self.fig.add_gridspec(1, 3, width_ratios=[1.5, 2, 1.5])  # Más espacio para los árboles
        self.ax_bfs = self.fig.add_subplot(gs[0])
        self.ax1 = self.fig.add_subplot(gs[1])
        self.ax_dfs = self.fig.add_subplot(gs[2])
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=3, column=0, columnspan=2, sticky="nsew")
        self.canvas.mpl_connect("button_press_event", self.on_canvas_click)
        self._resize_figure()
        self.update_idletasks()
        w = int(self.fig.get_figwidth() * self.fig.dpi)
        h = int(self.fig.get_figheight() * self.fig.dpi) + 150
        self.geometry(f"{w}x{h}")

        self.text = tk.Text(self, width=40, height=4)
        self.text.grid(row=4, column=0, columnspan=2, sticky="we")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)
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

    def _draw_text_nodes(self, ax, pos, nodelist, labels=None, node_color="lightgray", 
                        border_color="black", text_color="black", linewidth=1, zorder=1):
        """Dibuja nodos con forma ovalada cuyo tamaño depende de la etiqueta"""
        if labels is None:
            labels = {n: n for n in nodelist}
        
        # Aumentar significativamente el tamaño base y la escala
        base_w, base_h = 0.3, 0.2  # Valores mucho más grandes
        scale_w, scale_h = 0.03, 0.02  # Escala mayor para etiquetas largas
        
        for node in nodelist:
            if node not in pos:
                continue
                
            x, y = pos[node]
            label = str(labels[node])

            # Calcular tamaño del óvalo en función de la longitud de la etiqueta
            width = base_w + len(label) * scale_w
            height = base_h + len(label) * scale_h

            # Crear un óvalo (elipse)
            ellipse = patches.Ellipse(
                (x, y),
                width=width,
                height=height,
                facecolor=node_color,
                edgecolor=border_color,
                linewidth=linewidth,
                zorder=zorder
            )
            ax.add_patch(ellipse)
            
            # Añadir el texto centrado en el óvalo
            ax.text(
                x,
                y,
                label,
                ha='center',
                va='center',
                fontsize=9,
                color=text_color,
                zorder=zorder+1,
            )

    def _draw_nodes_circular(
        self, ax, pos, nodelist, labels=None, node_color="white",
        border_color="black", text_color="black", linewidth=1, zorder=1
    ):
        """Dibuja nodos circulares cuyo tamaño se ajusta a la longitud de la etiqueta."""
        if labels is None:
            labels = {n: n for n in nodelist}

        base_r = 0.15
        scale_r = 0.015

        for node in nodelist:
            if node not in pos:
                continue

            x, y = pos[node]
            label = str(labels[node])

            radius = base_r + len(label) * scale_r

            circle = patches.Circle(
                (x, y),
                radius=radius,
                facecolor=node_color,
                edgecolor=border_color,
                linewidth=linewidth,
                zorder=zorder,
            )
            ax.add_patch(circle)

            ax.text(
                x,
                y,
                label,
                ha="center",
                va="center",
                fontsize=9,
                color=text_color,
                zorder=zorder + 1,
            )

    def draw_base(self):
        self.ax1.clear()
        
        # Eliminar esta parte que recalcula el layout
        # if self.start_node or self.end_node:
        #     self.pos = self._compute_layout()
        
        # Dibujar aristas primero
        nx.draw_networkx_edges(
            self.G_nx,
            self.pos,
            ax=self.ax1,
            edge_color="gray",
            arrowsize=10,
            connectionstyle="arc3,rad=0.2",
        )
        
        # Dibujar nodos
        nodes = list(self.G_nx.nodes())
        self._draw_text_nodes(
            self.ax1, 
            self.pos, 
            nodes,
            node_color="lightgray"
        )
        
        # Resaltar nodos de inicio y fin si están seleccionados
        if self.start_node:
            self._draw_text_nodes(
                self.ax1,
                self.pos,
                [self.start_node],
                node_color="blue",
                text_color="white",
                zorder=10
            )
        if self.end_node:
            self._draw_text_nodes(
                self.ax1,
                self.pos,
                [self.end_node],
                node_color="orange",
                text_color="white",
                zorder=10
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
        self.draw_tree_axes(tree_bfs, tree_dfs)
        self.animate_paths(path_bfs, path_dfs)

    def draw_tree_axes(self, tree_bfs, tree_dfs):
        self._draw_tree(self.ax_bfs, tree_bfs, "BFS", "green")
        self._draw_tree(self.ax_dfs, tree_dfs, "DFS", "red")

    def _draw_tree(self, ax, tree, title, color):
        ax.clear()
        if not tree:
            ax.set_title(f"Arbol {title}")
            ax.axis('off')
            self.canvas.draw()
            return

        G = nx.DiGraph()

        # Identificar el nodo raíz
        root_node = None
        for child, parent in tree.items():
            if parent:
                G.add_edge(parent.id, child.id)
            elif not parent and child.id == self.start_node:
                root_node = child.id
                G.add_node(child.id)

        if not G.nodes():
            ax.set_title(f"Arbol {title}")
            ax.axis('off')
            self.canvas.draw()
            return

        try:
            from networkx.drawing.nx_agraph import graphviz_layout
            pos = graphviz_layout(G, prog="dot", args="-Grankdir=TB -Gnodesep=0.8 -Granksep=1.5")
        except Exception:
            pos = nx.spring_layout(G, seed=42, k=2.0, iterations=1500)

        # Aplicar factor de escala
        scaling_factor = 1.8
        for node in pos:
            pos[node] = (pos[node][0] * scaling_factor, pos[node][1] * scaling_factor)

        # Dibujar aristas
        nx.draw_networkx_edges(
            G,
            pos,
            ax=ax,
            edge_color=color,
            arrowsize=10,
            width=1.5,
            connectionstyle="arc3,rad=0.1",
        )

        # Dibujar nodos con estilo circular
        self._draw_nodes_circular(
            ax,
            pos,
            list(G.nodes()),
            node_color="white"
        )

        # Resaltar el nodo raíz
        if root_node and root_node in pos:
            self._draw_nodes_circular(
                ax,
                pos,
                [root_node],
                node_color=color,
                text_color="white",
                zorder=20
            )

        ax.set_title(f"Arbol {title}")
        ax.axis('off')
        self.canvas.draw()

    def animate_paths(self, path_bfs, path_dfs):
        self.anim = None
        max_steps = max(len(path_bfs or []), len(path_dfs or []))

        def update(i):
            self.draw_base()

            # Dibujar camino BFS hasta el paso i
            if path_bfs and i < len(path_bfs) - 1:
                edges_bfs = list(zip(path_bfs[:i+1], path_bfs[1:i+2]))
                nx.draw_networkx_edges(
                    self.G_nx,
                    self.pos,
                    ax=self.ax1,
                    edgelist=edges_bfs,
                    edge_color="green",
                    width=2,
                    connectionstyle="arc3,rad=0.2",
                )

                # Nodos del camino BFS
                self._draw_nodes_circular(
                    self.ax1,
                    self.pos,
                    path_bfs[:i+2],
                    node_color="lightgreen",
                    border_color="green",
                    zorder=20
                )

            # Dibujar camino DFS hasta el paso i
            if path_dfs and i < len(path_dfs) - 1:
                edges_dfs = list(zip(path_dfs[:i+1], path_dfs[1:i+2]))
                nx.draw_networkx_edges(
                    self.G_nx,
                    self.pos,
                    ax=self.ax1,
                    edgelist=edges_dfs,
                    edge_color="red",
                    width=2,
                    connectionstyle="arc3,rad=0.2",
                )

                # Nodos del camino DFS
                self._draw_nodes_circular(
                    self.ax1,
                    self.pos,
                    path_dfs[:i+2],
                    node_color="lightcoral",
                    border_color="darkred",
                    zorder=20
                )

            self.ax1.annotate(
                f"Paso {i+1}/{max_steps}",
                xy=(0.02, 0.02),
                xycoords="axes fraction",
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.7)
            )

        if max_steps > 0:
            self.anim = animation.FuncAnimation(
                self.fig, update, frames=max_steps, interval=800, repeat=False
            )
        self.canvas.draw()


if __name__ == '__main__':
    matplotlib.use('TkAgg')
    app = App()
    app.mainloop()