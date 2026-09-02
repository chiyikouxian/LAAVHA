/*
 * 无人机遥感异构网络垂直切换智能决策软件 V1.0
 * 运行可视化界面 —— 轨迹与时间序列解析
 *
 * 解析仿真运行产出的两类文件：
 *   1) 动画轨迹文件（XML）：节点初始坐标，以及位置、颜色、标注、尺寸
 *      四类随时间变化的更新事件；
 *   2) 决策时间序列文件（CSV，可选）：每个决策周期的候选网络评分与
 *      五类链路指标。
 *
 * 对外提供的核心能力是"给定仿真时刻，返回该时刻的完整场景状态"。
 */

export const NET_NAMES = { 0: '5G', 1: 'LTE', 2: 'WiFi' }

// 节点角色的显示配色与图元尺寸，与仿真端写入轨迹的着色规则一致
export const ROLE_COLORS = {
  uav: [230, 140, 0],
  wifi_ap: [0, 160, 0],
  lte_enb: [0, 0, 220],
  gnb: [230, 140, 0],
  relay: [150, 150, 150],
  sta: [190, 190, 190],
}

export const ROLE_SIZES = {
  uav: 40, wifi_ap: 30, lte_enb: 30, gnb: 30, relay: 18, sta: 15,
}

export const ROLE_LABELS = {
  uav: '无人机', wifi_ap: 'WiFi 接入点', lte_enb: 'LTE 基站',
  gnb: '5G 基站（代理）', relay: '协议栈辅助节点', sta: '背景业务终端',
}

const ROLE_BY_HEAD = {
  UAV: 'uav',
  'WiFi-AP': 'wifi_ap',
  'LTE-eNB': 'lte_enb',
  '5G-proxy-gNB': 'gnb',
  '5G-proxy-UE': 'relay',
  'LTE-UE': 'relay',
  RemoteHost: 'relay',
}

/** 依据节点标注文本判定节点角色，未携带标注者归入背景终端。 */
export function classifyRole(descr) {
  if (!descr) return 'sta'
  const head = descr.split('|')[0].trim()
  return ROLE_BY_HEAD[head] || 'sta'
}

/** 从无人机标注中取出当前服务网络名称，取不到时返回 null。 */
export function servingNetOf(descr) {
  if (!descr || !descr.includes('serving=')) return null
  return descr.split('serving=')[1].trim() || null
}

/**
 * 单个节点某一属性的时间线。
 *
 * 事件按时刻升序存放，查询时返回不晚于给定时刻的最后一个事件值，
 * 与动画回放"状态保持到下一次更新"的语义一致。
 */
class Timeline {
  constructor() {
    this.times = []
    this.values = []
  }

  add(t, value) {
    this.times.push(t)
    this.values.push(value)
  }

  sort() {
    if (this.times.length === 0) return
    const order = this.times.map((_, i) => i)
    order.sort((a, b) => this.times[a] - this.times[b] || a - b)
    this.times = order.map((i) => this.times[i])
    this.values = order.map((i) => this.values[i])
  }

  at(t, fallback = null) {
    if (this.times.length === 0) return fallback
    let lo = 0
    let hi = this.times.length - 1
    let found = -1
    while (lo <= hi) {
      const mid = (lo + hi) >> 1
      if (this.times[mid] <= t + 1e-9) {
        found = mid
        lo = mid + 1
      } else {
        hi = mid - 1
      }
    }
    return found < 0 ? fallback : this.values[found]
  }
}

/** 一个仿真节点及其四条属性时间线。 */
class TraceNode {
  constructor(id, x, y) {
    this.id = id
    this.x0 = x
    this.y0 = y
    this.pos = new Timeline()
    this.color = new Timeline()
    this.descr = new Timeline()
    this.size = new Timeline()
    this.labeled = false
  }

  sort() {
    for (const tl of [this.pos, this.color, this.descr, this.size]) tl.sort()
    // 仿真端只为参与切换决策的节点写入标注与配色，其余节点在轨迹里
    // 仅保留动画库的建节点默认值，显示时改用本界面的角色默认样式。
    this.labeled = this.descr.times.length > 0
  }

  stateAt(t) {
    const [x, y] = this.pos.at(t, [this.x0, this.y0])
    const descr = this.descr.at(t, '')
    const role = classifyRole(descr)
    const fallback = ROLE_COLORS[role] || [190, 190, 190]
    const span = ROLE_SIZES[role] || 15
    let size = this.labeled ? this.size.at(t, [span, span]) : [span, span]
    if (size[0] <= 1 || size[1] <= 1) size = [span, span]
    return {
      id: this.id,
      x, y, descr, role, size,
      color: this.labeled ? this.color.at(t, fallback) : fallback,
      serving: servingNetOf(descr),
    }
  }
}

/** 一份动画轨迹文件的解析结果。 */
export class TraceData {
  constructor() {
    this.version = ''
    this.nodes = new Map()
    this.links = []
    this.times = []
    this.duration = 0
    this.handovers = []
    this.sourceName = ''
    this.wirelessRx = 0
    this.packetCount = 0
  }

  /** 返回给定时刻全部节点的显示状态，按节点编号升序。 */
  stateAt(t) {
    return [...this.nodes.keys()]
      .sort((a, b) => a - b)
      .map((k) => this.nodes.get(k).stateAt(t))
  }

  /** 返回无人机节点，找不到时返回编号最小的节点。 */
  uav() {
    for (const key of [...this.nodes.keys()].sort((a, b) => a - b)) {
      const node = this.nodes.get(key)
      if (classifyRole(node.descr.at(this.duration, '')) === 'uav') return node
    }
    return this.nodes.get(0) || null
  }

  /**
   * 把任意时刻对齐到轨迹中最接近的事件时刻。
   *
   * 动画事件只在离散时刻产生，拖动时间轴时需要对齐到实际事件，
   * 否则会显示介于两个事件之间的中间状态。
   */
  snapTime(t) {
    if (this.times.length === 0) return t
    let lo = 0
    let hi = this.times.length - 1
    if (t <= this.times[0]) return this.times[0]
    if (t >= this.times[hi]) return this.times[hi]
    while (lo <= hi) {
      const mid = (lo + hi) >> 1
      if (this.times[mid] < t) lo = mid + 1
      else hi = mid - 1
    }
    const after = this.times[lo]
    const before = this.times[lo - 1]
    return t - before <= after - t ? before : after
  }

  /** 返回给定时刻所在的事件序号，用于时间轴定位。 */
  indexAt(t) {
    const snapped = this.snapTime(t)
    const index = this.times.indexOf(snapped)
    return index < 0 ? 0 : index
  }
}

const ATTR_RE = /([A-Za-z0-9_]+)\s*=\s*"([^"]*)"/g

/** 取出一行文本中的标签名与属性表。 */
function parseElement(line) {
  const tagMatch = /^<\s*([A-Za-z0-9_]+)/.exec(line)
  if (!tagMatch) return null
  const attrs = {}
  ATTR_RE.lastIndex = 0
  let m
  while ((m = ATTR_RE.exec(line)) !== null) attrs[m[1]] = m[2]
  return { tag: tagMatch[1], attrs }
}

/**
 * 解析动画轨迹文件文本，返回 TraceData。
 *
 * 轨迹文件不含单一根元素闭合结构，且体积可达数兆字节、元素数以万计，
 * 因此按行提取元素而不是构建完整文档树。
 */
export function loadTrace(text, sourceName = '') {
  const trace = new TraceData()
  trace.sourceName = sourceName
  const stamps = new Set()

  for (const raw of text.split('\n')) {
    const line = raw.trim()
    if (line.length === 0 || line[0] !== '<' || line[1] === '?') continue
    const el = parseElement(line)
    if (el === null) continue
    const { tag, attrs } = el

    if (tag === 'anim') {
      trace.version = attrs.ver || ''
    } else if (tag === 'node') {
      const id = parseInt(attrs.id, 10)
      trace.nodes.set(
        id,
        new TraceNode(id, parseFloat(attrs.locX) || 0, parseFloat(attrs.locY) || 0),
      )
    } else if (tag === 'nu') {
      applyUpdate(trace, attrs, stamps)
    } else if (tag === 'link') {
      trace.links.push([parseInt(attrs.fromId, 10), parseInt(attrs.toId, 10)])
    } else if (tag === 'wpr') {
      trace.wirelessRx += 1
    } else if (tag === 'p' || tag === 'pr') {
      trace.packetCount += 1
    }
  }

  for (const node of trace.nodes.values()) node.sort()
  trace.times = [...stamps].sort((a, b) => a - b)
  trace.duration = trace.times.length ? trace.times[trace.times.length - 1] : 0
  trace.handovers = extractHandovers(trace)
  return trace
}

/** 把一条 <nu> 更新事件写入对应节点的时间线。 */
function applyUpdate(trace, attrs, stamps) {
  const id = parseInt(attrs.id, 10)
  if (!trace.nodes.has(id)) trace.nodes.set(id, new TraceNode(id, 0, 0))
  const node = trace.nodes.get(id)
  const t = parseFloat(attrs.t) || 0
  stamps.add(t)

  switch (attrs.p) {
    case 'p':
      node.pos.add(t, [parseFloat(attrs.x) || 0, parseFloat(attrs.y) || 0])
      break
    case 'c':
      node.color.add(t, [
        parseInt(attrs.r, 10) || 0,
        parseInt(attrs.g, 10) || 0,
        parseInt(attrs.b, 10) || 0,
      ])
      break
    case 'd':
      node.descr.add(t, attrs.descr || '')
      break
    case 's':
      node.size.add(t, [parseFloat(attrs.w) || 15, parseFloat(attrs.h) || 15])
      break
    default:
      break
  }
}

/**
 * 从无人机标注时间线中提取服务网络的切换序列。
 * 时刻取自动画事件，即决策生效之后的时刻。
 */
function extractHandovers(trace) {
  const uav = trace.uav()
  if (uav === null) return []
  const events = []
  let prev = null
  for (let i = 0; i < uav.descr.times.length; i += 1) {
    const net = servingNetOf(uav.descr.values[i])
    if (net === null) continue
    if (prev !== null && net !== prev) {
      events.push({ t: uav.descr.times[i], from: prev, to: net })
    }
    prev = net
  }
  return events
}

/** 一份决策时间序列文件的解析结果。 */
export class SeriesData {
  constructor() {
    this.rows = []
    this.times = []
    this.columns = []
    this.sourceName = ''
  }

  /** 返回不晚于给定时刻的最后一个决策周期记录。 */
  rowAt(t) {
    if (this.times.length === 0) return null
    let lo = 0
    let hi = this.times.length - 1
    let found = -1
    while (lo <= hi) {
      const mid = (lo + hi) >> 1
      if (this.times[mid] <= t + 1e-9) {
        found = mid
        lo = mid + 1
      } else {
        hi = mid - 1
      }
    }
    return found < 0 ? null : this.rows[found]
  }

  has(column) {
    return this.columns.includes(column)
  }

  /** 按列名取浮点值，缺列或非数值时返回 fallback。 */
  value(row, column, fallback = null) {
    if (!row) return fallback
    const raw = row[column]
    if (raw === undefined || raw === null || raw === '') return fallback
    const num = Number(raw)
    return Number.isFinite(num) ? num : fallback
  }
}

/** 解析决策时间序列文件文本，返回 SeriesData。 */
export function loadSeries(text, sourceName = '') {
  const series = new SeriesData()
  series.sourceName = sourceName
  const lines = text.split('\n').filter((l) => l.trim().length > 0)
  if (lines.length === 0) return series

  series.columns = lines[0].split(',').map((c) => c.trim())
  const entries = []
  for (let i = 1; i < lines.length; i += 1) {
    const cells = lines[i].split(',')
    const row = {}
    series.columns.forEach((name, index) => {
      row[name] = (cells[index] ?? '').trim()
    })
    const t = Number(row.sim_time)
    if (!Number.isFinite(t)) continue
    entries.push([t, row])
  }
  entries.sort((a, b) => a[0] - b[0])
  series.times = entries.map((e) => e[0])
  series.rows = entries.map((e) => e[1])
  return series
}
