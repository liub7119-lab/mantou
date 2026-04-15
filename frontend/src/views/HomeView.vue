<template>
  <div class="text-center py-20">
    <h1 class="text-4xl font-bold text-gray-800 mb-4">辅导员工作辅助平台</h1>
    <p class="text-lg text-gray-500 mb-8">告别繁琐录入，让 AI 帮你搞定</p>
    <div class="flex justify-center gap-4">
      <router-link
        to="/upload"
        class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition shadow-md"
      >
        🎓 学生 · 上传证书
      </router-link>
      <router-link
        to="/admin"
        class="px-6 py-3 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition shadow-md"
      >
        📊 辅导员 · 管理后台
      </router-link>
    </div>

    <!-- 工作流程说明 -->
    <div class="mt-16 grid grid-cols-1 md:grid-cols-4 gap-6 max-w-4xl mx-auto text-left">
      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <div class="text-2xl mb-2">📸</div>
        <h3 class="font-semibold text-gray-800 mb-1">1. 拍照上传</h3>
        <p class="text-sm text-gray-500">学生上传获奖证书照片</p>
      </div>
      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <div class="text-2xl mb-2">🤖</div>
        <h3 class="font-semibold text-gray-800 mb-1">2. AI 识别</h3>
        <p class="text-sm text-gray-500">自动提取比赛名称、等级等信息</p>
      </div>
      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <div class="text-2xl mb-2">✅</div>
        <h3 class="font-semibold text-gray-800 mb-1">3. 确认提交</h3>
        <p class="text-sm text-gray-500">学生核对信息后一键确认</p>
      </div>
      <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100">
        <div class="text-2xl mb-2">📥</div>
        <h3 class="font-semibold text-gray-800 mb-1">4. 一键导出</h3>
        <p class="text-sm text-gray-500">辅导员导出 Excel 汇总表</p>
      </div>
    </div>
  </div>
</template>
