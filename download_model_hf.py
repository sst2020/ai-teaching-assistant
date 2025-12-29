#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGLM4-6B 模型下载脚本 (使用 HuggingFace)
"""
import sys
import os

# 设置UTF-8输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("ChatGLM4-6B 模型下载 (HuggingFace)")
print("=" * 60)

try:
    from huggingface_hub import snapshot_download
    print("\n✓ HuggingFace Hub 已安装")
except ImportError:
    print("\n✗ HuggingFace Hub 未安装，正在安装...")
    os.system("pip install huggingface-hub -i https://pypi.tuna.tsinghua.edu.cn/simple")
    from huggingface_hub import snapshot_download
    print("✓ HuggingFace Hub 安装完成")

print("\n开始下载 ChatGLM4-6B 模型...")
print("模型大小: 约 12GB")
print("下载位置: G:/ai-chatglm-demo/models/chatglm4-6b/")
print("使用镜像站: hf-mirror.com")
print("请耐心等待...\n")

# 设置HuggingFace镜像
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

try:
    model_dir = snapshot_download(
        repo_id="THUDM/glm-4-9b-chat",
        cache_dir="G:/ai-chatglm-demo/models",
        local_dir="G:/ai-chatglm-demo/models/chatglm4-6b",
        local_dir_use_symlinks=False
    )
    print("\n" + "=" * 60)
    print("✓ 模型下载完成！")
    print(f"模型路径: {model_dir}")
    print("=" * 60)
except Exception as e:
    print("\n" + "=" * 60)
    print(f"✗ 下载失败: {e}")
    print("\n可能的原因:")
    print("1. 网络连接问题")
    print("2. HuggingFace 访问受限")
    print("3. 磁盘空间不足")
    print("\n建议: 手动下载模型或使用镜像站")
    print("=" * 60)
    sys.exit(1)

