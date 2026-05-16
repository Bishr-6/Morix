// نظام الثيمات المركزي - Morix Platform
import { watchEffect } from 'vue'

export const THEMES = {
  // ════════════════════════════════════════════
  // 🌌 Dark — Space + Matrix
  // ════════════════════════════════════════════
  dark: {
    // Colors
    '--bg1':   '#00000e',
    '--bg2':   '#040a1c',
    '--bg3':   '#081428',
    '--text':  '#dff4ff',
    '--t2':    '#64b5d4',
    '--text2': '#64b5d4',
    '--accent':'#00ff9f',
    '--border':'rgba(0, 255, 159, 0.18)',
    '--card':  'rgba(4, 16, 44, 0.72)',

    // Surfaces
    '--sidebar-bg':    'rgba(4, 10, 28, 0.92)',
    '--topbar-bg':     'rgba(4, 10, 28, 0.88)',
    '--modal-bg':      'rgba(4, 16, 44, 0.96)',
    '--input-bg':      'rgba(255,255,255,0.06)',
    '--input-border':  'rgba(0,255,159,0.2)',
    '--input-focus':   'rgba(0,255,159,0.08)',

    // Blur
    '--card-blur':    'blur(10px)',
    '--sidebar-blur': 'blur(14px)',

    // Shadows & Glow
    '--shadow':       'none',
    '--shadow-hover': '0 0 22px rgba(0,255,159,0.22)',
    '--glow':         '0 0 18px rgba(0,255,159,0.25)',
    '--glow2':        '0 0 30px rgba(0,200,255,0.18)',

    // Nav
    '--nav-active-bg':     'rgba(0,255,159,0.12)',
    '--nav-active-shadow': 'inset 0 0 12px rgba(0,255,159,0.1)',
    '--nav-hover-bg':      'rgba(0,255,159,0.07)',

    // Buttons
    '--btn-gradient': 'linear-gradient(135deg, #00ff9f, #00c8ff)',
    '--btn-text':     '#000',
    '--btn-glow':     '0 0 16px rgba(0,255,159,0.28)',

    // Brand icon
    '--brand-gradient': 'linear-gradient(135deg, #00ff9f, #00c8ff)',
    '--brand-text':     '#000',

    // Shape
    '--radius':    '16px',
    '--radius-sm': '10px',
    '--radius-xs': '8px',

    // Sidebar border
    '--sidebar-border': '1px solid rgba(0,255,159,0.12)',
    '--topbar-border':  '1px solid rgba(0,255,159,0.1)',
  },

  // ════════════════════════════════════════════
  // ☀️ Light — Clean Modern
  // ════════════════════════════════════════════
  light: {
    '--bg1':   '#f0f5ff',
    '--bg2':   '#ffffff',
    '--bg3':   '#e2e8f0',
    '--text':  '#0f172a',
    '--t2':    '#64748b',
    '--text2': '#64748b',
    '--accent':'#6366f1',
    '--border':'rgba(0,0,0,0.08)',
    '--card':  '#ffffff',

    '--sidebar-bg':   '#ffffff',
    '--topbar-bg':    '#ffffff',
    '--modal-bg':     '#ffffff',
    '--input-bg':     '#f8fafc',
    '--input-border': 'rgba(0,0,0,0.12)',
    '--input-focus':  'rgba(99,102,241,0.05)',

    '--card-blur':    'none',
    '--sidebar-blur': 'none',

    '--shadow':       '0 2px 16px rgba(0,0,0,0.07)',
    '--shadow-hover': '0 8px 32px rgba(99,102,241,0.18)',
    '--glow':         '0 4px 20px rgba(99,102,241,0.12)',
    '--glow2':        '0 8px 24px rgba(139,92,246,0.12)',

    '--nav-active-bg':     'rgba(99,102,241,0.1)',
    '--nav-active-shadow': 'none',
    '--nav-hover-bg':      'rgba(99,102,241,0.05)',

    '--btn-gradient': 'linear-gradient(135deg, #6366f1, #8b5cf6)',
    '--btn-text':     '#ffffff',
    '--btn-glow':     '0 4px 16px rgba(99,102,241,0.3)',

    '--brand-gradient': 'linear-gradient(135deg, #6366f1, #8b5cf6)',
    '--brand-text':     '#ffffff',

    '--radius':    '12px',
    '--radius-sm': '8px',
    '--radius-xs': '6px',

    '--sidebar-border': '1px solid #e2e8f0',
    '--topbar-border':  '1px solid #e2e8f0',
  },

  // ════════════════════════════════════════════
  // 📚 Library — Warm Parchment
  // ════════════════════════════════════════════
  library: {
    '--bg1':   '#120d05',
    '--bg2':   '#1e1409',
    '--bg3':   '#2d1e0b',
    '--text':  '#f0ddb8',
    '--t2':    '#b8955a',
    '--text2': '#b8955a',
    '--accent':'#d4892a',
    '--border':'rgba(212,137,42,0.22)',
    '--card':  'rgba(40,26,10,0.85)',

    '--sidebar-bg':   '#1a1108',
    '--topbar-bg':    'rgba(18,13,5,0.96)',
    '--modal-bg':     '#261a08',
    '--input-bg':     'rgba(0,0,0,0.25)',
    '--input-border': 'rgba(212,137,42,0.25)',
    '--input-focus':  'rgba(212,137,42,0.06)',

    '--card-blur':    'none',
    '--sidebar-blur': 'none',

    '--shadow':       '0 3px 18px rgba(0,0,0,0.5)',
    '--shadow-hover': '0 8px 28px rgba(212,137,42,0.18)',
    '--glow':         '0 4px 18px rgba(212,137,42,0.15)',
    '--glow2':        '0 8px 24px rgba(180,100,20,0.2)',

    '--nav-active-bg':     'rgba(212,137,42,0.15)',
    '--nav-active-shadow': 'none',
    '--nav-hover-bg':      'rgba(212,137,42,0.08)',

    '--btn-gradient': 'linear-gradient(135deg, #d4892a, #e6a040)',
    '--btn-text':     '#120d05',
    '--btn-glow':     '0 4px 18px rgba(212,137,42,0.3)',

    '--brand-gradient': 'linear-gradient(135deg, #d4892a, #f0b050)',
    '--brand-text':     '#120d05',

    '--radius':    '8px',
    '--radius-sm': '6px',
    '--radius-xs': '4px',

    '--sidebar-border': '1px solid rgba(212,137,42,0.18)',
    '--topbar-border':  '1px solid rgba(212,137,42,0.15)',
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

    // data-theme للـ CSS selectors في style.css
    root.setAttribute('data-theme', theme)

    const br = settings.value?.brightness ?? 100
    root.style.setProperty('--brightness', br + '%')
    document.body.style.filter = br < 100 ? `brightness(${br}%)` : ''
  })
}
