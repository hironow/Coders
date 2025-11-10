# Benchmark Suite

This directory contains performance benchmarks comparing pygmt (ctypes) with pygmt_nb (nanobind).

## Benchmark Categories

### 1. Session Management (`benchmark_session.py`)
- Session creation overhead
- Session destruction cleanup
- Context manager overhead

### 2. Data I/O (`benchmark_dataio.py`)
- NumPy array → GMT transfer
- Matrix data transfer
- Vector data transfer
- Grid data transfer
- Virtual file creation

### 3. Module Execution (`benchmark_modules.py`)
- Simple module calls (gmtset, gmtdefaults)
- Data processing modules (grdmath, project)
- Plotting modules (basemap, coast)

### 4. Memory Usage (`benchmark_memory.py`)
- Session memory footprint
- Data transfer memory overhead
- Peak memory during operations

### 5. End-to-End Workflows (`benchmark_e2e.py`)
- Complete plotting workflow
- Data processing pipeline
- Multi-module workflows

## Metrics Collected

For each benchmark:
- **Execution time** (mean, median, std dev)
- **Memory usage** (current, peak)
- **Iterations per second**
- **Speedup ratio** (pygmt_nb vs pygmt)

## Running Benchmarks

```bash
# Run all benchmarks
just benchmark

# Run specific benchmark
just benchmark-category session

# Generate comparison report
just benchmark-report

# Run with profiling
just benchmark-profile
```

## Comparison Report Format

```
PyGMT vs PyGMT-nb Performance Comparison
========================================

Session Management
------------------
| Operation           | PyGMT (ctypes) | PyGMT-nb (nanobind) | Speedup |
|---------------------|----------------|---------------------|---------|
| Session creation    | 1.23 ms        | 0.45 ms             | 2.73x   |
| Context manager     | 1.45 ms        | 0.52 ms             | 2.79x   |

Data I/O
--------
| Operation           | PyGMT (ctypes) | PyGMT-nb (nanobind) | Speedup |
|---------------------|----------------|---------------------|---------|
| 1M float array      | 15.2 ms        | 2.3 ms              | 6.61x   |
| 10M float array     | 152 ms         | 23 ms               | 6.61x   |
```

## Current Status

- ✓ Benchmark framework structure
- ✓ Stub implementation benchmarks (baseline)
- [ ] PyGMT comparison (requires pygmt installation)
- [ ] Real GMT implementation benchmarks
- [ ] Memory profiling
- [ ] Visualization (charts)
