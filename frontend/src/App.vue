<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航 -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-14 items-center">
          <router-link to="/" class="text-lg font-bold text-blue-600">
            辅导员工作辅助平台
          </router-link>
          <div class="flex gap-4">
            <router-link
              to="/upload"
              class="text-sm text-gray-600 hover:text-blue-600 transition"
              active-class="text-blue-600 font-medium"
            >
              上传证书
            </router-link>
            <router-link
              to="/feedback"
              class="text-sm text-gray-600 hover:text-blue-600 transition"
              active-class="text-blue-600 font-medium"
            >
              树洞
            </router-link>
            <span class="text-gray-300">|</span>
            <router-link
              to="/admin"
              class="text-sm text-gray-600 hover:text-blue-600 transition"
              active-class="text-blue-600 font-medium"
            >
              成果管理
            </router-link>
            <router-link
              to="/admin/feedback"
              class="text-sm text-gray-600 hover:text-blue-600 transition"
              active-class="text-blue-600 font-medium"
            >
              树洞管理
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- 页面内容 -->
    <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <router-view />
    </main>
  </div>
</template>
