import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'
const backendOrigin = import.meta.env.VITE_BACKEND_ORIGIN || ''

const api = axios.create({
  baseURL,
  timeout: 30000,
})

// ── 请求拦截器：自动带上 JWT token ──
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── 响应拦截器：token 过期自动跳登录 ──
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

/**
 * 拼接后端静态资源 URL
 */
export function getAssetUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${backendOrigin}${path}`
}

// ── 认证 ──

export function register(data) {
  return api.post('/auth/register', data)
}

export function login(data) {
  return api.post('/auth/login', data)
}

export function getMe() {
  return api.get('/auth/me')
}

// ── 学生相关 ──

export function createStudent(data) {
  return api.post('/achievements/students', data)
}

export function getStudent(studentId) {
  return api.get(`/achievements/students/${studentId}`)
}

// ── 成果相关（按类别） ──

export function uploadCertificate(file, category) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/achievements/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    params: { category },
  })
}

export function confirmAchievement(category, data) {
  return api.post(`/achievements/confirm/${encodeURIComponent(category)}`, data)
}

export function listAchievements(category, params = {}) {
  return api.get(`/achievements/list/${encodeURIComponent(category)}`, { params })
}

export function listMyAllAchievements(studentId) {
  return api.get('/achievements/my-all', { params: { student_id: studentId } })
}

export function updateAchievementStatus(category, id, status) {
  return api.patch(`/achievements/${encodeURIComponent(category)}/${id}/status`, null, { params: { status } })
}

// ── 导出 ──

export function downloadExcel(category, status = 'confirmed') {
  return api.get('/export/achievements/excel', {
    params: { category, status },
    responseType: 'blob',
  })
}

// ── 树洞（匿名反馈） ──

export function submitFeedback(data) {
  return api.post('/feedback/submit', data)
}

export function getMyFeedback(anonymousId) {
  return api.get(`/feedback/mine/${anonymousId}`)
}

export function studentReply(anonymousId, content) {
  return api.post(`/feedback/mine/${anonymousId}/reply`, { content, is_counselor: false })
}

export function listFeedbacks(params = {}) {
  return api.get('/feedback/admin/list', { params })
}

export function getFeedbackDetail(id) {
  return api.get(`/feedback/admin/${id}`)
}

export function counselorReply(id, content) {
  return api.post(`/feedback/admin/${id}/reply`, { content, is_counselor: true })
}

export function closeFeedback(id) {
  return api.patch(`/feedback/admin/${id}/close`)
}

// ── 考勤模块 ──

export function importRoster(file) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/attendance/roster/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function getRoster(className = '') {
  return api.get('/attendance/roster', { params: { class_name: className } })
}

export function getRosterClasses() {
  return api.get('/attendance/roster/classes')
}

export function getClassSize(className) {
  return api.get('/attendance/roster/class-size', { params: { class_name: className } })
}

export function parseScheduleImage(file, className, weekNumber) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/attendance/schedule/parse-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    params: { class_name: className, week_number: weekNumber },
    timeout: 60000,
  })
}

export function batchAddSchedule(courses) {
  return api.post('/attendance/schedule/batch', courses)
}

export function getSchedule(className, weekNumber = 0) {
  return api.get('/attendance/schedule', { params: { class_name: className, week_number: weekNumber } })
}

export function deleteSchedule(id) {
  return api.delete(`/attendance/schedule/${id}`)
}

export function createAttendanceRecord(data) {
  return api.post('/attendance/record', data)
}

export function listAttendanceRecords(className = '', weekNumber = 0) {
  return api.get('/attendance/records', { params: { class_name: className, week_number: weekNumber } })
}

export function getAttendanceStats(className) {
  return api.get('/attendance/records/stats', { params: { class_name: className } })
}

export function exportAttendanceRecords(className = '', weekNumber = 0) {
  return api.get('/attendance/records/export', {
    params: { class_name: className, week_number: weekNumber },
    responseType: 'blob',
  })
}

export function createCheckInSession(data) {
  return api.post('/attendance/checkin/create', data)
}

export function doCheckIn(code, status = '正常') {
  return api.post(`/attendance/checkin/${code}`, null, { params: { status } })
}

export function getCheckInStatus(code) {
  return api.get(`/attendance/checkin/${code}/status`)
}

export function closeCheckIn(code) {
  return api.post(`/attendance/checkin/${code}/close`)
}

export function listCheckInSessions(className = '') {
  return api.get('/attendance/checkin-sessions', { params: { class_name: className } })
}

// ── 用户管理（辅导员） ──

export function setMonitor(username, action = 'promote') {
  return api.post(`/auth/set-monitor/${username}`, null, { params: { action } })
}

export function listMonitors() {
  return api.get('/auth/monitors')
}

export function listAllStudents() {
  return api.get('/auth/students')
}

export default api
