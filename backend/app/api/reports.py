from flask import Blueprint, request, jsonify

from ..models.price_formula import PriceFormula
from ..services.price_engine import price_engine
from ..services.labor_cost_service import LaborCostService
from ..services.project_service import ProjectService

reports_bp = Blueprint('reports', __name__, url_prefix='/api')
_labor_cost_svc = LaborCostService()
_project_svc = ProjectService()


@reports_bp.route('/price-engine/calculate', methods=['POST'])
def calculate_price():
    """后端价格验证端点"""
    data = request.get_json(silent=True) or {}

    quantity = data.get('quantity', 1)
    unit_price = data.get('unit_price', 0)
    discount_rate = data.get('discount_rate', 1)
    formula_str = data.get('formula_str')

    # 公式参数
    formula_params = {
        'loss_rate': data.get('loss_rate', 0),
        'tax_rate': data.get('tax_rate', 0),
        'aux_material_fee': data.get('aux_material_fee', 0),
        'labor_fee': data.get('labor_fee', 0),
    }

    base_price = price_engine.calculate_base_price(quantity, unit_price, discount_rate)
    final_price = price_engine.apply_formula(base_price, formula_str, **formula_params)

    return jsonify({"code": 0, "data": {"base_price": str(base_price), "final_price": final_price}, "message": "ok"})


@reports_bp.route('/price-formulas', methods=['GET'])
def list_price_formulas():
    """获取所有激活的价格公式列表"""
    formulas = PriceFormula.query.filter_by(is_active=True).all()
    return jsonify({"code": 0, "data": [f.to_dict() for f in formulas], "message": "ok"})


@reports_bp.route('/price-engine/calculate-labor', methods=['POST'])
def calculate_labor_cost():
    """计算人工费用"""
    from ..utils.decorators import require_auth
    
    data = request.get_json(silent=True) or {}
    cabinet_id = data.get('cabinet_id')
    base_cost = data.get('base_cost', 0)
    
    if not cabinet_id:
        return jsonify({"code": 422, "data": None, "message": "缺少 cabinet_id"}), 422
    
    try:
        cabinet = _project_svc.get_cabinet(cabinet_id)
        if not cabinet:
            return jsonify({"code": 404, "data": None, "message": "柜体不存在"}), 404
        
        # 计算人工费用
        labor_cost_detail = _labor_cost_svc.calculate_labor_cost(cabinet, float(base_cost))
        
        # 计算总价
        total_with_labor = _labor_cost_svc.calculate_cabinet_total_with_labor(cabinet)
        
        return jsonify({
            "code": 0, 
            "data": {
                "labor_cost_detail": labor_cost_detail,
                "total_with_labor": total_with_labor
            }, 
            "message": "ok"
        })
    except LookupError as e:
        return jsonify({"code": 404, "data": None, "message": str(e)}), 404
    except ValueError as e:
        return jsonify({"code": 422, "data": None, "message": str(e)}), 422
    except Exception as e:
        import logging
        logging.error(f"计算人工费用失败: {str(e)}")
        return jsonify({"code": 500, "data": None, "message": f"计算失败: {str(e)}"}), 500


# ── 审计日志端点 ──────────────────────────────────────────────────────────────

from datetime import datetime as _dt
from ..utils.decorators import require_auth, require_role
from ..services.audit_service import audit_service as _audit_service


@reports_bp.route('/audit-logs', methods=['GET'])
@require_auth
@require_role('admin')
def query_audit_logs():
    """查询审计日志（仅管理员）"""
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    user_id = request.args.get('user')
    entity_type = request.args.get('entity_type')
    action = request.args.get('action')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))

    start = _dt.fromisoformat(start_str) if start_str else None
    end = _dt.fromisoformat(end_str) if end_str else None

    result = _audit_service.query_logs(
        start=start, end=end,
        user_id=int(user_id) if user_id else None,
        entity_type=entity_type, action=action,
        page=page, per_page=per_page,
    )
    return jsonify({"code": 0, "data": result, "message": "ok"})


@reports_bp.route('/audit-logs/export', methods=['GET'])
@require_auth
@require_role('admin')
def export_audit_logs():
    """导出审计日志（仅管理员）"""
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    start = _dt.fromisoformat(start_str) if start_str else None
    end = _dt.fromisoformat(end_str) if end_str else None
    logs = _audit_service.export_logs(start=start, end=end)
    return jsonify({"code": 0, "data": logs, "message": "ok"})


# ── 报表生成端点 ──────────────────────────────────────────────────────────────

import os as _os
from flask import send_file as _send_file
from ..services.report_service import report_service as _report_service


@reports_bp.route('/reports/internal-pricing/<int:project_id>', methods=['POST'])
def generate_internal_pricing(project_id: int):
    """生成 Excel 核价单"""
    data = request.get_json(silent=True) or {}
    formula_params = {
        k: data[k]
        for k in ('loss_rate', 'tax_rate', 'aux_material_fee', 'labor_fee')
        if k in data
    }
    filepath = _report_service.generate_internal_pricing_sheet(
        project_id, formula_params or None
    )
    token = _os.path.basename(filepath)
    return jsonify({
        'code': 0,
        'data': {
            'token': token,
            'download_url': f'/api/reports/download/{token}',
        },
        'message': 'ok',
    })


@reports_bp.route('/reports/customer-quotation/<int:project_id>', methods=['POST'])
def generate_customer_quotation(project_id: int):
    """生成 PDF 客户报价单"""
    data = request.get_json(silent=True) or {}
    formula_params = {
        k: data[k]
        for k in ('loss_rate', 'tax_rate', 'aux_material_fee', 'labor_fee')
        if k in data
    }
    filepath = _report_service.generate_customer_quotation(
        project_id, formula_params or None
    )
    token = _os.path.basename(filepath)
    return jsonify({
        'code': 0,
        'data': {
            'token': token,
            'download_url': f'/api/reports/download/{token}',
        },
        'message': 'ok',
    })


@reports_bp.route('/reports/download/<token>', methods=['GET'])
def download_report(token: str):
    """下载报表文件"""
    filepath = _report_service.get_report_path(token)
    if filepath is None:
        return jsonify({'code': 404, 'message': '文件不存在或已过期'}), 404
    return _send_file(filepath, as_attachment=True, download_name=token)
