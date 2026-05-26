# Randomized Scenario Perturbations Results

## Verdict

Randomization works. Different RngRun values now produce different UAV initial positions and different handover outcomes.

## Modified Files

| File | Change |
|------|--------|
| `laavha-handover.cc` | Added `randomizeScenario`, `positionJitter`, `altitudeJitter` CLI params; UniformRandomVariable sampling; `m_initialPosOffsetX/Y` members |
| `laavha_batch_runner.py` | Added `--randomizeScenario`, `--positionJitter`, `--altitudeJitter`, `--ns3-arg` passthrough |

## Message Schema Modified

**No.**

## New CLI Parameters (C++)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--randomizeScenario` | false | Enable random perturbations |
| `--positionJitter` | 0.0 | Max x/y offset (m) |
| `--altitudeJitter` | 0.0 | Max altitude offset (m) |

## Default Deterministic Preserved

```
RngRun=1 randomizeScenario=false positionJitter=0 altitudeJitter=0
Sampled initial: x_offset=0 y_offset=0 altitude=100
decisions: 50
```

## Different RngRun Sampled Positions

| RngRun | x_offset | y_offset | altitude |
|--------|----------|----------|----------|
| 10 | -7.198 | 0.882 | 100.686 |
| 11 | -17.322 | 7.971 | 97.046 |

## batch_random.csv

```csv
run_index,duration,period,flowmonMode,seed,return_code,elapsed_seconds,decisions,handover_count,final_net,error
0,3.0,0.1,feed,10,0,3.3,30,2,2,
1,3.0,0.1,feed,11,0,3.2,30,1,1,
```

## Does Randomization Change Handover Outcomes?

**Yes.** Run 0 (seed=10): handovers=2, final_net=2 (WiFi). Run 1 (seed=11): handovers=1, final_net=1 (LTE). The different initial positions change the UAV-AP/eNB distances, affecting signal quality and triggering different handover decisions.

## Next Steps

1. Baseline algorithms (random, fixed, strongest-signal) for comparison
2. Plotting script to visualize handover count distribution across seeds
3. Larger batch runs (e.g. 20-50 seeds) to build statistical confidence
4. Real handover execution (actual WiFi/LTE association switching)
