"""Independent benchmark registry; synthetic entries are never production findings."""

BENCHMARKS = (
    {
        "id": "synthetic_flat_dem",
        "kind": "synthetic_test_only",
        "expected_behavior": "identical flat feature distributions have zero distance",
        "production_eligible": False,
    },
    {
        "id": "synthetic_gradient_dem",
        "kind": "synthetic_test_only",
        "expected_behavior": "larger feature distribution differences reduce TMSI",
        "production_eligible": False,
    },
)


def validate_registry() -> None:
    identifiers = [benchmark["id"] for benchmark in BENCHMARKS]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Benchmark identifiers must be unique")
    if any(benchmark["production_eligible"] for benchmark in BENCHMARKS):
        raise ValueError("Unreviewed benchmark cannot be production eligible")