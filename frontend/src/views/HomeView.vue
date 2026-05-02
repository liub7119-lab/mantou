<template>
  <section class="space-y-6">
    <!-- Hero Card -->
    <div class="rounded-2xl p-6 md:p-8 overflow-hidden relative"
         style="background: linear-gradient(135deg, #C8F0D4 0%, #8FD6B0 50%, #6BC495 100%); box-shadow: 0 4px 20px rgba(143,214,176,0.25);">
      <img src="/src/assets/ui/sticker-cloud.png" alt="" class="absolute -top-4 -left-4 w-20 h-20 opacity-20 pointer-events-none" />
      <img src="/src/assets/ui/sticker-star.png" alt="" class="absolute top-3 right-1/3 w-8 h-8 opacity-30 pointer-events-none animate-bounce-slow" />

      <div class="relative z-10 flex items-center justify-between gap-6">
        <div>
          <h1 class="text-2xl md:text-3xl font-bold mb-2" style="color: #FFFFFF;">早上好，{{ userName }}！</h1>
          <p class="text-sm md:text-base" style="color: rgba(255,255,255,0.85);">新的一天也要元气满满哦～</p>
        </div>
        <img src="/src/assets/ui/hero-cow.png" alt="小牛同学" class="w-36 h-36 md:w-44 md:h-44 object-contain drop-shadow-lg shrink-0" />
      </div>
    </div>

    <!-- Three Column: 今日待办 / 通知公告 / 课程安排 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
      <!-- 今日待办 -->
      <div class="bg-white rounded-2xl p-5" style="box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-sm font-bold" style="color: #333;">今日待办</h3>
          <span class="text-[10px] px-2 py-0.5 rounded-full" style="background: #E8F4FD; color: #6ECAFF;">{{ todoItems.filter(t => !t.done).length }}项待办</span>
        </div>
        <div class="space-y-3">
          <div v-for="item in todoItems" :key="item.text" class="flex items-center gap-3">
            <div class="w-4 h-4 rounded-full border-2 flex items-center justify-center shrink-0"
              :style="item.done ? 'border-color: #8FD6B0; background: #8FD6B0;' : 'border-color: #E8ECF0;'"
            >
              <Check v-if="item.done" class="w-2.5 h-2.5 text-white" />
            </div>
            <span class="text-xs flex-1" :style="item.done ? 'color: #CCC; text-decoration: line-through;' : 'color: #555;'">{{ item.text }}</span>
            <span class="text-[10px] shrink-0" style="color: #999;">{{ item.time }}</span>
          </div>
        </div>
        <router-link to="/upload" class="block text-center text-xs mt-4 py-2 rounded-lg transition-colors" style="color: #6ECAFF;" @mouseenter="$event.target.style.background='#E8F4FD'" @mouseleave="$event.target.style.background='transparent'">
          查看全部
        </router-link>
      </div>

      <!-- 通知公告 -->
      <div class="bg-white rounded-2xl p-5" style="box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-sm font-bold" style="color: #333;">通知公告</h3>
          <span class="text-[10px] px-2 py-0.5 rounded-full" style="background: #FFF5E5; color: #E5A520;">{{ announcements.length }}条未读</span>
        </div>
        <div class="space-y-3">
          <div v-for="a in announcements" :key="a.text" class="flex items-start gap-2">
            <div class="w-1.5 h-1.5 rounded-full mt-1.5 shrink-0" :style="{ background: a.color }"></div>
            <div class="flex-1 min-w-0">
              <p class="text-xs truncate" style="color: #333;">{{ a.text }}</p>
              <p class="text-[10px]" style="color: #999;">{{ a.date }}</p>
            </div>
          </div>
        </div>
        <button class="w-full text-center text-xs mt-4 py-2 rounded-lg transition-colors" style="color: #6ECAFF;" @mouseenter="$event.target.style.background='#E8F4FD'" @mouseleave="$event.target.style.background='transparent'">
          查看全部
        </button>
      </div>

      <!-- 课程安排 -->
      <div class="bg-white rounded-2xl p-5" style="box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-sm font-bold" style="color: #333;">课程安排</h3>
          <span class="text-[10px]" style="color: #999;">今日课程（{{ todayCourses.length }}节）</span>
        </div>
        <div class="space-y-3">
          <div v-for="c in todayCourses" :key="c.name" class="rounded-xl px-4 py-3" style="background: #F7F8FA;">
            <div class="flex justify-between items-center">
              <span class="text-xs font-medium" style="color: #333;">{{ c.time }}</span>
              <span class="text-[10px] px-2 py-0.5 rounded" style="background: #E8F4FD; color: #6ECAFF;">{{ c.room }}</span>
            </div>
            <p class="text-xs mt-1" style="color: #555;">{{ c.name }}</p>
          </div>
          <div v-if="todayCourses.length === 0" class="text-center py-4">
            <p class="text-xs" style="color: #999;">今日暂无课程</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 我的进度 -->
    <div class="bg-white rounded-2xl p-5" style="box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
      <div class="flex items-center justify-between mb-5">
        <h3 class="text-sm font-bold" style="color: #333;">我的进度</h3>
        <img src="/src/assets/ui/sticker-medal.png" alt="" class="w-8 h-8 opacity-60" />
      </div>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-5">
        <div v-for="p in progressItems" :key="p.label">
          <div class="flex justify-between items-center mb-1.5">
            <span class="text-xs" style="color: #555;">{{ p.label }}</span>
            <span class="text-xs font-bold" style="color: #333;">{{ p.current }}/{{ p.total }}</span>
          </div>
          <div class="w-full h-2 rounded-full overflow-hidden" style="background: #F2F4F7;">
            <div class="h-full rounded-full transition-all duration-500" :style="{ width: (p.current / p.total * 100) + '%', background: p.color }"></div>
          </div>
          <p class="text-[10px] mt-1 text-right" :style="{ color: p.color }">{{ Math.round(p.current / p.total * 100) }}%</p>
        </div>
      </div>
    </div>

    <!-- 底部牛牛 + 快捷服务 -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
      <!-- 快捷服务 -->
      <div class="bg-white rounded-2xl p-5" style="box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
        <h3 class="text-sm font-bold mb-4" style="color: #333;">服务快捷入口</h3>
        <div class="grid grid-cols-4 gap-3">
          <router-link v-for="s in quickServices" :key="s.label" :to="s.path"
            class="flex flex-col items-center gap-2 py-3 rounded-xl transition-colors cursor-pointer"
            @mouseenter="$event.currentTarget.style.background='#F7F8FA'"
            @mouseleave="$event.currentTarget.style.background='transparent'"
          >
            <div class="w-10 h-10 rounded-xl flex items-center justify-center" :style="{ background: s.bg }">
              <component :is="s.icon" class="w-5 h-5" :style="{ color: s.color }" />
            </div>
            <span class="text-[11px]" style="color: #555;">{{ s.label }}</span>
          </router-link>
        </div>
      </div>

      <!-- 牛牛问候 -->
      <div class="rounded-2xl p-5 flex items-center gap-5" style="background: linear-gradient(135deg, #E8F4FD, #F0F7FF); box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
        <img src="/src/assets/ui/sidebar-cow.png" alt="小牛同学" class="w-24 h-24 object-contain shrink-0" />
        <div>
          <div class="inline-block px-4 py-2 rounded-2xl rounded-bl-sm mb-2" style="background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
            <p class="text-xs" style="color: #555;">有什么可以帮你的吗？</p>
          </div>
          <p class="text-[10px]" style="color: #999;">小牛同学随时为你服务～</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import {
  Check, Upload, MessageCircle, ClipboardCheck, BookOpen,
  Trophy, Search as SearchIcon, Heart, Settings,
} from 'lucide-vue-next'

const user = JSON.parse(localStorage.getItem('user') || '{}')

const userName = computed(() => {
  const name = user.name || '同学'
  return name
})

const todoItems = [
  { text: '图书馆预约', time: '09:30', done: true },
  { text: '心理健康问卷', time: '截止·今天', done: false },
  { text: '课程作业提交', time: '截止·明天', done: false },
  { text: '体育课签到', time: '10:00', done: false },
  { text: '奖学金申请', time: '截止·本周五', done: false },
]

const announcements = [
  { text: '关于2024年五一放假安排的通知', date: '04-24', color: '#6ECAFF' },
  { text: '图书馆座位预约系统升级通知', date: '04-23', color: '#8FD6B0' },
  { text: '校园卡服务时间调整说明', date: '04-22', color: '#FFD60E' },
]

const todayCourses = [
  { time: '08:00 - 09:40', name: '高等数学', room: 'A201' },
  { time: '14:00 - 15:40', name: '大学英语', room: 'B105' },
]

const progressItems = [
  { label: '本学期学分', current: 32, total: 48, color: '#6ECAFF' },
  { label: '志愿服务时长', current: 18, total: 30, color: '#8FD6B0' },
  { label: '阅读计划', current: 6, total: 12, color: '#FFD60E' },
  { label: '成果上传', current: 3, total: 5, color: '#B4A0E5' },
]

const quickServices = [
  { label: '成果上传', icon: Upload, path: '/upload', color: '#6ECAFF', bg: '#E8F4FD' },
  { label: '签到考勤', icon: ClipboardCheck, path: '/attendance', color: '#8FD6B0', bg: '#E8F7EF' },
  { label: '匿名树洞', icon: MessageCircle, path: '/feedback', color: '#FFD60E', bg: '#FFF8E1' },
  { label: '成果查询', icon: Trophy, path: '/upload', color: '#B4A0E5', bg: '#F3F0FF' },
]
</script>

<style scoped>
@reference "../style.css";

@keyframes bounce-slow {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}
.animate-bounce-slow { animation: bounce-slow 3s ease-in-out infinite; }
</style>
