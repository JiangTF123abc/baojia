from datetime import datetime
from ..extensions import db


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)       # CREATE | UPDATE | DELETE | EXPORT
    entity_type = db.Column(db.String(100), nullable=False)
    entity_id = db.Column(db.Integer)
    old_value = db.Column(db.Text)   # JSON
    new_value = db.Column(db.Text)   # JSON
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # 关联（AuditLog 无 version 字段）
    user = db.relationship('User', back_populates='audit_logs')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<AuditLog {self.id}: {self.action} {self.entity_type}({self.entity_id})>'
