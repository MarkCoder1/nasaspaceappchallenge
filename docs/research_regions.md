# TerraMatch research regions

These are bounded research targets, not claims that Earth reproduces another world. Coordinates are working centers or bounding boxes for selecting data; they must be preserved with the source product's body-fixed coordinate convention.

## Moon

### South polar highlands near Shackleton crater

- **Working center:** approximately 89.9 S, 0.0 E; use a bounded south-polar window rather than a single pixel.
- **Why this region:** the south pole combines permanently shadowed terrain with nearby illuminated ridges and crater rims. That makes it relevant to surface operations, illumination, thermal extremes, terrain access, and resource investigations.
- **Measurable properties:** LOLA elevation, derived slope and roughness, illumination/terrain geometry, and Diviner thermal observations where the selected product supports them.
- **Limitations:** illumination is time-dependent; a shaded terrain map is not an observation of local temperature or ice abundance. The candidate must not be reduced to a visual analog.
- **Sources:** [LOLA PDS archive](https://pds-geosciences.wustl.edu/missions/lro/lola.htm), [Diviner PDS archive](https://pds-geosciences.wustl.edu/missions/lro/diviner.htm), and [Lunar Orbital Data Explorer](https://ode.rsl.wustl.edu/moon/).

### Permanently shadowed regions as a context class

PSRs are treated as a context class adjacent to illuminated operational terrain, not as an independent “location” until a specific LOLA/Diviner product and polygon are selected. Their relevance is scientific and operational, but the absence of direct sunlight makes Earth surface-temperature analogies especially weak.

## Mars

### Jezero Crater

- **Working center:** 18.44 N, 77.45 E; USGS CTX DTM coverage is approximately 18.211 to 18.7212 N and 77.1605 to 77.699 E.
- **Why this region:** NASA identifies Jezero as an ancient environment with evidence of a past habitable setting. Perseverance is studying its delta, rocks, regolith, and sample-caching context, making it a scientifically meaningful target rather than a merely famous crater.
- **Measurable properties:** elevation, slope and roughness derived from the CTX DTM; later, geology and thermal context can be added only with product-level validation.
- **Sources:** [NASA Perseverance science](https://science.nasa.gov/mission/mars-2020-perseverance/science/) and [USGS CTX DTM product](https://astrogeology.usgs.gov/search/map/mars_2020_terrain_relative_navigation_ctx_dtm_mosaic).

### Gale Crater

- **Working center:** approximately 5.4 S, 137.8 E.
- **Why this region:** NASA states that Curiosity is assessing whether Gale ever supported microbial life and has found chemical and mineral evidence of ancient habitable environments. Its layered central mound makes it useful for studying relief and geological context.
- **Measurable properties:** MOLA-scale elevation and, after a product is selected, geology or thermal observations from PDS archives.
- **Limitations:** the first acquisition slice does not yet include a bounded Gale raster. Gale is a documented next target, not a fabricated result.
- **Sources:** [NASA Curiosity science](https://science.nasa.gov/mission/msl-curiosity/science/) and [Mars Orbital Data Explorer](https://ode.rsl.wustl.edu/mars/).

## Earth candidates

### Atacama volcanic high desert, northern Chile

- **Working center:** approximately 23.0 S, 67.75 W.
- **Measurable relevance:** high elevation, aridity, volcanic terrain, sparse vegetation, exposed rock, and strong thermal cycles. NASADEM coverage includes this latitude.
- **Cannot reproduce:** Martian atmospheric pressure, radiation, gravity, chemistry, or dust transport; it is an environmental analog for selected variables only.

### Mojave volcanic and desert terrain, southwestern United States

- **Working center:** approximately 35.0 N, 115.5 W.
- **Measurable relevance:** arid alluvial and volcanic landforms, exposed sediment, terrain relief, and accessible Earth observation coverage.
- **Cannot reproduce:** lunar vacuum, Mars atmosphere, planetary regolith chemistry, or extraterrestrial illumination.

### Mauna Kea volcanic terrain, Hawai'i

- **Working center:** approximately 19.8 N, 155.5 W.
- **Measurable relevance:** high-elevation basaltic volcanic surfaces, cinder cones, exposed rock, and strong relief. NASADEM coverage includes the region.
- **Cannot reproduce:** lunar or Martian gravity, atmospheric composition, radiation, and thermal boundary conditions.

The next phase should keep these three Earth regions manageable and use the same explicitly documented terrain variables before introducing temperature or geology.

## Phase 5 acquisition window

The lunar acquisition uses a 40.96 km square centered on the south-polar stereographic origin, with native bounds `[-20480, 20480]` metres in both axes. This is a bounded terrain window for the south-polar/Shackleton context, not a claim that every pixel is inside Shackleton crater and not a conversion from Earth coordinates.
