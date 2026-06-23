"""Step 3 — GraphRAG querying (truy hồi quan hệ + mở rộng lân cận trên đồ thị).

1) Nhận câu hỏi.
2) TRUY HỒI QUAN HỆ: embedding câu hỏi, tìm các TRIPLE (cạnh) giống nhất trên toàn đồ thị
   -> các "neo" (anchor) chứa sự thật liên quan. (Mỗi triple được embed kèm câu gốc evidence
   để tăng độ chính xác truy hồi.)
3) MỞ RỘNG THEO CẤU TRÚC: lấy thêm cạnh 1-hop của các node neo (duyệt đồ thị) -> gộp các sự
   thật liên kết mà tìm kiếm phẳng dễ bỏ sót -> hỗ trợ suy luận multi-hop.
4) Textualize (kèm câu gốc để LLM phân biệt số liệu) -> gpt-4o trả lời CHỈ dựa trên đó.

Khác Flat RAG: Flat RAG truy hồi ĐOẠN VĂN theo độ tương tự; GraphRAG truy hồi QUAN HỆ có cấu
trúc rồi MỞ RỘNG theo cạnh đồ thị (graph traversal) để ghép sự thật từ nhiều tài liệu.
"""
import threading

import numpy as np
import networkx as nx
from openai import OpenAI

from src.config import OUT_DIR, ANSWER_MODEL, OPENAI_API_KEY, HOP, OPENAI_MAX_RETRIES
from src import flat_rag   # tái dùng embedder (all-MiniLM, offline)

_oai = OpenAI(api_key=OPENAI_API_KEY, max_retries=OPENAI_MAX_RETRIES)

_edge_emb = None       # embedding (chuẩn hoá) của triple + evidence
_edge_disp = None      # chuỗi hiển thị cho LLM (triple + câu gốc)
_edge_uv = None
_lock = threading.Lock()


def load_graph():
    return nx.read_graphml(OUT_DIR / "graph.graphml")


def warm(G):
    """Tính sẵn embedding mọi triple (kèm evidence) — gọi 1 lần trước khi chạy song song."""
    global _edge_emb, _edge_disp, _edge_uv
    with _lock:
        if _edge_emb is not None:
            return
        emb_texts, disp, uv = [], [], []
        for u, v, d in G.edges(data=True):
            rel = d.get("relation", "RELATED_TO")
            ev = (d.get("evidence", "") or "").strip()
            rel_readable = rel.replace("_", " ").lower()
            emb_texts.append(f"{u} {rel_readable} {v}. {ev}")        # giàu ngữ cảnh -> recall tốt
            disp.append(f"- {u} [{rel}] {v}" + (f'  (source: "{ev}")' if ev else ""))
            uv.append((u, v))
        e = flat_rag.embedder().encode(emb_texts, batch_size=256, show_progress_bar=False)
        _edge_emb = e / (np.linalg.norm(e, axis=1, keepdims=True) + 1e-9)
        _edge_disp, _edge_uv = disp, uv


def retrieve(G, q, top_edges=45, max_triples=55):
    """Top triple giống câu hỏi (anchor) + mở rộng 1-hop các node anchor (graph traversal)."""
    warm(G)
    qv = flat_rag.embedder().encode([q])[0]
    qv = qv / (np.linalg.norm(qv) + 1e-9)
    sims = _edge_emb @ qv

    top = np.argsort(-sims)[:top_edges]
    chosen, lines, anchors = set(), [], set()
    for i in top:
        chosen.add(int(i))
        lines.append(_edge_disp[i])
        u, v = _edge_uv[i]
        anchors.add(u); anchors.add(v)

    exp = [j for j, (u, v) in enumerate(_edge_uv)
           if j not in chosen and (u in anchors or v in anchors)]
    if exp:
        exp = np.array(exp)
        for j in exp[np.argsort(-(_edge_emb[exp] @ qv))]:
            if len(lines) >= max_triples:
                break
            lines.append(_edge_disp[int(j)])
    return "\n".join(lines[:max_triples]), len(anchors), sorted(anchors)[:8]


def answer(G, q, hop=HOP):
    ctx, n_anchor, anchors = retrieve(G, q)
    if not ctx:
        ctx = "(No related relations found in the graph.)"
    r = _oai.chat.completions.create(
        model=ANSWER_MODEL, temperature=0,
        messages=[
            {"role": "system", "content": "You are a QA assistant grounded in a KNOWLEDGE GRAPH. Answer "
             "CONCISELY using ONLY the relations (triples) below; each may include its source sentence. "
             "Several related figures may appear — pick the one that best matches the question's entity, "
             "time period and scope, and answer with that specific value. Only say 'Not enough "
             "information' if no relation is relevant."},
            {"role": "user", "content": f"KNOWLEDGE (relevant relations):\n{ctx}\n\nQUESTION: {q}"},
        ])
    info = {"linked_nodes": anchors, "subgraph_nodes": n_anchor}
    return r.choices[0].message.content.strip(), r.usage, ctx, info


if __name__ == "__main__":
    G = load_graph()
    a, _, ctx, info = answer(G, "What was Tesla's share of the US EV market in Q1 2024?")
    print("ANCHORS:", info["linked_nodes"])
    print("CTX:\n", ctx[:1200])
    print("ANSWER:", a)
