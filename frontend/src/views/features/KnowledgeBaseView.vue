<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { qaApi } from '@/services/api'

interface KBEntry {
  entry_id: string
  question: string
  answer: string
  category: string
  keywords: string[]
  created_at: string
  difficulty_level: number
}

const entries = ref<KBEntry[]>([])
const loading = ref(true)
const searchQuery = ref('')

onMounted(async () => {
  try {
    entries.value = await qaApi.getKnowledgeBase()
  } finally {
    loading.value = false
  }
})

const filteredEntries = computed(() => {
  if (!searchQuery.value) return entries.value
  const query = searchQuery.value.toLowerCase()
  return entries.value.filter(e =>
    e.question.toLowerCase().includes(query) ||
    e.answer.toLowerCase().includes(query) ||
    e.keywords.some(t => t.toLowerCase().includes(query))
  )
})
</script>

<template>
  <div class="knowledge-base">
    <h2>知识库</h2>

    <el-input
      v-model="searchQuery"
      placeholder="搜索知识库..."
      :prefix-icon="'Search'"
      clearable
      class="search-input"
    />

    <el-card v-loading="loading" class="entries-card">
      <el-empty v-if="filteredEntries.length === 0" description="暂无内容" />

      <el-collapse v-else>
        <el-collapse-item
          v-for="entry in filteredEntries"
          :key="entry.entry_id"
          :title="entry.question"
        >
          <p>{{ entry.answer }}</p>
          <el-tag
            v-for="tag in entry.keywords"
            :key="tag"
            size="small"
            class="tag"
          >
            {{ tag }}
          </el-tag>
        </el-collapse-item>
      </el-collapse>
    </el-card>
  </div>
</template>

<style scoped>
.knowledge-base {
  padding: 20px;
}

.search-input {
  margin-bottom: 20px;
  max-width: 400px;
}

.tag {
  margin-right: 8px;
  margin-top: 8px;
}
</style>
