<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-gray-800">管理后台</h2>
      <button
        @click="handleExport"
        :disabled="exporting"
        class="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition disabled:opacity-50"
      >
        {{ exporting ? '导出中...' : '📥 导出 Excel' }}
      </button>
    </div>

    <!-- 筛选栏 -->
    <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 mb-6 flex gap-4 items-end">
      <div>
        <label class="block text-xs text-gray-500 mb-1">学号搜索</label>
        <input
          v-model="filters.student_id"
          type="text"
          placeholder="输入学号"
          class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <div>
        <label class="block text-xs text-gray-500 mb-1">状态</label>
        <select
          v-model="filters.status"
          class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">全部</option>
          <option value="confirmed">已确认</option>
          <option value="pending">待确认</option>
          <option value="rejected">已驳回</option>
        </select>
      </div>
      <button
        @click="fetchList"
        class="px-4 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition"
      >
        查询
      </button>
    </div>

    <!-- 数据表格 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-600">
          <tr>
            <th class="px-4 py-3 text-left">学号</th>
            <th class="px-4 py-3 text-left">上报人</th>
            <th class="px-4 py-3 text-left">班级</th>
            <th class="px-4 py-3 text-left">学院</th>
            <th class="px-4 py-3 text-left">比赛/项目名称</th>
            <th class="px-4 py-3 text-left">获奖人（AI识别）</th>
            <th class="px-4 py-3 text-center">获奖等级</th>
            <th class="px-4 py-3 text-center">获奖日期</th>
            <th class="px-4 py-3 text-center">分类</th>
            <th class="px-4 py-3 text-center">状态</th>
            <th class="px-4 py-3 text-center">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-if="loading">
            <td colspan="11" class="px-4 py-8 text-center text-gray-400">加载中...</td>
          </tr>
          <tr v-else-if="achievements.length === 0">
            <td colspan="11" class="px-4 py-8 text-center text-gray-400">暂无数据</td>
          </tr>
          <tr v-for="item in achievements" :key="item.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 text-gray-500 whitespace-nowrap">{{ item.student?.student_id }}</td>
            <td class="px-4 py-3 font-medium whitespace-nowrap">{{ item.student?.name }}</td>
            <td class="px-4 py-3 whitespace-nowrap">{{ item.student?.class_name }}</td>
            <td class="px-4 py-3 whitespace-nowrap">{{ item.student?.major }}</td>
            <td class="px-4 py-3 max-w-[200px] truncate" :title="item.competition_name">
              {{ item.competition_name }}
            </td>
            <td class="px-4 py-3 max-w-[150px] truncate" :title="item.winner_name">
              {{ item.winner_name }}
            </td>
            <td class="px-4 py-3 text-center">{{ item.award_level }}</td>
            <td class="px-4 py-3 text-center">{{ item.award_date }}</td>
            <td class="px-4 py-3 text-center">
              <span class="px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-700">
                {{ item.category }}
              </span>
            </td>
            <td class="px-4 py-3 text-center">
              <span
                class="px-2 py-0.5 text-xs rounded-full"
                :class="statusClass(item.status)"
              >
                {{ statusText(item.status) }}
              </span>
            </td>
            <td class="px-4 py-3 text-center">
              <div class="flex justify-center gap-2">
                <button
                  v-if="item.status !== 'confirmed'"
                  @click="setStatus(item.id, 'confirmed')"
                  class="text-xs text-green-600 hover:underline"
                >
                  通过
                </button>
                <button
                  v-if="item.status !== 'rejected'"
                  @click="setStatus(item.id, 'rejected')"
                  class="text-xs text-red-600 hover:underline"
                >
                  驳回
                </button>
                <a
                  :href="getAssetUrl(item.certificate_image)"
                  target="_blank"
                  class="text-xs text-blue-600 hover:underline"
                >
                  查看证书
                </a>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { listAchievements, updateAchievementStatus, downloadExcel, getAssetUrl } from '../api'

const achievements = ref([])
const loading = ref(false)
const exporting = ref(false)
const filters = ref({ student_id: '', status: '' })

function statusClass(status) {
  return {
    confirmed: 'bg-green-100 text-green-700',
    pending: 'bg-yellow-100 text-yellow-700',
    rejected: 'bg-red-100 text-red-700',
  }[status] || 'bg-gray-100 text-gray-700'
}

function statusText(status) {
  return { confirmed: '已确认', pending: '待确认', rejected: '已驳回' }[status] || status
}

async function fetchList() {
  loading.value = true
  try {
    const params = {}
    if (filters.value.student_id) params.student_id = filters.value.student_id
    if (filters.value.status) params.status = filters.value.status
    const { data } = await listAchievements(params)
    achievements.value = data
  } catch (err) {
    console.error('获取列表失败', err)
  } finally {
    loading.value = false
  }
}

async function setStatus(id, status) {
  try {
    await updateAchievementStatus(id, status)
    await fetchList()
  } catch (err) {
    console.error('更新状态失败', err)
  }
}

async function handleExport() {
  exporting.value = true
  try {
    const { data } = await downloadExcel(filters.value.status || 'confirmed')
    const url = URL.createObjectURL(data)
    const a = document.createElement('a')
    a.href = url
    a.download = '科研与比赛成果汇总.xlsx'
    a.click()
    URL.revokeObjectURL(url)
  } catch (err) {
    console.error('导出失败', err)
  } finally {
    exporting.value = false
  }
}

onMounted(fetchList)
</script>
