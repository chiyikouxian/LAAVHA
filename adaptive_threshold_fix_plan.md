# 自适应阈值公式与实验图矛盾修正方案

## 问题诊断

### 问题1：阈值上限矛盾
- **公式(20)**（第10页）：Δth = 0.03 + 0.05(σ/10), σ ∈ [0,10]
  - 理论范围：[0.03, 0.08]
- **代码实现**（`laavha_inference.py:306`）：
  ```python
  volatility = np.clip(np.std(recent) / 10.0, 0.0, 1.0)
  threshold = 0.03 + 0.05 * volatility
  ```
  - 实际输出：[0.03, 0.08] ✓ 与公式一致
- **图7文字**（第18页第548行）：说"上升至约0.09" ✗ 错误
  - 实际数据最大值应为0.08
  - 图表y轴设为0.09只是为了留白

**结论**：代码正确，论文文字错误

### 问题2：公式(21)表达歧义
- **公式(21)**（第10页）：Th = max(2, |4 - v̄/30|), v̄ ∈ [0,30] m/s
  - 字面理解：4 - v/30 → 范围[3, 4]
- **代码实现**（`laavha_inference.py:308`）：
  ```python
  speed_factor = np.clip(velocity / 30.0, 0.0, 1.0)
  window = max(2, int(4 - 2 * speed_factor))
  ```
  - 实际计算：4 - 2v/30 → 范围[2, 4]
  
**结论**：公式(21)写法有误，应为 Th = max(2, ⌊4 - 2v̄/30⌋)

---

## 修改方案（优先级顺序）

### 方案A：仅修正论文文字（最简单，推荐）
**适用条件**：代码实现正确，只是论文描述错误

#### A1. 修正第18页图7文字说明
**位置**：`mdpi_baseline_version/main.tex` 第548行
**原文**：
> In Zone 2, it increases from 0.03 to approximately 0.09

**改为**：
> In Zone 2, it increases from 0.03 to approximately 0.08

#### A2. 修正公式(21)
**位置**：`mdpi_baseline_version/main.tex` 第318行
**原文**：
```latex
T_h = \max\left(2, \left|4 - \frac{\bar{v}}{30}\right|\right), \quad \bar{v} \in [0,30]~\text{m/s}.
```

**改为**：
```latex
T_h = \max\left(2, \left\lfloor 4 - \frac{2\bar{v}}{30}\right\rfloor\right), \quad \bar{v} \in [0,30]~\text{m/s}.
```

#### A3. 更新第318行后的文字说明
**原文**（需核对）：
> At 5 m/s, Th = 4 allows 12 m of movement...

**改为**：
> At 0 m/s, Th = 4 permits 12 m of movement; at 15 m/s, Th = 3 limits this to 9 m; at 30 m/s, Th = 2 limits this to 6 m, enabling timely handover near coverage boundaries.

---

### 方案B：如果代码有边界限制缺失（需重新实验）
**适用条件**：发现代码未正确限制volatility或window范围

#### B1. 修正代码
检查以下代码段是否有遗漏：
```python
# laavha_inference.py:305-308
volatility = np.clip(np.std(recent) / 10.0, 0.0, 1.0)  # 已有clip ✓
threshold = 0.03 + 0.05 * volatility                   # 未clip，但理论上不需要
window = max(2, int(4 - 2 * speed_factor))             # 已有max ✓
```

如需添加显式边界（防御性编程）：
```python
threshold = np.clip(0.03 + 0.05 * volatility, 0.03, 0.08)
```

#### B2. 重新运行实验
```bash
cd /home/suwen/reproduce/experiments
python3 exp_a_adaptive_hysteresis.py
```

#### B3. 检查新图表
确认 `th_vals` 最大值 ≤ 0.08

---

## 验证清单

### 1. 代码验证（已完成✓）
- [x] 检查 `laavha_inference.py:306` 阈值公式
- [x] 检查 `laavha_inference.py:308` 窗口公式
- [x] 验证volatility的clip范围
- [x] 手动计算极端情况

**结果**：代码实现正确，与公式(20)一致，但与公式(21)字面含义不符

### 2. 数据验证（待执行）
- [ ] 读取实验A生成的 `th_vals` 数组
- [ ] 确认实际最大值 = 0.08
- [ ] 检查图表y轴标注

### 3. 论文修正（待执行）
- [ ] 修改第18页第548行："0.09" → "0.08"
- [ ] 修改第10页公式(21)：添加系数2和取整符号
- [ ] 更新公式(21)后的文字说明
- [ ] 检查引言、摘要是否提到"0.09"

---

## 推荐行动

### 立即执行（方案A）
1. **读取 `mdpi_baseline_version/main.tex` 第548行**，确认准确原文
2. **修改 "0.09" → "0.08"**
3. **修改公式(21)**，添加系数2和取整符号
4. **验证编译**，确认PDF正常生成
5. **提交修改**，commit message说明修正了文字与公式不一致

### 谨慎执行（仅在发现代码问题时）
如果后续发现代码确实允许阈值超过0.08：
1. 在 `laavha_inference.py:306` 添加显式clip
2. 重新运行所有相关实验
3. 更新论文中的所有数值和图表

---

## 影响评估

### 低风险（方案A）
- 仅修改文字描述，不涉及数据重新生成
- 编译时间：<1分钟
- 影响范围：2处数值修正，1处公式修正

### 高风险（方案B）
- 需要重新运行实验
- 可能影响多个图表和表格
- 需要重新验证所有章节的数值引用

---

## 相关文件清单

- 论文源码：`mdpi_baseline_version/main.tex`
- 推理代码：`laavha_inference.py`
- 实验脚本：`experiments/exp_a_adaptive_hysteresis.py`
- 图表输出：`plots_chapter3_v2/fig_adaptive_hysteresis_proof.png`
