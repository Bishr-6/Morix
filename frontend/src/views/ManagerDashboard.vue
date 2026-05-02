<template>
  <div class="min-h-screen relative" style="background: linear-gradient(135deg, #0a0f2c 0%, #05060f 100%)">
    <Stars />

    <div class="relative z-10">
      <!-- الهيدر -->
      <header class="border-b px-3 md:px-6 py-3 md:py-4 flex items-center justify-between flex-wrap gap-2"
              style="border-color: #1a1f3a; background: rgba(11, 14, 31, 0.8); backdrop-filter: blur(10px)">
        <div class="flex items-center gap-2 md:gap-3 min-w-0">
          <div class="w-8 h-8 md:w-9 md:h-9 rounded-lg flex items-center justify-center flex-shrink-0"
               style="background: linear-gradient(135deg, #4a7eff, #8b5cf6)">
            <span class="text-white font-black text-sm">M</span>
          </div>
          <span class="font-black text-base md:text-xl gradient-text">Memorix</span>
          <span class="hidden sm:inline text-xs px-2 py-1 rounded-full" style="background: rgba(74,126,255,0.15); color: #4a7eff">
            لوحة الإدارة
          </span>
        </div>
        <div class="flex items-center gap-2 md:gap-3 min-w-0">
          <span class="text-xs md:text-sm truncate max-w-[100px] md:max-w-none" style="color: #94a3b8">{{ auth.user?.full_name }}</span>
          <button @click="handleLogout" class="text-xs md:text-sm px-3 md:px-4 py-1.5 md:py-2 rounded-lg transition-colors"
                  style="background: rgba(239,68,68,0.1); color: #ef4444; border: 1px solid rgba(239,68,68,0.3)">
            خروج
          </button>
        </div>
      </header>

      <div class="max-w-7xl mx-auto p-3 md:p-6">
        <!-- التبويبات (تمرير أفقي على الموبايل) -->
        <div class="flex gap-2 mb-4 md:mb-6 p-1 rounded-xl overflow-x-auto"
             style="background: rgba(11,14,31,0.8); border: 1px solid #1a1f3a; -webkit-overflow-scrolling: touch">
          <button v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id"
                  class="flex-shrink-0 py-2 md:py-2.5 px-3 md:px-4 rounded-lg text-xs md:text-sm font-medium transition-all whitespace-nowrap"
                  :style="activeTab === tab.id
                    ? 'background: linear-gradient(135deg, #4a7eff, #8b5cf6); color: white'
                    : 'color: #94a3b8'">
            {{ tab.icon }} {{ tab.label }}
          </button>
        </div>

        <!-- ============ تبويب الإحصائيات ============ -->
        <div v-if="activeTab === 'stats'" class="animate-fade-in">
          <h2 class="text-2xl font-bold mb-6 gradient-text">📊 لوحة الإحصائيات</h2>

          <div v-if="statsLoading" class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div v-for="i in 4" :key="i" class="skeleton h-28 rounded-xl" />
          </div>

          <div v-else-if="stats" class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div v-for="stat in statCards" :key="stat.label" class="memorix-card p-5 text-center">
              <div class="text-3xl mb-1">{{ stat.icon }}</div>
              <div class="text-3xl font-black" :style="`color: ${stat.color}`">{{ stat.value }}</div>
              <div class="text-xs mt-1" style="color: #94a3b8">{{ stat.label }}</div>
            </div>
          </div>

          <!-- أساليب التعلم -->
          <div v-if="stats" class="memorix-card p-6">
            <h3 class="font-bold mb-4" style="color: #00d4ff">🧠 توزيع أساليب التعلم</h3>
            <div class="grid grid-cols-3 gap-4">
              <div v-for="style in learningStyleCards" :key="style.key" class="text-center p-4 rounded-xl"
                   :style="`background: ${style.bg}; border: 1px solid ${style.border}`">
                <div class="text-2xl mb-1">{{ style.icon }}</div>
                <div class="text-2xl font-black" :style="`color: ${style.color}`">
                  {{ stats.learning_styles[style.key] || 0 }}
                </div>
                <div class="text-xs mt-1" style="color: #94a3b8">{{ style.label }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- ============ تبويب إعداد المدرسة ============ -->
        <!-- ============ 🏫 المدارس (إضافة + قائمة) ============ -->
        <div v-if="activeTab === 'schools'" class="animate-fade-in">
          <h2 class="text-2xl font-bold mb-6 gradient-text">🏫 إدارة المدارس</h2>

          <!-- إضافة مدرسة جديدة -->
          <div class="memorix-card p-6 mb-6">
            <h3 class="font-bold mb-4" style="color: #4a7eff">➕ إضافة مدرسة جديدة</h3>
            <div class="grid md:grid-cols-3 gap-4 mb-4">
              <input v-model="newSchool.name" class="memorix-input" placeholder="اسم المدرسة" dir="rtl" />
              <input v-model="newSchool.branch" class="memorix-input" placeholder="الفرع (اختياري)" dir="rtl" />
              <input v-model="newSchool.ministry_code" class="memorix-input" placeholder="كود الوزارة (اختياري)" dir="rtl" />
            </div>
            <button @click="createNewSchool" :disabled="newSchoolLoading || !newSchool.name.trim()"
                    class="btn-primary text-sm flex items-center gap-2">
              <span v-if="newSchoolLoading" class="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              💾 إضافة وحفظ في قاعدة البيانات
            </button>
            <p v-if="newSchoolMsg" class="mt-3 text-sm" :style="{color: newSchoolMsg.startsWith('✅')?'#10b981':'#ef4444'}">{{ newSchoolMsg }}</p>
          </div>

          <!-- قائمة المدارس -->
          <div class="memorix-card overflow-hidden">
            <div class="p-4" style="border-bottom: 1px solid #1a1f3a">
              <h3 class="font-bold">📋 المدارس المسجلة ({{ schools.length }})</h3>
            </div>
            <div v-if="!schools.length" class="p-8 text-center" style="color: #94a3b8">لا توجد مدارس بعد. أضف مدرستك الأولى أعلاه.</div>
            <table v-else class="w-full text-sm">
              <thead>
                <tr style="background: rgba(26,31,58,0.8)">
                  <th class="p-3 text-right" style="color: #94a3b8">الاسم</th>
                  <th class="p-3 text-right" style="color: #94a3b8">الحالة</th>
                  <th class="p-3 text-right" style="color: #94a3b8">إجراءات</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="s in schools" :key="s.id" class="border-t" style="border-color: #1a1f3a">
                  <td class="p-3 font-medium">{{ s.name }}</td>
                  <td class="p-3">
                    <span v-if="s.setup_completed" class="text-xs px-2 py-1 rounded-full" style="background: rgba(16,185,129,0.15); color: #10b981">✅ معدّة</span>
                    <span v-else class="text-xs px-2 py-1 rounded-full" style="background: rgba(251,191,36,0.15); color: #fbbf24">⏳ بانتظار الإعداد</span>
                  </td>
                  <td class="p-3 flex gap-2">
                    <button @click="goToSetup(s.id)" class="text-xs px-3 py-1 rounded" style="background: rgba(74,126,255,0.15); color: #4a7eff">📤 رفع Excel</button>
                    <button @click="confirmDeleteSchool(s)" class="text-xs px-3 py-1 rounded" style="background: rgba(239,68,68,0.15); color: #ef4444">🗑️ حذف</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- ============ 📤 إعداد + رفع Excel ============ -->
        <div v-if="activeTab === 'setup'" class="animate-fade-in">
          <h2 class="text-2xl font-bold mb-6 gradient-text">📤 إعداد المدرسة برفع ملف Excel</h2>

          <!-- اختيار المدرسة -->
          <div class="memorix-card p-6 mb-6">
            <label class="block text-sm font-medium mb-2" style="color: #94a3b8">اختر المدرسة</label>
            <select v-model="selectedSchool" class="memorix-input" style="direction: rtl">
              <option value="">-- اختر مدرسة --</option>
              <option v-for="s in schools" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
            <p v-if="!schools.length" class="text-xs mt-2" style="color: #fbbf24">⚠️ لا توجد مدارس — أضف مدرسة أولاً من تبويب "المدارس"</p>
          </div>

          <!-- شرح ملف Excel -->
          <div v-if="selectedSchool" class="memorix-card p-6 mb-6" style="border:1px solid rgba(74,126,255,.3)">
            <h3 class="font-bold mb-3" style="color:#4a7eff">📋 صيغة ملف Excel المتوقعة</h3>
            <p class="text-xs mb-3" style="color:#94a3b8">يجب أن يحتوي الملف على هذه الأعمدة (الترتيب غير مهم):</p>
            <table class="w-full text-xs" style="background:#0f172a;border-radius:8px">
              <thead>
                <tr style="background:rgba(99,102,241,.15)">
                  <th class="p-2">الاسم</th>
                  <th class="p-2">الدور</th>
                  <th class="p-2">الصف</th>
                  <th class="p-2">المادة</th>
                  <th class="p-2">الرقم الوزاري</th>
                </tr>
              </thead>
              <tbody>
                <tr><td class="p-2">محمد أحمد</td><td class="p-2">طالب</td><td class="p-2">الصف الخامس</td><td class="p-2">-</td><td class="p-2">12345</td></tr>
                <tr><td class="p-2">سارة علي</td><td class="p-2">معلم</td><td class="p-2">-</td><td class="p-2">رياضيات</td><td class="p-2">T001</td></tr>
                <tr><td class="p-2">خالد سعد</td><td class="p-2">إداري</td><td class="p-2">-</td><td class="p-2">-</td><td class="p-2">A01</td></tr>
              </tbody>
            </table>
            <p class="text-xs mt-3" style="color:#10b981">✅ يقبل: طالب/معلم/إداري أو student/teacher/admin</p>
          </div>

          <!-- رفع الملف -->
          <div v-if="selectedSchool" class="memorix-card p-6">
            <h3 class="font-bold mb-4" style="color:#a78bfa">📤 ارفع ملف Excel</h3>
            <input ref="excelInput" type="file" accept=".xlsx,.xls" @change="onExcelChange" class="memorix-input" />
            <p v-if="excelFileName" class="mt-3 text-sm" style="color:#10b981">📄 الملف المختار: {{ excelFileName }}</p>
            <button @click="uploadExcel" :disabled="!excelFile || uploadLoading"
                    class="btn-primary mt-4 flex items-center gap-2">
              <span v-if="uploadLoading" class="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ⚡ ارفع وولّد الحسابات
            </button>
            <div v-if="uploadResult" class="mt-4 p-4 rounded-lg" style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3)">
              <h4 class="font-bold mb-2" style="color:#10b981">✅ تم بنجاح!</h4>
              <p style="color:#94a3b8">المدرسة: {{ uploadResult.school_name }}</p>
              <p style="color:#94a3b8">إجمالي الحسابات المولدة: {{ uploadResult.total }}</p>
              <p style="color:#94a3b8">طلاب: {{ uploadResult.students_count }} • معلمون: {{ uploadResult.teachers_count }} • إداريون: {{ uploadResult.admins_count }}</p>
              <p class="mt-2 text-sm" style="color:#fbbf24">📋 الحسابات وكلمات السر متاحة الآن في تبويب "الحسابات"</p>
            </div>
          </div>
        </div>

        <!-- ============ تبويب الحسابات ============ -->
        <div v-if="activeTab === 'accounts'" class="animate-fade-in">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold gradient-text">👥 الحسابات المُولَّدة</h2>
            <button v-if="accounts.length && selectedSchoolForAccounts"
                    @click="downloadCSV"
                    class="btn-primary text-sm py-2 flex items-center gap-2">
              📥 تحميل CSV
            </button>
          </div>

          <!-- اختيار المدرسة -->
          <div class="memorix-card p-4 mb-6 flex items-center gap-4">
            <label class="text-sm" style="color: #94a3b8">المدرسة:</label>
            <select v-model="selectedSchoolForAccounts" @change="loadAccounts" class="memorix-input w-64" style="direction: rtl">
              <option value="">-- اختر مدرسة --</option>
              <option v-for="s in schools" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
          </div>

          <!-- جدول الحسابات -->
          <div v-if="accountsLoading" class="space-y-2">
            <div v-for="i in 5" :key="i" class="skeleton h-12 rounded-lg" />
          </div>

          <div v-else-if="accounts.length" class="memorix-card overflow-hidden">
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr style="background: rgba(26,31,58,0.8)">
                    <th class="p-3 text-right" style="color: #94a3b8">الاسم</th>
                    <th class="p-3 text-right" style="color: #94a3b8">الإيميل</th>
                    <th class="p-3 text-right" style="color: #94a3b8">الدور</th>
                    <th class="p-3 text-right" style="color: #94a3b8">الصف</th>
                    <th class="p-3 text-right" style="color: #94a3b8">المادة</th>
                    <th class="p-3 text-right" style="color: #94a3b8">كلمة السر</th>
                    <th class="p-3 text-right" style="color: #94a3b8">حذف</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="acc in accounts" :key="acc.id"
                      class="border-t transition-colors hover:bg-white/5"
                      style="border-color: #1a1f3a">
                    <td class="p-3">{{ acc.full_name }}</td>
                    <td class="p-3 font-mono text-xs" style="color: #4a7eff; direction: ltr">{{ acc.email }}</td>
                    <td class="p-3">
                      <span class="px-2 py-1 rounded-full text-xs"
                            :style="roleStyle(acc.role)">
                        {{ roleLabel(acc.role) }}
                      </span>
                    </td>
                    <td class="p-3" style="color: #94a3b8">{{ acc.grade || '-' }}</td>
                    <td class="p-3" style="color: #94a3b8">{{ acc.subject || '-' }}</td>
                    <td class="p-3">
                      <button v-if="!revealedPasswords[acc.id]"
                              @click="revealPassword(acc.id)"
                              :disabled="revealLoading[acc.id]"
                              class="text-xs px-3 py-1 rounded"
                              style="background:rgba(139,92,246,0.15);color:#a78bfa">
                        {{ revealLoading[acc.id] ? '⏳' : '🔑 عرض' }}
                      </button>
                      <span v-else class="font-mono px-2 py-1 rounded text-xs cursor-pointer"
                            @click="copyToClipboard(revealedPasswords[acc.id])"
                            style="background:rgba(139,92,246,0.15);color:#a78bfa;letter-spacing:1px"
                            title="انقر للنسخ">
                        {{ revealedPasswords[acc.id] }}
                      </span>
                    </td>
                    <td class="p-3">
                      <button @click="confirmDeleteAccount(acc)"
                              class="text-xs px-3 py-1 rounded"
                              style="background:rgba(239,68,68,0.15);color:#ef4444">
                        🗑️ حذف
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="p-3 text-center text-sm" style="color: #94a3b8; border-top: 1px solid #1a1f3a">
              إجمالي: {{ accounts.length }} حساب
            </div>
          </div>

          <div v-else-if="selectedSchoolForAccounts" class="memorix-card p-12 text-center" style="color: #94a3b8">
            لا توجد حسابات بعد. اذهب لتبويب "إعداد + رفع Excel" لتوليدها.
          </div>
        </div>

        <!-- ============ تبويب الكتب ============ -->
        <div v-if="activeTab === 'books'" class="animate-fade-in">
          <h2 class="text-2xl font-bold mb-6 gradient-text">📚 كتب المنهج</h2>

          <!-- إضافة كتاب -->
          <div class="memorix-card p-6 mb-6">
            <h3 class="font-bold mb-4" style="color: #00d4ff">➕ إضافة كتاب جديد</h3>
            <div class="grid md:grid-cols-3 gap-4 mb-4">
              <input v-model="newBook.title" class="memorix-input" placeholder="عنوان الكتاب" dir="rtl" />
              <input v-model="newBook.subject" class="memorix-input" placeholder="المادة" dir="rtl" />
              <input v-model="newBook.grade" class="memorix-input" placeholder="الصف الدراسي" dir="rtl" />
            </div>
            <textarea v-model="newBook.raw_text" class="memorix-input h-32 resize-none mb-4"
                      placeholder="محتوى الكتاب (اختياري - سيُولَّد ملخص تلقائياً بالذكاء الاصطناعي)" dir="rtl" />
            <button @click="addBook" class="btn-primary text-sm" :disabled="bookLoading">
              {{ bookLoading ? '⏳ جاري الإضافة...' : '📖 إضافة الكتاب' }}
            </button>
          </div>

          <!-- قائمة الكتب -->
          <div class="grid md:grid-cols-2 gap-4">
            <div v-for="book in books" :key="book.id" class="memorix-card p-5">
              <div class="flex items-start justify-between mb-2">
                <h4 class="font-bold">{{ book.title }}</h4>
                <span class="text-xs px-2 py-1 rounded-full" style="background: rgba(74,126,255,0.15); color: #4a7eff">
                  {{ book.grade }}
                </span>
              </div>
              <p class="text-xs mb-2" style="color: #8b5cf6">{{ book.subject }}</p>
              <p class="text-sm line-clamp-3" style="color: #94a3b8">
                {{ book.summary || 'لا يوجد ملخص بعد' }}
              </p>
            </div>
          </div>
        </div>

        <!-- ============ تبويب مساعد AI ============ -->
        <div v-if="activeTab === 'chat'" class="animate-fade-in" style="height: calc(100vh - 200px); display: flex; flex-direction: column;">
          <div ref="chatEl" style="flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px;">
            <div v-if="!chatMsgs.length" class="memorix-card p-10 text-center">
              <div style="font-size:48px;margin-bottom:12px">🤖</div>
              <h3 class="font-bold text-xl mb-2">مساعد المدير الذكي</h3>
              <p style="color: #94a3b8; margin-bottom: 16px">اسأل بأي لغة أو لهجة — الـ AI يرد بنفس الأسلوب</p>
              <div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center">
                <button v-for="q in mgrQuickQs" :key="q"
                  class="text-sm px-4 py-2 rounded-full transition-all"
                  style="background: rgba(74,126,255,0.1); border: 1px solid rgba(74,126,255,0.3); color: #94a3b8; cursor:pointer"
                  @click="sendMgrMsg(q)">{{ q }}</button>
              </div>
            </div>
            <div v-for="(msg, i) in chatMsgs" :key="i"
              :style="msg.role==='user' ? 'display:flex;justify-content:flex-start' : 'display:flex;justify-content:flex-end'">
              <div style="max-width:75%;display:flex;align-items:flex-start;gap:10px"
                :style="msg.role==='user' ? '' : 'flex-direction:row-reverse'">
                <span style="font-size:20px;flex-shrink:0;margin-top:4px">{{ msg.role==='user' ? '👤' : '🤖' }}</span>
                <div class="text-sm p-3 rounded-xl" style="line-height:1.6"
                  :style="msg.role==='user'
                    ? 'background:rgba(74,126,255,0.15);border:1px solid rgba(74,126,255,0.3);color:#e2e8f0'
                    : 'background:rgba(26,31,58,0.8);border:1px solid #1a1f3a;color:#e2e8f0'"
                  v-html="fmtChat(msg.content)"></div>
              </div>
            </div>
            <div v-if="chatThinking" style="display:flex;justify-content:flex-end">
              <div style="display:flex;align-items:center;gap:10px;flex-direction:row-reverse">
                <span style="font-size:20px">🤖</span>
                <div class="p-3 rounded-xl" style="background:rgba(26,31,58,0.8);border:1px solid #1a1f3a">
                  <div style="display:flex;gap:4px;align-items:center">
                    <span v-for="n in 3" :key="n" style="width:8px;height:8px;background:#94a3b8;border-radius:50%;animation:bounce 1s infinite" :style="`animation-delay:${(n-1)*0.15}s`"></span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="memorix-card p-3" style="display:flex;gap:10px;align-items:flex-end;margin:0;border-radius:0;border-left:none;border-right:none;border-bottom:none">
            <textarea v-model="chatInput" rows="2"
              class="memorix-input flex-1 resize-none" placeholder="اكتب سؤالك للمساعد الذكي..." dir="rtl"
              style="border-radius:10px"
              @keydown.enter.exact.prevent="sendMgrMsg()" @keydown.enter.shift.exact="chatInput+='\n'"></textarea>
            <button @click="sendMgrMsg()" :disabled="!chatInput.trim()||chatThinking"
              class="btn-primary px-4 py-3" style="border-radius:10px;font-size:18px;flex-shrink:0">➤</button>
          </div>
        </div>

        <!-- ============ 💪 صحة المدارس ============ -->
        <div v-if="activeTab === 'health'" class="animate-fade-in">
          <h2 class="text-2xl font-bold mb-6 gradient-text">💪 صحة المدارس</h2>
          <button @click="loadHealth" :disabled="hlLoading" class="btn-primary px-6 py-3 mb-4" style="border-radius:10px">
            {{ hlLoading ? '⏳' : '🔄 تحديث' }}
          </button>
          <div v-if="health.length" class="grid gap-3">
            <div v-for="h in health" :key="h.school_id" class="memorix-card p-4 flex justify-between items-center">
              <div>
                <h3 class="font-bold">{{ h.name }}</h3>
                <p class="text-sm" style="color:#94a3b8">{{ h.users }} مستخدم • {{ h.active_week }} نشط</p>
              </div>
              <div class="text-left">
                <div style="font-size:28px;font-weight:bold;color:#fbbf24">{{ h.score }}</div>
                <div class="text-sm">{{ h.status }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- ============ 🧠 مستشار استراتيجي ============ -->
        <div v-if="activeTab === 'advisor'" class="animate-fade-in">
          <h2 class="text-2xl font-bold mb-6 gradient-text">🧠 المستشار الاستراتيجي</h2>
          <div class="memorix-card p-6">
            <textarea v-model="adQuestion" rows="3" placeholder="مثال: كيف أحسّن نسبة الاحتفاظ بالطلاب في مدرسة الرياض؟"
                      class="w-full p-3 rounded-lg mb-3" style="background:#0f172a;color:#fff;border:1px solid #334155"></textarea>
            <textarea v-model="adContext" rows="2" placeholder="سياق إضافي (اختياري): البيانات/التحديات الحالية..."
                      class="w-full p-3 rounded-lg mb-3" style="background:#0f172a;color:#fff;border:1px solid #334155"></textarea>
            <button @click="askAdvisor" :disabled="adLoading" class="btn-primary px-6 py-3" style="border-radius:10px">
              {{ adLoading ? '⏳ يحلل...' : '🚀 احصل على استشارة' }}
            </button>
            <div v-if="adAnswer" class="mt-4 p-4 rounded-lg" style="background:#0f172a;white-space:pre-wrap;line-height:1.8;color:#e2e8f0">
              {{ adAnswer }}
            </div>
          </div>
        </div>

        <!-- ============ تبويب الإعدادات ============ -->
        <div v-if="activeTab === 'settings'" class="animate-fade-in">
          <h2 class="text-2xl font-bold mb-6 gradient-text">⚙️ الإعدادات</h2>
          <div class="grid md:grid-cols-2 gap-6">
            <div class="memorix-card p-6">
              <h3 class="font-bold mb-4" style="color: #00d4ff">👤 معلومات الحساب</h3>
              <div class="flex items-center gap-4 mb-4">
                <img v-if="mgrSettings.avatar_url" :src="mgrSettings.avatar_url"
                  style="width:60px;height:60px;border-radius:50%;object-fit:cover;border:2px solid #1a1f3a" />
                <div v-else style="width:60px;height:60px;border-radius:50%;background:linear-gradient(135deg,#4a7eff,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:700;color:#fff">
                  {{ auth.user?.full_name?.[0] || 'م' }}
                </div>
                <div style="flex:1">
                  <p class="text-xs mb-1" style="color:#94a3b8">رابط صورة البروفايل</p>
                  <input v-model="mgrSettings.avatar_url" class="memorix-input" placeholder="https://..." dir="ltr" @blur="saveMgrSettings" />
                </div>
              </div>
              <div class="flex justify-between py-2 text-sm" style="border-bottom:1px solid #1a1f3a;color:#94a3b8"><span>الاسم</span><b style="color:#e2e8f0">{{ auth.user?.full_name }}</b></div>
              <div class="flex justify-between py-2 text-sm" style="border-bottom:1px solid #1a1f3a;color:#94a3b8"><span>الإيميل</span><b style="color:#e2e8f0;direction:ltr">{{ auth.user?.email }}</b></div>
              <div class="flex justify-between py-2 text-sm" style="color:#94a3b8"><span>الدور</span><b style="color:#10b981">مدير</b></div>
            </div>
            <div class="memorix-card p-6">
              <h3 class="font-bold mb-4" style="color: #8b5cf6">🌐 اللغة</h3>
              <select v-model="mgrSettings.language" @change="saveMgrSettings" class="memorix-input mb-6" dir="rtl">
                <option value="ar">العربية</option>
                <option value="en">English</option>
                <option value="fr">Français</option>
                <option value="de">Deutsch</option>
              </select>
              <p v-if="settingsMsg" style="color:#4ade80;font-size:13px;text-align:center">{{ settingsMsg }}</p>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- نافذة نتائج التوليد -->
    <div v-if="generatedAccounts.length" class="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4">
      <div class="memorix-card p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-bold text-xl" style="color: #00d4ff">✅ تم توليد {{ generatedAccounts.length }} حساب</h3>
          <button @click="generatedAccounts = []" style="color: #94a3b8; font-size: 24px; background: none; border: none; cursor: pointer">×</button>
        </div>
        <div class="p-3 rounded-lg mb-4 text-sm"
             style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); color: #ef4444">
          ⚠️ احفظ كلمات المرور الآن! لن تظهر مرة أخرى.
        </div>
        <div class="space-y-2">
          <div v-for="acc in generatedAccounts" :key="acc.email"
               class="p-3 rounded-lg flex items-center justify-between"
               style="background: rgba(26,31,58,0.6); border: 1px solid #1a1f3a">
            <div>
              <div class="font-medium text-sm">{{ acc.full_name }}</div>
              <div class="text-xs font-mono mt-0.5" style="color: #4a7eff; direction: ltr">{{ acc.email }}</div>
            </div>
            <div class="text-right">
              <div class="font-mono text-sm px-2 py-1 rounded"
                   style="background: rgba(139,92,246,0.2); color: #8b5cf6">
                {{ acc.password }}
              </div>
              <div class="text-xs mt-1" style="color: #94a3b8">{{ roleLabel(acc.role) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import { managerAPI, teacherAPI } from '../api.js'
import Stars from '../components/Stars.vue'

const router = useRouter()
const auth = useAuthStore()

const activeTab = ref('stats')
const tabs = [
  { id: 'stats', label: 'الإحصائيات', icon: '📊' },
  { id: 'schools', label: 'المدارس', icon: '🏫' },
  { id: 'setup', label: 'إعداد + رفع Excel', icon: '📤' },
  { id: 'accounts', label: 'الحسابات', icon: '👥' },
  { id: 'books', label: 'الكتب', icon: '📚' },
  { id: 'health', label: 'صحة المدارس', icon: '💪' },
  { id: 'advisor', label: 'مستشار استراتيجي', icon: '🧠' },
  { id: 'chat', label: 'مساعد AI', icon: '💬' },
  { id: 'settings', label: 'الإعدادات', icon: '⚙️' },
]

// الإحصائيات
const stats = ref(null)
const statsLoading = ref(false)

const statCards = computed(() => stats.value ? [
  { label: 'إجمالي المستخدمين', value: stats.value.total_users, icon: '👤', color: '#4a7eff' },
  { label: 'الطلبة', value: stats.value.total_students, icon: '👨‍🎓', color: '#00d4ff' },
  { label: 'المعلمون', value: stats.value.total_teachers, icon: '👨‍🏫', color: '#8b5cf6' },
  { label: 'المحادثات', value: stats.value.total_conversations, icon: '💬', color: '#10b981' },
] : [])

const learningStyleCards = [
  { key: 'visual', label: 'بصري', icon: '👁️', color: '#4a7eff', bg: 'rgba(74,126,255,0.1)', border: 'rgba(74,126,255,0.3)' },
  { key: 'auditory', label: 'سمعي', icon: '🎧', color: '#00d4ff', bg: 'rgba(0,212,255,0.1)', border: 'rgba(0,212,255,0.3)' },
  { key: 'kinesthetic', label: 'حركي', icon: '🤸', color: '#8b5cf6', bg: 'rgba(139,92,246,0.1)', border: 'rgba(139,92,246,0.3)' },
]

// المدارس والحسابات
const schools = ref([])
const schoolSearch = ref('')
const filteredSchools = computed(() =>
  schoolSearch.value
    ? schools.value.filter(s => s.name.includes(schoolSearch.value))
    : schools.value
)
const selectedSchool = ref('')
const selectedSchoolForAccounts = ref('')
const accounts = ref([])
const accountsLoading = ref(false)

// AI Chat
const chatMsgs = ref([])
const chatInput = ref('')
const chatThinking = ref(false)
const chatEl = ref(null)
const mgrQuickQs = ['كيف أحسن أداء المدرسة؟', 'اقترح خطة تطوير للمعلمين', 'كيف أتابع الطلاب المتأخرين؟', 'أفضل استراتيجيات الإدارة']

// Settings
const mgrSettings = ref({ avatar_url: '', theme: 'dark', language: 'ar' })
const settingsMsg = ref('')

// إعداد المدرسة
const studentsText = ref('')
const teachersText = ref('')
const adminsCount = ref(1)
const setupLoading = ref(false)
const generatedAccounts = ref([])

const parsedStudents = computed(() => {
  return studentsText.value.split('\n')
    .map(l => l.trim()).filter(Boolean)
    .map(line => {
      const [name, ministry_id, grade] = line.split(',').map(s => s.trim())
      return { name: name || '', ministry_id: ministry_id || '', grade: grade || '' }
    })
})

const parsedTeachers = computed(() => {
  return teachersText.value.split('\n')
    .map(l => l.trim()).filter(Boolean)
    .map(line => {
      const [name, subject] = line.split(',').map(s => s.trim())
      return { name: name || '', subject: subject || '' }
    })
})

// الباسووردات
const savedPasswords = ref([])
const selectedSchoolForPasswords = ref('')
const passwordsLoading = ref(false)

// الكتب
const books = ref([])
const bookLoading = ref(false)
const newBook = ref({ title: '', subject: '', grade: '', raw_text: '' })

async function loadStats() {
  statsLoading.value = true
  try {
    const res = await managerAPI.getStats()
    stats.value = res.data
  } catch (e) {
    console.error('خطأ في الإحصائيات:', e)
  } finally {
    statsLoading.value = false
  }
}

async function loadAccounts() {
  if (!selectedSchoolForAccounts.value) return
  accountsLoading.value = true
  try {
    const res = await managerAPI.getAccounts(selectedSchoolForAccounts.value)
    accounts.value = res.data
  } catch (e) {
    console.error('خطأ في جلب الحسابات:', e)
  } finally {
    accountsLoading.value = false
  }
}

async function generateAccounts() {
  if (!selectedSchool.value) return
  if (!parsedStudents.value.length && !parsedTeachers.value.length && !adminsCount.value) {
    alert('أدخل بيانات على الأقل')
    return
  }

  setupLoading.value = true
  try {
    const res = await managerAPI.setupSchool({
      school_id: selectedSchool.value,
      students: parsedStudents.value,
      teachers: parsedTeachers.value,
      admins_count: adminsCount.value
    })
    generatedAccounts.value = res.data.accounts
    await loadStats()
  } catch (e) {
    alert('خطأ: ' + (e.response?.data?.detail || e.message))
  } finally {
    setupLoading.value = false
  }
}

async function downloadCSV() {
  try {
    const res = await managerAPI.exportCSV(selectedSchoolForAccounts.value)
    const url = URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = url
    a.download = 'memorix_accounts.csv'
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    alert('خطأ في التحميل')
  }
}

async function loadSavedPasswords() {
  if (!selectedSchoolForPasswords.value) return
  passwordsLoading.value = true
  try {
    const res = await managerAPI.getSavedPasswords(selectedSchoolForPasswords.value)
    savedPasswords.value = res.data.accounts || []
  } catch (e) {
    console.error('خطأ في جلب الباسووردات:', e)
  } finally {
    passwordsLoading.value = false
  }
}

function downloadPasswordsCSV() {
  const BOM = '﻿'
  const header = 'الاسم,الإيميل,الباسوورد,الدور\n'
  const rows = savedPasswords.value.map(a =>
    `${a.full_name},${a.email},${a.password},${roleLabel(a.role)}`
  ).join('\n')
  const blob = new Blob([BOM + header + rows], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'memorix_passwords.csv'
  link.click()
  URL.revokeObjectURL(url)
}

async function addBook() {
  if (!newBook.value.title || !newBook.value.subject) {
    alert('أدخل عنوان الكتاب والمادة')
    return
  }
  bookLoading.value = true
  try {
    await managerAPI.addBook(newBook.value)
    newBook.value = { title: '', subject: '', grade: '', raw_text: '' }
    const res = await managerAPI.getBooks()
    books.value = res.data
  } catch (e) {
    alert('خطأ في إضافة الكتاب')
  } finally {
    bookLoading.value = false
  }
}

function roleLabel(role) {
  return { student: 'طالب', teacher: 'معلم', admin: 'إداري', manager: 'مدير' }[role] || role
}

function roleStyle(role) {
  const map = {
    student: 'background: rgba(74,126,255,0.15); color: #4a7eff',
    teacher: 'background: rgba(0,212,255,0.15); color: #00d4ff',
    admin: 'background: rgba(139,92,246,0.15); color: #8b5cf6',
    manager: 'background: rgba(16,185,129,0.15); color: #10b981',
  }
  return map[role] || ''
}

async function sendMgrMsg(text) {
  const m = text || chatInput.value.trim(); if(!m) return
  chatInput.value = ''; chatMsgs.value.push({ role: 'user', content: m }); chatThinking.value = true
  nextTick(() => { if(chatEl.value) chatEl.value.scrollTop = chatEl.value.scrollHeight })
  try {
    const r = await teacherAPI.chat(m)
    chatMsgs.value.push({ role: 'assistant', content: r.data.reply })
  } catch {
    chatMsgs.value.push({ role: 'assistant', content: 'حدث خطأ في الاتصال.' })
  } finally {
    chatThinking.value = false
    nextTick(() => { if(chatEl.value) chatEl.value.scrollTop = chatEl.value.scrollHeight })
  }
}

function fmtChat(t) {
  if(!t) return ''
  return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>').replace(/\*(.*?)\*/g,'<em>$1</em>')
    .replace(/`(.*?)`/g,'<code style="background:rgba(255,255,255,.1);border-radius:4px;padding:1px 5px">$1</code>').replace(/\n/g,'<br>')
}

async function saveMgrSettings() {
  try {
    settingsMsg.value = '✅ تم الحفظ'
    setTimeout(() => { settingsMsg.value = '' }, 2000)
  } catch {}
}

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}

// 👔 ميزات المدير المتقدمة
const health = ref([]), hlLoading = ref(false)
async function loadHealth() { hlLoading.value=true; try { health.value=(await managerAPI.healthScore()).data } catch(e){alert('فشل')} hlLoading.value=false }
const adQuestion = ref(''), adContext = ref(''), adLoading = ref(false), adAnswer = ref('')
async function askAdvisor() {
  if (!adQuestion.value.trim()) return alert('اطرح سؤالك')
  adLoading.value=true; adAnswer.value=''
  try { adAnswer.value=(await managerAPI.strategicAdvisor(adQuestion.value, adContext.value)).data.advice }
  catch(e) { alert('فشل') }
  adLoading.value=false
}

// 🏫 إدارة المدارس
const newSchool = ref({ name:'', branch:'', ministry_code:'' })
const newSchoolLoading = ref(false)
const newSchoolMsg = ref('')
async function createNewSchool() {
  if (!newSchool.value.name.trim()) return
  newSchoolLoading.value = true; newSchoolMsg.value = ''
  try {
    await managerAPI.createSchool(newSchool.value)
    newSchoolMsg.value = '✅ تمت الإضافة وتم الحفظ في قاعدة البيانات'
    newSchool.value = { name:'', branch:'', ministry_code:'' }
    schools.value = (await managerAPI.getSchools()).data
  } catch (e) {
    newSchoolMsg.value = '❌ ' + (e.response?.data?.detail || e.message)
  }
  newSchoolLoading.value = false
}
async function confirmDeleteSchool(s) {
  if (!confirm(`⚠️ هل أنت متأكد من حذف مدرسة "${s.name}"؟\nسيتم حذف كل الحسابات المرتبطة بها نهائياً!`)) return
  try {
    await managerAPI.deleteSchool(s.id)
    schools.value = (await managerAPI.getSchools()).data
    alert('✅ تم حذف المدرسة وكل بياناتها')
  } catch (e) {
    alert('❌ فشل: ' + (e.response?.data?.detail || e.message))
  }
}
function goToSetup(schoolId) {
  selectedSchool.value = schoolId
  activeTab.value = 'setup'
}

// 📤 رفع Excel
const excelFile = ref(null)
const excelFileName = ref('')
const uploadLoading = ref(false)
const uploadResult = ref(null)
function onExcelChange(e) {
  const f = e.target.files?.[0]
  if (!f) return
  excelFile.value = f
  excelFileName.value = f.name
}
async function uploadExcel() {
  if (!excelFile.value || !selectedSchool.value) return
  uploadLoading.value = true; uploadResult.value = null
  try {
    const r = await managerAPI.uploadExcel(selectedSchool.value, excelFile.value)
    uploadResult.value = r.data
    schools.value = (await managerAPI.getSchools()).data
  } catch (e) {
    alert('❌ فشل الرفع: ' + (e.response?.data?.detail || e.message))
  }
  uploadLoading.value = false
}

// 🔑 عرض كلمة السر لكل حساب
const revealedPasswords = ref({})
const revealLoading = ref({})
async function revealPassword(userId) {
  revealLoading.value[userId] = true
  try {
    const r = await managerAPI.getAccountPassword(userId)
    revealedPasswords.value[userId] = r.data.password
  } catch (e) {
    alert('❌ ' + (e.response?.data?.detail || 'تعذر جلب كلمة السر'))
  }
  revealLoading.value[userId] = false
}
function copyToClipboard(text) {
  navigator.clipboard?.writeText(text)
  alert('✅ تم نسخ كلمة السر')
}

// 🗑️ حذف حساب
async function confirmDeleteAccount(acc) {
  if (!confirm(`⚠️ هل أنت متأكد من حذف الحساب "${acc.full_name}" (${acc.email})؟\nسيتم حذف كل بياناته نهائياً من قاعدة البيانات!`)) return
  try {
    await managerAPI.deleteAccount(acc.id)
    accounts.value = accounts.value.filter(a => a.id !== acc.id)
    delete revealedPasswords.value[acc.id]
    alert('✅ تم حذف الحساب نهائياً')
  } catch (e) {
    alert('❌ فشل: ' + (e.response?.data?.detail || e.message))
  }
}

onMounted(async () => {
  await loadStats()
  try {
    const res = await managerAPI.getSchools()
    schools.value = res.data
    const booksRes = await managerAPI.getBooks()
    books.value = booksRes.data
  } catch (e) {
    console.error('خطأ في تحميل البيانات:', e)
  }
})
</script>

<style scoped>
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}
</style>
