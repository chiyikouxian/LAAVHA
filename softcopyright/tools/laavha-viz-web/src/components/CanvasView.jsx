/*
 * 无人机遥感异构网络垂直切换智能决策软件 V1.0
 * 运行可视化界面 —— 画布视图容器
 *
 * 把一个绘制函数包装为随容器尺寸自适应的画布组件。容器尺寸变化时
 * 重新按设备像素比初始化画布并重绘，使线条与文字在高分屏与窗口
 * 缩放后保持清晰。
 */
import React, { useCallback, useEffect, useRef, useState } from 'react'
import { prepareCanvas } from '../lib/canvasRender.js'

export default function CanvasView({ title, extra, draw, minHeight = 120, onPick }) {
  const boxRef = useRef(null)
  const canvasRef = useRef(null)
  const [size, setSize] = useState({ width: 0, height: 0 })
  const pickedRef = useRef([])

  // 以尺寸观察器跟踪画布自身尺寸（而非外层容器），避免把标题行的高度
  // 计入绘图区，也避免依赖窗口 resize 事件而漏掉布局变化
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return undefined
    const observer = new ResizeObserver((entries) => {
      const rect = entries[0].contentRect
      setSize({ width: Math.round(rect.width), height: Math.round(rect.height) })
    })
    observer.observe(canvas)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || size.width < 20 || size.height < 20) return
    const ctx = prepareCanvas(canvas, size.width, size.height)
    pickedRef.current = draw(ctx, size) || []
  }, [draw, size])

  const handleMove = useCallback(
    (event) => {
      if (!onPick) return
      const rect = canvasRef.current.getBoundingClientRect()
      const mx = event.clientX - rect.left
      const my = event.clientY - rect.top
      let hit = null
      for (const item of pickedRef.current) {
        const cx = item.px + (item.dx || 0)
        const cy = item.py + (item.dy || 0)
        if (Math.hypot(mx - cx, my - cy) <= item.r + 4) {
          hit = item
          break
        }
      }
      onPick(hit ? { item: hit, x: mx, y: my } : null)
    },
    [onPick],
  )

  return (
    <section className="card" ref={boxRef} style={{ minHeight }}>
      <header className="card-head">
        <h2>{title}</h2>
        {extra ? <span className="card-extra">{extra}</span> : null}
      </header>
      <canvas
        ref={canvasRef}
        className="card-canvas"
        onMouseMove={handleMove}
        onMouseLeave={onPick ? () => onPick(null) : undefined}
      />
    </section>
  )
}
