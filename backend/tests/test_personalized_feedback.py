"""
Tests for Personalized Feedback System.

Tests cover:
- Student history analysis
- Personalized feedback generation
- Progressive suggestions
- Learning path creation
- Trend calculation
- Level determination
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from schemas.feedback import (
    FeedbackTone, FeedbackDetailLevel, SuggestionDifficulty,
    StudentLevel, PerformanceTrend, PersonalizedFeedbackRequest,
    StudentHistoryAnalysis, ProgressiveSuggestion, LearningPath
)
from services.feedback_service import (
    FeedbackGenerationService, FeedbackConfig,
    DETAIL_LEVEL_CONFIG, LEVEL_MESSAGES, TREND_MESSAGES
)


class TestFeedbackEnums:
    """Test new feedback enums."""

    def test_feedback_detail_level_values(self):
        """Test FeedbackDetailLevel enum values."""
        assert FeedbackDetailLevel.BRIEF.value == "brief"
        assert FeedbackDetailLevel.STANDARD.value == "standard"
        assert FeedbackDetailLevel.DETAILED.value == "detailed"
        assert FeedbackDetailLevel.COMPREHENSIVE.value == "comprehensive"

    def test_suggestion_difficulty_values(self):
        """Test SuggestionDifficulty enum values."""
        assert SuggestionDifficulty.EASY.value == "easy"
        assert SuggestionDifficulty.MEDIUM.value == "medium"
        assert SuggestionDifficulty.HARD.value == "hard"

    def test_student_level_values(self):
        """Test StudentLevel enum values."""
        assert StudentLevel.BEGINNER.value == "beginner"
        assert StudentLevel.INTERMEDIATE.value == "intermediate"
        assert StudentLevel.ADVANCED.value == "advanced"

    def test_performance_trend_values(self):
        """Test PerformanceTrend enum values."""
        assert PerformanceTrend.IMPROVING.value == "improving"
        assert PerformanceTrend.DECLINING.value == "declining"
        assert PerformanceTrend.STABLE.value == "stable"
        assert PerformanceTrend.FLUCTUATING.value == "fluctuating"


class TestDetailLevelConfig:
    """Test detail level configurations."""

    def test_brief_config(self):
        """Test BRIEF detail level config."""
        config = DETAIL_LEVEL_CONFIG[FeedbackDetailLevel.BRIEF]
        assert config["max_items"] == 3
        assert config["include_examples"] is False
        assert config["include_resources"] is False

    def test_comprehensive_config(self):
        """Test COMPREHENSIVE detail level config."""
        config = DETAIL_LEVEL_CONFIG[FeedbackDetailLevel.COMPREHENSIVE]
        assert config["max_items"] == 15
        assert config["include_examples"] is True
        assert config["include_resources"] is True


class TestLevelMessages:
    """Test level-specific messages."""

    def test_beginner_messages(self):
        """Test beginner level messages."""
        config = LEVEL_MESSAGES[StudentLevel.BEGINNER]
        assert "初学者" in config["prefix"]
        assert "beginner" in config["prefix_en"].lower()
        assert config["complexity_threshold"] == 5

    def test_advanced_messages(self):
        """Test advanced level messages."""
        config = LEVEL_MESSAGES[StudentLevel.ADVANCED]
        assert "高级" in config["prefix"]
        assert "advanced" in config["prefix_en"].lower()
        assert config["complexity_threshold"] == 15


class TestTrendMessages:
    """Test trend-specific messages."""

    def test_improving_trend(self):
        """Test improving trend messages."""
        config = TREND_MESSAGES[PerformanceTrend.IMPROVING]
        assert "进步" in config["message"]
        assert "improving" in config["message_en"].lower()
        assert config["emoji"] == "📈"

    def test_declining_trend(self):
        """Test declining trend messages."""
        config = TREND_MESSAGES[PerformanceTrend.DECLINING]
        assert "下滑" in config["message"]
        assert "declined" in config["message_en"].lower()
        assert config["emoji"] == "📉"


class TestFeedbackGenerationService:
    """Test FeedbackGenerationService personalized methods."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return FeedbackGenerationService()

    def test_calculate_trend_improving(self, service):
        """Test trend calculation for improving scores."""
        scores = [90, 88, 85, 80, 75, 70, 65, 60]  # Recent first
        trend, trend_zh = service._calculate_trend(scores)
        assert trend == PerformanceTrend.IMPROVING
        assert trend_zh == "进步中"

    def test_calculate_trend_declining(self, service):
        """Test trend calculation for declining scores."""
        scores = [60, 65, 70, 75, 80, 85, 88, 90]  # Recent first
        trend, trend_zh = service._calculate_trend(scores)
        assert trend == PerformanceTrend.DECLINING
        assert trend_zh == "退步中"

    def test_calculate_trend_stable(self, service):
        """Test trend calculation for stable scores."""
        scores = [75, 76, 74, 75, 76, 75, 74, 75]
        trend, trend_zh = service._calculate_trend(scores)
        assert trend == PerformanceTrend.STABLE
        assert trend_zh == "稳定"

    def test_calculate_trend_insufficient_data(self, service):
        """Test trend calculation with insufficient data."""
        scores = [80, 75]
        trend, trend_zh = service._calculate_trend(scores)
        assert trend == PerformanceTrend.STABLE

    def test_determine_level_beginner(self, service):
        """Test level determination for beginner."""
        level, level_zh = service._determine_level(50.0, 5)
        assert level == StudentLevel.BEGINNER
        assert level_zh == "初学者"

    def test_determine_level_intermediate(self, service):
        """Test level determination for intermediate."""
        level, level_zh = service._determine_level(75.0, 10)
        assert level == StudentLevel.INTERMEDIATE
        assert level_zh == "中级"

    def test_determine_level_advanced(self, service):
        """Test level determination for advanced."""
        level, level_zh = service._determine_level(90.0, 15)
        assert level == StudentLevel.ADVANCED
        assert level_zh == "高级"

    def test_determine_level_new_student(self, service):
        """Test level determination for new student."""
        level, level_zh = service._determine_level(85.0, 2)
        assert level == StudentLevel.BEGINNER  # Not enough submissions

    def test_calculate_improvement_rate_positive(self, service):
        """Test improvement rate calculation for positive improvement."""
        scores = [90, 85, 80, 70, 65, 60]  # Recent first
        rate = service._calculate_improvement_rate(scores)
        assert rate > 0

    def test_calculate_improvement_rate_negative(self, service):
        """Test improvement rate calculation for negative improvement."""
        scores = [60, 65, 70, 80, 85, 90]  # Recent first
        rate = service._calculate_improvement_rate(scores)
        assert rate < 0

    def test_translate_to_chinese(self, service):
        """Test translation of common terms."""
        result = service._translate_to_chinese("Low cyclomatic complexity - code is easy to follow")
        assert "圈复杂度" in result

        result = service._translate_to_chinese("Unknown term")
        assert result == "Unknown term"  # Returns original if not found


class TestProgressiveSuggestions:
    """Test progressive suggestion generation."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return FeedbackGenerationService()

    @pytest.fixture
    def mock_analysis(self):
        """Create mock analysis result."""
        analysis = MagicMock()
        analysis.naming_issues = [MagicMock()]
        analysis.complexity.cyclomatic_complexity = 15
        analysis.complexity.max_nesting_depth = 5
        analysis.security_issues = [MagicMock()]
        analysis.summary.overall_score = 70.0
        analysis.summary.grade = "C"
        return analysis

    def test_generate_progressive_suggestions(self, service, mock_analysis):
        """Test progressive suggestion generation."""
        suggestions = service._generate_progressive_suggestions(
            mock_analysis, "python", StudentLevel.INTERMEDIATE, 5
        )
        assert len(suggestions) > 0
        assert all(isinstance(s, ProgressiveSuggestion) for s in suggestions)

    def test_suggestions_have_difficulty_levels(self, service, mock_analysis):
        """Test that suggestions have appropriate difficulty levels."""
        suggestions = service._generate_progressive_suggestions(
            mock_analysis, "python", StudentLevel.INTERMEDIATE, 10
        )
        difficulties = {s.difficulty for s in suggestions}
        # Should have at least easy and medium
        assert SuggestionDifficulty.EASY in difficulties or SuggestionDifficulty.MEDIUM in difficulties

    def test_suggestions_have_chinese_translations(self, service, mock_analysis):
        """Test that suggestions have Chinese translations."""
        suggestions = service._generate_progressive_suggestions(
            mock_analysis, "python", StudentLevel.INTERMEDIATE, 5
        )
        for s in suggestions:
            assert s.title_zh
            assert s.description_zh
            assert s.estimated_time_zh


class TestLearningPath:
    """Test learning path creation."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return FeedbackGenerationService()

    @pytest.fixture
    def sample_suggestions(self):
        """Create sample suggestions."""
        return [
            ProgressiveSuggestion(
                suggestion_id="1",
                difficulty=SuggestionDifficulty.HARD,
                title="Fix Security",
                title_zh="修复安全问题",
                description="Fix security issues",
                description_zh="修复安全问题",
                estimated_time="1 hour",
                estimated_time_zh="1 小时",
                order=1
            ),
            ProgressiveSuggestion(
                suggestion_id="2",
                difficulty=SuggestionDifficulty.EASY,
                title="Fix Naming",
                title_zh="修复命名",
                description="Fix naming issues",
                description_zh="修复命名问题",
                estimated_time="10 minutes",
                estimated_time_zh="10 分钟",
                order=2
            ),
            ProgressiveSuggestion(
                suggestion_id="3",
                difficulty=SuggestionDifficulty.MEDIUM,
                title="Reduce Complexity",
                title_zh="降低复杂度",
                description="Reduce code complexity",
                description_zh="降低代码复杂度",
                estimated_time="30 minutes",
                estimated_time_zh="30 分钟",
                order=3
            ),
        ]

    def test_create_learning_path(self, service, sample_suggestions):
        """Test learning path creation."""
        path = service._create_learning_path(sample_suggestions, StudentLevel.INTERMEDIATE)
        assert isinstance(path, LearningPath)
        assert path.path_id
        assert path.title
        assert path.title_zh

    def test_learning_path_sorts_by_difficulty(self, service, sample_suggestions):
        """Test that learning path sorts suggestions by difficulty."""
        path = service._create_learning_path(sample_suggestions, StudentLevel.INTERMEDIATE)
        # First should be EASY, then MEDIUM, then HARD
        assert path.steps[0].difficulty == SuggestionDifficulty.EASY
        assert path.steps[1].difficulty == SuggestionDifficulty.MEDIUM
        assert path.steps[2].difficulty == SuggestionDifficulty.HARD

    def test_learning_path_calculates_total_time(self, service, sample_suggestions):
        """Test that learning path calculates total time."""
        path = service._create_learning_path(sample_suggestions, StudentLevel.INTERMEDIATE)
        assert path.total_estimated_time
        assert path.total_estimated_time_zh


class TestPersonalizedMessage:
    """Test personalized message generation."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return FeedbackGenerationService()

    @pytest.fixture
    def mock_analysis(self):
        """Create mock analysis result."""
        analysis = MagicMock()
        analysis.summary.overall_score = 80.0
        analysis.summary.grade = "B"
        return analysis

    def test_first_submission_message(self, service, mock_analysis):
        """Test message for first submission."""
        msg_en, msg_zh = service._generate_personalized_message(
            mock_analysis, None, FeedbackTone.PROFESSIONAL
        )
        assert "first" in msg_en.lower() or "welcome" in msg_en.lower()
        assert "第一次" in msg_zh or "欢迎" in msg_zh

    def test_above_average_message(self, service, mock_analysis):
        """Test message when score is above average."""
        history = StudentHistoryAnalysis(
            student_id="test",
            total_submissions=10,
            average_score=70.0,
            trend=PerformanceTrend.STABLE,
            trend_zh="稳定",
            level=StudentLevel.INTERMEDIATE,
            level_zh="中级"
        )
        msg_en, msg_zh = service._generate_personalized_message(
            mock_analysis, history, FeedbackTone.PROFESSIONAL
        )
        assert "above" in msg_en.lower()
        assert "高于" in msg_zh

    def test_below_average_message(self, service, mock_analysis):
        """Test message when score is below average."""
        mock_analysis.summary.overall_score = 60.0
        history = StudentHistoryAnalysis(
            student_id="test",
            total_submissions=10,
            average_score=75.0,
            trend=PerformanceTrend.STABLE,
            trend_zh="稳定",
            level=StudentLevel.INTERMEDIATE,
            level_zh="中级"
        )
        msg_en, msg_zh = service._generate_personalized_message(
            mock_analysis, history, FeedbackTone.PROFESSIONAL
        )
        assert "below" in msg_en.lower()
        assert "低于" in msg_zh


class TestEncouragement:
    """Test encouragement message generation."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return FeedbackGenerationService()

    @pytest.fixture
    def mock_analysis(self):
        """Create mock analysis result."""
        analysis = MagicMock()
        analysis.summary.overall_score = 85.0
        return analysis

    def test_encouragement_for_new_student_high_score(self, service, mock_analysis):
        """Test encouragement for new student with high score."""
        enc_en, enc_zh = service._generate_encouragement(
            mock_analysis, None, FeedbackTone.ENCOURAGING
        )
        assert enc_en
        assert enc_zh

    def test_encouragement_for_improving_student(self, service, mock_analysis):
        """Test encouragement for improving student."""
        history = StudentHistoryAnalysis(
            student_id="test",
            total_submissions=10,
            average_score=75.0,
            trend=PerformanceTrend.IMPROVING,
            trend_zh="进步中",
            level=StudentLevel.INTERMEDIATE,
            level_zh="中级",
            improvement_rate=15.0
        )
        enc_en, enc_zh = service._generate_encouragement(
            mock_analysis, history, FeedbackTone.ENCOURAGING
        )
        assert "📈" in enc_en
        assert "15.0%" in enc_en or "15%" in enc_en

    def test_encouragement_for_declining_student(self, service, mock_analysis):
        """Test encouragement for declining student."""
        history = StudentHistoryAnalysis(
            student_id="test",
            total_submissions=10,
            average_score=80.0,
            trend=PerformanceTrend.DECLINING,
            trend_zh="退步中",
            level=StudentLevel.INTERMEDIATE,
            level_zh="中级",
            improvement_rate=-10.0
        )
        enc_en, enc_zh = service._generate_encouragement(
            mock_analysis, history, FeedbackTone.ENCOURAGING
        )
        assert "📉" in enc_en
        assert "不要气馁" in enc_zh


class TestStudentHistoryAnalysisSchema:
    """Test StudentHistoryAnalysis schema."""

    def test_create_history_analysis(self):
        """Test creating StudentHistoryAnalysis."""
        history = StudentHistoryAnalysis(
            student_id="test_student",
            total_submissions=15,
            average_score=78.5,
            trend=PerformanceTrend.IMPROVING,
            trend_zh="进步中",
            level=StudentLevel.INTERMEDIATE,
            level_zh="中级",
            strengths=["Good naming", "Clean code"],
            strengths_zh=["命名规范", "代码整洁"],
            weaknesses=["Complex functions"],
            weaknesses_zh=["函数过于复杂"],
            recurring_issues=["Deep nesting"],
            recurring_issues_zh=["嵌套过深"],
            improvement_rate=12.5,
            recent_scores=[85, 82, 78, 75, 70]
        )
        assert history.student_id == "test_student"
        assert history.total_submissions == 15
        assert history.average_score == 78.5
        assert history.trend == PerformanceTrend.IMPROVING
        assert len(history.strengths) == 2
        assert len(history.weaknesses) == 1


class TestPersonalizedFeedbackRequest:
    """Test PersonalizedFeedbackRequest schema."""

    def test_create_request_with_defaults(self):
        """Test creating request with default values."""
        request = PersonalizedFeedbackRequest(
            code="def hello(): pass",
            student_id="test_student"
        )
        assert request.language == "python"
        assert request.detail_level == FeedbackDetailLevel.STANDARD
        assert request.tone == FeedbackTone.PROFESSIONAL
        assert request.include_learning_path is True
        assert request.include_history_analysis is True
        assert request.max_suggestions == 5

    def test_create_request_with_custom_values(self):
        """Test creating request with custom values."""
        request = PersonalizedFeedbackRequest(
            code="function hello() {}",
            language="javascript",
            student_id="test_student",
            detail_level=FeedbackDetailLevel.COMPREHENSIVE,
            tone=FeedbackTone.ENCOURAGING,
            include_learning_path=False,
            max_suggestions=10
        )
        assert request.language == "javascript"
        assert request.detail_level == FeedbackDetailLevel.COMPREHENSIVE
        assert request.tone == FeedbackTone.ENCOURAGING
        assert request.include_learning_path is False
        assert request.max_suggestions == 10

