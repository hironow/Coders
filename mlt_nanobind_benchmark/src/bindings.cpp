#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/string.h>
#include <mlt++/Mlt.h>
#include <framework/mlt_types.h>
#include <memory>
#include <cstring>

namespace nb = nanobind;
using namespace nb::literals;

// Helper function to convert mlt_image_format to bytes per pixel
static int bytes_per_pixel(mlt_image_format format) {
    switch (format) {
        case mlt_image_rgb:
            return 3;
        case mlt_image_rgba:
        case mlt_image_opengl_texture:
            return 4;
        case mlt_image_yuv422:
            return 2;
        default:
            return 4;  // Default to RGBA
    }
}

// Forward declarations
class RepositoryWrapper;

// Wrapper class for Factory
class FactoryWrapper {
public:
    FactoryWrapper() = default;

    RepositoryWrapper init(const std::string& directory = "");

    void close() {
        Mlt::Factory::close();
    }
};

// Wrapper class for Profile
class ProfileWrapper {
private:
    std::shared_ptr<Mlt::Profile> profile_;

public:
    ProfileWrapper() : profile_(std::make_shared<Mlt::Profile>()) {}

    ProfileWrapper(const std::string& name)
        : profile_(std::make_shared<Mlt::Profile>(name.c_str())) {}

    int width() const { return profile_->width(); }
    int height() const { return profile_->height(); }
    double fps() const { return profile_->fps(); }
    int frame_rate_num() const { return profile_->frame_rate_num(); }
    int frame_rate_den() const { return profile_->frame_rate_den(); }

    void from_producer(Mlt::Producer& producer) {
        profile_->from_producer(producer);
    }

    Mlt::Profile* get() { return profile_.get(); }
};

// Wrapper class for Frame with NumPy integration
class FrameWrapper {
private:
    std::shared_ptr<Mlt::Frame> frame_;

public:
    FrameWrapper(Mlt::Frame* frame) : frame_(frame) {}

    // Get image as NumPy array (zero-copy)
    nb::ndarray<nb::numpy, uint8_t, nb::ndim<3>> get_image() {
        mlt_image_format format = mlt_image_rgba;
        int width = 0;
        int height = 0;

        // Get image data from MLT - width and height are set by reference
        uint8_t* image_data = frame_->get_image(format, width, height);

        if (!image_data) {
            throw std::runtime_error("Failed to get image data from frame");
        }

        // Determine channels based on format
        int channels = bytes_per_pixel(format);

        // Create NumPy array shape: (height, width, channels)
        size_t shape[3] = {
            static_cast<size_t>(height),
            static_cast<size_t>(width),
            static_cast<size_t>(channels)
        };

        // Create ndarray with zero-copy (using existing data pointer)
        // The data is owned by the MLT frame, so we keep frame_ alive
        return nb::ndarray<nb::numpy, uint8_t, nb::ndim<3>>(
            image_data,
            3,
            shape,
            nb::handle()  // No owner; data lifetime managed by frame_
        );
    }

    int get_int(const std::string& name) const {
        return frame_->get_int(name.c_str());
    }

    void set(const std::string& name, const std::string& value) {
        frame_->set(name.c_str(), value.c_str());
    }
};

// Wrapper class for Producer
class ProducerWrapper {
private:
    std::shared_ptr<Mlt::Producer> producer_;

public:
    ProducerWrapper(ProfileWrapper& profile, const std::string& service,
                   const std::string& resource = "")
        : producer_(std::make_shared<Mlt::Producer>(
            *profile.get(),
            service.c_str(),
            resource.empty() ? nullptr : resource.c_str())) {}

    bool is_valid() const { return producer_->is_valid(); }

    FrameWrapper get_frame(int index = 0) {
        Mlt::Frame* frame = producer_->get_frame(index);
        return FrameWrapper(frame);
    }

    int get_length() const { return producer_->get_length(); }
    int get_in() const { return producer_->get_in(); }
    int get_out() const { return producer_->get_out(); }

    void set_in_and_out(int in, int out) {
        producer_->set_in_and_out(in, out);
    }

    Mlt::Producer* get() { return producer_.get(); }

    // Properties interface
    void set(const std::string& name, const std::string& value) {
        producer_->set(name.c_str(), value.c_str());
    }

    std::string get(const std::string& name) const {
        const char* value = producer_->get(name.c_str());
        return value ? std::string(value) : "";
    }
};

// Wrapper class for Consumer
class ConsumerWrapper {
private:
    std::shared_ptr<Mlt::Consumer> consumer_;

public:
    ConsumerWrapper(ProfileWrapper& profile, const std::string& id,
                   const std::string& service = "")
        : consumer_(std::make_shared<Mlt::Consumer>(
            *profile.get(),
            id.c_str(),
            service.empty() ? nullptr : service.c_str())) {}

    bool is_valid() const { return consumer_->is_valid(); }

    int connect(ProducerWrapper& producer) {
        return consumer_->connect(*producer.get());
    }

    int start() { return consumer_->start(); }
    int stop() { return consumer_->stop(); }
    bool is_stopped() const { return consumer_->is_stopped(); }

    void set(const std::string& name, const std::string& value) {
        consumer_->set(name.c_str(), value.c_str());
    }

    std::string get(const std::string& name) const {
        const char* value = consumer_->get(name.c_str());
        return value ? std::string(value) : "";
    }
};

// Wrapper class for Filter
class FilterWrapper {
private:
    std::shared_ptr<Mlt::Filter> filter_;

public:
    FilterWrapper(ProfileWrapper& profile, const std::string& id,
                 const std::string& service = "")
        : filter_(std::make_shared<Mlt::Filter>(
            *profile.get(),
            id.c_str(),
            service.empty() ? nullptr : service.c_str())) {}

    bool is_valid() const { return filter_->is_valid(); }

    void set(const std::string& name, const std::string& value) {
        filter_->set(name.c_str(), value.c_str());
    }

    std::string get(const std::string& name) const {
        const char* value = filter_->get(name.c_str());
        return value ? std::string(value) : "";
    }
};

// Wrapper class for Transition
class TransitionWrapper {
private:
    std::shared_ptr<Mlt::Transition> transition_;

public:
    TransitionWrapper(ProfileWrapper& profile, const std::string& id,
                     const std::string& service = "")
        : transition_(std::make_shared<Mlt::Transition>(
            *profile.get(),
            id.c_str(),
            service.empty() ? nullptr : service.c_str())) {}

    bool is_valid() const { return transition_->is_valid(); }

    void set(const std::string& name, const std::string& value) {
        transition_->set(name.c_str(), value.c_str());
    }

    std::string get(const std::string& name) const {
        const char* value = transition_->get(name.c_str());
        return value ? std::string(value) : "";
    }
};

// Wrapper class for Playlist
class PlaylistWrapper {
private:
    std::shared_ptr<Mlt::Playlist> playlist_;

public:
    PlaylistWrapper(ProfileWrapper& profile)
        : playlist_(std::make_shared<Mlt::Playlist>(*profile.get())) {}

    int count() const { return playlist_->count(); }

    int append(ProducerWrapper& producer, int in = -1, int out = -1) {
        return playlist_->append(*producer.get(), in, out);
    }

    int insert(ProducerWrapper& producer, int in, int out, int position) {
        return playlist_->insert(*producer.get(), in, out, position);
    }

    int remove(int where) {
        return playlist_->remove(where);
    }

    void clear() {
        playlist_->clear();
    }
};

// Wrapper class for Multitrack
class MultitrackWrapper {
private:
    std::shared_ptr<Mlt::Multitrack> multitrack_;

public:
    MultitrackWrapper()
        : multitrack_(std::make_shared<Mlt::Multitrack>(mlt_multitrack_init())) {}

    int count() const { return multitrack_->count(); }

    int connect(ProducerWrapper& producer, int track) {
        return multitrack_->connect(*producer.get(), track);
    }
};

// Wrapper class for Tractor
class TractorWrapper {
private:
    std::shared_ptr<Mlt::Tractor> tractor_;

public:
    TractorWrapper(ProfileWrapper& profile)
        : tractor_(std::make_shared<Mlt::Tractor>(*profile.get())) {}

    bool is_valid() const { return tractor_->is_valid(); }

    int count() const { return tractor_->count(); }
};

// Wrapper class for Repository
class RepositoryWrapper {
private:
    Mlt::Repository* repository_;

public:
    RepositoryWrapper(Mlt::Repository* repo) : repository_(repo) {}
};

// Implementation of FactoryWrapper::init() (must be after RepositoryWrapper definition)
RepositoryWrapper FactoryWrapper::init(const std::string& directory) {
    const char* dir = directory.empty() ? nullptr : directory.c_str();
    return RepositoryWrapper(Mlt::Factory::init(dir));
}

// Wrapper class for Properties
class PropertiesWrapper {
private:
    std::shared_ptr<Mlt::Properties> properties_;

public:
    PropertiesWrapper() : properties_(std::make_shared<Mlt::Properties>()) {}

    void set(const std::string& name, const std::string& value) {
        properties_->set(name.c_str(), value.c_str());
    }

    std::string get(const std::string& name) const {
        const char* value = properties_->get(name.c_str());
        return value ? std::string(value) : "";
    }

    int get_int(const std::string& name) const {
        return properties_->get_int(name.c_str());
    }

    double get_double(const std::string& name) const {
        return properties_->get_double(name.c_str());
    }
};

// Wrapper for Service (base class)
class ServiceWrapper {
private:
    std::shared_ptr<Mlt::Service> service_;

public:
    ServiceWrapper(Mlt::Service* service) : service_(service) {}
};

// Python module definition
NB_MODULE(_mlt_nb_core, m) {
    m.doc() = "MLT nanobind - High-performance Python bindings for MLT Framework";

    // Factory
    nb::class_<FactoryWrapper>(m, "Factory")
        .def(nb::init<>())
        .def("init", &FactoryWrapper::init,
             "directory"_a = "",
             "Initialize MLT factory")
        .def("close", &FactoryWrapper::close,
             "Close MLT factory");

    // Profile
    nb::class_<ProfileWrapper>(m, "Profile")
        .def(nb::init<>())
        .def(nb::init<const std::string&>())
        .def("width", &ProfileWrapper::width)
        .def("height", &ProfileWrapper::height)
        .def("fps", &ProfileWrapper::fps)
        .def("frame_rate_num", &ProfileWrapper::frame_rate_num)
        .def("frame_rate_den", &ProfileWrapper::frame_rate_den);

    // Frame
    nb::class_<FrameWrapper>(m, "Frame")
        .def("get_image", &FrameWrapper::get_image,
             "Get frame image as NumPy array (zero-copy)")
        .def("get_int", &FrameWrapper::get_int)
        .def("set", &FrameWrapper::set);

    // Producer
    nb::class_<ProducerWrapper>(m, "Producer")
        .def(nb::init<ProfileWrapper&, const std::string&, const std::string&>(),
             "profile"_a, "service"_a, "resource"_a = "")
        .def("is_valid", &ProducerWrapper::is_valid)
        .def("get_frame", &ProducerWrapper::get_frame, "index"_a = 0)
        .def("get_length", &ProducerWrapper::get_length)
        .def("get_in", &ProducerWrapper::get_in)
        .def("get_out", &ProducerWrapper::get_out)
        .def("set_in_and_out", &ProducerWrapper::set_in_and_out)
        .def("set", &ProducerWrapper::set)
        .def("get", static_cast<std::string (ProducerWrapper::*)(const std::string&) const>(&ProducerWrapper::get));

    // Consumer
    nb::class_<ConsumerWrapper>(m, "Consumer")
        .def(nb::init<ProfileWrapper&, const std::string&, const std::string&>(),
             "profile"_a, "id"_a, "service"_a = "")
        .def("is_valid", &ConsumerWrapper::is_valid)
        .def("connect", &ConsumerWrapper::connect)
        .def("start", &ConsumerWrapper::start)
        .def("stop", &ConsumerWrapper::stop)
        .def("is_stopped", &ConsumerWrapper::is_stopped)
        .def("set", &ConsumerWrapper::set)
        .def("get", &ConsumerWrapper::get);

    // Filter
    nb::class_<FilterWrapper>(m, "Filter")
        .def(nb::init<ProfileWrapper&, const std::string&, const std::string&>(),
             "profile"_a, "id"_a, "service"_a = "")
        .def("is_valid", &FilterWrapper::is_valid)
        .def("set", &FilterWrapper::set)
        .def("get", &FilterWrapper::get);

    // Transition
    nb::class_<TransitionWrapper>(m, "Transition")
        .def(nb::init<ProfileWrapper&, const std::string&, const std::string&>(),
             "profile"_a, "id"_a, "service"_a = "")
        .def("is_valid", &TransitionWrapper::is_valid)
        .def("set", &TransitionWrapper::set)
        .def("get", &TransitionWrapper::get);

    // Playlist
    nb::class_<PlaylistWrapper>(m, "Playlist")
        .def(nb::init<ProfileWrapper&>())
        .def("count", &PlaylistWrapper::count)
        .def("append", &PlaylistWrapper::append,
             "producer"_a, "in"_a = -1, "out"_a = -1)
        .def("insert", &PlaylistWrapper::insert)
        .def("remove", &PlaylistWrapper::remove)
        .def("clear", &PlaylistWrapper::clear);

    // Multitrack
    nb::class_<MultitrackWrapper>(m, "Multitrack")
        .def(nb::init<>())
        .def("count", &MultitrackWrapper::count)
        .def("connect", &MultitrackWrapper::connect);

    // Tractor
    nb::class_<TractorWrapper>(m, "Tractor")
        .def(nb::init<ProfileWrapper&>())
        .def("is_valid", &TractorWrapper::is_valid)
        .def("count", &TractorWrapper::count);

    // Repository
    nb::class_<RepositoryWrapper>(m, "Repository");

    // Properties
    nb::class_<PropertiesWrapper>(m, "Properties")
        .def(nb::init<>())
        .def("set", &PropertiesWrapper::set)
        .def("get", &PropertiesWrapper::get)
        .def("get_int", &PropertiesWrapper::get_int)
        .def("get_double", &PropertiesWrapper::get_double);

    // Service
    nb::class_<ServiceWrapper>(m, "Service");
}
