<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { assignmentsApi, gradingApi, submissionsApi } from '@/services/api'
import { useToastStore } from '@/stores/toast'
import type { Assignment, Submission } from '@/types'

const toast = useToastStore()
const assignments = ref<Assignment[]>([])
const selectedAssignmentId = ref('')
const submissions = ref<Submission[]>([])
const loading = ref(true)
const dialogVisible = ref(false)
const currentSubmission = ref<Submission | null>(null)
const feedback = ref('')
const grade = ref<number | undefined>(undefined)

onMounted(async () => {
  try {
    const res = await assignmentsApi.getAll()
    assignments.value = Array.isArray(res) ? res : (res.items ?? [])
  } finally {
    loading.value = false
  }
})

const loadSubmissions = async () => {
  if (!selectedAssignmentId.value) {
    submissions.value = []
    return
  }
  loading.value = true
  try {
    submissions.value = await submissionsApi.getByAssignment(selectedAssignmentId.value)
  } finally {
    loading.value = false
  }
}

const openGradeDialog = (submission: Submission) => {
  currentSubmission.value = submission
  feedback.value = ''
  grade.value = undefined
  dialogVisible.value = true
}

const handleGrade = async () => {
  if (!currentSubmission.value) return
  try {
    const feedbackObj = { summary: feedback.value }
    await gradingApi.gradeSubmission(
      Number(currentSubmission.value.id),
      feedbackObj,
      grade.value ?? 0
    )
    toast.success('批改完成')
    dialogVisible.value = false
    await loadSubmissions()
  } catch (error: any) {
    toast.error(error.response?.data?.detail || '批改失败')
  }
}

const handleAutoGrade = async (submission: Submission) => {
  try {
    await gradingApi.autoGrade(Number(submission.id))
    toast.success('自动批改已提交')
    await loadSubmissions()
  } catch (error: any) {
    toast.error(error.response?.data?.detail || '自动批改失败')
  }
}
</script>

<template>
  <div class="grading-view">
    <h2>批改作业</h2>

    <el-card class="selector-card">
      <el-select
        v-model="selectedAssignmentId"
        placeholder="选择要批改的作业"
        clearable
        style="width: 300px"
        @change="loadSubmissions"
      >
        <el-option
          v-for="a in assignments"
          :key="a.id"
          :label="a.title"
          :value="a.id"
        />
      </el-select>
    </el-card>

    <el-card v-loading="loading">
      <el-empty v-if="submissions.length === 0" description="暂无待批改的作业" />

      <el-table v-else :data="submissions" style="width: 100%">
        <el-table-column prop="id" label="提交ID" width="100" />
        <el-table-column prop="assignment_id" label="作业ID" />
        <el-table-column prop="student_id" label="学生ID" />
        <el-table-column prop="submitted_at" label="提交时间">
          <template #default="{ row }">
            {{ new Date(row.submitted_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openGradeDialog(row)">
              批改
            </el-button>
            <el-button size="small" @click="handleAutoGrade(row)">
              自动批改
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="批改作业" width="600px">
      <el-form label-position="top">
        <el-form-item label="成绩">
          <el-input-number v-model="grade" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="评语">
          <el-input v-model="feedback" type="textarea" rows="5" placeholder="请输入评语" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleGrade">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.grading-view {
  padding: 20px;
}

h2 {
  margin-bottom: 20px;
}

.selector-card {
  margin-bottom: 20px;
}
</style>
