<template>
  <div class="p-6 space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <Users class="w-8 h-8" style="color: #8FD6B0;" />
        <div>
          <h1 class="text-2xl font-bold" style="color: #333;">班级成长画像</h1>
          <p class="text-sm" style="color: #AABBC8;">查看全班学生成长情况和总体统计</p>
        </div>
      </div>

      <!-- 班级选择 -->
      <select v-model="selectedClass" @change="loadClassData" class="px-4 py-2 rounded-2xl text-sm font-medium border-0 cursor-pointer" style="background: #F5F7FA; color: #333;">
        <option v-for="cls in classList" :key="cls" :value="cls">{{ cls }}</option>
      </select>
    </div>

    <div v-if="loading" class="flex justify-center py-20">
      <Loader2 class="w-8 h-8 animate-spin" style="color: #8FD6B0;" />
    </div>

    <template v-else>
      <!-- 总体统计 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div class="bg-white rounded-3xl p-6 text-center" style="box-shadow: 0 4px 20px rgba(110,170,210,0.08);">
          <div class="text-3xl font-bold mb-1" style="color: #6ECAFF;">{{ data.summary.total_students }}</div>
          <div class="text-xs" style="color: #AABBC8;">班级总人数</div>
        </div>
        <div class="bg-white rounded-3xl p-6 text-center" style="box-shadow: 0 4px 20px rgba(110,170,210,0.08);">
          <div class="text-3xl font-bold mb-1" style="color: #8FD6B0;">{{ data.summary.students_with_achievements }}</div>
          <div class="text-xs" style="color: #AABBC8;">有成果学生</div>
        </div>
        <div class="bg-white rounded-3xl p-6 text-center" style="box-shadow: 0 4px 20px rgba(110,170,210,0.08);">
          <div class="text-3xl font-bold mb-1" style="color: #FFD60E;">{{ data.summary.participation_rate }}%</div>
          <div class="text-xs" style="color: #AABBC8;">参与率</div>
        </div>
        <div class="bg-white rounded-3xl p-6 text-center" style="box-shadow: 0 4px 20px rgba(110,170,210,0.08);">
          <div class="text-3xl font-bold mb-1" style="color: #FF9F43;">{{ data.summary.total_count }}</div>
          <div class="text-xs" style="color: #AABBC8;">总成果数</div>
        </div>
        <div class="bg-white rounded-3xl p-6 text-center" style="box-shadow: 0 4px 20px rgba(110,170,210,0.08);">
          <div class="text-3xl font-bold mb-1" style="color: #EE5A6F;">{{ avgAchievements }}</div>
          <div class="text-xs" style="color: #AABBC8;">人均成果</div>
        </div>
      </div>

      <!-- 成果分类统计 -->
      <div class="bg-white rounded-3xl p-8" style="box-shadow: 0 4px 20px rgba(110,170,210,0.08);">
        <h2 class="text-lg font-bold mb-6" style="color: #333;">成果分类统计</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="text-center p-4 rounded-2xl" style="background: #F5F7FA;">
            <div class="text-2xl font-bold mb-1" style="color: #8FD6B0;">{{ data.summary.total_achievements.research_projects }}</div>
            <div class="text-xs" style="color: #AABBC8;">科研项目</div>
          </div>
          <div class="text-center p-4 rounded-2xl" style="background: #F5F7FA;">
            <div class="text-2xl font-bold mb-1" style="color: #FF9F43;">{{ data.summary.total_achievements.patents }}</div>
            <div class="text-xs" style="color: #AABBC8;">专利软著</div>
          </div>
          <div class="text-center p-4 rounded-2xl" style="background: #F5F7FA;">
            <div class="text-2xl font-bold mb-1" style="color: #EE5A6F;">{{ data.summary.total_achievements.papers }}</div>
            <div class="text-xs" style="color: #AABBC8;">学术论文</div>
          </div>
          <div class="text-center p-4 rounded-2xl" style="background: #F5F7FA;">
            <div class="text-2xl font-bold mb-1" style="color: #A55EEA;">{{ data.summary.total_achievements.competitions }}</div>
            <div class="text-xs" style="color: #AABBC8;">学科竞赛</div>
          </div>
        </div>
      </div>

      <!-- 学生列表 -->
      <div class="bg-white rounded-3xl p-8" style="box-shadow: 0 4px 20px rgba(110,170,210,0.08);">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-lg font-bold" style="color: #333;">学生成长画像列表</h2>
          <div class="flex items-center gap-2">
            <input v-model="searchQuery" type="text" placeholder="搜索学号或姓名" class="px-4 py-2 rounded-2xl text-sm border-0" style="background: #F5F7FA; color: #333;" />
            <Search class="w-5 h-5" style="color: #AABBC8;" />
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b" style="border-color: #F5F7FA;">
                <th class="text-left py-3 px-4 text-xs font-semibold" style="color: #AABBC8;">学号</th>
                <th class="text-left py-3 px-4 text-xs font-semibold" style="color: #AABBC8;">姓名</th>
                <th class="text-left py-3 px-4 text-xs font-semibold" style="color: #AABBC8;">性别</th>
                <th class="text-left py-3 px-4 text-xs font-semibold" style="color: #AABBC8;">民族</th>
                <th class="text-left py-3 px-4 text-xs font-semibold" style="color: #AABBC8;">政治面貌</th>
                <th class="text-center py-3 px-4 text-xs font-semibold" style="color: #AABBC8;">科研项目</th>
                <th class="text-center py-3 px-4 text-xs font-semibold" style="color: #AABBC8;">专利软著</th>
                <th class="text-center py-3 px-4 text-xs font-semibold" style="color: #AABBC8;">学术论文</th>
                <th class="text-center py-3 px-4 text-xs font-semibold" style="color: #AABBC8;">学科竞赛</th>
                <th class="text-center py-3 px-4 text-xs font-semibold" style="color: #AABBC8;">总计</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in filteredStudents" :key="student.student_id" class="border-b hover:bg-gray-50 transition-colors" style="border-color: #F5F7FA;">
                <td class="py-3 px-4 text-sm" style="color: #666;">{{ student.student_id }}</td>
                <td class="py-3 px-4 text-sm font-medium" style="color: #333;">{{ student.name }}</td>
                <td class="py-3 px-4 text-sm" style="color: #666;">{{ student.gender }}</td>
                <td class="py-3 px-4 text-sm" style="color: #666;">{{ student.ethnicity }}</td>
                <td class="py-3 px-4 text-sm" style="color: #666;">{{ student.political_status }}</td>
                <td class="py-3 px-4 text-center text-sm font-semibold" :style="{ color: student.achievements.research_projects > 0 ? '#8FD6B0' : '#AABBC8' }">
                  {{ student.achievements.research_projects }}
                </td>
                <td class="py-3 px-4 text-center text-sm font-semibold" :style="{ color: student.achievements.patents > 0 ? '#FF9F43' : '#AABBC8' }">
                  {{ student.achievements.patents }}
                </td>
                <td class="py-3 px-4 text-center text-sm font-semibold" :style="{ color: student.achievements.papers > 0 ? '#EE5A6F' : '#AABBC8' }">
                  {{ student.achievements.papers }}
                </td>
                <td class="py-3 px-4 text-center text-sm font-semibold" :style="{ color: student.achievements.competitions > 0 ? '#A55EEA' : '#AABBC8' }">
                  {{ student.achievements.competitions }}
                </td>
                <td class="py-3 px-4 text-center">
                  <span class="inline-flex items-center justify-center w-8 h-8 rounded-full text-xs font-bold text-white" :style="{ background: student.achievements.total > 0 ? 'linear-gradient(135deg, #6ECAFF, #4DB8F0)' : '#AABBC8' }">
                    {{ student.achievements.total }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="filteredStudents.length === 0" class="text-center py-12">
          <Search class="w-12 h-12 mx-auto mb-3 opacity-20" style="color: #AABBC8;" />
          <p class="text-sm" style="color: #AABBC8;">未找到匹配的学生</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Users, Loader2, Search } from 'lucide-vue-next'
import { getClassOverview } from '../api'

const loading = ref(true)
const classList = ref([])
const selectedClass = ref('')
const searchQuery = ref('')
const data = ref({
  summary: {
    total_students: 0,
    students_with_achievements: 0,
    participation_rate: 0,
    total_achievements: {
      research_projects: 0,
      patents: 0,
      papers: 0,
      competitions: 0
    },
    total_count: 0
  },
  students: []
})

const avgAchievements = computed(() => {
  if (data.value.summary.total_students === 0) return '0.0'
  return (data.value.summary.total_count / data.value.summary.total_students).toFixed(1)
})

const filteredStudents = computed(() => {
  if (!searchQuery.value) return data.value.students
  const query = searchQuery.value.toLowerCase()
  return data.value.students.filter(s =>
    s.student_id.toLowerCase().includes(query) ||
    s.name.toLowerCase().includes(query)
  )
})

async function loadClassData() {
  loading.value = true
  try {
    const res = await getClassOverview(selectedClass.value)
    data.value = res.data
    classList.value = res.data.class_list
    selectedClass.value = res.data.current_class
  } catch (err) {
    console.error('获取班级画像失败:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadClassData()
})
</script>
