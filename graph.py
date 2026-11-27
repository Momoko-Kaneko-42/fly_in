# graph.py
from collections import deque
from parse_map import MapData


def build_graph(map_data: MapData) -> dict[str, list[str]]:
    """
    隣接リストadjacency listを作る。

    parameter:
    map_data:mapファイルの内容
    """

    graph: dict[str, list[str]] = {name: [] for name in map_data.zones}
    for c in map_data.connections:
        a, b = c.zone_a, c.zone_b
        if "blocked" in (map_data.zones[a].zone_type,
                         map_data.zones[b].zone_type):
            continue  # blockedゾーンにつながる道は最初から作らない
        graph[a].append(b)
        graph[b].append(a)
    return graph

def is_reachable(map_data: MapData) -> bool:
    """
    startからgoalに到達できなくても文法的に正しければパーサーはエラーにはしない。
    パーサーとは別の段階でこの処理を入れる必要がある。
    経路探索の前に「startからendへ行けるか」を確認し、明確に報告する
    """

    neighbors: dict[str, list[str]] = {name: [] for name in map_data.zones}
    for c in map_data.connections:
        neighbors[c.zone_a].append(c.zone_b)
        neighbors[c.zone_b].append(c.zone_a)  # 双方向なので両側に追加

    visited = {map_data.start}
    queue = deque([map_data.start])
    while queue:
        current = queue.popleft()
        if current == map_data.end:
            return True
        for nxt in neighbors[current]:
            if nxt in visited or map_data.zones[nxt].zone_type == "blocked":
                continue  # 訪問済み、または通れないゾーンは飛ばす
            visited.add(nxt)
            queue.append(nxt)
    return False
