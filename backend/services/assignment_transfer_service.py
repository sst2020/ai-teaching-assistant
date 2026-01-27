"""
作业传输服务 - 处理教师端提交和文件管理系统的集成
"""
import asyncio
import os
import shutil
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import tempfile
import zipfile
from pathlib import Path

from schemas.assignment_transfer import (
    TeacherAssignmentSubmit,
    BatchUploadRequest,
    FileManagerSyncRequest,
    FileManagerSyncResponse,
    AssignmentTransferResponse,
    BatchUploadResponse,
    FileValidationResult,
    AssignmentTransferStatus
)
from schemas.assignment import AssignmentSubmission
from services.grading_service import grading_service
from services.plagiarism_service import enhanced_plagiarism_service
from utils.crud import crud_assignment
from core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


class AssignmentTransferService:
    """作业传输服务类"""

    def __init__(self):
        self.upload_dir = "uploads/assignments"
        self.file_manager_dir = "file_manager"
        self.temp_dir = "temp"
        
        # 确保目录存在
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.file_manager_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    async def submit_assignment_from_teacher(
        self, 
        assignment_data: TeacherAssignmentSubmit
    ) -> Dict:
        """
        教师提交作业定义
        """
        try:
            # 创建作业记录
            assignment_record = {
                "assignment_id": assignment_data.assignment_id,
                "course_id": assignment_data.course_id,
                "title": assignment_data.title,
                "description": assignment_data.description,
                "due_date": assignment_data.due_date,
                "max_score": assignment_data.max_score,
                "assignment_type": assignment_data.assignment_type,
                "instructions": assignment_data.instructions,
                "created_at": datetime.utcnow()
            }
            
            # 如果有附件，保存附件
            if assignment_data.file_attachment and assignment_data.file_name:
                file_path = os.path.join(
                    self.upload_dir, 
                    assignment_data.course_id,
                    assignment_data.assignment_id,
                    assignment_data.file_name
                )
                
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, 'wb') as f:
                    f.write(assignment_data.file_attachment)
                
                assignment_record["attachment_path"] = file_path
            
            # 这里应该连接到数据库并保存作业记录
            # await crud_assignment.create_assignment(assignment_record)
            
            return {
                "success": True,
                "message": f"作业 {assignment_data.assignment_id} 已成功提交",
                "assignment_id": assignment_data.assignment_id,
                "course_id": assignment_data.course_id
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"提交作业失败: {str(e)}",
                "assignment_id": assignment_data.assignment_id
            }

    async def batch_upload_student_submissions(
        self, 
        batch_request: BatchUploadRequest
    ) -> BatchUploadResponse:
        """
        批量上传学生作业文件
        """
        upload_id = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        total_files = len(batch_request.student_submissions)
        successfully_uploaded = 0
        failed_uploads = 0
        validation_results = []
        
        try:
            for submission in batch_request.student_submissions:
                student_id = submission.get("student_id")
                student_name = submission.get("student_name", "")
                file_content = submission.get("file_content", "")
                file_name = submission.get("file_name", f"{student_id}_submission.txt")
                
                # 验证文件
                validation_result = self._validate_file(file_name, file_content.encode())
                validation_results.append(validation_result)
                
                if validation_result.is_valid:
                    # 保存文件
                    file_path = os.path.join(
                        self.upload_dir,
                        batch_request.course_id,
                        batch_request.assignment_id,
                        "submissions",
                        student_id,
                        file_name
                    )
                    
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(file_content)
                    
                    # 创建提交记录（模拟）
                    submission_record = AssignmentSubmission(
                        student_id=student_id,
                        assignment_id=batch_request.assignment_id,
                        assignment_type="code",  # 默认为代码作业
                        content=file_content,
                        file_name=file_name
                    )
                    
                    # 如果需要立即评分，可以在这里调用评分服务
                    # await grading_service.grade_submission(submission_record)
                    
                    successfully_uploaded += 1
                else:
                    failed_uploads += 1
        
        except Exception as e:
            return BatchUploadResponse(
                upload_id=upload_id,
                assignment_id=batch_request.assignment_id,
                course_id=batch_request.course_id,
                total_files=total_files,
                successfully_uploaded=successfully_uploaded,
                failed_uploads=total_files - successfully_uploaded,
                validation_results=validation_results,
                start_time=start_time,
                end_time=datetime.now()
            )
        
        # 如果需要同步到文件管理系统
        if batch_request.sync_to_file_manager:
            # 异步启动同步任务
            asyncio.create_task(
                self._sync_to_file_manager_async(
                    batch_request.assignment_id,
                    batch_request.course_id
                )
            )
        
        return BatchUploadResponse(
            upload_id=upload_id,
            assignment_id=batch_request.assignment_id,
            course_id=batch_request.course_id,
            total_files=total_files,
            successfully_uploaded=successfully_uploaded,
            failed_uploads=failed_uploads,
            validation_results=validation_results,
            start_time=start_time,
            end_time=datetime.now()
        )

    def _validate_file(self, filename: str, content: bytes) -> FileValidationResult:
        """
        验证上传的文件
        """
        errors = []
        file_size = len(content)
        
        # 检查文件扩展名
        allowed_extensions = ['.py', '.java', '.cpp', '.c', '.js', '.ts', '.pdf', '.docx', '.txt', '.zip']
        file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
        
        if file_ext not in allowed_extensions:
            errors.append(f"不支持的文件类型: {file_ext}")
        
        # 检查文件大小（限制为10MB）
        if file_size > 10 * 1024 * 1024:  # 10MB
            errors.append(f"文件过大: {file_size} 字节，最大允许 10MB")
        
        # 检测编程语言
        detected_language = None
        if file_ext in ['.py']:
            detected_language = 'python'
        elif file_ext in ['.java']:
            detected_language = 'java'
        elif file_ext in ['.cpp', '.c']:
            detected_language = 'cpp'
        elif file_ext in ['.js', '.ts']:
            detected_language = 'javascript'
        
        return FileValidationResult(
            filename=filename,
            is_valid=len(errors) == 0,
            validation_errors=errors,
            file_size=file_size,
            detected_language=detected_language
        )

    async def sync_with_file_manager(
        self, 
        sync_request: FileManagerSyncRequest
    ) -> FileManagerSyncResponse:
        """
        与文件管理系统同步
        """
        sync_id = f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        try:
            # 根据同步类型执行相应操作
            if sync_request.sync_type == "full":
                result = await self._perform_full_sync(sync_request)
            else:
                result = await self._perform_incremental_sync(sync_request)
            
            return FileManagerSyncResponse(
                sync_id=sync_id,
                assignment_id=sync_request.assignment_id,
                course_id=sync_request.course_id,
                status=AssignmentTransferStatus.COMPLETED,
                progress=100.0,
                total_files=result["total_files"],
                processed_files=result["processed_files"],
                failed_files=result["failed_files"],
                start_time=start_time,
                end_time=datetime.now(),
                error_message=None
            )
        except Exception as e:
            return FileManagerSyncResponse(
                sync_id=sync_id,
                assignment_id=sync_request.assignment_id,
                course_id=sync_request.course_id,
                status=AssignmentTransferStatus.FAILED,
                progress=0.0,
                total_files=0,
                processed_files=0,
                failed_files=0,
                start_time=start_time,
                end_time=datetime.now(),
                error_message=str(e)
            )

    async def _perform_full_sync(self, request: FileManagerSyncRequest) -> Dict:
        """
        执行完整同步
        """
        # 获取作业目录
        source_dir = os.path.join(
            self.upload_dir,
            request.course_id,
            request.assignment_id
        )
        
        if not os.path.exists(source_dir):
            return {"total_files": 0, "processed_files": 0, "failed_files": 0}
        
        # 目标目录
        target_dir = os.path.join(
            self.file_manager_dir,
            request.target_path,
            request.course_id,
            request.assignment_id
        )
        
        os.makedirs(target_dir, exist_ok=True)
        
        # 复制文件
        total_files = 0
        processed_files = 0
        failed_files = 0
        
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                total_files += 1
                try:
                    source_file = os.path.join(root, file)
                    rel_path = os.path.relpath(source_file, source_dir)
                    target_file = os.path.join(target_dir, rel_path)
                    
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    shutil.copy2(source_file, target_file)
                    
                    processed_files += 1
                except Exception:
                    failed_files += 1
        
        return {
            "total_files": total_files,
            "processed_files": processed_files,
            "failed_files": failed_files
        }

    async def _perform_incremental_sync(self, request: FileManagerSyncRequest) -> Dict:
        """
        执行增量同步
        """
        # 获取作业目录
        source_dir = os.path.join(
            self.upload_dir,
            request.course_id,
            request.assignment_id
        )
        
        if not os.path.exists(source_dir):
            return {"total_files": 0, "processed_files": 0, "failed_files": 0}
        
        # 目标目录
        target_dir = os.path.join(
            self.file_manager_dir,
            request.target_path,
            request.course_id,
            request.assignment_id
        )
        
        os.makedirs(target_dir, exist_ok=True)
        
        # 增量同步逻辑：只复制修改时间更新的文件
        total_files = 0
        processed_files = 0
        failed_files = 0
        
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                total_files += 1
                try:
                    source_file = os.path.join(root, file)
                    rel_path = os.path.relpath(source_file, source_dir)
                    target_file = os.path.join(target_dir, rel_path)
                    
                    # 检查目标文件是否存在且是否需要更新
                    if (not os.path.exists(target_file) or 
                        os.path.getmtime(source_file) > os.path.getmtime(target_file)):
                        
                        os.makedirs(os.path.dirname(target_file), exist_ok=True)
                        shutil.copy2(source_file, target_file)
                        processed_files += 1
                    else:
                        # 文件未更改，跳过
                        processed_files += 1
                except Exception:
                    failed_files += 1
        
        return {
            "total_files": total_files,
            "processed_files": processed_files,
            "failed_files": failed_files
        }

    async def _sync_to_file_manager_async(self, assignment_id: str, course_id: str):
        """
        异步同步到文件管理器
        """
        # 创建一个基本的同步请求
        sync_request = FileManagerSyncRequest(
            assignment_id=assignment_id,
            course_id=course_id,
            sync_type="incremental",
            target_path="assignments"
        )
        
        await self._perform_incremental_sync(sync_request)

    async def get_assignment_submissions(
        self, 
        assignment_id: str, 
        course_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> List[Dict]:
        """
        获取作业提交列表
        """
        submissions_dir = os.path.join(
            self.upload_dir,
            course_id,
            assignment_id,
            "submissions"
        )
        
        if not os.path.exists(submissions_dir):
            return []
        
        submissions = []
        all_students = os.listdir(submissions_dir)
        
        # 分页处理
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        students_page = all_students[start_idx:end_idx]
        
        for student_id in students_page:
            student_dir = os.path.join(submissions_dir, student_id)
            if os.path.isdir(student_dir):
                files = os.listdir(student_dir)
                for file_name in files:
                    file_path = os.path.join(student_dir, file_name)
                    stat = os.stat(file_path)
                    
                    submissions.append({
                        "submission_id": f"{assignment_id}_{student_id}_{file_name}",
                        "student_id": student_id,
                        "student_name": f"Student {student_id}",  # 实际应用中应从数据库获取
                        "file_name": file_name,
                        "file_size": stat.st_size,
                        "submitted_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "status": "graded" if os.path.exists(file_path.replace('.', '_graded.')) else "pending",
                        "content_preview": self._get_content_preview(file_path)
                    })
        
        return submissions

    def _get_content_preview(self, file_path: str, max_length: int = 100) -> str:
        """
        获取文件内容预览
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return content[:max_length] + ("..." if len(content) > max_length else "")
        except:
            return ""


# 创建服务实例
assignment_transfer_service = AssignmentTransferService()