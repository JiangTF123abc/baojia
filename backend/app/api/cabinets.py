from flask import Blueprint, request, g, jsonify

from ..utils.decorators import require_auth
from ..services.project_service import ProjectService, ConflictError
from ..services.auto_match_service import AutoMatchService

cabinets_bp = Blueprint('cabinets', __name__, url_prefix='/api')
_svc = ProjectService()
_auto_match_svc = AutoMatchService()


def _ok(data):
    return jsonify({"code": 0, "data": data, "message": "ok"}), 200


def _created(data):
    return jsonify({"code": 0, "data": data, "message": "ok"}), 201


@cabinets_bp.route('/cabinets', methods=['POST'])
@require_auth
def create_cabinet():
    body = request.get_json(silent=True) or {}
    project_id = body.get('project_id')
    name = body.get('name', '')
    sort_order = body.get('sort_order', 0)
    
    # 新增字段支持
    control_category = body.get('control_category')
    cabinet_type = body.get('cabinet_type')
    control_structure = body.get('control_structure')
    quotation_mode = body.get('quotation_mode', 'detailed')

    if not project_id:
        return jsonify({"code": 422, "data": None, "message": "缺少 project_id"}), 422

    try:
        cabinet = _svc.create_cabinet(
            project_id=project_id, 
            name=name, 
            sort_order=sort_order,
            control_category=control_category,
            cabinet_type=cabinet_type,
            control_structure=control_structure,
            quotation_mode=quotation_mode
        )
        
        # 如果是快速报价模式，自动触发匹配
        if quotation_mode == 'quick' and control_category and cabinet_type and control_structure:
            try:
                _auto_match_svc.apply_auto_match(cabinet)
                _auto_match_svc.apply_auto_hide_rules(cabinet)
            except Exception as e:
                # 自动匹配失败不影响柜体创建，只记录日志
                import logging
                logging.warning(f"自动匹配失败: {str(e)}")
                
    except LookupError as e:
        return jsonify({"code": 404, "data": None, "message": str(e)}), 404
    except ValueError as e:
        return jsonify({"code": 422, "data": None, "message": str(e)}), 422

    return _created(cabinet.to_dict())


@cabinets_bp.route('/cabinets/<int:cabinet_id>', methods=['PUT'])
@require_auth
def update_cabinet(cabinet_id):
    body = request.get_json(silent=True) or {}
    version = body.get('version')
    if version is None:
        return jsonify({"code": 422, "data": None, "message": "缺少 version 字段"}), 422

    fields = {k: v for k, v in body.items() if k != 'version'}
    try:
        cabinet = _svc.update_cabinet(cabinet_id, version, **fields)
    except LookupError as e:
        return jsonify({"code": 404, "data": None, "message": str(e)}), 404
    except ConflictError as e:
        return jsonify({"code": 409, "data": e.current_data, "message": str(e)}), 409
    except ValueError as e:
        return jsonify({"code": 422, "data": None, "message": str(e)}), 422

    return _ok(cabinet.to_dict())


@cabinets_bp.route('/cabinets/<int:cabinet_id>', methods=['DELETE'])
@require_auth
def delete_cabinet(cabinet_id):
    try:
        _svc.delete_cabinet(cabinet_id)
    except LookupError as e:
        return jsonify({"code": 404, "data": None, "message": str(e)}), 404
    return _ok(None)


@cabinets_bp.route('/cabinets/<int:cabinet_id>/copy', methods=['POST'])
@require_auth
def copy_cabinet(cabinet_id):
    try:
        new_cabinet = _svc.copy_cabinet(cabinet_id)
    except LookupError as e:
        return jsonify({"code": 404, "data": None, "message": str(e)}), 404

    return _created(new_cabinet.to_dict())


@cabinets_bp.route('/cabinets/<int:cabinet_id>/move', methods=['PUT'])
@require_auth
def move_cabinet(cabinet_id):
    body = request.get_json(silent=True) or {}
    target_project_id = body.get('target_project_id')

    if not target_project_id:
        return jsonify({"code": 422, "data": None, "message": "缺少 target_project_id"}), 422

    try:
        cabinet = _svc.move_cabinet(cabinet_id, target_project_id)
    except LookupError as e:
        return jsonify({"code": 404, "data": None, "message": str(e)}), 404

    return _ok(cabinet.to_dict())


@cabinets_bp.route('/cabinets/<int:cabinet_id>/auto-match', methods=['POST'])
@require_auth
def trigger_auto_match(cabinet_id):
    """触发自动匹配"""
    try:
        cabinet = _svc.get_cabinet(cabinet_id)
        if not cabinet:
            return jsonify({"code": 404, "data": None, "message": "柜体不存在"}), 404
        
        # 应用自动匹配规则
        matched_count = _auto_match_svc.apply_auto_match(cabinet)
        
        # 应用自动隐藏规则
        _auto_match_svc.apply_auto_hide_rules(cabinet)
        
        return _ok({
            "cabinet_id": cabinet_id,
            "matched_count": matched_count,
            "message": f"成功匹配 {matched_count} 个元器件"
        })
    except LookupError as e:
        return jsonify({"code": 404, "data": None, "message": str(e)}), 404
    except ValueError as e:
        return jsonify({"code": 422, "data": None, "message": str(e)}), 422
    except Exception as e:
        import logging
        logging.error(f"自动匹配失败: {str(e)}")
        return jsonify({"code": 500, "data": None, "message": f"自动匹配失败: {str(e)}"}), 500


@cabinets_bp.route('/cabinets/<int:cabinet_id>/apply-hide-rules', methods=['POST'])
@require_auth
def apply_hide_rules(cabinet_id):
    """应用自动隐藏规则"""
    try:
        cabinet = _svc.get_cabinet(cabinet_id)
        if not cabinet:
            return jsonify({"code": 404, "data": None, "message": "柜体不存在"}), 404
        
        # 应用自动隐藏规则
        hidden_count = _auto_match_svc.apply_auto_hide_rules(cabinet)
        
        return _ok({
            "cabinet_id": cabinet_id,
            "hidden_count": hidden_count,
            "message": f"成功隐藏 {hidden_count} 个元器件"
        })
    except LookupError as e:
        return jsonify({"code": 404, "data": None, "message": str(e)}), 404
    except Exception as e:
        import logging
        logging.error(f"应用隐藏规则失败: {str(e)}")
        return jsonify({"code": 500, "data": None, "message": f"应用隐藏规则失败: {str(e)}"}), 500


@cabinets_bp.route('/cabinets/<int:cabinet_id>/auto-match-preview', methods=['GET'])
@require_auth
def get_auto_match_preview(cabinet_id):
    """获取自动匹配预览"""
    try:
        cabinet = _svc.get_cabinet(cabinet_id)
        if not cabinet:
            return jsonify({"code": 404, "data": None, "message": "柜体不存在"}), 404
        
        preview = _auto_match_svc.get_auto_match_preview(cabinet)
        
        return _ok(preview)
    except LookupError as e:
        return jsonify({"code": 404, "data": None, "message": str(e)}), 404
    except Exception as e:
        import logging
        logging.error(f"获取预览失败: {str(e)}")
        return jsonify({"code": 500, "data": None, "message": f"获取预览失败: {str(e)}"}), 500
