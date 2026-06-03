<template>
  <header class="morix-nav">
    <!-- Brand + Title -->
    <div class="mn-left">
      <div class="mn-brand">
        <div class="mn-logo">M</div>
      </div>
      <h2 class="mn-title">{{ title }}</h2>
    </div>

    <!-- Center: Quick action slots -->
    <div class="mn-center">
      <slot name="actions" />
    </div>

    <!-- Right: Controls -->
    <div class="mn-right">
      <!-- Theme pills (desktop) -->
      <div class="mn-pills mn-themes" title="الثيم">
        <button v-for="th in themeList" :key="th.k"
          :class="['mn-pill', { active: currentTheme === th.k }]"
          @click="$emit('theme', th.k)" :title="th.label"
          v-html="th.svg">
        </button>
      </div>

      <div class="mn-sep mn-desk" />

      <!-- Language flags (desktop) -->
      <div class="mn-pills mn-langs">
        <button v-for="(L, code) in LANGUAGES" :key="code"
          :class="['mn-pill', 'lang-pill', { active: currentLang === code }]"
          @click="$emit('lang', code)" :title="L.name">
          <img :src="L.flagImg" :alt="L.name" class="mn-flag-img" />
        </button>
      </div>

      <!-- Mobile menu button (theme+lang in vertical dropdown) -->
      <button class="mn-pill mn-mobile-btn" @click.stop="menuOpen=!menuOpen" title="القائمة">
        <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18"><path d="M2 5h16M2 10h16M2 15h16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
      </button>

      <div class="mn-sep mn-desk" />

      <!-- User chip -->
      <div class="mn-user">
        <img v-if="avatarUrl && (avatarUrl.startsWith('data:') || avatarUrl.startsWith('http'))" :src="avatarUrl" class="mn-av-img" />
        <div v-else class="mn-av">{{ name?.[0] || '?' }}</div>
        <span class="mn-name">{{ name }}</span>
      </div>
    </div>

    <!-- Mobile dropdown (theme + languages, vertical) -->
    <div v-if="menuOpen" class="mn-backdrop" @click="menuOpen=false"></div>
    <div v-if="menuOpen" class="mn-dropdown">
      <div class="mn-dd-title">🎨 الثيم</div>
      <button v-for="th in themeList" :key="'th'+th.k"
        :class="['mn-dd-item', { active: currentTheme === th.k }]"
        @click="$emit('theme', th.k); menuOpen=false">
        <span v-html="th.svg" style="display:inline-flex;margin-left:8px"></span>{{ th.label }}
      </button>
      <div class="mn-dd-title">🌐 اللغة</div>
      <button v-for="(L, code) in LANGUAGES" :key="'lg'+code"
        :class="['mn-dd-item', { active: currentLang === code }]"
        @click="$emit('lang', code); menuOpen=false">
        <img :src="L.flagImg" :alt="L.name" style="width:22px;height:15px;border-radius:3px;margin-left:8px" />{{ L.name }}
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed, ref } from 'vue'
import { LANGUAGES } from '../composables/useI18n.js'

const menuOpen = ref(false)

const props = defineProps({
  title:        { type: String, default: '' },
  name:         { type: String, default: '' },
  avatarUrl:    { type: String, default: '' },
  currentTheme: { type: String, default: 'dark' },
  currentLang:  { type: String, default: 'ar' },
})

defineEmits(['theme', 'lang'])

const themeList = [
  { k: 'dark',    svg: `<svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16"><path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"/></svg>`, label: 'Dark' },
  { k: 'light',   svg: `<svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16"><circle cx="10" cy="10" r="4"/><path d="M10 1v2m0 14v2m-7-9H1m18 0h-2m-2.05-5.95l-1.41 1.41m-7.08 7.08l-1.41 1.41m0-9.9l1.41 1.41m7.08 7.08l1.41 1.41"/></svg>`, label: 'Light' },
  { k: 'library', svg: `<svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16"><path d="M2 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1H3a1 1 0 01-1-1V4zm5-1a1 1 0 00-1 1v12a1 1 0 001 1h2a1 1 0 001-1V4a1 1 0 00-1-1H7zm5 0a1 1 0 00-.8.4l4 12a1 1 0 001.2.6l1.9-.6a1 1 0 00.6-1.2l-4-12a1 1 0 00-1.2-.6L12.2 3z"/></svg>`, label: 'Library' },
  { k: 'neon',    svg: `<svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16"><path d="M11.3 1.05a1 1 0 00-1.1.45L5.7 9H2a1 1 0 00-.8 1.6l7.5 10a1 1 0 001.8-.6L9.7 13H18a1 1 0 00.8-1.6l-7.5-10.35z"/></svg>`, label: 'Neon' },
]
</script>

<style scoped>
.morix-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 20px;
  background: var(--topbar-bg);
  backdrop-filter: var(--sidebar-blur);
  -webkit-backdrop-filter: var(--sidebar-blur);
  border-bottom: var(--topbar-border);
  position: sticky;
  top: 0;
  z-index: 50;
  flex-wrap: nowrap;
}

/* Left */
.mn-left { display: flex; align-items: center; gap: 10px; min-width: 0; flex-shrink: 0; }
.mn-logo {
  width: 32px; height: 32px; border-radius: 9px; flex-shrink: 0;
  background: var(--brand-gradient);
  display: flex; align-items: center; justify-content: center;
  font-weight: 900; font-size: 16px; color: var(--brand-text);
  box-shadow: var(--btn-glow);
}
.mn-title {
  font-size: 16px; font-weight: 700; color: var(--text);
  margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

/* Center */
.mn-center { display: flex; align-items: center; gap: 8px; flex: 1; justify-content: center; flex-wrap: wrap; }

/* Right */
.mn-right { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.mn-sep { width: 1px; height: 22px; background: var(--border); }

/* Pills */
.mn-pills { display: flex; gap: 3px; }
.mn-langs { gap: 2px; }
.mn-pill {
  width: 30px; height: 30px; border-radius: 8px;
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer; font-size: 14px;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.18s;
  color: var(--text2);
}
.mn-pill:hover {
  background: var(--nav-hover-bg);
  border-color: var(--border);
}
.mn-pill.active {
  background: var(--nav-active-bg);
  border-color: var(--accent);
  box-shadow: var(--nav-active-shadow), 0 0 8px rgba(var(--accent-rgb, 79,158,255), 0.2);
  color: var(--accent);
}
.lang-pill { font-size: 16px; width: 28px; height: 28px; padding: 2px; }
.mn-flag-img { width: 20px; height: 14px; border-radius: 2px; object-fit: cover; display: block; }

/* User chip */
.mn-user { display: flex; align-items: center; gap: 8px; cursor: default; }
.mn-av-img, .mn-av {
  width: 32px; height: 32px; border-radius: 50%;
  object-fit: cover; font-size: 14px; font-weight: 700;
  background: var(--btn-gradient); color: var(--btn-text);
  display: flex; align-items: center; justify-content: center;
  box-shadow: var(--btn-glow);
}
.mn-name { font-size: 13px; color: var(--text2); font-weight: 500; white-space: nowrap; }

/* Mobile menu button (hidden on desktop) */
.mn-mobile-btn { display: none; color: var(--accent, #4f9eff); }
.morix-nav { position: relative; }
.mn-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 49; }
.mn-dropdown {
  position: absolute; top: calc(100% + 4px); left: 8px;
  width: 240px; max-height: 70vh; overflow-y: auto;
  background: var(--card, #0b0e1f);
  border: 1px solid var(--border, #1a1f3a);
  border-radius: 14px; padding: 10px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.45);
  z-index: 60;
}
.mn-dd-title {
  font-size: 11px; font-weight: 700;
  color: var(--t2, #94a3b8);
  text-transform: uppercase; letter-spacing: 1px;
  padding: 8px 8px 6px;
}
.mn-dd-item {
  display: flex; align-items: center; width: 100%;
  background: transparent; border: 1px solid transparent;
  color: var(--text, #fff); padding: 10px 10px;
  border-radius: 8px; cursor: pointer;
  font-size: 13px; text-align: right;
  font-family: inherit; margin-bottom: 2px;
}
.mn-dd-item:hover {
  background: var(--nav-hover-bg, rgba(99,102,241,0.08));
}
.mn-dd-item.active {
  background: var(--nav-active-bg, rgba(99,102,241,0.15));
  border-color: var(--accent, #4f9eff);
  color: var(--accent, #4f9eff);
}

/* Mobile breakpoint */
@media (max-width: 768px) {
  .mn-name, .mn-themes, .mn-langs, .mn-desk { display: none; }
  .mn-mobile-btn { display: flex; }
  .mn-title { font-size: 14px; }
  .morix-nav { padding: 8px 14px; }
}
</style>
