<template>
  <div class="h-screen flex overflow-hidden" style="background: #F5F7FA;">
    <!-- ========== 左侧封面图 ========== -->
    <div class="hidden lg:flex w-[55%] relative overflow-hidden" style="background: #E8F4FD;">
      <img src="/cover.png?v=2" alt="封面" class="w-full h-full object-cover" />
    </div>

    <!-- ========== 右侧登录区域 ========== -->
    <div class="flex-1 flex flex-col items-center justify-center relative px-6 py-4">
      <!-- 背景装饰 -->
      <div class="absolute inset-0 pointer-events-none overflow-hidden">
        <div ref="glow1" class="absolute w-[400px] h-[400px] rounded-full blur-[120px] -top-40 right-0" style="background: rgba(110,202,255,0.06);"></div>
        <div ref="glow2" class="absolute w-[300px] h-[300px] rounded-full blur-[100px] bottom-0 -left-20" style="background: rgba(143,214,176,0.05);"></div>
      </div>

      <!-- 顶部品牌 -->
      <div ref="brandRef" class="flex items-center gap-3 mb-6 relative z-10 opacity-0">
        <img src="/src/assets/ui/hero-cow.png" alt="小牛同学" class="w-14 h-14 object-contain drop-shadow-md" />
        <div>
          <h1 class="text-2xl font-bold tracking-wide" style="color: #333;">小牛同学</h1>
          <p class="text-xs" style="color: #AABBC8;">学生工作一站式服务平台</p>
        </div>
      </div>

      <!-- 登录卡片 -->
      <div ref="cardRef" class="w-full max-w-[400px] relative z-10 opacity-0">
        <div class="bg-white rounded-3xl px-10 py-8" style="box-shadow: 0 8px 40px rgba(110,170,210,0.1);">
          <!-- 欢迎语 -->
          <div class="text-center mb-5">
            <h2 class="text-xl font-bold mb-1" style="color: #333;">欢迎回来</h2>
            <p class="text-xs" style="color: #AABBC8;">登录你的账号以继续</p>
          </div>

          <!-- 身份选择 -->
          <div class="flex gap-3 mb-5">
            <button
              @click="switchRole('student')"
              class="flex-1 py-3 rounded-2xl text-sm font-medium transition-all duration-300 cursor-pointer flex items-center justify-center gap-2"
              :style="selectedRole === 'student'
                ? 'background: #6ECAFF; color: white; box-shadow: 0 4px 16px rgba(110,202,255,0.3);'
                : 'background: #F2F4F7; color: #999;'"
            >
              <GraduationCap class="w-4 h-4" />
              学生
            </button>
            <button
              @click="switchRole('counselor')"
              class="flex-1 py-3 rounded-2xl text-sm font-medium transition-all duration-300 cursor-pointer flex items-center justify-center gap-2"
              :style="selectedRole === 'counselor'
                ? 'background: #8FD6B0; color: white; box-shadow: 0 4px 16px rgba(143,214,176,0.3);'
                : 'background: #F2F4F7; color: #999;'"
            >
              <LayoutDashboard class="w-4 h-4" />
              辅导员
            </button>
          </div>

          <!-- 表单 -->
          <form @submit.prevent="handleSubmit">
            <template v-if="isLogin">
              <div class="mb-4 relative">
                <div class="absolute left-4 top-1/2 -translate-y-1/2">
                  <User class="w-4 h-4" style="color: #C0CDD8;" />
                </div>
                <input
                  v-model="loginForm.username"
                  type="text"
                  :placeholder="selectedRole === 'student' ? '请输入学号' : '请输入账号'"
                  class="login-input pl-11"
                  autofocus
                />
              </div>
              <div class="mb-6 relative">
                <div class="absolute left-4 top-1/2 -translate-y-1/2">
                  <Lock class="w-4 h-4" style="color: #C0CDD8;" />
                </div>
                <input
                  v-model="loginForm.password"
                  :type="showPwd ? 'text' : 'password'"
                  placeholder="请输入密码"
                  class="login-input pl-11 pr-11"
                />
                <button type="button" @click="showPwd = !showPwd" class="absolute right-4 top-1/2 -translate-y-1/2 cursor-pointer">
                  <EyeOff v-if="showPwd" class="w-4 h-4" style="color: #C0CDD8;" />
                  <Eye v-else class="w-4 h-4" style="color: #C0CDD8;" />
                </button>
              </div>
            </template>

            <!-- 错误提示 -->
            <div v-if="error" class="mb-4 px-4 py-2.5 rounded-xl flex items-center gap-2" style="background: #FEF2F2;">
              <TriangleAlert class="w-3.5 h-3.5 shrink-0" style="color: #EF4444;" />
              <p class="text-xs" style="color: #EF4444;">{{ error }}</p>
            </div>

            <!-- 提交按钮 -->
            <button
              type="submit"
              :disabled="loading"
              class="w-full py-3.5 rounded-2xl text-sm font-semibold text-white transition-all duration-300 disabled:opacity-50 cursor-pointer"
              :style="selectedRole === 'counselor'
                ? 'background: linear-gradient(135deg, #8FD6B0, #6BC495); box-shadow: 0 4px 16px rgba(143,214,176,0.35);'
                : 'background: linear-gradient(135deg, #6ECAFF, #4DB8F0); box-shadow: 0 4px 16px rgba(110,202,255,0.35);'"
              @mouseenter="$event.target.style.transform='translateY(-1px)'"
              @mouseleave="$event.target.style.transform='translateY(0)'"
            >
              <Loader2 v-if="loading" class="w-4 h-4 animate-spin mx-auto" />
              <span v-else>登 录</span>
            </button>
          </form>
        </div>

        <!-- 底部提示 -->
        <p class="text-center text-[11px] mt-5" style="color: #C0CDD8;">
          <span v-if="selectedRole === 'counselor'">辅导员账号由管理员分配</span>
          <span v-else>账号由辅导员统一创建</span>
        </p>
      </div>

      <!-- 装饰贴纸 -->
      <img src="/src/assets/ui/sticker-star.png" alt="" class="absolute top-8 right-10 w-10 h-10 opacity-15 pointer-events-none animate-float-slow z-0" />
      <img src="/src/assets/ui/sticker-cloud.png" alt="" class="absolute bottom-16 left-8 w-12 h-12 opacity-10 pointer-events-none animate-float-delay z-0" />

      <!-- 底部 -->
      <p ref="footerRef" class="absolute bottom-5 text-[11px] opacity-0 z-10" style="color: #C0CDD8;">
        © 2025 小牛同学 · 学生工作一站式服务
      </p>
    </div>

    <!-- 移动端封面图 (小屏幕顶部显示) -->
    <div class="lg:hidden fixed top-0 left-0 right-0 h-48 z-0 overflow-hidden">
      <img src="/cover.png?v=2" alt="封面" class="w-full h-full object-cover" />
      <div class="absolute inset-0" style="background: linear-gradient(to bottom, transparent 50%, #F5F7FA 100%);"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import gsap from 'gsap'
import {
  GraduationCap, LayoutDashboard, User, Lock, Eye, EyeOff,
  TriangleAlert, Loader2,
} from 'lucide-vue-next'
import { login } from '../api'

const router = useRouter()

const brandRef = ref(null)
const cardRef = ref(null)
const footerRef = ref(null)
const glow1 = ref(null)
const glow2 = ref(null)

const selectedRole = ref('student')
const isLogin = ref(true)
const showPwd = ref(false)
const loading = ref(false)
const error = ref('')

const loginForm = ref({ username: '', password: '' })

onMounted(() => {
  // 背景光晕动画
  gsap.to(glow1.value, { x: 60, y: 40, duration: 8, repeat: -1, yoyo: true, ease: 'sine.inOut' })
  gsap.to(glow2.value, { x: -40, y: -50, duration: 10, repeat: -1, yoyo: true, ease: 'sine.inOut' })

  // 入场动画
  gsap.fromTo(brandRef.value, { opacity: 0, y: -20 }, { opacity: 1, y: 0, duration: 0.6, delay: 0.2, ease: 'power2.out' })
  gsap.fromTo(cardRef.value, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.7, delay: 0.4, ease: 'power2.out' })
  gsap.to(footerRef.value, { opacity: 1, duration: 1, delay: 0.8 })
})

function switchRole(role) {
  selectedRole.value = role
  error.value = ''
  loginForm.value = { username: '', password: '' }
}

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    const res = await login(loginForm.value)
    const { access_token, user } = res.data
    localStorage.setItem('token', access_token)
    localStorage.setItem('user', JSON.stringify(user))
    router.push(
      user.role === 'counselor' ? '/admin'
        : user.role === 'monitor' ? '/attendance'
        : '/upload'
    )
  } catch (err) {
    const detail = err.response?.data?.detail
    error.value = typeof detail === 'string'
      ? detail
      : Array.isArray(detail)
        ? detail.map(d => d.msg).join('；')
        : '操作失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@reference "../style.css";

.login-input {
  @apply w-full rounded-2xl px-5 py-3.5 text-sm
         focus:outline-none focus:ring-2 focus:border-transparent
         transition-all duration-200;
  background: #F5F7FA;
  color: #333;
  --tw-ring-color: rgba(110, 202, 255, 0.35);
}
.login-input::placeholder {
  color: #C0CDD8;
}
.login-input:focus {
  background: #FAFBFC;
}

@keyframes float-slow {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-10px) rotate(5deg); }
}
@keyframes float-delay {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-8px) rotate(-3deg); }
}
.animate-float-slow { animation: float-slow 5s ease-in-out infinite; }
.animate-float-delay { animation: float-delay 4s ease-in-out 1s infinite; }
</style>
