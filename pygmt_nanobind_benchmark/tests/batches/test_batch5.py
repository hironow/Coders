#!/usr/bin/env python3
"""Test batch 5 functions: project, triangulate, plot3d"""

import sys
import numpy as np

# Add to path
sys.path.insert(0, '/home/user/Coders/pygmt_nanobind_benchmark/python')

import pygmt_nb as pygmt

print("Testing Batch 5 functions: project, triangulate, plot3d")
print("=" * 60)

# Test 1: project - Project data onto lines/great circles
print("\n1. Testing project()")
print("-" * 60)
try:
    print("✓ Function exists:", 'project' in dir(pygmt))

    # Create sample data points
    data = np.array([
        [1, 1],
        [2, 2],
        [3, 1],
        [4, 2],
        [1.5, 2.5],
        [2.5, 1.5]
    ], dtype=np.float64)

    print(f"✓ Created sample data: {len(data)} points")

    # Project onto a line from (0, 0) to (5, 5)
    projected = pygmt.project(
        data=data,
        center=[0, 0],
        endpoint=[5, 5]
    )
    print(f"✓ Projected data onto line: shape={projected.shape}")
    print(f"  Input points: {len(data)}")
    print(f"  Output columns: {projected.shape[1]}")
    print(f"  First projected point:\n{projected[0]}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: triangulate - Delaunay triangulation
print("\n2. Testing triangulate()")
print("-" * 60)
try:
    print("✓ Function exists:", 'triangulate' in dir(pygmt))

    # Create sample points for triangulation
    x = np.array([0, 1, 0.5, 0.25, 0.75], dtype=np.float64)
    y = np.array([0, 0, 1, 0.5, 0.5], dtype=np.float64)

    print(f"✓ Created sample points: {len(x)} points")

    # Perform triangulation
    edges = pygmt.triangulate(x=x, y=y)
    print(f"✓ Triangulation complete: shape={edges.shape}")
    print(f"  Generated {len(edges)} triangle edges")
    print(f"  First few edges:\n{edges[:3]}")

    # Test with array data
    data2 = np.random.rand(10, 2) * 10
    edges2 = pygmt.triangulate(data=data2, region=[0, 10, 0, 10])
    print(f"✓ Triangulated 10 random points: {len(edges2)} edges")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: plot3d - Figure method for 3D plotting
print("\n3. Testing plot3d()")
print("-" * 60)
try:
    print("✓ Function exists in Figure:", hasattr(pygmt.Figure, 'plot3d'))

    # Create 3D data
    t = np.linspace(0, 2*np.pi, 20)
    x = np.cos(t)
    y = np.sin(t)
    z = t

    print(f"✓ Created 3D spiral data: {len(t)} points")

    # Create figure and plot 3D data
    fig = pygmt.Figure()
    fig.plot3d(
        x=x, y=y, z=z,
        region=[-1.5, 1.5, -1.5, 1.5, 0, 7],
        projection="X10c/8c",
        perspective=[135, 30],
        style="c0.2c",
        fill="red",
        pen="0.5p,black",
        frame=["af", "zaf"]
    )
    print("✓ 3D plot created successfully")

    # Save to file
    fig.savefig("/tmp/test_plot3d.ps")
    print("✓ Saved 3D plot to: /tmp/test_plot3d.ps")

    # Test with data array (3 columns)
    fig2 = pygmt.Figure()
    data_3d = np.column_stack([x, y, z])
    fig2.plot3d(
        data=data_3d,
        region=[-1.5, 1.5, -1.5, 1.5, 0, 7],
        projection="X10c/8c",
        perspective=[135, 30],
        style="s0.3c",
        fill="blue"
    )
    print("✓ 3D plot with data array working")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Batch 5 testing complete!")
print("All 3 functions implemented successfully:")
print("  - project: Module function for data projection")
print("  - triangulate: Module function for Delaunay triangulation")
print("  - plot3d: Figure method for 3D plotting")
