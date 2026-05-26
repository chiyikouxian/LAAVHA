# Claude Prompt

```text
你现在在 /home/suwen/ns-3.45 中工作。OpenSpec 共享工作区在：

  /home/suwen/reproduce/openspec

当前 change：

  laavha-rngrun-parameter-sweeps

目标：
让 LAAVHA 批量实验支持可复现随机运行编号和简单参数 sweep。

当前状态：
- laavha_batch_runner.py 已存在，可多次 subprocess 调用 laavha_inference.py 并输出 CSV。
- --seed-base 已存在，但 C++ 侧暂未解析 RngRun，所以多次运行目前结果相同。
- 三候选网络在 flowmonMode=feed 下都有 ns-3 仿真驱动指标，但 5G 是 P2P proxy，不是真 NR。

任务：
1. 修改 laavha-handover.cc：
   - 添加 RngRun CLI 参数。
   - 使用 ns3::RngSeedManager::SetRun(rngRun)。
   - 必须在 topology/mobility/application setup 前调用。
   - 启动日志打印 active RngRun。
2. 修改 laavha_batch_runner.py：
   - 确认 --seed-base 会为每次 run 转发 --ns3-arg RngRun=<seed>。
   - CSV seed 字段记录实际 seed。
   - 添加 sweep 参数：
     --sweep-duration 例如 3.0,5.0
     --sweep-period 例如 0.05,0.1
     --sweep-flowmonMode 例如 feed,off
   - 如果 sweep 参数存在，用 sweep 值覆盖 scalar 参数。
   - 展开为参数组合；每个组合运行 --runs 次。
   - 打印 planned attempts 数量。
3. 不要修改：
   - laavha_msg.h
   - laavha_py.cc
   - 模型、论文、数据集文件
4. 验证：

   cd /home/suwen/ns-3.45
   conda activate deeplearn
   ./ns3 build ns3ai_laavha_handover

   cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
   conda activate deeplearn
   python laavha_inference.py --ns3-arg RngRun=7
   python laavha_batch_runner.py --runs 2 --duration 3.0 --period 0.1 --flowmonMode feed --seed-base 10 --output batch_seed.csv
   python laavha_batch_runner.py --runs 1 --sweep-duration 3.0,5.0 --sweep-period 0.1 --flowmonMode feed --seed-base 20 --output batch_sweep.csv

验收标准：
- 构建通过。
- 单次 RngRun=7 完成。
- seed batch 至少 2 行 CSV。
- sweep batch 行数等于参数组合数 * runs。
- CSV 记录 seed/duration/period/flowmonMode。
- message schema 未修改。
- 如果不同 seed 输出仍相同，报告中说明当前场景缺少随机扰动，这是预期风险，不算失败。

完成后报告：
1. 修改文件列表。
2. 是否修改 message schema。
3. RngRun CLI 行为。
4. sweep CLI 行为。
5. 验证命令和结果。
6. CSV 样例。
7. 不同 seed 是否改变结果。
8. 下一阶段建议。
```
