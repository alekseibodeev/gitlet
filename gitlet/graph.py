class Graph:
    """Represents a Directed Acyclic Graph."""

    def __init__(self) -> None:
        self.nodes: dict[str, list[str]] = {}

    def add(self, v: str, u: str) -> None:
        """Adds edge V -> U to the graph."""
        if v not in self.nodes:
            self.nodes[v] = []
        self.nodes[v].append(u)

    def latest_common_ancestor(self, start: str, p: str, q: str) -> str:
        def lca_helper(node: str) -> tuple[str, bool]:
            if node == p or node == q:
                return (node, False)
            is_p = False
            is_q = False
            for child in self.nodes[node]:
                pair = lca_helper(child)
                if pair[1]:
                    return pair
                if pair[0] == p:
                    is_p = True
                elif pair[0] == q:
                    is_q = True
            if is_p and is_q:
                return (node, True)
            elif is_p:
                return (p, False)
            elif is_q:
                return (q, False)
            return (node, False)

        return lca_helper(start)[0]
