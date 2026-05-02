<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center">
    <div class="bg-white rounded-xl shadow-lg p-8 w-full max-w-sm border border-gray-100">
      <h2 class="text-xl font-bold text-gray-800 text-center mb-2">管理端登录</h2>
      <p class="text-sm text-gray-400 text-center mb-6">仅限辅导员使用</p>

      <form @submit.prevent="handleLogin">
        <input
          v-model="password"
          type="password"
          placeholder="请输入管理密码"
          class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
          autofocus
        />
        <p v-if="error" class="text-red-500 text-xs mb-3">{{ error }}</p>
        <button
          type="submit"
          class="w-full bg-blue-600 text-white py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700 transition"
        >
          进入管理后台
        </button>
      </form>

      <router-link to="/" class="block text-center text-xs text-gray-400 mt-4 hover:text-blue-500">
        返回首页
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const password = ref('')
const error = ref('')

// 管理密码（简单方案，MVP 够用）
const ADMIN_PASSWORD = 'daoyuan2025'

function handleLogin() {
  if (password.value === ADMIN_PASSWORD) {
    sessionStorage.setItem('admin_auth', 'true')
    // 跳转到之前想去的页面，默认去成果管理
    const redirect = router.currentRoute.value.query.redirect || '/admin'
    router.push(redirect)
  } else {
    error.value = '密码错误，请联系辅导员获取'
    password.value = ''
  }
}
</script>
