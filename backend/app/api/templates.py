import os

from flask import Blueprint, request, jsonify, g, current_app

from ..utils.decorators import require_auth
from ..services.template_service import template_service, PermissionError
from ..services.bom_parser import bom_parser

templates_bp = Blueprint('templates', __name__, url_prefix='/api')


# ── 模板端点 ──────────────────────────────────────────────────────────────────

@templates_bp.route('/templates', methods=['GET'])
@require_auth
def list_templates():
    search = request.args.get('search', '').strip() or None
    user_id = g.current_user['user_id']
    # 管理员可查看所有模板，普通用户只看自己的
    role = g.current_user.get('role')
    uid = None if role == 'admin' else user_id
    templates = template_service.list_templates(user_id=uid, search=search)
    return jsonify({
        'code': 200,
        'data': [t.to_dict() for t in templates],
        'message': 'ok',
    })


@templates_bp.route('/templates', methods=['POST'])
@require_auth
def save_template():
    body = request.get_json(silent=True) or {}
    node_id = body.get('node_id')
    node_type = body.get('node_type')
    name = body.get('name', '').strip()
    description = body.get('description', '')

    if not node_id or not node_type:
        return jsonify({'code': 400, 'data': None, 'message': 'node_id 和 node_type 为必填项'}), 400
    if not name:
        return jsonify({'code': 400, 'data': None, 'message': '模板名称不能为空'}), 400

    user_id = g.current_user['user_id']
    try:
        template = template_service.save_as_template(
            node_id=int(node_id),
            node_type=node_type,
            name=name,
            description=description,
            user_id=user_id,
        )
        return jsonify({'code': 201, 'data': template.to_dict(), 'message': '模板保存成功'}), 201
    except LookupError as e:
        return jsonify({'code': 404, 'data': None, 'message': str(e)}), 404
    except ValueError as e:
        return jsonify({'code': 400, 'data': None, 'message': str(e)}), 400


@templates_bp.route('/templates/<int:template_id>/apply', methods=['POST'])
@require_auth
def apply_template(template_id: int):
    body = request.get_json(silent=True) or {}
    target_project_id = body.get('target_project_id')
    if not target_project_id:
        return jsonify({'code': 400, 'data': None, 'message': 'target_project_id 为必填项'}), 400

    try:
        node = template_service.apply_template(
            template_id=template_id,
            target_project_id=int(target_project_id),
        )
        return jsonify({'code': 200, 'data': node.to_dict(), 'message': '模板应用成功'})
    except LookupError as e:
        return jsonify({'code': 404, 'data': None, 'message': str(e)}), 404
    except ValueError as e:
        return jsonify({'code': 400, 'data': None, 'message': str(e)}), 400


@templates_bp.route('/templates/<int:template_id>', methods=['PUT'])
@require_auth
def update_template(template_id: int):
    body = request.get_json(silent=True) or {}
    user_id = g.current_user['user_id']
    fields = {k: v for k, v in body.items() if k in ('name', 'description')}
    if not fields:
        return jsonify({'code': 400, 'data': None, 'message': '没有可更新的字段'}), 400

    try:
        template = template_service.update_template(template_id, user_id, **fields)
        return jsonify({'code': 200, 'data': template.to_dict(), 'message': '更新成功'})
    except LookupError as e:
        return jsonify({'code': 404, 'data': None, 'message': str(e)}), 404
    except PermissionError as e:
        return jsonify({'code': 403, 'data': None, 'message': str(e)}), 403


@templates_bp.route('/templates/<int:template_id>', methods=['DELETE'])
@require_auth
def delete_template(template_id: int):
    user_id = g.current_user['user_id']
    try:
        template_service.delete_template(template_id, user_id)
        return jsonify({'code': 200, 'data': None, 'message': '删除成功'})
    except LookupError as e:
        return jsonify({'code': 404, 'data': None, 'message': str(e)}), 404
    except PermissionError as e:
        return jsonify({'code': 403, 'data': None, 'message': str(e)}), 403


# ── BOM 端点 ──────────────────────────────────────────────────────────────────

@templates_bp.route('/bom/upload', methods=['POST'])
@require_auth
def upload_bom():
    if 'file' not in request.files:
        return jsonify({'code': 400, 'data': None, 'message': '缺少 file 字段'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'code': 400, 'data': None, 'message': '文件名为空'}), 400

    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    # 安全保存文件
    from werkzeug.utils import secure_filename
    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    try:
        result = bom_parser.parse_excel(file_path)
        return jsonify({'code': 200, 'data': result, 'message': 'BOM 解析成功'})
    except Exception as e:
        return jsonify({'code': 400, 'data': None, 'message': f'BOM 解析失败: {str(e)}'}), 400
    finally:
        # 解析完成后删除临时文件
        if os.path.exists(file_path):
            os.remove(file_path)


@templates_bp.route('/bom/import', methods=['POST'])
@require_auth
def import_bom():
    body = request.get_json(silent=True) or {}
    rows = body.get('rows')
    target_sc_id = body.get('target_sc_id')

    if not rows or not isinstance(rows, list):
        return jsonify({'code': 400, 'data': None, 'message': 'rows 为必填项且须为列表'}), 400
    if not target_sc_id:
        return jsonify({'code': 400, 'data': None, 'message': 'target_sc_id 为必填项'}), 400

    try:
        components = bom_parser.import_bom(rows=rows, target_sc_id=int(target_sc_id))
        return jsonify({
            'code': 201,
            'data': [bc.to_dict() for bc in components],
            'message': f'成功导入 {len(components)} 条元器件',
        }), 201
    except LookupError as e:
        return jsonify({'code': 404, 'data': None, 'message': str(e)}), 404
    except Exception as e:
        return jsonify({'code': 400, 'data': None, 'message': str(e)}), 400
