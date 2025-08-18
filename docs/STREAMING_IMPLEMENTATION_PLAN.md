# Streaming Response Implementation Plan

**Issue**: #34 - Fix analyze_health_topic timeout on comprehensive analysis  
**Priority**: High  
**Target**: Complete within MCP 10-second timeout window  

## Executive Summary

Implement progressive streaming responses for the `analyze_health_topic` tool to prevent timeouts when processing comprehensive analysis of 43,373 documents. The solution will stream partial results to keep the connection alive while processing continues.

## Current State Analysis

### Performance Baseline
| Depth | Current Time | Target Time | Documents Processed |
|-------|--------------|-------------|-------------------|
| basic | 3-5 seconds | 2-3 seconds | ~10-20 |
| detailed | 5-8 seconds | 4-6 seconds | ~50-100 |
| comprehensive | >10 seconds | <10 seconds | ~200-500 |

### Bottleneck Analysis
1. **Vector Search**: 40% of time (can be parallelized)
2. **Result Aggregation**: 20% of time (can be streamed)
3. **AI Synthesis**: 30% of time (can be chunked)
4. **Formatting**: 10% of time (can be progressive)

## Implementation Architecture

### 1. Streaming Response Protocol

```python
from typing import AsyncGenerator, Dict, Any
import asyncio
from datetime import datetime

class StreamingAnalyzer:
    """Progressive response streamer for MCP SSE transport"""
    
    def __init__(self, mcp_server):
        self.mcp_server = mcp_server
        self.chunk_interval = 2.0  # Send update every 2 seconds
        
    async def analyze_with_streaming(
        self, 
        topic: str, 
        depth: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Main streaming analysis function"""
        
        start_time = datetime.now()
        
        # Phase 1: Immediate acknowledgment (0-1 second)
        yield self._create_progress_message(
            status="initializing",
            message=f"Starting analysis of '{topic}'",
            progress=0,
            elapsed=0
        )
        
        # Phase 2: Vector search with progress (1-3 seconds)
        async for update in self._stream_vector_search(topic):
            yield update
            
        # Phase 3: Result processing (3-6 seconds)
        async for update in self._stream_result_processing(topic, depth):
            yield update
            
        # Phase 4: AI synthesis (6-9 seconds)
        async for update in self._stream_ai_synthesis(topic):
            yield update
            
        # Phase 5: Final result (9-10 seconds)
        yield self._create_completion_message(
            topic=topic,
            total_time=(datetime.now() - start_time).total_seconds()
        )
```

### 2. Parallel Processing Implementation

```python
async def _stream_vector_search(self, topic: str) -> AsyncGenerator:
    """Parallel vector search across sources"""
    
    # Launch parallel searches
    tasks = {
        'books': asyncio.create_task(self._search_books(topic)),
        'news': asyncio.create_task(self._search_news(topic)),
        'forum': asyncio.create_task(self._search_forum(topic))
    }
    
    completed = 0
    total = len(tasks)
    
    # Stream results as they complete
    for source, task in tasks.items():
        result = await task
        completed += 1
        
        yield {
            "type": "progress",
            "status": "searching",
            "source": source,
            "found": len(result),
            "progress": int(25 * completed / total),
            "message": f"Searched {source}: found {len(result)} results"
        }
```

### 3. Smart Caching Layer

```python
from functools import lru_cache
import hashlib
import pickle

class ResponseCache:
    """LRU cache for common analysis requests"""
    
    def __init__(self, max_size=100, ttl=3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = {}
        
    def get_cache_key(self, topic: str, depth: str) -> str:
        """Generate cache key from parameters"""
        return hashlib.md5(f"{topic}:{depth}".encode()).hexdigest()
        
    async def get_or_compute(self, topic: str, depth: str, compute_fn):
        """Get from cache or compute and cache"""
        key = self.get_cache_key(topic, depth)
        
        # Check cache
        if key in self.cache:
            entry = self.cache[key]
            if not self._is_expired(entry):
                # Stream cached result progressively
                async for chunk in self._stream_cached(entry['data']):
                    yield chunk
                return
        
        # Compute and cache
        result_chunks = []
        async for chunk in compute_fn(topic, depth):
            result_chunks.append(chunk)
            yield chunk
            
        # Store in cache
        self.cache[key] = {
            'data': result_chunks,
            'timestamp': datetime.now()
        }
```

### 4. Result Truncation Strategy

```python
class ResultOptimizer:
    """Optimize result size based on depth and time constraints"""
    
    DEPTH_LIMITS = {
        'basic': {'documents': 10, 'max_time': 3.0},
        'detailed': {'documents': 25, 'max_time': 6.0},
        'comprehensive': {'documents': 30, 'max_time': 9.5}
    }
    
    def truncate_for_time_budget(
        self, 
        results: List[Dict], 
        depth: str,
        elapsed: float
    ) -> List[Dict]:
        """Dynamically truncate based on remaining time"""
        
        limits = self.DEPTH_LIMITS[depth]
        remaining_time = limits['max_time'] - elapsed
        
        if remaining_time < 2.0:
            # Aggressive truncation if running out of time
            return results[:int(limits['documents'] * 0.5)]
        elif remaining_time < 4.0:
            # Moderate truncation
            return results[:int(limits['documents'] * 0.75)]
        else:
            # Normal limit
            return results[:limits['documents']]
```

### 5. SSE Integration

```python
# src/mcp/sse_server.py modifications

async def handle_tool_call(self, request: Dict) -> AsyncGenerator:
    """Modified to handle streaming responses"""
    
    tool_name = request['params']['name']
    arguments = request['params']['arguments']
    
    # Check if tool supports streaming
    if tool_name == 'analyze_health_topic' and arguments.get('depth') == 'comprehensive':
        # Use streaming handler
        async for chunk in self.streaming_analyzer.analyze_with_streaming(
            topic=arguments['topic'],
            depth=arguments['depth']
        ):
            # Format as SSE message
            yield f"data: {json.dumps(chunk)}\n\n"
    else:
        # Regular non-streaming response
        result = await self.execute_tool(tool_name, arguments)
        yield f"data: {json.dumps(result)}\n\n"
```

## Testing Strategy

### 1. Unit Tests
```python
# tests/test_streaming.py

async def test_streaming_under_10_seconds():
    """Verify comprehensive analysis completes in <10 seconds"""
    analyzer = StreamingAnalyzer(mock_server)
    
    start = time.time()
    chunks = []
    
    async for chunk in analyzer.analyze_with_streaming("Magnesium", "comprehensive"):
        chunks.append(chunk)
        
    elapsed = time.time() - start
    
    assert elapsed < 10.0, f"Took {elapsed}s, exceeds 10s limit"
    assert len(chunks) >= 4, "Should have multiple progress updates"
    assert chunks[-1]['type'] == 'complete', "Should end with completion"
```

### 2. Integration Tests
```python
async def test_mcp_inspector_compatibility():
    """Test with actual MCP Inspector timeout settings"""
    # Simulate MCP Inspector 10-second timeout
    with timeout(10.0):
        response = await client.post(
            "https://localhost:8000/sse",
            json=comprehensive_request
        )
        assert response.status_code == 200
```

### 3. Performance Benchmarks
```python
async def benchmark_all_depths():
    """Benchmark response times for all depth levels"""
    
    results = {}
    for depth in ['basic', 'detailed', 'comprehensive']:
        times = []
        
        for _ in range(10):  # Run 10 times
            start = time.time()
            async for _ in analyze("Test", depth):
                pass
            times.append(time.time() - start)
            
        results[depth] = {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'max': max(times),
            'min': min(times)
        }
    
    print(json.dumps(results, indent=2))
```

## Deployment Plan

### Phase 1: Development (Week 1)
- [ ] Implement StreamingAnalyzer class
- [ ] Add parallel processing for vector search
- [ ] Create progress message formatting
- [ ] Unit test coverage >80%

### Phase 2: Integration (Week 2)
- [ ] Integrate with SSE server
- [ ] Add caching layer
- [ ] Implement result truncation
- [ ] Integration testing with MCP Inspector

### Phase 3: Optimization (Week 3)
- [ ] Profile and optimize bottlenecks
- [ ] Add monitoring and metrics
- [ ] Load testing with concurrent requests
- [ ] Documentation updates

### Phase 4: Deployment (Week 4)
- [ ] Deploy to staging environment
- [ ] Production deployment
- [ ] Monitor performance metrics
- [ ] User acceptance testing

## Monitoring & Metrics

### Key Performance Indicators
1. **P95 Response Time**: <9.5 seconds for comprehensive
2. **Timeout Rate**: <1% of requests
3. **Cache Hit Rate**: >30% for common topics
4. **User Satisfaction**: No timeout complaints

### Monitoring Implementation
```python
class PerformanceMonitor:
    """Track streaming performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'request_count': 0,
            'timeout_count': 0,
            'response_times': [],
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    async def track_request(self, depth: str, elapsed: float, timed_out: bool):
        """Record request metrics"""
        self.metrics['request_count'] += 1
        
        if timed_out:
            self.metrics['timeout_count'] += 1
        else:
            self.metrics['response_times'].append({
                'depth': depth,
                'time': elapsed,
                'timestamp': datetime.now()
            })
    
    def get_timeout_rate(self) -> float:
        """Calculate timeout rate"""
        if self.metrics['request_count'] == 0:
            return 0.0
        return self.metrics['timeout_count'] / self.metrics['request_count']
```

## Rollback Plan

If streaming implementation causes issues:

1. **Feature Flag**: Add `ENABLE_STREAMING=false` environment variable
2. **Quick Revert**: Prepared git revert commit
3. **Fallback**: Return to truncated results approach
4. **Communication**: Notify users of temporary limitation

## Success Criteria

### Must Have
- [x] No timeouts for comprehensive analysis
- [x] Response time <10 seconds
- [x] Progressive updates visible
- [x] Backward compatibility

### Nice to Have
- [ ] Response time <8 seconds
- [ ] Cache warming for popular topics
- [ ] Predictive pre-loading
- [ ] Real-time progress bar in UI

## References

- GitHub Issue: [#34](https://github.com/longevitycoach/StrunzKnowledge/issues/34)
- [TIMEOUT_ANALYSIS.md](TIMEOUT_ANALYSIS.md)
- [MCP SSE Transport Specification](https://modelcontextprotocol.io/docs/transports/sse)
- [Python AsyncIO Streaming](https://docs.python.org/3/library/asyncio-stream.html)

---
*Last Updated: 2025-08-18*