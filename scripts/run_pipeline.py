#!/usr/bin/env python3
"""Deterministic build/generate/validate/oracle/evaluate runner for CP data."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import re
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


class PipelineError(RuntimeError):
    pass


@dataclass
class ProcessResult:
    status: str
    returncode: int | None
    stdout: bytes
    stderr: bytes
    elapsed_ms: int


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def ensure_under(root: Path, path: Path, label: str) -> Path:
    resolved = path.resolve()
    try:
        common = Path(os.path.commonpath([str(root.resolve()), str(resolved)]))
    except ValueError as exc:
        raise PipelineError(f"{label} is on a different filesystem: {path}") from exc
    if common != root.resolve():
        raise PipelineError(f"{label} must stay under the configuration directory: {path}")
    return resolved


def run_process(
    command: list[str],
    input_data: bytes | None,
    timeout_ms: int,
    max_output_bytes: int,
) -> ProcessResult:
    started = time.perf_counter()
    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE if input_data is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as exc:
        return ProcessResult("RE", None, b"", str(exc).encode(), 0)

    try:
        stdout, stderr = process.communicate(input=input_data, timeout=timeout_ms / 1000)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        elapsed = round((time.perf_counter() - started) * 1000)
        return ProcessResult("TLE", process.returncode, stdout, stderr, elapsed)

    elapsed = round((time.perf_counter() - started) * 1000)
    if len(stdout) > max_output_bytes:
        return ProcessResult("OLE", process.returncode, stdout, stderr, elapsed)
    status = "OK" if process.returncode == 0 else "RE"
    return ProcessResult(status, process.returncode, stdout, stderr, elapsed)


class Pipeline:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path.resolve()
        self.root = self.config_path.parent
        try:
            self.config: dict[str, Any] = json.loads(self.config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PipelineError(f"cannot load configuration: {exc}") from exc

        self.task_path: Path | None = None
        self.task: dict[str, Any] = {}
        task_reference = self.config.get("task_contract")
        if isinstance(task_reference, str) and task_reference.strip():
            self.task_path = self.source_path(task_reference)
            try:
                loaded_task = json.loads(self.task_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise PipelineError(f"cannot load task contract: {exc}") from exc
            if not isinstance(loaded_task, dict):
                raise PipelineError("task contract must contain a JSON object")
            self.task = loaded_task

        self.build_dir = self.output_path("build_dir", "build")
        self.data_dir = self.output_path("data_dir", "data")
        self.logs_dir = self.output_path("logs_dir", "logs")
        self.manifest_path = self.output_path("manifest_path", "manifest.json")
        self.verdicts_path = self.output_path("verdicts_path", "verdicts.json")
        self.report_path = self.output_path("report_path", "report.md")
        self.testdata_config_path = self.data_dir / "config.yaml"
        self.max_output = int(self.config.get("max_output_bytes", 64 * 1024 * 1024))
        self.time_limit = int(self.config.get("time_limit_ms", 2000))
        self.memory_limit_mib = int(self.config.get("memory_limit_mib", 0))
        self.oracle_timeout = int(self.config.get("oracle_timeout_ms", self.time_limit))
        self.generator_timeout = int(self.config.get("generator_timeout_ms", 5000))
        self.validator_timeout = int(self.config.get("validator_timeout_ms", 2000))
        self.compare_mode = str(self.config.get("output_compare", "tokens"))
        self.executables: dict[str, Path] = {}
        self.compile_failures: dict[str, str] = {}
        self.gate_errors: list[str] = []
        self.environment: dict[str, Any] = {}
        self.timing_summary: dict[str, Any] = {}
        self.scoring_mode = ""
        self.total_points = 0.0
        self.scoring_units: list[dict[str, Any]] = []
        self.scoring_by_id: dict[str, dict[str, Any]] = {}
        self.scoring_unit_for_case: dict[str, dict[str, Any]] = {}
        self.polyhedron_zip_requested = False
        self.polyhedron_package_enabled = False
        self.polyhedron_package_path = self.root / "polyhedron.zip"
        self.polyhedron_package_metadata: dict[str, Any] | None = None
        self.judge_mode = ""
        self.validate_config()

    def output_path(self, key: str, default: str) -> Path:
        value = Path(str(self.config.get(key, default)))
        if value.is_absolute():
            path = value
        else:
            path = self.root / value
        return ensure_under(self.root, path, key)

    def source_path(self, value: str) -> Path:
        path = Path(value)
        return path.resolve() if path.is_absolute() else (self.root / path).resolve()

    @property
    def cases(self) -> list[dict[str, Any]]:
        return self.config["cases"]

    @property
    def case_ids(self) -> list[str]:
        return [str(case["id"]) for case in self.cases]

    def validate_config(self) -> None:
        required_sources = {"generator", "validator", "oracle"}
        sources = self.config.get("sources")
        if not isinstance(sources, dict) or not required_sources <= sources.keys():
            raise PipelineError("sources must define generator, validator, and oracle")

        count = self.config.get("case_count")
        cases = self.config.get("cases")
        if not isinstance(count, int) or count <= 0:
            raise PipelineError("case_count must be a positive integer")
        if not isinstance(cases, list) or len(cases) != count:
            raise PipelineError("cases length must equal case_count")

        seen: set[str] = set()
        for index, case in enumerate(cases, 1):
            if not isinstance(case, dict):
                raise PipelineError(f"case {index} must be an object")
            case_id = str(case.get("id", ""))
            if not re.fullmatch(r"[A-Za-z0-9_-]+", case_id):
                raise PipelineError(f"unsafe or empty case id: {case_id!r}")
            if case_id in seen:
                raise PipelineError(f"duplicate case id: {case_id}")
            seen.add(case_id)
            if not isinstance(case.get("seed"), int):
                raise PipelineError(f"case {case_id} seed must be an integer")
            if not isinstance(case.get("profile"), str) or not case["profile"]:
                raise PipelineError(f"case {case_id} profile must be nonempty")
            purpose = case.get("purpose")
            if not isinstance(purpose, str) or not purpose.strip():
                raise PipelineError(f"case {case_id} purpose must be nonempty")
            tags = case.get("tags")
            if (
                not isinstance(tags, list)
                or not tags
                or not all(isinstance(tag, str) and tag.strip() for tag in tags)
                or len(set(tags)) != len(tags)
            ):
                raise PipelineError(f"case {case_id} tags must be unique nonempty strings")
            group = case.get("group", "default")
            if not isinstance(group, str) or not group:
                raise PipelineError(f"case {case_id} group must be nonempty")
            if "points" in case:
                raise PipelineError(
                    f"case {case_id} must not define legacy points; use scoring.units"
                )
            if case.get("allow_duplicate") and not str(case.get("duplicate_reason", "")).strip():
                raise PipelineError(f"case {case_id} allows duplication but has no duplicate_reason")

        self.validate_testdata_config()
        self.validate_scoring()
        self.validate_task_contract()

        if self.compare_mode not in {"tokens", "exact"}:
            raise PipelineError("output_compare must be 'tokens' or 'exact'")
        self.validate_polyhedron_package()
        if self.memory_limit_mib <= 0:
            raise PipelineError("memory_limit_mib must be a positive integer")
        text_files = self.config.get("text_files", [])
        if not isinstance(text_files, list) or not all(isinstance(value, str) for value in text_files):
            raise PipelineError("text_files must be a list of paths")
        if self.config.get("calibrate_time_limit", False):
            runs = self.config.get("benchmark_runs", 3)
            if not isinstance(runs, int) or runs < 3:
                raise PipelineError("benchmark_runs must be at least 3 when calibrating")
            if not any(case.get("benchmark") for case in cases):
                raise PipelineError("calibrate_time_limit needs at least one benchmark case")
        for name, value in sources.items():
            if name in required_sources and not self.source_path(str(value)).is_file():
                raise PipelineError(f"missing {name} source: {value}")

        solutions = self.config.get("solutions", [])
        if not isinstance(solutions, list):
            raise PipelineError("solutions must be a list")
        names: set[str] = set()
        for item in solutions:
            if not isinstance(item, dict) or not item.get("name") or not item.get("source"):
                raise PipelineError("each solution needs name and source")
            name = str(item["name"])
            if not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
                raise PipelineError(f"unsafe solution name: {name!r}")
            if name in names:
                raise PipelineError(f"duplicate solution name: {name}")
            names.add(name)
            role = item.get("role")
            if role not in {"accepted", "subtask", "wrong"}:
                raise PipelineError(
                    f"solution {name} role must be accepted, subtask, or wrong"
                )
            for field in ("algorithm", "complexity", "supported_domain"):
                value = item.get(field)
                if not isinstance(value, str) or not value.strip():
                    raise PipelineError(f"solution {name} {field} must be nonempty")
            if role == "wrong":
                if item.get("defect_layer") not in {
                    "conceptual",
                    "complexity",
                    "implementation",
                }:
                    raise PipelineError(f"solution {name} has invalid defect_layer")
                for field in ("defect", "kill_profile"):
                    value = item.get(field)
                    if not isinstance(value, str) or not value.strip():
                        raise PipelineError(f"solution {name} {field} must be nonempty")
            expect = item.get("expect", {})
            self.validate_expectation(name, expect)
            if role == "accepted" and set(
                self.expand_case_ids(expect.get("must_pass", []), f"{name} must_pass")
            ) != set(self.case_ids):
                raise PipelineError(f"accepted solution {name} must pass every case")
            if role == "wrong" and not (
                expect.get("must_fail")
                or expect.get("must_fail_one_of")
                or "score_max" in expect
            ):
                raise PipelineError(f"wrong solution {name} needs a rejection expectation")

    def validate_polyhedron_package(self) -> None:
        package = self.config.get("polyhedron_package")
        if not isinstance(package, dict):
            raise PipelineError("polyhedron_package must be an object")

        enabled = package.get("enabled")
        if not isinstance(enabled, bool):
            raise PipelineError("polyhedron_package.enabled must be a boolean")
        path = package.get("path")
        if path != "polyhedron.zip":
            raise PipelineError("polyhedron_package.path must be polyhedron.zip")
        if enabled != self.polyhedron_zip_requested:
            raise PipelineError(
                "polyhedron_package.enabled does not match task polyhedron_zip preference"
            )
        if enabled and not self.judge_mode.lower().startswith("batch-"):
            raise PipelineError(
                "Polyhedron package requires standard batch judging"
            )
        if enabled and self.compare_mode not in {"tokens", "exact"}:
            raise PipelineError(
                "Polyhedron package requires tokens or exact output comparison"
            )

        self.polyhedron_package_enabled = enabled
        self.polyhedron_package_path = self.root / path

    def validate_testdata_config(self) -> None:
        config = self.config.get("testdata_config")
        if not isinstance(config, dict):
            raise PipelineError("testdata_config must be an object")

        path_value = config.get("path")
        if not isinstance(path_value, str) or not path_value.strip():
            raise PipelineError("testdata_config.path must be a nonempty path")
        path = Path(path_value)
        if not path.is_absolute():
            path = self.root / path
        self.testdata_config_path = ensure_under(
            self.root, path, "testdata_config.path"
        )
        if (
            self.testdata_config_path.parent != self.data_dir
            or self.testdata_config_path.name != "config.yaml"
        ):
            raise PipelineError(
                "testdata_config.path must be the config.yaml file in data_dir"
            )

        if any(re.fullmatch(r"[0-9]{3}", case_id) is None for case_id in self.case_ids):
            raise PipelineError(
                "testdata_config requires every case id to use exactly three digits"
            )

    def render_testdata_config(self) -> bytes:
        lines = [
            "type: default",
            "subtasks:",
        ]
        generated_ids = {
            unit["id"]: index
            for index, unit in enumerate(self.scoring_units, start=1)
        }
        for index, unit in enumerate(self.scoring_units, start=1):
            dependencies = ", ".join(
                str(generated_ids[dependency])
                for dependency in unit["depends_on"]
            )
            hydro_type = "min" if unit["type"] == "bundle" else "sum"
            lines.extend(
                [
                    f"- memory: {self.memory_limit_mib}MB",
                    f"  score: {unit['points']:g}",
                    f"  if: [{dependencies}]",
                    f"  id: {index}",
                    f"  type: {hydro_type}",
                    "  cases:",
                ]
            )
            for case_id in unit["cases"]:
                lines.extend(
                    [
                        f"  - input: {case_id}.in",
                        f"    output: {case_id}.ans",
                    ]
                )
        lines.append("")
        return "\n".join(lines).encode("utf-8")

    def write_testdata_config(self, check_only: bool = False) -> dict[str, Any]:
        for case_id in self.case_ids:
            for suffix in ("in", "ans"):
                path = self.data_dir / f"{case_id}.{suffix}"
                if not path.is_file():
                    raise PipelineError(
                        f"testdata_config references missing file: {path.name}"
                    )

        expected = self.render_testdata_config()
        if check_only:
            if not self.testdata_config_path.is_file():
                raise PipelineError(
                    f"missing test data configuration: {self.testdata_config_path}"
                )
            actual = self.testdata_config_path.read_bytes()
            if actual != expected:
                raise PipelineError(
                    "data/config.yaml is stale or does not match testdata_config"
                )
        else:
            atomic_write(self.testdata_config_path, expected)
            if self.testdata_config_path.read_bytes() != expected:
                raise PipelineError("data/config.yaml failed its write-back check")

        return {
            "path": str(self.testdata_config_path.relative_to(self.root)).replace(
                "\\", "/"
            ),
            "sha256": sha256_bytes(expected),
            "memory": f"{self.memory_limit_mib}MB",
            "subtasks": [
                {
                    "id": index,
                    "source_unit": unit["id"],
                    "score": unit["points"],
                    "type": "min" if unit["type"] == "bundle" else "sum",
                    "if": [
                        next(
                            dependency_index
                            for dependency_index, candidate in enumerate(
                                self.scoring_units, start=1
                            )
                            if candidate["id"] == dependency
                        )
                        for dependency in unit["depends_on"]
                    ],
                    "cases": unit["cases"],
                }
                for index, unit in enumerate(self.scoring_units, start=1)
            ],
        }

    def validate_task_contract(self) -> None:
        if self.task_path is None:
            raise PipelineError("task_contract is required")
        intake = self.task.get("intake")
        if not isinstance(intake, dict) or intake.get("status") != "complete":
            raise PipelineError("task contract intake.status must be 'complete'")
        preferences = intake.get("preferences")
        if not isinstance(preferences, dict):
            raise PipelineError("task contract intake.preferences must be an object")

        required = {
            "original_problem_dir",
            "output_dir",
            "case_count_policy",
            "deliverables",
            "scoring_mode",
            "scoring_plan",
            "statement_style",
            "rewrite_scope",
            "target_audience",
            "package_format",
            "polyhedron_zip",
        }
        missing = sorted(required - set(preferences))
        if missing:
            raise PipelineError(f"task contract has unresolved preferences: {missing}")

        values: dict[str, Any] = {}
        for field in sorted(required):
            entry = preferences[field]
            if not isinstance(entry, dict) or "value" not in entry:
                raise PipelineError(f"preference {field} must define value and source")
            source = entry.get("source")
            if source not in {"user", "delegated"}:
                raise PipelineError(
                    f"preference {field} source must be user or delegated, got {source!r}"
                )
            if source == "delegated" and not str(entry.get("decision_note", "")).strip():
                raise PipelineError(f"delegated preference {field} needs decision_note")
            values[field] = entry["value"]

        if preferences["original_problem_dir"]["source"] != "user":
            raise PipelineError("preference original_problem_dir must be supplied by the user")
        for field in ("original_problem_dir", "output_dir"):
            if not isinstance(values[field], str) or not values[field].strip():
                raise PipelineError(f"preference {field} must be a nonempty path")

        if preferences["case_count_policy"]["source"] != "user":
            raise PipelineError("preference case_count_policy must be supplied by the user")
        case_policy = values["case_count_policy"]
        if not isinstance(case_policy, dict):
            raise PipelineError("preference case_count_policy must be an object")
        policy_mode = case_policy.get("mode")
        if policy_mode == "fixed":
            count = case_policy.get("count")
            if (
                not isinstance(count, int)
                or isinstance(count, bool)
                or count <= 0
            ):
                raise PipelineError("fixed case_count_policy count must be positive")
            if count != len(self.cases):
                raise PipelineError(
                    "task contract fixed case count does not match pipeline cases"
                )
        elif policy_mode == "bounded_adaptive":
            minimum = case_policy.get("min")
            maximum = case_policy.get("max")
            if (
                not isinstance(minimum, int)
                or isinstance(minimum, bool)
                or not isinstance(maximum, int)
                or isinstance(maximum, bool)
                or minimum <= 0
                or minimum > maximum
            ):
                raise PipelineError("bounded case_count_policy needs 0 < min <= max")
            if not minimum <= len(self.cases) <= maximum:
                raise PipelineError(
                    "pipeline case count is outside the bounded case_count_policy"
                )
            if not case_policy.get("retain_existing"):
                raise PipelineError(
                    "bounded case_count_policy must retain supplied formal inputs"
                )
            if not case_policy.get("fill_by_hacks"):
                raise PipelineError(
                    "bounded case_count_policy must fill gaps with targeted hacks"
                )
        else:
            raise PipelineError("preference case_count_policy mode is invalid")

        deliverables = values["deliverables"]
        if (
            not isinstance(deliverables, list)
            or not deliverables
            or not all(isinstance(value, str) and value.strip() for value in deliverables)
            or len(set(deliverables)) != len(deliverables)
        ):
            raise PipelineError("preference deliverables must be unique nonempty strings")

        if values["scoring_mode"] not in {"per_case", "bundled", "mixed"}:
            raise PipelineError("preference scoring_mode is invalid")
        if values["scoring_mode"] != self.scoring_mode:
            raise PipelineError("task contract scoring_mode does not match pipeline scoring.mode")
        if policy_mode == "bounded_adaptive":
            if values["scoring_mode"] != "bundled":
                raise PipelineError(
                    "bounded case_count_policy is supported only for bundled scoring"
                )
            if case_policy["min"] < 20 or case_policy["max"] > 40:
                raise PipelineError(
                    "bounded bundled case_count_policy must stay within 20..40"
                )

        scoring_plan = values["scoring_plan"]
        if preferences["scoring_plan"]["source"] != "user":
            raise PipelineError("preference scoring_plan must be confirmed by the user")
        if not isinstance(scoring_plan, dict):
            raise PipelineError("preference scoring_plan must be an object")
        if scoring_plan.get("unit_authority") not in {
            "user-supplied",
            "delegated",
        }:
            raise PipelineError("scoring_plan unit_authority is invalid")
        if scoring_plan.get("expectation_mode") not in {"exact", "range"}:
            raise PipelineError("scoring_plan expectation_mode is invalid")

        style = values["statement_style"]
        if not isinstance(style, dict) or style.get("mode") not in {
            "formal",
            "light-context",
            "themed",
        }:
            raise PipelineError("preference statement_style needs a concrete supported mode")
        theme = style.get("theme")
        if style["mode"] == "themed" and (
            not isinstance(theme, str) or not theme.strip()
        ):
            raise PipelineError("themed statement_style requires a nonempty theme")
        for field in ("required_elements", "forbidden_elements"):
            elements = style.get(field, [])
            if not isinstance(elements, list) or not all(
                isinstance(value, str) and value.strip() for value in elements
            ):
                raise PipelineError(f"statement_style {field} must be a list of strings")
        if style["mode"] == "themed":
            if not isinstance(style.get("title_preference"), str) or not style[
                "title_preference"
            ].strip():
                raise PipelineError("themed statement_style requires title_preference")
            if not isinstance(style.get("allow_generic_names"), bool):
                raise PipelineError("themed statement_style requires allow_generic_names")
            if style.get("theme_term_scope") not in {"intro-only", "throughout"}:
                raise PipelineError("themed statement_style has invalid theme_term_scope")

        if values["rewrite_scope"] not in {
            "narrative-only",
            "constraints-and-subtasks",
            "equivalent-interface",
        }:
            raise PipelineError("preference rewrite_scope is invalid")
        for field in ("target_audience", "package_format"):
            if not isinstance(values[field], str) or not values[field].strip():
                raise PipelineError(f"preference {field} must be nonempty")

        if preferences["polyhedron_zip"]["source"] != "user":
            raise PipelineError("preference polyhedron_zip must be supplied by the user")
        if not isinstance(values["polyhedron_zip"], bool):
            raise PipelineError("preference polyhedron_zip must be a boolean")
        self.polyhedron_zip_requested = values["polyhedron_zip"]

        technical = self.task.get("technical_facts")
        required_technical = {
            "language_standard",
            "time_limit_ms",
            "memory_limit_mib",
            "judge_mode",
        }
        if not isinstance(technical, dict):
            raise PipelineError("task contract technical_facts must be an object")
        missing_technical = sorted(required_technical - set(technical))
        if missing_technical:
            raise PipelineError(
                f"task contract has unresolved technical facts: {missing_technical}"
            )
        technical_values: dict[str, Any] = {}
        for field in sorted(required_technical):
            entry = technical[field]
            if not isinstance(entry, dict) or "value" not in entry:
                raise PipelineError(f"technical fact {field} must define value and source")
            source = entry.get("source")
            if source not in {"user", "delegated", "discovered", "derived"}:
                raise PipelineError(f"technical fact {field} has unresolved source")
            if source in {"discovered", "derived"} and not str(
                entry.get("evidence", "")
            ).strip():
                raise PipelineError(f"technical fact {field} needs evidence")
            if source == "delegated" and not str(entry.get("decision_note", "")).strip():
                raise PipelineError(f"delegated technical fact {field} needs decision_note")
            technical_values[field] = entry["value"]

        for field in ("time_limit_ms", "memory_limit_mib"):
            value = technical_values[field]
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise PipelineError(f"technical fact {field} must be a positive integer")
        if technical_values["time_limit_ms"] != self.time_limit:
            raise PipelineError("task time_limit_ms does not match pipeline time_limit_ms")
        if technical_values["memory_limit_mib"] != self.memory_limit_mib:
            raise PipelineError(
                "task memory_limit_mib does not match pipeline memory_limit_mib"
            )

        language_standard = technical_values["language_standard"]
        if not isinstance(language_standard, str) or not language_standard.strip():
            raise PipelineError("technical fact language_standard must be nonempty")
        normalized_standard = language_standard.lower().replace(" ", "")
        flags = [str(flag).lower().replace(" ", "") for flag in self.config.get("cxxflags", [])]
        if not any(normalized_standard in flag for flag in flags):
            raise PipelineError("task language_standard does not match pipeline cxxflags")

        judge_mode = technical_values["judge_mode"]
        if not isinstance(judge_mode, str) or not judge_mode.strip():
            raise PipelineError("technical fact judge_mode must be nonempty")
        self.judge_mode = str(judge_mode)
        normalized_judge = judge_mode.lower()
        if "tokens" in normalized_judge and self.compare_mode != "tokens":
            raise PipelineError("task judge_mode tokens conflicts with output_compare")
        if "exact" in normalized_judge and self.compare_mode != "exact":
            raise PipelineError("task judge_mode exact conflicts with output_compare")

    def validate_scoring(self) -> None:
        scoring = self.config.get("scoring")
        if not isinstance(scoring, dict):
            raise PipelineError("scoring must be an object")
        mode = scoring.get("mode")
        if mode not in {"per_case", "bundled", "mixed"}:
            raise PipelineError("scoring.mode must be per_case, bundled, or mixed")
        total = scoring.get("total_points")
        if (
            not isinstance(total, (int, float))
            or isinstance(total, bool)
            or not math.isfinite(float(total))
            or float(total) <= 0
        ):
            raise PipelineError("scoring.total_points must be a positive finite number")
        units = scoring.get("units")
        if not isinstance(units, list) or not units:
            raise PipelineError("scoring.units must be a nonempty list")

        case_set = set(self.case_ids)
        by_id: dict[str, dict[str, Any]] = {}
        case_owner: dict[str, dict[str, Any]] = {}
        has_case_unit = False
        has_multi_bundle = False
        point_sum = 0.0
        for index, raw_unit in enumerate(units, 1):
            if not isinstance(raw_unit, dict):
                raise PipelineError(f"scoring unit {index} must be an object")
            unit_id = str(raw_unit.get("id", ""))
            if not re.fullmatch(r"[A-Za-z0-9_.-]+", unit_id):
                raise PipelineError(f"unsafe or empty scoring unit id: {unit_id!r}")
            if unit_id in by_id:
                raise PipelineError(f"duplicate scoring unit id: {unit_id}")
            unit_type = raw_unit.get("type")
            if unit_type not in {"case", "bundle"}:
                raise PipelineError(f"scoring unit {unit_id} has invalid type")
            members = raw_unit.get("cases")
            if (
                not isinstance(members, list)
                or not members
                or not all(isinstance(value, str) for value in members)
                or len(set(members)) != len(members)
            ):
                raise PipelineError(
                    f"scoring unit {unit_id} cases must be unique nonempty case ids"
                )
            unknown = set(members) - case_set
            if unknown:
                raise PipelineError(
                    f"scoring unit {unit_id} references unknown cases {sorted(unknown)}"
                )
            if unit_type == "case" and len(members) != 1:
                raise PipelineError(f"case scoring unit {unit_id} must contain exactly one case")
            points = raw_unit.get("points")
            if (
                not isinstance(points, (int, float))
                or isinstance(points, bool)
                or not math.isfinite(float(points))
                or float(points) < 0
            ):
                raise PipelineError(
                    f"scoring unit {unit_id} points must be a nonnegative finite number"
                )
            dependencies = raw_unit.get("depends_on", [])
            if (
                not isinstance(dependencies, list)
                or not all(isinstance(value, str) and value for value in dependencies)
                or len(set(dependencies)) != len(dependencies)
            ):
                raise PipelineError(
                    f"scoring unit {unit_id} depends_on must contain unique unit ids"
                )
            normalized = {
                **raw_unit,
                "id": unit_id,
                "type": unit_type,
                "cases": list(members),
                "points": float(points),
                "depends_on": list(dependencies),
            }
            by_id[unit_id] = normalized
            point_sum += float(points)
            has_case_unit = has_case_unit or unit_type == "case"
            has_multi_bundle = has_multi_bundle or (
                unit_type == "bundle" and len(members) > 1
            )
            for case_id in members:
                if case_id in case_owner:
                    raise PipelineError(
                        f"case {case_id} belongs to both {case_owner[case_id]['id']} and {unit_id}"
                    )
                case_owner[case_id] = normalized

        uncovered = sorted(case_set - set(case_owner))
        if uncovered:
            raise PipelineError(f"cases missing from scoring units: {uncovered}")
        if not math.isclose(point_sum, float(total), rel_tol=0.0, abs_tol=1e-9):
            raise PipelineError(
                f"scoring unit points total {point_sum:g}, expected {float(total):g}"
            )

        for unit_id, unit in by_id.items():
            unknown = set(unit["depends_on"]) - set(by_id)
            if unknown:
                raise PipelineError(
                    f"scoring unit {unit_id} depends on unknown units {sorted(unknown)}"
                )
            if unit_id in unit["depends_on"]:
                raise PipelineError(f"scoring unit {unit_id} depends on itself")

        state: dict[str, int] = {}

        def visit(unit_id: str, trail: list[str]) -> None:
            marker = state.get(unit_id, 0)
            if marker == 1:
                raise PipelineError(
                    "scoring dependency cycle: " + " -> ".join([*trail, unit_id])
                )
            if marker == 2:
                return
            state[unit_id] = 1
            for dependency in by_id[unit_id]["depends_on"]:
                visit(dependency, [*trail, unit_id])
            state[unit_id] = 2

        for unit_id in by_id:
            visit(unit_id, [])

        if mode == "per_case" and any(
            unit["type"] != "case" for unit in by_id.values()
        ):
            raise PipelineError("per_case scoring requires only single-case units")
        if mode == "bundled" and (
            any(unit["type"] != "bundle" for unit in by_id.values())
            or not has_multi_bundle
        ):
            raise PipelineError(
                "bundled scoring requires bundle units and at least one multi-case bundle"
            )
        if mode == "mixed" and not (has_case_unit and has_multi_bundle):
            raise PipelineError(
                "mixed scoring requires a case unit and a multi-case bundle"
            )

        self.scoring_mode = str(mode)
        self.total_points = float(total)
        self.scoring_units = list(by_id.values())
        self.scoring_by_id = by_id
        self.scoring_unit_for_case = case_owner

    def validate_expectation(self, name: str, expect: Any) -> None:
        if not isinstance(expect, dict):
            raise PipelineError(f"solution {name} expect must be an object")
        case_keys = {"must_pass", "must_fail", "must_fail_one_of"}
        score_keys = {"score_min", "score_max"}
        allowed = case_keys | score_keys
        unknown = set(expect) - allowed
        if unknown:
            raise PipelineError(f"solution {name} has unknown expectations: {sorted(unknown)}")
        for key in case_keys:
            if key not in expect:
                continue
            values = expect[key]
            if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
                raise PipelineError(f"solution {name} {key} must be a list of case ids")
            self.expand_case_ids(values, f"solution {name} {key}")
        for key in score_keys:
            if key in expect and (
                not isinstance(expect[key], (int, float)) or isinstance(expect[key], bool)
            ):
                raise PipelineError(f"solution {name} {key} must be numeric")
            if key in expect and not 0 <= float(expect[key]) <= self.total_points:
                raise PipelineError(
                    f"solution {name} {key} must stay within 0 and {self.total_points:g}"
                )
        if expect.get("score_min", float("-inf")) > expect.get("score_max", float("inf")):
            raise PipelineError(f"solution {name} score_min exceeds score_max")

    def expand_case_ids(self, values: Iterable[str], label: str) -> list[str]:
        values = list(values)
        if "*" in values:
            if len(values) != 1:
                raise PipelineError(f"{label}: '*' must be the only entry")
            return self.case_ids
        unknown = set(values) - set(self.case_ids)
        if unknown:
            raise PipelineError(f"{label}: unknown cases {sorted(unknown)}")
        return values

    def score_row(
        self, row: dict[str, dict[str, Any]]
    ) -> tuple[float, dict[str, dict[str, Any]]]:
        earned: dict[str, bool] = {}
        breakdown: dict[str, dict[str, Any]] = {}

        def unit_earned(unit_id: str) -> bool:
            if unit_id in earned:
                return earned[unit_id]
            unit = self.scoring_by_id[unit_id]
            cases_passed = all(row[case_id]["verdict"] == "AC" for case_id in unit["cases"])
            dependencies_passed = all(
                unit_earned(dependency) for dependency in unit["depends_on"]
            )
            awarded = cases_passed and dependencies_passed
            earned[unit_id] = awarded
            breakdown[unit_id] = {
                "type": unit["type"],
                "cases": list(unit["cases"]),
                "depends_on": list(unit["depends_on"]),
                "points": unit["points"],
                "cases_passed": cases_passed,
                "dependencies_passed": dependencies_passed,
                "awarded": awarded,
            }
            return awarded

        for unit in self.scoring_units:
            unit_earned(unit["id"])
        score = sum(
            unit["points"] for unit in self.scoring_units if earned[unit["id"]]
        )
        ordered = {unit["id"]: breakdown[unit["id"]] for unit in self.scoring_units}
        return score, ordered

    def executable_path(self, key: str) -> Path:
        suffix = ".exe" if os.name == "nt" else ""
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", key)
        return self.build_dir / f"{safe}{suffix}"

    def compile_one(self, key: str, source: Path, fatal: bool) -> None:
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        output = self.executable_path(key)
        compiler = str(self.config.get("compiler", "g++"))
        flags = [str(flag) for flag in self.config.get("cxxflags", ["-std=c++14", "-O2", "-Wall", "-Wextra"])]
        command = [compiler, *flags, str(source), "-o", str(output)]
        result = run_process(command, None, int(self.config.get("compile_timeout_ms", 30000)), self.max_output)
        log = b"COMMAND: " + shlex.join(command).encode() + b"\n\n" + result.stdout + result.stderr
        atomic_write(self.logs_dir / f"compile-{key}.log", log)
        if result.status != "OK":
            message = f"compile failed for {key}; see {self.logs_dir / f'compile-{key}.log'}"
            if fatal:
                raise PipelineError(message)
            self.compile_failures[key] = message
            return
        self.executables[key] = output

    def check_lf_files(self) -> None:
        if not self.config.get("require_lf", True):
            return
        sources = self.config["sources"]
        paths = [self.config_path]
        if self.task_path is not None:
            paths.append(self.task_path)
        paths.extend(self.source_path(str(sources[key])) for key in ("generator", "validator", "oracle"))
        paths.extend(
            self.source_path(str(solution["source"]))
            for solution in self.config.get("solutions", [])
            if self.source_path(str(solution["source"])).is_file()
        )
        paths.extend(self.source_path(value) for value in self.config.get("text_files", []))
        for path in dict.fromkeys(paths):
            if not path.is_file():
                self.gate_errors.append(f"configured text file is missing: {path}")
                continue
            if b"\r" in path.read_bytes():
                self.gate_errors.append(f"text file is not LF-only: {path}")

    def record_environment(self) -> None:
        compiler = str(self.config.get("compiler", "g++"))
        flags = [str(flag) for flag in self.config.get("cxxflags", ["-std=c++14", "-O2", "-Wall", "-Wextra"])]
        version = run_process([compiler, "--version"], None, 5000, self.max_output)
        version_line = (version.stdout or version.stderr).decode(errors="replace").splitlines()
        self.environment = {
            "platform": platform.platform(),
            "cpu": os.environ.get("PROCESSOR_IDENTIFIER") or platform.processor() or "unknown",
            "logical_cpu_count": os.cpu_count(),
            "compiler": compiler,
            "compiler_version": version_line[0] if version_line else "unavailable",
            "cxxflags": flags,
        }

    def build(self, include_solutions: bool) -> None:
        self.check_lf_files()
        self.record_environment()
        sources = self.config["sources"]
        for key in ("generator", "validator", "oracle"):
            self.compile_one(key, self.source_path(str(sources[key])), fatal=True)
        if include_solutions:
            for solution in self.config.get("solutions", []):
                key = "solution-" + str(solution["name"])
                source = self.source_path(str(solution["source"]))
                if not source.is_file():
                    self.compile_failures[key] = f"missing source: {source}"
                    continue
                self.compile_one(key, source, fatal=False)

    def format_case_args(
        self, config_key: str, default: list[str], case: dict[str, Any], index: int
    ) -> list[str]:
        template = self.config.get(config_key, default)
        if not isinstance(template, list):
            raise PipelineError(f"{config_key} must be a list")
        scoring_unit = self.scoring_unit_for_case[str(case["id"])]
        fields = {
            "case_id": str(case["id"]),
            "case_index": str(index),
            "seed": str(case["seed"]),
            "profile": str(case["profile"]),
            "group": str(case.get("group", "default")),
            "points": str(scoring_unit["points"]),
            "scoring_unit": str(scoring_unit["id"]),
        }
        try:
            return [str(part).format(**fields) for part in template]
        except KeyError as exc:
            raise PipelineError(f"unknown {config_key} placeholder: {exc}") from exc

    def format_generator_args(self, case: dict[str, Any], index: int) -> list[str]:
        return self.format_case_args(
            "generator_args",
            ["--case", "{case_index}", "--seed", "{seed}", "--profile", "{profile}"],
            case,
            index,
        )

    def format_validator_args(self, case: dict[str, Any], index: int) -> list[str]:
        return self.format_case_args("validator_args", [], case, index)

    def normalize_generated_text(self, data: bytes, label: str) -> bytes:
        if self.config.get("normalize_lf", True):
            data = data.replace(b"\r\n", b"\n")
        if self.config.get("require_lf", True) and b"\r" in data:
            raise PipelineError(f"{label} contains a non-LF carriage return")
        return data

    def generate(self) -> dict[str, Any]:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        manifest_cases: list[dict[str, Any]] = []
        seen_input_hashes: dict[str, str] = {}
        benchmark_measurements: dict[str, list[int]] = {}
        generator = self.executables["generator"]
        validator = self.executables["validator"]
        oracle = self.executables["oracle"]

        for index, case in enumerate(self.cases, 1):
            case_id = str(case["id"])
            source_input = case.get("input_path")
            provenance = "existing" if source_input else "generated"
            source_input_hash = None
            if source_input:
                source_path = (self.root / str(source_input)).resolve()
                if not source_path.is_file():
                    raise PipelineError(
                        f"adopted input for case {case_id} does not exist: {source_input}"
                    )
                source_bytes = source_path.read_bytes()
                source_input_hash = sha256_bytes(source_bytes)
                first_stdout = self.normalize_generated_text(
                    source_bytes, f"adopted input {case_id}"
                )
                atomic_write(
                    self.logs_dir / f"adopt-{case_id}.log",
                    (
                        f"source={source_path}\n"
                        f"source_sha256={source_input_hash}\n"
                        f"delivered_sha256={sha256_bytes(first_stdout)}\n"
                    ).encode(),
                )
            else:
                command = [str(generator), *self.format_generator_args(case, index)]
                first = run_process(command, None, self.generator_timeout, self.max_output)
                atomic_write(self.logs_dir / f"generate-{case_id}.log", first.stderr)
                if first.status != "OK":
                    raise PipelineError(f"generator {first.status} on case {case_id}")
                first_stdout = self.normalize_generated_text(
                    first.stdout, f"generated input {case_id}"
                )

                if self.config.get("check_reproducibility", True):
                    second = run_process(command, None, self.generator_timeout, self.max_output)
                    if second.status == "OK":
                        second.stdout = self.normalize_generated_text(
                            second.stdout, f"repeated generated input {case_id}"
                        )
                    if second.status != "OK" or first_stdout != second.stdout:
                        raise PipelineError(f"generator is not reproducible on case {case_id}")

            input_hash = sha256_bytes(first_stdout)
            if input_hash in seen_input_hashes:
                earlier = seen_input_hashes[input_hash]
                if not case.get("allow_duplicate"):
                    self.gate_errors.append(f"duplicate input cases: {earlier} and {case_id}")
            else:
                seen_input_hashes[input_hash] = case_id

            validator_command = [str(validator), *self.format_validator_args(case, index)]
            checked = run_process(validator_command, first_stdout, self.validator_timeout, self.max_output)
            atomic_write(self.logs_dir / f"validate-{case_id}.log", checked.stdout + checked.stderr)
            if checked.status != "OK":
                raise PipelineError(f"validator rejected case {case_id}")

            extra_token = first_stdout + b"\n__VALIDATOR_MUST_REJECT_EXTRA_TOKEN__\n"
            attacked = run_process(validator_command, extra_token, self.validator_timeout, self.max_output)
            atomic_write(self.logs_dir / f"validate-extra-token-{case_id}.log", attacked.stdout + attacked.stderr)
            if attacked.status == "OK":
                raise PipelineError(f"validator accepted an extra token on case {case_id}")

            answered = run_process([str(oracle)], first_stdout, self.oracle_timeout, self.max_output)
            oracle_log = bytearray(answered.stderr)
            if answered.status != "OK":
                raise PipelineError(f"oracle {answered.status} on case {case_id}")
            answered.stdout = self.normalize_generated_text(answered.stdout, f"generated answer {case_id}")

            oracle_runs = [answered.elapsed_ms]
            if case.get("benchmark"):
                run_count = int(self.config.get("benchmark_runs", 3))
                for run_index in range(2, run_count + 1):
                    repeated = run_process([str(oracle)], first_stdout, self.oracle_timeout, self.max_output)
                    oracle_log.extend(b"\n--- benchmark run " + str(run_index).encode() + b" ---\n")
                    oracle_log.extend(repeated.stderr)
                    if repeated.status != "OK":
                        raise PipelineError(f"oracle {repeated.status} on benchmark case {case_id}")
                    repeated.stdout = self.normalize_generated_text(
                        repeated.stdout, f"repeated answer {case_id}"
                    )
                    if repeated.stdout != answered.stdout:
                        raise PipelineError(f"oracle output changed across benchmark runs on case {case_id}")
                    oracle_runs.append(repeated.elapsed_ms)
                benchmark_measurements[case_id] = oracle_runs
            atomic_write(self.logs_dir / f"oracle-{case_id}.log", bytes(oracle_log))

            source_answer_hash = None
            if case.get("answer_path"):
                source_answer_path = (self.root / str(case["answer_path"])).resolve()
                if not source_answer_path.is_file():
                    raise PipelineError(
                        f"supplied answer for case {case_id} does not exist: "
                        f"{case['answer_path']}"
                    )
                source_answer_bytes = source_answer_path.read_bytes()
                source_answer_hash = sha256_bytes(source_answer_bytes)
                normalized_source_answer = self.normalize_generated_text(
                    source_answer_bytes, f"supplied answer {case_id}"
                )
                if normalized_source_answer.split() != answered.stdout.split():
                    raise PipelineError(
                        f"supplied answer disagrees with oracle on case {case_id}"
                    )

            input_path = self.data_dir / f"{case_id}.in"
            answer_path = self.data_dir / f"{case_id}.ans"
            atomic_write(input_path, first_stdout)
            atomic_write(answer_path, answered.stdout)
            manifest_cases.append(
                {
                    **case,
                    "input": str(input_path.relative_to(self.root)),
                    "answer": str(answer_path.relative_to(self.root)),
                    "provenance": provenance,
                    "source_input": str(source_input) if source_input else None,
                    "source_input_sha256": source_input_hash,
                    "source_answer": (
                        str(case.get("answer_path")) if case.get("answer_path") else None
                    ),
                    "source_answer_sha256": source_answer_hash,
                    "input_sha256": input_hash,
                    "answer_sha256": sha256_bytes(answered.stdout),
                    "input_bytes": len(first_stdout),
                    "answer_bytes": len(answered.stdout),
                    "oracle_runs_ms": oracle_runs,
                    "oracle_slowest_ms": max(oracle_runs),
                }
            )

        if self.config.get("calibrate_time_limit", False):
            slowest_ms = max(max(runs) for runs in benchmark_measurements.values())
            multiplier = float(self.config.get("time_limit_multiplier", 3.0))
            minimum = int(self.config.get("time_limit_min_seconds", 1))
            maximum = int(self.config.get("time_limit_max_seconds", 5))
            raw_seconds = math.ceil(slowest_ms * multiplier / 1000)
            suggested = min(max(raw_seconds, minimum), maximum)
            self.timing_summary = {
                "benchmark_runs": benchmark_measurements,
                "slowest_ms": slowest_ms,
                "multiplier": multiplier,
                "unclamped_seconds": raw_seconds,
                "suggested_seconds": suggested,
                "allowed_seconds": [minimum, maximum],
            }
            if raw_seconds > maximum:
                self.gate_errors.append(
                    f"derived time limit {raw_seconds}s exceeds configured maximum {maximum}s"
                )

        expected = {f"{case_id}.{suffix}" for case_id in self.case_ids for suffix in ("in", "ans")}
        actual = {path.name for path in self.data_dir.glob("*.*") if path.suffix in {".in", ".ans"}}
        extras = sorted(actual - expected)
        missing = sorted(expected - actual)
        if missing:
            self.gate_errors.append(f"missing configured data files: {missing}")
        if extras:
            self.gate_errors.append(f"unconfigured data files present (not deleted): {extras}")
        testdata_config = self.write_testdata_config()

        sources = self.config["sources"]
        generation_decision = "no_go" if self.gate_errors else "go"
        manifest = {
            "decision": generation_decision,
            "completed_gate": "generation",
            "blocking_issues": list(self.gate_errors),
            "next_actions": (
                ["repair generation blockers and rerun invalidated gates"]
                if self.gate_errors
                else ["run candidate evaluation and independent acceptance"]
            ),
            "case_count": len(manifest_cases),
            "config_sha256": sha256_file(self.config_path),
            "task_contract_sha256": (
                sha256_file(self.task_path) if self.task_path is not None else None
            ),
            "source_sha256": {
                key: sha256_file(self.source_path(str(sources[key])))
                for key in ("generator", "validator", "oracle")
            },
            "environment": self.environment,
            "timing": self.timing_summary,
            "scoring": self.config["scoring"],
            "testdata_config": testdata_config,
            "cases": manifest_cases,
            "gate_errors": list(self.gate_errors),
        }
        atomic_write(self.manifest_path, (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode())
        return manifest

    def outputs_equal(self, actual: bytes, expected: bytes) -> bool:
        if self.compare_mode == "exact":
            return actual == expected
        return actual.split() == expected.split()

    def evaluate(self) -> dict[str, Any]:
        self.write_testdata_config(check_only=True)
        matrix: dict[str, dict[str, dict[str, Any]]] = {}
        scores: dict[str, float] = {}
        score_breakdowns: dict[str, dict[str, dict[str, Any]]] = {}
        expectation_errors: list[str] = []
        for solution in self.config.get("solutions", []):
            name = str(solution["name"])
            key = "solution-" + name
            row: dict[str, dict[str, Any]] = {}
            if key in self.compile_failures:
                for case_id in self.case_ids:
                    row[case_id] = {"verdict": "CE", "time_ms": 0}
            else:
                executable = self.executables[key]
                multiplier = float(solution.get("time_multiplier", 1.0))
                timeout = max(1, round(self.time_limit * multiplier))
                arguments = [str(value) for value in solution.get("args", [])]
                for case_id in self.case_ids:
                    input_data = (self.data_dir / f"{case_id}.in").read_bytes()
                    expected = (self.data_dir / f"{case_id}.ans").read_bytes()
                    result = run_process([str(executable), *arguments], input_data, timeout, self.max_output)
                    verdict = result.status
                    if verdict == "OK":
                        verdict = "AC" if self.outputs_equal(result.stdout, expected) else "WA"
                    atomic_write(self.logs_dir / f"run-{name}-{case_id}.log", result.stderr)
                    row[case_id] = {"verdict": verdict, "time_ms": result.elapsed_ms}
            matrix[name] = row
            score, breakdown = self.score_row(row)
            scores[name] = score
            score_breakdowns[name] = breakdown
            expectation_errors.extend(
                self.check_expectations(name, row, score, solution.get("expect", {}))
            )

        self.gate_errors.extend(expectation_errors)
        catalog_fields = (
            "name",
            "role",
            "algorithm",
            "complexity",
            "supported_domain",
            "defect_layer",
            "defect",
            "kill_profile",
        )
        evaluation_decision = "no_go" if self.gate_errors else "go"
        result = {
            "decision": evaluation_decision,
            "completed_gate": "candidate-evaluation",
            "blocking_issues": list(self.gate_errors),
            "next_actions": (
                ["repair candidate or data blockers and rerun invalidated gates"]
                if self.gate_errors
                else ["run independent acceptance and editorial review"]
            ),
            "case_ids": self.case_ids,
            "scoring": self.config["scoring"],
            "total_points": self.total_points,
            "solution_catalog": [
                {field: solution[field] for field in catalog_fields if field in solution}
                for solution in self.config.get("solutions", [])
            ],
            "solutions": matrix,
            "scores": scores,
            "score_breakdowns": score_breakdowns,
            "expectation_errors": expectation_errors,
            "gate_errors": list(self.gate_errors),
        }
        atomic_write(self.verdicts_path, (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode())
        return result

    def check_expectations(
        self, name: str, row: dict[str, dict[str, Any]], score: float, expect: dict[str, Any]
    ) -> list[str]:
        errors: list[str] = []
        for case_id in self.expand_case_ids(expect.get("must_pass", []), f"{name} must_pass"):
            verdict = row[case_id]["verdict"]
            if verdict != "AC":
                errors.append(f"{name} must pass {case_id}, got {verdict}")
        for case_id in self.expand_case_ids(expect.get("must_fail", []), f"{name} must_fail"):
            if row[case_id]["verdict"] == "AC":
                errors.append(f"{name} unexpectedly passed required-kill case {case_id}")
        kill_pool = self.expand_case_ids(expect.get("must_fail_one_of", []), f"{name} must_fail_one_of")
        if kill_pool and all(row[case_id]["verdict"] == "AC" for case_id in kill_pool):
            errors.append(f"{name} survived every required-kill case: {kill_pool}")
        if "score_min" in expect and score < float(expect["score_min"]):
            errors.append(f"{name} scored {score:g}, below minimum {float(expect['score_min']):g}")
        if "score_max" in expect and score > float(expect["score_max"]):
            errors.append(f"{name} scored {score:g}, above maximum {float(expect['score_max']):g}")
        return errors

    def write_report(self, verdicts: dict[str, Any] | None, completed_gate: str) -> None:
        decision = "no_go" if self.gate_errors else "go"
        lines = [
            "# Test data pipeline report",
            "",
            f"- Decision: **{decision}**",
            f"- Completed gate: `{completed_gate}`",
            f"- Cases: {len(self.cases)}",
            f"- Scoring mode: `{self.scoring_mode}`",
            f"- Total points: {self.total_points:g}",
            f"- Compare mode: `{self.compare_mode}`",
            f"- Memory limit: {self.memory_limit_mib} MiB",
            "- Test data config: `"
            + str(self.testdata_config_path.relative_to(self.root)).replace("\\", "/")
            + "`",
        ]
        if self.environment:
            lines.extend(
                [
                    f"- CPU: `{self.environment.get('cpu', 'unknown')}`",
                    f"- Compiler: `{self.environment.get('compiler_version', 'unavailable')}`",
                ]
            )
        if self.timing_summary:
            lines.append(
                f"- Suggested time limit: {self.timing_summary['suggested_seconds']}s "
                f"(slowest {self.timing_summary['slowest_ms']}ms x "
                f"{self.timing_summary['multiplier']:g})"
            )
        if self.gate_errors:
            lines.extend(["- Overall gate: **FAILED**", "", "## Gate failures", ""])
            lines.extend(f"- {error}" for error in self.gate_errors)
            lines.extend(
                [
                    "",
                    "## Next actions",
                    "",
                    "- Repair each blocking issue and rerun this gate plus every invalidated downstream gate.",
                ]
            )
        else:
            lines.append("- Overall gate: **PASSED**")
            lines.extend(
                [
                    "",
                    "## Next actions",
                    "",
                    "- Continue to the next acceptance gate; this checkpoint alone is not a release approval.",
                ]
            )

        lines.extend(["", "## Scoring units", ""])
        lines.append("| Unit | Type | Cases | Points | Dependencies |")
        lines.append("|---|---|---|---:|---|")
        for unit in self.scoring_units:
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(unit["id"]).replace("|", "\\|"),
                        str(unit["type"]),
                        ", ".join(unit["cases"]),
                        f"{unit['points']:g}",
                        ", ".join(unit["depends_on"]),
                    ]
                )
                + " |"
            )

        if verdicts and verdicts.get("solution_catalog"):
            lines.extend(["", "## Solution catalog", ""])
            lines.append("| Solution | Role | Algorithm | Defect layer | Kill profile |")
            lines.append("|---|---|---|---|---|")
            for item in verdicts["solution_catalog"]:
                cells = [
                    str(item.get(field, "")).replace("|", "\\|")
                    for field in ("name", "role", "algorithm", "defect_layer", "kill_profile")
                ]
                lines.append("| " + " | ".join(cells) + " |")

        if verdicts and verdicts.get("solutions"):
            lines.extend(["", "## Verdict matrix", ""])
            header = "| Solution | " + " | ".join(self.case_ids) + " | Score |"
            divider = "|---|" + "|".join("---" for _ in self.case_ids) + "|---|"
            lines.extend([header, divider])
            for name, row in verdicts["solutions"].items():
                cells = [row[case_id]["verdict"] for case_id in self.case_ids]
                score = verdicts.get("scores", {}).get(name, 0)
                lines.append("| " + name + " | " + " | ".join(cells) + f" | {score:g} |")
        lines.append("")
        atomic_write(self.report_path, "\n".join(lines).encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="pipeline JSON configuration")
    parser.add_argument(
        "stage",
        choices=("build", "config", "generate", "evaluate", "all"),
        nargs="?",
        default="all",
    )
    args = parser.parse_args()

    try:
        pipeline = Pipeline(args.config)
        if args.stage == "build":
            pipeline.build(include_solutions=True)
            pipeline.write_report(None, "build")
        elif args.stage == "config":
            pipeline.write_testdata_config()
            pipeline.write_report(None, "testdata-config")
        elif args.stage == "generate":
            pipeline.build(include_solutions=False)
            pipeline.generate()
            pipeline.write_report(None, "generation")
        elif args.stage == "evaluate":
            pipeline.build(include_solutions=True)
            verdicts = pipeline.evaluate()
            pipeline.write_report(verdicts, "candidate-evaluation")
        else:
            pipeline.build(include_solutions=True)
            pipeline.generate()
            verdicts = pipeline.evaluate()
            pipeline.write_report(verdicts, "build-generation-evaluation")
        if pipeline.gate_errors:
            print(f"pipeline completed with {len(pipeline.gate_errors)} failed gate(s)", file=sys.stderr)
            return 2
        print(f"pipeline passed; report: {pipeline.report_path}")
        return 0
    except PipelineError as exc:
        print(f"pipeline error: {exc}", file=sys.stderr)
        return 2
    except (OSError, ValueError) as exc:
        print(f"pipeline system error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
