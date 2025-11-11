# Phase 3 Benchmark Results: Figure Methods

**Date**: 2025-11-11

> **⚠️ HISTORICAL DOCUMENT**: These benchmarks were conducted with the **classic mode** implementation.
> The project has since migrated to **modern mode** (November 11, 2025) with significantly improved performance.
>
> **Current Performance:** See `benchmark_modern_mode.py` for up-to-date results showing **103x speedup** via nanobind.
> - Simple basemap: 18.8 ms (vs 203 ms classic mode) - **10.8x faster**
> - Complete workflow: 291 ms (vs 495 ms classic mode) - **1.7x faster**

## Methods Benchmarked

1. **basemap()** - Map frames and axes
2. **coast()** - Coastlines and borders (Japan region, low resolution)
3. **plot()** - Scatter plots (100 data points)
4. **text()** - Text annotations (10 labels)
5. **Complete Workflow** - Multiple operations (basemap + plot + text)

## Summary

| Operation | pygmt_nb | PyGMT | Speedup | Memory |
|-----------|----------|-------|---------|--------|
| basemap() | 203.1 ms | - | - | 0.1 MB |
| coast() | 230.3 ms | - | - | 0.1 MB |
| plot() | 183.2 ms | - | - | 0.1 MB |
| text() | 191.8 ms | - | - | 0.1 MB |
| Complete Workflow | 494.9 ms | - | - | 0.1 MB |

## Detailed Results

### basemap()

**pygmt_nb**:
- Time: 203.076 ms ± 21.717 ms
- Throughput: 4.9 ops/sec
- Memory: 0.06 MB peak

### coast()

**pygmt_nb**:
- Time: 230.283 ms ± 17.540 ms
- Throughput: 4.3 ops/sec
- Memory: 0.06 MB peak

### plot()

**pygmt_nb**:
- Time: 183.198 ms ± 11.057 ms
- Throughput: 5.5 ops/sec
- Memory: 0.07 MB peak

### text()

**pygmt_nb**:
- Time: 191.817 ms ± 16.227 ms
- Throughput: 5.2 ops/sec
- Memory: 0.06 MB peak

### Complete Workflow

**pygmt_nb**:
- Time: 494.851 ms ± 32.372 ms
- Throughput: 2.0 ops/sec
- Memory: 0.07 MB peak

## Key Findings

- PyGMT comparison not available (PyGMT not installed)
- All pygmt_nb benchmarks completed successfully

## Notes

- All benchmarks use GMT classic mode (ps* commands)
- PostScript output files generated for all operations
- Warmup iterations: 3, Measurement iterations: 30
- Memory measurements include PostScript generation overhead
