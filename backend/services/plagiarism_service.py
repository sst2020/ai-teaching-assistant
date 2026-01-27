"""
Plagiarism Detection Service - AST-based code similarity detection
增强版：支持多种相似度算法、批量分析、原创性报告生成
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
    SubmissionComparison, CodeMatch, SubmissionRecord, SimilarityLevel, MatchType,
    # 新增类型
    SimilarityAlgorithm, CodeTransformationType, DetailedCodeMatch,
    SimilarityMatrixEntry, SimilarityMatrix, OriginalityReport,
    BatchAnalysisRequest, BatchAnalysisResponse, SubmissionData, PlagiarismSettings
)
from services.similarity_algorithms import similarity_algorithms


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

        # Weighted average - 使用新权重配置
        overall = struct_sim * 0.3 + token_sim * 0.25 + code_sim * 0.2

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


class EnhancedPlagiarismService:
    """
    增强的查重服务 - 支持批量分析、相似度矩阵、原创性报告
    """

    def __init__(self):
        # 使用更新后的默认权重配置
        self.settings = PlagiarismSettings(
            ast_weight=0.3,
            token_weight=0.25,
            text_weight=0.2,
            semantic_weight=0.15,
            order_invariant_weight=0.1
        )
        self._submission_cache: Dict[str, Dict[str, str]] = {}  # assignment_id -> {student_id: code}

    def update_settings(self, settings: PlagiarismSettings):
        """更新查重设置"""
        self.settings = settings

    async def batch_analyze(
        self, request: BatchAnalysisRequest
    ) -> BatchAnalysisResponse:
        """
        批量分析多个提交的相似度
        """
        report_id = str(uuid.uuid4())
        submissions = request.submissions
        n = len(submissions)

        # 初始化相似度矩阵
        student_ids = [s.student_id for s in submissions]
        student_names = [s.student_name or s.student_id for s in submissions]
        matrix = [[0.0] * n for _ in range(n)]
        entries: List[SimilarityMatrixEntry] = []
        suspicious_pairs: List[SubmissionComparison] = []

        # 计算所有两两之间的相似度
        total_comparisons = 0
        flagged_count = 0

        for i in range(n):
            matrix[i][i] = 1.0  # 自己与自己的相似度为1
            for j in range(i + 1, n):
                total_comparisons += 1
                code1 = submissions[i].code
                code2 = submissions[j].code

                # 使用改进的综合相似度算法
                similarity, scores = similarity_algorithms.advanced_combined_similarity(
                    code1, code2,
                    {
                        "ast": self.settings.ast_weight,
                        "token": self.settings.token_weight,
                        "cosine": self.settings.text_weight,
                        "semantic": 0.15,  # 固定语义权重
                        "order_invariant": 0.1  # 固定顺序不变权重
                    }
                )

                matrix[i][j] = round(similarity, 4)
                matrix[j][i] = round(similarity, 4)

                is_flagged = similarity >= request.similarity_threshold
                if is_flagged:
                    flagged_count += 1

                # 创建矩阵条目
                entry = SimilarityMatrixEntry(
                    student_id_1=student_ids[i],
                    student_id_2=student_ids[j],
                    student_name_1=student_names[i],
                    student_name_2=student_names[j],
                    similarity_score=round(similarity, 4),
                    algorithm_scores={k: round(v, 4) for k, v in scores.items()},
                    is_flagged=is_flagged
                )
                entries.append(entry)

                # 如果超过阈值，添加到可疑对列表
                if is_flagged:
                    # 检测代码变换
                    transformations = similarity_algorithms.detect_code_transformations(
                        code1, code2
                    )

                    # 查找匹配的代码段
                    matching_segments = similarity_algorithms.find_matching_segments(
                        code1, code2
                    )

                    matches = []
                    for seg in matching_segments[:5]:  # 最多5个匹配段
                        matches.append(CodeMatch(
                            match_type=MatchType.STRUCTURAL,
                            similarity=similarity,
                            code_snippet_1=seg[2][:200],  # 限制长度
                            code_snippet_2=seg[3][:200],
                            line_range_1=seg[0],
                            line_range_2=seg[1],
                            explanation=f"匹配代码段 (行 {seg[0][0]}-{seg[0][1]})"
                        ))

                    notes = self._generate_analysis_notes(similarity, transformations)

                    suspicious_pairs.append(SubmissionComparison(
                        submission_id_1=submissions[i].submission_id or f"sub_{i}",
                        submission_id_2=submissions[j].submission_id or f"sub_{j}",
                        student_id_1=student_ids[i],
                        student_id_2=student_ids[j],
                        similarity_score=round(similarity, 4),
                        matches=matches,
                        analysis_notes=notes
                    ))

        # 创建相似度矩阵对象
        similarity_matrix = SimilarityMatrix(
            report_id=report_id,
            assignment_id=request.assignment_id,
            created_at=datetime.utcnow(),
            student_ids=student_ids,
            student_names=student_names,
            matrix=matrix,
            entries=entries,
            threshold=request.similarity_threshold,
            flagged_count=flagged_count
        )

        # 生成原创性报告（如果需要）
        originality_reports = []
        if request.generate_reports:
            for i, sub in enumerate(submissions):
                report = self._generate_originality_report(
                    submission=sub,
                    index=i,
                    matrix=matrix,
                    submissions=submissions,
                    request=request
                )
                originality_reports.append(report)

        # 生成总结
        summary = self._generate_batch_summary(
            total=n,
            flagged=flagged_count,
            threshold=request.similarity_threshold
        )

        return BatchAnalysisResponse(
            report_id=report_id,
            assignment_id=request.assignment_id,
            created_at=datetime.utcnow(),
            total_submissions=n,
            total_comparisons=total_comparisons,
            flagged_count=flagged_count,
            similarity_matrix=similarity_matrix,
            suspicious_pairs=suspicious_pairs,
            originality_reports=originality_reports,
            summary=summary
        )

    def _generate_originality_report(
        self,
        submission: SubmissionData,
        index: int,
        matrix: List[List[float]],
        submissions: List[SubmissionData],
        request: BatchAnalysisRequest
    ) -> OriginalityReport:
        """生成单个提交的原创性报告"""
        report_id = str(uuid.uuid4())

        # 计算原创性分数（100 - 最高相似度 * 100）
        similarities = [matrix[index][j] for j in range(len(matrix)) if j != index]
        max_similarity = max(similarities) if similarities else 0.0
        originality_score = round((1.0 - max_similarity) * 100, 1)

        # 找出相似的提交
        similar_submissions = []
        detailed_matches = []

        for j, sim in enumerate(matrix[index]):
            if j != index and sim >= request.similarity_threshold:
                similar_submissions.append(submissions[j].student_id)

                # 生成详细匹配信息
                code1 = submission.code
                code2 = submissions[j].code

                # 检测代码变换
                transformations = similarity_algorithms.detect_code_transformations(
                    code1, code2
                )

                # 查找匹配段
                segments = similarity_algorithms.find_matching_segments(code1, code2)

                for seg in segments[:3]:  # 每对最多3个匹配段
                    detailed_matches.append(DetailedCodeMatch(
                        source_student_id=submission.student_id,
                        target_student_id=submissions[j].student_id,
                        source_start_line=seg[0][0],
                        source_end_line=seg[0][1],
                        source_start_col=0,
                        source_end_col=0,
                        target_start_line=seg[1][0],
                        target_end_line=seg[1][1],
                        target_start_col=0,
                        target_end_col=0,
                        source_snippet=seg[2][:300],
                        target_snippet=seg[3][:300],
                        similarity=sim,
                        algorithm=SimilarityAlgorithm.COMBINED,
                        transformation_type=transformations[0] if transformations else None,
                        explanation=f"与 {submissions[j].student_name or submissions[j].student_id} 的代码相似"
                    ))

        # 计算各算法的相似度分解
        similarity_breakdown = {}
        if similar_submissions:
            # 取最相似的那个进行分解
            most_similar_idx = matrix[index].index(max_similarity)
            if most_similar_idx != index:
                _, scores = similarity_algorithms.combined_similarity(
                    submission.code,
                    submissions[most_similar_idx].code
                )
                similarity_breakdown = {k: round(v, 4) for k, v in scores.items()}

        # 检测代码变换类型
        detected_transformations = []
        for j in range(len(submissions)):
            if j != index and matrix[index][j] >= request.similarity_threshold:
                trans = similarity_algorithms.detect_code_transformations(
                    submission.code, submissions[j].code
                )
                detected_transformations.extend(trans)
        detected_transformations = list(set(detected_transformations))

        # 生成改进建议
        suggestions = self._generate_improvement_suggestions(
            originality_score, max_similarity, detected_transformations
        )

        # 确定风险等级
        risk_level = self._get_risk_level(max_similarity)

        # 生成总结
        summary = self._generate_report_summary(
            originality_score, len(similar_submissions), detected_transformations
        )

        return OriginalityReport(
            report_id=report_id,
            submission_id=submission.submission_id or f"sub_{index}",
            student_id=submission.student_id,
            student_name=submission.student_name or submission.student_id,
            assignment_id=request.assignment_id,
            created_at=datetime.utcnow(),
            originality_score=originality_score,
            similarity_breakdown=similarity_breakdown,
            detailed_matches=detailed_matches,
            similar_submissions=similar_submissions,
            detected_transformations=detected_transformations,
            improvement_suggestions=suggestions,
            summary=summary,
            risk_level=risk_level
        )

    def _generate_analysis_notes(
        self, similarity: float, transformations: List[CodeTransformationType]
    ) -> str:
        """生成分析备注"""
        notes = []

        if similarity >= 0.9:
            notes.append("⚠️ 极高相似度，强烈建议人工审核")
        elif similarity >= 0.7:
            notes.append("⚡ 高相似度，建议进一步检查")

        if CodeTransformationType.VARIABLE_RENAME in transformations:
            notes.append("检测到变量重命名")
        if CodeTransformationType.FUNCTION_RENAME in transformations:
            notes.append("检测到函数重命名")
        if CodeTransformationType.COMMENT_MODIFICATION in transformations:
            notes.append("检测到注释修改")
        if CodeTransformationType.WHITESPACE_CHANGE in transformations:
            notes.append("检测到空白符修改")
        if CodeTransformationType.REORDER_STATEMENTS in transformations:
            notes.append("检测到语句重排序")

        return " | ".join(notes) if notes else "相似度检测完成"

    def _generate_improvement_suggestions(
        self,
        originality_score: float,
        max_similarity: float,
        transformations: List[CodeTransformationType]
    ) -> List[str]:
        """生成改进建议"""
        suggestions = []

        if originality_score < 30:
            suggestions.append("代码原创性较低，建议重新独立完成作业")
            suggestions.append("尝试使用不同的算法思路解决问题")
            suggestions.append("添加个人风格的代码注释和文档")
        elif originality_score < 60:
            suggestions.append("部分代码与他人相似，建议检查并修改")
            suggestions.append("尝试优化代码结构，使用不同的实现方式")
            suggestions.append("增加代码的个性化特征")
        elif originality_score < 80:
            suggestions.append("代码有一定原创性，可进一步优化")
            suggestions.append("考虑添加更多的错误处理和边界检查")
        else:
            suggestions.append("代码原创性良好，继续保持")

        if CodeTransformationType.VARIABLE_RENAME in transformations:
            suggestions.append("仅修改变量名不能提高原创性，建议重新设计代码逻辑")

        if CodeTransformationType.COMMENT_MODIFICATION in transformations:
            suggestions.append("仅修改注释不能提高原创性，建议重新实现核心功能")

        return suggestions

    def _get_risk_level(self, max_similarity: float) -> SimilarityLevel:
        """获取风险等级"""
        if max_similarity >= 0.9:
            return SimilarityLevel.VERY_HIGH
        elif max_similarity >= 0.7:
            return SimilarityLevel.HIGH
        elif max_similarity >= 0.5:
            return SimilarityLevel.MEDIUM
        elif max_similarity >= 0.3:
            return SimilarityLevel.LOW
        return SimilarityLevel.NONE

    def _generate_report_summary(
        self,
        originality_score: float,
        similar_count: int,
        transformations: List[CodeTransformationType]
    ) -> str:
        """生成报告总结"""
        if originality_score >= 80:
            status = "原创性良好"
        elif originality_score >= 60:
            status = "原创性一般"
        elif originality_score >= 40:
            status = "原创性较低"
        else:
            status = "原创性很低"

        summary = f"原创性评分: {originality_score}分 ({status})"

        if similar_count > 0:
            summary += f"，发现 {similar_count} 份相似作业"

        if transformations:
            trans_names = {
                CodeTransformationType.VARIABLE_RENAME: "变量重命名",
                CodeTransformationType.FUNCTION_RENAME: "函数重命名",
                CodeTransformationType.COMMENT_MODIFICATION: "注释修改",
                CodeTransformationType.WHITESPACE_CHANGE: "空白符修改",
                CodeTransformationType.REORDER_STATEMENTS: "语句重排序",
            }
            trans_str = "、".join([trans_names.get(t, str(t)) for t in transformations[:3]])
            summary += f"，检测到: {trans_str}"

        return summary

    def _generate_batch_summary(
        self, total: int, flagged: int, threshold: float
    ) -> str:
        """生成批量分析总结"""
        percentage = (flagged / (total * (total - 1) / 2) * 100) if total > 1 else 0
        return (
            f"共分析 {total} 份作业，"
            f"发现 {flagged} 对可疑相似（阈值: {threshold:.0%}），"
            f"可疑比例: {percentage:.1f}%"
        )


# 增强服务单例
enhanced_plagiarism_service = EnhancedPlagiarismService()

