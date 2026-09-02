/*
 * 无人机遥感异构网络垂直切换智能决策软件 V1.0
 * 运行可视化界面 —— 画布绘制
 *
 * 负责三个几何视图的绘制：拓扑视图、侧视高度视图、服务网络时间轴。
 * 指标数值部分由 React 组件以文档元素呈现，不在本文件中绘制。
 *
 * 所有绘制函数都接受设备像素比参数，在高分屏上按比例放大绘制，使
 * 线条与文字保持清晰。
 */

import { AxisMap, LabelPlacer, clusterSpans, rolePriority, spreadOverlaps, tickGroups } from './layout.js'
import { NET_COLORS, THEMES, mixHex, rgb } from './theme.js'
import { ROLE_LABELS } from './traceModel.js'

const FONT = '"Noto Sans CJK SC","Microsoft YaHei",sans-serif'

// 各角色的图元形状
const ROLE_SHAPES = {
  uav: 'diamond', wifi_ap: 'square', lte_enb: 'triangle',
  gnb: 'triangle', relay: 'circle', sta: 'circle',
}

/** 按设备像素比初始化画布并返回绘图上下文。 */
export function prepareCanvas(canvas, width, height) {
  const dpr = window.devicePixelRatio || 1
  canvas.width = Math.round(width * dpr)
  canvas.height = Math.round(height * dpr)
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`
  const ctx = canvas.getContext('2d')
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  ctx.clearRect(0, 0, width, height)
  return ctx
}

function setFont(ctx, size, bold = false) {
  ctx.font = `${bold ? '600 ' : ''}${size}px ${FONT}`
}

function fillText(ctx, text, x, y, { size = 11, bold = false, color, align = 'left', baseline = 'top' } = {}) {
  setFont(ctx, size, bold)
  ctx.fillStyle = color
  ctx.textAlign = align
  ctx.textBaseline = baseline
  ctx.fillText(text, x, y)
}

function strokeLine(ctx, points, color, width = 1, dash = null) {
  ctx.save()
  ctx.strokeStyle = color
  ctx.lineWidth = width
  ctx.setLineDash(dash || [])
  ctx.beginPath()
  points.forEach(([x, y], i) => (i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)))
  ctx.stroke()
  ctx.restore()
}

function roundRect(ctx, x0, y0, x1, y1, r, fill, stroke = null) {
  const radius = Math.min(r, (x1 - x0) / 2, (y1 - y0) / 2)
  ctx.beginPath()
  ctx.moveTo(x0 + radius, y0)
  ctx.lineTo(x1 - radius, y0)
  ctx.quadraticCurveTo(x1, y0, x1, y0 + radius)
  ctx.lineTo(x1, y1 - radius)
  ctx.quadraticCurveTo(x1, y1, x1 - radius, y1)
  ctx.lineTo(x0 + radius, y1)
  ctx.quadraticCurveTo(x0, y1, x0, y1 - radius)
  ctx.lineTo(x0, y0 + radius)
  ctx.quadraticCurveTo(x0, y0, x0 + radius, y0)
  ctx.closePath()
  if (fill) {
    ctx.fillStyle = fill
    ctx.fill()
  }
  if (stroke) {
    ctx.strokeStyle = stroke
    ctx.lineWidth = 1
    ctx.stroke()
  }
}

/** 按角色绘制节点图元。无人机附加一层光晕以在密集区域中突出。 */
function drawGlyph(ctx, theme, role, color, cx, cy, radius, glow = true) {
  const shape = ROLE_SHAPES[role] || 'circle'
  if (role === 'uav' && glow) {
    const halo = ctx.createRadialGradient(cx, cy, radius * 0.4, cx, cy, radius + 9)
    halo.addColorStop(0, color.replace('rgb(', 'rgba(').replace(')', ',0.45)'))
    halo.addColorStop(1, color.replace('rgb(', 'rgba(').replace(')', ',0)'))
    ctx.fillStyle = halo
    ctx.beginPath()
    ctx.arc(cx, cy, radius + 9, 0, Math.PI * 2)
    ctx.fill()
  }

  ctx.save()
  ctx.fillStyle = color
  ctx.strokeStyle = theme.panel
  ctx.lineWidth = 1.5
  ctx.beginPath()
  if (shape === 'diamond') {
    ctx.moveTo(cx, cy - radius)
    ctx.lineTo(cx + radius, cy)
    ctx.lineTo(cx, cy + radius)
    ctx.lineTo(cx - radius, cy)
    ctx.closePath()
  } else if (shape === 'square') {
    const r = radius * 0.92
    ctx.rect(cx - r, cy - r, r * 2, r * 2)
  } else if (shape === 'triangle') {
    ctx.moveTo(cx, cy - radius)
    ctx.lineTo(cx + radius, cy + radius * 0.8)
    ctx.lineTo(cx - radius, cy + radius * 0.8)
    ctx.closePath()
  } else {
    ctx.arc(cx, cy, radius, 0, Math.PI * 2)
  }
  ctx.fill()
  ctx.stroke()
  ctx.restore()
}

/** 节点标注文本。无人机附带当前服务网络，其余节点用中文角色名。 */
function nodeLabel(state) {
  if (state.role === 'uav') {
    return `无人机 UAV${state.serving ? `（服务：${state.serving}）` : ''}`
  }
  if (state.role === 'sta') return `STA-${state.id}`
  const head = state.descr.split('|')[0].trim()
  return head || ROLE_LABELS[state.role] || `节点 ${state.id}`
}

/**
 * 绘制拓扑视图。
 *
 * 自下而上划分三条横带：图例、横轴刻度、绘图区，避免三者互相压叠。
 * 返回节点的画面位置，供上层做鼠标拾取。
 */
export function drawTopology(ctx, size, trace, t, options, serving) {
  const theme = THEMES[options.theme]
  const { width, height } = size
  const states = trace.stateAt(t)

  const legendH = 20
  const tickH = 17
  const padX = 12
  const plotX0 = padX + 38
  const plotX1 = width - padX
  const plotY0 = 14
  const plotY1 = height - legendH - tickH

  const uav = trace.uav()
  const xs = states.map((s) => s.x)
  const ys = states.map((s) => s.y)
  if (uav && options.showTrack) {
    uav.pos.values.forEach((p) => {
      xs.push(p[0])
      ys.push(p[1])
    })
  }

  const spans = clusterSpans(xs, 140, 26)
  const axis = new AxisMap(spans, plotX0, plotX1, options.compressX)
  const groups = tickGroups(xs, spans)

  let yLo = Math.min(...ys)
  let yHi = Math.max(...ys)
  if (yHi - yLo < 40) {
    const mid = (yHi + yLo) / 2
    yLo = mid - 20
    yHi = mid + 20
  }
  const padY = (yHi - yLo) * 0.16
  yLo -= padY
  yHi += padY
  const toPy = (v) => plotY1 - ((plotY1 - plotY0) * (v - yLo)) / (yHi - yLo)

  drawTopoGrid(ctx, theme, axis, toPy, groups, [plotX0, plotY0, plotX1, plotY1], yLo, yHi)
  if (options.showTrack && uav) {
    drawTrack(ctx, theme, trace, uav, axis, toPy, t)
  }

  const placed = states.map((state) => ({
    id: state.id,
    role: state.role,
    state,
    px: axis.toPx(state.x),
    py: toPy(state.y),
    r: Math.max(5, Math.min(16, 4.5 + Math.max(state.size[0], state.size[1]) * 0.26)),
  }))
  if (options.spreadNodes) spreadOverlaps(placed)
  else placed.forEach((it) => Object.assign(it, { dx: 0, dy: 0, moved: false }))

  if (options.showLinks) drawServiceLink(ctx, theme, placed, serving)
  drawNodes(ctx, theme, placed, options, [padX, plotY0, plotX1, plotY1])
  drawLegend(ctx, theme, padX, plotY1 + tickH + 4, plotX1)
  return placed
}

function drawTopoGrid(ctx, theme, axis, toPy, groups, plot, yLo, yHi) {
  const [plotX0, plotY0, plotX1, plotY1] = plot

  // 纵轴刻度：间距不足时跳过标注，避免叠字
  let lastPy = null
  for (const frac of [0, 0.5, 1]) {
    const value = yLo + (yHi - yLo) * frac
    const py = toPy(value)
    strokeLine(ctx, [[plotX0, py], [plotX1, py]], theme.grid)
    if (lastPy !== null && Math.abs(lastPy - py) < 15) continue
    fillText(ctx, value.toFixed(0), plotX0 - 7, py, {
      size: 10, color: theme.txt2, align: 'right', baseline: 'middle',
    })
    lastPy = py
  }

  // 横轴刻度：同一区间内相邻标注宽度重叠时只保留两端
  setFont(ctx, 10)
  for (const ticks of groups) {
    const boxes = []
    for (const value of ticks) {
      const px = axis.toPx(value)
      const text = value.toFixed(0)
      const half = ctx.measureText(text).width / 2 + 3
      if (boxes.some(([b0, b1]) => px - half < b1 && b0 < px + half)) continue
      boxes.push([px - half, px + half])
      strokeLine(ctx, [[px, plotY1], [px, plotY1 + 4]], theme.track)
      fillText(ctx, text, px, plotY1 + 6, {
        size: 10, color: theme.txt2, align: 'center',
      })
    }
  }

  // 断隔标记：两道斜线表示此处横轴不连续
  for (const [bx0, bx1] of axis.breaks) {
    const mid = (bx0 + bx1) / 2
    for (const offset of [-3, 3]) {
      strokeLine(ctx, [
        [mid + offset - 3, plotY1 + 5],
        [mid + offset + 3, plotY1 - 5],
      ], theme.track, 1.2)
    }
    strokeLine(ctx, [[mid, plotY0], [mid, plotY1]], theme.grid, 1, [3, 4])
  }
}

/** 绘制无人机航迹。已飞过的航段按当时的服务网络配色分段着色。 */
function drawTrack(ctx, theme, trace, uav, axis, toPy, t) {
  const times = uav.pos.times
  const points = uav.pos.values
  if (points.length < 2) return

  strokeLine(ctx, points.map((p) => [axis.toPx(p[0]), toPy(p[1])]), theme.grid, 1, [4, 4])

  for (let i = 0; i < points.length - 1; i += 1) {
    if (times[i + 1] > t + 1e-9) break
    const net = uav.stateAt(times[i]).serving
    const color = NET_COLORS[net] || theme.track
    strokeLine(ctx, [
      [axis.toPx(points[i][0]), toPy(points[i][1])],
      [axis.toPx(points[i + 1][0]), toPy(points[i + 1][1])],
    ], mixHex(color, theme.bg, 0.3), 3)
  }

  for (const ev of trace.handovers) {
    if (ev.t > t + 1e-9) continue
    const pos = uav.pos.at(ev.t)
    if (!pos) continue
    const px = axis.toPx(pos[0])
    const py = toPy(pos[1])
    ctx.save()
    ctx.strokeStyle = NET_COLORS[ev.to] || theme.accent
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.arc(px, py, 4.5, 0, Math.PI * 2)
    ctx.stroke()
    ctx.restore()
  }
}

/** 绘制无人机与当前服务网络接入点之间的服务链路。 */
function drawServiceLink(ctx, theme, placed, serving) {
  const roleForNet = { '5G': 'gnb', LTE: 'lte_enb', WiFi: 'wifi_ap' }
  const targetRole = roleForNet[serving]
  if (!targetRole) return
  const uav = placed.find((it) => it.role === 'uav')
  const peer = placed.find((it) => it.role === targetRole)
  if (!uav || !peer) return
  strokeLine(ctx, [
    [uav.px + uav.dx, uav.py + uav.dy],
    [peer.px + peer.dx, peer.py + peer.dy],
  ], mixHex(NET_COLORS[serving] || theme.accent, theme.bg, 0.4), 2, [7, 5])
}

/** 绘制节点图元与标注。 */
function drawNodes(ctx, theme, placed, options, bounds) {
  const placer = new LabelPlacer(bounds)
  const order = [...placed].sort((a, b) => rolePriority(b.role) - rolePriority(a.role))

  for (const item of order) {
    const cx = item.px + item.dx
    const cy = item.py + item.dy
    if (item.moved) {
      // 引线连回真实位置，标明图元已为避让而偏移
      strokeLine(ctx, [[item.px, item.py], [cx, cy]], theme.track, 1, [2, 3])
      ctx.fillStyle = theme.track
      ctx.beginPath()
      ctx.arc(item.px, item.py, 1.8, 0, Math.PI * 2)
      ctx.fill()
    }
    drawGlyph(ctx, theme, item.role, rgb(item.state.color), cx, cy, item.r)
    placer.reserve([cx - item.r, cy - item.r, cx + item.r, cy + item.r])
  }

  if (!options.showLabels) return
  for (const item of order) {
    const cx = item.px + item.dx
    const cy = item.py + item.dy
    const text = nodeLabel(item.state)
    const size = ['uav', 'wifi_ap', 'lte_enb', 'gnb'].includes(item.role) ? 11 : 10
    const bold = item.role === 'uav'
    setFont(ctx, size, bold)
    const tw = ctx.measureText(text).width
    const th = size + 6
    const [lx, ly] = placer.place(cx, cy, item.r, tw + 10, th + 4)
    roundRect(ctx, lx, ly, lx + tw + 10, ly + th + 4, 4,
      mixHex(theme.panel2, theme.bg, 0.1), theme.line)
    fillText(ctx, text, lx + 5, ly + 3, {
      size, bold, color: item.role === 'uav' ? theme.txt : theme.txt2,
    })
  }
}

/** 绘制拓扑视图下方的图例。 */
function drawLegend(ctx, theme, x0, y0, x1) {
  const items = [
    ['uav', '#e68c00'], ['gnb', NET_COLORS['5G']], ['lte_enb', NET_COLORS.LTE],
    ['wifi_ap', NET_COLORS.WiFi], ['relay', 'rgb(150,150,150)'],
    ['sta', 'rgb(190,190,190)'],
  ]
  let cursor = x0
  setFont(ctx, 10)
  for (const [role, color] of items) {
    const label = ROLE_LABELS[role]
    drawGlyph(ctx, theme, role, color, cursor + 5, y0 + 5, 4.5, false)
    fillText(ctx, label, cursor + 13, y0, { size: 10, color: theme.txt2 })
    cursor += 13 + ctx.measureText(label).width + 15
    if (cursor > x1 - 60) break
  }
}

/**
 * 绘制侧视高度视图。
 *
 * 动画轨迹只记录节点的平面坐标，无人机高度由决策时间序列给出。
 * 缺少高度数据时给出提示而不绘制曲线。
 */
export function drawElevation(ctx, size, trace, series, t, options, serving) {
  const theme = THEMES[options.theme]
  const { width, height } = size

  if (!series || !series.has('altitude')) {
    fillText(ctx, '未导入决策时间序列，或时间序列不含高度字段',
      width / 2, height / 2, {
        size: 11, color: theme.txt2, align: 'center', baseline: 'middle',
      })
    return
  }

  const samples = []
  for (let i = 0; i < series.rows.length; i += 1) {
    const alt = series.value(series.rows[i], 'altitude')
    if (alt !== null) samples.push([series.times[i], alt])
  }
  if (samples.length < 2) {
    fillText(ctx, '高度样本不足，无法绘制曲线', width / 2, height / 2, {
      size: 11, color: theme.txt2, align: 'center', baseline: 'middle',
    })
    return
  }

  const plotX0 = 46
  const plotX1 = width - 10
  const plotY0 = 12
  const plotY1 = height - 20
  const tLo = samples[0][0]
  const tHi = samples[samples.length - 1][0]
  let aLo = Math.min(...samples.map((s) => s[1]))
  let aHi = Math.max(...samples.map((s) => s[1]))
  if (aHi - aLo < 5) aHi = aLo + 5
  const margin = (aHi - aLo) * 0.18
  aLo -= margin
  aHi += margin

  const toPx = (v) => (tHi - tLo < 1e-9 ? plotX0 : plotX0 + ((plotX1 - plotX0) * (v - tLo)) / (tHi - tLo))
  const toPy = (v) => plotY1 - ((plotY1 - plotY0) * (v - aLo)) / (aHi - aLo)

  for (const frac of [0, 0.5, 1]) {
    const value = aLo + (aHi - aLo) * frac
    const py = toPy(value)
    strokeLine(ctx, [[plotX0, py], [plotX1, py]], theme.grid)
    fillText(ctx, value.toFixed(0), plotX0 - 7, py, {
      size: 10, color: theme.txt2, align: 'right', baseline: 'middle',
    })
  }

  for (const ev of trace.handovers) {
    const px = toPx(ev.t)
    strokeLine(ctx, [[px, plotY0], [px, plotY1]],
      mixHex(NET_COLORS[ev.to] || theme.accent, theme.panel, 0.5), 1, [3, 3])
  }

  // 整条曲线以淡色画出，已经过的区段以当前服务网络配色叠画
  strokeLine(ctx, samples.map((s) => [toPx(s[0]), toPy(s[1])]), theme.grid, 2)
  const past = samples.filter((s) => s[0] <= t + 1e-9).map((s) => [toPx(s[0]), toPy(s[1])])
  if (past.length >= 2) {
    const color = NET_COLORS[serving] || theme.accent
    // 曲线下方填充淡色区域，强调高度包络
    ctx.save()
    ctx.beginPath()
    ctx.moveTo(past[0][0], plotY1)
    past.forEach(([px, py]) => ctx.lineTo(px, py))
    ctx.lineTo(past[past.length - 1][0], plotY1)
    ctx.closePath()
    ctx.fillStyle = mixHex(color, theme.panel, 0.82)
    ctx.fill()
    ctx.restore()
    strokeLine(ctx, past, color, 2.2)
  }

  const current = series.value(series.rowAt(t), 'altitude')
  if (current !== null) {
    const px = toPx(Math.min(Math.max(t, tLo), tHi))
    const py = toPy(current)
    ctx.save()
    ctx.fillStyle = NET_COLORS[serving] || theme.accent
    ctx.strokeStyle = theme.panel
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.arc(px, py, 4.5, 0, Math.PI * 2)
    ctx.fill()
    ctx.stroke()
    ctx.restore()
    fillText(ctx, `${current.toFixed(1)} m`, px + 9, py - 7, {
      size: 11, bold: true, color: theme.txt,
    })
  }

  for (const frac of [0, 0.25, 0.5, 0.75, 1]) {
    const value = tLo + (tHi - tLo) * frac
    const align = frac === 0 ? 'left' : frac === 1 ? 'right' : 'center'
    fillText(ctx, value.toFixed(1), toPx(value), plotY1 + 5, {
      size: 10, color: theme.txt2, align,
    })
  }
}

/**
 * 绘制服务网络时间轴。
 *
 * 色带按无人机标注的服务网络分段着色；切换时刻可能十分接近（相邻
 * 决策周期），标注按两层交错排布，同层内仍会重叠时向右让开。
 */
export function drawTimeline(ctx, size, trace, t, options) {
  const theme = THEMES[options.theme]
  const { width, height } = size
  const barX0 = 12
  const barX1 = width - 12
  const barY0 = 10
  const barY1 = 32
  const duration = trace.duration || 1
  const toPx = (v) => barX0 + ((barX1 - barX0) * v) / duration

  roundRect(ctx, barX0, barY0, barX1, barY1, 5, theme.panel2)

  const uav = trace.uav()
  if (uav && uav.descr.times.length) {
    const stamps = [...uav.descr.times, duration]
    ctx.save()
    roundRect(ctx, barX0, barY0, barX1, barY1, 5, null)
    ctx.clip()
    for (let i = 0; i < stamps.length - 1; i += 1) {
      const net = uav.stateAt(stamps[i]).serving
      if (!net) continue
      const px0 = toPx(stamps[i])
      let px1 = toPx(stamps[i + 1])
      if (px1 - px0 < 0.6) px1 = px0 + 0.6
      ctx.fillStyle = NET_COLORS[net] || theme.track
      ctx.fillRect(px0, barY0, px1 - px0, barY1 - barY0)
    }
    ctx.restore()
  }

  const rowH = 16
  const occupied = [[], []]
  setFont(ctx, 10)
  trace.handovers.forEach((ev, index) => {
    const px = toPx(ev.t)
    strokeLine(ctx, [[px, barY0 - 4], [px, barY1 + 4]], theme.txt, 1.4)
    const text = `${ev.t.toFixed(1)} s　${ev.from}→${ev.to}`
    const tw = ctx.measureText(text).width
    const layer = index % 2
    let left = px - tw / 2
    for (const [usedL, usedR] of occupied[layer]) {
      if (left < usedR && usedL < left + tw) left = usedR + 5
    }
    left = Math.max(barX0, Math.min(left, barX1 - tw))
    occupied[layer].push([left, left + tw])
    const ty = barY1 + 7 + layer * rowH
    strokeLine(ctx, [[px, barY1 + 4], [px, ty + 2]], theme.line)
    fillText(ctx, text, left, ty, { size: 10, color: theme.txt2 })
  })

  // 当前时刻游标
  const cursor = toPx(Math.min(t, duration))
  strokeLine(ctx, [[cursor, barY0 - 8], [cursor, barY1 + 6]], theme.accent, 2)
  ctx.save()
  ctx.fillStyle = theme.accent
  ctx.beginPath()
  ctx.moveTo(cursor, barY0 - 7)
  ctx.lineTo(cursor - 5, barY0 - 14)
  ctx.lineTo(cursor + 5, barY0 - 14)
  ctx.closePath()
  ctx.fill()
  ctx.restore()
}
