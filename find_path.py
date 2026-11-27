from collections import deque
from parse_map import MapData
from graph import build_graph

def find_path(map_data) -> list[str] | None:
    graph = build_graph(map_data)
    start, goal = map_data.start, map_data.end

    queue = deque([start])
    came_from: dict[str, str | None] = {start: None}   # 「このマスにはどこから来たか」



    while queue:
        current = queue.popleft()

        if current == goal:
            break

    # graphの値はリストで帰るのでfor文で回し一つずつ取りだす
        for nxt in graph[current]:
            if nxt in came_from:
                continue
        came_from[nxt] = current
        queue.append(nxt)

    # goalに一度も着けなかったら
    if goal not in came_from:
        return None


    path: list[str] = []
    node: str | None = goal
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return path
