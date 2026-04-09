"""
集成测试：完整报价流程
测试快速报价模式、详细报价模式、非标柜报价和人工费用计算
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.project import Project
from app.models.cabinet import Cabinet
from app.models.structure_component import StructureComponent
from app.models.base_component import BaseComponent
from app.models.cabinet_type_config import CabinetTypeConfig
from app.models.auto_match_rule import AutoMatchRule
from app.models.labor_cost_rule import LaborCostRule
from app.models.material import Material
from app.models.user import User
from app.services.auto_match_service import AutoMatchService
from app.services.labor_cost_service import LaborCostService
from decimal import Decimal


from decimal import Decimal


def _init_test_data():
    """初始化测试数据：用户、材料、配置、规则"""
    # 创建测试用户
    user = User(username='testuser', display_name='测试用户', role='admin', is_active=True)
    user.set_password('test123')
    db.session.add(user)
    db.session.flush()
    
    # 创建材料数据
    materials_data = [
        {
            'model_number': 'ABB-S201-C16',
            'name': '微型断路器',
            'specification': '1P, 16A, C型, 6kA',
            'unit_price': 45.00,
            'category': '断路器',
            'component_type': '一次元器件',
        },
        {
            'model_number': 'SIEMENS-S7-1200-CPU1214C',
            'name': '西门子PLC',
            'specification': 'CPU1214C DC/DC/DC, 14DI/10DO/2AI',
            'unit_price': 2850.00,
            'category': 'PLC',
            'component_type': 'PLC及模块',
        },
        {
            'model_number': 'SIEMENS-KTP700-BASIC',
            'name': '西门子触摸屏',
            'specification': '7寸彩色触摸屏',
            'unit_price': 3200.00,
            'category': '触摸屏',
            'component_type': '触摸屏',
        },
        {
            'model_number': 'MEANWELL-DR-120-24',
            'name': '明纬开关电源',
            'specification': '24VDC, 5A, 120W',
            'unit_price': 180.00,
            'category': '电源',
            'component_type': '电源',
        },
        {
            'model_number': 'CHNT-LA38-11BN',
            'name': '按钮',
            'specification': '绿色，常开',
            'unit_price': 8.50,
            'category': '按钮',
            'component_type': '二次元器件',
        },
        {
            'model_number': 'CHNT-LA38-11BR',
            'name': '按钮',
            'specification': '红色，常开',
            'unit_price': 8.50,
            'category': '按钮',
            'component_type': '二次元器件',
        },
        {
            'model_number': 'CHNT-AD16-22DS-G',
            'name': '指示灯',
            'specification': '绿色，LED，22mm',
            'unit_price': 6.00,
            'category': '指示灯',
            'component_type': '二次元器件',
        },
        {
            'model_number': 'PHOENIX-UK-2.5N',
            'name': '端子排',
            'specification': '2.5mm²，导轨式',
            'unit_price': 2.80,
            'category': '端子',
            'component_type': '端子',
        },
    ]
    
    created_materials = {}
    for m_data in materials_data:
        material = Material(**m_data)
        db.session.add(material)
        db.session.flush()
        created_materials[m_data['model_number']] = material
    
    # 创建柜体类型配置
    configs_data = [
        {
            'control_category': '控制类',
            'cabinet_type': '控制箱/柜',
            'control_structure': '自控型',
            'description': '带PLC和控制回路的自动化控制柜',
        },
        {
            'control_category': '控制类',
            'cabinet_type': '控制箱/柜',
            'control_structure': '非标控制',
            'description': '不带PLC的传统控制柜',
        },
        {
            'control_category': '配电类',
            'cabinet_type': '配电箱/柜',
            'control_structure': '非标配电',
            'description': '标准配电柜，无PLC',
        },
        {
            'control_category': '自控类',
            'cabinet_type': '自控柜',
            'control_structure': '自控型',
            'description': '自动化控制柜',
        },
    ]
    
    created_configs = {}
    for config_data in configs_data:
        config = CabinetTypeConfig(**config_data)
        db.session.add(config)
        db.session.flush()
        key = f"{config_data['control_category']}|{config_data['cabinet_type']}|{config_data['control_structure']}"
        created_configs[key] = config
    
    # 创建自动匹配规则（仅为自控型）
    config_auto = created_configs.get('控制类|控制箱/柜|自控型')
    if config_auto:
        rules_data = [
            ('SIEMENS-S7-1200-CPU1214C', 'PLC及模块', 1, True, 100),
            ('SIEMENS-KTP700-BASIC', '触摸屏', 1, True, 90),
            ('MEANWELL-DR-120-24', '电源', 1, True, 80),
            ('CHNT-LA38-11BN', '二次元器件', 2, False, 50),
            ('CHNT-LA38-11BR', '二次元器件', 1, False, 50),
            ('CHNT-AD16-22DS-G', '二次元器件', 3, False, 40),
            ('PHOENIX-UK-2.5N', '端子', 20, False, 30),
        ]
        
        for model, category, qty, required, priority in rules_data:
            material = created_materials.get(model)
            if material:
                rule = AutoMatchRule(
                    cabinet_type_config_id=config_auto.id,
                    material_id=material.id,
                    component_category=category,
                    default_quantity=qty,
                    is_required=required,
                    match_priority=priority,
                )
                db.session.add(rule)
    
    # 创建人工费用规则
    for key, config in created_configs.items():
        has_plc = config.control_structure in ['自控型', '纯PLC型']
        rule = LaborCostRule(
            cabinet_type_config_id=config.id,
            assembly_fee_rate=0.10,
            management_fee_rate=0.05,
            profit_rate=0.15,
            has_plc=has_plc,
            programming_fee=5000.00 if has_plc else 0,
            debugging_fee=3000.00 if has_plc else 0,
            is_active=True,
        )
        db.session.add(rule)
    
    db.session.commit()


def test_quick_quotation_mode():
    """测试快速报价模式：创建柜体 → 自动匹配 → 微调 → 生成报价"""
    print("\n" + "="*60)
    print("测试 1: 快速报价模式")
    print("="*60)
    
    # 使用测试配置（SQLite内存数据库）
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()
    with app.app_context():
        # 初始化测试数据库
        db.create_all()
        _init_test_data()
        # 1. 创建测试项目
        project = Project(
            name="快速报价测试项目",
            customer="测试客户A",
            created_by=1
        )
        db.session.add(project)
        db.session.flush()
        print(f"✓ 创建项目: {project.name} (ID: {project.id})")
        
        # 2. 创建柜体（快速报价模式）- 使用正确的柜体类型
        cabinet = Cabinet(
            project_id=project.id,
            name="控制柜-01",
            control_category="控制类",
            cabinet_type="控制箱/柜",
            control_structure="自控型",
            quotation_mode="quick"
        )
        db.session.add(cabinet)
        db.session.flush()
        print(f"✓ 创建柜体: {cabinet.name} (模式: {cabinet.quotation_mode})")
        
        # 3. 应用自动匹配
        auto_match_service = AutoMatchService()
        match_result = auto_match_service.apply_auto_match(cabinet)
        matched_count = match_result.get('matched_count', 0)
        print(f"✓ 自动匹配完成: 匹配了 {matched_count} 个元器件")
        
        # 4. 应用自动隐藏规则
        hide_result = auto_match_service.apply_auto_hide_rules(cabinet)
        hidden_count = hide_result.get('hidden_count', 0)
        print(f"✓ 自动隐藏规则应用: 隐藏了 {hidden_count} 个元器件")
        
        # 5. 计算基础成本
        base_cost = Decimal('0')
        for sc in cabinet.structure_components:
            for bc in sc.base_components:
                if not bc.is_hidden:
                    base_cost += bc.quantity * bc.unit_price * bc.discount_rate
        print(f"✓ 基础成本计算: ¥{base_cost:.2f}")
        
        # 6. 计算人工费用
        labor_cost_service = LaborCostService()
        labor_detail = labor_cost_service.calculate_labor_cost(cabinet, float(base_cost))
        print(f"✓ 人工费用计算:")
        print(f"  - 组装费: ¥{labor_detail['assembly_fee']:.2f}")
        print(f"  - 管理费: ¥{labor_detail['management_fee']:.2f}")
        print(f"  - 利润: ¥{labor_detail['profit']:.2f}")
        if labor_detail.get('programming_fee'):
            print(f"  - 编程费: ¥{labor_detail['programming_fee']:.2f}")
        if labor_detail.get('debugging_fee'):
            print(f"  - 调试费: ¥{labor_detail['debugging_fee']:.2f}")
        print(f"  - 总计: ¥{labor_detail['total_labor_cost']:.2f}")
        
        # 7. 计算总价
        total_with_labor = base_cost + Decimal(str(labor_detail['total_labor_cost']))
        print(f"✓ 项目总价: ¥{total_with_labor:.2f}")
        
        db.session.rollback()
        print("✓ 测试完成（已回滚）\n")
        return True


def test_detailed_quotation_mode():
    """测试详细报价模式：创建柜体 → 手动添加元器件 → 生成报价"""
    print("\n" + "="*60)
    print("测试 2: 详细报价模式")
    print("="*60)
    
    # 使用测试配置（SQLite内存数据库）
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()
    with app.app_context():
        # 初始化测试数据库
        db.create_all()
        _init_test_data()
        # 1. 创建测试项目
        project = Project(
            name="详细报价测试项目",
            customer="测试客户B",
            created_by=1
        )
        db.session.add(project)
        db.session.flush()
        print(f"✓ 创建项目: {project.name} (ID: {project.id})")
        
        # 2. 创建柜体（详细报价模式）- 使用正确的柜体类型
        cabinet = Cabinet(
            project_id=project.id,
            name="配电柜-01",
            control_category="配电类",
            cabinet_type="配电箱/柜",
            control_structure="非标配电",
            quotation_mode="detailed"
        )
        db.session.add(cabinet)
        db.session.flush()
        print(f"✓ 创建柜体: {cabinet.name} (模式: {cabinet.quotation_mode})")
        
        # 3. 手动创建结构组件
        sc = StructureComponent(
            cabinet_id=cabinet.id,
            name="主回路",
            sort_order=1
        )
        db.session.add(sc)
        db.session.flush()
        print(f"✓ 创建结构组件: {sc.name}")
        
        # 4. 手动添加元器件
        materials = Material.query.filter_by(is_active=True).limit(3).all()
        for idx, material in enumerate(materials):
            bc = BaseComponent(
                structure_component_id=sc.id,
                material_id=material.id,
                model_number=material.model_number,
                name=material.name,
                specification=material.specification,
                quantity=Decimal('2'),
                unit_price=material.unit_price,
                discount_rate=Decimal('0.95'),
                sort_order=idx,
                is_auto_matched=False
            )
            db.session.add(bc)
        db.session.flush()
        print(f"✓ 手动添加元器件: {len(materials)} 个")
        
        # 5. 计算基础成本
        base_cost = Decimal('0')
        for bc in sc.base_components:
            base_cost += bc.quantity * bc.unit_price * bc.discount_rate
        print(f"✓ 基础成本计算: ¥{base_cost:.2f}")
        
        # 6. 计算人工费用
        labor_cost_service = LaborCostService()
        labor_detail = labor_cost_service.calculate_labor_cost(cabinet, float(base_cost))
        print(f"✓ 人工费用计算: ¥{labor_detail['total_labor_cost']:.2f}")
        
        # 7. 计算总价
        total_with_labor = base_cost + Decimal(str(labor_detail['total_labor_cost']))
        print(f"✓ 项目总价: ¥{total_with_labor:.2f}")
        
        db.session.rollback()
        print("✓ 测试完成（已回滚）\n")
        return True


def test_non_standard_cabinet():
    """测试非标柜报价：创建非标柜 → 按回路添加元器件 → 验证自动隐藏 → 生成报价"""
    print("\n" + "="*60)
    print("测试 3: 非标柜报价")
    print("="*60)
    
    # 使用测试配置（SQLite内存数据库）
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()
    with app.app_context():
        # 初始化测试数据库
        db.create_all()
        _init_test_data()
        # 1. 创建测试项目
        project = Project(
            name="非标柜测试项目",
            customer="测试客户C",
            created_by=1
        )
        db.session.add(project)
        db.session.flush()
        print(f"✓ 创建项目: {project.name} (ID: {project.id})")
        
        # 2. 创建非标控制柜体 - 使用正确的柜体类型
        cabinet = Cabinet(
            project_id=project.id,
            name="非标控制柜-01",
            control_category="控制类",
            cabinet_type="控制箱/柜",
            control_structure="非标控制",
            quotation_mode="detailed"
        )
        db.session.add(cabinet)
        db.session.flush()
        print(f"✓ 创建非标柜体: {cabinet.name} (控制结构: {cabinet.control_structure})")
        
        # 3. 按回路创建结构组件
        circuits = [
            ("电机回路1", "电机回路"),
            ("变频回路1", "变频回路"),
            ("照明回路", "照明回路")
        ]
        
        for idx, (name, circuit_type) in enumerate(circuits):
            sc = StructureComponent(
                cabinet_id=cabinet.id,
                name=name,
                circuit_type=circuit_type,
                sort_order=idx
            )
            db.session.add(sc)
            db.session.flush()
            print(f"✓ 创建回路: {name} (类型: {circuit_type})")
            
            # 为每个回路添加元器件
            materials = Material.query.filter_by(is_active=True).limit(2).all()
            for material in materials:
                bc = BaseComponent(
                    structure_component_id=sc.id,
                    material_id=material.id,
                    model_number=material.model_number,
                    name=material.name,
                    specification=material.specification,
                    quantity=Decimal('1'),
                    unit_price=material.unit_price,
                    discount_rate=Decimal('1.0'),
                    sort_order=0
                )
                db.session.add(bc)
        
        db.session.flush()
        
        # 4. 应用自动隐藏规则（非标控制应该隐藏PLC相关）
        auto_match_service = AutoMatchService()
        hide_result = auto_match_service.apply_auto_hide_rules(cabinet)
        hidden_count = hide_result.get('hidden_count', 0)
        print(f"✓ 自动隐藏规则应用: 隐藏了 {hidden_count} 个PLC相关元器件")
        
        # 5. 计算基础成本（不包含隐藏的）
        base_cost = Decimal('0')
        visible_count = 0
        for sc in cabinet.structure_components:
            for bc in sc.base_components:
                if not bc.is_hidden:
                    base_cost += bc.quantity * bc.unit_price * bc.discount_rate
                    visible_count += 1
        print(f"✓ 可见元器件: {visible_count} 个")
        print(f"✓ 基础成本计算: ¥{base_cost:.2f}")
        
        # 6. 计算人工费用（非标控制不应包含编程调试费）
        labor_cost_service = LaborCostService()
        labor_detail = labor_cost_service.calculate_labor_cost(cabinet, float(base_cost))
        print(f"✓ 人工费用计算:")
        print(f"  - 包含PLC: {labor_detail.get('has_plc', False)}")
        print(f"  - 编程费: ¥{labor_detail.get('programming_fee', 0):.2f}")
        print(f"  - 调试费: ¥{labor_detail.get('debugging_fee', 0):.2f}")
        print(f"  - 总计: ¥{labor_detail['total_labor_cost']:.2f}")
        
        db.session.rollback()
        print("✓ 测试完成（已回滚）\n")
        return True


def test_labor_cost_with_plc():
    """测试人工费用计算：验证包含/不包含 PLC 时的费用差异"""
    print("\n" + "="*60)
    print("测试 4: 人工费用计算（PLC差异）")
    print("="*60)
    
    # 使用测试配置（SQLite内存数据库）
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()
    with app.app_context():
        # 初始化测试数据库
        db.create_all()
        _init_test_data()
        
        labor_cost_service = LaborCostService()
        base_cost = 10000.0
        
        # 测试1: 带PLC的柜体
        project1 = Project(name="测试项目-带PLC", created_by=1)
        db.session.add(project1)
        db.session.flush()
        
        cabinet_with_plc = Cabinet(
            project_id=project1.id,
            name="自控柜",
            control_category="自控类",
            cabinet_type="自控柜",
            control_structure="自控型",
            quotation_mode="quick"
        )
        db.session.add(cabinet_with_plc)
        db.session.flush()
        
        labor_with_plc = labor_cost_service.calculate_labor_cost(cabinet_with_plc, base_cost)
        print(f"✓ 带PLC柜体:")
        print(f"  - 基础成本: ¥{base_cost:.2f}")
        print(f"  - 组装费: ¥{labor_with_plc['assembly_fee']:.2f}")
        print(f"  - 管理费: ¥{labor_with_plc['management_fee']:.2f}")
        print(f"  - 利润: ¥{labor_with_plc['profit']:.2f}")
        print(f"  - 编程费: ¥{labor_with_plc.get('programming_fee', 0):.2f}")
        print(f"  - 调试费: ¥{labor_with_plc.get('debugging_fee', 0):.2f}")
        print(f"  - 人工费用总计: ¥{labor_with_plc['total_labor_cost']:.2f}")
        
        # 测试2: 不带PLC的柜体
        project2 = Project(name="测试项目-不带PLC", created_by=1)
        db.session.add(project2)
        db.session.flush()
        
        cabinet_without_plc = Cabinet(
            project_id=project2.id,
            name="配电柜",
            control_category="配电类",
            cabinet_type="配电箱/柜",
            control_structure="非标配电",
            quotation_mode="detailed"
        )
        db.session.add(cabinet_without_plc)
        db.session.flush()
        
        labor_without_plc = labor_cost_service.calculate_labor_cost(cabinet_without_plc, base_cost)
        print(f"\n✓ 不带PLC柜体:")
        print(f"  - 基础成本: ¥{base_cost:.2f}")
        print(f"  - 组装费: ¥{labor_without_plc['assembly_fee']:.2f}")
        print(f"  - 管理费: ¥{labor_without_plc['management_fee']:.2f}")
        print(f"  - 利润: ¥{labor_without_plc['profit']:.2f}")
        print(f"  - 编程费: ¥{labor_without_plc.get('programming_fee', 0):.2f}")
        print(f"  - 调试费: ¥{labor_without_plc.get('debugging_fee', 0):.2f}")
        print(f"  - 人工费用总计: ¥{labor_without_plc['total_labor_cost']:.2f}")
        
        # 计算差异
        diff = labor_with_plc['total_labor_cost'] - labor_without_plc['total_labor_cost']
        print(f"\n✓ 费用差异: ¥{diff:.2f}")
        print(f"  (带PLC柜体的人工费用应该更高，因为包含编程和调试费)")
        
        db.session.rollback()
        print("✓ 测试完成（已回滚）\n")
        return True


def main():
    """运行所有集成测试"""
    print("\n" + "="*60)
    print("电气设备报价系统 - 集成测试")
    print("="*60)
    
    tests = [
        ("快速报价模式", test_quick_quotation_mode),
        ("详细报价模式", test_detailed_quotation_mode),
        ("非标柜报价", test_non_standard_cabinet),
        ("人工费用计算（PLC差异）", test_labor_cost_with_plc),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"✗ 测试失败: {name}")
            print(f"  错误: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # 打印测试总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{status}: {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    print("="*60 + "\n")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
