# Baselines and Plots Results

## Verdict

Three algorithms implemented and validated. Batch CSV includes algorithm field. Plot script generates summary and PNG.

## Modified/New Files

| File | Status |
|------|--------|
| `laavha_inference.py` | Modified: added `--algorithm`, `--fixed-net` |
| `laavha_batch_runner.py` | Rewritten: added `--algorithm`, `--sweep-algorithm`, algorithm CSV field |
| `laavha_plot.py` | **New**: summary + matplotlib PNG |

## Message Schema Modified

**No.**

## Algorithm CLI Behavior

```bash
python laavha_inference.py --algorithm laavha          # default model
python laavha_inference.py --algorithm strongest-signal # pick max SINR
python laavha_inference.py --algorithm fixed --fixed-net 2  # always WiFi
```

- `fixed` default is `--fixed-net 1` (LTE)
- `strongest-signal` picks network with highest SINR from latest timestep

## Batch CSV Fields

```
run_index, algorithm, duration, period, flowmonMode, seed,
return_code, elapsed_seconds, decisions, handover_count, final_net, error
```

## Plot/Summary Output

```
Algorithm: fixed
  avg handover_count: 1.00
  final_net distribution: {1: 2}

Algorithm: laavha
  avg handover_count: 1.50
  final_net distribution: {2: 1, 1: 1}

Algorithm: strongest-signal
  avg handover_count: 0.00
  final_net distribution: {0: 2}
```

PNG saved: `plots/handover_count_by_algorithm.png`

## CSV Sample

```csv
run_index,algorithm,duration,period,flowmonMode,seed,...,handover_count,final_net
0,laavha,3.0,0.1,feed,10,...,2,2
1,laavha,3.0,0.1,feed,11,...,1,1
2,strongest-signal,3.0,0.1,feed,12,...,0,0
3,strongest-signal,3.0,0.1,feed,13,...,0,0
4,fixed,3.0,0.1,feed,14,...,1,1
5,fixed,3.0,0.1,feed,15,...,1,1
```

## Next Steps

1. Time-series logging (per-step metrics CSV for detailed analysis)
2. More baselines (random, hysteresis-based)
3. Paper figure reproduction (multi-seed, longer duration)
4. Real handover execution (actual WiFi/LTE/5G association switching)
