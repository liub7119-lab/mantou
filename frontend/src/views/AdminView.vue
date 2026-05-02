<template>
  <div>
    <!-- 顶部操作栏 -->
    <div class="flex justify-between items-center mb-7">
      <div class="flex items-center gap-3 relative">
        <img src="/src/assets/ui/sticker-medal.png" alt="" class="absolute -top-3 -left-3 w-7 h-7 opacity-25 pointer-events-none" />
        <div class="w-12 h-12 rounded-2xl flex items-center justify-center" style="background: #E8F4FD;">
          <Trophy class="w-5 h-5" style="color: #6ECAFF;" />
        </div>
        <div>
          <h2 class="text-lg font-bold" style="color: #1E293B;">成果管理</h2>
          <p class="text-xs" style="color: #94A3B8;">审核、导出学生成果数据</p>
        </div>
      </div>
      <button
        @click="handleExport"
        :disabled="exporting"
        class="px-5 py-2.5 rounded-full text-sm font-medium text-white transition-colors duration-200 disabled:opacity-50 cursor-pointer flex items-center gap-2"
        style="background: #10B981;"
        @mouseenter="!exporting && ($event.target.style.background='#059669')"
        @mouseleave="$event.target.style.background='#10B981'"
      >
        <Loader2 v-if="exporting" class="w-4 h-4 animate-spin" />
        <Download v-else class="w-4 h-4" />
        {{ exporting ? '导出中...' : '导出 Excel' }}
      </button>
    </div>

    <!-- 类别 Tab -->
    <div class="bg-white rounded-3xl p-2 mb-7 flex gap-2" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
      <button
        v-for="cat in categories" :key="cat.name"
        @click="switchCategory(cat.name)"
        class="flex-1 py-3 px-4 rounded-2xl text-sm font-medium transition-all duration-200 cursor-pointer flex items-center justify-center gap-2"
        :style="activeCategory === cat.name
          ? `background: ${cat.color}; color: white;`
          : 'background: transparent; color: #94A3B8;'"
        @mouseenter="activeCategory !== cat.name && ($event.currentTarget.style.background = '#F1F5F9')"
        @mouseleave="activeCategory !== cat.name && ($event.currentTarget.style.background = 'transparent')"
      >
        <component :is="cat.icon" class="w-4 h-4" />
        {{ cat.name }}
        <span v-if="categoryCounts[cat.name]" class="text-[10px] px-2 py-0.5 rounded-full"
          :style="activeCategory === cat.name ? 'background: rgba(255,255,255,0.25);' : `background: ${cat.bg}; color: ${cat.color};`"
        >{{ categoryCounts[cat.name] }}</span>
      </button>
    </div>

    <!-- KPI 统计卡片 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-5 mb-7">
      <div class="rounded-3xl p-5" style="background: linear-gradient(135deg, #ECFDF5, #D1FAE5); box-shadow: 0 2px 16px rgba(16,185,129,0.08);">
        <div class="flex justify-between items-start mb-4">
          <div class="w-12 h-12 rounded-2xl flex items-center justify-center" style="background: rgba(255,255,255,0.7);">
            <BarChart3 class="w-5 h-5" style="color: #10B981;" />
          </div>
        </div>
        <p class="text-2xl font-bold mb-0.5" style="color: #1E293B;">{{ achievements.length }}</p>
        <p class="text-xs" style="color: #059669;">全部{{ activeCategory }}</p>
      </div>
      <div class="rounded-3xl p-5" style="background: linear-gradient(135deg, #FFFBEB, #FEF3C7); box-shadow: 0 2px 16px rgba(245,158,11,0.08);">
        <div class="flex justify-between items-start mb-4">
          <div class="w-12 h-12 rounded-2xl flex items-center justify-center" style="background: rgba(255,255,255,0.7);">
            <Clock class="w-5 h-5" style="color: #F59E0B;" />
          </div>
        </div>
        <p class="text-2xl font-bold mb-0.5" style="color: #1E293B;">{{ countByStatus('pending') }}</p>
        <p class="text-xs" style="color: #B45309;">待审核</p>
      </div>
      <div class="rounded-3xl p-5" style="background: linear-gradient(135deg, #F0FDFA, #CCFBF1); box-shadow: 0 2px 16px rgba(20,184,166,0.08);">
        <div class="flex justify-between items-start mb-4">
          <div class="w-12 h-12 rounded-2xl flex items-center justify-center" style="background: rgba(255,255,255,0.7);">
            <CircleCheckBig class="w-5 h-5" style="color: #14B8A6;" />
          </div>
        </div>
        <p class="text-2xl font-bold mb-0.5" style="color: #1E293B;">{{ countByStatus('confirmed') }}</p>
        <p class="text-xs" style="color: #0D9488;">已通过</p>
      </div>
      <div class="rounded-3xl p-5" style="background: linear-gradient(135deg, #FEF2F2, #FECACA); box-shadow: 0 2px 16px rgba(239,68,68,0.08);">
        <div class="flex justify-between items-start mb-4">
          <div class="w-12 h-12 rounded-2xl flex items-center justify-center" style="background: rgba(255,255,255,0.7);">
            <XCircle class="w-5 h-5" style="color: #EF4444;" />
          </div>
        </div>
        <p class="text-2xl font-bold mb-0.5" style="color: #1E293B;">{{ countByStatus('rejected') }}</p>
        <p class="text-xs" style="color: #DC2626;">已驳回</p>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="rounded-3xl p-5 mb-7 flex items-end gap-4" style="background: #F0FDF4; box-shadow: 0 2px 16px rgba(16,185,129,0.06);">
      <div class="flex-1">
        <label class="block text-xs mb-1.5" style="color: #94A3B8;">学号搜索</label>
        <input v-model="filters.student_id" type="text" placeholder="输入学号" class="admin-input w-full" />
      </div>
      <div class="w-36">
        <label class="block text-xs mb-1.5" style="color: #94A3B8;">状态</label>
        <select v-model="filters.status" class="admin-input w-full cursor-pointer">
          <option value="">全部</option>
          <option value="confirmed">已通过</option>
          <option value="pending">待审核</option>
          <option value="rejected">已驳回</option>
        </select>
      </div>
      <button
        @click="fetchList"
        class="px-6 py-3 rounded-2xl text-sm font-medium text-white transition-colors duration-200 cursor-pointer flex items-center gap-2"
        style="background: #10B981;"
        @mouseenter="$event.target.style.background='#059669'"
        @mouseleave="$event.target.style.background='#10B981'"
      >
        <Filter class="w-3.5 h-3.5" />
        查询
      </button>
    </div>

    <!-- 数据表格 -->
    <div class="bg-white rounded-3xl overflow-hidden" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr style="background: #ECFDF5;">
              <th v-for="col in currentColumns" :key="col.key" class="px-5 py-4 text-left text-xs font-semibold" style="color: #059669;">{{ col.label }}</th>
              <th class="px-5 py-4 text-center text-xs font-semibold" style="color: #059669;">状态</th>
              <th class="px-5 py-4 text-center text-xs font-semibold" style="color: #059669;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td :colspan="currentColumns.length + 2" class="px-5 py-14 text-center">
                <Loader2 class="w-6 h-6 animate-spin mx-auto mb-2" style="color: #10B981;" />
                <p class="text-xs" style="color: #94A3B8;">加载中...</p>
              </td>
            </tr>
            <tr v-else-if="achievements.length === 0">
              <td :colspan="currentColumns.length + 2" class="px-5 py-14 text-center">
                <FileX class="w-8 h-8 mx-auto mb-2" style="color: #CBD5E1;" />
                <p class="text-xs" style="color: #94A3B8;">暂无数据</p>
              </td>
            </tr>
            <tr
              v-for="item in achievements" :key="item.id"
              class="transition-colors duration-150"
              style="border-top: 1px solid #F1F5F9;"
              @mouseenter="$event.currentTarget.style.background='#F1F5F9'"
              @mouseleave="$event.currentTarget.style.background='transparent'"
            >
              <td v-for="col in currentColumns" :key="col.key"
                class="px-5 py-4 text-xs"
                :class="col.truncate ? 'max-w-[200px] truncate' : 'whitespace-nowrap'"
                :style="col.bold ? 'color: #1E293B; font-weight: 500;' : 'color: #94A3B8;'"
                :title="col.truncate ? getCellValue(item, col) : undefined"
              >{{ getCellValue(item, col) }}</td>
              <td class="px-5 py-4 text-center">
                <span class="px-3 py-1 text-[10px] font-medium rounded-full" :style="statusStyle(item.status)">{{ statusText(item.status) }}</span>
              </td>
              <td class="px-5 py-4 text-center">
                <div class="flex justify-center gap-2">
                  <button
                    v-if="item.status === 'pending'"
                    @click="setStatus(item.id, 'confirmed')"
                    class="px-4 py-1.5 rounded-full text-xs font-medium text-white transition-colors duration-200 cursor-pointer"
                    style="background: #10B981;"
                    @mouseenter="$event.target.style.background='#5AB882'"
                    @mouseleave="$event.target.style.background='#10B981'"
                  >审核通过</button>
                  <button
                    v-if="item.status !== 'rejected'"
                    @click="setStatus(item.id, 'rejected')"
                    class="px-4 py-1.5 rounded-full text-xs font-medium transition-colors duration-200 cursor-pointer"
                    style="background: #FEF2F2; color: #EF4444;"
                    @mouseenter="$event.target.style.background='#FDE8E8'"
                    @mouseleave="$event.target.style.background='#FEF2F2'"
                  >驳回</button>
                  <a
                    v-if="item.certificate_image"
                    :href="getAssetUrl(item.certificate_image)"
                    target="_blank"
                    class="px-4 py-1.5 rounded-full text-xs font-medium transition-colors duration-200 cursor-pointer"
                    style="background: #F0FDF4; color: #34D399;"
                    @mouseenter="$event.target.style.background='#EDEAF7'"
                    @mouseleave="$event.target.style.background='#F0FDF4'"
                  >证书</a>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Trophy, Download, Loader2, Filter, FileX, BarChart3, Clock, CircleCheckBig, XCircle, FlaskConical, Copyright, GraduationCap } from 'lucide-vue-next'
import { listAchievements, updateAchievementStatus, downloadExcel, getAssetUrl } from '../api'

const categories = [
  { name: '科研项目', color: '#059669', bg: '#ECFDF5', icon: FlaskConical },
  { name: '专利软著', color: '#10B981', bg: '#D1FAE5', icon: Copyright },
  { name: '学术论文', color: '#047857', bg: '#A7F3D0', icon: GraduationCap },
  { name: '学科竞赛', color: '#34D399', bg: '#ECFDF5', icon: Trophy },
]

const COLUMNS = {
  '科研项目': [
    { key: 'student.student_id', label: '学号' },
    { key: 'student.name', label: '学生姓名', bold: true },
    { key: 'student.major', label: '所在学院' },
    { key: 'student.class_name', label: '年级专业班级' },
    { key: 'project_number', label: '立项编号' },
    { key: 'project_level', label: '项目层级' },
    { key: 'project_name', label: '项目名称', truncate: true, bold: true },
    { key: 'student_rank', label: '学生排名' },
    { key: 'project_year', label: '立项年度' },
    { key: 'project_source', label: '项目来源' },
    { key: 'project_leader', label: '项目负责人' },
    { key: 'leader_id', label: '工号' },
    { key: 'counselor_name', label: '辅导员姓名' },
  ],
  '专利软著': [
    { key: 'student.student_id', label: '学号' },
    { key: 'student.name', label: '学生姓名', bold: true },
    { key: 'student.major', label: '学院' },
    { key: 'student.class_name', label: '年级专业班级' },
    { key: 'name', label: '名称', truncate: true, bold: true },
    { key: 'patent_type', label: '类别' },
    { key: 'authorization_number', label: '授权号' },
    { key: 'approval_date', label: '获批时间' },
    { key: 'inventor_rank', label: '发明人排名' },
    { key: 'counselor_name', label: '辅导员姓名' },
  ],
  '学术论文': [
    { key: 'student.student_id', label: '学号' },
    { key: 'student.name', label: '学生姓名', bold: true },
    { key: 'student.major', label: '所在学院' },
    { key: 'student.class_name', label: '年级专业班级' },
    { key: 'paper_name', label: '论文名称', truncate: true, bold: true },
    { key: 'journal_name', label: '发表期刊', truncate: true },
    { key: 'author_rank', label: '作者排名' },
    { key: 'publish_date', label: '发表时间' },
    { key: 'indexing', label: '收录情况' },
    { key: 'paper_link', label: '论文链接', truncate: true },
    { key: 'counselor_name', label: '辅导员姓名' },
  ],
  '学科竞赛': [
    { key: 'student.student_id', label: '学号' },
    { key: 'student.name', label: '学生姓名', bold: true },
    { key: 'student.major', label: '所在学院' },
    { key: 'competition_name', label: '赛事名称', truncate: true, bold: true },
    { key: 'track', label: '赛道' },
    { key: 'organizer', label: '赛事主办方' },
    { key: 'project_name', label: '项目名称', truncate: true },
    { key: 'award_name', label: '奖项名称' },
    { key: 'team_leader', label: '项目负责人' },
    { key: 'phone', label: '联系电话' },
    { key: 'advisor', label: '指导老师' },
    { key: 'team_members', label: '学生成员', truncate: true },
    { key: 'award_date', label: '获奖时间' },
    { key: 'remark', label: '备注' },
  ],
}

const activeCategory = ref('科研项目')
const achievements = ref([])
const loading = ref(false)
const exporting = ref(false)
const filters = ref({ student_id: '', status: '' })
const categoryCounts = ref({})

const currentColumns = computed(() => COLUMNS[activeCategory.value] || [])

function getCellValue(item, col) {
  const keys = col.key.split('.')
  let val = item
  for (const k of keys) {
    val = val?.[k]
  }
  return val || ''
}

function countByStatus(status) {
  return achievements.value.filter(a => a.status === status).length
}

function statusStyle(status) {
  const styles = {
    confirmed: 'background: #ECFDF5; color: #10B981;',
    pending: 'background: #FFFBEB; color: #B45309;',
    rejected: 'background: #FEF2F2; color: #EF4444;',
  }
  return styles[status] || 'background: #F1F5F9; color: #94A3B8;'
}

function statusText(status) {
  return { confirmed: '已通过', pending: '待审核', rejected: '已驳回' }[status] || status
}

function switchCategory(cat) {
  activeCategory.value = cat
  fetchList()
}

async function fetchList() {
  loading.value = true
  try {
    const params = {}
    if (filters.value.student_id) params.student_id = filters.value.student_id
    if (filters.value.status) params.status = filters.value.status
    const { data } = await listAchievements(activeCategory.value, params)
    achievements.value = data
  } catch (err) {
    console.error('获取列表失败', err)
  } finally {
    loading.value = false
  }
}

async function fetchAllCounts() {
  for (const cat of categories) {
    try {
      const { data } = await listAchievements(cat.name, {})
      categoryCounts.value[cat.name] = data.length
    } catch {}
  }
}

async function setStatus(id, status) {
  try {
    await updateAchievementStatus(activeCategory.value, id, status)
    await fetchList()
  } catch (err) {
    console.error('更新状态失败', err)
  }
}

async function handleExport() {
  exporting.value = true
  try {
    const { data } = await downloadExcel(activeCategory.value, filters.value.status || 'confirmed')
    const url = URL.createObjectURL(data)
    const a = document.createElement('a')
    a.href = url
    const filenames = {
      '科研项目': '学生科研项目情况统计表.xlsx',
      '专利软著': '学生专利软著授权情况统计表.xlsx',
      '学术论文': '学生学术论文发表情况统计表.xlsx',
      '学科竞赛': '学科竞赛获奖情况统计表.xlsx',
    }
    a.download = filenames[activeCategory.value] || '成果汇总.xlsx'
    a.click()
    URL.revokeObjectURL(url)
  } catch (err) {
    console.error('导出失败', err)
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  fetchList()
  fetchAllCounts()
})
</script>

<style scoped>
@reference "../style.css";

.admin-input {
  @apply rounded-2xl px-4 py-3 text-sm
         transition-all duration-200
         focus:outline-none focus:ring-2 focus:border-transparent;
  background: #F1F5F9;
  color: #1E293B;
  --tw-ring-color: rgba(125, 175, 206, 0.4);
}
</style>
