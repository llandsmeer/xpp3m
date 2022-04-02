#!/usr/bin/env python3
#
# xppm3: experimental xournal++ 3-way automatic merge tool.
# Copyright (C) 2022 Lennart P. L. Landsmeer
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import gzip
from lxml import etree

def open_xournal(filename):
    with gzip.open(filename, 'rb') as f:
        ET = etree.parse(f)
    ET.getroot().remove(ET.xpath('//preview')[0])
    return ET

class XournalLayer:
    def __init__(self):
        self.items = []

    @classmethod
    def fromelem(cls, elem):
        self = cls()
        self.elem = elem
        for item in elem:
            # image, stroke, text
            self.items.append(etree.tostring(item, encoding='unicode').strip())
        return self

class XournalPage:
    def __init__(self):
        self.layers = []
        self.background = None
        self.attr = dict()

    @classmethod
    def fromelem(cls, elem):
        self = cls()
        self.elem = elem
        self.attr = dict(elem.attrib)
        for child in elem:
            if child.tag == 'layer':
                self.layers.append(XournalLayer.fromelem(child))
            elif child.tag == 'background':
                self.background = etree.tostring(child, encoding='unicode').strip()
            else:
                print(child)
                assert False
        return self

class XournalDocument:
    def __init__(self):
        self.filename = '?'
        self.title = '?'
        self.pages = []

    @classmethod
    def fromfile(cls, filename):
        self = cls()
        self.filename = filename
        tree = open_xournal(filename)
        self.title = tree.xpath('//title')[0].text
        pages = tree.xpath('//page')
        self.pages = [XournalPage.fromelem(page) for page in pages]
        return self

    def pprint(self):
        print('Document', self.filename)
        for i, page in enumerate(self.pages):
            print('||page', i, page.attr)
            print('|| - background', page.background)
            for j, layer in enumerate(page.layers):
                print('|| - layer', j)
                for item in layer.items:
                    print('||    -', item)
        print()

    def save(self, filename):
        tree = etree.Element('xournal')
        with gzip.open(filename, 'wb') as f:
            xournal = etree.SubElement(tree, 'xournal', attrib=dict(creator='xournal++ mergetool', fileversion='4'))
            title = etree.SubElement(xournal, 'title')
            title.text = self.title
            for page in self.pages:
                page_elem = etree.SubElement(xournal, 'page', attrib=page.attr)
                page_elem.append(etree.fromstring(page.background))
                for layer in page.layers:
                    layer_elem = etree.SubElement(page_elem, 'layer')
                    for item in layer.items:
                        layer_elem.append(etree.fromstring(item))
            f.write(etree.tostring(xournal, xml_declaration=True, encoding='utf-8', pretty_print=True))

    def __repr__(self):
        return f'Xournal({repr(self.filename)})'

def _merge3atom(root, a, b):
    if root != a:
        return a
    if root != b:
        return b
    return root

def _merge3dict(root, a, b):
    out = {}
    k = set(root.keys()) | set(a.keys()) | set(b.keys())
    for key in k:
        value = _merge3atom(root.get(key), a.get(key), b.get(key))
        if value is not None:
            out[key] = value
    return out

def _merge3list(root, a, b):
    root_lookup = set(root)
    a_lookup = set(a)
    b_lookup = set(b)
    removed = root_lookup - a_lookup - b_lookup
    added = (a_lookup - root_lookup) | (b_lookup - root_lookup)
    return list(root_lookup - removed) + list(added)

def merge_page(root, a, b):
    '''3-way automatic page merge

    root, a, b are XournalPage objects.
    in case of unresolved conflicts (mostly background), page a wins
    '''
    c = XournalPage()
    c.background = _merge3atom(root.background, a.background, b.background)
    c.attr = _merge3dict(root.attr, a.attr, b.attr)
    assert len(root.layers) == len(a.layers) == len(b.layers)
    for i in range(len(root.layers)):
        layer = XournalLayer()
        layer.items = _merge3list(root.layers[i].items, a.layers[i].items, b.layers[i].items)
        c.layers.append(layer)
    return c


def main():
    fn_root = 'root.xopp'
    fn_a = 'a.xopp'
    fn_b = 'b.xopp'
    fn_out = 'merged.xopp'

    import argparse
    parser = argparse.ArgumentParser(description='Merge xournal++ files')
    parser.add_argument('--root', default=fn_root, help='root file')
    parser.add_argument('--left', default=fn_a, help='file a')
    parser.add_argument('--right', default=fn_b, help='file b')
    parser.add_argument('--out', default=fn_out, help='output file')
    parser.add_argument('--verbose', default=False, action='store_true', help='verbose output')
    args = parser.parse_args()
    fn_root = args.root
    fn_a = args.left
    fn_b = args.right
    fn_out = args.out
    flag_verbose = args.verbose

    root = XournalDocument.fromfile(fn_root)
    a = XournalDocument.fromfile(fn_a)
    b = XournalDocument.fromfile(fn_b)

    if flag_verbose:
        root.pprint()
        a.pprint()
        b.pprint()

    page = merge_page(root.pages[0], a.pages[0], b.pages[0])
    c = XournalDocument()
    c.pages.append(page)
    if flag_verbose:
        c.pprint()
    c.title = _merge3atom(root.title, a.title, b.title)

    c.save(fn_out)

    if flag_verbose:
        with gzip.open(fn_out, 'rt') as f:
            print(f.read())

if __name__ == '__main__':
    main()
