<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { studentRecordsApi } from '@/services/api'
import { useToastStore } from '@/stores/toast'
import type { StudentRecord, StudentRecordCreate, StudentRecordUpdate } from '@/types'

const toast = useToastStore()

// --- State ---
const records = ref<StudentRecord[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchAssignmentNumber = ref('')

// Dialog state
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const dialogTitle = computed(() => dialogMode.value === 'create' ? '新增记录' : '编辑记录')
const submitting = ref(false)

const formData = reactive<StudentRecordCreate & { original_student_id?: string }>({
  name: '',
  student_id: '',
  password: '',
  assignment_number: '',
})

// Form validation
const formRef = ref()
const formRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  student_id: [{ required: true, message: '请输入学号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur', min: 6 }],
  assignment_number: [{ required: true, message: '请输入作业编号', trigger: 'blur' }],
}

const totalPages = computed(() => Math.ceil(total.value / pageSize.value) || 1)

// --- Methods ---
async function fetchRecords() {
  loading.value = true
  try {
    const params: any = { page: currentPage.value, page_size: pageSize.value }
    if (searchAssignmentNumber.value) {
      params.assignment_number = searchAssignmentNumber.value
    }
    const res = await studentRecordsApi.getAll(params)
    records.value = res.items
    total.value = res.total
  } catch {
    toast.error('获取记录失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  currentPage.value = 1
  fetchRecords()
}

function handlePageChange(page: number) {
  currentPage.value = page
  fetchRecords()
}

function handlePageSizeChange(size: number) {
  pageSize.value = size
  currentPage.value = 1
  fetchRecords()
}

// --- Create ---
function openCreate() {
  dialogMode.value = 'create'
  formData.name = ''
  formData.student_id = ''
  formData.password = ''
  formData.assignment_number = ''
  delete formData.original_student_id
  formRef.value?.resetFields()
  dialogVisible.value = true
}

// --- Edit ---
function openEdit(row: StudentRecord) {
  dialogMode.value = 'edit'
  formData.name = row.name
  formData.student_id = row.student_id
  formData.password = ''   // 编辑时密码留空,不修改则不传
  formData.assignment_number = row.assignment_number
  formData.original_student_id = row.student_id
  formRef.value?.resetFields()
  dialogVisible.value = true
}

// --- Submit ---
async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      await studentRecordsApi.create({
        name: formData.name,
        student_id: formData.student_id,
        password: formData.password,
        assignment_number: formData.assignment_number,
      })
      toast.success('创建成功')
    } else {
      const updateData: StudentRecordUpdate = {
        name: formData.name,
        student_id: formData.student_id,
        assignment_number: formData.assignment_number,
      }
      if (formData.password) {
        updateData.password = formData.password
      }
      await studentRecordsApi.update(formData.original_student_id!, updateData)
      toast.success('更新成功')
    }
    dialogVisible.value = false
    fetchRecords()
  } catch (err: any) {
    const msg = err?.response?.data?.detail || '操作失败'
    toast.error(msg)
  } finally {
    submitting.value = false
  }
}

// --- Delete ---
async function handleDelete(row: StudentRecord) {
  try {
    await studentRecordsApi.delete(row.student_id)
    toast.success('删除成功')
    fetchRecords()
  } catch (err: any) {
    const msg = err?.response?.data?.detail || '删除失败'
    toast.error(msg)
  }
}

onMounted(() => {
  fetchRecords()
})
</script>

<template>
  <div class="student-records-page">
    <div class="page-header">
      <div class="page-title">
        <h2>学生记录管理</h2>
        <p class="page-subtitle">管理学生基本信息与作业关联</p>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-value">{{ total }}</div>
            <div class="stat-label">总记录数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-value">{{ records.length }}</div>
            <div class="stat-label">当前页记录</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-value">{{ totalPages }}</div>
            <div class="stat-label">总页数</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 操作栏 -->
    <el-card class="toolbar-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-input
            v-model="searchAssignmentNumber"
            placeholder="按作业编号搜索"
            clearable
            style="width: 240px"
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </div>
        <div class="toolbar-right">
          <el-button type="primary" @click="openCreate">
            <el-icon><Plus /></el-icon>
            新增记录
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card" v-loading="loading">
      <el-table :data="records" stripe style="width: 100%">
        <el-table-column type="index" label="#" width="60" />
        <el-table-column prop="name" label="姓名" min-width="120" />
        <el-table-column prop="student_id" label="学号" min-width="140" />
        <el-table-column prop="assignment_number" label="作业编号" min-width="140" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString('zh-CN') }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ row.updated_at ? new Date(row.updated_at).toLocaleString('zh-CN') : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="openEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-popconfirm
              title="确定要删除该记录吗？"
              confirm-button-text="确定"
              cancel-button-text="取消"
              @confirm="handleDelete(row)"
            >
              <template #reference>
                <el-button type="danger" size="small" link>
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handlePageSizeChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="520px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
        label-position="right"
      >
        <el-form-item label="姓名" prop="name">
          <el-input v-model="formData.name" placeholder="请输入学生姓名" />
        </el-form-item>
        <el-form-item label="学号" prop="student_id">
          <el-input v-model="formData.student_id" placeholder="请输入学号" :disabled="dialogMode === 'edit'" />
        </el-form-item>
        <el-form-item label="密码" prop="password" :required="dialogMode === 'create'">
          <el-input
            v-model="formData.password"
            type="password"
            show-password
            :placeholder="dialogMode === 'create' ? '请输入密码' : '留空则不修改密码'"
          />
        </el-form-item>
        <el-form-item label="作业编号" prop="assignment_number">
          <el-input v-model="formData.assignment_number" placeholder="请输入作业编号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ dialogMode === 'create' ? '创建' : '保存' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.student-records-page {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title h2 {
  font-size: 26px;
  font-weight: 700;
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.page-subtitle {
  color: rgba(0, 0, 0, 0.5);
  margin: 6px 0 0;
  font-size: 14px;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.stat-item {
  text-align: center;
  padding: 8px 0;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  margin-top: 6px;
  color: rgba(0, 0, 0, 0.45);
  font-size: 14px;
  font-weight: 500;
}

/* 工具栏 */
.toolbar-card {
  margin-bottom: 20px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 表格卡片 */
.table-card {
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.table-card :deep(.el-card__body) {
  padding: 20px 24px;
}

/* 表格样式 */
:deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: rgba(0, 122, 255, 0.06);
  border-radius: 14px;
  overflow: hidden;
}

:deep(.el-table th.el-table__cell) {
  font-weight: 600;
  color: rgba(0, 0, 0, 0.7);
  border-bottom: 2px solid rgba(0, 122, 255, 0.15);
}

:deep(.el-table .el-table__row:hover > td) {
  background-color: rgba(0, 122, 255, 0.04) !important;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: rgba(0, 122, 255, 0.02);
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

/* 弹窗样式 */
:deep(.el-dialog) {
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.12);
}

:deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  padding: 20px 24px 16px;
}

:deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

:deep(.el-dialog__footer) {
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  padding: 16px 24px;
}

/* 输入框样式 */
:deep(.el-input__wrapper) {
  border-radius: 12px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(0, 122, 255, 0.3);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #007AFF;
}

/* 按钮样式 */
:deep(.el-button--primary) {
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
  border: none;
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 14px rgba(0, 122, 255, 0.3);
}

:deep(.el-button--primary:hover) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(0, 122, 255, 0.4);
}

:deep(.el-button--primary:active) {
  transform: translateY(0);
}
</style>
