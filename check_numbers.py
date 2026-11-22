"""Independent recomputation of the numbers the page shows, straight from the cleaned source tables."""
import json, math, sys, statistics, collections, re
d = json.load(open(sys.argv[1], encoding='utf-8'))
O = (41.0082, 28.9784)
def hav(a, b):
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    x = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(b[1] - a[1]) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(x))
RULES = [('ext', ['extortion','oppression','harassment','imprisonment','misconduct','confiscation','homicide']), ('debt', ['debt','nonpayment','loan','mahr']),
         ('prop', ['property','land','encroachment','sale','real estate','water','inheritance']), ('appt', ['appointment','mutasallim']),
         ('tax', ['tax','revenue','fee','customs','desolation','supply']), ('resettle', ['resettlement','runaway','jurisdictional'])]
def cls(s):
    t = (s or '').strip().lower()
    for k, ws in RULES:
        if any(w in t for w in ws): return k
    return 'other'
pets = sorted(d['petitioners'], key=lambda r: r['decree_id'])
sites = []
per = collections.defaultdict(list)
for p in pets:
    for l in [l for l in d['locations'] if l['decree_id'] == p['decree_id']]:
        s = next((s for s in sites if abs(s['lat'] - l['lat']) < 0.03 and abs(s['lng'] - l['long']) < 0.04), None)
        if not s:
            s = {'lat': l['lat'], 'lng': l['long'], 'name': l['receiver_location']}; s['km'] = round(hav(O, (s['lat'], s['lng']))); sites.append(s)
        if s not in per[p['decree_id']]: per[p['decree_id']].append(s)
marks = [s['km'] for i in per for s in per[i]]
recs = collections.defaultdict(list)
for r in d['receivers']: recs[r['decree_id']].append(r['receiver_title'])
out = {
  'decrees': len(pets), 'sites': len(sites), 'marks': len(marks), 'median_km': round(statistics.median(marks)),
  'cats': dict(collections.Counter(cls(p['complaint_subject']) for p in pets)),
  'kinds': dict(collections.Counter(p['petitioner_gender'] for p in pets)),
  'receiver_rows': len(d['receivers']), 'with_kadi': sum(1 for i in recs if any(re.search('kadi', t, re.I) for t in recs[i])),
  'one_place': sum(1 for i in per if len(per[i]) == 1), 'many': sum(1 for i in per if len(per[i]) > 1),
  'widest': max(((len(per[i]), i) for i in per)),
  'hatun': [p['decree_id'] for p in pets if 'hatun' in (p['petitioner_name'] or '').lower()],
  'ext_women': [p['decree_id'] for p in pets if cls(p['complaint_subject']) == 'ext' and p['petitioner_gender'] == 'female'],
  'top_receivers': collections.Counter(r['receiver_title'] for r in d['receivers']).most_common(4),
}
print(json.dumps(out, ensure_ascii=False))
