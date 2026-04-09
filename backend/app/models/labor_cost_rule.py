from datetime import datetime
from decimal import Decimal
from ..extensions import db


class LaborCostRule(db.Model):
    """人工费用规则表
    
    定义不同柜体配置的人工费用计算规则。
    包括组装费率、管理费率、利润率以及编程调试费用。
    """
    __tablename__ = 'labor_cost_rules'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cabinet_type_config_id = db.Column(
        db.Integer,
        db.ForeignKey('cabinet_type_configs.id', ondelete='CASCADE'),
        nullable=False,
    )
    assembly_fee_rate = db.Column(db.Numeric(5, 4), nullable=False, default=Decimal('0.10'))  # 组装费率（默认10%）
    management_fee_rate = db.Column(db.Numeric(5, 4), nullable=False, default=Decimal('0.05'))  # 管理费率（默认5%）
    profit_rate = db.Column(db.Numeric(5, 4), nullable=False, default=Decimal('0.15'))  # 利润率（默认15%）
    has_plc = db.Column(db.Boolean, default=False, nullable=False)  # 是否包含PLC（用于判断是否需要编程调试费）
    programming_fee = db.Column(db.Numeric(18, 4), default=Decimal('0'))  # 编程费用（固定金额）
    debugging_fee = db.Column(db.Numeric(18, 4), default=Decimal('0'))  # 调试费用（固定金额）
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # 关联
    cabinet_type_config = db.relationship('CabinetTypeConfig', back_populates='labor_cost_rules')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'cabinet_type_config_id': self.cabinet_type_config_id,
            'assembly_fee_rate': str(self.assembly_fee_rate) if self.assembly_fee_rate is not None else None,
            'management_fee_rate': str(self.management_fee_rate) if self.management_fee_rate is not None else None,
            'profit_rate': str(self.profit_rate) if self.profit_rate is not None else None,
            'has_plc': self.has_plc,
            'programming_fee': str(self.programming_fee) if self.programming_fee is not None else None,
            'debugging_fee': str(self.debugging_fee) if self.debugging_fee is not None else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<LaborCostRule {self.id}: config={self.cabinet_type_config_id}, has_plc={self.has_plc}>'
