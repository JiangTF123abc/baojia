from datetime import datetime
from ..extensions import db


class Cabinet(db.Model):
    __tablename__ = 'cabinets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(
        db.Integer,
        db.ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=False,
    )
    name = db.Column(db.String(200), nullable=False)
    
    # 新增：柜体分类字段
    control_category = db.Column(db.String(50))  # 控制大类：低压类/配电类/控制类/自控类
    cabinet_type = db.Column(db.String(100))  # 柜体类型：配电箱柜/控制箱柜/低压进线柜等
    control_structure = db.Column(db.String(100))  # 控制结构：非标控制/自控型/纯PLC型/MCC柜/抽屉柜
    quotation_mode = db.Column(db.String(50))  # 报价模式：detailed/quick
    
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
    project = db.relationship('Project', back_populates='cabinets')
    structure_components = db.relationship(
        'StructureComponent',
        back_populates='cabinet',
        cascade='all, delete-orphan',
        lazy='dynamic',
        order_by='StructureComponent.sort_order',
    )

    def to_dict(self, include_components: bool = False) -> dict:
        data = {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'control_category': self.control_category,
            'cabinet_type': self.cabinet_type,
            'control_structure': self.control_structure,
            'quotation_mode': self.quotation_mode,
            'sort_order': self.sort_order,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_components:
            data['structure_components'] = [
                sc.to_dict(include_base_components=True)
                for sc in self.structure_components
            ]
        return data

    def __repr__(self):
        return f'<Cabinet {self.id}: {self.name} (project={self.project_id})>'
