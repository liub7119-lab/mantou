import axios from 'axios'

// 开发环境走 Vite 代理 '/api/v1'，生产环境走 Render 后端完整地址
const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

// 后端根地址（用于拼接静态资源如 /uploads/xxx.jpg）
// 开发环境为空（走代理），生产环境为 Render 域名
const backendOrigin = import.meta.env.VITE_BACKEND_ORIGIN || ''

const api = axios.create({
  baseURL,
  timeout: 30000,
})

/**
 * 拼接后端静态资源完整 URL（证书图片等）
 * 开发环境: /uploads/xxx.jpg（走 Vite 代理）
 * 生产环境: https://xxx.onrender.com/uploads/xxx.jpg
 */
export function getAssetUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${backendOrigin}${path}`
}

// ── 学生相关 ──

export function createStudent(data) {
  return api.post('/achievements/students', data)
}

export function getStudent(studentId) {
  return api.get(`/achievements/students/${studentId}`)
}

// ── 成果相关 ──

export function uploadCertificate(file) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/achievements/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function confirmAchievement(data) {
  return api.post('/achievements/confirm', data)
}

export function listAchievements(params = {}) {
  return api.get('/achievements/list', { params })
}

export function updateAchievementStatus(id, status) {
  return api.patch(`/achievements/${id}/status`, null, { params: { status } })
}

// ── 导出 ──

export function downloadExcel(status = 'confirmed') {
  return api.get('/export/achievements/excel', {
    params: { status },
    responseType: 'blob',
  })
}

// ── 树洞（匿名反馈） ──

/** 匿名投递反馈 */
export function submitFeedback(data) {
  return api.post('/feedback/submit', data)
}

/** 学生通过匿名 ID 查看自己的反馈 + 对话 */
export function getMyFeedback(anonymousId) {
  return api.get(`/feedback/mine/${anonymousId}`)
}

/** 学生追加回复 */
export function studentReply(anonymousId, content) {
  return api.post(`/feedback/mine/${anonymousId}/reply`, { content, is_counselor: false })
}

/** 管理端：反馈列表 */
export function listFeedbacks(params = {}) {
  return api.get('/feedback/admin/list', { params })
}

/** 管理端：反馈详情 */
export function getFeedbackDetail(id) {
  return api.get(`/feedback/admin/${id}`)
}

/** 管理端：辅导员回复 */
export function counselorReply(id, content) {
  return api.post(`/feedback/admin/${id}/reply`, { content, is_counselor: true })
}

/** 管理端：关闭反馈 */
export function closeFeedback(id) {
  return api.patch(`/feedback/admin/${id}/close`)
}

export default api
