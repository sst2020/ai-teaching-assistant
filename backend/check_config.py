"""Check FastChat configuration"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import settings

print("=" * 60)
print("FastChat Configuration Check")
print("=" * 60)
print(f"USE_FASTCHAT: {settings.USE_FASTCHAT}")
print(f"FASTCHAT_API_BASE: {settings.FASTCHAT_API_BASE}")
print(f"FASTCHAT_MODEL_NAME: {settings.FASTCHAT_MODEL_NAME}")
print(f"FASTCHAT_TEMPERATURE: {settings.FASTCHAT_TEMPERATURE}")
print(f"FASTCHAT_MAX_TOKENS: {settings.FASTCHAT_MAX_TOKENS}")
print(f"FASTCHAT_TIMEOUT: {settings.FASTCHAT_TIMEOUT}")
print("=" * 60)

if settings.USE_FASTCHAT:
    print("[OK] FastChat is ENABLED")
else:
    print("[WARNING] FastChat is DISABLED")
    print("To enable FastChat, set USE_FASTCHAT=true in backend/.env")

