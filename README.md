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


## Resources
### Usage of AI

