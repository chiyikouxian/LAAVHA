# Prompt For Claude Code

You are Claude Code working in a shared project. Your role is implementation. Another assistant is responsible for architecture and code review. Please keep changes small, explicit, and easy to review.

Read these files first:

- `/home/suwen/reproduce/openspec/changes/laavha-ns3ai-smoke-test/proposal.md`
- `/home/suwen/reproduce/openspec/changes/laavha-ns3ai-smoke-test/design.md`
- `/home/suwen/reproduce/openspec/changes/laavha-ns3ai-smoke-test/tasks.md`

Then implement the change described there.

Important environment facts:

- Work area: `/home/suwen/reproduce`
- NS-3 root: `/home/suwen/ns-3.45`
- Conda env: `deeplearn`
- Python path: `/home/suwen/miniconda3/envs/deeplearn/bin/python`
- PyTorch works in `deeplearn`: `torch 2.2.2+cpu`
- ns3-ai is installed at `/home/suwen/ns-3.45/contrib/ai`
- `./ns3 build ai` already succeeds
- The ns3-ai struct-message A+B example has been verified and prints `get: 4`

Implementation goal:

Create a new ns3-ai smoke-test example for LAAVHA under:

```text
/home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
```

The example must prove this path:

```text
ns-3 C++ -> shared memory -> Python LAAVHA inference -> shared memory -> ns-3 C++
```

Use the struct-based ns3-ai message interface, not the old `py_interface.Ns3AIRLBase`.

The first runtime target is not full paper reproduction. It is a working integration smoke test with deterministic placeholder metrics.

Do not modify:

- `/home/suwen/reproduce/毕业论文完整版.pdf`
- `/home/suwen/reproduce/训练数据集.csv`
- `/home/suwen/reproduce/LAAVHA算法模型.pth`

Prefer not to modify ns3-ai framework files unless the build is blocked by a framework warning/error. If such a patch is unavoidable, explain it in your report.

Required verification:

```bash
cd /home/suwen/ns-3.45
conda activate deeplearn
./ns3 build ns3ai_laavha_handover
cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
python laavha_inference.py
```

When finished, report:

1. Added files
2. Modified files
3. Build command and result
4. Runtime command and result
5. Whether the model loaded or fallback random weights were used
6. Any points requiring architecture review
