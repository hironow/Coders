/**
 * PyGMT nanobind bindings - Real GMT API implementation
 *
 * This implementation uses actual GMT C API calls.
 *
 * Build modes:
 * - Header-only mode (default): Compiles against GMT headers but doesn't link libgmt
 * - Full mode: Links against libgmt for full functionality
 *
 * Runtime requirement: libgmt.so must be installed on the system
 */

#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/map.h>
#include <nanobind/stl/tuple.h>
#include <nanobind/ndarray.h>

#include <memory>
#include <stdexcept>
#include <string>
#include <map>
#include <sstream>
#include <tuple>
#include <cstring>

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
              "  - libgmt.so must be in your library path\n\n"
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
             "    str: Last error message, or empty string");

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
