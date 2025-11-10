/**
 * PyGMT nanobind bindings - Minimal stub implementation for testing
 *
 * This is a stub version that allows us to test the build system
 * without requiring a fully built GMT library.
 */

#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/map.h>

#include <memory>
#include <stdexcept>
#include <string>
#include <map>

namespace nb = nanobind;
using namespace nb::literals;

/**
 * Session class - stub implementation for testing
 */
class Session {
private:
    bool active_;

public:
    /**
     * Constructor - creates a new GMT session (stub)
     */
    Session() : active_(true) {
        // Stub: Just mark as active for now
        // Real implementation will call GMT_Create_Session
    }

    /**
     * Destructor - destroys the GMT session (stub)
     */
    ~Session() {
        active_ = false;
    }

    // Delete copy constructor and assignment operator
    Session(const Session&) = delete;
    Session& operator=(const Session&) = delete;

    /**
     * Get session information (stub)
     */
    std::map<std::string, std::string> info() const {
        std::map<std::string, std::string> result;

        if (!active_) {
            throw std::runtime_error("Session is not active");
        }

        // Stub: Return fake version info
        result["gmt_version"] = "6.5.0 (stub)";
        result["gmt_version_major"] = "6";
        result["gmt_version_minor"] = "5";
        result["gmt_version_patch"] = "0";

        return result;
    }

    /**
     * Call a GMT module (stub)
     */
    void call_module(const std::string& module, const std::string& args) {
        if (!active_) {
            throw std::runtime_error("Session is not active");
        }

        // Stub: Just validate that module name is not empty
        if (module.empty()) {
            throw std::runtime_error("Module name cannot be empty");
        }

        // Stub: Simulate error for unknown modules
        if (module == "nonexistent_module") {
            throw std::runtime_error("GMT module execution failed: " + module);
        }

        // Stub: Otherwise pretend it succeeded
        // Real implementation will call GMT_Call_Module
    }

    /**
     * Get the raw session pointer (stub)
     */
    void* session_pointer() const {
        // Stub: Return a fake pointer for now
        return (void*)0xDEADBEEF;
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
    m.doc() = "PyGMT nanobind core module - High-performance GMT bindings (stub version)";

    // Session class (context manager support added in Python wrapper)
    nb::class_<Session>(m, "Session")
        .def(nb::init<>(), "Create a new GMT session")
        .def("info", &Session::info, "Get session information")
        .def("call_module", &Session::call_module,
             "module"_a, "args"_a = "",
             "Execute a GMT module")
        .def_prop_ro("session_pointer", &Session::session_pointer,
                     "Get raw GMT session pointer")
        .def_prop_ro("is_active", &Session::is_active,
                     "Check if session is active");
}
