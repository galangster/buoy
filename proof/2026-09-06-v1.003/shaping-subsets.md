# Shaping proofs, Buoy v1.003

Every row is `hb-shape` output, not a table read.

## Buoy-Medium-from-woff2.ttf (expanded from woff2: this harfbuzz build cannot open a woff2 face)

| case | result | expectation | hb-shape |
| --- | --- | --- | --- |
| `kern on/off "AVATAR To Wa."` | **PASS** | +kern [gid2=0+1305|gid217=1+1305|gid2=2+1275|gid191=3+1160|gid2=4+1452|gid172=5+1327|gid776=6+546|gid191=7+1177|gid371=8+1237|gid776=9+546|gid220=10+1945|gid247=11+1163|gid650=12+621] | `-kern [gid2=0+1452|gid217=1+1452|gid2=2+1452|gid191=3+1337|gid2=4+1452|gid172=5+1327|gid776=6+546|gid191=7+1337|gid371=8+1237|gid776=9+546|gid220=10+2054|gid247=11+1163|gid650=12+621]` |
| `NFC/NFD café` | **PASS** | canonical equivalents produce the same glyph run | `NFC [gid270=0+1202|gid247=1+1159|gid299=2+722|gid286=3+1203]; NFD [gid270=0+1202|gid247=1+1159|gid299=2+722|gid286=3+1203]` |
| `NFC/NFD double acute` | **PASS** | canonical equivalents produce the same glyph run | `NFC [gid148=0+1570]; NFD [gid148=0+1570]` |
| `canonical pair "Ω Ω"` | **PASS** | both codepoints map and have the same advance | `OHM [gid482=0+1585]; OMEGA [gid482=0+1585]` |
| `+ccmp "i͗"` | **PASS** | dotless i substitution before an above mark | `on [gid319=0+516|gid944=0@-405,0+0]; off [gid318=0+516|gid944=0@-405,432+0]` |
| `+mark "q́"` | **PASS** | base-to-mark attachment changes the mark offset | `on [gid392=0+1266|gid769=0@-893,0+0]; off [gid392=0+1266|gid769=0+0]` |
| `+mkmk "q́̈"` | **PASS** | mark-to-mark attachment stacks the second mark | `on [gid392=0+1266|gid769=0@-893,0+0|gid912=0@-1252,444+0]; off [gid392=0+1266|gid769=0@-893,0+0|gid912=0@-1252,0+0]` |
| `+tnum --show-extents "0123456789"` | **PASS** | one advance for all ten digits, equal to the tabular four `gid530` (1327) | `[gid526=0+1327<125,1510,1076,-1530>|gid527=1+1327<209,1490,950,-1490>|gid528=2+1327<173,1510,984,-1510>|gid529=3+1327<136,1510,1050,-1530>|gid530=4+1327<103,1490,1120,-1490>|gid531=5+1327<162,1490,1000,-1510>|gid532=6+13` |
| `+zero "0"` | **PASS** | differs from the default `[gid514=0+1322]` | `[gid524=0+1322]` |
| `+ss02 "Il1O0"` | **PASS** | differs from the default `[gid83=0+558|gid344=1+516|gid515=2+850|gid139=3+1570|gid514=4+1322]` | `[gid98=0+927|gid351=1+587|gid515=2+850|gid139=3+1570|gid524=4+1322]` |
| `+cv02 "4"` | **PASS** | differs from the default `[gid518=0+1344]` | `[gid525=0+1344]` |
| `+cv06 "u"` | **PASS** | differs from the default `[gid418=0+1232]` | `[gid434=0+1232]` |
| `+ss03 ",;'"` | **PASS** | differs from the default `[gid649=0+621|gid655=1+621|gid634=2+641]` | `[gid852=0+621|gid853=1+646|gid634=2+641]` |
| `+frac "21/64"` | **PASS** | differs from the default `[gid516=0+1263|gid515=1+850|gid609=2+757|gid520=3+1290|gid518=4+1344]` | `[gid736=0+756|gid735=1+597|gid712=2+406|gid721=3+787|gid718=4+806]` |
| `-calt "==>"` | **PASS** | differs from the default `[gid806=0+2746]` | `[gid663=0+1367|gid663=1+1367|gid662=2+1367]` |
| `+case "(A)" against `-calt`` | **PASS** | differs from the default `[gid591=0+755|gid2=1+1452|gid592=2+755]` | `[gid600=0+755|gid2=1+1452|gid601=2+755]` |
| `default "4 u ,"` | **PASS** | each promoted default still has a reachable reverse toggle | `[gid518=0+1344|gid776=1+546|gid418=2+1232|gid776=3+546|gid649=4+621]` |

## Buoy-Regular-from-woff2.ttf (expanded from woff2: this harfbuzz build cannot open a woff2 face)

| case | result | expectation | hb-shape |
| --- | --- | --- | --- |
| `kern on/off "AVATAR To Wa."` | **PASS** | +kern [gid2=0+1273|gid217=1+1273|gid2=2+1239|gid191=3+1148|gid2=4+1413|gid172=5+1318|gid776=6+576|gid191=7+1162|gid371=8+1228|gid776=9+576|gid220=10+1914|gid247=11+1150|gid650=12+590] | `-kern [gid2=0+1413|gid217=1+1413|gid2=2+1413|gid191=3+1322|gid2=4+1413|gid172=5+1318|gid776=6+576|gid191=7+1322|gid371=8+1228|gid776=9+576|gid220=10+2018|gid247=11+1150|gid650=12+590]` |
| `NFC/NFD café` | **PASS** | canonical equivalents produce the same glyph run | `NFC [gid270=0+1190|gid247=1+1150|gid299=2+698|gid286=3+1194]; NFD [gid270=0+1190|gid247=1+1150|gid299=2+698|gid286=3+1194]` |
| `NFC/NFD double acute` | **PASS** | canonical equivalents produce the same glyph run | `NFC [gid148=0+1566]; NFD [gid148=0+1566]` |
| `canonical pair "Ω Ω"` | **PASS** | both codepoints map and have the same advance | `OHM [gid482=0+1577]; OMEGA [gid482=0+1577]` |
| `+ccmp "i͗"` | **PASS** | dotless i substitution before an above mark | `on [gid319=0+496|gid944=0@-394,0+0]; off [gid318=0+496|gid944=0@-394,421+0]` |
| `+mark "q́"` | **PASS** | base-to-mark attachment changes the mark offset | `on [gid392=0+1254|gid769=0@-878,0+0]; off [gid392=0+1254|gid769=0+0]` |
| `+mkmk "q́̈"` | **PASS** | mark-to-mark attachment stacks the second mark | `on [gid392=0+1254|gid769=0@-878,0+0|gid912=0@-1236,440+0]; off [gid392=0+1254|gid769=0@-878,0+0|gid912=0@-1236,0+0]` |
| `+tnum --show-extents "0123456789"` | **PASS** | one advance for all ten digits, equal to the tabular four `gid530` (1328) | `[gid526=0+1328<142,1510,1044,-1530>|gid527=1+1328<225,1490,921,-1490>|gid528=2+1328<189,1510,949,-1510>|gid529=3+1328<154,1510,1014,-1530>|gid530=4+1328<121,1490,1085,-1490>|gid531=5+1328<182,1490,961,-1510>|gid532=6+132` |
| `+zero "0"` | **PASS** | differs from the default `[gid514=0+1292]` | `[gid524=0+1292]` |
| `+ss02 "Il1O0"` | **PASS** | differs from the default `[gid83=0+550|gid344=1+496|gid515=2+833|gid139=3+1566|gid514=4+1292]` | `[gid98=0+903|gid351=1+564|gid515=2+833|gid139=3+1566|gid524=4+1292]` |
| `+cv02 "4"` | **PASS** | differs from the default `[gid518=0+1323]` | `[gid525=0+1323]` |
| `+cv06 "u"` | **PASS** | differs from the default `[gid418=0+1211]` | `[gid434=0+1211]` |
| `+ss03 ",;'"` | **PASS** | differs from the default `[gid649=0+590|gid655=1+590|gid634=2+614]` | `[gid852=0+590|gid853=1+618|gid634=2+614]` |
| `+frac "21/64"` | **PASS** | differs from the default `[gid516=0+1249|gid515=1+833|gid609=2+738|gid520=3+1270|gid518=4+1323]` | `[gid736=0+753|gid735=1+589|gid712=2+393|gid721=3+780|gid718=4+801]` |
| `-calt "==>"` | **PASS** | differs from the default `[gid806=0+2746]` | `[gid663=0+1355|gid663=1+1355|gid662=2+1355]` |
| `+case "(A)" against `-calt`` | **PASS** | differs from the default `[gid591=0+747|gid2=1+1413|gid592=2+747]` | `[gid600=0+747|gid2=1+1413|gid601=2+747]` |
| `default "4 u ,"` | **PASS** | each promoted default still has a reachable reverse toggle | `[gid518=0+1323|gid776=1+576|gid418=2+1211|gid776=3+576|gid649=4+590]` |

## Buoy-Medium-Latin.ttf

| case | result | expectation | hb-shape |
| --- | --- | --- | --- |
| `kern on/off "AVATAR To Wa."` | **PASS** | +kern [gid2=0+1305|gid217=1+1305|gid2=2+1275|gid191=3+1160|gid2=4+1452|gid172=5+1327|gid776=6+546|gid191=7+1177|gid371=8+1237|gid776=9+546|gid220=10+1945|gid247=11+1163|gid650=12+621] | `-kern [gid2=0+1452|gid217=1+1452|gid2=2+1452|gid191=3+1337|gid2=4+1452|gid172=5+1327|gid776=6+546|gid191=7+1337|gid371=8+1237|gid776=9+546|gid220=10+2054|gid247=11+1163|gid650=12+621]` |
| `NFC/NFD café` | **PASS** | canonical equivalents produce the same glyph run | `NFC [gid270=0+1202|gid247=1+1159|gid299=2+722|gid286=3+1203]; NFD [gid270=0+1202|gid247=1+1159|gid299=2+722|gid286=3+1203]` |
| `NFC/NFD double acute` | **PASS** | canonical equivalents produce the same glyph run | `NFC [gid148=0+1570]; NFD [gid148=0+1570]` |
| `canonical pair "Ω Ω"` | **PASS** | both codepoints map and have the same advance | `OHM [gid482=0+1585]; OMEGA [gid482=0+1585]` |
| `+ccmp "i͗"` | **PASS** | dotless i substitution before an above mark | `on [gid319=0+516|gid944=0@-405,0+0]; off [gid318=0+516|gid944=0@-405,432+0]` |
| `+mark "q́"` | **PASS** | base-to-mark attachment changes the mark offset | `on [gid392=0+1266|gid769=0@-893,0+0]; off [gid392=0+1266|gid769=0+0]` |
| `+mkmk "q́̈"` | **PASS** | mark-to-mark attachment stacks the second mark | `on [gid392=0+1266|gid769=0@-893,0+0|gid912=0@-1252,444+0]; off [gid392=0+1266|gid769=0@-893,0+0|gid912=0@-1252,0+0]` |
| `+tnum --show-extents "0123456789"` | **PASS** | one advance for all ten digits, equal to the tabular four `gid530` (1327) | `[gid526=0+1327<125,1510,1076,-1530>|gid527=1+1327<209,1490,950,-1490>|gid528=2+1327<173,1510,984,-1510>|gid529=3+1327<136,1510,1050,-1530>|gid530=4+1327<103,1490,1120,-1490>|gid531=5+1327<162,1490,1000,-1510>|gid532=6+13` |
| `+zero "0"` | **PASS** | differs from the default `[gid514=0+1322]` | `[gid524=0+1322]` |
| `+ss02 "Il1O0"` | **PASS** | differs from the default `[gid83=0+558|gid344=1+516|gid515=2+850|gid139=3+1570|gid514=4+1322]` | `[gid98=0+927|gid351=1+587|gid515=2+850|gid139=3+1570|gid524=4+1322]` |
| `+cv02 "4"` | **PASS** | differs from the default `[gid518=0+1344]` | `[gid525=0+1344]` |
| `+cv06 "u"` | **PASS** | differs from the default `[gid418=0+1232]` | `[gid434=0+1232]` |
| `+ss03 ",;'"` | **PASS** | differs from the default `[gid649=0+621|gid655=1+621|gid634=2+641]` | `[gid852=0+621|gid853=1+646|gid634=2+641]` |
| `+frac "21/64"` | **PASS** | differs from the default `[gid516=0+1263|gid515=1+850|gid609=2+757|gid520=3+1290|gid518=4+1344]` | `[gid736=0+756|gid735=1+597|gid712=2+406|gid721=3+787|gid718=4+806]` |
| `-calt "==>"` | **PASS** | differs from the default `[gid806=0+2746]` | `[gid663=0+1367|gid663=1+1367|gid662=2+1367]` |
| `+case "(A)" against `-calt`` | **PASS** | differs from the default `[gid591=0+755|gid2=1+1452|gid592=2+755]` | `[gid600=0+755|gid2=1+1452|gid601=2+755]` |
| `default "4 u ,"` | **PASS** | each promoted default still has a reachable reverse toggle | `[gid518=0+1344|gid776=1+546|gid418=2+1232|gid776=3+546|gid649=4+621]` |

## Buoy-Regular-Latin.ttf

| case | result | expectation | hb-shape |
| --- | --- | --- | --- |
| `kern on/off "AVATAR To Wa."` | **PASS** | +kern [gid2=0+1273|gid217=1+1273|gid2=2+1239|gid191=3+1148|gid2=4+1413|gid172=5+1318|gid776=6+576|gid191=7+1162|gid371=8+1228|gid776=9+576|gid220=10+1914|gid247=11+1150|gid650=12+590] | `-kern [gid2=0+1413|gid217=1+1413|gid2=2+1413|gid191=3+1322|gid2=4+1413|gid172=5+1318|gid776=6+576|gid191=7+1322|gid371=8+1228|gid776=9+576|gid220=10+2018|gid247=11+1150|gid650=12+590]` |
| `NFC/NFD café` | **PASS** | canonical equivalents produce the same glyph run | `NFC [gid270=0+1190|gid247=1+1150|gid299=2+698|gid286=3+1194]; NFD [gid270=0+1190|gid247=1+1150|gid299=2+698|gid286=3+1194]` |
| `NFC/NFD double acute` | **PASS** | canonical equivalents produce the same glyph run | `NFC [gid148=0+1566]; NFD [gid148=0+1566]` |
| `canonical pair "Ω Ω"` | **PASS** | both codepoints map and have the same advance | `OHM [gid482=0+1577]; OMEGA [gid482=0+1577]` |
| `+ccmp "i͗"` | **PASS** | dotless i substitution before an above mark | `on [gid319=0+496|gid944=0@-394,0+0]; off [gid318=0+496|gid944=0@-394,421+0]` |
| `+mark "q́"` | **PASS** | base-to-mark attachment changes the mark offset | `on [gid392=0+1254|gid769=0@-878,0+0]; off [gid392=0+1254|gid769=0+0]` |
| `+mkmk "q́̈"` | **PASS** | mark-to-mark attachment stacks the second mark | `on [gid392=0+1254|gid769=0@-878,0+0|gid912=0@-1236,440+0]; off [gid392=0+1254|gid769=0@-878,0+0|gid912=0@-1236,0+0]` |
| `+tnum --show-extents "0123456789"` | **PASS** | one advance for all ten digits, equal to the tabular four `gid530` (1328) | `[gid526=0+1328<142,1510,1044,-1530>|gid527=1+1328<225,1490,921,-1490>|gid528=2+1328<189,1510,949,-1510>|gid529=3+1328<154,1510,1014,-1530>|gid530=4+1328<121,1490,1085,-1490>|gid531=5+1328<182,1490,961,-1510>|gid532=6+132` |
| `+zero "0"` | **PASS** | differs from the default `[gid514=0+1292]` | `[gid524=0+1292]` |
| `+ss02 "Il1O0"` | **PASS** | differs from the default `[gid83=0+550|gid344=1+496|gid515=2+833|gid139=3+1566|gid514=4+1292]` | `[gid98=0+903|gid351=1+564|gid515=2+833|gid139=3+1566|gid524=4+1292]` |
| `+cv02 "4"` | **PASS** | differs from the default `[gid518=0+1323]` | `[gid525=0+1323]` |
| `+cv06 "u"` | **PASS** | differs from the default `[gid418=0+1211]` | `[gid434=0+1211]` |
| `+ss03 ",;'"` | **PASS** | differs from the default `[gid649=0+590|gid655=1+590|gid634=2+614]` | `[gid852=0+590|gid853=1+618|gid634=2+614]` |
| `+frac "21/64"` | **PASS** | differs from the default `[gid516=0+1249|gid515=1+833|gid609=2+738|gid520=3+1270|gid518=4+1323]` | `[gid736=0+753|gid735=1+589|gid712=2+393|gid721=3+780|gid718=4+801]` |
| `-calt "==>"` | **PASS** | differs from the default `[gid806=0+2746]` | `[gid663=0+1355|gid663=1+1355|gid662=2+1355]` |
| `+case "(A)" against `-calt`` | **PASS** | differs from the default `[gid591=0+747|gid2=1+1413|gid592=2+747]` | `[gid600=0+747|gid2=1+1413|gid601=2+747]` |
| `default "4 u ,"` | **PASS** | each promoted default still has a reachable reverse toggle | `[gid518=0+1323|gid776=1+576|gid418=2+1211|gid776=3+576|gid649=4+590]` |

