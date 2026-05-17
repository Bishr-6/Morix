<template>
  <div class="landing">
    <!-- Matrix Background Canvas -->
    <canvas ref="bgCanvas" class="bg-canvas" />

    <!-- Floating particles -->
    <div class="particles">
      <div v-for="i in 20" :key="i" class="particle" :style="particleStyle(i)" />
    </div>

    <!-- ======= NAVBAR ======= -->
    <nav class="navbar">
      <div class="nav-brand">
        <div class="brand-icon">M</div>
        <span class="brand-name">Morix</span>
      </div>
      <div class="nav-links">
        <a href="#features" class="nav-link">{{ t('features_nav') }}</a>
        <a href="#roles" class="nav-link">{{ t('roles_nav') }}</a>
        <a href="#stats" class="nav-link">{{ t('stats_nav') }}</a>
      </div>
      <!-- مبدّل اللغات -->
      <div class="nav-lang-switcher">
        <button v-for="(L, code) in LANGUAGES" :key="code"
                @click="setLang(code)"
                class="lang-pill"
                :class="{ active: lang === code }"
                :title="L.name">
          {{ L.flag }}
        </button>
      </div>
      <button class="nav-cta" @click="scrollToLogin">{{ t('start_now') }}</button>
    </nav>

    <!-- ======= HERO ======= -->
    <section class="hero">
      <div class="hero-badge">🚀 منصة التعلم الذكي #1</div>
      <h1 class="hero-title">
        تعلّم بذكاء<br/>
        <span class="gradient-text">مع الذكاء الاصطناعي</span>
      </h1>
      <p class="hero-sub">
        موريكس — منصة تعليمية متكاملة تجمع بين الذكاء الاصطناعي والتعليم الشخصي.
        للطلاب، المعلمين، والمدارس.
      </p>
      <div class="hero-actions">
        <button class="btn-hero" @click="scrollToLogin">تسجيل الدخول</button>
        <a href="#features" class="btn-ghost">اكتشف المزيد ↓</a>
      </div>

      <!-- Floating cards preview -->
      <div class="float-cards">
        <div class="float-card" style="animation-delay:0s">
          <span class="fc-icon">🤖</span>
          <span class="fc-label">مساعد AI</span>
        </div>
        <div class="float-card" style="animation-delay:0.4s">
          <span class="fc-icon">🎮</span>
          <span class="fc-label">ألعاب تعليمية</span>
        </div>
        <div class="float-card" style="animation-delay:0.8s">
          <span class="fc-icon">📊</span>
          <span class="fc-label">تحليل الأداء</span>
        </div>
        <div class="float-card" style="animation-delay:1.2s">
          <span class="fc-icon">🏆</span>
          <span class="fc-label">لوحة المتصدرين</span>
        </div>
      </div>
    </section>

    <!-- ======= STATS ======= -->
    <section id="stats" class="stats-section">
      <div class="stats-grid">
        <div class="stat-item" v-for="s in statsData" :key="s.label">
          <div class="stat-num">{{ s.num }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </div>
    </section>

    <!-- ======= FEATURES ======= -->
    <section id="features" class="features-section">
      <div class="section-header">
        <div class="section-tag">✨ المميزات</div>
        <h2 class="section-title">كل ما تحتاجه في مكان واحد</h2>
        <p class="section-sub">منصة شاملة مدعومة بأحدث تقنيات الذكاء الاصطناعي</p>
      </div>
      <div class="features-grid">
        <div v-for="f in features" :key="f.title" class="feature-card">
          <div class="feat-icon">{{ f.icon }}</div>
          <h3 class="feat-title">{{ f.title }}</h3>
          <p class="feat-desc">{{ f.desc }}</p>
        </div>
      </div>
    </section>

    <!-- ======= ROLES ======= -->
    <section id="roles" class="roles-section">
      <div class="section-header">
        <div class="section-tag">👥 لمن نحن</div>
        <h2 class="section-title">منصة لكل أدوار التعليم</h2>
      </div>
      <div class="roles-grid">
        <div v-for="r in roles" :key="r.title" class="role-card" :style="`--rc:${r.color}`">
          <div class="role-icon">{{ r.icon }}</div>
          <h3 class="role-title">{{ r.title }}</h3>
          <ul class="role-list">
            <li v-for="item in r.items" :key="item">{{ item }}</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- ======= LOGIN CARD ======= -->
    <section id="login-section" class="login-section">
      <div class="login-wrapper">
        <div class="login-info">
          <h2 class="login-info-title">ابدأ رحلتك التعليمية</h2>
          <p class="login-info-sub">سجّل دخولك وانضم إلى آلاف الطلاب والمعلمين على منصة موريكس</p>
          <div class="login-features">
            <div v-for="lf in loginFeatures" :key="lf" class="lf-item">
              <span class="lf-check">✓</span> {{ lf }}
            </div>
          </div>
        </div>

        <div class="login-card">
          <div class="card-header">
            <div class="card-logo">M</div>
            <div>
              <h2 class="card-title">{{ t('login') }}</h2>
              <p class="card-sub">{{ t('tagline') }}</p>
            </div>
          </div>

          <form @submit.prevent="handleLogin" class="login-form">
            <div class="field">
              <label>{{ t('email') }}</label>
              <input v-model="email" type="email" placeholder="you@morix.tech" autocomplete="username" required />
            </div>
            <div class="field">
              <label>{{ t('password') }}</label>
              <div class="pass-wrap">
                <input v-model="password" :type="showPass ? 'text' : 'password'" placeholder="••••••••" autocomplete="current-password" required />
                <button type="button" class="eye-btn" @click="showPass = !showPass">{{ showPass ? '🙈' : '👁️' }}</button>
              </div>
            </div>
            <div v-if="error" class="error-msg">{{ error }}</div>
            <button type="submit" class="login-btn" :disabled="loading">
              <span v-if="loading" class="spinner"></span>
              <span v-else>{{ t('login_button') }}</span>
            </button>
          </form>

        </div>
      </div>
    </section>

    <!-- ======= FOOTER ======= -->
    <footer class="footer">
      <div class="footer-brand">
        <div class="brand-icon sm">M</div>
        <span>Morix — منصة التعلم الذكي</span>
      </div>
      <p class="footer-copy">© 2026 Morix. {{ t('all_rights') }}</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import { useI18n, LANGUAGES } from '../composables/useI18n.js'

const router = useRouter()
const auth = useAuthStore()
const { t, lang, setLang } = useI18n()
const email = ref('')
const password = ref('')
const showPass = ref(false)
const loading = ref(false)
const error = ref('')

// ── Matrix canvas ──
const bgCanvas = ref(null)
let ctx, raf, drops = [], cols = 0
const CHARS = 'ﾑｱﾓｻﾘﾛｦｿﾃﾄｼｽｾ01アウエカキクコサシABCDEFGHIJ0123456789@#$%&'
const FS = 13

function initCanvas() {
  if (!bgCanvas.value) return
  const c = bgCanvas.value
  c.width = window.innerWidth
  c.height = window.innerHeight
  ctx = c.getContext('2d')
  cols = Math.floor(c.width / FS)
  drops = Array.from({ length: cols }, () => Math.random() * -(c.height / FS))
}

function drawCanvas() {
  if (!bgCanvas.value || !ctx) return
  const { width, height } = bgCanvas.value
  ctx.fillStyle = 'rgba(0, 0, 14, 0.07)'
  ctx.fillRect(0, 0, width, height)
  ctx.font = `${FS}px monospace`
  for (let i = 0; i < cols; i++) {
    const y = drops[i] * FS
    if (y < 0) { drops[i] += 0.4; continue }
    const char = CHARS[Math.floor(Math.random() * CHARS.length)]
    ctx.fillStyle = 'rgba(0, 200, 80, 0.5)'
    ctx.fillText(char, i * FS, y)
    if (Math.random() > 0.75) {
      ctx.shadowColor = '#00ff41'
      ctx.shadowBlur = 8
      ctx.fillStyle = 'rgba(180, 255, 180, 0.9)'
      ctx.fillText(char, i * FS, y)
      ctx.shadowBlur = 0
    }
    if (y > height && Math.random() > 0.975) drops[i] = 0
    drops[i] += 0.42
  }
  raf = requestAnimationFrame(drawCanvas)
}

function particleStyle(i) {
  const seed = i * 137.508
  return {
    left: `${(seed % 100)}%`,
    top: `${((seed * 1.618) % 100)}%`,
    width: `${2 + (i % 4)}px`,
    height: `${2 + (i % 4)}px`,
    animationDelay: `${(i * 0.4) % 8}s`,
    animationDuration: `${6 + (i % 6)}s`,
  }
}

function scrollToLogin() {
  document.getElementById('login-section')?.scrollIntoView({ behavior: 'smooth' })
}

async function handleLogin() {
  error.value = ''
  loading.value = true
  const result = await auth.login(email.value.trim(), password.value)
  loading.value = false
  if (result.success) {
    router.push(result.redirect)
  } else {
    error.value = result.error
  }
}

function fillDemo(e, p) {
  email.value = e
  password.value = p
  scrollToLogin()
}

onMounted(() => {
  initCanvas()
  drawCanvas()
  window.addEventListener('resize', initCanvas)
})
onUnmounted(() => {
  cancelAnimationFrame(raf)
  window.removeEventListener('resize', initCanvas)
})

// ── Data ──
const statsData = [
  { num: '١٠٠٠+', label: 'طالب نشط' },
  { num: '٥٠+', label: 'معلم محترف' },
  { num: '٢٠+', label: 'مدرسة' },
  { num: '٩٨٪', label: 'رضا المستخدمين' },
]

const features = [
  { icon: '🤖', title: 'مساعد AI ذكي', desc: 'محادثات تعليمية مدعومة بـ Gemini AI مع إمكانية رفع الملفات والصور' },
  { icon: '🎮', title: 'ألعاب تعليمية', desc: 'اختبارات MCQ وبطاقات تعليمية ومطابقة المفاهيم بشكل تفاعلي ممتع' },
  { icon: '📊', title: 'تحليل الأداء', desc: 'رسوم بيانية وإحصاءات مفصلة لتتبع تقدم الطلاب وتحديد نقاط الضعف' },
  { icon: '📚', title: 'ملخصات الكتب', desc: 'رفع الكتب وتوليد ملخصات ذكية وأسئلة تفاعلية بضغطة واحدة' },
  { icon: '🏆', title: 'نظام النقاط', desc: 'نجوم ومتصدرون وتحديات يومية لتحفيز الطلاب على الاستمرار' },
  { icon: '📋', title: 'واجبات واختبارات', desc: 'إنشاء وتوزيع الواجبات والاختبارات وتصحيحها تلقائياً بالذكاء الاصطناعي' },
  { icon: '🎨', title: 'توليد PPT وصور', desc: 'توليد عروض تقديمية وصور تعليمية بالذكاء الاصطناعي في ثوانٍ' },
  { icon: '🌐', title: '٦ لغات', desc: 'دعم كامل للعربية والإنجليزية والصينية والألمانية والإسبانية والفرنسية' },
  { icon: '⏱️', title: 'بومودورو ذكي', desc: 'مؤقت دراسة مدمج مع تتبع جلسات التركيز وتقنيات التعلم الفعّال' },
]

const roles = [
  {
    icon: '🏫', title: 'مدير المدرسة', color: '#3b82f6',
    items: ['إنشاء وإدارة المدارس', 'رفع بيانات الطلاب Excel', 'المستشار الاستراتيجي AI', 'إدارة الكتب والمحتوى'],
  },
  {
    icon: '🛡️', title: 'المشرف الإداري', color: '#22c55e',
    items: ['متابعة الطلاب والأنشطة', 'إعلانات المدرسة', 'تقارير الحوادث بالذكاء', 'لوحة صحة المدرسة'],
  },
  {
    icon: '👨‍🏫', title: 'المعلم', color: '#f59e0b',
    items: ['توليد خطط الدروس AI', 'إنشاء واجبات واختبارات', 'دفتر ذكي لتحليل الملفات', 'تقارير أداء الطلاب'],
  },
  {
    icon: '👨‍🎓', title: 'الطالب', color: '#00ff9f',
    items: ['محادثات AI مخصصة', 'ألعاب وتحديات يومية', 'ملخصات الكتب التفاعلية', 'تتبع التقدم والنجوم'],
  },
]

const loginFeatures = [
  'واجهة متعددة اللغات (٦ لغات)',
  'نظام ثيمات متعدد (داكن / فاتح / مكتبة)',
  'حماية كاملة للبيانات',
  'وصول فوري بعد تسجيل الدخول',
]
</script>

<style scoped>
/* ── Base ── */
.landing {
  min-height: 100vh;
  background: #00000e;
  color: #dff4ff;
  font-family: 'Segoe UI', 'Cairo', sans-serif;
  direction: rtl;
  position: relative;
  overflow-x: hidden;
}
.bg-canvas {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.28;
}

/* ── Particles ── */
.particles { position: fixed; inset: 0; z-index: 0; pointer-events: none; }
.particle {
  position: absolute;
  border-radius: 50%;
  background: rgba(0, 255, 159, 0.6);
  animation: float linear infinite;
  box-shadow: 0 0 6px rgba(0, 255, 159, 0.5);
}
@keyframes float {
  0% { transform: translateY(0) scale(1); opacity: 0.6; }
  50% { transform: translateY(-30px) scale(1.3); opacity: 1; }
  100% { transform: translateY(0) scale(1); opacity: 0.6; }
}

/* ── All sections above canvas ── */
nav, section, footer { position: relative; z-index: 1; }

/* ── Navbar ── */
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 40px;
  background: rgba(0, 5, 20, 0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0, 255, 159, 0.12);
  position: sticky;
  top: 0;
  z-index: 100;
}
.nav-brand { display: flex; align-items: center; gap: 10px; }
.brand-icon {
  width: 38px; height: 38px;
  background: linear-gradient(135deg, #00ff9f, #00c8ff);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 900; font-size: 20px; color: #000;
}
.brand-icon.sm { width: 28px; height: 28px; font-size: 14px; border-radius: 7px; }
.brand-name { font-size: 20px; font-weight: 800; color: #fff; }
.nav-links { display: flex; gap: 28px; }
.nav-link {
  color: #7ec8e3; font-size: 14px; text-decoration: none;
  transition: color 0.2s;
}
.nav-link:hover { color: #00ff9f; }
.nav-cta {
  background: linear-gradient(135deg, #00ff9f, #00c8ff);
  color: #000; border: none; border-radius: 10px;
  padding: 10px 22px; font-size: 14px; font-weight: 700;
  cursor: pointer; transition: opacity 0.2s, transform 0.1s;
}
.nav-cta:hover { opacity: 0.88; transform: translateY(-1px); }

/* ── Language switcher in navbar ── */
.nav-lang-switcher {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(0,255,159,0.06);
  border: 1px solid rgba(0,255,159,0.15);
  border-radius: 20px;
  padding: 4px 8px;
}
.lang-pill {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
  border-radius: 50%;
  width: 30px; height: 30px;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.2s, transform 0.15s;
  opacity: 0.6;
}
.lang-pill:hover { opacity: 1; transform: scale(1.15); }
.lang-pill.active {
  opacity: 1;
  background: rgba(0,255,159,0.2);
  box-shadow: 0 0 8px rgba(0,255,159,0.4);
  transform: scale(1.1);
}

/* ── Hero ── */
.hero {
  min-height: 90vh;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  text-align: center;
  padding: 80px 24px 60px;
}
.hero-badge {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(0, 255, 159, 0.1);
  border: 1px solid rgba(0, 255, 159, 0.3);
  color: #00ff9f; border-radius: 30px;
  padding: 6px 18px; font-size: 13px; font-weight: 600;
  margin-bottom: 28px;
  animation: pulse-badge 3s ease-in-out infinite;
}
@keyframes pulse-badge {
  0%, 100% { box-shadow: 0 0 0 0 rgba(0,255,159,0.3); }
  50% { box-shadow: 0 0 0 8px rgba(0,255,159,0); }
}
.hero-title {
  font-size: clamp(38px, 7vw, 80px);
  font-weight: 900; color: #fff;
  line-height: 1.15; margin: 0 0 20px;
  text-shadow: 0 0 40px rgba(0, 200, 255, 0.3);
}
.gradient-text {
  background: linear-gradient(135deg, #00ff9f, #00c8ff, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-sub {
  max-width: 560px; font-size: 17px; color: #7ec8e3;
  line-height: 1.7; margin: 0 0 36px;
}
.hero-actions { display: flex; gap: 16px; flex-wrap: wrap; justify-content: center; margin-bottom: 60px; }
.btn-hero {
  background: linear-gradient(135deg, #00ff9f, #00c8ff);
  color: #000; border: none; border-radius: 14px;
  padding: 16px 36px; font-size: 16px; font-weight: 800;
  cursor: pointer; transition: all 0.2s;
  box-shadow: 0 0 30px rgba(0, 255, 159, 0.3);
}
.btn-hero:hover { transform: translateY(-2px); box-shadow: 0 0 50px rgba(0,255,159,0.5); }
.btn-ghost {
  background: transparent;
  border: 1px solid rgba(0,255,159,0.4);
  color: #00ff9f; border-radius: 14px;
  padding: 16px 36px; font-size: 16px; font-weight: 700;
  cursor: pointer; text-decoration: none; display: inline-flex; align-items: center;
  transition: all 0.2s;
}
.btn-ghost:hover { background: rgba(0,255,159,0.08); border-color: #00ff9f; }

/* Float cards */
.float-cards { display: flex; gap: 16px; flex-wrap: wrap; justify-content: center; }
.float-card {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  background: rgba(4, 16, 44, 0.8);
  border: 1px solid rgba(0, 255, 159, 0.2);
  border-radius: 16px; padding: 18px 24px;
  backdrop-filter: blur(12px);
  animation: floatCard 4s ease-in-out infinite;
  transition: transform 0.2s;
}
.float-card:hover { transform: translateY(-4px) scale(1.04); }
@keyframes floatCard {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
.fc-icon { font-size: 28px; }
.fc-label { font-size: 12px; color: #7ec8e3; font-weight: 600; }

/* ── Stats ── */
.stats-section {
  padding: 60px 24px;
  background: rgba(0, 255, 159, 0.04);
  border-top: 1px solid rgba(0,255,159,0.1);
  border-bottom: 1px solid rgba(0,255,159,0.1);
}
.stats-grid {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 20px; max-width: 900px; margin: 0 auto;
}
.stat-item { text-align: center; }
.stat-num {
  font-size: 42px; font-weight: 900; color: #00ff9f;
  text-shadow: 0 0 20px rgba(0,255,159,0.5);
}
.stat-label { font-size: 14px; color: #7ec8e3; margin-top: 4px; }

/* ── Features ── */
.features-section { padding: 80px 24px; max-width: 1200px; margin: 0 auto; }
.section-header { text-align: center; margin-bottom: 56px; }
.section-tag {
  display: inline-block;
  background: rgba(0,255,159,0.1); border: 1px solid rgba(0,255,159,0.3);
  color: #00ff9f; border-radius: 20px; padding: 4px 16px;
  font-size: 13px; font-weight: 600; margin-bottom: 16px;
}
.section-title { font-size: 32px; font-weight: 800; color: #fff; margin: 0 0 12px; }
.section-sub { color: #7ec8e3; font-size: 15px; }
.features-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;
}
.feature-card {
  background: rgba(0, 255, 159, 0.03);
  border: 1px solid rgba(0,255,159,0.12);
  border-radius: 20px; padding: 28px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  transition: all 0.3s;
  position: relative; overflow: hidden;
}
.feature-card::before {
  content: '';
  position: absolute; inset: 0; border-radius: 20px;
  background: radial-gradient(ellipse at 50% 0%, rgba(0,255,159,0.06) 0%, transparent 70%);
  pointer-events: none;
}
.feature-card:hover {
  border-color: rgba(0,255,159,0.35);
  transform: translateY(-6px);
  box-shadow: 0 0 0 1px rgba(0,255,159,0.2), 0 12px 40px rgba(0,255,159,0.15);
}
.feat-icon { font-size: 32px; margin-bottom: 14px; }
.feat-title { font-size: 16px; font-weight: 700; color: #fff; margin: 0 0 8px; }
.feat-desc { font-size: 13px; color: #7ec8e3; line-height: 1.7; margin: 0; }

/* ── Roles ── */
.roles-section {
  padding: 80px 24px;
  background: rgba(0, 5, 20, 0.5);
}
.roles-section .section-header { text-align: center; margin-bottom: 48px; }
.roles-grid {
  display: grid; grid-template-columns: repeat(5, 1fr);
  gap: 16px; max-width: 1200px; margin: 0 auto;
}
.role-card {
  background: rgba(0, 5, 30, 0.6);
  border: 1px solid rgba(255,255,255,0.06);
  border-top: 3px solid var(--rc);
  border-radius: 18px; padding: 24px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  transition: all 0.3s;
  box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}
.role-card:hover {
  transform: translateY(-6px);
  border-color: var(--rc);
  box-shadow: 0 0 0 1px var(--rc), 0 12px 40px rgba(0,0,0,0.4), 0 0 30px rgba(0,0,0,0.2);
}
.role-icon { font-size: 36px; margin-bottom: 12px; }
.role-title { font-size: 15px; font-weight: 700; color: #fff; margin: 0 0 14px; }
.role-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 7px; }
.role-list li { color: #7ec8e3; font-size: 12px; padding-right: 14px; position: relative; }
.role-list li::before { content: '◆'; position: absolute; right: 0; color: var(--rc); font-size: 8px; top: 3px; }

/* ── Login Section ── */
.login-section { padding: 80px 24px; }
.login-wrapper {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 60px; max-width: 1000px; margin: 0 auto; align-items: center;
}
.login-info-title { font-size: 28px; font-weight: 800; color: #fff; margin: 0 0 12px; }
.login-info-sub { color: #7ec8e3; font-size: 15px; line-height: 1.7; margin: 0 0 28px; }
.login-features { display: flex; flex-direction: column; gap: 12px; }
.lf-item { display: flex; align-items: center; gap: 10px; color: #dff4ff; font-size: 14px; }
.lf-check {
  width: 22px; height: 22px; min-width: 22px;
  background: rgba(0,255,159,0.15); border: 1px solid rgba(0,255,159,0.4);
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  color: #00ff9f; font-size: 11px; font-weight: 700;
}

/* Login Card */
.login-card {
  background: rgba(2, 10, 32, 0.82);
  border: 1px solid rgba(0, 255, 159, 0.18);
  border-radius: 26px; padding: 40px 36px;
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  box-shadow: 0 0 0 1px rgba(0,255,159,0.08), 0 0 60px rgba(0,255,159,0.08), 0 30px 60px rgba(0,0,0,0.6);
  position: relative; overflow: hidden;
}
.login-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0,255,159,0.5), transparent);
}
.card-header { display: flex; align-items: center; gap: 16px; margin-bottom: 32px; }
.card-logo {
  width: 52px; height: 52px;
  background: linear-gradient(135deg, #00ff9f, #00c8ff);
  border-radius: 14px; display: flex; align-items: center; justify-content: center;
  font-weight: 900; font-size: 26px; color: #000;
  box-shadow: 0 0 20px rgba(0,255,159,0.3);
}
.card-title { font-size: 22px; font-weight: 800; color: #fff; margin: 0 0 2px; }
.card-sub { color: #7ec8e3; font-size: 13px; margin: 0; }
.login-form { display: flex; flex-direction: column; gap: 18px; margin-bottom: 24px; }
.field { display: flex; flex-direction: column; gap: 7px; }
.field label { color: #7ec8e3; font-size: 13px; font-weight: 600; }
.field input, .pass-wrap input {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(0,255,159,0.2);
  border-radius: 12px; padding: 13px 16px;
  color: #dff4ff; font-size: 15px; width: 100%;
  box-sizing: border-box; transition: border-color 0.2s; text-align: right;
  font-family: inherit;
}
.field input:focus, .pass-wrap input:focus {
  outline: none; border-color: #00ff9f;
  box-shadow: 0 0 0 3px rgba(0,255,159,0.1);
  background: rgba(0,255,159,0.05);
}
.field input::placeholder { color: #3a5a6a; }
.pass-wrap { position: relative; }
.eye-btn {
  position: absolute; left: 12px; top: 50%; transform: translateY(-50%);
  background: none; border: none; cursor: pointer; font-size: 18px;
}
.error-msg {
  background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.3);
  color: #fca5a5; padding: 10px 14px; border-radius: 10px;
  font-size: 13px; text-align: center;
}
.login-btn {
  background: linear-gradient(135deg, #00ff9f, #00c8ff);
  color: #000; border: none; border-radius: 12px; padding: 15px;
  font-size: 15px; font-weight: 800; cursor: pointer;
  transition: opacity 0.2s, transform 0.1s, box-shadow 0.2s;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  box-shadow: 0 0 20px rgba(0,255,159,0.2);
}
.login-btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); box-shadow: 0 0 35px rgba(0,255,159,0.4); }
.login-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.spinner {
  width: 18px; height: 18px;
  border: 2px solid rgba(0,0,0,0.3); border-top-color: #000;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.demo-box {
  padding: 14px; background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07); border-radius: 12px;
}
.demo-title { color: #3a5a6a; font-size: 11px; margin: 0 0 10px; text-align: center; }
.demo-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 9px 10px; border-radius: 8px; cursor: pointer;
  transition: background 0.15s; margin-bottom: 4px;
}
.demo-item:hover { background: rgba(0,255,159,0.1); }
.demo-item:last-child { margin-bottom: 0; }
.demo-role { color: #7ec8e3; font-size: 12px; font-weight: 600; }
.demo-email { color: #00ff9f; font-size: 11px; direction: ltr; }

/* ── Footer ── */
.footer {
  padding: 32px 40px;
  border-top: 1px solid rgba(0,255,159,0.1);
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;
}
.footer-brand { display: flex; align-items: center; gap: 10px; color: #7ec8e3; font-size: 14px; }
.footer-copy { color: #3a5a6a; font-size: 13px; margin: 0; }

/* ── Responsive ── */
@media (max-width: 1100px) {
  .roles-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 900px) {
  .features-grid { grid-template-columns: repeat(2, 1fr); }
  .login-wrapper { grid-template-columns: 1fr; gap: 40px; }
  .login-info { text-align: center; }
  .login-features { align-items: center; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
  .navbar { padding: 12px 20px; }
  .nav-links { display: none; }
  .hero { padding: 60px 16px 40px; }
  .features-grid { grid-template-columns: 1fr; }
  .roles-grid { grid-template-columns: 1fr 1fr; }
  .float-cards { gap: 10px; }
  .float-card { padding: 14px 16px; }
  .login-card { padding: 28px 20px; }
}
</style>
