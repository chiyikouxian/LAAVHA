# 无人异构网络垂直切换 仿真集成

## 一、项目简介

实现**AI 算法 + 网络物理仿真**结合的LAAVHA算法  （论文第三章）

1. **算法核心**：基于 PyTorch 实现 **LSTM-Attention (LAAVHA)** 智能算法，完成网络状态预测与最优接入网络决策；
2. **仿真核心**：基于 NS-3.31 搭建 5G/LTE/WiFi 异构网络环境，模拟无人机移动轨迹与网络切换物理过程；
3. **通信桥梁**：通过 `ns3-ai` 开源模块实现 **Python（AI 推理）与 NS-3（仿真）双向实时数据交互**。

---

## 二、核心文件清单与功能说明

表格

| **文件名称** | **存放路径** | **核心功能** |
| --- | --- | --- |
| `LAAVHA算法模型.pth` | `ns-3/contrib/ns3-ai/py_interface/laavha_handover/` | 预训练完成的 LSTM-Attention 模型权重文件 |
| `LAAVHA改进算法训练程序.py` | 本地 / 项目目录 | LAAVHA 神经网络结构定义、数据集训练、模型保存 |
| `LAAVHA模型加载程序.py` | `ns-3/contrib/ns3-ai/py_interface/laavha_handover/` | Python 推理服务：加载模型、接收 NS3 数据、输出决策结果 |
| `LAAVHA算法仿真程序.cc` | `ns-3/scratch/` | NS-3 仿真脚本：异构网络部署、无人机轨迹、垂直切换逻辑 |

---

## 三、环境要求

### 1. 操作系统

- **Ubuntu 20.04 LTS**

### 2. 核心软件

- **NS-3.31**
- **Python 3.7 ~ 3.9**
- **PyTorch 1.10+**
- **ns3-ai**

---

## 四、详细部署步骤

### 第一步：安装 ns3-ai 通信模块

1. 进入 NS-3 源码的 `contrib` 目录：
    
    bash
    
    `cd 你的ns-3.31主目录/contrib`
    
2. 克隆官方 ns3-ai 仓库：
    
    bash
    
    `git clone https://github.com/hust-diat/ns3-ai.git`
    
3. 安装 Python 接口：
    
    bash
    
    `cd ns3-ai
    python3 setup.py install`
    

### 第二步：创建项目目录 & 移动模型文件

1. 在 `py_interface` 下创建算法专属文件夹：
    
    bash
    
    `mkdir -p ../ns3-ai/py_interface/laavha_handover`
    
2. 将预训练模型 `LAAVHA算法模型.pth` 移动到该目录：
    
    bash
    
    `mv LAAVHA算法模型.pth 你的ns-3.31主目录/contrib/ns3-ai/py_interface/laavha_handover/`
    

### 第三步：配置 Python 推理端

1. 将 `LAAVHA模型加载程序.py` 放入目录：
    
    `ns-3/contrib/ns3-ai/py_interface/laavha_handover/`
    
2. 检查代码中**模型加载路径**，确保与实际路径一致。

### 第四步：配置 NS-3 仿真端

1. 将 `LAAVHA算法仿真程序.cc` 放入 NS-3 的 `scratch` 目录：
    
    `你的ns-3.31主目录/scratch/`
    
2. 可根据需求修改代码参数：网络基站位置、无人机轨迹、仿真时间、切换阈值等。

### 第五步：重新编译 NS-3（启用依赖模块）

回到 NS-3 主目录，执行编译命令：

bash

`cd 你的ns-3.31主目录
./ns3 configure --enable-modules=ai,lte,wifi
./ns3 build`

✅ 编译无报错则部署完成。

---

## 五、运行步骤（双终端，严格遵守顺序）

> ⚠️ 必须**先启动 Python 推理服务**，再启动 NS-3 仿真，否则通信失败！
> 

### 终端 1：启动 Python AI 推理服务

bash

`# 进入算法目录
cd 你的ns-3.31主目录/contrib/ns3-ai/py_interface/laavha_handover/
# 启动服务（等待NS3连接）
python3 LAAVHA模型加载程序.py`

### 终端 2：启动 NS-3 网络仿真

bash

`# 回到NS-3主目录
cd 你的ns-3.31主目录
# 运行仿真脚本
./ns3 run scratch/LAAVHA算法仿真程序`

✅ 运行成功后，两个终端会显示运行成功

---

## 六、训练模型（可选）

若需要重新训练 LAAVHA 算法：

1. 准备数据集可参考已有数据集（网络状态、无人机位置、切换标签等）；
2. 运行 `LAAVHA改进算法训练程序.py`；
3. 训练完成后，将新生成的 `.pth` 模型文件替换原有文件即可。

---

## 七、关键注意事项

1. **路径规范**
    - 所有文件路径**禁止包含中文、空格**，否则会导致模型加载 / 编译失败；（这里为了显示代码作用用中文举例）
    - 严格按照文档指定路径存放文件，不可随意修改。
2. **运行顺序**
    - 先 Python 服务 → 后 NS3 仿真，顺序颠倒会导致通信超时。
3. **模型兼容性**
    - `.pth` 模型必须与训练代码的网络结构一致，否则加载失败。

---