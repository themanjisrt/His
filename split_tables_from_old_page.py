"""Split the project's data into: the three source tables (cleaned) and the four later-added tables.
Usage: python3 -I build_data.py <repo-dir> <out-dir>
Nothing is invented here: rows are copied; only blank rows, float ids, stray spaces and 'woman' are normalised."""
import json, re, sys, math

repo, out = sys.argv[1], sys.argv[2]
raw = json.load(open(f'{repo}/dashboard_data.json', encoding='utf-8'))
html = open(f'{repo}/index.html', encoding='utf-8').read()

def is_blank(v): return v is None or (isinstance(v, float) and math.isnan(v)) or v == ''
def clean(v):
    if isinstance(v, str): return v.strip()
    return v
def as_int(v): return int(v) if not is_blank(v) else None

report = []
def table(name, rows, id_key):
    kept = []
    for r in rows:
        if is_blank(r.get('decree_id')):
            report.append(f'{name}: dropped blank row {id_key}={r.get(id_key)}'); continue
        r2 = {k: clean(v) for k, v in r.items()}
        r2['decree_id'] = as_int(r['decree_id'])
        for k, v in r.items():
            if isinstance(v, str) and v != v.strip(): report.append(f'{name}: trimmed space in {k} (decree {r2["decree_id"]})')
        kept.append(r2)
    return kept

pets = table('petitioners', raw['petitioners'], 'decree_id')
for p in pets:
    if p['petitioner_gender'] == 'woman':
        p['petitioner_gender'] = 'female'; report.append(f'petitioners: gender "woman" -> "female" (decree {p["decree_id"]})')
locs = table('locations', raw['locations'], 'location_id')
recs = table('receivers', raw['receivers'], 'receiver_id')
json.dump({'petitioners': pets, 'locations': locs, 'receivers': recs}, open(f'{out}/dashboard_data.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

def inline(name):
    m = re.search(r'const ' + name + r' = \[(.*?)\n    \];', html, re.S)
    rows = []
    for line in m.group(1).strip().split('\n'):
        line = line.strip().rstrip(',')
        if not line.startswith('{'): continue
        row = {}
        for k, v in re.findall(r'(\w+): (`[^`]*`|-?[\d.]+|null)', line):
            row[k] = v[1:-1] if v.startswith('`') else (None if v == 'null' else float(v) if '.' in v else int(v))
        # fidelity check: every backtick string and number in the source line must be captured
        assert len(row) == line.count(': '), (name, line[:80], len(row), line.count(': '))
        rows.append(row)
    return rows

layer = {
  'status': 'unverified',
  'note': 'These four tables were added on top of the three source tables in an earlier version of the page. They have not been checked line by line against the register. The page keeps them out of totals and charts.',
  'defendants': inline('DEFENDANTS_TABLE'),
  'financial_claims': inline('FINANCIAL_CLAIMS_TABLE'),
  'admin_hierarchy': inline('ADMIN_HIERARCHY_TABLE'),
  'resolutions': inline('RESOLUTIONS_TABLE'),
}
json.dump(layer, open(f'{out}/interpretive_layer.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('source rows:', len(pets), len(locs), len(recs), '| layer rows:', [len(layer[k]) for k in ('defendants', 'financial_claims', 'admin_hierarchy', 'resolutions')])
print('\n'.join(report))
