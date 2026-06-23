"""Step 1 — Indexing: trích xuất thực thể + quan hệ bằng langextract (backend OpenAI).

- Mỗi 'relationship' -> 1 triple (subject, relation, object).
- Mỗi entity (organization/person/product/location) -> node có kiểu.
- Checkpoint theo từng doc trong outputs/triples_by_doc/ để chạy lại không tốn token.
- Ước lượng token (tiktoken) + đo thời gian -> outputs/cost_index.json (phục vụ Deliverable 4).
"""
import json
import math
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import tiktoken
import langextract as lx

from src.config import (OUT_DIR, TRIPLE_DIR, EXTRACT_MODEL, OPENAI_API_KEY,
                        MAX_CHAR_BUFFER, MAX_WORKERS, DOC_WORKERS)

ENC = tiktoken.get_encoding("cl100k_base")

PROMPT = (
    "You are an information-extraction system building a KNOWLEDGE GRAPH for the US electric-vehicle (EV) "
    "industry. Clearly separate ENTITIES (nodes) — company/organization, person, product (vehicle model), "
    "location, policy — from ATTRIBUTES/VALUES (metric, money, percentage, date), which must be attached to an "
    "entity THROUGH a relation. For every relationship, emit an extraction with class='relationship' whose "
    "attributes are subject, relation (UPPER_SNAKE_CASE) and object. "
    "IMPORTANT rule about subject: the subject MUST be a named entity (company / person / vehicle model / "
    "policy / organization). If a figure is market-wide (not tied to a specific company), use the subject "
    "'US EV market'. Avoid vague subjects (e.g. 'sales data', 'EV share', 'Sales in Q1'). "
    "Only use information present in the text; never fabricate."
)

EXAMPLES = [
    lx.data.ExampleData(
        text=("In Q1 2024, Tesla's share of the US EV market was 51.3%, down from 61.7% a year "
              "earlier. Tesla is led by Elon Musk. Ford's EV sales rose 86.1% year over year, the "
              "second-highest volume behind Tesla. The Inflation Reduction Act offers a $7,500 credit."),
        extractions=[
            lx.data.Extraction("organization", "Tesla", attributes={"type": "company"}),
            lx.data.Extraction("organization", "Ford", attributes={"type": "company"}),
            lx.data.Extraction("person", "Elon Musk", attributes={"type": "person"}),
            lx.data.Extraction("organization", "Inflation Reduction Act",
                               attributes={"type": "policy"}),
            lx.data.Extraction("relationship", "is led by",
                               attributes={"subject": "Tesla", "relation": "LED_BY",
                                           "object": "Elon Musk"}),
            lx.data.Extraction("relationship", "share of the US EV market was 51.3%",
                               attributes={"subject": "Tesla", "relation": "US_EV_MARKET_SHARE",
                                           "object": "51.3% (Q1 2024, down from 61.7%)"}),
            lx.data.Extraction("relationship", "EV sales rose 86.1% year over year",
                               attributes={"subject": "Ford", "relation": "EV_SALES_GROWTH_YOY",
                                           "object": "86.1% (Q1 2024)"}),
            lx.data.Extraction("relationship", "offers a $7,500 credit",
                               attributes={"subject": "Inflation Reduction Act",
                                           "relation": "OFFERS_CREDIT", "object": "$7,500 per EV"}),
        ],
    )
]

PROMPT_OVERHEAD = len(ENC.encode(PROMPT)) + sum(
    len(ENC.encode(e.text)) for e in EXAMPLES) + 200  # token cố định gửi mỗi chunk


def extract_doc(text: str):
    return lx.extract(
        text_or_documents=text,
        prompt_description=PROMPT,
        examples=EXAMPLES,
        model_id=EXTRACT_MODEL,
        api_key=OPENAI_API_KEY,
        fence_output=True,             # bắt buộc với OpenAI
        use_schema_constraints=False,  # langextract chưa hỗ trợ schema cho OpenAI
        max_char_buffer=MAX_CHAR_BUFFER,
        max_workers=MAX_WORKERS,
        extraction_passes=1,
    )


def parse_result(res, doc_id):
    triples, entities = [], []
    for e in res.extractions:
        attrs = e.attributes or {}
        if e.extraction_class == "relationship":
            if attrs.get("subject") and attrs.get("object"):
                triples.append({
                    "subject": str(attrs["subject"]).strip(),
                    "relation": str(attrs.get("relation", "RELATED_TO")).strip().upper().replace(" ", "_"),
                    "object": str(attrs["object"]).strip(),
                    "doc_id": doc_id,
                    "evidence": e.extraction_text,
                })
        elif e.extraction_class in {"organization", "person", "product", "location"}:
            entities.append({"entity": e.extraction_text.strip(),
                             "etype": e.extraction_class,
                             "subtype": attrs.get("type", "")})
    return triples, entities


def _process_doc(d):
    """Trích xuất 1 doc (chạy trong thread). Trả (status, doc_id, payload)."""
    ckpt = TRIPLE_DIR / f"{d['doc_id']}.json"
    if ckpt.exists():
        return ("cached", d["doc_id"], None)
    t0 = time.time()
    try:
        res = extract_doc(d["text"])
    except Exception as ex:
        return ("error", d["doc_id"], str(ex))
    dt = time.time() - t0
    triples, entities = parse_result(res, d["doc_id"])
    ckpt.write_text(json.dumps({"triples": triples, "entities": entities},
                               ensure_ascii=False), encoding="utf-8")
    n_chunks = max(1, math.ceil(len(d["text"]) / MAX_CHAR_BUFFER))
    out_tok = len(ENC.encode(json.dumps(triples + entities, ensure_ascii=False)))
    return ("ok", d["doc_id"], {
        "res": res, "dt": dt, "n_triples": len(triples), "n_entities": len(entities),
        "in_tok": d["n_tokens"] + n_chunks * PROMPT_OVERHEAD, "out_tok": out_tok})


def run():
    docs = [json.loads(l) for l in
            (OUT_DIR / "clean_docs.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    cost = {"in_tokens_est": 0, "out_tokens_est": 0, "seconds": 0.0, "compute_seconds": 0.0,
            "docs_processed": 0, "docs_cached": 0, "model": EXTRACT_MODEL}
    annotated = []
    lock = threading.Lock()
    done = 0
    wall0 = time.time()

    # Trích xuất SONG SONG ở cấp document (mỗi doc lại tự song song ở cấp chunk)
    with ThreadPoolExecutor(max_workers=DOC_WORKERS) as pool:
        futs = [pool.submit(_process_doc, d) for d in docs]
        for fut in as_completed(futs):
            status, doc_id, payload = fut.result()
            with lock:
                done += 1
                if status == "cached":
                    cost["docs_cached"] += 1
                elif status == "error":
                    print(f"[extract] LỖI {doc_id}: {payload}")
                else:
                    annotated.append(payload["res"])
                    cost["in_tokens_est"] += payload["in_tok"]
                    cost["out_tokens_est"] += payload["out_tok"]
                    cost["compute_seconds"] += payload["dt"]
                    cost["docs_processed"] += 1
                    print(f"[extract] {done}/{len(docs)} {doc_id}: "
                          f"{payload['n_triples']} triples, {payload['n_entities']} entities, "
                          f"{payload['dt']:.1f}s")
    cost["seconds"] = time.time() - wall0   # thời gian THỰC (wall-clock) của cả pha indexing

    # gộp triples.jsonl tổng từ tất cả checkpoint
    all_triples, all_entities = [], []
    for ckpt in sorted(TRIPLE_DIR.glob("*.json")):
        obj = json.loads(ckpt.read_text(encoding="utf-8"))
        all_triples += obj["triples"]
        all_entities += obj["entities"]
    (OUT_DIR / "triples.jsonl").write_text(
        "\n".join(json.dumps(t, ensure_ascii=False) for t in all_triples), encoding="utf-8")
    (OUT_DIR / "entities.jsonl").write_text(
        "\n".join(json.dumps(e, ensure_ascii=False) for e in all_entities), encoding="utf-8")

    # cộng dồn token/doc cũ nếu chạy nhiều lần (KHÔNG cộng 'seconds' vì đó là wall-clock)
    cf = OUT_DIR / "cost_index.json"
    if cf.exists():
        old = json.loads(cf.read_text())
        for k in ("in_tokens_est", "out_tokens_est", "compute_seconds", "docs_processed"):
            cost[k] += old.get(k, 0)
    cf.write_text(json.dumps(cost, indent=2), encoding="utf-8")

    # lưu annotated + html trực quan hoá langextract (best-effort)
    if annotated:
        try:
            lx.io.save_annotated_documents(annotated, output_dir=str(OUT_DIR),
                                           output_name="annotated.jsonl", show_progress=False)
            html = lx.visualize(str(OUT_DIR / "annotated.jsonl"))
            (OUT_DIR / "extraction.html").write_text(getattr(html, "data", html), encoding="utf-8")
        except Exception as ex:
            print(f"[extract] bỏ qua visualize: {ex}")

    print(f"[extract] XONG: {len(all_triples)} triples, {len(all_entities)} entities "
          f"(mới {cost['docs_processed']} doc, cache {cost['docs_cached']} doc).")


if __name__ == "__main__":
    run()
