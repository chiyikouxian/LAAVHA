# 问题3修改方案 - Decision-Level Boundary Clarification

**修改目标**：明确区分"决策层网络选择"和"完整协议栈切换"  
**修改策略**：组合方案（术语精确化 + 边界说明）  
**预计时间**：30-45分钟  
**预计字数变化**：+50-60词

---

## 📝 修改清单

### ✅ 高优先级修改（必须执行）

#### 修改1：摘要 - 增加决策层边界说明

**位置**：第82-83行，摘要最后一句之后  
**当前内容**：
```latex
In 50 random scenarios, the handover count is only 0.24, achieving 84.8%-99.1% 
reduction compared to eight baseline algorithms.
\end{abstract}
```

**修改为**：
```latex
In 50 random scenarios, the decision-level handover count is only 0.24, achieving 
84.8%-99.1% reduction compared to eight baseline algorithms. The simulation 
evaluates network selection decision stability; the complete protocol-stack handover 
process (including authentication, link reestablishment, and data forwarding) 
remains outside the current scope.
\end{abstract}
```

**字数变化**：+28词  
**修改原因**：摘要是读者第一印象，必须明确研究边界

---

#### 修改2：关键词 - 增加decision-level限定

**位置**：第87行  
**当前内容**：
```latex
\begin{keyword}
UAV communications \sep heterogeneous wireless networks \sep vertical handover \sep network selection \sep LSTM \sep attention mechanism \sep adaptive decision
\end{keyword}
```

**修改为**：
```latex
\begin{keyword}
UAV communications \sep heterogeneous wireless networks \sep vertical handover decision \sep network selection \sep decision-level simulation \sep LSTM \sep attention mechanism \sep adaptive decision
\end{keyword}
```

**字数变化**：+3词  
**修改原因**：关键词帮助读者快速定位研究范围

---

#### 修改3：仿真设置 - 前置并强化边界说明

**位置**：第411行（当前）→ 移动到仿真设置章节开头（约第390行）  
**当前内容**：
```latex
The 5G candidate uses a proxy link, with SINR and RSRP calculated by a position-based 
propagation model following wireless-propagation and link-budget principles \cite{ref34}. 
Transport indicators are obtained from FlowMonitor statistics for point-to-point proxy 
flows. A handover event denotes a change in the network identifier selected by LAAVHA, 
rather than an actual Wi-Fi disassociation, LTE detachment, or 5G new-radio 
protocol-stack handover. Table~\ref{tab:metrics} summarizes the indicator sources 
for each candidate network.
```

**修改为**（移动到章节开头并强化）：
```latex
\subsection{Decision-Level Simulation Platform}\label{sec:sim}

This study evaluates network selection decision-making at the decision level rather 
than protocol-stack execution. A handover event denotes a change in the network 
identifier selected by LAAVHA---specifically, which network (5G, LTE, or Wi-Fi) the 
algorithm chooses at each decision period. It does not represent an actual Wi-Fi 
disassociation and reassociation, LTE detachment and attachment, or 5G new-radio 
protocol-stack handover, nor does it include the authentication, link reestablishment, 
or data-forwarding recovery processes that would occur in a real deployment. The 
simulation therefore verifies the stability of network selection decisions (when to 
switch and which network to select) rather than the end-to-end latency, interruption 
duration, or protocol overhead of complete handover execution.

The 5G candidate uses a proxy link, with SINR and RSRP calculated by a position-based 
propagation model following wireless-propagation and link-budget principles \cite{ref34}. 
Transport indicators are obtained from FlowMonitor statistics for point-to-point proxy 
flows. Table~\ref{tab:metrics} summarizes the indicator sources for each candidate network.
```

**字数变化**：+80词  
**修改原因**：在仿真设置章节开头明确说明，避免读者误解

---

#### 修改4：结论 - 增加decision-level限定和边界说明

**位置**：第495行，结论最后一句  
**当前内容**：
```latex
ALERA completes all necessary handovers under sustained degradation and produces 
zero false handovers under transient variation, demonstrating reliable and stable 
data transmission for UAV aerial missions in heterogeneous wireless networks.
```

**修改为**：
```latex
At the decision level, ALERA completes all necessary network selection changes 
under sustained degradation and produces zero false changes under transient variation, 
demonstrating stable decision-making for UAV aerial missions in heterogeneous wireless 
networks. The simulation evaluates the stability and correctness of network selection 
decisions (when to switch and which network to select); future work will extend the 
evaluation to include complete protocol-stack handover processes, such as 
authentication delays, link reestablishment overhead, and seamless data forwarding.
```

**字数变化**：+40词  
**修改原因**：结论是读者最后印象，必须明确研究边界和未来工作

---

### 🟡 中优先级修改（建议执行）

#### 修改5：引言 - 增加研究范围说明

**位置**：第94行，引言第一段末尾  
**当前内容**：
```latex
The core technical challenge lies in managing seamless connectivity across coverage 
boundaries while maintaining quality of service for real-time aerial data transmission 
\cite{ref1,ref2,ref3}.
```

**修改为**：
```latex
The core technical challenge lies in managing seamless connectivity across coverage 
boundaries while maintaining quality of service for real-time aerial data transmission 
\cite{ref1,ref2,ref3}. This study addresses the network selection decision problem: 
determining when to initiate a handover and which target network to select, based on 
predicted channel conditions and dynamic attribute weighting. The complete protocol-stack 
handover process---including authentication, link reestablishment, and data forwarding---is 
not evaluated in the current simulation platform.
```

**字数变化**：+50词  
**修改原因**：引言尽早明确研究范围，避免读者误解

---

#### 修改6：实验结果 - 统一使用decision-level限定

**位置**：多处（第429行、第444行、第450行等）  
**修改策略**：在首次出现"handover"的地方增加"decision-level"限定

**示例修改**：
- 第429行：`"decision-level simulation platform"` （已在修改3中处理）
- 第444行：`"decision-level handover count"` → 保持一致
- 第450行：`"decision-level handover stability"` → 增加限定

**字数变化**：+10词（分散在多处）  
**修改原因**：术语一致性，强化decision-level概念

---

### 🟢 低优先级修改（可选执行）

#### 修改7：Figure captions - 增加decision-level说明

**位置**：图表标题（第440行、第455行等）  
**修改策略**：在图表标题中增加"(decision-level)"说明

**示例修改**：
```latex
\caption{Mean handover-count comparison of 11 algorithms (decision-level; mean $\pm$ std, \textit{n}=50).}
```

**字数变化**：+2-3词/图  
**修改原因**：强化decision-level概念

---

## 📊 修改前后对比

### 摘要对比

**修改前**：
```
...In 50 random scenarios, the handover count is only 0.24, achieving 
84.8%-99.1% reduction compared to eight baseline algorithms.
```
❌ 读者可能误解：减少了真实通信中断次数

**修改后**：
```
...In 50 random scenarios, the decision-level handover count is only 0.24, 
achieving 84.8%-99.1% reduction compared to eight baseline algorithms. 
The simulation evaluates network selection decision stability; the 
complete protocol-stack handover process remains outside the current scope.
```
✅ 读者清楚理解：这是决策层仿真，不包含完整协议切换

---

### 结论对比

**修改前**：
```
ALERA completes all necessary handovers under sustained degradation and 
produces zero false handovers under transient variation, demonstrating 
reliable and stable data transmission for UAV aerial missions...
```
❌ 读者可能误解：改善了真实数据传输质量

**修改后**：
```
At the decision level, ALERA completes all necessary network selection 
changes under sustained degradation and produces zero false changes under 
transient variation, demonstrating stable decision-making for UAV aerial 
missions... The simulation evaluates the stability and correctness of 
network selection decisions; future work will extend the evaluation to 
include complete protocol-stack handover processes.
```
✅ 读者清楚理解：验证了决策稳定性，未来扩展到协议切换

---

## 🎯 执行步骤

### Step 1: 高优先级修改（必须）
1. ✅ 修改1：摘要增加边界说明（+28词）
2. ✅ 修改2：关键词增加decision-level（+3词）
3. ✅ 修改3：仿真设置前置并强化（+80词）
4. ✅ 修改4：结论增加边界说明（+40词）

**小计**：+151词

### Step 2: 中优先级修改（建议）
5. ✅ 修改5：引言增加研究范围（+50词）
6. ✅ 修改6：实验结果统一术语（+10词）

**小计**：+60词

### Step 3: 低优先级修改（可选）
7. 🔲 修改7：图表标题增加decision-level（+10词）

**小计**：+10词

---

## 📈 质量提升预期

| 评估维度 | 修改前 | 修改后 | 提升 |
|---------|--------|--------|------|
| **技术准确性** | 6/10 | 9/10 | +3 ⭐⭐⭐ |
| **研究边界清晰度** | 5/10 | 10/10 | +5 ⭐⭐⭐⭐⭐ |
| **可信度** | 7/10 | 9/10 | +2 ⭐⭐ |
| **审稿风险** | 中 | 低 | ✅ |

---

## ⚠️ 注意事项

### 1. 保持技术内容不变
- ✅ 所有算法、公式、实验数据保持不变
- ✅ 仅修改语义描述和研究边界说明
- ✅ 不改变技术贡献的核心价值

### 2. 避免过度防御
- ✅ 诚实说明研究范围
- ❌ 不要过度道歉或贬低研究价值
- ✅ 强调决策层研究的重要性和独立价值

### 3. 未来工作衔接
- ✅ 在结论中提及未来扩展方向
- ✅ 将协议切换作为未来工作
- ✅ 保持研究的连贯性和发展空间

---

## 🎯 修改后的核心信息传递

### 给读者的清晰信息：
1. ✅ 本研究聚焦**网络选择决策**（decision-making）
2. ✅ 研究**何时切换**和**切换到哪个网络**
3. ✅ 验证了**决策稳定性**和**反复切换抑制**
4. ✅ 仿真平台是**决策层**（decision-level）
5. ✅ **完整协议切换**不在当前研究范围
6. ✅ 未来工作将扩展到协议层

### 给审稿人的清晰信息：
1. ✅ 研究边界明确（decision-level simulation）
2. ✅ 技术贡献清晰（智能网络选择决策）
3. ✅ 未过度声明（不声称改善协议切换开销）
4. ✅ 未来工作明确（协议层扩展）

---

**执行确认**：
- [ ] 我已理解所有修改内容
- [ ] 我确认采用组合方案（术语精确化 + 边界说明）
- [ ] 我准备执行高优先级修改（必须）
- [ ] 我准备执行中优先级修改（建议）
- [ ] 我将跳过低优先级修改（可选）

---

**下一步**：执行修改并生成Git commit
