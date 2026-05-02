<template>
  <div>
    <div class="flex items-start justify-between mb-7">
      <div class="flex items-center gap-3 relative">
        <img src="/src/assets/ui/sticker-coffee.png" alt="" class="absolute -top-3 -left-3 w-7 h-7 opacity-25 pointer-events-none" />
        <div class="w-12 h-12 rounded-2xl flex items-center justify-center" style="background: #E8F4FD;">
          <MessageCircle class="w-5 h-5" style="color: #6ECAFF;" />
        </div>
        <div>
          <h2 class="text-lg font-bold" style="color: #1E293B;">匿名树洞</h2>
          <p class="text-xs" style="color: #94A3B8;">安全匿名，有话直说</p>
        </div>
      </div>
    </div>

    <!-- Tab 切换 -->
    <div class="flex gap-2 mb-7">
      <button
        @click="tab = 'submit'"
        class="px-5 py-2.5 text-sm font-medium rounded-full transition-all duration-200 cursor-pointer flex items-center gap-2"
        :style="tab === 'submit'
          ? 'background: #10B981; color: white;'
          : 'background: #F1F5F9; color: #94A3B8;'"
        @mouseenter="tab !== 'submit' && ($event.target.style.background='#E2E8F0')"
        @mouseleave="tab !== 'submit' && ($event.target.style.background='#F1F5F9')"
      >
        <Send class="w-4 h-4" />
        匿名投递
      </button>
      <button
        @click="tab = 'check'"
        class="px-5 py-2.5 text-sm font-medium rounded-full transition-all duration-200 cursor-pointer flex items-center gap-2"
        :style="tab === 'check'
          ? 'background: #10B981; color: white;'
          : 'background: #F1F5F9; color: #94A3B8;'"
        @mouseenter="tab !== 'check' && ($event.target.style.background='#E2E8F0')"
        @mouseleave="tab !== 'check' && ($event.target.style.background='#F1F5F9')"
      >
        <Eye class="w-4 h-4" />
        查看回复
      </button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-7">
      <!-- 左栏：主区域 -->
      <div class="lg:col-span-2">
        <!-- ========== 投递面板 ========== -->
        <template v-if="tab === 'submit'">
          <div class="bg-white rounded-3xl p-7 mb-7" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
            <!-- 匿名保障 -->
            <div class="flex items-center gap-2 mb-5 px-4 py-3 rounded-2xl" style="background: #ECFDF5;">
              <ShieldCheck class="w-4 h-4 shrink-0" style="color: #10B981;" />
              <p class="text-xs" style="color: #059669;">你的反馈完全匿名，辅导员无法看到你的身份信息。</p>
            </div>

            <!-- 分类选择 -->
            <div class="mb-5">
              <label class="block text-xs mb-2" style="color: #94A3B8;">选择分类</label>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="cat in categories"
                  :key="cat.value"
                  @click="form.category = cat.value"
                  class="px-4 py-2 text-xs rounded-full transition-all duration-200 cursor-pointer flex items-center gap-1.5"
                  :style="form.category === cat.value
                    ? `background: ${cat.color}; color: white;`
                    : `background: ${cat.bg}; color: ${cat.color};`"
                  @mouseenter="form.category !== cat.value && ($event.currentTarget.style.background='#E2E8F0')"
                  @mouseleave="form.category !== cat.value && ($event.currentTarget.style.background=cat.bg)"
                >
                  <component :is="cat.icon" class="w-3 h-3" />
                  {{ cat.value }}
                </button>
              </div>
            </div>

            <!-- 内容输入 -->
            <div class="mb-5">
              <label class="block text-xs mb-1.5" style="color: #94A3B8;">说说你的想法</label>
              <textarea
                v-model="form.content"
                rows="6"
                maxlength="2000"
                placeholder="可以聊聊你的困扰、建议或者任何想说的话..."
                class="feedback-textarea"
              ></textarea>
              <div class="flex justify-between mt-1.5">
                <p class="text-[10px]" style="color: #94A3B8;">支持换行，最多 2000 字</p>
                <p class="text-[10px]" :style="form.content.length > 1800 ? 'color: #EF4444;' : 'color: #94A3B8;'">{{ form.content.length }} / 2000</p>
              </div>
            </div>

            <!-- 提交按钮 -->
            <button
              @click="handleSubmit"
              :disabled="submitting || !form.content.trim()"
              class="w-full py-3 rounded-full text-sm font-medium text-white transition-colors duration-200 disabled:opacity-50 cursor-pointer flex items-center justify-center gap-2"
              style="background: #10B981;"
              @mouseenter="!submitting && ($event.target.style.background='#059669')"
              @mouseleave="$event.target.style.background='#10B981'"
            >
              <Loader2 v-if="submitting" class="w-4 h-4 animate-spin" />
              <Send v-else class="w-4 h-4" />
              {{ submitting ? '提交中...' : '提交' }}
            </button>
          </div>

          <!-- 提交成功 -->
          <div v-if="submitResult" class="bg-white rounded-3xl p-7" style="box-shadow: 0 2px 16px rgba(125,206,160,0.1);">
            <div class="text-center mb-5">
              <div class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4" style="background: #ECFDF5;">
                <CircleCheckBig class="w-8 h-8" style="color: #10B981;" />
              </div>
              <p class="text-base font-semibold mb-1" style="color: #1E293B;">投递成功！</p>
              <p class="text-xs" style="color: #94A3B8;">请牢记你的专属昵称，用于查看辅导员的回复</p>
            </div>

            <div class="rounded-2xl px-5 py-4 mb-5 text-center" style="background: #ECFDF5;">
              <p class="text-[10px] mb-1" style="color: #94A3B8;">你的专属昵称</p>
              <span class="text-lg font-bold" style="color: #1E293B;">{{ submitResult.anonymous_id }}</span>
            </div>

            <div class="flex items-start gap-2 px-4 py-3 rounded-2xl" style="background: #FFFBEB;">
              <TriangleAlert class="w-3.5 h-3.5 shrink-0 mt-0.5" style="color: #F59E0B;" />
              <p class="text-[11px]" style="color: #B45309;">请截图或牢记这个昵称哦，丢失后无法找回。切换到「查看回复」输入昵称即可查看对话。</p>
            </div>
          </div>
        </template>

        <!-- ========== 查看回复面板 ========== -->
        <template v-if="tab === 'check'">
          <div class="bg-white rounded-3xl p-7 mb-7" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
            <label class="block text-xs mb-2" style="color: #94A3B8;">输入你的专属昵称</label>
            <div class="flex gap-3">
              <input
                v-model="checkId"
                type="text"
                placeholder="如：树洞·冒泡的小水獭07"
                class="feedback-input flex-1"
                @keyup.enter="handleCheck"
              />
              <button
                @click="handleCheck"
                :disabled="checking"
                class="px-5 py-2.5 rounded-full text-sm font-medium text-white transition-colors duration-200 disabled:opacity-50 cursor-pointer flex items-center gap-2"
                style="background: #10B981;"
                @mouseenter="!checking && ($event.target.style.background='#059669')"
                @mouseleave="$event.target.style.background='#10B981'"
              >
                <Loader2 v-if="checking" class="w-4 h-4 animate-spin" />
                <Search v-else class="w-4 h-4" />
                {{ checking ? '查询中...' : '查看' }}
              </button>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-if="!feedbackDetail && !errorMsg" class="bg-white rounded-3xl p-10 text-center" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
            <MessageCircle class="w-10 h-10 mx-auto mb-3" style="color: #CBD5E1;" />
            <p class="text-sm font-medium mb-1" style="color: #1E293B;">输入昵称查看回复</p>
            <p class="text-xs" style="color: #94A3B8;">专属昵称在提交反馈成功后获得</p>
          </div>

          <!-- 反馈详情 + 对话 -->
          <div v-if="feedbackDetail" class="space-y-4">
            <!-- 原始反馈 -->
            <div class="bg-white rounded-3xl p-7" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
              <div class="flex justify-between items-start mb-4">
                <div class="flex items-center gap-2">
                  <span class="px-3 py-1 text-[10px] font-medium rounded-full" :style="categoryStyle(feedbackDetail.category)">{{ feedbackDetail.category }}</span>
                  <span class="px-3 py-1 text-[10px] font-medium rounded-full" :style="fbStatusStyle(feedbackDetail.status)">{{ fbStatusText(feedbackDetail.status) }}</span>
                </div>
                <span class="text-[10px]" style="color: #94A3B8;">{{ formatTime(feedbackDetail.created_at) }}</span>
              </div>
              <p class="text-sm whitespace-pre-wrap" style="color: #475569;">{{ feedbackDetail.content }}</p>
            </div>

            <!-- 对话列表 -->
            <div v-for="reply in feedbackDetail.replies" :key="reply.id"
              class="rounded-2xl p-5"
              :style="reply.is_counselor
                ? 'background: #ECFDF5; margin-left: 24px; box-shadow: 0 2px 12px rgba(125,206,160,0.08);'
                : 'background: #F1F5F9; margin-right: 24px;'"
            >
              <div class="flex justify-between items-center mb-2">
                <span class="text-[10px] font-medium flex items-center gap-1"
                  :style="reply.is_counselor ? 'color: #10B981;' : 'color: #94A3B8;'"
                >
                  <UserCircle v-if="reply.is_counselor" class="w-3.5 h-3.5" />
                  <MessageCircle v-else class="w-3.5 h-3.5" />
                  {{ reply.is_counselor ? '辅导员回复' : '我的追加' }}
                </span>
                <span class="text-[10px]" style="color: #94A3B8;">{{ formatTime(reply.created_at) }}</span>
              </div>
              <p class="text-sm whitespace-pre-wrap" style="color: #475569;">{{ reply.content }}</p>
            </div>

            <!-- 无回复提示 -->
            <div v-if="feedbackDetail.replies?.length === 0 && feedbackDetail.status === 'pending'" class="rounded-2xl p-5 text-center" style="background: #FFFBEB;">
              <p class="text-xs" style="color: #B45309;">辅导员尚未回复，请耐心等待</p>
            </div>

            <!-- 追加回复 -->
            <div v-if="feedbackDetail.status !== 'closed'" class="bg-white rounded-3xl p-7" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
              <textarea
                v-model="replyContent"
                rows="3"
                placeholder="追加说明..."
                class="feedback-textarea mb-4"
              ></textarea>
              <button
                @click="handleReply"
                :disabled="replying || !replyContent.trim()"
                class="px-6 py-2.5 rounded-full text-sm font-medium text-white transition-colors duration-200 disabled:opacity-50 cursor-pointer flex items-center gap-2"
                style="background: #10B981;"
                @mouseenter="!replying && ($event.target.style.background='#059669')"
                @mouseleave="$event.target.style.background='#10B981'"
              >
                <Loader2 v-if="replying" class="w-4 h-4 animate-spin" />
                <Send v-else class="w-4 h-4" />
                {{ replying ? '发送中...' : '发送' }}
              </button>
            </div>
            <div v-else class="text-center py-4 rounded-2xl text-xs" style="background: #F1F5F9; color: #94A3B8;">该反馈已关闭</div>
          </div>
        </template>
      </div>

      <!-- 右栏：提示信息 -->
      <div class="space-y-7">
        <!-- 曾用昵称看板 -->
        <div class="rounded-3xl p-7" style="background: linear-gradient(180deg, #F0FDF4, #FFFFFF); box-shadow: 0 2px 16px rgba(16,185,129,0.06);">
          <h3 class="text-sm font-semibold mb-4 flex items-center gap-2" style="color: #1E293B;">
            <Bookmark class="w-4 h-4" style="color: #10B981;" />
            曾用昵称
          </h3>
          <div v-if="savedNicknames.length === 0" class="text-center py-4">
            <MessageCircle class="w-6 h-6 mx-auto mb-2" style="color: #CBD5E1;" />
            <p class="text-[11px]" style="color: #94A3B8;">投递反馈后，昵称会自动保存在这里</p>
          </div>
          <div v-else class="space-y-2 max-h-52 overflow-y-auto">
            <button
              v-for="(nick, i) in savedNicknames" :key="i"
              @click="useNickname(nick)"
              class="w-full flex items-center justify-between px-4 py-3 rounded-2xl text-left transition-all duration-200 cursor-pointer group"
              style="background: #F1F5F9;"
              @mouseenter="$event.currentTarget.style.background='#ECFDF5'"
              @mouseleave="$event.currentTarget.style.background='#F1F5F9'"
            >
              <span class="text-xs font-medium truncate" style="color: #1E293B;">{{ nick }}</span>
              <span class="text-[10px] shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" style="color: #10B981;">点击查看 →</span>
            </button>
          </div>
        </div>

        <!-- 树洞须知 -->
        <div class="rounded-3xl p-7" style="background: linear-gradient(180deg, #ECFDF5, #FFFFFF); box-shadow: 0 2px 16px rgba(16,185,129,0.06);">
          <h3 class="text-sm font-semibold mb-4 flex items-center gap-2" style="color: #1E293B;">
            <Info class="w-4 h-4" style="color: #10B981;" />
            树洞须知
          </h3>
          <div class="space-y-4">
            <div class="flex gap-3">
              <div class="w-8 h-8 rounded-xl flex items-center justify-center shrink-0" style="background: #ECFDF5;">
                <ShieldCheck class="w-3.5 h-3.5" style="color: #10B981;" />
              </div>
              <div>
                <p class="text-xs font-medium" style="color: #1E293B;">完全匿名</p>
                <p class="text-[11px]" style="color: #94A3B8;">辅导员无法追溯身份</p>
              </div>
            </div>
            <div class="flex gap-3">
              <div class="w-8 h-8 rounded-xl flex items-center justify-center shrink-0" style="background: #F0FDF4;">
                <Clock class="w-3.5 h-3.5" style="color: #34D399;" />
              </div>
              <div>
                <p class="text-xs font-medium" style="color: #1E293B;">及时回复</p>
                <p class="text-[11px]" style="color: #94A3B8;">1-3 个工作日内回复</p>
              </div>
            </div>
            <div class="flex gap-3">
              <div class="w-8 h-8 rounded-xl flex items-center justify-center shrink-0" style="background: #FFFBEB;">
                <Key class="w-3.5 h-3.5" style="color: #F59E0B;" />
              </div>
              <div>
                <p class="text-xs font-medium" style="color: #1E293B;">保存凭证</p>
                <p class="text-[11px]" style="color: #94A3B8;">专属昵称是查看回复的唯一凭证</p>
              </div>
            </div>
            <div class="flex gap-3">
              <div class="w-8 h-8 rounded-xl flex items-center justify-center shrink-0" style="background: #FEF2F2;">
                <Heart class="w-3.5 h-3.5" style="color: #EF4444;" />
              </div>
              <div>
                <p class="text-xs font-medium" style="color: #1E293B;">紧急求助</p>
                <p class="text-[11px]" style="color: #94A3B8;">心理问题请拨打心理热线</p>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- 底部：常见问题 + 温馨提醒 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-7 mt-7">
      <div class="rounded-3xl p-7" style="background: #F0FDF4; box-shadow: 0 2px 16px rgba(16,185,129,0.06);">
        <h3 class="text-sm font-semibold mb-4 flex items-center gap-2" style="color: #1E293B;">
          <HelpCircle class="w-4 h-4" style="color: #10B981;" />
          常见问题
        </h3>
        <div class="space-y-4">
          <div>
            <p class="text-xs font-medium mb-0.5" style="color: #1E293B;">昵称丢了怎么办？</p>
            <p class="text-[11px]" style="color: #94A3B8;">很遗憾无法找回，请重新提交反馈。</p>
          </div>
          <div class="h-px" style="background: #F1F5F9;"></div>
          <div>
            <p class="text-xs font-medium mb-0.5" style="color: #1E293B;">可以发多条反馈吗？</p>
            <p class="text-[11px]" style="color: #94A3B8;">可以，每次提交会获得独立的可爱昵称。</p>
          </div>
          <div class="h-px" style="background: #F1F5F9;"></div>
          <div>
            <p class="text-xs font-medium mb-0.5" style="color: #1E293B;">辅导员能看到我是谁吗？</p>
            <p class="text-[11px]" style="color: #94A3B8;">不能，系统不记录任何身份关联信息。</p>
          </div>
        </div>
      </div>
      <div class="rounded-3xl p-7 flex flex-col justify-center" style="background: #FDF8F2; box-shadow: 0 2px 16px rgba(232,201,122,0.08);">
        <p class="text-sm font-semibold mb-3 flex items-center gap-1.5" style="color: #C4956A;">
          <Phone class="w-4 h-4" />
          温馨提醒
        </p>
        <p class="text-xs mb-2" style="color: #B45309;">如需心理支持，可以拨打：</p>
        <p class="text-base font-bold" style="color: #C4956A;">全国心理援助热线：400-161-9995</p>
        <p class="text-[11px] mt-2" style="color: #94A3B8;">24小时在线，随时倾听你的声音</p>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="rounded-2xl p-5 mt-7 flex items-start gap-3" style="background: #FEF2F2;">
      <TriangleAlert class="w-4 h-4 shrink-0 mt-0.5" style="color: #EF4444;" />
      <p class="text-sm" style="color: #EF4444;">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  Send, MessageCircle, ShieldCheck, Loader2, CircleCheckBig, Search, UserCircle, TriangleAlert,
  Info, Clock, Key, Heart, HelpCircle, Phone, Eye, Bookmark,
  Home, BookOpen, Lightbulb, HeartHandshake, MoreHorizontal,
} from 'lucide-vue-next'
import { submitFeedback, getMyFeedback, studentReply } from '../api'

const tab = ref('submit')
const categories = [
  { value: '寝室矛盾', icon: Home, color: '#10B981', bg: '#ECFDF5' },
  { value: '学业压力', icon: BookOpen, color: '#3B82F6', bg: '#EFF6FF' },
  { value: '教学建议', icon: Lightbulb, color: '#F59E0B', bg: '#FFFBEB' },
  { value: '心理困惑', icon: HeartHandshake, color: '#EC4899', bg: '#FDF2F8' },
  { value: '其他', icon: MoreHorizontal, color: '#6B7280', bg: '#F3F4F6' },
]

const form = ref({ content: '', category: '其他' })
const submitting = ref(false)
const submitResult = ref(null)

const checkId = ref('')
const checking = ref(false)
const feedbackDetail = ref(null)
const replyContent = ref('')
const replying = ref(false)

const errorMsg = ref('')

const NICKNAME_KEY = 'feedback_nicknames'
const savedNicknames = ref(JSON.parse(localStorage.getItem(NICKNAME_KEY) || '[]'))

function saveNickname(nick) {
  const list = savedNicknames.value.filter(n => n !== nick)
  list.unshift(nick)
  if (list.length > 20) list.pop()
  savedNicknames.value = list
  localStorage.setItem(NICKNAME_KEY, JSON.stringify(list))
}

function useNickname(nick) {
  tab.value = 'check'
  checkId.value = nick
  handleCheck()
}

function formatTime(t) {
  return new Date(t).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function fbStatusStyle(s) {
  const styles = {
    pending: 'background: #FFFBEB; color: #B45309;',
    replied: 'background: #ECFDF5; color: #10B981;',
    closed: 'background: #F1F5F9; color: #94A3B8;',
  }
  return styles[s] || ''
}

function fbStatusText(s) {
  return { pending: '待回复', replied: '已回复', closed: '已关闭' }[s] || s
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

async function handleSubmit() {
  if (!form.value.content.trim()) return
  submitting.value = true
  errorMsg.value = ''
  submitResult.value = null
  try {
    const { data } = await submitFeedback(form.value)
    submitResult.value = data
    saveNickname(data.anonymous_id)
    form.value.content = ''
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '投递失败，请重试'
  } finally {
    submitting.value = false
  }
}

async function handleCheck() {
  if (!checkId.value.trim()) return
  checking.value = true
  errorMsg.value = ''
  feedbackDetail.value = null
  try {
    const { data } = await getMyFeedback(checkId.value.trim())
    feedbackDetail.value = data
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '未找到该反馈'
  } finally {
    checking.value = false
  }
}

async function handleReply() {
  if (!replyContent.value.trim()) return
  replying.value = true
  errorMsg.value = ''
  try {
    await studentReply(feedbackDetail.value.anonymous_id, replyContent.value)
    replyContent.value = ''
    await handleCheck()
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '回复失败'
  } finally {
    replying.value = false
  }
}
</script>

<style scoped>
@reference "../style.css";

.feedback-textarea {
  @apply w-full rounded-2xl px-4 py-3 text-sm resize-none
         transition-all duration-200
         focus:outline-none focus:ring-2 focus:border-transparent;
  background: #F1F5F9;
  color: #1E293B;
  --tw-ring-color: rgba(125, 175, 206, 0.4);
}
.feedback-textarea::placeholder {
  color: #94A3B8;
}
.feedback-input {
  @apply w-full rounded-2xl px-4 py-3 text-sm
         transition-all duration-200
         focus:outline-none focus:ring-2 focus:border-transparent;
  background: #F1F5F9;
  color: #1E293B;
  --tw-ring-color: rgba(125, 175, 206, 0.4);
}
</style>
