"""测试 VerificationCode 模型类的功能"""
from datetime import datetime, timedelta
from app.models.verification_code import VerificationCode


def test_generate_code():
    """测试验证码生成功能"""
    print("测试 generate_code() 方法...")
    
    # 生成多个验证码，验证格式
    codes = [VerificationCode.generate_code() for _ in range(10)]
    
    for code in codes:
        # 验证长度为6
        assert len(code) == 6, f"验证码长度应为6，实际为 {len(code)}"
        
        # 验证全部为数字
        assert code.isdigit(), f"验证码应全部为数字，实际为 {code}"
        
        # 验证范围在 000000-999999
        code_int = int(code)
        assert 0 <= code_int <= 999999, f"验证码应在 0-999999 范围内，实际为 {code_int}"
    
    print(f"✓ 生成的验证码示例: {codes[:5]}")
    print("✓ generate_code() 测试通过\n")


def test_is_valid():
    """测试验证码有效性检查"""
    print("测试 is_valid() 方法...")
    
    # 创建一个有效的验证码对象（未使用，未过期）
    valid_code = VerificationCode()
    valid_code.code = "123456"
    valid_code.email = "test@example.com"
    valid_code.purpose = "password_reset"
    valid_code.is_used = False
    valid_code.expires_at = datetime.utcnow() + timedelta(minutes=5)
    valid_code.created_at = datetime.utcnow()
    
    assert valid_code.is_valid() == True, "未使用且未过期的验证码应该有效"
    print("✓ 未使用且未过期的验证码：有效")
    
    # 测试已使用的验证码
    used_code = VerificationCode()
    used_code.code = "654321"
    used_code.email = "test@example.com"
    used_code.purpose = "password_reset"
    used_code.is_used = True
    used_code.expires_at = datetime.utcnow() + timedelta(minutes=5)
    used_code.created_at = datetime.utcnow()
    
    assert used_code.is_valid() == False, "已使用的验证码应该无效"
    print("✓ 已使用的验证码：无效")
    
    # 测试已过期的验证码
    expired_code = VerificationCode()
    expired_code.code = "111111"
    expired_code.email = "test@example.com"
    expired_code.purpose = "password_reset"
    expired_code.is_used = False
    expired_code.expires_at = datetime.utcnow() - timedelta(minutes=1)  # 1分钟前过期
    expired_code.created_at = datetime.utcnow() - timedelta(minutes=6)
    
    assert expired_code.is_valid() == False, "已过期的验证码应该无效"
    print("✓ 已过期的验证码：无效")
    
    # 测试既已使用又已过期的验证码
    used_expired_code = VerificationCode()
    used_expired_code.code = "222222"
    used_expired_code.email = "test@example.com"
    used_expired_code.purpose = "password_reset"
    used_expired_code.is_used = True
    used_expired_code.expires_at = datetime.utcnow() - timedelta(minutes=1)
    used_expired_code.created_at = datetime.utcnow() - timedelta(minutes=6)
    
    assert used_expired_code.is_valid() == False, "已使用且已过期的验证码应该无效"
    print("✓ 已使用且已过期的验证码：无效")
    
    print("✓ is_valid() 测试通过\n")


def test_mark_as_used():
    """测试标记验证码为已使用"""
    print("测试 mark_as_used() 方法...")
    
    # 创建一个未使用的验证码
    code = VerificationCode()
    code.code = "999999"
    code.email = "test@example.com"
    code.purpose = "password_reset"
    code.is_used = False
    code.expires_at = datetime.utcnow() + timedelta(minutes=5)
    code.created_at = datetime.utcnow()
    
    # 验证初始状态
    assert code.is_used == False, "初始状态应为未使用"
    assert code.is_valid() == True, "初始状态应该有效"
    print("✓ 初始状态：未使用，有效")
    
    # 标记为已使用
    code.mark_as_used()
    
    # 验证标记后的状态
    assert code.is_used == True, "标记后应为已使用"
    assert code.is_valid() == False, "标记后应该无效"
    print("✓ 标记后状态：已使用，无效")
    
    print("✓ mark_as_used() 测试通过\n")


if __name__ == '__main__':
    print("=" * 60)
    print("开始测试 VerificationCode 模型类")
    print("=" * 60)
    print()
    
    try:
        test_generate_code()
        test_is_valid()
        test_mark_as_used()
        
        print("=" * 60)
        print("所有测试通过！✓")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        exit(1)
