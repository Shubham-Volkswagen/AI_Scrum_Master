from __future__ import annotations
import networkx as nx

def analyze_dependencies(backlog, dependencies):
    ids = set(backlog["TicketID"].dropna().astype(str))
    graph = nx.DiGraph()
    graph.add_nodes_from(ids)
    orphan_edges = []
    for _, row in dependencies.iterrows():
        dependent = str(row["FromTicketID"])
        prerequisite = str(row["ToTicketID (depends on)"])
        if dependent not in ids or prerequisite not in ids:
            orphan_edges.append({"dependent": dependent, "prerequisite": prerequisite})
            continue
        graph.add_edge(prerequisite, dependent)
    cycles = [cycle for cycle in nx.simple_cycles(graph)]
    order = list(nx.topological_sort(graph)) if not cycles else []
    rank = {ticket: i for i, ticket in enumerate(order)}
    return {"graph": graph, "orphan_edges": orphan_edges, "cycles": cycles, "order": order, "rank": rank}
