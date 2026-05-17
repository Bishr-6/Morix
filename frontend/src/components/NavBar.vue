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
      <!-- Theme pills -->
      <div class="mn-pills" title="الثيم">
        <button v-for="th in themeList" :key="th.k"
          :class="['mn-pill', { active: currentTheme === th.k }]"
          @click="$emit('theme', th.k)" :title="th.label">
          {{ th.icon }}
        </button>
      </div>

      <div class="mn-sep" />

      <!-- Language pills -->
      <div class="mn-pills mn-langs">
        <button v-for="(L, code) in LANGUAGES" :key="code"
          :class="['mn-pill', 'lang-pill', { active: currentLang === code }]"
          @click="$emit('lang', code)" :title="L.name">
          {{ L.flag }}
        </button>
      </div>

      <div class="mn-sep" />

      <!-- User chip -->
      <div class="mn-user">
        <img v-if="avatarUrl" :src="avatarUrl" class="mn-av-img" />
        <div v-else class="mn-av">{{ name?.[0] || '?' }}</div>
        <span class="mn-name">{{ name }}</span>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { LANGUAGES } from '../composables/useI18n.js'

const props = defineProps({
  title:        { type: String, default: '' },
  name:         { type: String, default: '' },
  avatarUrl:    { type: String, default: '' },
  currentTheme: { type: String, default: 'dark' },
  currentLang:  { type: String, default: 'ar' },
})

defineEmits(['theme', 'lang'])

const themeList = [
  { k: 'dark',    icon: '🌙', label: 'داكن' },
  { k: 'light',   icon: '☀️', label: 'فاتح' },
  { k: 'library', icon: '📚', label: 'مكتبة' },
  { k: 'neon',    icon: '💜', label: 'نيون' },
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
.lang-pill { font-size: 16px; width: 28px; height: 28px; }

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

/* Mobile */
@media (max-width: 768px) {
  .mn-name, .mn-sep, .mn-langs { display: none; }
  .mn-title { font-size: 14px; }
  .morix-nav { padding: 8px 14px; }
}
</style>
