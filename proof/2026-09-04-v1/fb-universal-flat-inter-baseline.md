## FontBakery report

fontbakery version: 1.1.0







## Check results



<details><summary>[1] Family checks</summary>
<div>
<details>
    <summary>🔥 <b>FAIL</b> Fonts have consistent underline thickness? <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/opentype.html#opentype-family-underline-thickness">opentype/family/underline_thickness</a></summary>
    <div>


> 
> Dave C Lemon (Adobe Type Team) recommends setting the underline thickness to be
> consistent across the family.
> 
> If thicknesses are not family consistent, words set on the same line which have
> different styles look strange.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/4829





* 🔥 **FAIL** <p>Thickness of the underline is not the same across this family. In order to fix this, please make sure that the underlineThickness value is the same in the 'post' table of all of this family font files.
Detected underlineThickness values are:
build/flat/Inter-Regular.ttf: 140
build/flat/Inter-Medium.ttf: 157</p>
 [code: inconsistent-underline-thickness]



</div>
</details>
</div>
</details>

<details><summary>[8] Inter-Regular.ttf</summary>
<div>
<details>
    <summary>🔥 <b>FAIL</b> Check base characters have non-zero advance width. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#base-has-width">base_has_width</a></summary>
    <div>


> 
> Base characters should have non-zero advance width.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/4906





* 🔥 **FAIL** <p>The following glyphs had zero advance width:
- uni0488 (U+0488)</p>
<pre><code>- uni0489 (U+0489)
</code></pre>
 [code: zero-width-bases]



</div>
</details>

<details>
    <summary>🔥 <b>FAIL</b> Ensure the font supports case swapping for all its glyphs. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#case-mapping">case_mapping</a></summary>
    <div>


> 
> Ensure that no glyph lacks its corresponding upper or lower counterpart
> (but only when unicode supports case-mapping).
> 




> Original proposal: https://github.com/googlefonts/fontbakery/issues/3230





* 🔥 **FAIL** <p>The following glyphs lack their case-swapping counterparts:</p>
<table>
<thead>
<tr>
<th align="left">Glyph present in the font</th>
<th align="left">Missing case-swapping counterpart</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left">U+019B: LATIN SMALL LETTER LAMBDA WITH STROKE</td>
<td align="left">U+A7DC: LATIN CAPITAL LETTER LAMBDA WITH STROKE</td>
</tr>
<tr>
<td align="left">U+01C6: LATIN SMALL LETTER DZ WITH CARON</td>
<td align="left">U+01C4: LATIN CAPITAL LETTER DZ WITH CARON</td>
</tr>
<tr>
<td align="left">U+023A: LATIN CAPITAL LETTER A WITH STROKE</td>
<td align="left">U+2C65: LATIN SMALL LETTER A WITH STROKE</td>
</tr>
<tr>
<td align="left">U+023E: LATIN CAPITAL LETTER T WITH DIAGONAL STROKE</td>
<td align="left">U+2C66: LATIN SMALL LETTER T WITH DIAGONAL STROKE</td>
</tr>
<tr>
<td align="left">U+0264: LATIN SMALL LETTER RAMS HORN</td>
<td align="left">U+A7CB: LATIN CAPITAL LETTER RAMS HORN</td>
</tr>
<tr>
<td align="left">U+0265: LATIN SMALL LETTER TURNED H</td>
<td align="left">U+A78D: LATIN CAPITAL LETTER TURNED H</td>
</tr>
<tr>
<td align="left">U+0266: LATIN SMALL LETTER H WITH HOOK</td>
<td align="left">U+A7AA: LATIN CAPITAL LETTER H WITH HOOK</td>
</tr>
<tr>
<td align="left">U+026A: LATIN LETTER SMALL CAPITAL I</td>
<td align="left">U+A7AE: LATIN CAPITAL LETTER SMALL CAPITAL I</td>
</tr>
<tr>
<td align="left">U+026C: LATIN SMALL LETTER L WITH BELT</td>
<td align="left">U+A7AD: LATIN CAPITAL LETTER L WITH BELT</td>
</tr>
<tr>
<td align="left">U+029D: LATIN SMALL LETTER J WITH CROSSED-TAIL</td>
<td align="left">U+A7B2: LATIN CAPITAL LETTER J WITH CROSSED-TAIL</td>
</tr>
<tr>
<td align="left">U+0376: GREEK CAPITAL LETTER PAMPHYLIAN DIGAMMA</td>
<td align="left">U+0377: GREEK SMALL LETTER PAMPHYLIAN DIGAMMA</td>
</tr>
<tr>
<td align="left">U+03FA: GREEK CAPITAL LETTER SAN</td>
<td align="left">U+03FB: GREEK SMALL LETTER SAN</td>
</tr>
<tr>
<td align="left">U+052F: CYRILLIC SMALL LETTER EL WITH DESCENDER</td>
<td align="left">U+052E: CYRILLIC CAPITAL LETTER EL WITH DESCENDER</td>
</tr>
<tr>
<td align="left">U+2132: TURNED CAPITAL F</td>
<td align="left">U+214E: TURNED SMALL F</td>
</tr>
</tbody>
</table>
 [code: missing-case-counterparts]



</div>
</details>

<details>
    <summary>🔥 <b>FAIL</b> Checking OS/2 usWinAscent & usWinDescent. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#family-win-ascent-and-descent">family/win_ascent_and_descent</a></summary>
    <div>


> 
> A font's winAscent and winDescent values should be greater than or equal to
> the head table's yMax, abs(yMin) values. If they are less than these values,
> clipping can occur on Windows platforms
> (https://github.com/RedHatBrand/Overpass/issues/33).
> 
> If the font includes tall/deep writing systems such as Arabic or Devanagari,
> the winAscent and winDescent can be greater than the yMax and absolute yMin
> values to accommodate vowel marks.
> 
> When the 'win' Metrics are significantly greater than the UPM, the linespacing
> can appear too loose. To counteract this, enabling the OS/2 fsSelection
> bit 7 (Use_Typo_Metrics), will force Windows to use the OS/2 'typo' values
> instead. This means the font developer can control the linespacing with
> the 'typo' values, whilst avoiding clipping by setting the 'win' values to
> values greater than the yMax and absolute yMin.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/4829





* 🔥 **FAIL** <p>OS/2.usWinAscent value should be equal or greater than 2272, but got 1984 instead</p>
 [code: ascent]



* 🔥 **FAIL** <p>OS/2.usWinDescent value should be equal or greater than 668, but got 494 instead</p>
 [code: descent]



</div>
</details>

<details>
    <summary>🔥 <b>FAIL</b> Ensure smart dropout control is enabled in "prep" table instructions. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#smart-dropout">smart_dropout</a></summary>
    <div>


> 
> This setup is meant to ensure consistent rendering quality for fonts across
> all devices (with different rendering/hinting capabilities).
> 
> Below is the snippet of instructions we expect to see in the fonts:
> B8 01 FF    PUSHW 0x01FF
> 85          SCANCTRL (unconditinally turn on
> dropout control mode)
> B0 04       PUSHB 0x04
> 8D          SCANTYPE (enable smart dropout control)
> 
> "Smart dropout control" means activating rules 1, 2 and 5:
> Rule 1: If a pixel's center falls within the glyph outline,
> that pixel is turned on.
> Rule 2: If a contour falls exactly on a pixel's center,
> that pixel is turned on.
> Rule 5: If a scan line between two adjacent pixel centers
> (either vertical or horizontal) is intersected
> by both an on-Transition contour and an off-Transition
> contour and neither of the pixels was already turned on
> by rules 1 and 2, turn on the pixel which is closer to
> the midpoint between the on-Transition contour and
> off-Transition contour. This is "Smart" dropout control.
> 
> For more detailed info (such as other rules not enabled in this snippet),
> please refer to the TrueType Instruction Set documentation.
> 
> Generally this occurs with unhinted fonts; if you are not using autohinting,
> use gftools-fix-nonhinting (or just gftools-fix-font) to fix this issue.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/4829





* 🔥 **FAIL** <p>The 'prep' table does not contain TrueType instructions enabling smart dropout control. To fix, export the font with autohinting enabled, or run ttfautohint on the font, or run the <code>gftools fix-nonhinting</code> script.</p>
 [code: lacks-smart-dropout]



</div>
</details>

<details>
    <summary>🔥 <b>FAIL</b> Ensure component transforms do not perform scaling or rotation. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#transformed-components">transformed_components</a></summary>
    <div>


> 
> Some families have glyphs which have been constructed by using
> transformed components e.g the 'u' being constructed from a flipped 'n'.
> 
> From a designers point of view, this sounds like a win (less work).
> However, such approaches can lead to rasterization issues, such as
> having the 'u' not sitting on the baseline at certain sizes after
> running the font through ttfautohint.
> 
> Other issues are outlines that end up reversed when only one dimension
> is flipped while the other isn't.
> 
> As of July 2019, Marc Foley observed that ttfautohint assigns cvt values
> to transformed glyphs as if they are not transformed and the result is
> they render very badly, and that vttLib does not support flipped components.
> 
> When building the font with fontmake, the problem can be fixed by adding
> this to the command line:
> 
> --filter DecomposeTransformedComponentsFilter
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/2011





* 🔥 **FAIL** <p>The following glyphs had components with scaling or rotation
or inverted outline direction:</p>
<ul>
<li>uni1EB0 (component uni0306)</li>
<li>uni1EB0 (component acute_compact)</li>
<li>uni1F08 (component uni1FFE)</li>
<li>uni1F0A (component uni1FFE)</li>
<li>uni1F0A (component tonos.top)</li>
<li>uni1F0B (component tonos.top)</li>
<li>uni1F0C (component uni1FFE)</li>
<li>uni1F0E (component uni1FFE)</li>
<li>uni1FBA (component tonos.top)</li>
<li>uni1F88 (component uni1FFE)</li>
<li>uni1F8A (component uni1FFE)</li>
<li>uni1F8A (component tonos.top)</li>
<li>uni1F8B (component tonos.top)</li>
<li>uni1F8C (component uni1FFE)</li>
<li>uni1F8E (component uni1FFE)</li>
<li>uni1F18 (component uni1FFE)</li>
<li>uni1F1A (component uni1FFE)</li>
<li>uni1F1A (component tonos.top)</li>
<li>uni1F1B (component tonos.top)</li>
<li>uni1F1C (component uni1FFE)</li>
<li>uni1FC8 (component tonos.top)</li>
<li>uni1F28 (component uni1FFE)</li>
<li>uni1F2A (component uni1FFE)</li>
<li>uni1F2A (component tonos.top)</li>
<li>uni1F2B (component tonos.top)</li>
<li>uni1F2C (component uni1FFE)</li>
<li>uni1F2E (component uni1FFE)</li>
<li>uni1FCA (component tonos.top)</li>
<li>uni1F98 (component uni1FFE)</li>
<li>uni1F9A (component uni1FFE)</li>
<li>uni1F9A (component tonos.top)</li>
<li>uni1F9B (component tonos.top)</li>
<li>uni1F9C (component uni1FFE)</li>
<li>uni1F9E (component uni1FFE)</li>
<li>uni1F38 (component uni1FFE)</li>
<li>uni1F3A (component uni1FFE)</li>
<li>uni1F3A (component tonos.top)</li>
<li>uni1F3B (component tonos.top)</li>
<li>uni1F3C (component uni1FFE)</li>
<li>uni1F3E (component uni1FFE)</li>
<li>uni1FDA (component tonos.top)</li>
<li>uni1F38.1 (component uni1FFE)</li>
<li>uni1F3A.1 (component uni1FFE)</li>
<li>uni1F3A.1 (component tonos.top)</li>
<li>uni1F3B.1 (component tonos.top)</li>
<li>uni1F3C.1 (component uni1FFE)</li>
<li>uni1F3E.1 (component uni1FFE)</li>
<li>uni1FDA.1 (component tonos.top)</li>
<li>uni0418 (component N)</li>
<li>uni040D (component N)</li>
<li>uni0419 (component N)</li>
<li>uni04E2 (component N)</li>
<li>uni04E4 (component N)</li>
<li>uni048A (component N)</li>
<li>uni0376 (component N)</li>
<li>Ohungarumlaut (component uni030F)</li>
<li>uni1F48 (component uni1FFE)</li>
<li>uni1F4A (component uni1FFE)</li>
<li>uni1F4A (component tonos.top)</li>
<li>uni1F4B (component tonos.top)</li>
<li>uni1F4C (component uni1FFE)</li>
<li>uni1FF8 (component tonos.top)</li>
<li>uni01A7 (component S)</li>
<li>Uhungarumlaut (component uni030F)</li>
<li>uni1F5B (component tonos.top)</li>
<li>uni1FEA (component tonos.top)</li>
<li>uni1EB1 (component uni0306)</li>
<li>uni1EB1 (component acute_compact)</li>
<li>uni1EB1.1 (component uni0306)</li>
<li>uni1EB1.1 (component acute_compact)</li>
<li>uni1EB1.2 (component uni0306)</li>
<li>uni1EB1.2 (component acute_compact)</li>
<li>d (component b)</li>
<li>dcroat (component b)</li>
<li>dcaron (component b)</li>
<li>uni1E0B (component b)</li>
<li>uni1E0D (component b)</li>
<li>uni1E0F (component b)</li>
<li>uni1E11 (component b)</li>
<li>uni1E13 (component b)</li>
<li>uni01F3 (component b)</li>
<li>uni01C6 (component b)</li>
<li>dong (component b)</li>
<li>ohungarumlaut (component uni030F)</li>
<li>uni1F40 (component uni1FFE)</li>
<li>uni1F42 (component uni1FFE)</li>
<li>uni1F42 (component tonos.top)</li>
<li>uni1F43 (component tonos.top)</li>
<li>uni1F44 (component uni1FFE)</li>
<li>uni1F78 (component tonos.top)</li>
<li>q (component p)</li>
<li>uni027F (component uni027E)</li>
<li>uhungarumlaut (component uni030F)</li>
<li>uhungarumlaut.1 (component uni030F)</li>
<li>uni04F3 (component uni030F)</li>
<li>uni04F2 (component uni030F)</li>
<li>uni1F68 (component uni1FFE)</li>
<li>uni1F6A (component uni1FFE)</li>
<li>uni1F6A (component tonos.top)</li>
<li>uni1F6B (component tonos.top)</li>
<li>uni1F6C (component uni1FFE)</li>
<li>uni1F6E (component uni1FFE)</li>
<li>uni1FFA (component tonos.top)</li>
<li>uni1FA8 (component uni1FFE)</li>
<li>uni1FAA (component uni1FFE)</li>
<li>uni1FAA (component tonos.top)</li>
<li>uni1FAB (component tonos.top)</li>
<li>uni1FAC (component uni1FFE)</li>
<li>uni1FAE (component uni1FFE)</li>
<li>uni042F (component R)</li>
<li>uni1F00 (component uni1FFE)</li>
<li>uni1F02 (component uni1FFE)</li>
<li>uni1F02 (component tonos.top)</li>
<li>uni1F03 (component tonos.top)</li>
<li>uni1F04 (component uni1FFE)</li>
<li>uni1F06 (component uni1FFE)</li>
<li>uni1F70 (component tonos.top)</li>
<li>uni1F80 (component uni1FFE)</li>
<li>uni1F82 (component uni1FFE)</li>
<li>uni1F82 (component tonos.top)</li>
<li>uni1F83 (component tonos.top)</li>
<li>uni1F84 (component uni1FFE)</li>
<li>uni1F86 (component uni1FFE)</li>
<li>uni1FB2 (component tonos.top)</li>
<li>uni025C (component epsilon)</li>
<li>uni025E (component uni029A)</li>
<li>uni1F10 (component uni1FFE)</li>
<li>uni1F12 (component uni1FFE)</li>
<li>uni1F12 (component tonos.top)</li>
<li>uni1F13 (component tonos.top)</li>
<li>uni1F14 (component uni1FFE)</li>
<li>uni1F72 (component tonos.top)</li>
<li>uni1F20 (component uni1FFE)</li>
<li>uni1F22 (component uni1FFE)</li>
<li>uni1F22 (component tonos.top)</li>
<li>uni1F23 (component tonos.top)</li>
<li>uni1F24 (component uni1FFE)</li>
<li>uni1F26 (component uni1FFE)</li>
<li>uni1F74 (component tonos.top)</li>
<li>uni1F90 (component uni1FFE)</li>
<li>uni1F92 (component uni1FFE)</li>
<li>uni1F92 (component tonos.top)</li>
<li>uni1F93 (component tonos.top)</li>
<li>uni1F94 (component uni1FFE)</li>
<li>uni1F96 (component uni1FFE)</li>
<li>uni1FC2 (component tonos.top)</li>
<li>uni1F30 (component uni1FFE)</li>
<li>uni1F32 (component uni1FFE)</li>
<li>uni1F32 (component tonos.top)</li>
<li>uni1F33 (component tonos.top)</li>
<li>uni1F34 (component uni1FFE)</li>
<li>uni1F36 (component uni1FFE)</li>
<li>uni1F76 (component tonos.top)</li>
<li>uni1FD2 (component dieresistonos)</li>
<li>uni1FE4 (component uni1FFE)</li>
<li>uni1F50 (component uni1FFE)</li>
<li>uni1F52 (component uni1FFE)</li>
<li>uni1F52 (component tonos.top)</li>
<li>uni1F53 (component tonos.top)</li>
<li>uni1F54 (component uni1FFE)</li>
<li>uni1F56 (component uni1FFE)</li>
<li>uni1F7A (component tonos.top)</li>
<li>uni1FE2 (component dieresistonos)</li>
<li>uni1F60 (component uni1FFE)</li>
<li>uni1F62 (component uni1FFE)</li>
<li>uni1F62 (component tonos.top)</li>
<li>uni1F63 (component tonos.top)</li>
<li>uni1F64 (component uni1FFE)</li>
<li>uni1F66 (component uni1FFE)</li>
<li>uni1F7C (component tonos.top)</li>
<li>uni1FA0 (component uni1FFE)</li>
<li>uni1FA2 (component uni1FFE)</li>
<li>uni1FA2 (component tonos.top)</li>
<li>uni1FA3 (component tonos.top)</li>
<li>uni1FA4 (component uni1FFE)</li>
<li>uni1FA6 (component uni1FFE)</li>
<li>uni1FF2 (component tonos.top)</li>
<li>uni044D (component uni0454)</li>
<li>uni044F (component uni0280)</li>
<li>quotereversed (component quoteright)</li>
<li>uni201F (component quoteright)</li>
<li>uni201F (component quoteright)</li>
<li>uni204B (component paragraph)</li>
<li>hungarumlaut (component uni030F)</li>
<li>arrowright (component arrowleft)</li>
<li>uni27F6 (component uni27F5)</li>
<li>uni2197 (component uni2196)</li>
<li>uni2199 (component uni2196)</li>
<li>uni21AA (component uni21A9)</li>
<li>arrowright.case (component arrowleft)</li>
<li>uni27F6.case (component uni27F5)</li>
<li>uni2197.case (component uni2196)</li>
<li>uni2199.case (component uni2196)</li>
<li>arrowright.circled (component arrowleft)</li>
<li>arrowright.squared (component arrowleft)</li>
<li>uni204F.ss03 (component quoteright.ss03)</li>
<li>uni204F.ss03 (component period)</li>
<li>quotereversed.ss03 (component quoteright.ss03)</li>
<li>quotedblreversed.ss03 (component quoteright.ss03)</li>
<li>quotedblreversed.ss03 (component quoteright.ss03)</li>
<li>uni1E0B.ss07 (component b)</li>
<li>uni1E0D.ss07 (component b)</li>
<li>uni04E4.ss07 (component N)</li>
<li>uni04ED.ss07 (component uni0454)</li>
<li>uni1FD2.ss07 (component dieresistonos.ss07)</li>
<li>uni1FE2.ss07 (component dieresistonos.ss07)</li>
<li>uni204F.ss07 (component comma.ss07)</li>
<li>uni204F.ss07 (component period.ss07)</li>
<li>uni1FED.ss07 (component dieresistonos.ss07)</li>
<li>quotereversed.ss08 (component comma.ss07)</li>
<li>quotedblreversed.ss08 (component comma.ss07)</li>
<li>quotedblreversed.ss08 (component comma.ss07)</li>
<li>uni0190 (component three)</li>
<li>uni0252 (component a.1)</li>
<li>uni04ED (component uni0454)</li>
<li>uni03FD (component C)</li>
<li>uni03FF (component C)</li>
<li>uni037B (component c)</li>
<li>uni217E (component b)</li>
<li>uni204F (component quoteright)</li>
<li>uni204F (component period)</li>
<li>uni02F6 (component uni030F)</li>
<li>uni1FBF (component uni1FFE)</li>
<li>uni1FBD (component uni1FFE)</li>
<li>uni1FCD (component uni1FFE)</li>
<li>uni1FCD (component tonos.top)</li>
<li>uni1FDD (component tonos.top)</li>
<li>uni1FCE (component uni1FFE)</li>
<li>uni1FCF (component uni1FFE)</li>
<li>uni1FED (component dieresistonos)</li>
<li>uni1FEF (component tonos.top)</li>
<li>acutedblcomb (component uni030F)</li>
<li>brevegravecomb.cn (component uni0306)</li>
<li>brevegravecomb.cn (component acute_compact)</li>
<li>uni1FCD.tonos (component uni1FFE)</li>
<li>uni1FCD.tonos (component tonos.top)</li>
<li>uni1FDD.tonos (component tonos.top)</li>
<li>uni1FCE.tonos (component uni1FFE)</li>
<li>uni1FCF.tonos (component uni1FFE)</li>
<li>uni1FEF.tonos (component tonos.top)</li>
<li>koronisaccentleft.cn (component uni1FFE)</li>
</ul>
 [code: transformed-components]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Check mark characters are in GDEF mark glyph class. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/opentype.html#opentype-gdef-mark-chars">opentype/gdef_mark_chars</a></summary>
    <div>


> 
> Mark characters should be in the GDEF mark glyph class.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/2877





* ⚠️ **WARN** <p>The following mark characters could be in the GDEF mark glyph class:
uni0488 (U+0488), uni0489 (U+0489), uni20DD (U+20DD) and uni20DE (U+20DE)</p>
 [code: mark-chars]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Check if each glyph has the recommended amount of contours. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#contour-count">contour_count</a></summary>
    <div>


> 
> Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only
> be constructured in a handful of ways. This means a glyph's contour count
> will only differ slightly amongst different fonts, e.g a 'g' could either
> be 2 or 3 contours, depending on whether its double story or single story.
> 
> However, a quotedbl should have 2 contours, unless the font belongs
> to a display family.
> 
> This check currently does not cover variable fonts because there's plenty
> of alternative ways of constructing glyphs with multiple outlines for each
> feature in a VarFont. The expected contour count data for this check is
> currently optimized for the typical construction of glyphs in static fonts.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/4829





* ⚠️ **WARN** <p>This check inspects the glyph outlines and detects the total number of contours in each of them. The expected values are infered from the typical ammounts of contours observed in a large collection of reference font families. The divergences listed below may simply indicate a significantly different design on some of your glyphs. On the other hand, some of these may flag actual bugs in the font such as glyphs mapped to an incorrect codepoint. Please consider reviewing the design and codepoint assignment of these to make sure they are correct.</p>
<p>The following glyphs do not have the recommended number of contours:</p>
<pre><code>- Glyph name: Eth	Contours detected: 3	Expected: 2

- Glyph name: aogonek	Contours detected: 3	Expected: 2

- Glyph name: Dcroat	Contours detected: 3	Expected: 2

- Glyph name: dcroat	Contours detected: 3	Expected: 2

- Glyph name: eogonek	Contours detected: 3	Expected: 2

- Glyph name: hbar	Contours detected: 2	Expected: 1

- Glyph name: Lslash	Contours detected: 2	Expected: 1

- Glyph name: lslash	Contours detected: 2	Expected: 1

- Glyph name: oe	Contours detected: 4	Expected: 3

- Glyph name: Tbar	Contours detected: 2	Expected: 1

- 103 more.
</code></pre>
<p>Use -F or --full-lists to disable shortening of long lists.</p>
 [code: contour-count]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Check font contains no unreachable glyphs <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#unreachable-glyphs">unreachable_glyphs</a></summary>
    <div>


> 
> Glyphs are either accessible directly through Unicode codepoints or through
> substitution rules.
> 
> In Color Fonts, glyphs are also referenced by the COLR table. And mathematical
> fonts also reference glyphs via the MATH table.
> 
> Any glyphs not accessible by these means are redundant and serve only
> to increase the font's file size.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/3160





* ⚠️ **WARN** <p>The following glyphs could not be reached by codepoint or substitution rules:</p>
<pre><code>- _part.t_base

- _part.tcurl_base

- _tildecross.cn

- aturn.1

- breveacutecomb.cn

- brevegravecomb.cn

- circumflexacutecomb.cn

- circumflexgravecomb.cn

- circumflexhookcomb.cn

- circumflextildecomb.cn

- 7 more.
</code></pre>
<p>Use -F or --full-lists to disable shortening of long lists.</p>
 [code: unreachable-glyphs]



</div>
</details>
</div>
</details>

<details><summary>[9] Inter-Medium.ttf</summary>
<div>
<details>
    <summary>🔥 <b>FAIL</b> Check base characters have non-zero advance width. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#base-has-width">base_has_width</a></summary>
    <div>


> 
> Base characters should have non-zero advance width.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/4906





* 🔥 **FAIL** <p>The following glyphs had zero advance width:
- uni0488 (U+0488)</p>
<pre><code>- uni0489 (U+0489)
</code></pre>
 [code: zero-width-bases]



</div>
</details>

<details>
    <summary>🔥 <b>FAIL</b> Ensure the font supports case swapping for all its glyphs. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#case-mapping">case_mapping</a></summary>
    <div>


> 
> Ensure that no glyph lacks its corresponding upper or lower counterpart
> (but only when unicode supports case-mapping).
> 




> Original proposal: https://github.com/googlefonts/fontbakery/issues/3230





* 🔥 **FAIL** <p>The following glyphs lack their case-swapping counterparts:</p>
<table>
<thead>
<tr>
<th align="left">Glyph present in the font</th>
<th align="left">Missing case-swapping counterpart</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left">U+019B: LATIN SMALL LETTER LAMBDA WITH STROKE</td>
<td align="left">U+A7DC: LATIN CAPITAL LETTER LAMBDA WITH STROKE</td>
</tr>
<tr>
<td align="left">U+01C6: LATIN SMALL LETTER DZ WITH CARON</td>
<td align="left">U+01C4: LATIN CAPITAL LETTER DZ WITH CARON</td>
</tr>
<tr>
<td align="left">U+023A: LATIN CAPITAL LETTER A WITH STROKE</td>
<td align="left">U+2C65: LATIN SMALL LETTER A WITH STROKE</td>
</tr>
<tr>
<td align="left">U+023E: LATIN CAPITAL LETTER T WITH DIAGONAL STROKE</td>
<td align="left">U+2C66: LATIN SMALL LETTER T WITH DIAGONAL STROKE</td>
</tr>
<tr>
<td align="left">U+0264: LATIN SMALL LETTER RAMS HORN</td>
<td align="left">U+A7CB: LATIN CAPITAL LETTER RAMS HORN</td>
</tr>
<tr>
<td align="left">U+0265: LATIN SMALL LETTER TURNED H</td>
<td align="left">U+A78D: LATIN CAPITAL LETTER TURNED H</td>
</tr>
<tr>
<td align="left">U+0266: LATIN SMALL LETTER H WITH HOOK</td>
<td align="left">U+A7AA: LATIN CAPITAL LETTER H WITH HOOK</td>
</tr>
<tr>
<td align="left">U+026A: LATIN LETTER SMALL CAPITAL I</td>
<td align="left">U+A7AE: LATIN CAPITAL LETTER SMALL CAPITAL I</td>
</tr>
<tr>
<td align="left">U+026C: LATIN SMALL LETTER L WITH BELT</td>
<td align="left">U+A7AD: LATIN CAPITAL LETTER L WITH BELT</td>
</tr>
<tr>
<td align="left">U+029D: LATIN SMALL LETTER J WITH CROSSED-TAIL</td>
<td align="left">U+A7B2: LATIN CAPITAL LETTER J WITH CROSSED-TAIL</td>
</tr>
<tr>
<td align="left">U+0376: GREEK CAPITAL LETTER PAMPHYLIAN DIGAMMA</td>
<td align="left">U+0377: GREEK SMALL LETTER PAMPHYLIAN DIGAMMA</td>
</tr>
<tr>
<td align="left">U+03FA: GREEK CAPITAL LETTER SAN</td>
<td align="left">U+03FB: GREEK SMALL LETTER SAN</td>
</tr>
<tr>
<td align="left">U+052F: CYRILLIC SMALL LETTER EL WITH DESCENDER</td>
<td align="left">U+052E: CYRILLIC CAPITAL LETTER EL WITH DESCENDER</td>
</tr>
<tr>
<td align="left">U+2132: TURNED CAPITAL F</td>
<td align="left">U+214E: TURNED SMALL F</td>
</tr>
</tbody>
</table>
 [code: missing-case-counterparts]



</div>
</details>

<details>
    <summary>🔥 <b>FAIL</b> Checking OS/2 usWinAscent & usWinDescent. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#family-win-ascent-and-descent">family/win_ascent_and_descent</a></summary>
    <div>


> 
> A font's winAscent and winDescent values should be greater than or equal to
> the head table's yMax, abs(yMin) values. If they are less than these values,
> clipping can occur on Windows platforms
> (https://github.com/RedHatBrand/Overpass/issues/33).
> 
> If the font includes tall/deep writing systems such as Arabic or Devanagari,
> the winAscent and winDescent can be greater than the yMax and absolute yMin
> values to accommodate vowel marks.
> 
> When the 'win' Metrics are significantly greater than the UPM, the linespacing
> can appear too loose. To counteract this, enabling the OS/2 fsSelection
> bit 7 (Use_Typo_Metrics), will force Windows to use the OS/2 'typo' values
> instead. This means the font developer can control the linespacing with
> the 'typo' values, whilst avoiding clipping by setting the 'win' values to
> values greater than the yMax and absolute yMin.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/4829





* 🔥 **FAIL** <p>OS/2.usWinAscent value should be equal or greater than 2272, but got 1984 instead</p>
 [code: ascent]



* 🔥 **FAIL** <p>OS/2.usWinDescent value should be equal or greater than 668, but got 494 instead</p>
 [code: descent]



</div>
</details>

<details>
    <summary>🔥 <b>FAIL</b> Ensure smart dropout control is enabled in "prep" table instructions. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#smart-dropout">smart_dropout</a></summary>
    <div>


> 
> This setup is meant to ensure consistent rendering quality for fonts across
> all devices (with different rendering/hinting capabilities).
> 
> Below is the snippet of instructions we expect to see in the fonts:
> B8 01 FF    PUSHW 0x01FF
> 85          SCANCTRL (unconditinally turn on
> dropout control mode)
> B0 04       PUSHB 0x04
> 8D          SCANTYPE (enable smart dropout control)
> 
> "Smart dropout control" means activating rules 1, 2 and 5:
> Rule 1: If a pixel's center falls within the glyph outline,
> that pixel is turned on.
> Rule 2: If a contour falls exactly on a pixel's center,
> that pixel is turned on.
> Rule 5: If a scan line between two adjacent pixel centers
> (either vertical or horizontal) is intersected
> by both an on-Transition contour and an off-Transition
> contour and neither of the pixels was already turned on
> by rules 1 and 2, turn on the pixel which is closer to
> the midpoint between the on-Transition contour and
> off-Transition contour. This is "Smart" dropout control.
> 
> For more detailed info (such as other rules not enabled in this snippet),
> please refer to the TrueType Instruction Set documentation.
> 
> Generally this occurs with unhinted fonts; if you are not using autohinting,
> use gftools-fix-nonhinting (or just gftools-fix-font) to fix this issue.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/4829





* 🔥 **FAIL** <p>The 'prep' table does not contain TrueType instructions enabling smart dropout control. To fix, export the font with autohinting enabled, or run ttfautohint on the font, or run the <code>gftools fix-nonhinting</code> script.</p>
 [code: lacks-smart-dropout]



</div>
</details>

<details>
    <summary>🔥 <b>FAIL</b> Ensure component transforms do not perform scaling or rotation. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#transformed-components">transformed_components</a></summary>
    <div>


> 
> Some families have glyphs which have been constructed by using
> transformed components e.g the 'u' being constructed from a flipped 'n'.
> 
> From a designers point of view, this sounds like a win (less work).
> However, such approaches can lead to rasterization issues, such as
> having the 'u' not sitting on the baseline at certain sizes after
> running the font through ttfautohint.
> 
> Other issues are outlines that end up reversed when only one dimension
> is flipped while the other isn't.
> 
> As of July 2019, Marc Foley observed that ttfautohint assigns cvt values
> to transformed glyphs as if they are not transformed and the result is
> they render very badly, and that vttLib does not support flipped components.
> 
> When building the font with fontmake, the problem can be fixed by adding
> this to the command line:
> 
> --filter DecomposeTransformedComponentsFilter
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/2011





* 🔥 **FAIL** <p>The following glyphs had components with scaling or rotation
or inverted outline direction:</p>
<ul>
<li>uni1EB0 (component uni0306)</li>
<li>uni1EB0 (component acute_compact)</li>
<li>uni1F08 (component uni1FFE)</li>
<li>uni1F0A (component uni1FFE)</li>
<li>uni1F0A (component tonos.top)</li>
<li>uni1F0B (component tonos.top)</li>
<li>uni1F0C (component uni1FFE)</li>
<li>uni1F0E (component uni1FFE)</li>
<li>uni1FBA (component tonos.top)</li>
<li>uni1F88 (component uni1FFE)</li>
<li>uni1F8A (component uni1FFE)</li>
<li>uni1F8A (component tonos.top)</li>
<li>uni1F8B (component tonos.top)</li>
<li>uni1F8C (component uni1FFE)</li>
<li>uni1F8E (component uni1FFE)</li>
<li>uni1F18 (component uni1FFE)</li>
<li>uni1F1A (component uni1FFE)</li>
<li>uni1F1A (component tonos.top)</li>
<li>uni1F1B (component tonos.top)</li>
<li>uni1F1C (component uni1FFE)</li>
<li>uni1FC8 (component tonos.top)</li>
<li>uni1F28 (component uni1FFE)</li>
<li>uni1F2A (component uni1FFE)</li>
<li>uni1F2A (component tonos.top)</li>
<li>uni1F2B (component tonos.top)</li>
<li>uni1F2C (component uni1FFE)</li>
<li>uni1F2E (component uni1FFE)</li>
<li>uni1FCA (component tonos.top)</li>
<li>uni1F98 (component uni1FFE)</li>
<li>uni1F9A (component uni1FFE)</li>
<li>uni1F9A (component tonos.top)</li>
<li>uni1F9B (component tonos.top)</li>
<li>uni1F9C (component uni1FFE)</li>
<li>uni1F9E (component uni1FFE)</li>
<li>uni1F38 (component uni1FFE)</li>
<li>uni1F3A (component uni1FFE)</li>
<li>uni1F3A (component tonos.top)</li>
<li>uni1F3B (component tonos.top)</li>
<li>uni1F3C (component uni1FFE)</li>
<li>uni1F3E (component uni1FFE)</li>
<li>uni1FDA (component tonos.top)</li>
<li>uni1F38.1 (component uni1FFE)</li>
<li>uni1F3A.1 (component uni1FFE)</li>
<li>uni1F3A.1 (component tonos.top)</li>
<li>uni1F3B.1 (component tonos.top)</li>
<li>uni1F3C.1 (component uni1FFE)</li>
<li>uni1F3E.1 (component uni1FFE)</li>
<li>uni1FDA.1 (component tonos.top)</li>
<li>uni0418 (component N)</li>
<li>uni040D (component N)</li>
<li>uni0419 (component N)</li>
<li>uni04E2 (component N)</li>
<li>uni04E4 (component N)</li>
<li>uni048A (component N)</li>
<li>uni0376 (component N)</li>
<li>Ohungarumlaut (component uni030F)</li>
<li>uni1F48 (component uni1FFE)</li>
<li>uni1F4A (component uni1FFE)</li>
<li>uni1F4A (component tonos.top)</li>
<li>uni1F4B (component tonos.top)</li>
<li>uni1F4C (component uni1FFE)</li>
<li>uni1FF8 (component tonos.top)</li>
<li>uni01A7 (component S)</li>
<li>Uhungarumlaut (component uni030F)</li>
<li>uni1F5B (component tonos.top)</li>
<li>uni1FEA (component tonos.top)</li>
<li>uni1EB1 (component uni0306)</li>
<li>uni1EB1 (component acute_compact)</li>
<li>uni1EB1.1 (component uni0306)</li>
<li>uni1EB1.1 (component acute_compact)</li>
<li>uni1EB1.2 (component uni0306)</li>
<li>uni1EB1.2 (component acute_compact)</li>
<li>d (component b)</li>
<li>dcroat (component b)</li>
<li>dcaron (component b)</li>
<li>uni1E0B (component b)</li>
<li>uni1E0D (component b)</li>
<li>uni1E0F (component b)</li>
<li>uni1E11 (component b)</li>
<li>uni1E13 (component b)</li>
<li>uni01F3 (component b)</li>
<li>uni01C6 (component b)</li>
<li>dong (component b)</li>
<li>ohungarumlaut (component uni030F)</li>
<li>uni1F40 (component uni1FFE)</li>
<li>uni1F42 (component uni1FFE)</li>
<li>uni1F42 (component tonos.top)</li>
<li>uni1F43 (component tonos.top)</li>
<li>uni1F44 (component uni1FFE)</li>
<li>uni1F78 (component tonos.top)</li>
<li>q (component p)</li>
<li>uni027F (component uni027E)</li>
<li>uhungarumlaut (component uni030F)</li>
<li>uhungarumlaut.1 (component uni030F)</li>
<li>uni04F3 (component uni030F)</li>
<li>uni04F2 (component uni030F)</li>
<li>uni1F68 (component uni1FFE)</li>
<li>uni1F6A (component uni1FFE)</li>
<li>uni1F6A (component tonos.top)</li>
<li>uni1F6B (component tonos.top)</li>
<li>uni1F6C (component uni1FFE)</li>
<li>uni1F6E (component uni1FFE)</li>
<li>uni1FFA (component tonos.top)</li>
<li>uni1FA8 (component uni1FFE)</li>
<li>uni1FAA (component uni1FFE)</li>
<li>uni1FAA (component tonos.top)</li>
<li>uni1FAB (component tonos.top)</li>
<li>uni1FAC (component uni1FFE)</li>
<li>uni1FAE (component uni1FFE)</li>
<li>uni042F (component R)</li>
<li>uni1F00 (component uni1FFE)</li>
<li>uni1F02 (component uni1FFE)</li>
<li>uni1F02 (component tonos.top)</li>
<li>uni1F03 (component tonos.top)</li>
<li>uni1F04 (component uni1FFE)</li>
<li>uni1F06 (component uni1FFE)</li>
<li>uni1F70 (component tonos.top)</li>
<li>uni1F80 (component uni1FFE)</li>
<li>uni1F82 (component uni1FFE)</li>
<li>uni1F82 (component tonos.top)</li>
<li>uni1F83 (component tonos.top)</li>
<li>uni1F84 (component uni1FFE)</li>
<li>uni1F86 (component uni1FFE)</li>
<li>uni1FB2 (component tonos.top)</li>
<li>uni025C (component epsilon)</li>
<li>uni025E (component uni029A)</li>
<li>uni1F10 (component uni1FFE)</li>
<li>uni1F12 (component uni1FFE)</li>
<li>uni1F12 (component tonos.top)</li>
<li>uni1F13 (component tonos.top)</li>
<li>uni1F14 (component uni1FFE)</li>
<li>uni1F72 (component tonos.top)</li>
<li>uni1F20 (component uni1FFE)</li>
<li>uni1F22 (component uni1FFE)</li>
<li>uni1F22 (component tonos.top)</li>
<li>uni1F23 (component tonos.top)</li>
<li>uni1F24 (component uni1FFE)</li>
<li>uni1F26 (component uni1FFE)</li>
<li>uni1F74 (component tonos.top)</li>
<li>uni1F90 (component uni1FFE)</li>
<li>uni1F92 (component uni1FFE)</li>
<li>uni1F92 (component tonos.top)</li>
<li>uni1F93 (component tonos.top)</li>
<li>uni1F94 (component uni1FFE)</li>
<li>uni1F96 (component uni1FFE)</li>
<li>uni1FC2 (component tonos.top)</li>
<li>uni1F30 (component uni1FFE)</li>
<li>uni1F32 (component uni1FFE)</li>
<li>uni1F32 (component tonos.top)</li>
<li>uni1F33 (component tonos.top)</li>
<li>uni1F34 (component uni1FFE)</li>
<li>uni1F36 (component uni1FFE)</li>
<li>uni1F76 (component tonos.top)</li>
<li>uni1FD2 (component dieresistonos)</li>
<li>uni1FE4 (component uni1FFE)</li>
<li>uni1F50 (component uni1FFE)</li>
<li>uni1F52 (component uni1FFE)</li>
<li>uni1F52 (component tonos.top)</li>
<li>uni1F53 (component tonos.top)</li>
<li>uni1F54 (component uni1FFE)</li>
<li>uni1F56 (component uni1FFE)</li>
<li>uni1F7A (component tonos.top)</li>
<li>uni1FE2 (component dieresistonos)</li>
<li>uni1F60 (component uni1FFE)</li>
<li>uni1F62 (component uni1FFE)</li>
<li>uni1F62 (component tonos.top)</li>
<li>uni1F63 (component tonos.top)</li>
<li>uni1F64 (component uni1FFE)</li>
<li>uni1F66 (component uni1FFE)</li>
<li>uni1F7C (component tonos.top)</li>
<li>uni1FA0 (component uni1FFE)</li>
<li>uni1FA2 (component uni1FFE)</li>
<li>uni1FA2 (component tonos.top)</li>
<li>uni1FA3 (component tonos.top)</li>
<li>uni1FA4 (component uni1FFE)</li>
<li>uni1FA6 (component uni1FFE)</li>
<li>uni1FF2 (component tonos.top)</li>
<li>uni044D (component uni0454)</li>
<li>uni044F (component uni0280)</li>
<li>quotereversed (component quoteright)</li>
<li>uni201F (component quoteright)</li>
<li>uni201F (component quoteright)</li>
<li>uni204B (component paragraph)</li>
<li>hungarumlaut (component uni030F)</li>
<li>arrowright (component arrowleft)</li>
<li>uni27F6 (component uni27F5)</li>
<li>uni2197 (component uni2196)</li>
<li>uni2199 (component uni2196)</li>
<li>uni21AA (component uni21A9)</li>
<li>arrowright.case (component arrowleft)</li>
<li>uni27F6.case (component uni27F5)</li>
<li>uni2197.case (component uni2196)</li>
<li>uni2199.case (component uni2196)</li>
<li>arrowright.circled (component arrowleft)</li>
<li>arrowright.squared (component arrowleft)</li>
<li>uni204F.ss03 (component quoteright.ss03)</li>
<li>uni204F.ss03 (component period)</li>
<li>quotereversed.ss03 (component quoteright.ss03)</li>
<li>quotedblreversed.ss03 (component quoteright.ss03)</li>
<li>quotedblreversed.ss03 (component quoteright.ss03)</li>
<li>uni1E0B.ss07 (component b)</li>
<li>uni1E0D.ss07 (component b)</li>
<li>uni04E4.ss07 (component N)</li>
<li>uni04ED.ss07 (component uni0454)</li>
<li>uni1FD2.ss07 (component dieresistonos.ss07)</li>
<li>uni1FE2.ss07 (component dieresistonos.ss07)</li>
<li>uni204F.ss07 (component comma.ss07)</li>
<li>uni204F.ss07 (component period.ss07)</li>
<li>uni1FED.ss07 (component dieresistonos.ss07)</li>
<li>quotereversed.ss08 (component comma.ss07)</li>
<li>quotedblreversed.ss08 (component comma.ss07)</li>
<li>quotedblreversed.ss08 (component comma.ss07)</li>
<li>uni0190 (component three)</li>
<li>uni0252 (component a.1)</li>
<li>uni04ED (component uni0454)</li>
<li>uni03FD (component C)</li>
<li>uni03FF (component C)</li>
<li>uni037B (component c)</li>
<li>uni217E (component b)</li>
<li>uni204F (component quoteright)</li>
<li>uni204F (component period)</li>
<li>uni02F6 (component uni030F)</li>
<li>uni1FBF (component uni1FFE)</li>
<li>uni1FBD (component uni1FFE)</li>
<li>uni1FCD (component uni1FFE)</li>
<li>uni1FCD (component tonos.top)</li>
<li>uni1FDD (component tonos.top)</li>
<li>uni1FCE (component uni1FFE)</li>
<li>uni1FCF (component uni1FFE)</li>
<li>uni1FED (component dieresistonos)</li>
<li>uni1FEF (component tonos.top)</li>
<li>acutedblcomb (component uni030F)</li>
<li>brevegravecomb.cn (component uni0306)</li>
<li>brevegravecomb.cn (component acute_compact)</li>
<li>uni1FCD.tonos (component uni1FFE)</li>
<li>uni1FCD.tonos (component tonos.top)</li>
<li>uni1FDD.tonos (component tonos.top)</li>
<li>uni1FCE.tonos (component uni1FFE)</li>
<li>uni1FCF.tonos (component uni1FFE)</li>
<li>uni1FEF.tonos (component tonos.top)</li>
<li>koronisaccentleft.cn (component uni1FFE)</li>
</ul>
 [code: transformed-components]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Check mark characters are in GDEF mark glyph class. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/opentype.html#opentype-gdef-mark-chars">opentype/gdef_mark_chars</a></summary>
    <div>


> 
> Mark characters should be in the GDEF mark glyph class.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/2877





* ⚠️ **WARN** <p>The following mark characters could be in the GDEF mark glyph class:
uni0488 (U+0488), uni0489 (U+0489), uni20DD (U+20DD) and uni20DE (U+20DE)</p>
 [code: mark-chars]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Check if each glyph has the recommended amount of contours. <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#contour-count">contour_count</a></summary>
    <div>


> 
> Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only
> be constructured in a handful of ways. This means a glyph's contour count
> will only differ slightly amongst different fonts, e.g a 'g' could either
> be 2 or 3 contours, depending on whether its double story or single story.
> 
> However, a quotedbl should have 2 contours, unless the font belongs
> to a display family.
> 
> This check currently does not cover variable fonts because there's plenty
> of alternative ways of constructing glyphs with multiple outlines for each
> feature in a VarFont. The expected contour count data for this check is
> currently optimized for the typical construction of glyphs in static fonts.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/4829





* ⚠️ **WARN** <p>This check inspects the glyph outlines and detects the total number of contours in each of them. The expected values are infered from the typical ammounts of contours observed in a large collection of reference font families. The divergences listed below may simply indicate a significantly different design on some of your glyphs. On the other hand, some of these may flag actual bugs in the font such as glyphs mapped to an incorrect codepoint. Please consider reviewing the design and codepoint assignment of these to make sure they are correct.</p>
<p>The following glyphs do not have the recommended number of contours:</p>
<pre><code>- Glyph name: Eth	Contours detected: 3	Expected: 2

- Glyph name: aogonek	Contours detected: 3	Expected: 2

- Glyph name: Dcroat	Contours detected: 3	Expected: 2

- Glyph name: dcroat	Contours detected: 3	Expected: 2

- Glyph name: eogonek	Contours detected: 3	Expected: 2

- Glyph name: hbar	Contours detected: 2	Expected: 1

- Glyph name: Lslash	Contours detected: 2	Expected: 1

- Glyph name: lslash	Contours detected: 2	Expected: 1

- Glyph name: oe	Contours detected: 4	Expected: 3

- Glyph name: Tbar	Contours detected: 2	Expected: 1

- 103 more.
</code></pre>
<p>Use -F or --full-lists to disable shortening of long lists.</p>
 [code: contour-count]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Check there are no overlapping path segments <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#overlapping-path-segments">overlapping_path_segments</a></summary>
    <div>


> 
> Some rasterizers encounter difficulties when rendering glyphs with
> overlapping path segments.
> 
> A path segment is a section of a path defined by two on-curve points.
> When two segments share the same coordinates, they are considered
> overlapping.
> 




> Original proposal: https://github.com/google/fonts/issues/7594#issuecomment-2401909084





* ⚠️ **WARN** <p>The following glyphs have overlapping path segments:</p>
<pre><code>* Ohorn (U+01A0): B&lt;&lt;786.0,1510.0&gt;-&lt;786.0,1510.0&gt;-&lt;786.0,1510.0&gt;&gt; has the same coordinates as a previous segment.

* uni1EDA (U+1EDA): B&lt;&lt;786.0,1510.0&gt;-&lt;786.0,1510.0&gt;-&lt;786.0,1510.0&gt;&gt; has the same coordinates as a previous segment.

* uni1EDC (U+1EDC): B&lt;&lt;786.0,1510.0&gt;-&lt;786.0,1510.0&gt;-&lt;786.0,1510.0&gt;&gt; has the same coordinates as a previous segment.

* uni1EDE (U+1EDE): B&lt;&lt;786.0,1510.0&gt;-&lt;786.0,1510.0&gt;-&lt;786.0,1510.0&gt;&gt; has the same coordinates as a previous segment.

* uni1EE0 (U+1EE0): B&lt;&lt;786.0,1510.0&gt;-&lt;786.0,1510.0&gt;-&lt;786.0,1510.0&gt;&gt; has the same coordinates as a previous segment.

* uni1EE2 (U+1EE2): B&lt;&lt;786.0,1510.0&gt;-&lt;786.0,1510.0&gt;-&lt;786.0,1510.0&gt;&gt; has the same coordinates as a previous segment.

* uni1EE2.ss07 (U+E206): B&lt;&lt;786.0,1510.0&gt;-&lt;786.0,1510.0&gt;-&lt;786.0,1510.0&gt;&gt; has the same coordinates as a previous segment.
</code></pre>
 [code: overlapping-path-segments]



</div>
</details>

<details>
    <summary>⚠️ <b>WARN</b> Check font contains no unreachable glyphs <a href="https://fontbakery.readthedocs.io/en/stable/fontbakery/checks/universal.html#unreachable-glyphs">unreachable_glyphs</a></summary>
    <div>


> 
> Glyphs are either accessible directly through Unicode codepoints or through
> substitution rules.
> 
> In Color Fonts, glyphs are also referenced by the COLR table. And mathematical
> fonts also reference glyphs via the MATH table.
> 
> Any glyphs not accessible by these means are redundant and serve only
> to increase the font's file size.
> 




> Original proposal: https://github.com/fonttools/fontbakery/issues/3160





* ⚠️ **WARN** <p>The following glyphs could not be reached by codepoint or substitution rules:</p>
<pre><code>- _part.t_base

- _part.tcurl_base

- _tildecross.cn

- aturn.1

- breveacutecomb.cn

- brevegravecomb.cn

- circumflexacutecomb.cn

- circumflexgravecomb.cn

- circumflexhookcomb.cn

- circumflextildecomb.cn

- 7 more.
</code></pre>
<p>Use -F or --full-lists to disable shortening of long lists.</p>
 [code: unreachable-glyphs]



</div>
</details>
</div>
</details>




### Summary

| 💥 ERROR | ☠ FATAL | 🔥 FAIL | ⚠️ WARN | ⏩ SKIP | ℹ️ INFO | ✅ PASS | 🔎 DEBUG | 
| ---|---|---|---|---|---|---|---|
| 0 | 0 | 11 | 7 | 74 | 8 | 142 | 0 | 
| 0% | 0% | 5% | 3% | 31% | 3% | 59% | 0% | 



**Note:** The following loglevels were omitted in this report:


* SKIP
* INFO
* PASS
* DEBUG
