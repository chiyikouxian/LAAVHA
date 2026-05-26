# Batch Experiment Runner Results

## Verdict

Batch runner works. 3/3 runs completed successfully, CSV written with all fields.

## New Files

- `laavha_batch_runner.py` — standalone batch experiment runner

## Modified Files

None. `laavha_inference.py` was not modified.

## CLI Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--runs` | 3 | Number of experiment runs |
| `--duration` | 5.0 | Simulation duration (seconds) |
| `--period` | 0.1 | Decision period (seconds) |
| `--flowmonMode` | feed | FlowMonitor mode (off/log/feed) |
| `--output` | batch_results.csv | Output CSV path |
| `--seed-base` | None | Base RNG seed (ns-3 RngRun, not yet verified) |
| `--stop-on-failure` | false | Stop batch on first failure |

## CSV Fields

```
run_index, duration, period, flowmonMode, seed, return_code,
elapsed_seconds, decisions, handover_count, final_net, error
```

## CSV Sample

```csv
run_index,duration,period,flowmonMode,seed,return_code,elapsed_seconds,decisions,handover_count,final_net,error
0,3.0,0.1,feed,,0,3.2,30,2,2,
1,3.0,0.1,feed,,0,3.3,30,2,2,
2,3.0,0.1,feed,,0,3.3,30,2,2,
```

## Validation

```bash
cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
conda activate deeplearn
python laavha_batch_runner.py --runs 3 --duration 3.0 --period 0.1 --flowmonMode feed --output batch_results.csv
```

Output:
```
[batch] run 0: OK, decisions=30, handovers=2, elapsed=3.2s
[batch] run 1: OK, decisions=30, handovers=2, elapsed=3.3s
[batch] run 2: OK, decisions=30, handovers=2, elapsed=3.3s
[batch] Done. 3 runs written to batch_results.csv
[batch] 3/3 succeeded.
```

## Seed Note

The `--seed-base` parameter forwards `RngRun=N` to ns-3, but the C++ side does not currently parse this CLI arg. All runs currently produce identical results. To enable stochastic variation, `RngRun` support would need to be added to `laavha-handover.cc` Configure().
