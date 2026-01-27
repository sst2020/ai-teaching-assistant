"""
数据模型定义 - 作业传输和文件管理
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal
from datetime import datetime
from enum import Enum


class AssignmentTransferStatus(str, Enum):
    """作业传输状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TeacherAssignmentSubmit(BaseModel):
    """教师提交作业的请求模型"""
    assignment_id: str = Field(..., description="作业唯一ID")
    course_id: str = Field(..., description="课程ID")
    title: str = Field(..., description="作业标题")
    description: str = Field(..., description="作业描述")
    due_date: str = Field(..., description="截止日期 (ISO 8601格式)")
    max_score: float = Field(100.0, description="最高分")
    assignment_type: str = Field("code", description="作业类型: code, essay, quiz")
    file_attachment: Optional[bytes] = Field(None, description="作业附件内容")
    file_name: Optional[str] = Field(None, description="附件文件名")
    rubric: Optional[Dict] = Field(None, description="评分标准")
    instructions: Optional[str] = Field(None, description="作业说明")


class BatchUploadRequest(BaseModel):
    """批量上传的请求模型"""
    assignment_id: str = Field(..., description="作业ID")
    course_id: str = Field(..., description="课程ID")
    student_submissions: List[Dict] = Field(..., description="学生提交列表")
    sync_to_file_manager: bool = Field(True, description="是否同步到文件管理系统")
    
    class Config:
        schema_extra = {
            "example": {
                "assignment_id": "hw001",
                "course_id": "CS101",
                "student_submissions": [
                    {
                        "student_id": "s001",
                        "student_name": "张三",
                        "file_content": "def hello():\n    print('Hello, world!')",
                        "file_name": "hello.py"
                    },
                    {
                        "student_id": "s002", 
                        "student_name": "李四",
                        "file_content": "def greet(name):\n    return f'Hello, {name}!'",
                        "file_name": "greet.py"
                    }
                ],
                "sync_to_file_manager": True
            }
        }


class FileManagerSyncRequest(BaseModel):
    """文件管理同步请求"""
    assignment_id: str = Field(..., description="作业ID")
    course_id: str = Field(..., description="课程ID")
    sync_type: Literal["full", "incremental"] = Field("full", description="同步类型")
    target_path: str = Field(..., description="目标路径")
    include_submissions: bool = Field(True, description="是否包含提交内容")
    include_feedback: bool = Field(False, description="是否包含反馈内容")


class FileManagerSyncResponse(BaseModel):
    """文件管理同步响应"""
    sync_id: str = Field(..., description="同步任务ID")
    assignment_id: str = Field(..., description="作业ID")
    course_id: str = Field(..., description="课程ID")
    status: AssignmentTransferStatus = Field(..., description="同步状态")
    progress: float = Field(0.0, description="进度百分比")
    total_files: int = Field(0, description="总文件数")
    processed_files: int = Field(0, description="已处理文件数")
    failed_files: int = Field(0, description="失败文件数")
    start_time: datetime = Field(..., description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    error_message: Optional[str] = Field(None, description="错误信息")


class AssignmentSubmissionRecord(BaseModel):
    """作业提交记录"""
    submission_id: str = Field(..., description="提交ID")
    assignment_id: str = Field(..., description="作业ID")
    student_id: str = Field(..., description="学生ID")
    student_name: str = Field(..., description="学生姓名")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    submitted_at: datetime = Field(..., description="提交时间")
    status: str = Field("pending", description="状态")
    content_preview: str = Field("", description="内容预览")


class AssignmentTransferResponse(BaseModel):
    """作业传输响应"""
    transfer_id: str = Field(..., description="传输任务ID")
    assignment_id: str = Field(..., description="作业ID")
    course_id: str = Field(..., description="课程ID")
    status: AssignmentTransferStatus = Field(..., description="传输状态")
    total_submissions: int = Field(0, description="总提交数")
    successful_transfers: int = Field(0, description="成功传输数")
    failed_transfers: int = Field(0, description="失败传输数")
    start_time: datetime = Field(..., description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    error_details: Optional[List[Dict]] = Field(None, description="错误详情")


class FileValidationResult(BaseModel):
    """文件验证结果"""
    filename: str = Field(..., description="文件名")
    is_valid: bool = Field(..., description="是否有效")
    validation_errors: List[str] = Field(default_factory=list, description="验证错误列表")
    file_size: int = Field(0, description="文件大小")
    detected_language: Optional[str] = Field(None, description="检测到的编程语言")


class BatchUploadResponse(BaseModel):
    """批量上传响应"""
    upload_id: str = Field(..., description="上传任务ID")
    assignment_id: str = Field(..., description="作业ID")
    course_id: str = Field(..., description="课程ID")
    total_files: int = Field(0, description="总文件数")
    successfully_uploaded: int = Field(0, description="成功上传数")
    failed_uploads: int = Field(0, description="失败上传数")
    validation_results: List[FileValidationResult] = Field(
        default_factory=list, description="验证结果列表"
    )
    start_time: datetime = Field(..., description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")