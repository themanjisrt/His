"""Clip Natural Earth (public domain) land, natural lakes and rivers to the map region.
Usage: python3 -I build_basemap.py <natural-earth-dir> <out.json>"""
import json, sys
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union

src, out = sys.argv[1], sys.argv[2]
W, S, E, N = 6, 24, 60, 53
TOL = float(sys.argv[3]) if len(sys.argv) > 3 else 0.008
bb = box(W, S, E, N)
r3 = lambda ring: [[round(x, 3), round(y, 3)] for x, y in ring]

def polys(geom):
    if geom.is_empty: return []
    if geom.geom_type == 'Polygon': return [geom]
    if geom.geom_type in ('MultiPolygon', 'GeometryCollection'):
        return [g for g in geom.geoms if g.geom_type == 'Polygon']
    return []

def lines(geom):
    if geom.is_empty: return []
    if geom.geom_type == 'LineString': return [geom]
    if geom.geom_type in ('MultiLineString', 'GeometryCollection'):
        return [g for g in geom.geoms if g.geom_type == 'LineString']
    return []

load = lambda f: json.load(open(f'{src}/{f}.geojson', encoding='utf-8'))['features']

land = unary_union([shape(f['geometry']).buffer(0).intersection(bb) for f in load('ne_10m_land') + load('ne_10m_minor_islands') if shape(f['geometry']).intersects(bb)])
land_out = []
for p in polys(land):
    p = p.simplify(TOL, preserve_topology=True)
    if p.area < 0.0008: continue
    land_out.append([r3(p.exterior.coords)] + [r3(i.coords) for i in p.interiors if box(*i.bounds).area > 0.002])

# Natural lakes only: reservoirs did not exist in 1649.
MODERN = ('reservoir', 'nasser', 'tharthar', 'razzaza', 'habbaniyah', 'sarygamysh', 'ijsselmeer')
lakes_out = []
for f in load('ne_50m_lakes'):
    name = (f['properties'].get('name') or '')
    if not name or any(m in name.lower() for m in MODERN): continue
    for p in polys(shape(f['geometry']).buffer(0).intersection(bb)):
        lakes_out.append({'n': name, 'r': [r3(p.simplify(0.004).exterior.coords)]})

rivers_out = []
for f in load('ne_10m_rivers_lake_centerlines'):
    p = f['properties']
    cla = (p.get('featurecla') or '')
    if 'Canal' in cla or 'canal' in (p.get('name') or '').lower() or 'Csatorna' in (p.get('name') or ''): continue
    rank = p.get('scalerank')
    if rank is None or rank > 8: continue
    for ln in lines(shape(f['geometry']).intersection(bb)):
        ln = ln.simplify(0.006)
        if ln.length < 0.15: continue
        rivers_out.append({'n': p.get('name_en') or p.get('name') or '', 'k': int(rank), 'c': r3(ln.coords)})

data = {'source': 'Natural Earth 1:10m land and river centerlines, 1:50m lakes (public domain). Reservoirs and canals removed.',
        'bbox': [W, S, E, N], 'land': land_out, 'lakes': lakes_out, 'rivers': rivers_out}
json.dump(data, open(out, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
npts = sum(len(r) for p in land_out for r in p)
print('land polygons', len(land_out), 'points', npts, '| lakes', [l['n'] for l in lakes_out], '| river segments', len(rivers_out), 'points', sum(len(r['c']) for r in rivers_out))
print('river names:', sorted({r['n'] for r in rivers_out}))
