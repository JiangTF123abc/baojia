from datetime import datetime
from ..extensions import db


class PriceFormula(db.Model):
    __tablename__ = 'price_formulas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    formula_str = db.Column(db.Text, nullable=False)  # SymPy 表达式字符串
    variables = db.Column(db.Text)                    # JSON: 变量说明
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    version = db.Column(db.Integer, default=1, nullable=False)  # 乐观锁
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'formula_str': self.formula_str,
            'variables': self.variables,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<PriceFormula {self.id}: {self.name}>'
