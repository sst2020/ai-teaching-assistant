"""
Enhanced Code Analysis Service - Comprehensive code quality analysis.
"""
import ast
import re
import json
import uuid
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Set, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field

from schemas.analysis_rules import (
    RuleSeverity, RuleCategory, SupportedLanguage,
    AnalysisRule, RuleConfiguration, RuleViolation,
    ComplexityResult, LineMetrics, StructureResult, NamingConventionResult,
    CategoryScore, AnalysisResultSummary, FullAnalysisResult
)

logger = logging.getLogger(__name__)


@dataclass
class AnalysisConfig:
    """Configuration for code analysis."""
    max_line_length: int = 100
    max_complexity: int = 10
    max_cognitive_complexity: int = 15
    max_function_length: int = 50
    max_nesting_depth: int = 4
    max_parameters: int = 5
    min_name_length: int = 2
    max_name_length: int = 30
    min_comment_ratio: float = 10.0
    duplicate_min_lines: int = 3


@dataclass
class LoadedRule:
    """A rule loaded with its configuration."""
    rule: AnalysisRule
    enabled: bool = True
    severity: RuleSeverity = RuleSeverity.WARNING
    thresholds: Dict[str, Any] = field(default_factory=dict)


NAMING_PATTERNS = {
    "snake_case": re.compile(r'^[a-z][a-z0-9]*(_[a-z0-9]+)*$'),
    "camelCase": re.compile(r'^[a-z][a-zA-Z0-9]*$'),
    "PascalCase": re.compile(r'^[A-Z][a-zA-Z0-9]*$'),
    "UPPER_CASE": re.compile(r'^[A-Z][A-Z0-9]*(_[A-Z0-9]+)*$'),
}

LANGUAGE_CONVENTIONS = {
    "python": {"variable": "snake_case", "function": "snake_case", "class": "PascalCase", "constant": "UPPER_CASE"},
    "javascript": {"variable": "camelCase", "function": "camelCase", "class": "PascalCase", "constant": "UPPER_CASE"},
    "typescript": {"variable": "camelCase", "function": "camelCase", "class": "PascalCase", "constant": "UPPER_CASE"},
    "java": {"variable": "camelCase", "function": "camelCase", "class": "PascalCase", "constant": "UPPER_CASE"},
    "c": {"variable": "snake_case", "function": "snake_case", "class": "PascalCase", "constant": "UPPER_CASE"},
    "cpp": {"variable": "camelCase", "function": "camelCase", "class": "PascalCase", "constant": "UPPER_CASE"},
}

SECURITY_PATTERNS = {
    "hardcoded_password": [
        re.compile(r'password\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
        re.compile(r'secret\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
        re.compile(r'api_key\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
        re.compile(r'token\s*=\s*["\'][a-zA-Z0-9]{20,}["\']', re.IGNORECASE),
    ],
    "sql_injection": [
        re.compile(r'execute\s*\(\s*f["\']', re.IGNORECASE),
        re.compile(r'cursor\.execute\s*\(\s*["\'].*\+', re.IGNORECASE),
    ],
    "eval_usage": [re.compile(r'\beval\s*\('), re.compile(r'\bexec\s*\(')],
    "xss_risk": [re.compile(r'innerHTML\s*='), re.compile(r'dangerouslySetInnerHTML')],
}

LOOP_COUNTERS = {'i', 'j', 'k', 'n', 'm', 'x', 'y', 'z'}


class EnhancedAnalysisService:
    """Enhanced service for comprehensive code analysis."""

    def __init__(self, config: Optional[AnalysisConfig] = None):
        self.config = config or AnalysisConfig()
        self.rules: Dict[str, LoadedRule] = {}
        self._load_default_rules()

    def _load_default_rules(self) -> None:
        """Load default rules from configuration file."""
        try:
            rules_path = Path(__file__).parent.parent / "config" / "default_rules.json"
            if rules_path.exists():
                with open(rules_path, 'r') as f:
                    data = json.load(f)
                    for rule_data in data.get("rules", []):
                        rule = AnalysisRule(
                            rule_id=rule_data["rule_id"],
                            name=rule_data["name"],
                            description=rule_data["description"],
                            category=RuleCategory(rule_data["category"]),
                            severity=RuleSeverity(rule_data["severity"]),
                            enabled=rule_data.get("enabled", True),
                            languages=[SupportedLanguage(l) for l in rule_data.get("languages", ["all"])],
                            thresholds=rule_data.get("thresholds", {}),
                            weight=rule_data.get("weight", 1.0)
                        )
                        self.rules[rule.rule_id] = LoadedRule(
                            rule=rule, enabled=rule.enabled,
                            severity=rule.severity, thresholds=rule.thresholds
                        )
                logger.info(f"Loaded {len(self.rules)} analysis rules")
        except Exception as e:
            logger.warning(f"Failed to load default rules: {e}")

    def apply_rule_overrides(self, overrides: List[RuleConfiguration]) -> None:
        """Apply user-specified rule overrides."""
        for override in overrides:
            if override.rule_id in self.rules:
                loaded = self.rules[override.rule_id]
                if override.enabled is not None:
                    loaded.enabled = override.enabled
                if override.severity is not None:
                    loaded.severity = override.severity
                if override.thresholds:
                    loaded.thresholds.update(override.thresholds)

    def is_rule_applicable(self, rule_id: str, language: str) -> bool:
        """Check if a rule applies to the given language."""

    async def analyze(
        self, code: str, language: str = "python",
        file_id: Optional[str] = None,
        rule_overrides: Optional[List[RuleConfiguration]] = None
    ) -> FullAnalysisResult:
        """Perform comprehensive code analysis."""
        analysis_id = str(uuid.uuid4())
        if rule_overrides:
            self.apply_rule_overrides(rule_overrides)

        violations: List[RuleViolation] = []
        line_metrics = self._calculate_line_metrics(code, language)
        complexity = self._analyze_complexity(code, language, violations)
        structure = self._analyze_structure(code, language, violations)
        naming = self._check_naming_conventions(code, language, violations)
        self._check_security(code, language, violations)
        self._check_style(code, language, violations)
        summary = self._calculate_scores(violations, line_metrics, complexity)
        recommendations = self._generate_recommendations(violations, complexity, structure)

        return FullAnalysisResult(
            analysis_id=analysis_id, file_id=file_id, language=language,
            analyzed_at=datetime.now(timezone.utc), summary=summary,
            line_metrics=line_metrics, complexity=complexity,
            structure=structure, naming=naming,
            violations=violations, recommendations=recommendations
        )

    def _calculate_line_metrics(self, code: str, language: str) -> LineMetrics:
        """Calculate line-based metrics."""
        lines = code.split('\n')
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = 0
        docstring_lines = 0
        code_lines = 0
        in_multiline_comment = False
        in_docstring = False

        for line in lines:
            stripped = line.strip()
            if language == "python":
                if '"""' in stripped or "'''" in stripped:
                    quote = '"""' if '"""' in stripped else "'''"
                    count = stripped.count(quote)
                    if count >= 2:
                        docstring_lines += 1
                        continue
                    in_docstring = not in_docstring
                    docstring_lines += 1
                    continue
                if in_docstring:
                    docstring_lines += 1
                    continue

            if language in ["java", "javascript", "typescript", "c", "cpp", "jsx", "tsx"]:
                if "/*" in stripped and "*/" in stripped:
                    comment_lines += 1
                    continue
                elif "/*" in stripped:
                    in_multiline_comment = True
                    comment_lines += 1
                    continue
                elif "*/" in stripped:
                    in_multiline_comment = False
                    comment_lines += 1
                    continue
                if in_multiline_comment:
                    comment_lines += 1
                    continue

            if stripped.startswith('#') or stripped.startswith('//'):
                comment_lines += 1
            elif stripped:
                code_lines += 1

        comment_ratio = (comment_lines / code_lines * 100) if code_lines > 0 else 0
        return LineMetrics(
            total_lines=total_lines, code_lines=code_lines,
            comment_lines=comment_lines, blank_lines=blank_lines,
            docstring_lines=docstring_lines, comment_ratio=round(comment_ratio, 2)
        )


    def _analyze_complexity(self, code: str, language: str, violations: List[RuleViolation]) -> ComplexityResult:
        """Analyze code complexity metrics."""
        result = ComplexityResult()

        if language == "python":
            try:
                tree = ast.parse(code)
                functions = self._extract_python_functions(tree, code)

                if functions:
                    complexities = []
                    cognitive_complexities = []
                    lengths = []
                    params = []
                    nesting_depths = []

                    for func in functions:
                        cc = self._calculate_cyclomatic_complexity(func['node'])
                        cog = self._calculate_cognitive_complexity(func['node'])
                        length = func['end_line'] - func['start_line'] + 1
                        param_count = len(func['node'].args.args)
                        depth = self._calculate_nesting_depth(func['node'])

                        complexities.append(cc)
                        cognitive_complexities.append(cog)
                        lengths.append(length)
                        params.append(param_count)
                        nesting_depths.append(depth)

                        # Check violations
                        if cc > self.config.max_complexity and self.is_rule_applicable("COMPLEXITY_001", language):
                            violations.append(RuleViolation(
                                rule_id="COMPLEXITY_001", rule_name="High Cyclomatic Complexity",
                                category=RuleCategory.COMPLEXITY, severity=RuleSeverity.WARNING,
                                line=func['start_line'], message=f"Function '{func['name']}' has complexity {cc} (max: {self.config.max_complexity})"
                            ))

                        if length > self.config.max_function_length and self.is_rule_applicable("COMPLEXITY_003", language):
                            violations.append(RuleViolation(
                                rule_id="COMPLEXITY_003", rule_name="Long Function",
                                category=RuleCategory.COMPLEXITY, severity=RuleSeverity.WARNING,
                                line=func['start_line'], message=f"Function '{func['name']}' has {length} lines (max: {self.config.max_function_length})"
                            ))

                        if param_count > self.config.max_parameters and self.is_rule_applicable("COMPLEXITY_004", language):
                            violations.append(RuleViolation(
                                rule_id="COMPLEXITY_004", rule_name="Too Many Parameters",
                                category=RuleCategory.COMPLEXITY, severity=RuleSeverity.WARNING,
                                line=func['start_line'], message=f"Function '{func['name']}' has {param_count} parameters (max: {self.config.max_parameters})"
                            ))

                        if depth > self.config.max_nesting_depth and self.is_rule_applicable("COMPLEXITY_002", language):
                            violations.append(RuleViolation(
                                rule_id="COMPLEXITY_002", rule_name="Deep Nesting",
                                category=RuleCategory.COMPLEXITY, severity=RuleSeverity.WARNING,
                                line=func['start_line'], message=f"Function '{func['name']}' has nesting depth {depth} (max: {self.config.max_nesting_depth})"
                            ))

                    result.total_functions = len(functions)
                    result.cyclomatic_complexity = round(sum(complexities) / len(complexities), 2)
                    result.max_cyclomatic_complexity = max(complexities)
                    result.cognitive_complexity = round(sum(cognitive_complexities) / len(cognitive_complexities), 2)
                    result.avg_function_length = round(sum(lengths) / len(lengths), 2)
                    result.max_function_length = max(lengths)
                    result.avg_parameters = round(sum(params) / len(params), 2)
                    result.max_parameters = max(params)
                    result.max_nesting_depth = max(nesting_depths)
                    result.avg_nesting_depth = round(sum(nesting_depths) / len(nesting_depths), 2)
                    result.complex_functions = sum(1 for c in complexities if c > self.config.max_complexity)
            except SyntaxError:
                pass
        else:
            # For other languages, use regex-based analysis
            result = self._analyze_complexity_regex(code, language, violations)

        return result

    def _extract_python_functions(self, tree: ast.AST, code: str) -> List[Dict[str, Any]]:
        """Extract function information from Python AST."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append({
                    'name': node.name,
                    'node': node,
                    'start_line': node.lineno,
                    'end_line': getattr(node, 'end_lineno', node.lineno + 10)
                })
        return functions

    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.Assert, ast.comprehension)):
                complexity += 1
        return complexity

    def _calculate_cognitive_complexity(self, node: ast.AST, depth: int = 0) -> int:
        """Calculate cognitive complexity for a function."""
        complexity = 0
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1 + depth
                complexity += self._calculate_cognitive_complexity(child, depth + 1)
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.Try, ast.ExceptHandler)):
                complexity += 1 + depth
                complexity += self._calculate_cognitive_complexity(child, depth + 1)
            else:
                complexity += self._calculate_cognitive_complexity(child, depth)
        return complexity

    def _calculate_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth."""
        max_depth = current_depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                child_depth = self._calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._calculate_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
        return max_depth


    def _analyze_complexity_regex(self, code: str, language: str, violations: List[RuleViolation]) -> ComplexityResult:
        """Analyze complexity for non-Python languages using regex."""
        result = ComplexityResult()

        # Count functions using regex patterns
        func_patterns = {
            "javascript": r'(?:function\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))',
            "typescript": r'(?:function\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))',
            "java": r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+\w+\s*\([^)]*\)\s*\{',
            "c": r'\w+\s+\w+\s*\([^)]*\)\s*\{',
            "cpp": r'\w+\s+\w+\s*\([^)]*\)\s*\{',
        }

        pattern = func_patterns.get(language, func_patterns.get("javascript"))
        if pattern:
            matches = re.findall(pattern, code)
            result.total_functions = len(matches)

        # Count control flow statements for complexity estimation
        control_flow = len(re.findall(r'\b(if|else|for|while|switch|case|catch)\b', code))
        if result.total_functions > 0:
            result.cyclomatic_complexity = round(control_flow / result.total_functions, 2)

        return result

    def _analyze_structure(self, code: str, language: str, violations: List[RuleViolation]) -> StructureResult:
        """Analyze code structure."""
        result = StructureResult()

        if language == "python":
            try:
                tree = ast.parse(code)
                classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]

                result.total_classes = len(classes)
                result.total_functions = len(functions)

                # Count methods (functions inside classes)
                methods = 0
                for cls in classes:
                    methods += sum(1 for n in ast.walk(cls) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
                result.total_methods = methods

                # Detect unused imports
                result.unused_imports = self._detect_unused_imports(tree, code)
                for imp in result.unused_imports:
                    if self.is_rule_applicable("STRUCTURE_002", language):
                        violations.append(RuleViolation(
                            rule_id="STRUCTURE_002", rule_name="Unused Import",
                            category=RuleCategory.STRUCTURE, severity=RuleSeverity.INFO,
                            line=1, message=f"Import '{imp}' is not used"
                        ))

                # Detect duplicate code patterns
                result.duplicate_patterns = self._detect_duplicates(code)
                if result.duplicate_patterns > 0 and self.is_rule_applicable("STRUCTURE_001", language):
                    violations.append(RuleViolation(
                        rule_id="STRUCTURE_001", rule_name="Duplicate Code",
                        category=RuleCategory.STRUCTURE, severity=RuleSeverity.WARNING,
                        line=1, message=f"Found {result.duplicate_patterns} duplicate code patterns"
                    ))
            except SyntaxError:
                pass
        else:
            # Regex-based structure analysis for other languages
            result = self._analyze_structure_regex(code, language)

        return result

    def _detect_unused_imports(self, tree: ast.AST, code: str) -> List[str]:
        """Detect unused imports in Python code."""
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.asname or alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name != '*':
                        imports.add(alias.asname or alias.name)

        # Check which imports are used
        used = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used.add(node.id)
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    used.add(node.value.id)

        return list(imports - used)

    def _detect_duplicates(self, code: str) -> int:
        """Detect duplicate code patterns."""
        lines = [l.strip() for l in code.split('\n') if l.strip() and not l.strip().startswith('#')]
        duplicates = 0
        seen = {}

        # Check for duplicate 3-line blocks
        for i in range(len(lines) - 2):
            block = tuple(lines[i:i+3])
            if block in seen:
                duplicates += 1
            else:
                seen[block] = i

        return duplicates

    def _analyze_structure_regex(self, code: str, language: str) -> StructureResult:
        """Analyze structure for non-Python languages."""
        result = StructureResult()

        class_patterns = {
            "java": r'\bclass\s+\w+',
            "javascript": r'\bclass\s+\w+',
            "typescript": r'\bclass\s+\w+',
            "cpp": r'\bclass\s+\w+',
        }

        if language in class_patterns:
            result.total_classes = len(re.findall(class_patterns[language], code))

        return result


    def _check_naming_conventions(self, code: str, language: str, violations: List[RuleViolation]) -> NamingConventionResult:
        """Check naming conventions."""
        result = NamingConventionResult()
        conventions = LANGUAGE_CONVENTIONS.get(language, LANGUAGE_CONVENTIONS["python"])

        if language == "python":
            try:
                tree = ast.parse(code)

                # Check function names
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        result.total_identifiers += 1
                        if not node.name.startswith('_') and not self._check_name(node.name, conventions["function"]):
                            result.violations += 1
                            if self.is_rule_applicable("NAMING_002", language):
                                violations.append(RuleViolation(
                                    rule_id="NAMING_002", rule_name="Invalid Function Name",
                                    category=RuleCategory.NAMING, severity=RuleSeverity.WARNING,
                                    line=node.lineno, message=f"Function '{node.name}' should use {conventions['function']}"
                                ))

                    elif isinstance(node, ast.ClassDef):
                        result.total_identifiers += 1
                        if not self._check_name(node.name, conventions["class"]):
                            result.violations += 1
                            if self.is_rule_applicable("NAMING_003", language):
                                violations.append(RuleViolation(
                                    rule_id="NAMING_003", rule_name="Invalid Class Name",
                                    category=RuleCategory.NAMING, severity=RuleSeverity.WARNING,
                                    line=node.lineno, message=f"Class '{node.name}' should use {conventions['class']}"
                                ))

                    elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                        result.total_identifiers += 1
                        name = node.id
                        if name.isupper() and '_' in name:
                            if not self._check_name(name, "UPPER_CASE"):
                                result.violations += 1
                        elif name not in LOOP_COUNTERS and len(name) > 1:
                            if not self._check_name(name, conventions["variable"]):
                                result.violations += 1
            except SyntaxError:
                pass
        else:
            result = self._check_naming_regex(code, language, violations)

        result.details = [v for v in violations if v.category == RuleCategory.NAMING]
        return result

    def _check_name(self, name: str, convention: str) -> bool:
        """Check if a name follows the specified convention."""
        pattern = NAMING_PATTERNS.get(convention)
        if pattern:
            return bool(pattern.match(name))
        return True

    def _check_naming_regex(self, code: str, language: str, violations: List[RuleViolation]) -> NamingConventionResult:
        """Check naming conventions using regex for non-Python languages."""
        result = NamingConventionResult()
        conventions = LANGUAGE_CONVENTIONS.get(language, LANGUAGE_CONVENTIONS["javascript"])

        # Check function names
        func_pattern = r'function\s+(\w+)'
        for match in re.finditer(func_pattern, code):
            result.total_identifiers += 1
            name = match.group(1)
            if not self._check_name(name, conventions["function"]):
                result.violations += 1

        # Check class names
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, code):
            result.total_identifiers += 1
            name = match.group(1)
            if not self._check_name(name, conventions["class"]):
                result.violations += 1

        return result

    def _check_security(self, code: str, language: str, violations: List[RuleViolation]) -> None:
        """Check for security vulnerabilities."""
        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            # Check hardcoded credentials
            if self.is_rule_applicable("SECURITY_001", language):
                for pattern in SECURITY_PATTERNS["hardcoded_password"]:
                    if pattern.search(line):
                        violations.append(RuleViolation(
                            rule_id="SECURITY_001", rule_name="Hardcoded Credentials",
                            category=RuleCategory.SECURITY, severity=RuleSeverity.ERROR,
                            line=i, message="Potential hardcoded credential detected"
                        ))
                        break

            # Check SQL injection
            if self.is_rule_applicable("SECURITY_002", language):
                for pattern in SECURITY_PATTERNS["sql_injection"]:
                    if pattern.search(line):
                        violations.append(RuleViolation(
                            rule_id="SECURITY_002", rule_name="SQL Injection Risk",
                            category=RuleCategory.SECURITY, severity=RuleSeverity.ERROR,
                            line=i, message="Potential SQL injection vulnerability"
                        ))
                        break

            # Check eval usage
            if self.is_rule_applicable("SECURITY_003", language):
                for pattern in SECURITY_PATTERNS["eval_usage"]:
                    if pattern.search(line):
                        violations.append(RuleViolation(
                            rule_id="SECURITY_003", rule_name="Eval Usage",
                            category=RuleCategory.SECURITY, severity=RuleSeverity.ERROR,
                            line=i, message="Use of eval() or exec() is dangerous"
                        ))
                        break

            # Check XSS risk
            if self.is_rule_applicable("SECURITY_004", language):
                for pattern in SECURITY_PATTERNS["xss_risk"]:
                    if pattern.search(line):
                        violations.append(RuleViolation(
                            rule_id="SECURITY_004", rule_name="XSS Risk",
                            category=RuleCategory.SECURITY, severity=RuleSeverity.ERROR,
                            line=i, message="Potential XSS vulnerability"
                        ))
                        break

    def _check_style(self, code: str, language: str, violations: List[RuleViolation]) -> None:
        """Check style issues."""
        lines = code.split('\n')
        max_length = self.config.max_line_length

        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > max_length and self.is_rule_applicable("STYLE_001", language):
                violations.append(RuleViolation(
                    rule_id="STYLE_001", rule_name="Line Too Long",
                    category=RuleCategory.STYLE, severity=RuleSeverity.INFO,
                    line=i, message=f"Line has {len(line)} characters (max: {max_length})"
                ))

            # Check trailing whitespace
            if line.rstrip() != line and self.is_rule_applicable("STYLE_003", language):
                violations.append(RuleViolation(
                    rule_id="STYLE_003", rule_name="Trailing Whitespace",
                    category=RuleCategory.STYLE, severity=RuleSeverity.INFO,
                    line=i, message="Line has trailing whitespace"
                ))


    def _calculate_scores(self, violations: List[RuleViolation], line_metrics: LineMetrics, complexity: ComplexityResult) -> AnalysisResultSummary:
        """Calculate quality scores based on violations."""
        # Count violations by severity
        errors = sum(1 for v in violations if v.severity == RuleSeverity.ERROR)
        warnings = sum(1 for v in violations if v.severity == RuleSeverity.WARNING)
        infos = sum(1 for v in violations if v.severity == RuleSeverity.INFO)

        # Calculate category scores
        category_violations: Dict[RuleCategory, List[RuleViolation]] = {}
        for v in violations:
            if v.category not in category_violations:
                category_violations[v.category] = []
            category_violations[v.category].append(v)

        category_scores = []
        category_weights = {
            RuleCategory.SECURITY: 3.0,
            RuleCategory.COMPLEXITY: 2.0,
            RuleCategory.BEST_PRACTICES: 1.5,
            RuleCategory.STRUCTURE: 1.0,
            RuleCategory.NAMING: 0.8,
            RuleCategory.STYLE: 0.5,
        }

        for category in RuleCategory:
            cat_violations = category_violations.get(category, [])
            weight = category_weights.get(category, 1.0)

            # Calculate penalty based on violations
            penalty = 0
            for v in cat_violations:
                if v.severity == RuleSeverity.ERROR:
                    penalty += 15
                elif v.severity == RuleSeverity.WARNING:
                    penalty += 5
                else:
                    penalty += 1

            score = max(0, 100 - penalty)
            category_scores.append(CategoryScore(
                category=category, score=score,
                violations=len(cat_violations), weight=weight
            ))

        # Calculate overall score (weighted average)
        total_weight = sum(cs.weight for cs in category_scores)
        weighted_sum = sum(cs.score * cs.weight for cs in category_scores)
        overall_score = round(weighted_sum / total_weight, 1) if total_weight > 0 else 100

        # Adjust for complexity
        if complexity.max_cyclomatic_complexity > 20:
            overall_score = max(0, overall_score - 10)
        elif complexity.max_cyclomatic_complexity > 15:
            overall_score = max(0, overall_score - 5)

        # Determine grade
        if overall_score >= 90:
            grade = "A"
        elif overall_score >= 80:
            grade = "B"
        elif overall_score >= 70:
            grade = "C"
        elif overall_score >= 60:
            grade = "D"
        else:
            grade = "F"

        return AnalysisResultSummary(
            overall_score=overall_score, grade=grade,
            category_scores=category_scores,
            total_violations=len(violations),
            critical_violations=errors,
            warnings=warnings, info_violations=infos
        )

    def _generate_recommendations(self, violations: List[RuleViolation], complexity: ComplexityResult, structure: StructureResult) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Security recommendations
        security_violations = [v for v in violations if v.category == RuleCategory.SECURITY]
        if security_violations:
            recommendations.append("🔒 Address security vulnerabilities immediately - found potential credential exposure or injection risks")

        # Complexity recommendations
        if complexity.max_cyclomatic_complexity > 15:
            recommendations.append(f"📊 Refactor complex functions - maximum complexity is {complexity.max_cyclomatic_complexity}, consider breaking into smaller functions")

        if complexity.max_function_length > 50:
            recommendations.append(f"📏 Reduce function length - longest function has {complexity.max_function_length} lines, aim for under 50")

        if complexity.max_nesting_depth > 4:
            recommendations.append(f"🔄 Reduce nesting depth - maximum depth is {complexity.max_nesting_depth}, consider early returns or extracting methods")

        # Structure recommendations
        if structure.unused_imports:
            recommendations.append(f"🧹 Remove {len(structure.unused_imports)} unused imports to clean up the code")

        if structure.duplicate_patterns > 0:
            recommendations.append(f"♻️ Found {structure.duplicate_patterns} duplicate code patterns - consider extracting to reusable functions")

        # Naming recommendations
        naming_violations = [v for v in violations if v.category == RuleCategory.NAMING]
        if len(naming_violations) > 5:
            recommendations.append("📝 Review naming conventions - multiple identifiers don't follow language standards")

        # Style recommendations
        style_violations = [v for v in violations if v.category == RuleCategory.STYLE]
        if len(style_violations) > 10:
            recommendations.append("✨ Consider using an auto-formatter to fix style issues")

        if not recommendations:
            recommendations.append("✅ Code quality looks good! Keep up the good work.")

        return recommendations


# Create singleton instance
enhanced_analysis_service = EnhancedAnalysisService()
