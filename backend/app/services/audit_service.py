import json
import logging
from datetime import datetime, timedelta

from ..extensions import db
from ..models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class AuditService:

    def log_action(
        self,
        user_id: int,
        action: str,
        entity_type: str,
        entity_id: int = None,
        old_value=None,
        new_value=None,
        ip_address: str = None,
    ) -> None:
        """
        记录审计日志。

        action: 'CREATE' | 'UPDATE' | 'DELETE' | 'EXPORT'
        old_value / new_value: dict 或 None，自动序列化为 JSON
        """
        try:
            log = AuditLog(
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                old_value=json.dumps(old_value, ensure_ascii=False, default=str) if old_value is not None else None,
                new_value=json.dumps(new_value, ensure_ascii=False, default=str) if new_value is not None else None,
                ip_address=ip_address,
            )
            db.session.add(log)
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            logger.error("审计日志写入失败: %s", exc)

    def query_logs(
        self,
        start: datetime = None,
        end: datetime = None,
        user_id: int = None,
        entity_type: str = None,
        action: str = None,
        page: int = 1,
        per_page: int = 50,
    ) -> dict:
        """查询审计日志，支持分页"""
        q = AuditLog.query
        if start:
            q = q.filter(AuditLog.created_at >= start)
        if end:
            q = q.filter(AuditLog.created_at <= end)
        if user_id:
            q = q.filter(AuditLog.user_id == user_id)
        if entity_type:
            q = q.filter(AuditLog.entity_type == entity_type)
        if action:
            q = q.filter(AuditLog.action == action)

        total = q.count()
        logs = q.order_by(AuditLog.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "items": [log.to_dict() for log in logs],
        }

    def export_logs(self, start: datetime = None, end: datetime = None) -> list:
        """导出审计日志（不分页）"""
        q = AuditLog.query
        if start:
            q = q.filter(AuditLog.created_at >= start)
        if end:
            q = q.filter(AuditLog.created_at <= end)
        logs = q.order_by(AuditLog.created_at.desc()).all()
        return [log.to_dict() for log in logs]


audit_service = AuditService()
