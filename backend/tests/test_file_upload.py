"""
Tests for File Upload and Parsing Functionality
"""
import pytest
import asyncio
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.file_parsing_service import file_parsing_service
from schemas.file_upload import ProgrammingLanguage


# Sample code for testing
PYTHON_CODE = '''
import os
from typing import List, Optional

def hello_world(name: str) -> str:
    """Greet someone."""
    return f"Hello, {name}!"

class Calculator:
    """A simple calculator."""
    def add(self, a: int, b: int) -> int:
        return a + b
    
    def subtract(self, a: int, b: int) -> int:
        return a - b

PI = 3.14159
'''

JAVASCRIPT_CODE = '''
import React from 'react';
import { useState } from 'react';

const greeting = "Hello";

function sayHello(name) {
    return `Hello, ${name}!`;
}

class Calculator {
    add(a, b) {
        return a + b;
    }
}

export default Calculator;
'''

JAVA_CODE = '''
import java.util.List;
import java.util.ArrayList;

public class Calculator {
    private int value;
    
    public int add(int a, int b) {
        return a + b;
    }
    
    public int subtract(int a, int b) {
        return a - b;
    }
}
'''

C_CODE = '''
#include <stdio.h>
#include <stdlib.h>

int add(int a, int b) {
    return a + b;
}

int main() {
    printf("Hello, World!");
    return 0;
}
'''


class TestFileParsingService:
    """Test cases for file parsing service."""
    
    @pytest.mark.asyncio
    async def test_detect_language_python(self):
        """Test language detection for Python files."""
        lang = file_parsing_service.detect_language(".py")
        assert lang == ProgrammingLanguage.PYTHON
    
    @pytest.mark.asyncio
    async def test_detect_language_javascript(self):
        """Test language detection for JavaScript files."""
        lang = file_parsing_service.detect_language(".js")
        assert lang == ProgrammingLanguage.JAVASCRIPT
        
        lang = file_parsing_service.detect_language(".jsx")
        assert lang == ProgrammingLanguage.JSX
    
    @pytest.mark.asyncio
    async def test_detect_language_java(self):
        """Test language detection for Java files."""
        lang = file_parsing_service.detect_language(".java")
        assert lang == ProgrammingLanguage.JAVA
    
    @pytest.mark.asyncio
    async def test_detect_language_c_cpp(self):
        """Test language detection for C/C++ files."""
        assert file_parsing_service.detect_language(".c") == ProgrammingLanguage.C
        assert file_parsing_service.detect_language(".cpp") == ProgrammingLanguage.CPP
        assert file_parsing_service.detect_language(".h") == ProgrammingLanguage.C
        assert file_parsing_service.detect_language(".hpp") == ProgrammingLanguage.CPP
    
    @pytest.mark.asyncio
    async def test_parse_python_file(self):
        """Test parsing Python code."""
        result = await file_parsing_service.parse_file(PYTHON_CODE, ".py", "test-py-001")
        
        assert result.language == ProgrammingLanguage.PYTHON
        assert result.syntax_validation.is_valid
        assert len(result.structure.imports) >= 2
        assert len(result.structure.functions) >= 1
        assert len(result.structure.classes) >= 1
        assert "PI" in result.structure.global_variables
        assert result.metrics.total_lines > 0
    
    @pytest.mark.asyncio
    async def test_parse_javascript_file(self):
        """Test parsing JavaScript code."""
        result = await file_parsing_service.parse_file(JAVASCRIPT_CODE, ".js", "test-js-001")
        
        assert result.language == ProgrammingLanguage.JAVASCRIPT
        assert len(result.structure.imports) >= 1
        assert len(result.structure.functions) >= 1
        assert len(result.structure.classes) >= 1
    
    @pytest.mark.asyncio
    async def test_parse_java_file(self):
        """Test parsing Java code."""
        result = await file_parsing_service.parse_file(JAVA_CODE, ".java", "test-java-001")
        
        assert result.language == ProgrammingLanguage.JAVA
        assert len(result.structure.imports) >= 2
        assert len(result.structure.classes) >= 1
    
    @pytest.mark.asyncio
    async def test_parse_c_file(self):
        """Test parsing C code."""
        result = await file_parsing_service.parse_file(C_CODE, ".c", "test-c-001")
        
        assert result.language == ProgrammingLanguage.C
        assert len(result.structure.imports) >= 2  # includes
        assert len(result.structure.functions) >= 1
    
    @pytest.mark.asyncio
    async def test_basic_metrics(self):
        """Test basic metrics calculation."""
        result = await file_parsing_service.parse_file(PYTHON_CODE, ".py", "test-metrics")
        
        assert result.metrics.total_lines > 0
        assert result.metrics.code_lines > 0
        assert result.metrics.function_count >= 1
        assert result.metrics.class_count >= 1
        assert result.metrics.import_count >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

