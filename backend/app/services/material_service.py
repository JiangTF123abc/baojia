from ..extensions import db
from ..models.material import Material
from ..models.material_accessory import MaterialAccessory


class MaterialService:

    def search_materials(self, query: str, limit: int = 20, category: str = None) -> list:
        """模糊搜索材料（型号、名称、规格），只返回 is_active=True，最多 limit 条"""
        if not query:
            return []
        limit = min(limit, 20)
        pattern = f'%{query}%'
        
        # 构建查询条件
        conditions = [
            Material.is_active == True,
            db.or_(
                Material.model_number.ilike(pattern),
                Material.name.ilike(pattern),
                Material.specification.ilike(pattern),
            )
        ]
        
        # 如果指定了分类，添加分类过滤
        if category:
            conditions.append(Material.component_type == category)
        
        results = (
            Material.query
            .filter(*conditions)
            .limit(limit)
            .all()
        )
        return [m.to_dict() for m in results]

    def get_accessories(self, material_id: int) -> list:
        """获取材料的关联附件列表"""
        links = MaterialAccessory.query.filter_by(material_id=material_id).all()
        result = []
        for link in links:
            accessory = Material.query.get(link.accessory_id)
            if accessory and accessory.is_active:
                result.append({
                    "accessory": accessory.to_dict(),
                    "is_required": link.is_required,
                    "default_quantity": str(link.default_quantity),
                })
        return result

    def get_material(self, material_id: int):
        """根据 ID 获取材料"""
        return Material.query.get(material_id)


material_service = MaterialService()
