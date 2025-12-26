"""
Q&A Service - Handles AI-powered question answering and triage
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from collections import Counter
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from models.qa_log import QALog, TriageResult, QALogStatus
from schemas.qa import (
    QuestionRequest, QuestionResponse, QuestionCategory, QuestionStatus,
    AIAnswer, QAAnalyticsReport, KnowledgeGap, EscalationRequest
)
from schemas.qa_log import QALogCreate, QALogResponse
from services.ai_service import ai_service
from services.qa_engine_service import qa_engine_service


class QAService:
    """Service for AI-powered Q&A triage."""

    def __init__(self):
        self._questions: dict = {}  # 保留用于向后兼容
        self.ai = ai_service
        self.qa_engine = qa_engine_service

    async def smart_answer(
        self,
        db: AsyncSession,
        question: str,
        user_id: Optional[str] = None,
        user_name: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> QALogResponse:
        """
        智能问答接口 - 使用知识库匹配和分诊逻辑

        Args:
            db: 数据库会话
            question: 用户问题
            user_id: 用户ID
            user_name: 用户名
            session_id: 会话ID

        Returns:
            QALogResponse: 问答日志响应
        """
        request = QALogCreate(
            user_id=user_id,
            user_name=user_name,
            session_id=session_id,
            question=question
        )
        return await self.qa_engine.process_question(db, request)

    async def answer_question(self, request: QuestionRequest) -> QuestionResponse:
        """Process and answer a student question using AI."""
        question_id = str(uuid.uuid4())

        # AI-powered categorization
        category_str = await self.ai.categorize_question(request.question)
        category = self._map_category(category_str)

        # Generate AI answer
        ai_answer = await self._generate_answer(request)

        # Determine status based on AI confidence
        status = QuestionStatus.AI_ANSWERED
        if ai_answer.needs_teacher_review or ai_answer.confidence < 0.6:
            status = QuestionStatus.ESCALATED

        response = QuestionResponse(
            question_id=question_id, student_id=request.student_id,
            course_id=request.course_id, question=request.question,
            category=category, status=status, ai_answer=ai_answer,
            created_at=datetime.utcnow(), answered_at=datetime.utcnow()
        )

        self._questions[question_id] = response
        return response

    def _map_category(self, category_str: str) -> QuestionCategory:
        """Map string category to enum."""
        mapping = {
            "basic": QuestionCategory.BASIC,
            "intermediate": QuestionCategory.INTERMEDIATE,
            "advanced": QuestionCategory.ADVANCED,
            "administrative": QuestionCategory.ADMINISTRATIVE
        }
        return mapping.get(category_str, QuestionCategory.INTERMEDIATE)

    async def _generate_answer(self, request: QuestionRequest) -> AIAnswer:
        """Generate an AI answer for the question."""
        context = f"Course: {request.course_id}" if request.course_id else ""
        result = await self.ai.answer_question(request.question, context)

        return AIAnswer(
            answer=result["answer"],
            confidence=result["confidence"],
            sources=result.get("sources", []),
            needs_teacher_review=result["needs_teacher_review"]
        )
    
    async def escalate_question(self, request: EscalationRequest) -> QuestionResponse:
        """Escalate a question to a teacher."""
        if request.question_id not in self._questions:
            raise ValueError(f"Question {request.question_id} not found")
        
        question = self._questions[request.question_id]
        question.status = QuestionStatus.ESCALATED
        return question
    
    async def generate_analytics_report(
        self,
        db: AsyncSession,
        course_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> QAAnalyticsReport:
        """
        Generate analytics report for Q&A records from database.

        分析问答记录，生成知识薄弱点报告。
        """
        # 查询时间范围内的问答记录
        query = select(QALog).where(
            and_(
                QALog.created_at >= start_date,
                QALog.created_at <= end_date
            )
        )
        result = await db.execute(query)
        logs = result.scalars().all()

        if not logs:
            return QAAnalyticsReport(
                course_id=course_id,
                period_start=start_date,
                period_end=end_date,
                total_questions=0,
                ai_resolved_count=0,
                teacher_resolved_count=0,
                average_response_time_seconds=0.0,
                knowledge_gaps=[],
                common_topics=[],
                recommendations=["暂无足够数据生成分析报告"]
            )

        # 统计基本指标
        total_questions = len(logs)
        ai_resolved = sum(1 for log in logs if log.triage_result == TriageResult.AUTO_REPLY)
        teacher_resolved = sum(1 for log in logs if log.triage_result == TriageResult.TO_TEACHER)

        # 计算平均响应时间
        response_times = [log.response_time_seconds for log in logs if log.response_time_seconds]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0

        # 分析知识薄弱点（基于问题分类和难度）
        knowledge_gaps = await self._analyze_knowledge_gaps(logs)

        # 分析常见主题（基于关键词）
        common_topics = self._analyze_common_topics(logs)

        # 生成教学建议
        recommendations = self._generate_recommendations(knowledge_gaps, common_topics, logs)

        return QAAnalyticsReport(
            course_id=course_id,
            period_start=start_date,
            period_end=end_date,
            total_questions=total_questions,
            ai_resolved_count=ai_resolved,
            teacher_resolved_count=teacher_resolved,
            average_response_time_seconds=round(avg_response_time, 2),
            knowledge_gaps=knowledge_gaps,
            common_topics=common_topics,
            recommendations=recommendations
        )

    async def _analyze_knowledge_gaps(self, logs: List[QALog]) -> List[KnowledgeGap]:
        """分析知识薄弱点"""
        # 按分类统计问题
        category_questions: Dict[str, List[str]] = {}
        category_difficulty: Dict[str, List[int]] = {}

        for log in logs:
            category = log.detected_category or "其他"
            if category not in category_questions:
                category_questions[category] = []
                category_difficulty[category] = []
            category_questions[category].append(log.question)
            if log.detected_difficulty:
                category_difficulty[category].append(log.detected_difficulty)

        # 生成知识薄弱点列表
        gaps = []
        for category, questions in category_questions.items():
            if len(questions) >= 3:  # 至少3个问题才算薄弱点
                difficulties = category_difficulty.get(category, [3])
                avg_difficulty = sum(difficulties) / len(difficulties) if difficulties else 3

                # 确定难度级别
                if avg_difficulty <= 2:
                    difficulty_level = "basic"
                elif avg_difficulty <= 3:
                    difficulty_level = "intermediate"
                else:
                    difficulty_level = "advanced"

                gaps.append(KnowledgeGap(
                    topic=self._translate_category(category),
                    frequency=len(questions),
                    difficulty_level=difficulty_level,
                    sample_questions=questions[:3]  # 取前3个样本问题
                ))

        # 按频率排序
        gaps.sort(key=lambda x: x.frequency, reverse=True)
        return gaps[:10]  # 返回前10个薄弱点

    def _translate_category(self, category: str) -> str:
        """翻译分类名称"""
        translations = {
            "syntax_error": "语法错误",
            "logic_error": "逻辑错误",
            "environment": "环境配置",
            "algorithm": "算法",
            "concept": "概念理解",
            "debugging": "调试技巧",
            "data_structure": "数据结构",
            "best_practice": "最佳实践",
            "其他": "其他问题"
        }
        return translations.get(category, category)

    def _analyze_common_topics(self, logs: List[QALog]) -> List[dict]:
        """分析常见主题"""
        # 收集所有关键词
        all_keywords = []
        for log in logs:
            if log.question_keywords:
                all_keywords.extend(log.question_keywords)

        # 统计关键词频率
        keyword_counts = Counter(all_keywords)

        # 返回前10个常见主题
        common = [{"topic": kw, "count": count} for kw, count in keyword_counts.most_common(10)]
        return common

    def _generate_recommendations(
        self,
        gaps: List[KnowledgeGap],
        topics: List[dict],
        logs: List[QALog]
    ) -> List[str]:
        """生成教学建议"""
        recommendations = []

        # 基于知识薄弱点生成建议
        for gap in gaps[:3]:  # 取前3个薄弱点
            if gap.difficulty_level == "basic":
                recommendations.append(f"建议加强 {gap.topic} 的基础讲解，该主题有 {gap.frequency} 个相关问题")
            elif gap.difficulty_level == "intermediate":
                recommendations.append(f"建议增加 {gap.topic} 的练习题目，帮助学生巩固理解")
            else:
                recommendations.append(f"建议提供 {gap.topic} 的进阶学习资料，满足学生深入学习需求")

        # 基于升级到教师的问题比例生成建议
        teacher_escalated = sum(1 for log in logs if log.triage_result == TriageResult.TO_TEACHER)
        if len(logs) > 0:
            escalation_rate = teacher_escalated / len(logs)
            if escalation_rate > 0.3:
                recommendations.append("较多问题需要教师介入，建议扩充知识库内容")

        # 基于平均难度生成建议
        difficulties = [log.detected_difficulty for log in logs if log.detected_difficulty]
        if difficulties:
            avg_difficulty = sum(difficulties) / len(difficulties)
            if avg_difficulty > 3.5:
                recommendations.append("学生问题整体难度较高，建议增加答疑时间")

        if not recommendations:
            recommendations.append("当前问答情况良好，建议继续保持")

        return recommendations

    async def get_student_question_history(
        self,
        db: AsyncSession,
        student_id: str,
        limit: int = 50
    ) -> List[QALogResponse]:
        """获取学生的问答历史"""
        query = select(QALog).where(
            QALog.user_id == student_id
        ).order_by(QALog.created_at.desc()).limit(limit)

        result = await db.execute(query)
        logs = result.scalars().all()

        return [self._log_to_response(log) for log in logs]

    async def get_weakness_report(
        self,
        db: AsyncSession,
        student_id: str
    ) -> Dict:
        """获取学生的知识薄弱点报告"""
        # 获取学生的所有问答记录
        query = select(QALog).where(QALog.user_id == student_id)
        result = await db.execute(query)
        logs = result.scalars().all()

        if not logs:
            return {
                "student_id": student_id,
                "total_questions": 0,
                "weakness_areas": [],
                "improvement_suggestions": ["暂无足够数据生成分析报告"]
            }

        # 分析薄弱点
        gaps = await self._analyze_knowledge_gaps(logs)

        # 分析问题解决率
        resolved = sum(1 for log in logs if log.status == QALogStatus.ANSWERED)
        resolution_rate = resolved / len(logs) if logs else 0

        # 生成改进建议
        suggestions = []
        for gap in gaps[:3]:
            suggestions.append(f"建议加强 {gap.topic} 的学习，您在该领域有 {gap.frequency} 个问题")

        if resolution_rate < 0.7:
            suggestions.append("部分问题未能得到满意解答，建议主动寻求教师帮助")

        return {
            "student_id": student_id,
            "total_questions": len(logs),
            "resolution_rate": round(resolution_rate, 2),
            "weakness_areas": [{"topic": g.topic, "frequency": g.frequency} for g in gaps],
            "improvement_suggestions": suggestions
        }

    def _log_to_response(self, log: QALog) -> QALogResponse:
        """将 QALog 模型转换为响应"""
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


# Singleton instance
qa_service = QAService()

