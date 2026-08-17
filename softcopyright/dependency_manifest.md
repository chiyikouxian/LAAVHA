# 软件依赖与证据清单

| 类别 | 名称/路径 | 状态 | 说明 |
|---|---|---|---|
| 模型权重 | `LAAVHA算法模型.pth` | 已存在 | 推理默认加载；二进制依赖，不作为源代码正文 |
| 训练数据 | `LAAVHA_Training_Dataset.csv` | 路径待确认 | 训练脚本默认名称；仓库另有`训练数据集.csv` |
| Python运行时 | Python 3.10+ | 要求 | 训练、推理、批处理和绘图 |
| 深度学习 | PyTorch 1.10+ | 要求 | LSTM、Attention和推理 |
| 数值处理 | NumPy、Pandas | 要求 | 数据整理和数值计算 |
| 绘图 | Matplotlib | 要求 | 结果分析和图表 |
| 仿真平台 | NS-3.45 | 外部工作区 | C++异构网络仿真 |
| 交互模块 | NS-3 contrib/ai ns3-ai | 外部模块 | 共享内存消息交换 |
| Python绑定 | pybind11生成的`ns3ai_laavha_handover_py` | 构建生成 | 由`laavha_py.cc`编译生成 |
| C++构建 | CMake/NS-3构建工具 | 要求 | 仿真目标和绑定 |
| 实验数据 | `experiments/results_stress/`等 | 证据 | 仅用于分析，不是运行依赖 |

## 已知边界

5G指标采用P2P及传播模型代理，不等价于真实NR/5G-LENA PHY测量；切换输出是决策层网络编号，不是协议层attach/detach；缺少NS-3.45外部工作区时只能完成Python静态检查和局部单元检查。
