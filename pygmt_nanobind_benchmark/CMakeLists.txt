cmake_minimum_required(VERSION 3.16...3.27)
project(pygmt_nb LANGUAGES CXX)

# Set C++17 standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(Python 3.11 COMPONENTS Interpreter Development.Module REQUIRED)

# Find GMT library
find_library(GMT_LIBRARY NAMES gmt REQUIRED)
find_path(GMT_INCLUDE_DIR gmt.h
    PATHS
        ${CMAKE_SOURCE_DIR}/../external/gmt/src
        /usr/include/gmt
        /usr/local/include/gmt
    REQUIRED
)

message(STATUS "Found GMT library: ${GMT_LIBRARY}")
message(STATUS "Found GMT headers: ${GMT_INCLUDE_DIR}")

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
    _pygmt_nb_core
    STABLE_ABI
    NB_STATIC
    src/bindings.cpp
)

# Link against GMT library
target_link_libraries(_pygmt_nb_core PRIVATE ${GMT_LIBRARY})
target_include_directories(_pygmt_nb_core PRIVATE ${GMT_INCLUDE_DIR})

# Install the extension module
install(TARGETS _pygmt_nb_core LIBRARY DESTINATION pygmt_nb/clib)
