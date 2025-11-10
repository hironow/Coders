cmake_minimum_required(VERSION 3.16...3.27)
project(pygmt_nb LANGUAGES CXX)

# Set C++17 standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(Python 3.11 COMPONENTS Interpreter Development.Module REQUIRED)

# Use GMT from external submodule
set(GMT_SOURCE_DIR "${CMAKE_SOURCE_DIR}/../external/gmt")
set(GMT_INCLUDE_DIR "${GMT_SOURCE_DIR}/src")

# Check if GMT source exists
if(NOT EXISTS "${GMT_INCLUDE_DIR}/gmt.h")
    message(FATAL_ERROR "GMT source not found at ${GMT_INCLUDE_DIR}. Did you initialize submodules?")
endif()

message(STATUS "Using GMT source from: ${GMT_SOURCE_DIR}")
message(STATUS "GMT headers at: ${GMT_INCLUDE_DIR}")

# For now, we'll build without linking to libgmt
# This allows us to test the build system first
# We'll add proper GMT library building later
message(WARNING "Building without GMT library - module will not be functional yet")

# Fetch nanobind
include(FetchContent)
FetchContent_Declare(
    nanobind
    GIT_REPOSITORY https://github.com/wjakob/nanobind
    GIT_TAG v2.0.0
)
FetchContent_MakeAvailable(nanobind)

# Create a minimal test version first
# We'll create a simple module that doesn't actually call GMT functions yet
nanobind_add_module(
    _pygmt_nb_core
    STABLE_ABI
    NB_STATIC
    src/bindings.cpp
)

# Include GMT headers (but don't link yet)
target_include_directories(_pygmt_nb_core PRIVATE ${GMT_INCLUDE_DIR})

# Install the extension module
install(TARGETS _pygmt_nb_core LIBRARY DESTINATION pygmt_nb/clib)
