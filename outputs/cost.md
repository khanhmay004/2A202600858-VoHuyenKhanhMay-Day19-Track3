# Phân tích chi phí (Token & Thời gian)

| Pha | Model | Input tok | Output tok | USD | Ghi chú |
|-----|-------|-----------|------------|-----|---------|
| Indexing (extract) | gpt-4o-mini | 307,161 | 138,714 | $0.1293 | ~68 doc, 327s (ước lượng token) |
| Querying (bench) | gpt-4o-mini | 6,015 | 965 | $0.0015 | token chính xác từ usage |
| Querying (bench) | gpt-4o | 73,458 | 1,201 | $0.1957 | token chính xác từ usage |
| **TỔNG** |  | **386,634** | **140,880** | **$0.3264** |  |

- ⏱️ Thời gian xây đồ thị (indexing): **327s**
- ⏱️ Thời gian chạy 20 câu benchmark (Flat+Graph+Judge): **116s**
- 💡 Token indexing là *ước lượng* (langextract không trả usage); token querying là *chính xác*.