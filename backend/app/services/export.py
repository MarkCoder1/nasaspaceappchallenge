"""Scientific export generators for CSV, JSON, and PDF research reports."""

import csv
import io
import json
from datetime import datetime, timezone
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)

from app.services.similarity import (
    DATASET_REGISTRY,
    UNAVAILABLE_DATASETS,
    feature_definitions,
    methodology,
    similarity_status,
    stored_experiment,
)

REPOSITORY_ROOT = None  # set lazily below


def _repository_root() -> Any:
    from pathlib import Path

    global REPOSITORY_ROOT
    if REPOSITORY_ROOT is None:
        REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
    return REPOSITORY_ROOT


def _load_json(relative_path: str) -> dict[str, Any]:
    path = _repository_root() / relative_path
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "--"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def build_export_package() -> dict[str, Any]:
    """Assemble the complete, real scientific export package."""
    experiment = stored_experiment()
    status = similarity_status()
    baseline = experiment.get("baseline_result", {})
    provenance = experiment.get("provenance", {})
    primary_bootstrap = experiment.get("primary_bootstrap_320m_1000", {})
    convergence = experiment.get("bootstrap_convergence", {})
    seed_sensitivity = experiment.get("seed_sensitivity", {})
    feature_ablation = experiment.get("feature_ablation", {})
    weight_sensitivity = experiment.get("weight_sensitivity", {})
    spatial_diagnostics = experiment.get("spatial_diagnostics", {})
    normalization = experiment.get("normalization_sensitivity", {})
    benchmarks = experiment.get("benchmarks", {})

    datasets = provenance.get("datasets", [])

    return {
        "exported_at_utc": datetime.now(timezone.utc).isoformat(),
        "experiment": experiment.get("experiment", "moon_mars_phase7_validation"),
        "methodology": methodology(),
        "engine_status": {
            "engine": status.get("engine"),
            "production_comparisons_enabled": status.get("production_comparisons_enabled"),
            "validated_comparisons": status.get("validated_comparisons"),
            "comparison_capabilities": status.get("comparison_capabilities"),
        },
        "datasets": datasets,
        "unavailable_datasets": UNAVAILABLE_DATASETS,
        "feature_definitions": feature_definitions(),
        "results": {
            "baseline": baseline,
            "primary_bootstrap_320m_1000": primary_bootstrap,
            "bootstrap_convergence": convergence,
            "seed_sensitivity": seed_sensitivity,
            "feature_ablation": feature_ablation,
            "weight_sensitivity": weight_sensitivity,
            "spatial_diagnostics": spatial_diagnostics,
            "normalization_sensitivity": normalization,
            "benchmarks": benchmarks,
        },
        "provenance": provenance,
        "interpretation": experiment.get("interpretation", []),
    }


def export_json() -> dict[str, Any]:
    return build_export_package()


def _csv_rows(package: dict[str, Any]) -> list[list[str]]:
    rows: list[list[str]] = []

    def section(title: str) -> None:
        rows.append([title, "", "", "", "", ""])

    def row(*cells: Any) -> None:
        rows.append([str(c) for c in cells])

    baseline = package["results"].get("baseline", {})
    primary = package["results"].get("primary_bootstrap_320m_1000", {})

    section("EXPORT METADATA")
    row("exported_at_utc", package.get("exported_at_utc", ""), "", "", "", "")
    row("experiment", package.get("experiment", ""), "", "", "", "")
    row("tmsi_formula", package["methodology"].get("score", ""), "", "", "", "")

    section("SIMILARITY RESULT")
    row("field", "value", "body", "", "", "")
    row("similarity_index", _fmt(baseline.get("similarity_index")), "", "", "", "")
    row("confidence", baseline.get("confidence", ""), "", "", "", "")
    row("combined_distance", _fmt(baseline.get("combined_distance")), "", "", "", "")
    row("strongest_matches", ", ".join(baseline.get("strongest_matches", [])), "", "", "", "")
    row("largest_differences", ", ".join(baseline.get("largest_differences", [])), "", "", "", "")

    section("FEATURE STATISTICS")
    row("feature", "units", "target_mean", "target_median", "candidate_mean", "candidate_median")
    for feature_id, feature in baseline.get("features", {}).items():
        ts = feature.get("target_summary", {})
        cs = feature.get("candidate_summary", {})
        row(
            feature_id,
            feature.get("units", ""),
            _fmt(ts.get("mean")),
            _fmt(ts.get("median")),
            _fmt(cs.get("mean")),
            _fmt(cs.get("median")),
        )
        dist = feature.get("distance", {})
        row(
            "  " + feature_id + " distance",
            "wasserstein",
            _fmt(dist.get("wasserstein")),
            "ks",
            _fmt(dist.get("ks_statistic")),
            "normalized",
        )
        row(
            "  " + feature_id + " distance (cont.)",
            "pooled_iqr",
            _fmt(dist.get("pooled_iqr")),
            "normalized_distance",
            _fmt(dist.get("normalized_distance")),
            "sample_n",
            str(dist.get("sample_count_target")) + "/" + str(dist.get("sample_count_candidate")),
        )

    section("WEIGHTS")
    row("feature", "weight")
    for feature_id, weight in baseline.get("weights", {}).items():
        row(feature_id, _fmt(weight))

    section("BOOTSTRAP UNCERTAINTY (primary, 320 m, 1000 repetitions)")
    row("metric", "value")
    row("method", primary.get("method", ""))
    row("block_size_m", _fmt(primary.get("block_size_m")))
    row("repetitions", primary.get("repetitions", ""))
    row("seed", primary.get("seed", ""))
    row("tmsi_mean", _fmt(primary.get("tmsi_mean")))
    row("tmsi_median", _fmt(primary.get("tmsi_median")))
    row("tmsi_lower_95", _fmt(primary.get("tmsi_lower_95")))
    row("tmsi_upper_95", _fmt(primary.get("tmsi_upper_95")))
    row("interpretation", primary.get("interpretation", ""))

    section("BOOTSTRAP CONVERGENCE")
    row("repetitions", "tmsi_mean", "tmsi_lower_95", "tmsi_upper_95", "", "")
    for count, result in package["results"].get("bootstrap_convergence", {}).get("results", {}).items():
        row(
            count,
            _fmt(result.get("tmsi_mean")),
            _fmt(result.get("tmsi_lower_95")),
            _fmt(result.get("tmsi_upper_95")),
            "",
            "",
        )

    section("SEED SENSITIVITY")
    row("seed", "tmsi_mean", "tmsi_lower_95", "tmsi_upper_95", "", "")
    for seed, result in package["results"].get("seed_sensitivity", {}).items():
        row(
            seed,
            _fmt(result.get("tmsi_mean")),
            _fmt(result.get("tmsi_lower_95")),
            _fmt(result.get("tmsi_upper_95")),
            "",
            "",
        )

    section("BLOCK-SIZE SENSITIVITY")
    row("block_size_m", "tmsi_mean", "tmsi_lower_95", "tmsi_upper_95", "", "")
    bss = package["results"].get("feature_ablation", {}).get("all_features", {}).get("block_size_sensitivity", {})
    for size, result in bss.get("results", {}).items():
        row(
            size,
            _fmt(result.get("tmsi_mean")),
            _fmt(result.get("tmsi_lower_95")),
            _fmt(result.get("tmsi_upper_95")),
            "",
            "",
        )

    section("FEATURE ABLATION")
    row("feature", "similarity_index", "combined_distance", "", "", "")
    for feature_id, block in package["results"].get("feature_ablation", {}).items():
        score = block.get("score", {})
        row(
            feature_id,
            _fmt(score.get("similarity_index")),
            _fmt(score.get("combined_distance")),
            "",
            "",
            "",
        )

    section("WEIGHT SENSITIVITY")
    row("scheme", "similarity_index", "combined_distance", "", "", "")
    for scheme, block in package["results"].get("weight_sensitivity", {}).items():
        score = block.get("score", {})
        row(
            scheme,
            _fmt(score.get("similarity_index")),
            _fmt(score.get("combined_distance")),
            "",
            "",
            "",
        )

    section("SPATIAL AUTOCORRELATION (Moran's I)")
    row("dataset", "feature", "morans_i", "", "", "")
    spatial = package["results"].get("spatial_diagnostics", {})
    for dataset_id, features in spatial.items():
        if not isinstance(features, dict):
            continue
        for feature_id, diag in features.items():
            if not isinstance(diag, dict):
                continue
            row(dataset_id, feature_id, _fmt(diag.get("morans_i")), "", "", "")

    section("DATASETS / PROVENANCE")
    row("dataset_id", "body", "state", "resolution_m", "effective_resolution_m", "valid_percent")
    for dataset in package.get("datasets", []):
        fm = dataset.get("feature_metadata", {})
        row(
            dataset.get("id", ""),
            dataset.get("body", ""),
            dataset.get("state", ""),
            fm.get("resolution_m", ["--", "--"])[0] if isinstance(fm.get("resolution_m"), list) else "--",
            _fmt(fm.get("effective_resolution_m")),
            _fmt(fm.get("source_valid_percent")),
        )
    row("earth_nasadem_hgt_v001", "Earth", "PENDING", "--", "--", "--")
    row("earth_acquisition_limitation", "NASA Earthdata authentication unavailable; protected NASADEM granules returned HTTP 401.", "", "", "", "")

    section("LIMITATIONS")
    for limitation in baseline.get("limitations", []):
        row(limitation, "", "", "", "", "")
    for note in package.get("interpretation", []):
        row(note, "", "", "", "", "")

    return rows


def export_csv() -> str:
    package = build_export_package()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    for row in _csv_rows(package):
        writer.writerow(row)
    return buffer.getvalue()


def _header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#8e928b"))
    canvas.drawString(15 * mm, 8 * mm, "TERRA TWIN  |  PLANETARY TERRAIN MORPHOLOGY LAB")
    canvas.drawRightString(A4[0] - 15 * mm, 8 * mm, "Research report  |  Not a safety or habitability certification")
    canvas.setStrokeColor(colors.HexColor("#2b2e2a"))
    canvas.setLineWidth(0.5)
    canvas.line(15 * mm, 11 * mm, A4[0] - 15 * mm, 11 * mm)
    canvas.restoreState()


def export_pdf() -> bytes:
    package = build_export_package()
    baseline = package["results"].get("baseline", {})
    primary = package["results"].get("primary_bootstrap_320m_1000", {})
    provenance = package.get("provenance", {})
    datasets = provenance.get("datasets", [])

    buffer = io.BytesIO()
    doc = BaseDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=14 * mm,
        bottomMargin=16 * mm,
        title="Terra Twin - Moon-Mars Terrain Morphology Similarity Report",
        author="Terra Twin",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="page", frames=[frame], onPage=_header_footer)])

    styles = getSampleStyleSheet()
    mono = ParagraphStyle(
        "mono",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=7.6,
        leading=9.6,
        textColor=colors.HexColor("#dce5d2"),
    )
    h1 = ParagraphStyle(
        "h1",
        parent=styles["Heading1"],
        fontSize=16,
        leading=19,
        textColor=colors.HexColor("#e7e8e3"),
        spaceAfter=6,
    )
    h2 = ParagraphStyle(
        "h2",
        parent=styles["Heading2"],
        fontSize=11.5,
        leading=14,
        textColor=colors.HexColor("#e6bb77"),
        spaceBefore=10,
        spaceAfter=4,
    )
    body = ParagraphStyle(
        "body",
        parent=styles["BodyText"],
        fontSize=8.6,
        leading=12,
        textColor=colors.HexColor("#bbc5b8"),
        spaceAfter=5,
    )
    small = ParagraphStyle(
        "small",
        parent=body,
        fontSize=7.4,
        leading=9.5,
        textColor=colors.HexColor("#8e928b"),
    )

    story: list[Any] = []
    story.append(Paragraph("TERRA TWIN", h1))
    story.append(Paragraph("Planetary Terrain Morphology Similarity &mdash; Moon &lt;-&gt; Mars Research Report", body))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#2b2e2a"), spaceAfter=8))

    story.append(Paragraph("1. Research Question", h2))
    story.append(Paragraph(
        package["methodology"].get("research_question", ""), body
    ))
    story.append(Paragraph(
        "<b>Index:</b> Terrain Morphology Similarity Index (TMSI)  |  "
        "<b>Formula:</b> TMSI = 100 &times; exp(&minus;D)  |  "
        "<b>D:</b> weighted mean of pooled-IQR-normalized Wasserstein distances", body
    ))
    story.append(Paragraph(
        "<i>TMSI compares terrain-feature distributions only. It is not a probability, not a habitability score, "
        "and not a safety or landing-suitability certification.</i>", small
    ))

    story.append(Paragraph("2. Datasets and Provenance", h2))
    for dataset in datasets:
        manifest = dataset.get("manifest", {})
        fm = dataset.get("feature_metadata", {})
        story.append(Paragraph(
            f"<b>{dataset.get('id', '')}</b> &mdash; {dataset.get('body', '')} &nbsp;|&nbsp; state: <b>{dataset.get('state', '')}</b>", body
        ))
        story.append(Paragraph(
            f"Source: {manifest.get('official_url', manifest.get('source_url', '--'))}", small
        ))
        story.append(Paragraph(
            f"Resolution: {fm.get('resolution_m', ['--', '--'])[0] if isinstance(fm.get('resolution_m'), list) else '--'} m "
            f"| Effective resolution: {_fmt(fm.get('effective_resolution_m'))} m "
            f"| Valid coverage: {_fmt(fm.get('source_valid_percent'))}%", small
        ))
        story.append(Paragraph(
            f"Processed SHA-256: {dataset.get('processed_sha256', '--')} | Source SHA-256: {manifest.get('sha256', '--')}", small
        ))
        story.append(Spacer(1, 4))

    story.append(Paragraph("Earth &mdash; NASADEM (PENDING)", h2))
    story.append(Paragraph(
        "Earth data acquisition remains PENDING. NASA Earthdata authentication was unavailable and protected "
        "NASADEM granules returned HTTP 401. No Earth dataset has been downloaded or validated. Earth comparisons "
        "(Earth &harr; Moon, Earth &harr; Mars) remain disabled.", body
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("3. Results", h2))
    result_rows = [
        ["Metric", "Value"],
        ["TMSI (equal-weight baseline)", _fmt(baseline.get("similarity_index"))],
        ["Confidence", baseline.get("confidence", "")],
        ["Combined distance D", _fmt(baseline.get("combined_distance"))],
        ["Bootstrap mean (1000 reps)", _fmt(primary.get("tmsi_mean"))],
        ["95% interval lower", _fmt(primary.get("tmsi_lower_95"))],
        ["95% interval upper", _fmt(primary.get("tmsi_upper_95"))],
        ["Block size", f"{_fmt(primary.get('block_size_m'))} m"],
    ]
    t = Table(result_rows, colWidths=[72 * mm, 72 * mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Courier"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.6),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#bbc5b8")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#151a16")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#8e928b")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#2b2e2a")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#0f1210"), colors.HexColor("#121613")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))

    story.append(Paragraph("3.1 Feature-level distances", h2))
    feat_rows = [["Feature", "Units", "Wasserstein", "Pooled IQR", "Normalized d", "Target mean", "Candidate mean"]]
    for feature_id, feature in baseline.get("features", {}).items():
        ts = feature.get("target_summary", {})
        cs = feature.get("candidate_summary", {})
        dist = feature.get("distance", {})
        feat_rows.append([
            feature_id.replace("_", " ").title(),
            feature.get("units", ""),
            _fmt(dist.get("wasserstein")),
            _fmt(dist.get("pooled_iqr")),
            _fmt(dist.get("normalized_distance")),
            _fmt(ts.get("mean")),
            _fmt(cs.get("mean")),
        ])
    ft = Table(feat_rows, colWidths=[26 * mm, 10 * mm, 18 * mm, 18 * mm, 20 * mm, 20 * mm, 22 * mm], repeatRows=1)
    ft.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Courier"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.0),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#bbc5b8")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#151a16")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#8e928b")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#2b2e2a")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#0f1210"), colors.HexColor("#121613")]),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(ft)
    story.append(Spacer(1, 6))

    story.append(Paragraph("4. Uncertainty and Sensitivity", h2))
    story.append(Paragraph(
        "Intervals quantify spatial sampling variability under the stated block-size assumption; they are not "
        "calibrated probabilities or measurement error bars. Pixels are not independent observations because "
        "spatial autocorrelation is strong (Moran's I &gt; 0.97 for all features on both bodies).", body
    ))
    conv_rows = [["Reps", "TMSI mean", "95% lower", "95% upper"]]
    for count, result in package["results"].get("bootstrap_convergence", {}).get("results", {}).items():
        conv_rows.append([count, _fmt(result.get("tmsi_mean")), _fmt(result.get("tmsi_lower_95")), _fmt(result.get("tmsi_upper_95"))])
    ct = Table(conv_rows, colWidths=[30 * mm, 30 * mm, 30 * mm, 30 * mm])
    ct.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Courier"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.2),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#bbc5b8")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#151a16")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#8e928b")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#2b2e2a")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#0f1210"), colors.HexColor("#121613")]),
    ]))
    story.append(ct)
    story.append(Spacer(1, 6))

    story.append(Paragraph("5. Limitations", h2))
    for limitation in baseline.get("limitations", []):
        story.append(Paragraph(f"&bull; {limitation}", body))
    for note in package.get("interpretation", []):
        story.append(Paragraph(f"&bull; {note}", body))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#2b2e2a"), spaceAfter=5))
    story.append(Paragraph(
        "Provenance and reproducibility: every value above is traceable to the validated Moon (LOLA-derived DEM "
        "subset) and Mars (Jezero CTX DTM) datasets and the stored Phase 7 experiment record. "
        "Earth remains PENDING pending authenticated NASADEM acquisition.", small
    ))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
