"""导入知识库预置数据脚本"""
import asyncio
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import AsyncSessionLocal, async_engine, Base
from models import KnowledgeBaseEntry
from services.knowledge_base_service import knowledge_base_service


async def import_data():
    """导入知识库数据"""
    # 读取种子数据
    seed_file = Path(__file__).parent.parent / "data" / "knowledge_base_seed.json"
    with open(seed_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    entries = data.get("entries", [])
    print(f"📚 准备导入 {len(entries)} 条知识库条目...")
    
    async with AsyncSessionLocal() as db:
        try:
            # 检查是否已有数据
            existing, total = await knowledge_base_service.list_entries(db, page=1, page_size=1)
            if total > 0:
                print(f"⚠️ 知识库已有 {total} 条数据，跳过导入")
                return

            # 批量创建
            from schemas.knowledge_base import KnowledgeBaseCreate
            create_entries = [KnowledgeBaseCreate(**e) for e in entries]

            created = await knowledge_base_service.bulk_create(db, create_entries)
            await db.commit()
            print(f"✅ 成功导入 {len(created)} 条知识库条目")
        except Exception as e:
            await db.rollback()
            print(f"❌ 导入失败: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(import_data())

