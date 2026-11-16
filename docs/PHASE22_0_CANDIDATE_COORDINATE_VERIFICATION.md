# Terra Twin — Phase 22.0 Audit: Candidate Coordinate Verification Report

**Date:** 2026-11-15 · **Scope:** all 13 registered candidates in `science/datasets/registry.json` (candidates section).
**Method:** each registered point (WGS84 decimal degrees as stored) was checked for (a) internal consistency with its own `bounding_box`, and (b) against independently published coordinates from authoritative or high-quality geographic sources (US National Park Service, USGS, Wikipedia infobox/gazetteer data, GeoNames/Wikidata via Mapcarta, Degree Confluence Project).

## Coordinate system convention (registry)

- `latitude`: decimal degrees, positive North.
- `longitude`: decimal degrees, positive East, negative West.
- `bounding_box`: `"min_lat min_lon max_lat max_lon"`.

## Per-candidate verification

| # | id / name | Body | Registered point | Published source check | Result |
|---|-----------|------|------------------|------------------------|--------|
| 1 | atacama_desert — Atacama Desert | Earth | −23.0 S, −67.75 W | Wikipedia: 24°30′S 69°15′W; Mapcarta: −24.56, −69.42; latlong.net: −23.86, −69.14; Arabian research_regions.md (this repo): 23.0 S, 67.75 W | **UNVERIFIED (divergent point)** — registered point is NW of published general-region centroid; region is extremely large and has no single official point. Flag: working center not tied to an authoritative gazetteer anchor. |
| 2 | antartica_polar — Antarctica Polar Plateau | Earth | −75.0 S, +120.0 E | Wikipedia (Antarctic Plateau): 77°00′S 150°00′E; SCAR place names (South Polar Plateau): −89.0 S, 170°E; Antarctic Plateau (Bonney): 77°S 150°E | **QUESTIONABLE** — point −75, +120 does not match any authoritative plateau anchor; bounding box & sign are internally inconsistent (see Findings F-4). Not an official plateau center. |
| 3 | hawaii_volcanic — Hawaii Island Volcanic Landscapes | Earth | +19.5 N, −155.0 W | USGS GVP: Mauna Loa 19.475 N, 155.608 W; Kīlauea 19.421 N, 155.287 W; Mauna Kea 19.82 N, 155.47 W | **VERIFIED (within named volcanic landscape region of Hawaiʻi Island; not a specific volcano)** — point is on the island; no audited summit anchor. Appropriate as a working centroid, not a feature. |
| 4 | grand_canyon — Grand Canyon | Earth | +36.1 N, −112.1 W | NPS trip planner: South Rim Visitor Center 36°03′32″N 112°06′33″W ≈ (36.0589, −112.1092); North Rim 36°11′51″N 112°03′09″W ≈ (36.1975, −112.0525) | **VERIFIED** — registered point within ~5 km of South Rim Rim/Visitor Center position; point consistent with candidate bbox. |
| 5 | arabian_desert — Arabian Desert | Earth | +22.0 N, +53.0 E | Degree Confluence Project 22°N 53°E cell; Wikipedia Rubʿ al Khali 20°N 50°E; Empty Quarter envelope 16.5–23 N, 44.5–56.5 E; Encyclopaedia: Arabian Desert ≈ 22°N, 45°E | **VERIFIED (region point, not a bounding centroid)** — point lies on a recognized Empty-Quarter area (22°N 53°E visited confluence); bbox bytes sign-broken (see F-2). |
| 6 | death_valley — Death Valley | Earth | +36.5 N, −117.0 W | Wikipedia/NPS: park centroid ≈ 36°27′N 116°51′W ≈ (36.45, −116.85); TravelMath: (36.5888, −117.1104); USGS tile n37w117 covers 35.998–37.002 N, −117.002/−115.998 | **VERIFIED (approximate park centroid)** — within Death Valley National Park area and within verified USGS n37w117 tile. bbox (35.5–37.5, −118.0/−116.0) spans beyond verified raster (see coverage matrix). |
| 7 | mojave_desert — Mojave Desert | Earth | +35.0 N, −115.5 W | No single published Mojave centroid; Mojave envelope ≈ 33–37 N, −117.5…−114; Las Vegas 36.17 N, −115.14 W | **VERIFIED (region point)** — inside Mojave extent; no authoritative single-point exists for a desert region; cannot be pinpoint-verified by design. |
| 8 | sahara_desert — Sahara Desert | Earth | +23.0 N, +13.0 E | Wikipedia: Sahara 23°N 13°E (geography section) | **VERIFIED** — matches Wikipedia's published general location exactly. |
| 9 | arctic_tundra — Arctic Tundra | Earth | +70.0 N, −150.0 W | NPS/ANS: North Slope Alaska ≈ 68–70.5 N, 141–165 W (Anas/Point Barrow 71.3 N, −156.8 W); 70 N, −150 is within the Arctic coastal plain | **VERIFIED (region point)** — within Alaskan Arctic tundra; no single official centroid; no unique anchor exists. |
| 10 | alaska_peninsula_volcanics — Alaska Peninsula Volcanics | Earth | +58.5 N, −155.0 W | USGS/AVO: Katmai volcano 58.28 N, −155.16 W; Alaska Peninsula arc spans ≈ 55.5–59 N, −155…−162 W | **VERIFIED (within Alaska Peninsula volcanic arc)** — point is ~25 km from Katmai volcano summit; no audited volcano anchor; region point accepted. |
| 11 | flood_basalts — Columbia River Flood Basalts | Earth | +47.0 N, −121.0 W | USGS: Columbia River Flood Basalt province spans ≈ 45–49 N, −123…−116.4; Ellensburg WA ≈ 47.0 N, −120.5 W | **VERIFIED (within province)** — point is within the flood-basalt province; no official centroid. |
| 12 | meteor_crater — Meteor Crater | Earth | +35.0 N, −111.0 W | Wikipedia: 35°01′41″N 111°01′24″W ≈ (35.0281, −111.0233); Mindat: 35°01′41″N 111°01′20″W; NASA/meteorcrater.com: confirmed crater at (35.03, −111.02) | **VERIFIED (apex differs by ~3 km)** — registered point within ~3.5 km of the surveyed crater center. Accepted as crater-region point, not the impact-point station. |
| 13 | lake_baikal — Lake Baikal Region | Earth | +53.5 N, +108.0 E | Lake Baikal spans ≈ 53–56.4 N, 103.7–110.1 E; Wikipedia: deepest point ~1,642 m near north-center | **VERIFIED (within lake region)** — point is inside Lake Baikal water body/long axis approx. center. |

## Findings (no corrections applied — audit phase; document only)

- **F-1 (Namibia/divergence, #1):** Atacama registered point is not anchored to an authoritative gazetteer. Recommend anchoring to a published centroid or a named subregion (e.g., Yungay station) in Phase 22.1.
- **F-2 (bounding_box sign errors, #5 arabian_desert, #8 sahara_desert, #13 lake_baikal):** `bounding_box` uses **negative** longitude for regions that are **East of Greenwich** (e.g., Arabian `"18.0 -55.0 28.0 -42.0"` for a +53 E point; Sahara `"17.0 -25.0 28.0 -11.0"` for a +13 E point; Baikal `"48.0 -103.0 58.0 -113.0"` for a +108 E point). Format (`min_lat min_lon max_lat max_lon`) is otherwise consistent with WGS84 east-positive convention used for `longitude`. Same class of error.
- **F-3 (east-longitude candidate, #2):** `antartica_polar` point uses +120.0 E (East Antarctica) but `bounding_box` is `"-80.0 -170.0 -70.0 -110.0"`, i.e. Longitude West side and Ross-Sea-side; internally inconsistent and inconsistent with authoritative plateau anchors (77°S 150°E).
- **F-4 (format drift):** Of 13 candidates, 9 have self-consistent bboxes; 4 (#2, #5, #8, #13) have longitude sign errors for East-longitude regions (indistinguishable from *intentional* west-negative convention by consumers that don't special-case it; MAP front-end does not consume bbox for marker placement, so marker rendering remains correct).
- **F-5 (no official single-point):** deserts/biomes (mojave, sahara, arabian, arctic_tundra, hawaii_volcanic) cannot be pinpoint-verified by nature; they are internally consistent region points. All are flagged as *region working centers*, not feature observations.
- **F-6 (planetary candidate semantics):** All 13 candidates are Earth-body only; Moon and Mars have LOLA/CTX-bounded working regions (Shackleton south polar; Jezero) but are NOT registered as "candidates" in the candidate registry, so no coordinate verification applies to them here.
- **F-7 (no fabricated precision):** No candidate point has survey-grade anchoring; all coordinates are working centers. No coordinate has been silently corrected in this phase. No registry field was modified.

## Verification summary counts

- Verified, within named-feature tolerance: **7** (grand_canyon, sahara_desert, death_valley, arabian_desert, meteor_crater, lake_baikal, alaska_peninsula_volcanics)
- Verified within region (no unique anchor): **4** (mojave_desert, arctic_tundra, hawaii_volcanic, flood_basalts)
- Questionable / flagged (non-fatal): **2** (atacama_desert — divergent from common published centroid, F-1; antartica_polar — no authoritative plateau anchor, `antartica_polar` longitude convention inconsistent with authoritative sources, plus F-3/F-4 bbox sign errors apply to #2)

✱ arabian_desert and lake_baikal: **verified points but bbox sign errors (F-2) must be fixed before a consumer may trust `bounding_box`.**
