from datetime import datetime
from ..extensions import db


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    customer = db.Column(db.String(200))
    project_date = db.Column(db.Date)
    notes = db.Column(db.Text)
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
    creator = db.relationship('User', back_populates='projects')
    cabinets = db.relationship(
        'Cabinet',
        back_populates='project',
        cascade='all, delete-orphan',
        lazy='dynamic',
        order_by='Cabinet.sort_order',
    )

    def to_dict(self, include_cabinets: bool = False) -> dict:
        data = {
            'id': self.id,
            'name': self.name,
            'customer': self.customer,
            'project_date': self.project_date.isoformat() if self.project_date else None,
            'notes': self.notes,
            'created_by': self.created_by,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_cabinets:
            data['cabinets'] = [c.to_dict(include_components=True) for c in self.cabinets]
        return data

    def __repr__(self):
        return f'<Project {self.id}: {self.name}>'
