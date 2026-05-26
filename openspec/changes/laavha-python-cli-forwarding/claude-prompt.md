# Prompt For Claude Code

You are Claude Code working in a shared project. Your role is implementation. Another assistant is responsible for architecture and code review.

Read these files first:

- `/home/suwen/reproduce/openspec/changes/laavha-python-cli-forwarding/proposal.md`
- `/home/suwen/reproduce/openspec/changes/laavha-python-cli-forwarding/design.md`
- `/home/suwen/reproduce/openspec/changes/laavha-python-cli-forwarding/tasks.md`

Then implement the change.

Goal:

Allow the Python LAAVHA runner to forward ns-3 CLI args so we can validate:

```text
flowmonMode=off
flowmonMode=log
flowmonMode=feed
duration
period
```

Primary file:

```text
/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover/laavha_inference.py
```

Inspect first:

```text
/home/suwen/ns-3.45/contrib/ai/python_utils/ns3ai_utils.py
```

Do not modify unless necessary:

```text
laavha_msg.h
laavha_py.cc
laavha-handover.cc
```

Preferred CLI:

```bash
python laavha_inference.py --ns3-arg flowmonMode=feed
python laavha_inference.py --ns3-arg flowmonMode=off
python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1
```

Requirements:

- Default `python laavha_inference.py` still works.
- Print forwarded ns-3 args at startup.
- Preserve model loading and inference logic.
- Preserve message schema.
- Do not change LAAVHA model architecture.
- Avoid modifying global `ns3ai_utils.py` unless there is no local alternative.

Validation:

```bash
cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
conda activate deeplearn
python laavha_inference.py
python laavha_inference.py --ns3-arg flowmonMode=off
python laavha_inference.py --ns3-arg flowmonMode=feed
python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1
```

Expected:

- default logs `flowmonMode=log`
- off logs `flowmonMode=off`
- feed logs `flowmonMode=feed`
- duration=3.0 period=0.1 produces 30 decisions
- feed mode completes through the Python-launched path

Write results:

```text
/home/suwen/reproduce/openspec/changes/laavha-python-cli-forwarding/results.md
```

Report back:

1. Modified files
2. Whether ns3ai_utils was modified
3. Whether message schema changed
4. Validation matrix result
5. Whether feed mode is stable through Python
6. Recommendation on switching default to feed
