# Time-Series Logging Results

## Verdict

Per-decision time-series CSV logging works. Each run produces a CSV with 30 rows (for duration=3.0/period=0.1), containing all metrics, scores, and handover flags.

## Modified Files

| File | Change |
|------|--------|
| `laavha_inference.py` | Added `--time-series-output`, `--run-index`, `--seed`; collects per-step data and writes CSV |
| `laavha_batch_runner.py` | Added `--time-series-dir`; generates absolute paths for per-run time-series CSVs |

## Message Schema Modified

**No.**

## Time-Series CSV Fields

```
run_index, algorithm, seed, decision_index, sim_time,
current_net, target_net, handover,
score_5g, score_lte, score_wifi,
sinr_5g, rsrp_5g, delay_5g, throughput_5g, plr_5g,
sinr_lte, rsrp_lte, delay_lte, throughput_lte, plr_lte,
sinr_wifi, rsrp_wifi, delay_wifi, throughput_wifi, plr_wifi
```

## Validation

| Command | Result |
|---------|--------|
| `python laavha_inference.py` (default) | 50 decisions, no time-series written |
| `python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1 --time-series-output ts_single.csv` | 30 rows written |
| `batch_runner --sweep-algorithm laavha,strongest-signal --time-series-dir time_series` | 4/4 OK, 4 CSV files (31 lines each) |

## CSV Sample (first 3 rows)

```csv
run_index,algorithm,seed,decision_index,sim_time,current_net,target_net,handover,score_5g,score_lte,score_wifi,...
0,laavha,,0,0.000,0,1,1,0.017052,0.988856,0.011137,...
0,laavha,,1,0.100,1,1,0,0.021821,0.996362,0.003636,...
0,laavha,,2,0.200,1,1,0,0.020959,0.997839,0.002160,...
```

## Next Steps

1. Time-series plotting (SINR/score trajectories, handover event markers)
2. Paper figure reproduction using multi-seed batch data
3. Real handover execution (actual WiFi/LTE association switching)
4. Aggregate statistics across seeds (mean/std of metrics over time)
