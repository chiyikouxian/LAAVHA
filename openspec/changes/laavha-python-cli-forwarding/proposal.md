# LAAVHA Python CLI Forwarding

## Why

FlowMonitor has been reintroduced into the LAAVHA/ns3-ai scheduled loop and is stable in default `flowmonMode=log`. The C++ side also implements `flowmonMode=feed`, but the standard Python runner cannot currently forward ns-3 command-line arguments.

As a result, `feed` mode cannot be validated through the normal run path:

```bash
python laavha_inference.py
```

This change adds a small argument-forwarding layer to the Python runner so C++ options can be tested without changing message schema or model code.

## What

Update `laavha_inference.py` to accept and forward ns-3 arguments to the `Experiment` launch.

Required use cases:

```bash
python laavha_inference.py --ns3-arg flowmonMode=feed
python laavha_inference.py --ns3-arg flowmonMode=off
python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1
```

Alternative accepted syntax:

```bash
python laavha_inference.py -- flowmonMode=feed duration=3.0
```

The implementation should choose one clear syntax and document it in the script/help text.

## Non-goals

- Do not change C++ message schema.
- Do not change model architecture.
- Do not change scoring logic unless needed for argument parsing.
- Do not add LTE/5G or new metrics.

## Deliverables

- Python runner supports passing ns-3 arguments to `ns3ai_utils.Experiment`.
- `flowmonMode=feed` can be run through the Python-launched path.
- Results are documented.

## Success Criteria

- Existing default run still works:

```bash
python laavha_inference.py
```

- Feed mode works:

```bash
python laavha_inference.py --ns3-arg flowmonMode=feed
```

- Off mode works:

```bash
python laavha_inference.py --ns3-arg flowmonMode=off
```

- C++ logs show the requested mode.
- 50 decisions complete for default duration.
