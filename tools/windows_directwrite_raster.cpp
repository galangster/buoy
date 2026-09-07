#define NOMINMAX

#include <windows.h>

#include <bcrypt.h>
#include <dwrite.h>
#include <wincodec.h>
#include <wrl/client.h>

#include <algorithm>
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using Microsoft::WRL::ComPtr;
namespace fs = std::filesystem;

namespace {

constexpr UINT32 kPadding = 12;
constexpr UINT32 kGap = 8;
constexpr auto kTextureType = DWRITE_TEXTURE_CLEARTYPE_3x1;

struct Run {
    std::string font_id;
    fs::path font_path;
    std::string expected_sha256;
    std::string weight;
    UINT32 upem = 0;
    FLOAT size_px = 0;
    std::string case_id;
    std::vector<UINT16> glyph_ids;
    std::vector<int> x_advances;
    std::vector<int> y_advances;
    std::vector<int> x_offsets;
    std::vector<int> y_offsets;
};

struct FontContext {
    ComPtr<IDWriteFontFile> file;
    ComPtr<IDWriteFontFace> face;
    std::string sha256;
};

struct Raster {
    UINT32 width = 0;
    UINT32 height = 0;
    std::vector<BYTE> bgra;
    RECT directwrite_bounds{};
    uint64_t ink_sum = 0;
};

struct SheetResult {
    std::string font_id;
    std::string weight;
    std::string sha256;
    FLOAT scale = 0;
    UINT32 width = 0;
    UINT32 height = 0;
    UINT32 run_count = 0;
    uint64_t ink_sum = 0;
    bool nonempty = false;
    bool unclipped = false;
    fs::path output;
};

void check_hr(HRESULT result, const char* operation) {
    if (FAILED(result)) {
        std::ostringstream message;
        message << operation << " failed with HRESULT 0x" << std::hex
                << static_cast<unsigned long>(result);
        throw std::runtime_error(message.str());
    }
}

std::vector<std::string> split(const std::string& value, char separator) {
    std::vector<std::string> parts;
    std::stringstream stream(value);
    std::string part;
    while (std::getline(stream, part, separator)) {
        parts.push_back(part);
    }
    return parts;
}

std::vector<int> parse_ints(const std::string& value) {
    std::vector<int> result;
    for (const auto& part : split(value, ',')) {
        result.push_back(std::stoi(part));
    }
    return result;
}

std::vector<Run> read_runs(const fs::path& fixture, const fs::path& root) {
    std::ifstream input(fixture, std::ios::binary);
    if (!input) {
        throw std::runtime_error("cannot open fixture: " + fixture.string());
    }

    std::vector<Run> runs;
    std::string line;
    bool saw_header = false;
    while (std::getline(input, line)) {
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        if (line.empty() || line[0] == '#') {
            continue;
        }
        if (!saw_header) {
            saw_header = true;
            continue;
        }
        const auto fields = split(line, '\t');
        if (fields.size() != 13) {
            throw std::runtime_error("fixture row does not have 13 fields");
        }
        Run run;
        run.font_id = fields[0];
        run.font_path = fs::absolute(root / fs::u8path(fields[1]));
        run.expected_sha256 = fields[2];
        run.weight = fields[3];
        run.upem = static_cast<UINT32>(std::stoul(fields[4]));
        run.size_px = std::stof(fields[5]);
        run.case_id = fields[6];
        const auto glyphs = parse_ints(fields[8]);
        run.x_advances = parse_ints(fields[9]);
        run.y_advances = parse_ints(fields[10]);
        run.x_offsets = parse_ints(fields[11]);
        run.y_offsets = parse_ints(fields[12]);
        for (const int glyph : glyphs) {
            if (glyph <= 0 || glyph > 65535) {
                throw std::runtime_error("fixture contains an invalid glyph id");
            }
            run.glyph_ids.push_back(static_cast<UINT16>(glyph));
        }
        const auto count = run.glyph_ids.size();
        if (!count || run.x_advances.size() != count ||
            run.y_advances.size() != count || run.x_offsets.size() != count ||
            run.y_offsets.size() != count || !run.upem) {
            throw std::runtime_error("fixture glyph and position counts differ");
        }
        runs.push_back(std::move(run));
    }
    if (!saw_header || runs.empty()) {
        throw std::runtime_error("fixture has no runs");
    }
    return runs;
}

std::string hex_string(const std::vector<BYTE>& bytes) {
    std::ostringstream out;
    out << std::hex << std::setfill('0');
    for (const BYTE byte : bytes) {
        out << std::setw(2) << static_cast<unsigned>(byte);
    }
    return out.str();
}

std::string sha256(const fs::path& path) {
    BCRYPT_ALG_HANDLE algorithm = nullptr;
    BCRYPT_HASH_HANDLE hash = nullptr;
    DWORD object_size = 0;
    DWORD digest_size = 0;
    DWORD received = 0;
    std::vector<BYTE> object;
    std::vector<BYTE> digest;
    try {
        auto status = BCryptOpenAlgorithmProvider(
            &algorithm, BCRYPT_SHA256_ALGORITHM, nullptr, 0);
        if (status < 0) {
            throw std::runtime_error("BCryptOpenAlgorithmProvider failed");
        }
        status = BCryptGetProperty(
            algorithm, BCRYPT_OBJECT_LENGTH,
            reinterpret_cast<PUCHAR>(&object_size), sizeof(object_size),
            &received, 0);
        if (status < 0) {
            throw std::runtime_error("BCryptGetProperty object length failed");
        }
        status = BCryptGetProperty(
            algorithm, BCRYPT_HASH_LENGTH,
            reinterpret_cast<PUCHAR>(&digest_size), sizeof(digest_size),
            &received, 0);
        if (status < 0) {
            throw std::runtime_error("BCryptGetProperty hash length failed");
        }
        object.resize(object_size);
        digest.resize(digest_size);
        status = BCryptCreateHash(
            algorithm, &hash, object.data(), object_size, nullptr, 0, 0);
        if (status < 0) {
            throw std::runtime_error("BCryptCreateHash failed");
        }

        std::ifstream input(path, std::ios::binary);
        if (!input) {
            throw std::runtime_error("cannot hash font: " + path.string());
        }
        std::array<char, 64 * 1024> buffer{};
        while (input) {
            input.read(buffer.data(), static_cast<std::streamsize>(buffer.size()));
            const auto count = input.gcount();
            if (count > 0) {
                status = BCryptHashData(
                    hash, reinterpret_cast<PUCHAR>(buffer.data()),
                    static_cast<ULONG>(count), 0);
                if (status < 0) {
                    throw std::runtime_error("BCryptHashData failed");
                }
            }
        }
        status = BCryptFinishHash(hash, digest.data(), digest_size, 0);
        if (status < 0) {
            throw std::runtime_error("BCryptFinishHash failed");
        }
    } catch (...) {
        if (hash) BCryptDestroyHash(hash);
        if (algorithm) BCryptCloseAlgorithmProvider(algorithm, 0);
        throw;
    }
    BCryptDestroyHash(hash);
    BCryptCloseAlgorithmProvider(algorithm, 0);
    return hex_string(digest);
}

FontContext load_font(IDWriteFactory* factory, const Run& run) {
    FontContext context;
    context.sha256 = sha256(run.font_path);
    if (context.sha256 != run.expected_sha256) {
        throw std::runtime_error("font hash mismatch: " + run.font_path.string());
    }
    check_hr(factory->CreateFontFileReference(
                 run.font_path.c_str(), nullptr, &context.file),
             "CreateFontFileReference");

    BOOL supported = FALSE;
    DWRITE_FONT_FILE_TYPE file_type{};
    DWRITE_FONT_FACE_TYPE face_type{};
    UINT32 face_count = 0;
    check_hr(context.file->Analyze(
                 &supported, &file_type, &face_type, &face_count),
             "IDWriteFontFile::Analyze");
    if (!supported || face_count != 1) {
        throw std::runtime_error("font must contain one supported face");
    }
    IDWriteFontFile* files[] = {context.file.Get()};
    check_hr(factory->CreateFontFace(
                 face_type, 1, files, 0, DWRITE_FONT_SIMULATIONS_NONE,
                 &context.face),
             "CreateFontFace");
    const auto metrics = [&] {
        DWRITE_FONT_METRICS value{};
        context.face->GetMetrics(&value);
        return value;
    }();
    if (metrics.designUnitsPerEm != run.upem) {
        throw std::runtime_error("fixture and DirectWrite UPEM differ");
    }
    return context;
}

Raster rasterize(
    IDWriteFactory* factory,
    IDWriteFontFace* face,
    const Run& run,
    FLOAT scale) {
    const FLOAT units_to_dip = run.size_px / static_cast<FLOAT>(run.upem);
    std::vector<FLOAT> advances;
    std::vector<DWRITE_GLYPH_OFFSET> offsets;
    advances.reserve(run.glyph_ids.size());
    offsets.reserve(run.glyph_ids.size());
    for (size_t i = 0; i < run.glyph_ids.size(); ++i) {
        advances.push_back(run.x_advances[i] * units_to_dip);
        offsets.push_back(DWRITE_GLYPH_OFFSET{
            run.x_offsets[i] * units_to_dip,
            run.y_offsets[i] * units_to_dip,
        });
        if (run.y_advances[i] != 0) {
            throw std::runtime_error("vertical advances are not supported");
        }
    }

    DWRITE_GLYPH_RUN glyph_run{};
    glyph_run.fontFace = face;
    glyph_run.fontEmSize = run.size_px;
    glyph_run.glyphCount = static_cast<UINT32>(run.glyph_ids.size());
    glyph_run.glyphIndices = run.glyph_ids.data();
    glyph_run.glyphAdvances = advances.data();
    glyph_run.glyphOffsets = offsets.data();
    glyph_run.isSideways = FALSE;
    glyph_run.bidiLevel = 0;

    ComPtr<IDWriteGlyphRunAnalysis> analysis;
    check_hr(factory->CreateGlyphRunAnalysis(
                 &glyph_run, scale, nullptr,
                 DWRITE_RENDERING_MODE_NATURAL_SYMMETRIC,
                 DWRITE_MEASURING_MODE_NATURAL, 0.0f, 0.0f, &analysis),
             "CreateGlyphRunAnalysis");
    RECT bounds{};
    check_hr(analysis->GetAlphaTextureBounds(kTextureType, &bounds),
             "GetAlphaTextureBounds");
    const LONG signed_width = bounds.right - bounds.left;
    const LONG signed_height = bounds.bottom - bounds.top;
    if (signed_width <= 0 || signed_height <= 0) {
        throw std::runtime_error("DirectWrite returned empty texture bounds");
    }
    const auto width = static_cast<UINT32>(signed_width);
    const auto height = static_cast<UINT32>(signed_height);
    const uint64_t alpha_size = static_cast<uint64_t>(width) * height * 3;
    if (alpha_size > UINT32_MAX) {
        throw std::runtime_error("alpha texture is too large");
    }
    std::vector<BYTE> alpha(static_cast<size_t>(alpha_size));
    check_hr(analysis->CreateAlphaTexture(
                 kTextureType, &bounds, alpha.data(),
                 static_cast<UINT32>(alpha.size())),
             "CreateAlphaTexture");

    Raster raster;
    raster.width = width;
    raster.height = height;
    raster.directwrite_bounds = bounds;
    raster.bgra.resize(static_cast<size_t>(width) * height * 4, 255);
    for (size_t pixel = 0; pixel < static_cast<size_t>(width) * height; ++pixel) {
        const BYTE red = alpha[pixel * 3];
        const BYTE green = alpha[pixel * 3 + 1];
        const BYTE blue = alpha[pixel * 3 + 2];
        raster.ink_sum += static_cast<uint64_t>(red) + green + blue;
        raster.bgra[pixel * 4] = static_cast<BYTE>(255 - blue);
        raster.bgra[pixel * 4 + 1] = static_cast<BYTE>(255 - green);
        raster.bgra[pixel * 4 + 2] = static_cast<BYTE>(255 - red);
        raster.bgra[pixel * 4 + 3] = 255;
    }
    if (!raster.ink_sum) {
        throw std::runtime_error("DirectWrite alpha texture is empty");
    }
    return raster;
}

void save_png(
    IWICImagingFactory* factory,
    const fs::path& path,
    UINT32 width,
    UINT32 height,
    const std::vector<BYTE>& pixels) {
    ComPtr<IWICStream> stream;
    check_hr(factory->CreateStream(&stream), "IWICImagingFactory::CreateStream");
    check_hr(stream->InitializeFromFilename(path.c_str(), GENERIC_WRITE),
             "IWICStream::InitializeFromFilename");
    ComPtr<IWICBitmapEncoder> encoder;
    check_hr(factory->CreateEncoder(
                 GUID_ContainerFormatPng, nullptr, &encoder),
             "IWICImagingFactory::CreateEncoder");
    check_hr(encoder->Initialize(stream.Get(), WICBitmapEncoderNoCache),
             "IWICBitmapEncoder::Initialize");
    ComPtr<IWICBitmapFrameEncode> frame;
    check_hr(encoder->CreateNewFrame(&frame, nullptr),
             "IWICBitmapEncoder::CreateNewFrame");
    check_hr(frame->Initialize(nullptr), "IWICBitmapFrameEncode::Initialize");
    check_hr(frame->SetSize(width, height), "IWICBitmapFrameEncode::SetSize");
    WICPixelFormatGUID format = GUID_WICPixelFormat32bppBGRA;
    check_hr(frame->SetPixelFormat(&format),
             "IWICBitmapFrameEncode::SetPixelFormat");
    if (!IsEqualGUID(format, GUID_WICPixelFormat32bppBGRA)) {
        throw std::runtime_error("WIC changed the requested pixel format");
    }
    const UINT32 stride = width * 4;
    if (pixels.size() > UINT32_MAX) {
        throw std::runtime_error("PNG buffer is too large");
    }
    check_hr(frame->WritePixels(
                 height, stride, static_cast<UINT32>(pixels.size()),
                 const_cast<BYTE*>(pixels.data())),
             "IWICBitmapFrameEncode::WritePixels");
    check_hr(frame->Commit(), "IWICBitmapFrameEncode::Commit");
    check_hr(encoder->Commit(), "IWICBitmapEncoder::Commit");
}

bool border_is_white(
    const std::vector<BYTE>& pixels, UINT32 width, UINT32 height) {
    const auto white = [&](UINT32 x, UINT32 y) {
        const size_t offset = (static_cast<size_t>(y) * width + x) * 4;
        return pixels[offset] == 255 && pixels[offset + 1] == 255 &&
               pixels[offset + 2] == 255 && pixels[offset + 3] == 255;
    };
    for (UINT32 x = 0; x < width; ++x) {
        if (!white(x, 0) || !white(x, height - 1)) return false;
    }
    for (UINT32 y = 0; y < height; ++y) {
        if (!white(0, y) || !white(width - 1, y)) return false;
    }
    return true;
}

SheetResult make_sheet(
    IWICImagingFactory* wic,
    const std::string& font_id,
    const std::string& weight,
    const std::string& digest,
    FLOAT scale,
    const std::vector<Raster>& rasters,
    const fs::path& output) {
    UINT32 width = kPadding * 2;
    UINT32 height = kPadding * 2;
    uint64_t ink_sum = 0;
    for (const auto& raster : rasters) {
        width = std::max(width, raster.width + kPadding * 2);
        height += raster.height + kGap;
        ink_sum += raster.ink_sum;
    }
    if (!rasters.empty()) height -= kGap;
    std::vector<BYTE> sheet(static_cast<size_t>(width) * height * 4, 255);
    UINT32 y = kPadding;
    for (const auto& raster : rasters) {
        for (UINT32 row = 0; row < raster.height; ++row) {
            const size_t source = static_cast<size_t>(row) * raster.width * 4;
            const size_t target =
                (static_cast<size_t>(y + row) * width + kPadding) * 4;
            std::copy_n(
                raster.bgra.begin() + source,
                static_cast<size_t>(raster.width) * 4,
                sheet.begin() + target);
        }
        y += raster.height + kGap;
    }
    const bool unclipped = border_is_white(sheet, width, height);
    if (!ink_sum || !unclipped) {
        throw std::runtime_error("sheet is empty or touches its target border");
    }
    save_png(wic, output, width, height, sheet);
    if (!fs::exists(output) || fs::file_size(output) == 0) {
        throw std::runtime_error("WIC did not write a nonempty PNG");
    }
    return SheetResult{
        font_id, weight, digest, scale, width, height,
        static_cast<UINT32>(rasters.size()), ink_sum, true, unclipped, output};
}

std::string json_escape(const std::string& value) {
    std::ostringstream out;
    for (const unsigned char character : value) {
        switch (character) {
            case '\\': out << "\\\\"; break;
            case '"': out << "\\\""; break;
            case '\n': out << "\\n"; break;
            case '\r': out << "\\r"; break;
            case '\t': out << "\\t"; break;
            default:
                if (character < 0x20) {
                    out << "\\u" << std::hex << std::setw(4)
                        << std::setfill('0') << static_cast<unsigned>(character)
                        << std::dec;
                } else {
                    out << character;
                }
        }
    }
    return out.str();
}

std::string os_version() {
    constexpr auto key = L"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion";
    DWORD major = 0;
    DWORD minor = 0;
    DWORD size = sizeof(DWORD);
    if (RegGetValueW(
            HKEY_LOCAL_MACHINE, key, L"CurrentMajorVersionNumber",
            RRF_RT_REG_DWORD, nullptr, &major, &size) != ERROR_SUCCESS) {
        return "unavailable";
    }
    size = sizeof(DWORD);
    if (RegGetValueW(
            HKEY_LOCAL_MACHINE, key, L"CurrentMinorVersionNumber",
            RRF_RT_REG_DWORD, nullptr, &minor, &size) != ERROR_SUCCESS) {
        return "unavailable";
    }
    std::array<wchar_t, 64> build{};
    size = static_cast<DWORD>(build.size() * sizeof(wchar_t));
    if (RegGetValueW(
            HKEY_LOCAL_MACHINE, key, L"CurrentBuildNumber", RRF_RT_REG_SZ,
            nullptr, build.data(), &size) != ERROR_SUCCESS) {
        return "unavailable";
    }
    std::ostringstream out;
    out << major << '.' << minor << '.';
    for (const wchar_t character : build) {
        if (!character) break;
        if (character < L'0' || character > L'9') return "unavailable";
        out << static_cast<char>(character);
    }
    return out.str();
}

void write_report(
    const fs::path& path,
    const fs::path& fixture,
    const std::vector<SheetResult>& sheets,
    size_t total_runs) {
    std::ofstream report(path, std::ios::binary);
    if (!report) throw std::runtime_error("cannot create report");
    report << "{\n"
           << "  \"schemaVersion\": 1,\n"
           << "  \"result\": \"pass\",\n"
           << "  \"proofType\": \"DirectWrite raster proof from pre-shaped HarfBuzz glyph runs\",\n"
           << "  \"windowsShapingProof\": false,\n"
           << "  \"osVersion\": \"" << os_version() << "\",\n"
           << "  \"renderer\": \"DirectWrite CreateGlyphRunAnalysis and CreateAlphaTexture\",\n"
           << "  \"rasterMode\": \"DWRITE_RENDERING_MODE_NATURAL_SYMMETRIC with DWRITE_TEXTURE_CLEARTYPE_3x1\",\n"
           << "  \"pngEncoder\": \"Windows Imaging Component\",\n"
           << "  \"fontLoading\": \"CreateFontFileReference and CreateFontFace; no system font installation\",\n"
           << "  \"fixture\": \"" << json_escape(fixture.generic_string()) << "\",\n"
           << "  \"sizesPx\": [11, 12, 13, 14, 16, 18],\n"
           << "  \"scales\": [1.0, 1.25],\n"
           << "  \"caseIds\": [\"stems\", \"round-punctuation\", \"digits\", \"accents\"],\n"
           << "  \"sourceRunCount\": " << total_runs << ",\n"
           << "  \"rasterizedRunCount\": " << total_runs * 2 << ",\n"
           << "  \"checks\": {\n"
           << "    \"fontHashesMatch\": true,\n"
           << "    \"allTexturesNonempty\": true,\n"
           << "    \"allPngsNonempty\": true,\n"
           << "    \"allTargetBordersClear\": true\n"
           << "  },\n"
           << "  \"sheets\": [\n";
    for (size_t index = 0; index < sheets.size(); ++index) {
        const auto& sheet = sheets[index];
        report << "    {\"fontId\": \"" << json_escape(sheet.font_id)
               << "\", \"weight\": \"" << json_escape(sheet.weight)
               << "\", \"sha256\": \"" << sheet.sha256
               << "\", \"scale\": " << sheet.scale
               << ", \"width\": " << sheet.width
               << ", \"height\": " << sheet.height
               << ", \"runCount\": " << sheet.run_count
               << ", \"inkSum\": " << sheet.ink_sum
               << ", \"nonempty\": true, \"targetBorderClear\": true"
               << ", \"png\": \"" << json_escape(sheet.output.filename().string())
               << "\"}" << (index + 1 == sheets.size() ? "\n" : ",\n");
    }
    report << "  ]\n}\n";
}

}  // namespace

int wmain(int argc, wchar_t** argv) {
    try {
        if (argc != 3) {
            std::cerr << "usage: windows_directwrite_raster <fixture.tsv> <output-dir>\n";
            return 2;
        }
        const fs::path fixture = fs::absolute(argv[1]);
        const fs::path output_dir = fs::absolute(argv[2]);
        const fs::path root = fs::current_path();
        fs::create_directories(output_dir);

        check_hr(CoInitializeEx(nullptr, COINIT_MULTITHREADED), "CoInitializeEx");
        struct CoCleanup {
            ~CoCleanup() { CoUninitialize(); }
        } cleanup;

        ComPtr<IDWriteFactory> dwrite;
        check_hr(DWriteCreateFactory(
                     DWRITE_FACTORY_TYPE_ISOLATED, __uuidof(IDWriteFactory),
                     reinterpret_cast<IUnknown**>(dwrite.GetAddressOf())),
                 "DWriteCreateFactory");
        ComPtr<IWICImagingFactory> wic;
        check_hr(CoCreateInstance(
                     CLSID_WICImagingFactory, nullptr, CLSCTX_INPROC_SERVER,
                     __uuidof(IWICImagingFactory),
                     reinterpret_cast<void**>(wic.GetAddressOf())),
                 "CoCreateInstance WIC factory");

        const auto runs = read_runs(fixture, root);
        std::map<std::string, std::vector<const Run*>> groups;
        for (const auto& run : runs) groups[run.font_id].push_back(&run);

        std::vector<SheetResult> sheets;
        for (const auto& [font_id, font_runs] : groups) {
            const Run& first = *font_runs.front();
            const auto context = load_font(dwrite.Get(), first);
            for (const Run* run : font_runs) {
                if (run->font_path != first.font_path ||
                    run->expected_sha256 != first.expected_sha256 ||
                    run->weight != first.weight || run->upem != first.upem) {
                    throw std::runtime_error("font fixture metadata is inconsistent");
                }
            }
            for (const FLOAT scale : {1.0f, 1.25f}) {
                std::vector<Raster> rasters;
                rasters.reserve(font_runs.size());
                for (const Run* run : font_runs) {
                    rasters.push_back(rasterize(
                        dwrite.Get(), context.face.Get(), *run, scale));
                }
                const std::string scale_name = scale == 1.0f ? "100" : "125";
                const fs::path output =
                    output_dir / fs::u8path(font_id + "-scale-" + scale_name + ".png");
                sheets.push_back(make_sheet(
                    wic.Get(), font_id, first.weight, context.sha256, scale,
                    rasters, output));
            }
        }
        if (sheets.size() != 8 || runs.size() != 96) {
            throw std::runtime_error("expected 96 runs and eight PNG sheets");
        }
        write_report(
            output_dir / "directwrite-report.json",
            fs::relative(fixture, root), sheets, runs.size());
        std::cout << "PASS: 192 DirectWrite raster runs, eight PNG sheets\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "FAIL: " << error.what() << '\n';
        return 1;
    }
}
