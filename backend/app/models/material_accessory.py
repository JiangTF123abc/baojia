from decimal import Decimal
from ..extensions import db


class MaterialAccessory(db.Model):
    """Materials N:N 关联表（主材料 → 附件）"""
    __tablename__ = 'material_accessories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    material_id = db.Column(
        db.Integer,
        db.ForeignKey('materials.id', ondelete='CASCADE'),
        nullable=False,
    )
    accessory_id = db.Column(
        db.Integer,
        db.ForeignKey('materials.id', ondelete='NO ACTION'),
        nullable=False,
    )
    is_required = db.Column(db.Boolean, default=False, nullable=False)
    default_quantity = db.Column(db.Numeric(18, 4), default=Decimal('1'), nullable=False)

    # 关联
    material = db.relationship(
        'Material',
        foreign_keys=[material_id],
        back_populates='accessory_links',
    )
    accessory = db.relationship(
        'Material',
        foreign_keys=[accessory_id],
        back_populates='as_accessory_links',
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'material_id': self.material_id,
            'accessory_id': self.accessory_id,
            'is_required': self.is_required,
            'default_quantity': str(self.default_quantity),
        }

    def __repr__(self):
        return f'<MaterialAccessory material={self.material_id} -> accessory={self.accessory_id}>'
