<template>
  <div class="min-h-screen flex flex-col items-center justify-center relative overflow-hidden px-4" style="background: linear-gradient(135deg, #E8F4FD 0%, #F0F7FF 30%, #F2F4F7 60%, #E8F4FD 100%);">
    <div class="absolute inset-0 pointer-events-none">
      <div ref="glow1" class="absolute w-[500px] h-[500px] rounded-full blur-[140px] -top-32 -left-32" style="background: rgba(110,202,255,0.1);"></div>
      <div ref="glow2" class="absolute w-[400px] h-[400px] rounded-full blur-[140px] -bottom-32 -right-32" style="background: rgba(143,214,176,0.08);"></div>
    </div>

    <div ref="titleRef" class="text-center mb-8 relative z-10 opacity-0">
      <div class="flex justify-center mb-4 relative">
        <div class="absolute -top-3 -right-6 w-10 h-10 animate-bounce" style="animation-duration: 3s;">
          <img src="/src/assets/ui/sticker-star.png" alt="" class="w-full h-full object-contain drop-shadow-lg" />
        </div>
        <img src="/src/assets/ui/hero-cow.png" alt="小牛同学" class="w-28 h-28 object-contain drop-shadow-xl" />
        <div class="absolute -bottom-1 -left-6 w-8 h-8 animate-float-delay opacity-70">
          <img src="/src/assets/ui/sticker-medal.png" alt="" class="w-full h-full object-contain drop-shadow-md" />
        </div>
      </div>
      <h1 class="text-3xl md:text-4xl font-bold tracking-wide mb-2" style="color: #333;">小牛同学</h1>
      <p class="text-sm" style="color: #999;">你的校园好伙伴 · 请选择身份以继续</p>
    </div>

    <div class="flex flex-col md:flex-row gap-8 relative z-10">
      <div ref="card1" @click="selectRole('student')" class="role-card group cursor-pointer opacity-0" :class="selectedRole === 'student' ? 'selected' : ''">
        <img src="/src/assets/ui/sticker-book.png" alt="" class="absolute -top-3 -right-3 w-10 h-10 opacity-30 pointer-events-none group-hover:opacity-50 transition-opacity" />
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center mb-5 transition-transform duration-300 group-hover:scale-110" style="background: linear-gradient(135deg, #E8F4FD, #D0ECFF);">
          <GraduationCap class="w-7 h-7" style="color: #6ECAFF;" />
        </div>
        <h2 class="text-lg font-bold mb-1" style="color: #333;">我是学生</h2>
        <p class="text-xs" style="color: #999;">上传证书 · 匿名反馈</p>
      </div>

      <div ref="card2" @click="selectRole('counselor')" class="role-card group cursor-pointer opacity-0" :class="selectedRole === 'counselor' ? 'selected' : ''">
        <img src="/src/assets/ui/sticker-coffee.png" alt="" class="absolute -top-3 -right-3 w-10 h-10 opacity-30 pointer-events-none group-hover:opacity-50 transition-opacity" />
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center mb-5 transition-transform duration-300 group-hover:scale-110" style="background: linear-gradient(135deg, #E8F7EF, #C8F0D4);">
          <LayoutDashboard class="w-7 h-7" style="color: #8FD6B0;" />
        </div>
        <h2 class="text-lg font-bold mb-1" style="color: #333;">我是辅导员</h2>
        <p class="text-xs" style="color: #999;">成果管理 · 树洞管理</p>
      </div>
    </div>

    <div v-show="selectedRole" ref="formRef" class="mt-10 w-full max-w-sm relative z-10">
      <div class="bg-white rounded-2xl p-8" style="box-shadow: 0 4px 24px rgba(0,0,0,0.06);">
        <div class="flex mb-6 rounded-full p-1" style="background: #F2F4F7;">
          <button @click="isLogin = true" :class="isLogin ? 'bg-white shadow-sm' : ''" :style="isLogin ? 'color: #333;' : 'color: #999;'" class="flex-1 py-2.5 text-sm font-medium rounded-full transition-all duration-200 cursor-pointer">登录</button>
          <button v-if="selectedRole === 'student'" @click="isLogin = false" :class="!isLogin ? 'bg-white shadow-sm' : ''" :style="!isLogin ? 'color: #333;' : 'color: #999;'" class="flex-1 py-2.5 text-sm font-medium rounded-full transition-all duration-200 cursor-pointer">注册</button>
        </div>

        <form @submit.prevent="handleSubmit">
          <template v-if="isLogin">
            <div class="mb-4">
              <input v-model="loginForm.username" type="text" :placeholder="selectedRole === 'student' ? '学号（11位）' : '辅导员账号'" class="login-input" autofocus />
            </div>
            <div class="mb-6">
              <input v-model="loginForm.password" type="password" placeholder="密码" class="login-input" />
            </div>
          </template>
          <template v-else>
            <div class="mb-3"><input v-model="registerForm.username" type="text" placeholder="学号（11位）" class="login-input" /></div>
            <div class="mb-3"><input v-model="registerForm.password" type="password" placeholder="密码（至少6位）" class="login-input" /></div>
            <div class="mb-3"><input v-model="registerForm.name" type="text" placeholder="姓名（中文）" class="login-input" /></div>
            <div class="mb-3"><input v-model="registerForm.class_name" type="text" placeholder="班级（如 2025级英语2班）" class="login-input" /></div>
            <div class="mb-6"><input v-model="registerForm.major" type="text" placeholder="学院（如 外国语言与文化学院）" class="login-input" /></div>
          </template>

          <p v-if="error" class="text-xs mb-3 text-center" style="color: #EF4444;">{{ error }}</p>

          <button type="submit" :disabled="loading" class="w-full py-3 rounded-full text-sm font-medium text-white transition-all duration-200 disabled:opacity-50 cursor-pointer" style="background: linear-gradient(135deg, #6ECAFF, #4DB8F0);" @mouseenter="$event.target.style.opacity='0.9'" @mouseleave="$event.target.style.opacity='1'">
            {{ loading ? '请稍候...' : (isLogin ? '登录' : '注册') }}
          </button>
        </form>
      </div>
    </div>

    <div class="absolute inset-0 pointer-events-none overflow-hidden">
      <div v-for="(bubble, i) in bubbles" :key="i" :ref="el => bubbleRefs[i] = el" class="absolute rounded-full flex items-center justify-center opacity-0" :style="{ width: bubble.size + 'px', height: bubble.size + 'px', left: bubble.x + '%', bottom: bubble.y + 'px', background: 'rgba(110,202,255,0.04)', border: '1px solid rgba(110,202,255,0.1)' }">
        <span class="text-[10px] leading-tight text-center px-2" style="color: rgba(110,202,255,0.5);">{{ bubble.text }}</span>
      </div>
    </div>

    <div class="absolute top-8 left-8 w-14 h-14 opacity-20 pointer-events-none animate-float-slow z-0">
      <img src="/src/assets/ui/sticker-cloud.png" alt="" class="w-full h-full object-contain" />
    </div>
    <div class="absolute bottom-12 right-12 w-12 h-12 opacity-15 pointer-events-none animate-float-delay z-0">
      <img src="/src/assets/ui/sticker-task.png" alt="" class="w-full h-full object-contain" />
    </div>

    <p ref="footerRef" class="absolute bottom-6 text-xs opacity-0 z-10" style="color: #999;">学生工作一站式服务</p>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import gsap from 'gsap'
import { GraduationCap, LayoutDashboard } from 'lucide-vue-next'
import { login, register } from '../api'

const router = useRouter()
const titleRef = ref(null), card1 = ref(null), card2 = ref(null), formRef = ref(null), footerRef = ref(null), glow1 = ref(null), glow2 = ref(null), bubbleRefs = ref([])

const bubbles = [
  { text: '已帮 20 人解决请假', size: 90, x: 8, y: 40 },
  { text: '本周反馈 5 条', size: 70, x: 25, y: 90 },
  { text: '综测录入 90%', size: 80, x: 45, y: 30 },
  { text: '证书识别 128 份', size: 95, x: 65, y: 80 },
  { text: '活动审批 12 项', size: 72, x: 82, y: 50 },
  { text: '学业预警 3 人', size: 68, x: 15, y: 160 },
  { text: '奖学金评定中', size: 85, x: 55, y: 150 },
]

const selectedRole = ref(null), isLogin = ref(true), loading = ref(false), error = ref('')
const loginForm = ref({ username: '', password: '' })
const registerForm = ref({ username: '', password: '', name: '', class_name: '', major: '' })

onMounted(() => {
  gsap.to(glow1.value, { x: 80, y: 60, duration: 8, repeat: -1, yoyo: true, ease: 'sine.inOut' })
  gsap.to(glow2.value, { x: -60, y: -80, duration: 10, repeat: -1, yoyo: true, ease: 'sine.inOut' })
  gsap.fromTo(titleRef.value, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.8, delay: 0.2, ease: 'power2.out' })
  gsap.fromTo(card1.value, { opacity: 0, x: -50 }, { opacity: 1, x: 0, duration: 0.6, delay: 0.5, ease: 'back.out(1.4)' })
  gsap.fromTo(card2.value, { opacity: 0, x: 50 }, { opacity: 1, x: 0, duration: 0.6, delay: 0.65, ease: 'back.out(1.4)' })
  gsap.to(footerRef.value, { opacity: 1, duration: 1, delay: 1 })
  bubbleRefs.value.forEach((el, i) => {
    if (!el) return
    const delay = 1.2 + i * 0.2, duration = 4 + Math.random() * 3
    gsap.to(el, { opacity: 1, duration: 1.5, delay, ease: 'power1.out' })
    gsap.to(el, { y: -(15 + Math.random() * 25), scale: 1 + Math.random() * 0.12, duration, delay, repeat: -1, yoyo: true, ease: 'sine.inOut' })
  })
})

function selectRole(role) {
  if (selectedRole.value === role) return
  selectedRole.value = role; isLogin.value = true; error.value = ''
  loginForm.value = { username: '', password: '' }
  registerForm.value = { username: '', password: '', name: '', class_name: '', major: '' }
  nextTick(() => { gsap.fromTo(formRef.value, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' }) })
}

async function handleSubmit() {
  error.value = ''; loading.value = true
  try {
    const res = isLogin.value ? await login(loginForm.value) : await register(registerForm.value)
    const { access_token, user } = res.data
    localStorage.setItem('token', access_token); localStorage.setItem('user', JSON.stringify(user))
    router.push(user.role === 'counselor' ? '/admin' : user.role === 'monitor' ? '/attendance' : '/upload')
  } catch (err) {
    const detail = err.response?.data?.detail
    error.value = typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map(d => d.msg).join('；') : '操作失败，请稍后重试'
  } finally { loading.value = false }
}
</script>

<style scoped>
@reference "../style.css";
.role-card {
  @apply relative w-56 h-52 flex flex-col items-center justify-center rounded-2xl bg-white transition-all duration-300 ease-out;
  box-shadow: 0 4px 16px rgba(0,0,0,0.04);
}
.role-card:hover {
  @apply scale-[1.03];
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}
.role-card.selected {
  box-shadow: 0 0 0 2px #6ECAFF, 0 8px 24px rgba(110,202,255,0.15);
}
.login-input {
  @apply w-full rounded-xl px-5 py-3 text-sm focus:outline-none focus:ring-2 focus:border-transparent transition-all duration-200;
  background: #F2F4F7;
  color: #333;
  --tw-ring-color: rgba(110, 202, 255, 0.4);
}
.login-input::placeholder { color: #999; }

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
