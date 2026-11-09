#!/bin/bash
# 测试不同α值对laavha性能的影响
# α: 融合系数，控制当前状态vs预测状态的权重

NS3_DIR="/home/suwen/ns-3.45"
LAAVHA_PY="$NS3_DIR/contrib/ai/examples/laavha-handover/laavha_inference.py"
OUTPUT_DIR="/home/suwen/reproduce/alpha_test"

mkdir -p "$OUTPUT_DIR"

# 备份原文件
cp "$LAAVHA_PY" "${LAAVHA_PY}.backup"

for alpha in 0.9 0.8 0.7 0.6 0.5 0.4 0.3; do
    echo "========================================="
    echo "测试 α = $alpha"
    echo "========================================="

    # 修改α值
    sed -i "s/^FUSION_ALPHA = .*/FUSION_ALPHA = $alpha/" "$LAAVHA_PY"

    # 运行1个种子测试
    cd "$NS3_DIR/contrib/ai/examples/laavha-handover"
    python3 laavha_batch_runner.py \
        --runs 1 \
        --duration 50 \
        --start-seed 200 \
        --algorithm laavha \
        --time-series-dir "$OUTPUT_DIR/alpha_${alpha}" \
        --output "$OUTPUT_DIR/alpha_${alpha}.csv" \
        2>&1 | tail -10

    # 统计QoS
    if [ -f "$OUTPUT_DIR/alpha_${alpha}/ts_run0_laavha_seed200.csv" ]; then
        qos=$(awk -F',' '
        NR==1 {
            for(i=1;i<=NF;i++) {
                if($i=="current_net") cn=i
                if($i=="throughput_5g") t5=i
                if($i=="delay_5g") d5=i
                if($i=="throughput_lte") tl=i
                if($i=="delay_lte") dl=i
                if($i=="throughput_wifi") tw=i
                if($i=="delay_wifi") dw=i
            }
            next
        }
        {
            net=$cn
            if(net==0) { thr=$t5; dly=$d5 }
            else if(net==1) { thr=$tl; dly=$dl }
            else { thr=$tw; dly=$dw }
            sum_thr+=thr; sum_dly+=dly; cnt++
        }
        END {
            printf "avg_thr=%.4f avg_dly=%.2f", sum_thr/cnt, sum_dly/cnt
        }
        ' "$OUTPUT_DIR/alpha_${alpha}/ts_run0_laavha_seed200.csv")

        echo "  → $qos"
    fi

    echo ""
done

# 恢复原文件
cp "${LAAVHA_PY}.backup" "$LAAVHA_PY"

echo "测试完成，查看 $OUTPUT_DIR/*/ts_run0_laavha_seed200.csv"
