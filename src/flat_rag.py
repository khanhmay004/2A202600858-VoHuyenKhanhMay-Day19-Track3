"""Flat RAG baseline — chỉ dùng vector search (MiniLM + ChromaDB), KHÔNG dùng đồ thị.

retrieve(): top-k chunk theo cosine. answer(): nhồi chunk vào prompt -> gpt-4o trả lời.
"""
import os
import json

os.environ.setdefault("HF_HUB_OFFLINE", "1")        # dùng model embedding đã cache
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI

from src.config import OUT_DIR, EMBED_MODEL, ANSWER_MODEL, OPENAI_API_KEY, TOP_K, OPENAI_MAX_RETRIES

_embedder = None
_oai = OpenAI(api_key=OPENAI_API_KEY, max_retries=OPENAI_MAX_RETRIES)


def embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL)
    return _embedder


def chunk_text(text, size=180, overlap=30):
    """Chia theo từ (~180 từ ≈ 230 token)."""
    words = text.split()
    out, i = [], 0
    while i < len(words):
        out.append(" ".join(words[i:i + size]))
        i += size - overlap
    return out


def build_index():
    docs = [json.loads(l) for l in
            (OUT_DIR / "clean_docs.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    client = chromadb.EphemeralClient()
    try:
        client.delete_collection("flat")
    except Exception:
        pass
    col = client.create_collection("flat")
    ids, texts, metas = [], [], []
    for d in docs:
        topic = " | ".join(filter(None, [d.get("title", ""), d.get("query", "")]))
        for j, ch in enumerate(chunk_text(d["text"])):
            ids.append(f"{d['doc_id']}_{j}")
            # gắn topic (title|query) vào mỗi chunk để truy hồi có ngữ cảnh chủ đề
            texts.append(f"[{topic}] {ch}" if topic else ch)
            metas.append({"doc": d["doc_id"], "title": d.get("title", "")})
    embs = embedder().encode(texts, batch_size=64, show_progress_bar=False).tolist()
    # add theo lô để tránh giới hạn batch của Chroma
    B = 2000
    for i in range(0, len(ids), B):
        col.add(ids=ids[i:i + B], documents=texts[i:i + B],
                embeddings=embs[i:i + B], metadatas=metas[i:i + B])
    print(f"[flat_rag] đã index {len(ids)} chunk từ {len(docs)} doc.")
    return col


def retrieve(col, q, k=TOP_K):
    qe = embedder().encode([q]).tolist()
    res = col.query(query_embeddings=qe, n_results=k)
    docs = res["documents"][0]
    srcs = [m["doc"] for m in res["metadatas"][0]]
    return docs, srcs


def answer(col, q, k=TOP_K):
    chunks, srcs = retrieve(col, q, k)
    ctx = "\n\n---\n".join(chunks)
    r = _oai.chat.completions.create(
        model=ANSWER_MODEL, temperature=0,
        messages=[
            {"role": "system", "content": "You are a QA assistant. Answer CONCISELY and ONLY from the "
             "provided context. If the context is insufficient, say 'Not enough information'."},
            {"role": "user", "content": f"CONTEXT:\n{ctx}\n\nQUESTION: {q}"},
        ])
    return r.choices[0].message.content.strip(), r.usage, srcs


if __name__ == "__main__":
    c = build_index()
    a, u, s = answer(c, "What was Tesla's share of the US EV market in Q1 2024?")
    print("ANSWER:", a)
    print("SOURCES:", s)
