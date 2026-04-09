"""
通用工具函数：乐观锁更新、输入验证
"""
from ..extensions import db


def optimistic_update(instance, version: int, **fields):
    """
    通用乐观锁更新工具。

    检查 instance.version == version，若不匹配抛出 ConflictError。
    更新 fields 中的字段，version+1，提交事务。

    使用方式：
        from ..utils.validators import optimistic_update
        from ..services.project_service import ConflictError
        updated = optimistic_update(project, version=2, name="新名称")
    """
    # 延迟导入避免循环依赖
    from ..services.project_service import ConflictError

    if instance.version != version:
        raise ConflictError(current_data=instance.to_dict() if hasattr(instance, 'to_dict') else None)

    for key, value in fields.items():
        if hasattr(instance, key):
            setattr(instance, key, value)

    instance.version = version + 1

    try:
        db.session.commit()
        return instance
    except Exception:
        db.session.rollback()
        raise
