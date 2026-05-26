# Design

## Starting Point

File:

```text
/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha_inference.py
```

Current launch:

```python
exp = Experiment(
    "ns3ai_laavha_handover",
    "../../../../",
    py_binding,
    handleFinish=True,
)
msg = exp.run(show_output=True)
```

Need to determine how `ns3ai_utils.Experiment` passes extra arguments to the ns-3 subprocess.

Inspect:

```text
/home/suwen/ns-3.45/contrib/ai/python_utils/ns3ai_utils.py
```

Use the existing API if it supports arguments. If not, make the smallest safe local change to the LAAVHA runner or document why direct support is unavailable.

## Preferred User Interface

Use repeated `--ns3-arg` flags:

```bash
python laavha_inference.py --ns3-arg flowmonMode=feed --ns3-arg duration=3.0
```

Then build the ns-3 argument list in the form expected by the ns3-ai Experiment.

If `Experiment` expects a command string, use:

```text
ns3ai_laavha_handover --flowmonMode=feed --duration=3.0
```

or the equivalent supported format.

## Backward Compatibility

No arguments should preserve current behavior:

```text
flowmonMode=log
duration=5.0
period=0.1
```

## Logging

At Python startup, print forwarded ns-3 arguments:

```text
[LAAVHA] Forwarding ns-3 args: ...
```

If no args:

```text
[LAAVHA] Forwarding ns-3 args: <none>
```

## Validation Matrix

Run:

```bash
python laavha_inference.py
python laavha_inference.py --ns3-arg flowmonMode=off
python laavha_inference.py --ns3-arg flowmonMode=feed
python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1
```

Expected:

- Default logs `flowmonMode=log`
- Off logs `flowmonMode=off`
- Feed logs `flowmonMode=feed`
- Duration 3.0 should produce 30 decisions if period is 0.1

## Risks

If `ns3ai_utils.Experiment` cannot forward arguments, do not rewrite the utility globally without review. Prefer a local runner workaround or document the limitation.
