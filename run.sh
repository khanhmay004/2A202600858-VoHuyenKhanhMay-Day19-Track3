#!/usr/bin/env bash
# Orchestrator — chạy toàn bộ pipeline GraphRAG trong conda env `main`.
# Cách dùng:  bash run.sh
set -e

source /c/Users/ADMIN/miniconda3/etc/profile.d/conda.sh
conda activate main

cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"
export PYTHONUTF8=1            # in được tiếng Việt trên console Windows
export PYTHONIOENCODING=utf-8

echo "============================================================"
echo " LAB DAY 19 — GraphRAG pipeline (conda main)"
echo "============================================================"

for step in preprocess extract build_graph visualize benchmark cost; do
  echo ""
  echo ">>> STEP: $step"
  python -m "src.$step"
done

echo ""
echo "============================================================"
echo " HOÀN TẤT. Xem thư mục outputs/ và report.md"
echo "============================================================"
