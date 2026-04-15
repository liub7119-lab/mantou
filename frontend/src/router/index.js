import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue'),
  },
  {
    path: '/upload',
    name: 'Upload',
    component: () => import('../views/UploadView.vue'),
    meta: { title: '上传证书' },
  },
  {
    path: '/feedback',
    name: 'Feedback',
    component: () => import('../views/FeedbackView.vue'),
    meta: { title: '树洞' },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/AdminView.vue'),
    meta: { title: '成果管理' },
  },
  {
    path: '/admin/feedback',
    name: 'AdminFeedback',
    component: () => import('../views/AdminFeedbackView.vue'),
    meta: { title: '树洞管理' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  document.title = to.meta?.title
    ? `${to.meta.title} - 辅导员工作辅助平台`
    : '辅导员工作辅助平台'
})

export default router
