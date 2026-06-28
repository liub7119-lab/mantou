<template>
  <aside
    class="w-[304px] h-screen fixed right-0 top-0 z-30 bg-white overflow-y-auto hidden lg:block"
    style="box-shadow: -4px 0 24px rgba(0,0,0,0.03);"
  >
    <div class="p-6">
      <!-- 辅导员考勤管理页：同步课程日历 -->
      <template v-if="isAdminPage">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-sm font-semibold flex items-center gap-2" style="color: #1E293B;">
            <BookOpen class="w-4 h-4" style="color: #10B981;" />
            课程日历
          </h3>
          <button @click="loadAdminCourses" class="p-1.5 rounded-lg cursor-pointer transition-all flex items-center" style="background: #ECFDF5; color: #10B981;">
            <RefreshCw class="w-3 h-3" :class="adminLoading ? 'animate-spin' : ''" />
          </button>
        </div>

        <div class="grid grid-cols-2 gap-2 mb-3">
          <select v-model="adminClass" class="cal-input-sm cursor-pointer text-[11px]" @change="loadAdminCourses">
            <option value="">选择班级</option>
            <option v-for="c in adminClasses" :key="c" :value="c">{{ c }}</option>
          </select>
          <input v-model.number="adminWeek" type="number" min="0" placeholder="周数(0=全部)" class="cal-input-sm text-[11px]" @change="loadAdminCourses" />
        </div>

        <div v-if="adminLoading" class="text-center py-6">
          <Loader2 class="w-5 h-5 animate-spin mx-auto mb-2" style="color: #10B981;" />
          <p class="text-[10px]" style="color: #94A3B8;">加载课程中...</p>
        </div>

        <div v-else-if="adminGroupedCourses.length > 0" class="space-y-3">
          <div v-for="day in adminGroupedCourses" :key="day.day">
            <p class="text-[10px] font-semibold mb-1.5 px-1 flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full" :style="`background: ${dayColor(day.day)};`"></span>
              <span :style="`color: ${dayColor(day.day)};`">{{ day.day }}</span>
            </p>
            <div class="space-y-1">
              <div v-for="c in day.courses" :key="c.id" class="px-3 py-2 rounded-xl text-[11px]" style="background: #F8FAFC;">
                <div class="flex items-center justify-between">
                  <span class="font-medium" style="color: #1E293B;">{{ c.course_name }}</span>
                  <span class="text-[9px]" style="color: #CBD5E1;">{{ formatPeriod(c.period) }}</span>
                </div>
                <div class="flex items-center gap-2 mt-0.5">
                  <span v-if="c.date_str" class="text-[9px] px-1.5 py-0.5 rounded" style="background: #ECFDF5; color: #10B981;">{{ c.date_str }}</span>
                  <span v-if="c.teacher" class="text-[9px]" style="color: #94A3B8;">{{ c.teacher }}</span>
                  <span v-if="c.classroom" class="text-[9px]" style="color: #CBD5E1;">{{ c.classroom }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else-if="adminClass" class="text-center py-6">
          <BookOpen class="w-6 h-6 mx-auto mb-1" style="color: #CBD5E1;" />
          <p class="text-[10px]" style="color: #94A3B8;">该班级暂无课程</p>
        </div>
        <div v-else class="text-center py-6">
          <p class="text-[10px]" style="color: #94A3B8;">请先选择班级查看课程日历</p>
        </div>
      </template>

      <template v-else>
      <!-- 一键考勤模式的课程日历 -->
      <template v-if="currentTab === 'attendance'">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-sm font-semibold flex items-center gap-2" style="color: #1E293B;">
            <BookOpen class="w-4 h-4" style="color: #10B981;" />
            第{{ weekNumber }}周课程
          </h3>
          <div class="flex gap-1">
            <label class="p-1.5 rounded-lg cursor-pointer transition-all flex items-center"
              style="background: #EFF6FF; color: #3B82F6;"
            >
              <Camera class="w-3 h-3" />
              <input type="file" accept="image/*" class="hidden" @change="$emit('parseImage', $event)" :disabled="!selectedClass || !weekNumber" />
            </label>
            <button @click="showAddCourse = true" class="p-1.5 rounded-lg cursor-pointer transition-all"
              style="background: #ECFDF5; color: #10B981;"
              :disabled="!selectedClass || !weekNumber"
            >
              <Plus class="w-3 h-3" />
            </button>
          </div>
        </div>

        <!-- 课表识别中 -->
        <div v-if="parsingSchedule" class="text-center py-6">
          <Loader2 class="w-5 h-5 animate-spin mx-auto mb-2" style="color: #3B82F6;" />
          <p class="text-[10px]" style="color: #94A3B8;">识别课表中...</p>
        </div>

        <!-- 识别结果预览 -->
        <div v-if="parsedCourses.length > 0" class="mb-3 p-3 rounded-2xl" style="background: #EFF6FF;">
          <p class="text-[10px] font-medium mb-2" style="color: #3B82F6;">识别到 {{ parsedCourses.length }} 门课程</p>
          <div class="space-y-1 max-h-40 overflow-y-auto">
            <div v-for="(c, i) in parsedCourses" :key="i" class="flex items-center gap-1.5 px-2 py-1.5 rounded-lg bg-white text-[10px]">
              <span class="font-medium" style="color: #1E293B;">{{ c.day_of_week }}</span>
              <span style="color: #94A3B8;">{{ c.period }}</span>
              <span class="flex-1 truncate" style="color: #1E293B;">{{ c.course_name }}</span>
              <button @click="parsedCourses.splice(i, 1)" class="cursor-pointer" style="color: #EF4444;"><X class="w-3 h-3" /></button>
            </div>
          </div>
          <div class="flex gap-2 mt-2">
            <button @click="$emit('confirmParsed')" class="px-3 py-1.5 rounded-full text-[10px] font-medium text-white cursor-pointer" style="background: #3B82F6;">确认</button>
            <button @click="parsedCourses.length = 0" class="px-3 py-1.5 rounded-full text-[10px] cursor-pointer" style="background: #F1F5F9; color: #94A3B8;">取消</button>
          </div>
        </div>

        <!-- 手动添加 -->
        <div v-if="showAddCourse" class="mb-3 p-3 rounded-2xl" style="background: #F0FDF4;">
          <div class="grid grid-cols-2 gap-2 mb-2">
            <div>
              <label class="block text-[9px] mb-0.5" style="color: #94A3B8;">星期</label>
              <select v-model="newCourse.day_of_week" class="cal-input-sm text-[10px]">
                <option v-for="d in dayOptions" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>
            <div>
              <label class="block text-[9px] mb-0.5" style="color: #94A3B8;">节次</label>
              <input v-model="newCourse.period" class="cal-input-sm text-[10px]" placeholder="1-2" />
            </div>
            <div class="col-span-2">
              <label class="block text-[9px] mb-0.5" style="color: #94A3B8;">课程</label>
              <input v-model="newCourse.course_name" class="cal-input-sm text-[10px]" placeholder="课程名称" />
            </div>
            <div>
              <label class="block text-[9px] mb-0.5" style="color: #94A3B8;">教师</label>
              <input v-model="newCourse.teacher" class="cal-input-sm text-[10px]" placeholder="教师" />
            </div>
            <div>
              <label class="block text-[9px] mb-0.5" style="color: #94A3B8;">教室</label>
              <input v-model="newCourse.classroom" class="cal-input-sm text-[10px]" placeholder="教室" />
            </div>
          </div>
          <div class="flex gap-2">
            <button @click="$emit('addCourse')" class="px-3 py-1.5 rounded-full text-[10px] text-white cursor-pointer" style="background: #10B981;">添加</button>
            <button @click="showAddCourse = false" class="px-3 py-1.5 rounded-full text-[10px] cursor-pointer" style="background: #F1F5F9; color: #94A3B8;">取消</button>
          </div>
        </div>

        <!-- 日历式课程列表 -->
        <div v-if="courses.length > 0" class="space-y-3">
          <div v-for="day in groupedCourses" :key="day.day">
            <p class="text-[10px] font-semibold mb-1.5 px-1 flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full" :style="`background: ${dayColor(day.day)};`"></span>
              <span :style="`color: ${dayColor(day.day)};`">{{ day.day }}</span>
            </p>
            <div class="space-y-1">
              <div v-for="c in day.courses" :key="c.id">
                <!-- 编辑模式 -->
                <div v-if="editingCourse === c.id" class="p-3 rounded-xl" style="background: #F0FDF4;">
                  <div class="grid grid-cols-2 gap-2 mb-2">
                    <div>
                      <select v-model="editForm.day_of_week" class="cal-input-sm text-[10px]">
                        <option v-for="d in dayOptions" :key="d" :value="d">{{ d }}</option>
                      </select>
                    </div>
                    <div>
                      <input v-model="editForm.period" class="cal-input-sm text-[10px]" placeholder="节次" />
                    </div>
                    <div class="col-span-2">
                      <input v-model="editForm.course_name" class="cal-input-sm text-[10px]" placeholder="课程名称" />
                    </div>
                    <div>
                      <input v-model="editForm.teacher" class="cal-input-sm text-[10px]" placeholder="教师" />
                    </div>
                    <div>
                      <input v-model="editForm.classroom" class="cal-input-sm text-[10px]" placeholder="教室" />
                    </div>
                  </div>
                  <div class="flex gap-2">
                    <button @click="saveEdit" class="px-3 py-1.5 rounded-full text-[10px] text-white cursor-pointer flex items-center gap-1" style="background: #10B981;">
                      <Check class="w-3 h-3" /> 保存
                    </button>
                    <button @click="cancelEdit" class="px-3 py-1.5 rounded-full text-[10px] cursor-pointer" style="background: #F1F5F9; color: #94A3B8;">取消</button>
                  </div>
                </div>
                <!-- 正常显示 -->
                <div v-else
                  class="px-3 py-2 rounded-xl text-[11px] cursor-pointer transition-all group relative"
                  :style="selectedCourse?.id === c.id
                    ? `background: ${dayColor(c.day_of_week)}15; box-shadow: 0 0 0 1.5px ${dayColor(c.day_of_week)};`
                    : 'background: #F8FAFC;'"
                  @click="$emit('selectCourse', c)"
                >
                  <div class="flex items-center justify-between">
                    <span class="font-medium" style="color: #1E293B;">{{ c.course_name }}</span>
                    <div class="flex items-center gap-0.5">
                      <span class="text-[9px] mr-1" style="color: #CBD5E1;">{{ formatPeriod(c.period) }}</span>
                      <button @click="startEdit(c, $event)" class="w-5 h-5 rounded flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer" style="background: #EFF6FF;">
                        <Pencil class="w-2.5 h-2.5" style="color: #3B82F6;" />
                      </button>
                      <button @click="removeCourse(c, $event)" class="w-5 h-5 rounded flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer" style="background: #FEF2F2;">
                        <Trash2 class="w-2.5 h-2.5" style="color: #EF4444;" />
                      </button>
                    </div>
                  </div>
                  <div class="flex items-center gap-2 mt-0.5">
                    <span v-if="c.teacher" class="text-[9px]" style="color: #94A3B8;">{{ c.teacher }}</span>
                    <span v-if="c.classroom" class="text-[9px]" style="color: #CBD5E1;">{{ c.classroom }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else-if="!parsingSchedule && selectedClass" class="text-center py-6">
          <BookOpen class="w-6 h-6 mx-auto mb-1" style="color: #CBD5E1;" />
          <p class="text-[10px]" style="color: #94A3B8;">暂无课程，拍课表或手动添加</p>
        </div>
        <div v-else-if="!selectedClass" class="text-center py-6">
          <p class="text-[10px]" style="color: #94A3B8;">请先选择班级</p>
        </div>
      </template>

      <!-- 签到抽查模式的课程日历 -->
      <template v-if="currentTab === 'checkin'">
        <h3 class="text-sm font-semibold mb-4 flex items-center gap-2" style="color: #1E293B;">
          <BookOpen class="w-4 h-4" style="color: #8B5CF6;" />
          选择课程发起签到
        </h3>
        <div class="mb-3">
          <select v-model="checkinCalClass" class="cal-input-sm cursor-pointer text-[11px]" @change="$emit('loadCheckinCourses')">
            <option value="">选择班级</option>
            <option v-for="c in classes" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
        <div v-if="checkinCourses.length > 0" class="space-y-3">
          <div v-for="day in checkinGroupedCourses" :key="day.day">
            <p class="text-[10px] font-semibold mb-1.5 px-1 flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full" :style="`background: ${dayColor(day.day)};`"></span>
              <span :style="`color: ${dayColor(day.day)};`">{{ day.day }}</span>
            </p>
            <div class="space-y-1">
              <div v-for="c in day.courses" :key="c.id"
                class="px-3 py-2 rounded-xl text-[11px] cursor-pointer transition-all"
                style="background: #F8FAFC;"
                @click="$emit('selectCheckinCourse', c)"
              >
                <span class="font-medium" style="color: #1E293B;">{{ c.course_name }}</span>
                <span class="text-[9px] ml-1" style="color: #CBD5E1;">{{ formatPeriod(c.period) }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else-if="checkinCalClass" class="text-center py-6">
          <p class="text-[10px]" style="color: #94A3B8;">该班级暂无课程</p>
        </div>
      </template>

      <!-- 学生扫码签到 / 辅导员统计 -->
      <template v-if="currentTab === 'scan' || currentTab === 'stats' || currentTab === 'records' || currentTab === 'monitors'">
        <div class="text-center py-10">
          <BookOpen class="w-8 h-8 mx-auto mb-2" style="color: #CBD5E1;" />
          <p class="text-xs" style="color: #94A3B8;">课程日历</p>
          <p class="text-[10px] mt-1" style="color: #CBD5E1;">切换到考勤标签查看课程</p>
        </div>
      </template>

      </template>
    </div>
  </aside>
</template>

<script setup>
import { computed, ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { BookOpen, Camera, Plus, X, Loader2, Pencil, Trash2, Check, RefreshCw } from 'lucide-vue-next'
import { useAttendanceCalendar } from '@/lib/useAttendanceCalendar'
import { formatPeriod } from '@/lib/periodUtils'
import { updateSchedule, deleteSchedule, getRosterClasses, getSchedule } from '@/api'

const route = useRoute()
const isAdminPage = computed(() => route.path === '/admin/attendance')

// ──── 辅导员端课程日历（同步课表）────
const adminClasses = ref([])
const adminClass = ref('')
const adminWeek = ref(0)
const adminCourses = ref([])
const adminLoading = ref(false)

const adminGroupedCourses = computed(() => {
  const dayOrder = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const grouped = {}
  for (const c of adminCourses.value) {
    if (!grouped[c.day_of_week]) grouped[c.day_of_week] = []
    grouped[c.day_of_week].push(c)
  }
  return dayOrder.filter(d => grouped[d]).map(d => ({ day: d, courses: grouped[d] }))
})

async function loadAdminClasses() {
  try {
    const { data } = await getRosterClasses()
    adminClasses.value = data.classes
  } catch {}
}

async function loadAdminCourses() {
  if (!adminClass.value) { adminCourses.value = []; return }
  adminLoading.value = true
  try {
    const { data } = await getSchedule(adminClass.value, adminWeek.value || 0)
    adminCourses.value = data
  } catch {
    adminCourses.value = []
  } finally {
    adminLoading.value = false
  }
}

onMounted(() => {
  if (isAdminPage.value) loadAdminClasses()
})

watch(isAdminPage, (v) => {
  if (v && adminClasses.value.length === 0) loadAdminClasses()
})

const {
  classes,
  selectedClass,
  weekNumber,
  courses,
  selectedCourse,
  parsingSchedule,
  parsedCourses,
  showAddCourse,
  newCourse,
  currentTab,
  checkinCalClass,
  checkinCourses,
  dayOptions,
  dayColor,
  groupedCourses,
  checkinGroupedCourses,
} = useAttendanceCalendar()

const emit = defineEmits([
  'selectCourse',
  'parseImage',
  'confirmParsed',
  'addCourse',
  'loadCheckinCourses',
  'selectCheckinCourse',
  'coursesUpdated',
])

const editingCourse = ref(null)
const editForm = ref({ day_of_week: '', period: '', course_name: '', teacher: '', classroom: '' })

function startEdit(c, e) {
  e.stopPropagation()
  editingCourse.value = c.id
  editForm.value = {
    day_of_week: c.day_of_week,
    period: c.period,
    course_name: c.course_name,
    teacher: c.teacher || '',
    classroom: c.classroom || '',
  }
}

async function saveEdit() {
  if (!editForm.value.course_name) return
  try {
    await updateSchedule(editingCourse.value, {
      class_name: selectedClass.value,
      week_number: weekNumber.value,
      ...editForm.value,
    })
    editingCourse.value = null
    emit('coursesUpdated')
  } catch {}
}

function cancelEdit() {
  editingCourse.value = null
}

async function removeCourse(c, e) {
  e.stopPropagation()
  if (!confirm(`确定删除「${c.course_name}」？`)) return
  try {
    await deleteSchedule(c.id)
    emit('coursesUpdated')
  } catch {}
}
</script>

<style scoped>
@reference "../../style.css";

.cal-input-sm {
  @apply w-full rounded-xl px-3 py-2 text-xs transition-all duration-200
         focus:outline-none focus:ring-2 focus:border-transparent;
  background: #F1F5F9;
  color: #1E293B;
  --tw-ring-color: rgba(59, 130, 246, 0.4);
}
</style>
