<template>
  <div>
    <!-- ========== 列表视图 ========== -->
    <div v-if="!selectedFeedback">
      <!-- 顶部 -->
      <div class="flex justify-between items-center mb-7">
        <div class="flex items-center gap-3 relative">
          <img src="/src/assets/ui/sticker-coffee.png" alt="" class="absolute -top-3 -left-3 w-7 h-7 opacity-25 pointer-events-none" />
          <div class="w-12 h-12 rounded-2xl flex items-center justify-center" style="background: #E8F4FD;">
            <MessageSquareText class="w-5 h-5" style="color: #6ECAFF;" />
          </div>
          <div>
            <h2 class="text-lg font-bold" style="color: #1E293B;">树洞管理</h2>
            <p class="text-xs" style="color: #94A3B8;">共 {{ feedbacks.length }} 条反馈</p>
          </div>
        </div>
        <div v-if="urgentCount > 0" class="flex items-center gap-1.5 px-4 py-2 rounded-full animate-pulse" style="background: #FEF2F2;">
          <AlertTriangle class="w-3.5 h-3.5" style="color: #EF4444;" />
          <span class="text-xs font-semibold" style="color: #EF4444;">紧急预警 {{ urgentCount }} 条</span>
        </div>
      </div>

      <!-- 筛选栏 -->
      <div class="rounded-3xl p-7 mb-7 flex gap-5 items-end flex-wrap" style="background: #F0FDF4; box-shadow: 0 2px 16px rgba(16,185,129,0.06);">
        <div>
          <label class="block text-xs mb-1.5" style="color: #94A3B8;">分类</label>
          <select v-model="filters.category" class="admin-fb-input cursor-pointer">
            <option value="">全部</option>
            <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
          </select>
        </div>
        <div>
          <label class="block text-xs mb-1.5" style="color: #94A3B8;">状态</label>
          <select v-model="filters.status" class="admin-fb-input cursor-pointer">
            <option value="">全部</option>
            <option value="pending">待回复</option>
            <option value="replied">已回复</option>
            <option value="closed">已关闭</option>
          </select>
        </div>
        <label class="flex items-center gap-1.5 text-xs cursor-pointer select-none" style="color: #94A3B8;">
          <input type="checkbox" v-model="filters.urgent_only" class="rounded" style="accent-color: #10B981;" />
          仅看预警
        </label>
        <button
          @click="fetchList"
          class="px-5 py-2.5 rounded-full text-sm font-medium text-white transition-colors duration-200 cursor-pointer flex items-center gap-2"
          style="background: #10B981;"
          @mouseenter="$event.target.style.background='#059669'"
          @mouseleave="$event.target.style.background='#10B981'"
        >
          <Filter class="w-3.5 h-3.5" />
          查询
        </button>
      </div>

      <!-- 反馈卡片列表 -->
      <div class="space-y-4">
        <div v-if="loading" class="text-center py-14">
          <Loader2 class="w-6 h-6 animate-spin mx-auto mb-2" style="color: #10B981;" />
          <p class="text-xs" style="color: #94A3B8;">加载中...</p>
        </div>
        <div v-else-if="feedbacks.length === 0" class="text-center py-14">
          <Inbox class="w-8 h-8 mx-auto mb-2" style="color: #CBD5E1;" />
          <p class="text-xs" style="color: #94A3B8;">暂无反馈</p>
        </div>

        <!-- 待处理分隔 -->
        <template v-if="!loading && sortedFeedbacks.some(f => f.status === 'pending') && sortedFeedbacks.some(f => f.status !== 'pending')">
          <div
            v-for="item in sortedFeedbacks"
            :key="item.id"
          >
            <!-- 分隔线：在第一个已处理条目前插入 -->
            <div v-if="item === sortedFeedbacks.find(f => f.status !== 'pending')" class="flex items-center gap-3 py-2 mb-4">
              <div class="flex-1 h-px" style="background: #E2E8F0;"></div>
              <span class="text-[10px] shrink-0" style="color: #94A3B8;">已处理</span>
              <div class="flex-1 h-px" style="background: #E2E8F0;"></div>
            </div>

            <div
              @click="openDetail(item.id)"
              class="bg-white rounded-3xl p-6 cursor-pointer transition-all duration-200 mb-4"
              :class="item.status !== 'pending' ? 'opacity-50' : ''"
              :style="item.is_urgent && item.status === 'pending'
                ? 'background: #FEF2F2; box-shadow: 0 2px 16px rgba(224,112,112,0.08);'
                : 'box-shadow: 0 2px 16px rgba(125,175,206,0.06);'"
              @mouseenter="$event.currentTarget.style.boxShadow='0 4px 24px rgba(125,175,206,0.12)'"
              @mouseleave="$event.currentTarget.style.boxShadow=(item.is_urgent && item.status === 'pending') ? '0 2px 16px rgba(224,112,112,0.08)' : '0 2px 16px rgba(125,175,206,0.06)'"
            >
              <div class="flex justify-between items-start mb-3">
                <div class="flex items-center gap-2 flex-wrap">
                  <span v-if="item.is_urgent && item.status === 'pending'" class="px-3 py-1 text-[10px] font-semibold rounded-full text-white flex items-center gap-1" style="background: #EF4444;">
                    <AlertTriangle class="w-3 h-3" />
                    紧急
                  </span>
                  <span class="px-3 py-1 text-[10px] font-medium rounded-full" :style="categoryStyle(item.category)">{{ item.category }}</span>
                  <span class="px-3 py-1 text-[10px] font-medium rounded-full" :style="statusStyle(item.status)">{{ statusText(item.status) }}</span>
                </div>
                <div class="text-right shrink-0 ml-3">
                  <div class="text-[10px]" style="color: #94A3B8;">{{ formatTime(item.created_at) }}</div>
                  <div class="text-[10px] mt-0.5 font-medium" :style="scoreStyle(item.emotion_score)">
                    情绪 {{ item.emotion_score }}/10 · {{ item.emotion_label }}
                  </div>
                </div>
              </div>
              <p class="text-sm line-clamp-2 mb-2" :style="item.status !== 'pending' ? 'color: #94A3B8; text-decoration: line-through;' : 'color: #475569;'">{{ item.content }}</p>
              <div class="text-[10px]" style="color: #94A3B8;">{{ item.anonymous_id }}</div>
            </div>
          </div>
        </template>

        <!-- 全部同一状态时不需要分隔 -->
        <template v-else-if="!loading">
          <div
            v-for="item in sortedFeedbacks"
            :key="item.id"
            @click="openDetail(item.id)"
            class="bg-white rounded-3xl p-6 cursor-pointer transition-all duration-200"
            :class="item.status !== 'pending' ? 'opacity-50' : ''"
            :style="item.is_urgent && item.status === 'pending'
              ? 'background: #FEF2F2; box-shadow: 0 2px 16px rgba(224,112,112,0.08);'
              : 'box-shadow: 0 2px 16px rgba(125,175,206,0.06);'"
            @mouseenter="$event.currentTarget.style.boxShadow='0 4px 24px rgba(125,175,206,0.12)'"
            @mouseleave="$event.currentTarget.style.boxShadow=(item.is_urgent && item.status === 'pending') ? '0 2px 16px rgba(224,112,112,0.08)' : '0 2px 16px rgba(125,175,206,0.06)'"
          >
            <div class="flex justify-between items-start mb-3">
              <div class="flex items-center gap-2 flex-wrap">
                <span v-if="item.is_urgent && item.status === 'pending'" class="px-3 py-1 text-[10px] font-semibold rounded-full text-white flex items-center gap-1" style="background: #EF4444;">
                  <AlertTriangle class="w-3 h-3" />
                  紧急
                </span>
                <span class="px-3 py-1 text-[10px] font-medium rounded-full" :style="categoryStyle(item.category)">{{ item.category }}</span>
                <span class="px-3 py-1 text-[10px] font-medium rounded-full" :style="statusStyle(item.status)">{{ statusText(item.status) }}</span>
              </div>
              <div class="text-right shrink-0 ml-3">
                <div class="text-[10px]" style="color: #94A3B8;">{{ formatTime(item.created_at) }}</div>
                <div class="text-[10px] mt-0.5 font-medium" :style="scoreStyle(item.emotion_score)">
                  情绪 {{ item.emotion_score }}/10 · {{ item.emotion_label }}
                </div>
              </div>
            </div>
            <p class="text-sm line-clamp-2 mb-2" :style="item.status !== 'pending' ? 'color: #94A3B8; text-decoration: line-through;' : 'color: #475569;'">{{ item.content }}</p>
            <div class="text-[10px]" style="color: #94A3B8;">{{ item.anonymous_id }}</div>
          </div>
        </template>
      </div>
    </div>

    <!-- ========== 反馈详情 + 对话 ========== -->
    <div v-else>
      <button
        @click="selectedFeedback = null"
        class="text-xs font-medium mb-5 inline-flex items-center gap-1 transition-colors duration-200 cursor-pointer"
        style="color: #10B981;"
        @mouseenter="$event.target.style.color='#059669'"
        @mouseleave="$event.target.style.color='#10B981'"
      >
        <ArrowLeft class="w-3.5 h-3.5" />
        返回列表
      </button>

      <!-- 反馈卡片 -->
      <div
        class="bg-white rounded-3xl p-7 mb-5"
        :style="selectedFeedback.is_urgent
          ? 'background: #FEF2F2; box-shadow: 0 2px 16px rgba(224,112,112,0.08);'
          : 'box-shadow: 0 2px 16px rgba(125,175,206,0.06);'"
      >
        <div class="flex justify-between items-start mb-4">
          <div class="flex items-center gap-2 flex-wrap">
            <span v-if="selectedFeedback.is_urgent" class="px-3 py-1 text-[10px] font-semibold rounded-full text-white flex items-center gap-1" style="background: #EF4444;">
              <AlertTriangle class="w-3 h-3" />
              紧急预警
            </span>
            <span class="px-3 py-1 text-[10px] font-medium rounded-full" style="background: #ECFDF5; color: #10B981;">{{ selectedFeedback.category }}</span>
            <span class="text-[10px] font-medium" :style="scoreStyle(selectedFeedback.emotion_score)">
              情绪评分 {{ selectedFeedback.emotion_score }}/10 · {{ selectedFeedback.emotion_label }}
            </span>
          </div>
          <span class="text-[10px]" style="color: #94A3B8;">{{ selectedFeedback.anonymous_id }}</span>
        </div>
        <p class="text-sm whitespace-pre-wrap mb-3" style="color: #475569;">{{ selectedFeedback.content }}</p>
        <div class="text-[10px]" style="color: #94A3B8;">{{ formatTime(selectedFeedback.created_at) }}</div>
      </div>

      <!-- 对话列表 -->
      <div class="space-y-4 mb-5">
        <div
          v-for="reply in selectedFeedback.replies"
          :key="reply.id"
          class="rounded-2xl p-5"
          :style="reply.is_counselor
            ? 'background: #ECFDF5; margin-left: 32px; box-shadow: 0 2px 12px rgba(125,206,160,0.08);'
            : 'background: #F1F5F9; margin-right: 32px;'"
        >
          <div class="flex justify-between items-center mb-2">
            <span class="text-[10px] font-medium flex items-center gap-1"
              :style="reply.is_counselor ? 'color: #10B981;' : 'color: #94A3B8;'"
            >
              <UserCircle class="w-3.5 h-3.5" />
              {{ reply.is_counselor ? '辅导员（你）' : '学生（匿名）' }}
            </span>
            <span class="text-[10px]" style="color: #94A3B8;">{{ formatTime(reply.created_at) }}</span>
          </div>
          <p class="text-sm whitespace-pre-wrap" style="color: #475569;">{{ reply.content }}</p>
        </div>
      </div>

      <!-- 回复输入 -->
      <div v-if="selectedFeedback.status !== 'closed'" class="bg-white rounded-3xl p-7" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
        <textarea
          v-model="adminReply"
          rows="3"
          placeholder="回复学生（学生可在树洞中看到你的回复）..."
          class="admin-fb-textarea mb-4"
        ></textarea>
        <div class="flex gap-3">
          <button
            @click="handleAdminReply"
            :disabled="replying || !adminReply.trim()"
            class="px-6 py-2.5 rounded-full text-sm font-medium text-white transition-colors duration-200 disabled:opacity-50 cursor-pointer flex items-center gap-2"
            style="background: #10B981;"
            @mouseenter="!replying && ($event.target.style.background='#059669')"
            @mouseleave="$event.target.style.background='#10B981'"
          >
            <Loader2 v-if="replying" class="w-4 h-4 animate-spin" />
            <Send v-else class="w-4 h-4" />
            {{ replying ? '发送中...' : '发送回复' }}
          </button>
          <button
            @click="handleClose"
            class="px-5 py-2.5 rounded-full text-sm transition-colors duration-200 cursor-pointer flex items-center gap-2"
            style="background: #F1F5F9; color: #94A3B8;"
            @mouseenter="$event.target.style.background='#E2E8F0'"
            @mouseleave="$event.target.style.background='#F1F5F9'"
          >
            <XCircle class="w-4 h-4" />
            关闭此反馈
          </button>
        </div>
      </div>
      <div v-else class="text-center py-4 rounded-2xl text-xs" style="background: #F1F5F9; color: #94A3B8;">该反馈已关闭</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { MessageSquareText, AlertTriangle, Filter, Loader2, Inbox, ArrowLeft, UserCircle, Send, XCircle } from 'lucide-vue-next'
import { listFeedbacks, getFeedbackDetail, counselorReply, closeFeedback } from '../api'

const categories = ['寝室矛盾', '学业压力', '教学建议', '心理困惑', '其他']
const feedbacks = ref([])
const loading = ref(false)
const filters = ref({ category: '', status: '', urgent_only: false })
const selectedFeedback = ref(null)
const adminReply = ref('')
const replying = ref(false)

const urgentCount = computed(() => feedbacks.value.filter(f => f.is_urgent && f.status === 'pending').length)

const sortedFeedbacks = computed(() => {
  const pending = feedbacks.value.filter(f => f.status === 'pending')
  const handled = feedbacks.value.filter(f => f.status !== 'pending')
  return [...pending, ...handled]
})

function formatTime(t) {
  return new Date(t).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function statusStyle(s) {
  const styles = {
    pending: 'background: #FFFBEB; color: #B45309;',
    replied: 'background: #ECFDF5; color: #10B981;',
    closed: 'background: #F1F5F9; color: #94A3B8;',
  }
  return styles[s] || ''
}

function statusText(s) {
  return { pending: '待回复', replied: '已回复', closed: '已关闭' }[s] || s
}

function scoreStyle(score) {
  if (score <= 3) return 'color: #EF4444; font-weight: 600;'
  if (score <= 5) return 'color: #F59E0B;'
  return 'color: #10B981;'
}

function categoryStyle(cat) {
  const map = {
    '寝室矛盾': 'background: #ECFDF5; color: #10B981;',
    '学业压力': 'background: #EFF6FF; color: #3B82F6;',
    '教学建议': 'background: #FFFBEB; color: #F59E0B;',
    '心理困惑': 'background: #FDF2F8; color: #EC4899;',
    '其他': 'background: #F3F4F6; color: #6B7280;',
  }
  return map[cat] || 'background: #F3F4F6; color: #6B7280;'
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

<style scoped>
@reference "../style.css";

.admin-fb-input {
  @apply rounded-2xl px-4 py-3 text-sm
         transition-all duration-200
         focus:outline-none focus:ring-2 focus:border-transparent;
  background: #F1F5F9;
  color: #1E293B;
  --tw-ring-color: rgba(125, 175, 206, 0.4);
}
.admin-fb-textarea {
  @apply w-full rounded-2xl px-4 py-3 text-sm resize-none
         transition-all duration-200
         focus:outline-none focus:ring-2 focus:border-transparent;
  background: #F1F5F9;
  color: #1E293B;
  --tw-ring-color: rgba(125, 175, 206, 0.4);
}
.admin-fb-textarea::placeholder {
  color: #94A3B8;
}
</style>
