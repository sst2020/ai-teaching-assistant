#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检测系统配置"""
import sys
import psutil
import shutil
import platform

# 设置UTF-8输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("系统配置检测")
print("=" * 60)

# CPU信息
print(f"\n【CPU】")
print(f"  核心数: {psutil.cpu_count()} (逻辑)")
print(f"  架构: {platform.machine()}")

# 内存信息
mem = psutil.virtual_memory()
print(f"\n【内存】")
print(f"  总内存: {round(mem.total / 1024**3, 2)} GB")
print(f"  可用内存: {round(mem.available / 1024**3, 2)} GB")
print(f"  使用率: {mem.percent}%")

# 磁盘信息
print(f"\n【磁盘】")
for partition in psutil.disk_partitions():
    if 'E:' in partition.mountpoint or 'E:\\' in partition.mountpoint or 'G:' in partition.mountpoint or 'G:\\' in partition.mountpoint:
        usage = psutil.disk_usage(partition.mountpoint)
        print(f"  {partition.mountpoint}")
        print(f"    总容量: {round(usage.total / 1024**3, 2)} GB")
        print(f"    已使用: {round(usage.used / 1024**3, 2)} GB")
        print(f"    可用: {round(usage.free / 1024**3, 2)} GB")

# Python版本
print(f"\n【Python】")
print(f"  版本: {platform.python_version()}")

# 检查关键包
print(f"\n【已安装的关键包】")
try:
    import torch
    print(f"  ✓ PyTorch: {torch.__version__}")
    print(f"    CUDA可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"    CUDA版本: {torch.version.cuda}")
        print(f"    GPU数量: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"    GPU {i}: {torch.cuda.get_device_name(i)}")
except ImportError:
    print(f"  X PyTorch 未安装")

try:
    import transformers
    print(f"  OK Transformers: {transformers.__version__}")
except ImportError:
    print(f"  X Transformers 未安装")

try:
    import fastapi
    print(f"  OK FastAPI: {fastapi.__version__}")
except ImportError:
    print(f"  X FastAPI 未安装")

print("\n" + "=" * 60)

