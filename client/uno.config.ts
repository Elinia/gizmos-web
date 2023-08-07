import { defineConfig } from 'unocss'
import presetUno, { type Theme } from '@unocss/preset-uno'

export default defineConfig({
  content: {
    filesystem: ['**/*.{html,js,ts,jsx,tsx,vue,svelte,astro}'],
  },
  theme: {
    breakpoints: {
      sm: '0rem',
      md: '48rem',
      lg: '72rem',
    },
  },
  extendTheme: theme => {
    return {
      ...theme,
      fontSize: {
        ...theme.fontSize,
        '2xs': ['0.5625rem', '0.75rem'],
      },
    } satisfies Theme
  },
  presets: [presetUno({})],
})
