/*
 * 开发期辅助脚本：以桩替换画布上下文，检查绘制过程的几何输出。
 *
 * 检查项：
 *   1) 绘制过程是否抛出异常；
 *   2) 是否产生 NaN 坐标（画布对 NaN 坐标静默不绘制，不易被发现）；
 *   3) 图元是否越出画面边界。
 *
 * 不属于软件功能的一部分，仅在调试界面绘制时使用。
 */

import { readFileSync } from 'fs'
import { drawElevation, drawTimeline, drawTopology } from '../src/lib/canvasRender.js'
import { loadSeries, loadTrace } from '../src/lib/traceModel.js'

/** 记录绘图调用的画布上下文桩。 */
function makeCtx(width, height) {
  const bad = []
  const seen = []
  const note = (op, values) => {
    for (const v of values) {
      if (typeof v === 'number' && !Number.isFinite(v)) {
        bad.push(`${op} 产生非有限坐标：${values.join(',')}`)
        return
      }
    }
    seen.push([op, values])
  }

  const ctx = {
    canvas: { width, height },
    globalAlpha: 1,
    lineWidth: 1,
    setTransform() {},
    clearRect() {},
    save() {},
    restore() {},
    beginPath() {},
    closePath() {},
    clip() {},
    fill() {},
    stroke() {},
    setLineDash() {},
    moveTo: (...a) => note('moveTo', a),
    lineTo: (...a) => note('lineTo', a),
    rect: (...a) => note('rect', a),
    arc: (...a) => note('arc', a),
    quadraticCurveTo: (...a) => note('quadraticCurveTo', a),
    fillRect: (...a) => note('fillRect', a),
    fillText: (text, x, y) => note('fillText', [x, y]),
    measureText: (text) => ({ width: [...String(text)].reduce(
      (sum, ch) => sum + (ch.charCodeAt(0) > 255 ? 11 : 6), 0) }),
    createRadialGradient: () => ({ addColorStop() {} }),
    createLinearGradient: () => ({ addColorStop() {} }),
    drawImage() {},
  }
  return { ctx, bad, seen }
}

// 画布绘制取 window.devicePixelRatio，Node 环境下补一个桩
globalThis.window = { devicePixelRatio: 1 }

const XML = '../../../evidence/laavha_handover_seed250.xml'
const CSV = '../../../evidence/ts_seed250_anim.csv'
const trace = loadTrace(readFileSync(new URL(XML, import.meta.url), 'utf8'), 'seed250.xml')
const series = loadSeries(readFileSync(new URL(CSV, import.meta.url), 'utf8'), 'ts.csv')

const BASE = {
  theme: 'dark', compressX: true, spreadNodes: true,
  showTrack: true, showLinks: true, showLabels: true,
}

const VIEWS = [
  ['拓扑视图', { width: 1000, height: 380 }, (ctx, size, opts, t, sv) =>
    drawTopology(ctx, size, trace, t, opts, sv)],
  ['高度视图', { width: 1000, height: 168 }, (ctx, size, opts, t, sv) =>
    drawElevation(ctx, size, trace, series, t, opts, sv)],
  ['时间轴', { width: 1000, height: 106 }, (ctx, size, opts, t) =>
    drawTimeline(ctx, size, trace, t, opts)],
]

function servingAt(t) {
  for (const s of trace.stateAt(t)) if (s.role === 'uav' && s.serving) return s.serving
  return null
}

let problems = 0

function run(label, opts, times, sizeOverride = null) {
  for (const t of times) {
    for (const [name, size, draw] of VIEWS) {
      const box = sizeOverride || size
      const { ctx, bad, seen } = makeCtx(box.width, box.height)
      try {
        draw(ctx, box, opts, t, servingAt(t))
      } catch (err) {
        console.log(`  ✗ ${label} t=${t} ${name} 抛出异常：${err.message}`)
        problems += 1
        continue
      }
      const out = seen.filter(([, v]) =>
        v.some((n, i) => typeof n === 'number' && i < 2
          && (n < -60 || (i === 0 ? n > box.width + 60 : n > box.height + 60))))
      if (bad.length || out.length) {
        console.log(`  ✗ ${label} t=${t} ${name}：非有限 ${bad.length} 越界 ${out.length}`)
        if (bad[0]) console.log(`      ${bad[0]}`)
        if (out[0]) console.log(`      越界示例 ${out[0][0]} ${out[0][1].slice(0, 2)}`)
        problems += bad.length + out.length
      }
    }
  }
  console.log(`  ${label}：${times.length} 个时刻 × ${VIEWS.length} 视图 检查完毕`)
}

console.log(`轨迹 ${trace.nodes.size} 节点 ${trace.times.length} 事件 切换 ${trace.handovers.length} 次`)
run('默认选项', BASE, [0, 0.2, 0.3, 0.7, 1.6, 1.7, 5, 10])
run('真实比例+不散开', { ...BASE, compressX: false, spreadNodes: false }, [0.3, 5])
run('无标注+无航迹', { ...BASE, showLabels: false, showTrack: false }, [0.3])
run('浅色', { ...BASE, theme: 'light' }, [1.6])
run('窄画面', BASE, [0.3], { width: 620, height: 260 })

// 无时间序列时高度视图应给出提示而不抛异常
{
  const { ctx, bad } = makeCtx(1000, 168)
  try {
    drawElevation(ctx, { width: 1000, height: 168 }, trace, null, 5, BASE, '5G')
    console.log(`  无时间序列：高度视图正常降级（非有限 ${bad.length}）`)
    problems += bad.length
  } catch (err) {
    console.log(`  ✗ 无时间序列时抛出异常：${err.message}`)
    problems += 1
  }
}

console.log(`\n合计问题 ${problems}`)
process.exit(problems === 0 ? 0 : 1)
