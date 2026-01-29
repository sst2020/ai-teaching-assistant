"""
QA Engine Service

问答引擎服务，实现问题意图识别、关键词提取、相似度匹配等功能。
"""
import re
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from collections import Counter
import math

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

import logging

from models.qa_log import QALog, TriageResult, QALogStatus
from models.knowledge_base import KnowledgeBaseEntry, DifficultyLevel
from schemas.qa_log import QALogCreate, QALogResponse, QALogStats
from services.knowledge_base_service import knowledge_base_service

logger = logging.getLogger(__name__)


# 中文停用词列表
CHINESE_STOPWORDS = {
    "的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一", "一个",
    "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好",
    "自己", "这", "那", "什么", "怎么", "为什么", "如何", "吗", "呢", "啊", "吧",
    "这个", "那个", "哪个", "怎样", "怎么样", "请问", "问一下", "想问", "请教",
}

# 英文停用词列表
ENGLISH_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "dare",
    "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
    "into", "through", "during", "before", "after", "above", "below",
    "between", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "each", "few",
    "more", "most", "other", "some", "such", "no", "nor", "not",
    "only", "own", "same", "so", "than", "too", "very", "just",
    "and", "but", "if", "or", "because", "until", "while", "what",
    "which", "who", "whom", "this", "that", "these", "those", "i",
    "me", "my", "myself", "we", "our", "ours", "you", "your", "he",
    "him", "his", "she", "her", "it", "its", "they", "them", "their",
}

# 编程相关关键词权重
PROGRAMMING_KEYWORDS = {
    # 错误类型
    "error": 2.0, "错误": 2.0, "exception": 2.0, "异常": 2.0,
    "bug": 2.0, "问题": 1.5, "报错": 2.0, "失败": 1.5,
    # 语言
    "python": 1.5, "java": 1.5, "javascript": 1.5, "js": 1.5,
    "c++": 1.5, "cpp": 1.5, "c语言": 1.5, "go": 1.5, "rust": 1.5,
    # 概念
    "函数": 1.3, "function": 1.3, "类": 1.3, "class": 1.3,
    "变量": 1.3, "variable": 1.3, "循环": 1.3, "loop": 1.3,
    "数组": 1.3, "array": 1.3, "列表": 1.3, "list": 1.3,
    "字典": 1.3, "dict": 1.3, "map": 1.3, "对象": 1.3, "object": 1.3,
    # 操作
    "安装": 1.2, "install": 1.2, "配置": 1.2, "config": 1.2,
    "运行": 1.2, "run": 1.2, "编译": 1.2, "compile": 1.2,
    "调试": 1.2, "debug": 1.2, "测试": 1.2, "test": 1.2,
}


class QAEngineService:
    """问答引擎服务"""
    
    # 匹配阈值
    HIGH_MATCH_THRESHOLD = 0.8
    MEDIUM_MATCH_THRESHOLD = 0.5
    LOW_MATCH_THRESHOLD = 0.3
    
    def __init__(self):
        self._idf_cache: Dict[str, float] = {}
    
    def extract_keywords(self, text: str) -> List[str]:
        """提取文本中的关键词"""
        # 转小写
        text_lower = text.lower()
        
        # 分词：按空格、标点符号分割
        tokens = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z_][a-zA-Z0-9_]*|\d+', text_lower)
        
        # 过滤停用词和短词
        keywords = []
        for token in tokens:
            if len(token) < 2:
                continue
            if token in CHINESE_STOPWORDS or token in ENGLISH_STOPWORDS:
                continue
            keywords.append(token)
        
        return keywords
    
    def calculate_similarity(
        self,
        query_keywords: List[str],
        entry_keywords: List[str],
        entry_question: str
    ) -> float:
        """计算查询与知识库条目的相似度"""
        if not query_keywords or not entry_keywords:
            return 0.0
        
        # 1. 关键词匹配得分 (Jaccard相似度)
        query_set = set(query_keywords)
        entry_set = set(entry_keywords)
        intersection = query_set & entry_set
        union = query_set | entry_set
        jaccard_score = len(intersection) / len(union) if union else 0.0
        
        # 2. 加权关键词匹配
        weighted_score = 0.0
        total_weight = 0.0
        for kw in query_keywords:
            weight = PROGRAMMING_KEYWORDS.get(kw, 1.0)
            total_weight += weight
            if kw in entry_set:
                weighted_score += weight
        weighted_match = weighted_score / total_weight if total_weight > 0 else 0.0
        
        # 3. 问题文本包含匹配
        entry_question_lower = entry_question.lower()
        contain_score = 0.0
        for kw in query_keywords:
            if kw in entry_question_lower:
                contain_score += 1
        contain_match = contain_score / len(query_keywords) if query_keywords else 0.0
        
        # 综合得分
        final_score = (jaccard_score * 0.3 + weighted_match * 0.4 + contain_match * 0.3)
        return min(final_score, 1.0)

    def detect_category(self, keywords: List[str], question: str) -> Optional[str]:
        """检测问题分类"""
        question_lower = question.lower()

        # 分类关键词映射
        category_keywords = {
            "syntax_error": ["语法", "syntax", "error", "报错", "编译错误", "indentation", "缩进"],
            "logic_error": ["逻辑", "logic", "bug", "结果不对", "死循环", "无限循环", "越界"],
            "environment": ["安装", "install", "配置", "环境", "pip", "npm", "path", "环境变量"],
            "algorithm": ["算法", "algorithm", "排序", "查找", "递归", "动态规划", "复杂度"],
            "concept": ["概念", "什么是", "原理", "区别", "理解", "含义", "定义"],
            "debugging": ["调试", "debug", "断点", "print", "日志", "排查"],
            "data_structure": ["数据结构", "数组", "链表", "栈", "队列", "树", "图", "哈希"],
            "best_practice": ["最佳实践", "规范", "命名", "风格", "设计模式", "重构"],
        }

        scores = {}
        for category, cat_keywords in category_keywords.items():
            score = 0
            for kw in cat_keywords:
                if kw in keywords or kw in question_lower:
                    score += 1
            if score > 0:
                scores[category] = score

        if scores:
            return max(scores, key=scores.get)
        return None

    def detect_difficulty(self, keywords: List[str], question: str) -> int:
        """检测问题难度级别 (1-5)"""
        question_lower = question.lower()

        # 难度关键词
        difficulty_indicators = {
            1: ["基础", "简单", "入门", "初学", "新手", "basic", "simple", "beginner"],
            2: ["常见", "一般", "普通", "常用", "common"],
            3: ["进阶", "中级", "算法", "递归", "intermediate", "algorithm"],
            4: ["高级", "复杂", "设计模式", "架构", "advanced", "complex", "pattern"],
            5: ["专家", "优化", "性能", "分布式", "并发", "expert", "performance"],
        }

        detected_level = 2  # 默认中等偏低

        for level, indicators in difficulty_indicators.items():
            for indicator in indicators:
                if indicator in keywords or indicator in question_lower:
                    detected_level = max(detected_level, level)

        return detected_level

    async def find_best_match(
        self,
        db: AsyncSession,
        question: str
    ) -> Tuple[Optional[KnowledgeBaseEntry], float, List[str]]:
        """查找最佳匹配的知识库条目"""
        # 提取关键词
        keywords = self.extract_keywords(question)

        if not keywords:
            return None, 0.0, []

        # 使用知识库服务搜索
        from schemas.knowledge_base import KnowledgeBaseSearchRequest
        search_request = KnowledgeBaseSearchRequest(
            query=question,
            limit=5
        )
        results = await knowledge_base_service.search(db, search_request)

        if not results:
            return None, 0.0, keywords

        # 获取最佳匹配
        best_result = results[0]

        # 获取完整条目 (best_result.entry 已经包含完整信息)
        entry = await knowledge_base_service.get_entry(db, best_result.entry.entry_id)

        return entry, best_result.relevance_score, keywords

    async def process_question(
        self,
        db: AsyncSession,
        request: QALogCreate
    ) -> QALogResponse:
        """处理用户问题，返回问答日志"""
        start_time = datetime.now()

        # 提取关键词
        keywords = self.extract_keywords(request.question)

        # 检测分类和难度
        detected_category = self.detect_category(keywords, request.question)
        detected_difficulty = self.detect_difficulty(keywords, request.question)

        # 查找最佳匹配
        matched_entry, match_score, _ = await self.find_best_match(db, request.question)

        # 确定分诊结果
        triage_result = self._determine_triage(match_score, detected_difficulty)

        # 确定回复
        answer = None
        answer_source = None
        status = QALogStatus.PENDING

        if matched_entry and match_score >= self.HIGH_MATCH_THRESHOLD:
            # 知识库高匹配度，使用知识库答案
            answer = matched_entry.answer
            answer_source = "knowledge_base"
            status = QALogStatus.ANSWERED
            triage_result = TriageResult.AUTO_REPLY
            # 增加查看次数
            await knowledge_base_service.increment_view(db, matched_entry.entry_id)
        else:
            # 知识库无匹配或低匹配度，使用 AI 生成回答
            try:
                from services.ai_service import ai_service
                ai_result = await ai_service.answer_question(
                    request.question,
                    context=""
                )
                answer = ai_result.get("answer", "")
                if answer and len(answer) > 10:
                    answer_source = "ai"
                    status = QALogStatus.ANSWERED
                    triage_result = TriageResult.AUTO_REPLY
                    logger.info(f"AI 回答生成成功，问题: {request.question[:50]}...")
                else:
                    logger.warning(f"AI 回答为空或过短，转人工处理")
            except Exception as e:
                logger.error(f"AI 服务调用失败: {e}，转人工处理")
                # AI 服务失败时保持原有分诊逻辑

        # 计算响应时间
        response_time = (datetime.now() - start_time).total_seconds()

        # 创建日志记录
        log = QALog(
            log_id=str(uuid.uuid4()),
            user_id=request.user_id,
            user_name=request.user_name,
            session_id=request.session_id,
            question=request.question,
            question_keywords=keywords,
            detected_category=detected_category,
            detected_difficulty=detected_difficulty,
            matched_entry_id=matched_entry.entry_id if matched_entry else None,
            match_score=match_score,
            match_method="hybrid_keyword_similarity",
            answer=answer,
            answer_source=answer_source,
            triage_result=triage_result,
            priority=self._calculate_priority(detected_difficulty, match_score),
            status=status,
            response_time_seconds=response_time,
        )

        db.add(log)
        await db.commit()
        await db.refresh(log)

        return QALogResponse(
            log_id=log.log_id,
            user_id=log.user_id,
            user_name=log.user_name,
            session_id=log.session_id,
            question=log.question,
            question_keywords=log.question_keywords,
            detected_category=log.detected_category,
            detected_difficulty=log.detected_difficulty,
            matched_entry_id=log.matched_entry_id,
            match_score=log.match_score,
            match_method=log.match_method,
            answer=log.answer,
            answer_source=log.answer_source,
            triage_result=log.triage_result,
            assigned_to=log.assigned_to,
            priority=log.priority,
            is_urgent=log.is_urgent,
            status=log.status,
            is_helpful=log.is_helpful,
            feedback_text=log.feedback_text,
            handled_by=log.handled_by,
            handled_at=log.handled_at,
            response_time_seconds=log.response_time_seconds,
            created_at=log.created_at,
            updated_at=log.updated_at,
        )

    def _determine_triage(self, match_score: float, difficulty: int) -> TriageResult:
        """确定分诊结果"""
        # 高匹配度
        if match_score >= self.HIGH_MATCH_THRESHOLD:
            if difficulty <= 3:
                return TriageResult.AUTO_REPLY
            else:
                return TriageResult.TO_ASSISTANT

        # 中等匹配度
        if match_score >= self.MEDIUM_MATCH_THRESHOLD:
            if difficulty <= 2:
                return TriageResult.AUTO_REPLY
            elif difficulty <= 3:
                return TriageResult.TO_ASSISTANT
            else:
                return TriageResult.TO_TEACHER

        # 低匹配度
        if difficulty <= 2:
            return TriageResult.TO_ASSISTANT
        else:
            return TriageResult.TO_TEACHER

    def _calculate_priority(self, difficulty: int, match_score: float) -> int:
        """计算优先级 (0-5)"""
        # 难度越高、匹配度越低，优先级越高
        priority = 0

        if difficulty >= 4:
            priority += 2
        elif difficulty >= 3:
            priority += 1

        if match_score < self.LOW_MATCH_THRESHOLD:
            priority += 2
        elif match_score < self.MEDIUM_MATCH_THRESHOLD:
            priority += 1

        return min(priority, 5)

    async def get_stats(self, db: AsyncSession) -> QALogStats:
        """获取问答统计信息"""
        # 总问题数
        total_result = await db.execute(select(func.count(QALog.id)))
        total = total_result.scalar() or 0

        # 按分诊结果统计
        auto_replied = await db.execute(
            select(func.count(QALog.id)).where(QALog.triage_result == TriageResult.AUTO_REPLY)
        )
        to_assistant = await db.execute(
            select(func.count(QALog.id)).where(QALog.triage_result == TriageResult.TO_ASSISTANT)
        )
        to_teacher = await db.execute(
            select(func.count(QALog.id)).where(QALog.triage_result == TriageResult.TO_TEACHER)
        )
        pending = await db.execute(
            select(func.count(QALog.id)).where(QALog.triage_result == TriageResult.PENDING)
        )

        # 平均响应时间
        avg_time_result = await db.execute(
            select(func.avg(QALog.response_time_seconds)).where(QALog.response_time_seconds.isnot(None))
        )
        avg_response_time = avg_time_result.scalar()

        # 有帮助率
        helpful_count = await db.execute(
            select(func.count(QALog.id)).where(QALog.is_helpful == True)
        )
        feedback_count = await db.execute(
            select(func.count(QALog.id)).where(QALog.is_helpful.isnot(None))
        )
        helpful_rate = None
        if feedback_count.scalar():
            helpful_rate = helpful_count.scalar() / feedback_count.scalar()

        # 按分类统计
        category_result = await db.execute(
            select(QALog.detected_category, func.count(QALog.id))
            .where(QALog.detected_category.isnot(None))
            .group_by(QALog.detected_category)
        )
        questions_by_category = {row[0]: row[1] for row in category_result.fetchall()}

        # 按难度统计
        difficulty_result = await db.execute(
            select(QALog.detected_difficulty, func.count(QALog.id))
            .where(QALog.detected_difficulty.isnot(None))
            .group_by(QALog.detected_difficulty)
        )
        questions_by_difficulty = {str(row[0]): row[1] for row in difficulty_result.fetchall()}

        return QALogStats(
            total_questions=total,
            auto_replied=auto_replied.scalar() or 0,
            to_assistant=to_assistant.scalar() or 0,
            to_teacher=to_teacher.scalar() or 0,
            pending=pending.scalar() or 0,
            avg_response_time=avg_response_time,
            helpful_rate=helpful_rate,
            questions_by_category=questions_by_category,
            questions_by_difficulty=questions_by_difficulty,
        )


# 全局服务实例
qa_engine_service = QAEngineService()

