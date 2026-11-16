# Terra Twin — Phase 21: Construct Validity and Interpretation Audit

## 1. Executive Summary

**VERDICT: VERIFIED WITH QUALIFICATIONS**

The Terrain Morphology Similarity Index (TMSI) measures **terrain morphology distribution similarity** — specifically, the statistical similarity of elevation-derived feature distributions (slope, local relief, terrain ruggedness) between two planetary surfaces at a common physical scale.

**TMSI does NOT measure:** geological similarity, environmental similarity, physical equivalence, habitability, landing safety, or planetary body identity.

The current terminology and conclusions appropriately distinguish TMSI from geological equivalence in most cases, but some phrasing could be strengthened to prevent misinterpretation.

## 2. Construct Validity Analysis

### 2.1 What TMSI Actually Measures

| Construct | Measured by TMSI? | Evidence |
|-----------|-------------------|----------|
| Terrain morphology distribution similarity | ✅ Yes | Directly computed from slope, local relief, terrain ruggedness distributions |
| Statistical similarity between terrain-feature distributions | ✅ Yes | Wasserstein distance and KS statistic quantify distribution differences |
| Geological similarity | ❌ No | TMSI uses elevation-derived morphology only; no rock type, age, or process data |
| Environmental similarity | ❌ No | No climate, atmosphere, hydrology, or biological data |
| Physical equivalence | ❌ No | Different bodies have different gravity, atmosphere, temperature, etc. |
| Planetary body identity | ❌ No | Explicitly stated limitation (Phase 17 limitation #1) |
| Landing safety | ❌ No | No rock abundance, slope stability, or trafficability data |
| Habitability | ❌ No | No temperature, pressure, radiation, or chemistry data |

### 2.2 Construct Validity Threats

| Threat | Description | Severity | Mitigation |
|--------|-------------|----------|------------|
| **Construct underrepresentation** | TMSI captures only 3 of many possible terrain attributes (slope, relief, ruggedness) | High | Explicitly stated as terrain morphology only |
| **Construct overreach** | TMSI score could be misinterpreted as overall similarity | Moderate | Limitations section in all outputs |
| **Nominal fallacy** | Naming a score "similarity index" could imply broader meaning | Moderate | "TMSI is a terrain-morphology index, not..." disclaimers |
| **Feature correlation** | Slope, relief, ruggedness derived from same elevation data; not independent | Moderate | Not addressed in current implementation |
| **Resolution confounding** | Earth data at ~29.3 m native vs. 20 m processing grid | High | Documented in Phase 20.6 corrections |

### 2.3 What a High TMSI Score Means

A high TMSI score (e.g., Earth–Mars = 73.14) means:

- The **distributions** of slope, local relief, and terrain ruggedness values are statistically similar between the two locations
- The **relative frequency** of different terrain types (flat, moderate, steep) is comparable
- The **spatial variability** of elevation within the compared windows is similar

A high TMSI score does NOT mean:
- The terrains formed by the same processes
- The terrains have the same rock composition
- The terrains have the same erosion history
- The terrains are equally suitable for exploration
- One terrain is a good "analog" for the other in any geological sense

## 3. Terminology Audit

### 3.1 Current Terminology in Documentation

| Term | Usage | Assessment |
|------|-------|------------|
| "Earth analog" | Used in phase titles and descriptions | Acceptable with explicit limitation that it means morphology similarity only |
| "Terrain similarity" | Used throughout | Accurate when qualified as "terrain morphology" |
| "Similarity index" | TMSI name | Could imply broader similarity; mitigated by limitation statements |
| "Analog candidate" | Used in candidate registry | Acceptable with explicit CANDIDATE status |
| "READY_FOR_COMPARISON" | Candidate status | Accurate — means data readiness, not scientific validity |

### 3.2 Recommended Terminology Clarifications

| Current Phrase | Recommended Clarification |
|---------------|--------------------------|
| "Earth analog candidate" | "Earth terrain morphology candidate (morphology similarity only)" |
| "TMSI similarity score" | "TMSI terrain morphology distribution similarity index" |
| "High similarity" | "High terrain morphology distribution similarity" |
| "Analog readiness" | "Data readiness for morphology comparison" |

### 3.3 Statements Requiring Stronger Caveats

| Statement | Current Status | Recommended Revision |
|-----------|---------------|---------------------|
| "Earth deserts resemble Mars morphology more than Moon" | Phase 20 conclusion | Add: "in terms of terrain morphology distribution statistics for the specific regions compared" |
| "Earth–Mars TMSI = 73.14 shows high similarity" | Documented with limitations | Add: "based on ~29.3 m effective resolution Earth data from Death Valley region only" |

## 4. Interpretation Boundaries

### 4.1 What Can Be Defensibly Concluded

1. **Morphology distribution similarity:** Earth desert terrain (Death Valley region) has statistically similar slope, relief, and ruggedness distributions to Martian terrain (Jezero crater region), with TMSI = 73.14.

2. **Statistical distinguishability:** All three pairwise comparisons produce TMSI values with confidence intervals excluding 0 and 100, confirming the distributions are statistically different from each other.

3. **Distribution shape similarity:** Earth–Mars comparison shows low KS statistics (0.14–0.16), indicating similar distribution shapes for all three features.

### 4.2 What Cannot Be Concluded

1. **Geological equivalence:** TMSI similarity does not imply similar formation processes, rock types, or geological history.
2. **Planetary body identity:** TMSI cannot distinguish Moon from Mars from Earth (within-body ranges overlap with between-body ranges).
3. **Habitability:** No information about temperature, pressure, radiation, chemistry, or biology.
4. **Landing safety:** No information about rock abundance, slope stability, trafficability, or dust.
5. **Global representativeness:** Two USGS tiles do not represent all Earth environments.
6. **Causation:** Statistical similarity does not imply similar geologic processes.

## 5. Terminology Recommendations

### 5.1 Immediate Changes (Documentation Only)

| Location | Current | Recommended |
|----------|---------|-------------|
| Candidate registry | "Candidate name" + "planetary_relevance" | Add: "terrain morphology relevance (morphology only)" |
| Comparison results | "similarity_index" | Keep, but ensure legend explains: "TMSI = terrain morphology distribution similarity index" |
| Detail panel | "Planetary relevance: Mars" | Add: "morphology similarity relevance (not geological equivalence)" |

### 5.2 Future Changes (Code)

| Location | Current | Recommended |
|----------|---------|-------------|
| `similarity_index` field name | `similarity_index` | Consider `terrain_morphology_similarity_index` |
| `confidence` field | "HIGH" (qualitative) | Add: "confidence_qualitative: true" |

## 6. Classification

**Construct Validity: VERIFIED WITH QUALIFICATIONS**

TMSI validly measures terrain morphology distribution similarity. The construct is clearly defined and limitations are documented. However, the terminology could be strengthened to prevent misinterpretation, and the distinction between morphological similarity and geological equivalence should be more prominent in user-facing displays.

## 7. Recommendations

1. **Strengthen terminology:** Use "terrain morphology similarity" consistently instead of just "similarity"
2. **Add interpretive guardrails:** In candidate detail panels, explicitly state "This candidate is selected for terrain morphology comparison only. It does not imply geological equivalence."
3. **Document feature selection rationale:** Explain why slope, local relief, and terrain ruggedness were chosen and what other terrain attributes are not captured
4. **Consider construct validity statement:** Add a formal construct validity statement to the methodology documentation