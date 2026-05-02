<template>
  <div>
    <div class="flex items-start justify-between mb-7">
      <div class="flex items-center gap-3 relative">
        <img src="/src/assets/ui/sticker-star.png" alt="" class="absolute -top-3 -left-3 w-7 h-7 opacity-25 pointer-events-none" />
        <div class="w-12 h-12 rounded-2xl flex items-center justify-center" style="background: #E8F4FD;">
          <BarChart3 class="w-5 h-5" style="color: #6ECAFF;" />
        </div>
        <div>
          <h2 class="text-lg font-bold" style="color: #1E293B;">考勤管理</h2>
          <p class="text-xs" style="color: #94A3B8;">查看考勤数据和管理纪律委员</p>
        </div>
      </div>
    </div>

    <!-- Tab 切换 -->
    <div class="flex gap-2 mb-7">
      <button
        v-for="t in tabList" :key="t.key"
        @click="currentTab = t.key"
        class="px-5 py-2.5 text-sm font-medium rounded-full transition-all duration-200 cursor-pointer flex items-center gap-2"
        :style="currentTab === t.key
          ? `background: ${t.color}; color: white;`
          : 'background: #F1F5F9; color: #94A3B8;'"
      >
        <component :is="t.icon" class="w-4 h-4" />
        {{ t.label }}
      </button>
    </div>

    <!-- ========== 统计概览 ========== -->
    <div v-if="currentTab === 'stats'" class="space-y-6">
      <div class="rounded-3xl p-7 flex gap-5 items-end flex-wrap" style="background: #F0FDF4; box-shadow: 0 2px 16px rgba(16,185,129,0.06);">
        <div>
          <label class="block text-xs mb-1.5" style="color: #94A3B8;">班级</label>
          <select v-model="statsFilter.class_name" class="admin-att-input cursor-pointer">
            <option value="">全部</option>
            <option v-for="c in classes" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        <div>
          <label class="block text-xs mb-1.5" style="color: #94A3B8;">周数</label>
          <input v-model.number="statsFilter.week" type="number" min="0" class="admin-att-input" placeholder="0=全部" />
        </div>
        <div>
          <label class="block text-xs mb-1.5" style="color: #94A3B8;">授课教师</label>
          <input v-model="statsFilter.teacher" class="admin-att-input" placeholder="教师姓名" />
        </div>
        <button @click="loadStats" class="px-5 py-2.5 rounded-full text-sm font-medium text-white cursor-pointer flex items-center gap-2" style="background: #10B981;">
          <Search class="w-3.5 h-3.5" />
          查询
        </button>
      </div>

      <div v-if="stats" class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="rounded-2xl p-5" style="background: linear-gradient(135deg, #ECFDF5, #D1FAE5);">
          <p class="text-[10px] mb-1" style="color: #059669;">考勤次数</p>
          <p class="text-xl font-bold" style="color: #047857;">{{ stats.total_records }}</p>
        </div>
        <div class="rounded-2xl p-5" style="background: linear-gradient(135deg, #EFF6FF, #DBEAFE);">
          <p class="text-[10px] mb-1" style="color: #3B82F6;">平均到课率</p>
          <p class="text-xl font-bold" style="color: #1D4ED8;">{{ stats.avg_rate }}</p>
        </div>
        <div class="rounded-2xl p-5" style="background: linear-gradient(135deg, #FFFBEB, #FEF3C7);">
          <p class="text-[10px] mb-1" style="color: #F59E0B;">总迟到人次</p>
          <p class="text-xl font-bold" style="color: #D97706;">{{ stats.total_late }}</p>
        </div>
        <div class="rounded-2xl p-5" style="background: linear-gradient(135deg, #FEF2F2, #FECACA);">
          <p class="text-[10px] mb-1" style="color: #EF4444;">总旷课人次</p>
          <p class="text-xl font-bold" style="color: #DC2626;">{{ stats.total_absent }}</p>
        </div>
      </div>

      <div v-if="stats && stats.total_records > 0" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white rounded-3xl p-7" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
          <h3 class="text-sm font-semibold mb-4" style="color: #1E293B;">各班到课率</h3>
          <canvas ref="barChartRef" height="200"></canvas>
        </div>
        <div class="bg-white rounded-3xl p-7" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
          <h3 class="text-sm font-semibold mb-4" style="color: #1E293B;">缺勤原因分布</h3>
          <canvas ref="pieChartRef" height="200"></canvas>
        </div>
      </div>
      <div v-else-if="stats && stats.total_records === 0" class="bg-white rounded-3xl p-7 text-center" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
        <Inbox class="w-8 h-8 mx-auto mb-2" style="color: #CBD5E1;" />
        <p class="text-xs" style="color: #94A3B8;">暂无考勤数据，纪律委员提交考勤后将在此处显示统计图表</p>
      </div>
    </div>

    <!-- ========== 考勤数据 ========== -->
    <div v-if="currentTab === 'records'" class="space-y-6">
      <div class="rounded-3xl p-7 flex gap-5 items-end flex-wrap" style="background: #F0FDF4; box-shadow: 0 2px 16px rgba(16,185,129,0.06);">
        <div>
          <label class="block text-xs mb-1.5" style="color: #94A3B8;">班级</label>
          <select v-model="filterClass" class="admin-att-input cursor-pointer">
            <option value="">全部</option>
            <option v-for="c in classes" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        <div>
          <label class="block text-xs mb-1.5" style="color: #94A3B8;">周数</label>
          <input v-model.number="filterWeek" type="number" min="0" class="admin-att-input" placeholder="0=全部" />
        </div>
        <button @click="loadRecords" class="px-5 py-2.5 rounded-full text-sm font-medium text-white cursor-pointer flex items-center gap-2" style="background: #10B981;">
          <Search class="w-3.5 h-3.5" />
          查询
        </button>
        <button @click="exportRecords" class="px-5 py-2.5 rounded-full text-sm font-medium cursor-pointer flex items-center gap-2" style="background: #EFF6FF; color: #3B82F6;">
          <Download class="w-3.5 h-3.5" />
          导出表格
        </button>
      </div>

      <div class="bg-white rounded-3xl p-7" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
        <div v-if="loading" class="text-center py-10">
          <Loader2 class="w-6 h-6 animate-spin mx-auto" style="color: #10B981;" />
        </div>
        <div v-else-if="records.length === 0" class="text-center py-10">
          <Inbox class="w-8 h-8 mx-auto mb-2" style="color: #CBD5E1;" />
          <p class="text-xs" style="color: #94A3B8;">暂无考勤记录</p>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-xs">
            <thead>
              <tr style="background: #F0FDF4;">
                <th class="px-3 py-3 text-left rounded-l-xl font-medium" style="color: #059669;">日期</th>
                <th class="px-3 py-3 text-left font-medium" style="color: #059669;">班级</th>
                <th class="px-3 py-3 text-left font-medium" style="color: #059669;">课程</th>
                <th class="px-3 py-3 text-center font-medium" style="color: #059669;">人数</th>
                <th class="px-3 py-3 text-center font-medium" style="color: #059669;">实到</th>
                <th class="px-3 py-3 text-center font-medium" style="color: #059669;">病/公假</th>
                <th class="px-3 py-3 text-center font-medium" style="color: #059669;">事假</th>
                <th class="px-3 py-3 text-center font-medium" style="color: #059669;">旷课</th>
                <th class="px-3 py-3 text-center font-medium" style="color: #059669;">到课率</th>
                <th class="px-3 py-3 text-left rounded-r-xl font-medium" style="color: #059669;">情况说明</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in records" :key="r.id" class="border-b" style="border-color: #F1F5F9;">
                <td class="px-3 py-3" style="color: #1E293B;">{{ r.date_str }} {{ r.day_of_week }}</td>
                <td class="px-3 py-3" style="color: #475569;">{{ r.class_name }}</td>
                <td class="px-3 py-3" style="color: #475569;">{{ r.course_name }}</td>
                <td class="px-3 py-3 text-center" style="color: #1E293B;">{{ r.class_size }}</td>
                <td class="px-3 py-3 text-center font-medium" style="color: #10B981;">{{ r.actual_count }}</td>
                <td class="px-3 py-3 text-center" style="color: #3B82F6;">{{ r.sick_leave_count }}</td>
                <td class="px-3 py-3 text-center" style="color: #F59E0B;">{{ r.personal_leave_count }}</td>
                <td class="px-3 py-3 text-center font-medium" :style="r.absent_count > 0 ? 'color: #EF4444;' : 'color: #94A3B8;'">{{ r.absent_count }}</td>
                <td class="px-3 py-3 text-center">
                  <span class="px-2 py-1 rounded-lg font-medium"
                    :style="parseInt(r.attendance_rate) >= 95 ? 'background: #ECFDF5; color: #10B981;' :
                             parseInt(r.attendance_rate) >= 90 ? 'background: #FFFBEB; color: #F59E0B;' :
                             'background: #FEF2F2; color: #EF4444;'"
                  >{{ r.attendance_rate }}</span>
                </td>
                <td class="px-3 py-3 max-w-48 truncate" style="color: #94A3B8;" :title="r.leave_details">{{ r.leave_details || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ========== 纪律委员管理 ========== -->
    <div v-if="currentTab === 'monitors'" class="space-y-6">
      <div class="bg-white rounded-3xl p-7" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
        <h3 class="text-sm font-semibold mb-4 flex items-center gap-2" style="color: #1E293B;">
          <Shield class="w-4 h-4" style="color: #8B5CF6;" />
          当前纪律委员
        </h3>
        <div v-if="monitors.length === 0" class="text-center py-8">
          <Users class="w-8 h-8 mx-auto mb-2" style="color: #CBD5E1;" />
          <p class="text-xs" style="color: #94A3B8;">暂未设置纪律委员</p>
        </div>
        <div v-else class="space-y-3">
          <div v-for="m in monitors" :key="m.username" class="flex items-center gap-3 px-4 py-3 rounded-2xl" style="background: #F5F3FF;">
            <div class="w-8 h-8 rounded-full flex items-center justify-center" style="background: #8B5CF6;">
              <span class="text-xs font-bold text-white">{{ m.name?.charAt(0) }}</span>
            </div>
            <div class="flex-1">
              <p class="text-sm font-medium" style="color: #1E293B;">{{ m.name }}</p>
              <p class="text-[10px]" style="color: #94A3B8;">{{ m.username }} · {{ m.class_name }}</p>
            </div>
            <button
              @click="demoteMonitor(m.username)"
              class="px-3 py-1.5 rounded-full text-[10px] cursor-pointer transition-all"
              style="background: #FEF2F2; color: #EF4444;"
            >
              取消权限
            </button>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-3xl p-7" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
        <h3 class="text-sm font-semibold mb-4 flex items-center gap-2" style="color: #1E293B;">
          <UserPlus class="w-4 h-4" style="color: #10B981;" />
          设置纪律委员
        </h3>
        <p class="text-xs mb-4" style="color: #94A3B8;">从已注册的学生中选择纪律委员（学生需先注册账号）</p>
        <div v-if="allStudents.length === 0" class="text-center py-6">
          <p class="text-xs" style="color: #94A3B8;">暂无已注册的学生</p>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div v-for="s in allStudents" :key="s.username" class="flex items-center gap-3 px-4 py-3 rounded-2xl" style="background: #F8FAFC;">
            <div class="flex-1">
              <p class="text-xs font-medium" style="color: #1E293B;">{{ s.name }}</p>
              <p class="text-[10px]" style="color: #94A3B8;">{{ s.username }} · {{ s.class_name }}</p>
            </div>
            <button
              v-if="s.role === 'student'"
              @click="promoteMonitor(s.username)"
              class="px-3 py-1.5 rounded-full text-[10px] font-medium cursor-pointer transition-all"
              style="background: #ECFDF5; color: #10B981;"
            >
              设为纪律委员
            </button>
            <span v-else class="px-3 py-1.5 rounded-full text-[10px] font-medium" style="background: #F5F3FF; color: #8B5CF6;">
              纪律委员
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import {
  BarChart3, Search, Loader2, Inbox, Shield, Users, UserPlus,
  ClipboardCheck, UserCog, PieChart, Download,
} from 'lucide-vue-next'
import { Chart, registerables } from 'chart.js'
import {
  getRosterClasses, listAttendanceRecords, getAttendanceStats,
  listMonitors, listAllStudents, setMonitor, exportAttendanceRecords,
} from '../api'

Chart.register(...registerables)

const tabList = [
  { key: 'stats', label: '统计概览', icon: PieChart, color: '#10B981' },
  { key: 'records', label: '考勤数据', icon: ClipboardCheck, color: '#3B82F6' },
  { key: 'monitors', label: '纪律委员', icon: UserCog, color: '#8B5CF6' },
]

const currentTab = ref('stats')
const classes = ref([])
const filterClass = ref('')
const filterWeek = ref(0)
const loading = ref(false)
const records = ref([])
const stats = ref(null)
const monitors = ref([])
const allStudents = ref([])

const statsFilter = ref({ class_name: '', week: 0, teacher: '' })
const barChartRef = ref(null)
const pieChartRef = ref(null)
let barChart = null
let pieChart = null

async function loadRecords() {
  loading.value = true
  try {
    const res = await listAttendanceRecords(filterClass.value, filterWeek.value)
    records.value = res.data
  } catch (err) {
    console.error('获取记录失败', err)
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    const res = await listAttendanceRecords(statsFilter.value.class_name, statsFilter.value.week)
    let data = res.data

    if (statsFilter.value.teacher) {
      data = data.filter(r => r.teacher?.includes(statsFilter.value.teacher))
    }

    const total = data.length
    const rates = []
    let totalAbsent = 0, totalLate = 0, totalSick = 0, totalPersonal = 0, totalEarly = 0
    const classRates = {}

    for (const r of data) {
      try { rates.push(parseInt(r.attendance_rate.replace('%', ''))) } catch {}
      totalAbsent += r.absent_count || 0
      totalLate += r.late_count || 0
      totalSick += r.sick_leave_count || 0
      totalPersonal += r.personal_leave_count || 0
      totalEarly += r.early_leave_count || 0

      if (!classRates[r.class_name]) classRates[r.class_name] = []
      try { classRates[r.class_name].push(parseInt(r.attendance_rate.replace('%', ''))) } catch {}
    }

    const avgRate = rates.length > 0 ? `${Math.round(rates.reduce((a, b) => a + b, 0) / rates.length)}%` : '0%'
    stats.value = { total_records: total, avg_rate: avgRate, total_absent: totalAbsent, total_late: totalLate }

    await nextTick()
    renderBarChart(classRates)
    renderPieChart({ totalSick, totalPersonal, totalLate, totalEarly, totalAbsent })
  } catch {}
}

function renderBarChart(classRates) {
  if (barChart) barChart.destroy()
  if (!barChartRef.value) return
  const labels = Object.keys(classRates)
  const values = labels.map(k => {
    const arr = classRates[k]
    return arr.length > 0 ? Math.round(arr.reduce((a, b) => a + b, 0) / arr.length) : 0
  })
  barChart = new Chart(barChartRef.value, {
    type: 'bar',
    data: {
      labels: labels.map(l => l.length > 10 ? l.slice(-6) : l),
      datasets: [{
        label: '平均到课率 %',
        data: values,
        backgroundColor: values.map(v => v >= 95 ? '#10B981' : v >= 90 ? '#F59E0B' : '#EF4444'),
        borderRadius: 8,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, max: 100 } },
    },
  })
}

function renderPieChart({ totalSick, totalPersonal, totalLate, totalEarly, totalAbsent }) {
  if (pieChart) pieChart.destroy()
  if (!pieChartRef.value) return
  const allZero = totalSick + totalPersonal + totalLate + totalEarly + totalAbsent === 0
  if (allZero) return
  pieChart = new Chart(pieChartRef.value, {
    type: 'doughnut',
    data: {
      labels: ['病/公假', '事假', '迟到', '早退', '旷课'],
      datasets: [{
        data: [totalSick, totalPersonal, totalLate, totalEarly, totalAbsent],
        backgroundColor: ['#3B82F6', '#F59E0B', '#EC4899', '#8B5CF6', '#EF4444'],
        borderWidth: 0,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom', labels: { font: { size: 11 }, padding: 12 } },
      },
    },
  })
}

async function exportRecords() {
  try {
    const res = await exportAttendanceRecords(filterClass.value, filterWeek.value)
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = `考勤记录_${filterClass.value || '全部'}_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error('导出失败', err)
  }
}

async function loadMonitors() {
  try {
    const [mRes, sRes] = await Promise.all([
      listMonitors(),
      listAllStudents(),
    ])
    monitors.value = mRes.data
    allStudents.value = sRes.data
  } catch {}
}

async function promoteMonitor(username) {
  try {
    await setMonitor(username, 'promote')
    loadMonitors()
  } catch (err) {
    console.error('设置失败', err)
  }
}

async function demoteMonitor(username) {
  try {
    await setMonitor(username, 'demote')
    loadMonitors()
  } catch (err) {
    console.error('取消失败', err)
  }
}

onMounted(async () => {
  try {
    const { data } = await getRosterClasses()
    classes.value = data.classes
  } catch {}
  loadStats()
  loadRecords()
  loadMonitors()
})
</script>

<style scoped>
@reference "../style.css";

.admin-att-input {
  @apply rounded-2xl px-4 py-3 text-sm transition-all duration-200
         focus:outline-none focus:ring-2 focus:border-transparent;
  background: #F1F5F9;
  color: #1E293B;
  --tw-ring-color: rgba(16, 185, 129, 0.4);
}
</style>
