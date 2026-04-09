from datetime import datetime
from sqlalchemy import UniqueConstraint
from ..extensions import db


class CabinetTypeConfig(db.Model):
    """柜体类型配置表
    
    存储控制大类、柜体类型、控制结构的组合配置。
    每个组合对应一套自动匹配规则和人工费用规则。
    """
    __tablename__ = 'cabinet_type_configs'
    __table_args__ = (
        UniqueConstraint(
            'control_category',
            'cabinet_type',
            'control_structure',
            name='uq_cabinet_type_config_combination'
        ),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    control_category = db.Column(db.String(50), nullable=False)  # 控制大类：低压类/配电类/控制类/自控类
    cabinet_type = db.Column(db.String(100), nullable=False)  # 柜体类型：配电箱柜/控制箱柜/低压进线柜等
    control_structure = db.Column(db.String(100), nullable=False)  # 控制结构：非标控制/自控型/纯PLC型/MCC柜/抽屉柜
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # 关联
    auto_match_rules = db.relationship(
        'AutoMatchRule',
        back_populates='cabinet_type_config',
        cascade='all, delete-orphan',
        lazy='dynamic',
    )
    labor_cost_rules = db.relationship(
        'LaborCostRule',
        back_populates='cabinet_type_config',
        cascade='all, delete-orphan',
        lazy='dynamic',
    )

    def to_dict(self, include_rules: bool = False) -> dict:
        data = {
            'id': self.id,
            'control_category': self.control_category,
            'cabinet_type': self.cabinet_type,
            'control_structure': self.control_structure,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_rules:
            data['auto_match_rules'] = [rule.to_dict() for rule in self.auto_match_rules]
            data['labor_cost_rules'] = [rule.to_dict() for rule in self.labor_cost_rules]
        return data

    def __repr__(self):
        return f'<CabinetTypeConfig {self.id}: {self.control_category}/{self.cabinet_type}/{self.control_structure}>'
