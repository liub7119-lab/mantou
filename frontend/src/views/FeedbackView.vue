<template>
  <div class="max-w-2xl mx-auto">
    <h2 class="text-2xl font-bold text-gray-800 mb-6">树洞 · 匿名反馈</h2>

    <!-- Tab 切换：投递 / 查看 -->
    <div class="flex gap-2 mb-6">
      <button
        @click="tab = 'submit'"
        class="px-4 py-2 text-sm rounded-lg transition"
        :class="tab === 'submit' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 border border-gray-300'"
      >
        匿名投递
      </button>
      <button
        @click="tab = 'check'"
        class="px-4 py-2 text-sm rounded-lg transition"
        :class="tab === 'check' ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 border border-gray-300'"
      >
        查看回复
      </button>
    </div>

    <!-- ========== 投递面板 ========== -->
    <div v-if="tab === 'submit'">
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 mb-6">
        <p class="text-sm text-gray-500 mb-4">你的反馈完全匿名，辅导员无法看到你的身份信息。</p>

        <!-- 分类选择 -->
        <div class="mb-4">
          <label class="block text-sm text-gray-600 mb-2">选择分类</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="cat in categories"
              :key="cat"
              @click="form.category = cat"
              class="px-3 py-1.5 text-sm rounded-full border transition"
              :class="form.category === cat
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'"
            >
              {{ cat }}
            </button>
          </div>
        </div>

        <!-- 内容输入 -->
        <div class="mb-4">
          <label class="block text-sm text-gray-600 mb-1">说说你的想法</label>
          <textarea
            v-model="form.content"
            rows="6"
            maxlength="2000"
            placeholder="可以聊聊你的困扰、建议或者任何想说的话..."
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          ></textarea>
          <p class="text-xs text-gray-400 text-right">{{ form.content.length }} / 2000</p>
        </div>

        <!-- 提交按钮 -->
        <button
          @click="handleSubmit"
          :disabled="submitting || !form.content.trim()"
          class="w-full py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
        >
          {{ submitting ? 'AI 分析中...' : '匿名投递' }}
        </button>
      </div>

      <!-- 提交成功 -->
      <div v-if="submitResult" class="bg-green-50 border border-green-200 rounded-xl p-6">
        <p class="text-green-700 font-semibold text-lg mb-2">投递成功！</p>
        <p class="text-sm text-gray-600 mb-3">请牢记你的匿名 ID，用于查看辅导员的回复：</p>
        <div class="bg-white border-2 border-green-400 rounded-lg px-4 py-3 text-center">
          <span class="text-2xl font-bold text-green-700 tracking-wider">{{ submitResult.anonymous_id }}</span>
        </div>
        <p class="text-xs text-gray-500 mt-3 text-center">切换到「查看回复」标签页，输入此 ID 即可查看对话</p>
      </div>
    </div>

    <!-- ========== 查看回复面板 ========== -->
    <div v-if="tab === 'check'">
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 mb-6">
        <label class="block text-sm text-gray-600 mb-2">输入你的匿名 ID</label>
        <div class="flex gap-2">
          <input
            v-model="checkId"
            type="text"
            placeholder="如：树洞#A3F8K2"
            class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            @keyup.enter="handleCheck"
          />
          <button
            @click="handleCheck"
            :disabled="checking"
            class="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
          >
            {{ checking ? '查询中...' : '查看' }}
          </button>
        </div>
      </div>

      <!-- 反馈详情 + 对话 -->
      <div v-if="feedbackDetail" class="space-y-4">
        <!-- 原始反馈 -->
        <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
          <div class="flex justify-between items-start mb-3">
            <span class="px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-700">{{ feedbackDetail.category }}</span>
            <span class="text-xs text-gray-400">{{ formatTime(feedbackDetail.created_at) }}</span>
          </div>
          <p class="text-gray-700 text-sm whitespace-pre-wrap">{{ feedbackDetail.content }}</p>
        </div>

        <!-- 对话列表 -->
        <div v-for="reply in feedbackDetail.replies" :key="reply.id"
          class="rounded-xl p-4 shadow-sm border"
          :class="reply.is_counselor
            ? 'bg-blue-50 border-blue-200 ml-4'
            : 'bg-gray-50 border-gray-200 mr-4'"
        >
          <div class="flex justify-between items-center mb-2">
            <span class="text-xs font-medium" :class="reply.is_counselor ? 'text-blue-600' : 'text-gray-500'">
              {{ reply.is_counselor ? '辅导员回复' : '我的追加' }}
            </span>
            <span class="text-xs text-gray-400">{{ formatTime(reply.created_at) }}</span>
          </div>
          <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ reply.content }}</p>
        </div>

        <!-- 追加回复 -->
        <div v-if="feedbackDetail.status !== 'closed'" class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <textarea
            v-model="replyContent"
            rows="3"
            placeholder="追加说明..."
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none mb-2"
          ></textarea>
          <button
            @click="handleReply"
            :disabled="replying || !replyContent.trim()"
            class="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
          >
            {{ replying ? '发送中...' : '发送' }}
          </button>
        </div>
        <div v-else class="text-center text-sm text-gray-400 py-2">该反馈已关闭</div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="bg-red-50 border border-red-200 rounded-xl p-4 mt-4">
      <p class="text-red-600 text-sm">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { submitFeedback, getMyFeedback, studentReply } from '../api'

const tab = ref('submit')
const categories = ['寝室矛盾', '学业压力', '教学建议', '心理困惑', '其他']

// 投递
const form = ref({ content: '', category: '其他' })
const submitting = ref(false)
const submitResult = ref(null)

// 查看
const checkId = ref('')
const checking = ref(false)
const feedbackDetail = ref(null)
const replyContent = ref('')
const replying = ref(false)

const errorMsg = ref('')

function formatTime(t) {
  return new Date(t).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

async function handleSubmit() {
  if (!form.value.content.trim()) return
  submitting.value = true
  errorMsg.value = ''
  submitResult.value = null
  try {
    const { data } = await submitFeedback(form.value)
    submitResult.value = data
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
    await handleCheck() // 刷新对话
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '回复失败'
  } finally {
    replying.value = false
  }
}
</script>
