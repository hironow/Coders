#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/string.h>
#include <tesseract/baseapi.h>
#include <leptonica/allheaders.h>
#include <memory>

namespace nb = nanobind;
using namespace nb::literals;

class TesseractAPI {
public:
    TesseractAPI() : api_(std::make_unique<tesseract::TessBaseAPI>()) {}
    
    ~TesseractAPI() {
        if (api_) {
            api_->End();
        }
    }
    
    // Initialize Tesseract with datapath and language
    int init(const std::string& datapath, const std::string& language) {
        const char* datapath_ptr = datapath.empty() ? nullptr : datapath.c_str();
        return api_->Init(datapath_ptr, language.c_str());
    }
    
    // Set image from NumPy array
    void set_image(nb::ndarray<uint8_t, nb::ndim<3>, nb::c_contig, nb::device::cpu> image) {
        size_t height = image.shape(0);
        size_t width = image.shape(1);
        size_t channels = image.shape(2);
        
        if (channels != 3) {
            throw std::runtime_error("Image must have 3 channels (RGB)");
        }
        
        // Get pointer to data
        const uint8_t* data = image.data();
        
        // Calculate bytes per line
        size_t bytes_per_line = width * channels;
        
        // SetImage expects: imagedata, width, height, bytes_per_pixel, bytes_per_line
        api_->SetImage(data, static_cast<int>(width), static_cast<int>(height), 
                      static_cast<int>(channels), static_cast<int>(bytes_per_line));
    }
    
    // Get OCR result as UTF-8 text
    std::string get_utf8_text() {
        char* text = api_->GetUTF8Text();
        if (!text) {
            return "";
        }
        std::string result(text);
        delete[] text;
        return result;
    }
    
    // Recognize the image
    int recognize() {
        return api_->Recognize(nullptr);
    }
    
    // Get Tesseract version
    static std::string version() {
        return tesseract::TessBaseAPI::Version();
    }

private:
    std::unique_ptr<tesseract::TessBaseAPI> api_;
};

NB_MODULE(_tesseract_nanobind, m) {
    m.doc() = "Tesseract OCR nanobind extension";
    
    nb::class_<TesseractAPI>(m, "TesseractAPI")
        .def(nb::init<>())
        .def("init", &TesseractAPI::init, 
             "datapath"_a, "language"_a,
             "Initialize Tesseract with datapath and language")
        .def("set_image", &TesseractAPI::set_image, 
             "image"_a,
             "Set image from NumPy array (height, width, 3)")
        .def("get_utf8_text", &TesseractAPI::get_utf8_text,
             "Get OCR result as UTF-8 text")
        .def("recognize", &TesseractAPI::recognize,
             "Recognize the image")
        .def_static("version", &TesseractAPI::version,
                   "Get Tesseract version");
}
