from datetime import datetime
from ..extensions import db


class StructureComponent(db.Model):
    __tablename__ = 'structure_components'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cabinet_id = db.Column(
        db.Integer,
        db.ForeignKey('cabinets.id', ondelete='CASCADE'),
        nullable=False,
    )
    name = db.Column(db.String(200), nullable=False)
    
    # 新增：回路类型（用于非标柜）
    circuit_type = db.Column(db.String(100))  # 回路类型：电机回路/变频回路/三角降压等
    
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    version = db.Column(db.Integer, default=1, nullable=False)  # 乐观锁
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # 关联
    cabinet = db.relationship('Cabinet', back_populates='structure_components')
    base_components = db.relationship(
        'BaseComponent',
        back_populates='structure_component',
        cascade='all, delete-orphan',
        lazy='dynamic',
        order_by='BaseComponent.sort_order',
    )

    def to_dict(self, include_base_components: bool = False) -> dict:
        data = {
            'id': self.id,
            'cabinet_id': self.cabinet_id,
            'name': self.name,
            'circuit_type': self.circuit_type,
            'sort_order': self.sort_order,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_base_components:
            data['base_components'] = [
                bc.to_dict() for bc in self.base_components
            ]
        return data

    def __repr__(self):
        return f'<StructureComponent {self.id}: {self.name} (cabinet={self.cabinet_id})>'
