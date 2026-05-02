<template>
  <div>
    <div class="flex items-start justify-between mb-7">
      <div class="flex items-center gap-3 relative">
        <img src="/src/assets/ui/sticker-book.png" alt="" class="absolute -top-3 -left-3 w-7 h-7 opacity-25 pointer-events-none" />
        <div class="w-12 h-12 rounded-2xl flex items-center justify-center" style="background: #E8F4FD;">
          <ImageUp class="w-5 h-5" style="color: #6ECAFF;" />
        </div>
        <div>
          <h2 class="text-lg font-bold" style="color: #1E293B;">成果上传</h2>
          <p class="text-xs" style="color: #94A3B8;">选择类别，上传证书，智能识别信息</p>
        </div>
      </div>
    </div>

    <!-- 步骤进度条 -->
    <div class="rounded-3xl p-5 mb-7" style="background: linear-gradient(135deg, #F0FDF4, #ECFDF5); box-shadow: 0 2px 16px rgba(16,185,129,0.06);">
      <div class="flex items-center justify-between">
        <div v-for="(step, i) in steps" :key="i" class="flex items-center" :class="i < steps.length - 1 ? 'flex-1' : ''">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold transition-colors duration-200" :style="currentStep >= i ? 'background: #10B981; color: white;' : 'background: #F1F5F9; color: #94A3B8;'">
              <Check v-if="currentStep > i" class="w-3.5 h-3.5" />
              <span v-else>{{ i + 1 }}</span>
            </div>
            <span class="text-xs font-medium hidden sm:inline" :style="currentStep >= i ? 'color: #1E293B;' : 'color: #94A3B8;'">{{ step }}</span>
          </div>
          <div v-if="i < steps.length - 1" class="flex-1 h-px mx-4" :style="currentStep > i ? 'background: #10B981;' : 'background: #E2E8F0;'"></div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-7">
      <div class="lg:col-span-2 space-y-7">
        <!-- 步骤1：选择成果类别 -->
        <div v-if="!selectedCategory" class="bg-white rounded-3xl p-7" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
          <h3 class="text-sm font-semibold mb-5 flex items-center gap-2" style="color: #1E293B;">
            <Layers class="w-4 h-4" style="color: #10B981;" />
            选择成果类别
          </h3>
          <div class="grid grid-cols-2 gap-4">
            <button
              v-for="cat in categoryList" :key="cat.name"
              @click="selectedCategory = cat.name"
              class="flex items-center gap-4 p-5 rounded-2xl transition-all duration-200 cursor-pointer border-2"
              style="border-color: transparent; background: #F1F5F9;"
              @mouseenter="$event.currentTarget.style.borderColor = cat.color; $event.currentTarget.style.background = cat.bg"
              @mouseleave="$event.currentTarget.style.borderColor = 'transparent'; $event.currentTarget.style.background = '#F1F5F9'"
            >
              <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0" :style="{ background: cat.bg }">
                <component :is="cat.icon" class="w-4.5 h-4.5" :style="{ color: cat.color }" />
              </div>
              <div class="text-left">
                <p class="text-sm font-medium" style="color: #1E293B;">{{ cat.name }}</p>
                <p class="text-[11px]" style="color: #94A3B8;">{{ cat.desc }}</p>
              </div>
            </button>
          </div>
        </div>

        <!-- 步骤2：上传区域 -->
        <div v-if="selectedCategory && !submitSuccess && !extractedData" class="bg-white rounded-3xl p-7" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
          <div class="flex items-center justify-between mb-5">
            <h3 class="text-sm font-semibold flex items-center gap-2" style="color: #1E293B;">
              <CloudUpload class="w-4 h-4" style="color: #10B981;" />
              上传证书照片
              <span class="text-[10px] font-normal px-3 py-1 rounded-full" style="background: #ECFDF5; color: #10B981;">{{ selectedCategory }}</span>
            </h3>
            <button @click="handleReset" class="text-xs cursor-pointer transition-colors duration-200" style="color: #94A3B8;" @mouseenter="$event.target.style.color='#10B981'" @mouseleave="$event.target.style.color='#94A3B8'">← 重新选择类别</button>
          </div>
          <div
            class="border-2 border-dashed rounded-3xl p-10 text-center transition-colors duration-200 cursor-pointer"
            :style="isDragging ? 'border-color: #10B981; background: #ECFDF5;' : 'border-color: #E2E8F0; background: #F1F5F9;'"
            @dragover.prevent="isDragging = true" @dragleave="isDragging = false" @drop.prevent="handleDrop" @click="$refs.fileInput.click()"
          >
            <input ref="fileInput" type="file" accept=".jpg,.jpeg,.png,.webp" class="hidden" @change="handleFileSelect" />
            <div v-if="!previewUrl" class="flex flex-col items-center gap-3">
              <div class="w-14 h-14 rounded-full flex items-center justify-center" style="background: #ECFDF5;">
                <CloudUpload class="w-6 h-6" style="color: #10B981;" />
              </div>
              <p class="text-sm" style="color: #475569;">点击或拖拽证书图片到此处</p>
              <p class="text-xs" style="color: #94A3B8;">支持 JPG / PNG / WebP，不超过 10MB</p>
            </div>
            <div v-else>
              <img :src="previewUrl" alt="证书预览" class="max-h-56 mx-auto rounded-2xl" />
              <p class="text-xs mt-3" style="color: #94A3B8;">{{ selectedFile?.name }}</p>
            </div>
          </div>
          <button v-if="selectedFile" @click="handleUpload" :disabled="uploading" class="mt-5 w-full py-3 rounded-full text-sm font-medium text-white transition-colors duration-200 disabled:opacity-50 cursor-pointer flex items-center justify-center gap-2" style="background: #10B981;" @mouseenter="!uploading && ($event.target.style.background='#059669')" @mouseleave="$event.target.style.background='#10B981'">
            <Loader2 v-if="uploading" class="w-4 h-4 animate-spin" />
            <Sparkles v-else class="w-4 h-4" />
            {{ uploading ? '智能识别中，请稍候...' : '开始智能识别' }}
          </button>
        </div>

        <!-- 步骤3：识别结果（按类别展示不同字段） -->
        <div v-if="extractedData" class="bg-white rounded-3xl p-7" style="box-shadow: 0 2px 16px rgba(125,206,160,0.1);">
          <h3 class="text-sm font-semibold mb-3 flex items-center gap-2" style="color: #1E293B;">
            <Sparkles class="w-4 h-4" style="color: #10B981;" />
            识别结果
            <span class="text-[10px] font-normal px-3 py-1 rounded-full" style="background: #ECFDF5; color: #10B981;">可修改</span>
            <span class="text-[10px] font-normal px-3 py-1 rounded-full ml-1" style="background: #ECFDF5; color: #10B981;">{{ selectedCategory }}</span>
          </h3>
          <div class="rounded-2xl p-4 mb-5 flex items-start gap-3" style="background: #FFFBEB;">
            <TriangleAlert class="w-4 h-4 shrink-0 mt-0.5" style="color: #D97706;" />
            <div>
              <p class="text-xs font-medium" style="color: #B45309;">AI 识别结果仅供参考，请务必逐项核对！</p>
              <p class="text-[11px] mt-1" style="color: #B45309;">识别不是百分百准确的，请仔细检查每个字段，确认无误后再提交。带 * 的为必填项。</p>
            </div>
          </div>
          <div v-if="formError" class="rounded-2xl p-4 mb-5 flex items-start gap-3" style="background: #FEF2F2;">
            <TriangleAlert class="w-4 h-4 shrink-0 mt-0.5" style="color: #EF4444;" />
            <p class="text-xs" style="color: #EF4444;">{{ formError }}</p>
          </div>

          <!-- 科研项目 -->
          <div v-if="selectedCategory === '科研项目'" class="space-y-4">
            <div><label class="block text-xs mb-1.5 req-label">参与科研项目名称 <span class="text-red-400">*</span></label><input v-model="extractedData.project_name" class="form-input" /></div>
            <div class="grid grid-cols-2 gap-4">
              <div><label class="block text-xs mb-1.5 req-label">立项编号 <span class="text-red-400">*</span></label><input v-model="extractedData.project_number" class="form-input" /></div>
              <div><label class="block text-xs mb-1.5 req-label">项目层级 <span class="text-red-400">*</span></label>
                <select v-model="extractedData.project_level" class="form-input cursor-pointer">
                  <option value="">请选择</option>
                  <option value="国家级">国家级</option><option value="省级">省级</option>
                  <option value="市厅级">市厅级</option><option value="校级">校级</option>
                </select>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div><label class="block text-xs mb-1.5 req-label">学生排名 <span class="text-red-400">*</span></label><input v-model="extractedData.student_rank" class="form-input" /></div>
              <div><label class="block text-xs mb-1.5 req-label">立项年度 <span class="text-red-400">*</span></label><input v-model="extractedData.project_year" class="form-input" /></div>
            </div>
            <div><label class="block text-xs mb-1.5 req-label">项目来源 <span class="text-red-400">*</span></label><input v-model="extractedData.project_source" class="form-input" /></div>
            <div class="grid grid-cols-2 gap-4">
              <div><label class="block text-xs mb-1.5 req-label">项目负责人 <span class="text-red-400">*</span></label><input v-model="extractedData.project_leader" class="form-input" /></div>
              <div><label class="block text-xs mb-1.5 req-label">工号 <span class="text-red-400">*</span></label><input v-model="extractedData.leader_id" class="form-input" /></div>
            </div>
            <div><label class="block text-xs mb-1.5 req-label">辅导员姓名 <span class="text-red-400">*</span></label><input v-model="extractedData.counselor_name" class="form-input" /></div>
          </div>

          <!-- 专利软著 -->
          <div v-if="selectedCategory === '专利软著'" class="space-y-4">
            <div><label class="block text-xs mb-1.5 req-label">名称 <span class="text-red-400">*</span></label><input v-model="extractedData.name" class="form-input" /></div>
            <div class="grid grid-cols-2 gap-4">
              <div><label class="block text-xs mb-1.5 req-label">类别 <span class="text-red-400">*</span></label>
                <select v-model="extractedData.patent_type" class="form-input cursor-pointer">
                  <option value="">请选择</option>
                  <option value="发明专利">发明专利</option><option value="实用新型专利">实用新型专利</option>
                  <option value="外观设计专利">外观设计专利</option><option value="软著">软著</option>
                </select>
              </div>
              <div><label class="block text-xs mb-1.5 req-label">授权号 <span class="text-red-400">*</span></label><input v-model="extractedData.authorization_number" class="form-input" /></div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div><label class="block text-xs mb-1.5 req-label">获批时间 <span class="text-red-400">*</span></label><input v-model="extractedData.approval_date" class="form-input" /></div>
              <div><label class="block text-xs mb-1.5 req-label">发明人排名 <span class="text-red-400">*</span></label><input v-model="extractedData.inventor_rank" class="form-input" /></div>
            </div>
            <div><label class="block text-xs mb-1.5 req-label">辅导员姓名 <span class="text-red-400">*</span></label><input v-model="extractedData.counselor_name" class="form-input" /></div>
          </div>

          <!-- 学术论文 -->
          <div v-if="selectedCategory === '学术论文'" class="space-y-4">
            <div><label class="block text-xs mb-1.5 req-label">论文名称 <span class="text-red-400">*</span></label><input v-model="extractedData.paper_name" class="form-input" /></div>
            <div><label class="block text-xs mb-1.5 req-label">发表期刊名称 <span class="text-red-400">*</span></label><input v-model="extractedData.journal_name" class="form-input" /></div>
            <div class="grid grid-cols-3 gap-4">
              <div><label class="block text-xs mb-1.5 req-label">作者排名 <span class="text-red-400">*</span></label><input v-model="extractedData.author_rank" class="form-input" /></div>
              <div><label class="block text-xs mb-1.5 req-label">发表时间 <span class="text-red-400">*</span></label><input v-model="extractedData.publish_date" class="form-input" /></div>
              <div><label class="block text-xs mb-1.5 req-label">收录情况 <span class="text-red-400">*</span></label>
                <select v-model="extractedData.indexing" class="form-input cursor-pointer">
                  <option value="">请选择</option>
                  <option value="SCI">SCI</option><option value="EI">EI</option>
                  <option value="CSSCI">CSSCI</option><option value="CPCI">CPCI</option>
                  <option value="北大核心">北大核心</option><option value="普刊">普刊</option>
                </select>
              </div>
            </div>
            <div><label class="block text-xs mb-1.5" style="color: #94A3B8;">论文链接（若有）</label><input v-model="extractedData.paper_link" class="form-input" /></div>
            <div><label class="block text-xs mb-1.5 req-label">辅导员姓名 <span class="text-red-400">*</span></label><input v-model="extractedData.counselor_name" class="form-input" /></div>
          </div>

          <!-- 学科竞赛 -->
          <div v-if="selectedCategory === '学科竞赛'" class="space-y-4">
            <div><label class="block text-xs mb-1.5 req-label">赛事名称 <span class="text-red-400">*</span></label><input v-model="extractedData.competition_name" class="form-input" /></div>
            <div class="grid grid-cols-2 gap-4">
              <div><label class="block text-xs mb-1.5 req-label">赛道 <span class="text-red-400">*</span></label><input v-model="extractedData.track" class="form-input" /></div>
              <div><label class="block text-xs mb-1.5 req-label">赛事主办方 <span class="text-red-400">*</span></label><input v-model="extractedData.organizer" class="form-input" /></div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div><label class="block text-xs mb-1.5 req-label">项目名称 <span class="text-red-400">*</span></label><input v-model="extractedData.project_name" class="form-input" /></div>
              <div><label class="block text-xs mb-1.5 req-label">奖项名称 <span class="text-red-400">*</span></label><input v-model="extractedData.award_name" class="form-input" /></div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div><label class="block text-xs mb-1.5 req-label">项目负责人 <span class="text-red-400">*</span></label><input v-model="extractedData.team_leader" class="form-input" /></div>
              <div><label class="block text-xs mb-1.5 req-label">联系电话 <span class="text-red-400">*</span></label><input v-model="extractedData.phone" class="form-input" /></div>
            </div>
            <div><label class="block text-xs mb-1.5 req-label">指导老师（全部） <span class="text-red-400">*</span></label><input v-model="extractedData.advisor" class="form-input" /></div>
            <div><label class="block text-xs mb-1.5 req-label">学生成员（全部，个人赛事填无） <span class="text-red-400">*</span></label><input v-model="extractedData.team_members" class="form-input" /></div>
            <div class="grid grid-cols-2 gap-4">
              <div><label class="block text-xs mb-1.5 req-label">获奖时间 <span class="text-red-400">*</span></label><input v-model="extractedData.award_date" class="form-input" /></div>
              <div><label class="block text-xs mb-1.5" style="color: #94A3B8;">备注</label><input v-model="extractedData.remark" class="form-input" /></div>
            </div>
          </div>

          <div class="flex gap-4 mt-6">
            <button @click="handleConfirm" :disabled="confirming" class="flex-1 py-3 rounded-full text-sm font-medium text-white transition-colors duration-200 disabled:opacity-50 cursor-pointer flex items-center justify-center gap-2" style="background: #10B981;" @mouseenter="!confirming && ($event.target.style.background='#059669')" @mouseleave="$event.target.style.background='#10B981'">
              <Loader2 v-if="confirming" class="w-4 h-4 animate-spin" /><Check v-else class="w-4 h-4" />
              {{ confirming ? '提交中...' : '确认无误，提交' }}
            </button>
            <button @click="handleReset" class="px-6 py-3 rounded-full text-sm transition-colors duration-200 cursor-pointer" style="background: #F1F5F9; color: #94A3B8;" @mouseenter="$event.target.style.background='#E2E8F0'" @mouseleave="$event.target.style.background='#F1F5F9'">重新上传</button>
          </div>
        </div>

        <!-- 成功 -->
        <div v-if="submitSuccess" class="bg-white rounded-3xl p-8 text-center" style="box-shadow: 0 2px 16px rgba(125,206,160,0.1);">
          <div class="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4" style="background: #ECFDF5;">
            <CircleCheckBig class="w-8 h-8" style="color: #10B981;" />
          </div>
          <p class="text-base font-semibold mb-1" style="color: #1E293B;">提交成功</p>
          <p class="text-xs mb-5" style="color: #94A3B8;">你的成果已记录，辅导员可在后台查看和确认</p>
          <button @click="handleReset" class="text-sm cursor-pointer transition-colors duration-200 font-medium" style="color: #10B981;" @mouseenter="$event.target.style.color='#059669'" @mouseleave="$event.target.style.color='#10B981'">继续上传其他证书 →</button>
        </div>

        <div v-if="errorMsg" class="rounded-2xl p-5 flex items-start gap-3" style="background: #FEF2F2;">
          <TriangleAlert class="w-4 h-4 shrink-0 mt-0.5" style="color: #EF4444;" />
          <p class="text-sm" style="color: #EF4444;">{{ errorMsg }}</p>
        </div>
      </div>

      <!-- 右栏 -->
      <div class="space-y-7">
        <div class="rounded-3xl p-7" style="background: linear-gradient(180deg, #F0FDF4, #FFFFFF); box-shadow: 0 2px 16px rgba(16,185,129,0.06);">
          <h3 class="text-sm font-semibold mb-4 flex items-center gap-2" style="color: #1E293B;">
            <History class="w-4 h-4" style="color: #10B981;" />
            我的提交记录
          </h3>
          <div v-if="myAchievements.length === 0" class="text-center py-6">
            <FileX class="w-6 h-6 mx-auto mb-2" style="color: #CBD5E1;" />
            <p class="text-xs" style="color: #94A3B8;">暂无提交记录</p>
          </div>
          <div v-else class="space-y-2.5 max-h-72 overflow-y-auto">
            <div v-for="item in myAchievements" :key="item.category + item.id" class="flex items-center gap-3 px-4 py-3 rounded-2xl" style="background: #F1F5F9;">
              <div class="flex-1 min-w-0">
                <p class="text-xs font-medium truncate" style="color: #1E293B;">{{ item.display_name }}</p>
                <p class="text-[10px]" style="color: #94A3B8;">{{ item.category }}</p>
              </div>
              <span class="px-3 py-1 text-[10px] font-medium rounded-full shrink-0" :style="statusStyle(item.status)">{{ statusText(item.status) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 成果墙 -->
    <div class="mt-7">
      <div class="rounded-3xl p-7" style="background: linear-gradient(135deg, #F0FDF4, #ECFDF5); box-shadow: 0 2px 16px rgba(16,185,129,0.08);">
        <h3 class="text-sm font-semibold mb-5 flex items-center gap-2" style="color: #1E293B;">
          <ImageUp class="w-4 h-4" style="color: #10B981;" />
          我的成果墙
        </h3>
        <div v-if="achievementsWithImage.length === 0" class="text-center py-10">
          <FileX class="w-8 h-8 mx-auto mb-2" style="color: #CBD5E1;" />
          <p class="text-xs" style="color: #94A3B8;">还没有上传过证书图片</p>
        </div>
        <template v-else>
          <div v-for="cat in wallCategories" :key="cat.name" class="mb-6 last:mb-0">
            <div class="flex items-center gap-2 mb-3">
              <div class="w-6 h-6 rounded-lg flex items-center justify-center" :style="{ background: cat.bg }">
                <component :is="cat.icon" class="w-3 h-3" :style="{ color: cat.color }" />
              </div>
              <span class="text-xs font-semibold" style="color: #1E293B;">{{ cat.name }}</span>
              <span class="text-[10px] px-2 py-0.5 rounded-full" :style="{ background: cat.bg, color: cat.color }">{{ cat.items.length }}</span>
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              <div v-for="item in cat.items" :key="item.id" class="group relative">
                <a :href="getAssetUrl(item.certificate_image)" target="_blank" class="block">
                  <div class="aspect-[4/3] rounded-2xl overflow-hidden" style="background: #F1F5F9;">
                    <img :src="getAssetUrl(item.certificate_image)" :alt="item.display_name" class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" />
                  </div>
                </a>
                <div class="mt-2">
                  <p class="text-[11px] font-medium truncate" style="color: #1E293B;" :title="item.display_name">{{ item.display_name }}</p>
                  <div class="flex items-center justify-between mt-0.5">
                    <span class="text-[10px]" style="color: #94A3B8;">{{ item.category }}</span>
                    <span class="px-2 py-0.5 text-[9px] font-medium rounded-full" :style="statusStyle(item.status)">{{ statusText(item.status) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ImageUp, CloudUpload, Sparkles, Loader2, Check, CircleCheckBig, TriangleAlert, Clock, History, FileX, Layers, FlaskConical, Copyright, GraduationCap, Trophy } from 'lucide-vue-next'
import { createStudent, uploadCertificate, confirmAchievement, listMyAllAchievements, getAssetUrl } from '../api'

const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
const steps = ['选择类别', '上传证书', '智能识别', '核对修改', '确认提交']
const currentStep = computed(() => {
  if (submitSuccess.value) return 5
  if (extractedData.value) return 3
  if (selectedFile.value) return 2
  if (selectedCategory.value) return 1
  return 0
})

const categoryList = [
  { name: '科研项目', desc: '科研项目立项', color: '#059669', bg: '#ECFDF5', icon: FlaskConical },
  { name: '专利软著', desc: '专利、软件著作权', color: '#10B981', bg: '#D1FAE5', icon: Copyright },
  { name: '学术论文', desc: '学术论文发表', color: '#047857', bg: '#A7F3D0', icon: GraduationCap },
  { name: '学科竞赛', desc: '学科竞赛获奖', color: '#34D399', bg: '#ECFDF5', icon: Trophy },
]

const achievementsWithImage = computed(() =>
  myAchievements.value.filter(a => a.certificate_image)
)
const wallCategories = computed(() =>
  categoryList
    .map(cat => ({
      ...cat,
      items: achievementsWithImage.value.filter(a => a.category === cat.name),
    }))
    .filter(cat => cat.items.length > 0)
)

const selectedCategory = ref(null)
const selectedFile = ref(null)
const previewUrl = ref('')
const isDragging = ref(false)
const uploading = ref(false)
const confirming = ref(false)
const submitSuccess = ref(false)
const errorMsg = ref('')
const formError = ref('')
const extractedData = ref(null)
const imagePath = ref('')
const myAchievements = ref([])

function statusStyle(s) { return { confirmed: 'background: #ECFDF5; color: #10B981;', pending: 'background: #FFFBEB; color: #D97706;', rejected: 'background: #FEF2F2; color: #EF4444;' }[s] || 'background: #F1F5F9; color: #94A3B8;' }
function statusText(s) { return { confirmed: '已通过', pending: '待审核', rejected: '已驳回' }[s] || s }
function handleFileSelect(e) { const f = e.target.files[0]; if (f) setFile(f) }
function handleDrop(e) { isDragging.value = false; const f = e.dataTransfer.files[0]; if (f) setFile(f) }
function setFile(file) { selectedFile.value = file; previewUrl.value = URL.createObjectURL(file); extractedData.value = null; submitSuccess.value = false; errorMsg.value = '' }

async function handleUpload() {
  if (!selectedFile.value || !selectedCategory.value) return
  uploading.value = true; errorMsg.value = ''
  try {
    const { data } = await uploadCertificate(selectedFile.value, selectedCategory.value)
    extractedData.value = data.extracted
    imagePath.value = data.image_path
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '上传失败，请重试'
  } finally {
    uploading.value = false
  }
}

const REQUIRED_FIELDS = {
  '科研项目': ['project_name', 'project_number', 'project_level', 'student_rank', 'project_year', 'project_source', 'project_leader', 'leader_id', 'counselor_name'],
  '专利软著': ['name', 'patent_type', 'authorization_number', 'approval_date', 'inventor_rank', 'counselor_name'],
  '学术论文': ['paper_name', 'journal_name', 'author_rank', 'publish_date', 'indexing', 'counselor_name'],
  '学科竞赛': ['competition_name', 'track', 'organizer', 'project_name', 'award_name', 'team_leader', 'phone', 'advisor', 'team_members', 'award_date'],
}

function validateForm() {
  const fields = REQUIRED_FIELDS[selectedCategory.value] || []
  for (const f of fields) {
    if (!extractedData.value[f] || String(extractedData.value[f]).trim() === '') {
      formError.value = '请填写所有必填项（带 * 的字段）'
      return false
    }
  }
  formError.value = ''
  return true
}

async function handleConfirm() {
  if (!validateForm()) return
  confirming.value = true; errorMsg.value = ''
  try {
    const { data: student } = await createStudent({
      student_id: currentUser.username,
      name: currentUser.name,
      class_name: currentUser.class_name,
      major: currentUser.major,
    })
    const payload = {
      ...extractedData.value,
      student_db_id: student.id,
      certificate_image: imagePath.value,
    }
    await confirmAchievement(selectedCategory.value, payload)
    submitSuccess.value = true
    extractedData.value = null
    fetchMyAchievements()
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || '提交失败，请重试'
  } finally {
    confirming.value = false
  }
}

function handleReset() {
  selectedCategory.value = null
  selectedFile.value = null
  previewUrl.value = ''
  extractedData.value = null
  imagePath.value = ''
  submitSuccess.value = false
  errorMsg.value = ''
}

async function fetchMyAchievements() {
  try {
    const { data } = await listMyAllAchievements(currentUser.username)
    myAchievements.value = Array.isArray(data) ? data : []
  } catch {}
}

onMounted(fetchMyAchievements)
</script>

<style scoped>
@reference "../style.css";
.form-input {
  @apply w-full rounded-2xl px-4 py-3 text-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:border-transparent;
  background: #F1F5F9; color: #1E293B; --tw-ring-color: rgba(125, 175, 206, 0.4);
}
.req-label {
  color: #94A3B8;
}
</style>
