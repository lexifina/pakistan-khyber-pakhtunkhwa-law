"""KP Code PDF -> units (private). Wraps scripts/pakistan-law/parse_pdf.py (the Pakistan Code parser: these are the
same Word-made consolidations) and adds what the provincial PDFs need: running heads (the Act's title and number at
the top of every page) are removed, the cover and the table of contents are left out, footnote markers are dropped
and the footnotes returned separately.

    python -X utf8 parse.py <pdf>     # print the units
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'pakistan-law'))
import parse_pdf as P  # noqa: E402
import pymupdf  # noqa: E402

MARK = re.compile(r'\[\^\d+\]')
CONTENTS = re.compile(r'^C\s*O\s*N\s*T\s*E\s*N\s*T\s*S\b|^TABLE\s+OF\s+CONTENTS$', re.I)
NUMROW = re.compile(r'^\d{1,3}[A-Z]{0,3}\s?\.\s')
TITLEISH = re.compile(r'^(THE\b.*\b(ACT|ORDINANCE|REGULATIONS?|CODE|ORDER)\b|\(.*\b(ACT|ORDINANCE|REGULATION)\s+NO\b|'
                      r'\(?\s*First\s+published|AN$|AN\s+(ACT|ORDINANCE)\b)', re.I)
DESIG = re.compile(r'^(Vice[- ]?|Co-?)?(Chair(man|person)?|Members?|Secretary|Convener|President)'
                   r'([- ]+(cum[- ]+)?(Secretary|Member|Chair(man|person)))?\s*[.;,:]?$', re.I)
PARTIAL = re.compile(r'^(Vice|Co-?|Member[- ]cum[- ]?|Chair(man|person)[- ]cum[- ]?)$', re.I)
PUBNOTE = re.compile(r'^(\[?\(?\s*First\s+published|AN$|AN\s+(ACT|ORDINANCE)\b|ACT$|ORDINANCE$)', re.I)
PAGE = re.compile(r'^\s*\d+\s*\|\s*P\s*a\s*g\s*e\s*$|^\s*Page\s*\d+\s*(of\s*\d+)?\s*$', re.I)


def ld(s: str) -> str:
    return ''.join(ch for ch in s if ch.isalnum()).lower()


def heads(pdf: Path) -> set[str]:
    """Letters and digits of every line printed in the top 13% of at least a third of the pages (and two or more)."""
    doc = pymupdf.open(str(pdf))
    cnt: Counter = Counter()
    for page in doc:
        h = page.rect.height
        seen = set()
        for b in page.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                if l['bbox'][1] > 0.13 * h:
                    continue
                t = ''.join(s['text'] for s in l['spans']).strip()
                if t and not PAGE.match(t):
                    seen.add(ld(t))
        cnt.update(k for k in seen if len(k) >= 4)
    n = len(doc)
    need = max(2, -(-n // 3))
    return {k for k, v in cnt.items() if v >= need} if n >= 2 else set()


def right_cells(pdf: Path) -> list[list[tuple[str, str]]]:
    """Designations printed alone in a right-hand table column beside a left cell (the "Chairperson" / "Member"
    column of a Board's membership table). The Pakistan Code parser joins each one into the left cell's row it sits
    beside; the printed order is the left cell, then the right cell. Returns, per cell, its lines as (the tail of the
    left-hand text on the same row, the cell line); a cell may take two lines ("Vice" / "Chairperson")."""
    doc = pymupdf.open(str(pdf))
    out = []
    for page in doc:
        W = page.rect.width
        lines = []
        for b in page.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                t = re.sub(r'\s+', ' ', ''.join(s['text'] for s in l['spans'])).strip()
                if t:
                    lines.append((l['bbox'], t))
        prev = None
        for (x0, y0, x1, y1), t in sorted(lines, key=lambda z: (z[0][1], z[0][0])):
            if x0 < 0.5 * W or len(t.split()) > 4 or not (DESIG.match(t) or PARTIAL.match(t)):
                continue
            left = [(bx1, tt) for (bx0, by0, bx1, by1), tt in lines if bx1 < x0 - 15 and by0 < y1 - 2 and by1 > y0 + 2]
            if not left:
                continue
            tail = max(left)[1][-25:]
            if prev and PARTIAL.match(prev[-1][1]) and y0 - prev_y1 < 1.6 * (y1 - y0):
                prev.append((tail, t))
            else:
                prev = [(tail, t)]
                out.append(prev)
            prev_y1 = y1
    return [c for c in out if DESIG.match(' '.join(x[1] for x in c).replace('- ', '-'))]


def move_cells(line: str, cells: list) -> str:
    """'(a) Secretary ..., Commerce Chairperson and Technical Education Department;' ->
    '(a) Secretary ..., Commerce and Technical Education Department; Chairperson' (a labelled table row only, and
    only where the designation follows the very words printed beside it)."""
    if not re.match(r'^\(?[a-z0-9ivx]{1,4}\)', line):
        return line
    for cell in cells:
        t = line
        ok = True
        for tail, part in cell:
            k = t.find(tail + ' ' + part)
            if k < 0 or k + len(tail) + 1 + len(part) >= len(t.rstrip()):
                ok = False
                break
            t = t[:k + len(tail)] + t[k + len(tail) + 1 + len(part):]
        if ok:
            return t.rstrip() + ' ' + ' '.join(p for _, p in cell).replace('- ', '-')
    return line


def key_of(u: dict, n: dict) -> str:
    if u['kind'] == 'section':
        num = u['num']
        m = re.match(r'(\d+)([A-Z]*)$', num)
        base = f'sec-{int(m.group(1)):03d}' + (('-' + m.group(2).lower()) if m.group(2) else '') if m else 'sec-' + ld(num)
    elif u['kind'] == 'schedule':
        base = f'schedule-{int(u["num"]):02d}'
    else:
        base = f'text-{int(u["num"]):02d}'
    n[base] = n.get(base, 0) + 1
    return base if n[base] == 1 else f'{base}-{n[base]}'


def clean(lines: list[str], hd: set[str]) -> list[str]:
    out = []
    for l in lines:
        l = MARK.sub('', l)
        l = re.sub(r'^#+\s*', '', l)
        l = re.sub(r'[ \t ]+', ' ', l).strip()
        if not l or PAGE.match(l) or ld(l) in hd or not ld(l):
            if l and not ld(l) and l.strip('_-–—.* ') == '':
                continue
            if l and not ld(l):
                out.append(l)   # punctuation-only rows ("* * *") stay as printed
            continue
        out.append(l)
    return out


def parse(pdf: Path) -> dict:
    r = P.parse(pdf)
    hd = heads(pdf)
    # everything before the first section: cover, table of contents, then the body's title rows and preamble (the
    # Pakistan Code parser splits these between 'title' and 'contents' in ways that vary from PDF to PDF)
    rows = list(r['title']) + list(r['contents'])
    ci = next((i for i, t in enumerate(rows) if CONTENTS.match(t.strip())), None)
    numbered = [i for i, t in enumerate(rows) if NUMROW.match(MARK.sub('', t).strip())]
    if ci is not None or len(numbered) >= 3:
        e = max([i for i in numbered if ci is None or i > ci] or [ci if ci is not None else -1])
        start = next((j for j in range(e + 1, len(rows))
                      if ld(MARK.sub('', rows[j])) in hd or TITLEISH.match(MARK.sub('', rows[j]).strip())), e + 1)
        rows = rows[start:]
    # the title and number rows are printed again as each page's running head: the block starts at the publication
    # note ("(First published ...") or the "AN ACT" line when there is one (the title and number are in the Act's
    # metadata), so the record never starts on a row the cover or a running head also carries
    pub = next((j for j, t in enumerate(rows) if PUBNOTE.match(MARK.sub('', t).strip())), None)
    if pub is not None:
        rows = rows[pub:]
    # in the title block a running head's text is kept only where it is printed last (the body's own title rows)
    keep = []
    for i, t in enumerate(rows):
        k = ld(MARK.sub('', t))
        if k in hd and any(ld(MARK.sub('', x)) == k for x in rows[i + 1:]):
            continue
        keep.append(t)
    title = [re.sub(r'\s+', ' ', MARK.sub('', t)).strip() for t in keep]
    title = [t for t in title if t and not PAGE.match(t)]
    # rows of one paragraph the parser left apart (the publication note runs over three printed lines): joined while
    # a bracket is still open
    joined: list[str] = []
    for t in title:
        if joined and (joined[-1].count('(') > joined[-1].count(')') or joined[-1].count('[') > joined[-1].count(']')):
            joined[-1] += ' ' + t
        else:
            joined.append(t)
    title = joined
    units: dict[str, dict] = {}
    if title:
        units['000-title'] = {'label': 'Title', 'kind': 'title', 'text': '# Title\n' + '\n'.join(title) + '\n'}
    seen: dict = {}
    nsec = 0
    rc = right_cells(pdf)
    cells = rc
    for u in r['units']:
        lines = [move_cells(l, cells) for l in clean(u['lines'], hd)] if cells else clean(u['lines'], hd)
        if not lines:
            continue
        k = key_of(u, seen)
        if u['kind'] == 'section':
            nsec += 1
            label = f'Section {u["num"]}'
        elif u['kind'] == 'schedule':
            label = f'Schedule {u["num"]}'
        else:
            label = 'Text'
        units[k] = {'label': label, 'kind': 'section' if u['kind'] == 'section' else u['kind'],
                    'text': f'# {label}\n' + '\n'.join(lines) + '\n'}
    notes = [{'page': n['page'], 'n': n['n'], 'g': n['g'], 'text': n['text']} for n in r['notes']]
    where = {}
    for u in r['units']:
        for g in u.get('notes', []):
            where.setdefault(g, u['id'])
    return {'units': units, 'notes': notes, 'note_unit': where, 'sections': nsec, 'pages': r['pages'],
            'text_layer': r['text_layer'], 'scan_pages': r['scan_pages'], 'invisible': r['invisible_chars'],
            'stamps': r['stamps'], 'heads': sorted(hd), 'unresolved': r['unresolved_markers']}


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    out = parse(Path(sys.argv[1]))
    print('HEADS', out['heads'], 'sections', out['sections'])
    for k, u in out['units'].items():
        print('=====', k); print(u['text'])
    for n in out['notes']:
        print('NOTE', n)
