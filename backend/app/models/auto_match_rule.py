from datetime import datetime
from decimal import Decimal
from ..extensions import db


class AutoMatchRule(db.Model):
    """自动匹配规则表
    
    定义每种柜体配置应自动匹配的元器件。
    用于快速报价模式下的自动元器件插入。
    """
    __tablename__ = 'auto_match_rules'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cabinet_type_config_id = db.Column(
        db.Integer,
        db.ForeignKey('cabinet_type_configs.id', ondelete='CASCADE'),
        nullable=False,
    )
    material_id = db.Column(
        db.Integer,
        db.ForeignKey('materials.id', ondelete='CASCADE'),
        nullable=False,
    )
    component_category = db.Column(db.String(100), nullable=False)  # 元器件分类
    default_quantity = db.Column(db.Numeric(18, 4), nullable=False, default=Decimal('1'))
    is_required = db.Column(db.Boolean, default=True, nullable=False)  # 是否必选
    match_priority = db.Column(db.Integer, default=0, nullable=False)  # 匹配优先级（数值越大优先级越高）
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # 关联
    cabinet_type_config = db.relationship('CabinetTypeConfig', back_populates='auto_match_rules')
    material = db.relationship('Material')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'cabinet_type_config_id': self.cabinet_type_config_id,
            'material_id': self.material_id,
            'component_category': self.component_category,
            'default_quantity': str(self.default_quantity) if self.default_quantity is not None else None,
            'is_required': self.is_required,
            'match_priority': self.match_priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # 包含关联的材料信息
            'material': self.material.to_dict() if self.material else None,
        }

    def __repr__(self):
        return f'<AutoMatchRule {self.id}: config={self.cabinet_type_config_id}, material={self.material_id}>'
