"""Cấu hình chung + nạp OPENAI_API_KEY từ .env (không hardcode key)."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "dataset"
OUT_DIR = ROOT / "outputs"
OUT_DIR.mkdir(exist_ok=True)
TRIPLE_DIR = OUT_DIR / "triples_by_doc"
TRIPLE_DIR.mkdir(exist_ok=True)


def _load_env():
    """Nạp .env thủ công (không phụ thuộc python-dotenv)."""
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
assert OPENAI_API_KEY, "Thiếu OPENAI_API_KEY (đặt trong .env hoặc export trước khi chạy)."

# ----- Model -----
EXTRACT_MODEL = "gpt-4o-mini"   # Step 1 — trích xuất triple
ANSWER_MODEL = "gpt-4o"         # Step 3/4 — TRẢ LỜI (Flat & Graph) bằng gpt-4o
JUDGE_MODEL = "gpt-4o-mini"     # LLM-judge — dùng mini (TPM cao) để tránh nghẽn 30k TPM của gpt-4o
EMBED_MODEL = "all-MiniLM-L6-v2"  # Flat RAG + xếp hạng triple trong subgraph (offline)
OPENAI_MAX_RETRIES = 8          # tự backoff khi gặp 429 (gpt-4o chỉ 30k TPM)

# ----- Tham số pipeline -----
MAX_DOC_TOKENS = 6000   # cap mỗi doc khi index
MAX_CHAR_BUFFER = 4000  # kích thước chunk (ký tự) langextract dùng để chia & trích
MAX_WORKERS = 2         # số luồng song song trong 1 doc (chunk-level) của langextract
DOC_WORKERS = 6         # số DOC trích xuất song song (doc-level) -> ~12 call đồng thời, tăng tốc ~6x
TOP_K = 5               # số chunk Flat RAG lấy về
HOP = 2                 # bán kính duyệt đồ thị (GraphRAG)

# ----- Đơn giá OpenAI (USD / 1 triệu token) để quy đổi chi phí -----
PRICING = {
    "gpt-4o-mini": {"in": 0.15, "out": 0.60},
    "gpt-4o": {"in": 2.50, "out": 10.00},
}
