/*
 * 无人机遥感异构网络垂直切换智能决策软件 V1.0
 * 运行可视化界面 —— 指标面板
 *
 * 呈现动画轨迹本身不包含的决策过程数据：当前服务网络、飞行状态、
 * 三个候选网络的实时评分与排序、五类链路指标，以及切换事件序列。
 * 数据来源为决策时间序列文件；未导入该文件时给出提示。
 */
import React from 'react'
import { NET_COLORS } from '../lib/theme.js'
import { NET_NAMES } from '../lib/traceModel.js'

const NET_ORDER = ['5G', 'LTE', 'WiFi']
const NET_KEYS = { '5G': '5g', LTE: 'lte', WiFi: 'wifi' }

// 五类链路指标的显示名称、列名前缀、小数位与单位
const METRIC_ROWS = [
  ['信干噪比 SINR', 'sinr', 2, 'dB'],
  ['参考信号功率', 'rsrp', 1, 'dBm'],
  ['时延', 'delay', 2, 'ms'],
  ['吞吐量', 'throughput', 2, 'Mb/s'],
  ['丢包率', 'plr', 4, ''],
]

const NET_NOTES = {
  '5G': '5G 代理链路',
  LTE: 'LTE 蜂窝链路',
  WiFi: 'WiFi 接入链路',
}

/** 当前服务网络卡片。 */
function ServingCard({ serving }) {
  const color = NET_COLORS[serving] || 'var(--track)'
  return (
    <div className="serving-card" style={{ '--net': color }}>
      <div className="serving-bar" />
      <div className="serving-body">
        <strong>{serving || '未知'}</strong>
        <span>{NET_NOTES[serving] || '轨迹未记录服务网络'}</span>
      </div>
    </div>
  )
}

/** 飞行状态四格。高度与速度取自决策时间序列，平面位置取自动画轨迹。 */
function FlightGrid({ altitude, velocity, x, y }) {
  const cells = [
    ['高度', altitude === null ? '—' : `${altitude.toFixed(1)} m`],
    ['速度', velocity === null ? '—' : `${velocity.toFixed(1)} m/s`],
    ['水平位置 x', `${x.toFixed(1)} m`],
    ['水平位置 y', `${y.toFixed(1)} m`],
  ]
  return (
    <div className="stat-grid">
      {cells.map(([label, value]) => (
        <div className="stat-cell" key={label}>
          <span className="stat-label">{label}</span>
          <span className="stat-value">{value}</span>
        </div>
      ))}
    </div>
  )
}

/** 候选网络评分条。条长按当前周期内的最高分归一化。 */
function ScoreBars({ series, row, serving }) {
  if (!series || !row) return <p className="hint">未导入决策时间序列</p>

  const scores = NET_ORDER.map((net) => [net, series.value(row, `score_${NET_KEYS[net]}`)])
  const valid = scores.filter(([, v]) => v !== null).map(([, v]) => v)
  const peak = valid.length ? Math.max(...valid, 1e-9) : 1
  const best = scores.reduce(
    (acc, cur) => (cur[1] !== null && (acc[1] === null || cur[1] > acc[1]) ? cur : acc),
    [null, null],
  )[0]

  const target = Number(row.target_net)
  const targetName = Number.isFinite(target) ? NET_NAMES[target] || '—' : '—'
  const handover = row.handover === '1'

  return (
    <>
      <div className="score-list">
        {scores.map(([net, value]) => (
          <div className="score-row" key={net}>
            <span className="score-mark">{net === serving ? '▸' : ''}</span>
            <span className={`score-net${net === best ? ' is-best' : ''}`}>{net}</span>
            <span className="score-track">
              <span
                className="score-fill"
                style={{
                  width: `${value === null ? 0 : Math.max(0, value / peak) * 100}%`,
                  background: NET_COLORS[net],
                }}
              />
            </span>
            <span className={`score-num${net === best ? ' is-best' : ''}`}>
              {value === null ? '—' : value.toFixed(4)}
            </span>
          </div>
        ))}
      </div>
      <p className={`decision${handover ? ' is-handover' : ''}`}>
        本周期决策目标：{targetName}
        {handover ? '　（触发切换）' : ''}
      </p>
    </>
  )
}

/** 三个候选网络的五类链路指标表，当前服务网络所在列加底色。 */
function MetricTable({ series, row, serving }) {
  if (!series || !row) return <p className="hint">未导入决策时间序列</p>
  return (
    <table className="metric-table">
      <thead>
        <tr>
          <th />
          {NET_ORDER.map((net) => (
            <th
              key={net}
              className={net === serving ? 'is-serving' : ''}
              style={{ '--net': NET_COLORS[net] }}
            >
              {net}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {METRIC_ROWS.map(([label, key, digits, unit]) => (
          <tr key={key}>
            <th scope="row">
              {label}
              {unit ? <em>{unit}</em> : null}
            </th>
            {NET_ORDER.map((net) => {
              const value = series.value(row, `${key}_${NET_KEYS[net]}`)
              return (
                <td key={net} className={net === serving ? 'is-serving' : ''}>
                  {value === null ? '—' : value.toFixed(digits)}
                </td>
              )
            })}
          </tr>
        ))}
      </tbody>
    </table>
  )
}

/** 切换事件序列。已发生的事件高亮，未发生的事件淡显，可点击跳转。 */
function EventList({ handovers, t, onSeek }) {
  if (handovers.length === 0) {
    return <p className="hint">本次运行未发生服务网络切换</p>
  }
  return (
    <ul className="event-list">
      {handovers.map((ev) => {
        const done = ev.t <= t + 1e-9
        return (
          <li
            key={`${ev.t}-${ev.to}`}
            className={done ? 'is-done' : ''}
            style={{ '--net': NET_COLORS[ev.to] }}
          >
            <button type="button" onClick={() => onSeek(ev.t)}>
              <span className="event-time">t={ev.t.toFixed(1)} s</span>
              <span className="event-path">
                {ev.from} → {ev.to}
              </span>
            </button>
          </li>
        )
      })}
    </ul>
  )
}

function Block({ title, children }) {
  return (
    <section className="panel-block">
      <h3>{title}</h3>
      {children}
    </section>
  )
}

export default function MetricsPanel({ trace, series, t, serving, onSeek }) {
  const row = series ? series.rowAt(t) : null
  const uav = trace.uav()
  const pos = uav ? uav.pos.at(t, [uav.x0, uav.y0]) : [0, 0]

  return (
    <aside className="panel">
      <Block title="当前服务网络">
        <ServingCard serving={serving} />
      </Block>
      <Block title="飞行状态">
        <FlightGrid
          altitude={series ? series.value(row, 'altitude') : null}
          velocity={series ? series.value(row, 'velocity') : null}
          x={pos[0]}
          y={pos[1]}
        />
      </Block>
      <Block title="候选网络评分">
        <ScoreBars series={series} row={row} serving={serving} />
      </Block>
      <Block title="链路指标（3 网络 × 5 指标）">
        <MetricTable series={series} row={row} serving={serving} />
      </Block>
      <Block title={`切换事件序列（${trace.handovers.length} 次）`}>
        <EventList handovers={trace.handovers} t={t} onSeek={onSeek} />
      </Block>
    </aside>
  )
}
