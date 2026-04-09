import logging
from decimal import Decimal, InvalidOperation

import sympy

from ..extensions import db
from ..models.price_formula import PriceFormula

logger = logging.getLogger(__name__)

# 默认公式（当配置公式无效时使用）
DEFAULT_FORMULA = "base_cost * (1 + loss_rate) * (1 + tax_rate) + aux_material_fee + labor_fee"

# 安全限制：禁止危险符号
_FORBIDDEN = {"__import__", "eval", "exec", "open", "os", "sys", "subprocess"}


def _is_safe_formula(formula_str: str) -> bool:
    for keyword in _FORBIDDEN:
        if keyword in formula_str:
            return False
    return True


class PriceEngine:

    def calculate_base_price(self, quantity, unit_price, discount_rate) -> Decimal:
        """计算基础元器件总价：quantity × unit_price × discount_rate"""
        try:
            qty = Decimal(str(quantity))
            price = Decimal(str(unit_price))
            discount = Decimal(str(discount_rate))
            return qty * price * discount
        except (InvalidOperation, TypeError, ValueError) as exc:
            logger.error("calculate_base_price 参数无效: %s", exc)
            return Decimal("0")

    def apply_formula(self, base_cost, formula_str: str = None, **params) -> float:
        """应用价格公式计算最终报价，公式无效时降级到 DEFAULT_FORMULA"""
        effective_formula = formula_str or DEFAULT_FORMULA

        if not _is_safe_formula(effective_formula):
            logger.error("公式包含危险关键字，降级到默认公式: %s", effective_formula)
            effective_formula = DEFAULT_FORMULA

        all_params = {"base_cost": float(base_cost), **{k: float(v) for k, v in params.items()}}

        for attempt_formula in (effective_formula, DEFAULT_FORMULA):
            try:
                expr = sympy.sympify(attempt_formula)
                symbols = list(expr.free_symbols)
                func = sympy.lambdify(symbols, expr, modules="math")
                kwargs = {str(s): all_params.get(str(s), 0.0) for s in symbols}
                return float(func(**kwargs))
            except sympy.SympifyError as exc:
                logger.error("公式解析失败 '%s': %s，降级到默认公式", attempt_formula, exc)
                if attempt_formula == DEFAULT_FORMULA:
                    raise
            except Exception as exc:
                logger.error("公式计算失败 '%s': %s，降级到默认公式", attempt_formula, exc)
                if attempt_formula == DEFAULT_FORMULA:
                    raise

        return 0.0

    def format_formula(self, formula_str: str) -> str:
        """将 SymPy 表达式格式化为可读字符串"""
        try:
            expr = sympy.sympify(formula_str)
            return str(expr)
        except Exception as exc:
            logger.error("公式格式化失败 '%s': %s", formula_str, exc)
            return formula_str

    def get_default_formula(self):
        """从数据库获取默认公式配置"""
        try:
            return PriceFormula.query.filter_by(is_default=True, is_active=True).first()
        except Exception as exc:
            logger.error("获取默认公式失败: %s", exc)
            return None

    def calculate_project_total(self, project) -> dict:
        """计算项目各层级总价"""
        project_total = Decimal("0")
        cabinets_result = []

        for cabinet in project.cabinets:
            cabinet_total = Decimal("0")
            scs_result = []

            for sc in cabinet.structure_components:
                sc_total = Decimal("0")
                bcs_result = []

                for bc in sc.base_components:
                    bc_price = self.calculate_base_price(bc.quantity, bc.unit_price, bc.discount_rate)
                    sc_total += bc_price
                    bcs_result.append({"bc_id": bc.id, "total_price": bc_price})

                cabinet_total += sc_total
                scs_result.append({"sc_id": sc.id, "sc_total": sc_total, "base_components": bcs_result})

            project_total += cabinet_total
            cabinets_result.append({"cabinet_id": cabinet.id, "cabinet_total": cabinet_total, "structure_components": scs_result})

        return {"project_total": project_total, "cabinets": cabinets_result}


price_engine = PriceEngine()
