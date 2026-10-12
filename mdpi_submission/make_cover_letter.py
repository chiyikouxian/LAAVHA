#!/usr/bin/env python3
"""Generate the Chinese cover letter for the Remote Sensing submission."""
import docx
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

OUT = "cover letter.docx"

doc = docx.Document()

# 页面：A4，2.5cm 页边距
sec = doc.sections[0]
sec.page_width = Cm(21.0)
sec.page_height = Cm(29.7)
sec.top_margin = sec.bottom_margin = Cm(2.0)
sec.left_margin = sec.right_margin = Cm(2.5)

# 正文默认字体：西文 Times New Roman，中文宋体，小四(12pt)
normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(12)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "SimSun")
normal.paragraph_format.space_after = Pt(3)
normal.paragraph_format.line_spacing = 1.15


def para(text="", bold=False, align=None, space_after=4, indent=True):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    if align is not None:
        p.alignment = align
    if text:
        if indent:
            p.paragraph_format.first_line_indent = Pt(24)  # 首行缩进两字
        r = p.add_run(text)
        r.bold = bold
    return p


def flush(text, bold=False, align=None, space_after=4):
    """无首行缩进的段落（称呼、落款等）。"""
    return para(text, bold=bold, align=align, space_after=space_after, indent=False)


# ---------------- 标题 ----------------
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
t.paragraph_format.space_after = Pt(14)
r = t.add_run("投稿信（Cover Letter）")
r.bold = True
r.font.size = Pt(15)
r.font.name = "Times New Roman"
r._element.rPr.rFonts.set(qn("w:eastAsia"), "SimHei")

# ---------------- 收信人 ----------------
flush("致：《Remote Sensing》编辑部主编及编委会", space_after=2)
flush("投稿类型：Article（研究论文）", space_after=2)
flush("稿件题目：Attention-LSTM Enhanced Risk-Aware Vertical Handoff Algorithm "
      "for UAV Remote Sensing Heterogeneous Networks", space_after=2)
flush("通讯作者：刘同（Tong Liu），成都理工大学计算机与网络安全学院，"
      "liutong1982@cdut.edu.cn", space_after=8)

flush("尊敬的编辑：", space_after=4)

# ---------------- 正文 ----------------
para("我们谨向贵刊投稿上述论文，恳请贵刊予以审阅并考虑发表。本文提出面向无人机遥感异构网络的"
     "垂直切换算法 LAAVHA 及其增强版本 ALERA，旨在解决无人机在大范围遥感巡航过程中跨越 5G、"
     "LTE 与 Wi-Fi 覆盖边界时的切换决策问题。")

# 1. 研究内容与重要性
para("一、研究内容及其重要性", bold=True, indent=False, space_after=4)
para("无人机遥感的核心产出是高分辨率光学与多光谱影像等观测数据，其价值高度依赖于回传链路的"
     "连续性与时效性。在灾害评估、农情调查与环境监测等任务中，无人机需要长时间、大范围巡航，"
     "不可避免地反复跨越异构网络的覆盖边界。此时若切换决策滞后，将造成影像回传中断与数据缺失；"
     "若在边界处频繁发生乒乓切换，则会引入额外时延与丢包，同样损害遥感数据的完整性。因此，"
     "垂直切换的稳定性直接决定了无人机遥感观测数据能否被可靠、实时地获取，这是遥感数据获取"
     "环节中一个尚未被充分解决的问题。")
para("本文的主要贡献是：在多属性决策框架中引入时序预测与动态权重，使切换决策不再仅依赖当前"
     "时刻的网络状态。LAAVHA 由堆叠 LSTM 短时状态预测、基于注意力机制的动态属性加权、"
     "融合当前与预测状态的改进 TOPSIS 排序，以及双迟滞判决四个环节构成；ALERA 在不改动 "
     "LSTM-注意力结构与训练过程的前提下，进一步加入自适应动态迟滞（ADH）与风险敏感 TOPSIS"
     "（RS-TOPSIS），分别改进“何时切换”与“切换到哪一个网络”两个决策维度。")

# 2. 与已有工作的关系
para("二、与已有研究的关系", bold=True, indent=False, space_after=4)
para("现有的垂直切换方法多基于 SAW、TOPSIS、VIKOR、GRA、SPOTIS、COPRAS 等多属性决策模型，"
     "普遍采用固定权重并仅使用当前时刻指标，缺少对链路状态演化趋势的建模；而最强信号选择类方法"
     "仅考虑 SINR，忽略时延、吞吐量与丢包率等对遥感数据回传同样关键的指标。这使得在覆盖边界"
     "附近候选网络评分交替占优时，容易产生重复切换。")
para("我们在 ns-3.45 与 ns3-ai 平台上、于 2000 m × 2000 m 的无人机遥感场景中使用 50 组随机种子"
     "进行了对比实验。结果显示，LAAVHA 在 11 种算法中取得最低的平均切换次数 0.24，相对八种基线"
     "方法降低 84.8%–99.1%，其中 38 次运行完全无需切换。消融实验进一步表明，去除 LSTM 预测"
     "或注意力动态加权后，平均切换次数分别升至 1.08 与 2.00，说明两个模块具有互补作用。"
     "在链路持续劣化与瞬时波动两类情形下，ALERA 既完成了全部必要切换，又未产生虚假切换。"
     "这些结果说明，将时序预测与动态权重结合，能够在不牺牲必要切换及时性的前提下显著抑制"
     "不必要的切换。")

# 3. 与期刊的关联
para("三、与《Remote Sensing》的关联及适用性", bold=True, indent=False, space_after=4)
para("本文的研究对象与研究目的均落在无人机遥感范畴内。首先，问题来源于遥感任务本身：论文所建模"
     "的飞行航迹、飞行高度（50–150 m）、巡航速度（5–30 m/s）以及地面站与重点成像点附近的网络"
     "部署，均按无人机遥感观测任务设定，而非一般性的通信仿真场景。其次，优化目标是遥感数据的"
     "获取质量：算法以维持影像回传的连续性与实时性为目的，切换稳定性指标直接对应观测数据是否"
     "完整可用。第三，本文属于遥感数据获取链路中的使能技术研究，为无人机遥感平台在异构网络下的"
     "实时数据传输提供了可用的决策方法，可支撑灾害评估、农业调查与环境监测等遥感应用。")
para("据此，我们认为本文契合贵刊在无人机遥感（UAV remote sensing）以及遥感数据获取与传输方面的"
     "征稿范围，尤其与无人机遥感平台、系统与数据链路相关的主题相符。")

# 4. 声明
para("四、相关声明", bold=True, indent=False, space_after=4)
para("本文为首次投稿，此前未曾向 MDPI 旗下任何期刊投稿，亦不存在需要说明的既往稿件编号。"
     "本研究未接受外部经费资助，全体作者声明不存在利益冲突。论文中的仿真代码与数据可应"
     "通讯作者的合理请求提供。")
para("We confirm that neither the manuscript nor any parts of its content are currently "
     "under consideration for publication with or published in another journal.", indent=False)
para("All authors have approved the manuscript and agree with its submission to "
     "Remote Sensing.", indent=False)

para("感谢您与各位审稿专家在评审过程中付出的时间与精力，期待您的回复。", space_after=8)

# ---------------- 落款 ----------------
flush("此致", space_after=2)
flush("敬礼！", space_after=8)

for line in ["通讯作者：刘同（Tong Liu）",
             "单位：成都理工大学 计算机与网络安全学院",
             "地址：中国 四川省成都市 610059",
             "邮箱：liutong1982@cdut.edu.cn",
             "代表全体作者：孙汉明、刘同、苏文、林杰、罗俊松、多滨"]:
    p = flush(line, space_after=0)
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

p = flush("日期：____年____月____日", space_after=0)
p.alignment = WD_ALIGN_PARAGRAPH.RIGHT

doc.save(OUT)
print("wrote", OUT)