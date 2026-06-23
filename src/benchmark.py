"""Step 4 — Evaluation: chạy 20 câu hỏi trên Flat RAG và GraphRAG, chấm bằng LLM-judge.

=> outputs/benchmark.md (bảng so sánh + mục "Flat ảo giác / Graph đúng")
=> outputs/benchmark.csv (chi tiết)
=> outputs/cost_query.json (token + thời gian phần querying, cho Deliverable 4)
"""
import json
import csv
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import networkx as nx
from openai import OpenAI

from src import flat_rag, graph_rag
from src.config import (OUT_DIR, ROOT, ANSWER_MODEL, EXTRACT_MODEL, JUDGE_MODEL,
                        OPENAI_API_KEY, OPENAI_MAX_RETRIES)

_oai = OpenAI(api_key=OPENAI_API_KEY, max_retries=OPENAI_MAX_RETRIES)
USAGE = {EXTRACT_MODEL: {"in": 0, "out": 0}, ANSWER_MODEL: {"in": 0, "out": 0}}
Q_WORKERS = 2                      # gpt-4o chỉ 30k TPM -> giữ ít luồng để tránh 429 (kèm backoff)
_usage_lock = threading.Lock()


def add_usage(model, usage):
    with _usage_lock:
        USAGE.setdefault(model, {"in": 0, "out": 0})
        USAGE[model]["in"] += usage.prompt_tokens
        USAGE[model]["out"] += usage.completion_tokens


def judge(q, ans, ref):
    r = _oai.chat.completions.create(
        model=JUDGE_MODEL, temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": 'You are a grader. Compare the answer with the reference answer. '
             'Return JSON {"verdict":"correct|partial|hallucinated","reason":"short"}. '
             '"hallucinated" = wrong or fabricated facts; "partial" = partially correct or incomplete; '
             '"correct" = matches the key facts.'},
            {"role": "user", "content": f"QUESTION: {q}\nREFERENCE ANSWER: {ref}\nANSWER TO GRADE: {ans}"},
        ])
    add_usage(JUDGE_MODEL, r.usage)
    try:
        return json.loads(r.choices[0].message.content)
    except Exception:
        return {"verdict": "partial", "reason": "parse-error"}


def run():
    t0 = time.time()
    G = nx.read_graphml(OUT_DIR / "graph.graphml")
    col = flat_rag.build_index()
    graph_rag.warm(G)   # tính sẵn embedding node (tránh tranh chấp khi chạy song song)
    questions = json.loads((ROOT / "benchmark_questions.json").read_text(encoding="utf-8"))

    def eval_q(it):
        q = it["q"]
        try:
            fa, fu, fsrc = flat_rag.answer(col, q)
            add_usage(ANSWER_MODEL, fu)
            ga, gu, gctx, ginfo = graph_rag.answer(G, q)
            add_usage(ANSWER_MODEL, gu)
            fj = judge(q, fa, it["ref"])
            gj = judge(q, ga, it["ref"])
            print(f"[bench] Q{it['id']:>2} {it['type']:<10} flat={fj['verdict']:<12} graph={gj['verdict']}")
            return {
                "id": it["id"], "type": it["type"], "q": q, "ref": it["ref"],
                "flat_answer": fa, "graph_answer": ga,
                "flat_verdict": fj["verdict"], "graph_verdict": gj["verdict"],
                "flat_reason": fj.get("reason", ""), "graph_reason": gj.get("reason", ""),
                "graph_linked": ", ".join(ginfo["linked_nodes"][:6]),
            }
        except Exception as ex:
            print(f"[bench] Q{it['id']} LỖI: {ex}")
            return {"id": it["id"], "type": it["type"], "q": q, "ref": it["ref"],
                    "flat_answer": "", "graph_answer": "", "flat_verdict": "error",
                    "graph_verdict": "error", "flat_reason": str(ex)[:80],
                    "graph_reason": "", "graph_linked": ""}

    # Chấm 20 câu SONG SONG (mỗi câu = Flat + Graph + 2 judge)
    rows = []
    with ThreadPoolExecutor(max_workers=Q_WORKERS) as pool:
        futs = [pool.submit(eval_q, it) for it in questions]
        for fut in as_completed(futs):
            rows.append(fut.result())
    rows.sort(key=lambda r: r["id"])

    seconds = time.time() - t0

    # CSV
    with open(OUT_DIR / "benchmark.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # Markdown
    def short(s, n=90):
        s = (s or "").replace("\n", " ").strip()
        return s[:n] + ("…" if len(s) > n else "")

    def emoji(v):
        return {"correct": "✅", "partial": "🟡", "hallucinated": "❌"}.get(v, v)

    n_flat_ok = sum(r["flat_verdict"] == "correct" for r in rows)
    n_graph_ok = sum(r["graph_verdict"] == "correct" for r in rows)
    n_flat_hal = sum(r["flat_verdict"] == "hallucinated" for r in rows)
    n_graph_hal = sum(r["graph_verdict"] == "hallucinated" for r in rows)

    md = []
    md.append("# Bảng so sánh Flat RAG vs GraphRAG (20 câu benchmark)\n")
    md.append(f"- **Flat RAG**: correct={n_flat_ok}/20, hallucinated={n_flat_hal}")
    md.append(f"- **GraphRAG**: correct={n_graph_ok}/20, hallucinated={n_graph_hal}\n")
    md.append("| # | Loại | Câu hỏi | Flat | Graph |")
    md.append("|---|------|---------|------|-------|")
    for r in rows:
        md.append(f"| {r['id']} | {r['type']} | {short(r['q'], 60)} | "
                  f"{emoji(r['flat_verdict'])} | {emoji(r['graph_verdict'])} |")

    md.append("\n## Chi tiết câu trả lời\n")
    for r in rows:
        md.append(f"**Q{r['id']} ({r['type']}). {r['q']}**  ")
        md.append(f"- *Đáp án đúng:* {r['ref']}  ")
        md.append(f"- Flat {emoji(r['flat_verdict'])}: {short(r['flat_answer'], 200)}  ")
        md.append(f"- Graph {emoji(r['graph_verdict'])}: {short(r['graph_answer'], 200)}  ")
        md.append("")

    md.append("## ⭐ Trường hợp Flat RAG ảo giác/sai nhưng GraphRAG trả lời đúng\n")
    hi = [r for r in rows if r["flat_verdict"] in ("hallucinated", "partial")
          and r["graph_verdict"] == "correct"]
    if hi:
        for r in hi:
            md.append(f"- **Q{r['id']}. {r['q']}**")
            md.append(f"  - Flat ({r['flat_verdict']}): _{short(r['flat_answer'], 160)}_")
            md.append(f"  - Graph (correct): _{short(r['graph_answer'], 160)}_")
            md.append(f"  - Node đồ thị dùng: {r['graph_linked']}")
    else:
        md.append("_(Không có — xem phân tích trong report.md.)_")

    (OUT_DIR / "benchmark.md").write_text("\n".join(md), encoding="utf-8")

    # lưu cost querying
    (OUT_DIR / "cost_query.json").write_text(json.dumps(
        {"usage": USAGE, "seconds": seconds, "n_questions": len(rows)},
        indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[bench] XONG {len(rows)} câu trong {seconds:.1f}s. "
          f"Flat correct={n_flat_ok}, Graph correct={n_graph_ok}.")


if __name__ == "__main__":
    run()
