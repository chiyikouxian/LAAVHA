/*
 * 无人机遥感异构网络垂直切换智能决策软件 V1.0
 * 运行可视化界面 —— 工具条
 *
 * 提供文件导入、回放控制、时间轴定位、显示选项与画面导出。时间轴以
 * 事件序号为刻度而非连续时间，拖动后总是落在实际存在的动画事件上。
 */
import React from 'react'

const SPEEDS = [0.5, 1, 2, 4]

const TOGGLES = [
  ['compressX', '横轴压缩'],
  ['spreadNodes', '重合散开'],
  ['showTrack', '航迹'],
  ['showLinks', '服务链路'],
  ['showLabels', '标注'],
]

export default function Toolbar({
  trace, t, index, playing, speed, options,
  onOpenXml, onOpenCsv, onSeekIndex, onStep, onTogglePlay,
  onSpeed, onToggleOption, onToggleTheme, onExport,
}) {
  const steps = Math.max(1, trace ? trace.times.length - 1 : 1)
  const ready = Boolean(trace)

  return (
    <div className="toolbar">
      <div className="tool-group">
        <label className="file-btn">
          导入轨迹 XML
          <input type="file" accept=".xml" onChange={onOpenXml} />
        </label>
        <label className="file-btn is-ghost">
          导入时间序列 CSV
          <input type="file" accept=".csv" onChange={onOpenCsv} />
        </label>
      </div>

      <div className="tool-group">
        <button
          type="button"
          className="btn is-primary"
          onClick={onTogglePlay}
          disabled={!ready}
        >
          {playing ? '暂停' : '播放'}
        </button>
        <button type="button" className="btn is-icon" onClick={() => onStep(-1)} disabled={!ready}>
          ◀
        </button>
        <button type="button" className="btn is-icon" onClick={() => onStep(1)} disabled={!ready}>
          ▶
        </button>
      </div>

      <div className="tool-group is-grow">
        <input
          type="range"
          className="timeline-range"
          min={0}
          max={steps}
          step={1}
          value={index}
          onChange={(e) => onSeekIndex(Number(e.target.value))}
          disabled={!ready}
        />
        <span className="time-readout">{t.toFixed(2)} s</span>
      </div>

      <div className="tool-group">
        <span className="tool-label">倍速</span>
        <select
          className="select"
          value={speed}
          onChange={(e) => onSpeed(Number(e.target.value))}
          disabled={!ready}
        >
          {SPEEDS.map((s) => (
            <option key={s} value={s}>{`${s}×`}</option>
          ))}
        </select>
      </div>

      <div className="tool-group is-toggles">
        {TOGGLES.map(([key, text]) => (
          <button
            key={key}
            type="button"
            className={`chip${options[key] ? ' is-on' : ''}`}
            onClick={() => onToggleOption(key)}
            disabled={!ready}
          >
            {text}
          </button>
        ))}
      </div>

      <div className="tool-group">
        <button type="button" className="btn" onClick={onToggleTheme}>
          {options.theme === 'dark' ? '浅色' : '深色'}
        </button>
        <button type="button" className="btn" onClick={onExport} disabled={!ready}>
          导出 PNG
        </button>
      </div>
    </div>
  )
}
