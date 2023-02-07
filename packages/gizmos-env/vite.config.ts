import { defineConfig } from 'vite'
import dts from 'vite-plugin-dts'

export default defineConfig({
  build: {
    lib: {
      entry: [
        './lib/common.ts',
        './lib/energy_pool.ts',
        './lib/Gizmo.ts',
        './lib/GizmosEnv.ts',
        './lib/gizmos_pool.ts',
        './lib/gizmos_utils.ts',
        './lib/Player.ts',
      ],
      formats: ['es'],
    },
    rollupOptions: {
      output: {
        preserveModules: true,
        sourcemapExcludeSources: true,
        entryFileNames: '[name].js',
      },
    },
  },
  plugins: [dts({ outputDir: ['dist'] })],
})
