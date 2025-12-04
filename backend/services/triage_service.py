"""
Triage Service

分诊服务，实现智能分诊逻辑、教师干预接口等功能。
"""
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, and_

from models.qa_log import QALog, TriageResult, QALogStatus
from models.knowledge_base import KnowledgeBaseEntry
from schemas.triage import (
    TriageRequest, TriageResponse, TriageDecision,
    PendingQuestion, PendingQueueResponse,
    TeacherTakeoverRequest, TeacherAnswerRequest, TeacherAnswerResponse,
    TriageStats, DifficultyInfo, DifficultyLevelsResponse,
    DIFFICULTY_DESCRIPTIONS
)
from schemas.qa_log import QALogCreate
from schemas.knowledge_base import KnowledgeBaseCreate
from services.qa_engine_service import qa_engine_service
from services.knowledge_base_service import knowledge_base_service


# 难度级别标签映射
DIFFICULTY_LABELS = {
    1: "L1 - 入门级",
    2: "L2 - 基础级",
    3: "L3 - 中级",
    4: "L4 - 高级",
    5: "L5 - 专家级",
}


class TriageService:
    """分诊服务"""
    
    # 匹配阈值
    HIGH_MATCH_THRESHOLD = 0.8
    MEDIUM_MATCH_THRESHOLD = 0.5
    
    async def triage_question(
        self,
        db: AsyncSession,
        request: TriageRequest
    ) -> TriageResponse:
        """对问题进行分诊"""
        # 使用问答引擎处理问题
        qa_request = QALogCreate(
            user_id=request.user_id,
            user_name=request.user_name,
            session_id=request.session_id,
            question=request.question
        )
        
        log_response = await qa_engine_service.process_question(db, qa_request)
        
        # 如果标记为紧急，更新日志
        if request.is_urgent:
            await db.execute(
                update(QALog)
                .where(QALog.log_id == log_response.log_id)
                .values(is_urgent=True, priority=5)
            )
            await db.commit()
        
        # 确定分诊决策
        decision = self._map_triage_to_decision(
            log_response.triage_result,
            log_response.match_score or 0,
            request.is_urgent
        )
        
        # 生成置信度消息
        confidence_message = self._generate_confidence_message(
            log_response.match_score or 0,
            decision
        )
        
        return TriageResponse(
            log_id=log_response.log_id,
            question=request.question,
            detected_category=log_response.detected_category,
            detected_difficulty=log_response.detected_difficulty or 2,
            difficulty_label=DIFFICULTY_LABELS.get(log_response.detected_difficulty or 2, "L2 - 基础级"),
            match_score=log_response.match_score or 0,
            matched_entry_id=log_response.matched_entry_id,
            decision=decision,
            answer=log_response.answer,
            answer_source=log_response.answer_source,
            assigned_to=log_response.assigned_to,
            priority=log_response.priority,
            is_urgent=request.is_urgent,
            confidence_message=confidence_message,
            created_at=log_response.created_at,
        )
    
    def _map_triage_to_decision(
        self,
        triage_result: Optional[TriageResult],
        match_score: float,
        is_urgent: bool
    ) -> TriageDecision:
        """将分诊结果映射为分诊决策"""
        if is_urgent:
            return TriageDecision.TO_TEACHER_URGENT
        
        if triage_result == TriageResult.AUTO_REPLY:
            if match_score >= self.HIGH_MATCH_THRESHOLD:
                return TriageDecision.AUTO_REPLY
            else:
                return TriageDecision.AUTO_REPLY_CONFIRM
        elif triage_result == TriageResult.TO_ASSISTANT:
            return TriageDecision.TO_ASSISTANT
        elif triage_result == TriageResult.TO_TEACHER:
            return TriageDecision.TO_TEACHER
        else:
            return TriageDecision.TO_ASSISTANT
    
    def _generate_confidence_message(
        self,
        match_score: float,
        decision: TriageDecision
    ) -> str:
        """生成置信度消息"""
        if decision == TriageDecision.AUTO_REPLY:
            return f"系统已找到高度匹配的答案（匹配度：{match_score:.0%}），已自动回复。"
        elif decision == TriageDecision.AUTO_REPLY_CONFIRM:
            return f"系统找到了可能相关的答案（匹配度：{match_score:.0%}），请确认是否有帮助。"
        elif decision == TriageDecision.TO_ASSISTANT:
            return "问题已转交助教处理，请耐心等待。"
        elif decision == TriageDecision.TO_TEACHER:
            return "问题已转交教师处理，请耐心等待。"
        elif decision == TriageDecision.TO_TEACHER_URGENT:
            return "紧急问题已优先转交教师处理。"
        return "问题正在处理中。"

    async def get_pending_queue(
        self,
        db: AsyncSession,
        handler_role: Optional[str] = None,
        handler_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> PendingQueueResponse:
        """获取待处理问题队列"""
        # 构建查询条件
        conditions = [QALog.status == QALogStatus.PENDING]

        if handler_role == "assistant":
            conditions.append(QALog.triage_result == TriageResult.TO_ASSISTANT)
        elif handler_role == "teacher":
            conditions.append(
                QALog.triage_result.in_([TriageResult.TO_TEACHER, TriageResult.TO_ASSISTANT])
            )

        if handler_id:
            conditions.append(QALog.assigned_to == handler_id)

        # 查询总数
        count_query = select(func.count(QALog.id)).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # 查询紧急数量
        urgent_query = select(func.count(QALog.id)).where(
            and_(*conditions, QALog.is_urgent == True)
        )
        urgent_result = await db.execute(urgent_query)
        urgent_count = urgent_result.scalar() or 0

        # 查询问题列表（按优先级和时间排序）
        query = (
            select(QALog)
            .where(and_(*conditions))
            .order_by(QALog.is_urgent.desc(), QALog.priority.desc(), QALog.created_at.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(query)
        logs = result.scalars().all()

        now = datetime.now()
        questions = [
            PendingQuestion(
                log_id=log.log_id,
                question=log.question,
                user_id=log.user_id,
                user_name=log.user_name,
                detected_category=log.detected_category,
                detected_difficulty=log.detected_difficulty or 2,
                difficulty_label=DIFFICULTY_LABELS.get(log.detected_difficulty or 2, "L2 - 基础级"),
                match_score=log.match_score,
                priority=log.priority,
                is_urgent=log.is_urgent,
                triage_result=log.triage_result.value if log.triage_result else "pending",
                created_at=log.created_at,
                waiting_time_seconds=(now - log.created_at).total_seconds(),
            )
            for log in logs
        ]

        return PendingQueueResponse(
            total=total,
            urgent_count=urgent_count,
            questions=questions,
        )

    async def teacher_takeover(
        self,
        db: AsyncSession,
        request: TeacherTakeoverRequest
    ) -> bool:
        """教师接管问题"""
        result = await db.execute(
            select(QALog).where(QALog.log_id == request.log_id)
        )
        log = result.scalar_one_or_none()

        if not log:
            return False

        log.assigned_to = request.teacher_id
        log.status = QALogStatus.ESCALATED
        await db.commit()

        return True

    async def teacher_answer(
        self,
        db: AsyncSession,
        request: TeacherAnswerRequest
    ) -> Optional[TeacherAnswerResponse]:
        """教师回答问题"""
        result = await db.execute(
            select(QALog).where(QALog.log_id == request.log_id)
        )
        log = result.scalar_one_or_none()

        if not log:
            return None

        now = datetime.now()

        # 更新日志
        log.answer = request.answer
        log.answer_source = "teacher"
        log.status = QALogStatus.ANSWERED
        log.handled_by = request.teacher_id
        log.handled_at = now
        if log.created_at:
            log.response_time_seconds = (now - log.created_at).total_seconds()

        new_entry_id = None

        # 如果需要更新知识库
        if request.update_knowledge_base:
            # 创建新的知识库条目
            new_entry = KnowledgeBaseCreate(
                category="other",
                question=log.question,
                answer=request.answer,
                keywords=request.new_keywords or log.question_keywords or [],
                difficulty_level=log.detected_difficulty or 2,
                language=None,
            )
            entry = await knowledge_base_service.create_entry(db, new_entry)
            new_entry_id = entry.entry_id

        await db.commit()

        return TeacherAnswerResponse(
            log_id=log.log_id,
            answer=request.answer,
            answered_by=request.teacher_id,
            answered_at=now,
            knowledge_base_updated=request.update_knowledge_base,
            new_entry_id=new_entry_id,
        )

    async def get_stats(self, db: AsyncSession) -> TriageStats:
        """获取分诊统计"""
        # 总问题数
        total_result = await db.execute(select(func.count(QALog.id)))
        total = total_result.scalar() or 0

        # 按分诊结果统计
        auto_replied = (await db.execute(
            select(func.count(QALog.id)).where(QALog.triage_result == TriageResult.AUTO_REPLY)
        )).scalar() or 0

        to_assistant = (await db.execute(
            select(func.count(QALog.id)).where(QALog.triage_result == TriageResult.TO_ASSISTANT)
        )).scalar() or 0

        to_teacher = (await db.execute(
            select(func.count(QALog.id)).where(QALog.triage_result == TriageResult.TO_TEACHER)
        )).scalar() or 0

        pending = (await db.execute(
            select(func.count(QALog.id)).where(QALog.status == QALogStatus.PENDING)
        )).scalar() or 0

        urgent_pending = (await db.execute(
            select(func.count(QALog.id)).where(
                and_(QALog.status == QALogStatus.PENDING, QALog.is_urgent == True)
            )
        )).scalar() or 0

        # 平均响应时间
        avg_time = (await db.execute(
            select(func.avg(QALog.response_time_seconds))
            .where(QALog.response_time_seconds.isnot(None))
        )).scalar()

        # 解决率
        answered = (await db.execute(
            select(func.count(QALog.id)).where(QALog.status == QALogStatus.ANSWERED)
        )).scalar() or 0
        resolution_rate = answered / total if total > 0 else 0.0

        # 按难度统计
        difficulty_result = await db.execute(
            select(QALog.detected_difficulty, func.count(QALog.id))
            .where(QALog.detected_difficulty.isnot(None))
            .group_by(QALog.detected_difficulty)
        )
        questions_by_difficulty = {
            DIFFICULTY_LABELS.get(row[0], f"L{row[0]}"): row[1]
            for row in difficulty_result.fetchall()
        }

        # 按决策统计
        decision_result = await db.execute(
            select(QALog.triage_result, func.count(QALog.id))
            .where(QALog.triage_result.isnot(None))
            .group_by(QALog.triage_result)
        )
        questions_by_decision = {
            row[0].value if row[0] else "unknown": row[1]
            for row in decision_result.fetchall()
        }

        return TriageStats(
            total_questions=total,
            auto_replied=auto_replied,
            to_assistant=to_assistant,
            to_teacher=to_teacher,
            pending=pending,
            urgent_pending=urgent_pending,
            avg_response_time=avg_time,
            avg_waiting_time=None,  # TODO: 计算平均等待时间
            resolution_rate=resolution_rate,
            questions_by_difficulty=questions_by_difficulty,
            questions_by_decision=questions_by_decision,
        )

    def get_difficulty_levels(self) -> DifficultyLevelsResponse:
        """获取难度级别列表"""
        levels = [
            DifficultyInfo(
                level=level,
                name=info["name"],
                description=info["description"],
                examples=info["examples"],
            )
            for level, info in DIFFICULTY_DESCRIPTIONS.items()
        ]
        return DifficultyLevelsResponse(levels=levels)


# 全局服务实例
triage_service = TriageService()

