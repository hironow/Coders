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

#include <memory>
#include <stdexcept>
#include <string>
#include <map>
#include <sstream>

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
 * Python module definition
 *
 * Exports the Session class to Python with all its methods.
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
}
