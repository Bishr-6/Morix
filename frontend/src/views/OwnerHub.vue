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
