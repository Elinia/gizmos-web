import preprocess from 'svelte-preprocess'
import adapter from '@sveltejs/adapter-static'
import { vitePreprocess } from '@sveltejs/kit/vite'
import { dirname, join } from 'path'
import { fileURLToPath } from 'url'
import UnoCSS from '@unocss/svelte-scoped/preprocess'

const __dirname = dirname(fileURLToPath(import.meta.url))

/** @type {import('@sveltejs/kit').Config} */
const config = {
  vitePlugin: {
    inspector: true,
  },
  // Consult https://kit.svelte.dev/docs/integrations#preprocessors
  // for more information about preprocessors
  preprocess: [
    UnoCSS(),
    vitePreprocess(),
    preprocess({
      postcss: {
        configFilePath: join(__dirname, 'postcss.config.cjs'),
      },
    }),
  ],

  kit: {
    adapter: adapter(),
  },
}

export default config
