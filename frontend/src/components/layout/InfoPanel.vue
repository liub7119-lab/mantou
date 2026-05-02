<template>
  <aside
    class="w-[304px] h-screen fixed right-0 top-0 z-30 bg-white overflow-y-auto hidden lg:block"
    style="border-left: 1px solid #E8ECF0;"
  >
    <div class="p-5">
      <!-- 牛牛形象 -->
      <div class="text-center mb-4">
        <img src="/src/assets/ui/sidebar-cow.png" alt="小牛同学" class="w-24 h-24 mx-auto object-contain" />
        <div class="inline-block mt-2 px-4 py-1.5 rounded-full text-xs font-medium" style="background: #FFD60E; color: #8B6914;">
          又是充实的一天呢！
        </div>
      </div>

      <!-- 学生端：五维雷达图 -->
      <template v-if="role === 'student'">
        <h3 class="text-sm font-bold mb-4 flex items-center gap-2" style="color: #333;">
          <Radar class="w-4 h-4" style="color: #6ECAFF;" />
          个人能力画像
        </h3>

        <div class="flex justify-center mb-4">
          <svg viewBox="0 0 200 200" class="w-40 h-40">
            <polygon
              v-for="level in [0.2, 0.4, 0.6, 0.8, 1.0]"
              :key="level"
              :points="gridPoints(level)"
              fill="none"
              :stroke="level === 1 ? '#E8ECF0' : '#F2F4F7'"
              stroke-width="0.8"
            />
            <line
              v-for="(_, i) in dims"
              :key="'ax-' + i"
              x1="100" y1="100"
              :x2="axisPoint(i, 1).x"
              :y2="axisPoint(i, 1).y"
              stroke="#E8ECF0"
              stroke-width="0.5"
            />
            <polygon
              :points="dataPoints"
              fill="rgba(110,202,255,0.15)"
              stroke="#6ECAFF"
              stroke-width="1.5"
            />
            <circle
              v-for="(dim, i) in dims"
              :key="'dot-' + i"
              :cx="axisPoint(i, dim.value).x"
              :cy="axisPoint(i, dim.value).y"
              r="3"
              fill="#6ECAFF"
            />
            <text
              v-for="(dim, i) in dims"
              :key="'lb-' + i"
              :x="axisPoint(i, 1.22).x"
              :y="axisPoint(i, 1.22).y"
              text-anchor="middle"
              dominant-baseline="central"
              fill="#999"
              font-size="9"
            >
              {{ dim.label }}
            </text>
          </svg>
        </div>

        <div class="space-y-2.5 mb-5">
          <div v-for="dim in dims" :key="dim.label" class="flex items-center justify-between">
            <span class="text-xs" style="color: #999;">{{ dim.label }}</span>
            <div class="flex items-center gap-2">
              <div class="w-20 h-1.5 rounded-full overflow-hidden" style="background: #F2F4F7;">
                <div class="h-full rounded-full transition-all duration-500" :style="{ width: dim.value * 100 + '%', background: barColor(dim.value) }"></div>
              </div>
              <span class="text-xs font-medium w-6 text-right" :style="{ color: dim.value < 0.4 ? '#EF4444' : '#333' }">{{ Math.round(dim.value * 100) }}</span>
            </div>
          </div>
        </div>

        <div v-if="warnings.length" class="p-3 rounded-xl mb-4" style="background: #FEF2F2;">
          <p class="text-xs font-medium mb-1 flex items-center gap-1" style="color: #EF4444;">
            <TriangleAlert class="w-3 h-3" />
            能力预警
          </p>
          <ul class="space-y-0.5">
            <li v-for="w in warnings" :key="w" class="text-[10px]" style="color: #EF4444;">· {{ w }}</li>
          </ul>
        </div>
      </template>

      <!-- 辅导员端 -->
      <template v-else>
        <!-- 快捷服务 -->
        <div class="grid grid-cols-4 gap-2 mb-5">
          <router-link v-for="s in services" :key="s.label" :to="s.path"
            class="flex flex-col items-center gap-1 py-2 rounded-lg transition-colors"
            @mouseenter="$event.currentTarget.style.background='#F7F8FA'"
            @mouseleave="$event.currentTarget.style.background='transparent'"
          >
            <div class="w-8 h-8 rounded-lg flex items-center justify-center" :style="{ background: s.bg }">
              <component :is="s.icon" class="w-4 h-4" :style="{ color: s.color }" />
            </div>
            <span class="text-[10px]" style="color: #555;">{{ s.label }}</span>
          </router-link>
        </div>

        <!-- 今日待办 -->
        <h3 class="text-sm font-bold mb-3 flex items-center gap-2" style="color: #333;">
          <CalendarDays class="w-4 h-4" style="color: #6ECAFF;" />
          今日待办
        </h3>
        <div class="space-y-2 mb-5">
          <div v-for="(task, i) in counselorTodos" :key="i" class="flex items-center gap-2.5 px-3 py-2 rounded-xl" style="background: #F7F8FA;">
            <div class="w-1.5 h-1.5 rounded-full shrink-0" :style="{ background: task.color }"></div>
            <span class="text-xs flex-1" style="color: #555;">{{ task.text }}</span>
            <span class="text-[10px]" style="color: #999;">{{ task.time }}</span>
          </div>
          <button class="w-full text-[10px] py-1.5 rounded-lg transition-colors" style="color: #6ECAFF;" @mouseenter="$event.target.style.background='#E8F4FD'" @mouseleave="$event.target.style.background='transparent'">
            查看全部
          </button>
        </div>

        <!-- 通知公告 -->
        <h3 class="text-sm font-bold mb-3 flex items-center gap-2" style="color: #333;">
          <Bell class="w-4 h-4" style="color: #FFD60E;" />
          通知公告
        </h3>
        <div class="space-y-2 mb-5">
          <div v-for="(n, i) in notices" :key="i" class="flex items-start gap-2 px-3 py-2 rounded-xl" style="background: #F7F8FA;">
            <div class="w-1.5 h-1.5 rounded-full mt-1.5 shrink-0" :style="{ background: n.color }"></div>
            <div class="flex-1 min-w-0">
              <p class="text-xs truncate" style="color: #333;">{{ n.text }}</p>
              <p class="text-[10px]" style="color: #999;">{{ n.date }}</p>
            </div>
          </div>
        </div>

        <div class="h-px mb-4" style="background: #E8ECF0;"></div>

        <!-- 班级成员 -->
        <h3 class="text-sm font-bold mb-3 flex items-center gap-2" style="color: #333;">
          <Users class="w-4 h-4" style="color: #8FD6B0;" />
          班级成员
        </h3>

        <input
          v-model="search"
          type="text"
          placeholder="搜索学生姓名或学号..."
          class="w-full px-3 py-2 text-xs rounded-lg transition-all duration-200 focus:outline-none focus:ring-2"
          style="background: #F2F4F7; color: #333; --tw-ring-color: rgba(110,202,255,0.4);"
        />
        <p class="text-[10px] mt-1.5 mb-2" style="color: #999;">共 {{ filteredStudents.length }} 名学生</p>

        <div class="space-y-0.5 max-h-[calc(100vh-700px)] overflow-y-auto">
          <button
            v-for="s in filteredStudents"
            :key="s.student_id"
            @click="$emit('selectStudent', s)"
            class="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-left cursor-pointer transition-all duration-200"
            @mouseenter="$event.currentTarget.style.background = '#F7F8FA'"
            @mouseleave="$event.currentTarget.style.background = 'transparent'"
          >
            <div class="w-7 h-7 rounded-full flex items-center justify-center shrink-0 text-[10px] font-semibold"
              :style="{ background: s.warning ? '#FEF2F2' : '#E8F4FD', color: s.warning ? '#EF4444' : '#6ECAFF' }"
            >
              {{ s.name?.charAt(0) }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-medium truncate" style="color: #333;">{{ s.name }}</p>
              <p class="text-[10px] truncate" style="color: #999;">{{ s.student_id }}</p>
            </div>
          </button>
          <p v-if="!filteredStudents.length" class="text-xs text-center py-4" style="color: #999;">暂无学生数据</p>
        </div>
      </template>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  Radar, TriangleAlert, Users, CalendarDays, Bell,
  LayoutDashboard, MessageSquareText, BarChart3, ClipboardCheck,
  Upload, MessageCircle, Trophy, Settings,
} from 'lucide-vue-next'

const props = defineProps({
  role: { type: String, required: true },
  students: { type: Array, default: () => [] },
})

defineEmits(['selectStudent'])

const search = ref('')

const filteredStudents = computed(() => {
  if (!search.value) return props.students
  const q = search.value.toLowerCase()
  return props.students.filter(s =>
    s.name?.toLowerCase().includes(q) || s.student_id?.includes(q)
  )
})

const dims = ref([
  { label: '学业成绩', value: 0.82 },
  { label: '竞赛获奖', value: 0.65 },
  { label: '社会实践', value: 0.45 },
  { label: '志愿服务', value: 0.35 },
  { label: '文体活动', value: 0.70 },
])

const warnings = computed(() =>
  dims.value.filter(d => d.value < 0.4).map(d => `${d.label}得分偏低，建议加强`)
)

function axisPoint(index, ratio) {
  const angle = (Math.PI * 2 * index) / dims.value.length - Math.PI / 2
  return {
    x: 100 + Math.cos(angle) * 70 * ratio,
    y: 100 + Math.sin(angle) * 70 * ratio,
  }
}

function gridPoints(level) {
  return dims.value.map((_, i) => {
    const p = axisPoint(i, level)
    return `${p.x},${p.y}`
  }).join(' ')
}

const dataPoints = computed(() =>
  dims.value.map((d, i) => {
    const p = axisPoint(i, d.value)
    return `${p.x},${p.y}`
  }).join(' ')
)

function barColor(val) {
  if (val < 0.4) return '#EF4444'
  if (val < 0.7) return '#FFD60E'
  return '#6ECAFF'
}

const services = [
  { label: '成果管理', icon: LayoutDashboard, path: '/admin', color: '#6ECAFF', bg: '#E8F4FD' },
  { label: '树洞管理', icon: MessageSquareText, path: '/admin/feedback', color: '#8FD6B0', bg: '#E8F7EF' },
  { label: '考勤管理', icon: BarChart3, path: '/admin/attendance', color: '#FFD60E', bg: '#FFF8E1' },
  { label: '设置', icon: Settings, path: '/', color: '#B4A0E5', bg: '#F3F0FF' },
]

const counselorTodos = [
  { text: '审核学生成果提交', time: '09:30', color: '#6ECAFF' },
  { text: '回复树洞反馈', time: '截止·今天', color: '#EF4444' },
  { text: '查看考勤统计', time: '10:00', color: '#8FD6B0' },
]

const notices = [
  { text: '关于2024年五一放假安排的通知', date: '04-24', color: '#6ECAFF' },
  { text: '校园卡服务时间调整说明', date: '04-22', color: '#FFD60E' },
]
</script>
