#!/usr/bin/env python3
"""Regression tests for intake and scoring validation."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


MODULE_PATH = Path(__file__).with_name("run_pipeline.py")
SKILL_ROOT = MODULE_PATH.parent.parent
SPEC = importlib.util.spec_from_file_location("build_cp_run_pipeline", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load run_pipeline.py")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
Pipeline = MODULE.Pipeline
PipelineError = MODULE.PipelineError


class PipelineConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        for name in ("gen.cpp", "valid.cpp", "std.cpp"):
            (self.root / name).write_text("// validation fixture\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

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
