// نظام الثيمات المركزي - Morix Platform
import { watchEffect } from 'vue'

export const THEMES = {
  dark: {
    '--bg1': '#00000e',
    '--bg2': 'rgba(4, 8, 24, 0.92)',
    '--bg3': '#081428',
    '--text': '#dff4ff',
    '--t2':   '#64b5d4',
    '--text2':'#64b5d4',
    '--accent':'#00ff9f',
    '--border':'rgba(0, 255, 159, 0.18)',
    '--card':  'rgba(4, 16, 44, 0.72)',
    '--glow':  '0 0 18px rgba(0,255,159,0.25)',
    '--glow2': '0 0 30px rgba(0,200,255,0.18)',
  },
  light: {
    '--bg1': '#f8fafc',
    '--bg2': '#e2e8f0',
    '--bg3': '#cbd5e1',
    '--text': '#0f172a',
    '--t2':   '#475569',
    '--text2':'#475569',
    '--accent':'#6366f1',
    '--border':'rgba(0,0,0,.1)',
    '--card':  '#ffffff',
  },
  library: {
    '--bg1': '#1a1207',
    '--bg2': '#2d1f0b',
    '--bg3': '#3d2a0f',
    '--text': '#f5e6c8',
    '--t2':   '#c9a96e',
    '--text2':'#c9a96e',
    '--accent':'#c97c2e',
    '--border':'rgba(201,124,46,.2)',
    '--card':  'rgba(201,124,46,.06)',
  },
}

/**
 * تطبيق الثيم والسطوع تلقائياً على document.documentElement
 * @param {Ref} settings - ref يحتوي على { theme, brightness }
 */
export function useTheme(settings) {
  watchEffect(() => {
    const theme = settings.value?.theme || 'dark'
    const vars = THEMES[theme] || THEMES.dark
    const root = document.documentElement

    for (const [key, val] of Object.entries(vars)) {
      root.style.setProperty(key, val)
    }
    root.setAttribute('data-theme', theme)

    const br = settings.value?.brightness ?? 100
    root.style.setProperty('--brightness', br + '%')

    // سطوع على body لأنه أسرع من كل مكوّن بشكل منفصل
    document.body.style.filter = br < 100 ? `brightness(${br}%)` : ''
  })
}
