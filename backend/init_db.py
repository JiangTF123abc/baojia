"""
数据库初始化脚本
- 建表
- 创建初始管理员账号
- 插入示例价格公式
"""
import os
import sys
import json
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 将 backend 目录加入路径
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from app.models import (
    User, PriceFormula, Material, MaterialAccessory,
    CabinetTypeConfig, AutoMatchRule, LaborCostRule
)


def init_db():
    app = create_app()

    with app.app_context():
        print('正在创建数据库表...')
        db.create_all()
        print('数据库表创建完成。')

        _create_admin_user()
        _insert_sample_formulas()
        _insert_sample_materials()
        _insert_cabinet_type_configs()
        _insert_auto_match_rules()
        _insert_labor_cost_rules()

        db.session.commit()
        print('数据库初始化完成。')


def _create_admin_user():
    """创建初始管理员账号"""
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin@123456')
    admin_display = os.environ.get('ADMIN_DISPLAY_NAME', '系统管理员')

    existing = User.query.filter_by(username=admin_username).first()
    if existing:
        print(f'管理员账号 "{admin_username}" 已存在，跳过创建。')
        return

    admin = User(
        username=admin_username,
        display_name=admin_display,
        role='admin',
        is_active=True,
    )
    admin.set_password(admin_password)
    db.session.add(admin)
    print(f'已创建管理员账号：{admin_username}')


def _insert_sample_formulas():
    """插入示例价格公式"""
    if PriceFormula.query.count() > 0:
        print('价格公式已存在，跳过插入。')
        return

    formulas = [
        {
            'name': '标准报价公式',
            'formula_str': 'base_cost * (1 + loss_rate) * (1 + aux_material_rate) * (1 + labor_rate) * (1 + tax_rate)',
            'variables': json.dumps({
                'base_cost': '基础成本（元器件总价）',
                'loss_rate': '损耗率（如 0.05 表示 5%）',
                'aux_material_rate': '辅材费率（如 0.03 表示 3%）',
                'labor_rate': '人工费率（如 0.10 表示 10%）',
                'tax_rate': '税率（如 0.13 表示 13%）',
            }, ensure_ascii=False),
            'is_default': True,
            'is_active': True,
        },
        {
            'name': '简化报价公式',
            'formula_str': 'base_cost * (1 + loss_rate + tax_rate)',
            'variables': json.dumps({
                'base_cost': '基础成本',
                'loss_rate': '损耗率',
                'tax_rate': '税率',
            }, ensure_ascii=False),
            'is_default': False,
            'is_active': True,
        },
        {
            'name': '含固定辅材费公式',
            'formula_str': 'base_cost * (1 + loss_rate) + aux_material_fee + labor_fee',
            'variables': json.dumps({
                'base_cost': '基础成本',
                'loss_rate': '损耗率',
                'aux_material_fee': '辅材费（固定金额，元）',
                'labor_fee': '人工费（固定金额，元）',
            }, ensure_ascii=False),
            'is_default': False,
            'is_active': True,
        },
    ]

    for f in formulas:
        formula = PriceFormula(**f)
        db.session.add(formula)

    print(f'已插入 {len(formulas)} 条示例价格公式。')


def _insert_sample_materials():
    """插入示例材料数据"""
    if Material.query.count() > 0:
        print('材料数据已存在，跳过插入。')
        return

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
            'model_number': 'ABB-S203-C32',
            'name': '微型断路器',
            'specification': '3P, 32A, C型, 6kA',
            'unit_price': 128.00,
            'category': '断路器',
            'component_type': '一次元器件',
        },
        {
            'model_number': 'CHNT-NXC-06M',
            'name': '交流接触器',
            'specification': '6A, 220V线圈',
            'unit_price': 35.00,
            'category': '接触器',
            'component_type': '一次元器件',
        },
        {
            'model_number': 'CHNT-NXC-06M-AUX',
            'name': '辅助触头',
            'specification': '1NO+1NC，适配NXC系列',
            'unit_price': 12.00,
            'category': '附件',
            'component_type': '二次元器件',
        },
        {
            'model_number': 'SIEMENS-3RT2015',
            'name': '西门子接触器',
            'specification': '7A, 3kW, 220V',
            'unit_price': 185.00,
            'category': '接触器',
            'component_type': '一次元器件',
        },
        {
            'model_number': 'SIEMENS-3RH2911-AUX',
            'name': '辅助触头模块',
            'specification': '2NO+2NC，适配3RT系列',
            'unit_price': 68.00,
            'category': '附件',
            'component_type': '二次元器件',
        },
        # 新增：PLC相关元器件
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
        # 新增：二次元器件
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
        db.session.flush()  # 获取 id
        created_materials[m_data['model_number']] = material

    # 插入附件关联
    accessory_links = [
        ('CHNT-NXC-06M', 'CHNT-NXC-06M-AUX', False, 1),
        ('SIEMENS-3RT2015', 'SIEMENS-3RH2911-AUX', False, 1),
    ]

    for main_model, acc_model, is_required, qty in accessory_links:
        main = created_materials.get(main_model)
        acc = created_materials.get(acc_model)
        if main and acc:
            link = MaterialAccessory(
                material_id=main.id,
                accessory_id=acc.id,
                is_required=is_required,
                default_quantity=qty,
            )
            db.session.add(link)

    print(f'已插入 {len(materials_data)} 条示例材料数据及附件关联。')


def _insert_cabinet_type_configs():
    """插入柜体类型配置数据"""
    if CabinetTypeConfig.query.count() > 0:
        print('柜体类型配置已存在，跳过插入。')
        return

    configs = [
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
            'control_structure': '非标控制',
            'description': '标准配电柜，无PLC',
        },
        {
            'control_category': '低压类',
            'cabinet_type': '低压进线柜/出线柜',
            'control_structure': 'MCC柜',
            'description': 'MCC电机控制中心柜',
        },
    ]

    for config_data in configs:
        config = CabinetTypeConfig(**config_data)
        db.session.add(config)

    db.session.flush()
    print(f'已插入 {len(configs)} 条柜体类型配置。')


def _insert_auto_match_rules():
    """插入自动匹配规则"""
    if AutoMatchRule.query.count() > 0:
        print('自动匹配规则已存在，跳过插入。')
        return

    # 获取配置和材料
    config_auto = CabinetTypeConfig.query.filter_by(
        control_category='控制类',
        cabinet_type='控制箱/柜',
        control_structure='自控型'
    ).first()

    if not config_auto:
        print('未找到自控型配置，跳过自动匹配规则插入。')
        return

    # 获取材料
    materials = {m.model_number: m for m in Material.query.all()}

    rules_data = [
        # 自控型柜体的自动匹配规则
        {
            'cabinet_type_config_id': config_auto.id,
            'material_id': materials.get('SIEMENS-S7-1200-CPU1214C').id if materials.get('SIEMENS-S7-1200-CPU1214C') else None,
            'component_category': 'PLC及模块',
            'default_quantity': 1,
            'is_required': True,
            'match_priority': 100,
        },
        {
            'cabinet_type_config_id': config_auto.id,
            'material_id': materials.get('SIEMENS-KTP700-BASIC').id if materials.get('SIEMENS-KTP700-BASIC') else None,
            'component_category': '触摸屏',
            'default_quantity': 1,
            'is_required': True,
            'match_priority': 90,
        },
        {
            'cabinet_type_config_id': config_auto.id,
            'material_id': materials.get('MEANWELL-DR-120-24').id if materials.get('MEANWELL-DR-120-24') else None,
            'component_category': '电源',
            'default_quantity': 1,
            'is_required': True,
            'match_priority': 80,
        },
        {
            'cabinet_type_config_id': config_auto.id,
            'material_id': materials.get('CHNT-LA38-11BN').id if materials.get('CHNT-LA38-11BN') else None,
            'component_category': '二次元器件',
            'default_quantity': 2,
            'is_required': False,
            'match_priority': 50,
        },
        {
            'cabinet_type_config_id': config_auto.id,
            'material_id': materials.get('CHNT-LA38-11BR').id if materials.get('CHNT-LA38-11BR') else None,
            'component_category': '二次元器件',
            'default_quantity': 1,
            'is_required': False,
            'match_priority': 50,
        },
        {
            'cabinet_type_config_id': config_auto.id,
            'material_id': materials.get('CHNT-AD16-22DS-G').id if materials.get('CHNT-AD16-22DS-G') else None,
            'component_category': '二次元器件',
            'default_quantity': 3,
            'is_required': False,
            'match_priority': 40,
        },
        {
            'cabinet_type_config_id': config_auto.id,
            'material_id': materials.get('PHOENIX-UK-2.5N').id if materials.get('PHOENIX-UK-2.5N') else None,
            'component_category': '端子',
            'default_quantity': 20,
            'is_required': False,
            'match_priority': 30,
        },
    ]

    # 过滤掉 material_id 为 None 的规则
    valid_rules = [r for r in rules_data if r['material_id'] is not None]

    for rule_data in valid_rules:
        rule = AutoMatchRule(**rule_data)
        db.session.add(rule)

    print(f'已插入 {len(valid_rules)} 条自动匹配规则。')


def _insert_labor_cost_rules():
    """插入人工费用规则"""
    if LaborCostRule.query.count() > 0:
        print('人工费用规则已存在，跳过插入。')
        return

    configs = CabinetTypeConfig.query.all()
    if not configs:
        print('未找到柜体类型配置，跳过人工费用规则插入。')
        return

    for config in configs:
        # 根据控制结构判断是否包含PLC
        has_plc = config.control_structure in ['自控型', '纯PLC型']

        rule = LaborCostRule(
            cabinet_type_config_id=config.id,
            assembly_fee_rate=0.10,  # 10%
            management_fee_rate=0.05,  # 5%
            profit_rate=0.15,  # 15%
            has_plc=has_plc,
            programming_fee=5000.00 if has_plc else 0,
            debugging_fee=3000.00 if has_plc else 0,
            is_active=True,
        )
        db.session.add(rule)

    print(f'已插入 {len(configs)} 条人工费用规则。')


if __name__ == '__main__':
    init_db()
