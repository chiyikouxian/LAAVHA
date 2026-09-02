/*
 * 无人机遥感异构网络垂直切换智能决策软件 V1.0
 * 运行可视化界面 —— 主组件
 *
 * 组织顶栏、工具条、三个几何视图与指标面板，并维护回放状态。
 *
 * 回放以动画事件序号推进而非连续时间：动画事件只在离散时刻产生，
 * 按事件推进可保证每一帧都对应一个真实存在的场景状态。
 */
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import Toolbar from './components/Toolbar.jsx'
import CanvasView from './components/CanvasView.jsx'
import MetricsPanel from './components/MetricsPanel.jsx'
import { drawElevation, drawTimeline, drawTopology } from './lib/canvasRender.js'
import { loadSeries, loadTrace, NET_NAMES } from './lib/traceModel.js'
import { THEMES } from './lib/theme.js'

const DEFAULT_OPTIONS = {
  theme: 'dark',
  compressX: true,
  spreadNodes: true,
  showTrack: true,
  showLinks: true,
  showLabels: true,
}

/** 取当前服务网络：优先取自轨迹标注，轨迹未给出时退回时间序列。 */
function servingAt(states, series, t) {
  for (const state of states) {
    if (state.role === 'uav' && state.serving) return state.serving
  }
  const row = series ? series.rowAt(t) : null
  if (row) {
    const net = Number(row.current_net)
    if (Number.isFinite(net)) return NET_NAMES[net] || null
  }
  return null
}

export default function App() {
  const [trace, setTrace] = useState(null)
  const [series, setSeries] = useState(null)
  const [index, setIndex] = useState(0)
  const [playing, setPlaying] = useState(false)
  const [speed, setSpeed] = useState(1)
  const [options, setOptions] = useState(DEFAULT_OPTIONS)
  const [notice, setNotice] = useState('请导入仿真运行产出的动画轨迹文件（XML）')
  const [hover, setHover] = useState(null)
  const timerRef = useRef(null)

  const t = trace && trace.times.length ? trace.times[Math.min(index, trace.times.length - 1)] : 0
  const states = useMemo(() => (trace ? trace.stateAt(t) : []), [trace, t])
  const serving = useMemo(() => servingAt(states, series, t), [states, series, t])

  // 配色切换同步到根元素，供 CSS 变量与画布取同一套取值
  useEffect(() => {
    document.documentElement.dataset.theme = options.theme
  }, [options.theme])

  // 自动回放：按固定墙钟间隔推进一个动画事件，走到末尾自动停止
  useEffect(() => {
    if (!playing || !trace) return undefined
    timerRef.current = window.setInterval(() => {
      setIndex((prev) => {
        if (prev >= trace.times.length - 1) {
          setPlaying(false)
          return prev
        }
        return prev + 1
      })
    }, Math.max(20, 120 / speed))
    return () => window.clearInterval(timerRef.current)
  }, [playing, speed, trace])

  const stepBy = useCallback(
    (delta) => {
      if (!trace) return
      setPlaying(false)
      setIndex((prev) => Math.max(0, Math.min(prev + delta, trace.times.length - 1)))
    },
    [trace],
  )

  // 左右方向键逐周期，空格播放/暂停
  useEffect(() => {
    const onKey = (event) => {
      if (event.target instanceof HTMLInputElement) return
      if (event.key === 'ArrowLeft') stepBy(-1)
      else if (event.key === 'ArrowRight') stepBy(1)
      else if (event.key === ' ') {
        event.preventDefault()
        setPlaying((prev) => !prev)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [stepBy])

  const readFile = (event, handler) => {
    const file = event.target.files && event.target.files[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => handler(String(reader.result), file.name)
    reader.onerror = () => setNotice(`读取失败：${file.name}`)
    reader.readAsText(file)
    event.target.value = ''
  }

  const handleOpenXml = (event) =>
    readFile(event, (text, name) => {
      try {
        const parsed = loadTrace(text, name)
        if (parsed.nodes.size === 0) {
          setNotice(`${name} 中未解析出任何节点，请确认是仿真产出的动画轨迹文件`)
          return
        }
        setTrace(parsed)
        setIndex(0)
        setPlaying(false)
        setNotice(
          `已导入 ${name}：${parsed.nodes.size} 个节点、${parsed.times.length} 个事件时刻、` +
            `时长 ${parsed.duration.toFixed(2)} s、切换 ${parsed.handovers.length} 次`,
        )
      } catch (err) {
        setNotice(`解析失败：${err.message}`)
      }
    })

  const handleOpenCsv = (event) =>
    readFile(event, (text, name) => {
      try {
        const parsed = loadSeries(text, name)
        if (parsed.rows.length === 0) {
          setNotice(`${name} 中未解析出决策周期记录`)
          return
        }
        setSeries(parsed)
        setNotice(`已导入 ${name}：${parsed.rows.length} 个决策周期`)
      } catch (err) {
        setNotice(`解析失败：${err.message}`)
      }
    })

  const seekTime = useCallback(
    (target) => {
      if (!trace) return
      setPlaying(false)
      setIndex(trace.indexAt(target))
    },
    [trace],
  )

  const toggleOption = (key) =>
    setOptions((prev) => ({ ...prev, [key]: !prev[key] }))

  const toggleTheme = () =>
    setOptions((prev) => ({ ...prev, theme: prev.theme === 'dark' ? 'light' : 'dark' }))

  /**
   * 导出当前画面。
   *
   * 把三个画布按纵向拼接为一张位图；指标面板为文档元素，无法直接写入
   * 位图，因此导出的是几何视图部分，与界面所见一致。
   */
  const handleExport = () => {
    const canvases = [...document.querySelectorAll('canvas.card-canvas')]
    if (canvases.length === 0) return
    const gap = 10
    const width = Math.max(...canvases.map((c) => c.clientWidth))
    const height = canvases.reduce((sum, c) => sum + c.clientHeight, 0) + gap * (canvases.length - 1)
    const dpr = window.devicePixelRatio || 1

    const out = document.createElement('canvas')
    out.width = Math.round(width * dpr)
    out.height = Math.round(height * dpr)
    const ctx = out.getContext('2d')
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    ctx.fillStyle = THEMES[options.theme].bg
    ctx.fillRect(0, 0, width, height)

    let cursor = 0
    for (const canvas of canvases) {
      ctx.drawImage(canvas, 0, cursor, canvas.clientWidth, canvas.clientHeight)
      cursor += canvas.clientHeight + gap
    }

    const link = document.createElement('a')
    const stem = (trace.sourceName || 'frame').replace(/\.xml$/i, '')
    link.download = `${stem}_t${t.toFixed(2)}.png`
    link.href = out.toDataURL('image/png')
    link.click()
    setNotice(`已导出 ${link.download}`)
  }

  const drawTopo = useCallback(
    (ctx, size) => drawTopology(ctx, size, trace, t, options, serving),
    [trace, t, options, serving],
  )
  const drawElev = useCallback(
    (ctx, size) => drawElevation(ctx, size, trace, series, t, options, serving),
    [trace, series, t, options, serving],
  )
  const drawTl = useCallback(
    (ctx, size) => drawTimeline(ctx, size, trace, t, options),
    [trace, t, options],
  )

  const row = series && trace ? series.rowAt(t) : null

  return (
    <div className="app">
      <header className="app-head">
        <div className="title-block">
          <h1>无人机遥感异构网络垂直切换智能决策软件 V1.0</h1>
          <p>运行可视化</p>
        </div>
        <div className="head-meta">
          {trace ? (
            <>
              <span className="stamp">t = {t.toFixed(2)} s</span>
              <span className="meta-line">
                {row ? `决策周期 #${row.decision_index}　` : ''}
                {serving ? `服务网络 ${serving}` : ''}
              </span>
            </>
          ) : null}
        </div>
      </header>

      <Toolbar
        trace={trace}
        t={t}
        index={index}
        playing={playing}
        speed={speed}
        options={options}
        onOpenXml={handleOpenXml}
        onOpenCsv={handleOpenCsv}
        onSeekIndex={(value) => {
          setPlaying(false)
          setIndex(value)
        }}
        onStep={stepBy}
        onTogglePlay={() => setPlaying((prev) => !prev)}
        onSpeed={setSpeed}
        onToggleOption={toggleOption}
        onToggleTheme={toggleTheme}
        onExport={handleExport}
      />

      <p className="notice">{notice}</p>

      {trace ? (
        <main className="app-body">
          <div className="stage">
            <CanvasView
              title="拓扑视图"
              extra={`横轴 x/m　纵轴 y/m　${options.compressX ? '横轴分段压缩' : '真实比例'}`}
              draw={drawTopo}
              minHeight={260}
              onPick={setHover}
            />
            <CanvasView
              title="侧视高度视图"
              extra="横轴 t/s　纵轴 高度/m"
              draw={drawElev}
              minHeight={168}
            />
            <CanvasView
              title="服务网络时间轴"
              extra={`切换事件 ${trace.handovers.length} 次`}
              draw={drawTl}
              minHeight={106}
            />
          </div>
          <MetricsPanel
            trace={trace}
            series={series}
            t={t}
            serving={serving}
            onSeek={seekTime}
          />
        </main>
      ) : (
        <div className="empty">
          <p>尚未导入运行数据</p>
          <p className="empty-hint">
            动画轨迹文件由仿真端 <code>--animFile</code> 参数产出；
            决策时间序列文件由 <code>--time-series-output</code> 参数产出，
            用于显示候选网络评分、链路指标与飞行高度。
          </p>
        </div>
      )}

      {hover ? (
        <div className="tooltip" style={{ left: hover.x + 18, top: hover.y + 90 }}>
          <strong>{hover.item.state.descr || `节点 ${hover.item.id}`}</strong>
          <span>
            x = {hover.item.state.x.toFixed(1)} m　y = {hover.item.state.y.toFixed(1)} m
          </span>
        </div>
      ) : null}
    </div>
  )
}
