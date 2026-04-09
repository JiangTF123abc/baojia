"""
自动匹配服务
根据柜体配置自动匹配标准元器件
"""
import logging
from typing import Dict, List, Optional
from decimal import Decimal

from ..extensions import db
from ..models import (
    Cabinet, CabinetTypeConfig, AutoMatchRule, 
    Material, BaseComponent, StructureComponent
)

logger = logging.getLogger(__name__)


class AutoMatchService:
    """自动匹配服务类"""

    @staticmethod
    def get_cabinet_type_config(
        control_category: str,
        cabinet_type: str,
        control_structure: str
    ) -> Optional[CabinetTypeConfig]:
        """
        根据柜体分类获取配置
        
        Args:
            control_category: 控制大类
            cabinet_type: 柜体类型
            control_structure: 控制结构
            
        Returns:
            CabinetTypeConfig 或 None
        """
        return CabinetTypeConfig.query.filter_by(
            control_category=control_category,
            cabinet_type=cabinet_type,
            control_structure=control_structure,
            is_active=True
        ).first()

    @staticmethod
    def apply_auto_match(cabinet: Cabinet) -> Dict:
        """
        应用自动匹配规则
        
        Args:
            cabinet: Cabinet 对象
            
        Returns:
            dict: {
                'status': 'success' | 'warning' | 'error',
                'message': str,
                'matched_count': int,
                'components': List[BaseComponent]
            }
        """
        try:
            # 验证柜体配置
            if not all([cabinet.control_category, cabinet.cabinet_type, cabinet.control_structure]):
                return {
                    'status': 'error',
                    'message': '柜体配置不完整，请先设置控制大类、柜体类型和控制结构',
                    'matched_count': 0,
                    'components': []
                }

            # 查询柜体类型配置
            config = AutoMatchService.get_cabinet_type_config(
                cabinet.control_category,
                cabinet.cabinet_type,
                cabinet.control_structure
            )

            if not config:
                logger.warning(
                    f"No config found for cabinet {cabinet.id}: "
                    f"{cabinet.control_category}/{cabinet.cabinet_type}/{cabinet.control_structure}"
                )
                return {
                    'status': 'warning',
                    'message': '未找到匹配的柜体配置，请手动添加元器件',
                    'matched_count': 0,
                    'components': []
                }

            # 查询自动匹配规则（按优先级降序）
            rules = AutoMatchRule.query.filter_by(
                cabinet_type_config_id=config.id
            ).order_by(AutoMatchRule.match_priority.desc()).all()

            if not rules:
                logger.warning(f"No auto-match rules for config {config.id}")
                return {
                    'status': 'warning',
                    'message': '该柜体类型暂无自动匹配规则',
                    'matched_count': 0,
                    'components': []
                }

            # 创建默认结构组件（如果不存在）
            structure_component = cabinet.structure_components.first()
            if not structure_component:
                structure_component = StructureComponent(
                    cabinet_id=cabinet.id,
                    name='自动匹配元器件',
                    sort_order=0
                )
                db.session.add(structure_component)
                db.session.flush()

            # 执行匹配
            matched_components = []
            matched_count = 0

            for rule in rules:
                material = Material.query.get(rule.material_id)
                if not material or not material.is_active:
                    logger.warning(f"Material {rule.material_id} not found or inactive")
                    continue

                # 创建基础元器件
                base_component = BaseComponent(
                    structure_component_id=structure_component.id,
                    material_id=material.id,
                    component_category=rule.component_category,
                    model_number=material.model_number,
                    name=material.name,
                    specification=material.specification,
                    quantity=rule.default_quantity,
                    unit_price=material.unit_price or Decimal('0'),
                    discount_rate=Decimal('1.0'),
                    is_auto_matched=True,
                    is_hidden=False,
                    sort_order=matched_count
                )
                db.session.add(base_component)
                matched_components.append(base_component)
                matched_count += 1

            db.session.flush()

            logger.info(
                f"Auto-matched {matched_count} components for cabinet {cabinet.id}"
            )

            return {
                'status': 'success',
                'message': f'成功匹配 {matched_count} 个元器件',
                'matched_count': matched_count,
                'components': matched_components
            }

        except Exception as e:
            logger.error(f"Auto-match error for cabinet {cabinet.id}: {e}", exc_info=True)
            db.session.rollback()
            return {
                'status': 'error',
                'message': f'自动匹配失败: {str(e)}',
                'matched_count': 0,
                'components': []
            }

    @staticmethod
    def apply_auto_hide_rules(cabinet: Cabinet) -> Dict:
        """
        应用自动隐藏规则
        
        当控制结构为"非标控制"时，隐藏PLC相关元器件
        
        Args:
            cabinet: Cabinet 对象
            
        Returns:
            dict: {
                'status': 'success' | 'info',
                'message': str,
                'hidden_count': int
            }
        """
        try:
            # 只有非标控制才需要隐藏
            if cabinet.control_structure != '非标控制':
                return {
                    'status': 'info',
                    'message': '当前控制结构不需要隐藏元器件',
                    'hidden_count': 0
                }

            # 定义需要隐藏的元器件分类
            hidden_categories = [
                'PLC及模块',
                '开关电源',
                '信号隔离器',
                '触摸屏'
            ]

            # 查询所有需要隐藏的元器件
            components_to_hide = []
            for sc in cabinet.structure_components:
                for bc in sc.base_components:
                    if bc.component_category in hidden_categories and not bc.is_hidden:
                        bc.is_hidden = True
                        components_to_hide.append(bc)

            hidden_count = len(components_to_hide)
            
            if hidden_count > 0:
                db.session.flush()
                logger.info(
                    f"Hidden {hidden_count} components for cabinet {cabinet.id} "
                    f"(control_structure={cabinet.control_structure})"
                )

            return {
                'status': 'success',
                'message': f'已隐藏 {hidden_count} 个PLC相关元器件',
                'hidden_count': hidden_count
            }

        except Exception as e:
            logger.error(f"Auto-hide error for cabinet {cabinet.id}: {e}", exc_info=True)
            db.session.rollback()
            return {
                'status': 'error',
                'message': f'自动隐藏失败: {str(e)}',
                'hidden_count': 0
            }

    @staticmethod
    def get_auto_match_preview(
        control_category: str,
        cabinet_type: str,
        control_structure: str
    ) -> Dict:
        """
        获取自动匹配预览（不实际创建元器件）
        
        Args:
            control_category: 控制大类
            cabinet_type: 柜体类型
            control_structure: 控制结构
            
        Returns:
            dict: {
                'config': CabinetTypeConfig dict or None,
                'rules': List[AutoMatchRule dict],
                'total_count': int
            }
        """
        config = AutoMatchService.get_cabinet_type_config(
            control_category,
            cabinet_type,
            control_structure
        )

        if not config:
            return {
                'config': None,
                'rules': [],
                'total_count': 0
            }

        rules = AutoMatchRule.query.filter_by(
            cabinet_type_config_id=config.id
        ).order_by(AutoMatchRule.match_priority.desc()).all()

        return {
            'config': config.to_dict(),
            'rules': [rule.to_dict() for rule in rules],
            'total_count': len(rules)
        }


# 导出服务实例
auto_match_service = AutoMatchService()
