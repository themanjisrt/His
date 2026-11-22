# History-GIS 2026: Atik Şikâyet Defteri no. 1 on a map

A single static page that shows where the Ottoman Imperial Council (Dîvân-ı Hümâyûn) sent its
answers to petitions in Muharrem 1059 (January to February 1649). Each decree in the register is
addressed to one or more officials in one or more towns; the map draws that address.

Source: Devlet Arşivleri Başkanlığı Osmanlı Arşivi, Atik Şikâyet Defterleri (A.DVNS.ŞKT.d),
register no. 1, entries 1 to 56. Entries 3, 4, 13 and 26 are not coded.

## Run it

The page loads its data with `fetch`, so it needs a web server:

```
python -m http.server
```

Then open http://localhost:8000. Publishing the folder with GitHub Pages works the same way.
There is no build step and no backend.

## Files

| File | What it holds |
|---|---|
| `index.html` | The page: map, register, patterns, data browser, method note. Leaflet from a CDN. |
| `dashboard_data.json` | The three tables coded from the register: `petitioners`, `locations`, `receivers`, joined on `decree_id`. This is the only copy of the data the page reads. |
| `interpretive_layer.json` | Four tables added later (`defendants`, `financial_claims`, `admin_hierarchy`, `resolutions`). Not yet checked against the register. The page keeps them out of every total and chart and shows them only on request. Delete the file and the page still works. |
| `basemap.json` | Coast, natural lakes and rivers for the map region, clipped from Natural Earth. Modern reservoirs and canals are removed. |
| `tools/build_basemap.py` | Rebuilds `basemap.json` from Natural Earth GeoJSON. |
| `tools/check_numbers.py` | Recomputes the counts the page shows, straight from `dashboard_data.json`. |
| `tools/split_tables_from_old_page.py` | One-off: how the four later tables were moved out of the old `index.html`. |

## What the page computes

- Complaint types are assigned by keyword from the English complaint summary. The rule table is in
  `index.html` (`RULES`) and is printed on the Method page.
- Coordinates within about 3 km are treated as one place. Distances are straight lines from Istanbul.
- Muharrem 1059 corresponds to about 15 January to 13 February 1649 (arithmetical conversion).

## Credits

Relief: Esri World Shaded Relief (optional; Esri's terms of use apply, see `RELIEF` in `index.html`).
Coast, lakes and rivers: Natural Earth (public domain). Type: Alegreya, Alegreya Sans, Amiri (SIL OFL).
Map library: Leaflet.
