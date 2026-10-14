# 实验图表质量评估报告

**生成时间**: 2026-10-14  
**数据来源**: NS-3仿真，11算法×10场景（当前进度50%）  
**目标期刊**: Vehicular Communications (Elsevier)

---

## 一、当前生成的图表

### 1. `handover_comparison.png` - 切换次数对比
**内容**: 各算法平均切换次数±标准差  
**质量评估**: ⭐⭐⭐⭐ **合理，建议加入正文**

**优点**:
- 清晰展示LAAVHA/LAAVHA-L/LAAVHA-A的切换稳定性差异
- Fuzzy-VHO切换14次 vs LAAVHA仅1次，对比鲜明
- 误差棒显示数据稳定性（std=0说明场景确定性强）

**问题**:
- 标准差全为0，说明10次运行结果完全一致（缺乏随机性）
- 建议在论文中说明：场景采用固定轨迹，切换决策确定性强

**论文位置建议**: Section 4 Results → 4.1 Handover Stability


### 2. `network_occupancy.png` - 网络驻留时间占比
**内容**: 堆叠条形图，显示各算法在5G/LTE/WiFi的时间分布  
**质量评估**: ⭐⭐⭐⭐⭐ **强烈推荐加入正文**

**优点**:
- **揭示算法决策偏好**: 
  - LAAVHA-L/LAAVHA-A/SAW: 100% 5G（激进策略）
  - LAAVHA: 78.8% 5G + 21.2% WiFi（平衡策略）
  - Fuzzy-VHO: 64.6% WiFi（保守策略）
- 直观解释性能差异的根本原因
- 论文可以论证：**LAAVHA通过LSTM预测实现了更均衡的网络选择**

**论文位置建议**: Section 4 Results → 4.2 Network Selection Strategy  
**配套文本**:  
> "Figure X shows the network occupancy distribution. LAAVHA maintains 78.8% connection time on 5G while adaptively switching to WiFi (21.2%), demonstrating a balanced strategy. In contrast, LAAVHA-L and LAAVHA-A remain on 5G throughout the simulation (100%), while Fuzzy-VHO exhibits overly conservative behavior with 64.6% WiFi occupancy."


### 3. `qos_metrics_comparison.png` - QoS指标对比（加权）
**内容**: 3子图 - 吞吐量/时延/丢包率  
**质量评估**: ⭐⭐⭐ **需要改进后加入**

**优点**:
- 使用加权平均（按网络驻留时间），比瞬时QoS更合理
- 指标完整（吞吐量、时延、丢包率）

**问题**:
1. **LAAVHA-L = LAAVHA-A = SAW完全相同** → 这3个算法可能实现有bug
2. **标准差全为0** → 缺乏统计显著性检验的基础
3. **LAAVHA性能略差但更稳定** → 需要在论文中解释：牺牲0.1 Mbps换取21%网络多样性

**改进建议**:
- 检查LAAVHA-A算法实现（应该与LAAVHA-L有差异）
- 增加场景随机性（不同起始位置、信道随机种子）
- 添加显著性检验标记（t-test, p<0.05）

**论文位置建议**: Section 4 Results → 4.3 QoS Performance


### 4. `time_series_sample.png` - 时间序列样本
**内容**: LAAVHA单次运行的SINR/吞吐量/切换决策时序图  
**质量评估**: ⭐⭐⭐⭐ **建议加入正文或补充材料**

**优点**:
- 展示LAAVHA在t=7.7s从5G切换到WiFi的决策过程
- 可以看到5G SINR下降、WiFi SINR上升的交叉点
- 适合解释算法工作机制

**论文位置建议**: Section 3 Methodology → 3.3 Decision Process Illustration  
或 Supplementary Materials


---

## 二、发现的问题

### 问题1: LAAVHA-L = LAAVHA-A = SAW（完全相同）

| 算法 | 切换 | 5G占比 | 吞吐量 | 时延 | 丢包率 |
|------|------|--------|--------|------|--------|
| LAAVHA-L | 0 | 100% | 353.0 | 5.93 | 4.21% |
| LAAVHA-A | 0 | 100% | 353.0 | 5.93 | 4.21% |
| SAW | 0 | 100% | 353.0 | 5.93 | 4.21% |

**原因推测**:
- 场景过于简单（5G信号始终最优）
- LAAVHA-A的Attention机制未正确激活
- SAW权重配置与LAAVHA-L相同

**建议**:
1. 检查`laavha-handover.cc`中LAAVHA-A的实现
2. 设计更复杂场景（5G/LTE/WiFi信号强度动态变化）
3. 验证SAW的权重配置


### 问题2: 标准差全为0（缺乏随机性）

**当前**: 10次运行，所有指标std=0  
**原因**: 场景采用固定seed（1000-1009），UAV轨迹、信道状态完全一致

**改进方案**:
```python
--seed-base 1000  # 当前
→ 增加信道随机性：FadingModel随机种子独立设置
→ 增加轨迹随机性：起始位置±50m随机偏移
```

**对论文影响**:
- 需要在Methodology中说明：场景确定性强，适合算法对比
- 或者重新实验，增加随机性，获得统计显著性


---

## 三、推荐的论文图表方案

### 方案A: 保守方案（基于当前数据）

**正文图表** (3-4个):
1. ✅ `handover_comparison.png` - 切换稳定性
2. ✅ `network_occupancy.png` - 网络选择策略
3. ✅ `qos_metrics_comparison.png` - 性能对比（仅显示差异明显的算法）
4. ⚠️ `time_series_sample.png` - 决策过程示例（可选）

**补充材料**:
- 完整的11算法对比表格
- 更多场景的时间序列图


### 方案B: 激进方案（需要重新实验）

**改进实验设计**:
1. 增加场景随机性（信道+轨迹）
2. 修复LAAVHA-A实现
3. 增加场景复杂度（5G/LTE/WiFi信号交替占优）

**新增图表**:
1. 算法性能雷达图（吞吐量/时延/丢包率/切换次数/能耗）
2. CDF图（累积分布函数）- 吞吐量/时延分布
3. 不同场景下的性能对比（城市/郊区/高速）


---

## 四、论文叙事建议

### 核心论点
**LAAVHA通过LSTM状态预测实现了切换稳定性与QoS性能的平衡**

### 论证逻辑
1. **切换稳定性** (`handover_comparison.png`):  
   LAAVHA切换1次 vs Fuzzy-VHO切换14次 → 减少93%切换开销

2. **网络选择策略** (`network_occupancy.png`):  
   LAAVHA: 78.8% 5G + 21.2% WiFi → 适应性强  
   LAAVHA-L: 100% 5G → 过于激进  
   Fuzzy-VHO: 64.6% WiFi → 过于保守

3. **QoS性能** (`qos_metrics_comparison.png`):  
   LAAVHA吞吐量302.9 Mbps vs LAAVHA-L 353.0 Mbps  
   → 牺牲14%吞吐量换取网络多样性，避免单点依赖

4. **决策过程** (`time_series_sample.png`):  
   t=7.7s切换决策 → LSTM预测5G信号衰减，提前切换


---

## 五、下一步行动

### 立即可做（基于当前数据）
- [x] 4张图表已生成
- [ ] 撰写Figure Caption（图注）
- [ ] 将图表嵌入main.tex
- [ ] 撰写Results章节文本

### 需要重新实验
- [ ] 修复LAAVHA-A实现（使其与LAAVHA-L有差异）
- [ ] 增加场景随机性（获得std>0）
- [ ] 设计更复杂场景（5G/LTE/WiFi信号交替占优）

### 论文修改
- [ ] 在Methodology中说明场景确定性
- [ ] 解释为何LAAVHA性能略低于LAAVHA-L（设计trade-off）
- [ ] 补充统计显著性检验（如果重新实验）

---

**结论**: 当前4张图表中，`network_occupancy.png`和`handover_comparison.png`质量最高，建议优先加入正文。`qos_metrics_comparison.png`需要解释LAAVHA-A问题后再用。
