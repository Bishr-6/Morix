<template>
  <div class="login-page">
    <div class="login-card">
      <div class="logo-section">
        <div class="logo-icon">M</div>
        <h1 class="logo-text">Morix</h1>
        <p class="logo-sub">منصة التعلم الذكي</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="field">
          <label>البريد الإلكتروني</label>
          <input v-model="email" type="email" placeholder="you@morix.tech" autocomplete="username" required />
        </div>

        <div class="field">
          <label>كلمة المرور</label>
          <div class="pass-wrap">
            <input v-model="password" :type="showPass ? 'text' : 'password'" placeholder="••••••••" autocomplete="current-password" required />
            <button type="button" class="eye-btn" @click="showPass = !showPass">{{ showPass ? '🙈' : '👁️' }}</button>
          </div>
        </div>

        <div v-if="error" class="error-msg">{{ error }}</div>

        <button type="submit" class="login-btn" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>تسجيل الدخول</span>
        </button>
      </form>

      <div class="demo-box">
        <p class="demo-title">بيانات تجريبية (اضغط للملء):</p>
        <div class="demo-item" @click="fillDemo('manager@morix.tech', 'admin123')">
          <span class="demo-role">🏫 مدير</span>
          <span class="demo-email">manager@morix.tech</span>
        </div>
        <div class="demo-item" @click="fillDemo('teacher1@morix.tech', 'teacher123')">
          <span class="demo-role">👨‍🏫 معلم</span>
          <span class="demo-email">teacher1@morix.tech</span>
        </div>
        <div class="demo-item" @click="fillDemo('student1@morix.tech', 'student123')">
          <span class="demo-role">👨‍🎓 طالب</span>
          <span class="demo-email">student1@morix.tech</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const auth = useAuthStore()
const email = ref('')
const password = ref('')
const showPass = ref(false)
const loading = ref(false)
const error = ref('')

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
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
  font-family: 'Segoe UI', 'Cairo', sans-serif;
  direction: rtl;
  padding: 16px;
}
.login-card {
  background: rgba(255,255,255,0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 24px;
  padding: 48px 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 25px 50px rgba(0,0,0,0.5);
}
@media (max-width: 480px) {
  .login-card { padding: 28px 20px; border-radius: 18px; }
  .logo-icon { width: 56px !important; height: 56px !important; }
  .logo-text { font-size: 28px !important; }
  input { font-size: 16px !important; }
}
.logo-section { text-align: center; margin-bottom: 36px; }
.logo-icon {
  width: 72px; height: 72px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 20px;
  display: flex; align-items: center; justify-content: center;
  font-size: 36px; font-weight: 900; color: white;
  margin: 0 auto 16px;
  box-shadow: 0 8px 24px rgba(99,102,241,0.4);
}
.logo-text { font-size: 32px; font-weight: 800; color: white; margin: 0 0 4px; }
.logo-sub { color: #94a3b8; font-size: 14px; margin: 0; }
.login-form { display: flex; flex-direction: column; gap: 20px; }
.field { display: flex; flex-direction: column; gap: 8px; }
.field label { color: #94a3b8; font-size: 14px; font-weight: 600; }
.field input, .pass-wrap input {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 12px;
  padding: 14px 16px;
  color: white; font-size: 15px; width: 100%;
  box-sizing: border-box; transition: border-color 0.2s; text-align: right;
}
.field input:focus, .pass-wrap input:focus {
  outline: none; border-color: #6366f1; background: rgba(99,102,241,0.1);
}
.field input::placeholder { color: #475569; }
.pass-wrap { position: relative; }
.eye-btn {
  position: absolute; left: 12px; top: 50%; transform: translateY(-50%);
  background: none; border: none; cursor: pointer; font-size: 18px;
}
.error-msg {
  background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.3);
  color: #fca5a5; padding: 12px 16px; border-radius: 10px; font-size: 14px; text-align: center;
}
.login-btn {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white; border: none; border-radius: 12px; padding: 16px;
  font-size: 16px; font-weight: 700; cursor: pointer;
  transition: opacity 0.2s, transform 0.1s;
  display: flex; align-items: center; justify-content: center; gap: 8px;
}
.login-btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
.login-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.spinner {
  width: 20px; height: 20px;
  border: 2px solid rgba(255,255,255,0.3); border-top-color: white;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.demo-box {
  margin-top: 28px; padding: 16px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08); border-radius: 12px;
}
.demo-title { color: #64748b; font-size: 12px; margin: 0 0 12px; text-align: center; }
.demo-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 12px; border-radius: 8px; cursor: pointer;
  transition: background 0.15s; margin-bottom: 6px;
}
.demo-item:hover { background: rgba(99,102,241,0.15); }
.demo-item:last-child { margin-bottom: 0; }
.demo-role { color: #94a3b8; font-size: 13px; font-weight: 600; }
.demo-email { color: #6366f1; font-size: 12px; direction: ltr; }
</style>
