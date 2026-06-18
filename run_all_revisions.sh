#!/bin/bash
# ============================================================================
# LAAVHA 论文修订 — 主执行脚本
# 用法: bash /home/suwen/reproduce/run_all_revisions.sh
# ============================================================================
set -e

# Python 路径：deeplearn conda 环境（有 PyTorch）用于实验，
# 系统 python3 用于 docx 操作
PYTHON_DL=/home/suwen/miniconda3/envs/deeplearn/bin/python3
PYTHON_SYS=python3

echo "============================================"
echo "  LAAVHA 论文修订 — 自动化执行脚本"
echo "============================================"

# ---- Step 1: Paper revision (system python3 has python-docx) ----
echo ""
echo "[Step 1] 运行论文 .docx 修改脚本..."
cd /home/suwen/reproduce
$PYTHON_SYS apply_paper_revisions.py
echo "[Step 1] 完成。"

# ---- Step 2: Build ns-3 target ----
echo ""
echo "[Step 2] 编译 ns-3 仿真目标..."
cd /home/suwen/ns-3.45
./ns3 build ns3ai_laavha_handover
echo "[Step 2] 完成。"

# ---- Step 3: Run 50-run experiment batch (11 algorithms) ----
echo ""
echo "[Step 3] 运行 50 组 × 11 算法的批量实验..."
echo "  预计时间: ~1.5 小时 (550 runs × ~10s each)"
cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover

$PYTHON_DL laavha_batch_runner.py \
    --runs 50 \
    --duration 10.0 \
    --period 0.1 \
    --flowmonMode feed \
    --seed-base 200 \
    --randomizeScenario \
    --positionJitter 30 \
    --altitudeJitter 10 \
    --sweep-algorithm laavha,topsis-q,fuzzy-vho,saw,vikor,gra,copras,spotis,strongest-signal,laavha-l,laavha-a \
    --output batch_chapter3_v2.csv \
    --time-series-dir time_series_chapter3_v2

echo "[Step 3] 完成。输出文件: batch_chapter3_v2.csv"

# ---- Step 4: Generate figures ----
echo ""
echo "[Step 4] 生成论文图表..."
$PYTHON_DL laavha_plot.py \
    --input batch_chapter3_v2.csv \
    --time-series-dir time_series_chapter3_v2 \
    --output-dir plots_chapter3_v2 \
    --style publication \
    --dpi 300

echo "[Step 4] 完成。图表输出: plots_chapter3_v2/"

# ---- Step 5: Copy results back to reproduce/ ----
echo ""
echo "[Step 5] 复制结果到 reproduce 仓库..."
cp batch_chapter3_v2.csv /home/suwen/reproduce/
cp -r time_series_chapter3_v2 /home/suwen/reproduce/
cp -r plots_chapter3_v2 /home/suwen/reproduce/

echo ""
echo "============================================"
echo "  全部完成!"
echo "============================================"
