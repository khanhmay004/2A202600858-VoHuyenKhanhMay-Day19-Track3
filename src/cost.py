"""Deliverable 4 — Phân tích chi phí (token + thời gian + USD).

Gộp:
- Indexing (langextract / gpt-4o-mini): token ƯỚC LƯỢNG bằng tiktoken + thời gian thực.
- Querying (Flat/Graph/Judge): token CHÍNH XÁC từ usage của OpenAI + thời gian thực.
=> outputs/cost.md + outputs/cost.json
"""
import json

from src.config import OUT_DIR, PRICING


def usd(model, tin, tout):
    p = PRICING.get(model, {"in": 0, "out": 0})
    return tin / 1e6 * p["in"] + tout / 1e6 * p["out"]


def run():
    idx = json.loads((OUT_DIR / "cost_index.json").read_text(encoding="utf-8")) \
        if (OUT_DIR / "cost_index.json").exists() else {}
    qry = json.loads((OUT_DIR / "cost_query.json").read_text(encoding="utf-8")) \
        if (OUT_DIR / "cost_query.json").exists() else {}

    rows = []  # (pha, model, in, out, usd, note)
    # --- Indexing ---
    im = idx.get("model", "gpt-4o-mini")
    i_in, i_out = idx.get("in_tokens_est", 0), idx.get("out_tokens_est", 0)
    rows.append(["Indexing (extract)", im, i_in, i_out, usd(im, i_in, i_out),
                 f"~{idx.get('docs_processed', 0)} doc, {idx.get('seconds', 0):.0f}s (ước lượng token)"])

    # --- Querying ---
    for model, u in qry.get("usage", {}).items():
        if u["in"] == 0 and u["out"] == 0:
            continue
        rows.append(["Querying (bench)", model, u["in"], u["out"],
                     usd(model, u["in"], u["out"]), "token chính xác từ usage"])

    total_in = sum(r[2] for r in rows)
    total_out = sum(r[3] for r in rows)
    total_usd = sum(r[4] for r in rows)
    idx_sec = idx.get("seconds", 0)
    qry_sec = qry.get("seconds", 0)

    out = {
        "rows": [{"phase": r[0], "model": r[1], "in_tokens": r[2], "out_tokens": r[3],
                  "usd": round(r[4], 4), "note": r[5]} for r in rows],
        "total_in_tokens": total_in, "total_out_tokens": total_out,
        "total_usd": round(total_usd, 4),
        "index_seconds": round(idx_sec, 1), "query_seconds": round(qry_sec, 1),
        "n_questions": qry.get("n_questions", 0),
    }
    (OUT_DIR / "cost.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    md = ["# Phân tích chi phí (Token & Thời gian)\n",
          "| Pha | Model | Input tok | Output tok | USD | Ghi chú |",
          "|-----|-------|-----------|------------|-----|---------|"]
    for r in rows:
        md.append(f"| {r[0]} | {r[1]} | {r[2]:,} | {r[3]:,} | ${r[4]:.4f} | {r[5]} |")
    md.append(f"| **TỔNG** |  | **{total_in:,}** | **{total_out:,}** | **${total_usd:.4f}** |  |\n")
    md.append(f"- ⏱️ Thời gian xây đồ thị (indexing): **{idx_sec:.0f}s**")
    md.append(f"- ⏱️ Thời gian chạy {out['n_questions']} câu benchmark (Flat+Graph+Judge): **{qry_sec:.0f}s**")
    md.append("- 💡 Token indexing là *ước lượng* (langextract không trả usage); token querying là *chính xác*.")
    (OUT_DIR / "cost.md").write_text("\n".join(md), encoding="utf-8")
    print(f"[cost] Tổng {total_in:,} in + {total_out:,} out token = ${total_usd:.4f}; "
          f"index {idx_sec:.0f}s, query {qry_sec:.0f}s.")


if __name__ == "__main__":
    run()
