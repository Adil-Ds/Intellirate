# Chapter: Data Structures and Algorithms in IntelliRate Gateway

## Abstract

This chapter explores the fundamental data structures and algorithms that power the IntelliRate API Gateway system. We examine how various data structures—from basic arrays and hash tables to advanced trees and graphs—are utilized throughout the application for efficient data management, request processing, and machine learning operations. The discussion encompasses algorithmic complexity analysis, search and sort algorithms, caching strategies, and the computational approaches employed in the gateway's core functionality.

---

## 1. Introduction to Data Structures in API Systems

### 1.1 Overview

Data structures and algorithms form the computational foundation of any software system. In the context of the IntelliRate API Gateway, they determine how efficiently the system can:
- Process incoming requests
- Store and retrieve cached data
- Manage rate limiting counters
- Execute machine learning predictions
- Query and analyze traffic logs

The choice of appropriate data structures directly impacts system performance, memory usage, and scalability—critical factors for an API gateway handling thousands of concurrent requests.

### 1.2 Importance in IntelliRate

The IntelliRate Gateway relies on data structures and algorithms in several key areas:

**Request Processing Pipeline:**
Every incoming request traverses a pipeline of operations, each requiring efficient data handling. From parsing JSON payloads to validating authentication tokens, data structures determine processing speed.

**Caching Infrastructure:**
Redis-based caching uses hash tables for O(1) key-value lookups, enabling sub-millisecond cache access that dramatically reduces response latency.

**Rate Limiting:**
Token bucket and sliding window algorithms track request counts, requiring efficient counter management and time-based expiration.

**Machine Learning:**
Feature vectors, model parameters, and prediction results all utilize specialized data structures optimized for numerical computation.

**Analytics and Logging:**
Efficient storage and querying of millions of request logs demands proper indexing and query optimization algorithms.

---

## 2. Fundamental Data Structures

### 2.1 Arrays and Lists

**Definition:**
Arrays are contiguous memory blocks storing elements of the same type, providing O(1) random access by index.

**Application in IntelliRate:**

1. **Request Messages Array:**
   ```python
   messages = [
       {"role": "system", "content": "You are an AI assistant"},
       {"role": "user", "content": "Analyze this data"}
   ]
   ```
   Chat messages are stored as arrays (Python lists) to preserve order and enable sequential processing.

2. **ML Feature Vectors:**
   ```python
   features = [150, 20, 15.5, 0.8, 0.3, 0.6]
   # [requests_per_minute, unique_endpoints, error_rate, ...]
   ```
   Machine learning models receive features as arrays for efficient numerical operations.

3. **Time Series Data:**
   ```python
   historical_traffic = [100, 120, 135, 110, 150, 145, 160]
   ```
   Prophet forecasting model processes time-series data as ordered arrays.

**Complexity Analysis:**
| Operation | Time Complexity |
|-----------|----------------|
| Access by index | O(1) |
| Search (unsorted) | O(n) |
| Insert at end | O(1) amortized |
| Insert at position | O(n) |
| Delete at position | O(n) |

### 2.2 Linked Lists

**Definition:**
A linked list consists of nodes, each containing data and a reference to the next node, enabling efficient insertions and deletions.

**Application in IntelliRate:**

1. **Request Queue Management:**
   ```
   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
   │ Req 1   │───>│ Req 2   │───>│ Req 3   │───>│ Req 4   │───> NULL
   │ (head)  │    │         │    │         │    │ (tail)  │
   └─────────┘    └─────────┘    └─────────┘    └─────────┘
   ```
   
2. **LRU Cache Implementation:**
   Doubly linked lists enable O(1) removal and reordering for Least Recently Used (LRU) cache eviction.

**Complexity Analysis:**
| Operation | Time Complexity |
|-----------|----------------|
| Access by position | O(n) |
| Insert at head/tail | O(1) |
| Delete with reference | O(1) |
| Search | O(n) |

### 2.3 Hash Tables (Dictionaries)

**Definition:**
Hash tables map keys to values using a hash function, providing average O(1) lookup, insertion, and deletion.

**Application in IntelliRate:**

1. **Configuration Storage:**
   ```python
   config = {
       "GROQ_API_URL": "https://api.groq.com/openai/v1/chat/completions",
       "RATE_LIMIT_FREE": 10,
       "RATE_LIMIT_PRO": 100,
       "RATE_LIMIT_ENTERPRISE": 1000,
       "ML_CACHE_TTL": 300
   }
   ```

2. **Request Headers:**
   ```python
   headers = {
       "Authorization": "Bearer eyJhbGc...",
       "Content-Type": "application/json",
       "X-User-Id": "firebase-uid-12345"
   }
   ```

3. **User Session Data:**
   ```python
   user_context = {
       "user_id": "uid123",
       "email": "user@example.com",
       "tier": "pro",
       "permissions": ["read", "write", "analyze"]
   }
   ```

4. **Redis Cache Keys:**
   ```python
   cache = {
       "rate_limit:uid123": 45,           # Current request count
       "user:uid123:tier": "pro",         # User tier
       "analytics:uid123": "{...json...}", # Cached analytics
       "abuse:hash123": "{...json...}"     # Cached ML prediction
   }
   ```

**Hash Function Example:**
```python
def hash_key(key: str) -> int:
    """Simple hash function for demonstration"""
    hash_value = 0
    for char in key:
        hash_value = (hash_value * 31 + ord(char)) % (2**32)
    return hash_value

# Real-world: Python uses SipHash for security against collision attacks
```

**Collision Handling:**
- **Chaining:** Each bucket contains a linked list of entries
- **Open Addressing:** Probe for next available slot (linear/quadratic probing)

```
Hash Table with Chaining:
┌─────────────────────────────────────────┐
│ Index │ Bucket                          │
├───────┼─────────────────────────────────┤
│   0   │ → (key1, val1) → (key5, val5)   │
│   1   │ → (key2, val2)                  │
│   2   │ → NULL                          │
│   3   │ → (key3, val3) → (key8, val8)   │
│   4   │ → (key4, val4)                  │
└───────┴─────────────────────────────────┘
```

**Complexity Analysis:**
| Operation | Average | Worst (collisions) |
|-----------|---------|-------------------|
| Insert | O(1) | O(n) |
| Lookup | O(1) | O(n) |
| Delete | O(1) | O(n) |

### 2.4 Sets

**Definition:**
Sets are collections of unique elements with O(1) membership testing (implemented using hash tables).

**Application in IntelliRate:**

1. **Unique Endpoints Tracking:**
   ```python
   accessed_endpoints = {
       "/api/v1/analyze",
       "/api/v1/users/profile",
       "/api/v1/analytics/usage"
   }
   unique_count = len(accessed_endpoints)  # 3
   ```

2. **CORS Allowed Origins:**
   ```python
   ALLOWED_ORIGINS = {
       "http://localhost:5173",
       "https://dataanlyzer.web.app",
       "https://dataanlyzer.firebaseapp.com"
   }
   
   def is_origin_allowed(origin: str) -> bool:
       return origin in ALLOWED_ORIGINS  # O(1) lookup
   ```

3. **Rate Limit User Exclusions:**
   ```python
   EXEMPT_USERS = {"admin-uid-001", "admin-uid-002", "test-user"}
   
   def should_apply_rate_limit(user_id: str) -> bool:
       return user_id not in EXEMPT_USERS
   ```

**Set Operations:**
```python
# Union - all endpoints across both users
user1_endpoints | user2_endpoints

# Intersection - common endpoints
user1_endpoints & user2_endpoints

# Difference - unique to user1
user1_endpoints - user2_endpoints
```

---

## 3. Advanced Data Structures

### 3.1 Trees

**Definition:**
Trees are hierarchical data structures with a root node and child nodes, forming a branching structure.

**Application in IntelliRate:**

**3.1.1 Binary Search Trees (BST):**

Used for ordered data storage with O(log n) operations:

```
          50 (Root)
         /  \
       30    70
      /  \   /  \
    20   40 60   80
```

**Application - Request Timestamp Indexing:**
```python
class TimeIndex:
    """BST for efficient time-range queries on request logs"""
    
    def insert(self, timestamp: datetime, request_id: str):
        # O(log n) insertion
        pass
    
    def find_range(self, start: datetime, end: datetime) -> List[str]:
        # O(log n + k) where k is number of results
        pass
```

**3.1.2 B-Trees and B+ Trees:**

PostgreSQL uses B+ trees for indexing the `request_logs` table:

```
              ┌────────────────┐
              │   100 | 200    │  Internal Node
              └───────┬────────┘
         ┌────────────┼────────────┐
         ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │ 10|50|75│  │120|150|180│ │220|250|280│  Leaf Nodes
   └────┬────┘  └────┬────┘  └────┬────┘
        │            │            │
   ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
   │ Records │  │ Records │  │ Records │  Data Pointers
   └─────────┘  └─────────┘  └─────────┘
```

**SQL Index Creation:**
```sql
CREATE INDEX idx_logs_user_timestamp 
ON request_logs (user_id, timestamp);
-- Creates B+ tree index for efficient queries
```

**3.1.3 Decision Trees (Machine Learning):**

XGBoost rate limit optimizer uses ensemble of decision trees:

```
                    [requests_per_min > 100?]
                   /                         \
                Yes                           No
                 |                             |
    [user_tier = 'enterprise'?]      [behavioral_score > 0.7?]
         /              \                  /              \
       Yes              No               Yes              No
        |                |                |                |
   Limit: 200       Limit: 80        Limit: 60        Limit: 30
```

**Feature Importance Analysis:**
```python
# XGBoost decision tree contribution
feature_importance = {
    'user_tier': 0.35,
    'historical_avg_requests': 0.25,
    'behavioral_consistency': 0.20,
    'time_of_day': 0.12,
    'day_of_week': 0.08
}
```

### 3.2 Heaps (Priority Queues)

**Definition:**
A heap is a complete binary tree where each parent is greater (max-heap) or smaller (min-heap) than its children.

**Application in IntelliRate:**

1. **Request Priority Queue:**
   ```python
   import heapq
   
   # Min-heap for request scheduling
   request_queue = []
   
   # Priority: (timestamp, priority_level, request_id)
   heapq.heappush(request_queue, (time.time(), 1, "req_enterprise_001"))
   heapq.heappush(request_queue, (time.time(), 3, "req_free_001"))
   heapq.heappush(request_queue, (time.time(), 2, "req_pro_001"))
   
   # Process highest priority first
   next_request = heapq.heappop(request_queue)
   ```

2. **Top-K Analytics:**
   ```python
   def get_top_users(logs: List[dict], k: int) -> List[dict]:
       """Get top K users by request count using max-heap"""
       user_counts = Counter(log['user_id'] for log in logs)
       
       # Use negative values for max-heap behavior
       heap = [(-count, user_id) for user_id, count in user_counts.items()]
       heapq.heapify(heap)
       
       return [heapq.heappop(heap) for _ in range(min(k, len(heap)))]
   ```

**Heap Structure:**
```
Max-Heap for Priority Queue:
           100 (highest priority)
          /   \
        75     80
       /  \   /  \
     50   60 70   55

Array representation: [100, 75, 80, 50, 60, 70, 55]
Parent of i: (i-1) // 2
Left child of i: 2i + 1
Right child of i: 2i + 2
```

**Complexity Analysis:**
| Operation | Time Complexity |
|-----------|----------------|
| Insert | O(log n) |
| Extract max/min | O(log n) |
| Peek max/min | O(1) |
| Heapify | O(n) |

### 3.3 Graphs

**Definition:**
Graphs consist of vertices (nodes) connected by edges, representing relationships between entities.

**Application in IntelliRate:**

1. **Service Dependency Graph:**
   ```
   ┌─────────────┐
   │   Client    │
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │  Gateway    │
   └──────┬──────┘
          │
     ┌────┴────┬────────────┐
     ▼         ▼            ▼
   ┌─────┐  ┌─────┐    ┌─────────┐
   │Redis│  │Postgres│  │SageMaker│
   └─────┘  └────┬────┘ └────┬────┘
                │            │
                ▼            ▼
          ┌──────────────────────┐
          │      Groq API        │
          └──────────────────────┘
   ```

   **Graph Representation:**
   ```python
   service_graph = {
       'client': ['gateway'],
       'gateway': ['redis', 'postgres', 'sagemaker', 'groq'],
       'redis': [],
       'postgres': [],
       'sagemaker': [],
       'groq': []
   }
   ```

2. **Request Flow Analysis:**
   Using Depth-First Search (DFS) to trace request paths:
   
   ```python
   def trace_request_path(graph: dict, start: str, end: str) -> List[str]:
       """Find path from client to backend service"""
       visited = set()
       path = []
       
       def dfs(node):
           if node == end:
               return True
           visited.add(node)
           path.append(node)
           
           for neighbor in graph.get(node, []):
               if neighbor not in visited:
                   if dfs(neighbor):
                       return True
           
           path.pop()
           return False
       
       dfs(start)
       return path
   ```

3. **Health Check Propagation:**
   Using Breadth-First Search (BFS) for dependency health checks:
   
   ```python
   from collections import deque
   
   async def check_service_health(service_graph: dict, start: str) -> dict:
       """BFS traversal to check all dependent service health"""
       queue = deque([start])
       visited = set()
       health_status = {}
       
       while queue:
           service = queue.popleft()
           if service in visited:
               continue
           
           visited.add(service)
           health_status[service] = await ping_service(service)
           
           for dependency in service_graph.get(service, []):
               if dependency not in visited:
                   queue.append(dependency)
       
       return health_status
   ```

**Graph Algorithms Applied:**
| Algorithm | Use Case | Complexity |
|-----------|----------|------------|
| DFS | Request path tracing | O(V + E) |
| BFS | Dependency health check | O(V + E) |
| Topological Sort | Service startup order | O(V + E) |

---

## 4. Algorithmic Patterns

### 4.1 Searching Algorithms

**4.1.1 Linear Search:**

Used for small collections or unsorted data:

```python
def find_user_in_logs(logs: List[dict], user_id: str) -> dict:
    """O(n) search through request logs"""
    for log in logs:
        if log['user_id'] == user_id:
            return log
    return None
```

**4.1.2 Binary Search:**

Used for sorted data or database index lookups:

```python
def binary_search_timestamp(
    sorted_logs: List[dict], 
    target_timestamp: datetime
) -> int:
    """O(log n) search in sorted logs"""
    left, right = 0, len(sorted_logs) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if sorted_logs[mid]['timestamp'] == target_timestamp:
            return mid
        elif sorted_logs[mid]['timestamp'] < target_timestamp:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1  # Not found
```

**Complexity Comparison:**
| Algorithm | Best | Average | Worst |
|-----------|------|---------|-------|
| Linear Search | O(1) | O(n) | O(n) |
| Binary Search | O(1) | O(log n) | O(log n) |
| Hash Table Lookup | O(1) | O(1) | O(n) |

### 4.2 Sorting Algorithms

**4.2.1 Quick Sort:**

Used for in-memory log sorting:

```python
def quicksort_logs(logs: List[dict], key: str) -> List[dict]:
    """O(n log n) average case sorting"""
    if len(logs) <= 1:
        return logs
    
    pivot = logs[len(logs) // 2]
    left = [x for x in logs if x[key] < pivot[key]]
    middle = [x for x in logs if x[key] == pivot[key]]
    right = [x for x in logs if x[key] > pivot[key]]
    
    return quicksort_logs(left, key) + middle + quicksort_logs(right, key)
```

**4.2.2 Merge Sort:**

Used for external sorting (large datasets):

```python
def merge_sorted_log_files(files: List[str]) -> Iterator[dict]:
    """Merge multiple sorted log files using k-way merge"""
    import heapq
    
    # Open all files and create iterators
    iterators = [iter_log_file(f) for f in files]
    
    # Initialize heap with first element from each file
    heap = []
    for i, it in enumerate(iterators):
        try:
            first = next(it)
            heapq.heappush(heap, (first['timestamp'], i, first))
        except StopIteration:
            pass
    
    # K-way merge
    while heap:
        timestamp, file_idx, log_entry = heapq.heappop(heap)
        yield log_entry
        
        try:
            next_entry = next(iterators[file_idx])
            heapq.heappush(heap, (next_entry['timestamp'], file_idx, next_entry))
        except StopIteration:
            pass
```

**4.2.3 Database Sorting:**

PostgreSQL uses various sorting algorithms:

```sql
-- Index-based sorting (B+ tree traversal)
SELECT * FROM request_logs 
ORDER BY timestamp DESC
LIMIT 100;

-- In-memory quicksort for small result sets
SELECT user_id, COUNT(*) as request_count
FROM request_logs
GROUP BY user_id
ORDER BY request_count DESC
LIMIT 10;
```

### 4.3 Time Complexity Analysis

**Big O Notation in IntelliRate Operations:**

| Operation | Description | Complexity |
|-----------|-------------|------------|
| Token validation | JWT signature verification | O(1)* |
| Rate limit check | Redis key lookup | O(1) |
| Cache lookup | Redis hash get | O(1) |
| Log insertion | PostgreSQL with index | O(log n) |
| User search by ID | Indexed query | O(log n) |
| Analytics aggregation | Full table scan | O(n) |
| ML prediction | Model inference | O(features × trees) |
| Sort logs by time | Database sort | O(n log n) |

*Assumed constant token size

---

## 5. Caching Algorithms

### 5.1 LRU (Least Recently Used) Cache

**Concept:**
Evict the least recently accessed item when the cache is full.

**Implementation:**

```python
from collections import OrderedDict

class LRUCache:
    """LRU Cache using OrderedDict (hash map + doubly linked list)"""
    
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: str, value: Any) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        
        self.cache[key] = value
        
        if len(self.cache) > self.capacity:
            # Remove least recently used (first item)
            self.cache.popitem(last=False)
```

**Visualization:**
```
LRU Cache (capacity=3):

Initial: [A] → [B] → [C]    (A is LRU, C is MRU)

Access B: [A] → [C] → [B]   (B moves to end)

Add D:    [C] → [B] → [D]   (A evicted, D added)
```

**Application in IntelliRate:**
```python
# ML prediction caching with LRU
prediction_cache = LRUCache(capacity=10000)

async def get_cached_prediction(features_hash: str) -> Optional[dict]:
    return prediction_cache.get(features_hash)

async def cache_prediction(features_hash: str, result: dict) -> None:
    prediction_cache.put(features_hash, result)
```

### 5.2 TTL (Time-To-Live) Cache

**Concept:**
Automatically expire cached items after a specified duration.

**Redis TTL Implementation:**
```python
import redis
import json

class TTLCache:
    def __init__(self, redis_client: redis.Redis, default_ttl: int = 300):
        self.redis = redis_client
        self.default_ttl = default_ttl
    
    async def get(self, key: str) -> Optional[dict]:
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: dict, ttl: int = None) -> None:
        ttl = ttl or self.default_ttl
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value)
        )
    
    async def delete(self, key: str) -> None:
        await self.redis.delete(key)
```

**Cache TTL Configuration:**
```python
CACHE_TTLS = {
    'user_profile': 3600,      # 1 hour
    'analytics': 300,          # 5 minutes
    'ml_prediction': 300,      # 5 minutes
    'rate_limit_count': 60,    # 1 minute (sliding window)
    'health_check': 30         # 30 seconds
}
```

### 5.3 Cache-Aside Pattern

**Flow:**
```
┌──────────────────────────────────────────────────────────────┐
│                     Cache-Aside Pattern                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Request → [Check Cache] ──Hit──→ Return Cached Data         │
│                 │                                             │
│                Miss                                           │
│                 ↓                                             │
│            [Query Database]                                   │
│                 │                                             │
│                 ↓                                             │
│            [Store in Cache]                                   │
│                 │                                             │
│                 ↓                                             │
│            Return Data                                        │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**Implementation:**
```python
async def get_user_analytics(user_id: str) -> dict:
    cache_key = f"analytics:{user_id}"
    
    # Step 1: Check cache
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    # Step 2: Query database (cache miss)
    analytics = await db.fetch_user_analytics(user_id)
    
    # Step 3: Store in cache
    await cache.set(cache_key, analytics, ttl=300)
    
    return analytics
```

---

## 6. Rate Limiting Algorithms

### 6.1 Token Bucket Algorithm

**Concept:**
Tokens are added to a bucket at a fixed rate. Each request consumes a token. Requests are rejected when the bucket is empty.

**Visualization:**
```
Token Bucket (capacity=10, refill=1 token/second):

Time 0:  [████████████] 10 tokens
Time 1:  [██████████░░]  8 tokens (2 requests consumed)
Time 2:  [████████████] 10 tokens (refilled, capped)
Time 3:  [░░░░░░░░░░░░]  0 tokens (burst of 10 requests)
Time 4:  [█░░░░░░░░░░░]  1 token  (1 refilled)
```

**Implementation:**
```python
import time

class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = capacity
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate
        )
        self.last_refill = now
```

### 6.2 Sliding Window Algorithm

**Concept:**
Track requests within a sliding time window rather than fixed intervals.

**Visualization:**
```
Sliding Window (60 seconds, limit=10):

Timeline:     |-------- 60 seconds --------|
              ▼                             ▼
Requests: [R1][R2][R3][R4][R5][R6][R7][R8][R9][R10][R11]
                                                    ↑
                                              REJECTED

Window slides as time progresses:
Old:      |-------- 60 seconds --------|
New:          |-------- 60 seconds --------|
              ↑
        R1 falls out of window
```

**Redis Implementation:**
```python
import time

class SlidingWindowRateLimiter:
    def __init__(self, redis_client, window_seconds: int, max_requests: int):
        self.redis = redis_client
        self.window = window_seconds
        self.max_requests = max_requests
    
    async def is_allowed(self, user_id: str) -> bool:
        key = f"rate_limit:{user_id}"
        now = time.time()
        window_start = now - self.window
        
        # Remove old entries
        await self.redis.zremrangebyscore(key, 0, window_start)
        
        # Count current window
        count = await self.redis.zcard(key)
        
        if count < self.max_requests:
            # Add new request
            await self.redis.zadd(key, {str(now): now})
            await self.redis.expire(key, self.window)
            return True
        
        return False
```

### 6.3 Rate Limiting by User Tier

**Configuration:**
```python
RATE_LIMITS = {
    'free': {'requests_per_minute': 10, 'burst': 5},
    'pro': {'requests_per_minute': 100, 'burst': 20},
    'enterprise': {'requests_per_minute': 1000, 'burst': 100}
}

async def check_rate_limit(user_id: str, tier: str) -> tuple[bool, int]:
    """Returns (is_allowed, retry_after_seconds)"""
    limits = RATE_LIMITS.get(tier, RATE_LIMITS['free'])
    
    rate_limiter = TokenBucket(
        capacity=limits['burst'],
        refill_rate=limits['requests_per_minute'] / 60
    )
    
    if rate_limiter.consume():
        return (True, 0)
    
    # Calculate retry time
    retry_after = 60 / limits['requests_per_minute']
    return (False, int(retry_after))
```

---

## 7. Machine Learning Data Structures

### 7.1 Feature Vectors

**Definition:**
Numerical arrays representing input data for ML models.

**IntelliRate Feature Vector:**
```python
# Abuse detection features
abuse_features = np.array([
    150,    # requests_per_minute
    20,     # unique_endpoints_accessed
    15.5,   # error_rate_percentage
    0.8,    # request_timing_patterns
    0.3,    # ip_reputation_score
    0.6     # endpoint_diversity_score
])

# Shape: (6,) - 1D array with 6 features
```

**Feature Normalization:**
```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
normalized_features = scaler.fit_transform(features.reshape(1, -1))

# Transforms to zero mean, unit variance
# Original: [150, 20, 15.5, 0.8, 0.3, 0.6]
# Normalized: [1.2, -0.5, 0.8, 0.1, -0.9, -0.2]
```

### 7.2 NumPy Arrays

**Matrix Operations:**
```python
import numpy as np

# Batch prediction - multiple users at once
batch_features = np.array([
    [150, 20, 15.5, 0.8, 0.3, 0.6],  # User 1
    [50, 5, 2.0, 0.9, 0.8, 0.3],     # User 2
    [200, 30, 25.0, 0.5, 0.1, 0.9]   # User 3
])

# Shape: (3, 6) - 3 users, 6 features each

# Model prediction (simplified)
weights = np.array([0.3, 0.2, 0.25, 0.1, -0.2, 0.15])
bias = 0.5

# Vectorized computation
predictions = np.dot(batch_features, weights) + bias
# Shape: (3,) - one prediction per user
```

### 7.3 Sparse Matrices

**Use Case:** User-endpoint interaction matrix

```python
from scipy.sparse import csr_matrix

# Users × Endpoints matrix (mostly zeros)
# Each cell = number of times user accessed endpoint
interaction_matrix = csr_matrix([
    [10, 0, 5, 0, 0, 0, 0, 0, 2, 0],  # User 1
    [0, 20, 0, 0, 3, 0, 0, 0, 0, 0],  # User 2
    [5, 0, 0, 15, 0, 0, 0, 0, 0, 8],  # User 3
])

# Memory efficient for sparse data
# Only non-zero values stored
```

### 7.4 Model Serialization

**Joblib for Model Storage:**
```python
import joblib

# Save trained model
joblib.dump(isolation_forest_model, 'ml-models/isolation_forest/model.joblib')

# Load model
model = joblib.load('ml-models/isolation_forest/model.joblib')

# Model structure includes:
# - Tree structures (arrays of nodes)
# - Split thresholds
# - Feature indices
# - Leaf values
```

---

## 8. Database Query Optimization

### 8.1 Index Data Structures

**B+ Tree Index:**
```sql
-- Create index for efficient lookups
CREATE INDEX idx_logs_user_id ON request_logs (user_id);

-- Query uses index (O(log n) lookup)
SELECT * FROM request_logs WHERE user_id = 'uid123';
```

**Hash Index:**
```sql
-- For exact match queries only
CREATE INDEX idx_logs_user_hash ON request_logs USING hash (user_id);
```

**Composite Index:**
```sql
-- Multi-column index for complex queries
CREATE INDEX idx_logs_user_time ON request_logs (user_id, timestamp DESC);

-- Efficient query using index
SELECT * FROM request_logs 
WHERE user_id = 'uid123' 
ORDER BY timestamp DESC 
LIMIT 100;
```

### 8.2 Query Execution Plans

**EXPLAIN ANALYZE:**
```sql
EXPLAIN ANALYZE
SELECT user_id, COUNT(*) as request_count
FROM request_logs
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY user_id
ORDER BY request_count DESC
LIMIT 10;

-- Output shows:
-- Index Scan vs Sequential Scan
-- Estimated vs Actual rows
-- Execution time per operation
```

### 8.3 Aggregation Algorithms

**Hash Aggregation:**
```
┌─────────────────────────────────────────┐
│        Hash Aggregation                  │
├─────────────────────────────────────────┤
│ Hash Table:                              │
│ {                                        │
│   hash(uid1): {count: 150, sum: 5000},  │
│   hash(uid2): {count: 75, sum: 2500},   │
│   hash(uid3): {count: 200, sum: 8000},  │
│   ...                                    │
│ }                                        │
│                                          │
│ Single pass: O(n) time, O(groups) space │
└─────────────────────────────────────────┘
```

**Sort Aggregation:**
```
Sort by user_id → Group consecutive rows → Compute aggregates

O(n log n) time for sort, O(1) extra space
```

---

## 9. Concurrent Data Structures

### 9.1 Thread-Safe Queues

**Asyncio Queue:**
```python
import asyncio

request_queue = asyncio.Queue(maxsize=1000)

async def producer(request):
    await request_queue.put(request)

async def consumer():
    while True:
        request = await request_queue.get()
        await process_request(request)
        request_queue.task_done()
```

### 9.2 Atomic Counters

**Redis Atomic Operations:**
```python
async def increment_counter(key: str) -> int:
    """Atomic increment operation"""
    return await redis.incr(key)

async def track_request_count(user_id: str) -> int:
    key = f"requests:{user_id}:{datetime.now().strftime('%Y-%m-%d')}"
    count = await increment_counter(key)
    await redis.expire(key, 86400)  # Expire after 24 hours
    return count
```

### 9.3 Connection Pooling

**Pool Data Structure:**
```python
class ConnectionPool:
    def __init__(self, max_size: int):
        self.pool = asyncio.Queue(maxsize=max_size)
        self.semaphore = asyncio.Semaphore(max_size)
    
    async def acquire(self):
        await self.semaphore.acquire()
        try:
            return await self.pool.get_nowait()
        except asyncio.QueueEmpty:
            return await self._create_connection()
    
    async def release(self, conn):
        await self.pool.put(conn)
        self.semaphore.release()
```

---

## 10. Algorithm Optimization Techniques

### 10.1 Memoization

**Caching Function Results:**
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def compute_user_risk_score(
    requests_per_minute: int,
    error_rate: float,
    endpoint_diversity: float
) -> float:
    """Expensive computation cached"""
    # Complex risk calculation
    base_score = requests_per_minute * 0.3
    error_penalty = error_rate * 0.5
    diversity_bonus = endpoint_diversity * 0.2
    return base_score + error_penalty - diversity_bonus
```

### 10.2 Lazy Evaluation

**Generator for Large Datasets:**
```python
def stream_logs(start_date: datetime, end_date: datetime):
    """Lazy evaluation - processes one record at a time"""
    query = """
        SELECT * FROM request_logs
        WHERE timestamp BETWEEN %s AND %s
        ORDER BY timestamp
    """
    
    cursor = db.execute(query, (start_date, end_date))
    
    for row in cursor:
        yield {
            'user_id': row[0],
            'timestamp': row[1],
            'endpoint': row[2],
            # ... more fields
        }

# Memory efficient - doesn't load all records at once
for log in stream_logs(start, end):
    process_log(log)
```

### 10.3 Batch Processing

**Bulk Operations:**
```python
async def bulk_insert_logs(logs: List[dict]) -> None:
    """Batch insert for efficiency"""
    
    # Single query with multiple values (much faster)
    values = [(log['user_id'], log['timestamp'], log['endpoint']) 
              for log in logs]
    
    await db.executemany(
        "INSERT INTO request_logs (user_id, timestamp, endpoint) VALUES ($1, $2, $3)",
        values
    )

# Instead of: 1000 individual INSERT queries
# Execute: 1 batch INSERT with 1000 rows
```

---

## 11. Complexity Summary Table

| Component | Operation | Data Structure | Time Complexity |
|-----------|-----------|----------------|-----------------|
| Cache | Lookup | Hash Table | O(1) |
| Cache | LRU Eviction | OrderedDict | O(1) |
| Rate Limiter | Check Limit | Redis Sorted Set | O(log n) |
| Rate Limiter | Token Bucket | Float Counter | O(1) |
| Database | Index Lookup | B+ Tree | O(log n) |
| Database | Full Scan | Array | O(n) |
| Database | Aggregation | Hash Table | O(n) |
| ML Inference | Prediction | Decision Tree | O(depth) |
| ML Inference | Batch | Matrix Multiply | O(n × features) |
| Logging | Insert | B+ Tree Index | O(log n) |
| Analytics | Top-K | Heap | O(n log k) |
| Health Check | BFS | Graph | O(V + E) |

---

## 12. Conclusion

### 12.1 Summary

The IntelliRate Gateway demonstrates practical application of fundamental data structures and algorithms:

1. **Hash Tables:** Core to caching, configuration, and fast lookups
2. **Trees:** Database indexing and ML decision trees
3. **Heaps:** Priority queues and top-K analytics
4. **Graphs:** Service dependencies and health checks
5. **Caching Algorithms:** LRU, TTL for performance optimization
6. **Rate Limiting:** Token bucket and sliding window algorithms
7. **Search/Sort:** Binary search, quicksort for log processing
8. **Concurrent Structures:** Thread-safe queues and atomic counters

### 12.2 Key Takeaways

- **Choose appropriate data structures:** O(1) hash lookups vs O(log n) tree operations
- **Consider space-time tradeoffs:** Caching uses memory to save computation
- **Design for scalability:** Algorithms that scale with data growth
- **Optimize hot paths:** Focus on frequently executed code paths
- **Leverage database optimizations:** Proper indexing and query planning

### 12.3 Future Considerations

- **Bloom Filters:** Probabilistic data structure for membership testing
- **Skip Lists:** Alternative to balanced trees with O(log n) operations
- **Consistent Hashing:** Distributed caching with minimal redistribution
- **Trie Structures:** Efficient prefix matching for route matching

---

## References

1. Cormen, T. H., et al. (2009). Introduction to Algorithms (3rd ed.). MIT Press.
2. Sedgewick, R., & Wayne, K. (2011). Algorithms (4th ed.). Addison-Wesley.
3. Kleppmann, M. (2017). Designing Data-Intensive Applications. O'Reilly Media.
4. Redis Documentation. https://redis.io/documentation
5. PostgreSQL Documentation. https://www.postgresql.org/docs/
6. Python Data Structures. https://docs.python.org/3/tutorial/datastructures.html
7. NumPy Documentation. https://numpy.org/doc/
8. scikit-learn Documentation. https://scikit-learn.org/stable/documentation.html
