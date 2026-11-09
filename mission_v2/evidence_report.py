"""Summarize saved evidence without converting development data into test claims."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from mission import ROOT,CONFIG,load_trace,abstract_trace
from reference import solve


def main():
    rows=[]
    for f in sorted((ROOT/'outputs/physical_pilot').glob('*.summary.json')):
        d=json.loads(f.read_text());rows.append({k:d.get(k) for k in ['seed','algorithm','raw_handover_count','telemetry_on_time_ratio','video_on_time_ratio','video_on_time_mbps','zero_delivery_cohort_s']})
    pilot=pd.DataFrame(rows)
    if len(pilot):
        pilot.to_csv(ROOT/'outputs/physical_pilot/comparison.csv',index=False)
        pilot.groupby('algorithm').mean(numeric_only=True).to_csv(ROOT/'outputs/physical_pilot/means.csv')
    refs=[]
    for seed in range(100,120):
        tr=abstract_trace(seed,stress=0)
        for k in [0,1,2,None]:
            r=solve(tr['metrics'],tr['demand'],max_switches=k)
            refs.append({'seed':seed,'backend':'service-abstraction','limit':'unrestricted' if k is None else str(k),'switches':r['switches'],'objective':r['objective']})
    pd.DataFrame(refs).to_csv(ROOT/'outputs/nominal_reference.csv',index=False)
    physical_refs=[]
    calibration_sensitivity=[]
    calibration=ROOT/'outputs/height75_calibration'
    calibration_rows=[]
    for seed in [100,108,119]:
        files=list(calibration.glob(f'ns3_fixed-nr_seed{seed}.trace.npz'))
        if not files:continue
        tr=load_trace(files[0])
        for k in [0,1,2,None]:
            r=solve(tr['metrics'],tr['demand'],max_switches=k)
            changes=np.flatnonzero(np.diff(np.r_[0,r['path']]))
            calibration_rows.append({'seed':seed,'limit':'unrestricted' if k is None else str(k),
                                     'switches':r['switches'],'objective':r['objective'],
                                     'times':tr['time'][changes].tolist(),'targets':r['path'][changes].tolist()})
        for cost in [.005,.02,.05]:
            for interruption in [0.,.05,.1,.2]:
                for demand_scale in [.9,1.,1.1]:
                    r=solve(tr['metrics'],tr['demand']*demand_scale,cost=cost,interruption=interruption)
                    calibration_sensitivity.append({'seed':seed,'cost':cost,'interruption_s':interruption,'demand_scale':demand_scale,'switches':r['switches'],'objective':r['objective']})
                for k in [0,1,2,None]:
                    r=solve(tr['metrics'],tr['demand'],cost=cost,interruption=interruption,max_switches=k)
                    physical_refs.append({'seed':seed,'cost':cost,'interruption_s':interruption,'limit':'unrestricted' if k is None else str(k),'switches':r['switches'],'objective':r['objective']})
    if physical_refs:pd.DataFrame(physical_refs).to_csv(ROOT/'outputs/physical_reference_sensitivity.csv',index=False)
    if calibration_rows:pd.DataFrame(calibration_rows).to_csv(ROOT/'outputs/physical_calibration_reference.csv',index=False)
    if calibration_sensitivity:pd.DataFrame(calibration_sensitivity).to_csv(ROOT/'outputs/physical_calibration_sensitivity.csv',index=False)
    model=json.loads((ROOT/'artifacts/physical_model.json').read_text())
    lines=['# 新场景与 LAAVHA 实施证据','',
           '全部结果均为开发/验证证据。训练种子 0–7，模型验证 100/101；物理 pilot 100/108/119。200–449 未用于训练、选参或新测试。',
           '', '## 已完成的实现','',
           f'- 三阶段几何、连续速度过渡、地理成像需求、预热和 drain；主场景屋顶 {CONFIG["building_bounds_m"][2][1]:g} m。',
           '- 真实 NR/LTE/Wi-Fi 栈，工程传播与显式建筑遮挡；统一上行 payload 与服务迁移。',
           '- 按包 cohort/截止时间测量，失效延迟标记，严格原始切换计数。',
           '- 物理观测训练的多时域 LSTM、可训练任务注意力、因果置信回退、未来目的地持续性判断。',
           '- 强简单对照、消融、独立服务 DP、穷举测试、包和动作完整性验证。',
           '', '## 模型验证','',
           '| 预测时域 | LSTM 归一化 MSE | 持久性 | 线性外推 |','|---|---:|---:|---:|']
    for i,h in enumerate([.1,.3,.5]):lines.append(f'| {h:.1f} s | {model["validation_mse"]["lstm"][i]:.6f} | {model["validation_mse"]["persistence"][i]:.6f} | {model["validation_mse"]["linear"][i]:.6f} |')
    lines+=['','## 物理链路 pilot','']
    if len(pilot):
        lines+=['| 方法 | n | 平均原始切换数 | 遥测按时交付 | 视频按时交付 |','|---|---:|---:|---:|---:|']
        for a,g in pilot.groupby('algorithm'):
            a={'ewma':'moving-average（CLI: ewma）','strongest-signal':'strongest-SINR'}.get(a,a)
            lines.append(f'| {a} | {len(g)} | {g.raw_handover_count.mean():.3f} | {100*g.telemetry_on_time_ratio.mean():.2f}% | {100*g.video_on_time_ratio.mean():.2f}% |')
        la=pilot[pilot.algorithm=='laavha']
        if len(la):
            lines+=['',f'LAAVHA 逐次原始计数：{dict(zip(la.seed.astype(int),la.raw_handover_count.astype(int)))}。',
                    '', '| 种子 | 实际迁移动作 |','|---|---|']
            for seed in sorted(la.seed.astype(int)):
                decisions=json.loads((ROOT/f'outputs/physical_pilot/ns3_laavha_seed{seed}.decisions.json').read_text())
                events='；'.join(f'{d["time"]:.1f} s：{CONFIG["network_names"][d["current_net"]]} → {CONFIG["network_names"][d["target_net"]]}' for d in decisions if d['handover'])
                lines.append(f'| {seed} | {events} |')
    else:lines+=['物理 pilot 尚未完成。']
    lines+=['','## 两次参考的含义','',
            '物理参考使用先于 LAAVHA 评测采集的固定 NR 校准观测。参考优化任意网络顺序/次数，仅对声明的 fresh-cohort 无队列服务模型精确；它不是闭环 packet 网络全局最优证明。',
            '', '| 种子 | 限制 | 参考采用次数 | 净任务收益 |','|---|---|---:|---:|']
    for r in calibration_rows:lines.append(f'| {r["seed"]} | {r["limit"]} | {r["switches"]} | {r["objective"]:.4f} |')
    if physical_refs:
        sensitivity=pd.DataFrame(physical_refs);unrestricted=sensitivity[sensitivity.limit.eq('unrestricted')]
        counts=unrestricted.switches.value_counts().sort_index().to_dict()
        lines+=['',f'独立校准的成本×中断敏感度（成本 0.005/0.02/0.05，中断 0/0.05/0.1/0.2 s）共 {len(unrestricted)} 组，不限次数参考的计数分布：{counts}。完整数据见 outputs/physical_reference_sensitivity.csv。',
                '另有 20 个明确标为服务抽象的名义开发任务，见 outputs/nominal_reference.csv。']
    if calibration_sensitivity:
        counts=pd.DataFrame(calibration_sensitivity).switches.value_counts().sort_index().to_dict()
        lines+=['',f'进一步将视频需求乘以 0.9/1.0/1.1，108 组参考结果的次数分布为 {counts}。在低需求或较高中断代价下，一次迁移可能获得更高净收益，见 outputs/physical_calibration_sensitivity.csv。']
    packet_rows=[]
    for folder in ['height75_fixed_controls','physical_reference_one','physical_reference_two']:
        for f in sorted((ROOT/'outputs'/folder).glob('*.summary.json')):
            d=json.loads(f.read_text())
            packet_rows.append({'source':folder,**{k:d[k] for k in ['seed','algorithm','raw_handover_count','telemetry_on_time_ratio','video_on_time_ratio','video_on_time_mbps']}})
    if packet_rows:
        pd.DataFrame(packet_rows).to_csv(ROOT/'outputs/physical_calibration_packet_controls.csv',index=False)
        lines+=['','## 实际包服务的校准对照','',
                '离线参考按先前固定 NR 观测生成计划，再将计划重放进真实协议栈。下面是实测包交付，不把该计划称为包网络最优。',
                '', '| 对照 | 种子 | 原始次数 | 遥测按时交付 | 视频按时交付 | 视频按时有效吞吐 Mbps |','|---|---:|---:|---:|---:|---:|']
        for r in packet_rows:lines.append(f'| {r["source"]}/{r["algorithm"]} | {r["seed"]} | {r["raw_handover_count"]} | {100*r["telemetry_on_time_ratio"]:.2f}% | {100*r["video_on_time_ratio"]:.2f}% | {r["video_on_time_mbps"]:.3f} |')
    lines+=['', '## 保留的前期证据','',
            '- 默认 UMa/LOS 校准中 NR 能独自完成任务，结果在 outputs/calibration/。',
            '- 85 m 屋顶导致种子 119 的独立参考和各控制器都采用三次；保留在 outputs/physical_pilot_height85/ 与 outputs/physical_training_height85/。75 m 主场景通过增加覆盖重叠校准，未对算法限制次数。',
            '- 抽象模型直接迁移到物理链路时出现多余中间迁移，结果在 outputs/physical_pilot_abstract_model/。',
            '- 阴影/遮挡下最优次数可变化，outputs/abstract_validation/ 为独立标注的服务抽象结果。',
            '', '## 尚未完成的论文级验证','',
            '完整留出种子统计、背景业务与更广站点/速度/高度组合、工程信道的外部校准、预测置信度校准及更大训练规模。当前不宣称所有方法都被 LAAVHA 超越，也不将三个 pilot 当作 250 次最终结果。',
            '', '代码与复现命令见 README.md；正文草稿见 manuscript_revision/main.pdf。']
    (ROOT/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    print(ROOT/'RESULTS.md')


if __name__=='__main__':main()
