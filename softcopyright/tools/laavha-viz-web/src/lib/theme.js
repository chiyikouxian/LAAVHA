/*
 * 无人机遥感异构网络垂直切换智能决策软件 V1.0
 * 运行可视化界面 —— 配色定义
 *
 * 深色与浅色两套配色。界面默认用深色；导出插图默认用浅色，以适应
 * 文档排版与黑白打印。画布绘制取本文件的取值，DOM 部分取同名的
 * CSS 变量，两者保持一致。
 */

export const THEMES = {
  dark: {
    bg: '#0f1420',
    panel: '#171d2c',
    panel2: '#1e2536',
    line: '#2b344a',
    txt: '#e7ecf5',
    txt2: '#97a3ba',
    grid: '#212a3c',
    accent: '#4ea1ff',
    track: '#5a6884',
  },
  light: {
    bg: '#f7f9fc',
    panel: '#ffffff',
    panel2: '#eff3f9',
    line: '#cdd6e4',
    txt: '#1a202c',
    txt2: '#636e82',
    grid: '#e2e8f0',
    accent: '#1565c0',
    track: '#8c98ac',
  },
}

// 三个候选网络的配色，与仿真端写入轨迹的着色规则一致
export const NET_COLORS = {
  '5G': '#e68c00',
  LTE: '#2b55dc',
  WiFi: '#009600',
}

/** 把 [r,g,b] 数组转为 CSS 颜色串。 */
export function rgb(color) {
  return `rgb(${color[0]},${color[1]},${color[2]})`
}

/** 按比例把颜色向目标色混合，用于绘制淡化的辅助图元。 */
export function mixHex(hex, targetHex, ratio) {
  const parse = (value) => [
    parseInt(value.slice(1, 3), 16),
    parseInt(value.slice(3, 5), 16),
    parseInt(value.slice(5, 7), 16),
  ]
  const a = parse(hex)
  const b = parse(targetHex)
  const out = a.map((v, i) => Math.round(v + (b[i] - v) * Math.min(1, Math.max(0, ratio))))
  return `rgb(${out[0]},${out[1]},${out[2]})`
}
