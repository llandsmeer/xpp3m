# xppm3

Experimental xournal++ 3-way automatic merge tool.
Currently merging only one page is supported.
This tool is mostly untested and it's usage will likely lead to data loss.

```
usage: xppm3.py [-h] [--root ROOT] [--left LEFT]
                [--right RIGHT] [--out OUT] [--verbose]

Merge xournal++ files

optional arguments:
  -h, --help     show this help message and exit
  --root ROOT    root file
  --left LEFT    file a
  --right RIGHT  file b
  --out OUT      output file
  --verbose      verbose output
```

Example

```
$ xppm3.py --root root.xopp --left a.xopp --right b.xopp --out merged.xopp --verbose

Document root.xopp
||page 0 {'width': '595.27559100', 'height': '841.88976400'}
|| - background <background type="solid" color="#ffffffff" style="lined"/>
|| - layer 0
||    - <text font="Sans" size="12.00000000" x="78.30106717" y="90.55477825" color="#000000ff" ts="0" fn="">Common root</text>

Document a.xopp
||page 0 {'width': '595.27559100', 'height': '841.88976400'}
|| - background <background type="solid" color="#ffffffff" style="lined"/>
|| - layer 0
||    - <text font="Sans" size="12.00000000" x="78.30106717" y="90.55477825" color="#000000ff" ts="0" fn="">Common root</text>
||    - <text font="Sans" size="12.00000000" x="97.06042903" y="147.60998571" color="#000000ff" ts="0" fn="">A</text>

Document b.xopp
||page 0 {'width': '595.27559100', 'height': '841.88976400'}
|| - background <background type="solid" color="#ffffffff" style="lined"/>
|| - layer 0
||    - <text font="Sans" size="12.00000000" x="78.30106717" y="90.55477825" color="#000000ff" ts="0" fn="">Common root</text>
||    - <text font="Sans" size="12.00000000" x="124.70300257" y="131.72696290" color="#000000ff" ts="0" fn="">B</text>

Document ?
||page 0 {'height': '841.88976400', 'width': '595.27559100'}
|| - background <background type="solid" color="#ffffffff" style="lined"/>
|| - layer 0
||    - <text font="Sans" size="12.00000000" x="78.30106717" y="90.55477825" color="#000000ff" ts="0" fn="">Common root</text>
||    - <text font="Sans" size="12.00000000" x="97.06042903" y="147.60998571" color="#000000ff" ts="0" fn="">A</text>
||    - <text font="Sans" size="12.00000000" x="124.70300257" y="131.72696290" color="#000000ff" ts="0" fn="">B</text>

<?xml version='1.0' encoding='utf-8'?>
<xournal creator="xournal++ mergetool" fileversion="4">
  <title>Xournal++ document - see https://github.com/xournalpp/xournalpp</title>
  <page height="841.88976400" width="595.27559100">
    <background type="solid" color="#ffffffff" style="lined"/>
    <layer>
      <text font="Sans" size="12.00000000" x="78.30106717" y="90.55477825" color="#000000ff" ts="0" fn="">Common root</text>
      <text font="Sans" size="12.00000000" x="97.06042903" y="147.60998571" color="#000000ff" ts="0" fn="">A</text>
      <text font="Sans" size="12.00000000" x="124.70300257" y="131.72696290" color="#000000ff" ts="0" fn="">B</text>
    </layer>
  </page>
```

# License

```
xppm3: experimental xournal++ 3-way automatic merge tool.
Copyright (C) 2022 Lennart P. L. Landsmeer

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
```
