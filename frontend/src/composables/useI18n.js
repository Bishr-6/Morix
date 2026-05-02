// نظام الترجمة متعدد اللغات - 6 لغات
import { ref, computed, watch } from 'vue'

export const LANGUAGES = {
  ar: { code: 'ar', name: 'العربية', flag: '🇸🇦', dir: 'rtl' },
  en: { code: 'en', name: 'English', flag: '🇬🇧', dir: 'ltr' },
  zh: { code: 'zh', name: '中文', flag: '🇨🇳', dir: 'ltr' },
  de: { code: 'de', name: 'Deutsch', flag: '🇩🇪', dir: 'ltr' },
  es: { code: 'es', name: 'Español', flag: '🇪🇸', dir: 'ltr' },
  fr: { code: 'fr', name: 'Français', flag: '🇫🇷', dir: 'ltr' },
}

const TRANSLATIONS = {
  // ============================================================
  // عام
  // ============================================================
  app_name: { ar:'موريكس', en:'Morix', zh:'莫瑞克斯', de:'Morix', es:'Morix', fr:'Morix' },
  tagline: { ar:'منصة التعلم الذكي', en:'Smart Learning Platform', zh:'智能学习平台', de:'Intelligente Lernplattform', es:'Plataforma de Aprendizaje Inteligente', fr:'Plateforme d\'Apprentissage Intelligent' },

  // أدوار
  role_owner: { ar:'مالك', en:'Owner', zh:'所有者', de:'Besitzer', es:'Propietario', fr:'Propriétaire' },
  role_manager: { ar:'مدير', en:'Manager', zh:'经理', de:'Manager', es:'Gerente', fr:'Gérant' },
  role_admin: { ar:'إداري', en:'Admin', zh:'管理员', de:'Verwalter', es:'Administrador', fr:'Administrateur' },
  role_teacher: { ar:'معلم', en:'Teacher', zh:'教师', de:'Lehrer', es:'Profesor', fr:'Enseignant' },
  role_student: { ar:'طالب', en:'Student', zh:'学生', de:'Schüler', es:'Estudiante', fr:'Étudiant' },

  // أزرار شائعة
  save: { ar:'حفظ', en:'Save', zh:'保存', de:'Speichern', es:'Guardar', fr:'Enregistrer' },
  cancel: { ar:'إلغاء', en:'Cancel', zh:'取消', de:'Abbrechen', es:'Cancelar', fr:'Annuler' },
  delete: { ar:'حذف', en:'Delete', zh:'删除', de:'Löschen', es:'Eliminar', fr:'Supprimer' },
  edit: { ar:'تعديل', en:'Edit', zh:'编辑', de:'Bearbeiten', es:'Editar', fr:'Modifier' },
  add: { ar:'إضافة', en:'Add', zh:'添加', de:'Hinzufügen', es:'Añadir', fr:'Ajouter' },
  search: { ar:'بحث', en:'Search', zh:'搜索', de:'Suchen', es:'Buscar', fr:'Rechercher' },
  loading: { ar:'جاري التحميل...', en:'Loading...', zh:'加载中...', de:'Wird geladen...', es:'Cargando...', fr:'Chargement...' },
  send: { ar:'إرسال', en:'Send', zh:'发送', de:'Senden', es:'Enviar', fr:'Envoyer' },
  logout: { ar:'تسجيل خروج', en:'Logout', zh:'退出', de:'Abmelden', es:'Cerrar sesión', fr:'Déconnexion' },
  login: { ar:'تسجيل الدخول', en:'Login', zh:'登录', de:'Anmelden', es:'Iniciar sesión', fr:'Connexion' },
  back: { ar:'رجوع', en:'Back', zh:'返回', de:'Zurück', es:'Volver', fr:'Retour' },
  confirm: { ar:'تأكيد', en:'Confirm', zh:'确认', de:'Bestätigen', es:'Confirmar', fr:'Confirmer' },

  // ============================================================
  // تسجيل الدخول
  // ============================================================
  email: { ar:'البريد الإلكتروني', en:'Email', zh:'电子邮件', de:'E-Mail', es:'Correo electrónico', fr:'E-mail' },
  password: { ar:'كلمة المرور', en:'Password', zh:'密码', de:'Passwort', es:'Contraseña', fr:'Mot de passe' },
  login_error: { ar:'الإيميل أو كلمة المرور غلط', en:'Invalid email or password', zh:'邮箱或密码错误', de:'Ungültige E-Mail oder Passwort', es:'Email o contraseña inválidos', fr:'Email ou mot de passe invalide' },
  demo_accounts: { ar:'بيانات تجريبية', en:'Demo Accounts', zh:'演示账户', de:'Demo-Konten', es:'Cuentas demo', fr:'Comptes démo' },

  // ============================================================
  // الإعدادات
  // ============================================================
  settings: { ar:'الإعدادات', en:'Settings', zh:'设置', de:'Einstellungen', es:'Configuración', fr:'Paramètres' },
  profile: { ar:'الملف الشخصي', en:'Profile', zh:'个人资料', de:'Profil', es:'Perfil', fr:'Profil' },
  appearance: { ar:'المظهر', en:'Appearance', zh:'外观', de:'Aussehen', es:'Apariencia', fr:'Apparence' },
  theme: { ar:'الثيم', en:'Theme', zh:'主题', de:'Thema', es:'Tema', fr:'Thème' },
  theme_dark: { ar:'داكن', en:'Dark', zh:'深色', de:'Dunkel', es:'Oscuro', fr:'Sombre' },
  theme_light: { ar:'فاتح', en:'Light', zh:'浅色', de:'Hell', es:'Claro', fr:'Clair' },
  theme_library: { ar:'المكتبة', en:'Library', zh:'图书馆', de:'Bibliothek', es:'Biblioteca', fr:'Bibliothèque' },
  brightness: { ar:'السطوع', en:'Brightness', zh:'亮度', de:'Helligkeit', es:'Brillo', fr:'Luminosité' },
  language: { ar:'اللغة', en:'Language', zh:'语言', de:'Sprache', es:'Idioma', fr:'Langue' },
  notifications: { ar:'الإشعارات', en:'Notifications', zh:'通知', de:'Benachrichtigungen', es:'Notificaciones', fr:'Notifications' },
  notifications_enabled: { ar:'تفعيل الإشعارات', en:'Enable notifications', zh:'启用通知', de:'Benachrichtigungen aktivieren', es:'Activar notificaciones', fr:'Activer les notifications' },
  difficulty: { ar:'الصعوبة', en:'Difficulty', zh:'难度', de:'Schwierigkeit', es:'Dificultad', fr:'Difficulté' },
  difficulty_easy: { ar:'سهل', en:'Easy', zh:'简单', de:'Leicht', es:'Fácil', fr:'Facile' },
  difficulty_medium: { ar:'متوسط', en:'Medium', zh:'中等', de:'Mittel', es:'Medio', fr:'Moyen' },
  difficulty_hard: { ar:'صعب', en:'Hard', zh:'困难', de:'Schwer', es:'Difícil', fr:'Difficile' },
  upload_avatar: { ar:'رفع صورة من الجهاز', en:'Upload avatar', zh:'上传头像', de:'Avatar hochladen', es:'Subir avatar', fr:'Télécharger un avatar' },
  account_info: { ar:'معلومات الحساب', en:'Account Info', zh:'账户信息', de:'Kontoinformationen', es:'Información de cuenta', fr:'Informations du compte' },
  full_name: { ar:'الاسم', en:'Name', zh:'姓名', de:'Name', es:'Nombre', fr:'Nom' },
  saved: { ar:'✅ تم الحفظ', en:'✅ Saved', zh:'✅ 已保存', de:'✅ Gespeichert', es:'✅ Guardado', fr:'✅ Enregistré' },
  change_password: { ar:'تغيير كلمة المرور', en:'Change password', zh:'更改密码', de:'Passwort ändern', es:'Cambiar contraseña', fr:'Changer le mot de passe' },

  // ============================================================
  // الطالب
  // ============================================================
  student_chat: { ar:'المحادثة', en:'Chat', zh:'聊天', de:'Chat', es:'Chat', fr:'Discussion' },
  books: { ar:'ملخص الكتاب', en:'Books', zh:'书籍', de:'Bücher', es:'Libros', fr:'Livres' },
  games: { ar:'الألعاب', en:'Games', zh:'游戏', de:'Spiele', es:'Juegos', fr:'Jeux' },
  homework: { ar:'الواجبات', en:'Homework', zh:'作业', de:'Hausaufgaben', es:'Tarea', fr:'Devoirs' },
  tests: { ar:'الاختبارات', en:'Tests', zh:'考试', de:'Tests', es:'Exámenes', fr:'Tests' },
  worksheets: { ar:'أوراق العمل', en:'Worksheets', zh:'练习册', de:'Arbeitsblätter', es:'Hojas de trabajo', fr:'Feuilles' },
  image_gen: { ar:'توليد صور', en:'Image Generation', zh:'生成图片', de:'Bild generieren', es:'Generar imagen', fr:'Générer image' },
  video_script: { ar:'سكريبت فيديو', en:'Video Script', zh:'视频脚本', de:'Videoskript', es:'Guion de video', fr:'Script vidéo' },
  leaderboard: { ar:'لوحة المتصدرين', en:'Leaderboard', zh:'排行榜', de:'Bestenliste', es:'Clasificación', fr:'Classement' },
  daily_challenge: { ar:'التحدي اليومي', en:'Daily Challenge', zh:'每日挑战', de:'Tägliche Herausforderung', es:'Desafío diario', fr:'Défi quotidien' },
  pomodoro: { ar:'بومودورو', en:'Pomodoro', zh:'番茄钟', de:'Pomodoro', es:'Pomodoro', fr:'Pomodoro' },
  mood: { ar:'مزاجي اليوم', en:'My Mood', zh:'我的心情', de:'Meine Stimmung', es:'Mi ánimo', fr:'Mon humeur' },
  reflection: { ar:'التأمل اليومي', en:'Daily Reflection', zh:'每日反思', de:'Tägliche Reflexion', es:'Reflexión diaria', fr:'Réflexion quotidienne' },
  digital_library: { ar:'المكتبة الرقمية', en:'Digital Library', zh:'数字图书馆', de:'Digitale Bibliothek', es:'Biblioteca digital', fr:'Bibliothèque numérique' },
  notebook: { ar:'دفتري الذكي', en:'Smart Notebook', zh:'智能笔记本', de:'Intelligentes Notizbuch', es:'Cuaderno inteligente', fr:'Carnet intelligent' },
  progress: { ar:'تقدمي', en:'My Progress', zh:'我的进度', de:'Mein Fortschritt', es:'Mi progreso', fr:'Mes progrès' },

  // ============================================================
  // المعلم
  // ============================================================
  overview: { ar:'نظرة عامة', en:'Overview', zh:'概览', de:'Übersicht', es:'Resumen', fr:'Aperçu' },
  students: { ar:'الطلاب', en:'Students', zh:'学生们', de:'Schüler', es:'Estudiantes', fr:'Étudiants' },
  ppt_generator: { ar:'توليد PPT', en:'PPT Generator', zh:'PPT生成器', de:'PPT Generator', es:'Generador PPT', fr:'Générateur PPT' },
  ai_assistant: { ar:'مساعد AI', en:'AI Assistant', zh:'AI助手', de:'KI-Assistent', es:'Asistente IA', fr:'Assistant IA' },
  lesson_plan: { ar:'خطة درس', en:'Lesson Plan', zh:'课程计划', de:'Unterrichtsplan', es:'Plan de lección', fr:'Plan de cours' },

  // ============================================================
  // المدير / المالك
  // ============================================================
  schools: { ar:'المدارس', en:'Schools', zh:'学校', de:'Schulen', es:'Escuelas', fr:'Écoles' },
  accounts: { ar:'الحسابات', en:'Accounts', zh:'账户', de:'Konten', es:'Cuentas', fr:'Comptes' },
  statistics: { ar:'الإحصائيات', en:'Statistics', zh:'统计', de:'Statistiken', es:'Estadísticas', fr:'Statistiques' },
  upload_excel: { ar:'رفع Excel', en:'Upload Excel', zh:'上传Excel', de:'Excel hochladen', es:'Subir Excel', fr:'Importer Excel' },
  add_school: { ar:'إضافة مدرسة', en:'Add School', zh:'添加学校', de:'Schule hinzufügen', es:'Añadir escuela', fr:'Ajouter école' },
  school_name: { ar:'اسم المدرسة', en:'School Name', zh:'学校名称', de:'Schulname', es:'Nombre de escuela', fr:'Nom d\'école' },
  branch: { ar:'الفرع', en:'Branch', zh:'分校', de:'Filiale', es:'Sucursal', fr:'Filiale' },
  ministry_code: { ar:'كود الوزارة', en:'Ministry Code', zh:'部委代码', de:'Ministeriumscode', es:'Código ministerio', fr:'Code ministère' },
  complaints: { ar:'الشكاوى', en:'Complaints', zh:'投诉', de:'Beschwerden', es:'Quejas', fr:'Plaintes' },
  all_users: { ar:'كل المستخدمين', en:'All Users', zh:'所有用户', de:'Alle Benutzer', es:'Todos los usuarios', fr:'Tous les utilisateurs' },
}

// الحالة العامة المشتركة
const currentLang = ref(localStorage.getItem('morix_lang') || 'ar')

// تطبيق الـ direction على الـ html
function applyDir(lang) {
  const meta = LANGUAGES[lang] || LANGUAGES.ar
  document.documentElement.setAttribute('lang', meta.code)
  document.documentElement.setAttribute('dir', meta.dir)
}

applyDir(currentLang.value)

watch(currentLang, (val) => {
  localStorage.setItem('morix_lang', val)
  applyDir(val)
})

export function useI18n() {
  const lang = currentLang
  const dir = computed(() => LANGUAGES[lang.value]?.dir || 'rtl')

  function t(key, fallback) {
    const entry = TRANSLATIONS[key]
    if (!entry) return fallback || key
    return entry[lang.value] || entry.ar || fallback || key
  }

  function setLang(newLang) {
    if (LANGUAGES[newLang]) lang.value = newLang
  }

  return { t, lang, dir, setLang, languages: LANGUAGES }
}
