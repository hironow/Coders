cmake_minimum_required(VERSION 3.16...3.27)
project(pygmt_nb LANGUAGES CXX)

# Set C++17 standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(Python 3.11 COMPONENTS Interpreter Development.Module REQUIRED)

# Use GMT headers from external submodule
set(GMT_SOURCE_DIR "${CMAKE_SOURCE_DIR}/../external/gmt")
set(GMT_INCLUDE_DIR "${GMT_SOURCE_DIR}/src")

# Check if GMT source exists
if(NOT EXISTS "${GMT_INCLUDE_DIR}/gmt.h")
    message(FATAL_ERROR "GMT source not found at ${GMT_INCLUDE_DIR}. Did you initialize submodules?")
endif()

message(STATUS "Using GMT headers from: ${GMT_INCLUDE_DIR}")

# NOTE: We compile against GMT headers but DO NOT link libgmt at build time
# The GMT library will be loaded at runtime via dlopen (similar to PyGMT's ctypes)
# Users must have GMT installed in their system to use this package
message(STATUS "Runtime GMT library required - will use dlopen to load libgmt.so")

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

# Add compile definitions
target_compile_definitions(_pygmt_nb_core PRIVATE
    GMT_RUNTIME_LOADING=1
)

# On Linux, we need libdl for dlopen/dlsym
if(UNIX AND NOT APPLE)
    target_link_libraries(_pygmt_nb_core PRIVATE ${CMAKE_DL_LIBS})
endif()

# Install the extension module
install(TARGETS _pygmt_nb_core LIBRARY DESTINATION pygmt_nb/clib)
