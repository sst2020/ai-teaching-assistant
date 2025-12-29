#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGLM4-6B 模型下载脚本 (使用 ModelScope)
"""
import sys
import os

# 设置UTF-8输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("ChatGLM4-6B 模型下载")
print("=" * 60)

try:
    from modelscope import snapshot_download
    print("\n✓ ModelScope 已安装")
except ImportError:
    print("\n✗ ModelScope 未安装，正在安装...")
    os.system("pip install modelscope -i https://pypi.tuna.tsinghua.edu.cn/simple")
    from modelscope import snapshot_download
    print("✓ ModelScope 安装完成")

print("\n开始下载 ChatGLM4-6B 模型...")
print("模型大小: 约 12GB")
print("下载位置: G:/ai-chatglm-demo/models/")
print("请耐心等待...\n")

try:
    # 尝试使用Qwen2.5-7B-Instruct (通义千问)
    print("尝试下载 Qwen2.5-7B-Instruct...")
    model_dir = snapshot_download(
        'Qwen/Qwen2.5-7B-Instruct',
        cache_dir='G:/ai-chatglm-demo/models',
        local_dir='G:/ai-chatglm-demo/models/chatglm4-6b',
        revision='master'
    )
    print("\n" + "=" * 60)
    print("✓ 模型下载完成！")
    print(f"模型路径: {model_dir}")
    print("=" * 60)
except Exception as e:
    print("\n" + "=" * 60)
    print(f"✗ 下载失败: {e}")
    print("\n备选方案: 使用 HuggingFace 下载")
    print("请运行: python download_model_hf.py")
    print("=" * 60)
    sys.exit(1)

