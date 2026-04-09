from flask import Blueprint, request, g, jsonify

from ..utils.decorators import require_auth
from ..services.project_service import ProjectService, ConflictError

components_bp = Blueprint('components', __name__, url_prefix='/api')
_svc = ProjectService()


def _ok(data):
    return jsonify({"code": 0, "data": data, "message": "ok"}), 200


def _created(data):
    return jsonify({"code": 0, "data": data, "message": "ok"}), 201


# ── StructureComponent ────────────────────────────────────────────────────────

@components_bp.route('/structure-components', methods=['POST'])
@require_auth
def create_structure_component():
    body = request.get_json(silent=True) or {}
    cabinet_id = body.get('cabinet_id')
    name = body.get('name', '')
    sort_order = body.get('sort_order', 0)

    if not cabinet_id:
        return jsonify({"code": 422, "data": None, "message": "缺少 cabinet_id"}), 422

    try:
        sc = _svc.create_structure_component(cabinet_id=cabinet_id, name=name, sort_order=sort_order)
    except LookupError as e:
        return jsonify({"code": 404, "data": None, "message": str(e)}), 404
    except ValueError as e:
        return jsonify({"code": 422, "data": None, "message": str(e)}), 422

    return _created(sc.to_dict())


@components_bp.route('/structure-components/<int:sc_id>', methods=['PUT'])
@require_auth
def update_structure_component(sc_id):
    body = request.get_json(silent=True) or {}
    version = body.get('version')
    if version is None:
        return jsonify({"code": 422, "data": None, "message": "缺少 version 字段"}), 422

    fields = {k: v for k, v in body.items() if k != 'version'}
    try:
        sc = _svc.update_structure_component(sc_id, version, **fields)
    except LookupError as e:
        return jsonify({"code": 404, "data": None, "message": str(e)}), 404
    except ConflictError as e:
        return jsonify({"code": 409, "data": e.current_data, "message": str(e)}), 409
    except ValueError as e:
        return jsonify({"code": 422, "data": None, "message": str(e)}), 422

    return _ok(sc.to_dict())


@components_bp.route('/structure-components/<int:sc_id>', methods=['DELETE'])
@require_auth
def delete_structure_component(sc_id):
    try:
        _svc.delete_structure_component(sc_id)
    except LookupError as e:
        return jsonify({"code": 404, "data": None, "message": str(e)}), 404
    return _ok(None)


# ── BaseComponent ─────────────────────────────────────────────────────────────

@components_bp.route('/base-components', methods=['POST'])
@require_auth
def create_base_component():
    body = request.get_json(silent=True) or {}
    sc_id = body.get('structure_component_id')
    if not sc_id:
        return jsonify({"code": 422, "data": None, "message": "缺少 structure_component_id"}), 422

    try:
        bc = _svc.create_base_component(
            sc_id=sc_id,
            model_number=body.get('model_number'),
            name=body.get('name'),
            quantity=body.get('quantity', 1),
            unit_price=body.get('unit_price', 0),
            discount_rate=body.get('discount_rate', 1.0),
            specification=body.get('specification'),
            material_id=body.get('material_id'),
            sort_order=body.get('sort_order', 0),
        )
    except LookupError as e:
        return jsonify({"code": 404, "data": None, "message": str(e)}), 404
    except ValueError as e:
        return jsonify({"code": 422, "data": None, "message": str(e)}), 422

    return _created(bc.to_dict())


@components_bp.route('/base-components/<int:bc_id>', methods=['PUT'])
@require_auth
def update_base_component(bc_id):
    body = request.get_json(silent=True) or {}
    version = body.get('version')
    if version is None:
        return jsonify({"code": 422, "data": None, "message": "缺少 version 字段"}), 422

    fields = {k: v for k, v in body.items() if k != 'version'}
    try:
        bc = _svc.update_base_component(bc_id, version, **fields)
    except LookupError as e:
        return jsonify({"code": 404, "data": None, "message": str(e)}), 404
    except ConflictError as e:
        return jsonify({"code": 409, "data": e.current_data, "message": str(e)}), 409
    except ValueError as e:
        return jsonify({"code": 422, "data": None, "message": str(e)}), 422

    return _ok(bc.to_dict())


@components_bp.route('/base-components/<int:bc_id>', methods=['DELETE'])
@require_auth
def delete_base_component(bc_id):
    try:
        _svc.delete_base_component(bc_id)
    except LookupError as e:
        return jsonify({"code": 404, "data": None, "message": str(e)}), 404
    return _ok(None)


@components_bp.route('/base-components/batch', methods=['POST'])
@require_auth
def batch_base_components():
    body = request.get_json(silent=True) or {}
    action = body.get('action')
    ids = body.get('ids', [])

    if not ids:
        return jsonify({"code": 422, "data": None, "message": "ids 不能为空"}), 422

    if action == 'delete':
        try:
            _svc.batch_delete_base_components(ids)
        except Exception as e:
            return jsonify({"code": 500, "data": None, "message": str(e)}), 500
        return _ok(None)

    elif action == 'update':
        fields = {k: v for k, v in body.items() if k not in ('action', 'ids')}
        try:
            components = _svc.batch_update_base_components(ids, **fields)
        except ValueError as e:
            return jsonify({"code": 422, "data": None, "message": str(e)}), 422
        except Exception as e:
            return jsonify({"code": 500, "data": None, "message": str(e)}), 500
        return _ok([bc.to_dict() for bc in components])

    else:
        return jsonify({"code": 422, "data": None, "message": "action 必须为 update 或 delete"}), 422
