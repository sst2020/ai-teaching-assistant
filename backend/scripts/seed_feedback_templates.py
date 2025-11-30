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
from core.database import async_session_maker, engine, Base
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

# Language-Specific Templates
LANGUAGE_TEMPLATES = [
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
        "name": "Java Access Modifier",
        "category": TemplateCategory.LANGUAGE_SPECIFIC.value,
        "language": "java",
        "title": "Consider Access Modifier",
        "message": "The field '{field_name}' should have an explicit access modifier. Consider making it private with getters/setters.",
        "severity": "info",
        "tags": ["java", "access-modifier", "encapsulation"],
        "variables": ["field_name"]
    },
]

# Combine all templates
ALL_TEMPLATES = DEFAULT_TEMPLATES + SECURITY_TEMPLATES + ENCOURAGEMENT_TEMPLATES + LANGUAGE_TEMPLATES


async def seed_templates():
    """Seed the database with default feedback templates."""
    async with async_session_maker() as session:
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
                is_active=True
            )
            session.add(template)

        await session.commit()
        print(f"Successfully seeded {len(ALL_TEMPLATES)} feedback templates.")


async def main():
    """Main entry point."""
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await seed_templates()


if __name__ == "__main__":
    asyncio.run(main())
