def walk_typetree_for_colors(tree, callback, path_prefix=""):
    def walk(node, path=""):
        if isinstance(node, dict):
            if all(k in node for k in ("r", "g", "b", "a")) and \
               all(isinstance(node[k], (int, float)) for k in ("r", "g", "b", "a")):
                callback(path, node)
            else:
                for k, v in node.items():
                    sub_path = f"{path}.{k}" if path else k
                    walk(v, sub_path)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                sub_path = f"{path}[{i}]"
                walk(v, sub_path)

    walk(tree, path_prefix)
