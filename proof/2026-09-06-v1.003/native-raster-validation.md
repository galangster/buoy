# Native raster validation

The hosted validation workflow renders the frozen v1.003 font artifacts on
Windows Server 2022 and Ubuntu 24.04. It does not install the fonts systemwide.

The checked-in fixture contains 96 glyph runs shaped by HarfBuzz on the local
build machine. Each native renderer consumes those fixed glyph ids, advances
and offsets at 100% and 125% scale. The result is 192 raster runs per renderer.
This is DirectWrite and FreeType raster evidence. It is not Windows or Linux
shaping evidence.

The runs cover both weights and both full and Latin TTF artifacts at 11, 12,
13, 14, 16 and 18 px. Each size contains these rows in order:

1. Basic stems.
2. Round commas and quotation marks.
3. Digits and financial punctuation.
4. NFC, NFD and stacked accent samples.

The Windows tool uses Microsoft's documented
[`CreateFontFileReference`](https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nf-dwrite-idwritefactory-createfontfilereference),
[`CreateFontFace`](https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nf-dwrite-idwritefactory-createfontface),
[`CreateGlyphRunAnalysis`](https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nf-dwrite-idwritefactory-createglyphrunanalysis),
[`GetAlphaTextureBounds`](https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nf-dwrite-idwriteglyphrunanalysis-getalphatexturebounds)
and
[`CreateAlphaTexture`](https://learn.microsoft.com/en-us/windows/win32/api/dwrite/nf-dwrite-idwriteglyphrunanalysis-createalphatexture)
APIs. WIC encodes the offscreen textures as PNG files.

Each job fails if a font SHA-256 differs, a texture is empty, a PNG is empty,
or rendered content reaches the outer target border. The JSON reports record
the actual OS, renderer, raster mode, font hashes, sheet sizes and ink totals.
Each job uploads eight PNG sheets and its JSON report as an Actions artifact.

The workflow is
`.github/workflows/native-raster-validation.yml`. Its actions are pinned to
commit hashes. It has read-only repository permissions and a ten-minute job
timeout.
