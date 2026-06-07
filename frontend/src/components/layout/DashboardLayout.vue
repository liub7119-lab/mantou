<template>
  <div class="min-h-screen app-shell">
    <AppSidebar
      :role="user.role"
      :user-name="user.name"
      @update:expanded="sidebarExpanded = $event"
    />

    <CourseCalendarPanel
      v-if="isAttendancePage"
      @select-course="handleCalendarSelectCourse"
      @parse-image="handleCalendarParseImage"
      @confirm-parsed="handleCalendarConfirmParsed"
      @add-course="handleCalendarAddCourse"
      @load-checkin-courses="handleCalendarLoadCheckinCourses"
      @select-checkin-course="handleCalendarSelectCheckinCourse"
      @courses-updated="handleCoursesUpdated"
    />
    <InfoPanel
      v-else
      :role="user.role"
      :students="students"
      @select-student="handleSelectStudent"
    />

    <!-- Main -->
    <main
      class="transition-all duration-300 ease-out min-h-screen pb-16 md:pb-0"
      :style="{
        marginLeft: isMobile ? '0' : (sidebarExpanded ? '224px' : '72px'),
        marginRight: showInfoPanel ? '304px' : '0',
      }"
    >
      <!-- Header -->
      <header class="h-[64px] glass-header sticky top-0 z-20 flex items-center justify-between px-4 md:px-6 lg:px-10">
        <div class="flex items-center gap-4">
          <p class="text-sm" style="color: #666;">
            {{ greeting }}
          </p>
        </div>
        <div class="flex items-center gap-3">
          <!-- Search (hidden on mobile) -->
          <div class="relative hidden md:block">
            <Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2" style="color: #999;" />
            <input
              type="text"
              placeholder="搜索功能或信息..."
              class="pl-9 pr-4 py-2 text-sm rounded-full w-36 md:w-44 lg:w-52 focus:outline-none focus:ring-2"
              style="background: #F2F4F7; color: #333; --tw-ring-color: #6ECAFF;"
            />
          </div>
          <!-- Bell (hidden on mobile) -->
          <button class="w-10 h-10 rounded-full hidden md:flex items-center justify-center cursor-pointer transition-colors duration-150" style="background: #F2F4F7;" @mouseenter="$event.currentTarget.style.background='#E8F4FD'" @mouseleave="$event.currentTarget.style.background='#F2F4F7'">
            <Bell class="w-[18px] h-[18px]" style="color: #333;" />
          </button>
          <!-- Logout -->
          <button
            @click="logout"
            class="flex items-center gap-2 px-4 py-2 rounded-full text-sm cursor-pointer transition-colors duration-150"
            style="color: #999;"
            @mouseenter="$event.currentTarget.style.background='#FEF2F2';$event.currentTarget.style.color='#EF4444'"
            @mouseleave="$event.currentTarget.style.background='transparent';$event.currentTarget.style.color='#999'"
          >
            <LogOut class="w-4 h-4" />
            <span class="hidden md:inline">退出</span>
          </button>
        </div>
      </header>

      <div class="p-4 md:p-6 lg:p-10">
        <router-view />
      </div>
    </main>

    <!-- Mobile Bottom Navigation -->
    <nav class="fixed bottom-0 left-0 right-0 z-50 md:hidden flex items-center justify-around h-14" style="background: #FFFFFF; border-top: 1px solid #E8ECF0; box-shadow: 0 -2px 10px rgba(0,0,0,0.05);">
      <router-link
        v-for="item in mobileNavItems"
        :key="item.path"
        :to="item.path"
        class="flex flex-col items-center justify-center gap-0.5 flex-1 h-full transition-colors"
        :style="isActive(item.path) ? 'color: #6ECAFF;' : 'color: #999;'"
      >
        <component :is="item.icon" class="w-5 h-5" />
        <span class="text-[10px]">{{ item.label }}</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  LogOut, Search, Bell,
  Home, Upload, MessageCircle, ClipboardCheck, ScanLine,
  UserCircle, LayoutDashboard, MessageSquareText, BarChart3, Users,
} from 'lucide-vue-next'
import AppSidebar from './AppSidebar.vue'
import InfoPanel from './InfoPanel.vue'
import CourseCalendarPanel from './CourseCalendarPanel.vue'
import { useAttendanceCalendar } from '@/lib/useAttendanceCalendar'
import { getRoster } from '@/api'

const router = useRouter()
const route = useRoute()

const user = ref(JSON.parse(localStorage.getItem('user') || '{}'))
const sidebarExpanded = ref(false)
const students = ref([])

const windowWidth = ref(typeof window !== 'undefined' ? window.innerWidth : 1024)
function onResize() { windowWidth.value = window.innerWidth }
onMounted(() => window.addEventListener('resize', onResize))
onUnmounted(() => window.removeEventListener('resize', onResize))
const isMobile = computed(() => windowWidth.value < 768)

function isActive(path) {
  return route.path === path
}

const mobileNavItems = computed(() => {
  if (user.value.role === 'counselor') {
    return [
      { path: '/', label: '首页', icon: Home },
      { path: '/admin', label: '成果', icon: LayoutDashboard },
      { path: '/admin/feedback', label: '树洞', icon: MessageSquareText },
      { path: '/admin/attendance', label: '考勤', icon: BarChart3 },
      { path: '/admin/profile', label: '画像', icon: Users },
    ]
  }
  if (user.value.role === 'monitor') {
    return [
      { path: '/', label: '首页', icon: Home },
      { path: '/attendance', label: '考勤', icon: ClipboardCheck },
      { path: '/upload', label: '上传', icon: Upload },
      { path: '/feedback', label: '树洞', icon: MessageCircle },
      { path: '/profile', label: '画像', icon: UserCircle },
    ]
  }
  return [
    { path: '/', label: '首页', icon: Home },
    { path: '/upload', label: '上传', icon: Upload },
    { path: '/feedback', label: '树洞', icon: MessageCircle },
    { path: '/attendance', label: '签到', icon: ScanLine },
    { path: '/profile', label: '画像', icon: UserCircle },
  ]
})

const greeting = computed(() => {
  const h = new Date().getHours()
  const name = user.value.name || '同学'
  const isCounselor = user.value.role === 'counselor'
  const isMonitor = user.value.role === 'monitor'

  if (isCounselor) {
    if (h < 6) return `夜深了，${name}老师，注意休息。`
    if (h < 9) return `早上好，${name}老师，新的一天从查看树洞开始。`
    if (h < 12) return `上午好，${name}老师，今天也在守护同学们。`
    if (h < 14) return `中午好，${name}老师，记得午休。`
    if (h < 18) return `下午好，${name}老师，辛苦了。`
    if (h < 21) return `晚上好，${name}老师，班里的小泡泡们都睡了。`
    return `夜深了，${name}老师，早点休息吧。`
  }

  if (isMonitor) {
    if (h < 9) return `早上好，${name}，今天的考勤就靠你了！`
    if (h < 12) return `上午好，${name}，别忘了给同学们点名。`
    if (h < 18) return `下午好，${name}，纪律委员辛苦了。`
    return `晚上好，${name}，今天的考勤都记录好了吗？`
  }

  if (h < 6) return `夜猫子${name}，别忘了睡觉哦。`
  if (h < 9) return `早上好，${name}，今天的空气和你的成果一样清新。`
  if (h < 12) return `上午好，${name}，状态在线，继续加油。`
  if (h < 14) return `中午好，${name}，吃饱了才有力气搞学术。`
  if (h < 18) return `下午好，${name}，下午茶时间到。`
  if (h < 21) return `晚上好，${name}，今天也辛苦了。`
  return `夜深了，${name}，早点休息明天继续。`
})

const showInfoPanel = computed(() => {
  return windowWidth.value >= 1024
})

const isAttendancePage = computed(() => {
  return route.name === 'Attendance' || route.name === 'AdminAttendance'
})

const calendarStore = useAttendanceCalendar()

function handleCalendarSelectCourse(c) {
  calendarStore.selectedCourse.value = c
}
function handleCalendarParseImage(e) {
  calendarStore._parseImageEvent.value = e
}
function handleCalendarConfirmParsed() {
  calendarStore._confirmParsedFlag.value = Date.now()
}
function handleCalendarAddCourse() {
  calendarStore._addCourseFlag.value = Date.now()
}
function handleCalendarLoadCheckinCourses() {
  calendarStore._loadCheckinCoursesFlag.value = Date.now()
}
function handleCoursesUpdated() {
  calendarStore._coursesUpdatedFlag.value = Date.now()
}
function handleCalendarSelectCheckinCourse(c) {
  calendarStore.checkinClass.value = calendarStore.checkinCalClass.value
  calendarStore.checkinCourse.value = c.course_name
  calendarStore.checkinScheduleId.value = c.id
}

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}

function handleSelectStudent(student) {
  router.push(`/admin/student/${student.student_id}`)
}

onMounted(async () => {
  if (user.value.role === 'counselor') {
    try {
      const res = await getRoster()
      const seen = new Map()
      for (const s of res.data || []) {
        if (!seen.has(s.student_id)) {
          seen.set(s.student_id, {
            student_id: s.student_id,
            name: s.name,
            class_name: s.class_name,
            major: s.major,
          })
        }
      }
      students.value = [...seen.values()]
    } catch {}
  }
})
</script>
