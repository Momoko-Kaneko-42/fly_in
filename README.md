*This project has been created as part of the 42 curriculum by mkaneko.*

# Fly-in

## index
    Description
    Instruction
    Resource
    
## Description
複数のドローンを接続されたゾーン間で移動させつつ、シミュレーションターンを最小限に抑え、移動制約を管理する、効率的なドローンルーティングシステムを設計する。
どの経路をどのドローンに使わせると全員が最も早く到着するかという最適化問題を解決し、シミュレーションの視覚的なフィードバックを提供する。

## Instruction
１．　与えられたmap.txtを１行ずつ読み、コメントや空行を飛ばし、種別ごとの生のdicrへ変換する。エラー時は行番号付きで例外を出す。
２．　１．のデータの意味のチェックを行う。
    ・ゾーン名の重複
    ・start/endが一つずつか
    ・connectionの両端が存在するか
    ・同じ接続の重複
    ・max_drones/ max_link_capability/ nb_dronesが正の値か
３．　グラフ構造用にデータを整形する。
４．　まずは１台だけ動くようにする。
    1台だけ動かす第一歩のイメージ

    (1)隣接リストを作る(map_data.connections は双方向なので、両側に追加)
    (2)移動コストを返す関数を作る
    (3)ターン数が最小になる経路を求める(重み付きの最短経路なので、ダイクストラ法)
    (4)経路を、ターンごとの動きに展開する

2と3はこんな形になります。
'''
import heapq

(2)移動コストの計算
def move_cost(zone: Zone) -> int:
    return 2 if zone.zone_type == "restricted" else 1

(3)最短経路
def shortest_path(map_data: MapData,
                  neighbors: dict[str, list[str]]) -> list[str] | None:
    start, end = map_data.start, map_data.end
    dist = {start: 0}
    prev: dict[str, str] = {}
    heap = [(0, start)]  # (ここまでのターン数, ゾーン名)
    while heap:
        d, current = heapq.heappop(heap)
        if d > dist[current]:
            continue  # 古い情報なので無視
        if current == end:
            break
        for nxt in neighbors[current]:
            zone = map_data.zones[nxt]
            if zone.zone_type == "blocked":
                continue
            nd = d + move_cost(zone)
            if nd < dist.get(nxt, float("inf")):
                dist[nxt] = nd
                prev[nxt] = current
                heapq.heappush(heap, (nd, nxt))
    if end not in dist:
        return None  # 到達不能
    path = [end]
    while path[-1] != start:
        path.append(prev[path[-1]])
    path.reverse()
    return path
    '''
## Resources
### Usage of AI

