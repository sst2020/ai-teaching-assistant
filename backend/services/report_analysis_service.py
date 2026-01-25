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

import json
import logging
import re
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional, Tuple

from schemas import report_analysis as schemas

if TYPE_CHECKING:
    from services.ai_service import AIService

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class ReportAnalysisConfig:
    """报告分析服务的配置选项。"""

    # AI 分析开关（默认禁用，需显式启用）
    use_ai_for_logic: bool = False  # 是否使用 AI 进行逻辑分析
    use_ai_for_innovation: bool = False  # 是否使用 AI 进行创新性分析
    use_ai_for_suggestions: bool = False  # 是否使用 AI 生成改进建议
    use_ai_for_language: bool = False  # 是否使用 AI 进行语言质量评估

    # AI 调用配置
    ai_timeout: int = 30  # AI API 调用超时时间（秒）
    fallback_to_rules: bool = True  # AI 失败时是否回退到规则分析

    # 提示词配置
    max_content_length: int = 8000  # 发送给 AI 的最大内容长度


class ReportAnalysisService:
    """Core service for project report analysis."""

    def __init__(
        self,
        ai_service: Optional["AIService"] = None,
        config: Optional[ReportAnalysisConfig] = None,
    ) -> None:
        """初始化报告分析服务。

        Args:
            ai_service: AI 服务实例，用于智能分析。如果为 None，将在需要时延迟加载。
            config: 服务配置选项。如果为 None，使用默认配置。
        """
        self.config = config or ReportAnalysisConfig()
        self._ai_service = ai_service
        self._ai_service_loaded = ai_service is not None

    @property
    def ai_service(self) -> Optional["AIService"]:
        """延迟加载 AI 服务，避免循环导入问题。"""
        if not self._ai_service_loaded:
            try:
                from services.ai_service import ai_service as default_ai_service
                self._ai_service = default_ai_service
                self._ai_service_loaded = True
                logger.info("AI 服务已成功加载")
            except ImportError as e:
                logger.warning(f"无法加载 AI 服务: {e}")
                self._ai_service = None
                self._ai_service_loaded = True
        return self._ai_service

    async def analyze_report(
        self,
        request: schemas.ReportAnalysisRequest,
        config: Optional[ReportAnalysisConfig] = None,
    ) -> schemas.ReportAnalysisResponse:
        """Analyze a project report based on plain text content.

        This is the main entry point when analysis is triggered via API.
        File-based analysis (PDF/DOCX/Markdown) will be supported by
        dedicated endpoints that first parse the file, then call this method.

        Args:
            request: The analysis request containing report content
            config: Optional configuration for AI-powered analysis features.
                    If None, defaults to ReportAnalysisConfig() with all AI
                    features disabled.
        """
        # Use default config if not provided
        if config is None:
            config = ReportAnalysisConfig()

        # Step 1: basic parse result from plain text
        parsed = await self._parse_from_text(request)

        # Get report content for AI analysis
        report_content = request.content

        # Step 2: quality metrics (completeness etc.) - rule-based only
        quality = self._evaluate_quality(parsed)

        # Step 3: logic and innovation analysis (with optional AI enhancement)
        logic, innovation = await self._analyze_logic_and_innovation(parsed)

        # Try AI-enhanced logic analysis if enabled
        if config.use_ai_for_logic:
            ai_logic = await self._analyze_logic_with_ai(parsed)
            if ai_logic is not None:
                logic = ai_logic

        # Try AI-enhanced innovation analysis if enabled
        if config.use_ai_for_innovation:
            ai_innovation = await self._analyze_innovation_with_ai(parsed)
            if ai_innovation is not None:
                innovation = ai_innovation

        # Step 4: language quality, formatting checks and suggestions
        language_quality, formatting, suggestions = await self._generate_suggestions(parsed)

        # Try AI-enhanced language quality analysis if enabled
        if config.use_ai_for_language:
            ai_language = await self._evaluate_language_with_ai(report_content)
            if ai_language is not None:
                language_quality = ai_language

        # Try AI-enhanced suggestions generation if enabled
        if config.use_ai_for_suggestions:
            ai_suggestions = await self._generate_suggestions_with_ai(parsed)
            if ai_suggestions is not None:
                suggestions = ai_suggestions

        # Step 5: aggregate overall score and summary
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

        # Generate summary based on whether AI was used
        ai_features_used = []
        if config.use_ai_for_logic:
            ai_features_used.append("逻辑分析")
        if config.use_ai_for_innovation:
            ai_features_used.append("创新性分析")
        if config.use_ai_for_language:
            ai_features_used.append("语言质量评估")
        if config.use_ai_for_suggestions:
            ai_features_used.append("改进建议生成")

        if ai_features_used:
            summary = f"项目报告分析结果：已完成结构解析、质量评估、逻辑与创新性分析，以及语言和格式检查。AI 增强功能已启用：{', '.join(ai_features_used)}。"
        else:
            summary = "项目报告分析结果：已完成结构解析、质量评估、逻辑与创新性分析，以及语言和格式检查。"

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

    async def _analyze_logic_with_ai(
        self, parsed: schemas.ReportParseResult
    ) -> Optional[schemas.LogicAnalysisResult]:
        """使用 DeepSeek AI 分析报告的逻辑结构。

        Args:
            parsed: 解析后的报告内容

        Returns:
            LogicAnalysisResult 或 None（如果 AI 分析失败）
        """
        if not self.ai_service or not self.config.use_ai_for_logic:
            return None

        try:
            # 提取报告文本用于分析
            report_text = parsed.raw_text or ""
            if len(report_text) > 8000:
                # 截取前后部分以保持上下文
                report_text = report_text[:4000] + "\n\n...[中间内容省略]...\n\n" + report_text[-4000:]

            # 构建分析提示词
            prompt = f"""你是一位专业的学术报告评审专家。请分析以下项目报告的逻辑结构和论证质量。

## 报告内容：
{report_text}

## 分析要求：
请从以下维度评估报告的逻辑质量，并以 JSON 格式返回结果：

1. **章节顺序评分 (section_order_score)**：评估章节的组织是否合理、逻辑是否清晰（0-100分）
2. **连贯性评分 (coherence_score)**：评估段落之间的衔接是否流畅、过渡是否自然（0-100分）
3. **论证完整性评分 (argumentation_score)**：评估论点是否有充分的证据支撑、论证是否完整（0-100分）
4. **逻辑问题列表 (issues)**：识别报告中存在的逻辑问题，每个问题包含：
   - issue_type: 问题类型，可选值为 "missing_evidence"（缺乏证据）、"logical_gap"（逻辑跳跃）、"weak_conclusion"（结论薄弱）、"redundant_content"（冗余内容）
   - description: 问题描述
   - suggested_fix: 修改建议
5. **总结 (summary)**：用一段话总结报告的逻辑质量

## 输出格式（严格按照 JSON 格式）：
```json
{{
    "section_order_score": 85,
    "coherence_score": 78,
    "argumentation_score": 82,
    "issues": [
        {{
            "issue_type": "missing_evidence",
            "description": "第二章中关于系统架构优势的论述缺乏具体数据支撑",
            "suggested_fix": "建议添加性能测试数据或对比实验结果"
        }}
    ],
    "summary": "报告整体逻辑结构清晰，但部分论证需要加强证据支撑..."
}}
```

请直接输出 JSON，不要包含其他解释文字。"""

            # 调用 AI 服务
            response = await self.ai_service.generate_response(
                prompt=prompt,
                system_prompt="你是一位严谨的学术报告评审专家，擅长分析学术文章的逻辑结构和论证质量。请以 JSON 格式输出分析结果。",
                max_tokens=2000,
                temperature=0.3  # 低温度以获得更稳定的输出
            )

            if not response:
                logger.warning("AI 逻辑分析返回空响应")
                return None

            # 解析 JSON 响应
            result = self._parse_logic_analysis_json(response)
            if result:
                logger.info("AI 逻辑分析成功完成")
            return result

        except Exception as e:
            logger.error(f"AI 逻辑分析失败: {e}")
            return None

    def _parse_logic_analysis_json(self, response: str) -> Optional[schemas.LogicAnalysisResult]:
        """解析 AI 返回的逻辑分析 JSON 响应。

        Args:
            response: AI 返回的原始响应文本

        Returns:
            LogicAnalysisResult 或 None（如果解析失败）
        """
        try:
            # 尝试提取 JSON 内容
            json_str = response.strip()

            # 处理可能包含 markdown 代码块的情况
            if "```json" in json_str:
                start = json_str.find("```json") + 7
                end = json_str.find("```", start)
                if end > start:
                    json_str = json_str[start:end].strip()
            elif "```" in json_str:
                start = json_str.find("```") + 3
                end = json_str.find("```", start)
                if end > start:
                    json_str = json_str[start:end].strip()

            # 解析 JSON
            data = json.loads(json_str)

            # 构建 LogicIssue 列表
            issues = []
            for issue_data in data.get("issues", []):
                issue_type_str = issue_data.get("issue_type", "logical_gap")
                try:
                    issue_type = schemas.LogicIssueType(issue_type_str)
                except ValueError:
                    issue_type = schemas.LogicIssueType.LOGICAL_GAP

                issues.append(schemas.LogicIssue(
                    issue_type=issue_type,
                    section_id=issue_data.get("section_id"),
                    paragraph_index=issue_data.get("paragraph_index"),
                    description=issue_data.get("description", "未知问题"),
                    suggested_fix=issue_data.get("suggested_fix")
                ))

            # 构建结果
            return schemas.LogicAnalysisResult(
                section_order_score=float(data.get("section_order_score", 70.0)),
                coherence_score=float(data.get("coherence_score", 70.0)),
                argumentation_score=float(data.get("argumentation_score", 70.0)),
                issues=issues,
                summary=data.get("summary", "逻辑分析完成")
            )

        except json.JSONDecodeError as e:
            logger.warning(f"JSON 解析失败: {e}")
            return None
        except Exception as e:
            logger.error(f"逻辑分析结果解析失败: {e}")
            return None

    async def _analyze_innovation_with_ai(
        self, parsed: schemas.ReportParseResult
    ) -> Optional[schemas.InnovationAnalysisResult]:
        """使用 DeepSeek AI 分析报告的创新点。

        Args:
            parsed: 解析后的报告结构

        Returns:
            创新性分析结果，如果 AI 分析失败则返回 None（将回退到规则分析）
        """
        if not self.ai_service:
            logger.warning("AI 服务不可用，跳过 AI 创新性分析")
            return None

        # 准备报告内容摘要
        report_content = parsed.raw_text or ""
        if len(report_content) > 8000:
            report_content = report_content[:4000] + "\n...[内容过长已截断]...\n" + report_content[-4000:]

        # 收集各章节标题和摘要
        sections_info = []
        for section in parsed.sections:
            section_text = section.text[:500] if section.text else ""
            sections_info.append(f"- {section.title}: {section_text[:200]}...")
        sections_summary = "\n".join(sections_info[:10])  # 最多10个章节

        prompt = f"""请分析以下学术/项目报告的创新性和独特之处。

## 报告章节结构：
{sections_summary}

## 报告全文摘要：
{report_content}

## 分析要求：
1. 评估报告的整体创新程度（0-100分）
2. 总结报告与同类报告的差异点
3. 识别报告中具体的创新点（技术创新、方法创新、思路创新等）

## 评分标准：
- 90-100分：具有突破性创新，提出了全新的概念或方法
- 70-89分：有明显创新，在现有基础上有显著改进
- 50-69分：有一定创新，但主要是常规改进
- 30-49分：创新性较弱，主要是已有方法的应用
- 0-29分：缺乏创新，完全是常规内容

请以 JSON 格式输出分析结果：
```json
{{
    "novelty_score": <0-100的创新性评分>,
    "difference_summary": "<与同类报告的差异总结，200字以内>",
    "innovation_points": [
        {{
            "section_id": "<所在章节ID，如无法确定则为null>",
            "highlight_text": "<创新点的原文引用或描述，50字以内>",
            "reason": "<为什么这是创新点，100字以内>"
        }}
    ]
}}
```

请确保输出的 JSON 格式正确，innovation_points 数组包含 0-5 个最重要的创新点。"""

        system_prompt = """你是一位资深的学术评审专家，擅长评估学术报告和项目文档的创新性。
你需要客观、专业地分析报告的创新程度，识别真正有价值的创新点。
评分时要严格但公正，既不过于苛刻也不过于宽松。
请务必以有效的 JSON 格式输出分析结果。"""

        try:
            response = await self.ai_service.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=2000,
                temperature=0.3
            )

            if not response:
                logger.warning("AI 创新性分析返回空响应")
                return None

            return self._parse_innovation_analysis_json(response)

        except Exception as e:
            logger.error(f"AI 创新性分析失败: {e}")
            return None

    def _parse_innovation_analysis_json(
        self, response: str
    ) -> Optional[schemas.InnovationAnalysisResult]:
        """解析 AI 返回的创新性分析 JSON 结果。

        Args:
            response: AI 返回的原始响应文本

        Returns:
            解析后的创新性分析结果，解析失败返回 None
        """
        try:
            # 尝试从 markdown 代码块中提取 JSON
            json_text = response
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                if end > start:
                    json_text = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                if end > start:
                    json_text = response[start:end].strip()

            data = json.loads(json_text)

            # 解析创新点列表
            innovation_points = []
            for point_data in data.get("innovation_points", []):
                if not isinstance(point_data, dict):
                    continue
                # highlight_text 和 reason 是必填字段
                highlight_text = point_data.get("highlight_text", "")
                reason = point_data.get("reason", "")
                if not highlight_text or not reason:
                    continue

                innovation_points.append(schemas.InnovationPoint(
                    section_id=point_data.get("section_id"),
                    highlight_text=highlight_text,
                    reason=reason
                ))

            # 构建结果
            return schemas.InnovationAnalysisResult(
                novelty_score=float(data.get("novelty_score", 50.0)),
                difference_summary=data.get("difference_summary", ""),
                innovation_points=innovation_points
            )

        except json.JSONDecodeError as e:
            logger.warning(f"创新性分析 JSON 解析失败: {e}")
            return None
        except Exception as e:
            logger.error(f"创新性分析结果解析失败: {e}")
            return None

    async def _generate_suggestions_with_ai(
        self, parsed: schemas.ReportParseResult
    ) -> Optional[List[schemas.ImprovementSuggestion]]:
        """使用 DeepSeek AI 生成个性化改进建议。

        Args:
            parsed: 解析后的报告结构

        Returns:
            改进建议列表，如果 AI 分析失败则返回 None（将回退到规则分析）
        """
        if not self.ai_service:
            logger.warning("AI 服务不可用，跳过 AI 改进建议生成")
            return None

        # 准备报告内容摘要
        report_content = parsed.raw_text or ""
        if len(report_content) > 8000:
            report_content = report_content[:4000] + "\n...[内容过长已截断]...\n" + report_content[-4000:]

        # 收集各章节信息
        sections_info = []
        for section in parsed.sections:
            section_text = section.text[:300] if section.text else ""
            sections_info.append(f"- [{section.id}] {section.title}: {section_text}...")
        sections_summary = "\n".join(sections_info[:15])  # 最多15个章节

        prompt = f"""请分析以下学术/项目报告，并提供具体的改进建议。

## 报告章节结构：
{sections_summary}

## 报告全文摘要：
{report_content}

## 分析要求：
请从以下四个维度提供改进建议：
1. **content（内容）**：内容完整性、深度、准确性方面的改进
2. **logic（逻辑）**：论证结构、逻辑连贯性、推理过程的改进
3. **language（语言）**：学术写作规范、表达清晰度、专业术语使用的改进
4. **formatting（格式）**：排版、图表、引用格式等方面的改进

## 建议要求：
- 每个建议要具体、可操作
- 尽量关联到具体的章节（提供 section_id）
- 提供简洁的建议摘要和详细的改进说明
- 总共提供 4-8 条最重要的建议

请以 JSON 格式输出：
```json
{{
    "suggestions": [
        {{
            "category": "<content|logic|language|formatting>",
            "section_id": "<相关章节ID，如 'section_1'，如无特定章节则为 null>",
            "summary": "<建议摘要，20字以内>",
            "details": "<详细说明，包含具体的改进方法和示例，100-200字>"
        }}
    ]
}}
```

请确保每个维度至少提供1条建议，优先关注最需要改进的方面。"""

        system_prompt = """你是一位经验丰富的学术写作导师，擅长提供建设性的改进建议。
你的建议应该：
1. 具体且可操作，避免空泛的评价
2. 平衡指出问题与提供解决方案
3. 考虑不同水平作者的接受能力
4. 以鼓励为主，同时不回避关键问题
请务必以有效的 JSON 格式输出建议。"""

        try:
            response = await self.ai_service.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=2500,
                temperature=0.4
            )

            if not response:
                logger.warning("AI 改进建议生成返回空响应")
                return None

            return self._parse_suggestions_json(response)

        except Exception as e:
            logger.error(f"AI 改进建议生成失败: {e}")
            return None

    def _parse_suggestions_json(
        self, response: str
    ) -> Optional[List[schemas.ImprovementSuggestion]]:
        """解析 AI 返回的改进建议 JSON 结果。

        Args:
            response: AI 返回的原始响应文本

        Returns:
            解析后的改进建议列表，解析失败返回 None
        """
        try:
            # 尝试从 markdown 代码块中提取 JSON
            json_text = response
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                if end > start:
                    json_text = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                if end > start:
                    json_text = response[start:end].strip()

            data = json.loads(json_text)

            # 解析建议列表
            suggestions = []
            valid_categories = {"content", "logic", "language", "formatting"}

            for sugg_data in data.get("suggestions", []):
                if not isinstance(sugg_data, dict):
                    continue

                # 验证必填字段
                category = sugg_data.get("category", "").lower()
                summary = sugg_data.get("summary", "")
                details = sugg_data.get("details", "")

                if not summary or not details:
                    continue

                # 验证 category 值
                if category not in valid_categories:
                    category = "content"  # 默认归类为内容类建议

                suggestions.append(schemas.ImprovementSuggestion(
                    category=category,
                    section_id=sugg_data.get("section_id"),
                    summary=summary,
                    details=details
                ))

            return suggestions if suggestions else None

        except json.JSONDecodeError as e:
            logger.warning(f"改进建议 JSON 解析失败: {e}")
            return None
        except Exception as e:
            logger.error(f"改进建议结果解析失败: {e}")
            return None


    async def _evaluate_language_with_ai(
        self, report_content: str
    ) -> Optional[schemas.LanguageQualityMetrics]:
        """
        使用 DeepSeek AI 评估报告语言质量。

        Args:
            report_content: 报告文本内容

        Returns:
            LanguageQualityMetrics 或 None（如果 AI 分析失败）
        """
        if not self._ai_service:
            logger.warning("AI 服务不可用，无法进行语言质量评估")
            return None

        # 限制报告内容长度，避免超出上下文限制
        max_content_length = 8000
        if len(report_content) > max_content_length:
            # 取首尾各 4000 字符，保留开头和结尾的信息
            report_content = (
                report_content[:4000]
                + "\n\n... [内容已截断] ...\n\n"
                + report_content[-4000:]
            )

        system_prompt = """你是一位专业的学术写作评估专家，精通语言质量分析和可读性评估。
你的任务是评估学术报告的语言质量，包括句子结构、词汇使用、语法规范性、学术风格和可读性。

请严格按照 JSON 格式输出评估结果，不要包含任何其他文字说明。"""

        user_prompt = f"""请分析以下学术报告的语言质量，并提供详细的评估指标。

## 报告内容
{report_content}

## 评估要求
请从以下维度评估语言质量：

1. **句子平均长度** (average_sentence_length)
   - 统计报告中句子的平均字数
   - 一般学术报告句子长度在 15-30 字为宜

2. **长句比例** (long_sentence_ratio)
   - 计算超过 40 字的长句占总句子数的比例
   - 值范围：0.0-1.0
   - 过多长句会影响可读性

3. **词汇丰富度** (vocabulary_richness)
   - 评估词汇的多样性和专业性
   - 值范围：0.0-1.0
   - 1.0 表示词汇非常丰富多样

4. **语法问题数量** (grammar_issue_count)
   - 统计明显的语法错误、标点错误、用词不当等问题
   - 整数，0 表示没有发现问题

5. **学术语调分数** (academic_tone_score)
   - 评估写作风格的学术性和正式性
   - 值范围：0-100
   - 考虑：客观性、专业术语使用、被动语态使用、引用规范等

6. **可读性分数** (readability_score)
   - 综合评估报告的可读性
   - 值范围：0-100
   - 考虑：段落结构、逻辑清晰度、过渡词使用、信息密度等

## 输出格式
请严格按以下 JSON 格式输出，不要包含任何额外说明：

```json
{{
    "average_sentence_length": <浮点数>,
    "long_sentence_ratio": <0.0-1.0 的浮点数>,
    "vocabulary_richness": <0.0-1.0 的浮点数>,
    "grammar_issue_count": <非负整数>,
    "academic_tone_score": <0-100 的浮点数>,
    "readability_score": <0-100 的浮点数>
}}
```"""

        try:
            response = await self._ai_service.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=500,
                temperature=0.3  # 低温度以获得更稳定的评分
            )

            if not response:
                logger.warning("AI 语言质量评估返回空响应")
                return None

            return self._parse_language_analysis_json(response)

        except Exception as e:
            logger.error(f"AI 语言质量评估失败: {e}")
            return None

    def _parse_language_analysis_json(
        self, response: str
    ) -> Optional[schemas.LanguageQualityMetrics]:
        """解析 AI 语言质量评估的 JSON 响应。"""
        try:
            # 尝试提取 JSON 内容（处理 markdown 代码块情况）
            json_content = response.strip()
            if "```json" in json_content:
                start = json_content.find("```json") + 7
                end = json_content.find("```", start)
                if end > start:
                    json_content = json_content[start:end].strip()
            elif "```" in json_content:
                start = json_content.find("```") + 3
                end = json_content.find("```", start)
                if end > start:
                    json_content = json_content[start:end].strip()

            data = json.loads(json_content)

            # 提取并验证各字段值
            avg_sentence_length = float(data.get("average_sentence_length", 0.0))
            if avg_sentence_length < 0:
                avg_sentence_length = 0.0

            long_sentence_ratio = float(data.get("long_sentence_ratio", 0.0))
            long_sentence_ratio = max(0.0, min(1.0, long_sentence_ratio))

            vocabulary_richness = float(data.get("vocabulary_richness", 0.0))
            vocabulary_richness = max(0.0, min(1.0, vocabulary_richness))

            grammar_issue_count = int(data.get("grammar_issue_count", 0))
            if grammar_issue_count < 0:
                grammar_issue_count = 0

            academic_tone_score = float(data.get("academic_tone_score", 0.0))
            academic_tone_score = max(0.0, min(100.0, academic_tone_score))

            readability_score = float(data.get("readability_score", 0.0))
            readability_score = max(0.0, min(100.0, readability_score))

            return schemas.LanguageQualityMetrics(
                average_sentence_length=avg_sentence_length,
                long_sentence_ratio=long_sentence_ratio,
                vocabulary_richness=vocabulary_richness,
                grammar_issue_count=grammar_issue_count,
                academic_tone_score=academic_tone_score,
                readability_score=readability_score
            )

        except json.JSONDecodeError as e:
            logger.warning(f"语言质量评估 JSON 解析失败: {e}")
            return None
        except Exception as e:
            logger.error(f"语言质量评估结果解析失败: {e}")
            return None


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


__all__ = ["ReportAnalysisService", "ReportAnalysisConfig", "report_analysis_service"]
