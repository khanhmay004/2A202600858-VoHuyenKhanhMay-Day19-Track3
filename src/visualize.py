"""Deliverable 2 — Ảnh chụp đồ thị tri thức (Matplotlib).

- graph.png: toàn đồ thị (nếu quá dày thì lấy subgraph các node bậc cao nhất cho dễ nhìn).
- graph_subgraph.png: vùng 2-hop quanh "Tesla" (hoặc node bậc cao nhất).
"""
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.config import OUT_DIR

TYPE_COLOR = {
    "organization": "#1f77b4", "person": "#d62728", "product": "#2ca02c",
    "location": "#9467bd", "policy": "#8c564b", "value": "#bbbbbb", "entity": "#ff7f0e",
}


def draw(G, path, title, max_label=25):
    if G.number_of_nodes() == 0:
        print(f"[visualize] đồ thị rỗng, bỏ {path.name}")
        return
    plt.figure(figsize=(20, 15))
    pos = nx.spring_layout(G, k=0.6, seed=42, iterations=60)
    deg = dict(G.degree())
    colors = [TYPE_COLOR.get(G.nodes[n].get("etype", "entity"), "#ff7f0e") for n in G]
    sizes = [80 + 60 * deg[n] for n in G]
    nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color=colors, alpha=0.85,
                           linewidths=0.3, edgecolors="white")
    nx.draw_networkx_edges(G, pos, alpha=0.15, arrows=False, width=0.6)
    top = dict(sorted(deg.items(), key=lambda x: -x[1])[:max_label])
    nx.draw_networkx_labels(G, pos, labels={n: n for n in top}, font_size=8)

    handles = [plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=c,
                          markersize=9, label=t) for t, c in TYPE_COLOR.items()]
    plt.legend(handles=handles, loc="lower left", fontsize=9, title="Node type")
    plt.title(title, fontsize=16)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[visualize] đã lưu {path.name} ({G.number_of_nodes()} node)")


def run():
    G = nx.read_graphml(OUT_DIR / "graph.graphml")

    # graph.png — nếu quá dày, lấy 120 node bậc cao nhất cho dễ đọc
    if G.number_of_nodes() > 150:
        top_nodes = [n for n, _ in sorted(G.degree, key=lambda x: -x[1])[:120]]
        Gv = G.subgraph(top_nodes)
        title = "Knowledge Graph — US EV Corpus (120 node bậc cao nhất)"
    else:
        Gv = G
        title = "Knowledge Graph — US EV Corpus"
    draw(Gv, OUT_DIR / "graph.png", title)

    # graph_subgraph.png — ego 2-hop quanh Tesla (hoặc node bậc cao nhất)
    center = "Tesla" if "Tesla" in G else max(G.degree, key=lambda x: x[1])[0]
    ego = nx.ego_graph(G.to_undirected(), center, radius=2)
    draw(ego, OUT_DIR / "graph_subgraph.png", f"Vùng 2-hop quanh '{center}'", max_label=40)


if __name__ == "__main__":
    run()
