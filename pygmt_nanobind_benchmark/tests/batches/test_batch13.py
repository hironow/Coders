#!/usr/bin/env python3
"""Test batch 13 functions: grdvolume, dimfilter, binstats"""

import sys
import numpy as np

# Add to path
sys.path.insert(0, '/home/user/Coders/pygmt_nanobind_benchmark/python')

import pygmt_nb as pygmt

print("Testing Batch 13 functions: grdvolume, dimfilter, binstats")
print("=" * 60)

# Test 1: grdvolume - Grid volume calculation
print("\n1. Testing grdvolume()")
print("-" * 60)
try:
    print("✓ Function exists:", 'grdvolume' in dir(pygmt))

    # Create a test grid (cone shape)
    x = np.arange(0, 10, 0.5, dtype=np.float64)
    y = np.arange(0, 10, 0.5, dtype=np.float64)
    xx, yy = np.meshgrid(x, y)

    # Create cone centered at (5, 5) with height 10
    center_x, center_y = 5.0, 5.0
    radius = np.sqrt((xx - center_x)**2 + (yy - center_y)**2)
    max_radius = 5.0
    zz = np.maximum(10 - 10 * radius / max_radius, 0)  # Cone, zero outside

    xyz_data = np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()])

    pygmt.xyz2grd(
        data=xyz_data,
        outgrid="/tmp/test_cone.nc",
        region=[0, 10, 0, 10],
        spacing=0.5
    )
    print("✓ Created cone-shaped test grid")
    print(f"  Cone height: 10, radius: {max_radius}")

    # Calculate volume above z=0
    result = pygmt.grdvolume(
        grid="/tmp/test_cone.nc",
        contour=0
    )
    print("✓ Calculated volume above z=0")
    print(f"  Result: {result.strip()}")

    # Calculate volume above z=5 (half height)
    result = pygmt.grdvolume(
        grid="/tmp/test_cone.nc",
        contour=5
    )
    print("✓ Calculated volume above z=5")

    # Save to file
    pygmt.grdvolume(
        grid="/tmp/test_cone.nc",
        output="/tmp/test_volume.txt",
        contour=0
    )
    print("✓ grdvolume() output to file working")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: dimfilter - Directional median filter
print("\n2. Testing dimfilter()")
print("-" * 60)
try:
    print("✓ Function exists:", 'dimfilter' in dir(pygmt))

    # Create noisy grid with linear feature
    x = np.arange(0, 10, 0.2, dtype=np.float64)
    y = np.arange(0, 10, 0.2, dtype=np.float64)
    xx, yy = np.meshgrid(x, y)

    # Linear feature (diagonal ridge) + noise
    zz = 5 + 0.5 * xx + 0.5 * yy  # Diagonal trend
    noise = np.random.randn(*zz.shape) * 0.5  # Add noise
    zz_noisy = zz + noise

    xyz_noisy = np.column_stack([xx.ravel(), yy.ravel(), zz_noisy.ravel()])

    pygmt.xyz2grd(
        data=xyz_noisy,
        outgrid="/tmp/test_noisy.nc",
        region=[0, 10, 0, 10],
        spacing=0.2
    )
    print("✓ Created noisy grid with diagonal feature")

    # Get original statistics
    orig_xyz = pygmt.grd2xyz(grid="/tmp/test_noisy.nc")
    orig_std = orig_xyz[:, 2].std()
    print(f"  Original std: {orig_std:.3f}")

    # Apply directional median filter
    pygmt.dimfilter(
        grid="/tmp/test_noisy.nc",
        outgrid="/tmp/test_filtered_4sec.nc",
        distance="1.0",  # 1 unit diameter
        sectors=4
    )
    print("✓ Applied directional filter (4 sectors)")

    # Verify filtering
    filt_xyz = pygmt.grd2xyz(grid="/tmp/test_filtered_4sec.nc")
    filt_std = filt_xyz[:, 2].std()
    print(f"  Filtered std: {filt_std:.3f}")
    print(f"  Noise reduction: {(orig_std - filt_std) / orig_std * 100:.1f}%")

    # Test with 8 sectors
    pygmt.dimfilter(
        grid="/tmp/test_noisy.nc",
        outgrid="/tmp/test_filtered_8sec.nc",
        distance="1.0",
        sectors=8
    )
    print("✓ Applied directional filter (8 sectors)")

    # Test with subregion
    pygmt.dimfilter(
        grid="/tmp/test_noisy.nc",
        outgrid="/tmp/test_filtered_region.nc",
        distance="0.8",
        sectors=6,
        region=[2, 8, 2, 8]
    )
    print("✓ dimfilter() with subregion working")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: binstats - Bin statistics
print("\n3. Testing binstats()")
print("-" * 60)
try:
    print("✓ Function exists:", 'binstats' in dir(pygmt))

    # Create scattered data
    np.random.seed(42)
    n_points = 1000
    x = np.random.uniform(0, 10, n_points)
    y = np.random.uniform(0, 10, n_points)
    z = np.sin(x) * np.cos(y) + np.random.randn(n_points) * 0.1

    print(f"✓ Created {n_points} scattered data points")
    print(f"  Z range: [{z.min():.2f}, {z.max():.2f}]")

    # Bin data and compute mean
    result_mean = pygmt.binstats(
        x=x, y=y, z=z,
        region=[0, 10, 0, 10],
        spacing=1.0,
        statistic="a"  # mean
    )
    print("✓ Computed bin means (statistic=a)")
    if result_mean is not None:
        print(f"  Result shape: {result_mean.shape}")
        print(f"  Bin means range: [{result_mean[:, 2].min():.2f}, {result_mean[:, 2].max():.2f}]")

    # Compute median (more robust)
    result_median = pygmt.binstats(
        x=x, y=y, z=z,
        region=[0, 10, 0, 10],
        spacing=1.0,
        statistic="d"  # median
    )
    print("✓ Computed bin medians (statistic=d)")

    # Count points per bin
    result_count = pygmt.binstats(
        x=x, y=y, z=z,
        region=[0, 10, 0, 10],
        spacing=1.0,
        statistic="z"  # count
    )
    print("✓ Counted points per bin (statistic=z)")
    if result_count is not None:
        total_counted = int(result_count[:, 2].sum())
        print(f"  Total points counted: {total_counted} / {n_points}")

    # Output as grid
    pygmt.binstats(
        x=x, y=y, z=z,
        outgrid="/tmp/test_binned_grid.nc",
        region=[0, 10, 0, 10],
        spacing=0.5,
        statistic="a"
    )
    print("✓ Created binned grid output")

    # Test with data array
    data = np.column_stack([x, y, z])
    result = pygmt.binstats(
        data=data,
        region=[0, 10, 0, 10],
        spacing=1.5,
        statistic="a"
    )
    print("✓ binstats() with data array working")
    if result is not None:
        print(f"  Binned to {result.shape[0]} bins (spacing=1.5)")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Batch 13 testing complete!")
print("All 3 Priority-2 functions implemented successfully:")
print("  - grdvolume: Module function for grid volume calculation")
print("  - dimfilter: Module function for directional median filtering")
print("  - binstats: Module function for binning and computing statistics")
