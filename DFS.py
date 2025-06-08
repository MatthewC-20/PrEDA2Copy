from Graph import Graph


def dfs_path(graph: Graph, start_id: str, goal_id: str) -> list[str] | None:
    """
    Realiza DFS y retorna una ruta (lista de IDs) desde start_id hasta goal_id.
    No garantiza la ruta más corta.
    """
    start = graph.nodos.get(start_id)
    goal = graph.nodos.get(goal_id)
    if not start or not goal:
        return None

    visited = set()
    path: list[str] = []
    found = False

    def dfs(node):
        nonlocal found
        visited.add(node)
        path.append(node.id)
        if node == goal:
            found = True
            return
        for neighbor in graph.ady[node]:
            if neighbor not in visited and not found:
                dfs(neighbor)
        if not found:
            path.pop()

    dfs(start)
    return path if found else None
