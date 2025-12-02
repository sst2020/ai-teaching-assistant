"""
Security and Performance Analysis Service.

This module provides:
- Security vulnerability detection using Bandit
- Performance anti-pattern detection
- Best practices evaluation
"""
import ast
import json
import uuid
import tempfile
import subprocess
import logging
import os
import re
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timezone

from schemas.analysis import (
    SecurityResult, SecurityIssue, SecurityRequest, SecuritySeverity,
    PerformanceResult, PerformanceIssue, PerformanceRequest,
    PerformanceIssueType, BestPracticeViolation, IssueSeverity
)

logger = logging.getLogger(__name__)


# Chinese translations for Bandit test IDs
BANDIT_MESSAGE_ZH: Dict[str, str] = {
    "B101": "使用 assert 语句（在优化模式下会被忽略）",
    "B102": "使用 exec 函数",
    "B103": "设置了宽松的文件权限",
    "B104": "绑定到所有接口",
    "B105": "硬编码的密码字符串",
    "B106": "硬编码的密码作为函数参数",
    "B107": "硬编码的密码作为默认值",
    "B108": "可能的硬编码临时文件路径",
    "B110": "使用 pass 处理异常",
    "B112": "使用 continue 处理异常",
    "B201": "使用 Flask 调试模式",
    "B301": "使用 pickle 模块",
    "B302": "使用 marshal 模块",
    "B303": "使用不安全的 MD5/SHA1 哈希",
    "B304": "使用不安全的密码",
    "B305": "使用不安全的密码模式",
    "B306": "使用 mktemp（不安全）",
    "B307": "使用 eval 函数",
    "B308": "使用 mark_safe 可能导致 XSS",
    "B309": "使用 HTTPSConnection 但未验证证书",
    "B310": "使用 urllib.urlopen",
    "B311": "使用 random 模块（非加密安全）",
    "B312": "使用 telnetlib",
    "B313": "使用不安全的 XML 解析器",
    "B314": "使用不安全的 XML 解析器",
    "B315": "使用不安全的 XML 解析器",
    "B316": "使用不安全的 XML 解析器",
    "B317": "使用不安全的 XML 解析器",
    "B318": "使用不安全的 XML 解析器",
    "B319": "使用不安全的 XML 解析器",
    "B320": "使用不安全的 XML 解析器",
    "B321": "使用 FTP",
    "B323": "使用不安全的 SSL 上下文",
    "B324": "使用不安全的哈希函数",
    "B401": "导入 telnetlib",
    "B402": "导入 ftplib",
    "B403": "导入 pickle",
    "B404": "导入 subprocess",
    "B405": "导入不安全的 XML 解析器",
    "B406": "导入不安全的 XML 解析器",
    "B407": "导入不安全的 XML 解析器",
    "B408": "导入不安全的 XML 解析器",
    "B409": "导入不安全的 XML 解析器",
    "B410": "导入 lxml",
    "B411": "导入 xmlrpc",
    "B412": "导入 httpoxy 易受攻击的库",
    "B413": "导入 pycrypto",
    "B501": "使用不安全的 SSL/TLS 版本",
    "B502": "使用不安全的 SSL/TLS 版本",
    "B503": "使用不安全的 SSL/TLS 版本",
    "B504": "使用不安全的 SSL/TLS 版本",
    "B505": "使用弱加密密钥",
    "B506": "使用不安全的 YAML 加载",
    "B507": "使用不安全的 SSH 主机密钥验证",
    "B601": "使用 paramiko 调用",
    "B602": "使用 subprocess 的 shell=True",
    "B603": "使用 subprocess 但未验证输入",
    "B604": "使用 shell 函数",
    "B605": "使用 os.system 启动进程",
    "B606": "使用 os.popen 启动进程",
    "B607": "使用部分可执行路径启动进程",
    "B608": "可能的 SQL 注入",
    "B609": "使用通配符注入",
    "B610": "使用 Django extra 可能导致 SQL 注入",
    "B611": "使用 Django RawSQL 可能导致 SQL 注入",
    "B701": "使用 Jinja2 自动转义禁用",
    "B702": "使用 Mako 模板",
    "B703": "使用 Django mark_safe",
}


# Security recommendations
BANDIT_RECOMMENDATIONS: Dict[str, str] = {
    "B101": "不要在生产代码中依赖 assert 进行安全检查，使用显式的条件判断",
    "B102": "避免使用 exec，考虑使用更安全的替代方案",
    "B105": "使用环境变量或配置文件存储密码，不要硬编码",
    "B106": "使用环境变量或配置文件存储密码",
    "B107": "使用环境变量或配置文件存储密码",
    "B301": "使用 json 模块替代 pickle，或确保只处理可信数据",
    "B303": "使用 SHA-256 或更强的哈希算法",
    "B307": "避免使用 eval，使用 ast.literal_eval 或其他安全替代方案",
    "B311": "对于安全相关的随机数，使用 secrets 模块",
    "B602": "避免使用 shell=True，使用参数列表传递命令",
    "B608": "使用参数化查询防止 SQL 注入",
}


def get_security_severity(severity: str) -> SecuritySeverity:
    """Convert Bandit severity to SecuritySeverity."""
    severity_map = {
        "HIGH": SecuritySeverity.HIGH,
        "MEDIUM": SecuritySeverity.MEDIUM,
        "LOW": SecuritySeverity.LOW,
    }
    return severity_map.get(severity.upper(), SecuritySeverity.LOW)


class SecurityAnalyzer:
    """Security vulnerability analyzer using Bandit."""
    
    async def analyze(self, request: SecurityRequest) -> SecurityResult:
        """Perform security analysis on code."""
        analysis_id = str(uuid.uuid4())
        
        if request.language != "python":
            return SecurityResult(
                analysis_id=analysis_id,
                analyzed_at=datetime.now(timezone.utc),
                language=request.language,
                score=100.0,
                total_issues=0,
                summary=f"暂不支持 {request.language} 语言的安全分析"
            )
        
        issues: List[SecurityIssue] = []
        bandit_available = False

        try:
            # Write code to temp file
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False, encoding='utf-8'
            ) as f:
                f.write(request.code)
                temp_path = f.name

            try:
                # Run Bandit
                cmd = [
                    "python", "-m", "bandit",
                    "-f", "json",
                    "-ll",  # Only report issues with severity >= LOW
                    temp_path
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                # Parse JSON output
                if result.stdout:
                    try:
                        bandit_output = json.loads(result.stdout)
                        issues = self._parse_bandit_output(
                            bandit_output, request.code, request.severity_threshold
                        )
                        bandit_available = True
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse Bandit JSON output")

            finally:
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass

        except subprocess.TimeoutExpired:
            return SecurityResult(
                analysis_id=analysis_id,
                analyzed_at=datetime.now(timezone.utc),
                language=request.language,
                score=0.0,
                summary="安全分析超时"
            )
        except FileNotFoundError:
            # Bandit not installed, use fallback analysis
            pass
        except Exception as e:
            logger.error(f"Security analysis failed: {e}")

        # Always run fallback check and merge results
        fallback_issues = self._fallback_security_check(request.code)

        # Merge issues, avoiding duplicates by line number and test_id
        existing_keys = {(i.line, i.test_id) for i in issues}
        for fi in fallback_issues:
            if (fi.line, fi.test_id) not in existing_keys:
                issues.append(fi)
        
        # Count by severity
        high = sum(1 for i in issues if i.severity == SecuritySeverity.HIGH)
        medium = sum(1 for i in issues if i.severity == SecuritySeverity.MEDIUM)
        low = sum(1 for i in issues if i.severity == SecuritySeverity.LOW)
        
        # Calculate score
        score = max(0, 100 - (high * 20 + medium * 10 + low * 5))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(issues)
        
        # Generate summary
        summary = self._generate_summary(len(issues), high, medium, low)
        
        return SecurityResult(
            analysis_id=analysis_id,
            analyzed_at=datetime.now(timezone.utc),
            language=request.language,
            score=round(score, 1),
            total_issues=len(issues),
            high_severity=high,
            medium_severity=medium,
            low_severity=low,
            issues=issues,
            summary=summary,
            recommendations=recommendations
        )

    def _parse_bandit_output(
        self, output: Dict, code: str, threshold: SecuritySeverity
    ) -> List[SecurityIssue]:
        """Parse Bandit JSON output into SecurityIssue objects."""
        issues = []
        lines = code.split('\n')

        severity_order = {
            SecuritySeverity.LOW: 0,
            SecuritySeverity.MEDIUM: 1,
            SecuritySeverity.HIGH: 2,
        }
        threshold_level = severity_order.get(threshold, 0)

        for result in output.get("results", []):
            severity = get_security_severity(result.get("issue_severity", "LOW"))

            # Filter by threshold
            if severity_order.get(severity, 0) < threshold_level:
                continue

            test_id = result.get("test_id", "")
            line = result.get("line_number", 1)

            # Get code snippet
            code_snippet = ""
            if 0 < line <= len(lines):
                code_snippet = lines[line - 1].strip()

            issues.append(SecurityIssue(
                issue_id=str(uuid.uuid4()),
                test_id=test_id,
                test_name=result.get("test_name", ""),
                severity=severity,
                confidence=result.get("issue_confidence", "MEDIUM"),
                line=line,
                column=result.get("col_offset", 0),
                code_snippet=code_snippet,
                issue_text=result.get("issue_text", ""),
                issue_text_zh=BANDIT_MESSAGE_ZH.get(test_id, result.get("issue_text", "")),
                more_info=result.get("more_info", ""),
                recommendation=BANDIT_RECOMMENDATIONS.get(test_id, "")
            ))

        return issues

    def _fallback_security_check(self, code: str) -> List[SecurityIssue]:
        """Fallback security check using pattern matching."""
        issues = []
        lines = code.split('\n')

        # Security patterns to check
        patterns = [
            (r'\beval\s*\(', "B307", "使用 eval 函数", SecuritySeverity.HIGH),
            (r'\bexec\s*\(', "B102", "使用 exec 函数", SecuritySeverity.HIGH),
            (r'password\s*=\s*["\'][^"\']+["\']', "B105", "硬编码的密码", SecuritySeverity.HIGH),
            (r'secret\s*=\s*["\'][^"\']+["\']', "B105", "硬编码的密钥", SecuritySeverity.HIGH),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "B105", "硬编码的 API 密钥", SecuritySeverity.HIGH),
            (r'\bpickle\.load', "B301", "使用 pickle 加载数据", SecuritySeverity.MEDIUM),
            (r'shell\s*=\s*True', "B602", "使用 shell=True", SecuritySeverity.HIGH),
            (r'os\.system\s*\(', "B605", "使用 os.system", SecuritySeverity.MEDIUM),
            (r'md5\s*\(|\.md5\(', "B303", "使用不安全的 MD5 哈希", SecuritySeverity.MEDIUM),
            (r'sha1\s*\(|\.sha1\(', "B303", "使用不安全的 SHA1 哈希", SecuritySeverity.MEDIUM),
            (r'random\.(random|randint|choice)', "B311", "使用非加密安全的随机数", SecuritySeverity.LOW),
            (r'assert\s+', "B101", "使用 assert 语句", SecuritySeverity.LOW),
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern, test_id, message, severity in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(SecurityIssue(
                        issue_id=str(uuid.uuid4()),
                        test_id=test_id,
                        test_name=test_id.lower(),
                        severity=severity,
                        confidence="MEDIUM",
                        line=line_num,
                        code_snippet=line.strip(),
                        issue_text=message,
                        issue_text_zh=BANDIT_MESSAGE_ZH.get(test_id, message),
                        recommendation=BANDIT_RECOMMENDATIONS.get(test_id, "")
                    ))

        return issues

    def _generate_recommendations(self, issues: List[SecurityIssue]) -> List[str]:
        """Generate security recommendations."""
        recommendations = []
        seen_tests = set()

        for issue in issues:
            if issue.test_id not in seen_tests and issue.recommendation:
                recommendations.append(f"🔒 {issue.recommendation}")
                seen_tests.add(issue.test_id)

        if not recommendations:
            recommendations.append("✅ 未发现明显的安全问题")

        return recommendations[:5]  # Limit to top 5

    def _generate_summary(
        self, total: int, high: int, medium: int, low: int
    ) -> str:
        """Generate security analysis summary."""
        if total == 0:
            return "代码安全检查通过，未发现安全漏洞。"

        parts = [f"发现 {total} 个安全问题"]

        if high > 0:
            parts.append(f"{high} 个高危")
        if medium > 0:
            parts.append(f"{medium} 个中危")
        if low > 0:
            parts.append(f"{low} 个低危")

        return "，".join(parts) + "。建议立即修复高危问题。"


# Performance patterns to detect
PERFORMANCE_PATTERNS = [
    {
        "pattern": r"for\s+\w+\s+in\s+range\s*\(\s*len\s*\(",
        "type": PerformanceIssueType.INEFFICIENT_ALGORITHM,
        "message": "使用 range(len()) 遍历，可以直接遍历或使用 enumerate",
        "suggestion": "使用 for item in list 或 for i, item in enumerate(list)",
        "severity": IssueSeverity.INFO,
    },
    {
        "pattern": r"\+\s*=\s*['\"]",
        "type": PerformanceIssueType.INEFFICIENT_ALGORITHM,
        "message": "在循环中使用字符串拼接，效率较低",
        "suggestion": "使用列表收集字符串，最后用 ''.join() 连接",
        "severity": IssueSeverity.WARNING,
    },
    {
        "pattern": r"while\s+True\s*:",
        "type": PerformanceIssueType.INFINITE_LOOP,
        "message": "无限循环，确保有正确的退出条件",
        "suggestion": "确保循环内有 break 或 return 语句",
        "severity": IssueSeverity.WARNING,
    },
    {
        "pattern": r"time\.sleep\s*\(\s*0\s*\)",
        "type": PerformanceIssueType.BLOCKING_OPERATION,
        "message": "sleep(0) 调用可能导致 CPU 空转",
        "suggestion": "使用适当的等待时间或异步等待",
        "severity": IssueSeverity.INFO,
    },
    {
        "pattern": r"\.read\s*\(\s*\)",
        "type": PerformanceIssueType.MEMORY_LEAK,
        "message": "一次性读取整个文件可能导致内存问题",
        "suggestion": "对于大文件，使用迭代器逐行读取",
        "severity": IssueSeverity.INFO,
    },
    {
        "pattern": r"global\s+\w+",
        "type": PerformanceIssueType.INEFFICIENT_ALGORITHM,
        "message": "使用全局变量可能影响性能和可维护性",
        "suggestion": "考虑使用类或函数参数传递状态",
        "severity": IssueSeverity.INFO,
    },
    {
        "pattern": r"import\s+\*",
        "type": PerformanceIssueType.INEFFICIENT_ALGORITHM,
        "message": "通配符导入会导入不必要的模块",
        "suggestion": "明确导入需要的名称",
        "severity": IssueSeverity.INFO,
    },
]


# Best practice rules
BEST_PRACTICE_RULES = [
    {
        "pattern": r"except\s*:",
        "category": "异常处理",
        "rule": "避免裸 except 子句",
        "description": "捕获所有异常会隐藏错误",
        "suggestion": "指定具体的异常类型",
        "severity": IssueSeverity.WARNING,
    },
    {
        "pattern": r"except\s+Exception\s*:",
        "category": "异常处理",
        "rule": "避免捕获过于宽泛的异常",
        "description": "捕获 Exception 会隐藏意外错误",
        "suggestion": "捕获更具体的异常类型",
        "severity": IssueSeverity.INFO,
    },
    {
        "pattern": r"print\s*\(",
        "category": "日志记录",
        "rule": "使用日志模块而不是 print",
        "description": "print 语句不适合生产环境",
        "suggestion": "使用 logging 模块进行日志记录",
        "severity": IssueSeverity.INFO,
    },
    {
        "pattern": r"#\s*TODO|#\s*FIXME|#\s*XXX|#\s*HACK",
        "category": "代码质量",
        "rule": "存在待处理的注释",
        "description": "代码中有未完成的工作",
        "suggestion": "完成或创建任务跟踪这些项目",
        "severity": IssueSeverity.INFO,
    },
    {
        "pattern": r"def\s+\w+\s*\([^)]*\)\s*:\s*\n\s*pass",
        "category": "代码完整性",
        "rule": "空函数实现",
        "description": "函数只有 pass 语句",
        "suggestion": "实现函数逻辑或添加 NotImplementedError",
        "severity": IssueSeverity.INFO,
    },
    {
        "pattern": r"if\s+\w+\s*==\s*True|if\s+\w+\s*==\s*False",
        "category": "代码风格",
        "rule": "不必要的布尔比较",
        "description": "与 True/False 的显式比较是多余的",
        "suggestion": "直接使用 if x 或 if not x",
        "severity": IssueSeverity.CONVENTION,
    },
    {
        "pattern": r"if\s+len\s*\([^)]+\)\s*==\s*0|if\s+len\s*\([^)]+\)\s*>\s*0",
        "category": "代码风格",
        "rule": "不必要的 len() 检查",
        "description": "可以直接使用容器的真值测试",
        "suggestion": "使用 if not container 或 if container",
        "severity": IssueSeverity.CONVENTION,
    },
]


class PerformanceAnalyzer:
    """Performance and best practices analyzer."""

    async def analyze(self, request: PerformanceRequest) -> PerformanceResult:
        """Perform performance analysis on code."""
        analysis_id = str(uuid.uuid4())

        performance_issues: List[PerformanceIssue] = []
        best_practice_violations: List[BestPracticeViolation] = []

        lines = request.code.split('\n')

        # Check performance patterns
        for line_num, line in enumerate(lines, 1):
            for pattern_info in PERFORMANCE_PATTERNS:
                if re.search(pattern_info["pattern"], line):
                    performance_issues.append(PerformanceIssue(
                        issue_type=pattern_info["type"],
                        severity=pattern_info["severity"],
                        line=line_num,
                        code_snippet=line.strip(),
                        description=pattern_info["message"],
                        description_zh=pattern_info["message"],
                        impact="可能影响代码执行效率",
                        suggestion=pattern_info["suggestion"]
                    ))

        # Check best practices
        if request.check_best_practices:
            for line_num, line in enumerate(lines, 1):
                for rule in BEST_PRACTICE_RULES:
                    if re.search(rule["pattern"], line, re.IGNORECASE):
                        best_practice_violations.append(BestPracticeViolation(
                            category=rule["category"],
                            rule=rule["rule"],
                            severity=rule["severity"],
                            line=line_num,
                            description=rule["description"],
                            description_zh=rule["description"],
                            suggestion=rule["suggestion"]
                        ))

        # AST-based analysis for Python
        if request.language == "python":
            try:
                tree = ast.parse(request.code)
                ast_issues = self._analyze_ast(tree, lines)
                performance_issues.extend(ast_issues)
            except SyntaxError:
                pass

        # Calculate score
        total_issues = len(performance_issues) + len(best_practice_violations)
        score = max(0, 100 - total_issues * 5)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            performance_issues, best_practice_violations
        )

        # Generate summary
        summary = self._generate_summary(
            len(performance_issues), len(best_practice_violations)
        )

        return PerformanceResult(
            analysis_id=analysis_id,
            analyzed_at=datetime.now(timezone.utc),
            language=request.language,
            score=round(score, 1),
            total_issues=total_issues,
            performance_issues=performance_issues,
            best_practice_violations=best_practice_violations,
            summary=summary,
            recommendations=recommendations
        )

    def _analyze_ast(
        self, tree: ast.AST, lines: List[str]
    ) -> List[PerformanceIssue]:
        """Analyze AST for performance issues."""
        issues = []

        for node in ast.walk(tree):
            # Check for nested loops (potential O(n²) complexity)
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if child is not node and isinstance(child, (ast.For, ast.While)):
                        issues.append(PerformanceIssue(
                            issue_type=PerformanceIssueType.INEFFICIENT_ALGORITHM,
                            severity=IssueSeverity.INFO,
                            line=node.lineno,
                            code_snippet=lines[node.lineno - 1].strip() if node.lineno <= len(lines) else "",
                            description="嵌套循环可能导致 O(n²) 复杂度",
                            description_zh="嵌套循环可能导致 O(n²) 复杂度",
                            impact="对于大数据集可能导致性能问题",
                            suggestion="考虑使用字典或集合优化查找操作"
                        ))
                        break

            # Check for list comprehension in loop
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, ast.ListComp):
                        issues.append(PerformanceIssue(
                            issue_type=PerformanceIssueType.MEMORY_LEAK,
                            severity=IssueSeverity.INFO,
                            line=node.lineno,
                            code_snippet=lines[node.lineno - 1].strip() if node.lineno <= len(lines) else "",
                            description="循环中创建列表推导式可能导致内存问题",
                            description_zh="循环中创建列表推导式可能导致内存问题",
                            impact="可能导致不必要的内存分配",
                            suggestion="考虑使用生成器表达式"
                        ))

        return issues

    def _generate_recommendations(
        self,
        perf_issues: List[PerformanceIssue],
        bp_violations: List[BestPracticeViolation]
    ) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []

        # Group by type
        issue_types = set(i.issue_type for i in perf_issues)

        if PerformanceIssueType.INEFFICIENT_ALGORITHM in issue_types:
            recommendations.append("⚡ 优化算法复杂度，避免不必要的嵌套循环")

        if PerformanceIssueType.MEMORY_LEAK in issue_types:
            recommendations.append("💾 注意内存使用，使用生成器处理大数据")

        if PerformanceIssueType.BLOCKING_OPERATION in issue_types:
            recommendations.append("⏱️ 避免阻塞操作，考虑使用异步处理")

        # Best practice recommendations
        categories = set(v.category for v in bp_violations)

        if "异常处理" in categories:
            recommendations.append("🛡️ 改进异常处理，捕获具体的异常类型")

        if "日志记录" in categories:
            recommendations.append("📝 使用 logging 模块替代 print 语句")

        if not recommendations:
            recommendations.append("✅ 代码性能良好，未发现明显问题")

        return recommendations[:5]

    def _generate_summary(
        self, perf_count: int, bp_count: int
    ) -> str:
        """Generate performance analysis summary."""
        if perf_count == 0 and bp_count == 0:
            return "代码性能良好，符合最佳实践。"

        parts = []
        if perf_count > 0:
            parts.append(f"发现 {perf_count} 个性能问题")
        if bp_count > 0:
            parts.append(f"{bp_count} 个最佳实践违规")

        return "，".join(parts) + "。"


# Create singleton instances
security_analyzer = SecurityAnalyzer()
performance_analyzer = PerformanceAnalyzer()

