/**
 * PyGMT nanobind bindings
 *
 * This file provides Python bindings for the GMT C API using nanobind.
 */

#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>
#include <nanobind/stl/map.h>

extern "C" {
    #include "gmt.h"
    #include "gmt_resources.h"
}

#include <memory>
#include <stdexcept>
#include <string>
#include <map>

namespace nb = nanobind;
using namespace nb::literals;

/**
 * Session class - wraps GMT C API session management
 */
class Session {
private:
    void* api_;  // GMT API pointer
    bool active_;

public:
    /**
     * Constructor - creates a new GMT session
     */
    Session() : api_(nullptr), active_(false) {
        // Create GMT session with default parameters
        // tag: "pygmt_nb"
        // pad: GMT_PAD_DEFAULT (2)
        // mode: GMT_SESSION_EXTERNAL
        // print_func: nullptr (use default)
        api_ = GMT_Create_Session("pygmt_nb", GMT_PAD_DEFAULT,
                                   GMT_SESSION_EXTERNAL, nullptr);

        if (api_ == nullptr) {
            throw std::runtime_error("Failed to create GMT session");
        }

        active_ = true;
    }

    /**
     * Destructor - destroys the GMT session
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
     * Context manager support: __enter__
     */
    Session& enter() {
        return *this;
    }

    /**
     * Context manager support: __exit__
     */
    void exit(nb::object exc_type, nb::object exc_value, nb::object traceback) {
        // Cleanup is handled by destructor
        (void)exc_type;
        (void)exc_value;
        (void)traceback;
    }

    /**
     * Get session information
     */
    std::map<std::string, std::string> info() const {
        std::map<std::string, std::string> result;

        if (!active_ || api_ == nullptr) {
            throw std::runtime_error("Session is not active");
        }

        // Get GMT version
        char version[GMT_LEN256] = "";
        int major = 0, minor = 0, patch = 0;
        GMT_Get_Version(api_, &major, &minor, &patch, version);

        result["gmt_version"] = version;
        result["gmt_version_major"] = std::to_string(major);
        result["gmt_version_minor"] = std::to_string(minor);
        result["gmt_version_patch"] = std::to_string(patch);

        return result;
    }

    /**
     * Call a GMT module
     */
    void call_module(const std::string& module, const std::string& args) {
        if (!active_ || api_ == nullptr) {
            throw std::runtime_error("Session is not active");
        }

        // Create argument string in GMT format
        std::string full_args = module;
        if (!args.empty()) {
            full_args += " " + args;
        }

        // Call the GMT module
        int status = GMT_Call_Module(api_, module.c_str(), GMT_MODULE_CMD,
                                      const_cast<char*>(args.c_str()));

        if (status != GMT_NOERROR) {
            throw std::runtime_error("GMT module execution failed: " + module);
        }
    }

    /**
     * Get the raw session pointer (for advanced usage)
     */
    void* session_pointer() const {
        return api_;
    }

    /**
     * Check if session is active
     */
    bool is_active() const {
        return active_;
    }
};

/**
 * Python module definition
 */
NB_MODULE(_pygmt_nb_core, m) {
    m.doc() = "PyGMT nanobind core module - High-performance GMT bindings";

    // Session class
    nb::class_<Session>(m, "Session")
        .def(nb::init<>(), "Create a new GMT session")
        .def("__enter__", &Session::enter, "Context manager entry")
        .def("__exit__", &Session::exit, "Context manager exit")
        .def("info", &Session::info, "Get session information")
        .def("call_module", &Session::call_module,
             "module"_a, "args"_a = "",
             "Execute a GMT module")
        .def_prop_ro("session_pointer", &Session::session_pointer,
                     "Get raw GMT session pointer")
        .def_prop_ro("is_active", &Session::is_active,
                     "Check if session is active");
}
