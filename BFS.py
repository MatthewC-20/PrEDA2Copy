from collections import deque
from Graph import Graph


def bfs_shortest_path(graph: Graph, start_id: str, goal_id: str) -> list[str] | None:
    """
    Realiza BFS y retorna la ruta más corta (lista de IDs) desde start_id hasta goal_id.
    """
    start = graph.nodos.get(start_id)
    goal = graph.nodos.get(goal_id)
    if not start or not goal:
        return None

    queue = deque([start])
    visited = {start}
    predecessor = {start: None}

    while queue:
        current = queue.popleft()
        if current == goal:
            break
        for neighbor in graph.ady[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                predecessor[neighbor] = current
                queue.append(neighbor)
                if neighbor == goal:
                    queue.clear()
                    break

    if goal not in predecessor:
        return None

    # Reconstruye la ruta desde goal hasta start
    path = []
    node = goal
    while node:
        path.append(node.id)
        node = predecessor[node]
    return path[::-1]
