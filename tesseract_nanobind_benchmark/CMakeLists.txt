cmake_minimum_required(VERSION 3.15)
project(tesseract_nanobind)

# Find Python
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)

# Find nanobind
execute_process(
  COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
  OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE nanobind_ROOT)
find_package(nanobind CONFIG REQUIRED)

# Allow specifying custom paths for Tesseract and Leptonica
set(TESSERACT_INCLUDE_DIR "" CACHE PATH "Path to Tesseract include directory")
set(TESSERACT_LIB_DIR "" CACHE PATH "Path to Tesseract lib directory")
set(LEPTONICA_INCLUDE_DIR "" CACHE PATH "Path to Leptonica include directory")
set(LEPTONICA_LIB_DIR "" CACHE PATH "Path to Leptonica lib directory")

# Find Tesseract
if(TESSERACT_INCLUDE_DIR AND TESSERACT_LIB_DIR)
  set(Tesseract_INCLUDE_DIRS ${TESSERACT_INCLUDE_DIR})
  find_library(Tesseract_LIBRARIES 
    NAMES tesseract libtesseract
    PATHS ${TESSERACT_LIB_DIR}
    NO_DEFAULT_PATH
    REQUIRED)
else()
  find_package(PkgConfig)
  if(PKG_CONFIG_FOUND)
    pkg_check_modules(Tesseract REQUIRED tesseract)
  else()
    # Fallback: try to find tesseract in standard locations
    find_path(Tesseract_INCLUDE_DIRS tesseract/baseapi.h)
    find_library(Tesseract_LIBRARIES NAMES tesseract libtesseract REQUIRED)
  endif()
endif()

# Find Leptonica
if(LEPTONICA_INCLUDE_DIR AND LEPTONICA_LIB_DIR)
  set(Leptonica_INCLUDE_DIRS ${LEPTONICA_INCLUDE_DIR})
  find_library(Leptonica_LIBRARIES 
    NAMES lept liblept
    PATHS ${LEPTONICA_LIB_DIR}
    NO_DEFAULT_PATH
    REQUIRED)
else()
  find_package(PkgConfig)
  if(PKG_CONFIG_FOUND)
    pkg_check_modules(Leptonica REQUIRED lept)
  else()
    # Fallback: try to find leptonica in standard locations
    find_path(Leptonica_INCLUDE_DIRS leptonica/allheaders.h)
    find_library(Leptonica_LIBRARIES NAMES lept liblept REQUIRED)
  endif()
endif()

# Create the extension module
nanobind_add_module(_tesseract_nanobind 
  NB_STATIC 
  src/tesseract_nanobind_ext.cpp
)

# Include directories
target_include_directories(_tesseract_nanobind PRIVATE 
  ${Tesseract_INCLUDE_DIRS}
  ${Leptonica_INCLUDE_DIRS}
)

# Link libraries
target_link_libraries(_tesseract_nanobind PRIVATE 
  ${Tesseract_LIBRARIES}
  ${Leptonica_LIBRARIES}
)

# Set C++ standard
target_compile_features(_tesseract_nanobind PRIVATE cxx_std_17)

# Install the extension module
install(TARGETS _tesseract_nanobind LIBRARY DESTINATION tesseract_nanobind)
