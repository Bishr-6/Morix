<template>
  <div class="hub">
    <aside :class="['sidebar',{collapsed:sb}]">
      <div class="sb-header" @click="sb=!sb">
        <div class="brand"><div class="b-icon">M</div><span v-if="!sb" class="b-name">Morix Owner</span></div>
      </div>
      <nav class="sb-nav">
        <button v-for="s in sections" :key="s.id" :class="['nav-item',{active:cur===s.id}]" @click="cur=s.id">
          <span>{{ s.icon }}</span><span v-if="!sb">{{ s.label }}</span>
        </button>
        <div style="height:1px;background:rgba(255,255,255,.08);margin:8px 4px"></div>
        <div style="padding:8px 12px;color:rgba(255,255,255,.3);font-size:11px" v-if="!sb">وصول كامل</div>
        <button v-for="s in otherSections" :key="s.path" class="nav-item" @click="router.push(s.path)">
          <span>{{ s.icon }}</span><span v-if="!sb">{{ s.label }}</span>
        </button>
      </nav>
      <div class="sb-footer">
        <button class="logout-btn" @click="doLogout"><span>🚪</span><span v-if="!sb">خروج</span></button>
      </div>
    </aside>

    <main class="main">
      <header class="top-bar">
        <h2>{{ sections.find(s=>s.id===cur)?.label || 'لوحة المالك' }}</h2>
        <div class="chip"><div class="av">👑</div><span>المالك</span></div>
      </header>

      <!-- ===== PLATFORM OVERVIEW ===== -->
      <section v-show="cur==='overview'" class="body pad">
        <div class="stats-grid" v-if="stats">
          <div class="sc"><div class="sn">{{ stats.total_schools }}</div><div class="sl">مدارس</div></div>
          <div class="sc"><div class="sn">{{ stats.total_users }}</div><div class="sl">مستخدمون</div></div>
          <div class="sc"><div class="sn">{{ stats.role_counts?.student||0 }}</div><div class="sl">طلاب</div></div>
          <div class="sc"><div class="sn">{{ stats.role_counts?.teacher||0 }}</div><div class="sl">معلمون</div></div>
          <div class="sc"><div class="sn">{{ stats.total_conversations }}</div><div class="sl">محادثات AI</div></div>
          <div class="sc warn"><div class="sn">{{ stats.complaint_stats?.pending||0 }}</div><div class="sl">شكاوى معلقة</div></div>
        </div>

        <div class="card mt" v-if="stats?.schools?.length">
          <h3>🏫 المدارس</h3>
          <div class="list-col">
            <div v-for="sch in stats.schools" :key="sch.id" class="list-item">
              <div style="flex:1"><h4>{{ sch.name }}</h4></div>
              <span :class="sch.setup_completed ? 'badge-ok' : 'badge-warn'">
                {{ sch.setup_completed ? '✅ جاهزة' : '⚠️ غير مكتملة' }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== COMPLAINTS ===== -->
      <section v-show="cur==='complaints'" class="body pad">
        <div class="card">
          <h3>📣 الشكاوى والاقتراحات</h3>
          <div v-if="complaintsLoading" class="empty">⏳ تحميل...</div>
          <div v-else-if="!complaints.length" class="empty">لا توجد شكاوى</div>
          <div v-else class="list-col">
            <div v-for="c in complaints" :key="c.id" class="complaint-item">
              <div class="cpl-header">
                <div class="cpl-meta">
                  <span :class="['type-badge', c.type]">{{ {complaint:'شكوى',suggestion:'اقتراح',bug:'مشكلة'}[c.type] }}</span>
                  <span style="color:var(--t2);font-size:12px">{{ c.users?.full_name }}</span>
                  <span style="color:var(--t2);font-size:12px">{{ fmtDate(c.created_at) }}</span>
                  <span :class="['status-badge', c.status]">{{ {pending:'معلق',reviewed:'قيد المراجعة',resolved:'محلول'}[c.status] }}</span>
                </div>
              </div>
              <h4>{{ c.title }}</h4>
              <p style="color:var(--t2);font-size:13px">{{ c.content }}</p>
              <div v-if="respondingTo === c.id" class="respond-form">
                <select v-model="respondStatus" class="inp sm">
                  <option value="reviewed">قيد المراجعة</option>
                  <option value="resolved">محلول</option>
                </select>
                <textarea v-model="respondText" class="inp" rows="3" placeholder="ردك..."></textarea>
                <div class="row-gap">
                  <button class="btn-p" @click="sendResponse(c.id)">إرسال الرد</button>
                  <button class="btn-o" @click="respondingTo=null">إلغاء</button>
                </div>
              </div>
              <div v-else-if="c.response" class="response-box">
                <p style="color:var(--t2);font-size:12px">رد المالك:</p>
                <p style="font-size:13px">{{ c.response }}</p>
              </div>
              <button v-if="respondingTo!==c.id" class="btn-s" style="margin-top:10px" @click="respondingTo=c.id;respondText=c.response||'';respondStatus=c.status">رد</button>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 💓 PULSE ===== -->
      <section v-show="cur==='pulse'" class="body pad">
        <div class="card">
          <h3>💓 نبض المنصة لحظياً</h3>
          <button class="btn-p" @click="loadPulse" :disabled="pulseLoading">{{ pulseLoading?'⏳':'🔄 تحديث' }}</button>
          <div v-if="pulse" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-top:16px">
            <div class="card"><b>👥 إجمالي المستخدمين</b><div style="font-size:32px;color:var(--accent)">{{ pulse.total_users }}</div></div>
            <div class="card"><b>🟢 نشط اليوم</b><div style="font-size:32px;color:#10b981">{{ pulse.active_today }}</div></div>
            <div class="card"><b>📅 نشط هذا الأسبوع</b><div style="font-size:32px;color:#10b981">{{ pulse.active_this_week }}</div></div>
            <div class="card"><b>🤖 استدعاءات AI</b><div style="font-size:32px;color:#a855f7">{{ pulse.ai_calls_week }}</div></div>
            <div class="card"><b>📣 شكاوى مفتوحة</b><div style="font-size:32px;color:#ef4444">{{ pulse.open_complaints }}</div></div>
            <div class="card"><b>💪 درجة الصحة</b><div style="font-size:32px;color:#fbbf24">{{ pulse.health_score }}/100</div></div>
          </div>
        </div>
      </section>

      <!-- ===== 💰 AI COST ===== -->
      <section v-show="cur==='aicost'" class="body pad">
        <div class="card">
          <h3>💰 تقدير تكلفة AI</h3>
          <button class="btn-p" @click="loadAiCost" :disabled="aiCostLoading">{{ aiCostLoading?'⏳':'📊 احسب' }}</button>
          <div v-if="aiCost" style="margin-top:16px;display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px">
            <div class="card"><b>📞 الاستدعاءات هذا الأسبوع</b><div style="font-size:28px;color:var(--accent)">{{ aiCost.calls_this_week }}</div></div>
            <div class="card"><b>💵 التكلفة الأسبوعية</b><div style="font-size:28px;color:#10b981">${{ aiCost.estimated_cost_usd }}</div></div>
            <div class="card"><b>📅 تقدير شهري</b><div style="font-size:28px;color:#fbbf24">${{ aiCost.estimated_monthly_cost }}</div></div>
            <div class="card"><b>♻️ توفير من الكاش</b><div style="font-size:18px;color:#10b981">{{ aiCost.savings_from_cache }}</div></div>
          </div>
        </div>
      </section>

      <!-- ===== ⚠️ CHURN ===== -->
      <section v-show="cur==='churn'" class="body pad">
        <div class="card">
          <h3>⚠️ مخاطر إلغاء اشتراك المدارس</h3>
          <button class="btn-p" @click="loadChurn" :disabled="churnLoading">{{ churnLoading?'⏳':'🔍 تحليل' }}</button>
          <div v-if="churn" style="margin-top:16px">
            <div v-if="!churn.at_risk_schools?.length" style="color:#10b981">✅ لا توجد مدارس في خطر الإلغاء حالياً</div>
            <div v-for="s in (churn.at_risk_schools||[])" :key="s.school_id" class="card" :style="{margin:'8px 0',borderRight:`4px solid ${s.risk_level==='high'?'#ef4444':'#fbbf24'}`}">
              <h4>{{ s.school_name }}</h4>
              <p>نسبة عدم النشاط: <b style="color:#ef4444">{{ s.inactive_pct }}%</b></p>
              <p>مستوى الخطر: <span :style="{color:s.risk_level==='high'?'#ef4444':'#fbbf24'}">{{ s.risk_level==='high'?'🔴 عالي':'🟡 متوسط' }}</span></p>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 📢 BROADCAST ===== -->
      <section v-show="cur==='broadcast'" class="body pad">
        <div class="card">
          <h3>📢 بث رسالة لكل المنصة</h3>
          <input v-model="bcTitle" class="inp" placeholder="عنوان الإعلان" style="width:100%;margin-bottom:8px" />
          <textarea v-model="bcContent" class="inp" rows="5" placeholder="محتوى الرسالة..." style="width:100%;margin-bottom:8px"></textarea>
          <button class="btn-p" @click="sendBroadcast" :disabled="bcLoading">{{ bcLoading?'⏳':'📡 بث الآن' }}</button>
          <div v-if="bcMsg" style="margin-top:12px;color:#10b981">{{ bcMsg }}</div>
        </div>
      </section>

      <!-- ===== USERS ===== -->
      <section v-show="cur==='users'" class="body pad">
        <div class="card">
          <div class="row-sb">
            <h3>👥 كل المستخدمين</h3>
            <input v-model="userSearch" class="inp" style="width:200px" placeholder="بحث..." />
          </div>
          <div v-if="usersLoading" class="empty">⏳ تحميل...</div>
          <div v-else class="list-col">
            <div v-for="u in filteredUsers" :key="u.id" class="list-item">
              <div style="flex:1">
                <h4>{{ u.full_name }}</h4>
                <div class="meta">
                  <span class="role-tag" :class="u.role">{{ {manager:'مدير',admin:'إداري',teacher:'معلم',student:'طالب'}[u.role]||u.role }}</span>
                  <span style="color:var(--t2);font-size:12px">{{ u.email }}</span>
                  <span v-if="u.schools" style="color:var(--t2);font-size:12px">🏫 {{ u.schools?.name }}</span>
                </div>
              </div>
              <div style="display:flex;align-items:center;gap:10px">
                <span :class="u.is_active?'badge-ok':'badge-warn'" style="font-size:12px">{{ u.is_active?'نشط':'معطل' }}</span>
                <button class="btn-s" @click="toggleUser(u.id)">{{ u.is_active?'تعطيل':'تفعيل' }}</button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import { useRouter } from 'vue-router'
import { ownerAPI } from '../api.js'

const auth = useAuthStore()
const router = useRouter()

const sections = [
  {id:'overview',icon:'📊',label:'نظرة عامة'},
  {id:'pulse',icon:'💓',label:'نبض المنصة'},
  {id:'aicost',icon:'💰',label:'تكلفة AI'},
  {id:'churn',icon:'⚠️',label:'مخاطر الإلغاء'},
  {id:'broadcast',icon:'📢',label:'بث رسالة'},
  {id:'complaints',icon:'📣',label:'الشكاوى'},
  {id:'users',icon:'👥',label:'كل المستخدمين'},
]
const otherSections = [
  {path:'/manager',icon:'🏫',label:'لوحة المدير'},
  {path:'/admin',icon:'🛡️',label:'لوحة المشرف الإداري'},
  {path:'/teacher',icon:'👨‍🏫',label:'لوحة المعلم'},
  {path:'/student',icon:'👨‍🎓',label:'لوحة الطالب'},
]

const cur = ref('overview')
const sb = ref(false)
const stats = ref(null)
const complaints = ref([])
const complaintsLoading = ref(false)
const users = ref([])
const usersLoading = ref(false)
const userSearch = ref('')
const respondingTo = ref(null)
const respondText = ref('')
const respondStatus = ref('reviewed')

const filteredUsers = computed(() => {
  if (!userSearch.value) return users.value
  const q = userSearch.value.toLowerCase()
  return users.value.filter(u => u.full_name?.toLowerCase().includes(q) || u.email?.toLowerCase().includes(q))
})

onMounted(async () => {
  try { stats.value=(await ownerAPI.getStats()).data } catch {}
  complaintsLoading.value=true
  try { complaints.value=(await ownerAPI.getComplaints()).data } catch {}
  finally { complaintsLoading.value=false }
  usersLoading.value=true
  try { users.value=(await ownerAPI.getUsers()).data } catch {}
  finally { usersLoading.value=false }
})

async function sendResponse(id) {
  try {
    await ownerAPI.respondComplaint(id, { status:respondStatus.value, response:respondText.value })
    const c = complaints.value.find(c=>c.id===id)
    if (c) { c.status=respondStatus.value; c.response=respondText.value }
    respondingTo.value=null
  } catch {}
}

async function toggleUser(id) {
  try {
    const r=await ownerAPI.toggleUser(id)
    const u=users.value.find(u=>u.id===id)
    if(u) u.is_active=r.data.is_active
  } catch {}
}

async function doLogout() { await auth.logout(); router.push('/login') }
function fmtDate(d) { return d?new Date(d).toLocaleDateString('ar-SA'):'' }

// 👑 ميزات المالك المتقدمة
const pulse = ref(null), pulseLoading = ref(false)
async function loadPulse() { pulseLoading.value=true; try { pulse.value=(await ownerAPI.platformPulse()).data } catch(e){alert('فشل')} pulseLoading.value=false }
const aiCost = ref(null), aiCostLoading = ref(false)
async function loadAiCost() { aiCostLoading.value=true; try { aiCost.value=(await ownerAPI.aiCost()).data } catch(e){alert('فشل')} aiCostLoading.value=false }
const churn = ref(null), churnLoading = ref(false)
async function loadChurn() { churnLoading.value=true; try { churn.value=(await ownerAPI.churnRisk()).data } catch(e){alert('فشل')} churnLoading.value=false }
const bcTitle = ref(''), bcContent = ref(''), bcLoading = ref(false), bcMsg = ref('')
async function sendBroadcast() {
  if (!bcContent.value.trim()) return alert('اكتب محتوى الرسالة')
  bcLoading.value=true; bcMsg.value=''
  try { const r = await ownerAPI.broadcast({title:bcTitle.value,content:bcContent.value}); bcMsg.value=r.data.message; bcTitle.value=''; bcContent.value='' }
  catch(e){alert('فشل')} bcLoading.value=false
}
</script>

<style scoped>
.hub{display:flex;height:100vh;overflow:hidden;font-family:'Segoe UI','Cairo',sans-serif;direction:rtl;--bg1:#0f172a;--bg2:#1e293b;--bg3:#334155;--text:#f1f5f9;--t2:#94a3b8;--accent:#a855f7;--border:rgba(255,255,255,.08);--card:rgba(255,255,255,.05);}
.sidebar{width:220px;min-width:220px;background:var(--bg2);border-left:1px solid var(--border);display:flex;flex-direction:column;transition:width .25s,min-width .25s;overflow:hidden;}
.sidebar.collapsed{width:60px;min-width:60px;}
.sb-header{padding:14px;cursor:pointer;border-bottom:1px solid var(--border);}
.brand{display:flex;align-items:center;gap:10px;}
.b-icon{width:34px;height:34px;min-width:34px;background:linear-gradient(135deg,#a855f7,#7c3aed);border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:18px;}
.b-name{font-size:15px;font-weight:800;color:var(--text);}
.sb-nav{flex:1;padding:8px;overflow-y:auto;}
.nav-item{display:flex;align-items:center;gap:10px;width:100%;padding:10px 12px;border-radius:10px;background:none;border:none;color:var(--t2);cursor:pointer;font-size:13px;transition:all .15s;text-align:right;white-space:nowrap;}
.nav-item:hover{background:rgba(168,85,247,.1);color:var(--text);}
.nav-item.active{background:rgba(168,85,247,.2);color:var(--accent);}
.sb-footer{padding:12px;border-top:1px solid var(--border);}
.logout-btn{display:flex;align-items:center;justify-content:center;gap:8px;background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.2);color:#f87171;border-radius:8px;padding:8px;cursor:pointer;font-size:13px;width:100%;}
.main{flex:1;display:flex;flex-direction:column;background:var(--bg1);overflow:hidden;}
.top-bar{display:flex;align-items:center;justify-content:space-between;padding:14px 24px;border-bottom:1px solid var(--border);background:var(--bg2);}
.top-bar h2{color:var(--text);margin:0;font-size:17px;}
.chip{display:flex;align-items:center;gap:10px;color:var(--t2);font-size:14px;}
.av{width:32px;height:32px;background:linear-gradient(135deg,#a855f7,#7c3aed);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;}
.body{flex:1;overflow-y:auto;}.body.pad{padding:24px;}
.card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:24px;}.card h3{color:var(--text);margin:0 0 20px;font-size:16px;}
.mt{margin-top:16px;}
.stats-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:16px;}
.sc{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px;text-align:center;}
.sc.warn{border-color:rgba(234,179,8,.3);background:rgba(234,179,8,.05);}
.sn{font-size:24px;font-weight:800;color:var(--text);margin-bottom:4px;}
.sl{color:var(--t2);font-size:12px;}
.row-sb{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;}
.row-gap{display:flex;gap:10px;flex-wrap:wrap;}
.list-col{display:flex;flex-direction:column;gap:10px;}
.list-item{display:flex;align-items:center;justify-content:space-between;padding:14px;background:var(--bg2);border:1px solid var(--border);border-radius:12px;}
.list-item h4{color:var(--text);margin:0 0 4px;}
.meta{display:flex;gap:8px;flex-wrap:wrap;align-items:center;}
.badge-ok{background:rgba(34,197,94,.15);color:#4ade80;border-radius:6px;padding:3px 8px;font-size:12px;}
.badge-warn{background:rgba(234,179,8,.15);color:#facc15;border-radius:6px;padding:3px 8px;font-size:12px;}
.complaint-item{padding:16px;background:var(--bg2);border:1px solid var(--border);border-radius:12px;margin-bottom:10px;}
.cpl-header{margin-bottom:10px;}
.cpl-meta{display:flex;gap:8px;flex-wrap:wrap;align-items:center;}
.complaint-item h4{color:var(--text);margin:0 0 6px;}
.type-badge{border-radius:6px;padding:2px 8px;font-size:11px;}
.type-badge.complaint{background:rgba(239,68,68,.15);color:#f87171;}
.type-badge.suggestion{background:rgba(34,197,94,.15);color:#4ade80;}
.type-badge.bug{background:rgba(234,179,8,.15);color:#facc15;}
.status-badge{border-radius:6px;padding:2px 8px;font-size:11px;}
.status-badge.pending{background:rgba(234,179,8,.15);color:#facc15;}
.status-badge.reviewed{background:rgba(99,102,241,.15);color:#818cf8;}
.status-badge.resolved{background:rgba(34,197,94,.15);color:#4ade80;}
.respond-form{margin-top:12px;display:flex;flex-direction:column;gap:10px;}
.response-box{margin-top:10px;padding:12px;background:rgba(99,102,241,.08);border:1px solid rgba(99,102,241,.2);border-radius:8px;}
.role-tag{border-radius:5px;padding:2px 7px;font-size:11px;}
.role-tag.manager{background:rgba(239,68,68,.15);color:#f87171;}
.role-tag.teacher{background:rgba(99,102,241,.15);color:#818cf8;}
.role-tag.student{background:rgba(34,197,94,.15);color:#4ade80;}
.role-tag.admin{background:rgba(234,179,8,.15);color:#facc15;}
.empty{text-align:center;padding:40px;color:var(--t2);font-size:14px;}
.inp{width:100%;box-sizing:border-box;background:var(--bg2);border:1px solid var(--border);color:var(--text);border-radius:10px;padding:12px 14px;font-size:14px;font-family:inherit;text-align:right;}
.inp.sm{padding:8px 12px;font-size:13px;}
.inp:focus{outline:none;border-color:var(--accent);}
select.inp{cursor:pointer;}textarea.inp{resize:vertical;}
.btn-p{background:var(--accent);color:#fff;border:none;border-radius:10px;padding:11px 18px;cursor:pointer;font-size:14px;font-weight:600;}
.btn-p:hover:not(:disabled){opacity:.88;}
.btn-o{background:transparent;border:1px solid var(--border);color:var(--t2);border-radius:10px;padding:11px 18px;cursor:pointer;font-size:14px;}
.btn-o:hover{border-color:var(--accent);color:var(--accent);}
.btn-s{background:var(--bg3);border:1px solid var(--border);color:var(--t2);border-radius:8px;padding:7px 12px;cursor:pointer;font-size:12px;}
.btn-s:hover{border-color:var(--accent);color:var(--accent);}
@media(max-width:768px){.sidebar{display:none}.stats-grid{grid-template-columns:1fr 1fr}}
</style>
