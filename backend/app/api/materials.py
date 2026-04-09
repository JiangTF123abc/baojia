from flask import Blueprint, request, jsonify

from ..utils.decorators import require_auth
from ..services.material_service import material_service

materials_bp = Blueprint('materials', __name__, url_prefix='/api')


@materials_bp.get('/materials/search')
@require_auth
def search_materials():
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()  # 新增：按分类过滤
    try:
        limit = int(request.args.get('limit', 20))
    except (ValueError, TypeError):
        limit = 20
    data = material_service.search_materials(query, limit, category=category if category else None)
    return jsonify({"code": 0, "data": data, "message": "ok"})


@materials_bp.get('/materials/<int:material_id>/accessories')
@require_auth
def get_accessories(material_id: int):
    material = material_service.get_material(material_id)
    if not material:
        return jsonify({"code": 404, "data": None, "message": "材料不存在"}), 404
    data = material_service.get_accessories(material_id)
    return jsonify({"code": 0, "data": data, "message": "ok"})
