"""Spatial block bootstrap uncertainty for correlated raster feature samples."""

from typing import Any

import numpy as np

from .distance import compare_distributions
from ..features.feature_extraction import TerrainFeatureSet


def _valid_blocks(values: np.ndarray, block_size: int, minimum_valid_fraction: float = 0.5) -> list[np.ndarray]:
    if values.ndim != 2:
        raise ValueError("Spatial bootstrap requires a two-dimensional raster feature")
    blocks: list[np.ndarray] = []
    for row in range(0, values.shape[0], block_size):
        for column in range(0, values.shape[1], block_size):
            block = values[row : row + block_size, column : column + block_size]
            valid = block[np.isfinite(block)]
            if valid.size >= block.size * minimum_valid_fraction:
                blocks.append(valid)
    return blocks


def _resample_blocks(values: np.ndarray, block_size: int, rng: np.random.Generator, sample_count: int = 4096) -> np.ndarray:
    blocks = _valid_blocks(values, block_size)
    return _resample_from_blocks(blocks, rng, sample_count)


def _resample_from_blocks(blocks: list[np.ndarray], rng: np.random.Generator, sample_count: int = 4096) -> np.ndarray:
    if not blocks:
        raise ValueError("No sufficiently valid spatial blocks available")
    selected = rng.integers(0, len(blocks), size=max(1, min(len(blocks), 32)))
    sample = np.concatenate([blocks[index] for index in selected])
    if sample.size > sample_count:
        sample = sample[rng.choice(sample.size, sample_count, replace=False)]
    return sample


def bootstrap_tmsi(
    target: TerrainFeatureSet,
    candidate: TerrainFeatureSet,
    weights: dict[str, float],
    *,
    block_size_m: float = 320.0,
    repetitions: int = 1000,
    seed: int = 42,
) -> dict[str, Any]:
    """Estimate TMSI uncertainty by resampling spatial blocks, not pixels."""
    target_cell = max(target.resolution_m)
    candidate_cell = max(candidate.resolution_m)
    target_block = max(2, round(block_size_m / target_cell))
    candidate_block = max(2, round(block_size_m / candidate_cell))
    rng = np.random.default_rng(seed)
    scores: list[float] = []
    feature_distances: dict[str, list[float]] = {name: [] for name in weights}
    target_blocks = {
        name: _valid_blocks(target.features[name].values, target_block)
        for name, weight in weights.items()
        if weight > 0 and name in target.features
    }
    candidate_blocks = {
        name: _valid_blocks(candidate.features[name].values, candidate_block)
        for name, weight in weights.items()
        if weight > 0 and name in candidate.features
    }
    for _ in range(repetitions):
        distances: dict[str, float] = {}
        for name, weight in weights.items():
            if weight <= 0 or name not in target.features or name not in candidate.features:
                continue
            target_sample = _resample_from_blocks(target_blocks[name], rng)
            candidate_sample = _resample_from_blocks(candidate_blocks[name], rng)
            distances[name] = compare_distributions(target_sample, candidate_sample).normalized_distance
            feature_distances[name].append(distances[name])
        total_weight = sum(weights[name] for name in distances)
        if total_weight:
            scores.append(float(100.0 * np.exp(-sum(weights[name] * distances[name] for name in distances) / total_weight)))
    if not scores:
        raise ValueError("Spatial bootstrap produced no valid repetitions")
    score_array = np.asarray(scores)
    return {
        "method": "non-overlapping spatial block bootstrap with replacement",
        "block_size_m": block_size_m,
        "target_block_size_cells": target_block,
        "candidate_block_size_cells": candidate_block,
        "repetitions": len(scores),
        "seed": seed,
        "tmsi_mean": float(score_array.mean()),
        "tmsi_median": float(np.median(score_array)),
        "tmsi_lower_95": float(np.percentile(score_array, 2.5)),
        "tmsi_upper_95": float(np.percentile(score_array, 97.5)),
        "feature_distance_means": {name: float(np.mean(values)) for name, values in feature_distances.items() if values},
        "interpretation": "Intervals quantify spatial sampling variability under this block-size assumption; they are not calibrated probabilities or measurement error bars.",
    }


def block_size_sensitivity(target: TerrainFeatureSet, candidate: TerrainFeatureSet, weights: dict[str, float]) -> dict[str, Any]:
    results = {}
    for block_size_m in (160.0, 320.0, 640.0):
        results[str(int(block_size_m))] = bootstrap_tmsi(target, candidate, weights, block_size_m=block_size_m, repetitions=32, seed=42)
    return {"block_sizes_m": [160, 320, 640], "results": results}


def seed_sensitivity(
    target: TerrainFeatureSet,
    candidate: TerrainFeatureSet,
    weights: dict[str, float],
    *,
    block_size_m: float = 320.0,
    repetitions: int = 1000,
    seeds: list[int] | None = None,
) -> dict[str, Any]:
    """Estimate TMSI uncertainty across multiple random seeds to assess seed sensitivity.

    Runs bootstrap_tmsi with multiple distinct random seeds using identical
    datasets, repetition count, block methodology, and other parameters.
    Reports per-seed TMSI estimates and confidence intervals, plus aggregate
    statistics across seeds.
    """
    if seeds is None:
        seeds = [42, 123, 456, 789, 1011]
    per_seed_results: list[dict[str, Any]] = []
    for seed in seeds:
        result = bootstrap_tmsi(
            target,
            candidate,
            weights,
            block_size_m=block_size_m,
            repetitions=repetitions,
            seed=seed,
        )
        per_seed_results.append(
            {
                "seed": seed,
                "tmsi_mean": result["tmsi_mean"],
                "tmsi_median": result["tmsi_median"],
                "tmsi_lower_95": result["tmsi_lower_95"],
                "tmsi_upper_95": result["tmsi_upper_95"],
                "repetitions": result["repetitions"],
                "block_size_m": result["block_size_m"],
            }
        )
    tmsi_values = [r["tmsi_mean"] for r in per_seed_results]
    lower_bounds = [r["tmsi_lower_95"] for r in per_seed_results]
    upper_bounds = [r["tmsi_upper_95"] for r in per_seed_results]
    max_tmsi_diff = max(tmsi_values) - min(tmsi_values)
    max_lower_diff = max(lower_bounds) - min(lower_bounds)
    max_upper_diff = max(upper_bounds) - min(upper_bounds)
    return {
        "block_size_m": block_size_m,
        "repetitions": repetitions,
        "seeds": seeds,
        "per_seed_results": per_seed_results,
        "aggregate": {
            "mean_tmsi_across_seeds": float(np.mean(tmsi_values)),
            "min_tmsi_across_seeds": float(min(tmsi_values)),
            "max_tmsi_across_seeds": float(max(tmsi_values)),
            "max_abs_tmsi_diff_across_seeds": float(max_tmsi_diff),
            "mean_lower_bound_across_seeds": float(np.mean(lower_bounds)),
            "mean_upper_bound_across_seeds": float(np.mean(upper_bounds)),
            "min_lower_bound_across_seeds": float(min(lower_bounds)),
            "max_upper_bound_across_seeds": float(max(upper_bounds)),
            "max_abs_lower_diff_across_seeds": float(max_lower_diff),
            "max_abs_upper_diff_across_seeds": float(max_upper_diff),
        },
        "interpretation": "Seed sensitivity results show how bootstrap confidence intervals "
        "vary across random seeds. Small differences indicate stable estimates; "
        "large differences indicate seed sensitivity.",
    }