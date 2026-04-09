from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint
from ..extensions import db


class BaseComponent(db.Model):
    __tablename__ = 'base_components'
    __table_args__ = (
        CheckConstraint('quantity > 0', name='ck_base_components_quantity_positive'),
        CheckConstraint('unit_price >= 0', name='ck_base_components_unit_price_non_negative'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    structure_component_id = db.Column(
        db.Integer,
        db.ForeignKey('structure_components.id', ondelete='CASCADE'),
        nullable=False,
    )
    material_id = db.Column(
        db.Integer,
        db.ForeignKey('materials.id', ondelete='SET NULL'),
        nullable=True,
    )
    
    # 新增：元器件分类和状态
    component_category = db.Column(db.String(100))  # 元器件分类：一次元器件/二次元器件/PLC及模块/触摸屏/电源/端子等
    
    model_number = db.Column(db.String(200))
    name = db.Column(db.String(200))
    specification = db.Column(db.String(500))
    quantity = db.Column(db.Numeric(18, 4), nullable=False)
    unit_price = db.Column(db.Numeric(18, 4), nullable=False, default=Decimal('0'))
    discount_rate = db.Column(db.Numeric(5, 4), nullable=False, default=Decimal('1.0'))
    
    # 新增：自动匹配和隐藏标记
    is_auto_matched = db.Column(db.Boolean, default=False, nullable=False)  # 是否为自动匹配的元器件
    is_hidden = db.Column(db.Boolean, default=False, nullable=False)  # 是否被自动隐藏
    
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
    structure_component = db.relationship('StructureComponent', back_populates='base_components')
    material = db.relationship('Material', back_populates='base_components')

    @property
    def total_price(self) -> Decimal:
        """计算总价：数量 × 单价 × 折扣率"""
        qty = self.quantity or Decimal('0')
        price = self.unit_price or Decimal('0')
        discount = self.discount_rate or Decimal('1')
        return qty * price * discount

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'structure_component_id': self.structure_component_id,
            'material_id': self.material_id,
            'component_category': self.component_category,
            'model_number': self.model_number,
            'name': self.name,
            'specification': self.specification,
            'quantity': str(self.quantity) if self.quantity is not None else None,
            'unit_price': str(self.unit_price) if self.unit_price is not None else None,
            'discount_rate': str(self.discount_rate) if self.discount_rate is not None else None,
            'total_price': str(self.total_price),
            'is_auto_matched': self.is_auto_matched,
            'is_hidden': self.is_hidden,
            'sort_order': self.sort_order,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<BaseComponent {self.id}: {self.model_number} (sc={self.structure_component_id})>'
