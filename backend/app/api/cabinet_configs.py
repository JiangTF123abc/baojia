"""
柜体配置 API
管理柜体类型配置、自动匹配规则和人工费用规则
"""
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import CabinetTypeConfig, AutoMatchRule, LaborCostRule
from ..utils.decorators import require_auth, require_role

bp = Blueprint('cabinet_configs', __name__, url_prefix='/api/cabinet-type-configs')


@bp.route('', methods=['GET'])
@require_auth
def get_cabinet_type_configs():
    """
    获取柜体类型配置列表
    
    Query Parameters:
        - is_active: 是否只返回激活的配置（默认 true）
        - include_rules: 是否包含规则详情（默认 false）
    """
    is_active = request.args.get('is_active', 'true').lower() == 'true'
    include_rules = request.args.get('include_rules', 'false').lower() == 'true'

    query = CabinetTypeConfig.query
    if is_active:
        query = query.filter_by(is_active=True)

    configs = query.order_by(
        CabinetTypeConfig.control_category,
        CabinetTypeConfig.cabinet_type,
        CabinetTypeConfig.control_structure
    ).all()

    return jsonify({
        'configs': [config.to_dict(include_rules=include_rules) for config in configs],
        'total': len(configs)
    }), 200


@bp.route('/<int:config_id>', methods=['GET'])
@require_auth
def get_cabinet_type_config(config_id):
    """获取单个柜体类型配置"""
    config = CabinetTypeConfig.query.get_or_404(config_id)
    include_rules = request.args.get('include_rules', 'true').lower() == 'true'
    return jsonify(config.to_dict(include_rules=include_rules)), 200


@bp.route('/<int:config_id>/auto-match-rules', methods=['GET'])
@require_auth
def get_auto_match_rules(config_id):
    """获取指定配置的自动匹配规则"""
    config = CabinetTypeConfig.query.get_or_404(config_id)
    
    rules = AutoMatchRule.query.filter_by(
        cabinet_type_config_id=config_id
    ).order_by(AutoMatchRule.match_priority.desc()).all()

    return jsonify({
        'config': config.to_dict(include_rules=False),
        'rules': [rule.to_dict() for rule in rules],
        'total': len(rules)
    }), 200


@bp.route('', methods=['POST'])
@require_auth
@require_role('admin')
def create_cabinet_type_config():
    """
    创建柜体类型配置（管理员）
    
    Request Body:
        {
            "control_category": str,
            "cabinet_type": str,
            "control_structure": str,
            "description": str (optional)
        }
    """
    data = request.get_json()

    # 验证必填字段
    required_fields = ['control_category', 'cabinet_type', 'control_structure']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'缺少必填字段: {field}'}), 422

    # 检查是否已存在相同配置
    existing = CabinetTypeConfig.query.filter_by(
        control_category=data['control_category'],
        cabinet_type=data['cabinet_type'],
        control_structure=data['control_structure']
    ).first()

    if existing:
        return jsonify({'error': '该柜体类型配置已存在'}), 409

    # 创建配置
    config = CabinetTypeConfig(
        control_category=data['control_category'],
        cabinet_type=data['cabinet_type'],
        control_structure=data['control_structure'],
        description=data.get('description'),
        is_active=True
    )

    db.session.add(config)
    db.session.commit()

    return jsonify(config.to_dict()), 201


@bp.route('/<int:config_id>', methods=['PUT'])
@require_auth
@require_role('admin')
def update_cabinet_type_config(config_id):
    """
    更新柜体类型配置（管理员）
    
    Request Body:
        {
            "description": str (optional),
            "is_active": bool (optional)
        }
    """
    config = CabinetTypeConfig.query.get_or_404(config_id)
    data = request.get_json()

    # 只允许更新描述和激活状态
    if 'description' in data:
        config.description = data['description']
    if 'is_active' in data:
        config.is_active = bool(data['is_active'])

    db.session.commit()

    return jsonify(config.to_dict()), 200


@bp.route('/<int:config_id>', methods=['DELETE'])
@require_auth
@require_role('admin')
def delete_cabinet_type_config(config_id):
    """删除柜体类型配置（管理员）"""
    config = CabinetTypeConfig.query.get_or_404(config_id)
    
    db.session.delete(config)
    db.session.commit()

    return jsonify({'message': '配置已删除'}), 200


@bp.route('/search', methods=['GET'])
@require_auth
def search_cabinet_type_config():
    """
    搜索柜体类型配置
    
    Query Parameters:
        - control_category: 控制大类
        - cabinet_type: 柜体类型
        - control_structure: 控制结构
    """
    control_category = request.args.get('control_category')
    cabinet_type = request.args.get('cabinet_type')
    control_structure = request.args.get('control_structure')

    if not all([control_category, cabinet_type, control_structure]):
        return jsonify({'error': '缺少搜索参数'}), 422

    config = CabinetTypeConfig.query.filter_by(
        control_category=control_category,
        cabinet_type=cabinet_type,
        control_structure=control_structure,
        is_active=True
    ).first()

    if not config:
        return jsonify({'config': None}), 404

    include_rules = request.args.get('include_rules', 'true').lower() == 'true'
    return jsonify({'config': config.to_dict(include_rules=include_rules)}), 200
