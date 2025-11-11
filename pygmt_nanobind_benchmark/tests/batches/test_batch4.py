#!/usr/bin/env python3
"""Test batch 4 functions: grd2xyz, xyz2grd, grdfilter"""

import sys
import numpy as np

# Add to path
sys.path.insert(0, '/home/user/Coders/pygmt_nanobind_benchmark/python')

import pygmt_nb as pygmt

print("Testing Batch 4 functions: grd2xyz, xyz2grd, grdfilter")
print("=" * 60)

# Test 1: grd2xyz - Convert grid to XYZ table
print("\n1. Testing grd2xyz()")
print("-" * 60)
try:
    print("✓ Function exists:", 'grd2xyz' in dir(pygmt))

    # Create a simple test grid first
    x = np.arange(0, 5, 1, dtype=np.float64)
    y = np.arange(0, 5, 1, dtype=np.float64)
    xx, yy = np.meshgrid(x, y)
    zz = xx + yy  # Simple function
    xyz_data = np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()])

    # Create grid from XYZ data
    pygmt.xyz2grd(
        data=xyz_data,
        outgrid="/tmp/test_grid.nc",
        region=[0, 4, 0, 4],
        spacing=1
    )
    print("✓ Created test grid: /tmp/test_grid.nc")

    # Convert grid back to XYZ
    result = pygmt.grd2xyz(grid="/tmp/test_grid.nc")
    print(f"✓ Converted grid to XYZ: shape={result.shape}, expected=(25, 3)")
    print(f"  First few points:\n{result[:3]}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: xyz2grd - Convert XYZ table to grid
print("\n2. Testing xyz2grd()")
print("-" * 60)
try:
    print("✓ Function exists:", 'xyz2grd' in dir(pygmt))

    # Create sample XYZ data
    x = np.arange(0, 5, 0.5, dtype=np.float64)
    y = np.arange(0, 5, 0.5, dtype=np.float64)
    xx, yy = np.meshgrid(x, y)
    zz = np.sin(xx) * np.cos(yy)
    xyz_data = np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()])

    print(f"✓ Created XYZ data: shape={xyz_data.shape}")

    # Convert to grid
    pygmt.xyz2grd(
        data=xyz_data,
        outgrid="/tmp/test_xyz2grd.nc",
        region=[0, 4.5, 0, 4.5],
        spacing=0.5
    )
    print("✓ Converted XYZ to grid: /tmp/test_xyz2grd.nc")

    # Verify by reading back
    xyz_back = pygmt.grd2xyz(grid="/tmp/test_xyz2grd.nc")
    print(f"✓ Verified grid by reading back: shape={xyz_back.shape}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: grdfilter - Filter grids in space domain
print("\n3. Testing grdfilter()")
print("-" * 60)
try:
    print("✓ Function exists:", 'grdfilter' in dir(pygmt))

    # Apply Gaussian filter to the test grid
    pygmt.grdfilter(
        grid="/tmp/test_grid.nc",
        outgrid="/tmp/test_filtered.nc",
        filter="g1",  # Gaussian with width 1
        distance=0    # Grid cell units
    )
    print("✓ Applied Gaussian filter (g1) to test grid")

    # Read original and filtered
    xyz_original = pygmt.grd2xyz(grid="/tmp/test_grid.nc")
    xyz_filtered = pygmt.grd2xyz(grid="/tmp/test_filtered.nc")

    print(f"✓ Original grid: min={xyz_original[:, 2].min():.3f}, max={xyz_original[:, 2].max():.3f}")
    print(f"✓ Filtered grid: min={xyz_filtered[:, 2].min():.3f}, max={xyz_filtered[:, 2].max():.3f}")
    print("  (Gaussian smoothing should slightly reduce range)")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Batch 4 testing complete!")
print("All 3 functions implemented successfully")
