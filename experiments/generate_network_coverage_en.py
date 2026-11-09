#!/usr/bin/env python3
"""Draw the executable mission layout in the original paper's map style."""
from pathlib import Path
import hashlib
import json
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Rectangle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'mission_v2'))
from mission import CONFIG, demand_at, motion

OUT = ROOT / 'plots_chapter3_v2' / 'plots_chapter3_v2_en'


def add_label(ax, text, xy, xytext, color='#174a73', size=13):
    return ax.annotate(
        text, xy=xy, xytext=xytext, ha='left', va='center', fontsize=size,
        color=color,
        bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                  edgecolor='#d7e0ea', linewidth=1.2, alpha=0.94),
        arrowprops=dict(arrowstyle='-', color=color, linewidth=1.2,
                        shrinkA=5, shrinkB=4), zorder=12,
    )


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Liberation Sans'],
        'axes.unicode_minus': False, 'svg.fonttype': 'none', 'pdf.fonttype': 42,
    })
    fig = plt.figure(figsize=(14.2, 10.4), dpi=200, facecolor='white')
    ax = fig.add_axes([0.07, 0.09, 0.66, 0.87])
    ax.set(xlim=(0, 2), ylim=(0, 2), aspect='equal', facecolor='#f7f9fc')
    ax.set_xticks(np.arange(0, 2.01, 0.5))
    ax.set_yticks(np.arange(0, 2.01, 0.5))
    ax.grid(True, color='#b7c9dd', linestyle=':', linewidth=0.9, alpha=0.8)
    ax.set_xlabel('x / km', fontsize=15)
    ax.set_ylabel('y / km', fontsize=15)
    ax.tick_params(labelsize=13, width=1.2)
    for spine in ax.spines.values():
        spine.set_color('#1f2d40')
        spine.set_linewidth(2.0)

    sites = np.asarray(CONFIG['sites'], dtype=float) / 1000
    radii = np.asarray(CONFIG['nominal_radii_m'], dtype=float) / 1000
    styles = {
        0: dict(face='#f5b5bf', edge='#d81b58', marker='P', site='#c31349', z=2),
        1: dict(face='#f8dca4', edge='#f5aa16', marker='^', site='#ed7d0b', z=1),
        2: dict(face='#b8dce8', edge='#079fe0', marker='o', site='#0b8bc5', z=4),
    }
    for n in [1, 0, 2]:
        style = styles[n]
        ax.add_patch(Circle(tuple(sites[n, :2]), radii[n],
                            facecolor=style['face'], edgecolor=style['edge'],
                            linewidth=2.0, linestyle=(0, (5, 3)), alpha=0.48,
                            zorder=style['z']))

    bounds = np.asarray(CONFIG['building_bounds_m'], dtype=float) / 1000
    ax.add_patch(Rectangle(tuple(bounds[:2, 0]),
                           bounds[0, 1]-bounds[0, 0], bounds[1, 1]-bounds[1, 0],
                           facecolor='#8795a8', edgecolor='#64748b',
                           linewidth=1.4, alpha=0.85, zorder=5))
    duration = CONFIG['duration_s']
    times = np.linspace(0, duration, int(duration*100)+1)
    route_x = np.array([motion(t)[0] for t in times])
    route_y = CONFIG['start'][1] / 1000
    path = np.column_stack((route_x / 1000, np.full(len(times), route_y)))
    ax.plot(path[:, 0], path[:, 1], color='#064b91', linewidth=4.0,
            solid_capstyle='round', zorder=7)
    for fraction in [0.04, 0.27, 0.63, 0.85]:
        x = path[0, 0] + fraction*(path[-1, 0]-path[0, 0])
        ax.annotate('', xy=(x-0.07, route_y), xytext=(x, route_y),
                    arrowprops=dict(arrowstyle='-|>', color='#064b91',
                                    linewidth=3.2, mutation_scale=18), zorder=8)
    imaging = np.array([demand_at(x) == CONFIG['imaging_mbps'] for x in route_x])
    imaging_bounds = [float(route_x[imaging].min()/1000),
                      float(route_x[imaging].max()/1000)]
    ax.add_patch(Rectangle((imaging_bounds[0], route_y-.055),
                           np.ptp(imaging_bounds), .11, facecolor='#b8dce8',
                           edgecolor='#0b8bc5', hatch='////', linewidth=1.4,
                           alpha=.65, zorder=6))
    for n in [1, 0, 2]:
        style = styles[n]
        ax.scatter(*sites[n, :2], marker=style['marker'],
                   s=310 if n != 2 else 230, c=style['site'],
                   edgecolors='white', linewidths=2.2, zorder=10)
    ax.scatter(*path[0], marker='<', s=160, c='#174f8f',
               edgecolors='white', linewidths=1.4, zorder=11)
    ax.scatter(*path[-1], marker='o', s=80, c='#174f8f',
               edgecolors='white', linewidths=1.2, zorder=11)
    ax.text(path[0, 0]+.035, route_y+.09, 'Start', fontsize=12, color='#174a73')
    ax.text(path[-1, 0]-.035, route_y+.09, 'End', ha='right', fontsize=12,
            color='#174a73')

    add_label(ax, r'Mission area: 2 km $\times$ 2 km', (.12, 1.93), (.02, 1.93), size=14)
    add_label(ax, f"Wi-Fi access point / imaging site\nNominal radius {radii[2]*1000:g} m",
              tuple(sites[2, :2]), (.55, 1.65), color='#087fac')
    add_label(ax, f'LTE base station\nNominal radius {radii[1]:g} km',
              tuple(sites[1, :2]), (.09, 1.36), color='#a34a0b')
    add_label(ax, f'5G NR gNB\nNominal radius {radii[0]*1000:g} m',
              tuple(sites[0, :2]), (1.35, 1.43), color='#b0184c')
    add_label(ax, 'UAV flight path\n(east to west)', (.51, route_y),
              (.10, .68), size=12.5)
    add_label(ax, f'Building obstruction\nRoof height {bounds[2, 1]*1000:g} m',
              (bounds[0].mean(), bounds[1, 0]), (1.21, .42), color='#56677c')
    add_label(ax, f"Low-speed imaging: {motion(25)[1]:g} m/s\n{CONFIG['imaging_mbps']:g} Mbps images",
              (np.mean(imaging_bounds), route_y-.055), (.55, .58), size=12.5)
    for x, title, speed in [(1.46, 'Cruise', motion(5)[1]),
                            (.65, 'Return', motion(40)[1])]:
        ax.text(x, .86, f"{title}: {speed:g} m/s\n{CONFIG['preview_mbps']:g} Mbps preview",
                ha='center', va='top', fontsize=11.5, color='#174a73')

    ax.plot([.08, .58], [.08, .08], color='#172237', linewidth=5, zorder=11)
    for x in [.08, .58]:
        ax.plot([x, x], [.05, .11], color='#172237', linewidth=4, zorder=11)
    ax.text(.33, .125, '500 m', ha='center', va='bottom', fontsize=13, color='#172237')
    handles = [
        Rectangle((0, 0), 1, 1, facecolor='#86cbe5', edgecolor='#079fe0', alpha=.55),
        Rectangle((0, 0), 1, 1, facecolor='#f8dca4', edgecolor='#f5aa16', alpha=.65),
        Rectangle((0, 0), 1, 1, facecolor='#f5b5bf', edgecolor='#d81b58', alpha=.70),
        Line2D([0], [0], color='#064b91', linewidth=4, marker='<', markersize=10),
    ]
    labels = [f'Wi-Fi nominal coverage\n(r = {radii[2]*1000:g} m)',
              f'LTE nominal coverage\n(r = {radii[1]:g} km)',
              f'5G NR nominal coverage\n(r = {radii[0]*1000:g} m)', 'UAV flight path']
    for n, label in [(2, 'Wi-Fi access point'), (1, 'LTE base station'), (0, '5G NR gNB')]:
        style = styles[n]
        handles.append(Line2D([0], [0], marker=style['marker'], color='none',
                              markerfacecolor=style['site'], markeredgecolor='white',
                              markersize=11))
        labels.append(label)
    handles.extend([
        Rectangle((0, 0), 1, 1, facecolor='#b8dce8', edgecolor='#0b8bc5', hatch='////'),
        Rectangle((0, 0), 1, 1, facecolor='#8795a8', edgecolor='#64748b'),
        Line2D([0], [0], marker='<', color='none', markerfacecolor='#174f8f',
               markeredgecolor='white', markersize=10),
    ])
    labels.extend(['Imaging task segment', 'Building footprint', 'UAV at mission start'])
    ax.legend(handles, labels, title='Legend', loc='upper left',
              bbox_to_anchor=(1.03, .99), borderaxespad=0, frameon=True,
              facecolor='white', edgecolor='#c8d4e1', framealpha=.95,
              fontsize=10.8, title_fontsize=14, labelspacing=.8,
              handlelength=2.3, handletextpad=.9)
    ax.text(1.035, .32,
            f"Nominal mission: {duration:g} s\nUAV altitude: {CONFIG['start'][2]:g} m\n\n"
            'Coverage circles show nominal\nlayout scales. Actual service is\n'
            'determined by propagation\nand packet delivery.',
            transform=ax.transAxes, ha='left', va='top', fontsize=10.5,
            color='#56677c', linespacing=1.5)
    for suffix in ['png', 'pdf', 'svg']:
        output = OUT.with_suffix('.'+suffix)
        fig.savefig(output, dpi=300, facecolor='white')
        print(f'Saved: {output}')
    plt.close(fig)
    provenance = {
        'config': str(ROOT / 'mission_v2/config.json'),
        'config_sha256': hashlib.sha256((ROOT / 'mission_v2/config.json').read_bytes()).hexdigest(),
        'route_source': str(ROOT / 'mission_v2/mission.py'),
        'route_source_sha256': hashlib.sha256((ROOT / 'mission_v2/mission.py').read_bytes()).hexdigest(),
        'sites_m': CONFIG['sites'], 'nominal_radii_m': CONFIG['nominal_radii_m'],
        'nominal_route_start_m': (path[0]*1000).tolist(),
        'nominal_route_end_m': (path[-1]*1000).tolist(),
        'imaging_x_bounds_m': (np.array(imaging_bounds)*1000).tolist(),
        'building_bounds_m': CONFIG['building_bounds_m'],
    }
    OUT.with_suffix('.json').write_text(json.dumps(provenance, indent=2)+'\n')


if __name__ == '__main__':
    main()
