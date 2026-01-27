"""
作业数据同步服务
从管理系统同步任务数据到学生端作业表
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from schemas.assignment_crud import AssignmentCreate
from models.assignment import AssignmentType as DBAssignmentType
from utils.crud import crud_assignment


class SyncResult(BaseModel):
    """同步结果"""
    sync_id: str
    sync_time: datetime
    total_tasks: int
    new_assignments: int
    skipped_duplicates: int
    errors: List[str]
    details: List[Dict]


class AssignmentSyncService:
    """作业数据同步服务"""
    
    def __init__(self):
        self.mgmt_system_path = "E:/Code/repo/管理系统/data/db.json"
        self.sync_log_path = "data/sync_log.json"
        
        # 任务类型映射
        self.type_mapping = {
            "知识点学习": DBAssignmentType.ESSAY,
            "OJ题目": DBAssignmentType.CODE,
            "ACDC系统任务": DBAssignmentType.CODE,
        }
        
    async def sync_assignments(self, db: AsyncSession) -> SyncResult:
        """执行同步任务"""
        sync_id = f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        sync_time = datetime.now()
        
        result = SyncResult(
            sync_id=sync_id,
            sync_time=sync_time,
            total_tasks=0,
            new_assignments=0,
            skipped_duplicates=0,
            errors=[],
            details=[]
        )
        
        try:
            # 1. 读取管理系统数据
            mgmt_data = self._read_management_data()
            
            # 2. 遍历所有班级的任务
            for class_info in mgmt_data.get('classes', []):
                tasks = class_info.get('tasks', [])
                result.total_tasks += len(tasks)
                
                for task in tasks:
                    try:
                        # 3. 检查是否已存在
                        assignment_id = f"mgmt_{task['id']}"
                        if await self._check_duplicate(db, assignment_id):
                            result.skipped_duplicates += 1
                            result.details.append({
                                "task_id": task['id'],
                                "assignment_id": assignment_id,
                                "status": "skipped",
                                "reason": "already_exists"
                            })
                            continue
                        
                        # 4. 映射并保存
                        assignment_data = self._map_task_to_assignment(task, class_info)
                        saved = await self._save_assignment(db, assignment_data)
                        
                        result.new_assignments += 1
                        result.details.append({
                            "task_id": task['id'],
                            "assignment_id": assignment_id,
                            "status": "created",
                            "title": saved.title
                        })
                        
                    except Exception as e:
                        error_msg = f"Failed to sync task {task.get('id')}: {str(e)}"
                        result.errors.append(error_msg)
            
            # 5. 记录同步日志
            self._log_sync_result(result)
            
        except Exception as e:
            result.errors.append(f"Sync failed: {str(e)}")
        
        return result
    
    def _read_management_data(self) -> dict:
        """读取管理系统 db.json"""
        if not os.path.exists(self.mgmt_system_path):
            raise FileNotFoundError(f"Management system data not found: {self.mgmt_system_path}")
        
        with open(self.mgmt_system_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _map_task_to_assignment(self, task: dict, class_info: dict) -> AssignmentCreate:
        """映射任务数据到作业数据"""
        # 生成标题（取内容前50字）
        content = task.get('content', '')
        title = content[:50] + ('...' if len(content) > 50 else '')
        
        # 映射任务类型
        task_type = task.get('type', 'OJ题目')
        assignment_type = self.type_mapping.get(task_type, DBAssignmentType.CODE)
        
        # 推导课程 ID（从班级 ID 或课程关联）
        course_id = str(class_info.get('id', 'default'))
        
        # 解析截止日期
        deadline_str = task.get('deadline', '')
        try:
            due_date = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
        except:
            due_date = None
        
        return AssignmentCreate(
            assignment_id=f"mgmt_{task['id']}",
            title=title,
            description=content,
            assignment_type=assignment_type.value,
            course_id=course_id,
            due_date=due_date,
            max_score=100.0,
            rubric_id=None
        )

    async def _check_duplicate(self, db: AsyncSession, assignment_id: str) -> bool:
        """检查作业是否已存在"""
        existing = await crud_assignment.get_by_assignment_id(db, assignment_id)
        return existing is not None

    async def _save_assignment(self, db: AsyncSession, assignment_data: AssignmentCreate):
        """保存作业到数据库"""
        # 映射枚举类型
        create_dict = assignment_data.model_dump()

        # 映射 assignment_type 字符串到数据库枚举
        type_str = create_dict.get('assignment_type', 'code')
        if type_str == 'code':
            create_dict['assignment_type'] = DBAssignmentType.CODE
        elif type_str == 'essay':
            create_dict['assignment_type'] = DBAssignmentType.ESSAY
        elif type_str == 'quiz':
            create_dict['assignment_type'] = DBAssignmentType.QUIZ
        else:
            create_dict['assignment_type'] = DBAssignmentType.CODE

        assignment = await crud_assignment.create(db, create_dict)
        await db.commit()
        return assignment

    def _log_sync_result(self, result: SyncResult):
        """记录同步日志"""
        os.makedirs(os.path.dirname(self.sync_log_path) if os.path.dirname(self.sync_log_path) else '.', exist_ok=True)

        # 读取现有日志
        logs = []
        if os.path.exists(self.sync_log_path):
            try:
                with open(self.sync_log_path, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []

        # 添加新日志
        logs.append(result.model_dump(mode='json'))

        # 只保留最近 100 条
        logs = logs[-100:]

        # 保存日志
        with open(self.sync_log_path, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2, default=str)


# 单例实例
assignment_sync_service = AssignmentSyncService()


