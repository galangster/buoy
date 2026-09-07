# Buoy 1.003

Two static weights: Regular 400 and Medium 500. No italic or bold.

Use WOFF2 for Latin web text with combining marks. Use Latin TTF for server
images. Use full TTF for desktop, print and the broader character set.
Keep OFL.txt and NOTICE.md with any redistribution.

```css
@font-face {
  font-family: "Buoy";
  src: url("Buoy-Regular.woff2") format("woff2");
  font-style: normal;
  font-weight: 400;
  font-display: swap;
}
@font-face {
  font-family: "Buoy";
  src: url("Buoy-Medium.woff2") format("woff2");
  font-style: normal;
  font-weight: 500;
  font-display: swap;
}
body { font-family: "Buoy", sans-serif; font-synthesis: none; }
.amount { font-variant-numeric: tabular-nums; }
```

Enable `zero` for a slashed zero and `ss02` for disambiguated I and l.
Optional fallback.css adjusts Arial/Helvetica Neue line metrics. Add
"Buoy Fallback" before sans-serif when using that stylesheet. It cannot
prevent every wrap change during loading.

Read READINESS.md for validated scope and remaining review requirements.
manifest.json hashes the frozen release files. PACKAGE-SHA256.json hashes
all package contents except itself. The archive is a candidate, not a tagged release.
