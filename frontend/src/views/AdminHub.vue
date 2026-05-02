<template>
  <div class="hub">
    <!-- Mobile menu -->
    <button class="mobile-toggle" @click="mobileOpen = !mobileOpen" aria-label="Menu">{{ mobileOpen ? '✕' : '☰' }}</button>
    <div :class="['mobile-overlay', { open: mobileOpen }]" @click="mobileOpen = false"></div>

    <aside :class="['sidebar',{collapsed:sb, open: mobileOpen}]">
      <div class="sb-header" @click="sb=!sb">
        <div class="brand"><div class="b-icon">M</div><span v-if="!sb" class="b-name">Morix</span></div>
      </div>
      <nav class="sb-nav">
        <button v-for="s in sections" :key="s.id" :class="['nav-item',{active:cur===s.id}]" @click="cur=s.id; mobileOpen=false" :title="s.label">
          <span>{{ s.icon }}</span><span v-if="!sb" class="nav-label">{{ s.label }}</span>
        </button>
      </nav>
      <div class="sb-footer">
        <button class="logout-btn" @click="doLogout"><span>🚪</span><span v-if="!sb">خروج</span></button>
      </div>
    </aside>

    <main class="main">
      <header class="top-bar">
        <h2>{{ sections.find(s=>s.id===cur)?.label }}</h2>
        <div class="chip">
          <img v-if="settings.avatar_url" :src="settings.avatar_url" class="av-img" />
          <div v-else class="av">{{ firstName[0] }}</div>
          <span>{{ firstName }}</span>
        </div>
      </header>

      <!-- ===== OVERVIEW ===== -->
      <section v-show="cur==='overview'" class="body pad">
        <div class="stats-grid">
          <div class="sc"><div class="sn">{{ stats.total_students }}</div><div class="sl">طالب</div></div>
          <div class="sc"><div class="sn">{{ stats.total_teachers }}</div><div class="sl">معلم</div></div>
          <div class="sc"><div class="sn">{{ stats.total_homework }}</div><div class="sl">واجب</div></div>
          <div class="sc"><div class="sn">{{ stats.total_tests }}</div><div class="sl">اختبار</div></div>
        </div>
        <div class="card mt">
          <h3>👋 مرحباً {{ firstName }}!</h3>
          <p style="color:var(--t2)">لوحة المشرف الإداري — يمكنك إدارة الطلاب وتحميل الحسابات من هنا.</p>
        </div>
      </section>

      <!-- ===== STUDENTS ===== -->
      <section v-show="cur==='students'" class="body pad">
        <div class="card">
          <div class="row-sb">
            <h3>👨‍🎓 الطلاب</h3>
            <input v-model="search" class="inp search" placeholder="🔍 بحث..." />
          </div>
          <div v-if="loading" class="empty">⏳ تحميل...</div>
          <div v-else-if="!filteredStudents.length" class="empty">لا يوجد طلاب</div>
          <div v-else class="list-col">
            <div v-for="s in filteredStudents" :key="s.id" class="list-item">
              <div style="flex:1">
                <h4>{{ s.full_name }}</h4>
                <div class="meta">
                  <span>{{ s.email }}</span>
                  <span v-if="s.grade">🎓 {{ s.grade }}</span>
                  <span :style="{color:s.is_active?'#4ade80':'#f87171'}">{{ s.is_active ? '✅ فعّال' : '❌ معطل' }}</span>
                </div>
              </div>
              <div class="row-gap">
                <button class="btn-s" @click="openReset(s)">🔑 كلمة المرور</button>
                <button class="btn-s" :class="{danger:s.is_active}" @click="toggleStudent(s)">
                  {{ s.is_active ? 'تعطيل' : 'تفعيل' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Reset Password Modal -->
        <div v-if="resetModal" class="modal-bg" @click.self="resetModal=null">
          <div class="modal-box">
            <h3>🔑 إعادة تعيين كلمة مرور</h3>
            <p style="color:var(--t2);font-size:14px;margin:0 0 16px">{{ resetModal.full_name }}</p>
            <input v-model="newPass" type="text" class="inp" placeholder="كلمة المرور الجديدة (6+ أحرف)" />
            <div class="row-gap" style="margin-top:14px">
              <button class="btn-p" @click="doReset" :disabled="newPass.length<6">حفظ</button>
              <button class="btn-o" @click="resetModal=null">إلغاء</button>
            </div>
            <p v-if="resetMsg" :style="{color:resetMsg.includes('✅')?'#4ade80':'#f87171',fontSize:'13px',marginTop:'10px'}">{{ resetMsg }}</p>
          </div>
        </div>
      </section>

      <!-- ===== UPLOAD EXCEL ===== -->
      <section v-show="cur==='upload'" class="body pad">
        <div class="card">
          <h3>📊 رفع ملف Excel لإنشاء الحسابات</h3>
          <div class="info-box">
            <p>📋 <strong>تنسيق الملف المطلوب:</strong></p>
            <p>• <strong>Sheet "طلاب" أو "Students":</strong> الاسم | الرقم الوزاري | الصف</p>
            <p>• <strong>Sheet "معلمون" أو "Teachers":</strong> الاسم | المادة (اختياري)</p>
          </div>
          <div class="col-gap" style="margin-top:20px">
            <input type="file" ref="fileInput" accept=".xlsx,.xls" @change="onFileSelect" class="file-input" />
            <div v-if="selectedFile" class="file-chip">
              📄 {{ selectedFile.name }}
              <button @click="selectedFile=null;fileInput.value=''" style="background:none;border:none;cursor:pointer;color:var(--t2)">✕</button>
            </div>
            <button class="btn-p" @click="uploadFile" :disabled="!selectedFile||uploading">
              {{ uploading ? '⏳ جاري الرفع...' : '⬆️ رفع وإنشاء الحسابات' }}
            </button>
          </div>
          <div v-if="uploadError" style="color:#f87171;font-size:13px;margin-top:12px">{{ uploadError }}</div>
        </div>

        <!-- نتائج الرفع -->
        <div v-if="uploadResult" class="card mt">
          <h3>✅ تم إنشاء {{ uploadResult.total }} حساب</h3>
          <p style="color:var(--t2);font-size:13px;margin:0 0 16px">طلاب: {{ uploadResult.students }} | معلمون: {{ uploadResult.teachers }}</p>
          <div class="list-col">
            <div v-for="acc in uploadResult.accounts" :key="acc.email" class="list-item">
              <div style="flex:1">
                <h4>{{ acc.full_name }}</h4>
                <div class="meta"><span>{{ acc.email }}</span><span>{{ {student:'طالب',teacher:'معلم',admin:'إداري'}[acc.role]||acc.role }}</span></div>
              </div>
              <div class="pass-badge">{{ acc.password }}</div>
            </div>
          </div>
          <button class="btn-s" style="margin-top:14px" @click="copyAccounts">📋 نسخ كل الحسابات</button>
        </div>
      </section>

      <!-- ===== 💓 SCHOOL PULSE ===== -->
      <section v-show="cur==='pulse'" class="body pad">
        <div class="card">
          <h3>💓 نبض المدرسة</h3>
          <button class="btn-p" @click="loadPulse" :disabled="pulseLoading">{{ pulseLoading?'⏳':'🔄 تحديث' }}</button>
          <div v-if="pulse" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-top:16px">
            <div class="card"><b>👨‍🎓 الطلاب</b><div style="font-size:32px;color:var(--accent)">{{ pulse.students }}</div></div>
            <div class="card"><b>👨‍🏫 المعلمون</b><div style="font-size:32px;color:#a855f7">{{ pulse.teachers }}</div></div>
            <div class="card"><b>🟢 نشط اليوم</b><div style="font-size:32px;color:#10b981">{{ pulse.active_today }}</div></div>
            <div class="card"><b>📅 نشط أسبوعياً</b><div style="font-size:32px;color:#10b981">{{ pulse.active_week }}</div></div>
            <div class="card"><b>🤖 استدعاءات AI</b><div style="font-size:32px;color:#fbbf24">{{ pulse.ai_calls_week }}</div></div>
            <div class="card"><b>💪 التفاعل</b><div style="font-size:32px;color:#fbbf24">{{ pulse.engagement_pct }}%</div></div>
          </div>
        </div>
      </section>

      <!-- ===== 📢 ANNOUNCEMENTS ===== -->
      <section v-show="cur==='announce'" class="body pad">
        <div class="card">
          <h3>📢 إعلانات المدرسة</h3>
          <input v-model="annTitle" class="inp" placeholder="عنوان الإعلان" style="width:100%;margin-bottom:8px" />
          <textarea v-model="annContent" class="inp" rows="4" placeholder="محتوى الإعلان..." style="width:100%;margin-bottom:8px"></textarea>
          <button class="btn-p" @click="postAnnouncement" :disabled="annLoading">{{ annLoading?'⏳':'📡 نشر' }}</button>
          <div v-if="annMsg" style="margin-top:12px;color:#10b981">{{ annMsg }}</div>
          <h4 style="margin-top:24px">📜 السابقة</h4>
          <button class="btn-s" @click="loadAnnouncements">🔄 تحميل</button>
          <div v-for="(a,i) in announcements" :key="i" class="card" style="margin:8px 0">
            <b>{{ a.event_data?.title }}</b>
            <p style="color:var(--t2);font-size:12px">{{ new Date(a.created_at).toLocaleString('ar') }}</p>
            <p>{{ a.event_data?.content }}</p>
          </div>
        </div>
      </section>

      <!-- ===== 📋 INCIDENT REPORT ===== -->
      <section v-show="cur==='incident'" class="body pad">
        <div class="card">
          <h3>📋 مساعد كتابة تقارير الحوادث (AI)</h3>
          <select v-model="incType" class="inp" style="width:100%;margin-bottom:8px">
            <option value="سلوكي">تقرير سلوكي</option>
            <option value="أكاديمي">تقرير أكاديمي</option>
            <option value="حادثة">حادثة</option>
            <option value="إصابة">إصابة</option>
          </select>
          <textarea v-model="incSummary" class="inp" rows="5" placeholder="ملخص الموقف بكلمات بسيطة..." style="width:100%;margin-bottom:8px"></textarea>
          <button class="btn-p" @click="genIncident" :disabled="incLoading">{{ incLoading?'⏳':'✍️ ولّد التقرير' }}</button>
          <div v-if="incReport" class="card" style="margin-top:16px;white-space:pre-wrap;line-height:1.8">{{ incReport }}</div>
        </div>
      </section>

      <!-- ===== SETTINGS ===== -->
      <section v-show="cur==='settings'" class="body pad">
        <div class="settings-grid">
          <!-- معلومات الحساب -->
          <div class="card">
            <h3>👤 معلومات الحساب</h3>
            <div class="avatar-section">
              <div style="position:relative;cursor:pointer" @click="adminAvatarInput?.click()">
                <img v-if="settings.avatar_url" :src="settings.avatar_url" class="av-preview" />
                <div v-else class="av-big">{{ firstName[0] }}</div>
                <div class="av-overlay">📷</div>
              </div>
              <div style="flex:1">
                <p style="color:var(--t2);font-size:12px;margin:0 0 6px">اضغط على الصورة لرفع صورة من جهازك</p>
                <input ref="adminAvatarInput" type="file" accept="image/*" style="display:none" @change="onAdminAvatarUpload" />
                <button class="btn-s" style="width:100%" @click="adminAvatarInput?.click()">📷 رفع صورة من الجهاز</button>
              </div>
            </div>
            <div class="info-row"><span>الاسم</span><b>{{ settings.full_name }}</b></div>
            <div class="info-row"><span>الإيميل</span><b>{{ settings.email }}</b></div>
            <div class="info-row"><span>الدور</span><b>مشرف إداري</b></div>
          </div>

          <!-- المظهر -->
          <div class="card">
            <h3>🎨 المظهر</h3>
            <p style="color:var(--t2);font-size:13px;margin:0 0 10px">الثيم</p>
            <div class="theme-row">
              <button :class="['t-btn',{active:settings.theme==='dark'}]" @click="setTheme('dark')">🌑 داكن</button>
              <button :class="['t-btn',{active:settings.theme==='light'}]" @click="setTheme('light')">☀️ فاتح</button>
              <button :class="['t-btn',{active:settings.theme==='library'}]" @click="setTheme('library')">📚 مكتبة</button>
            </div>
            <p style="color:var(--t2);font-size:13px;margin:16px 0 8px">السطوع {{ settings.brightness }}%</p>
            <input type="range" v-model.number="settings.brightness" min="40" max="100" step="5" @change="saveSettings" style="width:100%;accent-color:var(--accent)" />
          </div>

          <!-- اللغة -->
          <div class="card">
            <h3>🌐 اللغة</h3>
            <select v-model="settings.language" @change="saveSettings" class="inp">
              <option value="ar">العربية</option>
              <option value="en">English</option>
            </select>
          </div>

          <!-- الإشعارات -->
          <div class="card">
            <h3>🔔 الإشعارات</h3>
            <label class="toggle-lbl">
              <input type="checkbox" v-model="settings.notifications_enabled" @change="saveSettings" />
              <span>تفعيل الإشعارات</span>
            </label>
          </div>
        </div>
        <p v-if="settingsMsg" style="color:#4ade80;font-size:13px;margin-top:10px;text-align:center">{{ settingsMsg }}</p>
      </section>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import { useRouter } from 'vue-router'
import { adminAPI } from '../api.js'
import { useTheme } from '../composables/useTheme.js'

const auth = useAuthStore()
const router = useRouter()
const firstName = computed(() => (auth.user?.full_name || 'مشرف').split(' ')[0])

const sections = [
  { id:'overview', icon:'🏠', label:'نظرة عامة' },
  { id:'students', icon:'👨‍🎓', label:'الطلاب' },
  { id:'upload',   icon:'📊', label:'رفع Excel' },
  { id:'pulse',    icon:'💓', label:'نبض المدرسة' },
  { id:'announce', icon:'📢', label:'الإعلانات' },
  { id:'incident', icon:'📋', label:'تقرير حادثة AI' },
  { id:'settings', icon:'⚙️', label:'الإعدادات' },
]

const cur = ref('overview')
const sb = ref(false)
const mobileOpen = ref(false)

// Overview
const stats = ref({ total_students:0, total_teachers:0, total_homework:0, total_tests:0 })

// Students
const students = ref([])
const loading = ref(false)
const search = ref('')
const filteredStudents = computed(() =>
  search.value ? students.value.filter(s =>
    s.full_name?.includes(search.value) || s.email?.includes(search.value)
  ) : students.value
)

// Reset Password
const resetModal = ref(null)
const newPass = ref('')
const resetMsg = ref('')

// Upload
const fileInput = ref(null)
const selectedFile = ref(null)
const uploading = ref(false)
const uploadResult = ref(null)
const uploadError = ref('')

// Settings
const settings = ref({ theme:'dark', brightness:100, language:'ar', notifications_enabled:true, avatar_url:'', email:'', full_name:'' })
useTheme(settings)
const settingsMsg = ref('')
const adminAvatarInput = ref(null)

onMounted(async () => {
  await Promise.all([loadStats(), loadStudents(), loadSettings()])
})

async function loadStats() {
  try { stats.value = (await adminAPI.getOverview()).data } catch {}
}
async function loadStudents() {
  loading.value = true
  try { students.value = (await adminAPI.getStudents()).data } catch {}
  finally { loading.value = false }
}
async function loadSettings() {
  try { settings.value = { ...settings.value, ...(await adminAPI.getSettings()).data } } catch {}
}

function openReset(student) { resetModal.value = student; newPass.value = ''; resetMsg.value = '' }
async function doReset() {
  try {
    await adminAPI.resetPassword(resetModal.value.id, newPass.value)
    resetMsg.value = `✅ تم تغيير كلمة المرور إلى: ${newPass.value}`
    const s = students.value.find(s => s.id === resetModal.value.id)
    if (s) s.must_change_password = false
  } catch (e) { resetMsg.value = e.response?.data?.detail || 'خطأ' }
}
async function toggleStudent(s) {
  try { const r = await adminAPI.toggleStudent(s.id); s.is_active = r.data.is_active } catch {}
}

function onFileSelect(e) { selectedFile.value = e.target.files[0] || null; uploadResult.value = null; uploadError.value = '' }
async function uploadFile() {
  if (!selectedFile.value) return
  uploading.value = true; uploadError.value = ''
  const fd = new FormData()
  fd.append('file', selectedFile.value)
  try {
    const r = await adminAPI.uploadExcel(fd)
    uploadResult.value = r.data
    await loadStudents()
  } catch (e) { uploadError.value = e.response?.data?.detail || 'فشل رفع الملف' }
  finally { uploading.value = false }
}
function copyAccounts() {
  if (!uploadResult.value) return
  const text = uploadResult.value.accounts.map(a => `${a.full_name} | ${a.email} | ${a.password}`).join('\n')
  navigator.clipboard.writeText(text)
}

function setTheme(t) { settings.value.theme = t; saveSettings() }
async function saveSettings() {
  try { await adminAPI.updateSettings(settings.value); settingsMsg.value = '✅ تم الحفظ'; setTimeout(()=>{settingsMsg.value=''}, 2000) } catch {}
}
async function onAdminAvatarUpload(e) {
  const file = e.target.files?.[0]; if(!file) return
  if(file.size > 500 * 1024) { alert('الصورة أكبر من 500 كيلوبايت — اختر صورة أصغر'); return }
  const reader = new FileReader()
  reader.onload = async (ev) => { settings.value.avatar_url = ev.target.result; await saveSettings() }
  reader.readAsDataURL(file)
  if(adminAvatarInput.value) adminAvatarInput.value.value = ''
}

async function doLogout() { await auth.logout(); router.push('/login') }

// 🏫 ميزات الإداري المتقدمة
const pulse = ref(null), pulseLoading = ref(false)
async function loadPulse() { pulseLoading.value=true; try { pulse.value=(await adminAPI.schoolPulse()).data } catch(e){alert('فشل')} pulseLoading.value=false }

const annTitle = ref(''), annContent = ref(''), annLoading = ref(false), annMsg = ref('')
const announcements = ref([])
async function postAnnouncement() {
  if (!annTitle.value.trim() || !annContent.value.trim()) return alert('أدخل العنوان والمحتوى')
  annLoading.value=true
  try {
    const r = await adminAPI.makeAnnouncement({title:annTitle.value, content:annContent.value})
    annMsg.value=r.data.message; annTitle.value=''; annContent.value=''
    await loadAnnouncements()
  } catch(e) { alert('فشل') }
  annLoading.value=false
}
async function loadAnnouncements() { try { announcements.value=(await adminAPI.listAnnouncements()).data } catch {} }

const incType = ref('سلوكي'), incSummary = ref(''), incLoading = ref(false), incReport = ref('')
async function genIncident() {
  if (!incSummary.value.trim()) return alert('اكتب الملخص')
  incLoading.value=true; incReport.value=''
  try { incReport.value=(await adminAPI.incidentReport({type:incType.value, summary:incSummary.value})).data.report }
  catch(e) { alert('فشل') }
  incLoading.value=false
}
</script>

<style scoped>
.hub{display:flex;height:100vh;overflow:hidden;font-family:'Segoe UI','Cairo',sans-serif;direction:rtl;--bg1:#0f172a;--bg2:#1e293b;--bg3:#334155;--text:#f1f5f9;--t2:#94a3b8;--accent:#6366f1;--border:rgba(255,255,255,.08);--card:rgba(255,255,255,.05);}
.sidebar{width:220px;min-width:220px;background:var(--bg2);border-left:1px solid var(--border);display:flex;flex-direction:column;transition:width .25s,min-width .25s;overflow:hidden;}
.sidebar.collapsed{width:60px;min-width:60px;}
.sb-header{padding:14px;cursor:pointer;border-bottom:1px solid var(--border);}
.brand{display:flex;align-items:center;gap:10px;}
.b-icon{width:34px;height:34px;min-width:34px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:9px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:17px;color:#fff;}
.b-name{font-size:17px;font-weight:800;color:var(--text);}
.sb-nav{flex:1;padding:8px;overflow-y:auto;}
.nav-item{display:flex;align-items:center;gap:10px;width:100%;padding:10px 12px;border-radius:10px;background:none;border:none;color:var(--t2);cursor:pointer;font-size:14px;transition:all .15s;text-align:right;white-space:nowrap;}
.nav-item:hover{background:rgba(99,102,241,.1);color:var(--text);}
.nav-item.active{background:rgba(99,102,241,.2);color:var(--accent);}
.nav-label{font-size:13px;}
.sb-footer{padding:12px;border-top:1px solid var(--border);}
.logout-btn{display:flex;align-items:center;justify-content:center;gap:8px;background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.2);color:#f87171;border-radius:8px;padding:8px;cursor:pointer;font-size:13px;width:100%;}
.main{flex:1;display:flex;flex-direction:column;background:var(--bg1);overflow:hidden;}
.top-bar{display:flex;align-items:center;justify-content:space-between;padding:14px 24px;border-bottom:1px solid var(--border);background:var(--bg2);}
.top-bar h2{color:var(--text);margin:0;font-size:17px;}
.chip{display:flex;align-items:center;gap:10px;color:var(--t2);font-size:14px;}
.av{width:32px;height:32px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;color:#fff;font-size:14px;}
.av-img{width:32px;height:32px;border-radius:50%;object-fit:cover;}
.body{flex:1;overflow-y:auto;}.body.pad{padding:24px;}
.card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:24px;}.card h3{color:var(--text);margin:0 0 20px;font-size:16px;}
.mt{margin-top:16px;}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:16px;}
.sc{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px;text-align:center;}
.sn{font-size:28px;font-weight:800;color:var(--text);margin-bottom:4px;}
.sl{color:var(--t2);font-size:12px;}
.row-sb{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;}
.row-gap{display:flex;gap:10px;flex-wrap:wrap;}
.col-gap{display:flex;flex-direction:column;gap:12px;}
.list-col{display:flex;flex-direction:column;gap:10px;}
.list-item{display:flex;align-items:center;justify-content:space-between;padding:14px;background:var(--bg2);border:1px solid var(--border);border-radius:12px;}
.list-item h4{color:var(--text);margin:0 0 4px;font-size:14px;}
.meta{display:flex;gap:10px;flex-wrap:wrap;}
.meta span{color:var(--t2);font-size:12px;}
.empty{text-align:center;padding:40px;color:var(--t2);font-size:14px;}
.inp{width:100%;box-sizing:border-box;background:var(--bg2);border:1px solid var(--border);color:var(--text);border-radius:10px;padding:12px 14px;font-size:14px;font-family:inherit;text-align:right;}
.inp:focus{outline:none;border-color:var(--accent);}
.search{width:240px;padding:9px 14px;}
.btn-p{background:var(--accent);color:#fff;border:none;border-radius:10px;padding:11px 18px;cursor:pointer;font-size:14px;font-weight:600;}
.btn-p:disabled{opacity:.5;cursor:not-allowed;}
.btn-o{background:transparent;border:1px solid var(--border);color:var(--t2);border-radius:10px;padding:11px 18px;cursor:pointer;font-size:14px;}
.btn-s{background:var(--bg3);border:1px solid var(--border);color:var(--t2);border-radius:8px;padding:7px 12px;cursor:pointer;font-size:12px;}
.btn-s.danger{background:rgba(239,68,68,.1);border-color:rgba(239,68,68,.3);color:#f87171;}
.modal-bg{position:fixed;inset:0;background:rgba(0,0,0,.6);display:flex;align-items:center;justify-content:center;z-index:100;}
.modal-box{background:var(--bg2);border:1px solid var(--border);border-radius:20px;padding:32px;width:90%;max-width:420px;}
.modal-box h3{color:var(--text);margin:0 0 12px;}
.info-box{background:rgba(99,102,241,.1);border:1px solid rgba(99,102,241,.2);border-radius:12px;padding:16px;}
.info-box p{color:var(--t2);font-size:13px;margin:4px 0;line-height:1.7;}
.file-input{background:var(--bg2);border:2px dashed var(--border);color:var(--text);border-radius:10px;padding:20px;cursor:pointer;font-size:13px;text-align:center;}
.file-chip{display:flex;align-items:center;justify-content:space-between;background:rgba(99,102,241,.1);border:1px solid rgba(99,102,241,.3);border-radius:10px;padding:10px 14px;color:var(--text);font-size:13px;}
.pass-badge{background:rgba(99,102,241,.15);border:1px solid rgba(99,102,241,.3);color:var(--accent);border-radius:8px;padding:4px 10px;font-size:13px;font-family:monospace;}
.settings-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;}
.avatar-section{display:flex;align-items:center;gap:14px;margin-bottom:16px;}
.av-preview{width:60px;height:60px;border-radius:50%;object-fit:cover;border:2px solid var(--border);}
.av-overlay{position:absolute;inset:0;border-radius:50%;background:rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;font-size:18px;opacity:0;transition:opacity .15s;}
.avatar-section>div:first-child:hover .av-overlay{opacity:1;}
.av-big{width:60px;height:60px;min-width:60px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:26px;color:#fff;}
.info-row{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--border);color:var(--t2);font-size:13px;}
.info-row b{color:var(--text);}
.theme-row{display:flex;gap:10px;flex-wrap:wrap;}
.t-btn{background:var(--bg3);border:1px solid var(--border);color:var(--t2);border-radius:10px;padding:9px 16px;cursor:pointer;font-size:13px;transition:all .15s;}
.t-btn.active{background:rgba(99,102,241,.2);border-color:var(--accent);color:var(--accent);}
.toggle-lbl{display:flex;align-items:center;gap:10px;cursor:pointer;color:var(--t2);font-size:14px;}
.toggle-lbl input{accent-color:var(--accent);width:18px;height:18px;}
@media(max-width:768px){.sidebar{display:none}.stats-grid{grid-template-columns:1fr 1fr}.settings-grid{grid-template-columns:1fr}}
</style>
