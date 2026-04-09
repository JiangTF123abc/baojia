from datetime import datetime
from ..extensions import db


class Material(db.Model):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_number = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    specification = db.Column(db.String(500))
    unit_price = db.Column(db.Numeric(18, 4))
    category = db.Column(db.String(100))
    
    # 新增：元器件类型
    component_type = db.Column(db.String(100))  # 元器件类型：一次/二次/PLC/触摸屏/电源/端子等
    
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # 关联
    base_components = db.relationship('BaseComponent', back_populates='material', lazy='dynamic')
    # 作为主材料的附件关系
    accessory_links = db.relationship(
        'MaterialAccessory',
        foreign_keys='MaterialAccessory.material_id',
        back_populates='material',
        lazy='dynamic',
    )
    # 作为附件的关系
    as_accessory_links = db.relationship(
        'MaterialAccessory',
        foreign_keys='MaterialAccessory.accessory_id',
        back_populates='accessory',
        lazy='dynamic',
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'model_number': self.model_number,
            'name': self.name,
            'specification': self.specification,
            'unit_price': str(self.unit_price) if self.unit_price is not None else None,
            'category': self.category,
            'component_type': self.component_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Material {self.id}: {self.model_number} - {self.name}>'
