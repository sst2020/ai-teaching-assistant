"""
Seed script for feedback templates.
Run with: python -m scripts.seed_feedback_templates
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from core.database import AsyncSessionLocal, async_engine, Base
from models.feedback_template import FeedbackTemplate, TemplateCategory


# Default feedback templates
DEFAULT_TEMPLATES = [
    # Common Issues
    {
        "name": "Missing Docstring",
        "category": TemplateCategory.COMMON_ISSUES.value,
        "title": "Missing Documentation",
        "message": "The function '{function_name}' is missing a docstring. Adding documentation helps others understand what your code does and how to use it.",
        "severity": "info",
        "tags": ["documentation", "docstring", "best-practice"],
        "variables": ["function_name"]
    },
    {
        "name": "Unused Variable",
        "category": TemplateCategory.COMMON_ISSUES.value,
        "title": "Unused Variable Detected",
        "message": "The variable '{variable_name}' is defined but never used. Consider removing it or using it in your code.",
        "severity": "warning",
        "tags": ["unused", "variable", "cleanup"],
        "variables": ["variable_name"]
    },
    {
        "name": "Magic Number",
        "category": TemplateCategory.COMMON_ISSUES.value,
        "title": "Magic Number Found",
        "message": "The value '{value}' appears to be a magic number. Consider defining it as a named constant for better readability.",
        "severity": "info",
        "tags": ["magic-number", "constant", "readability"],
        "variables": ["value"]
    },
    {
        "name": "Long Function",
        "category": TemplateCategory.COMMON_ISSUES.value,
        "title": "Function Too Long",
        "message": "The function '{function_name}' has {line_count} lines. Consider breaking it into smaller, more focused functions.",
        "severity": "warning",
        "tags": ["complexity", "refactoring", "function-length"],
        "variables": ["function_name", "line_count"]
    },
    {
        "name": "Deep Nesting",
        "category": TemplateCategory.COMMON_ISSUES.value,
        "title": "Deep Nesting Detected",
        "message": "Your code has {nesting_level} levels of nesting. Consider using early returns or extracting logic to reduce complexity.",
        "severity": "warning",
        "tags": ["nesting", "complexity", "readability"],
        "variables": ["nesting_level"]
    },
    # Naming Issues
    {
        "name": "Non-Descriptive Name",
        "category": TemplateCategory.NAMING.value,
        "title": "Non-Descriptive Variable Name",
        "message": "The variable '{variable_name}' could be more descriptive. Consider using a name that explains its purpose.",
        "severity": "info",
        "tags": ["naming", "readability", "descriptive"],
        "variables": ["variable_name"]
    },
    {
        "name": "Wrong Naming Convention",
        "category": TemplateCategory.NAMING.value,
        "title": "Naming Convention Violation",
        "message": "'{identifier}' should follow {expected_convention} naming convention. Consider renaming to '{suggested_name}'.",
        "severity": "info",
        "tags": ["naming", "convention", "style"],
        "variables": ["identifier", "expected_convention", "suggested_name"]
    },
    {
        "name": "Single Letter Variable",
        "category": TemplateCategory.NAMING.value,
        "title": "Single Letter Variable Name",
        "message": "The variable '{variable_name}' uses a single letter. Unless it's a loop counter, consider using a more descriptive name.",
        "severity": "info",
        "tags": ["naming", "readability", "single-letter"],
        "variables": ["variable_name"]
    },
    # Style Issues
    {
        "name": "Inconsistent Indentation",
        "category": TemplateCategory.STYLE.value,
        "title": "Inconsistent Indentation",
        "message": "Line {line_number} has inconsistent indentation. Use {expected_spaces} spaces consistently throughout your code.",
        "severity": "warning",
        "tags": ["style", "indentation", "formatting"],
        "variables": ["line_number", "expected_spaces"]
    },
    {
        "name": "Line Too Long",
        "category": TemplateCategory.STYLE.value,
        "title": "Line Exceeds Maximum Length",
        "message": "Line {line_number} has {actual_length} characters, exceeding the recommended {max_length} character limit.",
        "severity": "info",
        "tags": ["style", "line-length", "formatting"],
        "variables": ["line_number", "actual_length", "max_length"]
    },
    {
        "name": "Missing Blank Lines",
        "category": TemplateCategory.STYLE.value,
        "title": "Missing Blank Lines",
        "message": "Consider adding blank lines between functions and logical sections to improve readability.",
        "severity": "info",
        "tags": ["style", "spacing", "readability"],
        "variables": []
    },
    # Complexity Issues
    {
        "name": "High Cyclomatic Complexity",
        "category": TemplateCategory.COMPLEXITY.value,
        "title": "High Cyclomatic Complexity",
        "message": "The function '{function_name}' has a cyclomatic complexity of {complexity}. Consider simplifying the logic.",
        "severity": "warning",
        "tags": ["complexity", "cyclomatic", "refactoring"],
        "variables": ["function_name", "complexity"]
    },
    {
        "name": "Too Many Parameters",
        "category": TemplateCategory.COMPLEXITY.value,
        "title": "Too Many Function Parameters",
        "message": "The function '{function_name}' has {param_count} parameters. Consider using a configuration object or breaking it down.",
        "severity": "info",
        "tags": ["complexity", "parameters", "refactoring"],
        "variables": ["function_name", "param_count"]
    },
    {
        "name": "Complex Conditional",
        "category": TemplateCategory.COMPLEXITY.value,
        "title": "Complex Conditional Expression",
        "message": "The conditional on line {line_number} is complex. Consider extracting it into a well-named boolean variable or function.",
        "severity": "info",
        "tags": ["complexity", "conditional", "readability"],
        "variables": ["line_number"]
    },
]


# Security Issues
SECURITY_TEMPLATES = [
    {
        "name": "SQL Injection Risk",
        "category": TemplateCategory.SECURITY.value,
        "title": "Potential SQL Injection Vulnerability",
        "message": "Line {line_number} may be vulnerable to SQL injection. Use parameterized queries instead of string concatenation.",
        "severity": "error",
        "tags": ["security", "sql-injection", "vulnerability"],
        "variables": ["line_number"]
    },
    {
        "name": "Hardcoded Credentials",
        "category": TemplateCategory.SECURITY.value,
        "title": "Hardcoded Credentials Detected",
        "message": "Hardcoded credentials found on line {line_number}. Use environment variables or a secure configuration system.",
        "severity": "error",
        "tags": ["security", "credentials", "secrets"],
        "variables": ["line_number"]
    },
    {
        "name": "Unsafe Eval",
        "category": TemplateCategory.SECURITY.value,
        "title": "Unsafe Use of eval()",
        "message": "Using eval() on line {line_number} is dangerous. Consider using safer alternatives like ast.literal_eval().",
        "severity": "error",
        "tags": ["security", "eval", "code-execution"],
        "variables": ["line_number"]
    },
    {
        "name": "Missing Input Validation",
        "category": TemplateCategory.SECURITY.value,
        "title": "Missing Input Validation",
        "message": "User input on line {line_number} should be validated before use to prevent security vulnerabilities.",
        "severity": "warning",
        "tags": ["security", "validation", "input"],
        "variables": ["line_number"]
    },
]

# Encouragement Templates
ENCOURAGEMENT_TEMPLATES = [
    {
        "name": "Great Code Structure",
        "category": TemplateCategory.ENCOURAGEMENT.value,
        "title": "Excellent Code Structure!",
        "message": "Your code is well-organized with clear separation of concerns. Keep up the great work!",
        "severity": "info",
        "tags": ["encouragement", "positive", "structure"],
        "variables": []
    },
    {
        "name": "Good Naming",
        "category": TemplateCategory.ENCOURAGEMENT.value,
        "title": "Great Variable Naming!",
        "message": "Your variable and function names are descriptive and follow conventions. This makes your code easy to read!",
        "severity": "info",
        "tags": ["encouragement", "positive", "naming"],
        "variables": []
    },
    {
        "name": "Clean Code",
        "category": TemplateCategory.ENCOURAGEMENT.value,
        "title": "Clean and Readable Code!",
        "message": "Your code is clean, well-formatted, and easy to follow. Excellent attention to code quality!",
        "severity": "info",
        "tags": ["encouragement", "positive", "clean-code"],
        "variables": []
    },
    {
        "name": "Good Documentation",
        "category": TemplateCategory.ENCOURAGEMENT.value,
        "title": "Well Documented!",
        "message": "Great job documenting your code! Your comments and docstrings help others understand your work.",
        "severity": "info",
        "tags": ["encouragement", "positive", "documentation"],
        "variables": []
    },
    {
        "name": "Improvement Noticed",
        "category": TemplateCategory.ENCOURAGEMENT.value,
        "title": "Great Improvement!",
        "message": "You've made significant improvements since your last submission. Keep learning and growing!",
        "severity": "info",
        "tags": ["encouragement", "positive", "improvement"],
        "variables": []
    },
    {
        "name": "Good Error Handling",
        "category": TemplateCategory.ENCOURAGEMENT.value,
        "title": "Excellent Error Handling!",
        "message": "Your error handling is thorough and well-implemented. This makes your code more robust!",
        "severity": "info",
        "tags": ["encouragement", "positive", "error-handling"],
        "variables": []
    },
]

# Language-Specific Templates - Python
PYTHON_TEMPLATES = [
    {
        "name": "Python Type Hints",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "python",
        "title": "Consider Adding Type Hints",
        "message": "Adding type hints to '{function_name}' would improve code clarity and enable better IDE support.",
        "severity": "info",
        "tags": ["python", "type-hints", "best-practice"],
        "variables": ["function_name"]
    },
    {
        "name": "Python List Comprehension",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "python",
        "title": "Use List Comprehension",
        "message": "The loop on line {line_number} could be simplified using a list comprehension for more Pythonic code.",
        "severity": "info",
        "tags": ["python", "list-comprehension", "pythonic"],
        "variables": ["line_number"]
    },
    {
        "name": "Python F-String",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "python",
        "title": "Use F-String Formatting",
        "message": "Consider using f-strings instead of .format() or % formatting on line {line_number} for cleaner string interpolation.",
        "severity": "info",
        "tags": ["python", "f-string", "formatting"],
        "variables": ["line_number"]
    },
    {
        "name": "Python Context Manager",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "python",
        "title": "Use Context Manager",
        "message": "Consider using a 'with' statement for resource management on line {line_number} to ensure proper cleanup.",
        "severity": "warning",
        "tags": ["python", "context-manager", "resource-management"],
        "variables": ["line_number"]
    },
    {
        "name": "Python Generator Expression",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "python",
        "title": "Consider Generator Expression",
        "message": "The list comprehension on line {line_number} could be a generator expression for better memory efficiency.",
        "severity": "info",
        "tags": ["python", "generator", "memory"],
        "variables": ["line_number"]
    },
    {
        "name": "Python Enumerate",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "python",
        "title": "Use enumerate()",
        "message": "Instead of using range(len()) on line {line_number}, consider using enumerate() for cleaner iteration.",
        "severity": "info",
        "tags": ["python", "enumerate", "pythonic"],
        "variables": ["line_number"]
    },
    {
        "name": "Python Dict Get",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "python",
        "title": "Use dict.get()",
        "message": "Consider using dict.get('{key}', default) instead of checking if key exists to simplify your code.",
        "severity": "info",
        "tags": ["python", "dict", "best-practice"],
        "variables": ["key"]
    },
    {
        "name": "Python Walrus Operator",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "python",
        "title": "Consider Walrus Operator",
        "message": "The assignment and condition on line {line_number} could use the walrus operator (:=) for conciseness.",
        "severity": "info",
        "tags": ["python", "walrus", "python3.8"],
        "variables": ["line_number"]
    },
    {
        "name": "Python Dataclass",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "python",
        "title": "Consider Using Dataclass",
        "message": "The class '{class_name}' could be simplified using @dataclass decorator for automatic __init__ and __repr__.",
        "severity": "info",
        "tags": ["python", "dataclass", "simplification"],
        "variables": ["class_name"]
    },
    {
        "name": "Python Pathlib",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "python",
        "title": "Use pathlib Instead of os.path",
        "message": "Consider using pathlib.Path instead of os.path on line {line_number} for more readable path operations.",
        "severity": "info",
        "tags": ["python", "pathlib", "modern"],
        "variables": ["line_number"]
    },
]

# Language-Specific Templates - JavaScript/TypeScript
JAVASCRIPT_TEMPLATES = [
    {
        "name": "JavaScript Const",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "javascript",
        "title": "Use const Instead of let",
        "message": "The variable '{variable_name}' is never reassigned. Consider using 'const' instead of 'let'.",
        "severity": "info",
        "tags": ["javascript", "const", "best-practice"],
        "variables": ["variable_name"]
    },
    {
        "name": "JavaScript Arrow Function",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "javascript",
        "title": "Consider Arrow Function",
        "message": "The callback on line {line_number} could be written as an arrow function for cleaner syntax.",
        "severity": "info",
        "tags": ["javascript", "arrow-function", "es6"],
        "variables": ["line_number"]
    },
    {
        "name": "JavaScript Template Literal",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "javascript",
        "title": "Use Template Literals",
        "message": "Consider using template literals (`${{}}`) instead of string concatenation on line {line_number}.",
        "severity": "info",
        "tags": ["javascript", "template-literal", "es6"],
        "variables": ["line_number"]
    },
    {
        "name": "JavaScript Destructuring",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "javascript",
        "title": "Use Destructuring",
        "message": "Consider using destructuring assignment on line {line_number} for cleaner property access.",
        "severity": "info",
        "tags": ["javascript", "destructuring", "es6"],
        "variables": ["line_number"]
    },
    {
        "name": "JavaScript Optional Chaining",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "javascript",
        "title": "Use Optional Chaining",
        "message": "Consider using optional chaining (?.) on line {line_number} instead of multiple null checks.",
        "severity": "info",
        "tags": ["javascript", "optional-chaining", "es2020"],
        "variables": ["line_number"]
    },
    {
        "name": "JavaScript Nullish Coalescing",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "javascript",
        "title": "Use Nullish Coalescing",
        "message": "Consider using nullish coalescing (??) on line {line_number} instead of || for default values.",
        "severity": "info",
        "tags": ["javascript", "nullish-coalescing", "es2020"],
        "variables": ["line_number"]
    },
    {
        "name": "JavaScript Async Await",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "javascript",
        "title": "Consider async/await",
        "message": "The Promise chain on line {line_number} could be simplified using async/await syntax.",
        "severity": "info",
        "tags": ["javascript", "async-await", "promises"],
        "variables": ["line_number"]
    },
    {
        "name": "JavaScript Spread Operator",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "javascript",
        "title": "Use Spread Operator",
        "message": "Consider using the spread operator (...) on line {line_number} for array/object operations.",
        "severity": "info",
        "tags": ["javascript", "spread", "es6"],
        "variables": ["line_number"]
    },
    {
        "name": "TypeScript Interface",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "typescript",
        "title": "Define Interface",
        "message": "Consider defining an interface for the object type used in '{variable_name}' for better type safety.",
        "severity": "info",
        "tags": ["typescript", "interface", "type-safety"],
        "variables": ["variable_name"]
    },
    {
        "name": "TypeScript Strict Null",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "typescript",
        "title": "Handle Null/Undefined",
        "message": "The variable '{variable_name}' could be null/undefined. Add proper null checks or use non-null assertion.",
        "severity": "warning",
        "tags": ["typescript", "null-safety", "strict"],
        "variables": ["variable_name"]
    },
]

# Language-Specific Templates - Java
JAVA_TEMPLATES = [
    {
        "name": "Java Access Modifier",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "java",
        "title": "Consider Access Modifier",
        "message": "The field '{field_name}' should have an explicit access modifier. Consider making it private with getters/setters.",
        "severity": "info",
        "tags": ["java", "access-modifier", "encapsulation"],
        "variables": ["field_name"]
    },
    {
        "name": "Java Stream API",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "java",
        "title": "Consider Stream API",
        "message": "The loop on line {line_number} could be simplified using Java Stream API for more functional style.",
        "severity": "info",
        "tags": ["java", "stream", "functional"],
        "variables": ["line_number"]
    },
    {
        "name": "Java Optional",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "java",
        "title": "Use Optional",
        "message": "Consider using Optional<{type}> instead of returning null from '{method_name}' to avoid NullPointerException.",
        "severity": "info",
        "tags": ["java", "optional", "null-safety"],
        "variables": ["type", "method_name"]
    },
    {
        "name": "Java Try With Resources",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "java",
        "title": "Use Try-With-Resources",
        "message": "Consider using try-with-resources on line {line_number} for automatic resource management.",
        "severity": "warning",
        "tags": ["java", "try-with-resources", "resource-management"],
        "variables": ["line_number"]
    },
    {
        "name": "Java Lambda",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "java",
        "title": "Use Lambda Expression",
        "message": "The anonymous class on line {line_number} could be replaced with a lambda expression.",
        "severity": "info",
        "tags": ["java", "lambda", "java8"],
        "variables": ["line_number"]
    },
    {
        "name": "Java StringBuilder",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "java",
        "title": "Use StringBuilder",
        "message": "String concatenation in loop on line {line_number} should use StringBuilder for better performance.",
        "severity": "warning",
        "tags": ["java", "stringbuilder", "performance"],
        "variables": ["line_number"]
    },
    {
        "name": "Java Record",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "java",
        "title": "Consider Using Record",
        "message": "The class '{class_name}' could be simplified using Java record for immutable data carriers.",
        "severity": "info",
        "tags": ["java", "record", "java16"],
        "variables": ["class_name"]
    },
]

# Language-Specific Templates - C++
CPP_TEMPLATES = [
    {
        "name": "C++ Smart Pointer",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "cpp",
        "title": "Use Smart Pointers",
        "message": "Consider using std::unique_ptr or std::shared_ptr instead of raw pointer on line {line_number}.",
        "severity": "warning",
        "tags": ["cpp", "smart-pointer", "memory-safety"],
        "variables": ["line_number"]
    },
    {
        "name": "C++ Range-Based For",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "cpp",
        "title": "Use Range-Based For Loop",
        "message": "Consider using range-based for loop on line {line_number} for cleaner iteration.",
        "severity": "info",
        "tags": ["cpp", "range-for", "cpp11"],
        "variables": ["line_number"]
    },
    {
        "name": "C++ Auto Keyword",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "cpp",
        "title": "Consider Using auto",
        "message": "Consider using 'auto' keyword on line {line_number} for type inference with complex types.",
        "severity": "info",
        "tags": ["cpp", "auto", "cpp11"],
        "variables": ["line_number"]
    },
    {
        "name": "C++ Const Reference",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "cpp",
        "title": "Pass by Const Reference",
        "message": "Parameter '{param_name}' should be passed by const reference to avoid unnecessary copying.",
        "severity": "info",
        "tags": ["cpp", "const-reference", "performance"],
        "variables": ["param_name"]
    },
    {
        "name": "C++ RAII",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "cpp",
        "title": "Apply RAII Pattern",
        "message": "Consider using RAII pattern for resource management on line {line_number}.",
        "severity": "info",
        "tags": ["cpp", "raii", "resource-management"],
        "variables": ["line_number"]
    },
    {
        "name": "C++ Move Semantics",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "cpp",
        "title": "Consider Move Semantics",
        "message": "Consider using std::move on line {line_number} to avoid unnecessary copying.",
        "severity": "info",
        "tags": ["cpp", "move-semantics", "cpp11"],
        "variables": ["line_number"]
    },
    {
        "name": "C++ Nullptr",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "cpp",
        "title": "Use nullptr",
        "message": "Use 'nullptr' instead of 'NULL' or '0' on line {line_number} for type safety.",
        "severity": "info",
        "tags": ["cpp", "nullptr", "cpp11"],
        "variables": ["line_number"]
    },
]

# Combine language templates
LANGUAGE_TEMPLATES = PYTHON_TEMPLATES + JAVASCRIPT_TEMPLATES + JAVA_TEMPLATES + CPP_TEMPLATES

# Performance Templates
PERFORMANCE_TEMPLATES = [
    {
        "name": "Inefficient Loop",
        "category": TemplateCategory.PERFORMANCE.value,
        "title": "Inefficient Loop Pattern",
        "message": "The loop on line {line_number} could be optimized. Consider caching the length or using a more efficient iteration method.",
        "severity": "warning",
        "tags": ["performance", "loop", "optimization"],
        "variables": ["line_number"]
    },
    {
        "name": "Unnecessary Computation",
        "category": TemplateCategory.PERFORMANCE.value,
        "title": "Repeated Computation in Loop",
        "message": "The computation on line {line_number} is repeated in each iteration. Consider moving it outside the loop.",
        "severity": "warning",
        "tags": ["performance", "computation", "optimization"],
        "variables": ["line_number"]
    },
    {
        "name": "Memory Leak Risk",
        "category": TemplateCategory.PERFORMANCE.value,
        "title": "Potential Memory Leak",
        "message": "Resources allocated on line {line_number} may not be properly released. Ensure proper cleanup.",
        "severity": "error",
        "tags": ["performance", "memory", "leak"],
        "variables": ["line_number"]
    },
    {
        "name": "Large Data Structure",
        "category": TemplateCategory.PERFORMANCE.value,
        "title": "Large Data Structure in Memory",
        "message": "Loading all data into memory on line {line_number} may cause issues. Consider using streaming or pagination.",
        "severity": "warning",
        "tags": ["performance", "memory", "data-structure"],
        "variables": ["line_number"]
    },
    {
        "name": "Blocking Operation",
        "category": TemplateCategory.PERFORMANCE.value,
        "title": "Blocking I/O Operation",
        "message": "The I/O operation on line {line_number} is blocking. Consider using async/await for better performance.",
        "severity": "info",
        "tags": ["performance", "blocking", "async"],
        "variables": ["line_number"]
    },
    {
        "name": "Excessive Database Queries",
        "category": TemplateCategory.PERFORMANCE.value,
        "title": "N+1 Query Problem",
        "message": "Multiple database queries in loop on line {line_number}. Consider using batch queries or eager loading.",
        "severity": "warning",
        "tags": ["performance", "database", "n+1"],
        "variables": ["line_number"]
    },
    {
        "name": "Unoptimized Regex",
        "category": TemplateCategory.PERFORMANCE.value,
        "title": "Unoptimized Regular Expression",
        "message": "The regex on line {line_number} may be slow. Consider compiling it once or simplifying the pattern.",
        "severity": "info",
        "tags": ["performance", "regex", "optimization"],
        "variables": ["line_number"]
    },
    {
        "name": "Excessive Object Creation",
        "category": TemplateCategory.PERFORMANCE.value,
        "title": "Excessive Object Creation",
        "message": "Creating objects in loop on line {line_number} may impact performance. Consider object pooling or reuse.",
        "severity": "info",
        "tags": ["performance", "object", "memory"],
        "variables": ["line_number"]
    },
]

# Error Handling Templates
ERROR_HANDLING_TEMPLATES = [
    {
        "name": "Missing Error Handling",
        "category": TemplateCategory.ERROR_HANDLING.value,
        "title": "Missing Error Handling",
        "message": "The operation on line {line_number} may throw an exception. Consider adding try-catch block.",
        "severity": "warning",
        "tags": ["error-handling", "exception", "robustness"],
        "variables": ["line_number"]
    },
    {
        "name": "Empty Catch Block",
        "category": TemplateCategory.ERROR_HANDLING.value,
        "title": "Empty Catch Block",
        "message": "The catch block on line {line_number} is empty. At minimum, log the error for debugging.",
        "severity": "warning",
        "tags": ["error-handling", "catch", "logging"],
        "variables": ["line_number"]
    },
    {
        "name": "Generic Exception",
        "category": TemplateCategory.ERROR_HANDLING.value,
        "title": "Catching Generic Exception",
        "message": "Catching generic Exception on line {line_number}. Consider catching specific exception types.",
        "severity": "info",
        "tags": ["error-handling", "exception", "specific"],
        "variables": ["line_number"]
    },
    {
        "name": "Missing Finally",
        "category": TemplateCategory.ERROR_HANDLING.value,
        "title": "Missing Finally Block",
        "message": "Consider adding a finally block on line {line_number} to ensure cleanup code always runs.",
        "severity": "info",
        "tags": ["error-handling", "finally", "cleanup"],
        "variables": ["line_number"]
    },
    {
        "name": "Swallowed Exception",
        "category": TemplateCategory.ERROR_HANDLING.value,
        "title": "Exception Swallowed",
        "message": "The exception on line {line_number} is caught but not properly handled or re-thrown.",
        "severity": "warning",
        "tags": ["error-handling", "swallowed", "debugging"],
        "variables": ["line_number"]
    },
    {
        "name": "Missing Null Check",
        "category": TemplateCategory.ERROR_HANDLING.value,
        "title": "Missing Null Check",
        "message": "The variable '{variable_name}' could be null. Add a null check before using it.",
        "severity": "warning",
        "tags": ["error-handling", "null", "defensive"],
        "variables": ["variable_name"]
    },
    {
        "name": "Unchecked Return Value",
        "category": TemplateCategory.ERROR_HANDLING.value,
        "title": "Unchecked Return Value",
        "message": "The return value on line {line_number} is not checked. It may indicate an error condition.",
        "severity": "info",
        "tags": ["error-handling", "return-value", "checking"],
        "variables": ["line_number"]
    },
]

# Testing Templates
TESTING_TEMPLATES = [
    {
        "name": "Missing Test",
        "category": TemplateCategory.TESTING.value,
        "title": "Missing Unit Test",
        "message": "The function '{function_name}' lacks unit tests. Consider adding tests for edge cases.",
        "severity": "info",
        "tags": ["testing", "unit-test", "coverage"],
        "variables": ["function_name"]
    },
    {
        "name": "Test Assertion",
        "category": TemplateCategory.TESTING.value,
        "title": "Weak Test Assertion",
        "message": "The test on line {line_number} uses a weak assertion. Consider using more specific assertions.",
        "severity": "info",
        "tags": ["testing", "assertion", "quality"],
        "variables": ["line_number"]
    },
    {
        "name": "Test Coverage",
        "category": TemplateCategory.TESTING.value,
        "title": "Low Test Coverage",
        "message": "The function '{function_name}' has {coverage}% test coverage. Consider adding more test cases.",
        "severity": "info",
        "tags": ["testing", "coverage", "quality"],
        "variables": ["function_name", "coverage"]
    },
    {
        "name": "Test Isolation",
        "category": TemplateCategory.TESTING.value,
        "title": "Test Isolation Issue",
        "message": "The test on line {line_number} may have dependencies on other tests. Ensure test isolation.",
        "severity": "warning",
        "tags": ["testing", "isolation", "independence"],
        "variables": ["line_number"]
    },
    {
        "name": "Missing Edge Case",
        "category": TemplateCategory.TESTING.value,
        "title": "Missing Edge Case Test",
        "message": "Consider adding tests for edge cases like empty input, null values, or boundary conditions.",
        "severity": "info",
        "tags": ["testing", "edge-case", "boundary"],
        "variables": []
    },
]

# Algorithm Templates
ALGORITHM_TEMPLATES = [
    {
        "name": "Inefficient Algorithm",
        "category": TemplateCategory.ALGORITHM.value,
        "title": "Inefficient Algorithm",
        "message": "The algorithm on line {line_number} has O({complexity}) complexity. Consider a more efficient approach.",
        "severity": "warning",
        "tags": ["algorithm", "complexity", "optimization"],
        "variables": ["line_number", "complexity"]
    },
    {
        "name": "Sorting Suggestion",
        "category": TemplateCategory.ALGORITHM.value,
        "title": "Consider Sorting",
        "message": "Sorting the data first on line {line_number} could improve the overall algorithm efficiency.",
        "severity": "info",
        "tags": ["algorithm", "sorting", "optimization"],
        "variables": ["line_number"]
    },
    {
        "name": "Hash Map Suggestion",
        "category": TemplateCategory.ALGORITHM.value,
        "title": "Use Hash Map",
        "message": "Consider using a hash map on line {line_number} for O(1) lookup instead of linear search.",
        "severity": "info",
        "tags": ["algorithm", "hash-map", "lookup"],
        "variables": ["line_number"]
    },
    {
        "name": "Recursion Depth",
        "category": TemplateCategory.ALGORITHM.value,
        "title": "Deep Recursion Risk",
        "message": "The recursive function '{function_name}' may cause stack overflow. Consider iterative approach.",
        "severity": "warning",
        "tags": ["algorithm", "recursion", "stack"],
        "variables": ["function_name"]
    },
    {
        "name": "Binary Search",
        "category": TemplateCategory.ALGORITHM.value,
        "title": "Consider Binary Search",
        "message": "If the data is sorted, consider using binary search on line {line_number} for O(log n) lookup.",
        "severity": "info",
        "tags": ["algorithm", "binary-search", "optimization"],
        "variables": ["line_number"]
    },
]

# Tone Variants - Encouraging
ENCOURAGING_TONE_TEMPLATES = [
    {
        "name": "Encouraging Missing Docstring",
        "category": TemplateCategory.COMMON_ISSUES.value,
        "title": "Let's Add Documentation! 📝",
        "message": "Great function '{function_name}'! Adding a docstring would make it even better by helping others understand your code.",
        "severity": "info",
        "tags": ["documentation", "encouraging", "docstring"],
        "variables": ["function_name"],
        "tone": "encouraging"
    },
    {
        "name": "Encouraging Complexity",
        "category": TemplateCategory.COMPLEXITY.value,
        "title": "Simplification Opportunity! 🎯",
        "message": "You've tackled a complex problem in '{function_name}'! Consider breaking it into smaller functions for even cleaner code.",
        "severity": "info",
        "tags": ["complexity", "encouraging", "refactoring"],
        "variables": ["function_name"],
        "tone": "encouraging"
    },
    {
        "name": "Encouraging Error Handling",
        "category": TemplateCategory.ERROR_HANDLING.value,
        "title": "Almost There! 💪",
        "message": "Your code is working well! Adding error handling on line {line_number} will make it production-ready.",
        "severity": "info",
        "tags": ["error-handling", "encouraging", "robustness"],
        "variables": ["line_number"],
        "tone": "encouraging"
    },
    {
        "name": "Encouraging Performance",
        "category": TemplateCategory.PERFORMANCE.value,
        "title": "Optimization Opportunity! 🚀",
        "message": "Your solution works! Here's a tip: optimizing line {line_number} could make it even faster.",
        "severity": "info",
        "tags": ["performance", "encouraging", "optimization"],
        "variables": ["line_number"],
        "tone": "encouraging"
    },
]

# Tone Variants - Strict/Professional
STRICT_TONE_TEMPLATES = [
    {
        "name": "Strict Missing Docstring",
        "category": TemplateCategory.COMMON_ISSUES.value,
        "title": "Documentation Required",
        "message": "Function '{function_name}' must have a docstring. This is a mandatory coding standard.",
        "severity": "warning",
        "tags": ["documentation", "strict", "docstring"],
        "variables": ["function_name"],
        "tone": "strict"
    },
    {
        "name": "Strict Complexity",
        "category": TemplateCategory.COMPLEXITY.value,
        "title": "Complexity Violation",
        "message": "Function '{function_name}' exceeds complexity threshold. Refactoring is required before merge.",
        "severity": "error",
        "tags": ["complexity", "strict", "refactoring"],
        "variables": ["function_name"],
        "tone": "strict"
    },
    {
        "name": "Strict Error Handling",
        "category": TemplateCategory.ERROR_HANDLING.value,
        "title": "Error Handling Required",
        "message": "Line {line_number} lacks proper error handling. This must be addressed before deployment.",
        "severity": "error",
        "tags": ["error-handling", "strict", "robustness"],
        "variables": ["line_number"],
        "tone": "strict"
    },
    {
        "name": "Strict Security",
        "category": TemplateCategory.SECURITY.value,
        "title": "Security Violation",
        "message": "Critical security issue on line {line_number}. This code cannot be deployed until fixed.",
        "severity": "error",
        "tags": ["security", "strict", "critical"],
        "variables": ["line_number"],
        "tone": "strict"
    },
]

# Chinese Templates (中文模板)
CHINESE_TEMPLATES = [
    {
        "name": "缺少文档字符串",
        "category": TemplateCategory.COMMON_ISSUES.value,
        "title": "缺少文档说明",
        "message": "函数 '{function_name}' 缺少文档字符串。添加文档可以帮助他人理解您的代码功能和使用方法。",
        "severity": "info",
        "tags": ["documentation", "docstring", "chinese"],
        "variables": ["function_name"],
        "locale": "zh-CN"
    },
    {
        "name": "未使用的变量",
        "category": TemplateCategory.COMMON_ISSUES.value,
        "title": "检测到未使用的变量",
        "message": "变量 '{variable_name}' 已定义但从未使用。请考虑删除它或在代码中使用它。",
        "severity": "warning",
        "tags": ["unused", "variable", "chinese"],
        "variables": ["variable_name"],
        "locale": "zh-CN"
    },
    {
        "name": "魔法数字",
        "category": TemplateCategory.COMMON_ISSUES.value,
        "title": "发现魔法数字",
        "message": "值 '{value}' 似乎是一个魔法数字。请考虑将其定义为命名常量以提高可读性。",
        "severity": "info",
        "tags": ["magic-number", "constant", "chinese"],
        "variables": ["value"],
        "locale": "zh-CN"
    },
    {
        "name": "函数过长",
        "category": TemplateCategory.COMMON_ISSUES.value,
        "title": "函数过长",
        "message": "函数 '{function_name}' 有 {line_count} 行代码。请考虑将其拆分为更小、更专注的函数。",
        "severity": "warning",
        "tags": ["complexity", "refactoring", "chinese"],
        "variables": ["function_name", "line_count"],
        "locale": "zh-CN"
    },
    {
        "name": "嵌套过深",
        "category": TemplateCategory.COMMON_ISSUES.value,
        "title": "检测到深层嵌套",
        "message": "您的代码有 {nesting_level} 层嵌套。请考虑使用提前返回或提取逻辑来降低复杂度。",
        "severity": "warning",
        "tags": ["nesting", "complexity", "chinese"],
        "variables": ["nesting_level"],
        "locale": "zh-CN"
    },
    {
        "name": "高圈复杂度",
        "category": TemplateCategory.COMPLEXITY.value,
        "title": "圈复杂度过高",
        "message": "函数 '{function_name}' 的圈复杂度为 {complexity}。请考虑简化逻辑。",
        "severity": "warning",
        "tags": ["complexity", "cyclomatic", "chinese"],
        "variables": ["function_name", "complexity"],
        "locale": "zh-CN"
    },
    {
        "name": "SQL注入风险",
        "category": TemplateCategory.SECURITY.value,
        "title": "潜在的SQL注入漏洞",
        "message": "第 {line_number} 行可能存在SQL注入漏洞。请使用参数化查询而不是字符串拼接。",
        "severity": "error",
        "tags": ["security", "sql-injection", "chinese"],
        "variables": ["line_number"],
        "locale": "zh-CN"
    },
    {
        "name": "硬编码凭证",
        "category": TemplateCategory.SECURITY.value,
        "title": "检测到硬编码凭证",
        "message": "在第 {line_number} 行发现硬编码凭证。请使用环境变量或安全的配置系统。",
        "severity": "error",
        "tags": ["security", "credentials", "chinese"],
        "variables": ["line_number"],
        "locale": "zh-CN"
    },
    {
        "name": "优秀的代码结构",
        "category": TemplateCategory.ENCOURAGEMENT.value,
        "title": "代码结构优秀！",
        "message": "您的代码组织良好，关注点分离清晰。继续保持！",
        "severity": "info",
        "tags": ["encouragement", "positive", "chinese"],
        "variables": [],
        "locale": "zh-CN"
    },
    {
        "name": "明显进步",
        "category": TemplateCategory.ENCOURAGEMENT.value,
        "title": "进步明显！",
        "message": "与上次提交相比，您有了显著的进步。继续学习和成长！",
        "severity": "info",
        "tags": ["encouragement", "improvement", "chinese"],
        "variables": [],
        "locale": "zh-CN"
    },
    {
        "name": "性能优化建议",
        "category": TemplateCategory.PERFORMANCE.value,
        "title": "性能优化建议",
        "message": "第 {line_number} 行的循环可以优化。考虑缓存长度或使用更高效的迭代方法。",
        "severity": "warning",
        "tags": ["performance", "loop", "chinese"],
        "variables": ["line_number"],
        "locale": "zh-CN"
    },
    {
        "name": "缺少错误处理",
        "category": TemplateCategory.ERROR_HANDLING.value,
        "title": "缺少错误处理",
        "message": "第 {line_number} 行的操作可能抛出异常。请考虑添加 try-catch 块。",
        "severity": "warning",
        "tags": ["error-handling", "exception", "chinese"],
        "variables": ["line_number"],
        "locale": "zh-CN"
    },
]

# Combine all templates
ALL_TEMPLATES = (
    DEFAULT_TEMPLATES +
    SECURITY_TEMPLATES +
    ENCOURAGEMENT_TEMPLATES +
    LANGUAGE_TEMPLATES +
    PERFORMANCE_TEMPLATES +
    ERROR_HANDLING_TEMPLATES +
    TESTING_TEMPLATES +
    ALGORITHM_TEMPLATES +
    ENCOURAGING_TONE_TEMPLATES +
    STRICT_TONE_TEMPLATES +
    CHINESE_TEMPLATES
)


async def seed_templates():
    """Seed the database with default feedback templates."""
    async with AsyncSessionLocal() as session:
        # Check if templates already exist
        result = await session.execute(select(FeedbackTemplate).limit(1))
        if result.scalar_one_or_none():
            print("Templates already exist. Skipping seed.")
            return

        # Create templates
        for template_data in ALL_TEMPLATES:
            template = FeedbackTemplate(
                name=template_data["name"],
                category=template_data["category"],
                language=template_data.get("language"),
                title=template_data["title"],
                message=template_data["message"],
                severity=template_data["severity"],
                tags=template_data.get("tags", []),
                variables=template_data.get("variables", []),
                tone=template_data.get("tone", "neutral"),
                locale=template_data.get("locale", "en"),
                is_active=True
            )
            session.add(template)

        await session.commit()
        print(f"Successfully seeded {len(ALL_TEMPLATES)} feedback templates.")


async def main():
    """Main entry point."""
    # Create tables if they don't exist
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await seed_templates()


if __name__ == "__main__":
    asyncio.run(main())
