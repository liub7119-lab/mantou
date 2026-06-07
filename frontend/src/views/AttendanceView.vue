<template>
  <div>
    <div class="flex items-start justify-between mb-7">
      <div class="flex items-center gap-3 relative">
        <img src="/src/assets/ui/sticker-task.png" alt="" class="absolute -top-3 -left-3 w-7 h-7 opacity-25 pointer-events-none" />
        <div class="w-12 h-12 rounded-2xl flex items-center justify-center" style="background: #E8F4FD;">
          <ClipboardCheck class="w-5 h-5" style="color: #6ECAFF;" />
        </div>
        <div>
          <h2 class="text-lg font-bold" style="color: #1E293B;">签到考勤</h2>
          <p class="text-xs" style="color: #94A3B8;">纪律委员考勤管理</p>
        </div>
      </div>
    </div>

    <!-- Tab 切换 -->
    <div class="flex gap-2 mb-7">
      <button
        v-for="t in tabs" :key="t.key"
        @click="tab = t.key"
        class="px-5 py-2.5 text-sm font-medium rounded-full transition-all duration-200 cursor-pointer flex items-center gap-2"
        :style="tab === t.key
          ? `background: ${t.color}; color: white;`
          : 'background: #F1F5F9; color: #94A3B8;'"
      >
        <component :is="t.icon" class="w-4 h-4" />
        {{ t.label }}
      </button>
    </div>

    <!-- ========== 一键考勤 ========== -->
    <div v-if="tab === 'attendance'" class="space-y-6">
        <!-- 基本设置 -->
        <div class="bg-white rounded-3xl p-7" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
          <h3 class="text-sm font-semibold mb-4 flex items-center gap-2" style="color: #1E293B;">
            <Settings2 class="w-4 h-4" style="color: #3B82F6;" />
            基本设置
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-xs mb-1.5" style="color: #94A3B8;">选择班级</label>
              <select v-model="selectedClass" class="att-input cursor-pointer" @change="onClassChange">
                <option value="">请选择</option>
                <option v-for="c in classes" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs mb-1.5" style="color: #94A3B8;">教学周数</label>
              <input v-model.number="weekNumber" type="number" min="1" max="20" class="att-input" placeholder="如：第3周" />
            </div>
            <div>
              <label class="block text-xs mb-1.5" style="color: #94A3B8;">班级人数</label>
              <div class="att-input flex items-center" style="background: #ECFDF5;">
                <Users class="w-4 h-4 mr-2" style="color: #10B981;" />
                <span class="font-semibold" style="color: #10B981;">{{ classSize }}</span>
              </div>
            </div>
          </div>

          <!-- 花名册（内嵌） -->
          <div v-if="selectedClass" class="mt-5 pt-5" style="border-top: 1px solid #F1F5F9;">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-xs font-semibold flex items-center gap-2" style="color: #1E293B;">
                <Users class="w-3.5 h-3.5" style="color: #10B981;" />
                花名册
                <span v-if="rosterStudents.length" class="px-2 py-0.5 rounded-full text-[10px] font-medium" style="background: #ECFDF5; color: #10B981;">{{ rosterStudents.length }}人</span>
                <span v-if="rosterStudents.length" class="text-[10px] font-normal" style="color: #CBD5E1;">已保存</span>
              </h4>
              <div class="flex items-center gap-2">
                <button v-if="rosterStudents.length" @click="showRosterList = !showRosterList" class="text-[10px] px-3 py-1.5 rounded-full cursor-pointer transition-all" style="background: #F1F5F9; color: #64748B;">
                  {{ showRosterList ? '收起名单' : '展开名单' }}
                </button>
                <label class="px-3 py-1.5 rounded-full text-[10px] font-medium cursor-pointer transition-all flex items-center gap-1"
                  :style="rosterStudents.length ? 'background: #F1F5F9; color: #94A3B8;' : 'background: #ECFDF5; color: #10B981;'"
                >
                  <Upload class="w-3 h-3" />
                  {{ rosterStudents.length ? '重新导入' : '导入CSV' }}
                  <input type="file" accept=".csv" class="hidden" @change="handleRosterImport" />
                </label>
              </div>
            </div>

            <div v-if="classSize === 0" class="flex items-center gap-2 px-4 py-3 rounded-2xl" style="background: #FFFBEB;">
              <TriangleAlert class="w-4 h-4 shrink-0" style="color: #F59E0B;" />
              <p class="text-xs" style="color: #B45309;">该班级暂无花名册数据，请导入 CSV 花名册文件（需包含学号、姓名列）。</p>
            </div>

            <p v-if="rosterMsg" class="text-xs mb-2" :style="rosterMsgType === 'success' ? 'color: #10B981;' : 'color: #EF4444;'">{{ rosterMsg }}</p>

            <div v-if="rosterStudents.length && showRosterList" class="grid grid-cols-3 md:grid-cols-5 gap-1.5 mt-2">
              <div v-for="s in rosterStudents" :key="s.student_id" class="px-2.5 py-1.5 rounded-xl text-[11px]" style="background: #F8FAFC;">
                <span class="font-medium" style="color: #1E293B;">{{ s.name }}</span>
                <span class="ml-1" style="color: #CBD5E1;">{{ s.student_id?.slice(-4) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 填写考勤信息 -->
        <div v-if="selectedCourse" class="bg-white rounded-3xl p-7" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
          <h3 class="text-sm font-semibold mb-4 flex items-center gap-2" style="color: #1E293B;">
            <ClipboardList class="w-4 h-4" style="color: #F59E0B;" />
            填写考勤 — {{ selectedCourse.course_name }}
            <span class="text-[10px] font-normal px-2 py-0.5 rounded-lg" style="background: #EFF6FF; color: #3B82F6;">{{ selectedCourse.day_of_week }} {{ selectedCourse.period }}节</span>
          </h3>

          <!-- 上课日期（必填，由纪律委员填写真实上课日期，而非默认当天） -->
          <div class="mb-5">
            <label class="block text-xs mb-1.5 font-semibold flex items-center gap-1.5" style="color: #1E293B;">
              <CalendarDays class="w-3.5 h-3.5" style="color: #3B82F6;" />
              上课日期
              <span class="text-[10px] font-normal px-2 py-0.5 rounded-lg" style="background: #FEF2F2; color: #EF4444;">必填，请选择实际上课日期</span>
            </label>
            <input v-model="attDate" type="date" class="att-input md:w-60" />
            <p v-if="!attDate" class="text-[11px] mt-1.5" style="color: #F59E0B;">请选择本次课程的真实上课日期（不要使用默认当天日期）</p>
          </div>

          <!-- 六项考勤计数 -->
          <div class="grid grid-cols-3 md:grid-cols-6 gap-3 mb-5">
            <div>
              <label class="block text-[10px] mb-1" style="color: #3B82F6;">病假</label>
              <input v-model.number="attForm.sick_leave_count" type="number" min="0" class="att-input text-center" readonly />
            </div>
            <div>
              <label class="block text-[10px] mb-1" style="color: #10B981;">公假</label>
              <input v-model.number="attForm.official_leave_count" type="number" min="0" class="att-input text-center" readonly />
            </div>
            <div>
              <label class="block text-[10px] mb-1" style="color: #F59E0B;">事假</label>
              <input v-model.number="attForm.personal_leave_count" type="number" min="0" class="att-input text-center" readonly />
            </div>
            <div>
              <label class="block text-[10px] mb-1" style="color: #EC4899;">迟到</label>
              <input v-model.number="attForm.late_count" type="number" min="0" class="att-input text-center" readonly />
            </div>
            <div>
              <label class="block text-[10px] mb-1" style="color: #8B5CF6;">早退</label>
              <input v-model.number="attForm.early_leave_count" type="number" min="0" class="att-input text-center" readonly />
            </div>
            <div>
              <label class="block text-[10px] mb-1" style="color: #EF4444;">旷课</label>
              <input v-model.number="attForm.absent_count" type="number" min="0" class="att-input text-center" readonly />
            </div>
          </div>

          <!-- 自动计算预览 -->
          <div class="grid grid-cols-3 gap-3 mb-5">
            <div class="rounded-2xl p-4 text-center" style="background: #ECFDF5;">
              <p class="text-[10px] mb-1" style="color: #94A3B8;">实到人数</p>
              <p class="text-lg font-bold" style="color: #10B981;">{{ computedActual }}</p>
            </div>
            <div class="rounded-2xl p-4 text-center" style="background: #EFF6FF;">
              <p class="text-[10px] mb-1" style="color: #94A3B8;">到课率</p>
              <p class="text-lg font-bold" style="color: #3B82F6;">{{ computedRate }}</p>
            </div>
            <div class="rounded-2xl p-4 text-center" style="background: #FDF2F8;">
              <p class="text-[10px] mb-1" style="color: #94A3B8;">到课率（含请假）</p>
              <p class="text-lg font-bold" style="color: #EC4899;">{{ computedRateWithLeave }}</p>
            </div>
          </div>

          <!-- 选择学生 + 原因（六种类型全部可选） -->
          <div class="mb-5">
            <label class="block text-xs mb-2" style="color: #94A3B8;">点选未正常到课的学生，选择原因后自动同步上方人数</label>
            <div v-if="rosterStudents.length > 0" class="mb-3">
              <div class="flex flex-wrap gap-1.5 mb-3 max-h-40 overflow-y-auto p-2 rounded-xl" style="background: #F8FAFC;">
                <button
                  v-for="s in rosterStudents" :key="s.student_id"
                  @click="toggleLeaveStudent(s)"
                  class="px-3 py-1.5 text-[11px] rounded-full cursor-pointer transition-all"
                  :style="leaveStudents.has(s.student_id)
                    ? `background: ${leaveTypeColor(leaveReasons[s.student_id])}15; color: ${leaveTypeColor(leaveReasons[s.student_id])}; font-weight: 600; box-shadow: 0 0 0 1px ${leaveTypeColor(leaveReasons[s.student_id])}40;`
                    : 'background: #F1F5F9; color: #64748B;'"
                >
                  {{ s.name }}
                  <span v-if="leaveStudents.has(s.student_id)" class="ml-0.5 text-[9px] opacity-70">{{ leaveReasons[s.student_id] }}</span>
                </button>
              </div>
              <div v-if="leaveStudents.size > 0" class="space-y-2">
                <div v-for="sid in leaveStudents" :key="sid" class="flex items-center gap-2">
                  <span class="text-xs font-medium w-16 shrink-0" style="color: #1E293B;">{{ getStudentName(sid) }}</span>
                  <select v-model="leaveReasons[sid]" @change="syncCounts" class="att-input-sm flex-1 cursor-pointer">
                    <option value="病假">病假</option>
                    <option value="公假">公假</option>
                    <option value="事假">事假</option>
                    <option value="迟到">迟到</option>
                    <option value="早退">早退</option>
                    <option value="旷课">旷课</option>
                  </select>
                  <label class="shrink-0 w-7 h-7 rounded-lg flex items-center justify-center cursor-pointer transition-all"
                    :style="leaveImages[sid] ? 'background: #ECFDF5;' : 'background: #FEF2F2;'"
                  >
                    <Loader2 v-if="uploadingImage[sid]" class="w-3.5 h-3.5 animate-spin" style="color: #3B82F6;" />
                    <ImageIcon v-else-if="leaveImages[sid]" class="w-3.5 h-3.5" style="color: #10B981;" />
                    <Camera v-else class="w-3.5 h-3.5" style="color: #EF4444;" />
                    <input type="file" accept="image/*" class="hidden" @change="handleLeaveImageUpload(sid, $event)" />
                  </label>
                  <button @click="removeLeaveStudent(sid)" class="w-6 h-6 rounded-full flex items-center justify-center cursor-pointer" style="background: #FEF2F2;">
                    <X class="w-3 h-3" style="color: #EF4444;" />
                  </button>
                </div>
              </div>
            </div>
            <textarea v-model="attForm.leave_details" rows="2" class="att-textarea" placeholder="补充说明（可选）"></textarea>
          </div>

          <!-- 教室照片上传（必须2张） -->
          <div class="mb-5">
            <label class="block text-xs mb-2 font-semibold flex items-center gap-1.5" style="color: #1E293B;">
              <Camera class="w-3.5 h-3.5" style="color: #3B82F6;" />
              教室照片
              <span class="text-[10px] font-normal px-2 py-0.5 rounded-lg" style="background: #FEF2F2; color: #EF4444;">必须上传2张</span>
            </label>
            <p class="text-[11px] mb-3" style="color: #94A3B8;">请拍摄教室全景照片，用于考勤核实</p>
            <div class="flex gap-3">
              <div v-for="(photo, idx) in classroomPhotos" :key="idx" class="relative w-28 h-28 rounded-2xl overflow-hidden group" style="background: #F8FAFC;">
                <img :src="getAssetUrl(photo)" class="w-full h-full object-cover" />
                <button @click="removeClassroomPhoto(idx)" class="absolute top-1.5 right-1.5 w-6 h-6 rounded-full flex items-center justify-center cursor-pointer opacity-0 group-hover:opacity-100 transition-opacity" style="background: rgba(239,68,68,0.9);">
                  <X class="w-3 h-3 text-white" />
                </button>
                <div class="absolute bottom-0 left-0 right-0 px-2 py-1 text-[9px] text-white text-center" style="background: rgba(0,0,0,0.4);">
                  照片{{ idx + 1 }}
                </div>
              </div>
              <label v-if="classroomPhotos.length < 2" class="w-28 h-28 rounded-2xl flex flex-col items-center justify-center cursor-pointer transition-all hover:shadow-md" :style="uploadingClassroomPhoto ? 'background: #EFF6FF; border: 2px dashed #93C5FD;' : 'background: #F8FAFC; border: 2px dashed #CBD5E1;'">
                <Loader2 v-if="uploadingClassroomPhoto" class="w-6 h-6 animate-spin mb-1" style="color: #3B82F6;" />
                <template v-else>
                  <ImagePlus class="w-6 h-6 mb-1" style="color: #94A3B8;" />
                  <span class="text-[10px]" style="color: #94A3B8;">点击上传</span>
                </template>
                <input type="file" accept="image/*" class="hidden" @change="handleClassroomPhotoUpload" :disabled="uploadingClassroomPhoto" />
              </label>
            </div>
            <div v-if="classroomPhotos.length < 2" class="flex items-center gap-1.5 mt-2 px-3 py-2 rounded-xl" style="background: #FFFBEB;">
              <TriangleAlert class="w-3.5 h-3.5 shrink-0" style="color: #F59E0B;" />
              <span class="text-[11px]" style="color: #B45309;">还需上传 {{ 2 - classroomPhotos.length }} 张教室照片才能提交考勤</span>
            </div>
          </div>

          <button
            @click="submitAttendance"
            :disabled="submitting || !canSubmitAttendance"
            class="w-full py-3 rounded-full text-sm font-medium text-white cursor-pointer flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            style="background: linear-gradient(135deg, #3B82F6, #10B981);"
          >
            <Loader2 v-if="submitting" class="w-4 h-4 animate-spin" />
            <Check v-else class="w-4 h-4" />
            {{ submitting ? '提交中...' : !attDate ? '请选择上课日期' : classroomPhotos.length < 2 ? '请上传2张教室照片' : !allLeaveImagesUploaded ? '请上传所有假条图片' : '提交考勤' }}
          </button>
        </div>

        <!-- 历史记录 -->
        <div v-if="records.length > 0" class="bg-white rounded-3xl p-7" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-semibold flex items-center gap-2" style="color: #1E293B;">
              <History class="w-4 h-4" style="color: #94A3B8;" />
              考勤记录
            </h3>
            <button @click="exportRecords" class="px-4 py-2 rounded-full text-[11px] font-medium cursor-pointer flex items-center gap-1.5" style="background: #EFF6FF; color: #3B82F6;">
              <Download class="w-3.5 h-3.5" />
              导出表格
            </button>
          </div>
          <div class="space-y-3">
            <div v-for="r in records" :key="r.id" class="flex items-center gap-3 px-4 py-3 rounded-2xl" style="background: #F8FAFC;">
              <span class="text-xs font-medium" style="color: #1E293B;">{{ r.date_str }} {{ r.day_of_week }}</span>
              <span class="text-xs" style="color: #94A3B8;">{{ r.period }}节</span>
              <span class="text-xs font-medium flex-1" style="color: #475569;">{{ r.course_name }}</span>
              <span class="px-2 py-1 rounded-lg text-[10px] font-semibold"
                :style="parseInt(r.attendance_rate) >= 95 ? 'background: #ECFDF5; color: #10B981;' :
                         parseInt(r.attendance_rate) >= 90 ? 'background: #FFFBEB; color: #F59E0B;' :
                         'background: #FEF2F2; color: #EF4444;'"
              >{{ r.attendance_rate }}</span>
            </div>
          </div>
        </div>
    </div>

    <!-- ========== 签到抽查 ========== -->
    <div v-if="tab === 'checkin'" class="space-y-6">
        <!-- 移动端课程选择（桌面端使用右侧面板） -->
        <div class="lg:hidden bg-white rounded-3xl p-7" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
          <h3 class="text-sm font-semibold mb-4 flex items-center gap-2" style="color: #1E293B;">
            <QrCode class="w-4 h-4" style="color: #8B5CF6;" />
            选择课程
          </h3>
          <div class="grid grid-cols-1 gap-3 mb-4">
            <div>
              <label class="block text-xs mb-1.5" style="color: #94A3B8;">班级</label>
              <select v-model="mobileCheckinClass" class="att-input cursor-pointer" @change="loadMobileCheckinCourses">
                <option value="">请选择班级</option>
                <option v-for="c in classes" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div v-if="mobileCheckinCourseList.length > 0">
              <label class="block text-xs mb-1.5" style="color: #94A3B8;">课程</label>
              <div class="space-y-1.5 max-h-48 overflow-y-auto">
                <div v-for="c in mobileCheckinCourseList" :key="c.id"
                  class="px-3 py-2 rounded-xl text-[11px] cursor-pointer transition-all"
                  :style="mobileSelectedCheckinCourse?.id === c.id
                    ? 'background: #F5F3FF; box-shadow: 0 0 0 1.5px #8B5CF6;'
                    : 'background: #F8FAFC;'"
                  @click="selectMobileCheckinCourse(c)"
                >
                  <span class="font-medium" style="color: #1E293B;">{{ c.course_name }}</span>
                  <span class="text-[9px] ml-1" style="color: #94A3B8;">{{ c.day_of_week }} {{ c.period }}节</span>
                </div>
              </div>
            </div>
          </div>
          <div v-if="mobileSelectedCheckinCourse" class="px-4 py-3 rounded-2xl" style="background: #ECFDF5;">
            <p class="text-xs font-medium" style="color: #10B981;">已选择：{{ mobileCheckinClass }} · {{ mobileSelectedCheckinCourse.course_name }}</p>
          </div>
        </div>

        <!-- 创建签到 -->
        <div v-if="!activeSession" class="bg-white rounded-3xl p-7" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
          <h3 class="text-sm font-semibold mb-4 flex items-center gap-2" style="color: #1E293B;">
            <QrCode class="w-4 h-4" style="color: #8B5CF6;" />
            发起签到
          </h3>
          <p class="text-xs mb-4 hidden lg:block" style="color: #94A3B8;">从右侧课程日历选择课程</p>
          <div v-if="!effectiveCheckinClass || !effectiveCheckinCourse" class="mb-5 px-4 py-3 rounded-2xl flex items-center gap-2" style="background: #FFFBEB;">
            <TriangleAlert class="w-4 h-4 shrink-0" style="color: #F59E0B;" />
            <p class="text-xs" style="color: #B45309;">请选择课程后发起签到</p>
          </div>
          <div v-else class="mb-5 px-4 py-3 rounded-2xl" style="background: #ECFDF5;">
            <p class="text-xs font-medium mb-1" style="color: #10B981;">已选择课程</p>
            <p class="text-sm" style="color: #1E293B;">{{ effectiveCheckinClass }} · {{ effectiveCheckinCourse }}</p>
          </div>
          <div class="mb-5">
            <label class="block text-xs mb-1.5" style="color: #94A3B8;">签到时长（分钟）</label>
            <div class="flex items-center gap-2">
              <input v-model.number="checkinExpire" type="range" min="1" max="30" class="flex-1 accent-purple-500" />
              <span class="text-sm font-semibold w-10 text-center" style="color: #7C3AED;">{{ checkinExpire }}</span>
            </div>
            <div class="flex justify-between text-[10px] mt-1" style="color: #CBD5E1;">
              <span>1分钟</span>
              <span>30分钟</span>
            </div>
          </div>
          <button
            @click="startCheckIn"
            :disabled="!effectiveCheckinClass || !effectiveCheckinCourse || creatingSession"
            class="px-6 py-3 rounded-full text-sm font-medium text-white cursor-pointer flex items-center gap-2 transition-all disabled:opacity-50"
            style="background: linear-gradient(135deg, #8B5CF6, #6366F1);"
          >
            <Loader2 v-if="creatingSession" class="w-4 h-4 animate-spin" />
            <QrCode v-else class="w-4 h-4" />
            {{ creatingSession ? '生成中...' : '生成签到二维码' }}
          </button>
        </div>

        <!-- 签到二维码展示 -->
        <div v-if="activeSession" class="bg-white rounded-3xl p-7 text-center" style="box-shadow: 0 2px 16px rgba(139,92,246,0.1);">
          <p class="text-xs mb-3" style="color: #94A3B8;">{{ activeSession.class_name }} · {{ activeSession.course_name || '课程签到' }}</p>
          <div class="inline-block p-4 rounded-2xl mb-4" style="background: #FAFAFA;">
            <canvas ref="qrCanvas"></canvas>
          </div>
          <p class="text-xs mb-1" style="color: #94A3B8;">扫描二维码或输入签到码</p>
          <p class="text-lg font-bold tracking-widest mb-1" style="color: #7C3AED;">{{ activeSession.code }}</p>
          <p class="text-[10px] mb-4" style="color: #CBD5E1;">有效期 {{ activeSession.expire_minutes }} 分钟</p>

          <div class="grid grid-cols-2 gap-4 mb-5">
            <div class="rounded-2xl p-4" style="background: #ECFDF5;">
              <p class="text-2xl font-bold" style="color: #10B981;">{{ checkinStatus?.checked_count || 0 }}</p>
              <p class="text-[10px]" style="color: #94A3B8;">已签到</p>
            </div>
            <div class="rounded-2xl p-4" style="background: #FEF2F2;">
              <p class="text-2xl font-bold" style="color: #EF4444;">{{ (checkinStatus?.roster_count || 0) - (checkinStatus?.checked_count || 0) }}</p>
              <p class="text-[10px]" style="color: #94A3B8;">未签到</p>
            </div>
          </div>

          <div v-if="checkinStatus?.not_checked_list?.length > 0" class="text-left mb-4">
            <p class="text-xs font-medium mb-2" style="color: #EF4444;">未签到学生：</p>
            <div class="flex flex-wrap gap-1.5">
              <span v-for="s in checkinStatus.not_checked_list" :key="s.student_id" class="px-3 py-1 rounded-full text-[11px]" style="background: #FEF2F2; color: #EF4444;">
                {{ s.name }}
              </span>
            </div>
          </div>

          <div class="flex gap-3 justify-center">
            <button @click="refreshCheckInStatus" class="px-5 py-2.5 rounded-full text-xs font-medium cursor-pointer flex items-center gap-1.5" style="background: #EFF6FF; color: #3B82F6;">
              <RefreshCw class="w-3.5 h-3.5" />
              刷新
            </button>
            <button @click="endCheckIn" class="px-5 py-2.5 rounded-full text-xs font-medium cursor-pointer flex items-center gap-1.5" style="background: #FEF2F2; color: #EF4444;">
              <XCircle class="w-3.5 h-3.5" />
              结束签到
            </button>
          </div>
        </div>

        <!-- 历史签到会话 -->
        <div v-if="checkinSessions.length > 0" class="bg-white rounded-3xl p-7" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
          <h3 class="text-sm font-semibold mb-4 flex items-center gap-2" style="color: #1E293B;">
            <History class="w-4 h-4" style="color: #94A3B8;" />
            签到历史
          </h3>
          <div class="space-y-3">
            <div v-for="s in checkinSessions" :key="s.id"
              class="flex items-center gap-3 px-4 py-3 rounded-2xl cursor-pointer transition-all"
              style="background: #F8FAFC;"
              @click="s.is_active ? resumeCheckIn(s) : null"
              :class="s.is_active ? 'hover:shadow-md' : ''"
            >
              <span class="text-xs font-medium" style="color: #1E293B;">{{ formatTime(s.created_at) }}</span>
              <span class="text-xs flex-1" style="color: #475569;">{{ s.class_name }} · {{ s.course_name || '签到' }}</span>
              <span class="px-2 py-1 rounded-lg text-[10px] font-medium" style="background: #ECFDF5; color: #10B981;">{{ s.log_count }}人</span>
              <span class="px-2 py-1 rounded-lg text-[10px]" :style="s.is_active ? 'background: #EFF6FF; color: #3B82F6;' : 'background: #F1F5F9; color: #94A3B8;'">
                {{ s.is_active ? '进行中 →' : '已结束' }}
              </span>
            </div>
          </div>
        </div>
    </div>

    <!-- 学生端签到入口 -->
    <div v-if="tab === 'scan'" class="space-y-6">
      <div class="bg-white rounded-3xl p-7 text-center" style="box-shadow: 0 2px 16px rgba(125,175,206,0.06);">
        <QrCode class="w-12 h-12 mx-auto mb-4" style="color: #8B5CF6;" />
        <h3 class="text-base font-semibold mb-2" style="color: #1E293B;">扫码签到</h3>
        <p class="text-xs mb-5" style="color: #94A3B8;">请扫描纪律委员提供的二维码完成签到</p>
        <div class="max-w-xs mx-auto">
          <div class="mb-4">
            <label class="block text-xs mb-2" style="color: #94A3B8;">签到状态</label>
            <select v-model="scanStatus" class="att-input cursor-pointer">
              <option value="正常">正常</option>
              <option value="病假">病假</option>
              <option value="公假">公假</option>
              <option value="事假">事假</option>
              <option value="迟到">迟到</option>
              <option value="早退">早退</option>
            </select>
          </div>
          <button
            @click="doScan"
            :disabled="!scanCode.trim() || scanning"
            class="w-full py-3 rounded-full text-sm font-medium text-white cursor-pointer flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            style="background: linear-gradient(135deg, #8B5CF6, #6366F1);"
          >
            <Loader2 v-if="scanning" class="w-4 h-4 animate-spin" />
            <Check v-else class="w-4 h-4" />
            {{ scanning ? '签到中...' : '签到' }}
          </button>
        </div>
        <p v-if="scanMsg" class="mt-4 text-sm font-medium" :style="scanMsgType === 'success' ? 'color: #10B981;' : 'color: #EF4444;'">{{ scanMsg }}</p>
      </div>
    </div>

    <!-- 提示 -->
    <div v-if="globalMsg" class="fixed bottom-6 right-6 z-50 px-5 py-3 rounded-2xl text-sm font-medium text-white animate-bounce"
      :style="globalMsgType === 'success' ? 'background: #10B981;' : 'background: #EF4444;'"
    >
      {{ globalMsg }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch, nextTick } from 'vue'
import {
  ClipboardCheck, ClipboardList, Settings2, Users, X, Check,
  Loader2, History, QrCode, RefreshCw, XCircle, Upload,
  TriangleAlert, ScanLine, Camera, ImageIcon, ImagePlus, Download, CalendarDays,
} from 'lucide-vue-next'
import QRCode from 'qrcode'
import {
  getRosterClasses, getClassSize, getRoster, importRoster,
  parseScheduleImage, batchAddSchedule, getSchedule,
  createAttendanceRecord, listAttendanceRecords, uploadLeaveSlip, uploadClassroomPhoto,
  createCheckInSession, doCheckIn as apiCheckIn, getCheckInStatus, closeCheckIn, listCheckInSessions,
  getAssetUrl, exportAttendanceRecords,
} from '../api'
import { useAttendanceCalendar } from '../lib/useAttendanceCalendar'

const calStore = useAttendanceCalendar()

const user = JSON.parse(localStorage.getItem('user') || '{}')
const isMonitor = user.role === 'monitor' || user.role === 'counselor'

const tabs = computed(() => {
  if (!isMonitor) {
    return [{ key: 'scan', label: '扫码签到', icon: ScanLine, color: '#8B5CF6' }]
  }
  return [
    { key: 'attendance', label: '一键考勤', icon: ClipboardCheck, color: '#3B82F6' },
    { key: 'checkin', label: '签到抽查', icon: QrCode, color: '#8B5CF6' },
    { key: 'scan', label: '扫码签到', icon: ScanLine, color: '#10B981' },
  ]
})

const tab = ref(isMonitor ? 'attendance' : 'scan')
watch(tab, (v) => { calStore.currentTab.value = v })
calStore.currentTab.value = tab.value

const { classes, selectedClass, weekNumber, classSize, courses, selectedCourse,
  parsingSchedule, parsedCourses, showAddCourse, newCourse,
  checkinCalClass, checkinCourses, checkinClass, checkinCourse, checkinScheduleId,
  dayColor } = calStore

watch(weekNumber, () => {
  if (selectedClass.value) {
    loadCourses()
    loadRecords()
  }
})

watch(() => calStore.selectedCourse.value, (c) => {
  if (c) selectCourse(c)
})

watch(() => calStore._parseImageEvent.value, (e) => {
  if (e) handleScheduleImage(e)
})

watch(() => calStore._confirmParsedFlag.value, (v) => {
  if (v) confirmParsedCourses()
})

watch(() => calStore._addCourseFlag.value, (v) => {
  if (v) addCourseManually()
})

watch(() => calStore._loadCheckinCoursesFlag.value, (v) => {
  if (v) loadCheckinCourses()
})

watch(() => calStore._coursesUpdatedFlag.value, (v) => {
  if (v) loadCourses()
})

const attForm = reactive({
  sick_leave_count: 0,
  official_leave_count: 0,
  personal_leave_count: 0,
  late_count: 0,
  early_leave_count: 0,
  absent_count: 0,
  leave_details: '',
})
const submitting = ref(false)
const records = ref([])
const attDate = ref('')

// 把课表里的 date_str（如 "3.2"）转换为 date 输入框可用的 YYYY-MM-DD
function isoFromDateStr(s) {
  if (!s) return ''
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s
  const m = s.match(/^(\d{1,2})\s*[.\-/]\s*(\d{1,2})$/)
  if (m) {
    const year = new Date().getFullYear()
    return `${year}-${String(m[1]).padStart(2, '0')}-${String(m[2]).padStart(2, '0')}`
  }
  return ''
}

const rosterStudents = ref([])
const showRosterList = ref(true)
const leaveStudents = reactive(new Set())
const leaveReasons = reactive({})
const leaveImages = reactive({})
const uploadingImage = reactive({})
const rosterMsg = ref('')
const rosterMsgType = ref('success')

const classroomPhotos = ref([])
const uploadingClassroomPhoto = ref(false)

const checkinExpire = ref(5)
const creatingSession = ref(false)
const activeSession = ref(null)
const checkinStatus = ref(null)
const checkinSessions = ref([])
const qrCanvas = ref(null)

const scanCode = ref('')
const scanStatus = ref('正常')
const scanning = ref(false)
const scanMsg = ref('')
const scanMsgType = ref('success')

const mobileCheckinClass = ref('')
const mobileCheckinCourseList = ref([])
const mobileSelectedCheckinCourse = ref(null)

const effectiveCheckinClass = computed(() => checkinClass.value || mobileCheckinClass.value)
const effectiveCheckinCourse = computed(() => checkinCourse.value || mobileSelectedCheckinCourse.value?.course_name || '')

async function loadMobileCheckinCourses() {
  mobileSelectedCheckinCourse.value = null
  if (!mobileCheckinClass.value) { mobileCheckinCourseList.value = []; return }
  try {
    const { data } = await getSchedule(mobileCheckinClass.value, 0)
    mobileCheckinCourseList.value = data
  } catch { mobileCheckinCourseList.value = [] }
}

function selectMobileCheckinCourse(c) {
  mobileSelectedCheckinCourse.value = c
}

const globalMsg = ref('')
const globalMsgType = ref('success')

function showGlobalMsg(msg, type = 'success') {
  globalMsg.value = msg
  globalMsgType.value = type
  setTimeout(() => { globalMsg.value = '' }, 3000)
}

function formatTime(t) {
  return new Date(t).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function leaveTypeColor(type) {
  const map = { '病假': '#3B82F6', '公假': '#10B981', '事假': '#F59E0B', '迟到': '#EC4899', '早退': '#8B5CF6', '旷课': '#EF4444' }
  return map[type] || '#94A3B8'
}

// 到课率计算：实到人数 / 班级人数
const computedAbsentTotal = computed(() => attForm.absent_count)
const computedLeaveTotal = computed(() => attForm.sick_leave_count + attForm.official_leave_count + attForm.personal_leave_count)
const computedActual = computed(() => Math.max(0, classSize.value - computedLeaveTotal.value - attForm.late_count - attForm.early_leave_count - computedAbsentTotal.value))
const computedRate = computed(() => {
  if (classSize.value <= 0) return '0%'
  return `${Math.round(computedActual.value / classSize.value * 100)}%`
})
const computedRateWithLeave = computed(() => {
  if (classSize.value <= 0) return '0%'
  const withLeave = computedActual.value + attForm.sick_leave_count + attForm.official_leave_count
  return `${Math.round(withLeave / classSize.value * 100)}%`
})

// 自动同步计数：根据选中的学生和原因统计
function syncCounts() {
  const counts = { '病假': 0, '公假': 0, '事假': 0, '迟到': 0, '早退': 0, '旷课': 0 }
  for (const sid of leaveStudents) {
    const r = leaveReasons[sid] || '病假'
    counts[r]++
  }
  attForm.sick_leave_count = counts['病假']
  attForm.official_leave_count = counts['公假']
  attForm.personal_leave_count = counts['事假']
  attForm.late_count = counts['迟到']
  attForm.early_leave_count = counts['早退']
  attForm.absent_count = counts['旷课']
}

async function toggleLeaveStudent(s) {
  if (leaveStudents.has(s.student_id)) {
    leaveStudents.delete(s.student_id)
    delete leaveReasons[s.student_id]
    delete leaveImages[s.student_id]
    delete uploadingImage[s.student_id]
  } else {
    leaveStudents.add(s.student_id)
    leaveReasons[s.student_id] = '病假'
  }
  await nextTick()
  syncCounts()
}


async function removeLeaveStudent(sid) {
  leaveStudents.delete(sid)
  delete leaveReasons[sid]
  delete leaveImages[sid]
  delete uploadingImage[sid]
  await nextTick()
  syncCounts()
}

function getStudentName(sid) {
  return rosterStudents.value.find(s => s.student_id === sid)?.name || sid
}

async function handleLeaveImageUpload(sid, e) {
  const file = e.target.files?.[0]
  if (!file) return
  uploadingImage[sid] = true
  try {
    const { data } = await uploadLeaveSlip(file)
    leaveImages[sid] = data.image_path
  } catch (err) {
    showGlobalMsg('图片上传失败', 'error')
  } finally {
    uploadingImage[sid] = false
  }
  e.target.value = ''
}

const allLeaveImagesUploaded = computed(() => {
  if (leaveStudents.size === 0) return true
  for (const sid of leaveStudents) {
    if (!leaveImages[sid]) return false
  }
  return true
})

const canSubmitAttendance = computed(() => {
  return !!attDate.value && allLeaveImagesUploaded.value && classroomPhotos.value.length >= 2
})

async function handleClassroomPhotoUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (classroomPhotos.value.length >= 2) {
    showGlobalMsg('最多上传2张教室照片', 'error')
    e.target.value = ''
    return
  }
  uploadingClassroomPhoto.value = true
  try {
    const { data } = await uploadClassroomPhoto(file)
    classroomPhotos.value.push(data.image_path)
  } catch (err) {
    showGlobalMsg('教室照片上传失败', 'error')
  } finally {
    uploadingClassroomPhoto.value = false
  }
  e.target.value = ''
}

function removeClassroomPhoto(index) {
  classroomPhotos.value.splice(index, 1)
}

async function onClassChange() {
  if (!selectedClass.value) {
    classSize.value = 0
    courses.value = []
    records.value = []
    rosterStudents.value = []
    return
  }
  try {
    const [sizeRes, rosterRes] = await Promise.all([
      getClassSize(selectedClass.value),
      getRoster(selectedClass.value),
    ])
    classSize.value = sizeRes.data.size
    rosterStudents.value = rosterRes.data
  } catch {}
  loadCourses()
  loadRecords()
}

async function loadCourses() {
  if (!selectedClass.value) return
  try {
    const { data } = await getSchedule(selectedClass.value, weekNumber.value)
    courses.value = data
  } catch {}
}

async function loadRecords() {
  if (!selectedClass.value) return
  try {
    const { data } = await listAttendanceRecords(selectedClass.value, weekNumber.value)
    records.value = data
  } catch {}
}

async function exportRecords() {
  try {
    const res = await exportAttendanceRecords(selectedClass.value, weekNumber.value)
    const blob = new Blob([res.data], { type: 'text/csv;charset=utf-8;' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `考勤记录_${selectedClass.value || '全部'}_第${weekNumber.value}周.csv`
    a.style.display = 'none'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    showGlobalMsg('导出失败', 'error')
  }
}

async function loadRoster() {
  try {
    const { data } = await getRoster(selectedClass.value)
    rosterStudents.value = data
  } catch {}
}

async function loadCheckinCourses() {
  if (!checkinCalClass.value) { checkinCourses.value = []; return }
  try {
    const { data } = await getSchedule(checkinCalClass.value, 0)
    checkinCourses.value = data
  } catch {}
}

async function handleScheduleImage(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (!selectedClass.value || !weekNumber.value) {
    showGlobalMsg('请先选择班级和周数', 'error')
    return
  }
  parsingSchedule.value = true
  try {
    const { data } = await parseScheduleImage(file, selectedClass.value, weekNumber.value)
    parsedCourses.value = data.courses || []
    if (parsedCourses.value.length === 0) showGlobalMsg('未识别到课程信息', 'error')
  } catch (err) {
    showGlobalMsg(err.response?.data?.detail || '课表识别失败', 'error')
  } finally {
    parsingSchedule.value = false
    e.target.value = ''
  }
}

async function confirmParsedCourses() {
  try {
    await batchAddSchedule(parsedCourses.value)
    parsedCourses.value = []
    showGlobalMsg('课程已保存')
    loadCourses()
  } catch (err) {
    showGlobalMsg(err.response?.data?.detail || '保存失败', 'error')
  }
}

async function addCourseManually() {
  if (!newCourse.value.course_name) return
  try {
    await batchAddSchedule([{
      class_name: selectedClass.value,
      week_number: weekNumber.value,
      ...newCourse.value,
    }])
    showAddCourse.value = false
    newCourse.value = { day_of_week: '周一', period: '', course_name: '', teacher: '', classroom: '', date_str: '' }
    showGlobalMsg('课程已添加')
    loadCourses()
  } catch (err) {
    showGlobalMsg(err.response?.data?.detail || '添加失败', 'error')
  }
}

function selectCourse(c) {
  selectedCourse.value = c
  attDate.value = isoFromDateStr(c.date_str)
  Object.assign(attForm, { sick_leave_count: 0, official_leave_count: 0, personal_leave_count: 0, late_count: 0, early_leave_count: 0, absent_count: 0, leave_details: '' })
  leaveStudents.clear()
  Object.keys(leaveReasons).forEach(k => delete leaveReasons[k])
  Object.keys(leaveImages).forEach(k => delete leaveImages[k])
  Object.keys(uploadingImage).forEach(k => delete uploadingImage[k])
  classroomPhotos.value = []
}

function buildLeaveDetails() {
  if (leaveStudents.size === 0) return attForm.leave_details
  const grouped = {}
  for (const sid of leaveStudents) {
    const reason = leaveReasons[sid] || '病假'
    if (!grouped[reason]) grouped[reason] = []
    grouped[reason].push(getStudentName(sid))
  }
  const parts = Object.entries(grouped).map(([reason, names]) => `${names.join('，')}${reason}`)
  const auto = parts.join('，')
  return attForm.leave_details ? `${auto}；${attForm.leave_details}` : auto
}

async function submitAttendance() {
  if (!selectedCourse.value) return
  if (!attDate.value) {
    showGlobalMsg('请先选择上课日期', 'error')
    return
  }
  submitting.value = true
  try {
    const details = buildLeaveDetails()
    const leaveSlipsList = []
    for (const sid of leaveStudents) {
      if (leaveImages[sid]) {
        leaveSlipsList.push({
          student_id: sid,
          student_name: getStudentName(sid),
          reason: leaveReasons[sid] || '病假',
          image_path: leaveImages[sid],
        })
      }
    }
    await createAttendanceRecord({
      schedule_id: selectedCourse.value.id,
      class_name: selectedClass.value,
      date_str: attDate.value,
      day_of_week: selectedCourse.value.day_of_week,
      period: selectedCourse.value.period,
      course_name: selectedCourse.value.course_name,
      teacher: selectedCourse.value.teacher,
      classroom: selectedCourse.value.classroom,
      class_size: classSize.value,
      sick_leave_count: attForm.sick_leave_count + attForm.official_leave_count,
      personal_leave_count: attForm.personal_leave_count,
      late_count: attForm.late_count,
      early_leave_count: attForm.early_leave_count,
      absent_count: attForm.absent_count,
      leave_details: details,
      week_number: weekNumber.value,
      leave_slips: leaveSlipsList,
      classroom_photos: classroomPhotos.value,
    })
    showGlobalMsg('考勤提交成功')
    selectedCourse.value = null
    attDate.value = ''
    leaveStudents.clear()
    Object.keys(leaveReasons).forEach(k => delete leaveReasons[k])
    Object.keys(leaveImages).forEach(k => delete leaveImages[k])
    Object.keys(uploadingImage).forEach(k => delete uploadingImage[k])
    classroomPhotos.value = []
    loadRecords()
  } catch (err) {
    showGlobalMsg(err.response?.data?.detail || '提交失败', 'error')
  } finally {
    submitting.value = false
  }
}

// QR码生成
async function renderQR(code) {
  await nextTick()
  if (!qrCanvas.value) return
  const url = `${window.location.origin}/attendance?checkin=${code}`
  QRCode.toCanvas(qrCanvas.value, url, {
    width: 200,
    margin: 2,
    color: { dark: '#7C3AED', light: '#FFFFFF' },
  })
}

async function startCheckIn() {
  const cls = effectiveCheckinClass.value
  const course = effectiveCheckinCourse.value
  if (!cls || !course) return
  creatingSession.value = true
  try {
    const scheduleId = checkinScheduleId.value || mobileSelectedCheckinCourse.value?.id || null
    const { data } = await createCheckInSession({
      class_name: cls,
      course_name: course,
      expire_minutes: checkinExpire.value,
      schedule_id: scheduleId,
    })
    activeSession.value = data
    localStorage.setItem('activeCheckinCode', data.code)
    await renderQR(data.code)
    refreshCheckInStatus()
  } catch (err) {
    showGlobalMsg(err.response?.data?.detail || '创建失败', 'error')
  } finally {
    creatingSession.value = false
  }
}

async function refreshCheckInStatus() {
  if (!activeSession.value) return
  try {
    const { data } = await getCheckInStatus(activeSession.value.code)
    checkinStatus.value = data
    activeSession.value = { ...activeSession.value, ...data.session }
  } catch {}
}

async function resumeCheckIn(session) {
  activeSession.value = session
  await renderQR(session.code)
  refreshCheckInStatus()
}

async function endCheckIn() {
  if (!activeSession.value) return
  try {
    await closeCheckIn(activeSession.value.code)
    activeSession.value = null
    checkinStatus.value = null
    localStorage.removeItem('activeCheckinCode')
    showGlobalMsg('签到已结束')
    loadCheckInSessions()
  } catch {}
}

async function loadCheckInSessions() {
  try {
    const { data } = await listCheckInSessions()
    checkinSessions.value = data
  } catch {}
}

async function restoreActiveSession() {
  const code = localStorage.getItem('activeCheckinCode')
  if (!code) return
  try {
    const { data } = await getCheckInStatus(code)
    if (data.session.is_active) {
      activeSession.value = data.session
      checkinStatus.value = data
      await renderQR(code)
    } else {
      localStorage.removeItem('activeCheckinCode')
    }
  } catch {
    localStorage.removeItem('activeCheckinCode')
  }
}

async function doScan() {
  if (!scanCode.value.trim()) return
  scanning.value = true
  scanMsg.value = ''
  try {
    const { data } = await apiCheckIn(scanCode.value.trim(), scanStatus.value)
    scanMsg.value = data.message
    scanMsgType.value = 'success'
  } catch (err) {
    scanMsg.value = err.response?.data?.detail || '签到失败'
    scanMsgType.value = 'error'
  } finally {
    scanning.value = false
  }
}

async function handleRosterImport(e) {
  const file = e.target.files?.[0]
  if (!file) return
  rosterMsg.value = ''
  try {
    const { data } = await importRoster(file)
    rosterMsg.value = data.message
    rosterMsgType.value = 'success'
    const classRes = await getRosterClasses()
    classes.value = classRes.data.classes
    loadRoster()
    const sizeRes = await getClassSize(selectedClass.value)
    classSize.value = sizeRes.data.size
  } catch (err) {
    rosterMsg.value = err.response?.data?.detail || '导入失败'
    rosterMsgType.value = 'error'
  }
  e.target.value = ''
}

onMounted(async () => {
  try {
    const { data } = await getRosterClasses()
    classes.value = data.classes
  } catch {}
  loadCheckInSessions()
  restoreActiveSession()

  // 从URL参数恢复签到码
  const params = new URLSearchParams(window.location.search)
  const checkinParam = params.get('checkin')
  if (checkinParam) {
    scanCode.value = checkinParam
    tab.value = 'scan'
  }
})
</script>

<style scoped>
@reference "../style.css";

.att-input {
  @apply w-full rounded-2xl px-4 py-3 text-sm transition-all duration-200
         focus:outline-none focus:ring-2 focus:border-transparent;
  background: #F1F5F9;
  color: #1E293B;
  --tw-ring-color: rgba(59, 130, 246, 0.4);
}
.att-input-sm {
  @apply w-full rounded-xl px-3 py-2 text-xs transition-all duration-200
         focus:outline-none focus:ring-2 focus:border-transparent;
  background: #F1F5F9;
  color: #1E293B;
  --tw-ring-color: rgba(59, 130, 246, 0.4);
}
.att-textarea {
  @apply w-full rounded-2xl px-4 py-3 text-sm resize-none transition-all duration-200
         focus:outline-none focus:ring-2 focus:border-transparent;
  background: #F1F5F9;
  color: #1E293B;
  --tw-ring-color: rgba(59, 130, 246, 0.4);
}
</style>
