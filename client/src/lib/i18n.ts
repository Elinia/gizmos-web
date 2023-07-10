import { register, init } from 'svelte-i18n'

register('en-US', () => import('../locales/en-US.json'))
register('zh-CN', () => import('../locales/zh-CN.json'))

init({
  fallbackLocale: 'zh-CN',
})
