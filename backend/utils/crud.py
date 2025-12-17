"""
CRUD Utility Functions for Database Operations

This module provides reusable CRUD operations for all database models.
"""
from typing import Optional, List, Type, TypeVar, Generic, Any, Dict
from datetime import datetime
import uuid

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import Base
from models import (
    User, RefreshToken, TokenBlacklist, AuthLog,
    Student, Assignment, Submission, GradingResult,
    Question, Answer, PlagiarismCheck, Rubric, AnalysisResult,
    FeedbackTemplate, AIInteraction
)
from models.submission import SubmissionStatus
from models.code_file import CodeFile
from models.feedback_template import TemplateCategory
from models.ai_interaction import AIInteractionType, AIProvider

# Generic type for models
ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    """Base class for CRUD operations."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """Get a single record by ID."""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination and optional filters."""
        query = select(self.model)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.where(getattr(self.model, key) == value)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def count(self, db: AsyncSession, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filters."""
        query = select(func.count()).select_from(self.model)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.where(getattr(self.model, key) == value)
        result = await db.execute(query)
        return result.scalar() or 0

    async def create(self, db: AsyncSession, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: Dict[str, Any]
    ) -> ModelType:
        """Update an existing record."""
        for field, value in obj_in.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: int) -> bool:
        """Delete a record by ID."""
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.flush()
            return True
        return False


# Student CRUD
class CRUDStudent(CRUDBase[Student]):
    """CRUD operations for Student model."""

    async def get_by_student_id(self, db: AsyncSession, student_id: str) -> Optional[Student]:
        """Get student by unique student_id."""
        result = await db.execute(
            select(Student).where(Student.student_id == student_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[Student]:
        """Get student by email."""
        result = await db.execute(
            select(Student).where(Student.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_course(
        self, db: AsyncSession, course_id: str, skip: int = 0, limit: int = 100
    ) -> List[Student]:
        """Get students by course ID."""
        result = await db.execute(
            select(Student)
            .where(Student.course_id == course_id)
            .offset(skip).limit(limit)
        )
        return list(result.scalars().all())


# Assignment CRUD
class CRUDAssignment(CRUDBase[Assignment]):
    """CRUD operations for Assignment model."""

    async def get_by_assignment_id(self, db: AsyncSession, assignment_id: str) -> Optional[Assignment]:
        """Get assignment by unique assignment_id."""
        result = await db.execute(
            select(Assignment).where(Assignment.assignment_id == assignment_id)
        )
        return result.scalar_one_or_none()

    async def get_by_course(
        self, db: AsyncSession, course_id: str, skip: int = 0, limit: int = 100
    ) -> List[Assignment]:
        """Get assignments by course ID."""
        result = await db.execute(
            select(Assignment)
            .where(Assignment.course_id == course_id)
            .order_by(Assignment.due_date.desc().nullslast())
            .offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_course(self, db: AsyncSession, course_id: str) -> int:
        """Count assignments by course ID."""
        result = await db.execute(
            select(func.count()).select_from(Assignment).where(Assignment.course_id == course_id)
        )
        return result.scalar() or 0


# Submission CRUD
class CRUDSubmission(CRUDBase[Submission]):
    """CRUD operations for Submission model."""

    async def get_by_submission_id(self, db: AsyncSession, submission_id: str) -> Optional[Submission]:
        """Get submission by unique submission_id."""
        result = await db.execute(
            select(Submission).where(Submission.submission_id == submission_id)
        )
        return result.scalar_one_or_none()

    async def get_by_student(
        self, db: AsyncSession, student_id: int, skip: int = 0, limit: int = 100
    ) -> List[Submission]:
        """Get submissions by student database ID."""
        result = await db.execute(
            select(Submission)
            .where(Submission.student_id == student_id)
            .order_by(Submission.submitted_at.desc())
            .offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_assignment(
        self, db: AsyncSession, assignment_id: int, skip: int = 0, limit: int = 100
    ) -> List[Submission]:
        """Get submissions by assignment database ID."""
        result = await db.execute(
            select(Submission)
            .where(Submission.assignment_id == assignment_id)
            .order_by(Submission.submitted_at.desc())
            .offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_student(self, db: AsyncSession, student_id: int) -> int:
        """Count submissions by student."""
        result = await db.execute(
            select(func.count()).select_from(Submission).where(Submission.student_id == student_id)
        )
        return result.scalar() or 0

    async def count_by_assignment(self, db: AsyncSession, assignment_id: int) -> int:
        """Count submissions by assignment."""
        result = await db.execute(
            select(func.count()).select_from(Submission).where(Submission.assignment_id == assignment_id)
        )
        return result.scalar() or 0

    async def update_status(
        self, db: AsyncSession, submission_id: str, status: SubmissionStatus
    ) -> Optional[Submission]:
        """Update submission status."""
        submission = await self.get_by_submission_id(db, submission_id)
        if submission:
            submission.status = status
            await db.flush()
            await db.refresh(submission)
        return submission


def generate_unique_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    unique_part = str(uuid.uuid4())[:8]
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    if prefix:
        return f"{prefix}_{timestamp}_{unique_part}"
    return f"{timestamp}_{unique_part}"


# CodeFile CRUD
class CRUDCodeFile(CRUDBase[CodeFile]):
    """CRUD operations for CodeFile model."""

    async def get_by_file_id(self, db: AsyncSession, file_id: str) -> Optional[CodeFile]:
        """Get file by unique file_id."""
        result = await db.execute(
            select(CodeFile).where(CodeFile.file_id == file_id)
        )
        return result.scalar_one_or_none()

    async def get_by_content_hash(self, db: AsyncSession, content_hash: str) -> Optional[CodeFile]:
        """Get file by content hash (for deduplication)."""
        result = await db.execute(
            select(CodeFile).where(CodeFile.content_hash == content_hash)
        )
        return result.scalar_one_or_none()

    async def get_by_uploader(
        self, db: AsyncSession, uploader_id: str, skip: int = 0, limit: int = 100
    ) -> List[CodeFile]:
        """Get files by uploader ID."""
        result = await db.execute(
            select(CodeFile)
            .where(CodeFile.uploader_id == uploader_id)
            .order_by(CodeFile.created_at.desc())
            .offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_assignment(
        self, db: AsyncSession, assignment_id: str, skip: int = 0, limit: int = 100
    ) -> List[CodeFile]:
        """Get files by assignment ID."""
        result = await db.execute(
            select(CodeFile)
            .where(CodeFile.assignment_id == assignment_id)
            .order_by(CodeFile.created_at.desc())
            .offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_uploader(self, db: AsyncSession, uploader_id: str) -> int:
        """Count files by uploader."""
        result = await db.execute(
            select(func.count()).select_from(CodeFile).where(CodeFile.uploader_id == uploader_id)
        )
        return result.scalar() or 0

    async def count_by_assignment(self, db: AsyncSession, assignment_id: str) -> int:
        """Count files by assignment."""
        result = await db.execute(
            select(func.count()).select_from(CodeFile).where(CodeFile.assignment_id == assignment_id)
        )
        return result.scalar() or 0

    async def update_status(
        self, db: AsyncSession, file_id: str, status: str
    ) -> Optional[CodeFile]:
        """Update file status."""
        file = await self.get_by_file_id(db, file_id)
        if file:
            file.status = status
            await db.flush()
            await db.refresh(file)
        return file

    async def update_analysis_result(
        self, db: AsyncSession, file_id: str, analysis_result: str
    ) -> Optional[CodeFile]:
        """Update file analysis result."""
        file = await self.get_by_file_id(db, file_id)
        if file:
            file.analysis_result = analysis_result
            await db.flush()
            await db.refresh(file)
        return file


# CRUD for AnalysisResult
class CRUDAnalysisResult(CRUDBase[AnalysisResult]):
    """CRUD operations for AnalysisResult model."""

    async def get_by_analysis_id(
        self, db: AsyncSession, analysis_id: str
    ) -> Optional[AnalysisResult]:
        """Get analysis result by analysis ID."""
        result = await db.execute(
            select(AnalysisResult).where(AnalysisResult.id == analysis_id)
        )
        return result.scalar_one_or_none()

    async def get_by_file_id(
        self, db: AsyncSession, file_id: str
    ) -> List[AnalysisResult]:
        """Get all analysis results for a file."""
        result = await db.execute(
            select(AnalysisResult)
            .where(AnalysisResult.file_id == file_id)
            .order_by(AnalysisResult.analyzed_at.desc())
        )
        return list(result.scalars().all())

    async def get_latest_by_file_id(
        self, db: AsyncSession, file_id: str
    ) -> Optional[AnalysisResult]:
        """Get the most recent analysis result for a file."""
        result = await db.execute(
            select(AnalysisResult)
            .where(AnalysisResult.file_id == file_id)
            .order_by(AnalysisResult.analyzed_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create_from_result(
        self, db: AsyncSession, analysis_result: dict
    ) -> AnalysisResult:
        """Create an analysis result from a dictionary."""
        db_result = AnalysisResult(
            id=analysis_result.get("analysis_id"),
            file_id=analysis_result.get("file_id"),
            language=analysis_result.get("language", "unknown"),
            overall_score=analysis_result.get("summary", {}).get("overall_score", 0),
            grade=analysis_result.get("summary", {}).get("grade", "F"),
            total_lines=analysis_result.get("line_metrics", {}).get("total_lines", 0),
            code_lines=analysis_result.get("line_metrics", {}).get("code_lines", 0),
            comment_lines=analysis_result.get("line_metrics", {}).get("comment_lines", 0),
            blank_lines=analysis_result.get("line_metrics", {}).get("blank_lines", 0),
            docstring_lines=analysis_result.get("line_metrics", {}).get("docstring_lines", 0),
            cyclomatic_complexity=analysis_result.get("complexity", {}).get("cyclomatic_complexity", 0),
            cognitive_complexity=analysis_result.get("complexity", {}).get("cognitive_complexity", 0),
            max_nesting_depth=analysis_result.get("complexity", {}).get("max_nesting_depth", 0),
            max_function_length=analysis_result.get("complexity", {}).get("max_function_length", 0),
            max_parameters=analysis_result.get("complexity", {}).get("max_parameters", 0),
            total_functions=analysis_result.get("complexity", {}).get("total_functions", 0),
            total_classes=analysis_result.get("structure", {}).get("total_classes", 0),
            total_methods=analysis_result.get("structure", {}).get("total_methods", 0),
            average_function_length=analysis_result.get("structure", {}).get("average_function_length", 0),
            total_violations=analysis_result.get("summary", {}).get("total_violations", 0),
            critical_violations=analysis_result.get("summary", {}).get("critical_violations", 0),
            warnings=analysis_result.get("summary", {}).get("warnings", 0),
            info_violations=analysis_result.get("summary", {}).get("info_violations", 0),
            category_scores=analysis_result.get("category_scores", {}),
            violations=analysis_result.get("violations", []),
            recommendations=analysis_result.get("recommendations", []),
            naming_results=analysis_result.get("naming_conventions", {})
        )
        db.add(db_result)
        await db.flush()
        await db.refresh(db_result)
        return db_result


# CRUD for Feedback Templates
class CRUDFeedbackTemplate(CRUDBase[FeedbackTemplate]):
    """CRUD operations for feedback templates."""

    async def get_by_category(
        self,
        db: AsyncSession,
        category: str,
        language: Optional[str] = None,
        is_active: bool = True
    ) -> List[FeedbackTemplate]:
        """Get templates by category and optionally language."""
        query = select(self.model).where(
            and_(
                self.model.category == category,
                self.model.is_active == is_active
            )
        )
        if language:
            query = query.where(
                (self.model.language == language) | (self.model.language.is_(None))
            )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_tags(
        self,
        db: AsyncSession,
        tags: List[str],
        is_active: bool = True
    ) -> List[FeedbackTemplate]:
        """Get templates that have any of the specified tags."""
        # Note: This is a simplified implementation
        # For production, consider using PostgreSQL array operations
        query = select(self.model).where(self.model.is_active == is_active)
        result = await db.execute(query)
        templates = result.scalars().all()

        # Filter by tags in Python (for SQLite compatibility)
        matching = []
        for template in templates:
            if template.tags and any(tag in template.tags for tag in tags):
                matching.append(template)
        return matching

    async def increment_usage(
        self,
        db: AsyncSession,
        template_id: int
    ) -> Optional[FeedbackTemplate]:
        """Increment the usage count for a template."""
        template = await self.get(db, template_id)
        if template:
            template.usage_count += 1
            await db.flush()
            await db.refresh(template)
        return template

    async def search(
        self,
        db: AsyncSession,
        search_term: str,
        is_active: bool = True
    ) -> List[FeedbackTemplate]:
        """Search templates by name or message."""
        pattern = f"%{search_term}%"
        query = select(self.model).where(
            and_(
                self.model.is_active == is_active,
                (self.model.name.ilike(pattern) | self.model.message.ilike(pattern))
            )
        )
        result = await db.execute(query)
        return list(result.scalars().all())


# CRUD for AI Interactions
class CRUDAIInteraction(CRUDBase[AIInteraction]):
    """CRUD operations for AI interactions."""

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 50
    ) -> List[AIInteraction]:
        """Get interactions for a specific user."""
        query = select(self.model).where(
            self.model.user_id == user_id
        ).order_by(self.model.created_at.desc()).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_type(
        self,
        db: AsyncSession,
        interaction_type: str,
        limit: int = 100
    ) -> List[AIInteraction]:
        """Get interactions by type."""
        query = select(self.model).where(
            self.model.interaction_type == interaction_type
        ).order_by(self.model.created_at.desc()).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """Get statistics about AI interactions."""
        # Total count
        total_result = await db.execute(select(func.count(self.model.id)))
        total = total_result.scalar() or 0

        # Average latency
        avg_latency_result = await db.execute(
            select(func.avg(self.model.latency_ms))
        )
        avg_latency = avg_latency_result.scalar() or 0

        # Total tokens
        total_tokens_result = await db.execute(
            select(func.sum(self.model.tokens_used))
        )
        total_tokens = total_tokens_result.scalar() or 0

        # Count by type
        type_counts = {}
        for itype in AIInteractionType:
            count_result = await db.execute(
                select(func.count(self.model.id)).where(
                    self.model.interaction_type == itype.value
                )
            )
            type_counts[itype.value] = count_result.scalar() or 0

        return {
            "total_interactions": total,
            "average_latency_ms": round(avg_latency, 2),
            "total_tokens_used": total_tokens,
            "interactions_by_type": type_counts
        }

    async def log_interaction(
        self,
        db: AsyncSession,
        interaction_type: str,
        provider: str,
        model: str,
        prompt: str,
        response: str,
        tokens_used: int = 0,
        latency_ms: int = 0,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AIInteraction:
        """Log a new AI interaction."""
        interaction = AIInteraction(
            interaction_type=interaction_type,
            provider=provider,
            model=model,
            prompt=prompt,
            response=response,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
            user_id=user_id,
            metadata=metadata or {}
        )
        db.add(interaction)
        await db.flush()
        await db.refresh(interaction)
        return interaction


# ============ Authentication CRUD Classes ============

class CRUDUser(CRUDBase[User]):
    """CRUD operations for User model."""

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """通过邮箱查找用户"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create_with_password(
        self,
        db: AsyncSession,
        email: str,
        password_hash: str,
        role: str = "student",
        **kwargs
    ) -> User:
        """创建用户 (密码已哈希)"""
        user = User(
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True,
            **kwargs
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    async def update_last_login(self, db: AsyncSession, user_id: int) -> None:
        """更新最后登录时间"""
        user = await self.get(db, user_id)
        if user:
            user.last_login = datetime.utcnow()
            await db.flush()

    async def deactivate(self, db: AsyncSession, user_id: int) -> bool:
        """停用用户"""
        user = await self.get(db, user_id)
        if user:
            user.is_active = False
            await db.flush()
            return True
        return False


class CRUDRefreshToken(CRUDBase[RefreshToken]):
    """CRUD operations for RefreshToken model."""

    async def get_by_token(self, db: AsyncSession, token: str) -> Optional[RefreshToken]:
        """通过 token 字符串查找"""
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()

    async def create_token(
        self,
        db: AsyncSession,
        user_id: int,
        token: str,
        expires_at: datetime
    ) -> RefreshToken:
        """创建刷新令牌"""
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            revoked=False
        )
        db.add(refresh_token)
        await db.flush()
        await db.refresh(refresh_token)
        return refresh_token

    async def revoke_token(self, db: AsyncSession, token: str) -> bool:
        """撤销令牌"""
        refresh_token = await self.get_by_token(db, token)
        if refresh_token:
            refresh_token.revoked = True
            await db.flush()
            return True
        return False

    async def revoke_all_user_tokens(self, db: AsyncSession, user_id: int) -> int:
        """撤销用户所有令牌"""
        result = await db.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.user_id == user_id,
                    RefreshToken.revoked == False
                )
            )
        )
        tokens = result.scalars().all()
        count = 0
        for token in tokens:
            token.revoked = True
            count += 1
        await db.flush()
        return count

    async def delete_expired(self, db: AsyncSession) -> int:
        """删除过期令牌"""
        now = datetime.utcnow()
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.expires_at < now)
        )
        tokens = result.scalars().all()
        count = len(tokens)
        for token in tokens:
            await db.delete(token)
        await db.flush()
        return count


class CRUDTokenBlacklist(CRUDBase[TokenBlacklist]):
    """CRUD operations for TokenBlacklist model."""

    async def add_to_blacklist(
        self,
        db: AsyncSession,
        jti: str,
        user_id: int,
        token_type: str,
        expires_at: datetime
    ) -> TokenBlacklist:
        """加入黑名单"""
        blacklist_entry = TokenBlacklist(
            jti=jti,
            user_id=user_id,
            token_type=token_type,
            expires_at=expires_at
        )
        db.add(blacklist_entry)
        await db.flush()
        await db.refresh(blacklist_entry)
        return blacklist_entry

    async def is_blacklisted(self, db: AsyncSession, jti: str) -> bool:
        """检查是否在黑名单"""
        result = await db.execute(
            select(TokenBlacklist).where(TokenBlacklist.jti == jti)
        )
        return result.scalar_one_or_none() is not None

    async def cleanup_expired(self, db: AsyncSession) -> int:
        """清理过期黑名单记录"""
        now = datetime.utcnow()
        result = await db.execute(
            select(TokenBlacklist).where(TokenBlacklist.expires_at < now)
        )
        entries = result.scalars().all()
        count = len(entries)
        for entry in entries:
            await db.delete(entry)
        await db.flush()
        return count


# Create singleton instances
crud_user = CRUDUser(User)
crud_refresh_token = CRUDRefreshToken(RefreshToken)
crud_token_blacklist = CRUDTokenBlacklist(TokenBlacklist)
crud_auth_log = CRUDBase(AuthLog)  # AuthLog 使用基础 CRUD 操作即可

crud_student = CRUDStudent(Student)
crud_assignment = CRUDAssignment(Assignment)
crud_submission = CRUDSubmission(Submission)
crud_code_file = CRUDCodeFile(CodeFile)
crud_analysis_result = CRUDAnalysisResult(AnalysisResult)
crud_feedback_template = CRUDFeedbackTemplate(FeedbackTemplate)
crud_ai_interaction = CRUDAIInteraction(AIInteraction)



# Rubric CRUD
class CRUDRubric(CRUDBase[Rubric]):
    """Rubric 的 CRUD 操作"""

    async def get_by_rubric_id(self, db: AsyncSession, rubric_id: str) -> Optional[Rubric]:
        """通过 rubric_id 获取 Rubric"""
        result = await db.execute(
            select(Rubric).where(Rubric.rubric_id == rubric_id)
        )
        return result.scalar_one_or_none()

    async def get_with_assignments(
        self, db: AsyncSession, rubric_id: str
    ) -> Optional[Rubric]:
        """获取 Rubric 及其关联的所有 Assignment（使用 eager loading）"""
        result = await db.execute(
            select(Rubric)
            .options(selectinload(Rubric.assignments))
            .where(Rubric.rubric_id == rubric_id)
        )
        return result.scalar_one_or_none()

    async def get_assignments_by_rubric(
        self, db: AsyncSession, rubric_id: str, skip: int = 0, limit: int = 100
    ) -> List[Assignment]:
        """获取使用指定 Rubric 的所有 Assignment"""
        rubric = await self.get_by_rubric_id(db, rubric_id)
        if not rubric:
            return []

        result = await db.execute(
            select(Assignment)
            .where(Assignment.rubric_id == rubric.id)
            .offset(skip).limit(limit)
        )
        return list(result.scalars().all())


# Create CRUD instance
crud_rubric = CRUDRubric(Rubric)
