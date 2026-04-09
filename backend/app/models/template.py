from datetime import datetime
from ..extensions import db


class Template(db.Model):
    __tablename__ = 'templates'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    source_type = db.Column(db.String(50))  # 'cabinet' | 'structure_component'
    template_data = db.Column(db.Text, nullable=False)  # JSON 序列化的完整配置
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    version = db.Column(db.Integer, default=1, nullable=False)  # 乐观锁
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # 关联
    creator = db.relationship('User', back_populates='templates')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'source_type': self.source_type,
            'template_data': self.template_data,
            'created_by': self.created_by,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Template {self.id}: {self.name}>'
