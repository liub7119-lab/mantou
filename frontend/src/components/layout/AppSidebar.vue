<template>
  <aside
    class="h-screen fixed left-0 top-0 z-40 hidden md:flex flex-col transition-all duration-300 ease-out"
    :class="expanded ? 'w-56' : 'w-[72px]'"
    style="background: #FFFFFF; border-right: 1px solid #E8ECF0;"
    @mouseenter="hovering = true"
    @mouseleave="hovering = false"
  >
    <!-- Logo -->
    <div class="h-[64px] flex items-center px-4 shrink-0 gap-2.5">
      <img src="/src/assets/ui/sidebar-cow.png" alt="小牛同学" class="w-10 h-10 rounded-full object-cover shrink-0" />
      <transition name="fade">
        <div v-show="expanded" class="whitespace-nowrap">
          <p class="text-sm font-bold" style="color: #333;">小牛同学</p>
          <p class="text-[10px]" style="color: #999;">学生服务平台</p>
        </div>
      </transition>
    </div>

    <!-- Nav -->
    <nav class="flex-1 py-4 px-3 space-y-1">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="group flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer transition-all duration-200 relative"
        :class="isActive(item.path) ? 'font-medium' : ''"
        :style="isActive(item.path)
          ? 'background: #6ECAFF; color: #FFFFFF; box-shadow: 0 4px 12px rgba(110,202,255,0.3);'
          : 'color: #666;'"
        @mouseenter="!isActive(item.path) && ($event.currentTarget.style.background = '#F2F4F7')"
        @mouseleave="!isActive(item.path) && ($event.currentTarget.style.background = 'transparent')"
      >
        <component :is="item.icon" class="w-5 h-5 shrink-0" />
        <transition name="fade">
          <span v-show="expanded" class="text-sm whitespace-nowrap">{{ item.label }}</span>
        </transition>
        <!-- Tooltip -->
        <div
          v-show="!expanded"
          class="absolute left-full ml-3 px-3 py-1.5 text-xs rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-150 z-50"
          style="background: #333; color: #FFF;"
        >
          {{ item.label }}
        </div>
      </router-link>
    </nav>

    <!-- Bottom -->
    <div class="px-3 py-4 space-y-1" style="border-top: 1px solid #E8ECF0;">
      <button
        @click="pinned = !pinned"
        class="flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer transition-all duration-200 w-full"
        style="color: #999;"
        @mouseenter="$event.currentTarget.style.background='#F2F4F7'"
        @mouseleave="$event.currentTarget.style.background='transparent'"
      >
        <Pin class="w-5 h-5 shrink-0 transition-transform duration-200" :class="pinned ? 'rotate-0' : '-rotate-45'" :style="pinned ? 'color: #6ECAFF;' : ''" />
        <transition name="fade">
          <span v-show="expanded" class="text-sm whitespace-nowrap">{{ pinned ? '收起侧栏' : '固定侧栏' }}</span>
        </transition>
      </button>

      <div class="flex items-center gap-3 px-3 py-2.5">
        <div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0" style="background: #E8F4FD;">
          <span class="text-xs font-semibold" style="color: #6ECAFF;">{{ userName?.charAt(0) }}</span>
        </div>
        <transition name="fade">
          <span v-show="expanded" class="text-sm truncate max-w-[120px]" style="color: #666;">{{ userName }}</span>
        </transition>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  Upload,
  MessageCircle,
  LayoutDashboard,
  MessageSquareText,
  Pin,
  ClipboardCheck,
  BarChart3,
  ScanLine,
  Home,
  UserCircle,
  Users,
} from 'lucide-vue-next'

const props = defineProps({
  role: { type: String, required: true },
  userName: { type: String, default: '' },
})

const route = useRoute()
const pinned = ref(false)
const hovering = ref(false)

const expanded = computed(() => pinned.value || hovering.value)

const emit = defineEmits(['update:expanded'])
watch(expanded, (val) => emit('update:expanded', val))

function isActive(path) {
  return route.path === path
}

const studentNav = [
  { path: '/', label: '首页', icon: Home },
  { path: '/upload', label: '成果上传', icon: Upload },
  { path: '/feedback', label: '树洞', icon: MessageCircle },
  { path: '/attendance', label: '扫码签到', icon: ScanLine },
  { path: '/profile', label: '成长画像', icon: UserCircle },
]

const monitorNav = [
  { path: '/', label: '首页', icon: Home },
  { path: '/attendance', label: '签到考勤', icon: ClipboardCheck },
  { path: '/upload', label: '成果上传', icon: Upload },
  { path: '/feedback', label: '树洞', icon: MessageCircle },
  { path: '/profile', label: '成长画像', icon: UserCircle },
]

const counselorNav = [
  { path: '/', label: '首页', icon: Home },
  { path: '/admin', label: '成果管理', icon: LayoutDashboard },
  { path: '/admin/feedback', label: '树洞管理', icon: MessageSquareText },
  { path: '/admin/attendance', label: '考勤管理', icon: BarChart3 },
  { path: '/admin/profile', label: '班级画像', icon: Users },
]

const navItems = computed(() => {
  if (props.role === 'counselor') return counselorNav
  if (props.role === 'monitor') return monitorNav
  return studentNav
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
