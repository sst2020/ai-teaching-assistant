"""
Tests for File Upload API Endpoints
"""
import pytest
import io
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from fastapi.testclient import TestClient


# Sample code for testing
PYTHON_CODE = """
import os
from typing import List

def hello(name: str) -> str:
    return f"Hello, {name}!"

class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b

PI = 3.14159
"""

JAVASCRIPT_CODE = """
import React from 'react';

function sayHello(name) {
    return `Hello, ${name}!`;
}

class Calculator {
    add(a, b) {
        return a + b;
    }
}

export default Calculator;
"""


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestFileUploadAPI:
    """Test cases for file upload API."""
    
    def test_list_files_empty(self, client):
        """Test listing files when empty."""
        response = client.get('/api/v1/files')
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        assert 'total' in data
        assert 'page' in data
        assert 'page_size' in data
    
    def test_upload_python_file(self, client):
        """Test uploading a Python file."""
        file_content = PYTHON_CODE.encode('utf-8')
        files = {'file': ('test_code.py', io.BytesIO(file_content), 'text/x-python')}

        response = client.post('/api/v1/files/upload', files=files)
        assert response.status_code == 201  # 201 Created is correct for resource creation
        
        data = response.json()
        assert 'file_id' in data
        assert data['original_filename'] == 'test_code.py'
        assert data['language'] == 'python'
        assert data['file_size'] > 0
        
        # Cleanup
        file_id = data['file_id']
        client.delete(f'/api/v1/files/{file_id}')
    
    def test_upload_javascript_file(self, client):
        """Test uploading a JavaScript file."""
        file_content = JAVASCRIPT_CODE.encode('utf-8')
        files = {'file': ('component.js', io.BytesIO(file_content), 'text/javascript')}

        response = client.post('/api/v1/files/upload', files=files)
        assert response.status_code == 201  # 201 Created is correct for resource creation
        
        data = response.json()
        assert data['language'] == 'javascript'
        
        # Cleanup
        client.delete(f'/api/v1/files/{data["file_id"]}')
    
    def test_upload_invalid_file_type(self, client):
        """Test uploading an invalid file type."""
        file_content = b"This is a text file"
        files = {'file': ('test.txt', io.BytesIO(file_content), 'text/plain')}
        
        response = client.post('/api/v1/files/upload', files=files)
        assert response.status_code == 400
        assert 'not allowed' in response.json()['detail'].lower()
    
    def test_get_file_metadata(self, client):
        """Test getting file metadata."""
        # Upload a file first
        file_content = PYTHON_CODE.encode('utf-8')
        files = {'file': ('test_meta.py', io.BytesIO(file_content), 'text/x-python')}
        upload_response = client.post('/api/v1/files/upload', files=files)
        file_id = upload_response.json()['file_id']
        
        # Get metadata
        response = client.get(f'/api/v1/files/{file_id}')
        assert response.status_code == 200
        
        data = response.json()
        assert data['file_id'] == file_id
        assert data['original_filename'] == 'test_meta.py'
        
        # Cleanup
        client.delete(f'/api/v1/files/{file_id}')
    
    def test_get_file_content(self, client):
        """Test getting file content."""
        # Upload a file first
        file_content = PYTHON_CODE.encode('utf-8')
        files = {'file': ('test_content.py', io.BytesIO(file_content), 'text/x-python')}
        upload_response = client.post('/api/v1/files/upload', files=files)
        file_id = upload_response.json()['file_id']
        
        # Get content
        response = client.get(f'/api/v1/files/{file_id}/content')
        assert response.status_code == 200
        
        data = response.json()
        assert 'content' in data
        assert 'def hello' in data['content']
        
        # Cleanup
        client.delete(f'/api/v1/files/{file_id}')
    
    def test_parse_file(self, client):
        """Test parsing a file."""
        # Upload a file first
        file_content = PYTHON_CODE.encode('utf-8')
        files = {'file': ('test_parse.py', io.BytesIO(file_content), 'text/x-python')}
        upload_response = client.post('/api/v1/files/upload', files=files)
        file_id = upload_response.json()['file_id']
        
        # Parse file
        response = client.get(f'/api/v1/files/{file_id}/parse')
        assert response.status_code == 200
        
        data = response.json()
        assert data['language'] == 'python'
        assert data['syntax_validation']['is_valid']
        assert len(data['structure']['imports']) >= 2
        assert len(data['structure']['functions']) >= 1
        assert len(data['structure']['classes']) >= 1
        
        # Cleanup
        client.delete(f'/api/v1/files/{file_id}')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

