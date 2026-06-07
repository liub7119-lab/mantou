import { createRouter, createWebHistory } from 'vue-router'
import DashboardLayout from '../components/layout/DashboardLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { title: '登录', guest: true },
  },
  // ── 需要登录的页面（使用 Dashboard 布局） ──
  {
    path: '/',
    component: DashboardLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('../views/HomeView.vue'),
        meta: { title: '首页', requiresAuth: true },
      },
      {
        path: 'upload',
        name: 'Upload',
        component: () => import('../views/UploadView.vue'),
        meta: { title: '成果上传', requiresAuth: true },
      },
      {
        path: 'feedback',
        name: 'Feedback',
        component: () => import('../views/FeedbackView.vue'),
        meta: { title: '树洞', requiresAuth: true },
      },
      {
        path: 'attendance',
        name: 'Attendance',
        component: () => import('../views/AttendanceView.vue'),
        meta: { title: '签到考勤', requiresAuth: true },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/ProfileView.vue'),
        meta: { title: '成长画像', requiresAuth: true },
      },
      {
        path: 'admin',
        name: 'Admin',
        component: () => import('../views/AdminView.vue'),
        meta: { title: '成果管理', requiresAuth: true, role: 'counselor' },
      },
      {
        path: 'admin/feedback',
        name: 'AdminFeedback',
        component: () => import('../views/AdminFeedbackView.vue'),
        meta: { title: '树洞管理', requiresAuth: true, role: 'counselor' },
      },
      {
        path: 'admin/attendance',
        name: 'AdminAttendance',
        component: () => import('../views/AdminAttendanceView.vue'),
        meta: { title: '考勤管理', requiresAuth: true, role: 'counselor' },
      },
      {
        path: 'admin/profile',
        name: 'AdminProfile',
        component: () => import('../views/AdminProfileView.vue'),
        meta: { title: '班级画像', requiresAuth: true, role: 'counselor' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  document.title = to.meta?.title
    ? `${to.meta.title} - 小牛同学`
    : '小牛同学 · 学生服务平台'

  const user = JSON.parse(localStorage.getItem('user') || 'null')
  const token = localStorage.getItem('token')

  if (to.meta?.guest && token && user) {
    if (user.role === 'counselor') return '/admin'
    if (user.role === 'monitor') return '/attendance'
    return '/upload'
  }

  if (to.meta?.requiresAuth && !token) {
    return '/login'
  }

  if (to.meta?.role && user?.role !== to.meta.role) {
    if (user?.role === 'counselor') return '/admin'
    if (user?.role === 'monitor') return '/attendance'
    return '/upload'
  }
})

export default router
