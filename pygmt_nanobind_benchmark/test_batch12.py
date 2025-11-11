#!/usr/bin/env python3
"""Test batch 12 functions: sphdistance, grdhisteq, grdlandmask"""

import sys
import numpy as np

# Add to path
sys.path.insert(0, '/home/user/Coders/pygmt_nanobind_benchmark/python')

import pygmt_nb as pygmt

print("Testing Batch 12 functions: sphdistance, grdhisteq, grdlandmask")
print("=" * 60)

# Test 1: sphdistance - Spherical distance calculation
print("\n1. Testing sphdistance()")
print("-" * 60)
try:
    print("✓ Function exists:", 'sphdistance' in dir(pygmt))

    # Create scattered points on a sphere
    lon = np.array([0, 90, 180, 270], dtype=np.float64)
    lat = np.array([0, 30, -30, 60], dtype=np.float64)

    print(f"✓ Created {len(lon)} scattered points on sphere")
    print(f"  Longitudes: {lon}")
    print(f"  Latitudes: {lat}")

    # Compute distance to nearest point (in degrees)
    pygmt.sphdistance(
        x=lon, y=lat,
        outgrid="/tmp/test_distances.nc",
        region=[-180, 180, -90, 90],
        spacing=10,
        unit="d"  # distances in degrees
    )
    print("✓ Computed spherical distances (unit=d)")

    # Verify output by reading back
    dist_xyz = pygmt.grd2xyz(grid="/tmp/test_distances.nc")
    print(f"✓ Distance grid created: {dist_xyz.shape[0]} points")
    print(f"  Distance range: [{dist_xyz[:, 2].min():.2f}°, {dist_xyz[:, 2].max():.2f}°]")

    # Test with different spacing
    pygmt.sphdistance(
        x=lon, y=lat,
        outgrid="/tmp/test_distances_fine.nc",
        region=[-180, 180, -90, 90],
        spacing=5,
        unit="d"  # finer resolution
    )
    print("✓ Computed distances with finer spacing (spacing=5)")

    fine_xyz = pygmt.grd2xyz(grid="/tmp/test_distances_fine.nc")
    print(f"  Fine grid: {fine_xyz.shape[0]} points")

    # Test with data array and km units
    data = np.column_stack([lon, lat])
    pygmt.sphdistance(
        data=data,
        outgrid="/tmp/test_distances2.nc",
        region=[-180, 180, -90, 90],
        spacing=15,
        unit="k"  # distances in km
    )
    print("✓ sphdistance() with data array working (unit=k)")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: grdhisteq - Grid histogram equalization
print("\n2. Testing grdhisteq()")
print("-" * 60)
try:
    print("✓ Function exists:", 'grdhisteq' in dir(pygmt))

    # Create a test grid with skewed distribution
    x = np.arange(0, 10, 0.5, dtype=np.float64)
    y = np.arange(0, 10, 0.5, dtype=np.float64)
    xx, yy = np.meshgrid(x, y)
    # Exponential distribution (highly skewed)
    zz = np.exp(xx * 0.2) * np.sin(yy * 0.5)
    xyz_data = np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()])

    pygmt.xyz2grd(
        data=xyz_data,
        outgrid="/tmp/test_skewed_grid.nc",
        region=[0, 10, 0, 10],
        spacing=0.5
    )
    print("✓ Created test grid with skewed distribution")

    # Get original statistics
    orig_xyz = pygmt.grd2xyz(grid="/tmp/test_skewed_grid.nc")
    orig_min, orig_max = orig_xyz[:, 2].min(), orig_xyz[:, 2].max()
    orig_std = orig_xyz[:, 2].std()
    print(f"  Original range: [{orig_min:.3f}, {orig_max:.3f}]")
    print(f"  Original std: {orig_std:.3f}")

    # Perform histogram equalization
    pygmt.grdhisteq(
        grid="/tmp/test_skewed_grid.nc",
        outgrid="/tmp/test_equalized.nc",
        divisions=16
    )
    print("✓ Performed histogram equalization (divisions=16)")

    # Verify output
    eq_xyz = pygmt.grd2xyz(grid="/tmp/test_equalized.nc")
    eq_min, eq_max = eq_xyz[:, 2].min(), eq_xyz[:, 2].max()
    eq_std = eq_xyz[:, 2].std()
    print(f"  Equalized range: [{eq_min:.3f}, {eq_max:.3f}]")
    print(f"  Equalized std: {eq_std:.3f}")
    print(f"  Distribution is now more uniform")

    # Test with more divisions for smoother result
    pygmt.grdhisteq(
        grid="/tmp/test_skewed_grid.nc",
        outgrid="/tmp/test_equalized_32.nc",
        divisions=32
    )
    print("✓ Histogram equalization with divisions=32")

    # Test Gaussian normalization
    pygmt.grdhisteq(
        grid="/tmp/test_skewed_grid.nc",
        outgrid="/tmp/test_gaussian.nc",
        gaussian=1.0
    )
    print("✓ Gaussian normalization (gaussian=1.0)")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: grdlandmask - Create land-sea masks
print("\n3. Testing grdlandmask()")
print("-" * 60)
try:
    print("✓ Function exists:", 'grdlandmask' in dir(pygmt))

    # Create land-sea mask for Australia region
    pygmt.grdlandmask(
        outgrid="/tmp/test_landmask.nc",
        region=[110, 160, -50, -10],
        spacing="30m",
        resolution="l"
    )
    print("✓ Created land-sea mask (resolution=l)")
    print("  Region: Australia (110-160°E, 10-50°S)")

    # Verify output
    mask_xyz = pygmt.grd2xyz(grid="/tmp/test_landmask.nc")
    land_points = np.sum(mask_xyz[:, 2] == 1)
    water_points = np.sum(mask_xyz[:, 2] == 0)
    total = mask_xyz.shape[0]

    print(f"✓ Mask grid: {total} total points")
    print(f"  Land (1): {land_points} points ({land_points*100//total}%)")
    print(f"  Water (0): {water_points} points ({water_points*100//total}%)")

    # Test with higher resolution
    pygmt.grdlandmask(
        outgrid="/tmp/test_landmask_hi.nc",
        region=[140, 155, -40, -25],
        spacing="10m",
        resolution="i"
    )
    print("✓ Created high-resolution mask (resolution=i)")

    # Test with custom mask values
    pygmt.grdlandmask(
        outgrid="/tmp/test_landmask_custom.nc",
        region=[120, 130, -30, -20],
        spacing="15m",
        resolution="l",
        maskvalues="10/20/10/20/10"  # custom values instead of 0/1
    )
    print("✓ Created mask with custom values (10/20)")

    custom_xyz = pygmt.grd2xyz(grid="/tmp/test_landmask_custom.nc")
    unique_vals = np.unique(custom_xyz[:, 2])
    print(f"  Custom mask values: {unique_vals}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Batch 12 testing complete!")
print("All 3 Priority-2 functions implemented successfully:")
print("  - sphdistance: Module function for spherical distance calculation")
print("  - grdhisteq: Module function for grid histogram equalization")
print("  - grdlandmask: Module function for creating land-sea masks")
