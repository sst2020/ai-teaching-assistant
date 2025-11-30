"""
File Parsing Service - Parses code files and extracts structure and metrics.

Supports multiple programming languages:
- Python (.py)
- Java (.java)
- JavaScript (.js, .jsx)
- TypeScript (.ts, .tsx)
- C (.c)
- C++ (.cpp)
"""
import ast
import re
import uuid
import logging
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
from dataclasses import dataclass

from schemas.file_upload import (
    ProgrammingLanguage, FileParseResult, CodeStructure,
    ImportInfo, FunctionInfo, ClassInfo, BasicMetrics, SyntaxValidation
)

logger = logging.getLogger(__name__)


# Extension to language mapping
EXTENSION_LANGUAGE_MAP: Dict[str, ProgrammingLanguage] = {
    ".py": ProgrammingLanguage.PYTHON,
    ".java": ProgrammingLanguage.JAVA,
    ".js": ProgrammingLanguage.JAVASCRIPT,
    ".jsx": ProgrammingLanguage.JSX,
    ".ts": ProgrammingLanguage.TYPESCRIPT,
    ".tsx": ProgrammingLanguage.TSX,
    ".c": ProgrammingLanguage.C,
    ".cpp": ProgrammingLanguage.CPP,
    ".cc": ProgrammingLanguage.CPP,
    ".cxx": ProgrammingLanguage.CPP,
    ".h": ProgrammingLanguage.C,
    ".hpp": ProgrammingLanguage.CPP,
}


@dataclass
class ParserConfig:
    """Configuration for file parsing."""
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    max_line_length: int = 1000
    extract_docstrings: bool = True


class FileParsingService:
    """Service for parsing code files and extracting structure."""

    def __init__(self, config: Optional[ParserConfig] = None):
        self.config = config or ParserConfig()

    def detect_language(self, extension: str) -> ProgrammingLanguage:
        """Detect programming language from file extension."""
        ext = extension.lower() if extension.startswith('.') else f'.{extension.lower()}'
        return EXTENSION_LANGUAGE_MAP.get(ext, ProgrammingLanguage.UNKNOWN)

    async def parse_file(
        self,
        content: str,
        extension: str,
        file_id: Optional[str] = None
    ) -> FileParseResult:
        """Parse a code file and extract structure and metrics."""
        file_id = file_id or str(uuid.uuid4())
        language = self.detect_language(extension)
        
        # Get basic metrics
        metrics = self._calculate_metrics(content, language)
        
        # Validate syntax
        syntax_validation = self._validate_syntax(content, language)
        
        # Extract code structure
        structure = self._extract_structure(content, language)
        
        # Update metrics with structure counts
        metrics.function_count = len(structure.functions) + sum(
            len(c.methods) for c in structure.classes
        )
        metrics.class_count = len(structure.classes)
        metrics.import_count = len(structure.imports)
        
        return FileParseResult(
            file_id=file_id,
            language=language,
            structure=structure,
            metrics=metrics,
            syntax_validation=syntax_validation,
            parsed_at=datetime.utcnow()
        )

    def _calculate_metrics(self, content: str, language: ProgrammingLanguage) -> BasicMetrics:
        """Calculate basic code metrics."""
        lines = content.split('\n')
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        
        # Count comment lines based on language
        comment_lines = self._count_comment_lines(content, language)
        code_lines = total_lines - blank_lines - comment_lines
        
        return BasicMetrics(
            total_lines=total_lines,
            code_lines=max(0, code_lines),
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            function_count=0,  # Will be updated after structure extraction
            class_count=0,
            import_count=0
        )

    def _count_comment_lines(self, content: str, language: ProgrammingLanguage) -> int:
        """Count comment lines based on language."""
        lines = content.split('\n')
        comment_count = 0
        in_multiline = False
        
        for line in lines:
            stripped = line.strip()
            
            if language == ProgrammingLanguage.PYTHON:
                # Python single-line comments
                if stripped.startswith('#'):
                    comment_count += 1
                # Python docstrings (simplified detection)
                elif '"""' in stripped or "'''" in stripped:
                    comment_count += 1
            elif language in (ProgrammingLanguage.JAVA, ProgrammingLanguage.JAVASCRIPT,
                            ProgrammingLanguage.TYPESCRIPT, ProgrammingLanguage.C,
                            ProgrammingLanguage.CPP, ProgrammingLanguage.JSX,
                            ProgrammingLanguage.TSX):
                # C-style comments
                if in_multiline:
                    comment_count += 1
                    if '*/' in stripped:
                        in_multiline = False
                elif stripped.startswith('//'):
                    comment_count += 1
                elif stripped.startswith('/*'):
                    comment_count += 1
                    if '*/' not in stripped:
                        in_multiline = True
        
        return comment_count

    def _validate_syntax(self, content: str, language: ProgrammingLanguage) -> SyntaxValidation:
        """Validate syntax based on language."""
        if language == ProgrammingLanguage.PYTHON:
            return self._validate_python_syntax(content)
        elif language in (ProgrammingLanguage.JAVASCRIPT, ProgrammingLanguage.JSX):
            return self._validate_js_syntax(content)
        elif language in (ProgrammingLanguage.TYPESCRIPT, ProgrammingLanguage.TSX):
            return self._validate_ts_syntax(content)
        elif language == ProgrammingLanguage.JAVA:
            return self._validate_java_syntax(content)
        elif language in (ProgrammingLanguage.C, ProgrammingLanguage.CPP):
            return self._validate_c_syntax(content)
        else:
            return SyntaxValidation(is_valid=True, errors=[], error_line=None)

    def _validate_python_syntax(self, content: str) -> SyntaxValidation:
        """Validate Python syntax using AST."""
        try:
            ast.parse(content)
            return SyntaxValidation(is_valid=True, errors=[], error_line=None)
        except SyntaxError as e:
            return SyntaxValidation(
                is_valid=False,
                errors=[f"SyntaxError: {e.msg}"],
                error_line=e.lineno
            )
        except Exception as e:
            return SyntaxValidation(
                is_valid=False,
                errors=[f"ParseError: {str(e)}"],
                error_line=None
            )

    def _validate_js_syntax(self, content: str) -> SyntaxValidation:
        """Basic JavaScript syntax validation using regex patterns."""
        errors = []
        error_line = None

        # Check for common syntax issues
        lines = content.split('\n')
        brace_count = 0
        paren_count = 0
        bracket_count = 0

        for i, line in enumerate(lines, 1):
            # Skip comments
            stripped = line.strip()
            if stripped.startswith('//'):
                continue

            brace_count += line.count('{') - line.count('}')
            paren_count += line.count('(') - line.count(')')
            bracket_count += line.count('[') - line.count(']')

        if brace_count != 0:
            errors.append(f"Unbalanced braces: {'+' if brace_count > 0 else ''}{brace_count}")
        if paren_count != 0:
            errors.append(f"Unbalanced parentheses: {'+' if paren_count > 0 else ''}{paren_count}")
        if bracket_count != 0:
            errors.append(f"Unbalanced brackets: {'+' if bracket_count > 0 else ''}{bracket_count}")

        return SyntaxValidation(
            is_valid=len(errors) == 0,
            errors=errors,
            error_line=error_line
        )

    def _validate_ts_syntax(self, content: str) -> SyntaxValidation:
        """Basic TypeScript syntax validation (same as JS for now)."""
        return self._validate_js_syntax(content)

    def _validate_java_syntax(self, content: str) -> SyntaxValidation:
        """Basic Java syntax validation."""
        errors = []

        # Check for balanced braces
        brace_count = content.count('{') - content.count('}')
        if brace_count != 0:
            errors.append(f"Unbalanced braces: {'+' if brace_count > 0 else ''}{brace_count}")

        # Check for class declaration
        if not re.search(r'\b(class|interface|enum)\s+\w+', content):
            errors.append("No class, interface, or enum declaration found")

        return SyntaxValidation(
            is_valid=len(errors) == 0,
            errors=errors,
            error_line=None
        )

    def _validate_c_syntax(self, content: str) -> SyntaxValidation:
        """Basic C/C++ syntax validation."""
        errors = []

        # Check for balanced braces
        brace_count = content.count('{') - content.count('}')
        if brace_count != 0:
            errors.append(f"Unbalanced braces: {'+' if brace_count > 0 else ''}{brace_count}")

        # Check for semicolons after statements (basic check)
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Skip preprocessor directives, comments, and control structures
            if (stripped and not stripped.startswith('#') and
                not stripped.startswith('//') and
                not stripped.endswith('{') and
                not stripped.endswith('}') and
                not stripped.startswith('/*') and
                not stripped.endswith('*/') and
                not any(stripped.startswith(kw) for kw in ['if', 'else', 'for', 'while', 'switch', 'case', 'default'])):
                # This is a simplified check
                pass

        return SyntaxValidation(
            is_valid=len(errors) == 0,
            errors=errors,
            error_line=None
        )

    def _extract_structure(self, content: str, language: ProgrammingLanguage) -> CodeStructure:
        """Extract code structure based on language."""
        if language == ProgrammingLanguage.PYTHON:
            return self._extract_python_structure(content)
        elif language in (ProgrammingLanguage.JAVASCRIPT, ProgrammingLanguage.JSX):
            return self._extract_js_structure(content)
        elif language in (ProgrammingLanguage.TYPESCRIPT, ProgrammingLanguage.TSX):
            return self._extract_ts_structure(content)
        elif language == ProgrammingLanguage.JAVA:
            return self._extract_java_structure(content)
        elif language in (ProgrammingLanguage.C, ProgrammingLanguage.CPP):
            return self._extract_c_structure(content)
        else:
            return CodeStructure(imports=[], functions=[], classes=[], global_variables=[])

    def _extract_python_structure(self, content: str) -> CodeStructure:
        """Extract structure from Python code using AST."""
        imports = []
        functions = []
        classes = []
        global_variables = []

        try:
            tree = ast.parse(content)

            for node in ast.iter_child_nodes(tree):
                # Extract imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(ImportInfo(
                            module=alias.name,
                            names=[alias.asname or alias.name],
                            line=node.lineno,
                            is_from_import=False
                        ))
                elif isinstance(node, ast.ImportFrom):
                    imports.append(ImportInfo(
                        module=node.module or '',
                        names=[alias.name for alias in node.names],
                        line=node.lineno,
                        is_from_import=True
                    ))

                # Extract functions
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    func_info = self._extract_python_function(node)
                    functions.append(func_info)

                # Extract classes
                elif isinstance(node, ast.ClassDef):
                    class_info = self._extract_python_class(node)
                    classes.append(class_info)

                # Extract global variables
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            global_variables.append(target.id)
                elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                    global_variables.append(node.target.id)

        except SyntaxError:
            logger.warning("Could not parse Python file for structure extraction")
        except Exception as e:
            logger.error(f"Error extracting Python structure: {e}")

        return CodeStructure(
            imports=imports,
            functions=functions,
            classes=classes,
            global_variables=global_variables
        )

    def _extract_python_function(self, node: ast.FunctionDef) -> FunctionInfo:
        """Extract function info from Python AST node."""
        # Get parameters
        params = []
        for arg in node.args.args:
            params.append(arg.arg)

        # Get return type annotation
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)

        # Get docstring
        docstring = ast.get_docstring(node)

        # Get decorators
        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(f"{dec.value.id}.{dec.attr}" if isinstance(dec.value, ast.Name) else dec.attr)
            elif isinstance(dec, ast.Call):
                if isinstance(dec.func, ast.Name):
                    decorators.append(dec.func.id)

        return FunctionInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', None),
            parameters=params,
            return_type=return_type,
            docstring=docstring[:200] if docstring else None,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            decorators=decorators
        )

    def _extract_python_class(self, node: ast.ClassDef) -> ClassInfo:
        """Extract class info from Python AST node."""
        # Get base classes
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(f"{base.value.id}.{base.attr}" if isinstance(base.value, ast.Name) else base.attr)

        # Get methods
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._extract_python_function(item))

        # Get docstring
        docstring = ast.get_docstring(node)

        # Get decorators
        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)

        return ClassInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=getattr(node, 'end_lineno', None),
            base_classes=base_classes,
            methods=methods,
            docstring=docstring[:200] if docstring else None,
            decorators=decorators
        )

    def _extract_js_structure(self, content: str) -> CodeStructure:
        """Extract structure from JavaScript code using regex patterns."""
        imports = []
        functions = []
        classes = []
        global_variables = []

        lines = content.split('\n')

        # Extract imports
        import_patterns = [
            r"import\s+(?:(\w+)(?:\s*,\s*)?)?(?:\{([^}]+)\})?\s+from\s+['\"]([^'\"]+)['\"]",
            r"import\s+['\"]([^'\"]+)['\"]",
            r"const\s+(\w+)\s*=\s*require\(['\"]([^'\"]+)['\"]\)",
        ]

        for i, line in enumerate(lines, 1):
            for pattern in import_patterns:
                match = re.search(pattern, line)
                if match:
                    groups = match.groups()
                    if len(groups) >= 3:
                        names = []
                        if groups[0]:
                            names.append(groups[0])
                        if groups[1]:
                            names.extend([n.strip() for n in groups[1].split(',')])
                        imports.append(ImportInfo(
                            module=groups[2],
                            names=names,
                            line=i,
                            is_from_import=True
                        ))
                    break

        # Extract functions
        func_patterns = [
            r"(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)",
            r"(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>",
            r"(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function",
        ]

        for i, line in enumerate(lines, 1):
            for pattern in func_patterns:
                match = re.search(pattern, line)
                if match:
                    name = match.group(1)
                    params = match.group(2).split(',') if len(match.groups()) > 1 and match.group(2) else []
                    functions.append(FunctionInfo(
                        name=name,
                        line_start=i,
                        line_end=None,
                        parameters=[p.strip().split(':')[0].strip() for p in params if p.strip()],
                        return_type=None,
                        docstring=None,
                        is_async='async' in line,
                        decorators=[]
                    ))
                    break

        # Extract classes
        class_pattern = r"class\s+(\w+)(?:\s+extends\s+(\w+))?"
        for i, line in enumerate(lines, 1):
            match = re.search(class_pattern, line)
            if match:
                classes.append(ClassInfo(
                    name=match.group(1),
                    line_start=i,
                    line_end=None,
                    base_classes=[match.group(2)] if match.group(2) else [],
                    methods=[],
                    docstring=None,
                    decorators=[]
                ))

        # Extract global variables
        var_pattern = r"(?:const|let|var)\s+(\w+)\s*="
        for i, line in enumerate(lines, 1):
            # Skip if it's a function declaration
            if 'function' in line or '=>' in line:
                continue
            match = re.search(var_pattern, line)
            if match:
                global_variables.append(match.group(1))

        return CodeStructure(
            imports=imports,
            functions=functions,
            classes=classes,
            global_variables=global_variables[:50]  # Limit to avoid too many
        )

    def _extract_ts_structure(self, content: str) -> CodeStructure:
        """Extract structure from TypeScript code (extends JS extraction)."""
        # Use JS extraction as base
        structure = self._extract_js_structure(content)

        # Additional TypeScript-specific patterns
        lines = content.split('\n')

        # Extract interfaces as classes
        interface_pattern = r"interface\s+(\w+)(?:\s+extends\s+([^{]+))?"
        for i, line in enumerate(lines, 1):
            match = re.search(interface_pattern, line)
            if match:
                extends = match.group(2).split(',') if match.group(2) else []
                structure.classes.append(ClassInfo(
                    name=match.group(1),
                    line_start=i,
                    line_end=None,
                    base_classes=[e.strip() for e in extends],
                    methods=[],
                    docstring=None,
                    decorators=[]
                ))

        # Extract type aliases as global variables
        type_pattern = r"type\s+(\w+)\s*="
        for i, line in enumerate(lines, 1):
            match = re.search(type_pattern, line)
            if match:
                structure.global_variables.append(match.group(1))

        return structure

    def _extract_java_structure(self, content: str) -> CodeStructure:
        """Extract structure from Java code using regex patterns."""
        imports = []
        functions = []
        classes = []

        lines = content.split('\n')

        # Extract imports
        import_pattern = r"import\s+(?:static\s+)?([a-zA-Z0-9_.]+(?:\.\*)?)\s*;"
        for i, line in enumerate(lines, 1):
            match = re.search(import_pattern, line)
            if match:
                module = match.group(1)
                imports.append(ImportInfo(
                    module=module,
                    names=[module.split('.')[-1]],
                    line=i,
                    is_from_import=False
                ))

        # Extract classes
        class_pattern = r"(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?"
        for i, line in enumerate(lines, 1):
            match = re.search(class_pattern, line)
            if match:
                base_classes = []
                if match.group(2):
                    base_classes.append(match.group(2))
                if match.group(3):
                    base_classes.extend([c.strip() for c in match.group(3).split(',')])
                classes.append(ClassInfo(
                    name=match.group(1),
                    line_start=i,
                    line_end=None,
                    base_classes=base_classes,
                    methods=[],
                    docstring=None,
                    decorators=[]
                ))

        # Extract methods
        method_pattern = r"(?:public|private|protected)?\s*(?:static)?\s*(?:final)?\s*(?:synchronized)?\s*(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)"
        for i, line in enumerate(lines, 1):
            # Skip class declarations
            if 'class ' in line:
                continue
            match = re.search(method_pattern, line)
            if match:
                return_type = match.group(1)
                name = match.group(2)
                params = match.group(3)
                # Skip constructors (return type same as class name)
                if return_type not in ['if', 'for', 'while', 'switch', 'catch']:
                    functions.append(FunctionInfo(
                        name=name,
                        line_start=i,
                        line_end=None,
                        parameters=[p.strip().split()[-1] for p in params.split(',') if p.strip()],
                        return_type=return_type,
                        docstring=None,
                        is_async=False,
                        decorators=[]
                    ))

        return CodeStructure(
            imports=imports,
            functions=functions,
            classes=classes,
            global_variables=[]
        )

    def _extract_c_structure(self, content: str) -> CodeStructure:
        """Extract structure from C/C++ code using regex patterns."""
        imports = []
        functions = []
        classes = []
        global_variables = []

        lines = content.split('\n')

        # Extract includes
        include_pattern = r'#include\s*[<"]([^>"]+)[>"]'
        for i, line in enumerate(lines, 1):
            match = re.search(include_pattern, line)
            if match:
                imports.append(ImportInfo(
                    module=match.group(1),
                    names=[match.group(1).split('/')[-1].split('.')[0]],
                    line=i,
                    is_from_import=False
                ))

        # Extract functions (simplified pattern)
        func_pattern = r"^(?!.*\b(?:if|for|while|switch)\b)(\w+(?:\s*\*)?)\s+(\w+)\s*\(([^)]*)\)\s*(?:\{|$)"
        for i, line in enumerate(lines, 1):
            match = re.search(func_pattern, line.strip())
            if match:
                return_type = match.group(1)
                name = match.group(2)
                params = match.group(3)
                if return_type not in ['return', 'if', 'for', 'while', 'switch']:
                    functions.append(FunctionInfo(
                        name=name,
                        line_start=i,
                        line_end=None,
                        parameters=[p.strip().split()[-1].replace('*', '') for p in params.split(',') if p.strip()],
                        return_type=return_type,
                        docstring=None,
                        is_async=False,
                        decorators=[]
                    ))

        # Extract C++ classes
        class_pattern = r"class\s+(\w+)(?:\s*:\s*(?:public|private|protected)\s+(\w+))?"
        for i, line in enumerate(lines, 1):
            match = re.search(class_pattern, line)
            if match:
                classes.append(ClassInfo(
                    name=match.group(1),
                    line_start=i,
                    line_end=None,
                    base_classes=[match.group(2)] if match.group(2) else [],
                    methods=[],
                    docstring=None,
                    decorators=[]
                ))

        # Extract structs as classes
        struct_pattern = r"struct\s+(\w+)"
        for i, line in enumerate(lines, 1):
            match = re.search(struct_pattern, line)
            if match:
                classes.append(ClassInfo(
                    name=match.group(1),
                    line_start=i,
                    line_end=None,
                    base_classes=[],
                    methods=[],
                    docstring=None,
                    decorators=[]
                ))

        return CodeStructure(
            imports=imports,
            functions=functions,
            classes=classes,
            global_variables=global_variables
        )


# Create singleton instance
file_parsing_service = FileParsingService()

