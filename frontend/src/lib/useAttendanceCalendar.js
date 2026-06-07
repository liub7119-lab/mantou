import { ref, computed } from 'vue'

const classes = ref([])
const selectedClass = ref('')
const weekNumber = ref(1)
const classSize = ref(0)
const courses = ref([])
const selectedCourse = ref(null)
const parsingSchedule = ref(false)
const parsedCourses = ref([])
const showAddCourse = ref(false)
const newCourse = ref({ day_of_week: '周一', period: '', course_name: '', teacher: '', classroom: '', date_str: '' })

const currentTab = ref('attendance')

const checkinCalClass = ref('')
const checkinCourses = ref([])
const checkinClass = ref('')
const checkinCourse = ref('')
const checkinScheduleId = ref(null)

const _parseImageEvent = ref(null)
const _confirmParsedFlag = ref(0)
const _addCourseFlag = ref(0)
const _loadCheckinCoursesFlag = ref(0)
const _coursesUpdatedFlag = ref(0)

const dayOptions = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

function dayColor(day) {
  const map = { '周一': '#3B82F6', '周二': '#10B981', '周三': '#F59E0B', '周四': '#EC4899', '周五': '#8B5CF6', '周六': '#6366F1', '周日': '#EF4444' }
  return map[day] || '#94A3B8'
}

const groupedCourses = computed(() => {
  const dayOrder = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const grouped = {}
  for (const c of courses.value) {
    if (!grouped[c.day_of_week]) grouped[c.day_of_week] = []
    grouped[c.day_of_week].push(c)
  }
  return dayOrder.filter(d => grouped[d]).map(d => ({ day: d, courses: grouped[d] }))
})

const checkinGroupedCourses = computed(() => {
  const dayOrder = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const grouped = {}
  for (const c of checkinCourses.value) {
    if (!grouped[c.day_of_week]) grouped[c.day_of_week] = []
    grouped[c.day_of_week].push(c)
  }
  return dayOrder.filter(d => grouped[d]).map(d => ({ day: d, courses: grouped[d] }))
})

export function useAttendanceCalendar() {
  return {
    classes,
    selectedClass,
    weekNumber,
    classSize,
    courses,
    selectedCourse,
    parsingSchedule,
    parsedCourses,
    showAddCourse,
    newCourse,
    currentTab,
    checkinCalClass,
    checkinCourses,
    checkinClass,
    checkinCourse,
    checkinScheduleId,
    dayOptions,
    dayColor,
    groupedCourses,
    checkinGroupedCourses,
    _parseImageEvent,
    _confirmParsedFlag,
    _addCourseFlag,
    _loadCheckinCoursesFlag,
    _coursesUpdatedFlag,
  }
}
