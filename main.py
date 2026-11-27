import sys
from parse_map import ParseError, parse_file
from graph import build_graph, is_reachable
from find_path import find_path

def  main() -> None:
    try:
        map_data = parse_file("linear_path.txt")
        graph = build_graph(map_data)
        path = find_path(map_data)
    except ParseError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:  # ファイルが無い、読めない、など
        print(f"Error: cannot read file: {e}", file=sys.stderr)
        sys.exit(1)
    print(map_data)
    print()
    print(graph)
    print()
    print(path)
    print(is_reachable(map_data))

if __name__ == "__main__":
    main()
