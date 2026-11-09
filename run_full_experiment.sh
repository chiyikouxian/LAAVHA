#!/bin/bash
# =============================================================================
# 完整实验批量运行脚本
# 对应论文 Section 4.2：11 算法 × 250 seeds（seed 200~449）
# 总运行次数：2750 次，预计 27~30 小时
#
# 用法：
#   bash run_full_experiment.sh          # 全部算法
#   bash run_full_experiment.sh laavha   # 仅跑指定算法（断点续跑）
#
# 输出：
#   time_series_50s/ts_run{i}_{algo}_seed{s}.csv  每次运行的时间序列
#   results/batch_{algo}.csv                       每个算法的汇总结果
# =============================================================================

set -euo pipefail

# ── 路径配置 ──────────────────────────────────────────────────────────────────
LAAVHA_DIR="/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover"
TS_DIR="/home/suwen/reproduce/time_series_50s"
RESULT_DIR="/home/suwen/reproduce/results_exp2"
LOG_DIR="/home/suwen/reproduce/logs_exp2"

# ── 实验参数（对应论文 Table 2）──────────────────────────────────────────────
DURATION=50.0
PERIOD=0.1
SEED_BASE=200
RUNS=250
FLOWMON=feed
JITTER_POS=30.0
JITTER_ALT=10.0
MOBILITY=constant-velocity

# ── 11 个算法 ─────────────────────────────────────────────────────────────────
ALL_ALGORITHMS=(
    laavha
    topsis-q
    fuzzy-vho
    saw
    vikor
    gra
    copras
    spotis
    strongest-signal
    laavha-l
    laavha-a
)

# ── 参数解析：支持只跑指定算法 ───────────────────────────────────────────────
if [ $# -ge 1 ]; then
    ALGORITHMS=("$@")
    echo "[INFO] 仅运行指定算法: ${ALGORITHMS[*]}"
else
    ALGORITHMS=("${ALL_ALGORITHMS[@]}")
    echo "[INFO] 运行全部 11 个算法"
fi

# ── 准备目录 ──────────────────────────────────────────────────────────────────
mkdir -p "$TS_DIR" "$RESULT_DIR" "$LOG_DIR"

export PYTHONPATH="$LAAVHA_DIR:${PYTHONPATH:-}"

# ── 主循环：按算法顺序依次运行 ───────────────────────────────────────────────
TOTAL_START=$(date +%s)
echo "========================================================================"
echo "实验开始：$(date)"
echo "参数：duration=${DURATION}s  period=${PERIOD}s  seeds=${SEED_BASE}~$((SEED_BASE+RUNS-1))"
echo "      positionJitter=${JITTER_POS}m  altitudeJitter=${JITTER_ALT}m"
echo "========================================================================"

for ALGO in "${ALGORITHMS[@]}"; do
    ALGO_START=$(date +%s)
    OUTCSV="$RESULT_DIR/batch_${ALGO}.csv"
    LOGFILE="$LOG_DIR/run_${ALGO}.log"

    echo ""
    echo "────────────────────────────────────────────────────────────────────"
    echo "算法：${ALGO}  ($(date +%H:%M:%S))"
    echo "输出：${OUTCSV}"
    echo "日志：${LOGFILE}"
    echo "────────────────────────────────────────────────────────────────────"

    cd "$LAAVHA_DIR"
    conda run -n deeplearn python3 "$LAAVHA_DIR/laavha_batch_runner.py" \
        --runs "$RUNS" \
        --duration "$DURATION" \
        --period "$PERIOD" \
        --flowmonMode "$FLOWMON" \
        --seed-base "$SEED_BASE" \
        --algorithm "$ALGO" \
        --randomizeScenario \
        --positionJitter "$JITTER_POS" \
        --altitudeJitter "$JITTER_ALT" \
        --ns3-arg "uavMobilityModel=${MOBILITY}" \
        --time-series-dir "$TS_DIR" \
        --output "$OUTCSV" \
        2>&1 | tee "$LOGFILE"

    ALGO_END=$(date +%s)
    ALGO_ELAPSED=$(( (ALGO_END - ALGO_START) / 60 ))
    echo "[完成] ${ALGO}：耗时 ${ALGO_ELAPSED} 分钟，结果 → ${OUTCSV}"
done

# ── 汇总 ─────────────────────────────────────────────────────────────────────
TOTAL_END=$(date +%s)
TOTAL_ELAPSED=$(( (TOTAL_END - TOTAL_START) / 60 ))

echo ""
echo "========================================================================"
echo "全部实验完成：$(date)"
echo "总耗时：${TOTAL_ELAPSED} 分钟"
echo "时间序列目录：${TS_DIR}/"
echo "汇总结果目录：${RESULT_DIR}/"
echo "========================================================================"
echo ""
echo "下一步："
echo "  绘图（实验 2/3/4 图表）："
echo "    python3 /home/suwen/reproduce/regenerate_figures.py"
echo "  参数敏感度图（实验 1）："
echo "    python3 /home/suwen/reproduce/experiments/parameter_sensitivity.py"
echo "  ALERA 验证图（实验 5）："
echo "    python3 /home/suwen/reproduce/experiments/enhanced_proof_experiments.py"
