# Tasks

## 1. Inspect ns3ai_utils

- [x] Read `/home/suwen/ns-3.45/contrib/ai/python_utils/ns3ai_utils.py`.
- [x] Identify how `Experiment` constructs the ns-3 command.
- [x] Determine whether extra arguments can be passed without modifying ns3ai_utils.

## 2. Add Python Argument Parsing

- [x] Add `argparse` or equivalent to `laavha_inference.py`.
- [x] Support repeated `--ns3-arg KEY=VALUE`.
- [x] Preserve default behavior when no args are provided.
- [x] Print forwarded args at startup.

## 3. Forward Args To ns-3

- [x] Pass forwarded args to the ns-3 subprocess using the supported `Experiment` mechanism.
- [x] If `Experiment` does not support this directly, implement the smallest local workaround.
- [x] Do not change message schema.

## 4. Validate Modes

- [x] Run default:

```bash
python laavha_inference.py
```

- [x] Run off mode:

```bash
python laavha_inference.py --ns3-arg flowmonMode=off
```

- [x] Run feed mode:

```bash
python laavha_inference.py --ns3-arg flowmonMode=feed
```

- [x] Run duration override:

```bash
python laavha_inference.py --ns3-arg duration=3.0 --ns3-arg period=0.1
```

## 5. Document Results

- [x] Create `/home/suwen/reproduce/openspec/changes/laavha-python-cli-forwarding/results.md`.
- [x] Record commands and decision counts.
- [x] Record whether C++ logs show requested modes.
- [x] State whether feed mode is stable through Python.

## 6. Report Back

- [x] List modified files.
- [x] State whether ns3ai_utils was modified.
- [x] State whether message schema changed.
- [x] Include validation matrix results.
- [x] Recommend whether default should switch to feed.
