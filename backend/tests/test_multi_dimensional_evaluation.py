"""
Tests for Multi-Dimensional Evaluation System.

Tests cover:
- Dimension score calculation
- Radar chart data generation
- Class comparison
- Overall summary generation
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from schemas.evaluation import (
    EvaluationDimension, DIMENSION_METADATA,
    DimensionScore, RadarChartData, ClassComparison,
    AbilityAnalysisReport, MultiDimensionalEvaluationRequest
)
from services.multi_dimensional_evaluator import MultiDimensionalEvaluator


class TestEvaluationDimension:
    """Test EvaluationDimension enum."""

    def test_dimension_values(self):
        """Test dimension enum values."""
        assert EvaluationDimension.TECHNICAL_ABILITY.value == "technical_ability"
        assert EvaluationDimension.CODE_QUALITY.value == "code_quality"
        assert EvaluationDimension.INNOVATION.value == "innovation"
        assert EvaluationDimension.BEST_PRACTICES.value == "best_practices"
        assert EvaluationDimension.EFFICIENCY.value == "efficiency"
        assert EvaluationDimension.DOCUMENTATION.value == "documentation"

    def test_dimension_count(self):
        """Test that we have 6 dimensions."""
        assert len(EvaluationDimension) == 6


class TestDimensionMetadata:
    """Test dimension metadata."""

    def test_all_dimensions_have_metadata(self):
        """Test that all dimensions have metadata."""
        for dim in EvaluationDimension:
            assert dim in DIMENSION_METADATA

    def test_metadata_has_required_fields(self):
        """Test that metadata has all required fields."""
        for dim, meta in DIMENSION_METADATA.items():
            assert "name" in meta
            assert "name_zh" in meta
            assert "description" in meta
            assert "description_zh" in meta
            assert "weight" in meta

    def test_weights_sum_to_one(self):
        """Test that dimension weights sum to 1.0."""
        total_weight = sum(meta["weight"] for meta in DIMENSION_METADATA.values())
        assert abs(total_weight - 1.0) < 0.01


class TestDimensionScore:
    """Test DimensionScore schema."""

    def test_create_dimension_score(self):
        """Test creating a dimension score."""
        score = DimensionScore(
            dimension=EvaluationDimension.CODE_QUALITY,
            score=85.0,
            weight=0.25,
            name="Code Quality",
            name_zh="代码质量",
            description="Good code quality",
            description_zh="良好的代码质量",
            strengths=["Low complexity"],
            strengths_zh=["低复杂度"],
            improvements=["Add more comments"],
            improvements_zh=["添加更多注释"]
        )
        assert score.dimension == EvaluationDimension.CODE_QUALITY
        assert score.score == 85.0
        assert score.weight == 0.25

    def test_score_validation(self):
        """Test score validation (0-100)."""
        with pytest.raises(ValueError):
            DimensionScore(
                dimension=EvaluationDimension.CODE_QUALITY,
                score=150.0,  # Invalid
                weight=0.25,
                name="Code Quality",
                name_zh="代码质量"
            )


class TestRadarChartData:
    """Test RadarChartData schema."""

    def test_create_radar_chart_data(self):
        """Test creating radar chart data."""
        data = RadarChartData(
            labels=["A", "B", "C"],
            labels_zh=["甲", "乙", "丙"],
            student_scores=[80, 75, 90],
            class_average=[70, 72, 85],
            max_scores=[100, 100, 100]
        )
        assert len(data.labels) == 3
        assert len(data.student_scores) == 3
        assert data.class_average is not None


class TestMultiDimensionalEvaluator:
    """Test MultiDimensionalEvaluator service."""

    @pytest.fixture
    def evaluator(self):
        """Create evaluator instance."""
        return MultiDimensionalEvaluator()

    @pytest.fixture
    def mock_analysis(self):
        """Create mock analysis result."""
        analysis = MagicMock()
        analysis.complexity.cyclomatic_complexity = 5
        analysis.complexity.cognitive_complexity = 8
        analysis.complexity.max_nesting_depth = 2
        analysis.complexity.max_function_length = 20
        analysis.complexity.avg_function_length = 15
        analysis.complexity.function_count = 3
        analysis.complexity.class_count = 1
        analysis.complexity.max_parameters = 3
        analysis.lines.total_lines = 50
        analysis.lines.comment_lines = 10
        analysis.naming_issues = []
        analysis.security_issues = []
        analysis.violations = []
        analysis.summary.overall_score = 85.0
        analysis.summary.grade = "B"
        return analysis

    def test_score_to_grade(self, evaluator):
        """Test score to grade conversion."""
        assert evaluator._score_to_grade(95) == "A"
        assert evaluator._score_to_grade(85) == "B"
        assert evaluator._score_to_grade(75) == "C"
        assert evaluator._score_to_grade(65) == "D"
        assert evaluator._score_to_grade(55) == "F"

    def test_calculate_technical_ability(self, evaluator, mock_analysis):
        """Test technical ability calculation."""
        score = evaluator._calculate_technical_ability(mock_analysis, "python")
        assert isinstance(score, DimensionScore)
        assert score.dimension == EvaluationDimension.TECHNICAL_ABILITY
        assert 0 <= score.score <= 100

    def test_calculate_code_quality(self, evaluator, mock_analysis):
        """Test code quality calculation."""
        score = evaluator._calculate_code_quality(mock_analysis)
        assert isinstance(score, DimensionScore)
        assert score.dimension == EvaluationDimension.CODE_QUALITY
        assert 0 <= score.score <= 100

    def test_calculate_innovation(self, evaluator, mock_analysis):
        """Test innovation calculation."""
        score = evaluator._calculate_innovation(mock_analysis)
        assert isinstance(score, DimensionScore)
        assert score.dimension == EvaluationDimension.INNOVATION
        assert 0 <= score.score <= 100

    def test_calculate_best_practices(self, evaluator, mock_analysis):
        """Test best practices calculation."""
        score = evaluator._calculate_best_practices(mock_analysis, "python")
        assert isinstance(score, DimensionScore)
        assert score.dimension == EvaluationDimension.BEST_PRACTICES
        assert 0 <= score.score <= 100

    def test_calculate_efficiency(self, evaluator, mock_analysis):
        """Test efficiency calculation."""
        score = evaluator._calculate_efficiency(mock_analysis)
        assert isinstance(score, DimensionScore)
        assert score.dimension == EvaluationDimension.EFFICIENCY
        assert 0 <= score.score <= 100

    def test_calculate_documentation(self, evaluator, mock_analysis):
        """Test documentation calculation."""
        score = evaluator._calculate_documentation(mock_analysis)
        assert isinstance(score, DimensionScore)
        assert score.dimension == EvaluationDimension.DOCUMENTATION
        assert 0 <= score.score <= 100

    def test_calculate_dimension_scores(self, evaluator, mock_analysis):
        """Test calculating all dimension scores."""
        scores = evaluator._calculate_dimension_scores(mock_analysis, "python")
        assert len(scores) == 6
        for score in scores:
            assert isinstance(score, DimensionScore)
            assert 0 <= score.score <= 100

    def test_generate_radar_chart_data(self, evaluator, mock_analysis):
        """Test radar chart data generation."""
        scores = evaluator._calculate_dimension_scores(mock_analysis, "python")
        radar = evaluator._generate_radar_chart_data(scores)
        assert isinstance(radar, RadarChartData)
        assert len(radar.labels) == 6
        assert len(radar.student_scores) == 6

    def test_generate_overall_summary(self, evaluator, mock_analysis):
        """Test overall summary generation."""
        scores = evaluator._calculate_dimension_scores(mock_analysis, "python")
        overall = sum(s.score * s.weight for s in scores)
        summary_en, summary_zh = evaluator._generate_overall_summary(overall, scores)
        assert summary_en
        assert summary_zh
        assert "Grade" in summary_en
        assert "等级" in summary_zh

    def test_identify_top_strengths(self, evaluator, mock_analysis):
        """Test identifying top strengths."""
        scores = evaluator._calculate_dimension_scores(mock_analysis, "python")
        strengths, strengths_zh = evaluator._identify_top_strengths(scores)
        assert isinstance(strengths, list)
        assert isinstance(strengths_zh, list)

    def test_identify_priority_improvements(self, evaluator, mock_analysis):
        """Test identifying priority improvements."""
        scores = evaluator._calculate_dimension_scores(mock_analysis, "python")
        improvements, improvements_zh = evaluator._identify_priority_improvements(scores)
        assert isinstance(improvements, list)
        assert isinstance(improvements_zh, list)

    def test_recommend_focus_areas(self, evaluator, mock_analysis):
        """Test recommending focus areas."""
        scores = evaluator._calculate_dimension_scores(mock_analysis, "python")
        focus, focus_zh = evaluator._recommend_focus_areas(scores)
        assert isinstance(focus, list)
        assert isinstance(focus_zh, list)
        assert len(focus) > 0


class TestMultiDimensionalEvaluationRequest:
    """Test MultiDimensionalEvaluationRequest schema."""

    def test_create_request_with_defaults(self):
        """Test creating request with default values."""
        request = MultiDimensionalEvaluationRequest(
            code="def hello(): pass",
            student_id="test_student"
        )
        assert request.language == "python"
        assert request.include_class_comparison is False
        assert request.class_id is None

    def test_create_request_with_class_comparison(self):
        """Test creating request with class comparison."""
        request = MultiDimensionalEvaluationRequest(
            code="def hello(): pass",
            student_id="test_student",
            include_class_comparison=True,
            class_id="class_001"
        )
        assert request.include_class_comparison is True
        assert request.class_id == "class_001"


class TestClassComparison:
    """Test ClassComparison schema."""

    def test_create_class_comparison(self):
        """Test creating class comparison."""
        comparison = ClassComparison(
            student_id="test_student",
            student_overall=85.0,
            class_average=75.0,
            class_median=76.0,
            class_max=95.0,
            class_min=55.0,
            percentile=80.0,
            rank=5,
            total_students=25,
            dimension_comparisons={
                "code_quality": {"student": 85, "class_avg": 75}
            }
        )
        assert comparison.student_id == "test_student"
        assert comparison.percentile == 80.0
        assert comparison.rank == 5


class TestAbilityAnalysisReport:
    """Test AbilityAnalysisReport schema."""

    def test_create_report(self):
        """Test creating ability analysis report."""
        radar = RadarChartData(
            labels=["A", "B"],
            labels_zh=["甲", "乙"],
            student_scores=[80, 75],
            max_scores=[100, 100]
        )
        report = AbilityAnalysisReport(
            report_id="test_report",
            student_id="test_student",
            overall_score=80.0,
            overall_grade="B",
            overall_summary="Good performance",
            overall_summary_zh="表现良好",
            radar_chart=radar
        )
        assert report.report_id == "test_report"
        assert report.overall_score == 80.0
        assert report.overall_grade == "B"

