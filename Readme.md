# LAAVHA 无人异构网络垂直切换仿真集成

## 一、项目简介

实现 **AI 算法 + 网络物理仿真** 结合的 LAAVHA（LSTM-Attention Vertical Handover
Algorithm）算法——论文第三章核心内容。

1. **算法核心**：基于 PyTorch 实现 **LSTM-Attention (LAAVHA)** 智能算法，
   完成网络状态预测与最优接入网络决策；
2. **仿真核心**：基于 NS-3.45 搭建 5G/LTE/WiFi 异构网络环境，模拟无人机
   移动轨迹与网络切换物理过程；
3. **通信桥梁**：通过 `ns3-ai` 模块实现 **Python（AI 推理）与 NS-3（仿真）
   双向实时共享内存数据交互**。

## 二、核心文件清单

| 文件 | 功能 |
|------|------|
| `LAAVHA改进算法训练程序.py` | LAAVHA 神经网络结构定义、数据集训练、模型保存 |
| `LAAVHA算法模型.pth` | 预训练完成的 LSTM-Attention 模型权重文件 |
| `laavha_inference.py` | **推理服务端**：加载模型，通过 ns3-ai 与 C++ 仿真交互，运行决策循环 |
| `laavha-handover.cc` | **NS-3 仿真端**：异构网络部署、无人机移动模型、FlowMonitor 指标采集 |
| `laavha_batch_runner.py` | **批处理运行器**：批量运行多次仿真并汇总结果 CSV |
| `laavha_plot.py` | **图表生成脚本**：从 CSV 生成论文风格图表 |
| `laavha_msg.h` | ns3-ai 消息结构定义（C++/Python 共享） |
| `laavha_py.cc` | ns3-ai Python 绑定代码 |
| `CMakeLists_laavha.txt` | NS-3 cmake 编译配置（参考用） |

### 已废弃文件

- `LAAVHA模型加载程序.py.deprecated` — 旧版推理服务（架构与训练代码不匹配，已废弃）
- `LAAVHA算法仿真程序.cpp.deprecated` — 旧版仿真 Demo（使用 rand() 占位，已废弃）

## 三、环境要求

- **操作系统**: Ubuntu 20.04 LTS 或更高
- **NS-3**: 3.45（含 `contrib/ai` ns3-ai 模块）
- **Python**: 3.10+（推荐 `deeplearn` conda 环境）
- **PyTorch**: 1.10+
- **其他**: NumPy, Pandas, Matplotlib

## 四、运行方式

当前推理服务通过 `laavha_inference.py` 自动启动 C++ 仿真，**无需双终端**。
以下命令均在 `/home/suwen/ns-3.45` 工作区执行（需先将本仓库中的 `.py`/`.cc`
文件放置在 ns-3.45 对应目录中编译运行）。

### 1. 编译 ns-3 仿真目标

```bash
cd /home/suwen/ns-3.45
./ns3 build ns3ai_laavha_handover
```

### 2. 单次 LAAVHA 推理运行

```bash
cd /home/suwen/ns-3.45/contrib/ai/examples/laavha-handover
python laavha_inference.py
# 默认: 5.0s, 0.1s period, flowmonMode=feed
```

### 3. 批处理实验

```bash
# LAAVHA 算法 20 次运行
python laavha_batch_runner.py \
    --runs 20 --duration 10.0 --period 0.1 \
    --flowmonMode feed --seed-base 100 \
    --randomizeScenario --positionJitter 30 --altitudeJitter 10 \
    --algorithm laavha \
    --output batch_final.csv \
    --time-series-dir time_series_final

# 多算法对比扫描
python laavha_batch_runner.py \
    --runs 20 --duration 10.0 --period 0.1 \
    --flowmonMode feed --seed-base 200 \
    --randomizeScenario --positionJitter 30 --altitudeJitter 10 \
    --sweep-algorithm laavha,topsis-q,strongest-signal,laavha-l,laavha-a \
    --output batch_chapter3.csv \
    --time-series-dir time_series_chapter3
```

### 4. 生成图表

```bash
python laavha_plot.py \
    --input batch_final.csv \
    --time-series-dir time_series_final \
    --output-dir plots_final \
    --style publication --dpi 300
```

## 五、支持的算法模式

| `--algorithm` | 说明 | 类型 |
|---------------|------|------|
| `laavha` | 完整 LSTM-Attention 算法（默认） | 完整算法 |
| `topsis-q` | 熵权法 + 传统 TOPSIS | 对比算法 |
| `strongest-signal` | 最大 SINR 选择 | 简单基线 |
| `laavha-l` | 消融：去除 LSTM 预测模块 | 消融变体 |
| `laavha-a` | 消融：去除 Attention 权重模块 | 消融变体 |
| `fixed` | 始终选择固定网络（`--fixed-net`） | 辅助参考 |

## 六、网络 ID 与指标顺序

- **网络 ID**: 0=5G, 1=LTE, 2=WiFi
- **指标顺序**: SINR(0), RSRP(1), Delay(2), Throughput(3), PLR(4)
- **效益型指标**（越高越好）: SINR, RSRP, Throughput
- **成本型指标**（越低越好）: Delay, PLR

## 七、已知局限

1. **5G 代理**: 5G 使用 P2P 代理链路 + 传播模型计算信号值，非真实 NR/5G-LENA。
2. **决策级切换**: 切换为 LAAVHA 决策层的网络索引切换，非真实协议层
   WiFi/LTE attach/detach 过程。
3. **SINR/RSRP**: 通过 MobilityModel 位置 + log-distance 路径损耗代理计算，
   非 PHY 层真实 trace 值。
4. **随机性**: 当前仅在初始 UAV 位置和高度引入随机扰动，未包括信道衰落和
   流量随机性。
5. **工作区位置**: 活跃的 ns-3 代码位于 `/home/suwen/ns-3.45`，本仓库保存
   参考副本和实验输出。

## 八、训练模型（可选）

```bash
python LAAVHA改进算法训练程序.py
# 需要 LAAVHA_Training_Dataset.csv 在相同目录
# 输出: laavha_model_final.pth
```

## 九、项目结构

```
reproduce/
├── Readme.md                          # 本文件
├── LAAVHA改进算法训练程序.py           # 训练脚本
├── LAAVHA算法模型.pth                  # 预训练权重
├── LAAVHA_Training_Dataset.csv         # 训练数据集
├── laavha_inference.py                # 推理服务（工作代码）
├── laavha-handover.cc                 # NS-3 仿真（工作代码）
├── laavha_batch_runner.py             # 批处理运行器
├── laavha_plot.py                     # 图表生成
├── laavha_msg.h / laavha_py.cc        # ns3-ai 消息接口
├── openspec/                          # OpenSpec 变更记录
│   ├── status.md                      # 当前状态总览
│   ├── final-summary.md               # LAAVHA 复现总结
│   └── changes/                       # 19 个已完成变更 + 当前变更
├── paper_assets/                      # 论文图源
└── 毕业论文完整版.pdf                  # 学长完整论文
```
