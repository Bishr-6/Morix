// طبقة API - Morix Platform
import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('memorix_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('memorix_token')
      localStorage.removeItem('memorix_user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ============================================
// المصادقة
// ============================================
export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  me: () => api.get('/auth/me'),
  logout: () => api.post('/auth/logout'),
  changePassword: (oldPass, newPass) => api.post('/auth/change-password', {
    old_password: oldPass, new_password: newPass
  }),
}

// ============================================
// المدير
// ============================================
export const managerAPI = {
  getSchools: () => api.get('/manager/schools'),
  setupSchool: (data) => api.post('/manager/setup', data),
  getAccounts: (schoolId) => api.get(`/manager/accounts/${schoolId}`),
  getStats: () => api.get('/manager/stats'),
  exportCSV: (schoolId) => api.get(`/manager/export/${schoolId}`, { responseType: 'blob' }),
  getBooks: () => api.get('/manager/books'),
  addBook: (data) => api.post('/manager/books', data),
  getSavedPasswords: (schoolId) => api.get(`/manager/passwords/${schoolId}`),
}

// ============================================
// الطالب
// ============================================
export const studentAPI = {
  getQuestions: () => api.get('/student/diagnostic/questions'),
  submitDiagnostic: (answers) => api.post('/student/diagnostic/submit', { answers }),
  getProfile: () => api.get('/student/profile'),
  getProgress: () => api.get('/student/progress'),

  // الإعدادات
  getSettings: () => api.get('/student/settings'),
  updateSettings: (data) => api.put('/student/settings', data),

  // الواجبات
  getHomework: () => api.get('/student/homework'),
  submitHomework: (id, content) => api.post(`/student/homework/${id}/submit`, { content }),

  // الاختبارات
  getTests: () => api.get('/student/tests'),
  getTest: (id) => api.get(`/student/tests/${id}`),
  submitTest: (id, answers) => api.post(`/student/tests/${id}/submit`, { answers }),

  // أوراق العمل
  getWorksheets: () => api.get('/student/worksheets'),
  getWorksheet: (id) => api.get(`/student/worksheets/${id}`),

  // الألعاب
  getGames: () => api.get('/student/games'),
  createGame: (data) => api.post('/student/games', data),
  updateGameScore: (id, score) => api.put(`/student/games/${id}/score`, { score }),

  // الشكاوى
  submitComplaint: (data) => api.post('/student/complaints', data),

  // 🏆 لوحة المتصدرين
  getLeaderboard: () => api.get('/student/leaderboard'),

  // 🎯 التحدي اليومي
  getDailyChallenge: () => api.get('/student/daily-challenge'),
  answerDailyChallenge: (correct) => api.post('/student/daily-challenge/answer', { correct }),

  // 😊 الحالة المزاجية
  logMood: (mood, note = '') => api.post('/student/mood', { mood, note }),
  getMoodHistory: () => api.get('/student/mood/history'),

  // ⏱️ بومودورو
  logFocusSession: (durationMinutes, technique = 'pomodoro') =>
    api.post('/student/focus-session', { duration_minutes: durationMinutes, technique }),

  // 🧠 شخصية المعلم الذكي
  getTutorPersonalities: () => api.get('/student/tutor-personalities'),
  setTutorPersonality: (personality) => api.post('/student/tutor-personality', { personality }),

  // 🌅 التأمل اليومي
  saveReflection: (text) => api.post('/student/reflection', { text }),
}

// ============================================
// الذكاء الاصطناعي
// ============================================
export const aiAPI = {
  chat: (message, conversationId = null, bookId = null, imageBase64 = null, fileText = null) => api.post('/ai/chat', {
    message, conversation_id: conversationId, book_id: bookId,
    image_base64: imageBase64 || undefined,
    file_text: fileText || undefined,
  }),
  getConversations: () => api.get('/ai/conversations'),
  getMessages: (conversationId) => api.get(`/ai/conversations/${conversationId}/messages`),
  deleteConversation: (conversationId) => api.delete(`/ai/conversations/${conversationId}`),
  getBooks: () => api.get('/ai/books'),
  generateImage: (prompt) => api.post('/ai/generate-image', { prompt }),
}

// ============================================
// المعلم
// ============================================
export const teacherAPI = {
  // الواجبات
  getHomework: () => api.get('/teacher/homework'),
  createHomework: (data) => api.post('/teacher/homework', data),
  deleteHomework: (id) => api.delete(`/teacher/homework/${id}`),
  getSubmissions: (hwId) => api.get(`/teacher/homework/${hwId}/submissions`),

  // الاختبارات
  getTests: () => api.get('/teacher/tests'),
  createTest: (data) => api.post('/teacher/tests', data),
  updateTest: (id, data) => api.put(`/teacher/tests/${id}`, data),
  deleteTest: (id) => api.delete(`/teacher/tests/${id}`),

  // أوراق العمل
  getWorksheets: () => api.get('/teacher/worksheets'),
  createWorksheet: (data) => api.post('/teacher/worksheets', data),
  deleteWorksheet: (id) => api.delete(`/teacher/worksheets/${id}`),

  // الطلاب
  getStudents: () => api.get('/teacher/students'),
  getStudentProgress: (id) => api.get(`/teacher/students/${id}/progress`),

  // التوليد
  generatePPT: (data) => api.post('/teacher/generate-ppt', data),
  generateVideo: (data) => api.post('/teacher/generate-video', data),
  chat: (message, imageBase64 = null, fileText = null) => api.post('/teacher/chat', {
    message,
    image_base64: imageBase64 || undefined,
    file_text: fileText || undefined,
  }),

  // الإعدادات
  getSettings: () => api.get('/teacher/settings'),
  updateSettings: (data) => api.put('/teacher/settings', data),

  // 🎓 الميزات الذكية الجديدة (11)
  generateLessonPlan: (data) => api.post('/teacher/lesson-plan', data),
  multimediaConvert: (text, mode) => api.post('/teacher/multimedia-convert', { text, mode }),
  designActivity: (data) => api.post('/teacher/activity-designer', data),
  composeMessage: (data) => api.post('/teacher/compose-message', data),
  autoFeedback: (data) => api.post('/teacher/auto-feedback', data),
  getPerformanceInsights: () => api.get('/teacher/performance-insights'),
  simplifyContent: (text, level) => api.post('/teacher/simplify-content', { text, level }),
  differentiatedStrategies: (concept) => api.post('/teacher/differentiated-strategies', { concept }),
  pedagogicalCoach: (challenge) => api.post('/teacher/pedagogical-coach', { challenge }),
  researchDigest: () => api.get('/teacher/research-digest'),
  promptLibrary: () => api.get('/teacher/prompt-library'),
}

// ============================================
// المشرف الإداري
// ============================================
export const adminAPI = {
  getOverview: () => api.get('/admin/overview'),
  getStudents: () => api.get('/admin/students'),
  resetPassword: (id, password) => api.put(`/admin/students/${id}/reset-password`, { new_password: password }),
  toggleStudent: (id) => api.put(`/admin/students/${id}/toggle`),
  uploadExcel: (formData) => api.post('/admin/upload-excel', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getSettings: () => api.get('/admin/settings'),
  updateSettings: (data) => api.put('/admin/settings', data),
}

// ============================================
// المالك
// ============================================
export const ownerAPI = {
  getStats: () => api.get('/owner/stats'),
  getComplaints: () => api.get('/owner/complaints'),
  respondComplaint: (id, data) => api.put(`/owner/complaints/${id}`, data),
  getUsers: () => api.get('/owner/users'),
  toggleUser: (id) => api.put(`/owner/users/${id}/toggle`),
  getSchools: () => api.get('/owner/schools'),
}

export default api
