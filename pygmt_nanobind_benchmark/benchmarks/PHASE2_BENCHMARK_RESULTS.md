# Phase 2 Benchmark Results: Grid + NumPy Integration

**Grid File**: `large_grid.nc`
**Grid Size**: 201 × 201 = 40,401 elements
**Region**: (0.0, 100.0, 0.0, 100.0)

## Summary

| Operation | pygmt_nb | PyGMT | Speedup | Memory Improvement |
|-----------|----------|-------|---------|-------------------|
| Grid Loading | 8.23 ms | 24.13 ms | **2.93x** | **784.47x** |
| Data Access | 0.05 ms | 0.04 ms | **0.80x** | **0.56x** |
| Data Manipulation | 0.24 ms | 0.19 ms | **0.78x** | **1.00x** |

## Detailed Results

### Grid Loading

**pygmt_nb**:
- Time: 8.234 ms ± 0.528 ms
- Throughput: 121.4 ops/sec
- Memory: 0.00 MB peak

**PyGMT**:
- Time: 24.131 ms ± 1.465 ms
- Throughput: 41.4 ops/sec
- Memory: 0.33 MB peak

**Comparison**:
- ✅ pygmt_nb is **2.93x faster**
- ✅ pygmt_nb uses **784.47x less memory**

### Data Access

**pygmt_nb**:
- Time: 0.050 ms ± 0.005 ms
- Throughput: 19828.1 ops/sec
- Memory: 0.00 MB peak

**PyGMT**:
- Time: 0.041 ms ± 0.005 ms
- Throughput: 24671.8 ops/sec
- Memory: 0.00 MB peak

**Comparison**:
- ⚠️  pygmt_nb is 1.24x slower
- ⚠️  pygmt_nb uses 1.79x more memory

### Data Manipulation

**pygmt_nb**:
- Time: 0.239 ms ± 0.034 ms
- Throughput: 4182.2 ops/sec
- Memory: 0.31 MB peak

**PyGMT**:
- Time: 0.186 ms ± 0.012 ms
- Throughput: 5371.3 ops/sec
- Memory: 0.31 MB peak

**Comparison**:
- ⚠️  pygmt_nb is 1.28x slower
- ⚠️  pygmt_nb uses 1.00x more memory
