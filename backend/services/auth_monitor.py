"""
认证监控服务 - 检测可疑登录活动
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.auth_log import AuthLog
import json


class AuthMonitorService:
    """认证监控服务 - 检测和记录可疑登录活动"""
    
    # 配置参数
    MAX_FAILED_ATTEMPTS = 5  # 最大失败尝试次数
    LOCKOUT_DURATION = 15  # 锁定时长(分钟)
    SUSPICIOUS_WINDOW = 10  # 可疑活动检测时间窗口(分钟)
    
    @staticmethod
    async def log_auth_event(
        db: AsyncSession,
        student_id: str,
        event_type: str,
        status: str,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuthLog:
        """
        记录认证事件

        Args:
            db: 数据库会话
            student_id: 用户学号
            event_type: 事件类型(login, logout, register, token_refresh, password_change, token_revoke, login_failed)
            status: 事件状态(success, failure)
            user_id: 用户 ID(可选)
            ip_address: IP 地址(可选)
            user_agent: 用户代理(可选)
            failure_reason: 失败原因(可选)
            metadata: 额外元数据(可选)

        Returns:
            AuthLog: 创建的日志记录
        """
        auth_log = AuthLog(
            user_id=user_id,
            student_id=student_id,
            event_type=event_type,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason=failure_reason,
            extra_data=json.dumps(metadata) if metadata else None
        )
        db.add(auth_log)
        await db.commit()
        await db.refresh(auth_log)
        return auth_log
    
    @staticmethod
    async def check_failed_login_attempts(
        db: AsyncSession,
        student_id: str,
        time_window_minutes: int = SUSPICIOUS_WINDOW
    ) -> Dict[str, Any]:
        """
        检查指定时间窗口内的失败登录尝试次数

        Args:
            db: 数据库会话
            student_id: 用户学号
            time_window_minutes: 时间窗口(分钟)

        Returns:
            Dict: 包含失败次数和是否被锁定的信息
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)

        # 查询时间窗口内的失败登录次数
        stmt = select(func.count(AuthLog.id)).where(
            AuthLog.student_id == student_id,
            AuthLog.event_type == 'login_failed',
            AuthLog.status == 'failure',
            AuthLog.created_at >= cutoff_time
        )
        result = await db.execute(stmt)
        failed_count = result.scalar() or 0

        # 检查是否应该被锁定
        is_locked = failed_count >= AuthMonitorService.MAX_FAILED_ATTEMPTS

        # 如果被锁定,计算剩余锁定时间
        remaining_lockout = 0
        if is_locked:
            # 获取最后一次失败登录的时间
            stmt = select(AuthLog.created_at).where(
                AuthLog.student_id == student_id,
                AuthLog.event_type == 'login_failed',
                AuthLog.status == 'failure'
            ).order_by(AuthLog.created_at.desc()).limit(1)
            result = await db.execute(stmt)
            last_failed = result.scalar()

            if last_failed:
                lockout_end = last_failed + timedelta(minutes=AuthMonitorService.LOCKOUT_DURATION)
                if datetime.utcnow() < lockout_end:
                    remaining_lockout = int((lockout_end - datetime.utcnow()).total_seconds() / 60)
                else:
                    # 锁定时间已过,不再锁定
                    is_locked = False

        return {
            'failed_count': failed_count,
            'is_locked': is_locked,
            'remaining_lockout_minutes': remaining_lockout,
            'max_attempts': AuthMonitorService.MAX_FAILED_ATTEMPTS
        }
    
    @staticmethod
    async def detect_suspicious_activity(
        db: AsyncSession,
        student_id: str,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        检测可疑登录活动

        Args:
            db: 数据库会话
            student_id: 用户学号
            ip_address: IP 地址(可选)

        Returns:
            Dict: 可疑活动检测结果
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=AuthMonitorService.SUSPICIOUS_WINDOW)

        # 检查短时间内的登录尝试次数
        stmt = select(func.count(AuthLog.id)).where(
            AuthLog.student_id == student_id,
            AuthLog.event_type.in_(['login', 'login_failed']),
            AuthLog.created_at >= cutoff_time
        )
        result = await db.execute(stmt)
        total_attempts = result.scalar() or 0

        # 检查是否有多个不同的 IP 地址
        stmt = select(func.count(func.distinct(AuthLog.ip_address))).where(
            AuthLog.student_id == student_id,
            AuthLog.event_type.in_(['login', 'login_failed']),
            AuthLog.created_at >= cutoff_time,
            AuthLog.ip_address.isnot(None)
        )
        result = await db.execute(stmt)
        unique_ips = result.scalar() or 0

        # 判断是否可疑
        is_suspicious = (
            total_attempts > 10 or  # 短时间内尝试次数过多
            unique_ips > 3  # 来自多个不同 IP
        )

        return {
            'is_suspicious': is_suspicious,
            'total_attempts': total_attempts,
            'unique_ips': unique_ips,
            'time_window_minutes': AuthMonitorService.SUSPICIOUS_WINDOW
        }

