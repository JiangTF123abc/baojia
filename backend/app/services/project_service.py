from decimal import Decimal
from datetime import date
from typing import Optional

from ..extensions import db
from ..models.project import Project
from ..models.cabinet import Cabinet
from ..models.structure_component import StructureComponent
from ..models.base_component import BaseComponent


class ConflictError(Exception):
    """乐观锁冲突"""
    def __init__(self, message="数据已被其他用户修改，请刷新后重试", current_data=None):
        super().__init__(message)
        self.current_data = current_data


class ProjectService:

    # ── Project CRUD ──────────────────────────────────────────────────────────

    def create_project(self, name: str, customer: str = None,
                       project_date=None, notes: str = None,
                       created_by: int = None) -> Project:
        if not name or not name.strip():
            raise ValueError("项目名称不能为空")
        project = Project(
            name=name.strip(),
            customer=customer,
            project_date=project_date,
            notes=notes,
            created_by=created_by,
        )
        try:
            db.session.add(project)
            db.session.commit()
            return project
        except Exception:
            db.session.rollback()
            raise

    def get_project(self, project_id: int) -> Optional[Project]:
        return Project.query.get(project_id)

    def get_project_tree(self, project_id: int) -> dict:
        project = self.get_project(project_id)
        if project is None:
            return None
        return project.to_dict(include_cabinets=True)

    def list_projects(self, user_id: int = None, role: str = None) -> list:
        if role == 'admin':
            return Project.query.order_by(Project.created_at.desc()).all()
        if user_id is not None:
            return (Project.query
                    .filter_by(created_by=user_id)
                    .order_by(Project.created_at.desc())
                    .all())
        return Project.query.order_by(Project.created_at.desc()).all()

    def update_project(self, project_id: int, version: int, **fields) -> Project:
        project = Project.query.get(project_id)
        if project is None:
            raise LookupError(f"项目 {project_id} 不存在")
        if project.version != version:
            raise ConflictError(current_data=project.to_dict())
        allowed = {'name', 'customer', 'project_date', 'notes'}
        for key, value in fields.items():
            if key in allowed:
                setattr(project, key, value)
        project.version = version + 1
        try:
            db.session.commit()
            return project
        except Exception:
            db.session.rollback()
            raise

    def delete_project(self, project_id: int) -> None:
        project = Project.query.get(project_id)
        if project is None:
            raise LookupError(f"项目 {project_id} 不存在")
        try:
            db.session.delete(project)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    # ── Cabinet CRUD ──────────────────────────────────────────────────────────

    def create_cabinet(self, project_id: int, name: str, sort_order: int = 0, 
                      control_category: str = None, cabinet_type: str = None,
                      control_structure: str = None, quotation_mode: str = 'detailed') -> Cabinet:
        if not name or not name.strip():
            raise ValueError("配电柜名称不能为空")
        project = Project.query.get(project_id)
        if project is None:
            raise LookupError(f"项目 {project_id} 不存在")
        cabinet = Cabinet(
            project_id=project_id, 
            name=name.strip(), 
            sort_order=sort_order,
            control_category=control_category,
            cabinet_type=cabinet_type,
            control_structure=control_structure,
            quotation_mode=quotation_mode
        )
        try:
            db.session.add(cabinet)
            db.session.commit()
            return cabinet
        except Exception:
            db.session.rollback()
            raise

    def get_cabinet(self, cabinet_id: int) -> Optional[Cabinet]:
        """获取单个柜体"""
        return Cabinet.query.get(cabinet_id)

    def update_cabinet(self, cabinet_id: int, version: int, **fields) -> Cabinet:
        cabinet = Cabinet.query.get(cabinet_id)
        if cabinet is None:
            raise LookupError(f"配电柜 {cabinet_id} 不存在")
        if cabinet.version != version:
            raise ConflictError(current_data=cabinet.to_dict())
        allowed = {'name', 'sort_order'}
        for key, value in fields.items():
            if key in allowed:
                setattr(cabinet, key, value)
        cabinet.version = version + 1
        try:
            db.session.commit()
            return cabinet
        except Exception:
            db.session.rollback()
            raise

    def delete_cabinet(self, cabinet_id: int) -> None:
        cabinet = Cabinet.query.get(cabinet_id)
        if cabinet is None:
            raise LookupError(f"配电柜 {cabinet_id} 不存在")
        try:
            db.session.delete(cabinet)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    # ── StructureComponent CRUD ───────────────────────────────────────────────

    def create_structure_component(self, cabinet_id: int, name: str,
                                   sort_order: int = 0) -> StructureComponent:
        if not name or not name.strip():
            raise ValueError("结构组件名称不能为空")
        cabinet = Cabinet.query.get(cabinet_id)
        if cabinet is None:
            raise LookupError(f"配电柜 {cabinet_id} 不存在")
        sc = StructureComponent(cabinet_id=cabinet_id, name=name.strip(), sort_order=sort_order)
        try:
            db.session.add(sc)
            db.session.commit()
            return sc
        except Exception:
            db.session.rollback()
            raise

    def update_structure_component(self, sc_id: int, version: int, **fields) -> StructureComponent:
        sc = StructureComponent.query.get(sc_id)
        if sc is None:
            raise LookupError(f"结构组件 {sc_id} 不存在")
        if sc.version != version:
            raise ConflictError(current_data=sc.to_dict())
        allowed = {'name', 'sort_order'}
        for key, value in fields.items():
            if key in allowed:
                setattr(sc, key, value)
        sc.version = version + 1
        try:
            db.session.commit()
            return sc
        except Exception:
            db.session.rollback()
            raise

    def delete_structure_component(self, sc_id: int) -> None:
        sc = StructureComponent.query.get(sc_id)
        if sc is None:
            raise LookupError(f"结构组件 {sc_id} 不存在")
        try:
            db.session.delete(sc)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    # ── BaseComponent CRUD ────────────────────────────────────────────────────

    def create_base_component(self, sc_id: int, model_number: str, name: str,
                               quantity, unit_price, discount_rate=Decimal('1.0'),
                               specification: str = None, material_id: int = None,
                               sort_order: int = 0) -> BaseComponent:
        if Decimal(str(quantity)) <= 0:
            raise ValueError("数量必须大于 0")
        if Decimal(str(unit_price)) < 0:
            raise ValueError("单价不能为负数")
        sc = StructureComponent.query.get(sc_id)
        if sc is None:
            raise LookupError(f"结构组件 {sc_id} 不存在")
        bc = BaseComponent(
            structure_component_id=sc_id,
            model_number=model_number,
            name=name,
            quantity=Decimal(str(quantity)),
            unit_price=Decimal(str(unit_price)),
            discount_rate=Decimal(str(discount_rate)),
            specification=specification,
            material_id=material_id,
            sort_order=sort_order,
        )
        try:
            db.session.add(bc)
            db.session.commit()
            return bc
        except Exception:
            db.session.rollback()
            raise

    def update_base_component(self, bc_id: int, version: int, **fields) -> BaseComponent:
        bc = BaseComponent.query.get(bc_id)
        if bc is None:
            raise LookupError(f"基础元器件 {bc_id} 不存在")
        if bc.version != version:
            raise ConflictError(current_data=bc.to_dict())
        allowed = {'model_number', 'name', 'specification', 'quantity',
                   'unit_price', 'discount_rate', 'material_id', 'sort_order'}
        for key, value in fields.items():
            if key in allowed:
                if key in ('quantity', 'unit_price', 'discount_rate') and value is not None:
                    value = Decimal(str(value))
                setattr(bc, key, value)
        bc.version = version + 1
        try:
            db.session.commit()
            return bc
        except Exception:
            db.session.rollback()
            raise

    def delete_base_component(self, bc_id: int) -> None:
        bc = BaseComponent.query.get(bc_id)
        if bc is None:
            raise LookupError(f"基础元器件 {bc_id} 不存在")
        try:
            db.session.delete(bc)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def batch_update_base_components(self, bc_ids: list, **fields) -> list:
        components = BaseComponent.query.filter(BaseComponent.id.in_(bc_ids)).all()
        allowed = {'model_number', 'name', 'specification', 'quantity',
                   'unit_price', 'discount_rate', 'material_id', 'sort_order'}
        try:
            for bc in components:
                for key, value in fields.items():
                    if key in allowed:
                        if key in ('quantity', 'unit_price', 'discount_rate') and value is not None:
                            value = Decimal(str(value))
                        setattr(bc, key, value)
                bc.version += 1
            db.session.commit()
            return components
        except Exception:
            db.session.rollback()
            raise

    def batch_delete_base_components(self, bc_ids: list) -> None:
        try:
            BaseComponent.query.filter(BaseComponent.id.in_(bc_ids)).delete(
                synchronize_session='fetch'
            )
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    # ── Cabinet 复制与移动 ─────────────────────────────────────────────────────

    def copy_cabinet(self, cabinet_id: int) -> Cabinet:
        """深度复制 Cabinet，新 Cabinet 名称追加"(副本)"，保留所有子节点"""
        cabinet = Cabinet.query.get(cabinet_id)
        if cabinet is None:
            raise LookupError(f"配电柜 {cabinet_id} 不存在")

        new_cabinet = Cabinet(
            project_id=cabinet.project_id,
            name=cabinet.name + "(副本)",
            sort_order=cabinet.sort_order,
        )
        try:
            db.session.add(new_cabinet)
            db.session.flush()  # 获取 new_cabinet.id

            for sc in cabinet.structure_components.all():
                new_sc = StructureComponent(
                    cabinet_id=new_cabinet.id,
                    name=sc.name,
                    sort_order=sc.sort_order,
                )
                db.session.add(new_sc)
                db.session.flush()  # 获取 new_sc.id

                for bc in sc.base_components.all():
                    new_bc = BaseComponent(
                        structure_component_id=new_sc.id,
                        material_id=bc.material_id,
                        model_number=bc.model_number,
                        name=bc.name,
                        specification=bc.specification,
                        quantity=bc.quantity,
                        unit_price=bc.unit_price,
                        discount_rate=bc.discount_rate,
                        sort_order=bc.sort_order,
                    )
                    db.session.add(new_bc)

            db.session.commit()
            return new_cabinet
        except Exception:
            db.session.rollback()
            raise

    def move_cabinet(self, cabinet_id: int, target_project_id: int) -> Cabinet:
        """将 Cabinet 移动到目标 Project，事务内执行，失败时回滚"""
        cabinet = Cabinet.query.get(cabinet_id)
        if cabinet is None:
            raise LookupError(f"配电柜 {cabinet_id} 不存在")

        target_project = Project.query.get(target_project_id)
        if target_project is None:
            raise LookupError(f"项目 {target_project_id} 不存在")

        original_project_id = cabinet.project_id
        try:
            cabinet.project_id = target_project_id
            db.session.commit()
            return cabinet
        except Exception:
            db.session.rollback()
            cabinet.project_id = original_project_id
            raise
