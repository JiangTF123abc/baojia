"""
人工费用计算服务
根据柜体配置和基础成本计算人工费用
"""
import logging
from typing import Dict, Optional
from decimal import Decimal

from ..extensions import db
from ..models import Cabinet, CabinetTypeConfig, LaborCostRule, BaseComponent

logger = logging.getLogger(__name__)


class LaborCostService:
    """人工费用计算服务类"""

    @staticmethod
    def check_cabinet_has_plc(cabinet: Cabinet) -> bool:
        """
        检查柜体是否包含PLC
        
        方法1：根据控制结构判断
        方法2：检查是否有PLC类元器件
        
        Args:
            cabinet: Cabinet 对象
            
        Returns:
            bool: True 表示包含PLC
        """
        # 方法1：根据控制结构判断
        if cabinet.control_structure in ['自控型', '纯PLC型']:
            return True

        # 方法2：检查是否有PLC类元器件（未被隐藏）
        for sc in cabinet.structure_components:
            plc_count = BaseComponent.query.filter_by(
                structure_component_id=sc.id,
                component_category='PLC及模块',
                is_hidden=False
            ).count()
            if plc_count > 0:
                return True

        return False

    @staticmethod
    def get_labor_cost_rule(cabinet: Cabinet) -> Optional[LaborCostRule]:
        """
        获取人工费用规则
        
        Args:
            cabinet: Cabinet 对象
            
        Returns:
            LaborCostRule 或 None
        """
        if not all([cabinet.control_category, cabinet.cabinet_type, cabinet.control_structure]):
            return None

        # 查询柜体类型配置
        config = CabinetTypeConfig.query.filter_by(
            control_category=cabinet.control_category,
            cabinet_type=cabinet.cabinet_type,
            control_structure=cabinet.control_structure,
            is_active=True
        ).first()

        if not config:
            return None

        # 查询人工费用规则
        rule = LaborCostRule.query.filter_by(
            cabinet_type_config_id=config.id,
            is_active=True
        ).first()

        return rule

    @staticmethod
    def get_default_labor_cost_rule() -> Dict:
        """
        获取默认人工费用规则
        
        Returns:
            dict: 默认费率配置
        """
        return {
            'assembly_fee_rate': Decimal('0.10'),  # 10%
            'management_fee_rate': Decimal('0.05'),  # 5%
            'profit_rate': Decimal('0.15'),  # 15%
            'programming_fee': Decimal('0'),
            'debugging_fee': Decimal('0')
        }

    @staticmethod
    def calculate_labor_cost(cabinet: Cabinet, base_cost: Decimal) -> Dict:
        """
        计算人工费用
        
        Args:
            cabinet: Cabinet 对象
            base_cost: 基础成本（元器件总价）
            
        Returns:
            dict: {
                'assembly_fee': Decimal,
                'management_fee': Decimal,
                'profit': Decimal,
                'programming_fee': Decimal,
                'debugging_fee': Decimal,
                'total_labor_cost': Decimal,
                'has_plc': bool,
                'rule_source': 'config' | 'default'
            }
        """
        try:
            # 查询费用规则
            rule = LaborCostService.get_labor_cost_rule(cabinet)
            rule_source = 'config' if rule else 'default'

            if not rule:
                logger.warning(
                    f"No labor cost rule for cabinet {cabinet.id}, using defaults"
                )
                default_rule = LaborCostService.get_default_labor_cost_rule()
                assembly_fee_rate = default_rule['assembly_fee_rate']
                management_fee_rate = default_rule['management_fee_rate']
                profit_rate = default_rule['profit_rate']
                programming_fee = default_rule['programming_fee']
                debugging_fee = default_rule['debugging_fee']
            else:
                assembly_fee_rate = rule.assembly_fee_rate
                management_fee_rate = rule.management_fee_rate
                profit_rate = rule.profit_rate
                programming_fee = rule.programming_fee
                debugging_fee = rule.debugging_fee

            # 验证费率范围
            if not (Decimal('0') <= assembly_fee_rate <= Decimal('1')):
                raise ValueError(f"Invalid assembly_fee_rate: {assembly_fee_rate}")
            if not (Decimal('0') <= management_fee_rate <= Decimal('1')):
                raise ValueError(f"Invalid management_fee_rate: {management_fee_rate}")
            if not (Decimal('0') <= profit_rate <= Decimal('1')):
                raise ValueError(f"Invalid profit_rate: {profit_rate}")

            # 确保 base_cost 是 Decimal 类型
            if not isinstance(base_cost, Decimal):
                base_cost = Decimal(str(base_cost))

            # 基础人工费用（按比例）
            assembly_fee = base_cost * assembly_fee_rate
            management_fee = base_cost * management_fee_rate
            profit = base_cost * profit_rate

            # 检查是否包含PLC
            has_plc = LaborCostService.check_cabinet_has_plc(cabinet)

            # 编程调试费用（固定金额，仅当包含PLC时）
            actual_programming_fee = programming_fee if has_plc else Decimal('0')
            actual_debugging_fee = debugging_fee if has_plc else Decimal('0')

            # 总人工费用
            total_labor_cost = (
                assembly_fee + management_fee + profit +
                actual_programming_fee + actual_debugging_fee
            )

            result = {
                'assembly_fee': assembly_fee,
                'management_fee': management_fee,
                'profit': profit,
                'programming_fee': actual_programming_fee,
                'debugging_fee': actual_debugging_fee,
                'total_labor_cost': total_labor_cost,
                'has_plc': has_plc,
                'rule_source': rule_source
            }

            logger.info(
                f"Calculated labor cost for cabinet {cabinet.id}: "
                f"total={total_labor_cost}, has_plc={has_plc}"
            )

            return result

        except ValueError as e:
            logger.error(f"Labor cost calculation validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"Labor cost calculation error: {e}", exc_info=True)
            # 返回零费用作为降级方案
            return {
                'assembly_fee': Decimal('0'),
                'management_fee': Decimal('0'),
                'profit': Decimal('0'),
                'programming_fee': Decimal('0'),
                'debugging_fee': Decimal('0'),
                'total_labor_cost': Decimal('0'),
                'has_plc': False,
                'rule_source': 'error',
                'error': str(e)
            }

    @staticmethod
    def calculate_cabinet_base_cost(cabinet: Cabinet) -> Decimal:
        """
        计算柜体的基础成本（所有元器件总价）
        
        Args:
            cabinet: Cabinet 对象
            
        Returns:
            Decimal: 基础成本
        """
        total = Decimal('0')
        for sc in cabinet.structure_components:
            for bc in sc.base_components:
                # 只计算未隐藏的元器件
                if not bc.is_hidden:
                    total += bc.total_price
        return total

    @staticmethod
    def calculate_cabinet_total_with_labor(cabinet: Cabinet) -> Dict:
        """
        计算柜体总价（包含人工费用）
        
        Args:
            cabinet: Cabinet 对象
            
        Returns:
            dict: {
                'base_cost': Decimal,
                'labor_cost': Dict,
                'total_cost': Decimal
            }
        """
        base_cost = LaborCostService.calculate_cabinet_base_cost(cabinet)
        labor_cost = LaborCostService.calculate_labor_cost(cabinet, base_cost)
        total_cost = base_cost + labor_cost['total_labor_cost']

        return {
            'base_cost': base_cost,
            'labor_cost': labor_cost,
            'total_cost': total_cost
        }


# 导出服务实例
labor_cost_service = LaborCostService()
