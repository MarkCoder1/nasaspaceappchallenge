# NASADEM acquisition report

## Result: NOT ACQUIRED; PENDING AUTHENTICATION

CMR collection `C2763264762-LPCLOUD` was queried for the Atacama ROI `[-68, -24, -67, -23]`. The exact returned granules and protected data URLs are recorded in [earth_nasadem_cmr.json](../data/metadata/earth_nasadem_cmr.json).

The manifest contains these relevant NASADEM HGT granules:

- `G2816779962-LPCLOUD` / `NASADEM_HGT_s23w067`
- `G2816779993-LPCLOUD` / `NASADEM_HGT_s23w068`
- `G2816780543-LPCLOUD` / `NASADEM_HGT_s24w068`
- `G2816780587-LPCLOUD` / `NASADEM_HGT_s24w069`

CMR returned neighboring overlapping granules as well; no unnecessary granule was downloaded. The protected LP DAAC URL redirects to Earthdata OAuth and returns HTTP `401` without credentials.

No NASADEM ZIP, HGT, or substitute DEM exists in `data/raw/`. The pending state and EGM96/1-arc-second metadata are recorded in [earth_nasadem_hgt_v001.json](../data/metadata/earth_nasadem_hgt_v001.json).

Earth cannot be registered as `VALIDATED` until the user authenticates, downloads the selected granules, verifies checksums, and runs Earth-specific CRS, EGM96, latitude-spacing, NoData, and coverage validation.
