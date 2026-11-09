#!/bin/bash
# 从50秒时序数据中计算真实QoS指标

TS_DIR="/home/suwen/reproduce/time_series_50s"
OUTPUT="/home/suwen/reproduce/qos_metrics_50s_truthful.csv"

echo "run_index,algorithm,seed,throughput_mbps,delay_ms,plr_pct" > "$OUTPUT"

for algo in laavha topsis-q gra strongest-signal vikor; do
    echo "处理算法: $algo"

    for csv in "$TS_DIR"/ts_run*_${algo}_seed*.csv; do
        [ -f "$csv" ] || continue

        # 提取run_index和seed
        fname=$(basename "$csv" .csv)
        run_idx=$(echo "$fname" | sed 's/ts_run\([0-9]*\)_.*/\1/')
        seed=$(echo "$fname" | sed 's/.*_seed\([0-9]*\)/\1/')

        # 使用awk计算：每行根据current_net选择对应网络的QoS，然后求均值
        result=$(awk -F',' '
        NR==1 {
            # 找到列索引
            for(i=1;i<=NF;i++) {
                if($i=="current_net") cn=i
                if($i=="throughput_5g") t5=i
                if($i=="delay_5g") d5=i
                if($i=="plr_5g") p5=i
                if($i=="throughput_lte") tl=i
                if($i=="delay_lte") dl=i
                if($i=="plr_lte") pl=i
                if($i=="throughput_wifi") tw=i
                if($i=="delay_wifi") dw=i
                if($i=="plr_wifi") pw=i
            }
            next
        }
        {
            net=$cn
            if(net==0) { thr=$t5; dly=$d5; plr=$p5 }
            else if(net==1) { thr=$tl; dly=$dl; plr=$pl }
            else { thr=$tw; dly=$dw; plr=$pw }

            sum_thr+=thr
            sum_dly+=dly
            sum_plr+=plr
            cnt++
        }
        END {
            if(cnt>0) {
                printf "%.4f,%.4f,%.4f", sum_thr/cnt, sum_dly/cnt, (sum_plr/cnt)*100
            } else {
                printf "0.0000,0.0000,0.0000"
            }
        }
        ' "$csv")

        echo "$run_idx,$algo,$seed,$result" >> "$OUTPUT"
    done
done

echo ""
echo "结果已保存到: $OUTPUT"
echo ""
echo "===== 各算法QoS统计 ====="

for algo in laavha topsis-q gra strongest-signal vikor; do
    echo ""
    echo "$algo:"
    awk -F',' -v a="$algo" '
    NR==1 {next}
    $2==a {
        thr[NR]=$4; dly[NR]=$5; plr[NR]=$6
        n++
    }
    END {
        if(n==0) {print "  无数据"; exit}

        # 计算均值
        for(i in thr) { sum_thr+=thr[i]; sum_dly+=dly[i]; sum_plr+=plr[i] }
        mean_thr=sum_thr/n
        mean_dly=sum_dly/n
        mean_plr=sum_plr/n

        # 计算标准差
        for(i in thr) {
            var_thr+=(thr[i]-mean_thr)^2
            var_dly+=(dly[i]-mean_dly)^2
            var_plr+=(plr[i]-mean_plr)^2
        }
        std_thr=sqrt(var_thr/n)
        std_dly=sqrt(var_dly/n)
        std_plr=sqrt(var_plr/n)

        printf "  吞吐量: %.2f ± %.2f Mbps\n", mean_thr, std_thr
        printf "  延迟:   %.2f ± %.2f ms\n", mean_dly, std_dly
        printf "  丢包率: %.2f ± %.2f %%\n", mean_plr, std_plr
        printf "  样本数: %d\n", n
    }
    ' "$OUTPUT"
done
