/*
 * 无人机遥感异构网络垂直切换智能决策软件 V1.0
 * 运行可视化界面 —— 拓扑视图几何计算
 *
 * 拓扑视图需要解决场景本身带来的两个显示问题：
 *   1) 场景横向跨度约 1400 单位而纵向仅数十单位，按真实比例绘制会把
 *      绝大部分画面宽度分配给没有节点的空白区域；
 *   2) 无人机、接入点与协议栈辅助节点在初始时刻位置重合，图元与标注
 *      互相遮挡。
 *
 * 前者由分段压缩的横轴映射（AxisMap）处理，后者由重合节点的扇形散开
 * （spreadOverlaps）与标注避让（LabelPlacer）处理。两项处理均可在界面
 * 上关闭，以回到真实比例、真实位置的显示方式。
 */

/**
 * 把一组横坐标聚成若干区间。
 *
 * 相邻取值之间的间隔超过 joinGap 时切分为不同区间；每个区间向两侧
 * 留出 pad 的余量，避免节点图元贴住区间边缘。
 */
export function clusterSpans(values, joinGap = 140, pad = 26) {
  if (values.length === 0) return [[0, 1]]
  const ordered = [...values].sort((a, b) => a - b)
  const groups = [[ordered[0], ordered[0]]]
  for (const value of ordered.slice(1)) {
    const last = groups[groups.length - 1]
    if (value - last[1] > joinGap) groups.push([value, value])
    else last[1] = value
  }
  return groups.map(([lo, hi]) => [lo - pad, hi + pad])
}

/**
 * 横轴映射。
 *
 * 压缩模式下按各簇的跨度分配画面宽度，簇之间只留固定宽度的断隔并
 * 记录断隔位置供绘制断隔标记；真实比例模式下退化为单一线性映射。
 */
export class AxisMap {
  constructor(spans, x0, x1, compress = true, gapPx = 28) {
    this.x0 = x0
    this.x1 = x1
    this.compress = compress
    this.segments = []
    this.breaks = []

    const lo = Math.min(...spans.map((s) => s[0]))
    let hi = Math.max(...spans.map((s) => s[1]))
    if (!compress || spans.length <= 1) {
      if (hi - lo < 1e-6) hi = lo + 1
      this.segments = [[lo, hi, x0, x1]]
      return
    }

    const totalData = spans.reduce((sum, s) => sum + (s[1] - s[0]), 0)
    const totalGap = gapPx * (spans.length - 1)
    const usable = Math.max(40, x1 - x0 - totalGap)
    let cursor = x0
    spans.forEach(([loI, hiI], index) => {
      const span = hiI - loI
      const share = Math.max(totalData > 0 ? usable * (span / totalData) : usable, 24)
      this.segments.push([loI, hiI, cursor, cursor + share])
      cursor += share
      if (index < spans.length - 1) {
        this.breaks.push([cursor, cursor + gapPx])
        cursor += gapPx
      }
    })
  }

  /** 把场景横坐标映射为画面横坐标。 */
  toPx(value) {
    const first = this.segments[0]
    if (value <= first[0]) return first[2]
    for (const [lo, hi, px0, px1] of this.segments) {
      if (value <= hi) {
        if (hi - lo < 1e-9) return px0
        return px0 + ((px1 - px0) * (value - lo)) / (hi - lo)
      }
    }
    return this.segments[this.segments.length - 1][3]
  }
}

/**
 * 为每个横轴区间挑选刻度取值。
 *
 * 取值来自区间内真实存在的节点坐标，而不是为留白而外扩的区间边界，
 * 使刻度标注反映实际存在的位置。
 */
export function tickGroups(values, spans) {
  const groups = []
  for (const [lo, hi] of spans) {
    const inside = values.filter((v) => v >= lo && v <= hi).sort((a, b) => a - b)
    if (inside.length === 0) continue
    const loV = inside[0]
    const hiV = inside[inside.length - 1]
    if (hiV - loV < 1e-6) groups.push([loV])
    else if (hiV - loV < 60) groups.push([loV, hiV])
    else groups.push([loV, inside[Math.floor(inside.length / 2)], hiV])
  }
  return groups
}

// 重合节点散开时的角色优先级，数值小者留在真实位置
const ROLE_PRIORITY = {
  uav: 0, wifi_ap: 1, lte_enb: 1, gnb: 1, relay: 2, sta: 3,
}

export function rolePriority(role) {
  return ROLE_PRIORITY[role] ?? 9
}

/**
 * 把画面上位置重合的节点图元散开。
 *
 * 优先级最高的节点保持在真实位置，其余节点沿圆周均匀散开，散开半径
 * 同时考虑图元尺寸与标注高度：相邻节点的角度间隔越小，所需半径越大，
 * 否则相邻两个标注在纵向上仍会互相压叠。绘制时由引线连回真实位置。
 */
export function spreadOverlaps(placed, minGap = 8, labelH = 17) {
  for (const item of placed) {
    item.dx = 0
    item.dy = 0
    item.moved = false
  }

  for (const group of groupOverlaps(placed, minGap)) {
    if (group.length < 2) continue
    group.sort((a, b) => rolePriority(a.role) - rolePriority(b.role) || a.id - b.id)
    const others = group.slice(1)
    const step = (2 * Math.PI) / others.length
    const need = (labelH + 4) / Math.max(0.35, Math.abs(Math.sin(step / 2)) * 2)
    const radius = Math.max(
      Math.max(...group.map((it) => it.r)) + minGap + 9,
      Math.min(need, 74),
    )
    others.forEach((item, index) => {
      const angle = -Math.PI / 2 + (2 * Math.PI * index) / others.length
      item.dx = Math.cos(angle) * radius
      item.dy = Math.sin(angle) * radius
      item.moved = true
    })
  }
  return placed
}

/** 按图元是否相交把节点分组。 */
function groupOverlaps(placed, minGap) {
  const parent = placed.map((_, i) => i)
  const find = (i) => {
    let cur = i
    while (parent[cur] !== cur) {
      parent[cur] = parent[parent[cur]]
      cur = parent[cur]
    }
    return cur
  }
  const union = (i, j) => {
    const ri = find(i)
    const rj = find(j)
    if (ri !== rj) parent[rj] = ri
  }

  for (let i = 0; i < placed.length; i += 1) {
    for (let j = i + 1; j < placed.length; j += 1) {
      const a = placed[i]
      const b = placed[j]
      const dist = Math.hypot(a.px - b.px, a.py - b.py)
      if (dist < a.r + b.r + minGap) union(i, j)
    }
  }

  const buckets = new Map()
  placed.forEach((item, index) => {
    const key = find(index)
    if (!buckets.has(key)) buckets.set(key, [])
    buckets.get(key).push(item)
  })
  return [...buckets.values()]
}

/**
 * 标注避让。
 *
 * 依次为每个节点在八个方位的候选位置中选取第一个不与已放置标注、
 * 已占用图元区域相交的位置；全部不可用时选取重叠面积最小的候选位置，
 * 使标注在拥挤区域也尽量少地压住其他内容，而不是被丢弃。
 */
export class LabelPlacer {
  constructor(bounds) {
    this.bounds = bounds
    this.taken = []
  }

  reserve(box) {
    this.taken.push(box)
  }

  fits(box) {
    const [bx0, by0, bx1, by1] = box
    const [lx0, ly0, lx1, ly1] = this.bounds
    if (bx0 < lx0 || bx1 > lx1 || by0 < ly0 || by1 > ly1) return false
    return !this.taken.some(
      ([tx0, ty0, tx1, ty1]) => bx0 < tx1 && tx0 < bx1 && by0 < ty1 && ty0 < by1,
    )
  }

  overlapArea(box) {
    const [bx0, by0, bx1, by1] = box
    let area = 0
    for (const [tx0, ty0, tx1, ty1] of this.taken) {
      const dx = Math.min(bx1, tx1) - Math.max(bx0, tx0)
      const dy = Math.min(by1, ty1) - Math.max(by0, ty0)
      if (dx > 0 && dy > 0) area += dx * dy
    }
    const [lx0, ly0, lx1, ly1] = this.bounds
    let out = 0
    if (bx0 < lx0) out += (lx0 - bx0) * (by1 - by0)
    if (bx1 > lx1) out += (bx1 - lx1) * (by1 - by0)
    if (by0 < ly0) out += (ly0 - by0) * (bx1 - bx0)
    if (by1 > ly1) out += (by1 - ly1) * (bx1 - bx0)
    return area + out * 2
  }

  place(cx, cy, radius, w, h) {
    const pad = 5
    const near = radius + pad
    const far = radius + pad + 2
    const options = [
      [cx + near, cy - h / 2],
      [cx - near - w, cy - h / 2],
      [cx - w / 2, cy - near - h],
      [cx - w / 2, cy + near],
      [cx + far, cy - far - h],
      [cx - far - w, cy - far - h],
      [cx + far, cy + far],
      [cx - far - w, cy + far],
    ]
    for (const [ox, oy] of options) {
      const box = [ox, oy, ox + w, oy + h]
      if (this.fits(box)) {
        this.reserve(box)
        return [ox, oy]
      }
    }
    let best = options[0]
    let bestArea = Infinity
    for (const opt of options) {
      const area = this.overlapArea([opt[0], opt[1], opt[0] + w, opt[1] + h])
      if (area < bestArea) {
        bestArea = area
        best = opt
      }
    }
    const [lx0, ly0, lx1, ly1] = this.bounds
    const ox = Math.max(lx0, Math.min(best[0], lx1 - w))
    const oy = Math.max(ly0, Math.min(best[1], ly1 - h))
    this.reserve([ox, oy, ox + w, oy + h])
    return [ox, oy]
  }
}
