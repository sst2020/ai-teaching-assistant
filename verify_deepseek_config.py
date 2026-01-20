#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速验证 DeepSeek 配置的测试脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.core.config import settings

def test_deepseek_config():
    """测试 DeepSeek 配置是否正确加载"""
    print("=" * 50)
    print("DeepSeek 配置验证")
    print("=" * 50)
    
    print(f"USE_DEEPSEEK: {settings.USE_DEEPSEEK}")
    print(f"DEEPSEEK_API_KEY: {'已配置' if settings.DEEPSEEK_API_KEY else '未配置'}")
    print(f"DEEPSEEK_API_BASE: {settings.DEEPSEEK_API_BASE}")
    print(f"DEEPSEEK_MODEL: {settings.DEEPSEEK_MODEL}")
    print(f"DEEPSEEK_TEMPERATURE: {settings.DEEPSEEK_TEMPERATURE}")
    print(f"DEEPSEEK_MAX_TOKENS: {settings.DEEPSEEK_MAX_TOKENS}")
    print(f"DEEPSEEK_MAX_RETRIES: {settings.DEEPSEEK_MAX_RETRIES}")
    print(f"DEEPSEEK_RETRY_DELAY: {settings.DEEPSEEK_RETRY_DELAY}")
    
    # 验证必需的配置项
    required_settings = [
        ('DEEPSEEK_API_BASE', settings.DEEPSEEK_API_BASE),
        ('DEEPSEEK_MODEL', settings.DEEPSEEK_MODEL),
    ]
    
    all_good = True
    for name, value in required_settings:
        if not value:
            print(f"[ERROR] {name} 未设置")
            all_good = False
        else:
            print(f"[OK] {name} 已设置: {value}")

    if all_good:
        print("\n[SUCCESS] 所有必需的 DeepSeek 配置项都已正确设置！")
        return True
    else:
        print("\n[ERROR] 一些必需的配置项缺失，请检查配置文件。")
        return False

if __name__ == "__main__":
    success = test_deepseek_config()
    if success:
        print("\n配置验证通过！")
    else:
        print("\n配置验证失败！")
    sys.exit(0 if success else 1)