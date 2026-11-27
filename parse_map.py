import sys
from dataclasses import dataclass
from collections import deque

ZONE_KEYS = {"zone", "color", "max_drones"}
LINK_KEYS = {"max_link_capacity"}

@dataclass
class Zone:
    """mapファイルのhubの情報

        Arrtibutes:
        name: hubの名前
        x: x座標
        y: y座標
        zone_type: ゾーンタイプ。デフォルトはnormal
        color: 色。デフォルトはnone
        max_drones: ドローンの最大数。デフォルトは1
        line_no: エラー表示用の行番号
    """
    name: str
    x: int
    y: int
    zone_type: str = "normal"
    color: str | None = None
    max_drones: int | None = 1 # None は無制限(start / end 用)
    line_no: int = 0  # エラー報告用に定義された行番号を持たせる


@dataclass
class Connection:
    """mapファイルの接続情報

    zone_a: hubの名前
    zone_b: hubの名前
    max_link_capacity: 一度にその道にいてもいいドローン数。デフォルトは1
    line_no: エラー報告時に使う行番号。デフォルトは0
    """
    zone_a: str
    zone_b: str
    max_link_capacity: int = 1
    line_no: int = 0


@dataclass
class MapData:
    """mapファイルの内容を保持するデータクラス
    
    Arrtibutes:
        nb_drones: ドローンの数。
        start: スタート地点のhub.
        end: ゴール地点のhub
        hub: 地点
        connection: 接続。ハイフンでつながる
        zone: ゾーンの４つのタイプ。
        max_link_capacity: 一度に接続できるドローンの数
        max_drones: そのゾーンに一度にいられるドローンの数

    """
    nb_drones: int
    start: str  # start_hubのゾーン名
    end: str    # end_hubのゾーン名
    zones: dict[str, Zone]
    connections: list[Connection]


class ParseError(Exception):
    """mapファイルがない・壊れている・内容が不正な場合に送出する例外。"""
    def __init__(self, line_no: int, message: str) -> None:
        super().__init__(f"line {line_no}: {message}")


# 小さな部品から処理
ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}


def parse_int(value: str, what: str, line_no: int) -> int:
    try:
        return int(value)
    except ValueError:
        raise ParseError(line_no, f"{what} must be an integer: {value!r}") from None 
        # 例外の連鎖を明示的に抑制するfrom None(原因の個所の特定とメッセージだけが必要なので元のErrorを隠すために使っている)


def split_metadata(rest: str) -> tuple[str, str]:
    """'roof1 3 4 [zone=restricted]' -> ('roof1 3 4', '[zone=restricted]')"""
    body, bracket, meta = rest.partition("[")  # 最初の "[" で3つに分ける
    return body.strip(), (bracket + meta).strip()


def parse_metadata(text: str, line_no: int, allowed: set[str]) -> dict[str, str]:
    """meta dataを辞書にする

    parameter:
        text: map.txtの中の[]で囲まれた文字列
        line_no: map.txtの中の行番号
        allowed: 許可するキー（ゾーン用と接続用で別々に渡す）
    return:
        meta dataを辞書にして返す（zone名、色）
    str.partition(区切り) は「前・区切り・後」の3つ組を返すメソッド
    """

    if not text:
        return {}
    if not (text.startswith("[") and text.endswith("]")):
        raise ParseError(line_no, f"invalid metadata: {text!r}")
    result: dict[str, str] = {}
    for token in text[1:-1].split():
        key, sep, value = token.partition("=")
        if not sep or not key or not value:
            raise ParseError(line_no, f"invalid metadata entry: {token!r}")
        if key not in allowed:
            raise ParseError(line_no, f"unknown metadata key: {key!r}")
        if key in result:
            raise ParseError(line_no, f"duplicate metadata key: {key!r}")
        result[key] = value
    return result


# hub と connection の解析
def parse_zone(rest: str, line_no: int, is_endpoint: bool = False) -> Zone:
    """
    meta dataからhubの値をチェックし保存する。

    parameter:
    rest: map.txtから余計な部分を省いた値
    line_no: 行番号
    is_endpoint: 通常のhubではないか（start_hubかend_hub)のフラグ
    """

    body, meta_text = split_metadata(rest)
    parts = body.split()
    if len(parts) != 3:
        raise ParseError(line_no, "hub must be '<name> <x> <y> [metadata]'")
    name, x, y = parts
    if "-" in name:
        raise ParseError(line_no, f"zone name must not contain '-': {name!r}")
    meta = parse_metadata(meta_text, line_no, ZONE_KEYS)
    zone_type = meta.get("zone", "normal")
    if zone_type not in ZONE_TYPES:
        raise ParseError(line_no, f"unknown zone type: {zone_type!r}")
    max_drones: int | None = None  # start / end は上限なし(指定があっても無視)
    if not is_endpoint:
        max_drones = parse_int(meta.get("max_drones", "1"), "max_drones", line_no)
        if max_drones < 1:
            raise ParseError(line_no, "max_drones must be positive")
    return Zone(
        name, parse_int(x, "x", line_no), parse_int(y, "y", line_no),
        zone_type, meta.get("color"), max_drones, line_no,
    )



def parse_connection(rest: str, line_no: int) -> Connection:
    """
    connectionの値をチェックし、値を保存する。
    parameter:
        rest: map.txtから余計な部分を省いた値
        line_no: 行番号
    """

    body, meta_text = split_metadata(rest)
    names = body.split("-")
    if len(names) != 2 or not all(names):
        raise ParseError(line_no, "connection must be '<zone>-<zone>'")
    meta = parse_metadata(meta_text, line_no,LINK_KEYS )
    capacity = parse_int(
        meta.get("max_link_capacity", "1"), "max_link_capacity", line_no
    )
    if capacity < 1:
        raise ParseError(line_no, "max_link_capacity must be positive")
    return Connection(names[0], names[1], capacity, line_no)


# ファイル全体をチェックする
def parse_file(path: str) -> MapData:
    """map.txtを開いて中身を確認し、Mapdataを作成する。

    parameter:
        path: map.txtのパス
    ゾーン名の重複は、読んでいる最中に見つかるので、ここでも行番号つきで出せます。
    接続先が存在するかなど、読み終えてから確認することは、validate で行う想定

    重複の接続は frozenset を使うと順序が関係なくなる
    """

    nb_drones: int | None = None
    start: str | None = None
    end: str | None = None
    zones: dict[str, Zone] = {}
    connections: list[Connection] = []
    seen_links: set[frozenset[str]] = set()
    line_no = 0

    with open(path) as f:
        for line_no, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            kind, sep, rest = line.partition(":")
            kind, rest = kind.strip(), rest.strip()
            if not sep:
                raise ParseError(line_no, "expected '<key>: <value>'")
            if nb_drones is None and kind != "nb_drones":
                raise ParseError(line_no, "first line must be 'nb_drones: <n>'")

            if kind == "nb_drones":
                if nb_drones is not None:
                    raise ParseError(line_no, "nb_drones defined twice")
                nb_drones = parse_int(rest, "nb_drones", line_no)
                if nb_drones < 1:
                    raise ParseError(line_no, "nb_drones must be positive")
            elif kind in ("start_hub", "end_hub", "hub"):
                zone = parse_zone(rest, line_no, is_endpoint=(kind != "hub"))
                if zone.name in zones:
                    raise ParseError(line_no, f"duplicate zone: {zone.name!r}")
                zones[zone.name] = zone
                if kind == "start_hub":
                    if start is not None:
                        raise ParseError(line_no, "start_hub defined twice")
                    start = zone.name
                elif kind == "end_hub":
                    if end is not None:
                        raise ParseError(line_no, "end_hub defined twice")
                    end = zone.name
            elif kind == "connection":
                conn = parse_connection(rest, line_no)
                if conn.zone_a == conn.zone_b:
                    raise ParseError(line_no, f"connection links zone {conn.zone_a!r} to itself")
                for name in (conn.zone_a, conn.zone_b):
                    if name not in zones:
                        raise ParseError(line_no, f"unknown zone: {name!r}")
                key = frozenset((conn.zone_a, conn.zone_b))
                if key in seen_links:
                    raise ParseError(line_no, "duplicate connection")
                seen_links.add(key)
                connections.append(conn)
            else:
                raise ParseError(line_no, f"unknown key: {kind!r}")

    if nb_drones is None or start is None or end is None:
        raise ParseError(line_no, "nb_drones, start_hub and end_hub are required")
    return MapData(nb_drones, start, end, zones, connections)
