"""
SQLAlchemy model for storing code analysis results.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from models.base import Base


class AnalysisResult(Base):
    """Model for storing code analysis results."""
    __tablename__ = "analysis_results"

    id = Column(String(36), primary_key=True)
    file_id = Column(String(100), ForeignKey("code_files.file_id"), nullable=True, index=True)
    language = Column(String(50), nullable=False)
    analyzed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Overall metrics
    overall_score = Column(Float, nullable=False, default=0.0)
    grade = Column(String(2), nullable=False, default="F")

    # Line metrics
    total_lines = Column(Integer, default=0)
    code_lines = Column(Integer, default=0)
    comment_lines = Column(Integer, default=0)
    blank_lines = Column(Integer, default=0)
    docstring_lines = Column(Integer, default=0)

    # Complexity metrics
    cyclomatic_complexity = Column(Integer, default=0)
    cognitive_complexity = Column(Integer, default=0)
    max_nesting_depth = Column(Integer, default=0)
    max_function_length = Column(Integer, default=0)
    max_parameters = Column(Integer, default=0)
    total_functions = Column(Integer, default=0)

    # Structure metrics
    total_classes = Column(Integer, default=0)
    total_methods = Column(Integer, default=0)
    average_function_length = Column(Float, default=0.0)

    # Violation counts
    total_violations = Column(Integer, default=0)
    critical_violations = Column(Integer, default=0)
    warnings = Column(Integer, default=0)
    info_violations = Column(Integer, default=0)

    # Category scores (stored as JSON)
    category_scores = Column(JSON, default=dict)

    # Detailed violations (stored as JSON)
    violations = Column(JSON, default=list)

    # Recommendations (stored as JSON)
    recommendations = Column(JSON, default=list)

    # Naming convention results (stored as JSON)
    naming_results = Column(JSON, default=dict)

    # Relationship to CodeFile
    code_file = relationship("CodeFile", back_populates="analysis_results")

    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, file_id={self.file_id}, score={self.overall_score})>"

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "file_id": self.file_id,
            "language": self.language,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
            "overall_score": self.overall_score,
            "grade": self.grade,
            "line_metrics": {
                "total_lines": self.total_lines,
                "code_lines": self.code_lines,
                "comment_lines": self.comment_lines,
                "blank_lines": self.blank_lines,
                "docstring_lines": self.docstring_lines
            },
            "complexity": {
                "cyclomatic_complexity": self.cyclomatic_complexity,
                "cognitive_complexity": self.cognitive_complexity,
                "max_nesting_depth": self.max_nesting_depth,
                "max_function_length": self.max_function_length,
                "max_parameters": self.max_parameters,
                "total_functions": self.total_functions
            },
            "structure": {
                "total_classes": self.total_classes,
                "total_methods": self.total_methods,
                "average_function_length": self.average_function_length
            },
            "summary": {
                "total_violations": self.total_violations,
                "critical_violations": self.critical_violations,
                "warnings": self.warnings,
                "info_violations": self.info_violations
            },
            "category_scores": self.category_scores,
            "violations": self.violations,
            "recommendations": self.recommendations,
            "naming_results": self.naming_results
        }

