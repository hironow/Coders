/**
 * PyGMT nanobind bindings - Real GMT API implementation
 *
 * This implementation uses actual GMT C API calls via nanobind.
 *
 * Cross-platform support:
 * - Linux: libgmt.so
 * - macOS: libgmt.dylib
 * - Windows: gmt.dll
 *
 * Runtime requirement: GMT library must be installed and accessible
 * Build requirement: GMT headers and library for linking
 */

#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/map.h>
#include <nanobind/stl/tuple.h>
#include <nanobind/stl/vector.h>
#include <nanobind/ndarray.h>

#include <memory>
#include <stdexcept>
#include <string>
#include <map>
#include <sstream>
#include <tuple>
#include <cstring>
#include <vector>

// Include GMT headers for API declarations
extern "C" {
    #include "gmt.h"
    #include "gmt_resources.h"
}

namespace nb = nanobind;
using namespace nb::literals;

/**
 * Session class - wraps GMT C API session management
 *
 * This provides RAII wrapper around GMT_Create_Session/GMT_Destroy_Session
 */
class Session {
private:
    void* api_;      // GMT API pointer
    bool active_;
    std::string last_error_;

    /**
     * Helper to set last error message
     */
    void set_error(const std::string& msg) {
        last_error_ = msg;
    }

public:
    /**
     * Constructor - creates a new GMT session
     *
     * Calls GMT_Create_Session with appropriate parameters:
     * - tag: "pygmt_nb"
     * - pad: GMT_PAD_DEFAULT (2)
     * - mode: GMT_SESSION_EXTERNAL
     * - print_func: nullptr (use default)
     */
    Session() : api_(nullptr), active_(false), last_error_("") {
        // Create GMT session
        // Note: This will fail at runtime if libgmt is not installed
        // The build succeeds because we have the header files
        api_ = GMT_Create_Session("pygmt_nb", GMT_PAD_DEFAULT,
                                   GMT_SESSION_EXTERNAL, nullptr);

        if (api_ == nullptr) {
            throw std::runtime_error(
                "Failed to create GMT session. "
                "Is GMT installed on your system? "
                "Install GMT 6.5.0 or later to use this package."
            );
        }

        active_ = true;
    }

    /**
     * Destructor - destroys the GMT session
     *
     * Calls GMT_Destroy_Session to free resources
     */
    ~Session() {
        if (active_ && api_ != nullptr) {
            GMT_Destroy_Session(api_);
            api_ = nullptr;
            active_ = false;
        }
    }

    // Delete copy constructor and assignment operator
    Session(const Session&) = delete;
    Session& operator=(const Session&) = delete;

    /**
     * Get session information
     *
     * Returns a dictionary with GMT version information using
     * GMT_Get_Version API call.
     */
    std::map<std::string, std::string> info() const {
        std::map<std::string, std::string> result;

        if (!active_ || api_ == nullptr) {
            throw std::runtime_error("Session is not active");
        }

        // Get GMT version using GMT_Get_Version
        unsigned int major = 0, minor = 0, patch = 0;
        float version_float = GMT_Get_Version(api_, &major, &minor, &patch);

        // Build version string
        std::ostringstream version_stream;
        version_stream << major << "." << minor << "." << patch;

        result["gmt_version"] = version_stream.str();
        result["gmt_version_major"] = std::to_string(major);
        result["gmt_version_minor"] = std::to_string(minor);
        result["gmt_version_patch"] = std::to_string(patch);

        return result;
    }

    /**
     * Call a GMT module
     *
     * Executes a GMT module using GMT_Call_Module API.
     *
     * Args:
     *     module: Module name (e.g., "gmtset", "basemap", "coast")
     *     args: Module arguments as a space-separated string
     *
     * Throws:
     *     runtime_error: If module execution fails
     */
    void call_module(const std::string& module, const std::string& args) {
        if (!active_ || api_ == nullptr) {
            throw std::runtime_error("Session is not active");
        }

        // Validate module name
        if (module.empty()) {
            throw std::runtime_error("Module name cannot be empty");
        }

        // Call the GMT module using GMT_Call_Module
        // Mode: GMT_MODULE_CMD for command-line style arguments
        int status = GMT_Call_Module(api_, module.c_str(), GMT_MODULE_CMD,
                                      const_cast<char*>(args.c_str()));

        if (status != GMT_NOERROR) {
            // Get error message from GMT
            char* gmt_error = GMT_Error_Message(api_);
            std::string error_msg = "GMT module execution failed: " + module;
            if (gmt_error && strlen(gmt_error) > 0) {
                error_msg += "\nGMT Error: " + std::string(gmt_error);
            }
            throw std::runtime_error(error_msg);
        }
    }

    /**
     * Get the raw GMT API pointer
     *
     * This is provided for advanced usage and debugging.
     * Most users should not need to access this directly.
     *
     * Returns:
     *     void*: Opaque pointer to GMT API structure
     */
    void* session_pointer() const {
        return api_;
    }

    /**
     * Check if session is active
     *
     * Returns:
     *     bool: True if session is active and ready to use
     */
    bool is_active() const {
        return active_ && api_ != nullptr;
    }

    /**
     * Get last error message
     *
     * Returns:
     *     std::string: Last error message, or empty string if no error
     */
    std::string get_last_error() const {
        return last_error_;
    }

    /**
     * Get GMT constant value by name
     *
     * Returns the integer value of a GMT constant (e.g., "GMT_IS_DATASET").
     * These constants are defined in GMT headers and used for API calls.
     *
     * Args:
     *     name: Constant name as string
     *
     * Returns:
     *     int: Constant value
     *
     * Throws:
     *     runtime_error: If constant is not recognized
     */
    int get_constant(const std::string& name) const {
        // Data family constants
        if (name == "GMT_IS_DATASET") return GMT_IS_DATASET;
        if (name == "GMT_IS_GRID") return GMT_IS_GRID;
        if (name == "GMT_IS_IMAGE") return GMT_IS_IMAGE;
        if (name == "GMT_IS_VECTOR") return GMT_IS_VECTOR;
        if (name == "GMT_IS_MATRIX") return GMT_IS_MATRIX;
        if (name == "GMT_IS_CUBE") return GMT_IS_CUBE;

        // Via modifiers
        if (name == "GMT_VIA_VECTOR") return GMT_VIA_VECTOR;
        if (name == "GMT_VIA_MATRIX") return GMT_VIA_MATRIX;

        // Geometry constants
        if (name == "GMT_IS_POINT") return GMT_IS_POINT;
        if (name == "GMT_IS_LINE") return GMT_IS_LINE;
        if (name == "GMT_IS_POLY") return GMT_IS_POLY;
        if (name == "GMT_IS_SURFACE") return GMT_IS_SURFACE;
        if (name == "GMT_IS_NONE") return GMT_IS_NONE;

        // Direction/method constants
        if (name == "GMT_IN") return GMT_IN;
        if (name == "GMT_OUT") return GMT_OUT;
        if (name == "GMT_IS_REFERENCE") return GMT_IS_REFERENCE;
        if (name == "GMT_IS_DUPLICATE") return GMT_IS_DUPLICATE;

        // Mode constants
        if (name == "GMT_CONTAINER_ONLY") return GMT_CONTAINER_ONLY;
        if (name == "GMT_CONTAINER_AND_DATA") return GMT_CONTAINER_AND_DATA;
        if (name == "GMT_DATA_ONLY") return GMT_DATA_ONLY;

        // Data type constants
        if (name == "GMT_DOUBLE") return GMT_DOUBLE;
        if (name == "GMT_FLOAT") return GMT_FLOAT;
        if (name == "GMT_INT") return GMT_INT;
        if (name == "GMT_LONG") return GMT_LONG;
        if (name == "GMT_ULONG") return GMT_ULONG;
        if (name == "GMT_CHAR") return GMT_CHAR;
        if (name == "GMT_TEXT") return GMT_TEXT;

        // Virtual file length
        if (name == "GMT_VF_LEN") return GMT_VF_LEN;

        throw std::runtime_error("Unknown GMT constant: " + name);
    }

    /**
     * Create a GMT data container
     *
     * Creates an empty GMT data container for storing vectors, matrices, or grids.
     * Wraps GMT_Create_Data.
     *
     * Args:
     *     family: Data family (e.g., GMT_IS_DATASET | GMT_VIA_VECTOR)
     *     geometry: Data geometry (e.g., GMT_IS_POINT)
     *     mode: Creation mode (e.g., GMT_CONTAINER_ONLY)
     *     dim: Dimensions array [n_columns, n_rows, data_type, unused]
     *
     * Returns:
     *     void*: Pointer to GMT data structure
     *
     * Throws:
     *     runtime_error: If data creation fails
     */
    void* create_data(unsigned int family, unsigned int geometry,
                     unsigned int mode, const std::vector<uint64_t>& dim) {
        if (!active_ || api_ == nullptr) {
            throw std::runtime_error("Session is not active");
        }

        // Convert dimension vector to array
        uint64_t dim_array[4] = {0, 0, 0, 0};
        for (size_t i = 0; i < std::min(dim.size(), size_t(4)); ++i) {
            dim_array[i] = dim[i];
        }

        void* data = GMT_Create_Data(
            api_,
            family,
            geometry,
            mode,
            dim_array,
            nullptr,  // ranges (NULL for vector/matrix)
            nullptr,  // inc (NULL for vector/matrix)
            0,        // registration (0 for default)
            0,        // pad (0 for default)
            nullptr   // existing data (NULL to allocate new)
        );

        if (data == nullptr) {
            throw std::runtime_error("Failed to create GMT data container");
        }

        return data;
    }

    /**
     * Attach a numpy array to a GMT dataset as a column
     *
     * Wraps GMT_Put_Vector to store vector data in a GMT container.
     *
     * Args:
     *     dataset: GMT dataset pointer (from create_data)
     *     column: Column index (0-based)
     *     type: GMT data type (e.g., GMT_DOUBLE)
     *     vector: Numpy array (must be contiguous)
     *
     * Throws:
     *     runtime_error: If operation fails
     */
    void put_vector(void* dataset, unsigned int column, unsigned int type,
                   nb::ndarray<double, nb::shape<-1>, nb::c_contig> vector) {
        if (!active_ || api_ == nullptr) {
            throw std::runtime_error("Session is not active");
        }

        // Get pointer to array data
        void* vector_ptr = const_cast<void*>(static_cast<const void*>(vector.data()));

        int status = GMT_Put_Vector(
            api_,
            static_cast<GMT_VECTOR*>(dataset),
            column,
            type,
            vector_ptr
        );

        if (status != GMT_NOERROR) {
            throw std::runtime_error(
                "Failed to put vector in column " + std::to_string(column)
            );
        }
    }

    /**
     * Open a GMT virtual file
     *
     * Creates a virtual file associated with a GMT data structure.
     * The virtual file can be passed as a filename to GMT modules.
     * Wraps GMT_Open_VirtualFile.
     *
     * Args:
     *     family: Data family (e.g., GMT_IS_DATASET)
     *     geometry: Data geometry (e.g., GMT_IS_POINT)
     *     direction: Direction (GMT_IN or GMT_OUT) with optional modifiers
     *     data: GMT data pointer (from create_data) or nullptr for output
     *
     * Returns:
     *     std::string: Virtual file name (e.g., "?GMTAPI@12345")
     *
     * Throws:
     *     runtime_error: If virtual file creation fails
     */
    std::string open_virtualfile(unsigned int family, unsigned int geometry,
                                 unsigned int direction, void* data) {
        if (!active_ || api_ == nullptr) {
            throw std::runtime_error("Session is not active");
        }

        // Buffer to receive virtual file name
        char vfname[GMT_VF_LEN];
        memset(vfname, 0, GMT_VF_LEN);

        int status = GMT_Open_VirtualFile(
            api_,
            family,
            geometry,
            direction,
            data,
            vfname
        );

        if (status != GMT_NOERROR) {
            throw std::runtime_error("Failed to open virtual file");
        }

        return std::string(vfname);
    }

    /**
     * Close a GMT virtual file
     *
     * Closes a virtual file previously opened with open_virtualfile.
     * Wraps GMT_Close_VirtualFile.
     *
     * Args:
     *     vfname: Virtual file name (from open_virtualfile)
     *
     * Throws:
     *     runtime_error: If closing fails
     */
    void close_virtualfile(const std::string& vfname) {
        if (!active_ || api_ == nullptr) {
            throw std::runtime_error("Session is not active");
        }

        int status = GMT_Close_VirtualFile(api_, vfname.c_str());

        if (status != GMT_NOERROR) {
            throw std::runtime_error(
                "Failed to close virtual file: " + vfname
            );
        }
    }
};

/**
 * Grid class - wraps GMT_GRID structure
 *
 * This provides a Python interface to GMT grid data with NumPy integration.
 */
class Grid {
private:
    void* api_;              // GMT API pointer (borrowed from Session)
    GMT_GRID* grid_;         // GMT grid structure
    bool owns_grid_;         // Whether this object owns the grid data

public:
    /**
     * Create Grid by reading from file
     *
     * Args:
     *     session: Active GMT Session
     *     filename: Path to grid file (GMT-compatible format, e.g., .nc, .grd)
     */
    Grid(Session& session, const std::string& filename)
        : api_(session.session_pointer()), grid_(nullptr), owns_grid_(true) {

        if (!session.is_active()) {
            throw std::runtime_error("Cannot create Grid: Session is not active");
        }

        // Read grid from file using GMT_Read_Data
        // GMT_IS_GRID: Data family
        // GMT_IS_FILE: Input method (from file)
        // GMT_IS_SURFACE: Geometry type
        // GMT_CONTAINER_AND_DATA: Read both container and data
        grid_ = static_cast<GMT_GRID*>(
            GMT_Read_Data(
                api_,
                GMT_IS_GRID,           // family
                GMT_IS_FILE,           // method
                GMT_IS_SURFACE,        // geometry
                GMT_CONTAINER_AND_DATA | GMT_GRID_IS_CARTESIAN,  // mode
                nullptr,               // wesn (NULL = use file's region)
                filename.c_str(),      // input file
                nullptr                // existing data (NULL = allocate new)
            )
        );

        if (grid_ == nullptr) {
            throw std::runtime_error(
                "Failed to read grid from file: " + filename + "\n"
                "Make sure the file exists and is a valid GMT grid format."
            );
        }
    }

    /**
     * Destructor - cleanup GMT grid
     */
    ~Grid() {
        if (owns_grid_ && grid_ != nullptr && api_ != nullptr) {
            // Destroy grid using GMT API
            GMT_Destroy_Data(api_, reinterpret_cast<void**>(&grid_));
            grid_ = nullptr;
        }
    }

    // Disable copy (would need deep copy of GMT_GRID)
    Grid(const Grid&) = delete;
    Grid& operator=(const Grid&) = delete;

    // Enable move
    Grid(Grid&& other) noexcept
        : api_(other.api_), grid_(other.grid_), owns_grid_(other.owns_grid_) {
        other.grid_ = nullptr;
        other.owns_grid_ = false;
    }

    /**
     * Get grid shape (n_rows, n_columns)
     *
     * Returns:
     *     tuple: (n_rows, n_columns)
     */
    std::tuple<size_t, size_t> shape() const {
        if (grid_ == nullptr || grid_->header == nullptr) {
            throw std::runtime_error("Grid not initialized");
        }
        return std::make_tuple(
            grid_->header->n_rows,
            grid_->header->n_columns
        );
    }

    /**
     * Get grid region (west, east, south, north)
     *
     * Returns:
     *     tuple: (west, east, south, north)
     */
    std::tuple<double, double, double, double> region() const {
        if (grid_ == nullptr || grid_->header == nullptr) {
            throw std::runtime_error("Grid not initialized");
        }
        return std::make_tuple(
            grid_->header->wesn[0],  // west
            grid_->header->wesn[1],  // east
            grid_->header->wesn[2],  // south
            grid_->header->wesn[3]   // north
        );
    }

    /**
     * Get grid registration type
     *
     * Returns:
     *     int: 0 for node registration, 1 for pixel registration
     */
    int registration() const {
        if (grid_ == nullptr || grid_->header == nullptr) {
            throw std::runtime_error("Grid not initialized");
        }
        return grid_->header->registration;
    }

    /**
     * Get grid data as NumPy array
     *
     * Returns a 2D NumPy array (n_rows, n_columns) with grid data.
     *
     * Returns:
     *     ndarray: 2D NumPy array of float32
     */
    nb::ndarray<nb::numpy, float> data() const {
        if (grid_ == nullptr || grid_->header == nullptr || grid_->data == nullptr) {
            throw std::runtime_error("Grid not initialized or no data");
        }

        size_t n_rows = grid_->header->n_rows;
        size_t n_cols = grid_->header->n_columns;
        size_t total_size = n_rows * n_cols;

        // Create shape array
        size_t shape[2] = {n_rows, n_cols};

        // Allocate new numpy array and copy data
        // This ensures memory safety and proper ownership
        float* data_copy = new float[total_size];
        std::memcpy(data_copy, grid_->data, total_size * sizeof(float));

        // Create capsule for memory management
        auto capsule = nb::capsule(data_copy, [](void* ptr) noexcept {
            delete[] static_cast<float*>(ptr);
        });

        // Create ndarray with ownership transfer
        return nb::ndarray<nb::numpy, float>(
            data_copy,      // data pointer
            2,              // ndim
            shape,          // shape
            capsule         // owner (capsule will delete data when array is destroyed)
        );
    }

    /**
     * Get raw GMT_GRID pointer (advanced usage)
     *
     * Returns:
     *     void*: Pointer to GMT_GRID structure
     */
    void* grid_pointer() const {
        return static_cast<void*>(grid_);
    }
};

/**
 * Python module definition
 *
 * Exports the Session and Grid classes to Python with all their methods.
 */
NB_MODULE(_pygmt_nb_core, m) {
    m.doc() = "PyGMT nanobind core module - High-performance GMT bindings\n\n"
              "This module provides Python bindings to GMT (Generic Mapping Tools)\n"
              "using nanobind for improved performance over ctypes.\n\n"
              "Requirements:\n"
              "  - GMT 6.5.0 or later must be installed on your system\n"
              "  - GMT library must be accessible (libgmt.so/dylib/dll)\n\n"
              "Example:\n"
              "  >>> from pygmt_nb import Session\n"
              "  >>> with Session() as lib:\n"
              "  ...     info = lib.info()\n"
              "  ...     print(info['gmt_version'])\n";

    // Session class
    nb::class_<Session>(m, "Session",
        "GMT session manager\n\n"
        "This class wraps a GMT API session and provides context manager support.\n"
        "Always use it in a 'with' statement to ensure proper cleanup.")
        .def(nb::init<>(),
             "Create a new GMT session.\n\n"
             "Raises:\n"
             "    RuntimeError: If GMT is not installed or session creation fails")
        .def("info", &Session::info,
             "Get GMT session information.\n\n"
             "Returns:\n"
             "    dict: Dictionary with keys:\n"
             "        - gmt_version: Full version string\n"
             "        - gmt_version_major: Major version number\n"
             "        - gmt_version_minor: Minor version number\n"
             "        - gmt_version_patch: Patch version number")
        .def("call_module", &Session::call_module,
             "module"_a, "args"_a = "",
             "Execute a GMT module.\n\n"
             "Args:\n"
             "    module (str): Module name (e.g., 'gmtset', 'basemap')\n"
             "    args (str): Module arguments as space-separated string\n\n"
             "Raises:\n"
             "    RuntimeError: If module execution fails")
        .def_prop_ro("session_pointer", &Session::session_pointer,
                     "Get raw GMT session pointer (advanced usage only).\n\n"
                     "Returns:\n"
                     "    int: Pointer address as integer")
        .def_prop_ro("is_active", &Session::is_active,
                     "Check if session is active.\n\n"
                     "Returns:\n"
                     "    bool: True if session is active")
        .def("get_last_error", &Session::get_last_error,
             "Get last error message.\n\n"
             "Returns:\n"
             "    str: Last error message, or empty string")
        .def("get_constant", &Session::get_constant,
             "name"_a,
             "Get GMT constant value by name.\n\n"
             "Args:\n"
             "    name (str): Constant name (e.g., 'GMT_IS_DATASET')\n\n"
             "Returns:\n"
             "    int: Constant value\n\n"
             "Raises:\n"
             "    RuntimeError: If constant name is not recognized")
        .def("create_data", &Session::create_data,
             "family"_a, "geometry"_a, "mode"_a, "dim"_a,
             "Create a GMT data container.\n\n"
             "Args:\n"
             "    family (int): Data family constant\n"
             "    geometry (int): Data geometry constant\n"
             "    mode (int): Creation mode constant\n"
             "    dim (list): Dimensions [n_columns, n_rows, data_type, unused]\n\n"
             "Returns:\n"
             "    int: Pointer to GMT data structure\n\n"
             "Raises:\n"
             "    RuntimeError: If data creation fails")
        .def("put_vector", &Session::put_vector,
             "dataset"_a, "column"_a, "type"_a, "vector"_a,
             "Attach numpy array to GMT dataset as column.\n\n"
             "Args:\n"
             "    dataset (int): GMT dataset pointer\n"
             "    column (int): Column index (0-based)\n"
             "    type (int): GMT data type constant\n"
             "    vector (ndarray): Contiguous numpy array\n\n"
             "Raises:\n"
             "    RuntimeError: If operation fails")
        .def("open_virtualfile", &Session::open_virtualfile,
             "family"_a, "geometry"_a, "direction"_a, "data"_a,
             "Open a GMT virtual file.\n\n"
             "Args:\n"
             "    family (int): Data family constant\n"
             "    geometry (int): Data geometry constant\n"
             "    direction (int): Direction constant (GMT_IN/GMT_OUT)\n"
             "    data (int): GMT data pointer or 0 for output\n\n"
             "Returns:\n"
             "    str: Virtual file name\n\n"
             "Raises:\n"
             "    RuntimeError: If virtual file creation fails")
        .def("close_virtualfile", &Session::close_virtualfile,
             "vfname"_a,
             "Close a GMT virtual file.\n\n"
             "Args:\n"
             "    vfname (str): Virtual file name\n\n"
             "Raises:\n"
             "    RuntimeError: If closing fails");

    // Grid class
    nb::class_<Grid>(m, "Grid",
        "GMT Grid data container\n\n"
        "This class wraps GMT grid data and provides NumPy array access.\n"
        "Grids are automatically cleaned up when the object is destroyed.")
        .def(nb::init<Session&, const std::string&>(),
             "session"_a, "filename"_a,
             "Create Grid by reading from file.\n\n"
             "Args:\n"
             "    session (Session): Active GMT session\n"
             "    filename (str): Path to grid file (GMT format, e.g., .nc, .grd)\n\n"
             "Raises:\n"
             "    RuntimeError: If file cannot be read or is invalid")
        .def_prop_ro("shape", &Grid::shape,
                     "Get grid shape.\n\n"
                     "Returns:\n"
                     "    tuple: (n_rows, n_columns)")
        .def_prop_ro("region", &Grid::region,
                     "Get grid region.\n\n"
                     "Returns:\n"
                     "    tuple: (west, east, south, north)")
        .def_prop_ro("registration", &Grid::registration,
                     "Get grid registration type.\n\n"
                     "Returns:\n"
                     "    int: 0 for node registration, 1 for pixel registration")
        .def("data", &Grid::data,
             "Get grid data as NumPy array.\n\n"
             "Returns:\n"
             "    ndarray: 2D NumPy array of float32 with shape (n_rows, n_columns)")
        .def_prop_ro("grid_pointer", &Grid::grid_pointer,
                     "Get raw GMT_GRID pointer (advanced usage only).\n\n"
                     "Returns:\n"
                     "    int: Pointer address as integer");
}
