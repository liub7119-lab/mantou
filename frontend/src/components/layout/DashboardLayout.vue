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
    />
    <InfoPanel
      v-else
      :role="user.role"
      :students="students"
      @select-student="handleSelectStudent"
    />

    <!-- Main -->
    <main
      class="transition-all duration-300 ease-out min-h-screen"
      :style="{
        marginLeft: sidebarExpanded ? '224px' : '72px',
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
          <!-- Search -->
          <div class="relative">
            <Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2" style="color: #999;" />
            <input
              type="text"
              placeholder="搜索功能或信息..."
              class="pl-9 pr-4 py-2 text-sm rounded-full w-36 md:w-44 lg:w-52 focus:outline-none focus:ring-2"
              style="background: #F2F4F7; color: #333; --tw-ring-color: #6ECAFF;"
            />
          </div>
          <!-- Bell -->
          <button class="w-10 h-10 rounded-full flex items-center justify-center cursor-pointer transition-colors duration-150" style="background: #F2F4F7;" @mouseenter="$event.currentTarget.style.background='#E8F4FD'" @mouseleave="$event.currentTarget.style.background='#F2F4F7'">
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
            退出
          </button>
        </div>
      </header>

      <div class="p-4 md:p-6 lg:p-10">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { LogOut, Search, Bell } from 'lucide-vue-next'
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
  if (typeof window !== 'undefined' && window.innerWidth < 1024) return false
  return true
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
