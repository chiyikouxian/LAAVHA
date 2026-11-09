#!/bin/bash
# Figure 6 修正实验：让三个算法在完全相同的种子下运行
# 目标：生成可用于公平对比的时间序列数据

set -e

OUTPUT_DIR="time_series_figure6_corrected"
BATCH_CSV="batch_figure6_corrected.csv"
DURATION=10.0
PERIOD=0.1

# 设置 ns3ai Python 绑定路径
export PYTHONPATH=/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover:$PYTHONPATH

# 使用论文声称的种子范围的前几个种子进行测试
# 完整实验应使用 200-249 共50个种子
TEST_SEEDS=(200 201 202 203 204)

echo "================================================================================"
echo "Figure 6 修正实验"
echo "================================================================================"
echo "输出目录: $OUTPUT_DIR"
echo "测试种子: ${TEST_SEEDS[@]}"
echo "仿真时长: ${DURATION}s (决策周期: ${PERIOD}s)"
echo ""
echo "【重要】此脚本将为三个算法在相同种子下生成可对比的时间序列数据"
echo "================================================================================"
echo ""

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 为每个种子运行三个算法
for seed in "${TEST_SEEDS[@]}"; do
    echo "--------------------------------------------------------------------------------"
    echo "种子 $seed: 开始运行三个算法"
    echo "--------------------------------------------------------------------------------"

    run_index=$((seed - 200))  # run0 对应 seed200

    for algo in laavha topsis-q fuzzy-vho; do
        echo "[$(date +%H:%M:%S)] 运行 $algo (seed=$seed, run_index=$run_index)"

        conda run -n deeplearn python3 laavha_batch_runner.py \
            --runs 1 \
            --duration "$DURATION" \
            --period "$PERIOD" \
            --flowmonMode feed \
            --seed-base "$seed" \
            --algorithm "$algo" \
            --time-series-dir "$OUTPUT_DIR" \
            --output "/tmp/batch_${algo}_seed${seed}.csv" \
            --randomizeScenario \
            --positionJitter 30.0 \
            --altitudeJitter 10.0 \
            2>&1 | tee "/tmp/log_${algo}_seed${seed}.txt"

        # 检查是否成功
        if [ $? -eq 0 ]; then
            echo "  ✓ $algo (seed=$seed) 完成"
        else
            echo "  ✗ $algo (seed=$seed) 失败"
            exit 1
        fi
    done

    echo ""
done

echo "================================================================================"
echo "实验完成"
echo "================================================================================"
echo "时间序列数据: $OUTPUT_DIR/"
echo ""
echo "【验证步骤】"
echo "1. 检查三个算法的 SINR 曲线是否完全一致："
echo "   python3 verify_same_scenario.py --seed 200 --ts-dir $OUTPUT_DIR"
echo ""
echo "2. 生成对比图表："
echo "   python3 generate_figure6_corrected.py --seed 200 --ts-dir $OUTPUT_DIR"
echo ""
echo "================================================================================"
