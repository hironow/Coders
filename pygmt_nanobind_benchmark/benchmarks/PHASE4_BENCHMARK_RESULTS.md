# Phase 4 Benchmark Results: colorbar + grdcontour

**Date**: 2025-11-11

> **⚠️ HISTORICAL DOCUMENT**: These benchmarks were conducted with the **classic mode** implementation.
> The project has since migrated to **modern mode** (November 11, 2025) with significantly improved performance via nanobind.
>
> **Current Performance:** See `benchmark_modern_mode.py` for complete modern mode benchmark results showing **103x speedup**.

## Methods Benchmarked

1. **colorbar()** - Color scale bar (after grdimage)
2. **grdcontour()** - Grid contour lines (interval=100, annotation=500)
3. **grdimage + colorbar** - Complete workflow
4. **grdimage + grdcontour** - Contour overlay on image
5. **Complete Map** - basemap + grdimage + grdcontour + colorbar

## Summary

| Operation | Time | Ops/sec | Memory |
|-----------|------|---------|--------|
| colorbar() | 293.9 ms | 3.4 | 0.06 MB |
| grdcontour() | 196.4 ms | 5.1 | 0.06 MB |
| grdimage + colorbar | 386.7 ms | 2.6 | 0.06 MB |
| grdimage + grdcontour | 374.3 ms | 2.7 | 0.06 MB |
| Complete Map Workflow | 469.1 ms | 2.1 | 0.06 MB |

## Detailed Results

### colorbar()

**pygmt_nb**:
- Time: 293.864 ms ± 9.852 ms
- Throughput: 3.4 ops/sec
- Memory: 0.06 MB peak

### grdcontour()

**pygmt_nb**:
- Time: 196.404 ms ± 9.904 ms
- Throughput: 5.1 ops/sec
- Memory: 0.06 MB peak

### grdimage + colorbar

**pygmt_nb**:
- Time: 386.662 ms ± 9.411 ms
- Throughput: 2.6 ops/sec
- Memory: 0.06 MB peak

### grdimage + grdcontour

**pygmt_nb**:
- Time: 374.297 ms ± 16.748 ms
- Throughput: 2.7 ops/sec
- Memory: 0.06 MB peak

### Complete Map Workflow

**pygmt_nb**:
- Time: 469.145 ms ± 24.135 ms
- Throughput: 2.1 ops/sec
- Memory: 0.06 MB peak

## Key Findings

- **colorbar()**: Lightweight addition to grid visualization
- **grdcontour()**: Efficient contour line generation
- **Workflows**: Multiple operations compose efficiently
- **Memory**: Consistently low memory usage (~0.06-0.08 MB peak)

## Notes

- All benchmarks use GMT classic mode (ps* commands)
- PostScript output files generated for all operations
- Warmup iterations: 3, Measurement iterations: 30
- Grid: test_grid.nc (10x10 region)
- Memory measurements include PostScript generation overhead
