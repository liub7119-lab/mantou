<template>
  <div class="max-w-2xl mx-auto">
    <h2 class="text-2xl font-bold text-gray-800 mb-6">上传获奖证书</h2>

    <!-- Step 1: 学生信息 -->
    <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 mb-6">
      <h3 class="font-semibold text-gray-700 mb-4">填写基本信息</h3>
      <div class="grid grid-cols-2 gap-4">
        <!-- 学号 -->
        <div>
          <label class="block text-sm text-gray-600 mb-1">学号 *</label>
          <input
            v-model="form.student_id"
            type="text"
            maxlength="11"
            placeholder="11位数字学号"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2"
            :class="fieldError.student_id ? 'border-red-400 focus:ring-red-400' : 'border-gray-300 focus:ring-blue-500'"
            @blur="validateField('student_id')"
          />
          <p v-if="fieldError.student_id" class="text-xs text-red-500 mt-1">{{ fieldError.student_id }}</p>
        </div>
        <!-- 姓名 -->
        <div>
          <label class="block text-sm text-gray-600 mb-1">姓名 *</label>
          <input
            v-model="form.name"
            type="text"
            placeholder="请输入中文姓名"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2"
            :class="fieldError.name ? 'border-red-400 focus:ring-red-400' : 'border-gray-300 focus:ring-blue-500'"
            @blur="validateField('name')"
          />
          <p v-if="fieldError.name" class="text-xs text-red-500 mt-1">{{ fieldError.name }}</p>
        </div>
        <!-- 班级 -->
        <div>
          <label class="block text-sm text-gray-600 mb-1">班级 *</label>
          <input
            v-model="form.class_name"
            type="text"
            placeholder="如：2025级英语2班"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2"
            :class="fieldError.class_name ? 'border-red-400 focus:ring-red-400' : 'border-gray-300 focus:ring-blue-500'"
            @blur="validateField('class_name')"
          />
          <p v-if="fieldError.class_name" class="text-xs text-red-500 mt-1">{{ fieldError.class_name }}</p>
        </div>
        <!-- 学院 -->
        <div>
          <label class="block text-sm text-gray-600 mb-1">学院 *</label>
          <input
            v-model="form.major"
            type="text"
            placeholder="如：外国语言与文化学院"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2"
            :class="fieldError.major ? 'border-red-400 focus:ring-red-400' : 'border-gray-300 focus:ring-blue-500'"
            @blur="validateField('major')"
          />
          <p v-if="fieldError.major" class="text-xs text-red-500 mt-1">{{ fieldError.major }}</p>
        </div>
      </div>
    </div>

    <!-- Step 2: 上传图片 -->
    <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 mb-6">
      <h3 class="font-semibold text-gray-700 mb-4">上传证书照片</h3>

      <!-- 拖拽上传区域 -->
      <div
        class="border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer"
        :class="isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'"
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
        @drop.prevent="handleDrop"
        @click="$refs.fileInput.click()"
      >
        <input ref="fileInput" type="file" accept=".jpg,.jpeg,.png,.webp" class="hidden" @change="handleFileSelect" />

        <div v-if="!previewUrl">
          <p class="text-gray-500">点击或拖拽证书图片到此处</p>
          <p class="text-xs text-gray-400 mt-1">支持 JPG / PNG / WebP，不超过 10MB</p>
        </div>

        <!-- 图片预览 -->
        <div v-else>
          <img :src="previewUrl" alt="证书预览" class="max-h-64 mx-auto rounded-lg" />
          <p class="text-sm text-gray-500 mt-2">{{ selectedFile?.name }}</p>
        </div>
      </div>

      <!-- 上传按钮 -->
      <button
        v-if="selectedFile && !extractedData"
        @click="handleUpload"
        :disabled="uploading"
        class="mt-4 w-full py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="uploading">AI 识别中，请稍候...</span>
        <span v-else>开始 AI 识别</span>
      </button>
    </div>

    <!-- Step 3: 识别结果确认 -->
    <div v-if="extractedData" class="bg-white rounded-xl p-6 shadow-sm border border-green-200 mb-6">
      <h3 class="font-semibold text-green-700 mb-4">AI 识别结果（可修改）</h3>
      <div class="space-y-3">
        <div>
          <label class="block text-sm text-gray-600 mb-1">比赛/项目名称</label>
          <input
            v-model="extractedData.competition_name"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">获奖人</label>
          <input
            v-model="extractedData.winner_name"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm text-gray-600 mb-1">获奖等级</label>
            <input
              v-model="extractedData.award_level"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">获奖日期</label>
            <input
              v-model="extractedData.award_date"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
        </div>
        <div>
          <label class="block text-sm text-gray-600 mb-1">成果分类</label>
          <select
            v-model="category"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="科研">科研</option>
            <option value="学科竞赛">学科竞赛</option>
            <option value="创新创业">创新创业</option>
            <option value="文体活动">文体活动</option>
            <option value="其他">其他</option>
          </select>
        </div>
      </div>

      <div class="flex gap-3 mt-5">
        <button
          @click="handleConfirm"
          :disabled="confirming"
          class="flex-1 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50"
        >
          {{ confirming ? '提交中...' : '确认无误，提交' }}
        </button>
        <button
          @click="handleReset"
          class="px-4 py-2.5 border border-gray-300 text-gray-600 rounded-lg hover:bg-gray-50 transition"
        >
          重新上传
        </button>
      </div>
    </div>

    <!-- 成功提示 -->
    <div v-if="submitSuccess" class="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
      <p class="text-green-700 font-semibold text-lg">提交成功！</p>
      <p class="text-sm text-green-600 mt-1">你的成果已记录，辅导员可在后台查看</p>
      <button @click="handleReset" class="mt-4 text-sm text-blue-600 hover:underline">
        继续上传其他证书
      </button>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="bg-red-50 border border-red-200 rounded-xl p-4 mt-4">
      <p class="text-red-600 text-sm">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { createStudent, uploadCertificate, confirmAchievement } from '../api'

// 表单数据
const form = ref({
  student_id: '',
  name: '',
  class_name: '',
  major: '',  // 实际存学院名
})

// 逐字段错误提示
const fieldError = reactive({
  student_id: '',
  name: '',
  class_name: '',
  major: '',
})

// 文件相关
const selectedFile = ref(null)
const previewUrl = ref('')
const isDragging = ref(false)

// 状态
const uploading = ref(false)
const confirming = ref(false)
const submitSuccess = ref(false)
const errorMsg = ref('')

// 识别结果
const extractedData = ref(null)
const imagePath = ref('')
const category = ref('学科竞赛')

// ──────────────────────────────────────────────
// 校验规则
// ──────────────────────────────────────────────
const validators = {
  student_id(val) {
    if (!val) return '请输入学号'
    if (!/^\d{11}$/.test(val)) return '学号必须为11位数字'
    return ''
  },
  name(val) {
    if (!val) return '请输入姓名'
    if (!/^[\u4e00-\u9fa5\u00b7]{2,20}$/.test(val)) return '姓名只能输入中文（2-20个字）'
    return ''
  },
  class_name(val) {
    if (!val) return '请输入班级'
    if (!/^\d{4}级.+\d+班$/.test(val)) return '格式：年级+专业+班号，如 2025级英语2班'
    return ''
  },
  major(val) {
    if (!val) return '请输入学院名称'
    if (!/^[\u4e00-\u9fa5]{4,20}$/.test(val.replace(/[（）()]/g, ''))) return '请输入完整学院名，如 外国语言与文化学院'
    return ''
  },
}

/** 校验单个字段（失焦时调用） */
function validateField(field) {
  fieldError[field] = validators[field](form.value[field])
}

/** 校验全部字段，返回是否全部通过 */
function validateAll() {
  let pass = true
  for (const field of Object.keys(validators)) {
    fieldError[field] = validators[field](form.value[field])
    if (fieldError[field]) pass = false
  }
  return pass
}

// ──────────────────────────────────────────────
// 文件选择
// ──────────────────────────────────────────────
function handleFileSelect(e) {
  const file = e.target.files[0]
  if (file) setFile(file)
}

function handleDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) setFile(file)
}

function setFile(file) {
  selectedFile.value = file
  previewUrl.value = URL.createObjectURL(file)
  extractedData.value = null
  submitSuccess.value = false
  errorMsg.value = ''
}

// ──────────────────────────────────────────────
// 上传 + AI 识别
// ──────────────────────────────────────────────
async function handleUpload() {
  if (!selectedFile.value) return

  uploading.value = true
  errorMsg.value = ''

  try {
    const { data } = await uploadCertificate(selectedFile.value)
    extractedData.value = data.extracted
    imagePath.value = data.image_path
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '上传失败，请重试'
  } finally {
    uploading.value = false
  }
}

// ──────────────────────────────────────────────
// 确认提交
// ──────────────────────────────────────────────
async function handleConfirm() {
  // 前端全量校验
  if (!validateAll()) {
    errorMsg.value = '请按要求填写所有学生信息'
    return
  }

  confirming.value = true
  errorMsg.value = ''

  try {
    // 1. 注册/获取学生
    const { data: student } = await createStudent(form.value)

    // 2. 提交成果
    await confirmAchievement({
      student_db_id: student.id,
      competition_name: extractedData.value.competition_name,
      winner_name: extractedData.value.winner_name,
      award_level: extractedData.value.award_level,
      award_date: extractedData.value.award_date,
      category: category.value,
      certificate_image: imagePath.value,
    })

    submitSuccess.value = true
    extractedData.value = null
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '提交失败，请重试'
  } finally {
    confirming.value = false
  }
}

// ──────────────────────────────────────────────
// 重置
// ──────────────────────────────────────────────
function handleReset() {
  selectedFile.value = null
  previewUrl.value = ''
  extractedData.value = null
  imagePath.value = ''
  submitSuccess.value = false
  errorMsg.value = ''
  category.value = '学科竞赛'
}
</script>
