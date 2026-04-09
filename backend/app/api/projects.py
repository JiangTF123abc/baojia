from datetime import date

from flask import Blueprint, request, g, jsonify

from ..utils.decorators import require_auth
from ..services.project_service import ProjectService, ConflictError

projects_bp = Blueprint('projects', __name__, url_prefix='/api')
_svc = ProjectService()


def _ok(data):
    return jsonify({"code": 0, "data": data, "message": "ok"}), 200


def _created(data):
    return jsonify({"code": 0, "data": data, "message": "ok"}), 201


@projects_bp.route('/projects', methods=['GET'])
@require_auth
def list_projects():
    user = g.current_user
    projects = _svc.list_projects(user_id=user['user_id'], role=user['role'])
    return _ok([p.to_dict() for p in projects])


@projects_bp.route('/projects', methods=['POST'])
@require_auth
def create_project():
    try:
        body = request.get_json(silent=True) or {}
        name = body.get('name', '')
        customer = body.get('customer')
        notes = body.get('notes')
        project_date_str = body.get('project_date')
        project_date = None
        if project_date_str:
            try:
                project_date = date.fromisoformat(project_date_str)
            except ValueError:
                return jsonify({"code": 422, "data": None, "message": "project_date 格式无效，应为 YYYY-MM-DD"}), 422

        try:
            project = _svc.create_project(
                name=name,
                customer=customer,
                project_date=project_date,
                notes=notes,
                created_by=g.current_user['user_id'],
            )
        except ValueError as e:
            return jsonify({"code": 422, "data": None, "message": str(e)}), 422

        return _created(project.to_dict())
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"code": 500, "data": None, "message": f"服务器错误: {str(e)}"}), 500


@projects_bp.route('/projects/<int:project_id>/tree', methods=['GET'])
@require_auth
def get_project_tree(project_id):
    try:
        tree = _svc.get_project_tree(project_id)
        if tree is None:
            return jsonify({"code": 404, "data": None, "message": "项目不存在"}), 404
        return _ok(tree)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"code": 500, "data": None, "message": f"服务器错误: {str(e)}"}), 500


@projects_bp.route('/projects/<int:project_id>', methods=['PUT'])
@require_auth
def update_project(project_id):
    body = request.get_json(silent=True) or {}
    version = body.get('version')
    if version is None:
        return jsonify({"code": 422, "data": None, "message": "缺少 version 字段"}), 422

    project_date_str = body.get('project_date')
    if project_date_str is not None:
        try:
            body['project_date'] = date.fromisoformat(project_date_str)
        except ValueError:
            return jsonify({"code": 422, "data": None, "message": "project_date 格式无效"}), 422

    fields = {k: v for k, v in body.items() if k != 'version'}
    try:
        project = _svc.update_project(project_id, version, **fields)
    except LookupError as e:
        return jsonify({"code": 404, "data": None, "message": str(e)}), 404
    except ConflictError as e:
        return jsonify({"code": 409, "data": e.current_data, "message": str(e)}), 409
    except ValueError as e:
        return jsonify({"code": 422, "data": None, "message": str(e)}), 422

    return _ok(project.to_dict())


@projects_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@require_auth
def delete_project(project_id):
    try:
        _svc.delete_project(project_id)
    except LookupError as e:
        return jsonify({"code": 404, "data": None, "message": str(e)}), 404
    return _ok(None)
