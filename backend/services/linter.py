"""
Linter Integration Service.

This module provides integration with code linting tools:
- Pylint for Python code
- Configurable rule system
- Structured output with Chinese explanations
"""
import json
import uuid
import tempfile
import subprocess
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path

from schemas.analysis import (
    LintResult, LintIssue, LintRuleConfig, LintRequest,
    IssueSeverity
)

logger = logging.getLogger(__name__)


# Chinese translations for common Pylint messages
PYLINT_MESSAGE_ZH: Dict[str, str] = {
    # Convention (C)
    "C0301": "行太长（超过最大字符限制）",
    "C0302": "模块行数过多",
    "C0303": "行尾有多余空格",
    "C0304": "文件末尾缺少换行符",
    "C0305": "文件末尾有多余空行",
    "C0321": "同一行有多条语句",
    "C0325": "不必要的括号",
    "C0326": "空格使用不规范",
    "C0330": "缩进不正确",
    "C0410": "多个导入在同一行",
    "C0411": "导入顺序错误（标准库应在第三方库之前）",
    "C0412": "导入未按字母顺序排列",
    "C0413": "导入语句位置错误（应在模块顶部）",
    "C0414": "无用的导入别名",
    "C0415": "在函数外部导入",
    
    # Refactor (R)
    "R0201": "方法可以是函数（不使用 self）",
    "R0801": "代码重复",
    "R0901": "类的继承层次过深",
    "R0902": "实例属性过多",
    "R0903": "公共方法过少",
    "R0904": "公共方法过多",
    "R0911": "返回语句过多",
    "R0912": "分支过多",
    "R0913": "参数过多",
    "R0914": "局部变量过多",
    "R0915": "语句过多",
    "R0916": "布尔表达式过于复杂",
    "R1702": "嵌套块过多",
    "R1703": "可以简化为三元表达式",
    "R1705": "else 后不需要 return",
    "R1710": "要么所有返回语句都返回值，要么都不返回",
    "R1714": "可以使用 in 运算符简化",
    "R1715": "可以使用 dict.get() 简化",
    "R1716": "可以使用链式比较简化",
    "R1720": "不必要的 else 块",
    "R1721": "不必要的列表推导式",
    "R1722": "使用 sys.exit() 而不是 exit()",
    "R1723": "不必要的 elif 块",
    "R1724": "不必要的 else 块（可以使用 continue）",
    "R1725": "使用 super() 而不是 super(类名, self)",
    "R1728": "使用生成器表达式而不是列表推导式",
    "R1729": "使用生成器表达式而不是列表推导式",
    "R1730": "可以使用 min() 内置函数",
    "R1731": "可以使用 max() 内置函数",
    "R1732": "使用 with 语句管理资源",
    "R1733": "不必要的字典索引查找",
    "R1734": "使用列表字面量而不是 list()",
    "R1735": "使用字典字面量而不是 dict()",
    
    # Warning (W)
    "W0101": "return 后有不可达代码",
    "W0102": "使用可变默认参数",
    "W0104": "语句无效果",
    "W0105": "字符串语句无效果",
    "W0106": "表达式结果未使用",
    "W0107": "不必要的 pass 语句",
    "W0108": "不必要的 lambda 表达式",
    "W0109": "字典键重复",
    "W0120": "else 子句在没有 break 的循环中",
    "W0122": "使用 exec",
    "W0123": "使用 eval",
    "W0125": "使用常量作为条件",
    "W0143": "比较使用 is 而不是 ==",
    "W0150": "finally 中的 return 会覆盖 try 中的 return",
    "W0199": "assert 语句总是为真",
    "W0201": "在 __init__ 外定义属性",
    "W0211": "静态方法使用了 self",
    "W0212": "访问受保护成员",
    "W0221": "参数与重写的方法不同",
    "W0222": "签名与重写的方法不同",
    "W0223": "抽象方法未实现",
    "W0231": "未调用父类 __init__",
    "W0233": "调用了错误的父类 __init__",
    "W0235": "无用的 super 委托",
    "W0236": "方法与重写的方法类型不同",
    "W0301": "不必要的分号",
    "W0311": "缩进使用了 Tab 而不是空格",
    "W0312": "混合使用 Tab 和空格缩进",
    "W0401": "使用通配符导入",
    "W0402": "使用已弃用的模块",
    "W0404": "重复导入",
    "W0406": "模块导入自身",
    "W0511": "TODO/FIXME 注释",
    "W0601": "全局变量未定义",
    "W0602": "使用全局变量但未赋值",
    "W0603": "使用 global 语句",
    "W0604": "使用 global 声明但未赋值",
    "W0611": "未使用的导入",
    "W0612": "未使用的变量",
    "W0613": "未使用的参数",
    "W0614": "通配符导入的未使用名称",
    "W0621": "重新定义外部作用域的名称",
    "W0622": "重新定义内置名称",
    "W0631": "循环变量在循环外使用",
    "W0640": "闭包中使用循环变量",
    "W0641": "可能未使用的变量",
    "W0642": "无效的类对象赋值",
    "W0702": "裸 except 子句",
    "W0703": "捕获过于宽泛的异常",
    "W0705": "except 块重复",
    "W0706": "except 处理程序立即引发异常",
    "W0707": "raise 缺少 from",
    "W0711": "except 中的二元运算",
    "W0715": "异常参数不是异常类",
    "W1113": "关键字参数在 *args 之前",
    "W1201": "使用 % 格式化日志",
    "W1202": "使用 .format() 格式化日志",
    "W1203": "使用 f-string 格式化日志",
    "W1300": "格式字符串参数不匹配",
    "W1301": "格式字符串中有未使用的参数",
    "W1302": "格式字符串中有无效的格式字符",
    "W1303": "格式字符串中缺少参数",
    "W1304": "格式字符串中有未使用的格式参数",
    "W1305": "格式字符串中混合使用位置和命名参数",
    "W1308": "格式字符串中有重复的键",
    "W1309": "f-string 中没有占位符",
    "W1310": "格式字符串中有无效的格式规范",
    "W1401": "字符串中有无效的转义序列",
    "W1404": "字符串中有隐式的字符串连接",
    "W1405": "使用 encode/decode 的默认编码",
    "W1406": "使用 open 的默认编码",
    "W1501": "open 的模式参数无效",
    "W1502": "open 的模式参数有重复字符",
    "W1503": "冗余的 open 模式参数",
    "W1505": "使用已弃用的方法",
    "W1506": "线程不安全的调用",
    "W1507": "浅拷贝 os.environ",
    "W1508": "os.getenv 的默认值无效",
    "W1509": "subprocess 的 preexec_fn 不安全",
    "W1510": "subprocess.run 缺少 check 参数",
    
    # Error (E)
    "E0001": "语法错误",
    "E0011": "无法识别的选项",
    "E0012": "错误的选项值",
    "E0100": "生成器中使用 return 返回值",
    "E0101": "__init__ 返回非 None 值",
    "E0102": "函数/类/方法重复定义",
    "E0103": "break/continue 在循环外使用",
    "E0104": "return 在函数外使用",
    "E0105": "yield 在函数外使用",
    "E0106": "return 带有参数在生成器中",
    "E0107": "无效的一元运算符",
    "E0108": "重复的参数名",
    "E0110": "抽象类被实例化",
    "E0111": "reversed() 参数不是序列",
    "E0112": "迭代器上调用 reversed()",
    "E0113": "无效的一元操作数类型",
    "E0114": "无效的二元操作数类型",
    "E0115": "非局部变量在赋值前引用",
    "E0116": "continue 在 finally 块中",
    "E0117": "非局部变量在外部作用域未绑定",
    "E0118": "在推导式中使用命名表达式",
    "E0119": "格式字符串参数类型错误",
    "E0202": "方法隐藏了类属性",
    "E0203": "在赋值前访问成员",
    "E0211": "方法没有参数",
    "E0213": "方法第一个参数应该是 self",
    "E0236": "无效的对象",
    "E0237": "赋值给非槽属性",
    "E0238": "无效的 __slots__ 对象",
    "E0239": "继承非类对象",
    "E0240": "不一致的方法解析顺序",
    "E0241": "重复的基类",
    "E0242": "类有重复的槽",
    "E0243": "无效的类对象",
    "E0244": "无效的类对象",
    "E0301": "__iter__ 返回非迭代器",
    "E0302": "__len__ 返回非整数",
    "E0303": "__len__ 返回负数",
    "E0304": "__bool__ 返回非布尔值",
    "E0305": "__index__ 返回非整数",
    "E0306": "__repr__ 返回非字符串",
    "E0307": "__str__ 返回非字符串",
    "E0308": "__bytes__ 返回非字节",
    "E0309": "__hash__ 返回非整数",
    "E0310": "__init__ 返回非 None",
    "E0311": "__del__ 返回非 None",
    "E0312": "__format__ 返回非字符串",
    "E0401": "无法导入模块",
    "E0402": "尝试相对导入但没有已知的父包",
    "E0601": "在赋值前使用变量",
    "E0602": "未定义的变量",
    "E0603": "未定义的变量名（在 __all__ 中）",
    "E0604": "__all__ 中有无效的对象",
    "E0605": "__all__ 中有无效的对象",
    "E0611": "模块中没有该名称",
    "E0633": "尝试解包非序列",
    "E0701": "except 块顺序错误",
    "E0702": "raise 只能在 except 处理程序中使用",
    "E0703": "异常上下文不是异常或 None",
    "E0704": "裸 raise 不在 except 处理程序中",
    "E0710": "raise 的不是异常类",
    "E0711": "raise 的是 NotImplemented 而不是 NotImplementedError",
    "E0712": "捕获的不是异常类",
    "E1003": "super 的第一个参数错误",
    "E1101": "对象没有该成员",
    "E1102": "对象不可调用",
    "E1111": "赋值给函数调用",
    "E1120": "缺少必需的参数",
    "E1121": "参数过多",
    "E1123": "意外的关键字参数",
    "E1124": "参数通过位置和关键字传递",
    "E1125": "缺少必需的关键字参数",
    "E1126": "序列索引不是整数",
    "E1127": "序列切片不是整数",
    "E1128": "赋值给函数调用结果",
    "E1129": "上下文管理器协议未实现",
    "E1130": "无效的一元操作数类型",
    "E1131": "无效的二元操作数类型",
    "E1132": "重复的关键字参数",
    "E1133": "非可迭代对象",
    "E1134": "非映射对象",
    "E1135": "不支持成员测试",
    "E1136": "不支持索引",
    "E1137": "不支持赋值",
    "E1138": "不支持删除",
    "E1139": "无效的元类",
    "E1140": "不可哈希的字典键",
    "E1141": "不可哈希的集合成员",
    "E1142": "await 在非异步函数中",
    "E1200": "日志格式字符串参数不匹配",
    "E1201": "日志格式字符串参数过多",
    "E1205": "日志格式字符串参数过多",
    "E1206": "日志格式字符串参数不足",
    "E1300": "格式字符串参数不匹配",
    "E1301": "格式字符串中有未使用的参数",
    "E1302": "格式字符串中有无效的格式字符",
    "E1303": "格式字符串中缺少参数",
    "E1304": "格式字符串中有未使用的格式参数",
    "E1305": "格式字符串参数过多",
    "E1306": "格式字符串参数不足",
    "E1307": "格式字符串中有无效的格式规范",
    "E1310": "字符串方法参数类型错误",
    "E1507": "os.getenv 的默认值类型错误",
    "E1519": "singledispatch 装饰器使用错误",
    "E1520": "singledispatchmethod 装饰器使用错误",
    "E1700": "yield 在 __init__ 中",
    "E1701": "yield 在异步函数中",
    
    # Fatal (F)
    "F0001": "致命错误",
    "F0002": "致命错误",
    "F0010": "解析错误",
    "F0202": "无法检查方法签名",
}


# Suggestions for common issues
PYLINT_SUGGESTIONS: Dict[str, str] = {
    "C0301": "将长行拆分为多行，或使用括号进行隐式续行",
    "C0303": "删除行尾的空格",
    "C0411": "按照标准库、第三方库、本地库的顺序组织导入",
    "W0102": "使用 None 作为默认值，在函数内部创建可变对象",
    "W0401": "明确列出需要导入的名称，避免使用 from xxx import *",
    "W0611": "删除未使用的导入语句",
    "W0612": "删除未使用的变量，或使用 _ 作为占位符",
    "W0613": "删除未使用的参数，或使用 _ 前缀表示有意忽略",
    "W0702": "指定具体的异常类型，如 except ValueError:",
    "W0703": "捕获更具体的异常类型，避免捕获 Exception",
    "E0401": "检查模块是否已安装，或检查 PYTHONPATH 设置",
    "E0602": "检查变量名拼写，或确保变量在使用前已定义",
    "E1101": "检查对象类型和属性名拼写",
    "R0913": "考虑使用配置对象或 **kwargs 减少参数数量",
    "R0914": "将部分逻辑提取到辅助函数中",
    "R0915": "将函数拆分为更小的函数",
    "R1702": "使用提前返回或提取子函数减少嵌套",
}


def get_severity_from_category(category: str) -> IssueSeverity:
    """Convert Pylint category to severity."""
    category_map = {
        "convention": IssueSeverity.CONVENTION,
        "refactor": IssueSeverity.REFACTOR,
        "warning": IssueSeverity.WARNING,
        "error": IssueSeverity.ERROR,
        "fatal": IssueSeverity.ERROR,
    }
    return category_map.get(category.lower(), IssueSeverity.WARNING)


class LinterService:
    """Service for code linting using Pylint."""
    
    def __init__(self):
        self.default_disabled_rules = [
            "C0114",  # Missing module docstring
            "C0115",  # Missing class docstring
            "C0116",  # Missing function docstring
        ]
    
    async def lint(self, request: LintRequest) -> LintResult:
        """Perform linting analysis on code."""
        analysis_id = str(uuid.uuid4())
        
        if request.language != "python":
            return LintResult(
                analysis_id=analysis_id,
                analyzed_at=datetime.now(timezone.utc),
                language=request.language,
                linter="unsupported",
                score=100.0,
                total_issues=0,
                summary=f"暂不支持 {request.language} 语言的 lint 检查"
            )
        
        issues: List[LintIssue] = []
        
        try:
            # Write code to temp file
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False, encoding='utf-8'
            ) as f:
                f.write(request.code)
                temp_path = f.name
            
            try:
                # Build Pylint command
                cmd = [
                    "python", "-m", "pylint",
                    "--output-format=json",
                    "--score=y",
                    temp_path
                ]
                
                # Add disabled rules
                disabled = self.default_disabled_rules.copy()
                for rule_config in request.rules:
                    if not rule_config.enabled:
                        disabled.append(rule_config.rule_id)
                
                if disabled:
                    cmd.append(f"--disable={','.join(disabled)}")
                
                # Run Pylint
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=os.path.dirname(temp_path)
                )
                
                # Parse JSON output
                if result.stdout:
                    try:
                        pylint_output = json.loads(result.stdout)
                        issues = self._parse_pylint_output(pylint_output, request.code)
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse Pylint JSON output")
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass
                    
        except subprocess.TimeoutExpired:
            return LintResult(
                analysis_id=analysis_id,
                analyzed_at=datetime.now(timezone.utc),
                language=request.language,
                linter="pylint",
                score=0.0,
                total_issues=0,
                summary="Lint 分析超时"
            )
        except FileNotFoundError:
            return LintResult(
                analysis_id=analysis_id,
                analyzed_at=datetime.now(timezone.utc),
                language=request.language,
                linter="pylint",
                score=0.0,
                total_issues=0,
                summary="Pylint 未安装，请运行 pip install pylint"
            )
        except Exception as e:
            logger.error(f"Linting failed: {e}")
            return LintResult(
                analysis_id=analysis_id,
                analyzed_at=datetime.now(timezone.utc),
                language=request.language,
                linter="pylint",
                score=0.0,
                total_issues=0,
                summary=f"Lint 分析失败: {str(e)}"
            )
        
        # Calculate score and counts
        errors = sum(1 for i in issues if i.severity == IssueSeverity.ERROR)
        warnings = sum(1 for i in issues if i.severity == IssueSeverity.WARNING)
        conventions = sum(1 for i in issues if i.severity == IssueSeverity.CONVENTION)
        refactors = sum(1 for i in issues if i.severity == IssueSeverity.REFACTOR)
        
        # Calculate score (Pylint style: 10 - (errors * 5 + warnings * 2 + conventions + refactors) / statements * 10)
        total_issues = len(issues)
        lines = len(request.code.split('\n'))
        penalty = (errors * 5 + warnings * 2 + conventions + refactors)
        score = max(0, min(100, 100 - (penalty / max(lines, 1)) * 10))
        
        # Generate summary
        summary = self._generate_summary(total_issues, errors, warnings, conventions, refactors)
        
        return LintResult(
            analysis_id=analysis_id,
            analyzed_at=datetime.now(timezone.utc),
            language=request.language,
            linter="pylint",
            score=round(score, 1),
            total_issues=total_issues,
            errors=errors,
            warnings=warnings,
            conventions=conventions,
            refactors=refactors,
            issues=issues,
            summary=summary
        )
    
    def _parse_pylint_output(
        self, output: List[Dict], code: str
    ) -> List[LintIssue]:
        """Parse Pylint JSON output into LintIssue objects."""
        issues = []
        lines = code.split('\n')
        
        for item in output:
            message_id = item.get("message-id", "")
            category = item.get("type", "warning")
            line = item.get("line", 1)
            column = item.get("column", 0)
            message = item.get("message", "")
            symbol = item.get("symbol", "")
            
            # Get Chinese translation
            message_zh = PYLINT_MESSAGE_ZH.get(message_id, message)
            
            # Get suggestion
            suggestion = PYLINT_SUGGESTIONS.get(message_id, "")
            
            # Get code snippet
            code_snippet = ""
            if 0 < line <= len(lines):
                code_snippet = lines[line - 1].strip()
            
            issues.append(LintIssue(
                rule_id=message_id,
                rule_name=symbol,
                category=category,
                severity=get_severity_from_category(category),
                line=line,
                column=column,
                message=message,
                message_zh=message_zh,
                suggestion=suggestion,
                code_snippet=code_snippet
            ))
        
        return issues
    
    def _generate_summary(
        self, total: int, errors: int, warnings: int, 
        conventions: int, refactors: int
    ) -> str:
        """Generate analysis summary."""
        if total == 0:
            return "代码符合编程规范，未发现问题。"
        
        parts = [f"共发现 {total} 个问题"]
        
        if errors > 0:
            parts.append(f"{errors} 个错误")
        if warnings > 0:
            parts.append(f"{warnings} 个警告")
        if conventions > 0:
            parts.append(f"{conventions} 个规范问题")
        if refactors > 0:
            parts.append(f"{refactors} 个重构建议")
        
        return "，".join(parts) + "。"


# Create singleton instance
linter_service = LinterService()

