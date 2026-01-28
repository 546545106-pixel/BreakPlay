import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build: {
    assetsDir: 'static',
    // 代码分割优化
    rollupOptions: {
      output: {
        manualChunks(id) {
          // 更精细的代码分割
          if (id.includes('node_modules')) {
            if (id.includes('vue') || id.includes('vue-router')) {
              return 'vue-vendor'
            }
            if (id.includes('element-plus')) {
              return 'element-plus'
            }
            if (id.includes('@vueuse')) {
              return 'vueuse'
            }
            // 其他第三方库
            return 'vendor'
          }
          // 按页面分割
          if (id.includes('/views/HomePage')) {
            return 'homepage'
          }
          if (id.includes('/views/DetailPage')) {
            return 'detailpage'
          }
        },
        // 优化文件命名
        chunkFileNames: 'static/js/[name]-[hash].js',
        entryFileNames: 'static/js/[name]-[hash].js',
        assetFileNames: 'static/[ext]/[name]-[hash].[ext]'
      }
    },
    // 压缩配置（使用 esbuild，Vite 默认，无需额外依赖）
    minify: 'esbuild',
    // 块大小警告限制
    chunkSizeWarningLimit: 1000,
    // 启用CSS代码分割
    cssCodeSplit: true,
    // 生成source map（生产环境可关闭以减小体积）
    sourcemap: false,
    // 启用gzip压缩报告
    reportCompressedSize: true,
    // 目标浏览器
    target: 'es2015'
    // CSS 压缩使用默认配置（无需额外依赖）
  },
  // 开发服务器配置
  server: {
    port: 5173,
    open: true,
    cors: true,
    // 启用HTTP/2
    https: false,
    // 预热常用文件
    warmup: {
      clientFiles: ['./src/main.js', './src/router/index.js']
    }
  },
  // 预览服务器配置
  preview: {
    port: 4173,
    open: true
  },
  // 优化依赖预构建
  optimizeDeps: {
    include: ['vue', 'vue-router', 'element-plus', '@vueuse/core'],
    exclude: []
  }
})
