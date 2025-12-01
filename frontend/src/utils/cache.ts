/**
 * Simple in-memory cache utility for API responses.
 * Helps reduce redundant API calls and improve performance.
 */

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
}

class SimpleCache {
  private cache: Map<string, CacheEntry<unknown>> = new Map();
  private defaultTTL: number = 5 * 60 * 1000; // 5 minutes default

  /**
   * Get a cached value if it exists and hasn't expired.
   */
  get<T>(key: string): T | null {
    const entry = this.cache.get(key) as CacheEntry<T> | undefined;
    
    if (!entry) {
      return null;
    }

    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  /**
   * Set a value in the cache with optional TTL.
   */
  set<T>(key: string, data: T, ttlMs?: number): void {
    const ttl = ttlMs ?? this.defaultTTL;
    const now = Date.now();
    
    this.cache.set(key, {
      data,
      timestamp: now,
      expiresAt: now + ttl,
    });
  }

  /**
   * Remove a specific key from the cache.
   */
  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  /**
   * Clear all entries matching a prefix.
   */
  clearByPrefix(prefix: string): void {
    for (const key of this.cache.keys()) {
      if (key.startsWith(prefix)) {
        this.cache.delete(key);
      }
    }
  }

  /**
   * Clear all cached entries.
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Get cache statistics.
   */
  getStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
    };
  }
}

// Singleton instance
export const apiCache = new SimpleCache();

// Cache key generators
export const cacheKeys = {
  assignment: (id: string) => `assignment:${id}`,
  assignments: (filters?: string) => `assignments:${filters || 'all'}`,
  submission: (id: string) => `submission:${id}`,
  submissions: (filters?: string) => `submissions:${filters || 'all'}`,
  submissionStats: () => 'submission:stats',
  studentProfile: () => 'student:profile',
  studentStats: () => 'student:stats',
  courses: () => 'courses:all',
  rubric: (assignmentId: string) => `rubric:${assignmentId}`,
};

// Cache TTL constants (in milliseconds)
export const cacheTTL = {
  short: 30 * 1000,        // 30 seconds - for frequently changing data
  medium: 5 * 60 * 1000,   // 5 minutes - default
  long: 15 * 60 * 1000,    // 15 minutes - for rarely changing data
  veryLong: 60 * 60 * 1000, // 1 hour - for static data
};

/**
 * Wrapper function to cache API calls.
 */
export async function cachedFetch<T>(
  key: string,
  fetchFn: () => Promise<T>,
  ttlMs?: number
): Promise<T> {
  // Check cache first
  const cached = apiCache.get<T>(key);
  if (cached !== null) {
    console.log(`[Cache] HIT: ${key}`);
    return cached;
  }

  // Fetch and cache
  console.log(`[Cache] MISS: ${key}`);
  const data = await fetchFn();
  apiCache.set(key, data, ttlMs);
  return data;
}

/**
 * Invalidate cache entries after mutations.
 */
export function invalidateCache(patterns: string[]): void {
  for (const pattern of patterns) {
    apiCache.clearByPrefix(pattern);
  }
  console.log(`[Cache] Invalidated: ${patterns.join(', ')}`);
}

