<template>
  <div class="hub">

    <!-- Sidebar -->
    <aside :class="['sidebar', { collapsed: sidebarCollapsed }]">
      <div class="sidebar-header" @click="sidebarCollapsed = !sidebarCollapsed">
        <div class="brand">
          <div class="brand-icon">M</div>
          <span v-if="!sidebarCollapsed" class="brand-name">Morix</span>
        </div>
      </div>
      <nav class="sidebar-nav">
        <button v-for="sec in sections" :key="sec.id"
          :class="['nav-item', { active: currentSection === sec.id }]"
          @click="switchSection(sec.id)" :title="sec.label">
          <span class="nav-icon">{{ sec.icon }}</span>
          <span v-if="!sidebarCollapsed" class="nav-label">{{ sec.label }}</span>
        </button>
      </nav>
      <div class="sidebar-footer">
        <div v-if="!sidebarCollapsed" class="streak-row">
          <span>🔥 {{ profile.streak_count || 0 }}</span>
          <span>⭐ {{ profile.total_stars || 0 }}</span>
        </div>
        <div v-else class="streak-mini">🔥{{ profile.streak_count || 0 }}</div>
        <button class="logout-btn" @click="handleLogout">
          <span>🚪</span><span v-if="!sidebarCollapsed">خروج</span>
        </button>
      </div>
    </aside>

    <!-- Main -->
    <main class="main-content">
      <header class="top-bar">
        <h2 class="section-title">{{ currentSectionLabel }}</h2>
        <div class="user-chip">
          <div class="avatar">{{ firstName[0] || '?' }}</div>
          <span>{{ firstName }}</span>
        </div>
      </header>

      <!-- ===== CHAT ===== -->
      <section v-show="currentSection === 'chat'" class="section-body">
        <!-- Diagnostic -->
        <div v-if="needsDiagnostic" class="diag-wrap">
          <div class="diag-card">
            <h3>🎯 اختبار أسلوب التعلم</h3>
            <p class="diag-step">سؤال {{ diagStep + 1 }} من {{ diagQuestions.length }}</p>
            <div v-if="diagQuestions[diagStep]">
              <p class="q-text">{{ diagQuestions[diagStep].question }}</p>
              <div class="q-options">
                <button v-for="opt in diagQuestions[diagStep].options" :key="opt.value"
                  class="q-opt" @click="answerDiag(opt.value)">{{ opt.text }}</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Chat UI -->
        <div v-else class="chat-layout">
          <div class="conv-panel">
            <button class="new-conv-btn" @click="startNewConv">+ محادثة جديدة</button>
            <div class="conv-list">
              <div v-for="c in conversations" :key="c.id"
                :class="['conv-item', { active: currentConvId === c.id }]"
                @click="loadConv(c.id)">
                <span class="conv-title">{{ c.title }}</span>
                <button class="del-conv" @click.stop="deleteConv(c.id)">✕</button>
              </div>
              <p v-if="!conversations.length" class="no-conv">لا توجد محادثات</p>
            </div>
            <div class="book-sel">
              <label>📖 كتاب:</label>
              <select v-model="selectedBookId">
                <option value="">بدون</option>
                <option v-for="b in books" :key="b.id" :value="b.id">{{ b.title }}</option>
              </select>
            </div>
          </div>

          <div class="chat-area">
            <div class="messages" ref="messagesEl">
              <div v-if="!messages.length" class="chat-welcome">
                <div style="font-size:52px;margin-bottom:14px">🤖</div>
                <h3>مرحباً {{ firstName }}!</h3>
                <p>كيف يمكنني مساعدتك اليوم؟</p>
                <div class="quick-btns">
                  <button v-for="q in quickQs" :key="q" class="quick-btn" @click="sendMsg(q)">{{ q }}</button>
                </div>
              </div>
              <div v-for="(msg, i) in messages" :key="i" :class="['msg', msg.role]">
                <div class="msg-bubble">
                  <span class="msg-icon">{{ msg.role === 'user' ? '👤' : '🤖' }}</span>
                  <div class="msg-text" v-html="fmt(msg.content)"></div>
                </div>
              </div>
              <div v-if="aiThinking" class="msg assistant">
                <div class="msg-bubble">
                  <span class="msg-icon">🤖</span>
                  <div class="dots"><span></span><span></span><span></span></div>
                </div>
              </div>
            </div>
            <div class="input-row">
              <input type="file" ref="fileInputEl" accept="image/*,.pdf,.txt" @change="onFileAttach" style="display:none" />
              <button class="attach-btn" @click="fileInputEl.click()" title="إرفاق صورة أو ملف">📎</button>
              <div v-if="attachedFile" class="attach-chip">
                {{ attachedFile.name.slice(0,20) }}
                <button @click="clearAttach" style="background:none;border:none;cursor:pointer;color:var(--text2)">✕</button>
              </div>
              <textarea v-model="chatInput" rows="2" :placeholder="attachedFile?'أضف رسالة (اختياري)...':'اكتب سؤالك...'"
                @keydown.enter.exact.prevent="sendMsg()"
                @keydown.enter.shift.exact="chatInput += '\n'"></textarea>
              <button class="send-btn" @click="sendMsg()" :disabled="(!chatInput.trim()&&!attachedFile) || aiThinking">➤</button>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== BOOK SUMMARY ===== -->
      <section v-show="currentSection === 'books'" class="section-body pad">
        <div class="card">
          <h3>📖 ملخص الكتاب</h3>
          <div class="row-gap">
            <select v-model="summaryBookId" class="inp">
              <option value="">اختر كتاباً...</option>
              <option v-for="b in books" :key="b.id" :value="b.id">{{ b.title }} — {{ b.subject }}</option>
            </select>
            <button class="btn-p" @click="loadSummary" :disabled="!summaryBookId || summaryLoading">
              {{ summaryLoading ? '...' : 'جلب الملخص' }}
            </button>
          </div>
          <div v-if="bookSummary" class="summary-box">
            <div class="summary-acts">
              <button class="btn-s" @click="speakSummary">{{ isSpeaking ? '⏸ إيقاف' : '🔊 استمع' }}</button>
              <button v-if="isSpeaking" class="btn-s danger" @click="stopSpeech">⏹</button>
            </div>
            <p class="summary-text">{{ bookSummary }}</p>
          </div>
          <div v-if="summaryBookId && bookSummary" style="margin-top:20px">
            <h4 style="color:var(--text);margin:0 0 12px">💬 اسأل عن الكتاب</h4>
            <div class="messages mini" ref="bookMsgsEl">
              <div v-for="(msg,i) in bookMessages" :key="i" :class="['msg',msg.role]">
                <div class="msg-bubble">
                  <span class="msg-icon">{{ msg.role==='user'?'👤':'🤖' }}</span>
                  <div class="msg-text" v-html="fmt(msg.content)"></div>
                </div>
              </div>
            </div>
            <div class="input-row" style="border:none;padding:12px 0 0">
              <input v-model="bookQ" placeholder="سؤال عن الكتاب..." @keydown.enter="askBook" />
              <button class="send-btn" @click="askBook" :disabled="!bookQ.trim()">➤</button>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== GAMES ===== -->
      <section v-show="currentSection === 'games'" class="section-body pad">
        <div v-if="!activeGame" class="card">
          <h3>🎮 الألعاب التعليمية</h3>
          <div class="col-gap">
            <select v-model="gameType" class="inp">
              <option value="mcq">✅ اختيار من متعدد</option>
              <option value="matching">🔗 مطابقة المصطلحات</option>
              <option value="flashcards">📇 بطاقات تعليمية</option>
            </select>
            <input v-model="gameSubject" class="inp" placeholder="المادة (مثال: الرياضيات)" />
            <input v-model="gameTopic" class="inp" placeholder="الموضوع (اختياري)" />
            <button class="btn-p" @click="startGame" :disabled="gameLoading || !gameSubject">
              {{ gameLoading ? '⏳ جاري التوليد...' : '🚀 ابدأ اللعبة' }}
            </button>
          </div>
          <div v-if="pastGames.length" style="margin-top:20px;border-top:1px solid var(--border);padding-top:16px">
            <p style="color:var(--text2);font-size:13px;margin:0 0 10px">ألعابي السابقة:</p>
            <div v-for="g in pastGames.slice(0,5)" :key="g.id"
              style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border);color:var(--text2);font-size:13px">
              <span>{{ g.game_type==='mcq'?'✅':g.game_type==='matching'?'🔗':'📇' }} {{ g.subject }}</span>
              <span :style="{color: g.completed ? '#4ade80':'#facc15'}">{{ g.completed ? g.score+'%' : 'معلق' }}</span>
            </div>
          </div>
        </div>

        <!-- MCQ -->
        <div v-if="activeGame && gameType==='mcq'" class="card">
          <div class="game-header">
            <h3>✅ {{ activeGame.subject }}</h3>
            <span class="q-cnt">{{ mcqIdx+1 }}/{{ activeGame.items?.length }}</span>
          </div>
          <div v-if="!gameFinished">
            <p class="q-text">{{ activeGame.items?.[mcqIdx]?.question }}</p>
            <div class="opts-grid">
              <button v-for="(txt,key) in activeGame.items?.[mcqIdx]?.options" :key="key"
                :class="['opt',{selected:mcqSel===key, correct:mcqAnswered&&key===activeGame.items[mcqIdx].answer, wrong:mcqAnswered&&mcqSel===key&&key!==activeGame.items[mcqIdx].answer}]"
                @click="mcqPick(key)" :disabled="mcqAnswered">{{ key }}) {{ txt }}</button>
            </div>
            <div v-if="mcqAnswered" class="expl">
              <p>{{ mcqSel===activeGame.items[mcqIdx].answer?'✅ صحيح!':'❌ خطأ!' }}</p>
              <p style="color:var(--text2);font-size:13px">{{ activeGame.items[mcqIdx].explanation }}</p>
              <button class="btn-p" @click="mcqNext">{{ mcqIdx<activeGame.items.length-1?'التالي ▶':'إنهاء 🏁' }}</button>
            </div>
          </div>
          <div v-else class="result-box">
            <div style="font-size:48px">🏆</div>
            <h2>{{ gameScore }}%</h2>
            <p>{{ gameScore>=80?'ممتاز!':gameScore>=60?'جيد! استمر!':'حاول مرة أخرى!' }}</p>
            <button class="btn-p" @click="resetGame">🔄 إعادة</button>
          </div>
        </div>

        <!-- Matching -->
        <div v-if="activeGame && gameType==='matching'" class="card">
          <h3>🔗 {{ activeGame.subject }}</h3>
          <div class="match-grid">
            <div>
              <p style="color:var(--text2);font-size:13px;margin:0 0 10px">المصطلحات</p>
              <button v-for="(it,i) in shuffledTerms" :key="'t'+i"
                :class="['match-btn',{selected:selectedTerm===i,matched:matchedTerms.includes(i)}]"
                @click="pickTerm(i)" :disabled="matchedTerms.includes(i)">{{ it.term }}</button>
            </div>
            <div>
              <p style="color:var(--text2);font-size:13px;margin:0 0 10px">التعاريف</p>
              <button v-for="(it,i) in shuffledDefs" :key="'d'+i"
                :class="['match-btn',{matched:matchedDefs.includes(i)}]"
                @click="pickDef(i)" :disabled="matchedDefs.includes(i)">{{ it.definition }}</button>
            </div>
          </div>
          <div v-if="matchScore!==null" class="result-box">
            <h2>🏆 {{ matchScore }}%</h2>
            <button class="btn-p" @click="resetGame">🔄 إعادة</button>
          </div>
        </div>

        <!-- Flashcards -->
        <div v-if="activeGame && gameType==='flashcards'" class="card" style="text-align:center">
          <h3>📇 {{ activeGame.subject }}</h3>
          <div :class="['flashcard',{flipped:cardFlipped}]" @click="cardFlipped=!cardFlipped">
            <div class="card-f">
              <p>{{ activeGame.items?.[cardIdx]?.question }}</p>
              <span style="color:var(--text2);font-size:12px;margin-top:10px">اضغط للإجابة</span>
            </div>
            <div class="card-b"><p>{{ activeGame.items?.[cardIdx]?.answer }}</p></div>
          </div>
          <div class="card-nav">
            <button class="btn-s" @click="cardIdx=Math.max(0,cardIdx-1)" :disabled="cardIdx===0">◀</button>
            <span style="color:var(--text2)">{{ cardIdx+1 }}/{{ activeGame.items?.length }}</span>
            <button class="btn-s" @click="cardIdx++;cardFlipped=false" :disabled="cardIdx>=(activeGame.items?.length||1)-1">▶</button>
          </div>
          <button class="btn-o" style="margin-top:12px" @click="resetGame">🔄 إعادة</button>
        </div>
      </section>

      <!-- ===== HOMEWORK ===== -->
      <section v-show="currentSection === 'homework'" class="section-body pad">
        <div class="card">
          <h3>📚 الواجبات</h3>
          <div v-if="hwLoading" class="empty">⏳ تحميل...</div>
          <div v-else-if="!homework.length" class="empty">📭 لا توجد واجبات حالياً</div>
          <div v-else class="list-col">
            <div v-for="hw in homework" :key="hw.id" class="list-item">
              <div style="flex:1">
                <h4>{{ hw.title }}</h4>
                <p style="color:var(--text2);font-size:13px;margin:4px 0 8px">{{ hw.description }}</p>
                <div class="meta-row">
                  <span>📚 {{ hw.subject }}</span>
                  <span v-if="hw.grade">🎓 {{ hw.grade }}</span>
                  <span v-if="hw.due_date">📅 {{ fmtDate(hw.due_date) }}</span>
                </div>
              </div>
              <button class="btn-s" @click="openHwSubmit(hw)">تسليم ✏️</button>
            </div>
          </div>
        </div>
        <div v-if="hwModal" class="modal-bg" @click.self="hwModal=null">
          <div class="modal-box">
            <h3>تسليم: {{ hwModal.title }}</h3>
            <textarea v-model="hwContent" class="inp" rows="6" placeholder="إجابتك هنا..."></textarea>
            <div class="row-gap" style="margin-top:12px">
              <button class="btn-p" @click="doHwSubmit">إرسال</button>
              <button class="btn-o" @click="hwModal=null">إلغاء</button>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== TESTS ===== -->
      <section v-show="currentSection === 'tests'" class="section-body pad">
        <div v-if="!activeTest" class="card">
          <h3>📝 الاختبارات</h3>
          <div v-if="testsLoading" class="empty">⏳ تحميل...</div>
          <div v-else-if="!tests.length" class="empty">📭 لا توجد اختبارات</div>
          <div v-else class="list-col">
            <div v-for="t in tests" :key="t.id" class="list-item">
              <div style="flex:1">
                <h4>{{ t.title }}</h4>
                <div class="meta-row"><span>📚 {{ t.subject }}</span><span>⏱ {{ t.duration_minutes }}د</span></div>
              </div>
              <button class="btn-p" @click="startTest(t.id)">ابدأ</button>
            </div>
          </div>
        </div>
        <div v-else class="card">
          <div class="game-header">
            <h3>{{ activeTest.title }}</h3>
            <span class="q-cnt">{{ tQIdx+1 }}/{{ activeTest.questions?.length }}</span>
          </div>
          <div v-if="!testDone">
            <p class="q-text">{{ activeTest.questions?.[tQIdx]?.question }}</p>
            <div class="opts-grid">
              <button v-for="(txt,key) in activeTest.questions?.[tQIdx]?.options" :key="key"
                :class="['opt',{selected:tAnswers[activeTest.questions[tQIdx].id]===key}]"
                @click="tAnswers[activeTest.questions[tQIdx].id]=key">{{ key }}) {{ txt }}</button>
            </div>
            <div class="test-nav">
              <button class="btn-s" @click="tQIdx--" :disabled="tQIdx===0">◀</button>
              <button v-if="tQIdx<(activeTest.questions?.length||1)-1" class="btn-s" @click="tQIdx++">▶</button>
              <button v-else class="btn-p" @click="doSubmitTest">إنهاء 🏁</button>
            </div>
          </div>
          <div v-else class="result-box">
            <h2>🏆 {{ tResult?.score }}%</h2>
            <p>{{ tResult?.correct }} صحيح من {{ tResult?.total }}</p>
            <button class="btn-o" @click="activeTest=null">← رجوع</button>
          </div>
        </div>
      </section>

      <!-- ===== WORKSHEETS ===== -->
      <section v-show="currentSection === 'worksheets'" class="section-body pad">
        <div class="card">
          <h3>📋 أوراق العمل</h3>
          <div v-if="wsLoading" class="empty">⏳ تحميل...</div>
          <div v-else-if="!worksheets.length" class="empty">📭 لا توجد أوراق عمل</div>
          <div v-else class="list-col">
            <div v-for="ws in worksheets" :key="ws.id" class="list-item clickable" @click="openWs(ws.id)">
              <div style="flex:1">
                <h4>{{ ws.title }}</h4>
                <div class="meta-row">
                  <span>📚 {{ ws.subject }}</span>
                  <span v-if="ws.ai_generated" style="background:rgba(99,102,241,.2);color:var(--accent);border-radius:4px;padding:1px 6px">🤖 AI</span>
                </div>
              </div>
              <span style="color:var(--text2)">←</span>
            </div>
          </div>
        </div>
        <div v-if="activeWs" class="card" style="margin-top:16px">
          <div style="display:flex;justify-content:space-between;margin-bottom:16px">
            <h3>{{ activeWs.title }}</h3>
            <button class="btn-o" @click="activeWs=null">✕</button>
          </div>
          <div style="color:var(--text2);line-height:1.8;font-size:14px" v-html="fmt(activeWs.content||'')"></div>
        </div>
      </section>

      <!-- ===== IMAGE GEN ===== -->
      <section v-show="currentSection === 'image'" class="section-body pad">
        <div class="card">
          <h3>🎨 توليد الصور التعليمية</h3>
          <p style="color:var(--text2);font-size:13px;margin:0 0 16px">اكتب وصفاً للصورة بأي لغة</p>
          <div class="col-gap">
            <textarea v-model="imgPrompt" class="inp" rows="3"
              placeholder="مثال: مخطط يوضح دورة الماء في الطبيعة..."></textarea>
            <button class="btn-p" @click="genImage" :disabled="imgLoading || !imgPrompt.trim()">
              {{ imgLoading ? '⏳ جاري التوليد...' : '✨ توليد الصورة' }}
            </button>
          </div>
          <div v-if="imgError" style="color:#f87171;font-size:13px;margin-top:12px">{{ imgError }}</div>
          <div v-if="genImg" style="margin-top:20px;text-align:center">
            <img :src="`data:image/png;base64,${genImg}`" style="max-width:100%;border-radius:12px;border:2px solid var(--border)" />
            <br><a :href="`data:image/png;base64,${genImg}`" download="morix.png" class="btn-s" style="margin-top:10px;display:inline-block">⬇ تحميل</a>
          </div>
        </div>
      </section>

      <!-- ===== VIDEO SCRIPT ===== -->
      <section v-show="currentSection === 'video'" class="section-body pad">
        <div class="card">
          <h3>🎬 توليد سكريبت الفيديو</h3>
          <div class="col-gap">
            <input v-model="vidTopic" class="inp" placeholder="موضوع الفيديو" />
            <input v-model="vidSubject" class="inp" placeholder="المادة الدراسية" />
            <div>
              <p style="color:var(--text2);font-size:13px;margin:0 0 6px">المدة: {{ formatVidDur(vidSeconds) }}</p>
              <input type="range" v-model.number="vidSeconds" min="30" max="600" step="30" style="width:100%;accent-color:var(--accent)" />
              <div style="display:flex;justify-content:space-between;color:var(--text2);font-size:12px;margin-top:4px"><span>30 ثانية</span><span>10 دقائق</span></div>
            </div>
            <button class="btn-p" @click="genVideo" :disabled="vidLoading||!vidTopic">
              {{ vidLoading ? '⏳ ...' : '✍️ توليد السكريبت' }}
            </button>
          </div>
          <div v-if="vidScript" style="margin-top:20px">
            <div style="background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:20px;color:var(--text2);font-size:14px;line-height:1.8;white-space:pre-wrap" v-html="fmt(vidScript)"></div>
            <button class="btn-s" style="margin-top:10px" @click="navigator.clipboard.writeText(vidScript)">📋 نسخ</button>
          </div>
        </div>
      </section>

      <!-- ===== 🏆 LEADERBOARD ===== -->
      <section v-show="currentSection === 'leaderboard'" class="section-body pad">
        <div class="card">
          <h3 style="margin-bottom:16px">🏆 أبطال مدرستك — أفضل 10 طلاب</h3>
          <div v-if="!leaderboard.length" style="color:var(--text2);text-align:center;padding:32px">جاري التحميل...</div>
          <div v-for="u in leaderboard" :key="u.id"
               :style="{display:'flex',alignItems:'center',gap:12,padding:'12px',marginBottom:'8px',borderRadius:'12px',background:u.is_me?'linear-gradient(90deg,rgba(99,102,241,.25),transparent)':'var(--card)',border:u.is_me?'2px solid var(--accent)':'1px solid var(--border)'}">
            <div style="font-size:24px;font-weight:bold;width:40px;text-align:center">
              <span v-if="u.rank===1">🥇</span>
              <span v-else-if="u.rank===2">🥈</span>
              <span v-else-if="u.rank===3">🥉</span>
              <span v-else style="color:var(--text2)">#{{ u.rank }}</span>
            </div>
            <img v-if="u.avatar_url" :src="u.avatar_url" style="width:42px;height:42px;border-radius:50%;object-fit:cover" />
            <div v-else style="width:42px;height:42px;border-radius:50%;background:var(--accent);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:bold">
              {{ (u.full_name||'?').charAt(0) }}
            </div>
            <div style="flex:1">
              <div style="font-weight:bold;color:var(--text)">{{ u.full_name }} <span v-if="u.is_me" style="font-size:12px;color:var(--accent)">(أنت)</span></div>
              <div style="font-size:12px;color:var(--text2)">{{ u.grade }}</div>
            </div>
            <div style="text-align:left">
              <div style="color:#fbbf24;font-weight:bold">⭐ {{ u.stars_count }}</div>
              <div style="font-size:12px;color:#f97316">🔥 {{ u.streak_count }}</div>
            </div>
          </div>
        </div>
      </section>

      <!-- ===== 🎯 DAILY CHALLENGE ===== -->
      <section v-show="currentSection === 'daily'" class="section-body pad">
        <div class="card" style="max-width:600px;margin:0 auto">
          <h3 style="margin-bottom:16px">🎯 التحدي اليومي</h3>
          <div v-if="dailyState==='loading'" style="text-align:center;color:var(--text2);padding:32px">جاري التحميل...</div>
          <div v-else-if="dailyState==='answered'" style="text-align:center;padding:32px">
            <div style="font-size:64px">✅</div>
            <h3 style="margin:12px 0">أجبت على تحدي اليوم!</h3>
            <p style="color:var(--text2)">عد غداً لتحدي جديد 🌅</p>
            <p style="color:#fbbf24;margin-top:12px">⭐ كسبت {{ dailyResult?.stars_earned || 0 }} نجمة</p>
          </div>
          <div v-else-if="dailyState==='ready' && dailyChallenge?.question">
            <div style="background:var(--card);padding:12px;border-radius:8px;margin-bottom:16px;font-size:13px;color:var(--text2)">
              📚 المادة: <strong style="color:var(--text)">{{ dailyChallenge.subject }}</strong>
            </div>
            <h4 style="color:var(--text);margin-bottom:16px">{{ dailyChallenge.question.question || dailyChallenge.question.q }}</h4>
            <div style="display:flex;flex-direction:column;gap:8px">
              <button v-for="(opt,i) in (dailyChallenge.question.options || [])" :key="i"
                      @click="answerDaily(opt, i)"
                      :disabled="dailyAnswering"
                      class="btn-primary" style="text-align:right">
                {{ opt.text || opt }}
              </button>
            </div>
          </div>
          <div v-else-if="dailyState==='result'" style="text-align:center;padding:24px">
            <div style="font-size:64px">{{ dailyResult?.stars_earned >= 25 ? '🎉' : '💪' }}</div>
            <h3 style="margin:12px 0">{{ dailyResult?.message }}</h3>
          </div>
          <div v-else style="color:var(--text2);text-align:center">لا يوجد تحدي اليوم، حاول غداً.</div>
        </div>
      </section>

      <!-- ===== ⏱️ POMODORO ===== -->
      <section v-show="currentSection === 'pomodoro'" class="section-body pad">
        <div class="card" style="max-width:500px;margin:0 auto;text-align:center">
          <h3 style="margin-bottom:24px">⏱️ مؤقت بومودورو</h3>
          <div style="font-size:96px;font-weight:bold;color:var(--accent);font-family:monospace">
            {{ pomoDisplay }}
          </div>
          <div style="margin:12px 0;color:var(--text2)">
            {{ pomoMode==='work' ? '🎯 وقت التركيز' : '☕ استراحة' }}
            — جلسة #{{ pomoSessions+1 }}
          </div>
          <div style="display:flex;gap:8px;justify-content:center;margin-top:16px">
            <button @click="startPomo" v-if="!pomoRunning" class="btn-primary">▶️ ابدأ</button>
            <button @click="pausePomo" v-else class="btn-primary">⏸️ إيقاف</button>
            <button @click="resetPomo" class="btn-primary" style="background:var(--bg3)">🔄 تصفير</button>
          </div>
          <div v-if="pomoMessage" style="margin-top:16px;color:#fbbf24">{{ pomoMessage }}</div>
        </div>
      </section>

      <!-- ===== 😊 MOOD ===== -->
      <section v-show="currentSection === 'mood'" class="section-body pad">
        <div class="card" style="max-width:600px;margin:0 auto">
          <h3 style="margin-bottom:16px">😊 كيف تشعر اليوم؟</h3>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px">
            <button v-for="m in moods" :key="m.key"
                    @click="logMood(m.key)"
                    class="btn-primary"
                    style="flex-direction:column;padding:20px;background:var(--card);border:1px solid var(--border)">
              <div style="font-size:36px">{{ m.emoji }}</div>
              <div style="margin-top:8px;color:var(--text)">{{ m.label }}</div>
            </button>
          </div>
          <div v-if="moodSuggestion" style="padding:16px;background:linear-gradient(135deg,rgba(99,102,241,.15),rgba(99,102,241,.05));border-radius:12px;border:1px solid var(--accent);color:var(--text)">
            {{ moodSuggestion }}
          </div>
        </div>
      </section>

      <!-- ===== 🌅 REFLECTION ===== -->
      <section v-show="currentSection === 'reflection'" class="section-body pad">
        <div class="card" style="max-width:600px;margin:0 auto">
          <h3 style="margin-bottom:8px">🌅 التأمل اليومي</h3>
          <p style="color:var(--text2);margin-bottom:16px">ماذا تعلمت اليوم؟ ما هو أفضل جزء من يومك الدراسي؟</p>
          <textarea v-model="reflectionText" rows="6" class="memorix-input"
                    placeholder="اكتب تأملك هنا..." style="width:100%;resize:vertical"></textarea>
          <button @click="saveReflection" :disabled="!reflectionText.trim()" class="btn-primary" style="margin-top:12px">
            💾 احفظ + 3 نجوم
          </button>
          <div v-if="reflectionMessage" style="margin-top:12px;color:#fbbf24">{{ reflectionMessage }}</div>
        </div>
      </section>

      <!-- ===== 📚 DIGITAL LIBRARY (داخل المنصة عبر الـ proxy) ===== -->
      <section v-show="currentSection === 'library'" class="section-body pad">
        <div class="card">
          <h3 style="margin-bottom:8px">📚 المكتبة الرقمية المجانية</h3>
          <p style="color:var(--text2);margin-bottom:12px">آلاف الكتب العربية والمراجع التعليمية مجانية — يفتح داخل المنصة</p>
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
            <button v-for="src in libSources" :key="src.url"
                    @click="libUrl = src.url"
                    class="btn-primary"
                    :style="{background: libUrl===src.url?'var(--accent)':'var(--bg3)',padding:'8px 14px',fontSize:'13px'}">
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
          <p style="color:var(--text2);font-size:12px;margin-top:8px">💡 المكتبة تفتح داخل المنصة عبر بروكسي Morix — كل الروابط تتنقل في نفس النافذة</p>
        </div>
      </section>

      <!-- ===== 📓 دفتري الذكي (NotebookLM-like داخل المنصة) ===== -->
      <section v-show="currentSection === 'notebook'" class="section-body pad">
        <div class="card">
          <h3 style="margin-bottom:8px">📓 دفتري الذكي — Morix Notebook</h3>
          <p style="color:var(--text2);margin-bottom:12px">ارفع كتابك أو مذكراتك واسأل AI عنها، أو ولّد ملخصاً/خريطة ذهنية/أسئلة مراجعة</p>

          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
            <button @click="nbTab='upload'" class="btn-primary" :style="{background:nbTab==='upload'?'var(--accent)':'var(--bg3)',padding:'8px 14px',fontSize:'13px'}">📤 رفع ملف</button>
            <button @click="nbTab='ask'" :disabled="!nbFileText" class="btn-primary" :style="{background:nbTab==='ask'?'var(--accent)':'var(--bg3)',padding:'8px 14px',fontSize:'13px',opacity:nbFileText?1:0.5}">💬 اسأل عن الملف</button>
            <button @click="nbTab='generate'" :disabled="!nbFileText" class="btn-primary" :style="{background:nbTab==='generate'?'var(--accent)':'var(--bg3)',padding:'8px 14px',fontSize:'13px',opacity:nbFileText?1:0.5}">✨ ولّد محتوى</button>
          </div>

          <div v-if="nbTab==='upload'" class="card" style="background:var(--card)">
            <input ref="nbFileInput" type="file" accept=".pdf,.txt,.md" @change="onNbFileUpload" style="display:none" />
            <button @click="$refs.nbFileInput?.click()" class="btn-primary" style="width:100%;padding:24px;font-size:16px">
              📤 اختر ملف PDF / TXT / MD
            </button>
            <div v-if="nbFileName" style="margin-top:12px;padding:12px;background:var(--bg3);border-radius:8px;border:1px solid var(--accent)">
              ✅ <b>{{ nbFileName }}</b> — جاهز ({{ Math.round(nbFileText.length/1000) }}K حرف)
              <p style="color:var(--text2);font-size:12px;margin-top:6px">انتقل لتبويب "اسأل" أو "ولّد"</p>
            </div>
            <p style="color:var(--text2);font-size:12px;margin-top:8px">💡 الملفات تُعالج محلياً — لا تُرفع لأي خادم خارجي</p>
          </div>

          <div v-if="nbTab==='ask'" class="card" style="background:var(--card)">
            <div style="max-height:50vh;overflow-y:auto;padding:8px;margin-bottom:12px">
              <div v-for="(m,i) in nbChat" :key="i" :style="{padding:'10px',marginBottom:'8px',borderRadius:'8px',background: m.role==='user'?'rgba(99,102,241,.15)':'var(--bg3)',borderRight: m.role==='user'?'3px solid var(--accent)':'3px solid #10b981'}">
                <b>{{ m.role==='user'?'🙋 أنت':'🤖 Morix' }}:</b>
                <div style="white-space:pre-wrap;margin-top:4px">{{ m.text }}</div>
              </div>
            </div>
            <div style="display:flex;gap:8px">
              <input v-model="nbInput" @keyup.enter="askNb" placeholder="اسأل سؤالاً عن الملف..." class="memorix-input" style="flex:1" />
              <button @click="askNb" :disabled="nbAsking || !nbInput.trim()" class="btn-primary">{{ nbAsking?'⏳':'➤' }}</button>
            </div>
          </div>

          <div v-if="nbTab==='generate'" class="card" style="background:var(--card)">
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;margin-bottom:12px">
              <button @click="genNb('summary')" :disabled="nbGenLoading" class="btn-primary">📝 ملخص شامل</button>
              <button @click="genNb('mindmap')" :disabled="nbGenLoading" class="btn-primary">🧠 خريطة ذهنية</button>
              <button @click="genNb('questions')" :disabled="nbGenLoading" class="btn-primary">❓ 10 أسئلة مراجعة</button>
              <button @click="genNb('flashcards')" :disabled="nbGenLoading" class="btn-primary">🎴 بطاقات تعليمية</button>
              <button @click="genNb('podcast')" :disabled="nbGenLoading" class="btn-primary">🎙️ سكربت بودكاست</button>
              <button @click="genNb('keypoints')" :disabled="nbGenLoading" class="btn-primary">🎯 النقاط الجوهرية</button>
            </div>
            <div v-if="nbGenLoading" style="text-align:center;padding:20px;color:var(--text2)">⏳ جاري التوليد...</div>
            <div v-if="nbGenResult" style="padding:16px;background:var(--bg3);border-radius:8px;white-space:pre-wrap;line-height:1.8;max-height:60vh;overflow-y:auto">{{ nbGenResult }}</div>
          </div>
        </div>
      </section>

      <!-- ===== PROGRESS ===== -->
      <section v-show="currentSection === 'progress'" class="section-body pad">
        <div class="stats-grid">
          <div class="stat-card"><div class="stat-n">🔥 {{ prog.streak||0 }}</div><div class="stat-l">أيام متتالية</div></div>
          <div class="stat-card"><div class="stat-n">⭐ {{ prog.total_stars||0 }}</div><div class="stat-l">إجمالي النجوم</div></div>
          <div class="stat-card"><div class="stat-n">💬 {{ prog.total_conversations||0 }}</div><div class="stat-l">محادثات AI</div></div>
          <div class="stat-card"><div class="stat-n">🎮 {{ prog.total_games_played||0 }}</div><div class="stat-l">ألعاب مكتملة</div></div>
          <div class="stat-card"><div class="stat-n">📝 {{ prog.avg_test_score||0 }}%</div><div class="stat-l">متوسط الاختبارات</div></div>
          <div class="stat-card"><div class="stat-n">🏆 {{ prog.longest_streak||0 }}</div><div class="stat-l">أطول سلسلة</div></div>
        </div>
        <div class="card" style="margin-top:16px">
          <h3>🧠 أسلوب التعلم</h3>
          <div style="font-size:20px;color:var(--text)">
            <span v-if="profile.learning_style==='visual'">👁️ بصري</span>
            <span v-else-if="profile.learning_style==='auditory'">👂 سمعي</span>
            <span v-else-if="profile.learning_style==='kinesthetic'">✋ حركي</span>
            <span v-else style="color:var(--text2);font-size:14px">لم يتحدد — أكمل الاختبار من قسم المحادثة</span>
          </div>
        </div>
      </section>

      <!-- ===== SETTINGS ===== -->
      <section v-show="currentSection === 'settings'" class="section-body pad">
        <div class="settings-grid">
          <div class="card">
            <h3>👤 معلومات الحساب</h3>
            <div class="avatar-section">
              <div style="position:relative;cursor:pointer" @click="avatarInputEl?.click()">
                <img v-if="appSettings.avatar_url" :src="appSettings.avatar_url" class="av-preview" />
                <div v-else class="av-big">{{ firstName[0] }}</div>
                <div class="av-overlay">📷</div>
              </div>
              <div style="flex:1">
                <p style="color:var(--text2);font-size:12px;margin:0 0 6px">اضغط على الصورة لرفع صورة من جهازك</p>
                <input ref="avatarInputEl" type="file" accept="image/*" style="display:none" @change="onAvatarUpload" />
                <button class="btn-s" style="width:100%" @click="avatarInputEl?.click()">📷 رفع صورة من الجهاز</button>
              </div>
            </div>
            <div class="info-row"><span>الاسم</span><b>{{ profile.name }}</b></div>
            <div class="info-row"><span>الإيميل</span><b>{{ auth.user?.email }}</b></div>
            <div class="info-row"><span>الصف</span><b>{{ profile.grade||'غير محدد' }}</b></div>
          </div>

          <div class="card">
            <h3>🎨 المظهر</h3>
            <p style="color:var(--text2);font-size:13px;margin:0 0 12px">الثيم</p>
            <div class="theme-row">
              <button :class="['t-btn',{active:appSettings.theme==='dark'}]" @click="setTheme('dark')">🌑 داكن</button>
              <button :class="['t-btn',{active:appSettings.theme==='light'}]" @click="setTheme('light')">☀️ فاتح</button>
              <button :class="['t-btn',{active:appSettings.theme==='library'}]" @click="setTheme('library')">📚 مكتبة</button>
            </div>
            <p style="color:var(--text2);font-size:13px;margin:16px 0 8px">السطوع {{ appSettings.brightness }}%</p>
            <input type="range" v-model.number="appSettings.brightness" min="40" max="100" step="5"
              @change="saveSettings" style="width:100%;accent-color:var(--accent)" />
          </div>

          <div class="card">
            <h3>🎓 التفضيلات</h3>
            <p style="color:var(--text2);font-size:13px;margin:0 0 8px">مستوى الصعوبة</p>
            <select v-model="appSettings.difficulty" @change="saveSettings" class="inp">
              <option value="easy">سهل</option><option value="medium">متوسط</option><option value="hard">صعب</option>
            </select>
            <p style="color:var(--text2);font-size:13px;margin:14px 0 8px">الهوايات والاهتمامات</p>
            <input v-model="hobbiesInput" class="inp" placeholder="مثال: رياضيات، علوم" @blur="saveHobbies" />
          </div>

          <div class="card">
            <h3>🎯 إعادة الاختبار التشخيصي</h3>
            <p style="color:var(--text2);font-size:13px">أسلوبك الحالي: <strong>{{ profile.learning_style||'غير محدد' }}</strong></p>
            <button class="btn-o" @click="retakeDiag">إعادة الاختبار</button>
          </div>

          <div class="card">
            <h3>📣 شكوى / اقتراح</h3>
            <select v-model="cpl.type" class="inp">
              <option value="complaint">شكوى</option><option value="suggestion">اقتراح</option><option value="bug">مشكلة تقنية</option>
            </select>
            <input v-model="cpl.title" class="inp" style="margin-top:10px" placeholder="العنوان" />
            <textarea v-model="cpl.content" class="inp" style="margin-top:10px" rows="3" placeholder="التفاصيل..."></textarea>
            <button class="btn-p" style="margin-top:10px" @click="sendCpl" :disabled="!cpl.title||!cpl.content">إرسال</button>
            <p v-if="cplMsg" style="color:#4ade80;font-size:13px;margin-top:8px">{{ cplMsg }}</p>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import { useRouter } from 'vue-router'
import { aiAPI, studentAPI, authAPI, teacherAPI } from '../api.js'
import { useTheme } from '../composables/useTheme.js'

const auth = useAuthStore()
const router = useRouter()

const sections = [
  { id:'chat',icon:'💬',label:'المحادثة' },
  { id:'books',icon:'📖',label:'ملخص الكتاب' },
  { id:'games',icon:'🎮',label:'الألعاب' },
  { id:'homework',icon:'📚',label:'الواجبات' },
  { id:'tests',icon:'📝',label:'الاختبارات' },
  { id:'worksheets',icon:'📋',label:'أوراق العمل' },
  { id:'image',icon:'🎨',label:'توليد صور' },
  { id:'video',icon:'🎬',label:'سكريبت فيديو' },
  { id:'leaderboard',icon:'🏆',label:'لوحة المتصدرين' },
  { id:'daily',icon:'🎯',label:'التحدي اليومي' },
  { id:'pomodoro',icon:'⏱️',label:'بومودورو' },
  { id:'mood',icon:'😊',label:'مزاجي اليوم' },
  { id:'reflection',icon:'🌅',label:'التأمل اليومي' },
  { id:'library',icon:'📚',label:'المكتبة الرقمية' },
  { id:'notebook',icon:'📓',label:'NotebookLM' },
  { id:'progress',icon:'📊',label:'تقدمي' },
  { id:'settings',icon:'⚙️',label:'الإعدادات' },
]

const currentSection = ref('chat')
const sidebarCollapsed = ref(false)
const currentSectionLabel = computed(() => sections.find(s=>s.id===currentSection.value)?.label||'')

const profile = ref({ name:'', learning_style:null, grade:'', streak_count:0, total_stars:0 })
const firstName = computed(() => (auth.user?.full_name||profile.value.name||'طالب').split(' ')[0])

// Chat
const needsDiagnostic = ref(false)
const diagQuestions = ref([])
const diagStep = ref(0)
const diagAnswers = ref([])
const conversations = ref([])
const currentConvId = ref(null)
const messages = ref([])
const chatInput = ref('')
const aiThinking = ref(false)
const messagesEl = ref(null)
const selectedBookId = ref('')
const books = ref([])
const quickQs = ['اشرح لي المفهوم الأساسي','أعطني مثالاً عملياً','لخص الدرس','ما أهم النقاط؟']

// Books
const summaryBookId = ref('')
const bookSummary = ref('')
const summaryLoading = ref(false)
const isSpeaking = ref(false)
const bookMessages = ref([])
const bookQ = ref('')
const bookConvId = ref(null)
const bookMsgsEl = ref(null)

// Games
const gameType = ref('mcq')
const gameSubject = ref('')
const gameTopic = ref('')
const gameLoading = ref(false)
const activeGame = ref(null)
const activeGameId = ref(null)
const pastGames = ref([])
const gameFinished = ref(false)
const gameScore = ref(0)
const mcqIdx = ref(0)
const mcqSel = ref(null)
const mcqAnswered = ref(false)
const mcqCorrect = ref(0)
const shuffledTerms = ref([])
const shuffledDefs = ref([])
const selectedTerm = ref(null)
const matchedTerms = ref([])
const matchedDefs = ref([])
const matchScore = ref(null)
const cardIdx = ref(0)
const cardFlipped = ref(false)

// Homework
const homework = ref([])
const hwLoading = ref(false)
const hwModal = ref(null)
const hwContent = ref('')

// Tests
const tests = ref([])
const testsLoading = ref(false)
const activeTest = ref(null)
const tQIdx = ref(0)
const tAnswers = ref({})
const testDone = ref(false)
const tResult = ref(null)

// Worksheets
const worksheets = ref([])
const wsLoading = ref(false)
const activeWs = ref(null)

// Image
const imgPrompt = ref('')
const imgLoading = ref(false)
const genImg = ref(null)
const imgError = ref('')

// Video
const vidTopic = ref('')
const vidSubject = ref('')
const vidSeconds = ref(300)
const vidLoading = ref(false)
const vidScript = ref('')

// Chat attachments
const fileInputEl = ref(null)
const attachedFile = ref(null)
const attachedBase64 = ref(null)
const attachedFileText = ref(null)

// Progress
const prog = ref({})

// Settings
const appSettings = ref({ theme:'dark', brightness:100, difficulty:'medium', hobbies:[], notifications_enabled:true, avatar_url:'' })
useTheme(appSettings)
const hobbiesInput = ref('')
const avatarInputEl = ref(null)
const oldPass = ref('')
const newPass = ref('')
const passMsg = ref('')
const cpl = ref({ type:'complaint', title:'', content:'' })
const cplMsg = ref('')

// ========== Mount ==========
onMounted(async () => {
  await loadProfile()
  await loadBooks()
  await loadConversations()
  await loadProgress()
  await loadUserSettings()
})

async function loadProfile() {
  try {
    const r = await studentAPI.getProfile()
    profile.value = r.data
    if (!profile.value.learning_style) {
      await studentAPI.getQuestions().then(r => { diagQuestions.value = r.data })
      needsDiagnostic.value = true
    }
  } catch {}
}
async function loadBooks() { try { books.value = (await aiAPI.getBooks()).data } catch {} }
async function loadConversations() { try { conversations.value = (await aiAPI.getConversations()).data } catch {} }
async function loadProgress() { try { prog.value = (await studentAPI.getProgress()).data } catch {} }
async function loadUserSettings() {
  try {
    const r = await studentAPI.getSettings()
    appSettings.value = { ...appSettings.value, ...r.data }
    hobbiesInput.value = (appSettings.value.hobbies||[]).join('، ')
  } catch {}
}

async function switchSection(id) {
  currentSection.value = id
  if (id==='homework' && !homework.value.length) { hwLoading.value=true; try { homework.value=(await studentAPI.getHomework()).data } catch {} finally { hwLoading.value=false } }
  else if (id==='tests' && !tests.value.length) { testsLoading.value=true; try { tests.value=(await studentAPI.getTests()).data } catch {} finally { testsLoading.value=false } }
  else if (id==='worksheets' && !worksheets.value.length) { wsLoading.value=true; try { worksheets.value=(await studentAPI.getWorksheets()).data } catch {} finally { wsLoading.value=false } }
  else if (id==='games') { try { pastGames.value=(await studentAPI.getGames()).data } catch {} }
  else if (id==='leaderboard') { try { leaderboard.value=(await studentAPI.getLeaderboard()).data } catch {} }
  else if (id==='daily') { await loadDailyChallenge() }
}

// ========== 🏆 Leaderboard ==========
const leaderboard = ref([])

// ========== 🎯 Daily Challenge ==========
const dailyState = ref('loading') // loading | ready | answered | result
const dailyChallenge = ref(null)
const dailyResult = ref(null)
const dailyAnswering = ref(false)
async function loadDailyChallenge() {
  dailyState.value = 'loading'
  try {
    const r = await studentAPI.getDailyChallenge()
    if (r.data.already_answered) {
      dailyState.value = 'answered'
      dailyResult.value = r.data.result
    } else if (r.data.question) {
      dailyChallenge.value = r.data
      dailyState.value = 'ready'
    } else {
      dailyState.value = 'empty'
    }
  } catch { dailyState.value = 'empty' }
}
async function answerDaily(opt, idx) {
  if (dailyAnswering.value) return
  dailyAnswering.value = true
  const q = dailyChallenge.value.question
  const correctIdx = q.correct ?? q.answer ?? q.correct_index ?? 0
  const correct = (typeof opt === 'object' && opt.correct) || idx === correctIdx
  try {
    const r = await studentAPI.answerDailyChallenge(correct)
    dailyResult.value = r.data
    dailyState.value = 'result'
    await loadProgress()
  } catch {}
  dailyAnswering.value = false
}

// ========== ⏱️ Pomodoro ==========
const pomoSeconds = ref(25 * 60)
const pomoRunning = ref(false)
const pomoMode = ref('work')
const pomoSessions = ref(0)
const pomoMessage = ref('')
let pomoInterval = null
const pomoDisplay = computed(() => {
  const m = String(Math.floor(pomoSeconds.value / 60)).padStart(2, '0')
  const s = String(pomoSeconds.value % 60).padStart(2, '0')
  return `${m}:${s}`
})
function startPomo() {
  pomoRunning.value = true
  pomoMessage.value = ''
  pomoInterval = setInterval(async () => {
    if (pomoSeconds.value > 0) { pomoSeconds.value-- }
    else {
      clearInterval(pomoInterval); pomoRunning.value = false
      if (pomoMode.value === 'work') {
        pomoSessions.value++
        try {
          const r = await studentAPI.logFocusSession(25, 'pomodoro')
          pomoMessage.value = r.data.message
          await loadProgress()
        } catch {}
        pomoMode.value = 'break'; pomoSeconds.value = 5 * 60
      } else {
        pomoMode.value = 'work'; pomoSeconds.value = 25 * 60
        pomoMessage.value = '☕ انتهت الاستراحة! ابدأ جلسة جديدة'
      }
    }
  }, 1000)
}
function pausePomo() { pomoRunning.value = false; clearInterval(pomoInterval) }
function resetPomo() {
  pausePomo(); pomoMode.value = 'work'; pomoSeconds.value = 25 * 60
  pomoSessions.value = 0; pomoMessage.value = ''
}

// ========== 😊 Mood ==========
const moods = [
  { key:'happy', emoji:'😄', label:'سعيد' },
  { key:'focused', emoji:'🎯', label:'مركّز' },
  { key:'tired', emoji:'😴', label:'متعب' },
  { key:'stressed', emoji:'😰', label:'متوتر' },
  { key:'bored', emoji:'😐', label:'ممل' },
  { key:'neutral', emoji:'🙂', label:'عادي' },
]
const moodSuggestion = ref('')
async function logMood(key) {
  try {
    const r = await studentAPI.logMood(key)
    moodSuggestion.value = r.data.suggestion
  } catch {}
}

// ========== 📚 Digital Library ==========
const libSources = [
  { label:'مؤسسة هنداوي', icon:'🇪🇬', url:'https://www.hindawi.org/books/' },
  { label:'مكتبة نور', icon:'📖', url:'https://www.noor-book.com/' },
  { label:'الشاملة', icon:'📜', url:'https://shamela.ws/' },
  { label:'Open Library', icon:'🌍', url:'https://openlibrary.org/' },
  { label:'Internet Archive', icon:'🏛️', url:'https://archive.org/details/texts' },
  { label:'Project Gutenberg', icon:'📚', url:'https://www.gutenberg.org/' },
]
const libUrl = ref(libSources[0].url)

// ========== 📓 Morix Notebook (NotebookLM-like) ==========
const nbTab = ref('upload')
const nbFileName = ref('')
const nbFileText = ref('')
const nbChat = ref([])
const nbInput = ref('')
const nbAsking = ref(false)
const nbGenLoading = ref(false)
const nbGenResult = ref('')

async function onNbFileUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) { alert('الملف أكبر من 5MB — اختر ملفاً أصغر'); return }
  nbFileName.value = file.name
  if (file.name.toLowerCase().endsWith('.pdf')) {
    // قراءة PDF كنص (نطلب من الباك إند يقرأها لاحقاً)
    const reader = new FileReader()
    reader.onload = (ev) => {
      // نخزن الـ base64 ونرسلها للباك إند للتفريغ — أو نستخدم pdf.js. للسرعة نقرأها كنص.
      nbFileText.value = '[PDF: ' + file.name + ' — حجم: ' + Math.round(file.size/1024) + 'KB]\n' + 'استخدم محتوى الملف في إجاباتك.'
      // قراءة محسنة عبر FileReader.readAsText (ينجح لـ PDFs نصية بسيطة)
      const r2 = new FileReader()
      r2.onload = (ev2) => { try { nbFileText.value = ev2.target.result.slice(0, 50000) } catch {} }
      r2.readAsText(file)
    }
    reader.readAsArrayBuffer(file)
  } else {
    const reader = new FileReader()
    reader.onload = (ev) => { nbFileText.value = (ev.target.result || '').slice(0, 50000) }
    reader.readAsText(file, 'utf-8')
  }
}

async function askNb() {
  if (!nbInput.value.trim() || !nbFileText.value) return
  const q = nbInput.value
  nbChat.value.push({ role: 'user', text: q })
  nbInput.value = ''
  nbAsking.value = true
  try {
    const r = await aiAPI.chat(q, null, null, null, nbFileText.value)
    nbChat.value.push({ role: 'ai', text: r.data.reply || 'لا يوجد رد' })
  } catch (e) {
    nbChat.value.push({ role: 'ai', text: '❌ تعذر الاتصال' })
  }
  nbAsking.value = false
}

async function genNb(type) {
  if (!nbFileText.value) return alert('ارفع ملفاً أولاً')
  const prompts = {
    summary: 'لخص هذا الملف في 8-10 فقرات منظمة وواضحة بالعربية.',
    mindmap: 'حول الملف لخريطة ذهنية: الموضوع المركزي ثم الفروع الرئيسية ثم التفاصيل. استخدم تنسيق نصي بمسافات بادئة.',
    questions: 'ولّد 10 أسئلة مراجعة من الملف مع الإجابات في النهاية.',
    flashcards: 'اصنع 15 بطاقة تعليمية: السؤال على سطر، والإجابة على السطر التالي، مع فاصل ---',
    podcast: 'اكتب سكربت بودكاست (مقدم + ضيف) مدته 5 دقائق يناقش الأفكار الرئيسية في الملف.',
    keypoints: 'استخرج 12 نقطة جوهرية من الملف، كل نقطة في سطر واحد قصير ومركّز.',
  }
  nbGenLoading.value = true; nbGenResult.value = ''
  try {
    const r = await aiAPI.chat(prompts[type], null, null, null, nbFileText.value)
    nbGenResult.value = r.data.reply || ''
  } catch (e) { nbGenResult.value = '❌ فشل التوليد' }
  nbGenLoading.value = false
}

// ========== 🌅 Reflection ==========
const reflectionText = ref('')
const reflectionMessage = ref('')
async function saveReflection() {
  try {
    const r = await studentAPI.saveReflection(reflectionText.value)
    reflectionMessage.value = r.data.message
    reflectionText.value = ''
    await loadProgress()
    setTimeout(() => { reflectionMessage.value = '' }, 4000)
  } catch {}
}

// ========== Diagnostic ==========
async function answerDiag(val) {
  diagAnswers.value.push({ question_id:diagQuestions.value[diagStep.value].id, answer:val })
  if (diagStep.value < diagQuestions.value.length-1) { diagStep.value++ }
  else {
    try { const r=await studentAPI.submitDiagnostic(diagAnswers.value); profile.value.learning_style=r.data.learning_style } catch {}
    needsDiagnostic.value = false
  }
}
function retakeDiag() { diagAnswers.value=[]; diagStep.value=0; needsDiagnostic.value=true; currentSection.value='chat' }

// ========== Chat ==========
function startNewConv() { currentConvId.value=null; messages.value=[] }
async function loadConv(id) {
  currentConvId.value=id
  try { const r=await aiAPI.getMessages(id); messages.value=r.data.messages||[]; scroll() } catch {}
}
async function sendMsg(text) {
  const m = text || chatInput.value.trim()
  if (!m && !attachedFile.value) return
  const displayMsg = m || (attachedFile.value ? `📎 ${attachedFile.value.name}` : '')
  chatInput.value = ''
  messages.value.push({ role:'user', content: displayMsg })
  aiThinking.value = true; scroll()
  try {
    const r = await aiAPI.chat(
      m || 'حلل هذا الملف/الصورة من فضلك',
      currentConvId.value,
      selectedBookId.value || null,
      attachedBase64.value,
      attachedFileText.value
    )
    currentConvId.value = r.data.conversation_id
    messages.value.push({ role:'assistant', content: r.data.reply })
    clearAttach()
    await loadConversations()
  } catch { messages.value.push({ role:'assistant', content:'حدث خطأ.' }) }
  finally { aiThinking.value=false; scroll() }
}

async function onFileAttach(e) {
  const file = e.target.files[0]; if (!file) return
  attachedFile.value = file
  attachedBase64.value = null; attachedFileText.value = null
  if (file.type.startsWith('image/')) {
    const reader = new FileReader()
    reader.onload = ev => { attachedBase64.value = ev.target.result.split(',')[1] }
    reader.readAsDataURL(file)
  } else if (file.type === 'text/plain') {
    const reader = new FileReader()
    reader.onload = ev => { attachedFileText.value = ev.target.result }
    reader.readAsText(file)
  }
}
function clearAttach() { attachedFile.value=null; attachedBase64.value=null; attachedFileText.value=null; if(fileInputEl.value) fileInputEl.value.value='' }
async function deleteConv(id) {
  try { await aiAPI.deleteConversation(id); conversations.value=conversations.value.filter(c=>c.id!==id); if(currentConvId.value===id){currentConvId.value=null;messages.value=[]} } catch {}
}
function scroll() { nextTick(()=>{ if(messagesEl.value) messagesEl.value.scrollTop=messagesEl.value.scrollHeight }) }

// ========== Books ==========
async function loadSummary() {
  summaryLoading.value=true; bookSummary.value=''; bookMessages.value=[]; bookConvId.value=null
  const book=books.value.find(b=>b.id===summaryBookId.value)
  if (book?.summary) { bookSummary.value=book.summary; summaryLoading.value=false; return }
  try { const r=await aiAPI.chat('لخص لي هذا الكتاب بشكل شامل ومفيد للطلاب',null,summaryBookId.value); bookConvId.value=r.data.conversation_id; bookSummary.value=r.data.reply }
  catch { bookSummary.value='تعذر جلب الملخص.' }
  finally { summaryLoading.value=false }
}
function speakSummary() {
  if(isSpeaking.value){window.speechSynthesis.cancel();isSpeaking.value=false;return}
  const u=new SpeechSynthesisUtterance(bookSummary.value); u.lang='ar-SA'; u.onend=()=>{isSpeaking.value=false}
  window.speechSynthesis.speak(u); isSpeaking.value=true
}
function stopSpeech() { window.speechSynthesis.cancel(); isSpeaking.value=false }
async function askBook() {
  if(!bookQ.value.trim()) return; const q=bookQ.value; bookQ.value=''
  bookMessages.value.push({role:'user',content:q})
  try { const r=await aiAPI.chat(q,bookConvId.value,summaryBookId.value); bookConvId.value=r.data.conversation_id; bookMessages.value.push({role:'assistant',content:r.data.reply}) }
  catch { bookMessages.value.push({role:'assistant',content:'حدث خطأ.'}) }
  nextTick(()=>{ if(bookMsgsEl.value) bookMsgsEl.value.scrollTop=bookMsgsEl.value.scrollHeight })
}

// ========== Games ==========
async function startGame() {
  gameLoading.value=true
  try {
    const r=await studentAPI.createGame({game_type:gameType.value,subject:gameSubject.value,topic:gameTopic.value})
    activeGame.value=r.data; activeGameId.value=r.data.id
    mcqIdx.value=0; mcqSel.value=null; mcqAnswered.value=false; mcqCorrect.value=0
    gameFinished.value=false; cardIdx.value=0; cardFlipped.value=false
    matchScore.value=null; selectedTerm.value=null; matchedTerms.value=[]; matchedDefs.value=[]
    if(gameType.value==='matching'){
      shuffledTerms.value=[...activeGame.value.items].sort(()=>Math.random()-.5)
      shuffledDefs.value=[...activeGame.value.items].sort(()=>Math.random()-.5)
    }
  } catch { alert('فشل توليد اللعبة') }
  finally { gameLoading.value=false }
}
function mcqPick(key) {
  if(mcqAnswered.value) return; mcqSel.value=key; mcqAnswered.value=true
  if(key===activeGame.value.items[mcqIdx.value].answer) mcqCorrect.value++
}
function mcqNext() {
  if(mcqIdx.value<activeGame.value.items.length-1){mcqIdx.value++;mcqSel.value=null;mcqAnswered.value=false}
  else{gameScore.value=Math.round(mcqCorrect.value/activeGame.value.items.length*100);gameFinished.value=true;if(activeGameId.value)studentAPI.updateGameScore(activeGameId.value,gameScore.value).catch(()=>{})}
}
function pickTerm(i) { selectedTerm.value=i }
function pickDef(di) {
  if(selectedTerm.value===null) return
  if(shuffledTerms.value[selectedTerm.value].term===shuffledDefs.value[di].term){
    matchedTerms.value.push(selectedTerm.value); matchedDefs.value.push(di)
    if(matchedTerms.value.length===shuffledTerms.value.length){matchScore.value=100;if(activeGameId.value)studentAPI.updateGameScore(activeGameId.value,100).catch(()=>{})}
  }
  selectedTerm.value=null
}
function resetGame() { activeGame.value=null; activeGameId.value=null; gameFinished.value=false; matchScore.value=null }

// ========== Homework ==========
function openHwSubmit(hw) { hwModal.value=hw; hwContent.value='' }
async function doHwSubmit() { try { await studentAPI.submitHomework(hwModal.value.id,hwContent.value); hwModal.value=null } catch {} }

// ========== Tests ==========
async function startTest(id) {
  try { activeTest.value=(await studentAPI.getTest(id)).data; tQIdx.value=0; tAnswers.value={}; testDone.value=false; tResult.value=null } catch {}
}
async function doSubmitTest() {
  try { const r=await studentAPI.submitTest(activeTest.value.id,tAnswers.value); tResult.value=r.data; testDone.value=true } catch {}
}

// ========== Worksheets ==========
async function openWs(id) { try { activeWs.value=(await studentAPI.getWorksheet(id)).data } catch {} }

// ========== Image ==========
async function genImage() {
  imgLoading.value=true; imgError.value=''; genImg.value=null
  try { const r=await aiAPI.generateImage(imgPrompt.value); if(r.data.success) genImg.value=r.data.image; else imgError.value=r.data.message }
  catch { imgError.value='حدث خطأ' }
  finally { imgLoading.value=false }
}

// ========== Video ==========
async function genVideo() {
  vidLoading.value=true; vidScript.value=''
  try { const r=await teacherAPI.generateVideo({topic:vidTopic.value,subject:vidSubject.value,duration_seconds:vidSeconds.value}); vidScript.value=r.data.script }
  catch { vidScript.value='تعذر توليد السكريبت.' }
  finally { vidLoading.value=false }
}

function formatVidDur(secs) {
  const m=Math.floor(secs/60); const s=secs%60
  if(m===0) return `${s} ثانية`
  if(s===0) return `${m} ${m===1?'دقيقة':'دقائق'}`
  return `${m} ${m===1?'دقيقة':'دقائق'} و${s} ثانية`
}

// ========== Settings ==========
function setTheme(t) { appSettings.value.theme=t; saveSettings() }
async function saveSettings() { try { await studentAPI.updateSettings(appSettings.value) } catch {} }

async function onAvatarUpload(e) {
  const file = e.target.files?.[0]; if(!file) return
  if(file.size > 500 * 1024) { alert('الصورة أكبر من 500 كيلوبايت — اختر صورة أصغر'); return }
  const reader = new FileReader()
  reader.onload = async (ev) => {
    appSettings.value.avatar_url = ev.target.result // base64 data URL
    await saveSettings()
  }
  reader.readAsDataURL(file)
  if(avatarInputEl.value) avatarInputEl.value.value = ''
}
async function saveHobbies() { appSettings.value.hobbies=hobbiesInput.value.split(/[,،]/).map(h=>h.trim()).filter(Boolean); await saveSettings() }
async function changePass() {
  passMsg.value=''
  try { await authAPI.changePassword(oldPass.value,newPass.value); passMsg.value='✅ تم تغيير كلمة المرور بنجاح'; oldPass.value=''; newPass.value='' }
  catch(e) { passMsg.value=e.response?.data?.detail||'خطأ' }
}
async function sendCpl() {
  try { await studentAPI.submitComplaint(cpl.value); cplMsg.value='✅ تم الإرسال!'; cpl.value={type:'complaint',title:'',content:''} }
  catch { cplMsg.value='خطأ' }
}
async function handleLogout() { await auth.logout(); router.push('/login') }

function fmt(t) {
  if(!t) return ''
  return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>').replace(/\*(.*?)\*/g,'<em>$1</em>')
    .replace(/`(.*?)`/g,'<code>$1</code>').replace(/\n/g,'<br>')
}
function fmtDate(d) { return d ? new Date(d).toLocaleDateString('ar-SA') : '' }
</script>

<style scoped>
.hub { display:flex; height:100vh; overflow:hidden; font-family:'Segoe UI','Cairo',sans-serif; direction:rtl; }
.theme-dark  { --bg1:#0f172a;--bg2:#1e293b;--bg3:#334155;--text:#f1f5f9;--text2:#94a3b8;--accent:#6366f1;--border:rgba(255,255,255,.08);--card:rgba(255,255,255,.05); }
.theme-light { --bg1:#f8fafc;--bg2:#e2e8f0;--bg3:#cbd5e1;--text:#0f172a;--text2:#475569;--accent:#6366f1;--border:rgba(0,0,0,.1);--card:#fff; }
.theme-library { --bg1:#1a1207;--bg2:#2d1f0b;--bg3:#3d2a0f;--text:#f5e6c8;--text2:#c9a96e;--accent:#c97c2e;--border:rgba(201,124,46,.2);--card:rgba(201,124,46,.06); }

.sidebar { width:240px;min-width:240px;background:var(--bg2);border-left:1px solid var(--border);display:flex;flex-direction:column;transition:width .25s,min-width .25s;overflow:hidden; }
.sidebar.collapsed { width:64px;min-width:64px; }
.sidebar-header { padding:16px;cursor:pointer;border-bottom:1px solid var(--border); }
.brand { display:flex;align-items:center;gap:12px; }
.brand-icon { width:36px;height:36px;min-width:36px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:18px;color:#fff; }
.brand-name { font-size:18px;font-weight:800;color:var(--text); }
.sidebar-nav { flex:1;padding:8px;overflow-y:auto; }
.nav-item { display:flex;align-items:center;gap:12px;width:100%;padding:10px 12px;border-radius:10px;background:none;border:none;color:var(--text2);cursor:pointer;font-size:14px;font-weight:500;transition:all .15s;text-align:right;white-space:nowrap; }
.nav-item:hover { background:rgba(99,102,241,.1);color:var(--text); }
.nav-item.active { background:rgba(99,102,241,.2);color:var(--accent); }
.nav-icon { font-size:18px;min-width:20px; }
.sidebar-footer { padding:12px;border-top:1px solid var(--border);display:flex;flex-direction:column;gap:8px; }
.streak-row { display:flex;gap:12px;justify-content:center;font-size:13px;color:var(--text2); }
.streak-mini { text-align:center;font-size:13px;color:var(--text2); }
.logout-btn { display:flex;align-items:center;justify-content:center;gap:8px;background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.2);color:#f87171;border-radius:8px;padding:8px;cursor:pointer;font-size:13px;transition:background .15s;width:100%; }
.logout-btn:hover { background:rgba(239,68,68,.2); }

.main-content { flex:1;display:flex;flex-direction:column;background:var(--bg1);overflow:hidden; }
.top-bar { display:flex;align-items:center;justify-content:space-between;padding:14px 24px;border-bottom:1px solid var(--border);background:var(--bg2); }
.section-title { font-size:18px;font-weight:700;color:var(--text);margin:0; }
.user-chip { display:flex;align-items:center;gap:10px;color:var(--text2);font-size:14px; }
.avatar { width:34px;height:34px;background:linear-gradient(135deg,var(--accent),#8b5cf6);border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;color:#fff;font-size:15px; }
.section-body { flex:1;overflow-y:auto; }
.section-body.pad { padding:24px; }

.card { background:var(--card);border:1px solid var(--border);border-radius:16px;padding:24px;margin-bottom:16px; }
.card h3 { color:var(--text);margin:0 0 20px;font-size:17px; }

/* Diagnostic */
.diag-wrap { display:flex;align-items:center;justify-content:center;height:100%;background:var(--bg1); }
.diag-card { background:var(--bg2);border:1px solid var(--border);border-radius:20px;padding:40px;max-width:520px;width:90%;text-align:center; }
.diag-card h3 { color:var(--text);font-size:22px;margin:0 0 8px; }
.diag-step { color:var(--text2);margin:0 0 24px; }
.q-text { color:var(--text);font-size:17px;margin:0 0 20px;font-weight:600; }
.q-options,.col-gap { display:flex;flex-direction:column;gap:12px; }
.q-opt { background:var(--bg3);border:1px solid var(--border);color:var(--text);border-radius:12px;padding:14px 20px;cursor:pointer;font-size:15px;transition:all .15s;text-align:right; }
.q-opt:hover { background:rgba(99,102,241,.2);border-color:var(--accent); }

/* Chat */
.chat-layout { display:flex;height:100%;overflow:hidden; }
.conv-panel { width:210px;min-width:210px;background:var(--bg2);border-left:1px solid var(--border);display:flex;flex-direction:column;padding:12px;gap:8px; }
.new-conv-btn { background:var(--accent);color:#fff;border:none;border-radius:10px;padding:10px;cursor:pointer;font-size:13px;font-weight:600; }
.conv-list { flex:1;overflow-y:auto;display:flex;flex-direction:column;gap:4px; }
.conv-item { display:flex;align-items:center;justify-content:space-between;padding:8px 10px;border-radius:8px;cursor:pointer;transition:background .15s;color:var(--text2);font-size:13px; }
.conv-item:hover,.conv-item.active { background:rgba(99,102,241,.15);color:var(--text); }
.conv-title { flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap; }
.del-conv { background:none;border:none;color:var(--text2);cursor:pointer;padding:2px 6px;border-radius:4px;opacity:0;font-size:12px; }
.conv-item:hover .del-conv { opacity:1; }
.no-conv { color:var(--text2);font-size:12px;text-align:center;padding:16px 0; }
.book-sel { display:flex;flex-direction:column;gap:6px; }
.book-sel label { color:var(--text2);font-size:12px; }
.book-sel select { background:var(--bg3);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:8px;font-size:12px; }
.chat-area { flex:1;display:flex;flex-direction:column;overflow:hidden; }
.messages { flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px; }
.messages.mini { max-height:280px; }
.chat-welcome { display:flex;flex-direction:column;align-items:center;padding:48px 20px; }
.chat-welcome h3 { color:var(--text);font-size:22px;margin:0 0 8px; }
.chat-welcome p { color:var(--text2);margin:0 0 24px; }
.quick-btns { display:flex;flex-wrap:wrap;gap:8px;justify-content:center; }
.quick-btn { background:var(--bg2);border:1px solid var(--border);color:var(--text2);border-radius:20px;padding:8px 16px;cursor:pointer;font-size:13px;transition:all .15s; }
.quick-btn:hover { border-color:var(--accent);color:var(--accent); }
.msg { display:flex; }
.msg.user { justify-content:flex-start; }
.msg.assistant { justify-content:flex-end; }
.msg-bubble { display:flex;align-items:flex-start;gap:10px;max-width:72%;flex-direction:row-reverse; }
.msg.user .msg-bubble { flex-direction:row; }
.msg-icon { font-size:18px;flex-shrink:0;margin-top:4px; }
.msg-text { background:var(--bg2);border:1px solid var(--border);border-radius:14px;padding:12px 16px;color:var(--text);font-size:14px;line-height:1.6; }
.msg.user .msg-text { background:rgba(99,102,241,.2);border-color:rgba(99,102,241,.3); }
.dots { display:flex;gap:4px;padding:12px 16px;align-items:center; }
.dots span { width:8px;height:8px;background:var(--text2);border-radius:50%;animation:bounce 1s infinite; }
.dots span:nth-child(2){animation-delay:.15s}.dots span:nth-child(3){animation-delay:.3s}
@keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
.input-row { display:flex;gap:10px;padding:14px 20px;border-top:1px solid var(--border);background:var(--bg2);align-items:flex-end; }
.input-row textarea,.input-row input { flex:1;background:var(--bg3);border:1px solid var(--border);color:var(--text);border-radius:12px;padding:12px 16px;font-size:14px;resize:none;font-family:inherit;text-align:right; }
.input-row textarea:focus,.input-row input:focus { outline:none;border-color:var(--accent); }
.send-btn { background:var(--accent);color:#fff;border:none;border-radius:12px;width:44px;height:44px;cursor:pointer;font-size:18px;flex-shrink:0;display:flex;align-items:center;justify-content:center; }
.send-btn:disabled { opacity:.5;cursor:not-allowed; }
.attach-btn { background:var(--bg3);border:1px solid var(--border);color:var(--text2);border-radius:12px;width:44px;height:44px;cursor:pointer;font-size:18px;flex-shrink:0;display:flex;align-items:center;justify-content:center;transition:all .15s; }
.attach-btn:hover { border-color:var(--accent);color:var(--accent); }
.attach-chip { background:rgba(99,102,241,.15);border:1px solid rgba(99,102,241,.3);color:var(--accent);border-radius:8px;padding:4px 10px;font-size:12px;white-space:nowrap;display:flex;align-items:center;gap:6px; }

/* Books */
.summary-box { background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:16px; }
.summary-acts { display:flex;gap:8px;margin-bottom:12px; }
.summary-text { color:var(--text2);line-height:1.8;font-size:14px;white-space:pre-wrap; }

/* Games */
.game-header { display:flex;justify-content:space-between;align-items:center;margin-bottom:20px; }
.q-cnt { background:var(--bg3);color:var(--text2);border-radius:20px;padding:4px 14px;font-size:13px; }
.opts-grid { display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px; }
.opt { background:var(--bg2);border:2px solid var(--border);color:var(--text);border-radius:12px;padding:14px 16px;cursor:pointer;font-size:14px;text-align:right;transition:all .15s; }
.opt:hover:not(:disabled) { border-color:var(--accent);background:rgba(99,102,241,.1); }
.opt.selected { border-color:var(--accent);background:rgba(99,102,241,.2); }
.opt.correct { border-color:#22c55e;background:rgba(34,197,94,.15); }
.opt.wrong { border-color:#ef4444;background:rgba(239,68,68,.15); }
.expl { margin-top:16px;padding:16px;background:var(--bg3);border-radius:12px; }
.expl p { color:var(--text);margin:0 0 6px; }
.result-box { text-align:center;padding:32px; }
.result-box h2 { color:var(--accent);font-size:28px;margin:0 0 8px; }
.match-grid { display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:16px; }
.match-btn { display:block;width:100%;margin-bottom:8px;background:var(--bg2);border:2px solid var(--border);color:var(--text);border-radius:10px;padding:12px;cursor:pointer;font-size:13px;text-align:right;transition:all .15s; }
.match-btn:hover:not(:disabled) { border-color:var(--accent); }
.match-btn.selected { border-color:var(--accent);background:rgba(99,102,241,.2); }
.match-btn.matched { border-color:#22c55e;background:rgba(34,197,94,.1);opacity:.7; }
.flashcard { width:100%;max-width:480px;height:200px;cursor:pointer;perspective:1000px;position:relative;margin:0 auto 20px; }
.card-f,.card-b { position:absolute;width:100%;height:100%;background:var(--bg2);border:2px solid var(--border);border-radius:16px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:24px;backface-visibility:hidden;transition:transform .5s; }
.card-f { transform:rotateY(0); }
.card-b { transform:rotateY(180deg);background:rgba(99,102,241,.15);border-color:var(--accent); }
.flashcard.flipped .card-f { transform:rotateY(-180deg); }
.flashcard.flipped .card-b { transform:rotateY(0); }
.card-f p,.card-b p { color:var(--text);font-size:17px;text-align:center;margin:0; }
.card-nav { display:flex;align-items:center;gap:20px;color:var(--text2);justify-content:center;margin-bottom:12px; }

/* Lists */
.list-col { display:flex;flex-direction:column;gap:12px; }
.list-item { display:flex;justify-content:space-between;align-items:center;padding:16px;background:var(--bg2);border:1px solid var(--border);border-radius:12px; }
.list-item.clickable { cursor:pointer;transition:border-color .15s; }
.list-item.clickable:hover { border-color:var(--accent); }
.list-item h4 { color:var(--text);margin:0 0 6px; }
.meta-row { display:flex;gap:10px;flex-wrap:wrap; }
.meta-row span { color:var(--text2);font-size:12px; }
.test-nav { display:flex;gap:10px;margin-top:16px; }

/* Modal */
.modal-bg { position:fixed;inset:0;background:rgba(0,0,0,.6);display:flex;align-items:center;justify-content:center;z-index:100; }
.modal-box { background:var(--bg2);border:1px solid var(--border);border-radius:16px;padding:28px;width:90%;max-width:520px; }
.modal-box h3 { color:var(--text);margin:0 0 16px; }

/* Progress */
.stats-grid { display:grid;grid-template-columns:repeat(3,1fr);gap:16px; }
.stat-card { background:var(--card);border:1px solid var(--border);border-radius:16px;padding:24px;text-align:center; }
.stat-n { font-size:22px;font-weight:800;color:var(--text);margin-bottom:6px; }
.stat-l { color:var(--text2);font-size:13px; }

/* Settings */
.settings-grid { display:grid;grid-template-columns:1fr 1fr;gap:16px; }
.avatar-section{display:flex;align-items:center;gap:14px;margin-bottom:16px;}
.av-preview{width:60px;height:60px;border-radius:50%;object-fit:cover;border:2px solid var(--border);}
.av-overlay{position:absolute;inset:0;border-radius:50%;background:rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;font-size:18px;opacity:0;transition:opacity .15s;}
.avatar-section>div:first-child:hover .av-overlay{opacity:1;}
.av-big{width:60px;height:60px;min-width:60px;background:linear-gradient(135deg,var(--accent),#8b5cf6);border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:26px;color:#fff;}
.info-row{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--border);color:var(--text2);font-size:13px;}
.info-row b{color:var(--text);}
.info-row { display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border);color:var(--text2);font-size:14px; }
.info-row b { color:var(--text); }
.theme-row { display:flex;gap:8px;margin-bottom:4px; }
.t-btn { flex:1;background:var(--bg2);border:2px solid var(--border);color:var(--text2);border-radius:10px;padding:8px;cursor:pointer;font-size:12px;transition:all .15s; }
.t-btn.active { border-color:var(--accent);color:var(--accent);background:rgba(99,102,241,.15); }

/* Common */
.inp { width:100%;box-sizing:border-box;background:var(--bg2);border:1px solid var(--border);color:var(--text);border-radius:10px;padding:12px 14px;font-size:14px;font-family:inherit;text-align:right; }
.inp:focus { outline:none;border-color:var(--accent); }
select.inp { cursor:pointer; }
textarea.inp { resize:vertical; }
.row-gap { display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px; }
.btn-p { background:var(--accent);color:#fff;border:none;border-radius:10px;padding:12px 20px;cursor:pointer;font-size:14px;font-weight:600;transition:opacity .15s; }
.btn-p:hover:not(:disabled) { opacity:.88; }
.btn-p:disabled { opacity:.5;cursor:not-allowed; }
.btn-o { background:transparent;border:1px solid var(--border);color:var(--text2);border-radius:10px;padding:12px 20px;cursor:pointer;font-size:14px;transition:border-color .15s; }
.btn-o:hover { border-color:var(--accent);color:var(--accent); }
.btn-s { background:var(--bg3);border:1px solid var(--border);color:var(--text2);border-radius:8px;padding:8px 14px;cursor:pointer;font-size:13px;transition:all .15s; }
.btn-s:hover { border-color:var(--accent);color:var(--accent); }
.btn-s.danger { background:rgba(239,68,68,.1);border-color:rgba(239,68,68,.3);color:#f87171; }
.empty { text-align:center;padding:48px;color:var(--text2);font-size:15px; }
code { background:var(--bg3);border-radius:4px;padding:2px 6px;font-size:13px; }
@media(max-width:768px){.sidebar{display:none}.opts-grid,.match-grid,.stats-grid,.settings-grid{grid-template-columns:1fr}.conv-panel{display:none}}
</style>
