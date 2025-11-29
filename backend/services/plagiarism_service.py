"""
Plagiarism Detection Service - AST-based code similarity detection
"""
import ast
import hashlib
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from collections import defaultdict

from schemas.plagiarism import (
    PlagiarismCheckRequest, PlagiarismReport, BatchPlagiarismReport,
    SubmissionComparison, CodeMatch, SubmissionRecord, SimilarityLevel, MatchType
)


@dataclass
class CodeFingerprint:
    """Fingerprint of code structure for comparison."""
    submission_id: str
    student_id: str
    ast_hash: str
    token_sequence: List[str]
    structure_signature: str
    normalized_code: str


@dataclass
class SubmissionStore:
    """In-memory store for submissions (replace with DB in production)."""
    submissions: Dict[str, List[CodeFingerprint]] = field(default_factory=lambda: defaultdict(list))

    def add(self, course_id: str, fingerprint: CodeFingerprint):
        self.submissions[course_id].append(fingerprint)

    def get_all(self, course_id: str) -> List[CodeFingerprint]:
        return self.submissions.get(course_id, [])


class PlagiarismDetectionService:
    """Service for detecting code plagiarism using AST analysis."""

    def __init__(self):
        self.store = SubmissionStore()
        self.similarity_threshold = 0.7

    async def check_plagiarism(self, request: PlagiarismCheckRequest) -> PlagiarismReport:
        """Check a submission for plagiarism against stored submissions."""
        report_id = str(uuid.uuid4())
        fingerprint = self._create_fingerprint(request.submission_id, request.student_id, request.code)

        # Get existing submissions for comparison
        existing = self.store.get_all(request.course_id)
        comparisons = []
        highest_similarity = 0.0

        for other in existing:
            if other.student_id == request.student_id:
                continue  # Skip self-comparison

            similarity, matches = self._compare_fingerprints(fingerprint, other)
            if similarity >= self.similarity_threshold:
                comparisons.append(SubmissionComparison(
                    submission_id_1=fingerprint.submission_id,
                    submission_id_2=other.submission_id,
                    student_id_1=fingerprint.student_id,
                    student_id_2=other.student_id,
                    similarity_score=similarity,
                    matches=matches,
                    analysis_notes=self._generate_notes(similarity, matches)
                ))
                highest_similarity = max(highest_similarity, similarity)

        # Store this submission for future comparisons
        self.store.add(request.course_id, fingerprint)

        return PlagiarismReport(
            report_id=report_id,
            submission_id=request.submission_id,
            checked_at=datetime.utcnow(),
            overall_similarity=highest_similarity,
            similarity_level=self._get_similarity_level(highest_similarity),
            is_flagged=highest_similarity >= self.similarity_threshold,
            comparisons=comparisons,
            summary=self._generate_summary(highest_similarity, len(comparisons))
        )

    async def batch_check(self, course_id: str, submissions: List[dict]) -> BatchPlagiarismReport:
        """Check multiple submissions against each other."""
        fingerprints = []
        for sub in submissions:
            fp = self._create_fingerprint(sub['submission_id'], sub['student_id'], sub['code'])
            fingerprints.append(fp)

        all_comparisons = []
        flagged_pairs = []

        for i, fp1 in enumerate(fingerprints):
            for fp2 in fingerprints[i+1:]:
                similarity, matches = self._compare_fingerprints(fp1, fp2)
                if similarity >= self.similarity_threshold:
                    comp = SubmissionComparison(
                        submission_id_1=fp1.submission_id, submission_id_2=fp2.submission_id,
                        student_id_1=fp1.student_id, student_id_2=fp2.student_id,
                        similarity_score=similarity, matches=matches,
                        analysis_notes=self._generate_notes(similarity, matches)
                    )
                    all_comparisons.append(comp)
                    flagged_pairs.append((fp1.student_id, fp2.student_id))

        return BatchPlagiarismReport(
            report_id=str(uuid.uuid4()), course_id=course_id, checked_at=datetime.utcnow(),
            total_submissions=len(submissions), flagged_pairs=len(flagged_pairs),
            comparisons=all_comparisons,
            summary=f"Checked {len(submissions)} submissions. Found {len(flagged_pairs)} suspicious pairs."
        )

    def _create_fingerprint(self, submission_id: str, student_id: str, code: str) -> CodeFingerprint:
        """Create a fingerprint from code for comparison."""
        normalized = self._normalize_code(code)
        tokens = self._tokenize_code(code)
        structure = self._get_structure_signature(code)
        ast_hash = hashlib.md5(structure.encode()).hexdigest()

        return CodeFingerprint(
            submission_id=submission_id, student_id=student_id,
            ast_hash=ast_hash, token_sequence=tokens,
            structure_signature=structure, normalized_code=normalized
        )

    def _normalize_code(self, code: str) -> str:
        """Normalize code by removing variable names and comments."""
        try:
            tree = ast.parse(code)
            return ast.dump(tree)
        except SyntaxError:
            return code.lower().strip()

    def _tokenize_code(self, code: str) -> List[str]:
        """Tokenize code into a sequence of tokens."""
        import tokenize
        import io
        tokens = []
        try:
            for tok in tokenize.generate_tokens(io.StringIO(code).readline):
                if tok.type not in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
                                    tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING):
                    # Use token type for identifiers to ignore variable names
                    if tok.type == tokenize.NAME:
                        tokens.append('NAME')
                    elif tok.type == tokenize.NUMBER:
                        tokens.append('NUMBER')
                    elif tok.type == tokenize.STRING:
                        tokens.append('STRING')
                    else:
                        tokens.append(tok.string)
        except tokenize.TokenizeError:
            # Fallback: simple word tokenization
            tokens = code.split()
        return tokens

    def _get_structure_signature(self, code: str) -> str:
        """Get structural signature from AST."""
        try:
            tree = ast.parse(code)
            return self._ast_to_signature(tree)
        except SyntaxError:
            return ""

    def _ast_to_signature(self, node: ast.AST) -> str:
        """Convert AST to structural signature."""
        parts = [type(node).__name__]
        for child in ast.iter_child_nodes(node):
            parts.append(self._ast_to_signature(child))
        return f"({','.join(parts)})"

    def _compare_fingerprints(self, fp1: CodeFingerprint, fp2: CodeFingerprint) -> Tuple[float, List[CodeMatch]]:
        """Compare two fingerprints and return similarity score and matches."""
        matches = []

        # AST structure similarity
        struct_sim = 1.0 if fp1.ast_hash == fp2.ast_hash else SequenceMatcher(
            None, fp1.structure_signature, fp2.structure_signature
        ).ratio()

        # Token sequence similarity
        token_sim = SequenceMatcher(None, fp1.token_sequence, fp2.token_sequence).ratio()

        # Normalized code similarity
        code_sim = SequenceMatcher(None, fp1.normalized_code, fp2.normalized_code).ratio()

        # Weighted average
        overall = struct_sim * 0.4 + token_sim * 0.35 + code_sim * 0.25

        if struct_sim > 0.8:
            matches.append(CodeMatch(
                match_type=MatchType.STRUCTURAL, similarity=struct_sim,
                code_snippet_1="[AST structure match]", code_snippet_2="[AST structure match]",
                line_range_1=(1, 1), line_range_2=(1, 1),
                explanation="Code structure is highly similar"
            ))

        if token_sim > 0.8:
            matches.append(CodeMatch(
                match_type=MatchType.TOKEN_SEQUENCE, similarity=token_sim,
                code_snippet_1="[Token sequence match]", code_snippet_2="[Token sequence match]",
                line_range_1=(1, 1), line_range_2=(1, 1),
                explanation="Token patterns are highly similar"
            ))

        return round(overall, 3), matches

    def _get_similarity_level(self, score: float) -> SimilarityLevel:
        if score >= 0.9: return SimilarityLevel.VERY_HIGH
        if score >= 0.7: return SimilarityLevel.HIGH
        if score >= 0.5: return SimilarityLevel.MEDIUM
        if score >= 0.3: return SimilarityLevel.LOW
        return SimilarityLevel.NONE

    def _generate_notes(self, similarity: float, matches: List[CodeMatch]) -> str:
        if similarity >= 0.9:
            return "Very high similarity detected. Manual review strongly recommended."
        if similarity >= 0.7:
            return "Significant similarity found. Review for potential plagiarism."
        return "Some similarity detected."

    def _generate_summary(self, highest: float, count: int) -> str:
        if count == 0:
            return "No significant similarities found with existing submissions."
        return f"Found {count} similar submission(s). Highest similarity: {highest:.1%}"


plagiarism_service = PlagiarismDetectionService()

