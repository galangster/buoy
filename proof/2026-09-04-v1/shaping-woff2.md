# Shaping proofs, Buoy v1

Every row is `hb-shape` output, not a table read.

## Buoy-Medium-from-woff2.ttf (expanded from woff2: this harfbuzz build cannot open a woff2 face)

| case | result | expectation | hb-shape |
| --- | --- | --- | --- |
| `kern on/off "AVATAR To Wa."` | **PASS** | +kern [gid2=0+1305|gid114=1+1305|gid2=2+1275|gid100=3+1160|gid2=4+1452|gid90=5+1327|gid547=6+546|gid100=7+1177|gid205=8+1237|gid547=9+546|gid115=10+1945|gid126=11+1163|gid438=12+621] | `-kern [gid2=0+1452|gid114=1+1452|gid2=2+1452|gid100=3+1337|gid2=4+1452|gid90=5+1327|gid547=6+546|gid100=7+1337|gid205=8+1237|gid547=9+546|gid115=10+2054|gid126=11+1163|gid438=12+621]` |
| `+tnum --show-extents "0123456789"` | **PASS** | one advance for all ten digits, equal to the tabular four `gid318` (1327) | `[gid314=0+1327<125,1510,1076,-1530>|gid315=1+1327<209,1490,950,-1490>|gid316=2+1327<173,1510,984,-1510>|gid317=3+1327<136,1510,1050,-1530>|gid318=4+1327<103,1490,1120,-1490>|gid319=5+1327<162,1490,1000,-1510>|gid320=6+13` |
| `+zero "0"` | **PASS** | differs from the default `[gid302=0+1322]` | `[gid312=0+1322]` |
| `+ss02 "Il1O0"` | **PASS** | differs from the default `[gid41=0+558|gid186=1+516|gid303=2+850|gid77=3+1570|gid302=4+1322]` | `[gid51=0+927|gid192=1+587|gid303=2+850|gid77=3+1570|gid312=4+1322]` |
| `+cv02 "4"` | **PASS** | differs from the default `[gid306=0+1344]` | `[gid313=0+1344]` |
| `+cv06 "u"` | **PASS** | differs from the default `[gid235=0+1232]` | `[gid247=0+1232]` |
| `+ss03 ",;'"` | **PASS** | differs from the default `[gid437=0+621|gid443=1+621|gid422=2+641]` | `[gid614=0+621|gid615=1+646|gid422=2+641]` |
| `default "4 u ,"` | **PASS** | each promoted default still has a reachable reverse toggle | `[gid306=0+1344|gid547=1+546|gid235=2+1232|gid547=3+546|gid437=4+621]` |

## Buoy-Regular-from-woff2.ttf (expanded from woff2: this harfbuzz build cannot open a woff2 face)

| case | result | expectation | hb-shape |
| --- | --- | --- | --- |
| `kern on/off "AVATAR To Wa."` | **PASS** | +kern [gid2=0+1273|gid114=1+1273|gid2=2+1239|gid100=3+1148|gid2=4+1413|gid90=5+1318|gid547=6+576|gid100=7+1162|gid205=8+1228|gid547=9+576|gid115=10+1914|gid126=11+1150|gid438=12+590] | `-kern [gid2=0+1413|gid114=1+1413|gid2=2+1413|gid100=3+1322|gid2=4+1413|gid90=5+1318|gid547=6+576|gid100=7+1322|gid205=8+1228|gid547=9+576|gid115=10+2018|gid126=11+1150|gid438=12+590]` |
| `+tnum --show-extents "0123456789"` | **PASS** | one advance for all ten digits, equal to the tabular four `gid318` (1328) | `[gid314=0+1328<142,1510,1044,-1530>|gid315=1+1328<225,1490,921,-1490>|gid316=2+1328<189,1510,949,-1510>|gid317=3+1328<154,1510,1014,-1530>|gid318=4+1328<121,1490,1085,-1490>|gid319=5+1328<182,1490,961,-1510>|gid320=6+132` |
| `+zero "0"` | **PASS** | differs from the default `[gid302=0+1292]` | `[gid312=0+1292]` |
| `+ss02 "Il1O0"` | **PASS** | differs from the default `[gid41=0+550|gid186=1+496|gid303=2+833|gid77=3+1566|gid302=4+1292]` | `[gid51=0+903|gid192=1+564|gid303=2+833|gid77=3+1566|gid312=4+1292]` |
| `+cv02 "4"` | **PASS** | differs from the default `[gid306=0+1323]` | `[gid313=0+1323]` |
| `+cv06 "u"` | **PASS** | differs from the default `[gid235=0+1211]` | `[gid247=0+1211]` |
| `+ss03 ",;'"` | **PASS** | differs from the default `[gid437=0+590|gid443=1+590|gid422=2+614]` | `[gid614=0+590|gid615=1+618|gid422=2+614]` |
| `default "4 u ,"` | **PASS** | each promoted default still has a reachable reverse toggle | `[gid306=0+1323|gid547=1+576|gid235=2+1211|gid547=3+576|gid437=4+590]` |

## Promoted alternates moved the drawing

`build/C` is the same rounding run without `SwapAlternatesFilter`.
The two builds may differ only by the swap, so Buoy's default must
carry C's alternate outline and Buoy's alternate must carry C's
default outline. Compared in TTF outline space.

| weight | default | alternate | result | detail |
| --- | --- | --- | --- | --- |
| Regular | `four` | `four.ss01` | **PASS** | default==C[four.ss01]: True, four.ss01==C[four]: True |
| Regular | `four.tf` | `four.tf.ss01` | **PASS** | default==C[four.tf.ss01]: True, four.tf.ss01==C[four.tf]: True |
| Regular | `u` | `u.1` | **PASS** | default==C[u.1]: True, u.1==C[u]: True |
| Regular | `comma` | `comma.ss03` | **PASS** | default==C[comma.ss03]: True, comma.ss03==C[comma]: True |
| Regular | `quoteright` | `quoteright.ss03` | **PASS** | default==C[quoteright.ss03]: True, quoteright.ss03==C[quoteright]: True |
| Regular | `semicolon` | `semicolon.ss03` | **PASS** | default==C[semicolon.ss03]: True, semicolon.ss03==C[semicolon]: True |
| Medium | `four` | `four.ss01` | **PASS** | default==C[four.ss01]: True, four.ss01==C[four]: True |
| Medium | `four.tf` | `four.tf.ss01` | **PASS** | default==C[four.tf.ss01]: True, four.tf.ss01==C[four.tf]: True |
| Medium | `u` | `u.1` | **PASS** | default==C[u.1]: True, u.1==C[u]: True |
| Medium | `comma` | `comma.ss03` | **PASS** | default==C[comma.ss03]: True, comma.ss03==C[comma]: True |
| Medium | `quoteright` | `quoteright.ss03` | **PASS** | default==C[quoteright.ss03]: True, quoteright.ss03==C[quoteright]: True |
| Medium | `semicolon` | `semicolon.ss03` | **PASS** | default==C[semicolon.ss03]: True, semicolon.ss03==C[semicolon]: True |

