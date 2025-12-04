"""
Knowledge Base Service - Handles knowledge base operations with memory cache.
"""
import uuid
import logging
import re
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from models.knowledge_base import KnowledgeBaseEntry, KnowledgeBaseCategory
from schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    KnowledgeBaseSearchResult,
    KnowledgeBaseSearchRequest,
    KnowledgeBaseStats,
)

logger = logging.getLogger(__name__)


class KnowledgeBaseCache:
    """In-memory cache for knowledge base with inverted index."""
    
    def __init__(self):
        self._entries: Dict[str, dict] = {}  # entry_id -> entry data
        self._keyword_index: Dict[str, Set[str]] = defaultdict(set)  # keyword -> entry_ids
        self._category_index: Dict[str, Set[str]] = defaultdict(set)  # category -> entry_ids
        self._is_loaded: bool = False
    
    @property
    def is_loaded(self) -> bool:
        return self._is_loaded
    
    def clear(self) -> None:
        """Clear all cache data."""
        self._entries.clear()
        self._keyword_index.clear()
        self._category_index.clear()
        self._is_loaded = False
    
    def add_entry(self, entry_id: str, entry_data: dict) -> None:
        """Add an entry to the cache."""
        self._entries[entry_id] = entry_data
        
        # Update keyword index
        for keyword in entry_data.get("keywords", []):
            keyword_lower = keyword.lower()
            self._keyword_index[keyword_lower].add(entry_id)
        
        # Update category index
        category = entry_data.get("category", "")
        if category:
            self._category_index[category].add(entry_id)
    
    def remove_entry(self, entry_id: str) -> None:
        """Remove an entry from the cache."""
        if entry_id not in self._entries:
            return
        
        entry_data = self._entries[entry_id]
        
        # Remove from keyword index
        for keyword in entry_data.get("keywords", []):
            keyword_lower = keyword.lower()
            self._keyword_index[keyword_lower].discard(entry_id)
        
        # Remove from category index
        category = entry_data.get("category", "")
        if category:
            self._category_index[category].discard(entry_id)
        
        del self._entries[entry_id]
    
    def update_entry(self, entry_id: str, entry_data: dict) -> None:
        """Update an entry in the cache."""
        self.remove_entry(entry_id)
        self.add_entry(entry_id, entry_data)
    
    def get_entry(self, entry_id: str) -> Optional[dict]:
        """Get an entry by ID."""
        return self._entries.get(entry_id)
    
    def search_by_keywords(self, keywords: List[str]) -> List[Tuple[str, int]]:
        """Search entries by keywords, return (entry_id, match_count) pairs."""
        entry_matches: Dict[str, int] = defaultdict(int)
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Exact match
            if keyword_lower in self._keyword_index:
                for entry_id in self._keyword_index[keyword_lower]:
                    entry_matches[entry_id] += 2  # Higher weight for exact match
            
            # Partial match
            for cached_keyword, entry_ids in self._keyword_index.items():
                if keyword_lower in cached_keyword or cached_keyword in keyword_lower:
                    for entry_id in entry_ids:
                        entry_matches[entry_id] += 1
        
        # Sort by match count descending
        return sorted(entry_matches.items(), key=lambda x: x[1], reverse=True)
    
    def get_by_category(self, category: str) -> List[str]:
        """Get entry IDs by category."""
        return list(self._category_index.get(category, set()))
    
    def get_all_entries(self) -> List[dict]:
        """Get all cached entries."""
        return list(self._entries.values())
    
    def set_loaded(self, loaded: bool = True) -> None:
        """Set the loaded flag."""
        self._is_loaded = loaded


# Global cache instance
_cache = KnowledgeBaseCache()


class KnowledgeBaseService:
    """Service for knowledge base operations."""
    
    def __init__(self):
        self.cache = _cache
    
    async def load_cache(self, db: AsyncSession) -> None:
        """Load all active entries into cache."""
        if self.cache.is_loaded:
            return
        
        logger.info("Loading knowledge base into cache...")
        self.cache.clear()
        
        result = await db.execute(
            select(KnowledgeBaseEntry).where(KnowledgeBaseEntry.is_active == True)
        )
        entries = result.scalars().all()
        
        for entry in entries:
            self.cache.add_entry(entry.entry_id, self._entry_to_dict(entry))
        
        self.cache.set_loaded(True)
        logger.info(f"Loaded {len(entries)} entries into cache")
    
    def _entry_to_dict(self, entry: KnowledgeBaseEntry) -> dict:
        """Convert entry model to dictionary."""
        return {
            "entry_id": entry.entry_id,
            "category": entry.category.value if entry.category else None,
            "question": entry.question,
            "answer": entry.answer,
            "keywords": entry.keywords or [],
            "difficulty_level": entry.difficulty_level,
            "language": entry.language,
            "view_count": entry.view_count,
            "helpful_count": entry.helpful_count,
            "is_active": entry.is_active,
            "created_at": entry.created_at,
            "updated_at": entry.updated_at,
        }

    async def create_entry(
        self, db: AsyncSession, data: KnowledgeBaseCreate
    ) -> KnowledgeBaseEntry:
        """Create a new knowledge base entry."""
        entry = KnowledgeBaseEntry(
            entry_id=str(uuid.uuid4()),
            category=KnowledgeBaseCategory(data.category.value),
            question=data.question,
            answer=data.answer,
            keywords=data.keywords,
            difficulty_level=data.difficulty_level,
            language=data.language,
        )
        db.add(entry)
        await db.flush()

        # Update cache
        self.cache.add_entry(entry.entry_id, self._entry_to_dict(entry))

        return entry

    async def get_entry(
        self, db: AsyncSession, entry_id: str
    ) -> Optional[KnowledgeBaseEntry]:
        """Get an entry by ID."""
        result = await db.execute(
            select(KnowledgeBaseEntry).where(KnowledgeBaseEntry.entry_id == entry_id)
        )
        return result.scalar_one_or_none()

    async def update_entry(
        self, db: AsyncSession, entry_id: str, data: KnowledgeBaseUpdate
    ) -> Optional[KnowledgeBaseEntry]:
        """Update an existing entry."""
        entry = await self.get_entry(db, entry_id)
        if not entry:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "category" and value:
                value = KnowledgeBaseCategory(value.value)
            setattr(entry, field, value)

        await db.flush()

        # Update cache
        self.cache.update_entry(entry_id, self._entry_to_dict(entry))

        return entry

    async def delete_entry(self, db: AsyncSession, entry_id: str) -> bool:
        """Delete an entry (soft delete by setting is_active=False)."""
        entry = await self.get_entry(db, entry_id)
        if not entry:
            return False

        entry.is_active = False
        await db.flush()

        # Remove from cache
        self.cache.remove_entry(entry_id)

        return True

    async def list_entries(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        language: Optional[str] = None,
        is_active: bool = True,
    ) -> Tuple[List[KnowledgeBaseEntry], int]:
        """List entries with pagination and filters."""
        query = select(KnowledgeBaseEntry).where(
            KnowledgeBaseEntry.is_active == is_active
        )

        if category:
            query = query.where(KnowledgeBaseEntry.category == category)
        if language:
            query = query.where(KnowledgeBaseEntry.language == language)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        # Get paginated results
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        entries = result.scalars().all()

        return list(entries), total

    async def search(
        self, db: AsyncSession, request: KnowledgeBaseSearchRequest
    ) -> List[KnowledgeBaseSearchResult]:
        """Search knowledge base entries."""
        await self.load_cache(db)

        # Extract keywords from query
        keywords = self._extract_keywords(request.query)

        # Search in cache
        matches = self.cache.search_by_keywords(keywords)

        results = []
        for entry_id, match_count in matches[:request.limit * 2]:
            entry_data = self.cache.get_entry(entry_id)
            if not entry_data or not entry_data.get("is_active", True):
                continue

            # Apply filters
            if request.category and entry_data.get("category") != request.category.value:
                continue
            if request.language and entry_data.get("language") != request.language:
                continue

            difficulty = entry_data.get("difficulty_level", 2)
            if request.difficulty_min and difficulty < request.difficulty_min:
                continue
            if request.difficulty_max and difficulty > request.difficulty_max:
                continue

            # Calculate relevance score
            relevance = self._calculate_relevance(
                request.query, entry_data, keywords, match_count
            )

            # Find matched keywords
            matched = [k for k in keywords if k.lower() in
                      [kw.lower() for kw in entry_data.get("keywords", [])]]

            results.append(KnowledgeBaseSearchResult(
                entry=KnowledgeBaseResponse(**entry_data),
                relevance_score=relevance,
                matched_keywords=matched,
            ))

        # Sort by relevance and limit
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:request.limit]

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction: split by spaces and punctuation
        words = re.split(r'[\s,，。.!?！？;；:：\'"()（）\[\]【】]+', text)
        # Filter out short words and common stop words
        stop_words = {'的', '是', '在', '有', '和', '与', '或', '了', '吗', '呢',
                      'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                      'what', 'how', 'why', 'when', 'where', 'which', 'who',
                      '什么', '怎么', '如何', '为什么', '哪个', '哪些'}
        keywords = [w.lower() for w in words if len(w) >= 2 and w.lower() not in stop_words]
        return keywords

    def _calculate_relevance(
        self, query: str, entry: dict, keywords: List[str], match_count: int
    ) -> float:
        """Calculate relevance score between query and entry."""
        score = 0.0
        max_score = 10.0

        # Keyword match score (0-4)
        keyword_score = min(match_count / max(len(keywords), 1), 1.0) * 4
        score += keyword_score

        # Question text similarity (0-3)
        question = entry.get("question", "").lower()
        query_lower = query.lower()
        if query_lower in question:
            score += 3.0
        else:
            common_words = set(query_lower.split()) & set(question.split())
            score += min(len(common_words) / max(len(query_lower.split()), 1), 1.0) * 2

        # Category relevance (0-2)
        category_keywords = {
            "syntax_error": ["语法", "syntax", "error", "错误", "报错"],
            "logic_error": ["逻辑", "logic", "bug", "结果不对"],
            "environment": ["环境", "安装", "配置", "environment", "install"],
            "algorithm": ["算法", "algorithm", "复杂度", "效率"],
            "concept": ["概念", "理解", "什么是", "concept", "understand"],
        }
        for cat, cat_keywords in category_keywords.items():
            if entry.get("category") == cat:
                if any(kw in query_lower for kw in cat_keywords):
                    score += 2.0
                    break

        # Helpfulness bonus (0-1)
        if entry.get("view_count", 0) > 0:
            helpfulness = entry.get("helpful_count", 0) / entry.get("view_count", 1)
            score += helpfulness

        return min(score / max_score, 1.0)

    async def increment_view(self, db: AsyncSession, entry_id: str) -> None:
        """Increment view count for an entry."""
        entry = await self.get_entry(db, entry_id)
        if entry:
            entry.increment_view()
            await db.flush()
            # Update cache
            cached = self.cache.get_entry(entry_id)
            if cached:
                cached["view_count"] = entry.view_count

    async def increment_helpful(self, db: AsyncSession, entry_id: str) -> None:
        """Increment helpful count for an entry."""
        entry = await self.get_entry(db, entry_id)
        if entry:
            entry.increment_helpful()
            await db.flush()
            # Update cache
            cached = self.cache.get_entry(entry_id)
            if cached:
                cached["helpful_count"] = entry.helpful_count

    async def get_stats(self, db: AsyncSession) -> KnowledgeBaseStats:
        """Get knowledge base statistics."""
        # Total and active counts
        total = (await db.execute(
            select(func.count()).select_from(KnowledgeBaseEntry)
        )).scalar() or 0

        active = (await db.execute(
            select(func.count()).select_from(KnowledgeBaseEntry).where(
                KnowledgeBaseEntry.is_active == True
            )
        )).scalar() or 0

        # By category
        cat_result = await db.execute(
            select(KnowledgeBaseEntry.category, func.count()).group_by(
                KnowledgeBaseEntry.category
            )
        )
        by_category = {str(cat.value): count for cat, count in cat_result.all()}

        # By difficulty
        diff_result = await db.execute(
            select(KnowledgeBaseEntry.difficulty_level, func.count()).group_by(
                KnowledgeBaseEntry.difficulty_level
            )
        )
        by_difficulty = {str(level): count for level, count in diff_result.all()}

        # By language
        lang_result = await db.execute(
            select(KnowledgeBaseEntry.language, func.count()).where(
                KnowledgeBaseEntry.language.isnot(None)
            ).group_by(KnowledgeBaseEntry.language)
        )
        by_language = {lang or "unknown": count for lang, count in lang_result.all()}

        # Totals
        totals = await db.execute(
            select(
                func.sum(KnowledgeBaseEntry.view_count),
                func.sum(KnowledgeBaseEntry.helpful_count)
            )
        )
        total_views, total_helpful = totals.one()
        total_views = total_views or 0
        total_helpful = total_helpful or 0

        avg_helpfulness = total_helpful / total_views if total_views > 0 else 0.0

        return KnowledgeBaseStats(
            total_entries=total,
            active_entries=active,
            entries_by_category=by_category,
            entries_by_difficulty=by_difficulty,
            entries_by_language=by_language,
            total_views=total_views,
            total_helpful=total_helpful,
            average_helpfulness=avg_helpfulness,
        )

    async def bulk_create(
        self, db: AsyncSession, entries: List[KnowledgeBaseCreate]
    ) -> List[KnowledgeBaseEntry]:
        """Bulk create knowledge base entries."""
        created = []
        for data in entries:
            entry = await self.create_entry(db, data)
            created.append(entry)
        return created


# Global service instance
knowledge_base_service = KnowledgeBaseService()

