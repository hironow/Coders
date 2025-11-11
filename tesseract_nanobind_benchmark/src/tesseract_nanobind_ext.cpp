#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/list.h>
#include <tesseract/baseapi.h>
#include <tesseract/resultiterator.h>
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
    
    // Get mean confidence score
    int get_mean_confidence() {
        return api_->MeanTextConf();
    }
    
    // Get bounding boxes with text and confidence for each word
    nb::list get_bounding_boxes() {
        nb::list result;
        
        tesseract::ResultIterator* ri = api_->GetIterator();
        if (!ri) {
            return result;
        }
        
        tesseract::PageIteratorLevel level = tesseract::RIL_WORD;
        
        do {
            const char* word = ri->GetUTF8Text(level);
            if (!word) continue;
            
            float conf = ri->Confidence(level);
            int x1, y1, x2, y2;
            ri->BoundingBox(level, &x1, &y1, &x2, &y2);
            
            nb::dict box;
            box["text"] = std::string(word);
            box["left"] = x1;
            box["top"] = y1;
            box["width"] = x2 - x1;
            box["height"] = y2 - y1;
            box["confidence"] = conf;
            
            result.append(box);
            delete[] word;
        } while (ri->Next(level));
        
        delete ri;
        return result;
    }
    
    // Get Tesseract version
    static std::string version() {
        return tesseract::TessBaseAPI::Version();
    }

    // Phase 1: High-priority methods for tesserocr compatibility

    // Page Segmentation Mode
    void set_page_seg_mode(int mode) {
        api_->SetPageSegMode(static_cast<tesseract::PageSegMode>(mode));
    }

    int get_page_seg_mode() {
        return static_cast<int>(api_->GetPageSegMode());
    }

    // Variable setting and getting
    bool set_variable(const std::string& name, const std::string& value) {
        return api_->SetVariable(name.c_str(), value.c_str());
    }

    bool get_int_variable(const std::string& name, int* value) {
        return api_->GetIntVariable(name.c_str(), value);
    }

    bool get_bool_variable(const std::string& name, bool* value) {
        return api_->GetBoolVariable(name.c_str(), value);
    }

    bool get_double_variable(const std::string& name, double* value) {
        return api_->GetDoubleVariable(name.c_str(), value);
    }

    std::string get_string_variable(const std::string& name) {
        const char* value = api_->GetStringVariable(name.c_str());
        return value ? std::string(value) : "";
    }

    // Rectangle for ROI
    void set_rectangle(int left, int top, int width, int height) {
        api_->SetRectangle(left, top, width, height);
    }

    // Alternative output formats
    std::string get_hocr_text(int page_number) {
        char* text = api_->GetHOCRText(page_number);
        if (!text) {
            return "";
        }
        std::string result(text);
        delete[] text;
        return result;
    }

    std::string get_tsv_text(int page_number) {
        char* text = api_->GetTSVText(page_number);
        if (!text) {
            return "";
        }
        std::string result(text);
        delete[] text;
        return result;
    }

    std::string get_box_text(int page_number) {
        char* text = api_->GetBoxText(page_number);
        if (!text) {
            return "";
        }
        std::string result(text);
        delete[] text;
        return result;
    }

    std::string get_unlv_text() {
        char* text = api_->GetUNLVText();
        if (!text) {
            return "";
        }
        std::string result(text);
        delete[] text;
        return result;
    }

    // Additional useful methods
    void clear() {
        api_->Clear();
    }

    void clear_adaptive_classifier() {
        api_->ClearAdaptiveClassifier();
    }

    std::string get_datapath() {
        return api_->GetDatapath();
    }

    std::string get_init_languages_as_string() {
        return api_->GetInitLanguagesAsString();
    }

    // Phase 2: Medium-priority methods
    nb::tuple detect_orientation_script() {
        int orient_deg = 0;
        float orient_conf = 0.0f;
        const char* script_name = nullptr;
        float script_conf = 0.0f;

        bool success = api_->DetectOrientationScript(
            &orient_deg, &orient_conf, &script_name, &script_conf
        );

        if (!success || !script_name) {
            return nb::make_tuple(0, 0.0f, std::string(""), 0.0f);
        }

        return nb::make_tuple(orient_deg, orient_conf, std::string(script_name), script_conf);
    }

    nb::list get_component_images(int level, bool text_only) {
        nb::list boxes;

        Boxa* boxa = api_->GetComponentImages(
            static_cast<tesseract::PageIteratorLevel>(level),
            text_only,
            nullptr,  // pixa not needed for now
            nullptr   // blockids not needed
        );

        if (boxa) {
            int n = boxaGetCount(boxa);
            for (int i = 0; i < n; i++) {
                Box* box = boxaGetBox(boxa, i, L_CLONE);
                if (box) {
                    l_int32 x, y, w, h;
                    boxGetGeometry(box, &x, &y, &w, &h);
                    boxes.append(nb::make_tuple(x, y, w, h));
                    boxDestroy(&box);
                }
            }
            boxaDestroy(&boxa);
        }

        return boxes;
    }

    // Phase 3: Additional layout analysis methods
    nb::list get_words() {
        nb::list words;

        tesseract::ResultIterator* ri = api_->GetIterator();
        if (ri != nullptr) {
            do {
                const char* word = ri->GetUTF8Text(tesseract::RIL_WORD);
                if (word) {
                    float conf = ri->Confidence(tesseract::RIL_WORD);
                    int x1, y1, x2, y2;
                    ri->BoundingBox(tesseract::RIL_WORD, &x1, &y1, &x2, &y2);

                    words.append(nb::make_tuple(
                        std::string(word),
                        static_cast<int>(conf),
                        x1, y1,
                        x2 - x1,  // width
                        y2 - y1   // height
                    ));
                    delete[] word;
                }
            } while (ri->Next(tesseract::RIL_WORD));
            delete ri;
        }

        return words;
    }

    nb::list get_textlines() {
        nb::list lines;

        tesseract::ResultIterator* ri = api_->GetIterator();
        if (ri != nullptr) {
            do {
                const char* line = ri->GetUTF8Text(tesseract::RIL_TEXTLINE);
                if (line) {
                    float conf = ri->Confidence(tesseract::RIL_TEXTLINE);
                    int x1, y1, x2, y2;
                    ri->BoundingBox(tesseract::RIL_TEXTLINE, &x1, &y1, &x2, &y2);

                    lines.append(nb::make_tuple(
                        std::string(line),
                        static_cast<int>(conf),
                        x1, y1,
                        x2 - x1,  // width
                        y2 - y1   // height
                    ));
                    delete[] line;
                }
            } while (ri->Next(tesseract::RIL_TEXTLINE));
            delete ri;
        }

        return lines;
    }

    // Phase 3b: GetThresholdedImage
    // Returns (height, width, data_as_list) tuple for Python to convert to numpy
    nb::tuple get_thresholded_image() {
        Pix* pix = api_->GetThresholdedImage();
        if (!pix) {
            // Return empty dimensions
            return nb::make_tuple(0, 0, nb::list());
        }

        // Convert 1bpp to 8bpp for easier handling
        Pix* pix8 = nullptr;
        int depth = pixGetDepth(pix);

        if (depth == 1) {
            // Convert 1bpp to 8bpp (0 -> 0, 1 -> 255)
            pix8 = pixConvert1To8(nullptr, pix, 0, 255);
        } else if (depth == 8) {
            // Already 8bpp
            pix8 = pixClone(pix);
        } else {
            // Unsupported depth
            pixDestroy(&pix);
            return nb::make_tuple(0, 0, nb::list());
        }

        int width = pixGetWidth(pix8);
        int height = pixGetHeight(pix8);

        // Create bytes object for efficient transfer
        std::vector<uint8_t> data(height * width);

        // Copy pixel data
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                uint32_t val;
                pixGetPixel(pix8, x, y, &val);
                data[y * width + x] = static_cast<uint8_t>(val);
            }
        }

        // Clean up Pix objects
        pixDestroy(&pix);
        pixDestroy(&pix8);

        // Convert to Python bytes for efficient transfer
        nb::bytes py_data(reinterpret_cast<const char*>(data.data()), data.size());

        return nb::make_tuple(height, width, py_data);
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
        .def("get_mean_confidence", &TesseractAPI::get_mean_confidence,
             "Get mean confidence score (0-100)")
        .def("get_bounding_boxes", &TesseractAPI::get_bounding_boxes,
             "Get bounding boxes with text and confidence for each word")
        .def_static("version", &TesseractAPI::version,
                   "Get Tesseract version")

        // Phase 1: High-priority methods
        .def("set_page_seg_mode", &TesseractAPI::set_page_seg_mode,
             "mode"_a,
             "Set page segmentation mode")
        .def("get_page_seg_mode", &TesseractAPI::get_page_seg_mode,
             "Get current page segmentation mode")
        .def("set_variable", &TesseractAPI::set_variable,
             "name"_a, "value"_a,
             "Set a Tesseract variable")
        .def("get_int_variable", &TesseractAPI::get_int_variable,
             "name"_a, "value"_a,
             "Get an integer variable value")
        .def("get_bool_variable", &TesseractAPI::get_bool_variable,
             "name"_a, "value"_a,
             "Get a boolean variable value")
        .def("get_double_variable", &TesseractAPI::get_double_variable,
             "name"_a, "value"_a,
             "Get a double variable value")
        .def("get_string_variable", &TesseractAPI::get_string_variable,
             "name"_a,
             "Get a string variable value")
        .def("set_rectangle", &TesseractAPI::set_rectangle,
             "left"_a, "top"_a, "width"_a, "height"_a,
             "Set rectangle to restrict recognition to a sub-image")
        .def("get_hocr_text", &TesseractAPI::get_hocr_text,
             "page_number"_a = 0,
             "Get OCR result in hOCR format")
        .def("get_tsv_text", &TesseractAPI::get_tsv_text,
             "page_number"_a = 0,
             "Get OCR result in TSV format")
        .def("get_box_text", &TesseractAPI::get_box_text,
             "page_number"_a = 0,
             "Get OCR result in box file format")
        .def("get_unlv_text", &TesseractAPI::get_unlv_text,
             "Get OCR result in UNLV format")
        .def("clear", &TesseractAPI::clear,
             "Clear recognition results")
        .def("clear_adaptive_classifier", &TesseractAPI::clear_adaptive_classifier,
             "Clear adaptive classifier")
        .def("get_datapath", &TesseractAPI::get_datapath,
             "Get tessdata path")
        .def("get_init_languages_as_string", &TesseractAPI::get_init_languages_as_string,
             "Get initialized languages as string")

        // Phase 2: Medium-priority methods
        .def("detect_orientation_script", &TesseractAPI::detect_orientation_script,
             "Detect page orientation and script")
        .def("get_component_images", &TesseractAPI::get_component_images,
             "level"_a, "text_only"_a = true,
             "Get component images at specified level")

        // Phase 3: Additional layout analysis methods
        .def("get_words", &TesseractAPI::get_words,
             "Get all words with text, confidence, and bounding boxes")
        .def("get_textlines", &TesseractAPI::get_textlines,
             "Get all text lines with text, confidence, and bounding boxes")

        // Phase 3b: GetThresholdedImage
        .def("get_thresholded_image", &TesseractAPI::get_thresholded_image,
             "Get the thresholded (binarized) image as a numpy array");
}
