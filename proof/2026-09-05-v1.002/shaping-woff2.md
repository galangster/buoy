# Shaping proofs, Buoy v1

Every row is `hb-shape` output, not a table read.

## Buoy-Regular-from-woff2.ttf (expanded from woff2: this harfbuzz build cannot open a woff2 face)

| case | result | expectation | hb-shape |
| --- | --- | --- | --- |
| `kern on/off "AVATAR To Wa."` | **PASS** | +kern [gid2=0+1273|gid117=1+1273|gid2=2+1239|gid103=3+1148|gid2=4+1413|gid91=5+1318|gid565=6+576|gid103=7+1162|gid208=8+1228|gid565=9+576|gid118=10+1914|gid129=11+1150|gid442=12+590] | `-kern [gid2=0+1413|gid117=1+1413|gid2=2+1413|gid103=3+1322|gid2=4+1413|gid91=5+1318|gid565=6+576|gid103=7+1322|gid208=8+1228|gid565=9+576|gid118=10+2018|gid129=11+1150|gid442=12+590]` |
| `+tnum --show-extents "0123456789"` | **PASS** | one advance for all ten digits, equal to the tabular four `gid322` (1328) | `[gid318=0+1328<142,1510,1044,-1530>|gid319=1+1328<225,1490,921,-1490>|gid320=2+1328<189,1510,949,-1510>|gid321=3+1328<154,1510,1014,-1530>|gid322=4+1328<121,1490,1085,-1490>|gid323=5+1328<182,1490,961,-1510>|gid324=6+132` |
| `+zero "0"` | **PASS** | differs from the default `[gid306=0+1292]` | `[gid316=0+1292]` |
| `+ss02 "Il1O0"` | **PASS** | differs from the default `[gid42=0+550|gid189=1+496|gid307=2+833|gid78=3+1566|gid306=4+1292]` | `[gid52=0+903|gid195=1+564|gid307=2+833|gid78=3+1566|gid316=4+1292]` |
| `+cv02 "4"` | **PASS** | differs from the default `[gid310=0+1323]` | `[gid317=0+1323]` |
| `+cv06 "u"` | **PASS** | differs from the default `[gid238=0+1211]` | `[gid250=0+1211]` |
| `+ss03 ",;'"` | **PASS** | differs from the default `[gid441=0+590|gid447=1+590|gid426=2+614]` | `[gid641=0+590|gid642=1+618|gid426=2+614]` |
| `+frac "21/64"` | **PASS** | differs from the default `[gid308=0+1249|gid307=1+833|gid401=2+738|gid312=3+1270|gid310=4+1323]` | `[gid527=0+753|gid526=1+589|gid503=2+393|gid512=3+780|gid509=4+801]` |
| `-calt "==>"` | **PASS** | differs from the default `[gid595=0+2746]` | `[gid455=0+1355|gid455=1+1355|gid454=2+1355]` |
| `+case "(A)" against `-calt`` | **PASS** | differs from the default `[gid383=0+747|gid2=1+1413|gid384=2+747]` | `[gid392=0+747|gid2=1+1413|gid393=2+747]` |
| `default "4 u ,"` | **PASS** | each promoted default still has a reachable reverse toggle | `[gid310=0+1323|gid565=1+576|gid238=2+1211|gid565=3+576|gid441=4+590]` |

## Buoy-Medium-from-woff2.ttf (expanded from woff2: this harfbuzz build cannot open a woff2 face)

| case | result | expectation | hb-shape |
| --- | --- | --- | --- |
| `kern on/off "AVATAR To Wa."` | **PASS** | +kern [gid2=0+1305|gid117=1+1305|gid2=2+1275|gid103=3+1160|gid2=4+1452|gid91=5+1327|gid565=6+546|gid103=7+1177|gid208=8+1237|gid565=9+546|gid118=10+1945|gid129=11+1163|gid442=12+621] | `-kern [gid2=0+1452|gid117=1+1452|gid2=2+1452|gid103=3+1337|gid2=4+1452|gid91=5+1327|gid565=6+546|gid103=7+1337|gid208=8+1237|gid565=9+546|gid118=10+2054|gid129=11+1163|gid442=12+621]` |
| `+tnum --show-extents "0123456789"` | **PASS** | one advance for all ten digits, equal to the tabular four `gid322` (1327) | `[gid318=0+1327<125,1510,1076,-1530>|gid319=1+1327<209,1490,950,-1490>|gid320=2+1327<173,1510,984,-1510>|gid321=3+1327<136,1510,1050,-1530>|gid322=4+1327<103,1490,1120,-1490>|gid323=5+1327<162,1490,1000,-1510>|gid324=6+13` |
| `+zero "0"` | **PASS** | differs from the default `[gid306=0+1322]` | `[gid316=0+1322]` |
| `+ss02 "Il1O0"` | **PASS** | differs from the default `[gid42=0+558|gid189=1+516|gid307=2+850|gid78=3+1570|gid306=4+1322]` | `[gid52=0+927|gid195=1+587|gid307=2+850|gid78=3+1570|gid316=4+1322]` |
| `+cv02 "4"` | **PASS** | differs from the default `[gid310=0+1344]` | `[gid317=0+1344]` |
| `+cv06 "u"` | **PASS** | differs from the default `[gid238=0+1232]` | `[gid250=0+1232]` |
| `+ss03 ",;'"` | **PASS** | differs from the default `[gid441=0+621|gid447=1+621|gid426=2+641]` | `[gid641=0+621|gid642=1+646|gid426=2+641]` |
| `+frac "21/64"` | **PASS** | differs from the default `[gid308=0+1263|gid307=1+850|gid401=2+757|gid312=3+1290|gid310=4+1344]` | `[gid527=0+756|gid526=1+597|gid503=2+406|gid512=3+787|gid509=4+806]` |
| `-calt "==>"` | **PASS** | differs from the default `[gid595=0+2746]` | `[gid455=0+1367|gid455=1+1367|gid454=2+1367]` |
| `+case "(A)" against `-calt`` | **PASS** | differs from the default `[gid383=0+755|gid2=1+1452|gid384=2+755]` | `[gid392=0+755|gid2=1+1452|gid393=2+755]` |
| `default "4 u ,"` | **PASS** | each promoted default still has a reachable reverse toggle | `[gid310=0+1344|gid565=1+546|gid238=2+1232|gid565=3+546|gid441=4+621]` |

