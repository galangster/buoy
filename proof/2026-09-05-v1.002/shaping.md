# Shaping proofs, Buoy v1

Every row is `hb-shape` output, not a table read.

## Buoy-Regular.ttf

| case | result | expectation | hb-shape |
| --- | --- | --- | --- |
| `kern on/off "AVATAR To Wa."` | **PASS** | +kern [A=0+1273|V=1+1273|A=2+1239|T=3+1148|A=4+1413|R=5+1318|space=6+576|T=7+1162|o=8+1228|space=9+576|W=10+1914|a=11+1150|period=12+590] | `-kern [A=0+1413|V=1+1413|A=2+1413|T=3+1322|A=4+1413|R=5+1318|space=6+576|T=7+1322|o=8+1228|space=9+576|W=10+2018|a=11+1150|period=12+590]` |
| `+tnum --show-extents "0123456789"` | **PASS** | one advance for all ten digits, equal to the tabular four `four.tf` (1328) | `[zero.tf=0+1328<142,1510,1044,-1530>|one.tf=1+1328<225,1490,921,-1490>|two.tf=2+1328<189,1510,949,-1510>|three.tf=3+1328<154,1510,1014,-1530>|four.tf=4+1328<121,1490,1085,-1490>|five.tf=5+1328<182,1490,961,-1510>|six.tf=` |
| `+zero "0"` | **PASS** | expected zero.slash | `[zero.slash=0+1292]` |
| `+ss02 "Il1O0"` | **PASS** | differs from the default `[I=0+550|l=1+496|one=2+833|O=3+1566|zero=4+1292]` | `[I.1=0+903|l.ss02=1+564|one=2+833|O=3+1566|zero.slash=4+1292]` |
| `+cv02 "4"` | **PASS** | expected four.ss01 | `[four.ss01=0+1323]` |
| `+cv06 "u"` | **PASS** | expected u.1 | `[u.1=0+1211]` |
| `+ss03 ",;'"` | **PASS** | differs from the default `[comma=0+590|semicolon=1+590|quotesingle=2+614]` | `[comma.ss03=0+590|semicolon.ss03=1+618|quotesingle=2+614]` |
| `+frac "21/64"` | **PASS** | differs from the default `[two=0+1249|one=1+833|slash=2+738|six=3+1270|four=4+1323]` | `[two.numr=0+753|one.numr=1+589|fraction=2+393|six.dnom=3+780|four.dnom=4+801]` |
| `-calt "==>"` | **PASS** | differs from the default `[uni27F9=0+2746]` | `[equal=0+1355|equal=1+1355|greater=2+1355]` |
| `+case "(A)" against `-calt`` | **PASS** | expected parenleft.case | `[parenleft.case=0+747|A=1+1413|parenright.case=2+747]` |
| `default "4 u ,"` | **PASS** | the promoted alternates are the default glyphs | `[four=0+1323|space=1+576|u=2+1211|space=3+576|comma=4+590]` |

## Buoy-Medium.ttf

| case | result | expectation | hb-shape |
| --- | --- | --- | --- |
| `kern on/off "AVATAR To Wa."` | **PASS** | +kern [A=0+1305|V=1+1305|A=2+1275|T=3+1160|A=4+1452|R=5+1327|space=6+546|T=7+1177|o=8+1237|space=9+546|W=10+1945|a=11+1163|period=12+621] | `-kern [A=0+1452|V=1+1452|A=2+1452|T=3+1337|A=4+1452|R=5+1327|space=6+546|T=7+1337|o=8+1237|space=9+546|W=10+2054|a=11+1163|period=12+621]` |
| `+tnum --show-extents "0123456789"` | **PASS** | one advance for all ten digits, equal to the tabular four `four.tf` (1327) | `[zero.tf=0+1327<125,1510,1076,-1530>|one.tf=1+1327<209,1490,950,-1490>|two.tf=2+1327<173,1510,984,-1510>|three.tf=3+1327<136,1510,1050,-1530>|four.tf=4+1327<103,1490,1120,-1490>|five.tf=5+1327<162,1490,1000,-1510>|six.tf` |
| `+zero "0"` | **PASS** | expected zero.slash | `[zero.slash=0+1322]` |
| `+ss02 "Il1O0"` | **PASS** | differs from the default `[I=0+558|l=1+516|one=2+850|O=3+1570|zero=4+1322]` | `[I.1=0+927|l.ss02=1+587|one=2+850|O=3+1570|zero.slash=4+1322]` |
| `+cv02 "4"` | **PASS** | expected four.ss01 | `[four.ss01=0+1344]` |
| `+cv06 "u"` | **PASS** | expected u.1 | `[u.1=0+1232]` |
| `+ss03 ",;'"` | **PASS** | differs from the default `[comma=0+621|semicolon=1+621|quotesingle=2+641]` | `[comma.ss03=0+621|semicolon.ss03=1+646|quotesingle=2+641]` |
| `+frac "21/64"` | **PASS** | differs from the default `[two=0+1263|one=1+850|slash=2+757|six=3+1290|four=4+1344]` | `[two.numr=0+756|one.numr=1+597|fraction=2+406|six.dnom=3+787|four.dnom=4+806]` |
| `-calt "==>"` | **PASS** | differs from the default `[uni27F9=0+2746]` | `[equal=0+1367|equal=1+1367|greater=2+1367]` |
| `+case "(A)" against `-calt`` | **PASS** | expected parenleft.case | `[parenleft.case=0+755|A=1+1452|parenright.case=2+755]` |
| `default "4 u ,"` | **PASS** | the promoted alternates are the default glyphs | `[four=0+1344|space=1+546|u=2+1232|space=3+546|comma=4+621]` |

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

