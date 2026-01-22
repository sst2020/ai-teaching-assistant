"""Service for project report intelligent analysis.

This service is responsible for:
- Parsing project report files (PDF/DOCX/Markdown)
- Extracting document structure (sections, references, appendices)
- Evaluating report quality and completeness
- Analyzing logic structure and innovation
- Assessing language quality and formatting
- Generating improvement suggestions

Note: This initial implementation only defines the service skeleton and
method signatures. Detailed logic will be implemented incrementally.
"""

from __future__ import annotations

import re
import uuid
from typing import Tuple

from schemas import report_analysis as schemas


class ReportAnalysisService:
    """Core service for project report analysis."""

    def __init__(self) -> None:
        # Placeholder for future configuration and dependencies
        # e.g., AI model clients, reference corpora, etc.
        pass

    async def analyze_report(
        self,
        request: schemas.ReportAnalysisRequest,
    ) -> schemas.ReportAnalysisResponse:
        """Analyze a project report based on plain text content.

        This is the main entry point when analysis is triggered via API.
        File-based analysis (PDF/DOCX/Markdown) will be supported by
        dedicated endpoints that first parse the file, then call this method.
        """

        # Step 1: basic parse result from plain text
        parsed = await self._parse_from_text(request)

        # Step 2: quality metrics (completeness etc.)
        quality = self._evaluate_quality(parsed)

        # Step 3: logic and innovation analysis
        logic, innovation = await self._analyze_logic_and_innovation(parsed)

        # Step 4: language quality, formatting checks and suggestions
        language_quality, formatting, suggestions = await self._generate_suggestions(parsed)

        # Step 5: aggregate overall score and summary (simple placeholder for now)
        overall_score = float(
            min(
                100.0,
                max(
                    0.0,
                    0.3 * quality.overall_completeness_score
                    + 0.25 * logic.argumentation_score
                    + 0.2 * innovation.novelty_score
                    + 0.25 * language_quality.academic_tone_score,
                ),
            )
        )

        summary = "项目报告分析结果：已完成结构解析、质量评估、逻辑与创新性分析，以及语言和格式检查。"  # noqa: E501

        return schemas.ReportAnalysisResponse(
            report_id=str(uuid.uuid4()),
            file_name=request.file_name,
            parsed=parsed,
            quality=quality,
            logic=logic,
            innovation=innovation,
            language_quality=language_quality,
            formatting=formatting,
            suggestions=suggestions,
            overall_score=overall_score,
            summary=summary,
        )

    async def _parse_from_text(
        self, request: schemas.ReportAnalysisRequest
    ) -> schemas.ReportParseResult:
        """Create a parse result from plain text content with real structure detection.

        This method detects document sections, references, and other structural elements.
        """
        content = request.content
        language = request.language or schemas.ReportLanguage.MIXED

        # Detect document sections based on common academic report patterns
        sections = await self._detect_sections(content, language)

        # Extract references
        references = await self._extract_references(content)

        return schemas.ReportParseResult(
            file_id=None,
            file_name=request.file_name,
            file_type=request.file_type,
            language=language,
            sections=sections,
            references=references,
            raw_text=content,
        )

    async def _detect_sections(self, content: str, language: schemas.ReportLanguage) -> List[schemas.ReportSection]:
        """Detect document sections based on heading patterns."""
        # Define section patterns based on language
        if language == schemas.ReportLanguage.ZH:
            section_patterns = {
                schemas.SectionType.ABSTRACT: [r'(?:^|\n)\s*摘要\s*', r'(?:^|\n)\s*摘\s+要\s*'],
                schemas.SectionType.INTRODUCTION: [r'(?:^|\n)\s*引言\s*', r'(?:^|\n)\s*绪论\s*', r'(?:^|\n)\s*介绍\s*'],
                schemas.SectionType.RELATED_WORK: [r'(?:^|\n)\s*相关工作\s*', r'(?:^|\n)\s*文献综述\s*', r'(?:^|\n)\s*研究现状\s*'],
                schemas.SectionType.METHOD: [r'(?:^|\n)\s*方法\s*', r'(?:^|\n)\s*算法\s*', r'(?:^|\n)\s*实现\s*', r'(?:^|\n)\s*设计\s*'],
                schemas.SectionType.RESULTS: [r'(?:^|\n)\s*实验\s*', r'(?:^|\n)\s*结果\s*', r'(?:^|\n)\s*验证\s*'],
                schemas.SectionType.DISCUSSION: [r'(?:^|\n)\s*讨论\s*', r'(?:^|\n)\s*分析\s*'],
                schemas.SectionType.CONCLUSION: [r'(?:^|\n)\s*结论\s*', r'(?:^|\n)\s*总结\s*'],
                schemas.SectionType.REFERENCES: [r'(?:^|\n)\s*参考文献\s*', r'(?:^|\n)\s*引用\s*'],
                schemas.SectionType.APPENDIX: [r'(?:^|\n)\s*附录\s*', r'(?:^|\n)\s*附件\s*'],
            }
        else:  # English or mixed
            section_patterns = {
                schemas.SectionType.ABSTRACT: [r'(?:^|\n)\s*Abstract\s*', r'(?:^|\n)\s*ABSTRACT\s*'],
                schemas.SectionType.INTRODUCTION: [r'(?:^|\n)\s*Introduction\s*', r'(?:^|\n)\s*INTRODUCTION\s*'],
                schemas.SectionType.RELATED_WORK: [r'(?:^|\n)\s*Related Work\s*', r'(?:^|\n)\s*Literature Review\s*', r'(?:^|\n)\s*Background\s*'],
                schemas.SectionType.METHOD: [r'(?:^|\n)\s*Method(?:ology)?\s*', r'(?:^|\n)\s*Algorithm\s*', r'(?:^|\n)\s*Implementation\s*', r'(?:^|\n)\s*Design\s*'],
                schemas.SectionType.RESULTS: [r'(?:^|\n)\s*Results?\s*', r'(?:^|\n)\s*Experiments?\s*', r'(?:^|\n)\s*Evaluation\s*'],
                schemas.SectionType.DISCUSSION: [r'(?:^|\n)\s*Discussion\s*', r'(?:^|\n)\s*Analysis\s*'],
                schemas.SectionType.CONCLUSION: [r'(?:^|\n)\s*Conclusion\s*', r'(?:^|\n)\s*Summary\s*'],
                schemas.SectionType.REFERENCES: [r'(?:^|\n)\s*References?\s*', r'(?:^|\n)\s*Bibliography\s*'],
                schemas.SectionType.APPENDIX: [r'(?:^|\n)\s*Appendix\s*', r'(?:^|\n)\s*Appendices\s*'],
            }

        # Split content into paragraphs/sections
        paragraphs = content.split('\n\n')

        sections = []
        current_section_idx = 0
        section_id_counter = 0

        # Look for headings and section content
        lines = content.split('\n')

        # First, identify potential headers
        header_positions = []
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Check for section headers (lines that are likely headers)
            # Heuristic: short lines with capital letters or Chinese characters followed by longer content
            likely_header = False
            section_type = schemas.SectionType.OTHER

            # Check for specific section patterns
            for sec_type, patterns in section_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, f"\n{line_stripped}\n", re.IGNORECASE):
                        likely_header = True
                        section_type = sec_type
                        break
                if likely_header:
                    break

            # Alternative heuristic for detecting headers: short line with title-like characteristics
            if not likely_header and len(line_stripped) < 100:
                # Check if it looks like a header (capitalized, or contains common heading words)
                if (line_stripped.isupper() or
                    re.match(r'^\d+[.\d]*\s+', line_stripped) or  # Numbered headings like "1. Introduction"
                    (len(line_stripped) > 3 and line_stripped[0].isupper() and not line_stripped.lower().startswith(('the ', 'and ', 'or ', 'but '))) or
                    line_stripped.startswith('#')):  # Markdown headers
                    likely_header = True
                    # Don't assign a specific type if not matched by pattern

            if likely_header:
                header_positions.append((i, line_stripped, section_type))

        # Now extract content for each section
        for idx, (pos, title, section_type) in enumerate(header_positions):
            # Find content until next header or end of document
            if idx + 1 < len(header_positions):
                end_pos = header_positions[idx + 1][0]
                section_content = "\n".join(lines[pos + 1:end_pos]).strip()
            else:
                # From this header to the end of document
                section_content = "\n".join(lines[pos + 1:]).strip()

            section = schemas.ReportSection(
                id=f"section-{section_id_counter}",
                title=title,
                level=self._determine_heading_level(title),
                section_type=section_type,
                order_index=section_id_counter,
                text=section_content,
                children=[],
            )

            sections.append(section)
            section_id_counter += 1

        # If no sections were detected, create a single section with all content
        if not sections:
            sections = [
                schemas.ReportSection(
                    id="section-0",
                    title="正文" if language == schemas.ReportLanguage.ZH else "Main Content",
                    level=1,
                    section_type=schemas.SectionType.OTHER,
                    order_index=0,
                    text=content,
                    children=[],
                )
            ]

        return sections

    def _determine_heading_level(self, title: str) -> int:
        """Determine heading level based on format (e.g., 1.1.2 would be level 3)."""
        # Check for numbered headings like "1.", "1.1.", "1.1.1."
        match = re.match(r'^(\d+\.)*\d+\.', title)
        if match:
            num_dots = match.group(0).count('.')
            return min(num_dots + 1, 6)  # Max level 6
        return 1  # Default to level 1

    async def _extract_references(self, content: str) -> List[schemas.ReferenceEntry]:
        """Extract references from the content."""
        # Common reference patterns
        ref_patterns = [
            # APA style: (Author, Year)
            r'[A-Z][a-z]+,\s*[A-Z]\.\s*\([^0-9]{0,4}[12][0-9]{3}[^\)]*\)',
            # Numbered references: [1], [2], etc.
            r'\[[0-9]+\][^\n]*',
            # Simple author-year: Author (Year)
            r'[A-Z][a-z]+\s*\([^0-9]{0,4}[12][0-9]{3}[^\)]*\)',
        ]

        references = []
        for pattern in ref_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                # Determine format based on pattern
                if '[' in match and ']' in match:
                    format_type = schemas.ReferenceFormat.GBT7714  # Using GBT7714 for numbered refs
                elif '(' in match and ')' in match:
                    format_type = schemas.ReferenceFormat.APA
                else:
                    format_type = schemas.ReferenceFormat.UNKNOWN

                ref_entry = schemas.ReferenceEntry(
                    raw_text=match.strip(),
                    detected_format=format_type,
                    is_valid=True,  # Simplified validation
                    problems=[]
                )
                references.append(ref_entry)

        return references

    def _evaluate_quality(
        self, parsed: schemas.ReportParseResult
    ) -> schemas.ReportQualityMetrics:
        """Evaluate basic completeness and structural quality.

        For now, we compute simple metrics based on total word count and
        a single chapter. More detailed logic (per-chapter stats, required
        sections, figure/table stats, references) will be added later.
        """

        text = parsed.raw_text or ""
        # Rough word count: split by whitespace
        words = [w for w in text.split() if w.strip()]
        total_word_count = len(words)

        if total_word_count < 1000:
            word_eval = "too_short"
            completeness_score = 40.0
        elif total_word_count < 3000:
            word_eval = "normal"
            completeness_score = 75.0
        else:
            word_eval = "too_long"
            completeness_score = 65.0

        chapter_stats = [
            schemas.ChapterLengthStats(
                section_id=s.id,
                title=s.title,
                word_count=total_word_count,
                proportion=1.0,
                evaluation=word_eval,
            )
            for s in parsed.sections
        ] or [
            schemas.ChapterLengthStats(
                section_id="section-0",
                title="全文",
                word_count=total_word_count,
                proportion=1.0,
                evaluation=word_eval,
            )
        ]

        figure_table = schemas.FigureTableStats(
            figure_count=0,
            table_count=0,
            evaluation="未检测到图表，后续将通过解析和规则进一步统计。",
        )

        ref_stats = schemas.ReferenceStats(
            total_count=0,
            valid_count=0,
            expected_min_count=0,
            format_compliance_ratio=0.0,
            evaluation="参考文献暂未解析，后续将增加格式与数量检查。",
        )

        required_map = {st: False for st in schemas.SectionType}

        return schemas.ReportQualityMetrics(
            total_word_count=total_word_count,
            word_count_evaluation=word_eval,
            required_sections_present=required_map,
            chapter_length_stats=chapter_stats,
            figure_table_stats=figure_table,
            reference_stats=ref_stats,
            overall_completeness_score=completeness_score,
        )

    async def _analyze_logic_and_innovation(
        self, parsed: schemas.ReportParseResult
    ) -> Tuple[schemas.LogicAnalysisResult, schemas.InnovationAnalysisResult]:
        """Analyze logic structure and innovation using NLP techniques."""

        # Analyze logic structure
        logic_issues = await self._identify_logic_issues(parsed)
        section_order_score = await self._evaluate_section_order(parsed)
        coherence_score = await self._evaluate_coherence(parsed)
        argumentation_score = await self._evaluate_argumentation(parsed)

        logic = schemas.LogicAnalysisResult(
            section_order_score=section_order_score,
            coherence_score=coherence_score,
            argumentation_score=argumentation_score,
            issues=logic_issues,
            summary=self._generate_logic_summary(section_order_score, coherence_score, argumentation_score),
        )

        # Analyze innovation
        innovation_score = await self._evaluate_innovation(parsed)
        innovation_points = await self._identify_innovation_points(parsed)

        innovation = schemas.InnovationAnalysisResult(
            novelty_score=innovation_score,
            difference_summary=self._generate_difference_summary(innovation_score),
            innovation_points=innovation_points,
        )

        return logic, innovation

    async def _identify_logic_issues(self, parsed: schemas.ReportParseResult) -> List[schemas.LogicIssue]:
        """Identify logic issues in the report."""
        issues = []
        text = parsed.raw_text or ""

        # Look for common logic issues
        sentences = self._split_sentences(text)

        # Check for missing evidence indicators
        for i, sentence in enumerate(sentences):
            if self._has_missing_evidence_indicators(sentence):
                issues.append(schemas.LogicIssue(
                    issue_type=schemas.LogicIssueType.MISSING_EVIDENCE,
                    section_id=None,
                    paragraph_index=i,
                    description=f"句子 '{sentence[:50]}...' 包含断言但缺乏证据支撑",
                    suggested_fix="请提供更多数据、引用或实验证据来支撑此断言"
                ))

        # Check for logical gaps
        for i in range(len(sentences)-1):
            if self._has_logical_gap(sentences[i], sentences[i+1]):
                issues.append(schemas.LogicIssue(
                    issue_type=schemas.LogicIssueType.LOGICAL_GAP,
                    section_id=None,
                    paragraph_index=i,
                    description=f"句子之间存在逻辑跳跃：'{sentences[i][:30]}...' 到 '{sentences[i+1][:30]}...'",
                    suggested_fix="请添加过渡句或解释来连接这两个概念"
                ))

        # Check for weak conclusions
        conclusion_sentences = [s for s in sentences if self._appears_to_be_conclusion(s)]
        for sent in conclusion_sentences:
            if self._has_weak_conclusion(sent):
                issues.append(schemas.LogicIssue(
                    issue_type=schemas.LogicIssueType.WEAK_CONCLUSION,
                    section_id=None,
                    paragraph_index=sentences.index(sent),
                    description=f"结论句 '{sent[:50]}...' 缺乏充分的支撑",
                    suggested_fix="请确保结论基于前文的论证和证据"
                ))

        return issues

    def _has_missing_evidence_indicators(self, sentence: str) -> bool:
        """Check if sentence has indicators of missing evidence."""
        # Keywords that suggest claims without evidence
        claim_words = [
            '表明', '说明', '证明', '证实', '显示', '揭示', 'demonstrates', 'shows', 'proves',
            'indicates', 'reveals', 'confirms', 'suggests', 'implies'
        ]
        weak_evidence_words = [
            '可能', '或许', '也许', '大概', 'possibly', 'perhaps', 'maybe', 'likely'
        ]

        sentence_lower = sentence.lower()
        has_claim = any(word in sentence for word in claim_words)
        has_weak_evidence = any(word in sentence for word in weak_evidence_words)

        return has_claim and has_weak_evidence

    def _has_logical_gap(self, sent1: str, sent2: str) -> bool:
        """Check if there's a logical gap between sentences."""
        # Simple heuristic: if sentences discuss completely different topics without transition
        sent1_lower = sent1.lower()
        sent2_lower = sent2.lower()

        # Look for transition words that indicate logical connection
        transition_words = [
            '因此', '所以', '因而', '于是', '此外', '而且', '同时', '然而', '但是',
            'therefore', 'thus', 'hence', 'so', 'additionally', 'furthermore',
            'meanwhile', 'however', 'but', 'although'
        ]

        has_transition = any(word in sent2_lower for word in transition_words)

        # If no transition words and topics seem unrelated, likely a gap
        if not has_transition:
            # Very basic topic similarity check (could be improved with NLP)
            words1 = set(sent1_lower.split())
            words2 = set(sent2_lower.split())
            common_words = words1.intersection(words2)
            # If less than 10% overlap in words, might indicate a gap
            if len(common_words) / max(len(words1), 1) < 0.1:
                return True

        return False

    def _appears_to_be_conclusion(self, sentence: str) -> bool:
        """Check if sentence appears to be a conclusion."""
        conclusion_indicators = [
            '总结', '结论', '总之', '综上所述', '总而言之', '总的来说', '最后', '最终',
            'conclude', 'conclusion', 'summarize', 'in summary', 'in conclusion',
            'overall', 'finally', 'ultimately'
        ]
        return any(indicator in sentence.lower() for indicator in conclusion_indicators)

    def _has_weak_conclusion(self, sentence: str) -> bool:
        """Check if conclusion is weak."""
        weak_indicators = [
            '可能', '似乎', '看起来', '好像', '大概', '也许',
            'may', 'might', 'seems', 'appears', 'probably', 'perhaps'
        ]
        return any(indicator in sentence.lower() for indicator in weak_indicators)

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Basic sentence splitting
        import re
        # Split on sentence-ending punctuation
        sentences = re.split(r'[.!?。！？]+', text)
        # Filter out empty sentences and strip whitespace
        return [s.strip() for s in sentences if s.strip()]

    async def _evaluate_section_order(self, parsed: schemas.ReportParseResult) -> float:
        """Evaluate if sections are in logical order."""
        expected_order = [
            schemas.SectionType.ABSTRACT,
            schemas.SectionType.INTRODUCTION,
            schemas.SectionType.RELATED_WORK,
            schemas.SectionType.METHOD,
            schemas.SectionType.RESULTS,
            schemas.SectionType.DISCUSSION,
            schemas.SectionType.CONCLUSION,
            schemas.SectionType.REFERENCES
        ]

        actual_sections = [section.section_type for section in parsed.sections]

        # Calculate how well the actual order matches expected order
        score = 0.0
        expected_idx = 0

        for actual_section in actual_sections:
            if expected_idx < len(expected_order) and actual_section == expected_order[expected_idx]:
                score += 1.0
                expected_idx += 1
            elif actual_section in expected_order:
                # If section exists but not in expected position, find its expected position
                expected_pos = expected_order.index(actual_section)
                if expected_pos >= expected_idx:
                    # It's in the right general area
                    score += 0.5
                else:
                    # It's out of order
                    score += 0.0
            else:
                # Unknown section type, neutral score
                score += 0.7

        # Normalize score to 0-100 range
        if len(actual_sections) > 0:
            score = (score / len(actual_sections)) * 100
        else:
            score = 70.0  # Default if no sections detected

        return min(100.0, max(0.0, score))

    async def _evaluate_coherence(self, parsed: schemas.ReportParseResult) -> float:
        """Evaluate paragraph and section coherence."""
        total_score = 0.0
        section_count = 0

        for section in parsed.sections:
            section_text = section.text
            if not section_text.strip():
                continue

            # Evaluate internal coherence of the section
            coherence_score = self._calculate_internal_coherence(section_text)
            total_score += coherence_score
            section_count += 1

        if section_count > 0:
            avg_score = (total_score / section_count) * 20  # Scale to 0-100
        else:
            avg_score = 70.0  # Default score

        return min(100.0, max(0.0, avg_score))

    def _calculate_internal_coherence(self, text: str) -> float:
        """Calculate internal coherence of a text block."""
        sentences = self._split_sentences(text)
        if len(sentences) < 2:
            return 1.0  # Perfect coherence for single sentence

        # Basic coherence measure based on topic continuity
        connected_pairs = 0
        total_pairs = len(sentences) - 1

        for i in range(len(sentences) - 1):
            if self._sentences_are_connected(sentences[i], sentences[i+1]):
                connected_pairs += 1

        if total_pairs > 0:
            return connected_pairs / total_pairs
        else:
            return 1.0

    def _sentences_are_connected(self, sent1: str, sent2: str) -> bool:
        """Check if two sentences are topically connected."""
        # Basic check: do they share common words?
        words1 = set(sent1.lower().split())
        words2 = set(sent2.lower().split())

        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        if union == 0:
            return True  # Both empty, considered connected

        jaccard_similarity = intersection / union
        return jaccard_similarity > 0.1  # At least 10% overlap

    async def _evaluate_argumentation(self, parsed: schemas.ReportParseResult) -> float:
        """Evaluate argumentation quality."""
        text = parsed.raw_text or ""
        sentences = self._split_sentences(text)

        # Count argumentative elements
        claim_count = 0
        evidence_count = 0
        reasoning_count = 0

        for sentence in sentences:
            if self._is_claim(sentence):
                claim_count += 1
            if self._is_evidence(sentence):
                evidence_count += 1
            if self._is_reasoning(sentence):
                reasoning_count += 1

        # Calculate argumentation score based on balance of claims, evidence, and reasoning
        if claim_count > 0:
            evidence_support_ratio = evidence_count / claim_count
            reasoning_support_ratio = reasoning_count / claim_count

            # Ideal ratios: 1 evidence per claim, 0.5 reasoning per claim
            evidence_score = min(1.0, evidence_support_ratio / 1.0) * 50
            reasoning_score = min(1.0, reasoning_support_ratio / 0.5) * 30
            presence_score = min(1.0, claim_count / 5) * 20  # At least 5 claims for good argumentation

            total_score = evidence_score + reasoning_score + presence_score
        else:
            total_score = 30.0  # Low score if no claims found

        return min(100.0, max(0.0, total_score))

    def _is_claim(self, sentence: str) -> bool:
        """Check if sentence contains a claim."""
        claim_indicators = [
            '提出', '认为', '指出', '表明', '说明', '证明', '发现', '显示',
            'propose', 'argue', 'claim', 'assert', 'state', 'suggest',
            'find', 'show', 'demonstrate'
        ]
        return any(indicator in sentence.lower() for indicator in claim_indicators)

    def _is_evidence(self, sentence: str) -> bool:
        """Check if sentence contains evidence."""
        evidence_indicators = [
            '数据显示', '实验表明', '研究表明', '调查发现', '统计显示',
            'data shows', 'experiment indicates', 'study reveals',
            'research shows', 'survey finds', 'statistics indicate'
        ]
        # Look for numbers, percentages, or experimental terms
        has_numbers = bool(re.search(r'\d+%', sentence) or re.search(r'\d+\.\d+', sentence))
        has_evidence_terms = any(indicator in sentence.lower() for indicator in evidence_indicators)

        return has_numbers or has_evidence_terms

    def _is_reasoning(self, sentence: str) -> bool:
        """Check if sentence contains reasoning."""
        reasoning_indicators = [
            '因为', '由于', '因此', '所以', '原因是', '这表明', '这意味着',
            'because', 'since', 'therefore', 'so', 'due to', 'this indicates',
            'this means', 'as a result', 'consequently'
        ]
        return any(indicator in sentence.lower() for indicator in reasoning_indicators)

    def _generate_logic_summary(self, section_order: float, coherence: float, argumentation: float) -> str:
        """Generate a natural language summary of logic analysis."""
        avg_score = (section_order + coherence + argumentation) / 3

        if avg_score >= 80:
            return "逻辑结构优秀：章节顺序合理，段落连贯性强，论证充分有力。"
        elif avg_score >= 60:
            return "逻辑结构良好：大部分章节有序，连贯性较好，论证基本充分，但仍有改进空间。"
        else:
            return "逻辑结构需改进：章节顺序、段落连贯性或论证方面存在问题，建议加强逻辑组织。"

    async def _evaluate_innovation(self, parsed: schemas.ReportParseResult) -> float:
        """Evaluate innovation/novelty of the report."""
        text = parsed.raw_text or ""

        # Look for innovation indicators
        innovation_indicators = [
            '创新', '新颖', '首次', '突破', '独创', '原创', '首创', '独特',
            'innovative', 'novel', 'first', 'breakthrough', 'original',
            'unique', 'pioneering', 'novelty'
        ]

        # Look for improvement indicators
        improvement_indicators = [
            '改进', '优化', '提升', '增强', '改善', '改良',
            'improve', 'optimize', 'enhance', 'upgrade', 'better', 'advance'
        ]

        # Count occurrences
        innovation_count = sum(text.lower().count(ind) for ind in innovation_indicators)
        improvement_count = sum(text.lower().count(ind) for ind in improvement_indicators)

        # Calculate innovation score based on indicators and context
        base_score = min(100.0, (innovation_count * 15) + (improvement_count * 10))

        # Boost score if technical terms suggest novel approach
        technical_terms = [
            'algorithm', 'method', 'approach', 'technique', 'framework', 'model',
            '算法', '方法', '方案', '技术', '框架', '模型', '系统', '机制'
        ]

        tech_term_count = sum(text.lower().count(term) for term in technical_terms)
        tech_score = min(30.0, tech_term_count * 2)

        total_score = base_score + tech_score
        return min(100.0, max(0.0, total_score))

    async def _identify_innovation_points(self, parsed: schemas.ReportParseResult) -> List[schemas.InnovationPoint]:
        """Identify specific innovation points in the report."""
        points = []
        text = parsed.raw_text or ""

        # Look for sentences that mention innovations
        sentences = self._split_sentences(text)

        for i, sentence in enumerate(sentences):
            if self._mentions_innovation(sentence):
                points.append(schemas.InnovationPoint(
                    section_id=None,
                    highlight_text=sentence,
                    reason="句子中提到了创新、新颖性或改进相关内容"
                ))

        # If no specific innovation mentions, look for technical contributions
        if not points:
            for i, sentence in enumerate(sentences):
                if self._mentions_technical_contribution(sentence):
                    points.append(schemas.InnovationPoint(
                        section_id=None,
                        highlight_text=sentence,
                        reason="句子中提到了技术贡献或方法改进"
                    ))

        return points

    def _mentions_innovation(self, sentence: str) -> bool:
        """Check if sentence mentions innovation."""
        innovation_terms = [
            '创新', '新颖', '首次', '突破', '独创', '原创', '首创', '独特',
            'innovative', 'novel', 'first', 'breakthrough', 'original',
            'unique', 'pioneering', 'novelty', 'improve', 'optimize',
            'enhance', 'advance', '改进', '优化', '提升', '增强'
        ]
        return any(term in sentence.lower() for term in innovation_terms)

    def _mentions_technical_contribution(self, sentence: str) -> bool:
        """Check if sentence mentions technical contribution."""
        tech_terms = [
            '提出', '设计', '开发', '构建', '创建', '实现', '建立',
            'propose', 'design', 'develop', 'construct', 'create',
            'implement', 'establish', 'algorithm', 'method', 'approach',
            '算法', '方法', '方案', '技术', '框架', '模型', '系统'
        ]
        return any(term in sentence.lower() for term in tech_terms)

    def _generate_difference_summary(self, innovation_score: float) -> str:
        """Generate summary of differences/innovation."""
        if innovation_score >= 80:
            return "报告具有显著的创新性和独特性，在方法、理论或应用方面有重要突破。"
        elif innovation_score >= 60:
            return "报告具有一定的创新性，在某些方面提出了新的见解或改进。"
        elif innovation_score >= 40:
            return "报告创新性一般，主要在现有基础上进行了一些改进或应用。"
        else:
            return "报告创新性有限，主要是对现有工作的复现或简单应用。"

    async def _generate_suggestions(
        self, parsed: schemas.ReportParseResult
    ) -> Tuple[
        schemas.LanguageQualityMetrics,
        schemas.FormattingCheckResult,
        list[schemas.ImprovementSuggestion],
    ]:
        """Generate language/formatting metrics and high-level suggestions."""

        text = parsed.raw_text or ""

        # Calculate language quality metrics
        language_quality = await self._calculate_language_metrics(text, parsed.language)

        # Perform formatting checks
        formatting = await self._perform_formatting_checks(parsed)

        # Generate improvement suggestions
        suggestions = await self._generate_improvement_suggestions(parsed, language_quality, formatting)

        return language_quality, formatting, suggestions

    async def _calculate_language_metrics(self, text: str, language: schemas.ReportLanguage) -> schemas.LanguageQualityMetrics:
        """Calculate detailed language quality metrics."""
        sentences = self._split_sentences(text)

        if not sentences:
            return schemas.LanguageQualityMetrics(
                average_sentence_length=0.0,
                long_sentence_ratio=0.0,
                vocabulary_richness=0.0,
                grammar_issue_count=0,
                academic_tone_score=0.0,
                readability_score=0.0,
            )

        # Average sentence length
        word_counts = [len(s.split()) for s in sentences if s.strip()]
        avg_sentence_length = sum(word_counts) / len(word_counts) if word_counts else 0.0

        # Long sentence ratio (>20 words is considered long)
        long_sentences = [wc for wc in word_counts if wc > 20]
        long_sentence_ratio = len(long_sentences) / len(word_counts) if word_counts else 0.0

        # Vocabulary richness (Type-Token Ratio)
        all_words = text.split()
        unique_words = set(all_words)
        vocabulary_richness = len(unique_words) / len(all_words) if all_words else 0.0

        # Academic tone score
        academic_tone_score = await self._calculate_academic_tone(text, language)

        # Readability score (simplified Flesch Reading Ease adaptation)
        readability_score = await self._calculate_readability_score(avg_sentence_length, text)

        # Grammar issue count (placeholder - would need actual NLP/grammar checker)
        grammar_issue_count = await self._count_potential_grammar_issues(text)

        return schemas.LanguageQualityMetrics(
            average_sentence_length=avg_sentence_length,
            long_sentence_ratio=long_sentence_ratio,
            vocabulary_richness=vocabulary_richness,
            grammar_issue_count=grammar_issue_count,
            academic_tone_score=academic_tone_score,
            readability_score=readability_score,
        )

    async def _calculate_academic_tone(self, text: str, language: schemas.ReportLanguage) -> float:
        """Calculate how academic/formal the writing style is."""
        # Academic tone indicators
        if language == schemas.ReportLanguage.ZH:
            formal_indicators = [
                '本文', '该', '本研究', '实验', '分析', '表明', '显示', '证明',
                '提出', '设计', '构建', '验证', '评估', '比较', '讨论'
            ]
            informal_indicators = [
                '我觉得', '我认为', '就是', '嘛', '呢', '吧', '啊', '呀',
                'I think', 'I believe', 'just', 'well', 'you know'
            ]
        else:  # English or mixed
            formal_indicators = [
                'this paper', 'the study', 'the experiment', 'analysis', 'indicates',
                'demonstrates', 'proposes', 'designs', 'validates', 'evaluates',
                'compares', 'discusses', 'furthermore', 'moreover', 'however'
            ]
            informal_indicators = [
                'I think', 'I believe', 'just', 'well', 'you know', 'sort of',
                'kind of', 'pretty much', 'a lot', 'um', 'uh', 'basically'
            ]

        # Count formal vs informal indicators
        formal_count = sum(text.lower().count(ind) for ind in formal_indicators)
        informal_count = sum(text.lower().count(ind) for ind in informal_indicators)

        # Calculate score (higher = more academic)
        total_indicators = formal_count + informal_count
        if total_indicators == 0:
            return 70.0  # Default score

        academic_score = (formal_count / total_indicators) * 100
        return min(100.0, max(0.0, academic_score))

    async def _calculate_readability_score(self, avg_sentence_length: float, text: str) -> float:
        """Calculate readability score (adapted from Flesch Reading Ease)."""
        # Simplified calculation
        # Higher scores indicate easier readability
        if avg_sentence_length == 0:
            return 70.0  # Default readability

        # Adjust based on average sentence length
        # Shorter sentences are more readable
        readability = max(0, 100 - (avg_sentence_length * 1.5))
        return min(100.0, max(0.0, readability))

    async def _count_potential_grammar_issues(self, text: str) -> int:
        """Count potential grammar issues."""
        # Simple heuristics for potential grammar issues
        issues = 0

        sentences = self._split_sentences(text)
        for sentence in sentences:
            # Check for very long sentences (potential run-on)
            if len(sentence.split()) > 50:
                issues += 1

            # Check for sentences that start with conjunctions (sometimes incorrect)
            conjunctions = ['but', 'and', 'or', 'so', 'yet', 'for', 'but', '但是', '而且', '或者']
            if any(sentence.lower().strip().startswith(conj.lower()) for conj in conjunctions):
                issues += 0.5  # Partial issue

        return int(issues)

    async def _perform_formatting_checks(self, parsed: schemas.ReportParseResult) -> schemas.FormattingCheckResult:
        """Perform formatting and style checks."""
        # Determine reference style from detected references
        reference_style = self._determine_reference_style(parsed.references)

        # Check title consistency
        title_consistency_score = await self._check_title_consistency(parsed.sections)

        # Check figure/table consistency (placeholder - would need actual detection)
        figure_table_consistency_score = await self._check_figure_table_consistency(parsed.raw_text)

        # Identify formatting issues
        formatting_issues = await self._identify_formatting_issues(parsed)

        return schemas.FormattingCheckResult(
            reference_style=reference_style,
            title_consistency_score=title_consistency_score,
            figure_table_consistency_score=figure_table_consistency_score,
            issues=formatting_issues,
        )

    def _determine_reference_style(self, references: List[schemas.ReferenceEntry]) -> schemas.ReferenceFormat:
        """Determine the reference style based on detected references."""
        if not references:
            return schemas.ReferenceFormat.UNKNOWN

        apa_count = sum(1 for ref in references if ref.detected_format == schemas.ReferenceFormat.APA)
        gbt_count = sum(1 for ref in references if ref.detected_format == schemas.ReferenceFormat.GBT7714)
        mla_count = sum(1 for ref in references if ref.detected_format == schemas.ReferenceFormat.MLA)

        # Return the most common format
        if apa_count >= gbt_count and apa_count >= mla_count:
            return schemas.ReferenceFormat.APA
        elif gbt_count >= mla_count:
            return schemas.ReferenceFormat.GBT7714
        else:
            return schemas.ReferenceFormat.MLA

    async def _check_title_consistency(self, sections: List[schemas.ReportSection]) -> float:
        """Check consistency of section titles."""
        if not sections:
            return 60.0  # Default score

        titles = [s.title for s in sections if s.title.strip()]
        if not titles:
            return 60.0

        # Check for consistent capitalization/punctuation
        consistent_count = 0
        total_titles = len(titles)

        # Simple heuristic: check if titles follow similar patterns
        has_colon = [':' in title for title in titles]
        has_period = ['.' in title for title in titles]
        is_capitalized = [title[0].isupper() if title else False for title in titles]

        # Calculate consistency scores
        colon_consistency = 1.0 - abs(sum(has_colon) / total_titles - 0.5) * 2  # Closer to 0.5 is less consistent
        period_consistency = 1.0 - abs(sum(has_period) / total_titles - 0.5) * 2
        cap_consistency = sum(is_capitalized) / total_titles

        # Average consistency
        avg_consistency = (colon_consistency + period_consistency + cap_consistency) / 3
        consistency_score = avg_consistency * 100

        return min(100.0, max(0.0, consistency_score))

    async def _check_figure_table_consistency(self, text: str) -> float:
        """Check consistency of figure and table references."""
        # Look for figure/table references
        fig_refs = len(re.findall(r'Figure\s+\d+|Fig\.\s+\d+|图\s*\d+', text, re.IGNORECASE))
        tab_refs = len(re.findall(r'Table\s+\d+|表\s*\d+', text, re.IGNORECASE))

        # Look for actual figures and tables mentioned
        fig_mentions = len(re.findall(r'fig\w*|图表|图像|图形', text, re.IGNORECASE))
        tab_mentions = len(re.findall(r'tab\w*|表格|表项', text, re.IGNORECASE))

        # Calculate consistency score
        if fig_refs + tab_refs == 0:
            return 50.0  # Neutral score if no references found

        # Check if references match mentions
        total_refs = fig_refs + tab_refs
        total_mentions = fig_mentions + tab_mentions

        if total_refs == 0:
            return 50.0

        # Score based on ratio consistency
        ratio_diff = abs(total_refs - total_mentions) / total_refs
        consistency_score = max(0.0, (1.0 - ratio_diff)) * 100

        return min(100.0, max(0.0, consistency_score))

    async def _identify_formatting_issues(self, parsed: schemas.ReportParseResult) -> List[schemas.FormattingIssue]:
        """Identify specific formatting issues."""
        issues = []
        text = parsed.raw_text or ""

        # Check for inconsistent heading formatting
        lines = text.split('\n')
        heading_patterns = []

        for i, line in enumerate(lines):
            if re.match(r'^\s*[#\d\-.]+\s+', line):  # Likely a heading
                heading_patterns.append((i, line.strip()))

        # Check for reference formatting issues
        if not parsed.references:
            issues.append(schemas.FormattingIssue(
                issue_type=schemas.FormattingIssueType.REFERENCE_FORMAT,
                location="References section",
                description="未检测到参考文献格式，建议按照指定格式（如APA、GB/T 7714等）规范引用",
                suggested_fix="请确保所有引用都符合学术规范格式"
            ))

        # Check for title formatting consistency
        if len(parsed.sections) > 1:
            titles = [s.title for s in parsed.sections if s.title.strip()]
            if titles:
                # Check if titles have consistent formatting
                has_periods = [title.endswith('.') for title in titles if title]
                if len(set(has_periods)) > 1:  # Mixed formatting
                    issues.append(schemas.FormattingIssue(
                        issue_type=schemas.FormattingIssueType.TITLE_INCONSISTENT,
                        location="Section titles",
                        description="章节标题格式不一致（有些以句号结尾，有些没有）",
                        suggested_fix="请统一章节标题的格式，要么都加句号，要么都不加"
                    ))

        return issues

    async def _generate_improvement_suggestions(self, parsed: schemas.ReportParseResult,
                                               language_metrics: schemas.LanguageQualityMetrics,
                                               formatting_result: schemas.FormattingCheckResult) -> List[schemas.ImprovementSuggestion]:
        """Generate specific improvement suggestions based on analysis."""
        suggestions = []
        text = parsed.raw_text or ""

        # Content suggestions
        if len(text) < 1000:
            suggestions.append(schemas.ImprovementSuggestion(
                category="content",
                section_id=None,
                summary="报告整体篇幅偏短",
                details="当前报告字数偏少，建议在方法、实验设计和结果分析部分增加更详细的描述。"
            ))
        elif len(text) > 10000:
            suggestions.append(schemas.ImprovementSuggestion(
                category="content",
                section_id=None,
                summary="报告篇幅过长",
                details="报告内容较长，建议精简冗余部分，突出重点内容。"
            ))

        # Language suggestions based on metrics
        if language_metrics.average_sentence_length > 25:
            suggestions.append(schemas.ImprovementSuggestion(
                category="language",
                section_id=None,
                summary="句子长度偏长",
                details=f"平均句长为{language_metrics.average_sentence_length:.1f}词，建议适当拆分长句以提高可读性。"
            ))

        if language_metrics.long_sentence_ratio > 0.3:
            suggestions.append(schemas.ImprovementSuggestion(
                category="language",
                section_id=None,
                summary="长句比例过高",
                details=f"超过30%的句子长度过长({language_metrics.long_sentence_ratio*100:.1f}%)，建议简化复杂句式。"
            ))

        if language_metrics.academic_tone_score < 60:
            suggestions.append(schemas.ImprovementSuggestion(
                category="language",
                section_id=None,
                summary="学术表达风格有待提升",
                details="建议减少口语化表达，使用更规范的学术语言，并适当引用相关文献支持论述。"
            ))

        # Structure suggestions
        if len(parsed.sections) < 3:
            suggestions.append(schemas.ImprovementSuggestion(
                category="structure",
                section_id=None,
                summary="报告结构较为简单",
                details="建议按学术报告标准结构组织内容，包括引言、方法、结果、讨论、结论等部分。"
            ))

        # Formatting suggestions
        if formatting_result.title_consistency_score < 70:
            suggestions.append(schemas.ImprovementSuggestion(
                category="formatting",
                section_id=None,
                summary="标题格式不够统一",
                details="章节标题格式应保持一致，注意大小写、标点符号的统一使用。"
            ))

        if formatting_result.reference_style == schemas.ReferenceFormat.UNKNOWN and len(parsed.references) == 0:
            suggestions.append(schemas.ImprovementSuggestion(
                category="formatting",
                section_id=None,
                summary="缺少参考文献",
                details="学术报告应包含适当的参考文献，以支撑论述和体现研究基础。"
            ))

        # Add suggestions based on logic issues
        # Since we don't have direct access to logic issues here, we'll add general ones
        if language_metrics.grammar_issue_count > 3:
            suggestions.append(schemas.ImprovementSuggestion(
                category="language",
                section_id=None,
                summary="存在潜在语法问题",
                details=f"检测到{language_metrics.grammar_issue_count}个潜在语法问题，建议仔细校对。"
            ))

        return suggestions


# Singleton instance used by API layer
report_analysis_service = ReportAnalysisService()


__all__ = ["ReportAnalysisService", "report_analysis_service"]
