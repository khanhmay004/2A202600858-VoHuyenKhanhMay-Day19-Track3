"""Step 2 — Construction + Deduplication: dựng NetworkX MultiDiGraph từ triples.

- Chuẩn hoá tên thực thể (lowercase, bỏ dấu câu) + alias map + fuzzy (difflib) => khử trùng lặp.
- Node = thực thể canonical (giữ kiểu nếu có). Edge = quan hệ (relation, doc_id, evidence).
=> outputs/graph.graphml + outputs/graph_stats.json
"""
import json
import re
import difflib

import networkx as nx

from src.config import OUT_DIR

ALIAS = {
    "tesla inc": "Tesla", "tesla motors": "Tesla", "tsla": "Tesla",
    "general motors": "GM", "gm": "GM",
    "ford motor": "Ford", "ford motor company": "Ford",
    "vinfast auto": "VinFast", "vinfast": "VinFast",
    "the inflation reduction act": "Inflation Reduction Act", "ira": "Inflation Reduction Act",
    "kelley blue book": "Kelley Blue Book", "kbb": "Kelley Blue Book",
    "cox automotive": "Cox Automotive",
    "us": "United States", "usa": "United States", "u s": "United States",
    "united states of america": "United States", "the united states": "United States",
}

# Các kiểu được coi là THỰC THỂ (được phép gộp). Giá trị/metric thì không gộp mạnh.
ENTITY_TYPES = {"organization", "person", "product", "location"}


def norm(s: str) -> str:
    return re.sub(r"[^\w\s]", "", s.lower()).strip()


def looks_like_value(s: str) -> bool:
    """Object kiểu số liệu/tiền/% -> coi là 'value', không gộp fuzzy."""
    return bool(re.search(r"[\d%$]", s)) and len(s) < 60


def build_canonicalizer(entity_names):
    """Trả về hàm canon() gộp tên gần trùng cho thực thể."""
    canon_map = {}
    table = []  # danh sách tên canonical đã chốt

    def canon(name: str, is_value=False) -> str:
        raw = name.strip()
        key = norm(raw)
        if key in canon_map:
            return canon_map[key]
        if key in ALIAS:
            canon_map[key] = ALIAS[key]
            return ALIAS[key]
        if not is_value:
            for c in table:
                if difflib.SequenceMatcher(None, key, norm(c)).ratio() > 0.9:
                    canon_map[key] = c
                    return c
        table.append(raw)
        canon_map[key] = raw
        return raw

    # nạp trước các thực thể đã biết để ưu tiên làm canonical
    for n in entity_names:
        canon(n)
    return canon, canon_map


def run():
    triples = [json.loads(l) for l in
               (OUT_DIR / "triples.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    ent_rows = [json.loads(l) for l in
                (OUT_DIR / "entities.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()] \
        if (OUT_DIR / "entities.jsonl").exists() else []

    etype = {}
    for e in ent_rows:
        etype.setdefault(e["entity"], e["etype"])

    canon, canon_map = build_canonicalizer(list(etype.keys()))

    G = nx.MultiDiGraph()
    raw_pairs = set()
    for t in triples:
        s = canon(t["subject"])
        o_is_val = looks_like_value(t["object"]) and t["subject"] not in (t["object"],)
        o = canon(t["object"], is_value=o_is_val)
        raw_pairs.add(t["subject"])
        raw_pairs.add(t["object"])
        G.add_node(s, etype=etype.get(t["subject"], "entity"))
        G.add_node(o, etype=("value" if o_is_val else etype.get(t["object"], "entity")))
        G.add_edge(s, o, key=t["relation"], relation=t["relation"],
                   doc_id=t.get("doc_id", ""), evidence=(t.get("evidence", "") or "")[:240])

    merged = len(raw_pairs) - len(set(canon_map[norm(x)] for x in raw_pairs))

    nx.write_graphml(G, OUT_DIR / "graph.graphml")
    deg = sorted(G.degree, key=lambda x: -x[1])[:15]
    stats = {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "merged_duplicates": int(max(0, merged)),
        "distinct_relations": len({d["relation"] for _, _, d in G.edges(data=True)}),
        "top_degree": [[n, d] for n, d in deg],
    }
    (OUT_DIR / "graph_stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False),
                                              encoding="utf-8")
    print(f"[build_graph] Nodes={stats['nodes']} Edges={stats['edges']} "
          f"merged≈{stats['merged_duplicates']} relations={stats['distinct_relations']}")
    print("[build_graph] Top degree:", deg[:10])


if __name__ == "__main__":
    run()
