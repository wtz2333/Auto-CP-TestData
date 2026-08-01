#!/usr/bin/env python3
"""Regression tests for intake and scoring validation."""

from __future__ import annotations

import copy
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock


MODULE_PATH = Path(__file__).with_name("run_pipeline.py")
SKILL_ROOT = MODULE_PATH.parent.parent
SPEC = importlib.util.spec_from_file_location("build_cp_run_pipeline", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load run_pipeline.py")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
ORIGINAL_SYS_PATH = list(sys.path)
try:
    if str(MODULE_PATH.parent) not in sys.path:
        sys.path.insert(0, str(MODULE_PATH.parent))
    SPEC.loader.exec_module(MODULE)
finally:
    sys.path[:] = ORIGINAL_SYS_PATH
Pipeline = MODULE.Pipeline
PipelineError = MODULE.PipelineError


class CliPipelineFixture:
    def __init__(
        self,
        *,
        enabled: bool,
        gate_errors: list[str] | None = None,
    ) -> None:
        self.polyhedron_package_enabled = enabled
        self.polyhedron_package_metadata: dict[str, Any] | None = None
        self.gate_errors = list(gate_errors or [])
        self.report_path = Path("report.md")
        self.calls: list[Any] = []

    def build(self, *, include_solutions: bool) -> None:
        self.calls.append(("build", include_solutions))

    def generate(self) -> None:
        self.calls.append("generate")

    def evaluate(self) -> dict[str, Any]:
        self.calls.append("evaluate")
        return {"decision": "go"}

    def package_polyhedron(self) -> dict[str, Any]:
        self.calls.append("package")
        self.polyhedron_package_metadata = {
            "path": "polyhedron.zip",
            "sha256": "a" * 64,
            "members": [],
        }
        return self.polyhedron_package_metadata

    def write_report(
        self, verdicts: dict[str, Any] | None, completed_gate: str
    ) -> None:
        self.calls.append(("report", completed_gate, verdicts))


class PipelineConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        for name in ("gen.cpp", "valid.cpp", "std.cpp"):
            (self.root / name).write_text("// validation fixture\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_run_pipeline_supports_script_module_and_package_imports(self) -> None:
        commands = [
            [sys.executable, str(MODULE_PATH), "--help"],
            [sys.executable, "-m", "scripts.run_pipeline", "--help"],
            [sys.executable, "-c", "import scripts.run_pipeline"],
        ]
        for command in commands:
            with self.subTest(command=command):
                result = subprocess.run(
                    command,
                    cwd=SKILL_ROOT,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    result.stderr.decode("utf-8", errors="replace"),
                )

    def base_task(self) -> dict[str, Any]:
        return {
            "intake": {
                "status": "complete",
                "preferences": {
                    "original_problem_dir": {"value": "original", "source": "user"},
                    "output_dir": {"value": "workspace", "source": "user"},
                    "case_count_policy": {
                        "value": {"mode": "fixed", "count": 3},
                        "source": "user",
                    },
                    "deliverables": {
                        "value": ["statement", "data", "editorial"],
                        "source": "user",
                    },
                    "scoring_mode": {"value": "mixed", "source": "user"},
                    "scoring_plan": {
                        "value": {
                            "unit_authority": "delegated",
                            "expectation_mode": "range",
                        },
                        "source": "user",
                    },
                    "statement_style": {
                        "value": {
                            "mode": "light-context",
                            "theme": None,
                            "required_elements": [],
                            "forbidden_elements": [],
                        },
                        "source": "user",
                    },
                    "rewrite_scope": {
                        "value": "constraints-and-subtasks",
                        "source": "user",
                    },
                    "target_audience": {"value": "NOIP", "source": "user"},
                    "package_format": {
                        "value": "luogu-markdown",
                        "source": "user",
                    },
                    "polyhedron_zip": {"value": False, "source": "user"},
                },
            },
            "technical_facts": {
                "language_standard": {
                    "value": "C++14",
                    "source": "discovered",
                    "evidence": "statement",
                },
                "time_limit_ms": {
                    "value": 2000,
                    "source": "discovered",
                    "evidence": "statement",
                },
                "memory_limit_mib": {
                    "value": 512,
                    "source": "derived",
                    "evidence": "project policy",
                },
                "judge_mode": {
                    "value": "batch-tokens",
                    "source": "discovered",
                    "evidence": "statement",
                },
            },
        }

    def mixed_scoring(self) -> dict[str, Any]:
        return {
            "mode": "mixed",
            "total_points": 100,
            "units": [
                {
                    "id": "base",
                    "type": "case",
                    "cases": ["001"],
                    "points": 20,
                    "depends_on": [],
                },
                {
                    "id": "full",
                    "type": "bundle",
                    "cases": ["002", "003"],
                    "points": 80,
                    "depends_on": ["base"],
                },
            ],
        }

    def base_config(self) -> dict[str, Any]:
        return {
            "task_contract": "task.json",
            "case_count": 3,
            "memory_limit_mib": 512,
            "time_limit_ms": 2000,
            "output_compare": "tokens",
            "testdata_config": {"path": "data/config.yaml"},
            "polyhedron_package": {
                "enabled": False,
                "path": "polyhedron.zip",
            },
            "cxxflags": ["-std=c++14", "-O2"],
            "sources": {
                "generator": "gen.cpp",
                "validator": "valid.cpp",
                "oracle": "std.cpp",
            },
            "scoring": self.mixed_scoring(),
            "cases": [
                {
                    "id": "001",
                    "seed": 1,
                    "profile": "minimum",
                    "group": "small",
                    "tags": ["sanity"],
                    "purpose": "minimum legal case",
                },
                {
                    "id": "002",
                    "seed": 2,
                    "profile": "maximum",
                    "group": "full",
                    "tags": ["boundary"],
                    "purpose": "maximum legal case",
                },
                {
                    "id": "003",
                    "seed": 3,
                    "profile": "adversarial",
                    "group": "full",
                    "tags": ["adversarial"],
                    "purpose": "kill a plausible wrong solution",
                },
            ],
            "solutions": [],
        }

    def load(
        self,
        config: dict[str, Any] | None = None,
        task: dict[str, Any] | None = None,
    ) -> Any:
        actual_config = copy.deepcopy(config or self.base_config())
        actual_task = copy.deepcopy(task or self.base_task())
        (self.root / "task.json").write_text(
            json.dumps(actual_task, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        config_path = self.root / "pipeline.json"
        config_path.write_text(
            json.dumps(actual_config, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        return Pipeline(config_path)

    @staticmethod
    def enable_polyhedron(config: dict[str, Any], task: dict[str, Any]) -> None:
        config["polyhedron_package"]["enabled"] = True
        task["intake"]["preferences"]["polyhedron_zip"]["value"] = True

    def write_packaging_artifacts(self, pipeline: Any) -> None:
        (pipeline.root / "statement.md").write_text(
            "# Packaging fixture\n\nProblem statement.\n", encoding="utf-8"
        )
        oracle_path = pipeline.source_path(str(pipeline.config["sources"]["oracle"]))
        self.assertTrue(oracle_path.is_file())
        pipeline.data_dir.mkdir(parents=True, exist_ok=True)
        for case_id in pipeline.case_ids:
            (pipeline.data_dir / f"{case_id}.in").write_bytes(b"input\n")
            (pipeline.data_dir / f"{case_id}.ans").write_bytes(b"answer\n")
        pipeline.write_testdata_config()

    def write_previous_polyhedron_artifacts(
        self, pipeline: Any
    ) -> tuple[bytes, str]:
        package_bytes = b"previous Polyhedron package\n"
        package_sha = MODULE.sha256_bytes(package_bytes)
        pipeline.polyhedron_package_path.write_bytes(package_bytes)
        pipeline.report_path.write_text(
            "# Previous pipeline report\n\n"
            "- Decision: **go**\n"
            "- Polyhedron package status: `built`\n"
            f"- Polyhedron package SHA-256: `{package_sha}`\n",
            encoding="utf-8",
        )
        return package_bytes, package_sha

    def run_cli(
        self, pipeline: Any, stage: str
    ) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            mock.patch.object(MODULE, "Pipeline", return_value=pipeline),
            mock.patch.object(
                sys, "argv", ["run_pipeline.py", "pipeline.json", stage]
            ),
            mock.patch.object(sys, "stdout", stdout),
            mock.patch.object(sys, "stderr", stderr),
        ):
            exit_code = MODULE.main()
        return exit_code, stdout.getvalue(), stderr.getvalue()

    @staticmethod
    def row(*accepted: str) -> dict[str, dict[str, Any]]:
        accepted_set = set(accepted)
        return {
            case_id: {
                "verdict": "AC" if case_id in accepted_set else "WA",
                "time_ms": 0,
            }
            for case_id in ("001", "002", "003")
        }

    def test_mixed_scoring_is_all_or_nothing_and_honors_dependencies(self) -> None:
        pipeline = self.load()
        score, breakdown = pipeline.score_row(self.row("001", "002"))
        self.assertEqual(score, 20)
        self.assertFalse(breakdown["full"]["awarded"])

        score, breakdown = pipeline.score_row(self.row("002", "003"))
        self.assertEqual(score, 0)
        self.assertTrue(breakdown["full"]["cases_passed"])
        self.assertFalse(breakdown["full"]["dependencies_passed"])

        score, _ = pipeline.score_row(self.row("001", "002", "003"))
        self.assertEqual(score, 100)

    def test_shipped_examples_validate_with_polyhedron_defaults(self) -> None:
        config = json.loads(
            (SKILL_ROOT / "assets" / "pipeline.example.json").read_text(encoding="utf-8")
        )
        task = json.loads(
            (SKILL_ROOT / "assets" / "task.example.json").read_text(encoding="utf-8")
        )
        config["polyhedron_package"] = {
            "enabled": False,
            "path": "polyhedron.zip",
        }
        task["intake"]["preferences"]["polyhedron_zip"] = {
            "value": False,
            "source": "user",
        }
        pipeline = self.load(config, task)
        self.assertEqual(pipeline.scoring_mode, "mixed")
        self.assertEqual(pipeline.total_points, 100)

    def test_polyhedron_package_is_built_and_reported_after_acceptance(self) -> None:
        config = self.base_config()
        task = self.base_task()
        self.enable_polyhedron(config, task)
        pipeline = self.load(config, task)
        self.write_packaging_artifacts(pipeline)

        metadata = pipeline.package_polyhedron()

        expected_members = [
            "polyhedron-export/",
            "polyhedron-export/problem.yaml",
            "polyhedron-export/problem_zh.md",
            "polyhedron-export/testdata/",
            "polyhedron-export/testdata/001.in",
            "polyhedron-export/testdata/001.out",
            "polyhedron-export/testdata/002.in",
            "polyhedron-export/testdata/002.out",
            "polyhedron-export/testdata/003.in",
            "polyhedron-export/testdata/003.out",
            "polyhedron-export/testdata/_solution_std.cc",
            "polyhedron-export/testdata/config.yaml",
            "polyhedron-export/testdata/polyhedron.metadata",
        ]
        self.assertEqual(pipeline.polyhedron_package_status, "built")
        self.assertEqual(metadata["path"], "polyhedron.zip")
        self.assertEqual(
            metadata["sha256"], MODULE.sha256_file(pipeline.polyhedron_package_path)
        )
        self.assertEqual(metadata["members"], expected_members)
        pipeline.write_report(None, "polyhedron-package")
        report = pipeline.report_path.read_text(encoding="utf-8")
        self.assertIn("Polyhedron package status: `built`", report)
        self.assertIn("Polyhedron package: `polyhedron.zip`", report)
        self.assertIn(metadata["sha256"], report)
        for member in expected_members:
            self.assertIn(f"- `{member}`", report)

    def test_polyhedron_package_does_not_overwrite_after_upstream_gate_failure(self) -> None:
        config = self.base_config()
        task = self.base_task()
        self.enable_polyhedron(config, task)
        pipeline = self.load(config, task)
        self.write_packaging_artifacts(pipeline)
        pipeline.gate_errors.append("candidate acceptance failed")

        with self.assertRaisesRegex(PipelineError, "upstream gate"):
            pipeline.package_polyhedron()
        self.assertFalse(pipeline.polyhedron_package_path.exists())

        pipeline.polyhedron_package_path.write_bytes(b"existing package")
        with self.assertRaisesRegex(PipelineError, "upstream gate"):
            pipeline.package_polyhedron()
        self.assertEqual(
            pipeline.polyhedron_package_path.read_bytes(), b"existing package"
        )

    def test_polyhedron_package_rejects_direct_call_when_not_enabled(self) -> None:
        pipeline = self.load()
        self.write_packaging_artifacts(pipeline)

        with self.assertRaisesRegex(PipelineError, "not enabled"):
            pipeline.package_polyhedron()

        self.assertFalse(pipeline.polyhedron_package_path.exists())

    def test_polyhedron_packager_failure_is_wrapped_as_pipeline_error(self) -> None:
        config = self.base_config()
        task = self.base_task()
        self.enable_polyhedron(config, task)
        pipeline = self.load(config, task)
        self.write_packaging_artifacts(pipeline)
        (pipeline.root / "statement.md").unlink()

        with self.assertRaisesRegex(
            PipelineError, r"^Polyhedron package failed:.*statement"
        ):
            pipeline.package_polyhedron()

    def test_all_cli_packages_after_successful_evaluation_when_enabled(self) -> None:
        pipeline = CliPipelineFixture(enabled=True)

        exit_code, _, _ = self.run_cli(pipeline, "all")

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            pipeline.calls,
            [
                ("build", True),
                "generate",
                "evaluate",
                "package",
                (
                    "report",
                    "build-generation-evaluation-package",
                    {"decision": "go"},
                ),
            ],
        )

    def test_all_cli_skips_packaging_when_disabled(self) -> None:
        pipeline = CliPipelineFixture(enabled=False)

        exit_code, _, _ = self.run_cli(pipeline, "all")

        self.assertEqual(exit_code, 0)
        self.assertNotIn("package", pipeline.calls)
        self.assertIn(
            (
                "report",
                "build-generation-evaluation",
                {"decision": "go"},
            ),
            pipeline.calls,
        )

    def test_package_cli_fails_clearly_when_packaging_is_disabled(self) -> None:
        pipeline = self.load()
        previous_package, previous_sha = self.write_previous_polyhedron_artifacts(
            pipeline
        )

        with (
            mock.patch.object(pipeline, "build") as build,
            mock.patch.object(pipeline, "generate") as generate,
            mock.patch.object(pipeline, "evaluate") as evaluate,
            mock.patch.object(
                pipeline,
                "package_polyhedron",
                wraps=pipeline.package_polyhedron,
            ) as package_polyhedron,
        ):
            exit_code, _, stderr = self.run_cli(pipeline, "package")

        self.assertEqual(exit_code, 2)
        build.assert_not_called()
        generate.assert_not_called()
        evaluate.assert_not_called()
        package_polyhedron.assert_not_called()
        self.assertIn("1 failed gate", stderr)
        self.assertEqual(
            pipeline.polyhedron_package_path.read_bytes(), previous_package
        )
        report = pipeline.report_path.read_text(encoding="utf-8")
        self.assertIn("Decision: **no_go**", report)
        self.assertIn("Completed gate: `polyhedron-package-preflight`", report)
        self.assertIn("Polyhedron package status: `disabled`", report)
        self.assertIn("not updated by this run", report)
        self.assertIn("previous run", report)
        self.assertIn("Polyhedron package is not enabled", report)
        self.assertNotIn(previous_sha, report)

    def test_package_cli_does_not_package_when_evaluation_has_gate_errors(self) -> None:
        pipeline = CliPipelineFixture(
            enabled=True, gate_errors=["candidate acceptance failed"]
        )

        exit_code, _, stderr = self.run_cli(pipeline, "package")

        self.assertEqual(exit_code, 2)
        self.assertNotIn("package", pipeline.calls)
        self.assertIn(
            (
                "report",
                "build-generation-evaluation",
                {"decision": "go"},
            ),
            pipeline.calls,
        )
        self.assertIn("1 failed gate", stderr)

    def test_package_cli_failure_preserves_old_zip_and_overwrites_old_go_report(self) -> None:
        config = self.base_config()
        task = self.base_task()
        self.enable_polyhedron(config, task)
        pipeline = self.load(config, task)
        self.write_packaging_artifacts(pipeline)
        previous_package, previous_sha = self.write_previous_polyhedron_artifacts(
            pipeline
        )
        (pipeline.root / "statement.md").unlink()

        with (
            mock.patch.object(pipeline, "build"),
            mock.patch.object(pipeline, "generate"),
            mock.patch.object(
                pipeline, "evaluate", return_value={"decision": "go"}
            ),
        ):
            exit_code, _, _ = self.run_cli(pipeline, "package")

        self.assertEqual(exit_code, 2)
        self.assertEqual(
            pipeline.polyhedron_package_path.read_bytes(), previous_package
        )
        report = pipeline.report_path.read_text(encoding="utf-8")
        self.assertIn("Decision: **no_go**", report)
        self.assertIn(
            "Polyhedron package status: `failed_preserved_previous`", report
        )
        self.assertIn("not updated by this run", report)
        self.assertIn("previous run", report)
        self.assertNotIn(previous_sha, report)

    def test_upstream_gate_failure_marks_old_zip_as_stale_in_new_report(self) -> None:
        config = self.base_config()
        task = self.base_task()
        self.enable_polyhedron(config, task)
        pipeline = self.load(config, task)
        previous_package, previous_sha = self.write_previous_polyhedron_artifacts(
            pipeline
        )
        pipeline.gate_errors.append("candidate acceptance failed")

        with (
            mock.patch.object(pipeline, "build"),
            mock.patch.object(pipeline, "generate"),
            mock.patch.object(
                pipeline, "evaluate", return_value={"decision": "no_go"}
            ),
            mock.patch.object(
                pipeline,
                "package_polyhedron",
                wraps=pipeline.package_polyhedron,
            ) as package_polyhedron,
        ):
            exit_code, _, _ = self.run_cli(pipeline, "package")

        self.assertEqual(exit_code, 2)
        package_polyhedron.assert_not_called()
        self.assertEqual(
            pipeline.polyhedron_package_path.read_bytes(), previous_package
        )
        report = pipeline.report_path.read_text(encoding="utf-8")
        self.assertIn("Decision: **no_go**", report)
        self.assertIn(
            "Polyhedron package status: `skipped_upstream_failure`", report
        )
        self.assertIn("not updated by this run", report)
        self.assertIn("previous run", report)
        self.assertNotIn(previous_sha, report)

    def test_all_disabled_marks_old_zip_as_stale_without_failing_pipeline(self) -> None:
        pipeline = self.load()
        previous_package, previous_sha = self.write_previous_polyhedron_artifacts(
            pipeline
        )

        with (
            mock.patch.object(pipeline, "build"),
            mock.patch.object(pipeline, "generate"),
            mock.patch.object(
                pipeline, "evaluate", return_value={"decision": "go"}
            ),
            mock.patch.object(
                pipeline,
                "package_polyhedron",
                wraps=pipeline.package_polyhedron,
            ) as package_polyhedron,
        ):
            exit_code, _, _ = self.run_cli(pipeline, "all")

        self.assertEqual(exit_code, 0)
        package_polyhedron.assert_not_called()
        self.assertEqual(
            pipeline.polyhedron_package_path.read_bytes(), previous_package
        )
        report = pipeline.report_path.read_text(encoding="utf-8")
        self.assertIn("Decision: **go**", report)
        self.assertIn("Polyhedron package status: `disabled`", report)
        self.assertIn("not updated by this run", report)
        self.assertIn("previous run", report)
        self.assertNotIn(previous_sha, report)

    def test_cli_persists_polyhedron_preparation_failures(self) -> None:
        scenarios = [
            ("all", "generate", "generator preparation failed"),
            ("package", "build", "build preparation failed"),
        ]
        for stage, failing_step, error_text in scenarios:
            with self.subTest(stage=stage, failing_step=failing_step):
                config = self.base_config()
                task = self.base_task()
                self.enable_polyhedron(config, task)
                pipeline = self.load(config, task)
                previous_package, previous_sha = (
                    self.write_previous_polyhedron_artifacts(pipeline)
                )

                with (
                    mock.patch.object(pipeline, "build") as build,
                    mock.patch.object(pipeline, "generate") as generate,
                    mock.patch.object(pipeline, "evaluate") as evaluate,
                    mock.patch.object(
                        pipeline,
                        "package_polyhedron",
                        wraps=pipeline.package_polyhedron,
                    ) as package_polyhedron,
                ):
                    failing_mock = build if failing_step == "build" else generate
                    failing_mock.side_effect = PipelineError(error_text)
                    exit_code, _, stderr = self.run_cli(pipeline, stage)

                self.assertEqual(exit_code, 2)
                build.assert_called_once_with(include_solutions=True)
                if failing_step == "build":
                    generate.assert_not_called()
                else:
                    generate.assert_called_once_with()
                evaluate.assert_not_called()
                package_polyhedron.assert_not_called()
                self.assertEqual(
                    pipeline.polyhedron_package_path.read_bytes(),
                    previous_package,
                )
                report = pipeline.report_path.read_text(encoding="utf-8")
                stable_error = f"Polyhedron preparation failed: {error_text}"
                self.assertIn("Decision: **no_go**", report)
                self.assertIn(
                    "Completed gate: `polyhedron-preparation`", report
                )
                self.assertIn(
                    "Polyhedron package status: `skipped_upstream_failure`",
                    report,
                )
                self.assertIn("not updated by this run", report)
                self.assertIn("previous run", report)
                self.assertIn(stable_error, report)
                self.assertIn(stable_error, stderr)
                self.assertNotIn(previous_sha, report)

    def test_testdata_config_is_derived_from_scoring_units(self) -> None:
        pipeline = self.load()
        pipeline.data_dir.mkdir(parents=True)
        for case_id in pipeline.case_ids:
            (pipeline.data_dir / f"{case_id}.in").write_bytes(b"input\n")
            (pipeline.data_dir / f"{case_id}.ans").write_bytes(b"answer\n")
        metadata = pipeline.write_testdata_config()
        expected = (
            SKILL_ROOT / "assets" / "testdata-config.example.yaml"
        ).read_bytes()
        self.assertEqual((pipeline.data_dir / "config.yaml").read_bytes(), expected)
        self.assertEqual(
            [(item["score"], item["type"], item["if"]) for item in metadata["subtasks"]],
            [(20.0, "sum", []), (80.0, "min", [1])],
        )

    def test_testdata_config_rejects_stale_content(self) -> None:
        pipeline = self.load()
        pipeline.data_dir.mkdir(parents=True)
        for case_id in pipeline.case_ids:
            (pipeline.data_dir / f"{case_id}.in").write_bytes(b"input\n")
            (pipeline.data_dir / f"{case_id}.ans").write_bytes(b"answer\n")
        pipeline.write_testdata_config()
        (pipeline.data_dir / "config.yaml").write_bytes(b"type: default\n")
        with self.assertRaisesRegex(PipelineError, "stale"):
            pipeline.write_testdata_config(check_only=True)

    def test_per_case_scoring(self) -> None:
        config = self.base_config()
        config["scoring"] = {
            "mode": "per_case",
            "total_points": 100,
            "units": [
                {"id": "a", "type": "case", "cases": ["001"], "points": 20},
                {"id": "b", "type": "case", "cases": ["002"], "points": 30},
                {"id": "c", "type": "case", "cases": ["003"], "points": 50},
            ],
        }
        task = self.base_task()
        task["intake"]["preferences"]["scoring_mode"]["value"] = "per_case"
        score, _ = self.load(config, task).score_row(self.row("001", "003"))
        self.assertEqual(score, 70)

    def test_bundled_scoring(self) -> None:
        config = self.base_config()
        config["scoring"] = {
            "mode": "bundled",
            "total_points": 100,
            "units": [
                {"id": "a", "type": "bundle", "cases": ["001"], "points": 20},
                {
                    "id": "b",
                    "type": "bundle",
                    "cases": ["002", "003"],
                    "points": 80,
                    "depends_on": ["a"],
                },
            ],
        }
        task = self.base_task()
        task["intake"]["preferences"]["scoring_mode"]["value"] = "bundled"
        score, _ = self.load(config, task).score_row(self.row("001", "002"))
        self.assertEqual(score, 20)

    def test_bounded_adaptive_policy_requires_bundled_scoring(self) -> None:
        task = self.base_task()
        task["intake"]["preferences"]["case_count_policy"]["value"] = {
            "mode": "bounded_adaptive",
            "min": 3,
            "max": 40,
            "retain_existing": True,
            "fill_by_hacks": True,
        }
        with self.assertRaisesRegex(PipelineError, "only for bundled"):
            self.load(task=task)

    def test_delegated_output_path_is_allowed_with_reason(self) -> None:
        task = self.base_task()
        task["intake"]["preferences"]["output_dir"] = {
            "value": "workspace/rewritten-title",
            "source": "delegated",
            "decision_note": "User delegated the rewritten title and same-named folder.",
        }
        self.load(task=task)

    def test_missing_required_preference_is_rejected(self) -> None:
        task = self.base_task()
        del task["intake"]["preferences"]["statement_style"]
        with self.assertRaisesRegex(PipelineError, "unresolved preferences"):
            self.load(task=task)

    def test_delegation_without_reason_is_rejected(self) -> None:
        task = self.base_task()
        task["intake"]["preferences"]["statement_style"]["source"] = "delegated"
        with self.assertRaisesRegex(PipelineError, "needs decision_note"):
            self.load(task=task)

    def test_duplicate_case_membership_is_rejected(self) -> None:
        config = self.base_config()
        config["scoring"]["units"][1]["cases"].append("001")
        with self.assertRaisesRegex(PipelineError, "belongs to both"):
            self.load(config=config)

    def test_dependency_cycle_is_rejected(self) -> None:
        config = self.base_config()
        config["scoring"]["units"][0]["depends_on"] = ["full"]
        with self.assertRaisesRegex(PipelineError, "dependency cycle"):
            self.load(config=config)

    def test_scoring_total_mismatch_is_rejected(self) -> None:
        config = self.base_config()
        config["scoring"]["total_points"] = 99
        with self.assertRaisesRegex(PipelineError, "points total"):
            self.load(config=config)

    def test_legacy_case_points_are_rejected(self) -> None:
        config = self.base_config()
        config["cases"][0]["points"] = 20
        with self.assertRaisesRegex(PipelineError, "legacy points"):
            self.load(config=config)

    def test_themed_style_requires_a_theme(self) -> None:
        task = self.base_task()
        style = task["intake"]["preferences"]["statement_style"]["value"]
        style["mode"] = "themed"
        style["theme"] = None
        with self.assertRaisesRegex(PipelineError, "requires a nonempty theme"):
            self.load(task=task)

    def test_missing_technical_fact_is_rejected(self) -> None:
        task = self.base_task()
        del task["technical_facts"]["judge_mode"]
        with self.assertRaisesRegex(PipelineError, "unresolved technical facts"):
            self.load(task=task)

    def test_missing_task_contract_is_rejected(self) -> None:
        config = self.base_config()
        del config["task_contract"]
        with self.assertRaisesRegex(PipelineError, "task_contract is required"):
            self.load(config=config)

    def test_task_and_pipeline_scoring_modes_must_match(self) -> None:
        task = self.base_task()
        task["intake"]["preferences"]["scoring_mode"]["value"] = "per_case"
        with self.assertRaisesRegex(PipelineError, "does not match"):
            self.load(task=task)

    def test_polyhedron_package_must_match_task_preference(self) -> None:
        config = self.base_config()
        config["polyhedron_package"]["enabled"] = True
        with self.assertRaisesRegex(PipelineError, "does not match"):
            self.load(config=config)

    def test_polyhedron_package_path_must_be_polyhedron_zip(self) -> None:
        config = self.base_config()
        config["polyhedron_package"]["path"] = "dist/problem.zip"
        with self.assertRaisesRegex(PipelineError, "must be polyhedron.zip"):
            self.load(config=config)

    def test_polyhedron_package_requires_standard_batch_judging(self) -> None:
        config = self.base_config()
        config["polyhedron_package"]["enabled"] = True
        task = self.base_task()
        task["intake"]["preferences"]["polyhedron_zip"]["value"] = True
        task["technical_facts"]["judge_mode"]["value"] = "custom-checker"
        with self.assertRaisesRegex(PipelineError, "standard batch"):
            self.load(config=config, task=task)


if __name__ == "__main__":
    unittest.main()
