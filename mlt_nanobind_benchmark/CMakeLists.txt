cmake_minimum_required(VERSION 3.16...3.27)
project(mlt_nb LANGUAGES CXX)

# Set C++17 standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(Python 3.10 COMPONENTS Interpreter Development.Module REQUIRED)

# Allow user to specify MLT paths via CMake variables or environment
set(MLT_INCLUDE_DIR "$ENV{MLT_INCLUDE_DIR}" CACHE PATH "MLT include directory")
set(MLT_LIBRARY_DIR "$ENV{MLT_LIBRARY_DIR}" CACHE PATH "MLT library directory")
set(MLTPP_INCLUDE_DIR "$ENV{MLTPP_INCLUDE_DIR}" CACHE PATH "MLT++ include directory")

# Fallback to external submodule if not specified
if(NOT MLT_INCLUDE_DIR OR NOT EXISTS "${MLT_INCLUDE_DIR}/framework/mlt.h")
    set(MLT_SOURCE_DIR "${CMAKE_SOURCE_DIR}/../external/mlt")
    set(MLT_INCLUDE_DIR "${MLT_SOURCE_DIR}/src")
    set(MLTPP_INCLUDE_DIR "${MLT_SOURCE_DIR}/src/mlt++")
    message(STATUS "Using MLT headers from external submodule: ${MLT_INCLUDE_DIR}")
endif()

# Check if MLT source exists
if(NOT EXISTS "${MLT_INCLUDE_DIR}/framework/mlt.h")
    message(FATAL_ERROR "MLT headers not found at ${MLT_INCLUDE_DIR}. Please install MLT or specify MLT_INCLUDE_DIR.")
endif()

message(STATUS "Using MLT headers from: ${MLT_INCLUDE_DIR}")
message(STATUS "Using MLT++ headers from: ${MLTPP_INCLUDE_DIR}")

# Try to find MLT library
# Search in user-specified path first, then common locations
find_library(MLT_LIBRARY
    NAMES mlt mlt-7 libmlt libmlt-7
    PATHS
        ${MLT_LIBRARY_DIR}
        # macOS Homebrew paths
        /opt/homebrew/lib
        /opt/homebrew/Cellar/mlt/*/lib
        /usr/local/lib
        /usr/local/Cellar/mlt/*/lib
        # Linux standard paths
        /usr/lib
        /usr/lib/x86_64-linux-gnu
        /usr/lib/aarch64-linux-gnu
        /lib
        /lib/x86_64-linux-gnu
        # Windows paths (conda, vcpkg)
        "$ENV{CONDA_PREFIX}/Library/lib"
        "C:/Program Files/MLT/lib"
        "C:/Program Files (x86)/MLT/lib"
    PATH_SUFFIXES
        lib
        lib64
)

# Try to find MLT++ library
find_library(MLTPP_LIBRARY
    NAMES mlt++ mlt++-7 libmlt++ libmlt++-7
    PATHS
        ${MLT_LIBRARY_DIR}
        # macOS Homebrew paths
        /opt/homebrew/lib
        /opt/homebrew/Cellar/mlt/*/lib
        /usr/local/lib
        /usr/local/Cellar/mlt/*/lib
        # Linux standard paths
        /usr/lib
        /usr/lib/x86_64-linux-gnu
        /usr/lib/aarch64-linux-gnu
        /lib
        /lib/x86_64-linux-gnu
        # Windows paths (conda, vcpkg)
        "$ENV{CONDA_PREFIX}/Library/lib"
        "C:/Program Files/MLT/lib"
        "C:/Program Files (x86)/MLT/lib"
    PATH_SUFFIXES
        lib
        lib64
)

if(NOT MLT_LIBRARY)
    message(FATAL_ERROR
        "MLT library not found. Please install MLT:\n"
        "  macOS (Homebrew): brew install mlt\n"
        "  Linux (apt): sudo apt-get install libmlt-dev\n"
        "  Windows (conda): conda install -c conda-forge mlt\n"
        "Or specify MLT_LIBRARY_DIR:\n"
        "  cmake -DMLT_LIBRARY_DIR=/path/to/mlt/lib ..\n"
        "  set MLT_LIBRARY_DIR=C:\\path\\to\\mlt\\lib  (Windows)")
endif()

if(NOT MLTPP_LIBRARY)
    message(FATAL_ERROR
        "MLT++ library not found. Please install MLT development packages.")
endif()

message(STATUS "Found MLT library: ${MLT_LIBRARY}")
message(STATUS "Found MLT++ library: ${MLTPP_LIBRARY}")

# Fetch nanobind
include(FetchContent)
FetchContent_Declare(
    nanobind
    GIT_REPOSITORY https://github.com/wjakob/nanobind
    GIT_TAG v2.0.0
)
FetchContent_MakeAvailable(nanobind)

# Create the Python extension module
nanobind_add_module(
    _mlt_nb_core
    STABLE_ABI
    NB_STATIC
    src/bindings.cpp
)

# Include MLT headers
target_include_directories(_mlt_nb_core PRIVATE
    ${MLT_INCLUDE_DIR}
    ${MLTPP_INCLUDE_DIR}
)

# Link against MLT libraries
target_link_libraries(_mlt_nb_core PRIVATE
    ${MLT_LIBRARY}
    ${MLTPP_LIBRARY}
)

message(STATUS "Linking against MLT and MLT++ libraries")

# Install the extension module
install(TARGETS _mlt_nb_core LIBRARY DESTINATION mlt_nb)
