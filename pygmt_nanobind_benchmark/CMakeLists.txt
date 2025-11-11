cmake_minimum_required(VERSION 3.16...3.27)
project(pygmt_nb LANGUAGES CXX)

# Set C++17 standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(Python 3.10 COMPONENTS Interpreter Development.Module REQUIRED)

# Allow user to specify GMT paths via CMake variables or environment
set(GMT_INCLUDE_DIR "$ENV{GMT_INCLUDE_DIR}" CACHE PATH "GMT include directory")
set(GMT_LIBRARY_DIR "$ENV{GMT_LIBRARY_DIR}" CACHE PATH "GMT library directory")

# Fallback to external submodule if not specified
if(NOT GMT_INCLUDE_DIR OR NOT EXISTS "${GMT_INCLUDE_DIR}/gmt.h")
    set(GMT_SOURCE_DIR "${CMAKE_SOURCE_DIR}/../external/gmt")
    set(GMT_INCLUDE_DIR "${GMT_SOURCE_DIR}/src")
    message(STATUS "Using GMT headers from external submodule: ${GMT_INCLUDE_DIR}")
endif()

# Check if GMT source exists
if(NOT EXISTS "${GMT_INCLUDE_DIR}/gmt.h")
    message(FATAL_ERROR "GMT headers not found at ${GMT_INCLUDE_DIR}. Please install GMT or specify GMT_INCLUDE_DIR.")
endif()

message(STATUS "Using GMT headers from: ${GMT_INCLUDE_DIR}")

# Try to find GMT library
# Search in user-specified path first, then common locations
# Support multiple library naming conventions (gmt, gmt6, libgmt)
find_library(GMT_LIBRARY
    NAMES gmt gmt6 libgmt
    PATHS
        ${GMT_LIBRARY_DIR}
        # macOS Homebrew paths
        /opt/homebrew/lib
        /opt/homebrew/Cellar/gmt/*/lib
        /usr/local/lib
        /usr/local/Cellar/gmt/*/lib
        # Linux standard paths
        /usr/lib
        /usr/lib/x86_64-linux-gnu
        /usr/lib/aarch64-linux-gnu
        /lib
        /lib/x86_64-linux-gnu
        # Windows paths (conda, vcpkg, OSGeo4W)
        "$ENV{CONDA_PREFIX}/Library/lib"
        "C:/Program Files/GMT/lib"
        "C:/Program Files (x86)/GMT/lib"
        "C:/OSGeo4W/lib"
        "C:/OSGeo4W64/lib"
    PATH_SUFFIXES
        lib
        lib64
)

if(NOT GMT_LIBRARY)
    message(FATAL_ERROR
        "GMT library not found. Please install GMT:\n"
        "  macOS (Homebrew): brew install gmt\n"
        "  Linux (apt): sudo apt-get install libgmt-dev\n"
        "  Windows (conda): conda install -c conda-forge gmt\n"
        "  Windows (vcpkg): vcpkg install gmt\n"
        "Or specify GMT_LIBRARY_DIR:\n"
        "  cmake -DGMT_LIBRARY_DIR=/path/to/gmt/lib ..\n"
        "  set GMT_LIBRARY_DIR=C:\\path\\to\\gmt\\lib  (Windows)")
endif()

message(STATUS "Found GMT library: ${GMT_LIBRARY}")

# Fetch nanobind
include(FetchContent)
FetchContent_Declare(
    nanobind
    GIT_REPOSITORY https://github.com/wjakob/nanobind
    GIT_TAG v2.0.0
)
FetchContent_MakeAvailable(nanobind)

# Create the Python extension module with real GMT implementation
nanobind_add_module(
    _pygmt_nb_core
    STABLE_ABI
    NB_STATIC
    src/bindings.cpp
)

# Include GMT headers for type definitions and function declarations
target_include_directories(_pygmt_nb_core PRIVATE ${GMT_INCLUDE_DIR})

# Link against GMT library
target_link_libraries(_pygmt_nb_core PRIVATE ${GMT_LIBRARY})
message(STATUS "Linking against GMT library")

# Install the extension module
install(TARGETS _pygmt_nb_core LIBRARY DESTINATION pygmt_nb/clib)
