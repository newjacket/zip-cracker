#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试脚本：创建带密码的压缩包并验证破解工具"""

import os
import sys
import zipfile

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_ZIP = os.path.join(TEST_DIR, 'test_secret.zip')
TEST_FILE = os.path.join(TEST_DIR, 'test_content.txt')
TEST_PASSWORD = 'pass2026'


def create_test_zip():
    """创建带密码的测试压缩包"""
    # 创建测试内容文件
    with open(TEST_FILE, 'w', encoding='utf-8') as f:
        f.write('这是一个测试文件，用于验证ZIP密码恢复工具。\n')
        f.write('密码是: pass2026\n')

    # 创建带密码的ZIP（使用传统ZipCrypto加密，兼容性最好）
    with zipfile.ZipFile(TEST_ZIP, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.setpassword(TEST_PASSWORD.encode('utf-8'))
        zf.write(TEST_FILE, arcname='test_content.txt')

    print(f"✅ 测试压缩包已创建: {TEST_ZIP}")
    print(f"   密码: {TEST_PASSWORD}")
    return True


def verify_zip_encrypted():
    """验证压缩包确实是加密的"""
    with zipfile.ZipFile(TEST_ZIP, 'r') as zf:
        for info in zf.infolist():
            if info.flag_bits & 0x1:
                print(f"✅ 压缩包已加密: {info.filename}")
                return True
    print("❌ 压缩包未加密")
    return False


def main():
    print("=" * 50)
    print("  ZIP密码恢复工具 - 测试")
    print("=" * 50)

    # 1. 创建测试压缩包
    print("\n[1/3] 创建测试压缩包...")
    create_test_zip()

    # 2. 验证加密
    print("\n[2/3] 验证加密...")
    if not verify_zip_encrypted():
        sys.exit(1)

    # 3. 提示运行破解命令
    print("\n[3/3] 运行破解测试...")
    print(f"\n请执行以下命令测试字典攻击：")
    print(f"  python zip_cracker.py -f test_secret.zip -m dict -d passwords.txt")
    print(f"\n或者测试掩码攻击（密码是 pass + 4位数字）：")
    print(f"  python zip_cracker.py -f test_secret.zip -m mask -k \"pass?d?d?d?d\"")
    print(f"\n预期结果：密码应为 '{TEST_PASSWORD}'")

    # 清理测试内容文件
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)

    print("\n✅ 测试准备完成！")


if __name__ == '__main__':
    main()
