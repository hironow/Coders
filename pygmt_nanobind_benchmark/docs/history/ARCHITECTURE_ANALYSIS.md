# PyGMT Codebase Architecture Analysis
## Comprehensive Technical Research

---

## Executive Summary

PyGMT is a comprehensive Python wrapper for GMT (Generic Mapping Tools) v6.5+ that uses **ctypes** as its binding technology. The library provides both low-level C API access through the `Session` class and high-level Pythonic APIs through the `Figure` class and standalone functions. The architecture is designed for drop-in compatibility with scientific Python ecosystem (NumPy, Pandas, xarray, GeoPandas).

---

## 1. BINDING TECHNOLOGY: CTYPES

### Current Approach
- **Technology**: Python's standard `ctypes` library
- **Location**: `/pygmt/clib/` directory
- **Core Module**: `session.py` (2,372 lines)
- **Loading Module**: `loading.py`

### Why ctypes?
- No compilation needed - pure Python
- Direct access to GMT C library functions
- Part of Python standard library
- Lightweight - no additional C extensions

### Library Loading Strategy (`loading.py`)
```python
Priority order for finding libgmt:
1. GMT_LIBRARY_PATH environment variable
2. `gmt --show-library` command output
3. System PATH (Windows only)
4. System default search paths

Supported platforms:
- Linux/FreeBSD: libgmt.so
- macOS: libgmt.dylib
- Windows: gmt.dll, gmt_w64.dll, gmt_w32.dll
```

### GMT Version Requirement
- Minimum: GMT 6.5.0
- Checked at import time via `GMT_Get_Version()`
- Raises `GMTVersionError` if incompatible

---

## 2. MAIN ARCHITECTURE LAYERS

### Layer 1: C Library Binding (`pygmt/clib/`)
**Purpose**: Direct wrapping of GMT C API functions

Key Files:
- `session.py` - Core Session class (context manager pattern)
- `loading.py` - Library discovery and loading
- `conversion.py` - Type conversions (numpy ↔ ctypes)
- `__init__.py` - Exports Session class

**Key Functions**:
```
Session Methods (partial list):
- __enter__/__exit__  - Context manager
- create()            - Start GMT session
- destroy()           - End GMT session
- call_module()       - Execute GMT modules
- create_data()       - Create GMT data containers
- put_vector()        - Attach 1-D arrays
- put_matrix()        - Attach 2-D arrays
- put_strings()       - Attach string arrays
- read_data()         - Read from files/virtualfiles
- write_data()        - Write to files/virtualfiles
- open_virtualfile()  - Virtual file management
- virtualfile_from_vectors()
- virtualfile_from_matrix()
- virtualfile_from_grid()
- get_enum()          - Get GMT constants
- get_default()       - Get GMT config parameters
- get_common()        - Query common GMT options
- extract_region()    - Extract region from session
```

### Layer 2: Data Type Wrappers (`pygmt/datatypes/`)
**Purpose**: ctypes Structure definitions for GMT data types

Implemented Structures:
```
_GMT_GRID       - Grid data with header
_GMT_DATASET    - Table/point data with metadata
_GMT_IMAGE      - Image data with header
_GMT_GRID_HEADER - Grid metadata structure
```

Example:
```python
class _GMT_GRID(ctp.Structure):
    _fields_ = [
        ("header", ctp.POINTER(_GMT_GRID_HEADER)),
        ("data", ctp.POINTER(gmt_grdfloat)),
        ("x", ctp.POINTER(ctp.c_double)),
        ("y", ctp.POINTER(ctp.c_double)),
        ("hidden", ctp.c_void_p),
    ]
    
    def to_xarray(self) -> xr.DataArray: ...
```

### Layer 3: High-Level Functions (`pygmt/src/`)
**Purpose**: Pythonic wrappers around GMT modules

Structure:
- One Python file per GMT module (~60 modules)
- Functions take Pythonic parameters
- Convert to GMT command-line arguments
- Call GMT via `Session.call_module()`

Example Module Functions:
```
basemap.py      → basemap()
coast.py        → coast()
plot.py         → plot()
grdsample.py    → grdsample()
... (60+ modules)
```

### Layer 4: Main API (`pygmt/`)
**Purpose**: User-facing high-level interface

Key Classes:
- `Figure` - Main plotting interface
- Methods on Figure correspond to GMT plotting modules

Example Usage:
```python
fig = pygmt.Figure()
fig.basemap(region=[0,10,0,10], projection="X10c/5c", frame=True)
fig.plot(data=xyz_data, style="c0.3c", fill="red")
fig.savefig("output.png")
```

---

## 3. DIRECTORY STRUCTURE & ORGANIZATION

```
pygmt/
├── clib/                      # C library binding layer
│   ├── session.py             # Core Session class (2,372 lines)
│   ├── loading.py             # Library loading logic
│   ├── conversion.py           # Type conversions
│   └── __init__.py            # Exports Session
│
├── datatypes/                 # GMT data structure wrappers
│   ├── grid.py                # _GMT_GRID ctypes structure
│   ├── dataset.py             # _GMT_DATASET ctypes structure
│   ├── image.py               # _GMT_IMAGE ctypes structure
│   ├── header.py              # _GMT_GRID_HEADER structure
│   └── __init__.py
│
├── src/                       # High-level GMT module wrappers
│   ├── basemap.py
│   ├── coast.py
│   ├── plot.py
│   ├── grdimage.py
│   ... (60+ module files)
│   ├── _common.py             # Shared logic (focal mechanisms, etc)
│   └── __init__.py            # Exports all module functions
│
├── helpers/                   # Utility functions
│   ├── decorators.py          # @use_alias, @fmt_docstring, @kwargs_to_strings
│   ├── validators.py          # Input validation
│   ├── utils.py               # Helper utilities
│   ├── testing.py             # Test helpers
│   ├── tempfile.py            # Temp file management
│   └── caching.py             # Data caching
│
├── params/                    # Parameter specifications
│   └── ... (pattern specs)
│
├── figure.py                  # Figure class (main API)
├── alias.py                   # Alias system (long-form → GMT short-form)
├── encodings.py               # Character encoding handling
├── enums.py                   # Enum definitions
├── exceptions.py              # Custom exceptions
├── io.py                      # I/O utilities
├── session_management.py      # Global session management
├── __init__.py                # Main package exports
├── _show_versions.py          # Version info
└── _typing.py                 # Type hints
```

---

## 4. HOW PYGMT WRAPS GMT FUNCTIONS

### Pattern for Each GMT Module Wrapper

**Step 1: Import Dependencies**
```python
from pygmt.alias import AliasSystem
from pygmt.clib import Session
from pygmt.helpers import build_arg_list, use_alias, kwargs_to_strings
```

**Step 2: Apply Decorators**
```python
@fmt_docstring
@use_alias(
    J="projection",      # Long-form parameter → GMT short option
    R="region",
    V="verbose",
    B="frame",
    ...
)
@kwargs_to_strings(...)  # Type conversions
def basemap(self, projection=None, region=None, **kwargs):
    ...
```

**Step 3: Build Arguments and Call GMT**
```python
def basemap(self, ...):
    self._activate_figure()  # Ensure figure is active
    
    aliasdict = AliasSystem().add_common(
        J=projection,
        R=region,
        V=verbose,
        ...
    )
    aliasdict.merge(kwargs)
    
    with Session() as lib:
        lib.call_module(
            module="basemap",
            args=build_arg_list(aliasdict)  # Convert dict to GMT args
        )
```

### Key Components

**1. AliasSystem** (`alias.py`)
- Maps user-friendly parameter names to GMT option letters
- Validates parameter values
- Handles type conversions with mapping dictionaries
- Example: `projection="M10c"` → `-JM10c`

**2. Decorators** (`helpers/decorators.py`)
- `@use_alias`: Declares parameter aliases
- `@kwargs_to_strings`: Converts Python types to GMT strings
- `@fmt_docstring`: Interpolates docstring templates

**3. build_arg_list()** (`helpers/`)
- Converts Python dict of options to list of GMT command-line args
- Example: `{J: "M10c", R: [0, 10, 0, 10]}` → `["-JM10c", "-R0/10/0/10"]`

---

## 5. SESSION CLASS: CORE OF THE BINDING

### Context Manager Pattern
```python
with Session() as lib:
    lib.call_module("basemap", ["-JM10c", "-R0/10/0/10"])
    # Session automatically created and destroyed in __enter__/__exit__
```

### Key Operations

**1. Session Creation/Destruction**
```python
def create(self, name: str) -> None:
    """Create GMT C API session via GMT_Create_Session()"""
    
def destroy(self) -> None:
    """Destroy GMT C API session via GMT_Destroy_Session()"""
```

**2. Module Execution**
```python
def call_module(self, module: str, args: str | list[str]) -> None:
    """
    Call GMT module via GMT_Call_Module()
    - module: "basemap", "coast", "plot", etc
    - args: list of command-line arguments
    """
```

**3. Data Container Management**
```python
def create_data(self, family, geometry, mode, dim, ranges, inc, 
                registration, pad) -> ctp.c_void_p:
    """Create GMT data container (GMT_Create_Data)"""
    
def put_vector(self, dataset, column, vector) -> None:
    """Attach 1-D array as column (GMT_Put_Vector)"""
    
def put_matrix(self, dataset, matrix, pad) -> None:
    """Attach 2-D array as matrix (GMT_Put_Matrix)"""
```

**4. Virtual File Management** (Key Innovation)
```python
@contextlib.contextmanager
def open_virtualfile(self, family, geometry, direction, data):
    """Open virtual file for passing data in/out of GMT modules"""
    
@contextlib.contextmanager
def virtualfile_from_vectors(self, vectors):
    """Convenience: create virtual file from 1-D array list"""
    
@contextlib.contextmanager
def virtualfile_from_grid(self, grid):
    """Convenience: create virtual file from xarray.DataArray"""
```

**5. GMT Constant/Parameter Queries**
```python
def get_enum(self, name: str) -> int:
    """Get value of GMT constant (GMT_Get_Enum)"""
    
def get_default(self, name: str) -> str:
    """Get GMT config parameter or API parameter (GMT_Get_Default)"""
    
def get_common(self, option: str) -> bool | int | float | np.ndarray:
    """Query common option values (GMT_Get_Common)"""
```

### ctypes Function Wrapping
```python
def get_libgmt_func(self, name: str, argtypes=None, restype=None):
    """
    Get a ctypes function wrapper for a GMT C function
    
    Example:
    c_call_module = self.get_libgmt_func(
        "GMT_Call_Module",
        argtypes=[ctp.c_void_p, ctp.c_char_p, ctp.c_int, ctp.c_void_p],
        restype=ctp.c_int
    )
    """
```

---

## 6. DATA CONVERSION LAYER

### Location: `pygmt/clib/conversion.py`

**Key Functions**:
```python
def dataarray_to_matrix(grid: xr.DataArray) -> tuple[np.ndarray, list, list]:
    """Convert xarray.DataArray → 2-D numpy array + metadata"""
    
def vectors_to_arrays(vectors: Sequence) -> list[np.ndarray]:
    """Convert mixed sequence types → C-contiguous numpy arrays"""
    
def sequence_to_ctypes_array(seq, ctp_type, size) -> ctp.Array:
    """Convert Python sequence → ctypes array"""
    
def strings_to_ctypes_array(strings: np.ndarray) -> ctp.POINTER(ctp.c_char_p):
    """Convert string array → ctypes char pointer array"""
```

**Type Mapping** (numpy ↔ GMT):
```python
DTYPES_NUMERIC = {
    np.int8: "GMT_CHAR",
    np.float32: "GMT_FLOAT",
    np.float64: "GMT_DOUBLE",
    ... (comprehensive mapping)
}

DTYPES_TEXT = {
    np.str_: "GMT_TEXT",
    np.datetime64: "GMT_DATETIME",
}
```

---

## 7. FIGURE CLASS: HIGH-LEVEL API

### Location: `pygmt/figure.py`

**Key Features**:
```python
class Figure:
    def __init__(self):
        """Create figure with unique name"""
        
    def _activate_figure(self):
        """Tell GMT to work on this figure"""
        with Session() as lib:
            lib.call_module("figure", [self._name, "-"])
    
    @property
    def region(self) -> np.ndarray:
        """Get figure's geographic region (WESN)"""
    
    def savefig(self, fname, **kwargs) -> None:
        """Save figure to file (PNG, PDF, etc)"""
        
    def show(self, method="notebook", **kwargs) -> None:
        """Display figure preview"""
```

**Methods from src/** (injected as methods):
```python
from pygmt.src import basemap, coast, plot, plot3d, ...

class Figure:
    basemap = basemap
    coast = coast
    plot = plot
    ... (60+ plotting methods)
```

**Display Support**:
- Jupyter notebooks: `_repr_png_()`, `_repr_html_()` for rich display
- External viewer support
- Configurable via `pygmt.set_display()`

---

## 8. KEY ARCHITECTURAL PATTERNS

### Pattern 1: Context Manager for Session Management
```python
# Ensures proper cleanup even if errors occur
with Session() as lib:
    lib.call_module(...)
# Session automatically destroyed here
```

### Pattern 2: Virtual Files for Data Passing
```python
# Instead of writing to disk, use virtual files
with lib.virtualfile_from_vectors([x, y, z]) as vfile:
    lib.call_module("plot", [vfile, "-Sc0.3c"])
```

### Pattern 3: Decorator-Based Argument Processing
```python
@use_alias(J="projection", R="region")  # Define aliases
@kwargs_to_strings(...)                  # Type conversions
def plot(self, projection=None, region=None, **kwargs):
    # Automatic alias expansion and validation
```

### Pattern 4: Lazy Figure Activation
```python
def basemap(self, ...):
    self._activate_figure()  # Only create when needed
    with Session() as lib:
        lib.call_module(...)
```

### Pattern 5: Data Type Transparency
```python
# Accept multiple input types
fig.plot(data=file.txt)           # File path
fig.plot(data=dataframe)          # pandas.DataFrame
fig.plot(data=np.array(...))      # NumPy array
fig.plot(x=x_values, y=y_values)  # x/y arrays
```

---

## 9. BUILD SYSTEM & DEPENDENCIES

### pyproject.toml Configuration
```toml
[build-system]
requires = ["setuptools>=77", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
requires-python = ">=3.11"
dependencies = [
    "numpy>=2.0",
    "pandas>=2.2",
    "xarray>=2024.5",
    "packaging>=24.2",
]

[project.optional-dependencies]
all = ["contextily>=1.5", "geopandas>=1.0", "IPython", "pyarrow>=16", "rioxarray"]
```

### Version Management
- Uses `setuptools_scm` for semantic versioning
- Minimum Python: 3.11
- Minimum GMT: 6.5.0
- Follows SPEC 0 for minimum dependency versions

---

## 10. TEST INFRASTRUCTURE

### Test Organization
```
pygmt/tests/
├── test_clib*.py          # C library binding tests
├── test_figure.py         # Figure class tests
├── test_basemap.py        # Module-specific tests
├── test_plot.py
├── test_grd*.py
└── ... (100+ test files)
```

### Test Configuration (`pyproject.toml`)
```python
[tool.pytest.ini_options]
addopts = "--verbose --color=yes --durations=0 --doctest-modules --mpl"
markers = ["benchmark: mark a test with custom benchmark settings"]
```

### Testing Features
- `pytest` framework
- `pytest-mpl` for image comparison
- Doctest integration
- Benchmarking support

---

## 11. EXCEPTION HANDLING

### Custom Exceptions (`exceptions.py`)
```python
GMTCLibError              # C library errors
GMTCLibNotFoundError      # Library not found
GMTCLibNoSessionError     # Session not open
GMTVersionError           # GMT version incompatible
GMTValueError             # Invalid parameter value
GMTTypeError              # Type mismatch
GMTInvalidInput           # Invalid input
```

### Error Message Generation
```python
# Session captures GMT error output
self._error_log = []  # Accumulate error messages
@CFUNCTYPE callback   # Callback for GMT print output
# Format detailed error messages with GMT context
```

---

## 12. MAIN API ENTRY POINTS

### Package-Level Exports (`__init__.py`)
```python
from pygmt.figure import Figure, set_display
from pygmt.io import load_dataarray
from pygmt.src import basemap, coast, plot, ... (60+ functions)
from pygmt.datasets import load_earth_relief, ... (data loading)

# Global session management
_begin()  # Start GMT session on import
atexit.register(_end)  # Clean up on exit
```

### Module-Level Structure
```
pygmt.Figure              # Main class
pygmt.Figure.basemap      # Method (plots on current figure)
pygmt.basemap             # Function (same as Figure.basemap)
pygmt.config              # Configuration
pygmt.load_dataarray      # I/O
pygmt.datasets.*          # Data loading
pygmt.clib.Session        # Low-level API access
```

---

## 13. KEY DESIGN DECISIONS FOR DROP-IN REPLACEMENT

### Must Preserve
1. **Figure class interface** - same methods, same signatures
2. **Standalone function signatures** - e.g., `basemap(projection=...)` 
3. **Parameter names** - all long-form parameter names (projection, region, etc)
4. **Return types** - xarray.DataArray for grids, GeoDataFrame for tables
5. **Exception types** - GMTValueError, GMTTypeError, etc
6. **Virtual file system** - for memory-based data passing
7. **Session context manager** - `with Session() as lib:`
8. **Data type wrappers** - _GMT_GRID, _GMT_DATASET, _GMT_IMAGE
9. **Configuration system** - pygmt.config()
10. **Module call interface** - `lib.call_module(module, args)`

### Can Improve/Change
1. **Internal binding implementation** - replace ctypes with nanobind
2. **Error message generation** - can be cleaner with better logging
3. **Performance** - nanobind likely faster than ctypes
4. **Type hints** - can be more comprehensive
5. **Memory management** - nanobind gives more control
6. **Thread safety** - nanobind handles this better

---

## 14. PERFORMANCE CONSIDERATIONS

### Current ctypes Overhead
- Type conversion overhead at every call
- String encoding/decoding for GMT constants
- Array copying for non-contiguous data
- Virtual file wrapper overhead

### Nanobind Advantages
- Direct C++ binding (less Python overhead)
- Native numpy integration
- Better error handling and stack traces
- Type safety at compile time
- Direct memory access without conversion

---

## 15. DEPENDENCY GRAPH

```
User Code
    ↓
pygmt.Figure
    ↓
pygmt.src.* (module functions)
    ↓
pygmt.alias.AliasSystem (parameter mapping)
    ↓
pygmt.clib.Session (C API wrapper)
    ↓
pygmt.clib.conversion (type conversion)
    ↓
ctypes ← → libgmt.so/dylib/dll (GMT C library)
```

---

## RECOMMENDATIONS FOR NANOBIND REPLACEMENT

### 1. **Preserve Compatibility**
- Keep exact same Python API
- Maintain exception types and messages
- Support same parameter names and types
- Keep Figure class and session context manager pattern

### 2. **Improve Performance**
- Use nanobind's native numpy integration
- Avoid unnecessary data copying
- Better type safety
- Faster function calls

### 3. **Better Error Handling**
- More informative error messages
- Better stack traces
- Type validation at binding level

### 4. **Incremental Migration**
- Can write nanobind bindings module-by-module
- Keep ctypes as fallback during transition
- Use feature detection to switch implementations
- Maintain same external API throughout

### 5. **Key Nanobind Implementation Points**
- Core Session class: full replacement
- Data type structures: simpler with nanobind
- Conversion layer: mostly eliminated (direct numpy arrays)
- Module wrappers: no changes needed (call same C functions)

---

## SUMMARY OF KEY FILES FOR REFERENCE

| File | Lines | Purpose |
|------|-------|---------|
| `clib/session.py` | 2,372 | Core C API wrapper |
| `clib/conversion.py` | ~400 | Type conversions |
| `figure.py` | ~490 | Figure class |
| `alias.py` | ~500 | Alias system |
| `datatypes/grid.py` | ~400 | GMT grid structure |
| `src/basemap.py` | ~110 | Example module wrapper |
| `src/plot.py` | ~400+ | Complex module example |

