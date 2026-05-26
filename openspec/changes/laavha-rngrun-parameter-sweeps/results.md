# RngRun & Parameter Sweeps Results

## Verdict

RngRun CLI parameter works. Sweep support added to batch runner. All validation passes.

## Modified Files

| File | Change |
|------|--------|
| `laavha-handover.cc` | Added `RngRun` CLI parameter + `RngSeedManager::SetRun()` + `#include <ns3/rng-seed-manager.h>` |
| `laavha_batch_runner.py` | Added `--sweep-duration`, `--sweep-period`, `--sweep-flowmonMode`; updated seed-base note |

## RngRun CLI Behavior

```
python laavha_inference.py --ns3-arg RngRun=7
```

C++ side parses `--RngRun=N`, calls `RngSeedManager::SetRun(N)` before any topology setup, and prints `RngRun=7` at startup.

## Sweep CLI Behavior

```bash
python laavha_batch_runner.py --runs 1 \
    --sweep-duration 3.0,5.0 --sweep-period 0.1 \
    --flowmonMode feed --seed-base 20 --output batch_sweep.csv
```

Expands to `len(durations) * len(periods) * len(modes) * runs` total runs. Each combo gets `runs` repetitions with incrementing seed.

## Validation

| Command | Result |
|---------|--------|
| `./ns3 build ns3ai_laavha_handover` | PASS |
| `python laavha_inference.py --ns3-arg RngRun=7` | 50 decisions, RngRun=7 printed |
| `python laavha_batch_runner.py --runs 2 ... --seed-base 10` | 2/2 OK |
| `python laavha_batch_runner.py --runs 1 --sweep-duration 3.0,5.0 ...` | 2/2 OK (2 combos) |

## CSV Samples

**batch_seed.csv:**
```csv
run_index,duration,period,flowmonMode,seed,return_code,elapsed_seconds,decisions,handover_count,final_net,error
0,3.0,0.1,feed,10,0,3.3,30,2,2,
1,3.0,0.1,feed,11,0,3.3,30,2,2,
```

**batch_sweep.csv:**
```csv
run_index,duration,period,flowmonMode,seed,return_code,elapsed_seconds,decisions,handover_count,final_net,error
0,3.0,0.1,feed,20,0,3.3,30,2,2,
1,5.0,0.1,feed,21,0,4.4,50,2,2,
```

## Do Different Seeds Change Results?

**No** — both seed=10 and seed=11 produce identical handover_count=2, final_net=2. This is expected because:
- Mobility is deterministic (ConstantVelocityMobilityModel)
- Traffic is constant-rate (OnOff at fixed DataRate)
- WiFi uses default rate control (Aarf) which is largely deterministic in this scenario

RngRun would matter with: random waypoint mobility, Poisson traffic, fading channels, or random initial positions.

## Next Steps

1. Add random perturbation (e.g., random initial position offset, or use RandomWalk2dMobilityModel) to make RngRun meaningful
2. Baseline algorithms (random, strongest-signal, fixed-network) for comparison
3. Plotting script to visualize sweep results
4. Longer duration experiments with more handover opportunities
