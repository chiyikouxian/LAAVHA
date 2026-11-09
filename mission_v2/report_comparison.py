"""Summarize a complete frozen campaign using independent missions as samples."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from mission import ROOT, CONFIG, load_trace
from verify import verify


LABELS = {
    'laavha': 'LAAVHA', 'alera': 'ALERA', 'no-pred': 'LAAVHA-L',
    'no-attention': 'LAAVHA-A', 'topsis-q': 'TOPSIS-Q',
    'fuzzy-vho': 'Fuzzy-VHO', 'saw': 'SAW', 'vikor': 'VIKOR',
    'gra': 'GRA', 'copras': 'COPRAS', 'spotis': 'SPOTIS',
    'strongest-signal': 'Strongest SINR', 'topsis': 'Task TOPSIS',
    'trend': 'Linear trend', 'ewma': 'Moving average',
}
METRICS = ['raw_handover_count', 'telemetry_on_time_ratio',
           'video_on_time_ratio', 'video_on_time_mbps',
           'zero_delivery_cohort_s', 'telemetry_p95_delay_ms',
           'video_p95_delay_ms']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('directory', type=Path)
    args = ap.parse_args()
    directory = args.directory.resolve()
    manifest = json.loads((directory/'manifest.json').read_text())
    seeds, algorithms = manifest['seeds'], manifest['algorithms']
    expected_names = {f'ns3_{a}_seed{s}.summary.json' for s in seeds for a in algorithms}
    found_names = {p.name for p in directory.glob('*.summary.json')}
    if found_names != expected_names:
        raise ValueError(f'Campaign summaries differ: missing={sorted(expected_names-found_names)}, extra={sorted(found_names-expected_names)}')
    for name, expected in manifest['files_sha256'].items():
        if digest(Path(name)) != expected:
            raise ValueError(f'Frozen input changed: {name}')

    rows, packet_rows, event_rows, bases, receipts = [], [], [], {}, {}
    exogenous = {}
    for seed in seeds:
        for algo in algorithms:
            prefix = directory/f'ns3_{algo}_seed{seed}'
            summary_file = prefix.with_suffix('.summary.json')
            if not summary_file.exists():
                raise ValueError(f'Campaign incomplete: {summary_file.name}')
            s = json.loads(summary_file.read_text())
            assert s['algorithm'] == algo and s['seed'] == seed
            assert s['backend'] == 'ns3'
            for name, expected in s['source_hashes'].items():
                assert digest(ROOT/name) == expected, name
            metadata = s['run_metadata']
            for name, expected in [('building_height', 75.), ('obstruction_db', 18.),
                                   ('shadow_db', 0.), ('duration', 50.),
                                   ('threshold', .03), ('window', 3),
                                   ('alpha', .6), ('interruption', .1)]:
                assert metadata[name] == expected, (algo, seed, name)
            binary = Path('/home/suwen/ns-3.45/build/scratch/ns3.45-laavha-mission-debug')
            assert metadata['binary_sha256'] == digest(binary)
            if algo in ['laavha', 'alera', 'no-pred', 'no-attention']:
                assert metadata['checkpoint_sha256'] == digest(ROOT/'artifacts/physical_model.pt')

            payload_births = verify(prefix)
            if seed in bases:
                np.testing.assert_allclose(payload_births, bases[seed], atol=1e-7)
            else:
                bases[seed] = payload_births
            trace = load_trace(prefix.with_suffix('.trace.npz'))
            assert len(trace['time']) == 500
            if seed in exogenous:
                for name in ['time', 'position', 'speed', 'demand']:
                    np.testing.assert_allclose(trace[name], exogenous[seed][name], atol=1e-7)
            else:
                exogenous[seed] = {name: trace[name] for name in ['time', 'position', 'speed', 'demand']}
            row = {'seed': seed, 'algorithm': algo, **{k: s[k] for k in METRICS}}
            row['interruption_drops'] = s['interruption_drops']
            row['service_reference_switches'] = s['reference_model']['None']['switches']
            rows.append(row)
            decisions = json.loads(prefix.with_suffix('.decisions.json').read_text())
            for d in decisions:
                if d['handover']:
                    event_rows.append({'seed': seed, 'algorithm': algo,
                                       'time_s': d['time'],
                                       'from': CONFIG['network_names'][d['current_net']],
                                       'to': CONFIG['network_names'][d['target_net']]})
            packets = pd.read_csv(prefix.with_suffix('.packets.csv'))
            for kind, name in [(1, 'telemetry'), (2, 'video')]:
                q = packets[packets.kind.eq(kind)]
                received = q[q.received_s.ge(0)]
                delay = (received.received_s-received.generated_s)*1000
                assert np.isclose(s[name+'_on_time_ratio'], q.on_time.mean())
                goodput = q.loc[q.on_time.eq(1), 'bytes'].sum()*8/50/1e6
                assert np.isclose(s[name+'_on_time_mbps'], goodput)
                if len(received):
                    assert np.isclose(s[name+'_p95_delay_ms'], delay.quantile(.95))
                packet_rows.append({'seed': seed, 'algorithm': algo, 'traffic': name,
                                    'generated_packets': len(q), 'received_packets': len(received),
                                    'on_time_ratio': q.on_time.mean(),
                                    'final_loss_ratio': q.received_s.lt(0).mean(),
                                    'received_mean_delay_ms': delay.mean(),
                                    'received_delay_variance_ms2': delay.var(ddof=1),
                                    'received_p95_delay_ms': delay.quantile(.95)})
            receipts[summary_file.name] = digest(summary_file)

    data = pd.DataFrame(rows)
    initial_positions = [exogenous[s]['position'][0] for s in seeds]
    for i in range(len(seeds)):
        for j in range(i):
            assert np.linalg.norm(initial_positions[i]-initial_positions[j]) > 1e-3
    data.to_csv(directory/'comparison.csv', index=False)
    pd.DataFrame(packet_rows).to_csv(directory/'packet_statistics.csv', index=False)
    pd.DataFrame(event_rows).to_csv(directory/'handover_events.csv', index=False)
    statistics = []
    for algo in algorithms:
        g = data[data.algorithm.eq(algo)]
        assert len(g) == len(seeds)
        for metric in METRICS:
            statistics.append({'algorithm': algo, 'metric': metric, 'n': len(g),
                               'mean': g[metric].mean(), 'std': g[metric].std(ddof=1),
                               'variance': g[metric].var(ddof=1)})
    pd.DataFrame(statistics).to_csv(directory/'summary_statistics.csv', index=False)

    labels = [LABELS[a] for a in algorithms]
    fig, ax = plt.subplots(figsize=(14, 5.2))
    x = np.arange(len(algorithms)); width = .8/len(seeds)
    for j, seed in enumerate(seeds):
        counts = data[data.seed.eq(seed)].set_index('algorithm').loc[algorithms].raw_handover_count
        positions = x+(j-(len(seeds)-1)/2)*width
        bars = ax.bar(positions, counts, width=width, label=f'Seed {seed}')
        ax.bar_label(bars, fontsize=8)
    ax.set_xticks(x, labels, rotation=38, ha='right')
    ax.set_ylabel('Raw handover count')
    ax.set_title(f'Frozen 75 m mission: {len(seeds)} paired runs per method')
    ax.yaxis.get_major_locator().set_params(integer=True)
    ax.set_ylim(0, max(3., data.raw_handover_count.max()+1.))
    ax.grid(axis='y', alpha=.2); ax.set_axisbelow(True); ax.legend()
    fig.tight_layout(); fig.savefig(directory/'handover_counts.png', dpi=220)
    fig.savefig(directory/'handover_counts.pdf'); plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    panels = [('telemetry_on_time_ratio', 'Telemetry deadline misses (%)', True),
              ('video_on_time_ratio', 'Video deadline misses (%)', True),
              ('video_on_time_mbps', 'On-time video goodput (Mbps)', False),
              ('zero_delivery_cohort_s', 'Zero-delivery cohort duration (s)', False)]
    for ax, (metric, label, complement) in zip(axes.flat, panels):
        for j, seed in enumerate(seeds):
            values = data[data.seed.eq(seed)].set_index('algorithm').loc[algorithms, metric]
            if complement:
                values = 100*(1-values)
            ax.bar(x+(j-(len(seeds)-1)/2)*width, values, width=width, label=f'Seed {seed}')
        ax.set_xticks(x, labels, rotation=42, ha='right', fontsize=9)
        ax.set_ylabel(label); ax.set_ylim(bottom=0)
        ax.grid(axis='y', alpha=.2); ax.set_axisbelow(True)
    axes[0, 0].legend()
    fig.suptitle('Packet-level service outcomes; identical offered payload for each seed')
    fig.tight_layout(); fig.savefig(directory/'qos_comparison.png', dpi=220)
    plt.close(fig)

    lines = ['# 各算法两次配对仿真结果', '',
             f'共 {len(algorithms)} 种方法，每种 {len(seeds)} 次，共 {len(data)} 次真实 ns-3 仿真。种子为 '+
             '、'.join(map(str, seeds))+'；每次正式任务 50 s，主场景屋顶 75 m。场景、模型和算法参数沿用冻结版本，没有根据这两个种子的结果调整。', '',
             '| 方法 | '+ ' | '.join(f'seed {s} 次数' for s in seeds)+
             ' | 遥测按时交付均值 | 视频按时交付均值 | 视频按时有效吞吐均值 Mbps |',
             '|---|'+ '---:|'*len(seeds)+'---:|---:|---:|']
    for algo in algorithms:
        g = data[data.algorithm.eq(algo)].set_index('seed').loc[seeds]
        counts = ' | '.join(str(int(v)) for v in g.raw_handover_count)
        lines.append(f'| {LABELS[algo]} | {counts} | {100*g.telemetry_on_time_ratio.mean():.2f}% | '
                     f'{100*g.video_on_time_ratio.mean():.2f}% | {g.video_on_time_mbps.mean():.3f} |')
    lines += ['', 'LAAVHA-L 为去预测版本；LAAVHA-A 为以固定任务权重替换学习权重的版本。移动平均对照保留 CLI 标识 ewma，实际为五样本等权移动平均。最强信号对照最大化 SINR。各方法沿用已声明的共同可用性和滞回机制，MADM 方法为这一共同框架下的适配版本。', '',
              '## LAAVHA 实际动作', '']
    for seed in seeds:
        ev = [r for r in event_rows if r['seed'] == seed and r['algorithm'] == 'laavha']
        lines.append(f'- seed {seed}：'+ '；'.join(f'{r["time_s"]:.1f} s {r["from"]} → {r["to"]}' for r in ev)+'。')
    lines += ['', '## 文件与指标', '',
              '- handover_counts.png：每种方法两个种子的原始切换次数。',
              '- qos_comparison.png：按时交付违约、有效吞吐与零交付 cohort 的逐次对比。',
              '- comparison.csv：逐次任务指标；summary_statistics.csv：按独立任务计算的均值、样本标准差和方差。',
              '- packet_statistics.csv：实际接收包的延迟、最终未接收比例及截止交付率；handover_events.csv：全部动作时间和方向。',
              '- manifest.json：测试种子、算法、固定参数及源码/模型/二进制哈希；validation.json：完整性检查记录。', '',
              '按时有效吞吐只计算截止时间内收到的有效载荷。延迟统计针对实际收到的包，包括晚到包；最终丢包率与截止违约率分别保存。零交付 cohort 时长不是物理断联时长。', '',
              '每种方法只有两次，适合先检查行为和服务效果；均值、标准差仅作描述，不作为稳定优势或显著性结论。summary 中的服务参考针对该次运行的候选容量估计，不能当作闭环包网络全局最优。']
    (directory/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    receipt = {'completed_runs': len(data), 'expected_runs': manifest['expected_runs'],
               'seeds': seeds, 'algorithms': algorithms,
               'checks': ['frozen input hashes', 'source/checkpoint/binary consistency',
                          'physical metric ranges', 'packet deadlines and IDs',
                          'identical payload births across methods', 'action propagation',
                          'raw handover counts', 'mission geometry',
                          'identical exogenous mission within seed', 'distinct seed perturbations'],
               'summary_sha256': receipts}
    (directory/'validation.json').write_text(json.dumps(receipt, indent=2)+'\n')
    manifest['campaign_status'] = 'complete'
    (directory/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print(directory/'RESULTS.md')


if __name__ == '__main__':
    main()
