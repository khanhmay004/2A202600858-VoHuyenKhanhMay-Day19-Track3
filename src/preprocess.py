"""Step 0 — Làm sạch corpus.

- Parse header (Title / Link / Full Content).
- Bỏ boilerplate web (cookie, mailing list...).
- Phát hiện & bỏ doc nhị phân (dump PDF: doc_50, doc_60).
- Cap mỗi doc ~MAX_DOC_TOKENS token bằng tiktoken.
=> outputs/clean_docs.jsonl + outputs/skipped_docs.log
"""
import json
import re
import tiktoken

from src.config import DATA_DIR, OUT_DIR, MAX_DOC_TOKENS

ENC = tiktoken.get_encoding("cl100k_base")
BOILER = [
    r"We use cookies.*", r"This website uses cookies.*", r"Join our mailing list.*",
    r"Essential cookies.*", r"We use Google Analytics.*", r"Contact Us\s*$",
    r"\*Terms and conditions apply.*", r"Don't miss out!.*",
]


def parse_fields(raw: str):
    def grab(tag):
        m = re.search(rf"^{tag}:\s*(.*)$", raw, re.MULTILINE)
        return m.group(1).strip() if m else ""
    query, title, link = grab("Query"), grab("Title"), grab("Link")
    snippet = grab("Snippet")
    body = raw.split("Full Content:", 1)[-1] if "Full Content:" in raw else raw
    return query, title, link, snippet, body


def is_binary(text: str) -> bool:
    head = text[:20000]
    if not head:
        return True
    if "endstreamendobj" in text or "stream\n" in head and "endobj" in head:
        return True
    printable = sum((c.isprintable() or c.isspace()) for c in head)
    if printable / max(1, len(head)) < 0.85:
        return True
    # Mật độ chữ cái thấp => dump bảng/PDF số liệu (vd doc_60: ~0.24, văn bản thường ~0.75)
    letters = sum(c.isalpha() for c in head)
    return letters / max(1, len(head)) < 0.5


def clean(text: str) -> str:
    for pat in BOILER:
        text = re.sub(pat, "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def cap(text: str, n=MAX_DOC_TOKENS) -> str:
    ids = ENC.encode(text)
    return ENC.decode(ids[:n]) if len(ids) > n else text


def run():
    files = sorted(DATA_DIR.glob("doc_*.txt"),
                   key=lambda p: int(re.findall(r"\d+", p.stem)[0]))
    rows, skipped = [], []
    for f in files:
        raw = f.read_text(encoding="utf-8", errors="ignore")
        query, title, link, snippet, body = parse_fields(raw)
        if is_binary(body):
            skipped.append(f"{f.name}\tbinary/pdf-dump")
            continue
        body = clean(body)
        # Gộp Query (chủ đề) + Title + Snippet vào nội dung để embed/extract có ngữ cảnh
        header = []
        if query:
            header.append(f"Topic: {query}")
        if title:
            header.append(f"Title: {title}")
        if snippet:
            header.append(f"Summary: {snippet}")
        text = cap("\n".join(header + ["", body]) if header else body)
        if len(text) < 200:
            skipped.append(f"{f.name}\ttoo-short")
            continue
        rows.append({"doc_id": f.stem, "query": query, "title": title, "url": link,
                     "snippet": snippet, "text": text, "n_tokens": len(ENC.encode(text))})

    (OUT_DIR / "clean_docs.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    (OUT_DIR / "skipped_docs.log").write_text("\n".join(skipped), encoding="utf-8")
    total_tok = sum(r["n_tokens"] for r in rows)
    print(f"[preprocess] giữ {len(rows)} doc, bỏ {len(skipped)} doc.")
    print(f"[preprocess] tổng token (đã cap) = {total_tok:,}")
    print(f"[preprocess] bỏ: {[s.split(chr(9))[0] for s in skipped]}")


if __name__ == "__main__":
    run()
