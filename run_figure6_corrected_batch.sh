#!/bin/bash
# Figure 6 修正实验批量运行脚本
# 在 ns-3.45 目录中执行，三个算法使用相同种子

set -e

NS3_DIR="/home/suwen/ns-3.45"
WORK_DIR="/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover"
OUTPUT_DIR="/home/suwen/reproduce/time_series_figure6_corrected"
DURATION=10.0
PERIOD=0.1

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 使用论文中声称的 seed=200（图标题中明确标注）
# 以及附近的几个种子用于验证一致性
SEEDS=(200 201 202 203 204)
ALGORITHMS=("laavha" "topsis-q" "fuzzy-vho")

echo "========================================"
echo "Figure 6 修正实验：相同种子公平对比"
echo "========================================"
echo "种子: ${SEEDS[@]}"
echo "算法: ${ALGORITHMS[@]}"
echo "输出目录: $OUTPUT_DIR"
echo ""

# 切换到 ns-3.45 的 laavha-handover 目录
cd "$WORK_DIR"

TOTAL=$((${#SEEDS[@]} * ${#ALGORITHMS[@]}))
COUNT=0

for seed in "${SEEDS[@]}"; do
    for algo in "${ALGORITHMS[@]}"; do
        COUNT=$((COUNT + 1))
        RUN_IDX=$((seed - 200))  # run0 对应 seed=200
        OUTPUT_FILE="$OUTPUT_DIR/ts_run${RUN_IDX}_${algo}_seed${seed}.csv"

        echo "[${COUNT}/${TOTAL}] 运行: ${algo} seed=${seed} (run${RUN_IDX})"

        conda run -n deeplearn python3 laavha_inference.py \
            --algorithm "$algo" \
            --ns3-arg duration="$DURATION" \
            --ns3-arg period="$PERIOD" \
            --ns3-arg flowmonMode=feed \
            --run-index "$RUN_IDX" \
            --ns3-arg RngRun="$seed" \
            --seed "$seed" \
            --ns3-arg randomizeScenario=true \
            --ns3-arg positionJitter=30.0 \
            --ns3-arg altitudeJitter=10.0 \
            --ns3-arg uavMobilityModel=constant-velocity \
            --time-series-output "$OUTPUT_FILE" \
            > /dev/null 2>&1

        if [ $? -eq 0 ]; then
            echo "  ✓ 完成: $OUTPUT_FILE"
        else
            echo "  ✗ 失败: ${algo} seed=${seed}"
        fi
    done
done

echo ""
echo "========================================"
echo "批量实验完成"
echo "生成文件数: $(ls -1 $OUTPUT_DIR/*.csv 2>/dev/null | wc -l)"
echo "========================================"
