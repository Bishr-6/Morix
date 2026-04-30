<template>
  <div class="hub">
    <!-- Sidebar -->
    <aside :class="['sidebar',{collapsed:sb}]">
      <div class="sb-header" @click="sb=!sb">
        <div class="brand"><div class="b-icon">M</div><span v-if="!sb" class="b-name">Morix</span></div>
      </div>
      <nav class="sb-nav">
        <button v-for="s in sections" :key="s.id" :class="['nav-item',{active:cur===s.id}]" @click="cur=s.id" :title="s.label">
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
        <div class="chip"><div class="av">{{ firstName[0] }}</div><span>{{ firstName }}</span></div>
      </header>

      <!-- ===== OVERVIEW ===== -->
      <section v-show="cur==='overview'" class="body pad">
        <div class="stats-grid">
          <div class="sc"><div class="sn">{{ students.length }}</div><div class="sl">طلاب المدرسة</div></div>
          <div class="sc"><div class="sn">{{ homework.length }}</div><div class="sl">واجبات محددة</div></div>
          <div class="sc"><div class="sn">{{ myTests.length }}</div><div class="sl">اختبارات</div></div>
          <div class="sc"><div class="sn">{{ worksheets.length }}</div><div class="sl">أوراق عمل</div></div>
        </div>
        <div class="card mt">
          <h3>👋 مرحباً {{ firstName }}!</h3>
          <p style="color:var(--t2)">اختر قسماً من القائمة الجانبية للبدء.</p>
        </div>
      </section>

      <!-- ===== HOMEWORK ===== -->
      <section v-show="cur==='homework'" class="body pad">
        <div class="card">
          <div class="row-sb"><h3>📚 الواجبات</h3><button class="btn-p" @click="hwForm=!hwForm">+ إضافة</button></div>
          <div v-if="hwForm" class="form-box">
            <p style="color:var(--t2);font-size:13px;margin:0 0 8px">🤖 AI يولّد العنوان والتعليمات تلقائياً — فقط أدخل الموضوع والمادة.</p>
            <input v-model="hwNew.topic" class="inp" placeholder="الموضوع / ما تريد الطلاب يدرسونه *" />
            <div class="row-gap">
              <input v-model="hwNew.subject" class="inp" placeholder="المادة *" />
              <input v-model="hwNew.grade" class="inp" placeholder="الصف" />
              <input v-model="hwNew.due_date" class="inp" type="datetime-local" />
            </div>
            <div class="row-gap"><button class="btn-p" @click="createHw" :disabled="hwLoading||!hwNew.topic||!hwNew.subject">{{ hwLoading?'⏳ AI يولّد...':'✨ إنشاء بالـ AI' }}</button><button class="btn-o" @click="hwForm=false">إلغاء</button></div>
          </div>
          <div v-if="!homework.length" class="empty">لا توجد واجبات</div>
          <div v-else class="list-col">
            <div v-for="hw in homework" :key="hw.id" class="list-item">
              <div style="flex:1"><h4>{{ hw.title }}</h4>
                <div class="meta"><span>📚 {{ hw.subject }}</span><span v-if="hw.grade">🎓 {{ hw.grade }}</span><span v-if="hw.due_date">📅 {{ fmtDate(hw.due_date) }}</span></div>
              </div>
              <div class="row-gap">
                <button class="btn-s" @click="viewSubmissions(hw.id)">عرض التسليمات</button>
                <button class="btn-s danger" @click="deleteHw(hw.id)">حذف</button>
              </div>
            </div>
          </div>
        </div>
        <div v-if="submissions.length" class="card mt">
          <h3>📥 التسليمات</h3>
          <div class="list-col">
            <div v-for="s in submissions" :key="s.id" class="list-item">
              <div><h4>{{ s.users?.full_name }}</h4><p style="color:var(--t2);font-size:13px">{{ s.content }}</p></div>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== TESTS ===== -->
      <section v-show="cur==='tests'" class="body pad">
        <div class="card">
          <div class="row-sb"><h3>📝 الاختبارات</h3><button class="btn-p" @click="testForm=!testForm">+ إضافة</button></div>
          <div v-if="testForm" class="form-box">
            <p style="color:var(--t2);font-size:13px;margin:0 0 8px">🤖 AI يولّد الأسئلة تلقائياً — فقط حدد الموضوع والمادة.</p>
            <input v-model="testNew.topic" class="inp" placeholder="الموضوع المحدد *" />
            <div class="row-gap">
              <input v-model="testNew.subject" class="inp" placeholder="المادة *" />
              <input v-model="testNew.grade" class="inp" placeholder="الصف" />
              <input v-model.number="testNew.duration_minutes" class="inp" type="number" placeholder="المدة (دقيقة)" />
            </div>
            <div class="row-gap"><button class="btn-p" @click="createTest" :disabled="testLoading||!testNew.topic||!testNew.subject">{{ testLoading?'⏳ AI يولّد الأسئلة...':'✨ إنشاء بالـ AI' }}</button><button class="btn-o" @click="testForm=false">إلغاء</button></div>
          </div>
          <div v-if="!myTests.length" class="empty">لا توجد اختبارات</div>
          <div v-else class="list-col">
            <div v-for="t in myTests" :key="t.id" class="list-item">
              <div style="flex:1"><h4>{{ t.title }}</h4><div class="meta"><span>📚 {{ t.subject }}</span><span>⏱ {{ t.duration_minutes }}د</span></div></div>
              <button class="btn-s danger" @click="deleteTest(t.id)">حذف</button>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== WORKSHEETS ===== -->
      <section v-show="cur==='worksheets'" class="body pad">
        <div class="card">
          <div class="row-sb"><h3>📋 أوراق العمل</h3><button class="btn-p" @click="wsForm=!wsForm">+ إضافة</button></div>
          <div v-if="wsForm" class="form-box">
            <p style="color:var(--t2);font-size:13px;margin:0 0 8px">🤖 AI يولّد ورقة العمل الكاملة — فقط أدخل الموضوع والمادة.</p>
            <input v-model="wsNew.topic" class="inp" placeholder="الموضوع المحدد *" />
            <div class="row-gap">
              <input v-model="wsNew.subject" class="inp" placeholder="المادة *" />
              <input v-model="wsNew.grade" class="inp" placeholder="الصف" />
            </div>
            <div class="row-gap"><button class="btn-p" @click="createWs" :disabled="wsLoading||!wsNew.topic||!wsNew.subject">{{ wsLoading?'⏳ AI يولّد ورقة العمل...':'✨ إنشاء بالـ AI' }}</button><button class="btn-o" @click="wsForm=false">إلغاء</button></div>
          </div>
          <div v-if="!worksheets.length" class="empty">لا توجد أوراق عمل</div>
          <div v-else class="list-col">
            <div v-for="ws in worksheets" :key="ws.id" class="list-item clickable" @click="viewWs(ws)">
              <div style="flex:1"><h4>{{ ws.title }}</h4><div class="meta"><span>📚 {{ ws.subject }}</span><span v-if="ws.ai_generated" class="ai-tag">🤖 AI</span></div></div>
              <button class="btn-s danger" @click.stop="deleteWs(ws.id)">حذف</button>
            </div>
          </div>
        </div>
        <div v-if="activeWs" class="card mt">
          <div class="row-sb"><h3>{{ activeWs.title }}</h3><button class="btn-o" @click="activeWs=null">✕</button></div>
          <div style="color:var(--t2);line-height:1.8;font-size:14px;white-space:pre-wrap" v-html="fmt(activeWs.content||'')"></div>
        </div>
      </section>

      <!-- ===== STUDENTS ===== -->
      <section v-show="cur==='students'" class="body pad">
        <div class="card">
          <h3>👨‍🎓 الطلاب</h3>
          <div v-if="studLoading" class="empty">⏳ تحميل...</div>
          <div v-else-if="!students.length" class="empty">لا يوجد طلاب</div>
          <div v-else class="list-col">
            <div v-for="s in students" :key="s.id" class="list-item">
              <div style="flex:1">
                <h4>{{ s.full_name }}</h4>
                <div class="meta">
                  <span v-if="s.grade">🎓 {{ s.grade }}</span>
                  <span v-if="s.learning_style">🧠 {{ {visual:'بصري',auditory:'سمعي',kinesthetic:'حركي'}[s.learning_style]||s.learning_style }}</span>
                  <span>🔥 {{ s.streak_count||0 }} يوم</span>
                  <span>⭐ {{ s.stars_count||0 }}</span>
                </div>
              </div>
              <button class="btn-s" @click="viewStudentProgress(s.id)">التقدم</button>
            </div>
          </div>
        </div>
        <div v-if="studentProgress" class="card mt">
          <div class="row-sb">
            <h3>{{ studentProgress.student?.full_name }}</h3>
            <button class="btn-o" @click="studentProgress=null">✕</button>
          </div>
          <div class="stats-grid">
            <div class="sc"><div class="sn">🔥 {{ studentProgress.streak?.current_streak||0 }}</div><div class="sl">أيام متتالية</div></div>
            <div class="sc"><div class="sn">💬 {{ studentProgress.total_conversations||0 }}</div><div class="sl">محادثات</div></div>
            <div class="sc"><div class="sn">📝 {{ studentProgress.test_results?.length||0 }}</div><div class="sl">اختبارات</div></div>
          </div>
        </div>
      </section>

      <!-- ===== PPT GENERATOR ===== -->
      <section v-show="cur==='ppt'" class="body pad">
        <div class="card">
          <h3>📊 توليد عرض PowerPoint</h3>
          <p style="color:var(--t2);font-size:13px;margin:0 0 16px">أدخل معلومات الكتاب وسيولّد الذكاء الاصطناعي مخططاً احترافياً للعرض</p>
          <div class="col-gap">
            <input v-model="pptTitle" class="inp" placeholder="عنوان الكتاب / الدرس *" />
            <input v-model="pptSubject" class="inp" placeholder="المادة الدراسية *" />
            <textarea v-model="pptContent" class="inp" rows="4" placeholder="محتوى الكتاب (اختياري — الصفحات الأولى)"></textarea>
            <button class="btn-p" @click="genPPT" :disabled="pptLoading||!pptTitle||!pptSubject">
              {{ pptLoading?'⏳ جاري التوليد...':'✨ توليد المخطط' }}
            </button>
          </div>
          <div v-if="pptHtml" class="result-box" style="margin-top:16px">
            <div style="display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap">
              <button class="btn-s" @click="downloadPpt">⬇ تحميل HTML</button>
              <button class="btn-s" @click="openPptNewTab">🔗 فتح في نافذة جديدة</button>
              <button class="btn-s" @click="copyText(pptResult)">📋 نسخ JSON</button>
            </div>
            <iframe :srcdoc="pptHtml"
                    style="width:100%;height:600px;border:2px solid var(--accent);border-radius:16px;background:#0f172a"
                    sandbox="allow-scripts allow-same-origin allow-popups">
            </iframe>
            <p style="color:var(--t2);font-size:12px;margin-top:8px">💡 استخدم أزرار التنقل أو ← → بلوحة المفاتيح، أو زر ملء الشاشة</p>
          </div>
          <div v-if="pptSlides.length" class="result-box" style="margin-top:16px">
            <h4 style="color:var(--accent);margin-bottom:8px">📋 الشرائح كنص:</h4>
            <div v-for="slide in pptSlides" :key="slide.slide" class="ppt-slide">
              <div class="ppt-num">شريحة {{ slide.slide || (pptSlides.indexOf(slide)+1) }}</div>
              <div class="ppt-title">{{ slide.title }}</div>
              <ul class="ppt-points">
                <li v-for="pt in (slide.points || slide.bullets || [])" :key="pt">{{ pt }}</li>
              </ul>
              <div v-if="slide.notes" class="ppt-notes">💡 {{ slide.notes }}</div>
            </div>
          </div>
          <div v-else-if="pptResult && !pptHtml" class="result-box">
            <pre class="code-block">{{ pptResult }}</pre>
          </div>
        </div>
      </section>

      <!-- ===== AI CHAT ===== -->
      <section v-show="cur==='chat'" class="body">
        <div class="chat-area">
          <div class="messages" ref="chatEl">
            <div v-if="!chatMsgs.length" class="chat-welcome">
              <div style="font-size:48px;margin-bottom:14px">🤖</div>
              <h3>مساعد المعلم الذكي</h3>
              <p style="color:var(--t2)">اسأل بلهجتك — الـ AI يرد بنفس اللهجة. ويمكنك إرسال صور وملفات 📎</p>
              <div class="quick-btns">
                <button v-for="q in tQuickQs" :key="q" class="quick-btn" @click="sendTeacherMsg(q)">{{ q }}</button>
              </div>
            </div>
            <div v-for="(msg,i) in chatMsgs" :key="i" :class="['msg',msg.role]">
              <div class="msg-bubble">
                <span class="msg-icon">{{ msg.role==='user'?'👤':'🤖' }}</span>
                <div class="msg-text" v-html="fmt(msg.content)"></div>
              </div>
            </div>
            <div v-if="chatThinking" class="msg assistant"><div class="msg-bubble"><span class="msg-icon">🤖</span><div class="dots"><span></span><span></span><span></span></div></div></div>
          </div>
          <div v-if="tAttachedFile" class="attach-chip">
            <span>📎 {{ tAttachedFile.name }}</span>
            <button @click="clearTAttach">✕</button>
          </div>
          <div class="input-row">
            <input type="file" ref="tFileInputEl" accept="image/*,.pdf,.txt,.docx" @change="onTFileAttach" style="display:none" />
            <button class="attach-btn" @click="tFileInputEl.click()" title="إرفاق ملف أو صورة">📎</button>
            <textarea v-model="chatInput" rows="2" placeholder="اكتب سؤالك للمساعد الذكي..."
              @keydown.enter.exact.prevent="sendTeacherMsg()" @keydown.enter.shift.exact="chatInput+='\n'"></textarea>
            <button class="send-btn" @click="sendTeacherMsg()" :disabled="(!chatInput.trim()&&!tAttachedFile)||chatThinking">➤</button>
          </div>
        </div>
      </section>

      <!-- ===== VIDEO SCRIPT ===== -->
      <section v-show="cur==='video'" class="body pad">
        <div class="card">
          <h3>🎬 توليد سكريبت فيديو تعليمي</h3>
          <p style="color:var(--t2);font-size:13px;margin:0 0 16px">المدة من 30 ثانية حتى 10 دقائق</p>
          <div class="col-gap">
            <input v-model="vidTopic" class="inp" placeholder="موضوع الفيديو *" />
            <input v-model="vidSubject" class="inp" placeholder="المادة الدراسية" />
            <div>
              <p style="color:var(--t2);font-size:13px;margin:0 0 6px">المدة: {{ formatDur(vidSeconds) }}</p>
              <input type="range" v-model.number="vidSeconds" min="30" max="600" step="30" style="width:100%;accent-color:var(--accent)" />
              <div style="display:flex;justify-content:space-between;color:var(--t2);font-size:12px;margin-top:4px"><span>30 ثانية</span><span>10 دقائق</span></div>
            </div>
            <button class="btn-p" @click="genVid" :disabled="vidLoading||!vidTopic">
              {{ vidLoading ? '⏳ جاري التوليد...' : '✨ توليد السكريبت' }}
            </button>
          </div>
          <div v-if="vidScript" class="result-box" style="margin-top:20px">
            <div style="background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:20px;color:var(--t2);font-size:14px;line-height:1.8;white-space:pre-wrap;max-height:500px;overflow-y:auto" v-html="fmt(vidScript)"></div>
            <button class="btn-s" style="margin-top:10px" @click="copyText(vidScript)">📋 نسخ</button>
          </div>
        </div>
      </section>

      <!-- ===== IMAGE GEN ===== -->
      <section v-show="cur==='image'" class="body pad">
        <div class="card">
          <h3>🎨 توليد الصور التعليمية</h3>
          <div class="col-gap">
            <textarea v-model="imgPrompt" class="inp" rows="3" placeholder="وصف الصورة المطلوبة..."></textarea>
            <button class="btn-p" @click="genImg" :disabled="imgLoading||!imgPrompt.trim()">{{ imgLoading?'⏳...':'✨ توليد' }}</button>
          </div>
          <div v-if="imgError" style="color:#f87171;font-size:13px;margin-top:12px">{{ imgError }}</div>
          <div v-if="genImage" style="margin-top:20px;text-align:center">
            <img :src="`data:image/png;base64,${genImage}`" style="max-width:100%;border-radius:12px" />
            <br><a :href="`data:image/png;base64,${genImage}`" download="morix.png" class="btn-s" style="display:inline-block;margin-top:10px">⬇ تحميل</a>
          </div>
        </div>
      </section>

      <!-- ============ 1️⃣ خطة درس ذكية ============ -->
      <section v-show="cur==='lesson_plan'" class="body pad">
        <div class="card">
          <h3>📋 مولد خطط الدروس التكيفي</h3>
          <input v-model="lp.topic" placeholder="موضوع الدرس" class="memorix-input" style="width:100%;margin-bottom:8px" />
          <input v-model="lp.grade" placeholder="المرحلة (مثال: الصف الخامس)" class="memorix-input" style="width:100%;margin-bottom:8px" />
          <input v-model.number="lp.duration_minutes" type="number" placeholder="المدة بالدقائق" class="memorix-input" style="width:100%;margin-bottom:8px" />
          <textarea v-model="lp.objectives" placeholder="النتائج المرجوة (اختياري)" rows="3" class="memorix-input" style="width:100%;margin-bottom:8px"></textarea>
          <button class="btn-primary" :disabled="lpLoading" @click="genLessonPlan">{{ lpLoading?'⏳ يولّد...':'🚀 ولّد الخطة' }}</button>
          <div v-if="lpResult" class="card mt" style="margin-top:16px">
            <h4 style="color:var(--accent)">{{ lpResult.title || 'الخطة' }}</h4>
            <div v-if="lpResult.objectives"><b>🎯 الأهداف:</b><ul><li v-for="o in lpResult.objectives" :key="o">{{o}}</li></ul></div>
            <div v-if="lpResult.warm_up"><b>🔥 التمهيد:</b><p>{{ lpResult.warm_up }}</p></div>
            <div v-if="lpResult.main_activities"><b>📚 الأنشطة الرئيسية:</b>
              <div v-for="(a,i) in lpResult.main_activities" :key="i" style="background:var(--card);padding:8px;border-radius:6px;margin:6px 0">
                <b>{{a.name}}</b> — {{a.duration}} دقيقة<br><span style="color:var(--t2)">{{a.description}}</span>
              </div>
            </div>
            <div v-if="lpResult.assessment"><b>✅ التقييم:</b><p>{{ lpResult.assessment }}</p></div>
            <div v-if="lpResult.discussion_questions"><b>❓ أسئلة نقاشية:</b><ul><li v-for="q in lpResult.discussion_questions" :key="q">{{q}}</li></ul></div>
            <div v-if="lpResult.homework"><b>🏠 الواجب:</b><p>{{ lpResult.homework }}</p></div>
            <div v-if="lpResult.materials"><b>🧰 المواد:</b><p>{{ lpResult.materials.join(' • ') }}</p></div>
            <pre v-if="lpResult.raw" style="white-space:pre-wrap">{{ lpResult.raw }}</pre>
          </div>
        </div>
      </section>

      <!-- ============ 2️⃣ محول الوسائط ============ -->
      <section v-show="cur==='multimedia'" class="body pad">
        <div class="card">
          <h3>🔄 محول الوسائط المتعددة</h3>
          <textarea v-model="mm.text" rows="6" placeholder="ألصق نص الدرس هنا..." class="memorix-input" style="width:100%;margin-bottom:8px"></textarea>
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
            <button v-for="m in [{k:'bullets',l:'📝 نقاط'},{k:'slides',l:'🎯 شرائح'},{k:'quiz',l:'❓ اختبار'},{k:'mindmap',l:'🧠 خريطة'}]"
                    :key="m.k" class="btn-s" :class="{active: mm.mode===m.k}" @click="mm.mode=m.k"
                    :style="{background: mm.mode===m.k?'var(--accent)':'var(--card)'}">{{ m.l }}</button>
          </div>
          <button class="btn-primary" :disabled="mmLoading" @click="convertMM">{{ mmLoading?'⏳':'🚀 حوّل' }}</button>
          <div v-if="mmResult" class="card mt" style="margin-top:16px">
            <pre v-if="typeof mmResult==='string'" style="white-space:pre-wrap;color:var(--text)">{{ mmResult }}</pre>
            <div v-else>
              <div v-if="mmResult.slides"><h4>🎯 الشرائح</h4>
                <div v-for="(s,i) in mmResult.slides" :key="i" style="background:var(--card);padding:10px;border-radius:8px;margin:6px 0">
                  <b>{{i+1}}. {{s.title}}</b><ul><li v-for="b in s.bullets" :key="b">{{b}}</li></ul>
                </div>
              </div>
              <div v-if="mmResult.questions"><h4>❓ الأسئلة</h4>
                <div v-for="(q,i) in mmResult.questions" :key="i" style="background:var(--card);padding:10px;border-radius:8px;margin:6px 0">
                  <b>{{i+1}}. {{q.q}}</b>
                  <ul><li v-for="(o,j) in q.options" :key="j" :style="{color: j===q.correct?'#10b981':'var(--text)'}">{{o}}<span v-if="j===q.correct"> ✓</span></li></ul>
                </div>
              </div>
              <div v-if="mmResult.central"><h4>🧠 خريطة المفاهيم: {{ mmResult.central }}</h4>
                <div v-for="(b,i) in mmResult.branches" :key="i" style="background:var(--card);padding:10px;border-radius:8px;margin:6px 0">
                  <b>🌿 {{b.label}}</b><ul><li v-for="s in b.sub" :key="s">{{s}}</li></ul>
                </div>
              </div>
              <pre v-if="mmResult.raw" style="white-space:pre-wrap">{{ mmResult.raw }}</pre>
            </div>
          </div>
        </div>
      </section>

      <!-- ============ 3️⃣ تصميم أنشطة ============ -->
      <section v-show="cur==='activity'" class="body pad">
        <div class="card">
          <h3>🎯 مساعد تصميم الأنشطة الصفية</h3>
          <input v-model="act.topic" placeholder="موضوع النشاط" class="memorix-input" style="width:100%;margin-bottom:8px" />
          <input v-model.number="act.student_count" type="number" placeholder="عدد الطلاب" class="memorix-input" style="width:100%;margin-bottom:8px" />
          <label style="display:block;margin-bottom:8px;color:var(--text)"><input type="checkbox" v-model="act.has_internet" /> يوجد إنترنت متاح</label>
          <select v-model="act.activity_type" class="memorix-input" style="width:100%;margin-bottom:8px">
            <option value="أي">أي نوع</option>
            <option value="حركي">حركي</option>
            <option value="جماعي">جماعي</option>
            <option value="فردي">فردي</option>
          </select>
          <textarea v-model="act.constraints" placeholder="قيود إضافية..." rows="2" class="memorix-input" style="width:100%;margin-bottom:8px"></textarea>
          <button class="btn-primary" :disabled="actLoading" @click="genActivity">{{ actLoading?'⏳':'💡 اقترح أنشطة' }}</button>
          <div v-if="actResult?.activities" class="mt" style="margin-top:16px">
            <div v-for="(a,i) in actResult.activities" :key="i" class="card" style="margin-bottom:8px">
              <h4 style="color:var(--accent)">{{i+1}}. {{a.name}} ({{a.duration_minutes}} دقيقة)</h4>
              <p><b>🧰 المواد:</b> {{ (a.materials||[]).join(' • ') }}</p>
              <ol><li v-for="s in a.steps" :key="s">{{s}}</li></ol>
              <p><b>🎯 المخرجات:</b> {{ (a.learning_outcomes||[]).join(' • ') }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- ============ 4️⃣ صياغة رسائل ============ -->
      <section v-show="cur==='compose'" class="body pad">
        <div class="card">
          <h3>✉️ مساعد صياغة الرسائل</h3>
          <select v-model="cm.recipient" class="memorix-input" style="width:100%;margin-bottom:8px">
            <option value="ولي الأمر">ولي الأمر</option>
            <option value="الإدارة">الإدارة</option>
            <option value="زميل معلم">زميل معلم</option>
          </select>
          <select v-model="cm.tone" class="memorix-input" style="width:100%;margin-bottom:8px">
            <option value="ودودة">ودودة</option>
            <option value="رسمية">رسمية</option>
            <option value="حازمة">حازمة</option>
          </select>
          <input v-model="cm.student_name" placeholder="اسم الطالب (اختياري)" class="memorix-input" style="width:100%;margin-bottom:8px" />
          <textarea v-model="cm.purpose" rows="2" placeholder="غرض الرسالة..." class="memorix-input" style="width:100%;margin-bottom:8px"></textarea>
          <textarea v-model="cm.notes" rows="3" placeholder="ملاحظات إضافية..." class="memorix-input" style="width:100%;margin-bottom:8px"></textarea>
          <button class="btn-primary" :disabled="cmLoading" @click="composeMsg">{{ cmLoading?'⏳':'✍️ اكتب الرسالة' }}</button>
          <div v-if="cmResult" class="card mt" style="margin-top:16px;white-space:pre-wrap;line-height:1.8">{{ cmResult }}</div>
        </div>
      </section>

      <!-- ============ 5️⃣ تقارير ذكية ============ -->
      <section v-show="cur==='feedback'" class="body pad">
        <div class="card">
          <h3>📝 أتمتة التقارير التربوية</h3>
          <input v-model="fb.student_name" placeholder="اسم الطالب" class="memorix-input" style="width:100%;margin-bottom:8px" />
          <input v-model="fb.subject" placeholder="المادة" class="memorix-input" style="width:100%;margin-bottom:8px" />
          <textarea v-model="fb.strengths" rows="2" placeholder="نقاط القوة (اكتب بسرعة، AI ينظمها)" class="memorix-input" style="width:100%;margin-bottom:8px"></textarea>
          <textarea v-model="fb.weaknesses" rows="2" placeholder="نقاط الضعف (اكتب بسرعة، AI ينظمها)" class="memorix-input" style="width:100%;margin-bottom:8px"></textarea>
          <button class="btn-primary" :disabled="fbLoading" @click="genFeedback">{{ fbLoading?'⏳':'📋 ولّد التقرير' }}</button>
          <div v-if="fbResult" class="card mt" style="margin-top:16px;white-space:pre-wrap;line-height:1.8">{{ fbResult }}</div>
        </div>
      </section>

      <!-- ============ 6️⃣ تحليل الأداء ============ -->
      <section v-show="cur==='insights'" class="body pad">
        <div class="card">
          <h3>📊 محلل بيانات الأداء</h3>
          <button class="btn-primary" :disabled="insLoading" @click="loadInsights">{{ insLoading?'⏳':'🔍 حلّل الآن' }}</button>
          <div v-if="insights" style="margin-top:16px">
            <div v-if="insights.alert" style="padding:12px;background:rgba(251,191,36,.15);border:1px solid #fbbf24;border-radius:8px;margin-bottom:12px;color:#fbbf24">
              {{ insights.alert }}
            </div>
            <div class="stats-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px">
              <div class="card"><b>👥 الطلاب</b><div style="font-size:24px">{{ insights.total_students }}</div></div>
              <div class="card"><b>📊 المتوسط</b><div style="font-size:24px">{{ insights.avg_score }}%</div></div>
              <div class="card"><b>⚠️ مواضيع ضعف</b><div style="font-size:24px">{{ insights.weak_topics?.length || 0 }}</div></div>
              <div class="card"><b>✅ مواضيع قوة</b><div style="font-size:24px">{{ insights.strong_topics?.length || 0 }}</div></div>
            </div>
            <div v-if="insights.weak_topics?.length" class="mt" style="margin-top:12px">
              <h4 style="color:#ef4444">⚠️ نقاط الضعف</h4>
              <div v-for="t in insights.weak_topics" :key="t.topic" class="card" style="margin:4px 0">
                {{ t.topic }} — متوسط: <b>{{ t.avg }}%</b>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ============ 7️⃣ تبسيط المحتوى ============ -->
      <section v-show="cur==='simplify'" class="body pad">
        <div class="card">
          <h3>🔍 مبسط المحتوى</h3>
          <textarea v-model="sm.text" rows="5" placeholder="النص المراد تبسيطه..." class="memorix-input" style="width:100%;margin-bottom:8px"></textarea>
          <select v-model="sm.level" class="memorix-input" style="width:100%;margin-bottom:8px">
            <option value="beginner">🟢 مبتدئ (صعوبات تعلم)</option>
            <option value="intermediate">🟡 متوسط</option>
            <option value="advanced">🔴 متقدم</option>
          </select>
          <button class="btn-primary" :disabled="smLoading" @click="simplify">{{ smLoading?'⏳':'✨ بسّط' }}</button>
          <div v-if="smResult" class="card mt" style="margin-top:16px;white-space:pre-wrap;line-height:1.8">{{ smResult }}</div>
        </div>
      </section>

      <!-- ============ 8️⃣ تعلم متمايز ============ -->
      <section v-show="cur==='differentiate'" class="body pad">
        <div class="card">
          <h3>🌈 استراتيجيات التعلم المتمايز</h3>
          <input v-model="diff.concept" placeholder="المفهوم التعليمي" class="memorix-input" style="width:100%;margin-bottom:8px" />
          <button class="btn-primary" :disabled="diffLoading" @click="genDiff">{{ diffLoading?'⏳':'🎨 اقترح طرقاً' }}</button>
          <div v-if="diffResult" class="mt" style="margin-top:16px;display:grid;gap:8px">
            <div v-if="diffResult.visual" class="card" style="border-right:4px solid #6366f1">
              <h4>👁️ بصري</h4>
              <p><b>الأسلوب:</b> {{ diffResult.visual.approach }}</p>
              <p><b>النشاط:</b> {{ diffResult.visual.activity }}</p>
              <p><b>الأدوات:</b> {{ (diffResult.visual.tools||[]).join(' • ') }}</p>
            </div>
            <div v-if="diffResult.auditory" class="card" style="border-right:4px solid #10b981">
              <h4>👂 سمعي</h4>
              <p><b>الأسلوب:</b> {{ diffResult.auditory.approach }}</p>
              <p><b>النشاط:</b> {{ diffResult.auditory.activity }}</p>
              <p><b>الأدوات:</b> {{ (diffResult.auditory.tools||[]).join(' • ') }}</p>
            </div>
            <div v-if="diffResult.kinesthetic" class="card" style="border-right:4px solid #f59e0b">
              <h4>✋ حركي</h4>
              <p><b>الأسلوب:</b> {{ diffResult.kinesthetic.approach }}</p>
              <p><b>النشاط:</b> {{ diffResult.kinesthetic.activity }}</p>
              <p><b>الأدوات:</b> {{ (diffResult.kinesthetic.tools||[]).join(' • ') }}</p>
            </div>
            <pre v-if="diffResult.raw" style="white-space:pre-wrap">{{ diffResult.raw }}</pre>
          </div>
        </div>
      </section>

      <!-- ============ 9️⃣ مدرب تربوي ============ -->
      <section v-show="cur==='coach'" class="body pad">
        <div class="card">
          <h3>🧠 الموجه التربوي الذكي</h3>
          <textarea v-model="coachInput" rows="4" placeholder="اوصف التحدي الصفي..." class="memorix-input" style="width:100%;margin-bottom:8px"></textarea>
          <button class="btn-primary" :disabled="coachLoading" @click="askCoach">{{ coachLoading?'⏳':'💬 احصل على نصيحة' }}</button>
          <div v-if="coachAdvice" class="card mt" style="margin-top:16px;white-space:pre-wrap;line-height:1.8">{{ coachAdvice }}</div>
        </div>
      </section>

      <!-- ============ 🔟 أبحاث تربوية ============ -->
      <section v-show="cur==='research'" class="body pad">
        <div class="card">
          <h3>📰 ملخصات الأبحاث التربوية</h3>
          <button class="btn-primary" :disabled="rdLoading" @click="loadResearch">{{ rdLoading?'⏳':'📡 احصل على ملخصات هذا الأسبوع' }}</button>
          <div v-if="rdResult?.digest?.length" class="mt" style="margin-top:16px">
            <div v-for="(r,i) in rdResult.digest" :key="i" class="card" style="margin-bottom:8px">
              <h4 style="color:var(--accent)">{{i+1}}. {{r.title}}</h4>
              <p style="color:var(--text)">{{r.summary}}</p>
              <p style="color:#10b981"><b>💡 نصيحة:</b> {{r.actionable_tip}}</p>
              <small style="color:var(--t2)">{{r.source_type}}</small>
            </div>
          </div>
          <pre v-else-if="rdResult?.raw" style="white-space:pre-wrap;margin-top:16px">{{ rdResult.raw }}</pre>
        </div>
      </section>

      <!-- ============ 1️⃣1️⃣ مكتبة قوالب ============ -->
      <section v-show="cur==='prompts'" class="body pad">
        <div class="card">
          <h3>📚 مكتبة قوالب الـ Prompts</h3>
          <p style="color:var(--t2);margin-bottom:12px">انسخ القالب وعدّل ما بين [الأقواس] ثم استخدمه في مساعد AI</p>
          <button v-if="!promptCats.length" class="btn-primary" :disabled="plLoading" @click="loadPrompts">{{ plLoading?'⏳':'📥 حمّل المكتبة' }}</button>
          <div v-for="cat in promptCats" :key="cat.name" style="margin-top:16px">
            <h4 style="color:var(--accent)">{{cat.name}}</h4>
            <div v-for="p in cat.prompts" :key="p.title" class="card" style="margin:6px 0;background:var(--card)">
              <b>{{p.title}}</b>
              <p style="color:var(--t2);font-size:13px;margin:6px 0">{{p.template}}</p>
              <button class="btn-s" @click="copyPrompt(p.template)">📋 نسخ</button>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 📚 المكتبة الرقمية (داخل المنصة) ===== -->
      <section v-show="cur==='library'" class="body pad">
        <div class="card">
          <h3>📚 المكتبة الرقمية المجانية للمعلمين</h3>
          <p style="color:var(--t2);margin-bottom:12px">المراجع والكتب التربوية تفتح داخل المنصة</p>
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
            <button v-for="src in libSources" :key="src.url"
                    @click="libUrl = src.url"
                    class="btn-s"
                    :style="{background: libUrl===src.url?'var(--accent)':'var(--card)',padding:'8px 14px'}">
              {{ src.icon }} {{ src.label }}
            </button>
          </div>
          <div style="background:var(--card);border-radius:12px;overflow:hidden;border:1px solid var(--border)">
            <iframe :src="'/api/v1/proxy?url=' + encodeURIComponent(libUrl)"
                    style="width:100%;height:80vh;border:none;background:#fff"
                    sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
                    referrerpolicy="no-referrer"
                    loading="lazy">
            </iframe>
          </div>
          <p style="color:var(--t2);font-size:12px;margin-top:8px">💡 المكتبة تفتح داخل المنصة عبر بروكسي Morix</p>
        </div>
      </section>

      <!-- ===== 📓 دفتري الذكي (NotebookLM-like) ===== -->
      <section v-show="cur==='notebook'" class="body pad">
        <div class="card">
          <h3>📓 دفتري الذكي للمعلم — Morix Notebook</h3>
          <p style="color:var(--t2);margin-bottom:12px">ارفع المنهج/المرجع وولّد ملخصات، أسئلة، خرائط، وبودكاست AI داخل المنصة</p>
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
            <button @click="nbTab='upload'" class="btn-s" :style="{background:nbTab==='upload'?'var(--accent)':'var(--card)',padding:'8px 14px'}">📤 رفع ملف</button>
            <button @click="nbTab='ask'" :disabled="!nbFileText" class="btn-s" :style="{background:nbTab==='ask'?'var(--accent)':'var(--card)',padding:'8px 14px',opacity:nbFileText?1:0.5}">💬 اسأل عن الملف</button>
            <button @click="nbTab='generate'" :disabled="!nbFileText" class="btn-s" :style="{background:nbTab==='generate'?'var(--accent)':'var(--card)',padding:'8px 14px',opacity:nbFileText?1:0.5}">✨ ولّد محتوى تعليمي</button>
          </div>

          <div v-if="nbTab==='upload'" class="card" style="background:var(--card)">
            <input ref="nbFileInput" type="file" accept=".pdf,.txt,.md" @change="onNbFileUpload" style="display:none" />
            <button @click="$refs.nbFileInput?.click()" class="btn-p" style="width:100%;padding:24px;font-size:16px">
              📤 اختر ملف PDF / TXT / MD
            </button>
            <div v-if="nbFileName" style="margin-top:12px;padding:12px;background:var(--bg3);border-radius:8px;border:1px solid var(--accent)">
              ✅ <b>{{ nbFileName }}</b> — جاهز ({{ Math.round(nbFileText.length/1000) }}K حرف)
            </div>
          </div>

          <div v-if="nbTab==='ask'" class="card" style="background:var(--card)">
            <div style="max-height:50vh;overflow-y:auto;padding:8px;margin-bottom:12px">
              <div v-for="(m,i) in nbChat" :key="i" :style="{padding:'10px',marginBottom:'8px',borderRadius:'8px',background: m.role==='user'?'rgba(99,102,241,.15)':'var(--bg3)',borderRight: m.role==='user'?'3px solid var(--accent)':'3px solid #10b981'}">
                <b>{{ m.role==='user'?'🙋 أنت':'🤖 Morix' }}:</b>
                <div style="white-space:pre-wrap;margin-top:4px">{{ m.text }}</div>
              </div>
            </div>
            <div style="display:flex;gap:8px">
              <input v-model="nbInput" @keyup.enter="askNb" placeholder="اسأل سؤالاً عن الملف..." class="inp" style="flex:1" />
              <button @click="askNb" :disabled="nbAsking || !nbInput.trim()" class="btn-p">{{ nbAsking?'⏳':'➤' }}</button>
            </div>
          </div>

          <div v-if="nbTab==='generate'" class="card" style="background:var(--card)">
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px;margin-bottom:12px">
              <button @click="genNb('summary')" :disabled="nbGenLoading" class="btn-p">📝 ملخص الكتاب</button>
              <button @click="genNb('lesson_plan')" :disabled="nbGenLoading" class="btn-p">📋 خطة درس من الكتاب</button>
              <button @click="genNb('mcq_test')" :disabled="nbGenLoading" class="btn-p">📝 اختبار MCQ</button>
              <button @click="genNb('worksheet')" :disabled="nbGenLoading" class="btn-p">📄 ورقة عمل</button>
              <button @click="genNb('mindmap')" :disabled="nbGenLoading" class="btn-p">🧠 خريطة ذهنية</button>
              <button @click="genNb('podcast')" :disabled="nbGenLoading" class="btn-p">🎙️ سكربت بودكاست</button>
            </div>
            <div v-if="nbGenLoading" style="text-align:center;padding:20px;color:var(--t2)">⏳ جاري التوليد...</div>
            <div v-if="nbGenResult" style="padding:16px;background:var(--bg3);border-radius:8px;white-space:pre-wrap;line-height:1.8;max-height:60vh;overflow-y:auto">{{ nbGenResult }}</div>
          </div>
        </div>
      </section>

      <!-- ===== SETTINGS ===== -->
      <section v-show="cur==='settings'" class="body pad">
        <div class="settings-grid">
          <div class="card">
            <h3>👤 معلومات الحساب</h3>
            <div class="avatar-section">
              <div style="position:relative;cursor:pointer" @click="tAvatarInput?.click()">
                <img v-if="tSettings.avatar_url" :src="tSettings.avatar_url" class="av-preview" />
                <div v-else class="av-big">{{ firstName[0] }}</div>
                <div class="av-overlay">📷</div>
              </div>
              <div style="flex:1">
                <p style="color:var(--t2);font-size:12px;margin:0 0 6px">اضغط على الصورة لرفع صورة من جهازك</p>
                <input ref="tAvatarInput" type="file" accept="image/*" style="display:none" @change="onTAvatarUpload" />
                <button class="btn-s" style="width:100%" @click="tAvatarInput?.click()">📷 رفع صورة من الجهاز</button>
              </div>
            </div>
            <div class="info-row"><span>الاسم</span><b>{{ tSettings.full_name }}</b></div>
            <div class="info-row"><span>الإيميل</span><b>{{ tSettings.email }}</b></div>
            <div class="info-row"><span>الدور</span><b>معلم</b></div>
          </div>
          <div class="card">
            <h3>🎨 المظهر</h3>
            <p style="color:var(--t2);font-size:13px;margin:0 0 10px">الثيم</p>
            <div class="theme-row">
              <button :class="['t-btn',{active:tSettings.theme==='dark'}]" @click="tSettings.theme='dark';saveTeacherSettings()">🌑 داكن</button>
              <button :class="['t-btn',{active:tSettings.theme==='light'}]" @click="tSettings.theme='light';saveTeacherSettings()">☀️ فاتح</button>
              <button :class="['t-btn',{active:tSettings.theme==='library'}]" @click="tSettings.theme='library';saveTeacherSettings()">📚 مكتبة</button>
            </div>
            <p style="color:var(--t2);font-size:13px;margin:16px 0 8px">السطوع {{ tSettings.brightness }}%</p>
            <input type="range" v-model.number="tSettings.brightness" min="40" max="100" step="5" @change="saveTeacherSettings" style="width:100%;accent-color:var(--accent)" />
          </div>
          <div class="card">
            <h3>🌐 اللغة</h3>
            <select v-model="tSettings.language" @change="saveTeacherSettings" class="inp">
              <option value="ar">العربية</option><option value="en">English</option>
            </select>
          </div>
        </div>
        <p v-if="settingsMsg" style="color:#4ade80;font-size:13px;margin-top:10px;text-align:center">{{ settingsMsg }}</p>
      </section>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import { useRouter } from 'vue-router'
import { teacherAPI, aiAPI } from '../api.js'
import { useTheme } from '../composables/useTheme.js'

const auth = useAuthStore()
const router = useRouter()
const firstName = ref(auth.user?.full_name?.split(' ')?.[0] || 'معلم')

// Settings
const tSettings = ref({ theme:'dark', brightness:100, language:'ar', notifications_enabled:true, avatar_url:'', email:'', full_name:'' })
useTheme(tSettings)
const settingsMsg = ref('')

const sections = [
  {id:'overview',icon:'🏠',label:'نظرة عامة'},
  {id:'homework',icon:'📚',label:'الواجبات'},
  {id:'tests',icon:'📝',label:'الاختبارات'},
  {id:'worksheets',icon:'📋',label:'أوراق العمل'},
  {id:'students',icon:'👨‍🎓',label:'الطلاب'},
  {id:'ppt',icon:'📊',label:'توليد PPT'},
  {id:'video',icon:'🎬',label:'سكريبت فيديو'},
  {id:'chat',icon:'💬',label:'مساعد AI'},
  {id:'image',icon:'🎨',label:'توليد صور'},
  {id:'lesson_plan',icon:'📋',label:'خطة درس ذكية'},
  {id:'multimedia',icon:'🔄',label:'محول الوسائط'},
  {id:'activity',icon:'🎯',label:'تصميم أنشطة'},
  {id:'compose',icon:'✉️',label:'صياغة رسائل'},
  {id:'feedback',icon:'📝',label:'تقارير ذكية'},
  {id:'insights',icon:'📊',label:'تحليل الأداء'},
  {id:'simplify',icon:'🔍',label:'تبسيط المحتوى'},
  {id:'differentiate',icon:'🌈',label:'تعلم متمايز'},
  {id:'coach',icon:'🧠',label:'مدرب تربوي'},
  {id:'research',icon:'📰',label:'أبحاث تربوية'},
  {id:'prompts',icon:'📚',label:'مكتبة قوالب'},
  {id:'library',icon:'📚',label:'المكتبة الرقمية'},
  {id:'notebook',icon:'📓',label:'NotebookLM'},
  {id:'settings',icon:'⚙️',label:'الإعدادات'},
]

const cur = ref('overview')
const sb = ref(false)

const homework = ref([])
const hwForm = ref(false)
const hwLoading = ref(false)
const hwNew = ref({topic:'',subject:'',grade:'',due_date:''})
const submissions = ref([])

const myTests = ref([])
const testForm = ref(false)
const testLoading = ref(false)
const testNew = ref({title:'',subject:'',grade:'',duration_minutes:60,ai_generate:false,topic:''})

const worksheets = ref([])
const wsForm = ref(false)
const wsLoading = ref(false)
const wsNew = ref({topic:'',subject:'',grade:''})

// Video
const vidTopic = ref('')
const vidSubject = ref('')
const vidSeconds = ref(300)
const vidLoading = ref(false)
const vidScript = ref('')
const activeWs = ref(null)

const students = ref([])
const studLoading = ref(false)
const studentProgress = ref(null)

const pptTitle = ref('')
const pptSubject = ref('')
const pptContent = ref('')
const pptLoading = ref(false)
const pptResult = ref('')
const pptSlides = ref([])

const chatMsgs = ref([])
const chatInput = ref('')
const chatThinking = ref(false)
const chatEl = ref(null)
const tQuickQs = ['كيف أصمم درساً تفاعلياً؟','اقترح 5 أسئلة اختبار','اكتب خطة درس في 30 دقيقة','استراتيجيات لإدارة الفصل']

// Avatar upload
const tAvatarInput = ref(null)

// Teacher chat attachments
const tFileInputEl = ref(null)
const tAttachedFile = ref(null)
const tAttachedBase64 = ref(null)
const tAttachedFileText = ref(null)

const imgPrompt = ref('')
const imgLoading = ref(false)
const genImage = ref(null)
const imgError = ref('')

onMounted(async () => {
  await Promise.all([loadHomework(), loadTests(), loadWorksheets(), loadStudents(), loadTeacherSettings()])
})

async function loadTeacherSettings() {
  try { tSettings.value = { ...tSettings.value, ...(await teacherAPI.getSettings()).data } } catch {}
}
async function saveTeacherSettings() {
  try { await teacherAPI.updateSettings(tSettings.value); settingsMsg.value='✅ تم الحفظ'; setTimeout(()=>{settingsMsg.value=''},2000) } catch {}
}
async function onTAvatarUpload(e) {
  const file = e.target.files?.[0]; if(!file) return
  if(file.size > 500 * 1024) { alert('الصورة أكبر من 500 كيلوبايت — اختر صورة أصغر'); return }
  const reader = new FileReader()
  reader.onload = async (ev) => { tSettings.value.avatar_url = ev.target.result; await saveTeacherSettings() }
  reader.readAsDataURL(file)
  if(tAvatarInput.value) tAvatarInput.value.value = ''
}

async function loadHomework() { try { homework.value=(await teacherAPI.getHomework()).data } catch {} }
async function loadTests() { try { myTests.value=(await teacherAPI.getTests()).data } catch {} }
async function loadWorksheets() { try { worksheets.value=(await teacherAPI.getWorksheets()).data } catch {} }
async function loadStudents() { studLoading.value=true; try { students.value=(await teacherAPI.getStudents()).data } catch {} finally { studLoading.value=false } }

async function createHw() {
  hwLoading.value=true
  try {
    await teacherAPI.createHomework({ ...hwNew.value, ai_generate: true })
    hwForm.value=false; hwNew.value={topic:'',subject:'',grade:'',due_date:''}; await loadHomework()
  } catch {} finally { hwLoading.value=false }
}
async function deleteHw(id) { try { await teacherAPI.deleteHomework(id); await loadHomework() } catch {} }
async function viewSubmissions(id) { try { submissions.value=(await teacherAPI.getSubmissions(id)).data } catch {} }

async function createTest() {
  testLoading.value=true
  try {
    await teacherAPI.createTest({ ...testNew.value, ai_generate: true, title: testNew.value.topic })
    testForm.value=false; testNew.value={topic:'',subject:'',grade:'',duration_minutes:60}; await loadTests()
  } catch {} finally { testLoading.value=false }
}
async function deleteTest(id) { try { await teacherAPI.deleteTest(id); await loadTests() } catch {} }

async function createWs() {
  wsLoading.value=true
  try {
    await teacherAPI.createWorksheet({ ...wsNew.value, ai_generate: true, title: `ورقة عمل — ${wsNew.value.topic}` })
    wsForm.value=false; wsNew.value={topic:'',subject:'',grade:''}; await loadWorksheets()
  } catch {} finally { wsLoading.value=false }
}

async function genVid() {
  vidLoading.value=true; vidScript.value=''
  try { const r=await teacherAPI.generateVideo({topic:vidTopic.value,subject:vidSubject.value,duration_seconds:vidSeconds.value}); vidScript.value=r.data.script }
  catch { vidScript.value='تعذر توليد السكريبت.' }
  finally { vidLoading.value=false }
}

function formatDur(secs) {
  const m=Math.floor(secs/60); const s=secs%60
  if(m===0) return `${s} ثانية`
  if(s===0) return `${m} ${m===1?'دقيقة':'دقائق'}`
  return `${m} ${m===1?'دقيقة':'دقائق'} و${s} ثانية`
}
async function deleteWs(id) { try { await teacherAPI.deleteWorksheet(id); await loadWorksheets() } catch {} }
function viewWs(ws) { activeWs.value=ws }

async function viewStudentProgress(id) { try { studentProgress.value=(await teacherAPI.getStudentProgress(id)).data } catch {} }

async function genPPT() {
  pptLoading.value=true; pptResult.value=''; pptSlides.value=[]; pptHtml.value=''
  try {
    const r = await teacherAPI.generatePPT({title:pptTitle.value,subject:pptSubject.value,content:pptContent.value})
    pptResult.value = typeof r.data.outline === 'string' ? r.data.outline : JSON.stringify(r.data.outline, null, 2)
    pptHtml.value = r.data.html || ''
    // استخراج الشرائح كنص
    try {
      const parsed = typeof r.data.outline === 'string' ? JSON.parse(r.data.outline) : r.data.outline
      pptSlides.value = parsed.slides || (Array.isArray(parsed) ? parsed : [])
    } catch { pptSlides.value = [] }
  }
  catch (e) { pptResult.value='تعذر توليد المخطط. تأكد من صلاحية مفتاح Gemini API.' }
  finally { pptLoading.value=false }
}
const pptHtml = ref('')
function downloadPpt() {
  const blob = new Blob([pptHtml.value], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = `${pptTitle.value || 'morix-presentation'}.html`
  a.click(); URL.revokeObjectURL(url)
}
function openPptNewTab() {
  const w = window.open('', '_blank')
  if (w) { w.document.write(pptHtml.value); w.document.close() }
}

async function onTFileAttach(e) {
  const file = e.target.files?.[0]; if(!file) return
  tAttachedFile.value = file
  tAttachedBase64.value = null; tAttachedFileText.value = null
  if(file.type.startsWith('image/')) {
    const reader = new FileReader()
    reader.onload = ev => { tAttachedBase64.value = ev.target.result.split(',')[1] }
    reader.readAsDataURL(file)
  } else {
    const reader = new FileReader()
    reader.onload = ev => { tAttachedFileText.value = ev.target.result }
    reader.readAsText(file)
  }
  if(tFileInputEl.value) tFileInputEl.value.value = ''
}
function clearTAttach() { tAttachedFile.value=null; tAttachedBase64.value=null; tAttachedFileText.value=null }

async function sendTeacherMsg(text) {
  const m=text||chatInput.value.trim()
  if(!m && !tAttachedFile.value) return
  const displayMsg = m || `📎 ${tAttachedFile.value?.name}`
  const imgB64 = tAttachedBase64.value
  const fileTxt = tAttachedFileText.value
  chatInput.value=''; clearTAttach()
  chatMsgs.value.push({role:'user',content:displayMsg}); chatThinking.value=true
  nextTick(()=>{ if(chatEl.value) chatEl.value.scrollTop=chatEl.value.scrollHeight })
  try {
    const r = await teacherAPI.chat(m || 'حلل هذا الملف/الصورة', imgB64, fileTxt)
    chatMsgs.value.push({role:'assistant',content:r.data.reply})
  }
  catch { chatMsgs.value.push({role:'assistant',content:'حدث خطأ.'}) }
  finally { chatThinking.value=false; nextTick(()=>{ if(chatEl.value) chatEl.value.scrollTop=chatEl.value.scrollHeight }) }
}

async function genImg() {
  imgLoading.value=true; imgError.value=''; genImage.value=null
  try { const r=await aiAPI.generateImage(imgPrompt.value); if(r.data.success) genImage.value=r.data.image; else imgError.value=r.data.message }
  catch { imgError.value='خطأ في التوليد' }
  finally { imgLoading.value=false }
}

function copyText(t) { navigator.clipboard.writeText(t).catch(()=>{}) }
async function doLogout() { await auth.logout(); router.push('/login') }
function fmtDate(d) { return d?new Date(d).toLocaleDateString('ar-SA'):'' }
function fmt(t) {
  if(!t) return ''
  return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>').replace(/\*(.*?)\*/g,'<em>$1</em>')
    .replace(/`(.*?)`/g,'<code>$1</code>').replace(/\n/g,'<br>')
}

// ============================================================
// 🎓 ميزات المعلم الذكية (11 ميزة) — State + Methods
// ============================================================

// 1️⃣ Lesson Plan
const lp = ref({ topic:'', grade:'', duration_minutes:45, objectives:'' })
const lpLoading = ref(false)
const lpResult = ref(null)
async function genLessonPlan() {
  if (!lp.value.topic.trim()) return alert('أدخل موضوع الدرس')
  lpLoading.value = true; lpResult.value = null
  try { lpResult.value = (await teacherAPI.generateLessonPlan(lp.value)).data.plan }
  catch (e) { alert('فشل التوليد: ' + (e.response?.data?.detail || e.message)) }
  lpLoading.value = false
}

// 2️⃣ Multimedia Convert
const mm = ref({ text:'', mode:'bullets' })
const mmLoading = ref(false)
const mmResult = ref(null)
async function convertMM() {
  if (!mm.value.text.trim()) return alert('أدخل النص')
  mmLoading.value = true; mmResult.value = null
  try { mmResult.value = (await teacherAPI.multimediaConvert(mm.value.text, mm.value.mode)).data.data }
  catch (e) { alert('فشل: ' + (e.response?.data?.detail || e.message)) }
  mmLoading.value = false
}

// 3️⃣ Activity Designer
const act = ref({ topic:'', student_count:30, has_internet:true, activity_type:'أي', constraints:'' })
const actLoading = ref(false)
const actResult = ref(null)
async function genActivity() {
  if (!act.value.topic.trim()) return alert('أدخل الموضوع')
  actLoading.value = true; actResult.value = null
  try { actResult.value = (await teacherAPI.designActivity(act.value)).data }
  catch (e) { alert('فشل: ' + (e.response?.data?.detail || e.message)) }
  actLoading.value = false
}

// 4️⃣ Compose Message
const cm = ref({ recipient:'ولي الأمر', tone:'ودودة', purpose:'', student_name:'', notes:'' })
const cmLoading = ref(false)
const cmResult = ref('')
async function composeMsg() {
  if (!cm.value.purpose.trim()) return alert('اكتب غرض الرسالة')
  cmLoading.value = true; cmResult.value = ''
  try { cmResult.value = (await teacherAPI.composeMessage(cm.value)).data.message }
  catch (e) { alert('فشل: ' + (e.response?.data?.detail || e.message)) }
  cmLoading.value = false
}

// 5️⃣ Auto Feedback
const fb = ref({ student_name:'', subject:'', strengths:'', weaknesses:'' })
const fbLoading = ref(false)
const fbResult = ref('')
async function genFeedback() {
  if (!fb.value.strengths.trim() && !fb.value.weaknesses.trim()) return alert('أدخل نقاط القوة أو الضعف')
  fbLoading.value = true; fbResult.value = ''
  try { fbResult.value = (await teacherAPI.autoFeedback(fb.value)).data.report }
  catch (e) { alert('فشل: ' + (e.response?.data?.detail || e.message)) }
  fbLoading.value = false
}

// 6️⃣ Performance Insights
const insights = ref(null)
const insLoading = ref(false)
async function loadInsights() {
  insLoading.value = true
  try { insights.value = (await teacherAPI.getPerformanceInsights()).data }
  catch (e) { alert('فشل: ' + (e.response?.data?.detail || e.message)) }
  insLoading.value = false
}

// 7️⃣ Simplify
const sm = ref({ text:'', level:'beginner' })
const smLoading = ref(false)
const smResult = ref('')
async function simplify() {
  if (!sm.value.text.trim()) return alert('أدخل النص')
  smLoading.value = true; smResult.value = ''
  try { smResult.value = (await teacherAPI.simplifyContent(sm.value.text, sm.value.level)).data.simplified }
  catch (e) { alert('فشل: ' + (e.response?.data?.detail || e.message)) }
  smLoading.value = false
}

// 8️⃣ Differentiated Strategies
const diff = ref({ concept:'' })
const diffLoading = ref(false)
const diffResult = ref(null)
async function genDiff() {
  if (!diff.value.concept.trim()) return alert('أدخل المفهوم')
  diffLoading.value = true; diffResult.value = null
  try { diffResult.value = (await teacherAPI.differentiatedStrategies(diff.value.concept)).data }
  catch (e) { alert('فشل: ' + (e.response?.data?.detail || e.message)) }
  diffLoading.value = false
}

// 9️⃣ Pedagogical Coach
const coachInput = ref('')
const coachLoading = ref(false)
const coachAdvice = ref('')
async function askCoach() {
  if (!coachInput.value.trim()) return alert('اوصف التحدي')
  coachLoading.value = true; coachAdvice.value = ''
  try { coachAdvice.value = (await teacherAPI.pedagogicalCoach(coachInput.value)).data.advice }
  catch (e) { alert('فشل: ' + (e.response?.data?.detail || e.message)) }
  coachLoading.value = false
}

// 🔟 Research Digest
const rdResult = ref(null)
const rdLoading = ref(false)
async function loadResearch() {
  rdLoading.value = true
  try { rdResult.value = (await teacherAPI.researchDigest()).data }
  catch (e) { alert('فشل: ' + (e.response?.data?.detail || e.message)) }
  rdLoading.value = false
}

// 1️⃣1️⃣ Prompt Library
const promptCats = ref([])
const plLoading = ref(false)
async function loadPrompts() {
  plLoading.value = true
  try { promptCats.value = (await teacherAPI.promptLibrary()).data.categories || [] }
  catch (e) { alert('فشل: ' + (e.response?.data?.detail || e.message)) }
  plLoading.value = false
}
function copyPrompt(t) {
  navigator.clipboard?.writeText(t)
  alert('✅ تم نسخ القالب')
}

// 📚 Digital Library + 📓 NotebookLM
const libSources = [
  { label:'مؤسسة هنداوي', icon:'🇪🇬', url:'https://www.hindawi.org/books/' },
  { label:'مكتبة نور', icon:'📖', url:'https://www.noor-book.com/' },
  { label:'الشاملة', icon:'📜', url:'https://shamela.ws/' },
  { label:'Open Library', icon:'🌍', url:'https://openlibrary.org/' },
  { label:'Internet Archive', icon:'🏛️', url:'https://archive.org/details/texts' },
  { label:'ERIC تربوي', icon:'🎓', url:'https://eric.ed.gov/' },
]
const libUrl = ref(libSources[0].url)

// 📓 Morix Notebook (Teacher)
const nbTab = ref('upload')
const nbFileName = ref('')
const nbFileText = ref('')
const nbChat = ref([])
const nbInput = ref('')
const nbAsking = ref(false)
const nbGenLoading = ref(false)
const nbGenResult = ref('')

async function onNbFileUpload(e) {
  const file = e.target.files?.[0]; if (!file) return
  if (file.size > 5 * 1024 * 1024) { alert('الملف أكبر من 5MB'); return }
  nbFileName.value = file.name
  const r = new FileReader()
  r.onload = (ev) => { nbFileText.value = (ev.target.result || '').slice(0, 50000) }
  r.readAsText(file, 'utf-8')
}
async function askNb() {
  if (!nbInput.value.trim() || !nbFileText.value) return
  const q = nbInput.value
  nbChat.value.push({ role:'user', text:q }); nbInput.value=''; nbAsking.value=true
  try {
    const r = await teacherAPI.chat(q, null, nbFileText.value)
    nbChat.value.push({ role:'ai', text: r.data.reply || 'لا يوجد رد' })
  } catch { nbChat.value.push({ role:'ai', text:'❌ فشل' }) }
  nbAsking.value=false
}
async function genNb(type) {
  if (!nbFileText.value) return alert('ارفع ملفاً أولاً')
  const prompts = {
    summary: 'لخص هذا الكتاب/المرجع للمعلم في 10 فقرات منظمة بنقاط الأفكار الرئيسية لكل فصل.',
    lesson_plan: 'استخرج من الملف خطة درس متكاملة (أهداف، تمهيد، أنشطة، تقييم، واجب).',
    mcq_test: 'ولّد اختبار MCQ من 10 أسئلة من محتوى الملف مع الإجابات النموذجية.',
    worksheet: 'صمم ورقة عمل تطبيقية للطلاب من محتوى الملف، تحتوي على 6 تمارين متدرجة.',
    mindmap: 'حول الملف لخريطة ذهنية نصية (الموضوع → الفروع → التفاصيل).',
    podcast: 'اكتب سكربت بودكاست تعليمي مدته 5 دقائق بصوت معلم وضيف يناقشان أهم محتوى الملف.',
  }
  nbGenLoading.value=true; nbGenResult.value=''
  try {
    const r = await teacherAPI.chat(prompts[type], null, nbFileText.value)
    nbGenResult.value = r.data.reply || ''
  } catch { nbGenResult.value = '❌ فشل التوليد' }
  nbGenLoading.value=false
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
.body{flex:1;overflow-y:auto;}.body.pad{padding:24px;}
.card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:24px;}.card h3{color:var(--text);margin:0 0 20px;font-size:16px;}
.mt{margin-top:16px;}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:16px;}
.sc{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px;text-align:center;}
.sn{font-size:22px;font-weight:800;color:var(--text);margin-bottom:4px;}
.sl{color:var(--t2);font-size:12px;}
.row-sb{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;}
.form-box{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:16px;display:flex;flex-direction:column;gap:12px;}
.col-gap{display:flex;flex-direction:column;gap:12px;}
.row-gap{display:flex;gap:10px;flex-wrap:wrap;}
.ai-row{display:flex;align-items:center;}
.toggle-lbl{display:flex;align-items:center;gap:8px;cursor:pointer;color:var(--t2);font-size:14px;}
.toggle-lbl input{accent-color:var(--accent);}
.list-col{display:flex;flex-direction:column;gap:10px;}
.list-item{display:flex;align-items:center;justify-content:space-between;padding:14px;background:var(--bg2);border:1px solid var(--border);border-radius:12px;}
.list-item.clickable{cursor:pointer;transition:border-color .15s;}
.list-item.clickable:hover{border-color:var(--accent);}
.list-item h4{color:var(--text);margin:0 0 4px;}
.meta{display:flex;gap:10px;flex-wrap:wrap;}
.meta span{color:var(--t2);font-size:12px;}
.ai-tag{background:rgba(99,102,241,.2);color:var(--accent);border-radius:4px;padding:1px 6px;}
.empty{text-align:center;padding:40px;color:var(--t2);font-size:14px;}
.chat-area{flex:1;display:flex;flex-direction:column;overflow:hidden;}
.messages{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px;}
.chat-welcome{display:flex;flex-direction:column;align-items:center;padding:48px 20px;}
.chat-welcome h3{color:var(--text);font-size:20px;margin:0 0 8px;}
.quick-btns{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:16px;}
.quick-btn{background:var(--bg2);border:1px solid var(--border);color:var(--t2);border-radius:20px;padding:8px 16px;cursor:pointer;font-size:12px;transition:all .15s;}
.quick-btn:hover{border-color:var(--accent);color:var(--accent);}
.msg{display:flex;}.msg.user{justify-content:flex-start;}.msg.assistant{justify-content:flex-end;}
.msg-bubble{display:flex;align-items:flex-start;gap:10px;max-width:72%;flex-direction:row-reverse;}
.msg.user .msg-bubble{flex-direction:row;}
.msg-icon{font-size:18px;flex-shrink:0;margin-top:4px;}
.msg-text{background:var(--bg2);border:1px solid var(--border);border-radius:14px;padding:12px 16px;color:var(--text);font-size:14px;line-height:1.6;}
.msg.user .msg-text{background:rgba(99,102,241,.2);border-color:rgba(99,102,241,.3);}
.dots{display:flex;gap:4px;padding:12px 16px;align-items:center;}
.dots span{width:8px;height:8px;background:var(--t2);border-radius:50%;animation:bounce 1s infinite;}
.dots span:nth-child(2){animation-delay:.15s}.dots span:nth-child(3){animation-delay:.3s}
@keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
.input-row{display:flex;gap:10px;padding:14px 20px;border-top:1px solid var(--border);background:var(--bg2);align-items:flex-end;}
.input-row textarea{flex:1;background:var(--bg3);border:1px solid var(--border);color:var(--text);border-radius:12px;padding:12px 16px;font-size:14px;resize:none;font-family:inherit;text-align:right;}
.input-row textarea:focus{outline:none;border-color:var(--accent);}
.send-btn{background:var(--accent);color:#fff;border:none;border-radius:12px;width:44px;height:44px;cursor:pointer;font-size:18px;flex-shrink:0;}
.send-btn:disabled{opacity:.5;cursor:not-allowed;}
.result-box{margin-top:20px;}
.code-block{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:20px;color:var(--t2);font-size:13px;line-height:1.7;overflow:auto;max-height:500px;white-space:pre-wrap;}
.inp{width:100%;box-sizing:border-box;background:var(--bg2);border:1px solid var(--border);color:var(--text);border-radius:10px;padding:12px 14px;font-size:14px;font-family:inherit;text-align:right;}
.inp:focus{outline:none;border-color:var(--accent);}
select.inp{cursor:pointer;}textarea.inp{resize:vertical;}
.btn-p{background:var(--accent);color:#fff;border:none;border-radius:10px;padding:11px 18px;cursor:pointer;font-size:14px;font-weight:600;transition:opacity .15s;}
.btn-p:hover:not(:disabled){opacity:.88;}.btn-p:disabled{opacity:.5;cursor:not-allowed;}
.btn-o{background:transparent;border:1px solid var(--border);color:var(--t2);border-radius:10px;padding:11px 18px;cursor:pointer;font-size:14px;}
.btn-o:hover{border-color:var(--accent);color:var(--accent);}
.btn-s{background:var(--bg3);border:1px solid var(--border);color:var(--t2);border-radius:8px;padding:7px 12px;cursor:pointer;font-size:12px;transition:all .15s;}
.btn-s:hover{border-color:var(--accent);color:var(--accent);}
.btn-s.danger{background:rgba(239,68,68,.1);border-color:rgba(239,68,68,.3);color:#f87171;}
code{background:var(--bg3);border-radius:4px;padding:2px 6px;font-size:12px;}
.settings-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;}
.avatar-section{display:flex;align-items:center;gap:14px;margin-bottom:16px;}
.av-preview{width:60px;height:60px;border-radius:50%;object-fit:cover;border:2px solid var(--border);}
.av-big{width:60px;height:60px;min-width:60px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:26px;color:#fff;}
.av-overlay{position:absolute;inset:0;border-radius:50%;background:rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;font-size:18px;opacity:0;transition:opacity .15s;}
.avatar-section>div:first-child:hover .av-overlay{opacity:1;}
.info-row{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--border);color:var(--t2);font-size:13px;}
.info-row b{color:var(--text);}
.theme-row{display:flex;gap:10px;flex-wrap:wrap;}
.t-btn{background:var(--bg3);border:1px solid var(--border);color:var(--t2);border-radius:10px;padding:9px 16px;cursor:pointer;font-size:13px;transition:all .15s;}
.t-btn.active{background:rgba(99,102,241,.2);border-color:var(--accent);color:var(--accent);}
select.inp{cursor:pointer;}
.attach-btn{background:var(--bg3);border:1px solid var(--border);color:var(--t2);border-radius:10px;width:40px;height:40px;cursor:pointer;font-size:16px;flex-shrink:0;transition:all .15s;}
.attach-btn:hover{border-color:var(--accent);color:var(--accent);}
.attach-chip{display:flex;align-items:center;gap:8px;padding:6px 16px;background:rgba(99,102,241,.1);border-top:1px solid var(--border);color:var(--t2);font-size:12px;}
.attach-chip button{background:none;border:none;cursor:pointer;color:var(--t2);font-size:14px;line-height:1;}
.ppt-slide{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:16px;margin-bottom:12px;}
.ppt-num{color:var(--accent);font-size:11px;font-weight:700;margin-bottom:4px;text-transform:uppercase;}
.ppt-title{color:var(--text);font-size:16px;font-weight:700;margin-bottom:10px;}
.ppt-points{padding-right:16px;margin:0 0 8px;color:var(--t2);font-size:13px;line-height:2;}
.ppt-notes{color:var(--t2);font-size:12px;padding:8px;background:rgba(99,102,241,.08);border-radius:8px;border-right:3px solid var(--accent);}
@media(max-width:768px){.sidebar{display:none}.stats-grid{grid-template-columns:1fr 1fr}.settings-grid{grid-template-columns:1fr}}
</style>
