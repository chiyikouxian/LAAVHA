import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 打包为相对路径引用，便于在本地文件系统或任意子路径下直接打开
export default defineConfig({
  plugins: [react()],
  base: './',
  server: { port: 5173, open: false },
  build: { outDir: 'dist', assetsDir: 'assets' },
})
