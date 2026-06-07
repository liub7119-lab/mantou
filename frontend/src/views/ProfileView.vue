<template>
  <div class="p-6 space-y-6">
    <!-- 页面标题 -->
    <div class="flex items-center gap-3">
      <UserCircle class="w-8 h-8" style="color: #6ECAFF;" />
      <div>
        <h1 class="text-2xl font-bold" style="color: #333;">我的成长画像</h1>
        <p class="text-sm" style="color: #AABBC8;">查看个人基本信息和成果统计</p>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center py-20">
      <Loader2 class="w-8 h-8 animate-spin" style="color: #6ECAFF;" />
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 基本信息卡片 -->
      <div class="bg-white rounded-3xl p-8" style="box-shadow: 0 4px 20px rgba(110,170,210,0.08);">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-2xl flex items-center justify-center" style="background: linear-gradient(135deg, #6ECAFF, #4DB8F0);">
            <User class="w-5 h-5 text-white" />
          </div>
          <h2 class="text-lg font-bold" style="color: #333;">基本信息</h2>
        </div>

        <div class="space-y-4">
          <div class="flex items-start gap-3">
            <div class="w-20 text-sm font-medium" style="color: #AABBC8;">姓名</div>
            <div class="flex-1 text-sm font-medium" style="color: #333;">{{ profile.basic_info.name }}</div>
          </div>
          <div class="flex items-start gap-3">
            <div class="w-20 text-sm font-medium" style="color: #AABBC8;">学号</div>
            <div class="flex-1 text-sm" style="color: #666;">{{ profile.basic_info.student_id }}</div>
          </div>
          <div class="flex items-start gap-3">
            <div class="w-20 text-sm font-medium" style="color: #AABBC8;">班级</div>
            <div class="flex-1 text-sm" style="color: #666;">{{ profile.basic_info.class_name }}</div>
          </div>
          <div class="flex items-start gap-3">
            <div class="w-20 text-sm font-medium" style="color: #AABBC8;">学院</div>
            <div class="flex-1 text-sm" style="color: #666;">{{ profile.basic_info.major }}</div>
          </div>
          <div v-if="profile.basic_info.gender" class="flex items-start gap-3">
            <div class="w-20 text-sm font-medium" style="color: #AABBC8;">性别</div>
            <div class="flex-1 text-sm" style="color: #666;">{{ profile.basic_info.gender }}</div>
          </div>
          <div v-if="profile.basic_info.ethnicity" class="flex items-start gap-3">
            <div class="w-20 text-sm font-medium" style="color: #AABBC8;">民族</div>
            <div class="flex-1 text-sm" style="color: #666;">{{ profile.basic_info.ethnicity }}</div>
          </div>
          <div v-if="profile.basic_info.political_status" class="flex items-start gap-3">
            <div class="w-20 text-sm font-medium" style="color: #AABBC8;">政治面貌</div>
            <div class="flex-1 text-sm" style="color: #666;">{{ profile.basic_info.political_status }}</div>
          </div>
          <div v-if="profile.basic_info.phone" class="flex items-start gap-3">
            <div class="w-20 text-sm font-medium" style="color: #AABBC8;">电话</div>
            <div class="flex-1 text-sm" style="color: #666;">{{ profile.basic_info.phone }}</div>
          </div>
          <div v-if="profile.basic_info.hometown" class="flex items-start gap-3">
            <div class="w-20 text-sm font-medium" style="color: #AABBC8;">生源地</div>
            <div class="flex-1 text-sm" style="color: #666;">{{ profile.basic_info.hometown }}</div>
          </div>
          <div v-if="profile.basic_info.dorm_nickname" class="flex items-start gap-3">
            <div class="w-20 text-sm font-medium" style="color: #AABBC8;">宿舍</div>
            <div class="flex-1 text-sm" style="color: #666;">{{ profile.basic_info.dorm_nickname }}</div>
          </div>
          <div v-if="profile.basic_info.parent_name" class="flex items-start gap-3">
            <div class="w-20 text-sm font-medium" style="color: #AABBC8;">家长姓名</div>
            <div class="flex-1 text-sm" style="color: #666;">{{ profile.basic_info.parent_name }}</div>
          </div>
          <div v-if="profile.basic_info.parent_phone" class="flex items-start gap-3">
            <div class="w-20 text-sm font-medium" style="color: #AABBC8;">家长电话</div>
            <div class="flex-1 text-sm" style="color: #666;">{{ profile.basic_info.parent_phone }}</div>
          </div>
          <div v-if="profile.basic_info.counselor" class="flex items-start gap-3">
            <div class="w-20 text-sm font-medium" style="color: #AABBC8;">辅导员</div>
            <div class="flex-1 text-sm" style="color: #666;">{{ profile.basic_info.counselor }}</div>
          </div>
        </div>
      </div>

      <!-- 成果统计卡片 -->
      <div class="bg-white rounded-3xl p-8" style="box-shadow: 0 4px 20px rgba(110,170,210,0.08);">
        <div class="flex items-center gap-3 mb-6">
          <div class="w-10 h-10 rounded-2xl flex items-center justify-center" style="background: linear-gradient(135deg, #FFD60E, #FFC107);">
            <Trophy class="w-5 h-5 text-white" />
          </div>
          <h2 class="text-lg font-bold" style="color: #333;">成果统计</h2>
        </div>

        <div class="grid grid-cols-2 gap-4 mb-6">
          <div class="text-center p-4 rounded-2xl" style="background: #F5F7FA;">
            <div class="text-3xl font-bold mb-1" style="color: #6ECAFF;">{{ profile.achievements.total }}</div>
            <div class="text-xs" style="color: #AABBC8;">总成果数</div>
          </div>
          <div class="text-center p-4 rounded-2xl" style="background: #F5F7FA;">
            <div class="text-3xl font-bold mb-1" style="color: #8FD6B0;">{{ profile.achievements.research_projects }}</div>
            <div class="text-xs" style="color: #AABBC8;">科研项目</div>
          </div>
          <div class="text-center p-4 rounded-2xl" style="background: #F5F7FA;">
            <div class="text-3xl font-bold mb-1" style="color: #FF9F43;">{{ profile.achievements.patents }}</div>
            <div class="text-xs" style="color: #AABBC8;">专利软著</div>
          </div>
          <div class="text-center p-4 rounded-2xl" style="background: #F5F7FA;">
            <div class="text-3xl font-bold mb-1" style="color: #EE5A6F;">{{ profile.achievements.papers }}</div>
            <div class="text-xs" style="color: #AABBC8;">学术论文</div>
          </div>
        </div>

        <div class="text-center p-4 rounded-2xl" style="background: #F5F7FA;">
          <div class="text-3xl font-bold mb-1" style="color: #A55EEA;">{{ profile.achievements.competitions }}</div>
          <div class="text-xs" style="color: #AABBC8;">学科竞赛</div>
        </div>
      </div>
    </div>

    <!-- 成果详情提示 -->
    <div v-if="!loading && profile.achievements.total > 0" class="bg-white rounded-3xl p-6 flex items-center gap-4" style="box-shadow: 0 4px 20px rgba(110,170,210,0.08);">
      <Info class="w-5 h-5 shrink-0" style="color: #6ECAFF;" />
      <p class="text-sm" style="color: #666;">
        以上统计仅包含<span class="font-semibold" style="color: #6ECAFF;">已通过审核</span>的成果。如需查看详细成果列表，请前往<router-link to="/upload" class="font-semibold underline" style="color: #6ECAFF;">成果上传</router-link>页面。
      </p>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && profile.achievements.total === 0" class="bg-white rounded-3xl p-12 text-center" style="box-shadow: 0 4px 20px rgba(110,170,210,0.08);">
      <Trophy class="w-16 h-16 mx-auto mb-4 opacity-20" style="color: #AABBC8;" />
      <h3 class="text-lg font-bold mb-2" style="color: #333;">暂无成果记录</h3>
      <p class="text-sm mb-6" style="color: #AABBC8;">快去上传你的科研成果、专利软著、学术论文或竞赛获奖吧！</p>
      <router-link to="/upload" class="inline-flex items-center gap-2 px-6 py-3 rounded-2xl text-sm font-semibold text-white transition-all" style="background: linear-gradient(135deg, #6ECAFF, #4DB8F0); box-shadow: 0 4px 16px rgba(110,202,255,0.35);">
        <Upload class="w-4 h-4" />
        立即上传成果
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { UserCircle, User, Trophy, Info, Upload, Loader2 } from 'lucide-vue-next'
import { getMyProfile } from '../api'

const loading = ref(true)
const profile = ref({
  basic_info: {
    student_id: '',
    name: '',
    class_name: '',
    major: '',
    gender: '',
    ethnicity: '',
    political_status: '',
    phone: '',
    hometown: '',
    home_address: '',
    parent_name: '',
    parent_phone: '',
    dorm_nickname: '',
    dorm_address: '',
    education_level: '',
    grade: '',
    specialty: '',
    counselor: ''
  },
  achievements: {
    research_projects: 0,
    patents: 0,
    papers: 0,
    competitions: 0,
    total: 0
  }
})

onMounted(async () => {
  try {
    const res = await getMyProfile()
    profile.value = res.data
  } catch (err) {
    console.error('获取成长画像失败:', err)
  } finally {
    loading.value = false
  }
})
</script>
