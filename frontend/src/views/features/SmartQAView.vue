<script setup lang="ts">
import { ref, nextTick, onUnmounted } from 'vue'
import { qaApi } from '@/services/api'
import { useToastStore } from '@/stores/toast'
import { useAuthStore } from '@/stores/auth'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  loading?: boolean
  confidence?: number
}

const toast = useToastStore()
const auth = useAuthStore()
const input = ref('')
const messages = ref<ChatMessage[]>([])
const streaming = ref(false)
const chatContainer = ref<HTMLElement | null>(null)
let abortCtrl: AbortController | null = null

const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

const handleSend = () => {
  const text = input.value.trim()
  if (!text || streaming.value) return

  // 添加用户消息
  messages.value.push({ role: 'user', content: text })
  input.value = ''

  // 添加 AI 占位消息
  const aiMsg: ChatMessage = { role: 'assistant', content: '', loading: true }
  messages.value.push(aiMsg)
  streaming.value = true
  scrollToBottom()

  abortCtrl = qaApi.askStream(text, {
    studentId: auth.user?.student_id || 'anonymous',
    courseId: 'general',
    onChunk(chunk: string) {
      aiMsg.loading = false
      aiMsg.content += chunk
      scrollToBottom()
    },
    onDone(meta) {
      aiMsg.loading = false
      aiMsg.confidence = meta.confidence
      streaming.value = false
      scrollToBottom()
    },
    onError(msg: string) {
      aiMsg.loading = false
      aiMsg.content = aiMsg.content || `回答失败: ${msg}`
      streaming.value = false
      toast.error(msg)
    }
  })
}

const handleStop = () => {
  abortCtrl?.abort()
  abortCtrl = null
  streaming.value = false
  const lastMsg = messages.value[messages.value.length - 1]
  if (lastMsg?.role === 'assistant') {
    lastMsg.loading = false
    if (!lastMsg.content) lastMsg.content = '（已中断）'
  }
}

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

onUnmounted(() => {
  abortCtrl?.abort()
})
</script>

<template>
  <div class="smart-qa">
    <div class="chat-header">
      <h2>智能答疑</h2>
      <span class="powered-by">Powered by DeepSeek</span>
    </div>

    <el-card class="chat-card">
      <!-- 消息列表 -->
      <div ref="chatContainer" class="chat-messages">
        <div v-if="messages.length === 0" class="empty-state">
          <el-icon :size="48" color="#c0c4cc"><ChatLineRound /></el-icon>
          <p>输入问题开始对话</p>
          <div class="suggestions">
            <el-tag
              v-for="s in ['什么是递归？', 'Python列表和元组的区别', '如何优化排序算法']"
              :key="s"
              class="suggestion-tag"
              @click="input = s"
            >{{ s }}</el-tag>
          </div>
        </div>

        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          :class="['chat-bubble', msg.role]"
        >
          <div class="bubble-avatar">
            <el-icon v-if="msg.role === 'assistant'" :size="20"><Monitor /></el-icon>
            <el-icon v-else :size="20"><User /></el-icon>
          </div>
          <div class="bubble-body">
            <div v-if="msg.loading" class="typing-indicator">
              <span /><span /><span />
            </div>
            <div v-else class="bubble-text" v-html="formatContent(msg.content)" />
            <div v-if="msg.confidence !== undefined" class="bubble-meta">
              置信度: {{ (msg.confidence * 100).toFixed(0) }}%
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="chat-input-area">
        <el-input
          v-model="input"
          :autosize="{ minRows: 1, maxRows: 4 }"
          type="textarea"
          placeholder="输入问题，Enter 发送，Shift+Enter 换行"
          :disabled="streaming"
          @keydown="handleKeydown"
        />
        <el-button
          v-if="!streaming"
          type="primary"
          circle
          :disabled="!input.trim()"
          @click="handleSend"
        >
          <el-icon><Promotion /></el-icon>
        </el-button>
        <el-button
          v-else
          type="danger"
          circle
          @click="handleStop"
        >
          <el-icon><VideoPause /></el-icon>
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script lang="ts">
// formatContent: 简单 markdown 渲染
function formatContent(text: string): string {
  if (!text) return ''
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code class="lang-$1">$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>')
}
</script>

<style scoped>
.smart-qa {
  padding: 24px;
  height: calc(100vh - 80px);
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 16px;
}

.chat-header h2 {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1d1d1f 0%, #434344 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.powered-by {
  font-size: 13px;
  color: #909399;
}

/* Card */
:deep(.el-card) {
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.08),
    0 2px 8px rgba(0, 0, 0, 0.04);
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

:deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}

.chat-card {
  flex: 1;
  min-height: 0;
}

/* Messages */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #909399;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.suggestion-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.2);
}

/* Bubble */
.chat-bubble {
  display: flex;
  gap: 10px;
  max-width: 80%;
}

.chat-bubble.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.bubble-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.chat-bubble.assistant .bubble-avatar {
  background: linear-gradient(135deg, #007AFF, #5856D6);
  color: white;
}

.chat-bubble.user .bubble-avatar {
  background: linear-gradient(135deg, #34C759, #30D158);
  color: white;
}

.bubble-body {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 18px;
  padding: 12px 16px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.chat-bubble.user .bubble-body {
  background: linear-gradient(135deg, #007AFF, #5856D6);
  color: white;
  border: none;
}

.bubble-text {
  font-size: 14px;
  line-height: 1.7;
  word-break: break-word;
}

.bubble-text :deep(pre) {
  background: rgba(0, 0, 0, 0.06);
  border-radius: 8px;
  padding: 12px;
  overflow-x: auto;
  margin: 8px 0;
}

.chat-bubble.user .bubble-text :deep(pre) {
  background: rgba(255, 255, 255, 0.15);
}

.bubble-text :deep(code) {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
}

.bubble-text :deep(code:not(pre code)) {
  background: rgba(0, 0, 0, 0.06);
  padding: 2px 6px;
  border-radius: 4px;
}

.bubble-meta {
  font-size: 11px;
  color: #909399;
  margin-top: 6px;
}

/* Typing indicator */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #c0c4cc;
  border-radius: 50%;
  animation: typing-bounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.16s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.32s; }

@keyframes typing-bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* Input area */
.chat-input-area {
  display: flex;
  gap: 10px;
  align-items: flex-end;
  padding: 16px 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  background: rgba(255, 255, 255, 0.5);
}

.chat-input-area :deep(.el-textarea__inner) {
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.08);
  padding: 10px 16px;
  resize: none;
}

.chat-input-area :deep(.el-textarea__inner:focus) {
  border-color: #007AFF;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
}

.chat-input-area :deep(.el-button.is-circle) {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #007AFF, #5856D6);
  border: none;
}
</style>
