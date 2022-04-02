#!/usr/bin/env python3

import os
import gzip
import sqlite3
import hashlib
import re
import argparse

PATTERN_FROM = r'FROM:([0-9a-f]{32}(:?,[0-9a-f]{32})?)'
TEMPLATE_FROM = '<text font="Sans" size="12" x="100" y="100" color="#000000ff" ts="0" fn="">FROM:{0}</text>'

def index_file(fn_database, fn_in):
    rowids = []
    con = sqlite3.connect(fn_database)
    cur = con.cursor()
    cur.execute('create table if not exists lines (line blob primary key)')
    # PARENT can be one or two hash values
    cur.execute('create table if not exists files (hash text primary key, filename text, rowids text, parents text)')
    parents = 'none'
    m = hashlib.sha256()
    with gzip.open(fn_in, 'rt') as f:
        state = 0
        for line in f:
            match = re.match(PATTERN_FROM, line)
            if match:
                if parents != 'none':
                    print('WARNING!! MULTIPLE FROM:<DOCID> DECLARATIONS, IGNORING ALL BUT FIRST')
                else:
                    parents = match.group(1)
            if state == 0 and line.startswith('<?xml'):
                state = 1
            elif state == 1 and line.startswith('<xournal'):
                state = 2
            elif state == 2 and line.startswith('<title'):
                state = 3
            elif state == 3 and re.match(r'^<preview>[^><]+</preview>\n$', line):
                state = 4
                continue
            m.update(line.encode('utf-8'))
            if line.endswith('\n'):
                line = line[:-1]
            # line = lzma.compress(line.encode('utf-8'), lzma.FORMAT_XZ, preset=9)
            cur.execute('''insert or ignore into lines values (?)''', (line,))
            #rowid = cur.lastrowid if rowid == 0:
            cur.execute('select rowid from lines where line = ?', (line,))
            rowid = cur.fetchone()[0]
            rowids.append(rowid)
    rowids = ','.join(map(str, rowids))
    filehash = m.hexdigest()[:32]
    cur.execute('insert or ignore into files values (?, ?, ?, ?)', (filehash, fn_in, rowids, parents))
    con.commit()
    con.close()
    return filehash

def derive(fn_in, fn_out, hash_in):
    with gzip.open(fn_in, 'rt') as f:
        content = f.read()
        count = len(re.findall(PATTERN_FROM, content))
        if count == 0:
            print('ADDING FROM:<DOCID> DECLARATION')
            assert '<layer>' in content
            content = re.sub(r'(<layer>\n?)', r'\1' + TEMPLATE_FROM.format(hash_in) + '\n', content)
        else:
            if count > 1:
                print('WARNING!! MULTIPLE FROM:<DOCID> DECLARATIONS, IGNORING ALL BUT FIRST')
            content = re.sub(PATTERN_FROM, 'FROM:' + hash_in, content, count=1)
        with gzip.open(fn_out, 'wt') as fout:
            fout.write(content)

def main():
    parser = argparse.ArgumentParser(description='minimal xournal++ version control database')
    parser.add_argument('--database', default='~/.config/xpp3m', help='database file')

    sub = parser.add_subparsers(dest='sub', help='subcommands')
    index_parser = sub.add_parser('index', help='index a xournal++ file')
    index_parser.add_argument('--file', default='root.xopp', help='Input file', required=True)

    derive_parser = sub.add_parser('commit', help='derive from a xournal++ file')
    derive_parser.add_argument('--input', default='root.xopp', help='Input file')
    derive_parser.add_argument('--output', help='Output file', required=True)

    args = parser.parse_args()
    dbpath = os.path.expanduser(args.database)
    if args.sub == 'index':
        filehash = index_file(dbpath, args.file)
        print(filehash)
    elif args.sub == 'commit':
        filehash = index_file(dbpath, args.input)
        derive(args.input, args.output, filehash)
        filehash2 = index_file(dbpath, args.output)
        print(filehash, '->', filehash2)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
