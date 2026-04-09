import json
from decimal import Decimal

from ..extensions import db
from ..models.template import Template
from ..models.cabinet import Cabinet
from ..models.structure_component import StructureComponent
from ..models.base_component import BaseComponent
from ..models.material import Material
from ..models.project import Project


class PermissionError(Exception):
    """权限不足"""


class TemplateService:

    def _serialize_cabinet(self, cabinet: Cabinet) -> dict:
        return {
            "type": "cabinet",
            "name": cabinet.name,
            "structure_components": [
                {
                    "name": sc.name,
                    "base_components": [
                        {
                            "model_number": bc.model_number,
                            "name": bc.name,
                            "quantity": str(bc.quantity) if bc.quantity is not None else "1.0000",
                            "unit_price": str(bc.unit_price) if bc.unit_price is not None else "0.0000",
                            "discount_rate": str(bc.discount_rate) if bc.discount_rate is not None else "1.0000",
                            "specification": bc.specification,
                            "material_id": bc.material_id,
                        }
                        for bc in sc.base_components.all()
                    ],
                }
                for sc in cabinet.structure_components.all()
            ],
        }

    def _serialize_structure_component(self, sc: StructureComponent) -> dict:
        return {
            "type": "structure_component",
            "name": sc.name,
            "base_components": [
                {
                    "model_number": bc.model_number,
                    "name": bc.name,
                    "quantity": str(bc.quantity) if bc.quantity is not None else "1.0000",
                    "unit_price": str(bc.unit_price) if bc.unit_price is not None else "0.0000",
                    "discount_rate": str(bc.discount_rate) if bc.discount_rate is not None else "1.0000",
                    "specification": bc.specification,
                    "material_id": bc.material_id,
                }
                for bc in sc.base_components.all()
            ],
        }

    def _resolve_unit_price(self, bc_data: dict) -> Decimal:
        material_id = bc_data.get("material_id")
        if material_id:
            material = Material.query.get(material_id)
            if material and material.unit_price is not None:
                return material.unit_price
        return Decimal(bc_data.get("unit_price") or "0.0000")

    def _create_bc_from_data(self, sc_id: int, bc_data: dict, sort_order: int) -> BaseComponent:
        bc = BaseComponent(
            structure_component_id=sc_id,
            model_number=bc_data.get("model_number"),
            name=bc_data.get("name"),
            quantity=Decimal(bc_data.get("quantity") or "1.0000"),
            unit_price=self._resolve_unit_price(bc_data),
            discount_rate=Decimal(bc_data.get("discount_rate") or "1.0000"),
            specification=bc_data.get("specification"),
            material_id=bc_data.get("material_id"),
            sort_order=sort_order,
        )
        db.session.add(bc)
        return bc

    def save_as_template(self, node_id: int, node_type: str, name: str,
                         description: str, user_id: int) -> Template:
        if node_type == "cabinet":
            node = Cabinet.query.get(node_id)
            if node is None:
                raise LookupError(f"配电柜 {node_id} 不存在")
            data = self._serialize_cabinet(node)
        elif node_type == "structure_component":
            node = StructureComponent.query.get(node_id)
            if node is None:
                raise LookupError(f"结构组件 {node_id} 不存在")
            data = self._serialize_structure_component(node)
        else:
            raise ValueError(f"不支持的节点类型: {node_type}")

        template = Template(
            name=name,
            description=description,
            source_type=node_type,
            template_data=json.dumps(data, ensure_ascii=False),
            created_by=user_id,
        )
        try:
            db.session.add(template)
            db.session.commit()
            return template
        except Exception:
            db.session.rollback()
            raise

    def apply_template(self, template_id: int, target_project_id: int) -> object:
        template = Template.query.get(template_id)
        if template is None:
            raise LookupError(f"模板 {template_id} 不存在")
        project = Project.query.get(target_project_id)
        if project is None:
            raise LookupError(f"项目 {target_project_id} 不存在")

        data = json.loads(template.template_data)
        node_type = data.get("type")

        try:
            if node_type == "cabinet":
                cabinet = Cabinet(project_id=target_project_id, name=data["name"], sort_order=0)
                db.session.add(cabinet)
                db.session.flush()
                for sc_idx, sc_data in enumerate(data.get("structure_components", [])):
                    sc = StructureComponent(cabinet_id=cabinet.id, name=sc_data["name"], sort_order=sc_idx)
                    db.session.add(sc)
                    db.session.flush()
                    for bc_idx, bc_data in enumerate(sc_data.get("base_components", [])):
                        self._create_bc_from_data(sc.id, bc_data, bc_idx)
                db.session.commit()
                return cabinet
            elif node_type == "structure_component":
                cabinet = Cabinet(project_id=target_project_id, name=data["name"], sort_order=0)
                db.session.add(cabinet)
                db.session.flush()
                sc = StructureComponent(cabinet_id=cabinet.id, name=data["name"], sort_order=0)
                db.session.add(sc)
                db.session.flush()
                for bc_idx, bc_data in enumerate(data.get("base_components", [])):
                    self._create_bc_from_data(sc.id, bc_data, bc_idx)
                db.session.commit()
                return sc
            else:
                raise ValueError(f"模板数据类型无效: {node_type}")
        except Exception:
            db.session.rollback()
            raise

    def list_templates(self, user_id: int = None, search: str = None) -> list:
        query = Template.query
        if user_id is not None:
            query = query.filter_by(created_by=user_id)
        if search:
            query = query.filter(Template.name.ilike(f"%{search}%"))
        return query.order_by(Template.created_at.desc()).all()

    def get_template(self, template_id: int):
        return Template.query.get(template_id)

    def update_template(self, template_id: int, user_id: int, **fields) -> Template:
        template = Template.query.get(template_id)
        if template is None:
            raise LookupError(f"模板 {template_id} 不存在")
        if template.created_by != user_id:
            raise PermissionError("只有创建者可以更新模板")
        for key, value in fields.items():
            if key in ("name", "description"):
                setattr(template, key, value)
        template.version += 1
        try:
            db.session.commit()
            return template
        except Exception:
            db.session.rollback()
            raise

    def delete_template(self, template_id: int, user_id: int) -> None:
        template = Template.query.get(template_id)
        if template is None:
            raise LookupError(f"模板 {template_id} 不存在")
        if template.created_by != user_id:
            raise PermissionError("只有创建者可以删除模板")
        try:
            db.session.delete(template)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise


template_service = TemplateService()
