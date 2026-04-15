<template>
  <div>
    <!-- 如果没有选中某条反馈，显示列表 -->
    <div v-if="!selectedFeedback">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-800">树洞管理</h2>
        <div class="flex gap-2 text-sm">
          <span class="px-3 py-1 bg-red-100 text-red-700 rounded-full">
            紧急预警 {{ urgentCount }} 条
          </span>
        </div>
      </div>

      <!-- 筛选栏 -->
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 mb-6 flex gap-4 items-end flex-wrap">
        <div>
          <label class="block text-xs text-gray-500 mb-1">分类</label>
          <select v-model="filters.category" class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm">
            <option value="">全部</option>
            <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
          </select>
        </div>
        <div>
          <label class="block text-xs text-gray-500 mb-1">状态</label>
          <select v-model="filters.status" class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm">
            <option value="">全部</option>
            <option value="pending">待回复</option>
            <option value="replied">已回复</option>
            <option value="closed">已关闭</option>
          </select>
        </div>
        <label class="flex items-center gap-1.5 text-sm text-gray-600 cursor-pointer">
          <input type="checkbox" v-model="filters.urgent_only" class="rounded" />
          仅看预警
        </label>
        <button @click="fetchList" class="px-4 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition">
          查询
        </button>
      </div>

      <!-- 反馈卡片列表 -->
      <div class="space-y-3">
        <div v-if="loading" class="text-center text-gray-400 py-8">加载中...</div>
        <div v-else-if="feedbacks.length === 0" class="text-center text-gray-400 py-8">暂无反馈</div>

        <div
          v-for="item in feedbacks"
          :key="item.id"
          @click="openDetail(item.id)"
          class="bg-white rounded-xl p-4 shadow-sm border cursor-pointer hover:shadow-md transition"
          :class="item.is_urgent ? 'border-red-300 bg-red-50' : 'border-gray-100'"
        >
          <div class="flex justify-between items-start mb-2">
            <div class="flex items-center gap-2">
              <span v-if="item.is_urgent" class="px-2 py-0.5 text-xs rounded-full bg-red-600 text-white font-medium animate-pulse">
                紧急预警
              </span>
              <span class="px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-700">{{ item.category }}</span>
              <span class="px-2 py-0.5 text-xs rounded-full" :class="statusClass(item.status)">
                {{ statusText(item.status) }}
              </span>
            </div>
            <div class="text-right">
              <div class="text-xs text-gray-400">{{ formatTime(item.created_at) }}</div>
              <div class="text-xs mt-0.5" :class="scoreColor(item.emotion_score)">
                情绪 {{ item.emotion_score }}/10 · {{ item.emotion_label }}
              </div>
            </div>
          </div>
          <p class="text-sm text-gray-700 line-clamp-2">{{ item.content }}</p>
          <div class="text-xs text-gray-400 mt-2">{{ item.anonymous_id }}</div>
        </div>
      </div>
    </div>

    <!-- ========== 反馈详情 + 对话 ========== -->
    <div v-else>
      <button @click="selectedFeedback = null" class="text-sm text-blue-600 hover:underline mb-4 inline-block">
        &larr; 返回列表
      </button>

      <!-- 反馈卡片 -->
      <div
        class="bg-white rounded-xl p-5 shadow-sm border mb-4"
        :class="selectedFeedback.is_urgent ? 'border-red-300' : 'border-gray-100'"
      >
        <div class="flex justify-between items-start mb-3">
          <div class="flex items-center gap-2">
            <span v-if="selectedFeedback.is_urgent" class="px-2 py-0.5 text-xs rounded-full bg-red-600 text-white">紧急预警</span>
            <span class="px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-700">{{ selectedFeedback.category }}</span>
            <span class="text-xs" :class="scoreColor(selectedFeedback.emotion_score)">
              情绪评分 {{ selectedFeedback.emotion_score }}/10 · {{ selectedFeedback.emotion_label }}
            </span>
          </div>
          <span class="text-xs text-gray-400">{{ selectedFeedback.anonymous_id }}</span>
        </div>
        <p class="text-gray-700 text-sm whitespace-pre-wrap">{{ selectedFeedback.content }}</p>
        <div class="text-xs text-gray-400 mt-3">{{ formatTime(selectedFeedback.created_at) }}</div>
      </div>

      <!-- 对话列表 -->
      <div class="space-y-3 mb-4">
        <div
          v-for="reply in selectedFeedback.replies"
          :key="reply.id"
          class="rounded-xl p-4 shadow-sm border"
          :class="reply.is_counselor ? 'bg-blue-50 border-blue-200 ml-8' : 'bg-gray-50 border-gray-200 mr-8'"
        >
          <div class="flex justify-between items-center mb-2">
            <span class="text-xs font-medium" :class="reply.is_counselor ? 'text-blue-600' : 'text-gray-500'">
              {{ reply.is_counselor ? '辅导员（你）' : '学生（匿名）' }}
            </span>
            <span class="text-xs text-gray-400">{{ formatTime(reply.created_at) }}</span>
          </div>
          <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ reply.content }}</p>
        </div>
      </div>

      <!-- 回复输入 -->
      <div v-if="selectedFeedback.status !== 'closed'" class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <textarea
          v-model="adminReply"
          rows="3"
          placeholder="回复学生（学生可在树洞中看到你的回复）..."
          class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none mb-3"
        ></textarea>
        <div class="flex gap-2">
          <button
            @click="handleAdminReply"
            :disabled="replying || !adminReply.trim()"
            class="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
          >
            {{ replying ? '发送中...' : '发送回复' }}
          </button>
          <button
            @click="handleClose"
            class="px-4 py-2 border border-gray-300 text-gray-600 text-sm rounded-lg hover:bg-gray-50 transition"
          >
            关闭此反馈
          </button>
        </div>
      </div>
      <div v-else class="text-center text-sm text-gray-400 py-3 bg-gray-50 rounded-xl">该反馈已关闭</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { listFeedbacks, getFeedbackDetail, counselorReply, closeFeedback } from '../api'

const categories = ['寝室矛盾', '学业压力', '教学建议', '心理困惑', '其他']
const feedbacks = ref([])
const loading = ref(false)
const filters = ref({ category: '', status: '', urgent_only: false })
const selectedFeedback = ref(null)
const adminReply = ref('')
const replying = ref(false)

const urgentCount = computed(() => feedbacks.value.filter(f => f.is_urgent).length)

function formatTime(t) {
  return new Date(t).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function statusClass(s) {
  return { pending: 'bg-yellow-100 text-yellow-700', replied: 'bg-green-100 text-green-700', closed: 'bg-gray-100 text-gray-500' }[s] || ''
}
function statusText(s) {
  return { pending: '待回复', replied: '已回复', closed: '已关闭' }[s] || s
}
function scoreColor(score) {
  if (score <= 3) return 'text-red-600 font-semibold'
  if (score <= 5) return 'text-yellow-600'
  return 'text-green-600'
}

async function fetchList() {
  loading.value = true
  try {
    const params = {}
    if (filters.value.category) params.category = filters.value.category
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.urgent_only) params.urgent_only = true
    const { data } = await listFeedbacks(params)
    feedbacks.value = data
  } catch (err) {
    console.error('获取反馈列表失败', err)
  } finally {
    loading.value = false
  }
}

async function openDetail(id) {
  try {
    const { data } = await getFeedbackDetail(id)
    selectedFeedback.value = data
    adminReply.value = ''
  } catch (err) {
    console.error('获取详情失败', err)
  }
}

async function handleAdminReply() {
  if (!adminReply.value.trim()) return
  replying.value = true
  try {
    await counselorReply(selectedFeedback.value.id, adminReply.value)
    adminReply.value = ''
    await openDetail(selectedFeedback.value.id)
  } catch (err) {
    console.error('回复失败', err)
  } finally {
    replying.value = false
  }
}

async function handleClose() {
  try {
    await closeFeedback(selectedFeedback.value.id)
    selectedFeedback.value.status = 'closed'
    await fetchList()
  } catch (err) {
    console.error('关闭失败', err)
  }
}

onMounted(fetchList)
</script>
